# Fase 2 — Cronograma de Migração React → Streamlit

> DQX Studio · React → Streamlit Migration  
> Data base: 2026-09-21

---

## Critérios de Priorização

| Critério | Peso |
|----------|------|
| Valor de negócio (tela mais usada) | Alto |
| Complexidade técnica (nº de APIs + interatividade) | Alto |
| Dependências entre telas | Médio |
| Risco de regressão | Médio |

Ordem geral: **infraestrutura → telas simples → telas médias → telas complexas**

---

## Estrutura de Fases

```
Sprint 0  — Infraestrutura & fundação (sem telas)
Sprint 1  — Telas de baixa complexidade
Sprint 2  — Listagens principais
Sprint 3  — Detalhes com tabs (fluxo de aprovação)
Sprint 4  — Settings
Sprint 5  — Editor de Regras (componente mais complexo)
Sprint 6  — Profiler + Marketplace + ajustes finais
```

---

## Sprint 0 — Infraestrutura e Fundação

**Duração estimada: 5 dias**  
**Objetivo:** app Streamlit "esqueleto" funcionando, sem lógica de negócio.

| Tarefa | Esforço | Entregável |
|--------|---------|-----------|
| Estrutura de pastas e `app.py` principal | 0,5 dia | Projeto Streamlit rodando |
| Cliente HTTP Python (`api_client.py`) — wrapper sobre `requests`/`httpx` com base URL `/api/v1` e timeout | 1 dia | Todas as chamadas centralizadas |
| Autenticação — ler headers `X-Forwarded-User` / `X-Forwarded-Email` do Databricks Apps; injetar token Bearer nas chamadas | 0,5 dia | Sessão autenticada |
| Gerenciamento de sessão — `st.session_state` como substituto do React Query cache (TTL simples por chave) | 1 dia | Cache client-side |
| Layout base — sidebar com navegação, logo, user menu, dark/light via CSS injetado | 1 dia | Shell visual |
| Utilitários — formatadores de data/FQN/score, helpers de paginação, constantes de badges | 1 dia | Lib compartilhada |

**Dependências:** nenhuma  
**Risco:** configuração do Databricks Apps para passar headers — validar no ambiente alvo antes de avançar.

---

## Sprint 1 — Telas de Baixa Complexidade

**Duração estimada: 5 dias**  
**Telas:** Home · Profile · Marketplace · Fila de Aprovação (Drafts)

### Home (`/home`) — 1 dia
- APIs: `GET /current-user`, `GET /home/stats`
- Componentes: stat cards (`st.metric`), grid de links (`st.columns`)
- Sem interatividade — só exibição

### Profile (`/profile`) — 0,5 dia
- APIs: `GET /current-user`
- Seletor de idioma: `st.selectbox` + `st.session_state`
- Exibição de grupos/role em tabela simples

### Marketplace (`/marketplace`) — 1 dia
- APIs: `GET /marketplace/packs`
- Lista de packs com `st.expander` por pack, botão de instalação
- Guard de admin: redirecionar se não for admin

### Fila de Aprovação — Drafts (`/rules/drafts`) — 2,5 dias
- APIs: `GET /registry-rules`, `GET /monitored-tables`, `GET /data-products` (filtro status=pending)
- Lifecycle actions: submit/approve/reject com `st.text_area` para rationale
- Diff simplificado: exibir JSON/YAML antes × depois em `st.code`

**Dependências:** Sprint 0  
**Risco:** baixo

---

## Sprint 2 — Listagens Principais

**Duração estimada: 7 dias**  
**Telas:** Registry Rules list · Monitored Tables list · Collections list · Runs History

### Registry Rules List (`/registry-rules`) — 2 dias
- APIs: `GET /registry-rules`, `DELETE`, lifecycle batch actions, `GET /export/registry-rules`
- `st.dataframe` com filtros (status, label, busca texto)
- Bulk actions via `st.multiselect` + botões de ação
- Export: `st.download_button`

### Monitored Tables List (`/monitored-tables`) — 2 dias
- APIs: `GET /monitored-tables`, `DELETE`, lifecycle, run, export
- Mesma estrutura da lista de Registry Rules
- Filtros por status/score

