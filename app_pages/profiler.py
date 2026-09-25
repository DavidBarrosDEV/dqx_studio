"""
Profiler — analisa o perfil estatístico de uma tabela Delta e sugere regras de qualidade.

Views (st.session_state["prof_view"]):
  "list"   → histórico de runs + form de nova análise
  "detail" → estatísticas por coluna de um run específico + "Save as Rules"
"""

import pandas as pd
import streamlit as st

from core.api_client import APIError
from core.catalog_browser import catalog_browser
from core.session import get_client

_STATUS_COLOR = {
    "SUCCEEDED": "green", "FAILED": "red",
    "RUNNING": "blue", "PENDING": "gray", "CANCELLED": "gray",
}
_STATUS_ICON = {
    "SUCCEEDED": ":material/check_circle:",
    "FAILED": ":material/error:",
    "RUNNING": ":material/hourglass_top:",
    "PENDING": ":material/schedule:",
    "CANCELLED": ":material/cancel:",
}


# ── Polling fragment ──────────────────────────────────────────────────────────

@st.fragment(run_every=5)
def _poll_running(run_id: str):
    try:
        status_data = get_client().get_profiler_run_status(run_id)
        status = status_data.get("status", "RUNNING")
        if status in ("RUNNING", "PENDING"):
            st.info(f":material/hourglass_top: Profiling em andamento... (`{run_id}`)", icon=None)
            return
        if status == "SUCCEEDED":
            st.success(f"Profiling concluído! Clique em **Ver resultados** para analisar.", icon=":material/check_circle:")
            st.session_state.pop("_prof_active_run", None)
            st.session_state.pop("_prof_runs", None)
        else:
            st.error(f"Run falhou: {status}", icon=":material/error:")
            st.session_state.pop("_prof_active_run", None)
    except APIError as e:
        st.error(str(e))


# ── Save as Rules dialog ──────────────────────────────────────────────────────

@st.dialog("Salvar candidatos como Regras", width="large")
def _save_as_rules_dialog(candidates: list, table_fqn: str):
    st.caption(f"Tabela: `{table_fqn}`")
    st.markdown("Selecione os candidatos que deseja criar como **regras rascunho** no Registry:")
    st.divider()

    _SEVERITY_MAP = {"is_not_null": "CRITICAL", "is_unique": "HIGH", "is_in_range": "HIGH",
                     "matches_regex": "MEDIUM", "is_in_list": "MEDIUM"}

    selected = []
    for i, c in enumerate(candidates):
        col_name = c.get("column", "—")
        check = c.get("check", "—")
        rationale = c.get("rationale", "")
        confidence = c.get("confidence", 0)
        severity = _SEVERITY_MAP.get(check, "MEDIUM")

        with st.container(border=True):
            ch1, ch2, ch3 = st.columns([1, 7, 2])
            checked = ch1.checkbox("", key=f"cand_{i}", value=confidence >= 0.85)
            ch2.markdown(f"**`{col_name}`** → `{check}`")
            ch2.caption(rationale)
            ch3.markdown(f"`{severity}`")
            ch3.caption(f"{confidence*100:.0f}% confiança")
            if checked:
                selected.append({"column": col_name, "check": check, "severity": severity})

    st.divider()
    if selected:
        st.markdown(f"**{len(selected)} regra(s)** serão criadas como DRAFT.")
    else:
        st.caption("Nenhum candidato selecionado.")

    c1, c2 = st.columns(2)
    if c1.button("Criar regras", type="primary", disabled=not selected):
        saved, failed = 0, 0
        for s in selected:
            try:
                get_client().create_registry_rule({
                    "name": f"{s['check']}_{s['column']}",
                    "description": f"Gerada pelo Profiler para `{table_fqn}`",
                    "check_function": s["check"],
                    "column": s["column"],
                    "severity": s["severity"],
                    "status": "DRAFT",
                })
                saved += 1
            except APIError:
                failed += 1
        st.session_state.pop("_prof_rr_cache", None)
        if saved:
            st.success(f"**{saved}** regra(s) criada(s) como DRAFT!")
        if failed:
            st.warning(f"{failed} regra(s) não puderam ser criadas.")
        st.rerun()
    if c2.button("Cancelar"):
        st.rerun()


