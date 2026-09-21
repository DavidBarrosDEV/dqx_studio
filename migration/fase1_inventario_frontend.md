# Fase 1 — Inventário do Frontend React

> DQX Studio · React → Streamlit Migration  
> Data: 2026-09-21

---

## 1. Estrutura de Diretórios

```
app/
├── package.json
├── orval.config.ts          ← geração automática de hooks via OpenAPI
├── databricks.yml
└── src/databricks_labs_dqx_app/
    └── ui/
        ├── components/      ← componentes reutilizáveis
        ├── hooks/           ← custom hooks React
        ├── lib/             ← utilitários, API gerada, formatadores
        ├── routes/          ← páginas (TanStack Router file-based)
        ├── styles/
        └── types/
```

---

## 2. Páginas / Rotas

| # | URL | Arquivo de Rota | Descrição |
|---|-----|-----------------|-----------|
| 1 | `/` | `routes/index.tsx` | Redirect → `/home` |
| 2 | `/home` | `routes/_sidebar/home.tsx` | Página inicial: saudação personalizada, stat cards, grid de acesso rápido |
| 3 | `/settings` | `routes/_sidebar/settings.tsx` | Configurações do workspace (Admin). ~3 000 linhas. Tabs: Timezone, Label Definitions, Retention, Run Review Statuses, AI, Rules Registry, Pass Threshold, Approvals, Compute, Roles, Database Reset |
| 4 | `/profile` | `routes/_sidebar/profile.tsx` | Perfil do usuário: info SCIM (nome, e-mail, grupos), seletor de idioma |
| 5 | `/profiler` | `routes/_sidebar/profiler.tsx` | Profiler de dados: seleciona tabela via Catalog Browser, configura sampling, submete runs de perfil, exibe resultados em modal |
| 6 | `/marketplace` | `routes/_sidebar/marketplace.tsx` | Marketplace de rule-packs (apenas Admin). Navegar e instalar pacotes de regras pré-construídos |
| 7 | `/results` | `routes/_sidebar/results.tsx` | Resultados globais de DQ. Score médio, tendências, breakdown por dimensão/severidade/regra/tabela/coluna |
| 8 | `/registry-rules` | `routes/_sidebar/registry-rules.index.tsx` | Lista do Registry de Regras. Tabela com busca, filtros, bulk actions (submit/approve/reject/deprecate/export) |
| 9 | `/registry-rules/new` | `routes/_sidebar/registry-rules.new.tsx` | Criar nova regra no registry. Modos: DQX Native / Low-Code / SQL |
| 10 | `/registry-rules/$ruleId` | `routes/_sidebar/registry-rules.$ruleId.tsx` | Detalhe de regra: edição, lifecycle (submit/approve/reject/revoke/deprecate), histórico de versões, export YAML/ODCS, thread de comentários |
| 11 | `/registry-rules/import` | `routes/_sidebar/registry-rules.import.tsx` | Import de regras: aba DQX YAML (paste/upload) e aba Data Contract |
| 12 | `/registry-rules/bulk-import` | `routes/_sidebar/registry-rules.bulk-import.tsx` | Import em massa de regras (CSV/estruturado) |
| 13 | `/monitored-tables` | `routes/_sidebar/monitored-tables.index.tsx` | Lista de Monitored Tables. Bulk actions: delete/approve/reject/run/revert/diff. Paginação, busca, filtro por status/score |
| 14 | `/monitored-tables/new` | `routes/_sidebar/monitored-tables.new.tsx` | Registrar nova tabela monitorada: Catalog Browser → configurar regras e mapeamento de colunas |
| 15 | `/monitored-tables/$bindingId` | `routes/_sidebar/monitored-tables.$bindingId.tsx` | Detalhe da tabela monitorada. Tabs: Rules Applied, Profiling, Results, Scheduling, History, Permissions, Comments |
| 16 | `/collections` | `routes/_sidebar/collections.index.tsx` | Lista de Collections (Data Products). Bulk actions: delete/approve/reject/run/revert. Filtro por DQ score |
| 17 | `/collections/new` | `routes/_sidebar/collections.new.tsx` | Criar nova collection / data product |
| 18 | `/collections/$productId` | `routes/_sidebar/collections.$productId.tsx` | Detalhe da collection. Tabs: About, Tables, Results, Runs, Scheduling, History, Permissions |
| 19 | `/rules/drafts` | `routes/_sidebar/rules.drafts.tsx` | Fila de Aprovação unificada: Registry Rules + Monitored Tables + Data Products pendentes. Approve/reject com rationale |
| 20 | `/runs-history` | `routes/_sidebar/runs-history.tsx` | Histórico de Runs. Tabela paginada de todos os runs de validação e profiling. Filtros, sort, link para job no Databricks, review status, agendamentos, comentários |
| 21 | `/runs/$runName` | `routes/_sidebar/runs.$runName.tsx` | Detalhe/editor de um run set (collection run) |
| 22 | `/rules/active` | `routes/_sidebar/rules.active.tsx` | (Legacy) Active Rules por tabela |
| R | Múltiplas `/data-products/*`, `/table-spaces/*`, `/rules/create-sql`, etc. | Redirects → equivalente atual |

