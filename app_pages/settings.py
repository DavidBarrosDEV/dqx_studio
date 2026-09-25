"""
Settings — Sprint 4.
Admin-only. 12 seções em st.expander + st.form.

Seções:
  1. Timezone
  2. Label Definitions
  3. Retention
  4. Run Review Statuses
  5. AI Settings
  6. Rules Registry
  7. Approvals Mode + Draft Run Gate + Sample Limits
  8. Compute
  9. Share Tables with Workspace Users
  10. Role Management (RBAC)
  11. Métricas Customizadas
  12. Danger Zone (Database Reset / Deploy Demo)
"""

import zoneinfo

import streamlit as st

from core.api_client import APIError
from core.session import get_client, is_admin

# ── Guard ─────────────────────────────────────────────────────────────────────
if not is_admin():
    st.error("Acesso restrito a administradores.", icon=":material/lock:")
    st.stop()

st.title(":material/settings: Configurações")
st.caption("Configurações globais do workspace DQX Studio. Todas as alterações têm efeito imediato.")
st.divider()

client = get_client()


def _save_ok():
    st.toast("Configuração salva!", icon=":material/check_circle:")


def _save_err(e):
    st.error(f"Erro ao salvar: {e}", icon=":material/error:")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Timezone
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(":material/schedule: Timezone", expanded=False):
    try:
        tz_data = client.get_timezone_settings()
        all_tz = sorted(zoneinfo.available_timezones())
        current_tz = tz_data.get("timezone", "UTC")

        with st.form("form_timezone"):
            selected_tz = st.selectbox(
                "Fuso horário do workspace",
                all_tz,
                index=all_tz.index(current_tz) if current_tz in all_tz else 0,
            )
            if st.form_submit_button("Salvar timezone", type="primary"):
                try:
                    client.update_timezone_settings({"timezone": selected_tz})
                    _save_ok()
                except APIError as e:
                    _save_err(e)
    except APIError as e:
        st.error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 2. Label Definitions
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(":material/label: Label Definitions", expanded=False):
    try:
        labels = client.get_label_definitions()
        if not isinstance(labels, list):
            labels = []

        st.caption("Labels disponíveis para classificar regras e tabelas monitoradas.")

        for i, lbl in enumerate(labels):
            with st.container(border=True):
                c1, c2 = st.columns([3, 6])
                c1.markdown(f"**{lbl.get('key', '')}**")
                c2.caption(", ".join(lbl.get("values", [])))

        st.divider()
        st.subheader("Adicionar label")
        with st.form("form_add_label"):
            new_key = st.text_input("Chave (ex: domain)", placeholder="domain")
            new_vals = st.text_input("Valores separados por vírgula", placeholder="finance, sales, hr")
            if st.form_submit_button("Adicionar", type="primary"):
                if new_key.strip():
                    vals = [v.strip() for v in new_vals.split(",") if v.strip()]
                    labels.append({"key": new_key.strip(), "values": vals})
                    try:
                        client.update_label_definitions(labels)
                        _save_ok()
                        st.rerun()
                    except APIError as e:
                        _save_err(e)
    except APIError as e:
        st.error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 3. Retention
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(":material/archive: Retenção de Dados", expanded=False):
    try:
        ret = client.get_retention_settings()
        with st.form("form_retention"):
            run_days = st.number_input(
                "Retenção de resultados de runs (dias)",
                min_value=1, max_value=3650,
                value=int(ret.get("run_results_days", 90)),
            )
            profiler_days = st.number_input(
                "Retenção de resultados do Profiler (dias)",
                min_value=1, max_value=3650,
                value=int(ret.get("profiler_results_days", 30)),
            )
            comments_days = st.number_input(
                "Retenção de comentários (dias)",
                min_value=1, max_value=3650,
                value=int(ret.get("comments_days", 365)),
            )
            if st.form_submit_button("Salvar retenção", type="primary"):
                try:
                    client.update_retention_settings({
                        "run_results_days": run_days,
                        "profiler_results_days": profiler_days,
                        "comments_days": comments_days,
                    })
                    _save_ok()
                except APIError as e:
                    _save_err(e)
    except APIError as e:
        st.error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 4. Run Review Statuses
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(":material/fact_check: Status de Revisão de Runs", expanded=False):
    try:
        statuses = client.get_run_review_statuses()
        if not isinstance(statuses, list):
            statuses = []

        st.caption("Status personalizados disponíveis para revisão manual de runs.")

        with st.form("form_run_statuses"):
            raw = st.text_area(
                "Status (um por linha)",
                value="\n".join(statuses),
                height=120,
            )
            if st.form_submit_button("Salvar status", type="primary"):
                new_statuses = [s.strip() for s in raw.splitlines() if s.strip()]
                try:
                    client.update_run_review_statuses({"statuses": new_statuses})
                    _save_ok()
                except APIError as e:
                    _save_err(e)
    except APIError as e:
        st.error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 5. AI Settings
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(":material/smart_toy: Configurações de IA", expanded=False):
    try:
        ai = client.get_ai_settings()
        endpoints = []
        try:
            endpoints = client.list_ai_serving_endpoints()
        except APIError:
            pass

        with st.form("form_ai"):
            enabled = st.toggle("Habilitar assistente IA", value=bool(ai.get("enabled", False)))
            current_ep = ai.get("endpoint", "")
            if endpoints:
                idx = endpoints.index(current_ep) if current_ep in endpoints else 0
                endpoint = st.selectbox("Endpoint de serving", endpoints, index=idx, disabled=not enabled)
            else:
                endpoint = st.text_input("Endpoint de serving", value=current_ep, disabled=not enabled)
            st.caption("O assistente IA usa este endpoint para sugestões de regras e consultas analíticas.")

            if st.form_submit_button("Salvar configurações de IA", type="primary"):
                try:
                    client.update_ai_settings({"enabled": enabled, "endpoint": endpoint})
                    _save_ok()
                except APIError as e:
                    _save_err(e)
    except APIError as e:
        st.error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 6. Rules Registry
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(":material/rule: Registry de Regras", expanded=False):
    try:
        rr = client.get_rules_registry_settings()
        with st.form("form_registry"):
            auto_upgrade = st.toggle(
                "Auto-upgrade de regras vinculadas",
                value=bool(rr.get("auto_upgrade", False)),
                help="Ao aprovar nova versão de uma regra, atualiza automaticamente todos os bindings.",
            )
            tag_auto_assign = st.toggle(
                "Auto-atribuição de tags",
                value=bool(rr.get("tag_auto_assign", True)),
                help="Atribui tags automaticamente com base nos metadados da regra.",
            )
            pass_threshold = st.slider(
                "Pass threshold global (%)",
                min_value=0.0, max_value=1.0, step=0.01,
                value=float(rr.get("pass_threshold", 0.95)),
                format="%.2f",
                help="Proporção mínima de checks aprovados para considerar a tabela como 'passou'.",
            )
            if st.form_submit_button("Salvar registry", type="primary"):
                try:
                    client.update_rules_registry_settings({
                        "auto_upgrade": auto_upgrade,
                        "tag_auto_assign": tag_auto_assign,
                        "pass_threshold": pass_threshold,
                    })
                    _save_ok()
                except APIError as e:
                    _save_err(e)
    except APIError as e:
        st.error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 7. Aprovações + Draft Run Gate + Sample Limits
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(":material/approval: Aprovações e Execuções", expanded=False):
    try:
        approvals = client.get_approvals_mode()
        gate = client.get_draft_run_gate()
        limits = client.get_sample_limits()

        with st.form("form_approvals"):
            st.subheader("Modo de aprovação")
            mode = st.radio(
                "Modo",
                ["OPTIONAL", "REQUIRED", "DISABLED"],
                index=["OPTIONAL", "REQUIRED", "DISABLED"].index(approvals.get("mode", "OPTIONAL")),
                horizontal=True,
                help="REQUIRED: nenhuma regra pode ser aplicada sem aprovação.",
            )

            st.subheader("Draft Run Gate")
            require_draft_run = st.toggle(
                "Exigir dry-run antes de submeter regra",
                value=bool(gate.get("enabled", False)),
                help="Impede submissão de regras que nunca foram testadas.",
            )

            st.subheader("Limites de amostragem")
            dry_run_rows = st.number_input(
                "Máx. linhas por dry-run",
                min_value=100, max_value=10_000_000, step=1000,
                value=int(limits.get("dry_run_sample_rows", 10000)),
            )
            profiler_rows = st.number_input(
                "Máx. linhas por profiler run",
                min_value=100, max_value=10_000_000, step=1000,
                value=int(limits.get("profiler_sample_rows", 50000)),
            )

            if st.form_submit_button("Salvar aprovações e limites", type="primary"):
                try:
                    client.update_approvals_mode({"mode": mode, "require_draft_run": require_draft_run})
                    client.update_draft_run_gate({"enabled": require_draft_run})
                    client.update_sample_limits({
                        "dry_run_sample_rows": dry_run_rows,
                        "profiler_sample_rows": profiler_rows,
                    })
                    _save_ok()
                except APIError as e:
                    _save_err(e)
    except APIError as e:
        st.error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 8. Compute
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(":material/memory: Compute", expanded=False):
    try:
        compute = client.get_compute_settings()
        warehouses = client.list_compute_warehouses()
        clusters = client.list_compute_clusters()

        wh_opts = {w["name"]: w["id"] for w in warehouses}
        cl_opts = {c["name"]: c["id"] for c in clusters}

        with st.form("form_compute"):
            st.subheader("SQL Warehouse")
            wh_names = list(wh_opts.keys())
            cur_wh_id = compute.get("warehouse_id", "")
            cur_wh_name = next((n for n, i in wh_opts.items() if i == cur_wh_id), wh_names[0] if wh_names else "")
            selected_wh = st.selectbox(
                "Warehouse para queries DQ",
                wh_names,
                index=wh_names.index(cur_wh_name) if cur_wh_name in wh_names else 0,
            )

            st.subheader("Job Cluster (opcional)")
            cl_names = ["— Nenhum —"] + list(cl_opts.keys())
            cur_cl_id = compute.get("cluster_id")
            cur_cl_name = next((n for n, i in cl_opts.items() if i == cur_cl_id), "— Nenhum —")
            selected_cl = st.selectbox("Cluster para jobs agendados", cl_names,
                                       index=cl_names.index(cur_cl_name) if cur_cl_name in cl_names else 0)

            grant_access = st.toggle(
                "Conceder acesso automático ao warehouse para novos usuários",
                value=bool(compute.get("grant_access", True)),
            )

            if st.form_submit_button("Salvar compute", type="primary"):
                cl_id = cl_opts.get(selected_cl) if selected_cl != "— Nenhum —" else None
                try:
                    client.update_compute_settings({
                        "warehouse_id": wh_opts.get(selected_wh, ""),
                        "cluster_id": cl_id,
                        "grant_access": grant_access,
                    })
                    _save_ok()
                except APIError as e:
                    _save_err(e)
    except APIError as e:
        st.error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 9. Share Tables with Workspace Users
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(":material/share: Compartilhar Tabelas com Usuários", expanded=False):
    try:
        share = client.get_share_tables_settings()
        with st.form("form_share"):
            enabled = st.toggle(
                "Compartilhar tabelas monitoradas com todos os usuários do workspace",
                value=bool(share.get("enabled", True)),
                help="Quando ativo, todos os usuários autenticados podem visualizar as tabelas monitoradas.",
            )
            if st.form_submit_button("Salvar", type="primary"):
                try:
                    client.update_share_tables_settings({"enabled": enabled})
                    _save_ok()
                except APIError as e:
                    _save_err(e)
    except APIError as e:
        st.error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 10. Role Management (RBAC)
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(":material/manage_accounts: Gestão de Papéis (RBAC)", expanded=False):
    try:
        mappings = client.list_role_mappings()
        groups = client.list_workspace_groups()
        roles = client.list_available_roles()

        st.caption("Associe grupos do workspace a papéis do DQX Studio.")

        if mappings:
            for m in mappings:
                c1, c2, c3 = st.columns([4, 3, 1])
                c1.markdown(f"**{m.get('group', '—')}**")
                c2.markdown(f"`{m.get('role', '—')}`")
                if c3.button(":material/delete:", key=f"del_rm_{m.get('id')}"):
                    try:
                        client.delete_role_mapping(m["id"])
                        st.rerun()
                    except APIError as e:
                        st.error(str(e))
        else:
            st.info("Nenhum mapeamento configurado.", icon=":material/info:")

        st.divider()
        with st.form("form_add_role"):
            col1, col2 = st.columns(2)
            sel_group = col1.selectbox("Grupo", groups)
            sel_role = col2.selectbox("Papel", roles)
            if st.form_submit_button("Adicionar mapeamento", type="primary"):
                try:
                    client.create_role_mapping({"group": sel_group, "role": sel_role})
                    _save_ok()
                    st.rerun()
                except APIError as e:
                    _save_err(e)
    except APIError as e:
        st.error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 11. Métricas Customizadas
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(":material/bar_chart: Métricas Customizadas", expanded=False):
    try:
        metrics = client.list_custom_metrics()
        st.caption("Defina SQL templates para métricas calculadas sobre tabelas monitoradas. Use `{table}` como placeholder.")

        if metrics:
            for m in metrics:
                with st.container(border=True):
                    h1, h2 = st.columns([6, 1])
                    h1.markdown(f"**{m.get('name', '—')}**")
                    h1.caption(m.get("description", ""))
                    h1.code(m.get("sql", ""), language="sql")
                    if h2.button(":material/delete:", key=f"del_cm_{m.get('id')}"):
                        try:
                            client.delete_custom_metric(m["id"])
                            st.rerun()
                        except APIError as e:
                            st.error(str(e))
        else:
            st.info("Nenhuma métrica customizada definida.")

        st.divider()
        st.subheader("Adicionar métrica")
        with st.form("form_add_metric"):
            m_name = st.text_input("Nome", placeholder="pct_nulls")
            m_desc = st.text_input("Descrição", placeholder="Percentual de valores nulos")
            m_sql = st.text_area(
                "SQL",
                placeholder="SELECT COUNT(*) FILTER (WHERE col IS NULL) * 100.0 / COUNT(*) FROM {table}",
                height=100,
            )
            if st.form_submit_button("Adicionar métrica", type="primary"):
                if m_name.strip() and m_sql.strip():
                    try:
                        client.create_custom_metric({
                            "name": m_name.strip(),
                            "description": m_desc.strip(),
                            "sql": m_sql.strip(),
                        })
                        _save_ok()
                        st.rerun()
                    except APIError as e:
                        _save_err(e)
    except APIError as e:
        st.error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 12. Danger Zone
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(":material/warning: Zona de Perigo", expanded=False):
    st.error(
        "As ações abaixo são **irreversíveis** e afetam todos os usuários do workspace.",
        icon=":material/warning:",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Reset do Banco de Dados")
        st.caption("Remove todos os dados de configuração, regras, bindings e resultados. Útil para recomeçar do zero em ambiente de desenvolvimento.")
        if st.button(":material/delete_forever: Resetar banco de dados", type="secondary"):
            st.session_state["_danger_confirm"] = "reset"

    with col2:
        st.subheader("Implantar Demo")
        st.caption("Popula o workspace com dados de demonstração: regras de exemplo, tabelas monitoradas e resultados simulados.")
        if st.button(":material/rocket_launch: Implantar Demo", type="secondary"):
            st.session_state["_danger_confirm"] = "demo"

    confirm = st.session_state.get("_danger_confirm")
    if confirm:
        st.divider()
        action_label = "resetar o banco de dados" if confirm == "reset" else "implantar a demo"
        st.warning(f"Tem certeza que deseja **{action_label}**? Esta ação não pode ser desfeita.")
        c1, c2 = st.columns(2)
        if c1.button("Confirmar", type="primary", key="danger_ok"):
            try:
                if confirm == "reset":
                    client.reset_database()
                    st.success("Banco de dados resetado com sucesso!")
                else:
                    client.deploy_demo()
                    st.success("Demo implantada com sucesso!")
                st.session_state.pop("_danger_confirm", None)
            except APIError as e:
                st.error(str(e))
        if c2.button("Cancelar", key="danger_cancel"):
            st.session_state.pop("_danger_confirm", None)
            st.rerun()
