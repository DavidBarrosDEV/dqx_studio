"""
Registry de Regras — Sprint 5.

Views (st.session_state["rr_view"]):
  "list"             → listagem com filtros, bulk actions, export
  "detail"           → detalhe com tabs (Detalhes, Versões, Comentários) + export YAML
  "create"           → editor de regras: DQX Native | SQL | Low-code
                       AI Assist sidebar, dry-run, duplicate detection
  "import_yaml"      → importar regras via arquivo YAML
  "import_contract"  → importar regras a partir de Data Contract (ODCS)
"""

import io

import pandas as pd
import streamlit as st

from core.api_client import APIError
from core.catalog_browser import catalog_browser
from core.session import get_client, get_user_role, is_admin

# ── Constantes ────────────────────────────────────────────────────────────────

_STATUS_COLOR = {
    "DRAFT": "gray", "SUBMITTED": "blue", "APPROVED": "green",
    "REJECTED": "red", "DEPRECATED": "orange", "REVOKED": "orange",
}
_SEVERITY_COLOR = {
    "CRITICAL": "red", "HIGH": "orange", "MEDIUM": "yellow", "LOW": "gray",
}
_SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
_STATUSES = ["DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "DEPRECATED"]

_LOWCODE_CONDITIONS = {
    "Não é nulo":          {"fn": "is_not_null",   "params": []},
    "É único":             {"fn": "is_unique",      "params": []},
    "Está em lista":       {"fn": "is_in_list",     "params": ["allowed_values"]},
    "Dentro do intervalo": {"fn": "is_in_range",    "params": ["min", "max"]},
    "Corresponde a regex": {"fn": "matches_regex",  "params": ["pattern"]},
    "Não está em lista":   {"fn": "is_not_in_list", "params": ["forbidden_values"]},
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _badge(text: str, color_map: dict) -> str:
    return f":{color_map.get(text, 'gray')}[{text}]"


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
        "submit": "Enviar para aprovação", "approve": "Aprovar regra",
        "reject": "Rejeitar regra", "revoke": "Revogar submissão",
        "deprecate": "Deprecar regra", "undeprecate": "Remover deprecação",
        "delete": "Excluir regra permanentemente",
    }
    st.subheader(_labels.get(action, action))
    needs_rationale = action in ("approve", "reject")
    rationale = st.text_area("Motivo (obrigatório):") if needs_rationale else ""

    c1, c2 = st.columns(2)
    if c1.button("Confirmar", type="primary"):
        if needs_rationale and not rationale.strip():
            st.warning("Insira o motivo.")
            return
        client = get_client()
        try:
            if action == "submit":       client.submit_registry_rule(rule_id)
            elif action == "approve":    client.approve_registry_rule(rule_id, rationale)
            elif action == "reject":     client.reject_registry_rule(rule_id, rationale)
            elif action == "revoke":     client.post(f"/registry-rules/{rule_id}/revoke")
            elif action == "deprecate":  client.deprecate_registry_rule(rule_id)
            elif action == "undeprecate":client.post(f"/registry-rules/{rule_id}/undeprecate")
            elif action == "delete":
                client.delete_registry_rule(rule_id)
                _invalidate()
                st.session_state["rr_view"] = "list"
        except APIError as e:
            st.error(str(e)); return
        _invalidate(); st.rerun()
    if c2.button("Cancelar"): st.rerun()


# ── Dry-run dialog ────────────────────────────────────────────────────────────

@st.dialog("Testar regra (dry-run)", width="large")
def _dryrun_dialog(payload: dict):
    st.caption("Selecione uma tabela para testar a regra antes de salvar.")
    fqn = catalog_browser(key_prefix="rr_dryrun")
    if not fqn:
        return

    if st.button("Executar teste", type="primary"):
        try:
            result = get_client().submit_dry_run({"rule": payload, "table_fqn": fqn})
            run_id = result.get("run_id")

            # Poll (simplified: immediate result in mock)
            with st.spinner("Executando dry-run..."):
                import time; time.sleep(1)
                res = get_client().get_run_results(run_id)

            score = res.get("dq_score")
            passed = res.get("checks_passed", 0)
            failed = res.get("checks_failed", 0)

            col1, col2, col3 = st.columns(3)
            col1.metric("DQ Score", f"{score:.1f}%" if score else "—")
            col2.metric("Aprovados", passed)
            col3.metric("Falhas", failed)

            if failed == 0:
                st.success("Regra passou em todos os registros testados!")
            else:
                st.warning(f"**{failed}** registro(s) violaram a regra.")
        except APIError as e:
            st.error(str(e))


# ── LIST VIEW ─────────────────────────────────────────────────────────────────

def _show_list():
    h1, h2, h3, h4 = st.columns([5, 1, 1, 1])
    h1.title(":material/rule: Registry de Regras")
    if h2.button(":material/upload_file: YAML"):
        _go("import_yaml")
    if h3.button(":material/description: Contract"):
        _go("import_contract")
    if h4.button("+ Nova", type="primary"):
        _go("create")

    st.divider()
    rules = _load_rules()

    f1, f2, f3 = st.columns([3, 2, 2])
    search = f1.text_input("Pesquisar", placeholder="Nome da regra...", label_visibility="collapsed")
    status_filter = f2.multiselect("Status", _STATUSES, placeholder="Status", label_visibility="collapsed")
    severity_filter = f3.multiselect("Severidade", _SEVERITIES, placeholder="Severidade", label_visibility="collapsed")

    filtered = rules
    if search:         filtered = [r for r in filtered if search.lower() in r.get("name", "").lower()]
    if status_filter:  filtered = [r for r in filtered if r.get("status") in status_filter]
    if severity_filter:filtered = [r for r in filtered if r.get("severity") in severity_filter]

    st.caption(f"{len(filtered)} regra(s) encontrada(s)")
    if not filtered:
        st.info("Nenhuma regra encontrada.", icon=":material/search_off:")
        return

    df = pd.DataFrame([{
        "Nome": r.get("name", ""), "Status": r.get("status", ""),
        "Severidade": r.get("severity", ""), "Descrição": r.get("description", ""),
        "Criado em": r.get("created_at", ""),
    } for r in filtered])

    event = st.dataframe(df, selection_mode="multi-row", on_select="rerun", key="rr_table",
        column_config={
            "Nome": st.column_config.TextColumn(width="medium"),
            "Status": st.column_config.TextColumn(width="small"),
            "Severidade": st.column_config.TextColumn(width="small"),
            "Descrição": st.column_config.TextColumn(width="large"),
        })

    selected_idx = event.selection.rows
    selected = [filtered[i] for i in selected_idx] if selected_idx else []
    if not selected: return

    st.markdown(f"**{len(selected)} selecionada(s)**")
    role = get_user_role()

    with st.container(horizontal=True):
        if len(selected) == 1:
            if st.button(":material/open_in_new: Abrir"):
                _go("detail", selected[0].get("id"))

        if st.button(":material/send: Submeter"):
            for r in selected:
                try: get_client().submit_registry_rule(r["id"])
                except APIError: pass
            _invalidate(); st.rerun()

        if role in ("ADMIN", "RULE_APPROVER"):
            if st.button(":material/check_circle: Aprovar"):
                for r in selected:
                    try: get_client().approve_registry_rule(r["id"])
                    except APIError: pass
                _invalidate(); st.rerun()
            if st.button(":material/cancel: Rejeitar"):
                for r in selected:
                    try: get_client().reject_registry_rule(r["id"])
                    except APIError: pass
                _invalidate(); st.rerun()

        if is_admin():
            if st.button(":material/archive: Deprecar"):
                for r in selected:
                    try: get_client().deprecate_registry_rule(r["id"])
                    except APIError: pass
                _invalidate(); st.rerun()
            if st.button(":material/delete: Excluir"):
                for r in selected:
                    try: get_client().delete_registry_rule(r["id"])
                    except APIError: pass
                _invalidate(); st.rerun()

        # Export selected
        if st.button(":material/download: Exportar YAML"):
            try:
                ids = [r["id"] for r in selected]
                yaml_content = get_client().export_registry_rules(ids)
                st.download_button(
                    "⬇ Baixar rules.yaml",
                    data=yaml_content if isinstance(yaml_content, str) else str(yaml_content),
                    file_name="rules.yaml",
                    mime="text/yaml",
                    key="dl_export",
                )
            except APIError as e:
                st.error(str(e))


# ── DETAIL VIEW ───────────────────────────────────────────────────────────────

def _show_detail():
    rule_id = st.session_state.get("rr_selected_id")
    if st.button(":material/arrow_back: Voltar à lista"): _go("list")

    cache_key = f"_rr_detail_{rule_id}"
    if cache_key not in st.session_state:
        try:
            st.session_state[cache_key] = get_client().get_registry_rule(rule_id)
        except APIError as e:
            st.error(str(e), icon=":material/error:"); return
    rule = st.session_state[cache_key]

    status = rule.get("status", "DRAFT")
    severity = rule.get("severity", "HIGH")
    role = get_user_role()
    editable = status == "DRAFT"

    h1, h2 = st.columns([8, 1])
    h1.title(f":material/rule: {rule.get('name', rule_id)}")
    h1.markdown(f"{_badge(status, _STATUS_COLOR)} &nbsp;&nbsp; {_badge(severity, _SEVERITY_COLOR)}")

    # Export YAML
    try:
        yaml_str = get_client().export_registry_rules([rule_id])
        h2.download_button(
            ":material/download: YAML",
            data=yaml_str if isinstance(yaml_str, str) else str(yaml_str),
            file_name=f"{rule.get('name', rule_id)}.yaml",
            mime="text/yaml",
        )
    except APIError:
        pass

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

    tab_det, tab_ver, tab_com = st.tabs([
        ":material/info: Detalhes",
        ":material/history: Versões",
        ":material/chat: Comentários",
    ])

    with tab_det:
        with st.form("form_detail"):
            name = st.text_input("Nome", value=rule.get("name", ""), disabled=not editable)
            description = st.text_area("Descrição", value=rule.get("description", ""), disabled=not editable)
            sev_idx = _SEVERITIES.index(severity) if severity in _SEVERITIES else 1
            new_severity = st.selectbox("Severidade", _SEVERITIES, index=sev_idx, disabled=not editable)

            if rule.get("check_function"):
                st.text_input("Função", value=rule["check_function"], disabled=True)
            if rule.get("column"):
                st.text_input("Coluna", value=rule["column"], disabled=True)
            if rule.get("sql"):
                st.code(rule["sql"], language="sql")

            if editable:
                if st.form_submit_button("Salvar rascunho", type="primary"):
                    try:
                        get_client().update_registry_rule(rule_id, {
                            "name": name, "description": description, "severity": new_severity,
                        })
                        st.session_state.pop(cache_key, None); _invalidate()
                        st.success("Regra atualizada."); st.rerun()
                    except APIError as e:
                        st.error(str(e))
            else:
                st.form_submit_button("Edição desabilitada", disabled=True)
                st.caption(f"Status **{status}** — somente rascunhos podem ser editados.")

    with tab_ver:
        try:
            versions = get_client().get_registry_rule_versions(rule_id)
            if versions:
                df_v = pd.DataFrame([{"Versão": v.get("version"), "Status": v.get("status"), "Criado em": v.get("created_at")} for v in versions])
                st.dataframe(df_v, key="rr_versions_table")
            else:
                st.info("Nenhuma versão anterior.")
        except APIError as e:
            st.error(str(e))

    with tab_com:
        user_email = st.session_state.get("_dqx_auth_email", "")
        try:
            comments = get_client().list_comments("registry_rule", rule_id)
            if comments:
                for c in comments:
                    with st.container(border=True):
                        c1, c2 = st.columns([8, 1])
                        c1.markdown(f"**{c.get('author', '—')}** · {c.get('created_at', '')}")
                        c1.write(c.get("text", ""))
                        if is_admin() or c.get("author") == user_email:
                            if c2.button(":material/delete:", key=f"del_c_{c.get('id')}"):
                                try: get_client().delete_comment(c["id"]); st.rerun()
                                except APIError as e: st.error(str(e))
            else:
                st.info("Nenhum comentário.")
            st.divider()
            with st.form("form_comment", clear_on_submit=True):
                new_text = st.text_area("Comentário", label_visibility="collapsed", placeholder="Escreva um comentário...")
                if st.form_submit_button(":material/send: Comentar"):
                    if new_text.strip():
                        try:
                            get_client().add_comment({"entity_type": "registry_rule", "entity_id": rule_id, "text": new_text.strip()})
                            st.rerun()
                        except APIError as e: st.error(str(e))
        except APIError as e:
            st.error(str(e))


# ── CREATE VIEW (Sprint 5) ────────────────────────────────────────────────────

def _show_create():
    if st.button(":material/arrow_back: Voltar à lista"): _go("list")
    st.title(":material/add: Nova Regra")

    # ── AI Assist sidebar ──────────────────────────────────────────────────────
    with st.sidebar:
        st.subheader(":material/smart_toy: AI Assist")
        ai_mode = st.radio("Ação", ["Gerar checks", "Escrever SQL", "Melhorar SQL", "Explicar SQL"], label_visibility="collapsed")

        if ai_mode == "Gerar checks":
            ai_prompt = st.text_area("Descreva a regra que quer criar:", placeholder="ex: validar que order_id não é nulo e é positivo")
            ai_col = st.text_input("Coluna (opcional):", placeholder="order_id")
            if st.button("Gerar", type="primary", key="ai_gen"):
                try:
                    res = get_client().generate_checks({"prompt": ai_prompt, "column": ai_col})
                    st.session_state["_rr_ai_yaml"] = res.get("yaml", "")
                except APIError as e:
                    st.error(str(e))

            if st.session_state.get("_rr_ai_yaml"):
                st.code(st.session_state["_rr_ai_yaml"], language="yaml")
                if st.button("Usar sugestão"):
                    st.session_state["_rr_ai_mode_preset"] = "DQX Native"
                    st.session_state["_rr_ai_fill_yaml"] = st.session_state["_rr_ai_yaml"]
                    st.rerun()

        elif ai_mode == "Escrever SQL":
            ai_desc = st.text_area("Descreva a validação:", placeholder="ex: verificar que amount é positivo")
            ai_col2 = st.text_input("Coluna:", placeholder="amount")
            if st.button("Gerar SQL", type="primary", key="ai_sql"):
                try:
                    res = get_client().ai_write_sql({"description": ai_desc, "column": ai_col2})
                    st.session_state["_rr_ai_sql"] = res.get("sql", "")
                except APIError as e:
                    st.error(str(e))
            if st.session_state.get("_rr_ai_sql"):
                st.code(st.session_state["_rr_ai_sql"], language="sql")
                if st.button("Usar SQL"):
                    st.session_state["_rr_ai_mode_preset"] = "SQL"
                    st.session_state["_rr_ai_fill_sql"] = st.session_state["_rr_ai_sql"]
                    st.rerun()

        elif ai_mode == "Melhorar SQL":
            sql_in = st.text_area("SQL atual:", height=120)
            if st.button("Melhorar", type="primary", key="ai_improve"):
                try:
                    res = get_client().ai_improve_sql({"sql": sql_in})
                    st.session_state["_rr_ai_sql"] = res.get("sql", "")
                except APIError as e:
                    st.error(str(e))
            if st.session_state.get("_rr_ai_sql"):
                st.code(st.session_state["_rr_ai_sql"], language="sql")

        elif ai_mode == "Explicar SQL":
            sql_explain = st.text_area("SQL para explicar:", height=120)
            if st.button("Explicar", type="primary", key="ai_explain"):
                try:
                    res = get_client().ai_explain_sql({"sql": sql_explain})
                    st.info(res.get("explanation", ""))
                except APIError as e:
                    st.error(str(e))

    st.divider()

    # ── Mode switcher (outside form) ───────────────────────────────────────────
    preset_mode = st.session_state.pop("_rr_ai_mode_preset", None)
    mode_options = ["DQX Native", "SQL", "Low-code"]
    default_mode = preset_mode if preset_mode in mode_options else "DQX Native"
    mode = st.segmented_control("Modo", mode_options, default=default_mode, key="rr_create_mode")

    # ── Main form ──────────────────────────────────────────────────────────────
    with st.form("form_create"):
        name = st.text_input("Nome da regra *", placeholder="ex: not_null_order_id")
        description = st.text_area("Descrição", placeholder="Descreva o objetivo desta regra")
        severity = st.selectbox("Severidade *", _SEVERITIES, index=1)

        st.divider()

        # Preset values from AI
        preset_sql = st.session_state.pop("_rr_ai_fill_sql", "")
        preset_yaml = st.session_state.pop("_rr_ai_fill_yaml", "")

        sql_expr = selected_fn = column = params_raw = None
        condition_label = fn_params = None

        # ── DQX Native ────────────────────────────────────────────────────────
        if mode == "DQX Native":
            if "_check_functions" not in st.session_state:
                try: st.session_state["_check_functions"] = get_client().list_check_functions()
                except APIError: st.session_state["_check_functions"] = []
            fns = st.session_state["_check_functions"]
            fn_names = [f["name"] for f in fns]
            fn_desc = {f["name"]: f.get("description", "") for f in fns}
            selected_fn = st.selectbox("Função de verificação *", fn_names)
            if selected_fn: st.caption(fn_desc.get(selected_fn, ""))
            column = st.text_input("Coluna", placeholder="ex: order_id")
            params_raw = st.text_area("Parâmetros adicionais (YAML)", value=preset_yaml, placeholder="min: 0\nmax: 1000", height=80)

        # ── SQL ───────────────────────────────────────────────────────────────
        elif mode == "SQL":
            sql_expr = st.text_area("SQL *", value=preset_sql, height=160,
                                    placeholder="SELECT * FROM {table} WHERE order_id IS NOT NULL")
            if sql_expr:
                st.subheader("Pré-visualização:")
                st.code(sql_expr, language="sql")

        # ── Low-code ──────────────────────────────────────────────────────────
        elif mode == "Low-code":
            st.caption("Construa a condição de validação sem escrever código.")
            condition_label = st.selectbox("Condição *", list(_LOWCODE_CONDITIONS.keys()))
            column = st.text_input("Coluna *", placeholder="nome_da_coluna")

            condition_def = _LOWCODE_CONDITIONS.get(condition_label, {})
            fn_params = {}
            for param in condition_def.get("params", []):
                fn_params[param] = st.text_input(
                    f"Parâmetro: {param}",
                    placeholder={"allowed_values": "val1, val2, val3",
                                 "min": "0", "max": "100",
                                 "pattern": "^[A-Z]+$",
                                 "forbidden_values": "INVALID, NULL"}.get(param, ""),
                )

        submitted = st.form_submit_button("Salvar como rascunho", type="primary")
        test_clicked = st.form_submit_button(":material/science: Testar (dry-run)")

    # ── Process form ──────────────────────────────────────────────────────────
    if submitted or test_clicked:
        errors = []
        if not name.strip(): errors.append("Nome é obrigatório.")
        if mode == "DQX Native" and not selected_fn:  errors.append("Selecione uma função.")
        if mode == "SQL" and not (sql_expr or "").strip(): errors.append("SQL é obrigatório.")
        if mode == "Low-code" and not (column or "").strip(): errors.append("Coluna é obrigatória.")

        if errors:
            for err in errors: st.error(err)
        else:
            payload: dict = {"name": name.strip(), "description": description.strip(),
                             "severity": severity, "status": "DRAFT"}
            if mode == "DQX Native":
                payload["check_function"] = selected_fn
                if column: payload["column"] = column
                if params_raw: payload["params_yaml"] = params_raw
            elif mode == "SQL":
                payload["sql"] = sql_expr.strip()
            elif mode == "Low-code":
                cond = _LOWCODE_CONDITIONS[condition_label]
                payload["check_function"] = cond["fn"]
                payload["column"] = column.strip()
                if fn_params: payload["params"] = {k: v for k, v in fn_params.items() if v}

            # Dry-run path
            if test_clicked:
                _dryrun_dialog(payload)
                return

            # ── Duplicate detection ────────────────────────────────────────────
            try:
                dup = get_client().check_rule_duplicates({"name": name.strip(), "check_function": payload.get("check_function"), "column": payload.get("column")})
                if dup.get("has_duplicates"):
                    duplicates = dup.get("duplicates", [])
                    st.warning(f"⚠️ Encontramos {len(duplicates)} regra(s) semelhante(s):")
                    for d in duplicates:
                        st.markdown(f"- **{d.get('name')}** ({d.get('status')})")
                    st.session_state["_rr_pending_payload"] = payload
                    st.session_state["_rr_save_anyway"] = True
                    st.rerun()
            except APIError:
                pass

            _do_save(payload)

    # ── Save anyway (after duplicate warning) ─────────────────────────────────
    if st.session_state.get("_rr_save_anyway"):
        st.warning("Existem regras similares. Deseja salvar mesmo assim?")
        c1, c2 = st.columns(2)
        if c1.button("Salvar mesmo assim", type="primary"):
            _do_save(st.session_state.pop("_rr_pending_payload", {}))
            st.session_state.pop("_rr_save_anyway", None)
        if c2.button("Cancelar"):
            st.session_state.pop("_rr_pending_payload", None)
            st.session_state.pop("_rr_save_anyway", None)
            st.rerun()


def _do_save(payload: dict):
    try:
        created = get_client().create_registry_rule(payload)
        _invalidate()
        st.success(f"Regra **{payload.get('name')}** criada como rascunho!")
        rule_id = created.get("id")
        _go("detail", rule_id) if rule_id else _go("list")
    except APIError as e:
        st.error(str(e))


# ── IMPORT YAML VIEW ──────────────────────────────────────────────────────────

def _show_import_yaml():
    if st.button(":material/arrow_back: Voltar"): _go("list")
    st.title(":material/upload_file: Importar Regras — YAML")
    st.caption("Faça upload de um arquivo `.yaml` com uma ou mais regras no formato DQX.")
    st.divider()

    uploaded = st.file_uploader("Arquivo YAML de regras", type=["yaml", "yml"])
    if not uploaded:
        st.info("Aguardando arquivo...")
        return

    try:
        content = uploaded.read().decode("utf-8")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        return

    st.subheader("Pré-visualização do conteúdo")
    st.code(content, language="yaml")

    if st.button("Importar regras", type="primary"):
        try:
            result = get_client().batch_import_registry_rules({"yaml": content})
            imported = result.get("imported", 0)
            skipped = result.get("skipped", 0)
            _invalidate()
            st.success(f"**{imported}** regra(s) importada(s). **{skipped}** ignorada(s) (duplicatas).")
            if st.button("Ver lista de regras"): _go("list")
        except APIError as e:
            st.error(str(e))


# ── IMPORT DATA CONTRACT VIEW ─────────────────────────────────────────────────

def _show_import_contract():
    if st.button(":material/arrow_back: Voltar"): _go("list")
    st.title(":material/description: Importar via Data Contract (ODCS)")
    st.caption("Cole um contrato de dados no formato ODCS. O assistente irá gerar regras DQX automaticamente.")
    st.divider()

    contract_text = st.text_area(
        "Contrato de Dados (YAML/JSON)", height=300,
        placeholder="schema:\n  name: orders\n  fields:\n    - name: order_id\n      type: integer\n      constraints:\n        - notNull: true\n        - unique: true\n..."
    )

    if not contract_text.strip():
        return

    if st.button("Gerar regras a partir do contrato", type="primary"):
        try:
            result = get_client().generate_rules_from_contract({"contract": contract_text})
            generated = result.get("rules", [])
            st.session_state["_rr_contract_rules"] = generated
            st.rerun()
        except APIError as e:
            st.error(str(e))

    rules = st.session_state.get("_rr_contract_rules", [])
    if not rules:
        return

    st.divider()
    st.subheader(f"Regras geradas ({len(rules)})")
    st.caption("Selecione as regras que deseja importar:")

    selected_rules = []
    for i, rule in enumerate(rules):
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 5, 2])
            checked = c1.checkbox("", key=f"cr_{i}", value=True)
            c2.markdown(f"**{rule.get('name', '—')}**")
            c2.caption(f"Função: `{rule.get('check_function', '—')}` · Coluna: `{rule.get('column', '—')}` · {rule.get('description', '')}")
            c3.markdown(f"`{rule.get('severity', 'HIGH')}`")
            if checked:
                selected_rules.append(rule)

    st.divider()
    if selected_rules:
        if st.button(f"Importar {len(selected_rules)} regra(s) selecionada(s)", type="primary"):
            imported_count = 0
            for rule in selected_rules:
                try:
                    get_client().create_registry_rule({**rule, "status": "DRAFT"})
                    imported_count += 1
                except APIError:
                    pass
            _invalidate()
            st.session_state.pop("_rr_contract_rules", None)
            st.success(f"**{imported_count}** regra(s) importada(s) como DRAFT!")
            _go("list")


# ── Router ────────────────────────────────────────────────────────────────────

_view = st.session_state.get("rr_view", "list")

if _view == "list":             _show_list()
elif _view == "detail":         _show_detail()
elif _view == "create":         _show_create()
elif _view == "import_yaml":    _show_import_yaml()
elif _view == "import_contract":_show_import_contract()
else:
    st.session_state["rr_view"] = "list"
    st.rerun()
