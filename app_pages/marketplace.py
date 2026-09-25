"""
Marketplace — navegação e instalação de pacotes de regras pré-construídos.
Admin-only para instalação; todos podem visualizar.
"""

import streamlit as st

from core.api_client import APIError
from core.session import get_client, is_admin

st.title(":material/storefront: Marketplace")
st.caption("Pacotes de regras pré-construídas prontos para importar no Registry.")
st.divider()

client = get_client()

try:
    packs = client.list_marketplace_packs()
except APIError as e:
    st.error(str(e), icon=":material/error:")
    st.stop()

if not packs:
    st.info("Nenhum pacote disponível no momento.", icon=":material/search_off:")
    st.stop()

# ── Search ────────────────────────────────────────────────────────────────────
search = st.text_input("Pesquisar pacotes", placeholder="Nome ou descrição...", label_visibility="collapsed")
filtered = packs
if search:
    filtered = [p for p in packs if search.lower() in p.get("name", "").lower()
                or search.lower() in p.get("description", "").lower()]

st.caption(f"{len(filtered)} pacote(s) encontrado(s)")

# ── Pack cards ────────────────────────────────────────────────────────────────
for pack in filtered:
    pack_id = pack.get("id", "")
    name = pack.get("name", "—")
    description = pack.get("description", "")
    rule_count = pack.get("rule_count", 0)
    categories = pack.get("categories", [])

    with st.expander(f":material/inventory_2: **{name}** — {rule_count} regra(s)", expanded=False):
        st.markdown(description)

        if categories:
            st.caption("Categorias: " + " · ".join(f"`{c}`" for c in categories))

        # Rules preview
        rules_preview = pack.get("rules", [])
        if rules_preview:
            st.subheader("Regras incluídas")
            for r in rules_preview:
                st.markdown(f"- **{r.get('name', '—')}** — {r.get('description', '')}")
        else:
            st.caption(f"Este pacote contém {rule_count} regra(s). Instale para ver detalhes.")

        st.divider()

        col1, col2 = st.columns([3, 1])
        col1.caption(f"ID do pacote: `{pack_id}`")

        install_key = f"install_{pack_id}"
        confirm_key = f"confirm_{pack_id}"

        if is_admin():
            if not st.session_state.get(confirm_key):
                if col2.button(":material/download: Instalar", key=install_key, type="primary"):
                    st.session_state[confirm_key] = True
                    st.rerun()
            else:
                st.warning(f"Confirmar instalação de **{name}**? As regras serão adicionadas ao Registry como DRAFT.")
                c1, c2 = st.columns(2)
                if c1.button("Confirmar", key=f"ok_{pack_id}", type="primary"):
                    try:
                        client.batch_import_registry_rules({"pack_id": pack_id})
                        st.success(f"Pacote **{name}** instalado com sucesso! Regras disponíveis no Registry.")
                        st.session_state.pop(confirm_key, None)
                        st.rerun()
                    except APIError as e:
                        st.error(str(e))
                if c2.button("Cancelar", key=f"cancel_{pack_id}"):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
        else:
            col2.caption(":material/lock: Apenas admins podem instalar")
