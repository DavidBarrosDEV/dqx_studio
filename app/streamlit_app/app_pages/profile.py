"""
Perfil do usuário — informações, grupos, papel e preferências de idioma.
"""

import streamlit as st

from core.api_client import APIError
from core.session import get_client, get_current_user, get_user_role

_LANGS = {
    "pt-BR": "Português (Brasil)",
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
}

# ── Page ──────────────────────────────────────────────────────────────────────

st.title(":material/person: Perfil")

user = get_current_user()
role = get_user_role()

display_name = user.get("display_name") or user.get("user_name") or "—"
email = user.get("email") or st.session_state.get("_dqx_auth_email", "—")
groups = [g.get("display", g) if isinstance(g, dict) else g for g in user.get("groups", [])]

# ── Info card ─────────────────────────────────────────────────────────────────
with st.container(border=True):
    c1, c2 = st.columns([1, 4])
    c1.markdown("### :material/account_circle:")
    c2.markdown(f"### {display_name}")
    c2.caption(email)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Papel no DQX Studio")
    role_labels = {
        "ADMIN": ":red[Admin]",
        "RULE_APPROVER": ":blue[Rule Approver]",
        "RULE_AUTHOR": ":green[Rule Author]",
        "VIEWER": ":gray[Viewer]",
    }
    st.markdown(f"**{role_labels.get(role, role)}**")
    st.caption("Papel atribuído pelo administrador do workspace.")

with col2:
    st.subheader("Grupos do Workspace")
    if groups:
        for g in groups:
            st.markdown(f"• `{g}`")
    else:
        st.caption("Sem grupos atribuídos.")

st.divider()

# ── Preferências ──────────────────────────────────────────────────────────────
st.subheader(":material/language: Preferências")

current_lang = st.session_state.get("_ui_lang", "pt-BR")
lang_names = list(_LANGS.values())
lang_codes = list(_LANGS.keys())

with st.form("form_prefs"):
    sel_lang = st.selectbox(
        "Idioma da interface",
        lang_names,
        index=lang_codes.index(current_lang) if current_lang in lang_codes else 0,
        help="Preferência salva localmente na sessão.",
    )
    if st.form_submit_button("Salvar preferências", type="primary"):
        sel_code = lang_codes[lang_names.index(sel_lang)]
        st.session_state["_ui_lang"] = sel_code
        st.success(f"Idioma definido: {sel_lang}")
        st.rerun()

st.divider()
st.caption("As informações de identidade (nome, e-mail, grupos) são gerenciadas pelo Databricks e não podem ser editadas aqui.")
