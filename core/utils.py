"""
Shared utilities: formatters, badge helpers, pagination, constants.
"""

from datetime import datetime


# ── Badge / status constants ──────────────────────────────────────────────────

STATUS_COLOR: dict[str, str] = {
    "DRAFT": "gray",
    "SUBMITTED": "blue",
    "APPROVED": "green",
    "REJECTED": "red",
    "DEPRECATED": "orange",
    "REVOKED": "orange",
}

SEVERITY_COLOR: dict[str, str] = {
    "CRITICAL": "red",
    "HIGH": "orange",
    "MEDIUM": "yellow",
    "LOW": "blue",
    "INFO": "gray",
}

RUN_STATUS_COLOR: dict[str, str] = {
    "SUCCEEDED": "green",
    "FAILED": "red",
    "RUNNING": "blue",
    "PENDING": "blue",
    "CANCELLED": "gray",
    "SKIPPED": "gray",
}

ALL_STATUSES = ["DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "DEPRECATED"]
ALL_SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]


# ── Formatters ────────────────────────────────────────────────────────────────

def fmt_score(score: float | None, decimals: int = 1) -> str:
    """Format a DQ score float to a percentage string, or '—' if None."""
    if score is None:
        return "—"
    return f"{score:.{decimals}f}%"


def fmt_fqn(catalog: str, schema: str, table: str) -> str:
    """Build a Unity Catalog fully-qualified table name."""
    return f"{catalog}.{schema}.{table}"


def fmt_datetime(iso_str: str | None) -> str:
    """Format an ISO-8601 string to a readable local format."""
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return iso_str


def fmt_date(iso_str: str | None) -> str:
    """Format an ISO-8601 date string to dd/mm/yyyy."""
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.split("T")[0])
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return iso_str


def badge(text: str, color_map: dict) -> str:
    """Return a Streamlit colored badge string, e.g. ':green[APPROVED]'."""
    color = color_map.get(text, "gray")
    return f":{color}[{text}]"


def status_badge(status: str) -> str:
    return badge(status, STATUS_COLOR)


def severity_badge(severity: str) -> str:
    return badge(severity, SEVERITY_COLOR)


def run_status_badge(status: str) -> str:
    return badge(status, RUN_STATUS_COLOR)


# ── Pagination ────────────────────────────────────────────────────────────────

def paginate(items: list, page: int, page_size: int = 20) -> tuple[list, int]:
    """
    Slice a list for the given 1-based page.
    Returns (page_items, total_pages).
    """
    total = len(items)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    return items[start : start + page_size], total_pages


def page_selector(key: str, total_pages: int) -> int:
    """
    Renders prev/next buttons and returns the current 1-based page number.
    Stores state in st.session_state[key].
    """
    import streamlit as st

    if key not in st.session_state:
        st.session_state[key] = 1

    current = st.session_state[key]

    col1, col2, col3 = st.columns([1, 2, 1])
    if col1.button(":material/chevron_left:", key=f"{key}_prev", disabled=current <= 1):
        st.session_state[key] = current - 1
        st.rerun()
    col2.markdown(f"<center>Página {current} de {total_pages}</center>", unsafe_allow_html=True)
    if col3.button(":material/chevron_right:", key=f"{key}_next", disabled=current >= total_pages):
        st.session_state[key] = current + 1
        st.rerun()

    return st.session_state[key]
