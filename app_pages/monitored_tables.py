"""
Tabelas Monitoradas — bindings tabela × regra, aplicação de regras,
execução de validações e monitoramento de execuções.

View routing via st.session_state["mt_view"]:
  "list"   → listagem de tabelas monitoradas
  "detail" → detalhe (tabs: Regras, Resultados, Execuções, Agendamento, Histórico, Comentários)
  "new"    → registrar nova tabela (Catalog Browser)
"""

import pandas as pd
import streamlit as st

from core.api_client import APIError
from core.catalog_browser import catalog_browser
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
_STATUSES = ["DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "DEPRECATED"]
_RUN_STATUS_COLOR = {
    "SUCCEEDED": "green",
    "FAILED": "red",
    "RUNNING": "blue",
    "PENDING": "blue",
    "CANCELLED": "gray",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _badge(text: str, color_map: dict) -> str:
    color = color_map.get(text, "gray")
    return f":{color}[{text}]"


def _load_tables() -> list:
    if "_mt_tables" not in st.session_state:
        try:
            st.session_state["_mt_tables"] = get_client().list_monitored_tables()
        except APIError as e:
            st.error(str(e), icon=":material/error:")
            st.session_state["_mt_tables"] = []
    return st.session_state["_mt_tables"]


def _invalidate():
    st.session_state.pop("_mt_tables", None)
    for k in list(st.session_state.keys()):
        if k.startswith("_mt_detail_"):
            del st.session_state[k]


def _go(view: str, binding_id: str = None):
    st.session_state["mt_view"] = view
    if binding_id is not None:
        st.session_state["mt_selected_id"] = binding_id
    st.rerun()


# ── Lifecycle dialog ──────────────────────────────────────────────────────────

@st.dialog("Confirmar ação")
def _lifecycle_dialog(action: str, binding_id: str):
    _labels = {
        "submit":  "Enviar para aprovação",
        "approve": "Aprovar tabela monitorada",
        "reject":  "Rejeitar tabela monitorada",
        "revert":  "Reverter para rascunho",
        "delete":  "Excluir tabela monitorada",
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
                client.submit_monitored_table(binding_id)
            elif action == "approve":
                client.approve_monitored_table(binding_id, rationale)
            elif action == "reject":
                client.reject_monitored_table(binding_id, rationale)
            elif action == "revert":
                client.revert_monitored_table(binding_id)
            elif action == "delete":
                client.delete_monitored_table(binding_id)
                _invalidate()
                st.session_state["mt_view"] = "list"
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
    col_title.title(":material/table_chart: Tabelas Monitoradas")
    if col_btn.button("+ Registrar", type="primary"):
        _go("new")

    st.divider()

    tables = _load_tables()

    # Filters
    f1, f2 = st.columns([3, 2])
    search = f1.text_input(
        "Pesquisar", placeholder="Nome ou FQN da tabela...", label_visibility="collapsed"
    )
    status_filter = f2.multiselect(
        "Status", _STATUSES, placeholder="Filtrar por status", label_visibility="collapsed"
    )

    filtered = tables
    if search:
        filtered = [t for t in filtered if search.lower() in t.get("table_fqn", "").lower()]
    if status_filter:
        filtered = [t for t in filtered if t.get("status") in status_filter]

    st.caption(f"{len(filtered)} tabela(s) encontrada(s)")

    if not filtered:
        st.info("Nenhuma tabela encontrada.", icon=":material/search_off:")
        return

    df = pd.DataFrame([
        {
            "Tabela (FQN)": t.get("table_fqn", ""),
            "Status": t.get("status", ""),
            "DQ Score": f"{t['dq_score']:.1f}%" if t.get("dq_score") is not None else "—",
            "Último run": t.get("last_run", "—"),
        }
        for t in filtered
    ])

    event = st.dataframe(
        df,
        selection_mode="multi-row",
        on_select="rerun",
        key="mt_table",
        column_config={
            "Tabela (FQN)": st.column_config.TextColumn(width="large"),
            "Status": st.column_config.TextColumn(width="small"),
            "DQ Score": st.column_config.TextColumn(width="small"),
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
                _go("detail", selected[0].get("binding_id"))

        if st.button(":material/play_arrow: Executar"):
            for t in selected:
                try:
                    get_client().run_monitored_table(t["binding_id"])
                except APIError:
                    pass
            st.toast("Execução iniciada!", icon=":material/rocket_launch:")
            _invalidate()
            st.rerun()

        if st.button(":material/send: Submeter"):
            for t in selected:
                try:
                    get_client().submit_monitored_table(t["binding_id"])
                except APIError:
                    pass
            _invalidate()
            st.rerun()

        if role in ("ADMIN", "RULE_APPROVER"):
            if st.button(":material/check_circle: Aprovar"):
                for t in selected:
                    try:
                        get_client().approve_monitored_table(t["binding_id"])
                    except APIError:
                        pass
                _invalidate()
                st.rerun()

            if st.button(":material/cancel: Rejeitar"):
                for t in selected:
                    try:
                        get_client().reject_monitored_table(t["binding_id"])
                    except APIError:
                        pass
                _invalidate()
                st.rerun()

        if is_admin():
            if st.button(":material/delete: Excluir"):
                for t in selected:
                    try:
                        get_client().delete_monitored_table(t["binding_id"])
                    except APIError:
                        pass
                _invalidate()
                st.rerun()


# ── NEW TABLE VIEW ────────────────────────────────────────────────────────────

def _show_new():
    if st.button(":material/arrow_back: Voltar"):
        _go("list")

    st.title(":material/add: Registrar Tabela Monitorada")
    st.caption("Selecione a tabela no Unity Catalog e confirme o registro.")
    st.divider()

    fqn = catalog_browser(key_prefix="mt_new")

    if fqn:
        st.success(f"Tabela selecionada: **{fqn}**")

    if fqn and st.button("Registrar tabela", type="primary"):
        try:
            result = get_client().create_monitored_table({"table_fqn": fqn})
            _invalidate()
            st.success(f"Tabela **{fqn}** registrada com sucesso!")
            binding_id = result.get("binding_id")
            if binding_id:
                _go("detail", binding_id)
            else:
                _go("list")
        except APIError as e:
            st.error(str(e))


# ── DETAIL VIEW ───────────────────────────────────────────────────────────────

def _show_detail():
    binding_id = st.session_state.get("mt_selected_id")

    if st.button(":material/arrow_back: Voltar à lista"):
        _go("list")

    cache_key = f"_mt_detail_{binding_id}"
    if cache_key not in st.session_state:
        try:
            st.session_state[cache_key] = get_client().get_monitored_table(binding_id)
        except APIError as e:
            st.error(str(e), icon=":material/error:")
            return
    binding = st.session_state[cache_key]

    table_fqn = binding.get("table_fqn", binding_id)
    status = binding.get("status", "DRAFT")
    role = get_user_role()

    # ── Header ────────────────────────────────────────────────────────────────
    st.title(f":material/table_chart: {table_fqn}")
    score = binding.get("dq_score")
    score_str = f"{score:.1f}%" if score is not None else "—"
    st.markdown(f"{_badge(status, _STATUS_COLOR)} &nbsp;&nbsp; **DQ Score:** {score_str}")

    # ── Lifecycle actions ─────────────────────────────────────────────────────
    with st.container(horizontal=True):
        if st.button(":material/play_arrow: Executar agora", type="primary"):
            try:
                result = get_client().run_monitored_table(binding_id)
                run_id = result.get("run_id")
                st.session_state["_mt_active_run"] = run_id
                st.toast(f"Run `{run_id}` iniciada!", icon=":material/rocket_launch:")
                st.session_state.pop(cache_key, None)
                st.rerun()
            except APIError as e:
                st.error(str(e))

        if status == "DRAFT":
            if st.button(":material/send: Submeter"):
                _lifecycle_dialog("submit", binding_id)
        if status == "SUBMITTED" and role in ("ADMIN", "RULE_APPROVER"):
            if st.button(":material/check_circle: Aprovar"):
                _lifecycle_dialog("approve", binding_id)
            if st.button(":material/cancel: Rejeitar"):
                _lifecycle_dialog("reject", binding_id)
        if status in ("SUBMITTED", "APPROVED") and is_admin():
            if st.button(":material/undo: Reverter"):
                _lifecycle_dialog("revert", binding_id)
        if is_admin():
            if st.button(":material/delete: Excluir"):
                _lifecycle_dialog("delete", binding_id)

    st.divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_rules, tab_results, tab_runs, tab_sched, tab_hist, tab_perm, tab_com = st.tabs([
        ":material/rule: Regras",
        ":material/analytics: Resultados",
        ":material/play_circle: Execuções",
        ":material/schedule: Agendamento",
        ":material/history: Histórico",
        ":material/lock: Permissões",
        ":material/chat: Comentários",
    ])

    # ── Tab: Regras Aplicadas ─────────────────────────────────────────────────
    with tab_rules:
        applied = binding.get("applied_rules", [])

        if applied:
            st.subheader("Regras associadas")
            for rule in applied:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([5, 2, 1])
                    c1.markdown(f"**{rule.get('name', rule.get('rule_id'))}**")
                    c1.caption(f"Severidade: {rule.get('severity', '—')}  ·  Status: {rule.get('status', '—')}")
                    pin = rule.get("pinned_version")
                    c2.caption(f"Pin: v{pin}" if pin else "Pin: automático")
                    if c3.button(":material/delete:", key=f"rm_{rule.get('rule_id')}", help="Remover regra"):
                        try:
                            get_client().remove_rule_from_table(binding_id, rule["rule_id"])
                            st.session_state.pop(cache_key, None)
                            _invalidate()
                            st.rerun()
                        except APIError as e:
                            st.error(str(e))
        else:
            st.info("Nenhuma regra associada a esta tabela.", icon=":material/info:")

        st.divider()
        st.subheader("Associar regra do Registry")

        try:
            all_rules = get_client().list_registry_rules(status="APPROVED")
            applied_ids = {r.get("rule_id") for r in applied}
            available = [r for r in all_rules if r.get("id") not in applied_ids]

            if available:
                rule_options = {r["name"]: r["id"] for r in available}
                selected_name = st.selectbox(
                    "Selecionar regra",
                    list(rule_options.keys()),
                    label_visibility="collapsed",
                    placeholder="Escolha uma regra aprovada...",
                )
                if st.button(":material/add: Associar regra", type="primary"):
                    try:
                        get_client().apply_rule_to_table(binding_id, rule_options[selected_name])
                        st.session_state.pop(cache_key, None)
                        _invalidate()
                        st.success(f"Regra **{selected_name}** associada!")
                        st.rerun()
                    except APIError as e:
                        st.error(str(e))
            else:
                st.caption("Todas as regras aprovadas já estão associadas.")
        except APIError as e:
            st.error(str(e))

    # ── Tab: Resultados DQ ────────────────────────────────────────────────────
    with tab_results:
        try:
            results = get_client().get_table_results(table_fqn)
            dq_score = results.get("dq_score")

            if dq_score is not None:
                col1, col2, col3 = st.columns(3)
                col1.metric("DQ Score", f"{dq_score:.1f}%")
                col2.metric("Checks aprovados", results.get("checks_passed", "—"))
                col3.metric("Checks com falha", results.get("checks_failed", "—"))
            else:
                st.info("Nenhum resultado disponível. Execute uma validação primeiro.", icon=":material/info:")

            # Breakdown por dimensão/severidade se disponível
            breakdown = results.get("breakdown")
            if breakdown:
                st.subheader("Breakdown por severidade")
                df_br = pd.DataFrame(breakdown)
                st.bar_chart(df_br, x="severity", y="count")

        except APIError as e:
            st.error(str(e))

    # ── Tab: Execuções ────────────────────────────────────────────────────────
    with tab_runs:
        # Active run polling via fragment
        active_run_id = st.session_state.get("_mt_active_run")

        if active_run_id:
            @st.fragment(run_every=5)
            def _poll_run():
                try:
                    status_data = get_client().get_run_status(active_run_id)
                    run_status = status_data.get("status", "UNKNOWN")
                    if run_status in ("RUNNING", "PENDING"):
                        st.status(f"Run `{active_run_id}` em execução...", state="running")
                    elif run_status == "SUCCEEDED":
                        st.success(f"Run `{active_run_id}` concluída com sucesso!")
                        st.session_state.pop("_mt_active_run", None)
                        _invalidate()
                    else:
                        st.error(f"Run `{active_run_id}` falhou com status: {run_status}")
                        st.session_state.pop("_mt_active_run", None)
                except APIError as e:
                    st.error(str(e))

            _poll_run()
            st.divider()

        # Run history
        try:
            runs = get_client().list_table_runs(binding_id)
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
                st.dataframe(
                    df_runs,
                    key="mt_runs_table",
                    column_config={
                        "Run ID": st.column_config.TextColumn(width="medium"),
                        "Status": st.column_config.TextColumn(width="small"),
                        "Iniciado em": st.column_config.TextColumn(width="medium"),
                        "DQ Score": st.column_config.TextColumn(width="small"),
                    },
                )
            else:
                st.info("Nenhuma execução registrada ainda.", icon=":material/info:")
        except APIError as e:
            st.error(str(e))

    # ── Tab: Agendamento ──────────────────────────────────────────────────────
    with tab_sched:
        st.subheader("Agendamento de execução")
        current_schedule = binding.get("schedule", "")

        with st.form("form_schedule"):
            cron = st.text_input(
                "Expressão Cron",
                value=current_schedule,
                placeholder="ex: 0 6 * * * (todo dia às 6h)",
            )
            st.caption("Formato: minuto hora dia-do-mês mês dia-da-semana")

            col1, col2 = st.columns(2)
            save = col1.form_submit_button("Salvar agendamento", type="primary")
            clear = col2.form_submit_button("Remover agendamento")

        if save:
            try:
                get_client().update_table_schedule(binding_id, {"cron": cron})
                st.session_state.pop(cache_key, None)
                st.success("Agendamento salvo!")
                st.rerun()
            except APIError as e:
                st.error(str(e))

        if clear:
            try:
                get_client().update_table_schedule(binding_id, {"cron": ""})
                st.session_state.pop(cache_key, None)
                st.success("Agendamento removido.")
                st.rerun()
            except APIError as e:
                st.error(str(e))

    # ── Tab: Histórico ────────────────────────────────────────────────────────
    with tab_hist:
        try:
            versions = get_client().list_table_versions(binding_id)
            if versions:
                df_v = pd.DataFrame([
                    {
                        "Versão": v.get("version"),
                        "Status": v.get("status"),
                        "Regras": v.get("rules_count", "—"),
                        "Criado em": v.get("created_at"),
                    }
                    for v in versions
                ])
                st.dataframe(df_v, key="mt_versions_table")
            else:
                st.info("Nenhuma versão anterior registrada.")
        except APIError as e:
            st.error(str(e))

    # ── Tab: Permissões ───────────────────────────────────────────────────────
    with tab_perm:
        _permissions_tab("monitored_table", binding_id)

    # ── Tab: Comentários ──────────────────────────────────────────────────────
    with tab_com:
        user_email = st.session_state.get("_dqx_auth_email", "")
        try:
            comments = get_client().list_comments("monitored_table", binding_id)

            if comments:
                for c in comments:
                    with st.container(border=True):
                        c1, c2 = st.columns([8, 1])
                        c1.markdown(f"**{c.get('author', '—')}** · {c.get('created_at', '')}")
                        c1.write(c.get("text", ""))
                        can_delete = is_admin() or c.get("author") == user_email
                        if can_delete and c2.button(":material/delete:", key=f"del_mc_{c.get('id')}"):
                            try:
                                get_client().delete_comment(c["id"])
                                st.rerun()
                            except APIError as e:
                                st.error(str(e))
            else:
                st.info("Nenhum comentário ainda.")

            st.divider()
            with st.form("form_mt_comment", clear_on_submit=True):
                new_text = st.text_area(
                    "Comentário", label_visibility="collapsed", placeholder="Escreva um comentário..."
                )
                if st.form_submit_button(":material/send: Comentar"):
                    if new_text.strip():
                        try:
                            get_client().add_comment({
                                "entity_type": "monitored_table",
                                "entity_id": binding_id,
                                "text": new_text.strip(),
                            })
                            st.rerun()
                        except APIError as e:
                            st.error(str(e))
        except APIError as e:
            st.error(str(e))


# ── Router ────────────────────────────────────────────────────────────────────

_view = st.session_state.get("mt_view", "list")

if _view == "list":
    _show_list()
elif _view == "detail":
    _show_detail()
elif _view == "new":
    _show_new()
else:
    st.session_state["mt_view"] = "list"
    st.rerun()
