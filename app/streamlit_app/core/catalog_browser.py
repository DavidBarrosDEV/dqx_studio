"""
Reusable 3-level Unity Catalog browser (Catalog → Schema → Table).
Returns the fully-qualified table name or None if selection is incomplete.
"""

import streamlit as st

from core.api_client import APIError
from core.session import get_client


def catalog_browser(key_prefix: str = "cb") -> str | None:
    """
    Renders three selectboxes (catalog → schema → table).
    Returns "catalog.schema.table" when all three are selected, otherwise None.
    key_prefix must be unique per page to avoid session-state conflicts.
    """
    client = get_client()

    # ── Catalog ───────────────────────────────────────────────────────────────
    try:
        catalogs = client.list_catalogs()
    except APIError as e:
        st.error(f"Erro ao listar catálogos: {e}")
        return None

    catalog = st.selectbox(
        "Catálogo",
        [""] + (catalogs if isinstance(catalogs, list) else []),
        key=f"{key_prefix}_catalog",
    )
    if not catalog:
        return None

    # ── Schema ────────────────────────────────────────────────────────────────
    try:
        schemas = client.list_schemas(catalog)
    except APIError as e:
        st.error(f"Erro ao listar schemas: {e}")
        return None

    schema = st.selectbox(
        "Schema",
        [""] + (schemas if isinstance(schemas, list) else []),
        key=f"{key_prefix}_schema",
    )
    if not schema:
        return None

    # ── Table ─────────────────────────────────────────────────────────────────
    try:
        tables = client.list_tables(catalog, schema)
    except APIError as e:
        st.error(f"Erro ao listar tabelas: {e}")
        return None

    table = st.selectbox(
        "Tabela",
        [""] + (tables if isinstance(tables, list) else []),
        key=f"{key_prefix}_table",
    )
    if not table:
        return None

    return f"{catalog}.{schema}.{table}"