---

## 3. Componentes Reutilizáveis

### 3.1 Infraestrutura Central

| Componente | Arquivo | Responsabilidade |
|-----------|---------|-----------------|
| `AuthGuard` | `components/AuthGuard.tsx` | Polling exponencial em `GET /api/v1/current-user` (até 15 tentativas). Nada renderiza até auth concluir |
| `AIAssistantProvider` | `components/AIAssistantProvider.tsx` | Context para painel lateral de IA. Contém `open`/`runContext`. Renderiza Sheet com `AICheckGenerator` |
| `StudioLoadingScreen` | `components/StudioLoadingScreen.tsx` | Spinner full-screen durante inicialização |

### 3.2 Layout

| Componente | Arquivo | Responsabilidade |
|-----------|---------|-----------------|
| `SidebarLayout` | `components/layout/SidebarLayout.tsx` | Shell da página: header sticky + sidebar colapsável + `<Outlet>` |
| `ThemeProvider` | `components/layout/theme-provider.tsx` | Context de tema (light/dark/system), persistido em localStorage |
| `HeaderUserMenu` | `components/layout/HeaderUserMenu.tsx` | Dropdown do usuário no topo: links para `/profile` e `/settings` |
| `Logo` | `components/layout/Logo.tsx` | Logotipo DQX Studio, link para `/home` |
| `ModeToggle` | `components/layout/ModeToggle.tsx` | Botão dark/light/system |
| `PageBreadcrumb` | `components/layout/PageBreadcrumb.tsx` | Breadcrumb no topo do conteúdo |

### 3.3 Dados & Descoberta

| Componente | Arquivo | Responsabilidade |
|-----------|---------|-----------------|
| `CatalogBrowser` | `components/CatalogBrowser.tsx` | Browser de 3 níveis Unity Catalog (Catalog → Schema → Table). Single ou multi-select |
| `ColumnDiscoveryPanel` | `components/ColumnDiscoveryPanel.tsx` | Explorer de colunas de uma tabela selecionada. Nomes/tipos com botões de cópia |
| `DryRunResults` | `components/DryRunResults.tsx` | Resultados de dry-run: contagem de erros/warnings, resumo por check, registros em quarentena paginados |

### 3.4 Regras & IA

| Componente | Arquivo | Responsabilidade |
|-----------|---------|-----------------|
| `AICheckGenerator` | `components/AICheckGenerator.tsx` | Formulário do painel de IA: gera YAML de checks a partir de linguagem natural |
| `RegistryRuleBadges` | `components/RegistryRuleBadges.tsx` | Badges de severidade, criticidade e status do ciclo de vida |
| `Labels` / `LabelFilter` | `components/Labels.tsx` | Renderização e filtro de tags/labels |
| `LifecycleRationaleDialog` | `components/LifecycleRationaleDialog.tsx` | Modal para inserir rationale de aprovação/rejeição |
| `HelpTooltip` | `components/HelpTooltip.tsx` | Tooltip de ajuda contextual |
| Low-Code Editor | `components/rules/lowcode/` | Builder visual de regras sem SQL/YAML manual |
| `RuleTestPanel` | `components/rules/test/RuleTestPanel.tsx` | Painel para testar regra contra dados de amostra |

### 3.5 Governança / Aprovação

| Componente | Arquivo | Responsabilidade |
|-----------|---------|-----------------|
| `ApprovalQueueCard` | `components/drafts/ApprovalQueueCard.tsx` | Card da fila de aprovação com ações approve/reject |
| `ChangeDiffDialog` | `components/drafts/ChangeDiffDialog.tsx` | Dialog de diff entre versões (regra, monitored table, data product) |
| `RoleManagement` | `components/RoleManagement.tsx` | Painel admin de mapeamento grupo → papel (RBAC) |

### 3.6 Resultados & Runs