### Collections List (`/collections`) — 1,5 dia
- APIs: `GET /data-products`, `DELETE`, lifecycle, run, export
- Filtro por DQ score

### Runs History (`/runs-history`) — 1,5 dia
- APIs: `GET /dryrun/runs`, `GET /profiler/runs`, `GET /schedules`, `GET /config/run-review-statuses`
- Tabela paginada com filtros (tabela, status, data, coleção)
- Review status: `st.selectbox` inline
- Link para job no Databricks via `workspace-host`

**Dependências:** Sprint 0  
**Risco:** paginação e filtros combinados exigem cuidado com `st.session_state`

---

## Sprint 3 — Páginas de Detalhe (Tabs + Aprovação)

**Duração estimada: 10 dias**  
**Telas:** Registry Rule detail · Monitored Table detail · Collection detail

### Registry Rule Detail (`/registry-rules/$ruleId`) — 3 dias
- APIs: GET/PUT/DELETE rule, versions, lifecycle, comments, export, DQ results, DQ score
- `st.tabs`: Detalhes · Versões · Resultados · Comentários
- Edição inline de campos simples
- Lifecycle buttons com `LifecycleRationaleDialog` → `st.text_area` em `st.dialog`
- Export YAML/ODCS via `st.download_button`

### Monitored Table Detail (`/monitored-tables/$bindingId`) — 4 dias
- APIs: ~27 endpoints (o mais amplo da aplicação)
- `st.tabs`: Rules Applied · Profiling · Results · Scheduling · History · Permissions · Comments
- Tab Rules: listar regras aplicadas, version pins, severity overrides, add/remove rules
- Tab Scheduling: cron picker (input texto + preview)
- Tab Permissions: add/remove grants por principal
- Tab Comments: thread com add/delete
- Run Now: botão + polling de status com `st.spinner` + `st.rerun()`

### Collection Detail (`/collections/$productId`) — 3 dias
- APIs: ~13 endpoints
- `st.tabs`: About · Tables · Results · Runs · Scheduling · History · Permissions
- Tab Tables: add/remove monitored tables com `st.multiselect`
- Tab Results: gráficos Plotly (score, tendência, breakdown)
- Tab Runs: tabela de run sets
- Lifecycle + Run Now igual ao padrão estabelecido

**Dependências:** Sprint 0 + Sprint 2 (padrões de UI definidos)  
**Risco:** polling de job status (Run Now) — usar `st.fragment` com `time.sleep(3)` + `st.rerun()`

---

## Sprint 4 — Settings

**Duração estimada: 6 dias**  
**Tela:** `/settings` (~3 000 linhas React, 12+ seções, 30 endpoints de config)

| Seção | Esforço |
|-------|---------|
| Timezone | 0,5 dia |
| Label Definitions (builtin + custom) | 1 dia |
| Retention | 0,25 dia |
| Run Review Statuses | 0,5 dia |
| AI Settings (toggle + endpoint) | 0,5 dia |
| Rules Registry (auto-upgrade, tag auto-assign, pass threshold) | 0,5 dia |
| Approvals Mode + Require Draft Run + Sample Limits | 0,5 dia |
| Compute (warehouse/cluster picker + grant access) | 0,5 dia |
| Share Tables with Workspace Users | 0,25 dia |
| Role Management (RBAC — grupos → papéis) | 0,75 dia |
| Database Reset / Deploy Demo | 0,25 dia |
| Métricas customizadas | 0,5 dia |

Cada seção → `st.expander` + `st.form` com `st.form_submit_button` (substitui auto-save debounced).

**Dependências:** Sprint 0  
**Risco:** médio — muitas seções independentes, mas simples individualmente. Guard de admin em toda a página.

---

## Sprint 5 — Editor de Regras

**Duração estimada: 8 dias**  
**Telas:** `/registry-rules/new` · `/registry-rules/import` · `/registry-rules/bulk-import`

Esta é a parte mais complexa da aplicação.

