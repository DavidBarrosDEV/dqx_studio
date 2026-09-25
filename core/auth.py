import os
from dataclasses import dataclass

import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class AuthContext:
    token: str
    email: str


def get_auth_context() -> AuthContext:
    """Read auth from Databricks Apps headers (prod) or env vars (local dev)."""
    headers = st.context.headers

    token = headers.get("X-Forwarded-Access-Token") or os.getenv("DATABRICKS_TOKEN", "")
    email = headers.get("X-Forwarded-Email") or os.getenv("DQX_DEV_USER_EMAIL", "dev@localhost")

    if not token:
        st.error(
            "**Autenticação necessária.** "
            "Em desenvolvimento local, defina `DATABRICKS_TOKEN` com um PAT do Databricks.",
            icon=":material/lock:",
        )
        st.stop()

    return AuthContext(token=token, email=email)
