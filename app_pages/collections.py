"""
Collections (Data Products) — CRUD, agrupamento de tabelas monitoradas,
agendamentos e monitoramento de execuções.

View routing via st.session_state["col_view"]:
  "list"   → listagem de collections
  "detail" → detalhe (tabs: Tabelas, Execuções, Agendamento, Histórico, Comentários)
  "new"    → criar nova collection
  "edit"   → editar nome/descrição
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
}
_STATUSES = ["DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "DEPRECATED"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _badge(text: str, color_map: dict) -> str:
    color = color_map.get(text, "gray")
    return f":{color}[{text}]"


def _load_collections() -> list:
    if "_col_list" not in st.session_state:
        try:
            st.session_state["_col_list"] = get_client().list_collections()
        except APIError as e:
            st.error(str(e), icon=":material/error:")
            st.session_state["_col_list"] = []
    return st.session_state["_col_list"]


def _invalidate():
    st.session_state.pop("_col_list", None)
    for k in list(st.session_state.keys()):
        if k.startswith("_col_detail_"):
            del st.session_state[k]


def _go(view: str, product_id: str = None):
    st.session_state["col_view"] = view
    if product_id is not None:
        st.session_state["col_selected_id"] = product_id
    st.rerun()


# ── Lifecycle dialog ──────────────────────────────────────────────────────────

@st.dialog("Confirmar ação")
def _lifecycle_dialog(action: str, product_id: str):
    _labels = {
        "submit":  "Enviar collection para aprovação",
        "approve": "Aprovar collection",
        "reject":  "Rejeitar collection",
        "revert":  "Reverter para rascunho",
        "delete":  "Excluir collection",
    }
    st.subheader(_labels.get(action, action))

    rationale = ""
    if action in ("approve", "reject"):
        rationale = st.text_area("Motivo (obrigatório):")

    col1, col2 = st.columns(2)
    if col1.button("Confirmar", type="primary"):
        if action in ("approve", "reject") and not rationale.strip():
            st.warning("Insira o motivo antes de confirmar.")
            return

        client = get_client()
        try:
            if action == "submit":
                client.submit_collection(product_id)
            elif action == "approve":
                client.approve_collection(product_id, rationale)
            elif action == "reject":
                client.reject_collection(product_id, rationale)
            elif action == "revert":
                client.revert_collection(product_id)
            elif action == "delete":
                client.delete_collection(product_id)
                _invalidate()
                st.session_state["col_view"] = "list"
        except APIError as e:
            st.error(str(e))
            return

        _invalidate()
        st.rerun()

    if col2.button("Cancelar"):
        st.rerun()


# ── Permissions tab ───────────────────────────────────────────────────────────

def _permissions_tab(object_type: str, object_id: str):
    _PERMISSIONS = ["VIEW", "MODIFY", "APPLY", "EXECUTE"]
    client = get_client()

    try:
        grants = client.list_object_grants(object_type, object_id)
    except APIError as e:
        st.error(str(e)); return

    st.subheader("Permissões de acesso")
    if grants:
        for g in grants:
            with st.container(border=True):
                c1, c2, c3 = st.columns([5, 3, 1])
                c1.markdown(f"**{g.get('principal', '—')}**")
                c1.caption(f"Concedido por: {g.get('granted_by', '—')}")
                c2.markdown(f"`{g.get('permission', '—')}`")
                if is_admin() and c3.button(":material/delete:", key=f"rm_grant_{object_id}_{g.get('principal')}"):
                    try:
                        client.remove_object_grant(object_type, object_id, g["principal"])
                        st.rerun()
                    except APIError as e:
                        st.error(str(e))
    else:
        st.info("Nenhuma permissão específica definida. Acesso herdado das configurações globais.", icon=":material/info:")

    if is_admin():
        st.divider()
        st.subheader("Adicionar permissão")
        with st.form(f"form_grant_{object_id}"):
            principal = st.text_input("Principal (e-mail ou grupo)", placeholder="user@company.com ou nome-do-grupo")
            permission = st.selectbox("Permissão", _PERMISSIONS)
            if st.form_submit_button("Adicionar", type="primary"):
                if principal.strip():
                    try:
                        client.add_object_grant(object_type, object_id, {"principal": principal.strip(), "permission": permission})
                        st.success(f"Permissão **{permission}** concedida a **{principal.strip()}**.")
                        st.rerun()
                    except APIError as e:
                        st.error(str(e))
                else:
                    st.warning("Informe o principal.")


# ── LIST VIEW ─────────────────────────────────────────────────────────────────

def _show_list():
    col_title, col_btn = st.columns([6, 1])
    col_title.title(":material/folder_open: Collections")
    if col_btn.button("+ Nova", type="primary"):
        _go("new")

    st.divider()

    collections = _load_collections()

    f1, f2 = st.columns([3, 2])
    search = f1.text_input(
        "Pesquisar", placeholder="Nome da collection...", label_visibility="collapsed"
    )
    status_filter = f2.multiselect(
        "Status", _STATUSES, placeholder="Filtrar por status", label_visibility="collapsed"
    )

    filtered = collections
    if search:
        filtered = [c for c in filtered if search.lower() in c.get("name", "").lower()]
    if status_filter:
        filtered = [c for c in filtered if c.get("status") in status_filter]

    st.caption(f"{len(filtered)} collection(s) encontrada(s)")

    if not filtered:
        st.info("Nenhuma collection encontrada.", icon=":material/search_off:")
        return

    df = pd.DataFrame([
        {
            "Nome": c.get("name", ""),
            "Status": c.get("status", ""),
            "DQ Score": f"{c['dq_score']:.1f}%" if c.get("dq_score") is not None else "—",
            "Tabelas": c.get("table_count", "—"),
            "Último run": c.get("last_run", "—"),
        }
        for c in filtered
    ])

    event = st.dataframe(
        df,
        selection_mode="multi-row",
        on_select="rerun",
        key="col_table",
        column_config={
            "Nome": st.column_config.TextColumn(width="large"),
            "Status": st.column_config.TextColumn(width="small"),
            "DQ Score": st.column_config.TextColumn(width="small"),
            "Tabelas": st.column_config.TextColumn(width="small"),
            "Último run": st.column_config.TextColumn(width="small"),
        },
    )

    selected_idx = event.selection.rows
    selected = [filtered[i] for i in selected_idx] if selected_idx else []

    if not selected:
        return

    st.markdown(f"**{len(selected)} selecionada(s)**")
    role = get_user_role()

    with st.container(horizontal=True):
        if len(selected) == 1:
            if st.button(":material/open_in_new: Abrir"):
                _go("detail", selected[0].get("product_id"))
            if st.button(":material/edit: Editar"):
                _go("edit", selected[0].get("product_id"))

        if st.button(":material/play_arrow: Executar"):
            for c in selected:
                try:
                    get_client().run_collection(c["product_id"])
                except APIError:
                    pass
            st.toast("Execução iniciada!", icon=":material/rocket_launch:")
            _invalidate()
            st.rerun()

        if st.button(":material/send: Submeter"):
            for c in selected:
                try:
                    get_client().submit_collection(c["product_id"])
                except APIError:
                    pass
            _invalidate()
            st.rerun()

        if role in ("ADMIN", "RULE_APPROVER"):
            if st.button(":material/check_circle: Aprovar"):
                for c in selected:
                    try:
                        get_client().approve_collection(c["product_id"])
                    except APIError:
                        pass
                _invalidate()
                st.rerun()

            if st.button(":material/cancel: Rejeitar"):
                for c in selected:
                    try:
                        get_client().reject_collection(c["product_id"])
                    except APIError:
                        pass
                _invalidate()
                st.rerun()

        if is_admin():
            if st.button(":material/delete: Excluir"):
                for c in selected:
                    try:
                        get_client().delete_collection(c["product_id"])
                    except APIError:
                        pass
                _invalidate()
                st.rerun()


# ── NEW / EDIT VIEW ───────────────────────────────────────────────────────────

def _show_form(product_id: str = None):
    is_edit = product_id is not None
    title = ":material/edit: Editar Collection" if is_edit else ":material/add: Nova Collection"

    if st.button(":material/arrow_back: Voltar"):
        _go("list")

    st.title(title)
    st.divider()

    # Carregar dados existentes se editar
    current = {}
    if is_edit:
        cache_key = f"_col_detail_{product_id}"
        if cache_key not in st.session_state:
            try:
                st.session_state[cache_key] = get_client().get_collection(product_id)
            except APIError as e:
                st.error(str(e))
                return
        current = st.session_state[cache_key]

    with st.form("form_collection"):
        name = st.text_input("Nome da Collection", value=current.get("name", ""), placeholder="ex: Sales Data Product")
        description = st.text_area(
            "Descrição",
            value=current.get("description", ""),
            placeholder="Descreva o objetivo desta collection...",
        )

        submitted = st.form_submit_button("Salvar", type="primary")

    if submitted:
        if not name.strip():
            st.warning("Nome é obrigatório.")
            return

        payload = {"name": name.strip(), "description": description.strip()}
        try:
            if is_edit:
                get_client().update_collection(product_id, payload)
                st.session_state.pop(f"_col_detail_{product_id}", None)
                _invalidate()
                st.success("Collection atualizada!")
                _go("detail", product_id)
            else:
                result = get_client().create_collection(payload)
                _invalidate()
                st.success(f"Collection **{name}** criada!")
                new_id = result.get("product_id")
                _go("detail", new_id) if new_id else _go("list")
        except APIError as e:
            st.error(str(e))


# ── DETAIL VIEW ───────────────────────────────────────────────────────────────

def _show_detail():
    product_id = st.session_state.get("col_selected_id")

    if st.button(":material/arrow_back: Voltar à lista"):
        _go("list")

    cache_key = f"_col_detail_{product_id}"
    if cache_key not in st.session_state:
        try:
            st.session_state[cache_key] = get_client().get_collection(product_id)
        except APIError as e:
            st.error(str(e), icon=":material/error:")
            return
    col = st.session_state[cache_key]

    name = col.get("name", product_id)
    status = col.get("status", "DRAFT")
    role = get_user_role()

    # ── Header ────────────────────────────────────────────────────────────────
    h1, h2 = st.columns([8, 1])
    h1.title(f":material/folder_open: {name}")
    if h2.button(":material/edit: Editar"):
        _go("edit", product_id)

    score = col.get("dq_score")
    score_str = f"{score:.1f}%" if score is not None else "—"
    desc = col.get("description", "")
    st.markdown(f"{_badge(status, _STATUS_COLOR)} &nbsp;&nbsp; **DQ Score:** {score_str}")
    if desc:
        st.caption(desc)

    # ── Lifecycle actions ─────────────────────────────────────────────────────
    with st.container(horizontal=True):
        if st.button(":material/play_arrow: Executar agora", type="primary"):
            try:
                result = get_client().run_collection(product_id)
                run_id = result.get("run_id")
                st.session_state["_col_active_run"] = run_id
                st.toast(f"Run `{run_id}` iniciada!", icon=":material/rocket_launch:")
                st.session_state.pop(cache_key, None)
                st.rerun()
            except APIError as e:
                st.error(str(e))

        if status == "DRAFT":
            if st.button(":material/send: Submeter"):
                _lifecycle_dialog("submit", product_id)
        if status == "SUBMITTED" and role in ("ADMIN", "RULE_APPROVER"):
            if st.button(":material/check_circle: Aprovar"):
                _lifecycle_dialog("approve", product_id)
            if st.button(":material/cancel: Rejeitar"):
                _lifecycle_dialog("reject", product_id)
        if status in ("SUBMITTED", "APPROVED") and is_admin():
            if st.button(":material/undo: Reverter"):
                _lifecycle_dialog("revert", product_id)
        if is_admin():
            if st.button(":material/delete: Excluir"):
                _lifecycle_dialog("delete", product_id)

    st.divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_tables, tab_runs, tab_sched, tab_hist, tab_perm, tab_com = st.tabs([
        ":material/table_chart: Tabelas",
        ":material/play_circle: Execuções",
        ":material/schedule: Agendamento",
        ":material/history: Histórico",
        ":material/lock: Permissões",
        ":material/chat: Comentários",
    ])

    # ── Tab: Tabelas (Agrupamento) ─────────────────────────────────────────────
    with tab_tables:
        st.subheader("Tabelas agrupadas nesta collection")

        try:
            tables = get_client().list_collection_tables(product_id)

            if tables:
                for t in tables:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([6, 2, 1])
                        c1.markdown(f"**{t.get('table_fqn', t.get('binding_id'))}**")
                        score_t = t.get("dq_score")
                        c2.metric(
                            "DQ Score",
                            f"{score_t:.1f}%" if score_t is not None else "—",
                            label_visibility="collapsed",
                        )
                        c2.caption(f"Status: {t.get('status', '—')}")
                        if c3.button(":material/delete:", key=f"rm_t_{t.get('binding_id')}", help="Remover da collection"):
                            try:
                                get_client().remove_table_from_collection(product_id, t["binding_id"])
                                st.session_state.pop(cache_key, None)
                                _invalidate()
                                st.rerun()
                            except APIError as e:
                                st.error(str(e))
            else:
                st.info("Nenhuma tabela agrupada ainda.", icon=":material/info:")

        except APIError as e:
            st.error(str(e))

        st.divider()
        st.subheader("Adicionar tabela monitorada")

        try:
            all_monitored = get_client().list_monitored_tables()
            already_ids = {t.get("binding_id") for t in tables} if tables else set()
            available = [t for t in all_monitored if t.get("binding_id") not in already_ids]

            if available:
                table_options = {t["table_fqn"]: t["binding_id"] for t in available}
                selected_fqn = st.selectbox(
                    "Selecionar tabela",
                    list(table_options.keys()),
                    label_visibility="collapsed",
                    placeholder="Escolha uma tabela monitorada...",
                )
                if st.button(":material/add: Adicionar tabela", type="primary"):
                    try:
                        get_client().add_table_to_collection(product_id, table_options[selected_fqn])
                        st.session_state.pop(cache_key, None)
                        _invalidate()
                        st.success(f"Tabela **{selected_fqn}** adicionada!")
                        st.rerun()
                    except APIError as e:
                        st.error(str(e))
            else:
                st.caption("Todas as tabelas monitoradas já estão nesta collection.")

        except APIError as e:
            st.error(str(e))

    # ── Tab: Execuções ────────────────────────────────────────────────────────
    with tab_runs:
        active_run_id = st.session_state.get("_col_active_run")

        if active_run_id:
            @st.fragment(run_every=5)
            def _poll_run():
                try:
                    status_data = get_client().get_run_status(active_run_id)
                    run_status = status_data.get("status", "UNKNOWN")
                    if run_status in ("RUNNING", "PENDING"):
                        st.status(f"Run `{active_run_id}` em execução...", state="running")
                    elif run_status == "SUCCEEDED":
                        st.success(f"Run `{active_run_id}` concluída!")
                        st.session_state.pop("_col_active_run", None)
                        _invalidate()
                    else:
                        st.error(f"Run `{active_run_id}` falhou: {run_status}")
                        st.session_state.pop("_col_active_run", None)
                except APIError as e:
                    st.error(str(e))

            _poll_run()
            st.divider()

        try:
            runs = get_client().list_collection_runs(product_id)
            if runs:
                df_runs = pd.DataFrame([
                    {
                        "Run ID": r.get("run_id", ""),
                        "Status": r.get("status", ""),
                        "Iniciado em": r.get("started_at", ""),
                        "DQ Score": f"{r['dq_score']:.1f}%" if r.get("dq_score") is not None else "—",
                        "Aprovados": r.get("checks_passed", "—"),
                        "Falhas": r.get("checks_failed", "—"),
                    }
                    for r in runs
                ])
                st.dataframe(df_runs, key="col_runs_table")
            else:
                st.info("Nenhuma execução registrada.", icon=":material/info:")
        except APIError as e:
            st.error(str(e))

    # ── Tab: Agendamento ──────────────────────────────────────────────────────
    with tab_sched:
        st.subheader("Agendamento de execução da collection")
        current_cron = col.get("schedule", "")

        with st.form("form_col_schedule"):
            cron = st.text_input(
                "Expressão Cron",
                value=current_cron,
                placeholder="ex: 0 7 * * 1 (toda segunda às 7h)",
            )
            st.caption("Formato: minuto hora dia-do-mês mês dia-da-semana")

            c1, c2 = st.columns(2)
            save = c1.form_submit_button("Salvar agendamento", type="primary")
            clear = c2.form_submit_button("Remover agendamento")

        if save:
            try:
                get_client().update_collection_schedule(product_id, {"cron": cron})
                st.session_state.pop(cache_key, None)
                st.success("Agendamento salvo!")
                st.rerun()
            except APIError as e:
                st.error(str(e))

        if clear:
            try:
                get_client().update_collection_schedule(product_id, {"cron": ""})
                st.session_state.pop(cache_key, None)
                st.success("Agendamento removido.")
                st.rerun()
            except APIError as e:
                st.error(str(e))

    # ── Tab: Histórico ────────────────────────────────────────────────────────
    with tab_hist:
        try:
            versions = get_client().list_collection_versions(product_id)
            if versions:
                df_v = pd.DataFrame([
                    {
                        "Versão": v.get("version"),
                        "Status": v.get("status"),
                        "Tabelas": v.get("table_count", "—"),
                        "Criado em": v.get("created_at"),
                    }
                    for v in versions
                ])
                st.dataframe(df_v, key="col_versions_table")
            else:
                st.info("Nenhuma versão anterior registrada.")
        except APIError as e:
            st.error(str(e))

    # ── Tab: Permissões ───────────────────────────────────────────────────────
    with tab_perm:
        _permissions_tab("data_product", product_id)

    # ── Tab: Comentários ──────────────────────────────────────────────────────
    with tab_com:
        user_email = st.session_state.get("_dqx_auth_email", "")
        try:
            comments = get_client().list_comments("data_product", product_id)

            if comments:
                for c in comments:
                    with st.container(border=True):
                        c1, c2 = st.columns([8, 1])
                        c1.markdown(f"**{c.get('author', '—')}** · {c.get('created_at', '')}")
                        c1.write(c.get("text", ""))
                        can_delete = is_admin() or c.get("author") == user_email
                        if can_delete and c2.button(":material/delete:", key=f"del_cc_{c.get('id')}"):
                            try:
                                get_client().delete_comment(c["id"])
                                st.rerun()
                            except APIError as e:
                                st.error(str(e))
            else:
                st.info("Nenhum comentário ainda.")

            st.divider()
            with st.form("form_col_comment", clear_on_submit=True):
                new_text = st.text_area(
                    "Comentário", label_visibility="collapsed", placeholder="Escreva um comentário..."
                )
                if st.form_submit_button(":material/send: Comentar"):
                    if new_text.strip():
                        try:
                            get_client().add_comment({
                                "entity_type": "data_product",
                                "entity_id": product_id,
                                "text": new_text.strip(),
                            })
                            st.rerun()
                        except APIError as e:
                            st.error(str(e))

        except APIError as e:
            st.error(str(e))


# ── Router ────────────────────────────────────────────────────────────────────

_view = st.session_state.get("col_view", "list")

if _view == "list":
    _show_list()
elif _view == "detail":
    _show_detail()
elif _view == "new":
    _show_form()
elif _view == "edit":
    _show_form(product_id=st.session_state.get("col_selected_id"))
else:
    st.session_state["col_view"] = "list"
    st.rerun()
