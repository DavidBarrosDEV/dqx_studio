"""
Histórico de Runs — tabela paginada de todos os runs de validação e profiling.
Filtros por tabela, status, data. Review status inline. Link para job no Databricks.
"""

import pandas as pd
import streamlit as st

from core.api_client import APIError
from core.session import get_client
from core.utils import fmt_datetime, paginate, page_selector

@st.dialog("Registros em Quarentena", width="large")
def _quarantine_dialog(run_id: str):
    client = get_client()
    try:
        count_data = client.get_quarantine_count(run_id)
        total = count_data.get("count", 0)
        by_severity = count_data.get("by_severity", {})

        st.caption(f"Run: `{run_id}` · **{total}** registro(s) em quarentena")

        if by_severity:
            cols = st.columns(len(by_severity))
            for i, (sev, cnt) in enumerate(by_severity.items()):
                cols[i].metric(sev, cnt)

        st.divider()

        records = client.get_quarantine_records(run_id)
        if records:
            df_q = pd.DataFrame(records)
            st.dataframe(df_q, key=f"quarantine_{run_id}")

            # Download CSV
            try:
                csv_data = client.export_quarantine(run_id)
                st.download_button(
                    ":material/download: Exportar CSV",
                    data=csv_data if isinstance(csv_data, str) else str(csv_data),
                    file_name=f"quarantine_{run_id}.csv",
                    mime="text/csv",
                )
            except APIError:
                pass
        else:
            st.info("Nenhum registro em quarentena.", icon=":material/check_circle:")
    except APIError as e:
        st.error(str(e))


_RUN_STATUS_OPTS = ["", "SUCCEEDED", "FAILED", "RUNNING", "PENDING", "CANCELLED"]
_PAGE_SIZE = 15

client = get_client()

st.title(":material/history: Histórico de Runs")
st.caption("Todos os runs de validação e profiling do workspace.")
st.divider()

# ── Filters ───────────────────────────────────────────────────────────────────
f1, f2, f3 = st.columns([3, 2, 2])
search_table = f1.text_input("Tabela", placeholder="Filtrar por FQN...", label_visibility="collapsed")
status_filter = f2.selectbox("Status", _RUN_STATUS_OPTS, format_func=lambda x: x or "Todos os status", label_visibility="collapsed")
run_type = f3.selectbox("Tipo", ["", "validation", "profiler"], format_func=lambda x: x or "Todos os tipos", label_visibility="collapsed")

if st.button(":material/refresh: Atualizar"):
    st.session_state.pop("_runs_data", None)
    st.rerun()

# ── Load runs ─────────────────────────────────────────────────────────────────
if "_runs_data" not in st.session_state:
    try:
        dry_runs = client.list_dry_runs()
        profiler_runs = client.list_profiler_runs()

        for r in dry_runs:
            r["_type"] = "validation"
        for r in profiler_runs:
            r["_type"] = "profiler"

        st.session_state["_runs_data"] = dry_runs + profiler_runs
    except APIError as e:
        st.error(str(e), icon=":material/error:")
        st.session_state["_runs_data"] = []

runs = st.session_state["_runs_data"]

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = runs
if search_table:
    filtered = [r for r in filtered if search_table.lower() in r.get("table_fqn", "").lower()]
if status_filter:
    filtered = [r for r in filtered if r.get("status") == status_filter]
if run_type:
    filtered = [r for r in filtered if r.get("_type") == run_type]

# Sort newest first
filtered = sorted(filtered, key=lambda r: r.get("started_at", ""), reverse=True)

st.caption(f"**{len(filtered)}** run(s) encontrado(s)")
st.divider()

if not filtered:
    st.info("Nenhum run encontrado com os filtros selecionados.", icon=":material/search_off:")
    st.stop()

# ── Pagination ────────────────────────────────────────────────────────────────
page_items, total_pages = paginate(filtered, st.session_state.get("_runs_page", 1), _PAGE_SIZE)

# ── Review statuses ───────────────────────────────────────────────────────────
try:
    review_statuses = client.get_run_review_statuses()
    if not isinstance(review_statuses, list):
        review_statuses = []
except APIError:
    review_statuses = []

# ── Workspace host for Databricks links ───────────────────────────────────────
try:
    ws_host = client.get_workspace_host().get("host", "")
except APIError:
    ws_host = ""

# ── Run cards ─────────────────────────────────────────────────────────────────
_STATUS_ICON = {
    "SUCCEEDED": ":material/check_circle:",
    "FAILED": ":material/error:",
    "RUNNING": ":material/hourglass_top:",
    "PENDING": ":material/schedule:",
    "CANCELLED": ":material/cancel:",
}
_STATUS_COLOR = {
    "SUCCEEDED": "green", "FAILED": "red", "RUNNING": "blue",
    "PENDING": "blue", "CANCELLED": "gray",
}

for run in page_items:
    run_id = run.get("run_id", "—")
    table_fqn = run.get("table_fqn", "—")
    status = run.get("status", "—")
    started = fmt_datetime(run.get("started_at"))
    rtype = run.get("_type", "validation")
    dq_score = run.get("dq_score")
    job_id = run.get("job_id")

    icon = _STATUS_ICON.get(status, "")
    color = _STATUS_COLOR.get(status, "gray")

    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([4, 2, 2, 2])

        c1.markdown(f"{icon} **{run_id}**")
        c1.caption(f"`{table_fqn}` · {rtype.title()}")

        c2.markdown(f":{color}[{status}]")
        c2.caption(started)

        if dq_score is not None:
            c3.metric("DQ Score", f"{dq_score:.1f}%", label_visibility="collapsed")
            c3.caption(f"DQ Score: {dq_score:.1f}%")
        else:
            c3.caption("DQ Score: —")

        # Review status selector + Databricks link
        with c4:
            if review_statuses:
                current_review = run.get("review_status", "")
                opts = [""] + review_statuses
                sel = st.selectbox(
                    "Review",
                    opts,
                    index=opts.index(current_review) if current_review in opts else 0,
                    key=f"rev_{run_id}",
                    label_visibility="collapsed",
                )
                if sel != current_review:
                    run["review_status"] = sel

            if ws_host and job_id:
                job_url = f"{ws_host.rstrip('/')}/#job/{job_id}"
                st.markdown(f"[:material/open_in_new: Ver no Databricks]({job_url})")

            if status in ("SUCCEEDED", "FAILED"):
                if st.button(":material/bug_report: Quarentena", key=f"quar_{run_id}"):
                    _quarantine_dialog(run_id)

# ── Pagination controls ───────────────────────────────────────────────────────
if total_pages > 1:
    st.divider()
    current_page = page_selector("_runs_page", total_pages)