# ── LIST VIEW ─────────────────────────────────────────────────────────────────

def _show_list():
    st.title(":material/troubleshoot: Profiler")
    st.caption("Analisa o perfil estatístico de tabelas Delta e sugere regras de qualidade automaticamente.")

    # ── New profile run form (sidebar) ────────────────────────────────────────
    with st.sidebar:
        st.subheader(":material/add_circle: Nova Análise")
        fqn = catalog_browser(key_prefix="prof_new")

        st.divider()
        sample_rows = st.number_input(
            "Linhas para sampling",
            min_value=1000, max_value=500_000, value=50_000, step=1000,
            help="Número de linhas amostradas. Mais linhas = análise mais precisa, porém mais lenta.",
        )
        include_cols = st.text_input(
            "Colunas (opcional)",
            placeholder="col1, col2 — deixe vazio para todas",
            help="Lista de colunas separadas por vírgula.",
        )
        compute_candidates = st.toggle("Gerar candidatos a regras", value=True,
            help="O Profiler irá sugerir checks baseados nas estatísticas detectadas.")

        if st.button(":material/play_arrow: Iniciar análise", type="primary", disabled=not fqn):
            try:
                cols = [c.strip() for c in include_cols.split(",") if c.strip()] if include_cols else None
                result = get_client().submit_profile_run({
                    "table_fqn": fqn,
                    "sample_rows": sample_rows,
                    "columns": cols,
                    "compute_candidates": compute_candidates,
                })
                st.session_state["_prof_active_run"] = result.get("run_id")
                st.session_state.pop("_prof_runs", None)
                st.rerun()
            except APIError as e:
                st.error(str(e))

    # ── Active run polling ────────────────────────────────────────────────────
    if active := st.session_state.get("_prof_active_run"):
        _poll_running(active)
        st.divider()

    # ── History ───────────────────────────────────────────────────────────────
    if "_prof_runs" not in st.session_state:
        try:
            st.session_state["_prof_runs"] = get_client().list_profiler_runs()
        except APIError as e:
            st.error(str(e), icon=":material/error:")
            st.session_state["_prof_runs"] = []

    runs = st.session_state["_prof_runs"]

    c1, c2 = st.columns([8, 1])
    c1.subheader(":material/history: Histórico de Runs")
    if c2.button(":material/refresh: Atualizar"):
        st.session_state.pop("_prof_runs", None)
        st.rerun()

    if not runs:
        st.info("Nenhum run de profiling encontrado. Inicie uma análise pelo menu lateral.", icon=":material/info:")
        return

    # Filters
    f1, f2 = st.columns([4, 2])
    search = f1.text_input("Filtrar tabela", placeholder="FQN...", label_visibility="collapsed")
    status_filter = f2.selectbox("Status", ["", "SUCCEEDED", "FAILED", "RUNNING", "PENDING"],
                                 format_func=lambda x: x or "Todos", label_visibility="collapsed")
    filtered = [r for r in runs
                if (not search or search.lower() in r.get("table_fqn", "").lower())
                and (not status_filter or r.get("status") == status_filter)]

    st.caption(f"{len(filtered)} run(s)")
    st.divider()

    for run in filtered:
        run_id = run.get("run_id", "—")
        fqn = run.get("table_fqn", "—")
        status = run.get("status", "—")
        started = run.get("started_at", "—")
        icon = _STATUS_ICON.get(status, ":material/info:")
        color = _STATUS_COLOR.get(status, "gray")

        with st.container(border=True):
            col1, col2, col3 = st.columns([5, 3, 2])
            col1.markdown(f"{icon} **`{fqn}`**")
            col1.caption(f"Run ID: `{run_id}` · {started}")
            col2.markdown(f":{color}[{status}]")
            if status == "SUCCEEDED" and col3.button("Ver resultados", key=f"view_{run_id}"):
                st.session_state["prof_view"] = "detail"
                st.session_state["prof_run_id"] = run_id
                st.session_state["prof_run_fqn"] = fqn
                st.rerun()
            elif status == "RUNNING":
                col3.caption("Em andamento...")


