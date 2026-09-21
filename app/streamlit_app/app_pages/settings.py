import streamlit as st

from core.session import is_admin

if not is_admin():
    st.error("Acesso restrito a administradores.", icon=":material/lock:")
    st.stop()

# Sprint 4
st.title(":material/settings: Configurações")
st.info(
    "Esta página será implementada no **Sprint 4**. "
    "Timezone, Label Definitions, AI Settings, Compute, RBAC e demais configurações do workspace.",
    icon=":material/construction:",
)
