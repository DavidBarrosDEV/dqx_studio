"""
i18n básico — dicionário Python com suporte a pt-BR (padrão) e en.

Uso:
    from core.i18n import t
    st.button(t("save"))
"""

import streamlit as st

_STRINGS: dict[str, dict[str, str]] = {
    "pt": {
        # Actions
        "save":          "Salvar",
        "cancel":        "Cancelar",
        "delete":        "Excluir",
        "edit":          "Editar",
        "create":        "Criar",
        "back":          "Voltar",
        "refresh":       "Atualizar",
        "search":        "Pesquisar",
        "submit":        "Submeter",
        "approve":       "Aprovar",
        "reject":        "Rejeitar",
        "export":        "Exportar",
        "import":        "Importar",
        "confirm":       "Confirmar",
        "run":           "Executar",
        "save_draft":    "Salvar como rascunho",
        "new":           "+ Novo",
        # Status
        "draft":         "Rascunho",
        "submitted":     "Submetido",
        "approved":      "Aprovado",
        "rejected":      "Rejeitado",
        "deprecated":    "Deprecado",
        "revoked":       "Revogado",
        "running":       "Em execução",
        "succeeded":     "Concluído",
        "failed":        "Falhou",
        "pending":       "Aguardando",
        # Severity
        "critical":      "Crítico",
        "high":          "Alto",
        "medium":        "Médio",
        "low":           "Baixo",
        # Sections
        "home":          "Home",
        "rules":         "Registry de Regras",
        "tables":        "Tabelas Monitoradas",
        "collections":   "Collections",
        "results":       "Resultados DQ",
        "profiler":      "Profiler",
        "assistant":     "Assistente DQX",
        "settings":      "Configurações",
        "profile":       "Perfil",
        # Errors / empty states
        "no_results":    "Nenhum resultado encontrado.",
        "error_load":    "Erro ao carregar dados.",
        "no_permission": "Você não tem permissão para realizar esta ação.",
        "loading":       "Carregando...",
        # Common fields
        "name":          "Nome",
        "description":   "Descrição",
        "severity":      "Severidade",
        "status":        "Status",
        "created_at":    "Criado em",
        "table":         "Tabela",
        "column":        "Coluna",
        "rationale":     "Motivo",
        # Profiler
        "prof_new":      "Nova Análise",
        "prof_results":  "Ver resultados",
        "prof_save_rules": "Salvar como Regras",
        "prof_candidates": "Candidatos a regras",
        # Misc
        "language":      "Idioma",
    },
    "en": {
        # Actions
        "save":          "Save",
        "cancel":        "Cancel",
        "delete":        "Delete",
        "edit":          "Edit",
        "create":        "Create",
        "back":          "Back",
        "refresh":       "Refresh",
        "search":        "Search",
        "submit":        "Submit",
        "approve":       "Approve",
        "reject":        "Reject",
        "export":        "Export",
        "import":        "Import",
        "confirm":       "Confirm",
        "run":           "Run",
        "save_draft":    "Save as draft",
        "new":           "+ New",
        # Status
        "draft":         "Draft",
        "submitted":     "Submitted",
        "approved":      "Approved",
        "rejected":      "Rejected",
        "deprecated":    "Deprecated",
        "revoked":       "Revoked",
        "running":       "Running",
        "succeeded":     "Succeeded",
        "failed":        "Failed",
        "pending":       "Pending",
        # Severity
        "critical":      "Critical",
        "high":          "High",
        "medium":        "Medium",
        "low":           "Low",
        # Sections
        "home":          "Home",
        "rules":         "Rule Registry",
        "tables":        "Monitored Tables",
        "collections":   "Collections",
        "results":       "DQ Results",
        "profiler":      "Profiler",
        "assistant":     "DQX Assistant",
        "settings":      "Settings",
        "profile":       "Profile",
        # Errors / empty states
        "no_results":    "No results found.",
        "error_load":    "Error loading data.",
        "no_permission": "You don't have permission to perform this action.",
        "loading":       "Loading...",
        # Common fields
        "name":          "Name",
        "description":   "Description",
        "severity":      "Severity",
        "status":        "Status",
        "created_at":    "Created at",
        "table":         "Table",
        "column":        "Column",
        "rationale":     "Rationale",
        # Profiler
        "prof_new":      "New Analysis",
        "prof_results":  "View results",
        "prof_save_rules": "Save as Rules",
        "prof_candidates": "Rule candidates",
        # Misc
        "language":      "Language",
    },
}

_SUPPORTED = {"pt": "Português (pt-BR)", "en": "English (en)"}


def t(key: str) -> str:
    """Return the translated string for `key` in the current session language."""
    lang = st.session_state.get("_lang", "pt")
    return _STRINGS.get(lang, _STRINGS["pt"]).get(key, key)


def lang_selector(sidebar: bool = True) -> None:
    """Render a compact language toggle. Call from streamlit_app.py sidebar."""
    container = st.sidebar if sidebar else st
    with container:
        current = st.session_state.get("_lang", "pt")
        opts = list(_SUPPORTED.keys())
        labels = list(_SUPPORTED.values())
        idx = opts.index(current) if current in opts else 0
        chosen = st.radio(
            t("language"),
            opts,
            index=idx,
            format_func=lambda k: _SUPPORTED[k],
            horizontal=True,
            key="_lang_radio",
            label_visibility="collapsed",
        )
        if chosen != current:
            st.session_state["_lang"] = chosen
            st.rerun()