# ── DETAIL VIEW ───────────────────────────────────────────────────────────────

def _show_detail():
    run_id = st.session_state.get("prof_run_id", "—")
    fqn = st.session_state.get("prof_run_fqn", "—")

    if st.button(":material/arrow_back: Voltar ao histórico"):
        st.session_state["prof_view"] = "list"
        st.rerun()

    st.title(f":material/troubleshoot: Profiler — `{fqn}`")
    st.caption(f"Run ID: `{run_id}`")
    st.divider()

    cache_key = f"_prof_results_{run_id}"
    if cache_key not in st.session_state:
        with st.spinner("Carregando resultados..."):
            try:
                st.session_state[cache_key] = get_client().get_profiler_run_results(run_id)
            except APIError as e:
                st.error(str(e), icon=":material/error:"); return

    results = st.session_state[cache_key]
    columns_data = results.get("columns", [])
    row_count = results.get("row_count", "—")
    cols_count = results.get("columns_profiled", len(columns_data))

    # ── Summary metrics ───────────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    m1.metric("Linhas analisadas", f"{row_count:,}" if isinstance(row_count, int) else row_count)
    m2.metric("Colunas perfiladas", cols_count)
    all_candidates = [c for col in columns_data for c in col.get("candidates", [])]
    m3.metric("Candidatos a regras", len(all_candidates))

    st.divider()

    if not columns_data:
        st.info("Nenhuma estatística de coluna disponível.", icon=":material/info:")
        return

    # ── Column statistics table ───────────────────────────────────────────────
    st.subheader(":material/table_chart: Estatísticas por Coluna")
    df_rows = []
    for col in columns_data:
        df_rows.append({
            "Coluna": col.get("name", "—"),
            "Tipo": col.get("type", "—"),
            "Nulos %": f"{col.get('null_pct', 0):.1f}%",
            "Únicos %": f"{col.get('unique_pct', 0):.1f}%",
            "Mín": str(col.get("min", "—")),
            "Máx": str(col.get("max", "—")),
            "Média": f"{col.get('mean', 0):.2f}" if col.get("mean") is not None else "—",
            "Candidatos": len(col.get("candidates", [])),
        })
    df = pd.DataFrame(df_rows)
    st.dataframe(df, key="prof_col_table",
        column_config={
            "Coluna": st.column_config.TextColumn(width="medium"),
            "Nulos %": st.column_config.TextColumn(width="small"),
            "Únicos %": st.column_config.TextColumn(width="small"),
            "Candidatos": st.column_config.NumberColumn(width="small"),
        })

    # ── Per-column expandable detail ──────────────────────────────────────────
    st.divider()
    st.subheader(":material/rule: Candidatos a Regras por Coluna")

    has_candidates = False
    for col in columns_data:
        cands = col.get("candidates", [])
        if not cands:
            continue
        has_candidates = True
        col_name = col.get("name", "—")
        with st.expander(f"`{col_name}` — {len(cands)} candidato(s)"):
            for c in cands:
                conf = c.get("confidence", 0)
                color = "green" if conf >= 0.9 else "orange" if conf >= 0.7 else "red"
                st.markdown(f"- `{c.get('check')}` · :{color}[{conf*100:.0f}% confiança] — {c.get('rationale', '')}")

    if not has_candidates:
        st.info("Nenhum candidato a regra foi identificado para esta tabela.", icon=":material/search_off:")

    # ── Save as Rules ─────────────────────────────────────────────────────────
    if all_candidates:
        st.divider()
        enriched = [
            {**c, "column": col.get("name")}
            for col in columns_data
            for c in col.get("candidates", [])
        ]
        if st.button(":material/save: Salvar candidatos como Regras", type="primary"):
            _save_as_rules_dialog(enriched, fqn)


# ── Router ────────────────────────────────────────────────────────────────────

_view = st.session_state.get("prof_view", "list")
if _view == "list":     _show_list()
elif _view == "detail": _show_detail()
else:
    st.session_state["prof_view"] = "list"
    st.rerun()