| Componente | Arquivo | Responsabilidade |
|-----------|---------|-----------------|
| `MultiTableResults` | `components/results/MultiTableResults.tsx` | Composição multi-tabela de resultados: score médio, tendência, breakdown por tabela/regra/dimensão/severidade |
| `AskGenieButton` | `components/results/AskGenieButton.tsx` | Botão "Ask Genie" — abre painel de chat IA do Databricks para explorar dados de DQ |

### 3.7 Collections / Data Products

| Componente | Arquivo | Responsabilidade |
|-----------|---------|-----------------|
| `ProductTabsShell` | `components/data-products/ProductTabsShell.tsx` | Shell de tabs da página de detalhe da collection |
| `ProductHeader` | `components/data-products/ProductHeader.tsx` | Header: nome, badges, botões de ação |
| `ProductAboutTab` | `components/data-products/ProductAboutTab.tsx` | Tab About: nome/descrição editáveis, owner, labels |
| `ProductTablesTab` | `components/data-products/ProductTablesTab.tsx` | Tab Tables: gerenciar monitored tables membros |
| `ProductResultsTab` | `components/data-products/ProductResultsTab.tsx` | Tab Results: `MultiTableResults` com escopo da collection |
| `ProductRunsTab` | `components/data-products/ProductRunsTab.tsx` | Tab Runs: histórico de runs da collection |
| `ProductSchedulingTab` | `components/data-products/ProductSchedulingTab.tsx` | Tab Scheduling: agendamento cron |
| `ProductHistoryTab` | `components/data-products/ProductHistoryTab.tsx` | Tab History: audit log de mudanças |
| `DataProductsTable` | `components/data-products/DataProductsTable.tsx` | Tabela ordenável/selecionável da lista de collections |

### 3.8 Monitored Tables

| Componente | Arquivo | Responsabilidade |
|-----------|---------|-----------------|
| `MonitoredTablesTable` | `components/monitored-tables/MonitoredTablesTable.tsx` | Tabela ordenável/selecionável da lista |
| `AddMonitoredTableModal` | `components/monitored-tables/AddMonitoredTableModal.tsx` | Modal de registro via catalog browser |

### 3.9 Registry Rules

| Componente | Arquivo | Responsabilidade |
|-----------|---------|-----------------|
| `RulesTable` | `components/registry-rules/RulesTable.tsx` | Tabela ordenável/selecionável da lista de regras |
| `ImportRulesWorkspace` | `components/registry-rules/ImportRulesWorkspace.tsx` | Workspace de import: DQX YAML e Data Contract |

### 3.10 Permissões & Marketplace

| Componente | Arquivo | Responsabilidade |
|-----------|---------|-----------------|
| `PermissionsTab` | `components/permissions/PermissionsTab.tsx` | Gestão de grants por objeto (View/Modify/Apply/Execute) |
| `MarketplacePage` | `components/marketplace/MarketplacePage.tsx` | Browser do marketplace de rule-packs |
| `GovernedKeyPicker` | `components/settings/GovernedKeyPicker.tsx` | Popover para importar UC governed tags como label definitions |

### 3.11 Utilitários Genéricos

| Componente | Arquivo | Responsabilidade |
|-----------|---------|-----------------|
| `Pagination` | `components/Pagination.tsx` | Controles de paginação por número de página |
| `ExportDialog` | `components/ExportDialog.tsx` | Modal de escolha de formato de export (DQX YAML / ODCS) |
| `CommentThread` | `components/CommentThread.tsx` | Thread de comentários colapsável para qualquer entidade |
| `BulkActionBar` | `components/data-table/BulkActionBar.tsx` | Barra de ações em bulk que aparece ao selecionar linhas |
| `SearchableSelect` | `components/data-table/SearchableSelect.tsx` | Combobox com busca em tempo real |
| `HomeStats` | `components/home/HomeStats.tsx` | Cards de estatísticas "At a Glance" da home |
| `HomeGrid` | `components/home/HomeGrid.tsx` | Grid "Get Started" de navegação rápida |

### 3.12 UI Primitivos (shadcn/ui)

Wrappers sobre Radix UI em `components/ui/`: `alert-dialog`, `avatar`, `badge`, `button`, `card`, `checkbox`, `collapsible`, `command`, `dialog`, `dropdown-menu`, `input`, `label`, `pagination`, `popover`, `select`, `separator`, `sheet`, `sidebar`, `skeleton`, `switch`, `table`, `tabs`, `textarea`, `tooltip`.

---

## 4. Gerenciamento de Estado

