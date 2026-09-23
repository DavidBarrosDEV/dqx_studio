"""
Resultados DQ — score global, tendências e breakdown por dimensão/severidade/tabela.
"""

import pandas as pd
import streamlit as st

from core.api_client import APIError
from core.session import get_client
from core.utils import fmt_score

client = get_client()

st.title(":material/analytics: Resultados DQ")
st.caption("Visão consolidada da qualidade de dados do workspace.")
st.divider()

# ── Load global results ───────────────────────────────────────────────────────
try:
    results = client.get_global_results()
except APIError as e:
    st.error(str(e), icon=":material/error:")
    st.stop()

# ── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
avg_score = results.get("avg_score")
k1.metric("DQ Score Global", fmt_score(avg_score))
k2.metric("Tabelas Monitoradas", results.get("tables_monitored", "—"))
k3.metric("Checks com Falha", results.get("checks_failed", "—"))
k4.metric("Runs Hoje", results.get("runs_today", "—"))

st.divider()

# ── Trend ─────────────────────────────────────────────────────────────────────
trend = results.get("trend", [])
if trend:
    st.subheader(":material/trending_up: Tendência do DQ Score")
    labels = results.get("trend_labels", [f"T-{i}" for i in range(len(trend) - 1, -1, -1)])
    df_trend = pd.DataFrame({"Período": labels, "DQ Score (%)": trend}).set_index("Período")
    st.line_chart(df_trend)
else:
    st.info("Dados de tendência não disponíveis.", icon=":material/info:")

st.divider()

# ── By severity ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader(":material/warning: Falhas por Severidade")
    by_severity = results.get("by_severity", {})
    if by_severity:
        df_sev = pd.DataFrame(
            [{"Severidade": k, "Falhas": v} for k, v in by_severity.items()]
        ).set_index("Severidade")
        st.bar_chart(df_sev)
    else:
        st.caption("Sem dados.")

with col2:
    st.subheader(":material/table_chart: DQ Score por Tabela")
    try:
        tables = client.list_monitored_tables()
        if tables:
            df_tables = pd.DataFrame([
                {
                    "Tabela": t.get("table_fqn", ""),
                    "DQ Score (%)": t.get("dq_score"),
                    "Status": t.get("status", ""),
                    "Último run": t.get("last_run", "—"),
                }
                for t in tables if t.get("dq_score") is not None
            ]).sort_values("DQ Score (%)", ascending=True)

            st.bar_chart(df_tables.set_index("Tabela")[["DQ Score (%)"]])
        else:
            st.caption("Sem tabelas monitoradas.")
    except APIError as e:
        st.error(str(e))

st.divider()

# ── Per-table detail table ─────────────────────────────────────────────────────
st.subheader(":material/table_view: Detalhe por Tabela")
try:
    tables = client.list_monitored_tables()
    if tables:
        df_detail = pd.DataFrame([
            {
                "Tabela (FQN)": t.get("table_fqn", ""),
                "Status": t.get("status", ""),
                "DQ Score": fmt_score(t.get("dq_score")),
                "Último run": t.get("last_run", "—"),
            }
            for t in tables
        ])
        st.dataframe(
            df_detail,
            column_config={
                "Tabela (FQN)": st.column_config.TextColumn(width="large"),
                "Status": st.column_config.TextColumn(width="small"),
                "DQ Score": st.column_config.TextColumn(width="small"),
                "Último run": st.column_config.TextColumn(width="small"),
            },
        )
    else:
        st.info("Nenhuma tabela monitorada encontrada.", icon=":material/info:")
except APIError as e:
    st.error(str(e))
