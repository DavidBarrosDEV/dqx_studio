import streamlit as st

from core.session import is_admin

if not is_admin():
    st.error("Acesso restrito a administradores.", icon=":material/lock:")
    st.stop()

# Sprint 1
st.title(":material/storefront: Marketplace")
st.info(
    "Esta página será implementada no **Sprint 1**. "
    "Navegação e instalação de pacotes de regras pré-construídos.",
    icon=":material/construction:",
)
