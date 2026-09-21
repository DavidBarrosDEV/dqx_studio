import streamlit as st

from core.session import get_current_user

# Sprint 1
st.title(":material/person: Perfil")

user = get_current_user()

with st.container(border=True):
    st.markdown(f"**Nome:** {user.get('display_name', '—')}")
    st.markdown(f"**E-mail:** {user.get('email', '—')}")
    groups = user.get("groups", [])
    if groups:
        st.markdown(f"**Grupos:** {', '.join(g.get('display', g) if isinstance(g, dict) else g for g in groups)}")

st.info(
    "Seleção de idioma e demais configurações de perfil serão adicionadas no **Sprint 1**.",
    icon=":material/construction:",
)
