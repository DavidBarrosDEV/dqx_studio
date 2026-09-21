import streamlit as st

from core.session import get_current_user, get_user_role, init_session, is_admin

st.set_page_config(
    page_title="DQX Studio",
    page_icon=":material/verified:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Bootstrap auth + API client (runs once per browser session) ───────────────
init_session()

# ── Fetch user info (cached in session_state) ─────────────────────────────────
user = get_current_user()
role = get_user_role()

display_name = user.get("display_name") or user.get("user_name") or user.get("email", "")
email = user.get("email", st.session_state.get("_dqx_auth_email", ""))

# ── Sidebar: user identity ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**{display_name}**")
    st.caption(f"{email} · {role.replace('_', ' ').title()}")
    st.divider()

# ── Navigation pages ──────────────────────────────────────────────────────────
pages: dict = {
    "": [
        st.Page("app_pages/home.py", title="Home", icon=":material/home:", default=True),
    ],
    "Qualidade de Dados": [
        st.Page("app_pages/registry_rules.py", title="Registry de Regras", icon=":material/rule:"),
        st.Page("app_pages/monitored_tables.py", title="Tabelas Monitoradas", icon=":material/table_chart:"),
        st.Page("app_pages/collections.py", title="Collections", icon=":material/folder_open:"),
    ],
    "Operações": [
        st.Page("app_pages/drafts.py", title="Review & Aprovar", icon=":material/approval:"),
        st.Page("app_pages/results.py", title="Resultados DQ", icon=":material/analytics:"),
        st.Page("app_pages/runs_history.py", title="Histórico de Runs", icon=":material/history:"),
    ],
    "Ferramentas": [
        st.Page("app_pages/profiler.py", title="Profiler", icon=":material/troubleshoot:"),
    ],
    "Conta": [
        st.Page("app_pages/profile.py", title="Perfil", icon=":material/person:"),
    ],
}

# Admin-only pages appear only when the user has the ADMIN role
if is_admin():
    pages["Ferramentas"].append(
        st.Page("app_pages/marketplace.py", title="Marketplace", icon=":material/storefront:")
    )
    pages["Conta"].append(
        st.Page("app_pages/settings.py", title="Configurações", icon=":material/settings:")
    )

pg = st.navigation(pages, position="sidebar")
pg.run()
