"""
DQ Insights — consultas em linguagem natural aos resultados e métricas de qualidade.

Cada mensagem do assistente tem estrutura:
  {
    id: str,
    role: "user" | "assistant",
    content: str,
    job_id: str | None,
    status: "pending" | "succeeded" | "failed",
    result: dict | None,   # type, data, message, parts
    feedback: None | "up" | "down",
  }

Polling via @st.fragment(run_every=3) enquanto há jobs pendentes.
"""

import uuid

import pandas as pd
import streamlit as st

from core.api_client import APIError
from core.session import get_client

_HIST_KEY = "_ins_history"
_PENDING_KEY = "_ins_pending"
_ENTITIES_KEY = "_ins_entities"

_QUICK_QUERIES = [
    "Qual o DQ Score global?",
    "Mostre a tendência de qualidade nos últimos meses",
    "Quais checks falharam hoje?",
    "DQ Score por tabela monitorada",
    "Distribuição de falhas por severidade",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _history() -> list:
    if _HIST_KEY not in st.session_state:
        st.session_state[_HIST_KEY] = []
    return st.session_state[_HIST_KEY]


def _pending() -> set:
    if _PENDING_KEY not in st.session_state:
        st.session_state[_PENDING_KEY] = set()
    return st.session_state[_PENDING_KEY]


def _load_entities() -> dict:
    if _ENTITIES_KEY not in st.session_state:
        try:
            st.session_state[_ENTITIES_KEY] = get_client().list_mentionable_entities()
        except APIError:
            st.session_state[_ENTITIES_KEY] = {"tables": [], "rules": [], "collections": []}
    return st.session_state[_ENTITIES_KEY]


def _parse_mentions(text: str, entities: dict) -> tuple[str, dict]:
    """Extract @mentions from text, return cleaned text and context dict."""
    context = {"mentioned": []}
    all_entities = (
        entities.get("tables", [])
        + entities.get("rules", [])
        + entities.get("collections", [])
    )
    entity_map = {e["label"].lower(): e for e in all_entities}

    words = text.split()
    mentions = []
    clean_words = []
    for w in words:
        if w.startswith("@"):
            name = w[1:].lower()
            match = entity_map.get(name)
            if match:
                mentions.append(match)
                clean_words.append(f"**{match['label']}**")
            else:
                clean_words.append(w)
        else:
            clean_words.append(w)

    if mentions:
        context["mentioned"] = mentions
    return " ".join(clean_words), context


def _submit_query(question: str):
    entities = _load_entities()
    clean_question, context = _parse_mentions(question, entities)

    history = _history()
    pending = _pending()

    user_id = uuid.uuid4().hex
    history.append({
        "id": user_id,
        "role": "user",
        "content": clean_question,
        "job_id": None,
        "status": "succeeded",
        "result": None,
        "feedback": None,
    })

    try:
        resp = get_client().submit_analytics_query(question, context=context)
        job_id = resp.get("job_id")
        status = resp.get("status", "PENDING").upper()

        msg_id = uuid.uuid4().hex
        if status == "SUCCEEDED":
            history.append({
                "id": msg_id,
                "role": "assistant",
                "content": resp.get("result", {}).get("message", ""),
                "job_id": job_id,
                "status": "succeeded",
                "result": resp.get("result"),
                "feedback": None,
            })
        else:
            history.append({
                "id": msg_id,
                "role": "assistant",
                "content": "Processando sua consulta...",
                "job_id": job_id,
                "status": "pending",
                "result": None,
                "feedback": None,
            })
            pending.add(job_id)

    except APIError as e:
        history.append({
            "id": uuid.uuid4().hex,
            "role": "assistant",
            "content": f"Erro ao processar consulta: {e}",
            "job_id": None,
            "status": "failed",
            "result": None,
            "feedback": None,
        })

    st.session_state[_HIST_KEY] = history
    st.session_state[_PENDING_KEY] = pending


# ── Result renderer ───────────────────────────────────────────────────────────

def _render_result(result: dict):
    if not result:
        return

    rtype = result.get("type", "text")

    if rtype == "metrics":
        _render_metrics(result["data"]["metrics"])

    elif rtype == "table":
        data = result["data"]
        df = pd.DataFrame(data["rows"], columns=data["columns"])
        st.dataframe(df, use_container_width=True)

    elif rtype == "chart":
        _render_chart(result)

    elif rtype == "mixed":
        for part in result.get("parts", []):
            _render_result(part)

    sql = result.get("sql")
    if sql:
        with st.expander(":material/code: SQL gerado"):
            st.code(sql, language="sql")


def _render_metrics(metrics: list):
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        delta = m.get("delta")
        col.metric(label=m["label"], value=str(m["value"]), delta=delta)


def _render_chart(result: dict):
    chart_type = result.get("chart_type", "bar")
    data = result.get("data", {})
    labels = data.get("labels", [])
    series = data.get("series", [])

    if not labels or not series:
        return

    df = pd.DataFrame({"Categoria": labels})
    for s in series:
        df[s["name"]] = s["values"]
    df = df.set_index("Categoria")

    if chart_type == "line":
        st.line_chart(df)
    else:
        st.bar_chart(df)


# ── Feedback widget ───────────────────────────────────────────────────────────

def _render_feedback(msg: dict):
    if msg.get("feedback"):
        icon = ":material/thumb_up:" if msg["feedback"] == "up" else ":material/thumb_down:"
        st.caption(f"{icon} Feedback registrado")
        return

    job_id = msg.get("job_id")
    msg_id = msg["id"]

    with st.container(horizontal=True):
        st.caption("Esta resposta foi útil?")
        if st.button(":material/thumb_up:", key=f"up_{msg_id}", help="Útil"):
            if job_id:
                try:
                    get_client().submit_analytics_feedback(job_id, "up")
                except APIError:
                    pass
            msg["feedback"] = "up"
            st.rerun()
        if st.button(":material/thumb_down:", key=f"dn_{msg_id}", help="Não útil"):
            if job_id:
                try:
                    get_client().submit_analytics_feedback(job_id, "down")
                except APIError:
                    pass
            msg["feedback"] = "down"
            st.rerun()


# ── Polling fragment ──────────────────────────────────────────────────────────

def _poll_pending():
    pending = _pending()
    if not pending:
        return

    @st.fragment(run_every=3)
    def _poller():
        history = _history()
        still_pending = set()
        updated = False

        for msg in history:
            if msg.get("status") == "pending" and msg.get("job_id") in pending:
                try:
                    resp = get_client().get_analytics_query_status(msg["job_id"])
                    status = resp.get("status", "PENDING").upper()
                    if status == "SUCCEEDED":
                        result = resp.get("result", {})
                        msg["content"] = result.get("message", "Consulta concluída.")
                        msg["result"] = result
                        msg["status"] = "succeeded"
                        updated = True
                    elif status == "FAILED":
                        msg["content"] = "A consulta falhou. Tente novamente."
                        msg["status"] = "failed"
                        updated = True
                    else:
                        still_pending.add(msg["job_id"])
                except APIError:
                    still_pending.add(msg["job_id"])

        st.session_state[_HIST_KEY] = history
        st.session_state[_PENDING_KEY] = still_pending

        if updated:
            st.rerun()
        elif still_pending:
            st.caption(":material/hourglass_top: Aguardando resultados...")

    _poller()


# ── Page layout ───────────────────────────────────────────────────────────────

st.title(":material/query_stats: DQ Insights")
st.caption("Consulte métricas e resultados de qualidade em linguagem natural.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("Consultas rápidas")
    for q in _QUICK_QUERIES:
        if st.button(q, use_container_width=True, key=f"qq_{q[:20]}"):
            _submit_query(q)
            st.rerun()

    st.divider()

    # @ Entities panel
    entities = _load_entities()
    all_ent = (
        [f"@{e['label']}" for e in entities.get("tables", [])]
        + [f"@{e['label']}" for e in entities.get("rules", [])]
        + [f"@{e['label']}" for e in entities.get("collections", [])]
    )
    if all_ent:
        st.subheader("Entidades disponíveis (@)")
        st.caption("Use @nome na sua pergunta para referenciar uma entidade.")
        for ent in all_ent:
            st.caption(f"• `{ent}`")

    st.divider()
    if st.button(":material/delete_sweep: Limpar conversa", use_container_width=True):
        st.session_state.pop(_HIST_KEY, None)
        st.session_state.pop(_PENDING_KEY, None)
        st.rerun()

# ── Chat area ─────────────────────────────────────────────────────────────────

history = _history()

if not history:
    with st.chat_message("assistant"):
        st.markdown(
            "Olá! Sou o **DQ Insights**, seu assistente analítico.\n\n"
            "Faça perguntas sobre seus dados de qualidade, como:\n"
            "- *Qual o DQ Score global?*\n"
            "- *Quais tabelas têm mais falhas críticas?*\n"
            "- *Mostre a tendência de qualidade no último mês*\n\n"
            "Você também pode usar **@** para referenciar tabelas, regras ou collections diretamente."
        )
else:
    for msg in history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])

        else:  # assistant
            with st.chat_message("assistant"):
                if msg["status"] == "pending":
                    st.status("Processando consulta...", state="running")

                elif msg["status"] == "failed":
                    st.error(msg["content"], icon=":material/error:")

                else:
                    if msg["content"]:
                        st.markdown(msg["content"])
                    _render_result(msg.get("result"))
                    st.divider()
                    _render_feedback(msg)

# ── Polling (se houver jobs pendentes) ────────────────────────────────────────
_poll_pending()

# ── Input ─────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Faça uma pergunta sobre seus dados de qualidade... (use @ para mencionar entidades)"):
    _submit_query(prompt)
    st.rerun()
