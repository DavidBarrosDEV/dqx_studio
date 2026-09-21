import streamlit as st

from core.api_client import APIError
from core.session import get_client, get_current_user

user = get_current_user()
display_name = user.get("display_name") or user.get("user_name") or "Usuário"

st.title(f"Olá, {display_name} :material/waving_hand:")
st.caption("Bem-vindo ao DQX Studio")

st.divider()

# ── Stats ─────────────────────────────────────────────────────────────────────
try:
    stats = get_client().get_home_stats()
    cols = st.columns(4)
    stat_items = [
        ("Tabelas monitoradas", stats.get("monitored_tables", "—"), ":material/table_chart:"),
        ("Regras ativas", stats.get("active_rules", "—"), ":material/rule:"),
        ("Collections", stats.get("collections", "—"), ":material/folder_open:"),
        ("Score médio DQ", stats.get("avg_dq_score", "—"), ":material/analytics:"),
    ]
    for col, (label, value, icon) in zip(cols, stat_items):
        col.metric(label=f"{icon}  {label}", value=value)
except APIError as e:
    st.warning(f"Não foi possível carregar estatísticas: {e}", icon=":material/warning:")

st.divider()

# ── Quick access ──────────────────────────────────────────────────────────────
st.subheader("Acesso rápido")

c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.markdown(":material/rule: **Registry de Regras**")
        st.caption("Gerencie regras de qualidade versionadas")
with c2:
    with st.container(border=True):
        st.markdown(":material/table_chart: **Tabelas Monitoradas**")
        st.caption("Configure e monitore tabelas Delta")
with c3:
    with st.container(border=True):
        st.markdown(":material/folder_open: **Collections**")
        st.caption("Agrupe tabelas em produtos de dados")
