"""
Review & Aprovar — fila unificada de itens pendentes de aprovação.
Agrega regras, tabelas monitoradas e collections com status SUBMITTED.
"""

import streamlit as st

from core.api_client import APIError
from core.session import get_client, get_user_role, is_admin

_STATUS_COLOR = {
    "DRAFT": "gray", "SUBMITTED": "blue", "APPROVED": "green",
    "REJECTED": "red", "DEPRECATED": "orange",
}

_TYPE_ICON = {
    "rule": ":material/rule:",
    "table": ":material/table_chart:",
    "collection": ":material/folder_open:",
}

_TYPE_LABEL = {
    "rule": "Regra",
    "table": "Tabela Monitorada",
    "collection": "Collection",
}


def _badge(text, color_map):
    return f":{color_map.get(text, 'gray')}[{text}]"


@st.dialog("Confirmar aprovação / rejeição")
def _action_dialog(action: str, item: dict):
    entity_type = item["_type"]
    entity_id = item["_id"]
    name = item.get("name") or item.get("table_fqn") or entity_id

    st.subheader(f"{'Aprovar' if action == 'approve' else 'Rejeitar'}: {name}")
    st.caption(f"Tipo: {_TYPE_LABEL.get(entity_type, entity_type)}")

    rationale = st.text_area("Motivo (obrigatório):")

    c1, c2 = st.columns(2)
    if c1.button("Confirmar", type="primary"):
        if not rationale.strip():
            st.warning("Insira o motivo.")
            return
        client = get_client()
        try:
            if entity_type == "rule":
                if action == "approve":
                    client.approve_registry_rule(entity_id, rationale)
                else:
                    client.reject_registry_rule(entity_id, rationale)
            elif entity_type == "table":
                if action == "approve":
                    client.approve_monitored_table(entity_id, rationale)
                else:
                    client.reject_monitored_table(entity_id, rationale)
            elif entity_type == "collection":
                if action == "approve":
                    client.approve_collection(entity_id, rationale)
                else:
                    client.reject_collection(entity_id, rationale)
            st.session_state.pop("_drafts_items", None)
            st.rerun()
        except APIError as e:
            st.error(str(e))
    if c2.button("Cancelar"):
        st.rerun()


@st.dialog("Alterações pendentes", width="large")
def _diff_dialog(item: dict):
    entity_type = item["_type"]
    entity_id = item["_id"]
    name = item.get("name", entity_id)

    st.subheader(f"Diff: {name}")
    st.caption(f"Tipo: {_TYPE_LABEL.get(entity_type, entity_type)}")
    st.divider()

    before = None
    after = None

    try:
        if entity_type == "collection":
            diff = get_client().get_collection_review_changes(entity_id)
            before = diff.get("before")
            after = diff.get("after")
            changed = diff.get("changed_fields", [])
            if changed:
                st.caption(f"Campos alterados: **{', '.join(changed)}**")
    except APIError:
        pass

    if before and after:
        col1, col2 = st.columns(2)
        col1.markdown("**Estado anterior (aprovado)**")
        col1.json(before)
        col2.markdown("**Estado pendente (submetido)**")
        col2.json(after)
    else:
        # Fallback: mostrar estado atual do item
        st.markdown("**Estado atual (submetido)**")
        display = {k: v for k, v in item.items() if not k.startswith("_")}
        st.json(display)
        st.caption("Diff completo disponível apenas para Collections neste momento.")


# ── Load pending items ────────────────────────────────────────────────────────

def _load_pending():
    if "_drafts_items" in st.session_state:
        return st.session_state["_drafts_items"]

    client = get_client()
    items = []

    try:
        rules = client.list_registry_rules(status="SUBMITTED")
        for r in rules:
            items.append({**r, "_type": "rule", "_id": r.get("id", ""), "name": r.get("name", "—")})
    except APIError:
        pass

    try:
        tables = client.list_monitored_tables()
        for t in [t for t in tables if t.get("status") == "SUBMITTED"]:
            items.append({**t, "_type": "table", "_id": t.get("binding_id", ""), "name": t.get("table_fqn", "—")})
    except APIError:
        pass

    try:
        collections = client.list_collections()
        for c in [c for c in collections if c.get("status") == "SUBMITTED"]:
            items.append({**c, "_type": "collection", "_id": c.get("product_id", ""), "name": c.get("name", "—")})
    except APIError:
        pass

    st.session_state["_drafts_items"] = items
    return items


# ── Page ──────────────────────────────────────────────────────────────────────

st.title(":material/approval: Review & Aprovar")
st.caption("Fila unificada de itens aguardando aprovação.")
st.divider()

role = get_user_role()
can_approve = role in ("ADMIN", "RULE_APPROVER")

items = _load_pending()

# ── Filters ───────────────────────────────────────────────────────────────────
f1, f2 = st.columns([3, 2])
search = f1.text_input("Pesquisar", placeholder="Nome do item...", label_visibility="collapsed")
type_filter = f2.multiselect(
    "Tipo", ["Regra", "Tabela Monitorada", "Collection"],
    placeholder="Filtrar por tipo", label_visibility="collapsed"
)

_type_reverse = {"Regra": "rule", "Tabela Monitorada": "table", "Collection": "collection"}
filtered = items
if search:
    filtered = [i for i in filtered if search.lower() in i.get("name", "").lower()]
if type_filter:
    type_codes = [_type_reverse[t] for t in type_filter]
    filtered = [i for i in filtered if i["_type"] in type_codes]

if col := st.columns(1)[0]:
    col.caption(f"**{len(filtered)}** item(s) aguardando aprovação")

if st.button(":material/refresh: Atualizar fila"):
    st.session_state.pop("_drafts_items", None)
    st.rerun()

st.divider()

if not filtered:
    st.success("Nenhum item pendente de aprovação.", icon=":material/check_circle:")
else:
    for item in filtered:
        entity_type = item["_type"]
        entity_id = item["_id"]
        name = item.get("name", "—")
        status = item.get("status", "SUBMITTED")
        created = item.get("created_at", "—")
        severity = item.get("severity")

        with st.container(border=True):
            header_cols = st.columns([1, 5, 2, 2])
            header_cols[0].markdown(_TYPE_ICON.get(entity_type, ""))
            header_cols[1].markdown(f"**{name}**")
            header_cols[1].caption(
                f"{_TYPE_LABEL[entity_type]}"
                + (f" · Severidade: **{severity}**" if severity else "")
                + f" · Criado: {created}"
            )
            header_cols[2].markdown(_badge(status, _STATUS_COLOR))

            if can_approve:
                with header_cols[3]:
                    with st.container(horizontal=True):
                        if st.button(":material/check_circle:", key=f"app_{entity_id}", help="Aprovar"):
                            _action_dialog("approve", item)
                        if st.button(":material/cancel:", key=f"rej_{entity_id}", help="Rejeitar"):
                            _action_dialog("reject", item)
                        if st.button(":material/diff:", key=f"diff_{entity_id}", help="Ver alterações"):
                            _diff_dialog(item)
            else:
                header_cols[3].caption(":material/lock: sem permissão")
                if header_cols[3].button(":material/diff:", key=f"diff_{entity_id}", help="Ver alterações"):
                    _diff_dialog(item)

if not can_approve:
    st.info("Você não tem permissão para aprovar ou rejeitar itens. Apenas ADMIN e RULE_APPROVER podem realizar essa ação.", icon=":material/info:")
