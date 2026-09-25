import os

import streamlit as st

from core.api_client import APIError, DQXClient
from core.auth import get_auth_context

_MOCK = os.getenv("DQX_MOCK", "").lower() in ("1", "true", "yes")


def init_session() -> None:
    """Bootstrap auth + API client. Called once per session in streamlit_app.py."""
    if "_dqx_client" not in st.session_state:
        if _MOCK:
            from core.mock_client import DQXMockClient
            st.session_state["_dqx_client"] = DQXMockClient()
            st.session_state["_dqx_auth_email"] = "dev@mock.local"
        else:
            auth = get_auth_context()
            base_url = os.getenv("DQX_API_BASE_URL", "http://localhost:8000")
            st.session_state["_dqx_client"] = DQXClient(base_url=base_url, token=auth.token)
            st.session_state["_dqx_auth_email"] = auth.email


def get_client() -> DQXClient:
    return st.session_state["_dqx_client"]


def get_current_user() -> dict:
    """Fetch and cache the current user. Returns user dict."""
    if "_dqx_user" not in st.session_state:
        try:
            st.session_state["_dqx_user"] = get_client().get_current_user()
        except APIError as e:
            st.error(f"Erro ao buscar usuário: {e}", icon=":material/error:")
            st.stop()
    return st.session_state["_dqx_user"]


def get_user_role() -> str:
    """Fetch and cache the current user role. Returns role string (e.g. 'ADMIN')."""
    if "_dqx_role" not in st.session_state:
        try:
            role_data = get_client().get_current_user_role()
            st.session_state["_dqx_role"] = role_data.get("role", "VIEWER")
        except APIError:
            st.session_state["_dqx_role"] = "VIEWER"
    return st.session_state["_dqx_role"]


def is_admin() -> bool:
    return get_user_role() == "ADMIN"


def clear_cache(key: str) -> None:
    """Remove a specific key from session state to force a refresh."""
    st.session_state.pop(key, None)