| Sub-componente | Abordagem Streamlit | Esforço |
|---------------|---------------------|---------|
| Modo DQX Native (form guiado por `check-functions`) | `st.selectbox` + campos dinâmicos por função | 2 dias |
| Modo SQL (editor de texto) | `st.text_area` com syntax highlight via `st.code` preview | 0,5 dia |
| Modo Low-Code (builder visual) | Simplificar para form estruturado (sem drag); `@dnd-kit` não tem equivalente direto em Streamlit | 1,5 dia |
| AI Assist (`/ai/generate-checks`, `write-sql`, `improve-sql`, `explain-sql`) | Painel lateral com `st.sidebar` ou `st.expander`; input texto → botão → `st.code` com resultado | 1 dia |
| Dry-run (`/dryrun`, `/dryrun/results`) | Botão "Test" → spinner → tabela de resultados + contagem erros/warnings | 1 dia |
| Duplicate detection (`/rules/check-duplicates`) | Aviso inline após submit | 0,5 dia |
| Import YAML (`/registry-rules/batch-import`) | `st.file_uploader` + preview + botão de importação | 0,5 dia |
| Import Data Contract (`/contract/generate-rules`) | `st.text_area` para colar contrato + preview de regras geradas | 1 dia |

**Dependências:** Sprint 0 + Sprint 3 (padrões de detalhe)  
**Risco:** alto — o Low-Code builder perde interatividade visual; alinhar com o usuário se simplificação é aceitável.

---

## Sprint 6 — Profiler + Ajustes Finais

**Duração estimada: 5 dias**

### Profiler (`/profiler`) — 3 dias
- APIs: `POST /profiler/runs`, `GET /profiler/runs/{id}/status`, `GET /profiler/runs/{id}/results`
- Catalog Browser para selecionar tabela → configurar sampling → submit
- Polling de status com `st.spinner` + `st.rerun()`
- Modal de resultados: candidatos a checks em `st.dataframe` com botão "Save as Rules"

### Ajustes Finais — 2 dias
- Testes de integração fim a fim por tela
- Validação de guards de permissão (admin vs. usuário comum)
- Revisão de mensagens de erro / empty states
- i18n básico (pt-BR + en) via dicionário Python
- Documentação de deploy no Databricks Apps

---

## Resumo do Cronograma

| Sprint | Conteúdo | Duração | Acumulado |
|--------|----------|---------|-----------|
| Sprint 0 | Infraestrutura | 5 dias | 5 dias |
| Sprint 1 | Home, Profile, Marketplace, Drafts | 5 dias | 10 dias |
| Sprint 2 | Listagens (RR, MT, Collections, Runs) | 7 dias | 17 dias |
| Sprint 3 | Detalhes com tabs | 10 dias | 27 dias |
| Sprint 4 | Settings | 6 dias | 33 dias |
| Sprint 5 | Editor de Regras + Import | 8 dias | 41 dias |
| Sprint 6 | Profiler + Ajustes finais | 5 dias | 46 dias |
| **Total** | | **~46 dias úteis** | **~9,5 semanas** |

> Estimativas para **1 desenvolvedor** trabalhando full-time.  
> Com 2 desenvolvedores em paralelo (Sprints 1–4 paralelizáveis): **~6 semanas**.

---

## Dependências Críticas

```
Sprint 0 (infra)
    ├── Sprint 1 (telas simples)
    ├── Sprint 2 (listagens)
    │       └── Sprint 3 (detalhes)
    │               └── Sprint 5 (editor)
    └── Sprint 4 (settings) ← independente das demais
Sprint 6 depende de todos os anteriores
```

---

## Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Low-Code builder sem equivalente visual em Streamlit | Alto | Simplificar para form estruturado; alinhar expectativa antes de Sprint 5 |
| Polling de jobs (`run-failure-toasts`, `job-polling`) em Streamlit | Médio | `st.fragment` com `rerun_on="timer"` (Streamlit ≥ 1.37) ou loop manual com `time.sleep` |
| Performance com muitos `st.rerun()` em telas complexas | Médio | Usar `st.cache_data` com TTL para dados que não mudam frequentemente |
| Auth via headers Databricks Apps — comportamento em dev local | Baixo | Mock de headers via variável de ambiente em desenvolvimento |
| i18n — 5 idiomas | Baixo | Priorizar pt-BR + en; demais idiomas em iteração posterior |