| Camada | Tecnologia | Uso |
|--------|-----------|-----|
| **Server state** | TanStack React Query | Todos os dados remotos (regras, runs, catálogo, config). Hooks gerados pelo orval (`useGetXxx`, `useSaveXxx`). Invalidação via `queryClient.invalidateQueries`. |
| **UI global** | React Context | (1) `ThemeProvider` — tema light/dark/system em localStorage. (2) `AIAssistantProvider` — estado do painel de IA. |
| **UI local** | `useState` / `useReducer` | Formulários, linhas selecionadas, paginação, dialogs abertos, filtros. |

### Custom Hooks Notáveis

| Hook | Propósito |
|------|-----------|
| `use-permissions.ts` | Deriva `isAdmin`, `canCreateRules`, `canApproveRules` do role do usuário |
| `use-job-polling.ts` | Polling de status de dry-run / profiler job em intervalo fixo |
| `use-run-failure-toasts.ts` | Poller global de `recent-failures`; dispara toast para runs com falha |
| `use-approvals-mode.ts` | Lê configuração global de modo de aprovação |
| `use-ai-availability.ts` | Verifica se features de IA estão habilitadas |
| `use-unsaved-guard.ts` | Alerta antes de navegar com mudanças não salvas |
| `use-object-permissions.ts` | Busca permissões efetivas por objeto para o usuário corrente |

---

## 5. Dependências Externas

### Runtime

| Pacote | Propósito |
|--------|-----------|
| `react` 19, `react-dom` | Framework UI |
| `@tanstack/react-query` | Server state |
| `@tanstack/react-router` | Roteamento file-based type-safe |
| `axios` | HTTP client |
| `@radix-ui/react-*` | Primitivos UI headless (via shadcn) |
| `recharts` | Gráficos (Results page: linha, barra, pizza) |
| `@codemirror/*`, `@uiw/react-codemirror` | Editor SQL |
| `@dnd-kit/*` | Drag-and-drop para reordenação de regras |
| `i18next`, `react-i18next` | Internacionalização (en, fr, pt-BR, it, es) |
| `js-yaml` | Parse/serialização de YAML |
| `lucide-react` | Icons |
| `motion` (Framer Motion) | Animações |
| `sonner` | Toasts |
| `xlsx` | Export Excel |
| `cmdk` | Command palette |

### Dev / Build

| Pacote | Propósito |
|--------|-----------|
| `vite` 7 | Build tool e dev server |
| `orval` 7.21 | Geração de tipos e hooks React Query a partir do OpenAPI spec |
| `@tanstack/router-plugin` | Plugin Vite para gerar route tree |
| `typescript` 5.9 (strict) | Type checking |
| `tailwindcss` 4 | Estilos |
| `prettier` | Formatação |

---

## 6. Pontos de Atenção para a Migração

| # | Área | Complexidade | Observação |
|---|------|-------------|-----------|
| 1 | **Auth** | Média | `AuthGuard` faz polling exponencial. Em Streamlit, auth vem via headers `X-Forwarded-*` do Databricks Apps server-side |
| 2 | **Polling de jobs** | Média | `use-job-polling.ts` faz polling de status em intervalo. Em Streamlit: `st.rerun()` com `time.sleep()` ou `st.fragment` |
| 3 | **Settings page** | Alta | ~3 000 linhas, 12+ seções com auto-save debounced (600 ms). Mapear para `st.form` / `st.expander` por seção |
| 4 | **Páginas multi-tab** | Baixa | Collection detail (7 tabs), Monitored Table detail (7 tabs) → `st.tabs` |
| 5 | **Editor de regras** | Muito Alta | Low-code + SQL + DQX-native, CodeMirror, AI assist, dry-run preview, dedup detection. Componente mais complexo |
| 6 | **Workflow de aprovação** | Média | Ciclo draft → submitted → approved/rejected/revoked em 3 tipos de entidade. Modelar como UI baseada em status com botões de ação |
| 7 | **Gráficos de resultados** | Média | `MultiTableResults` usa Recharts. Substituir por Plotly (`st.plotly_chart`) |
| 8 | **Drag-and-drop** | Alta | `@dnd-kit` para reordenação de regras. Em Streamlit: componente customizado via `st.components.v2` ou simplificar para up/down buttons |
| 9 | **i18n** | Baixa | 5 idiomas. Em Streamlit: implementar com dicionário Python simples por idioma |
| 10 | **Superfície de API** | — | ~280+ endpoints distintos em `/api/v1/*`. Backend FastAPI permanece intacto; apenas o frontend muda |
