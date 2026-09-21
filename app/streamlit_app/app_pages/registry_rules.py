"""
Registry de Regras — listagem, detalhe, criação, edição,
fluxo de aprovação e histórico de versões.

View routing via st.session_state["rr_view"]:
  "list"   → tabela de regras com filtros e bulk actions
  "detail" → detalhe de uma regra (tabs: Detalhes, Versões, Comentários)
  "create" → formulário de criação (DQX Native ou SQL)
"""

import pandas as pd
import streamlit as st

from core.api_client import APIError
from core.session import get_client, get_user_role, is_admin

# ── Constantes ────────────────────────────────────────────────────────────────

_STATUS_COLOR = {
    "DRAFT": "gray",
    "SUBMITTED": "blue",
    "APPROVED": "green",
    "REJECTED": "red",
    "DEPRECATED": "orange",
    "REVOKED": "orange",
}
_SEVERITY_COLOR = {
    "CRITICAL": "red",
    "HIGH": "orange",
    "MEDIUM": "yellow",
    "LOW": "gray",
}
_SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
_STATUSES = ["DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "DEPRECATED"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _badge(text: str, color_map: dict) -> str:
    color = color_map.get(text, "gray")
    return f":{color}[{text}]"


def _load_rules() -> list:
    if "_rr_rules" not in st.session_state:
        try:
            st.session_state["_rr_rules"] = get_client().list_registry_rules()
        except APIError as e:
            st.error(str(e), icon=":material/error:")
            st.session_state["_rr_rules"] = []
    return st.session_state["_rr_rules"]


def _invalidate():
    st.session_state.pop("_rr_rules", None)
    # Clear any cached detail
    for key in list(st.session_state.keys()):
        if key.startswith("_rr_detail_"):
            del st.session_state[key]


def _go(view: str, rule_id: str = None):
    st.session_state["rr_view"] = view
    if rule_id is not None:
        st.session_state["rr_selected_id"] = rule_id
    st.rerun()


# ── Lifecycle dialog ──────────────────────────────────────────────────────────

@st.dialog("Confirmar ação")
def _lifecycle_dialog(action: str, rule_id: str):
    _labels = {
        "submit":      "Enviar para aprovação",
        "approve":     "Aprovar regra",
        "reject":      "Rejeitar regra",
        "revoke":      "Revogar submissão",
        "deprecate":   "Deprecar regra",
        "undeprecate": "Remover deprecação",
        "delete":      "Excluir regra permanentemente",
    }
    st.subheader(_labels.get(action, action))

    needs_rationale = action in ("approve", "reject")
    rationale = ""
    if needs_rationale:
        rationale = st.text_area("Motivo (obrigatório):")

    col1, col2 = st.columns(2)
    if col1.button("Confirmar", type="primary"):
        if needs_rationale and not rationale.strip():
            st.warning("Insira o motivo antes de confirmar.")
            return

        client = get_client()
        try:
            if action == "submit":
                client.submit_registry_rule(rule_id)
            elif action == "approve":
                client.approve_registry_rule(rule_id, rationale)
            elif action == "reject":
                client.reject_registry_rule(rule_id, rationale)
            elif action == "revoke":
                client.post(f"/registry-rules/{rule_id}/revoke")
            elif action == "deprecate":
                client.deprecate_registry_rule(rule_id)
            elif action == "undeprecate":
                client.post(f"/registry-rules/{rule_id}/undeprecate")
            elif action == "delete":
                client.delete_registry_rule(rule_id)
                _invalidate()
                st.session_state["rr_view"] = "list"
        except APIError as e:
            st.error(str(e))
            return

        _invalidate()
        st.rerun()

    if col2.button("Cancelar"):
        st.rerun()


# ── LIST VIEW ─────────────────────────────────────────────────────────────────

def _show_list():
    col_title, col_btn = st.columns([6, 1])
    col_title.title(":material/rule: Registry de Regras")
    if col_btn.button("+ Nova regra", type="primary"):
        _go("create")

    st.divider()

    rules = _load_rules()

    # Filters
    f1, f2, f3 = st.columns([3, 2, 2])
    search = f1.text_input(
        "Pesquisar",
        placeholder="Nome da regra...",
        label_visibility="collapsed",
    )
    status_filter = f2.multiselect(
        "Status",
        _STATUSES,
        placeholder="Filtrar por status",
        label_visibility="collapsed",
    )
    severity_filter = f3.multiselect(
        "Severidade",
        _SEVERITIES,
        placeholder="Filtrar por severidade",
        label_visibility="collapsed",
    )

    # Apply filters
    filtered = rules
    if search:
        filtered = [r for r in filtered if search.lower() in r.get("name", "").lower()]
    if status_filter:
        filtered = [r for r in filtered if r.get("status") in status_filter]
    if severity_filter:
        filtered = [r for r in filtered if r.get("severity") in severity_filter]

    st.caption(f"{len(filtered)} regra(s) encontrada(s)")

    if not filtered:
        st.info("Nenhuma regra encontrada com os filtros aplicados.", icon=":material/search_off:")
        return

    # Table
    df = pd.DataFrame([
        {
            "Nome": r.get("name", ""),
            "Status": r.get("status", ""),
            "Severidade": r.get("severity", ""),
            "Descrição": r.get("description", ""),
            "Criado em": r.get("created_at", ""),
        }
        for r in filtered
    ])

    event = st.dataframe(
        df,
        selection_mode="multi-row",
        on_select="rerun",
        key="rr_table",
        column_config={
            "Nome": st.column_config.TextColumn(width="medium"),
            "Status": st.column_config.TextColumn(width="small"),
            "Severidade": st.column_config.TextColumn(width="small"),
            "Descrição": st.column_config.TextColumn(width="large"),
            "Criado em": st.column_config.TextColumn(width="small"),
        },
    )

    selected_idx = event.selection.rows
    selected = [filtered[i] for i in selected_idx] if selected_idx else []

    # Action bar
    if not selected:
        return

    st.markdown(f"**{len(selected)} selecionada(s)**")
    role = get_user_role()

    with st.container(horizontal=True):
        if len(selected) == 1:
            if st.button(":material/open_in_new: Abrir"):
                _go("detail", selected[0].get("id"))

        if st.button(":material/send: Submeter"):
            for r in selected:
                try:
                    get_client().submit_registry_rule(r["id"])
                except APIError:
                    pass
            _invalidate()
            st.rerun()

        if role in ("ADMIN", "RULE_APPROVER"):
            if st.button(":material/check_circle: Aprovar"):
                for r in selected:
                    try:
                        get_client().approve_registry_rule(r["id"])
                    except APIError:
                        pass
                _invalidate()
                st.rerun()

            if st.button(":material/cancel: Rejeitar"):
                for r in selected:
                    try:
                        get_client().reject_registry_rule(r["id"])
                    except APIError:
                        pass
                _invalidate()
                st.rerun()

        if is_admin():
            if st.button(":material/archive: Deprecar"):
                for r in selected:
                    try:
                        get_client().deprecate_registry_rule(r["id"])
                    except APIError:
                        pass
                _invalidate()
                st.rerun()

            if st.button(":material/delete: Excluir"):
                for r in selected:
                    try:
                        get_client().delete_registry_rule(r["id"])
                    except APIError:
                        pass
                _invalidate()
                st.rerun()


# ── DETAIL VIEW ───────────────────────────────────────────────────────────────

def _show_detail():
    rule_id = st.session_state.get("rr_selected_id")

    if st.button(":material/arrow_back: Voltar à lista"):
        _go("list")

    # Load rule (cached per rule_id)
    cache_key = f"_rr_detail_{rule_id}"
    if cache_key not in st.session_state:
        try:
            st.session_state[cache_key] = get_client().get_registry_rule(rule_id)
        except APIError as e:
            st.error(str(e), icon=":material/error:")
            return
    rule = st.session_state[cache_key]

    status = rule.get("status", "DRAFT")
    severity = rule.get("severity", "HIGH")
    role = get_user_role()
    editable = status == "DRAFT"

    # Header
    st.title(f":material/rule: {rule.get('name', rule_id)}")
    st.markdown(
        f"{_badge(status, _STATUS_COLOR)} &nbsp;&nbsp; {_badge(severity, _SEVERITY_COLOR)}"
    )

    # Lifecycle actions
    with st.container(horizontal=True):
        if status == "DRAFT":
            if st.button(":material/send: Submeter", type="primary"):
                _lifecycle_dialog("submit", rule_id)

        if status == "SUBMITTED" and role in ("ADMIN", "RULE_APPROVER"):
            if st.button(":material/check_circle: Aprovar", type="primary"):
                _lifecycle_dialog("approve", rule_id)
            if st.button(":material/cancel: Rejeitar"):
                _lifecycle_dialog("reject", rule_id)
            if st.button(":material/undo: Revogar"):
                _lifecycle_dialog("revoke", rule_id)

        if status == "APPROVED" and is_admin():
            if st.button(":material/archive: Deprecar"):
                _lifecycle_dialog("deprecate", rule_id)

        if status == "DEPRECATED" and is_admin():
            if st.button(":material/unarchive: Remover deprecação"):
                _lifecycle_dialog("undeprecate", rule_id)

        if is_admin():
            if st.button(":material/delete: Excluir"):
                _lifecycle_dialog("delete", rule_id)

    st.divider()

    # Tabs
    tab_det, tab_ver, tab_com = st.tabs([
        ":material/info: Detalhes",
        ":material/history: Versões",
        ":material/chat: Comentários",
    ])

    # ── Tab: Detalhes ──────────────────────────────────────────────────────────
    with tab_det:
        with st.form("form_detail"):
            name = st.text_input(
                "Nome", value=rule.get("name", ""), disabled=not editable
            )
            description = st.text_area(
                "Descrição", value=rule.get("description", ""), disabled=not editable
            )
            sev_idx = _SEVERITIES.index(severity) if severity in _SEVERITIES else 1
            new_severity = st.selectbox(
                "Severidade", _SEVERITIES, index=sev_idx, disabled=not editable
            )

            if rule.get("check_function"):
                st.text_input("Função de verificação", value=rule["check_function"], disabled=True)
            if rule.get("column"):
                st.text_input("Coluna", value=rule["column"], disabled=True)
            if rule.get("sql"):
                st.code(rule["sql"], language="sql")

            if editable:
                if st.form_submit_button("Salvar rascunho", type="primary"):
                    try:
                        get_client().update_registry_rule(rule_id, {
                            "name": name,
                            "description": description,
                            "severity": new_severity,
                        })
                        st.session_state.pop(cache_key, None)
                        _invalidate()
                        st.success("Regra atualizada.")
                        st.rerun()
                    except APIError as e:
                        st.error(str(e))
            else:
                st.form_submit_button("Edição desabilitada", disabled=True)
                st.caption(f"Regra em status **{status}**. Somente rascunhos podem ser editados.")

    # ── Tab: Versões ───────────────────────────────────────────────────────────
    with tab_ver:
        try:
            versions = get_client().get_registry_rule_versions(rule_id)
            if versions:
                df_v = pd.DataFrame([
                    {
                        "Versão": v.get("version"),
                        "Status": v.get("status"),
                        "Criado em": v.get("created_at"),
                    }
                    for v in versions
                ])
                st.dataframe(df_v, key="rr_versions_table")
            else:
                st.info("Nenhuma versão anterior registrada.")
        except APIError as e:
            st.error(str(e))

    # ── Tab: Comentários ───────────────────────────────────────────────────────
    with tab_com:
        try:
            comments = get_client().list_comments("registry_rule", rule_id)
            user_email = st.session_state.get("_dqx_auth_email", "")

            if comments:
                for c in comments:
                    with st.container(border=True):
                        c1, c2 = st.columns([8, 1])
                        c1.markdown(f"**{c.get('author', '—')}** · {c.get('created_at', '')}")
                        c1.write(c.get("text", ""))
                        can_delete = is_admin() or c.get("author") == user_email
                        if can_delete:
                            if c2.button(
                                ":material/delete:",
                                key=f"del_c_{c.get('id')}",
                                help="Excluir comentário",
                            ):
                                try:
                                    get_client().delete_comment(c["id"])
                                    st.rerun()
                                except APIError as e:
                                    st.error(str(e))
            else:
                st.info("Nenhum comentário ainda.")

            st.divider()
            with st.form("form_comment", clear_on_submit=True):
                new_text = st.text_area("Adicionar comentário:", label_visibility="collapsed",
                                        placeholder="Escreva um comentário...")
                if st.form_submit_button(":material/send: Comentar"):
                    if new_text.strip():
                        try:
                            get_client().add_comment({
                                "entity_type": "registry_rule",
                                "entity_id": rule_id,
                                "text": new_text.strip(),
                            })
                            st.rerun()
                        except APIError as e:
                            st.error(str(e))
        except APIError as e:
            st.error(str(e))


# ── CREATE VIEW ───────────────────────────────────────────────────────────────

def _show_create():
    if st.button(":material/arrow_back: Voltar à lista"):
        _go("list")

    st.title(":material/add: Nova Regra")
    st.divider()

    mode = st.segmented_control(
        "Modo de criação",
        ["DQX Native", "SQL"],
        default="DQX Native",
    )

    with st.form("form_create"):
        name = st.text_input("Nome da regra *", placeholder="ex: not_null_customer_id")
        description = st.text_area("Descrição", placeholder="Descreva o objetivo desta regra")
        severity = st.selectbox("Severidade *", _SEVERITIES, index=1)

        st.divider()

        sql_expr = None
        selected_fn = None
        column = None
        params_raw = None

        if mode == "DQX Native":
            if "_check_functions" not in st.session_state:
                try:
                    st.session_state["_check_functions"] = get_client().list_check_functions()
                except APIError:
                    st.session_state["_check_functions"] = []

            fns = st.session_state["_check_functions"]
            fn_names = [f["name"] for f in fns]
            fn_desc = {f["name"]: f.get("description", "") for f in fns}

            selected_fn = st.selectbox("Função de verificação *", fn_names)
            if selected_fn:
                st.caption(fn_desc.get(selected_fn, ""))

            column = st.text_input("Coluna", placeholder="ex: customer_id")
            params_raw = st.text_area(
                "Parâmetros adicionais (YAML)",
                placeholder="min: 0\nmax: 1000",
            )

        else:
            sql_expr = st.text_area(
                "SQL *",
                height=160,
                placeholder="SELECT * FROM {table} WHERE customer_id IS NOT NULL",
            )

        submitted = st.form_submit_button("Salvar como rascunho", type="primary")

    if submitted:
        errors = []
        if not name.strip():
            errors.append("Nome é obrigatório.")
        if mode == "DQX Native" and not selected_fn:
            errors.append("Selecione uma função de verificação.")
        if mode == "SQL" and not (sql_expr or "").strip():
            errors.append("SQL é obrigatório.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            payload = {
                "name": name.strip(),
                "description": description.strip(),
                "severity": severity,
                "status": "DRAFT",
            }
            if mode == "DQX Native":
                payload["check_function"] = selected_fn
                if column:
                    payload["column"] = column
                if params_raw:
                    payload["params_yaml"] = params_raw
            else:
                payload["sql"] = sql_expr.strip()

            try:
                created = get_client().create_registry_rule(payload)
                _invalidate()
                st.success(f"Regra **{name}** criada como rascunho!")
                rule_id = created.get("id")
                if rule_id:
                    _go("detail", rule_id)
                else:
                    _go("list")
            except APIError as e:
                st.error(str(e))


# ── Router ────────────────────────────────────────────────────────────────────

_view = st.session_state.get("rr_view", "list")

if _view == "list":
    _show_list()
elif _view == "detail":
    _show_detail()
elif _view == "create":
    _show_create()
else:
    st.session_state["rr_view"] = "list"
    st.rerun()
