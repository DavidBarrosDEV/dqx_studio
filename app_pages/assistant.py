"""
Assistente DQX — interface conversacional para criação e entendimento de regras.

Histórico armazenado em st.session_state["_ai_history"] como lista de
{"role": "user"|"assistant", "content": str}.
"""

import streamlit as st

from core.api_client import APIError
from core.session import get_client

_HISTORY_KEY = "_ai_history"
_ENDPOINT_KEY = "_ai_endpoint"

_SUGGESTIONS = [
    "Como crio uma regra para validar campos nulos?",
    "O que é DQ Score e como é calculado?",
    "Qual a diferença entre Collection e Tabela Monitorada?",
    "Quais funções de validação estão disponíveis?",
    "Como configuro um agendamento de validação?",
]


def _history() -> list:
    if _HISTORY_KEY not in st.session_state:
        st.session_state[_HISTORY_KEY] = []
    return st.session_state[_HISTORY_KEY]


def _send(user_text: str, endpoint: str):
    history = _history()
    history.append({"role": "user", "content": user_text})

    try:
        response = get_client().ai_chat(history, endpoint=endpoint or None)
        history.append({"role": "assistant", "content": response.get("content", "")})
    except APIError as e:
        history.append({
            "role": "assistant",
            "content": f":material/error: Erro ao contatar o assistente: {e}",
        })

    st.session_state[_HISTORY_KEY] = history


# ── Layout ────────────────────────────────────────────────────────────────────

st.title(":material/smart_toy: Assistente DQX")
st.caption("Converse com o assistente para criar e entender regras de qualidade de dados.")

# ── Sidebar de configuração ────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("Configurações do assistente")

    try:
        endpoints = get_client().list_ai_serving_endpoints()
    except APIError:
        endpoints = []

    if endpoints:
        selected_endpoint = st.selectbox(
            "Modelo",
            endpoints,
            key=_ENDPOINT_KEY,
            help="Endpoint de serving do Databricks a usar.",
        )
    else:
        selected_endpoint = ""
        st.caption("Nenhum endpoint disponível.")

    st.divider()

    if st.button(":material/delete_sweep: Limpar histórico", use_container_width=True):
        st.session_state[_HISTORY_KEY] = []
        st.rerun()

    st.divider()
    st.caption("**Sugestões de perguntas:**")
    for suggestion in _SUGGESTIONS:
        if st.button(suggestion, use_container_width=True, key=f"sug_{suggestion[:20]}"):
            _send(suggestion, selected_endpoint)
            st.rerun()

# ── Área de chat ──────────────────────────────────────────────────────────────

history = _history()

if not history:
    with st.chat_message("assistant"):
        st.markdown(
            "Olá! Sou o assistente do **DQX Studio**. Posso ajudar você a criar regras de qualidade, "
            "entender os resultados e configurar monitoramentos.\n\n"
            "Use as sugestões no painel lateral ou escreva sua pergunta abaixo."
        )
else:
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────

if prompt := st.chat_input("Escreva sua pergunta..."):
    _send(prompt, selected_endpoint)
    st.rerun()
