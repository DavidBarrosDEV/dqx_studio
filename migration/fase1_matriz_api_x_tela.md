# Fase 1 — Matriz API × Tela

> DQX Studio · React → Streamlit Migration  
> Data: 2026-09-21

Legenda de telas abreviadas usadas na coluna "Usado em":

| Abrev. | Tela |
|--------|------|
| HOME | `/home` |
| SETTINGS | `/settings` |
| PROFILE | `/profile` |
| PROFILER | `/profiler` |
| MARKET | `/marketplace` |
| RESULTS | `/results` |
| RR-LIST | `/registry-rules` |
| RR-NEW | `/registry-rules/new` |
| RR-DETAIL | `/registry-rules/$ruleId` |
| RR-IMPORT | `/registry-rules/import` |
| RR-BULK | `/registry-rules/bulk-import` |
| MT-LIST | `/monitored-tables` |
| MT-NEW | `/monitored-tables/new` |
| MT-DETAIL | `/monitored-tables/$bindingId` |
| COL-LIST | `/collections` |
| COL-NEW | `/collections/new` |
| COL-DETAIL | `/collections/$productId` |
| DRAFTS | `/rules/drafts` |
| RUNS | `/runs-history` |
| GLOBAL | Global (hook carregado em toda a app) |

---

## 1. Autenticação & Usuário

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/current-user` | GET | GLOBAL (`AuthGuard`), HOME, PROFILE |
| `/api/v1/current-user/role` | GET | GLOBAL (`use-permissions`) |

---

## 2. Setup / Admin

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/setup/status` | GET | GLOBAL (prefetch em `AuthGuard`) |
| `/api/v1/admin/reconcile` | POST | SETTINGS |
| `/api/v1/admin/reset-database` | POST | SETTINGS |
| `/api/v1/admin/reset-status` | GET | SETTINGS (polling) |
| `/api/v1/admin/deploy-demo` | POST | SETTINGS |
| `/api/v1/admin/demo-status` | GET | SETTINGS (polling) |

---

## 3. Configuração

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/config` | GET | SETTINGS |
| `/api/v1/config` | PUT | SETTINGS |
| `/api/v1/config/timezone` | GET | SETTINGS, GLOBAL (TimezoneSync) |
| `/api/v1/config/timezone` | PUT | SETTINGS |
| `/api/v1/config/retention` | GET | SETTINGS |
| `/api/v1/config/retention` | PUT | SETTINGS |
| `/api/v1/config/label-definitions` | GET | SETTINGS, RR-NEW, RR-DETAIL, MT-DETAIL, COL-DETAIL (label pickers) |
| `/api/v1/config/label-definitions` | PUT | SETTINGS |
| `/api/v1/config/run-review-statuses` | GET | SETTINGS, RUNS |
| `/api/v1/config/run-review-statuses` | PUT | SETTINGS |
| `/api/v1/config/workspace-host` | GET | SETTINGS, RUNS (link ao job Databricks) |
| `/api/v1/config/ai-settings` | GET | SETTINGS, GLOBAL (`use-ai-availability`) |
| `/api/v1/config/ai-settings` | PUT | SETTINGS |
| `/api/v1/config/rules-registry-settings` | GET | SETTINGS, RR-DETAIL (`use-default-auto-upgrade`, `use-pass-threshold-enabled`) |
| `/api/v1/config/rules-registry-settings` | PUT | SETTINGS |
| `/api/v1/config/approvals-mode` | GET | SETTINGS, GLOBAL (`use-approvals-mode`) |
| `/api/v1/config/approvals-mode` | PUT | SETTINGS |
| `/api/v1/config/require-draft-run` | GET | SETTINGS, GLOBAL (`use-require-draft-run`) |
| `/api/v1/config/require-draft-run` | PUT | SETTINGS |
| `/api/v1/config/draft-run-sample-limit` | GET | SETTINGS |
| `/api/v1/config/draft-run-sample-limit` | PUT | SETTINGS |
| `/api/v1/config/profiler-sample` | GET | SETTINGS |
| `/api/v1/config/profiler-sample` | PUT | SETTINGS |
| `/api/v1/config/share-tables-with-workspace-users` | GET | SETTINGS |
| `/api/v1/config/share-tables-with-workspace-users` | PUT | SETTINGS |
| `/api/v1/config/global-results-settings` | GET | RESULTS |
| `/api/v1/config/global-results-settings` | PUT | RESULTS |
| `/api/v1/config/run-config` | GET | RUNS |
| `/api/v1/config/run-config` | PUT | RUNS |
| `/api/v1/config/run-config` | DELETE | RUNS |

---

## 4. Discovery (Catalog Browser)

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/discovery/catalogs` | GET | MT-NEW, MT-DETAIL, PROFILER, COL-DETAIL (CatalogBrowser, ColumnDiscoveryPanel) |
| `/api/v1/discovery/schemas` | GET | MT-NEW, MT-DETAIL, PROFILER, COL-DETAIL |
| `/api/v1/discovery/tables` | GET | MT-NEW, MT-DETAIL, PROFILER, COL-DETAIL |
| `/api/v1/discovery/tables/all` | GET | PROFILER (batch), COL-DETAIL (table-picker) |
| `/api/v1/discovery/columns` | GET | MT-DETAIL, RR-NEW, RR-DETAIL (ColumnDiscoveryPanel, rule editor) |
| `/api/v1/discovery/table-tags` | GET | RR-NEW, RR-DETAIL (rule editor) |
| `/api/v1/discovery/table-schema-ddl` | GET | RR-NEW, RR-DETAIL (check `has_valid_schema`) |
| `/api/v1/discovery/governed-tags` | GET | SETTINGS (GovernedKeyPicker) |
| `/api/v1/discovery/filter-tables-by-columns` | POST | PROFILER (batch — filtra tabelas por colunas requeridas) |

---

## 5. Regras (Legacy por tabela)

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/rules` | GET | `/rules/active`, PROFILER |
| `/api/v1/rules` | POST | RR-NEW, RR-DETAIL (editor) |
| `/api/v1/rules/history` | GET | RR-DETAIL |
| `/api/v1/rules/batch` | POST | PROFILER (batch save) |
| `/api/v1/rules/check-duplicates` | POST | RR-NEW, RR-DETAIL |
| `/api/v1/rules/backfill-ids` | POST | SETTINGS (admin) |
| `/api/v1/rules/validate-checks` | POST | RR-NEW, RR-DETAIL |
| `/api/v1/rules/{ruleId}` | DELETE | RR-LIST, RR-DETAIL |
| `/api/v1/rules/{ruleId}/submit` | POST | RR-DETAIL, DRAFTS |
| `/api/v1/rules/{ruleId}/approve` | POST | RR-DETAIL, DRAFTS |
| `/api/v1/rules/{ruleId}/reject` | POST | RR-DETAIL, DRAFTS |
| `/api/v1/rules/{ruleId}/revoke` | POST | RR-DETAIL |

---

## 6. Registry Rules (versionadas)

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/registry-rules` | GET | RR-LIST, DRAFTS |
| `/api/v1/registry-rules` | POST | RR-NEW |
| `/api/v1/registry-rules/{ruleId}` | GET | RR-DETAIL |
| `/api/v1/registry-rules/{ruleId}` | PUT | RR-DETAIL |
| `/api/v1/registry-rules/{ruleId}` | DELETE | RR-LIST, RR-DETAIL |
| `/api/v1/registry-rules/{ruleId}/versions` | GET | RR-DETAIL |
| `/api/v1/registry-rules/batch-import` | POST | RR-IMPORT, RR-BULK |
| `/api/v1/registry-rules/{ruleId}/submit` | POST | RR-DETAIL, RR-LIST, DRAFTS |
| `/api/v1/registry-rules/{ruleId}/approve` | POST | RR-DETAIL, RR-LIST, DRAFTS |
| `/api/v1/registry-rules/{ruleId}/reject` | POST | RR-DETAIL, RR-LIST, DRAFTS |
| `/api/v1/registry-rules/{ruleId}/revoke` | POST | RR-DETAIL, RR-LIST |
| `/api/v1/registry-rules/{ruleId}/deprecate` | POST | RR-DETAIL, RR-LIST |
| `/api/v1/registry-rules/{ruleId}/undeprecate` | POST | RR-DETAIL, RR-LIST |
| `/api/v1/registry-rules/backfill-embeddings` | POST | SETTINGS (admin) |

---

## 7. Monitored Tables (Bindings)

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/monitored-tables` | GET | MT-LIST, DRAFTS, COL-DETAIL |
| `/api/v1/monitored-tables` | POST | MT-NEW |
| `/api/v1/monitored-tables/{bindingId}` | GET | MT-DETAIL |
| `/api/v1/monitored-tables/{bindingId}` | DELETE | MT-LIST, MT-DETAIL |
| `/api/v1/monitored-tables/bulk-register` | POST | MT-NEW (bulk) |
| `/api/v1/monitored-tables/{bindingId}/owner` | PUT | MT-DETAIL |
| `/api/v1/monitored-tables/{bindingId}/schedule` | PUT | MT-DETAIL |
| `/api/v1/monitored-tables/{bindingId}/profile` | GET | MT-DETAIL (tab Profiling) |
| `/api/v1/monitored-tables/{bindingId}/versions` | GET | MT-DETAIL (tab History) |
| `/api/v1/monitored-tables/{bindingId}/version-checks` | GET | MT-DETAIL |
| `/api/v1/monitored-tables/{bindingId}/run` | POST | MT-DETAIL, MT-LIST |
| `/api/v1/monitored-tables/{bindingId}/apply-rule` | POST | MT-DETAIL (tab Rules) |
| `/api/v1/monitored-tables/{bindingId}/applied-rules` | PUT | MT-DETAIL (tab Rules) |
| `/api/v1/monitored-tables/{bindingId}/remove-rule` | POST | MT-DETAIL (tab Rules) |
| `/api/v1/monitored-tables/{bindingId}/set-rule-pin` | PUT | MT-DETAIL (tab Rules) |
| `/api/v1/monitored-tables/{bindingId}/set-rule-severity-override` | PUT | MT-DETAIL (tab Rules) |
| `/api/v1/monitored-tables/{bindingId}/submit` | POST | MT-DETAIL, MT-LIST, DRAFTS |
| `/api/v1/monitored-tables/{bindingId}/approve` | POST | MT-DETAIL, MT-LIST, DRAFTS |
| `/api/v1/monitored-tables/{bindingId}/reject` | POST | MT-DETAIL, MT-LIST, DRAFTS |
| `/api/v1/monitored-tables/{bindingId}/revert` | POST | MT-DETAIL, MT-LIST |
| `/api/v1/monitored-tables/pending-applications/batch` | POST | MT-DETAIL |
| `/api/v1/monitored-tables/{bindingId}/pending-applications` | GET | MT-DETAIL |
| `/api/v1/monitored-tables/suggest-rules` | POST | MT-DETAIL (AI suggest) |
| `/api/v1/monitored-tables/match-rules` | POST | MT-DETAIL |
| `/api/v1/monitored-tables/{bindingId}/tag-suggestions` | GET | MT-DETAIL |
| `/api/v1/monitored-tables/{bindingId}/profiling-suggestions` | GET | MT-DETAIL |
| `/api/v1/monitored-tables/{bindingId}/apply-profiling-suggestions` | POST | MT-DETAIL |

---

## 8. Collections / Data Products

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/data-products` | GET | COL-LIST, DRAFTS |
| `/api/v1/data-products` | POST | COL-NEW |
| `/api/v1/data-products/{productId}` | GET | COL-DETAIL |
| `/api/v1/data-products/{productId}` | PUT | COL-DETAIL |
| `/api/v1/data-products/{productId}` | DELETE | COL-LIST, COL-DETAIL |
| `/api/v1/data-products/{productId}/review-changes` | GET | COL-DETAIL (diff dialog) |
| `/api/v1/data-products/{productId}/add-member` | POST | COL-DETAIL (tab Tables) |
| `/api/v1/data-products/{productId}/remove-member` | POST | COL-DETAIL (tab Tables) |
| `/api/v1/data-products/{productId}/submit` | POST | COL-DETAIL, COL-LIST, DRAFTS |
| `/api/v1/data-products/{productId}/approve` | POST | COL-DETAIL, COL-LIST, DRAFTS |
| `/api/v1/data-products/{productId}/reject` | POST | COL-DETAIL, COL-LIST, DRAFTS |
| `/api/v1/data-products/{productId}/revert` | POST | COL-DETAIL, COL-LIST |
| `/api/v1/data-products/{productId}/run` | POST | COL-DETAIL |

---

## 9. Dry Runs (Validação)

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/dryrun` | POST | RR-NEW, RR-DETAIL (editor — submit single dry run) |
| `/api/v1/dryrun/runs` | GET | RUNS |
| `/api/v1/dryrun/runs/{runId}/status` | GET | GLOBAL (`use-job-polling`) |
| `/api/v1/dryrun/runs/{runId}/cancel` | POST | RUNS |
| `/api/v1/dryrun/results/{runId}` | GET | RR-DETAIL, MT-DETAIL (DryRunResults) |
| `/api/v1/dryrun/batch-from-catalog` | POST | COL-DETAIL ("Run now") |
| `/api/v1/dryrun/validate` | POST | RR-NEW, RR-DETAIL |
| `/api/v1/dryrun/recent-failures` | GET | GLOBAL (`use-run-failure-toasts`) |

---

## 10. Profiler

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/profiler/runs` | POST | PROFILER |
| `/api/v1/profiler/runs/batch` | POST | PROFILER |
| `/api/v1/profiler/runs` | GET | PROFILER, RUNS |
| `/api/v1/profiler/runs/{runId}/status` | GET | GLOBAL (`use-job-polling`) |
| `/api/v1/profiler/runs/{runId}/cancel` | POST | PROFILER |
| `/api/v1/profiler/runs/{runId}/results` | GET | PROFILER (modal de resultados) |
| `/api/v1/profiler/recent-failures` | GET | GLOBAL (`use-run-failure-toasts`) |

---

## 11. Quarentena

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/quarantine/runs/{runId}` | GET | MT-DETAIL, RUNS (DryRunResults) |
| `/api/v1/quarantine/runs/{runId}/count` | GET | MT-DETAIL (DryRunResults) |
| `/api/v1/quarantine/runs/{runId}/export` | GET | MT-DETAIL (export de registros) |

---

## 12. Métricas & Resultados DQ

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/metrics/{tableFqn}` | GET | MT-DETAIL (trend de métricas) |
| `/api/v1/metrics` | GET | SETTINGS |
| `/api/v1/metrics` | PUT | SETTINGS |
| `/api/v1/dq-results/global` | GET | RESULTS |
| `/api/v1/dq-results/rules/{ruleId}` | GET | RR-DETAIL |
| `/api/v1/dq-results/products/{productId}/runs` | GET | COL-DETAIL (tab Results — run picker) |
| `/api/v1/dq-results/products/{productId}` | GET | COL-DETAIL (tab Results) |
| `/api/v1/dq-results/failed-rows/{tableFqn}` | GET | RESULTS (failing rows OBO) |
| `/api/v1/dq-results/runs/{bindingOrTable}` | GET | MT-DETAIL (run selector) |
| `/api/v1/dq-results/tables/{tableFqn}` | GET | MT-DETAIL (tab Results) |
| `/api/v1/dq-score/rules/{ruleId}` | GET | RR-DETAIL |
| `/api/v1/dq-score/severities` | GET | RESULTS |
| `/api/v1/dq-score/dimensions` | GET | RESULTS |
| `/api/v1/dq-score/refresh` | POST | SETTINGS (admin) |
| `/api/v1/home/stats` | GET | HOME |

---

## 13. Genie (AI Q&A)

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/genie/ask` | POST | RESULTS (`AskGenieButton`) |
| `/api/v1/genie/messages` | POST | RESULTS (chat Genie) |
| `/api/v1/genie/messages/{messageId}` | GET | RESULTS (polling) |
| `/api/v1/genie/space` | GET | RESULTS |
| `/api/v1/genie/entitlements/verify` | POST | RESULTS (pre-verify para failing rows) |
| `/api/v1/genie/feedback` | POST | RESULTS |
| `/api/v1/genie/sample-questions` | GET | RESULTS |

---

## 14. IA / Geração de Código

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/ai/generate-checks` | POST | GLOBAL (`AIAssistantProvider` → `AICheckGenerator`) |
| `/api/v1/ai/generate-rule` | POST | RR-NEW, RR-DETAIL |
| `/api/v1/ai/suggest-field` | POST | RR-NEW, RR-DETAIL |
| `/api/v1/ai/write-sql` | POST | RR-NEW, RR-DETAIL (SQL editor) |
| `/api/v1/ai/improve-sql` | POST | RR-NEW, RR-DETAIL |
| `/api/v1/ai/explain-sql` | POST | RR-NEW, RR-DETAIL |
| `/api/v1/contract/generate-rules` | POST | RR-IMPORT (gerar regras de data contract) |
| `/api/v1/ai/serving-endpoints` | GET | SETTINGS |

---

## 15. Check Functions & Rule Test

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/check-functions` | GET | RR-NEW, RR-DETAIL (lista de funções DQX disponíveis) |
| `/api/v1/rule-test/run` | POST | RR-DETAIL (`RuleTestPanel`) |
| `/api/v1/rule-test/generate-data` | POST | RR-DETAIL (`RuleTestPanel`) |
| `/api/v1/rule-test/prewarm` | POST | RR-DETAIL (`RuleTestPanel`) |

---

## 16. Preview de Dados de Tabela

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/table-data/preview` | GET | MT-DETAIL (preview da tabela) |
| `/api/v1/table-data/query` | POST | MT-DETAIL |

---

## 17. Compute

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/compute/warehouses` | GET | SETTINGS |
| `/api/v1/compute/clusters` | GET | SETTINGS |
| `/api/v1/compute/warehouse-access` | GET | SETTINGS |
| `/api/v1/compute/grant-warehouse-access` | POST | SETTINGS |

---

## 18. Roles & Permissões (RBAC)

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/roles/mappings` | GET | SETTINGS (`RoleManagement`) |
| `/api/v1/roles/mappings` | POST | SETTINGS |
| `/api/v1/roles/mappings/{id}` | DELETE | SETTINGS |
| `/api/v1/roles/mappings/history` | GET | SETTINGS |
| `/api/v1/roles/workspace-groups` | GET | SETTINGS |
| `/api/v1/roles/privileged-principals` | GET | SETTINGS |
| `/api/v1/roles/available` | GET | SETTINGS |

---

## 19. Permissões por Objeto

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/permissions/default-inherit` | GET | MT-DETAIL, COL-DETAIL (tab Permissions) |
| `/api/v1/permissions/default-inherit` | PUT | MT-DETAIL, COL-DETAIL |
| `/api/v1/permissions/{objectType}/{objectId}/grants` | GET | MT-DETAIL, COL-DETAIL (`PermissionsTab`) |
| `/api/v1/permissions/{objectType}/{objectId}/grants` | PUT | MT-DETAIL, COL-DETAIL |
| `/api/v1/permissions/{objectType}/{objectId}/grants` | DELETE | MT-DETAIL, COL-DETAIL |
| `/api/v1/permissions/{objectType}/{objectId}/effective` | GET | GLOBAL (`use-object-permissions`) |
| `/api/v1/principals/search` | GET | MT-DETAIL, COL-DETAIL (busca usuários/grupos) |

---

## 20. Agendamentos

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/schedules` | GET | RUNS |
| `/api/v1/schedules/{name}` | GET | RUNS |
| `/api/v1/schedules/{name}` | PUT | RUNS |
| `/api/v1/schedules/{name}` | DELETE | RUNS |
| `/api/v1/schedules/{name}/history` | GET | RUNS |
| `/api/v1/schedule-grants/preflight` | POST | RUNS |

---

## 21. Run Sets

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/run-sets` | GET | COL-DETAIL (tab Runs), RUNS |
| `/api/v1/run-sets/{runSetId}` | GET | COL-DETAIL (tab Runs) |

---

## 22. Run Review Status

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/runs/{runId}/review-status` | GET | RUNS |
| `/api/v1/runs/{runId}/review-status` | PUT | RUNS |
| `/api/v1/runs/{runId}/review-status` | DELETE | RUNS |
| `/api/v1/runs/{runId}/review-status/history` | GET | RUNS |

---

## 23. Comentários

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/comments` | POST | RR-DETAIL, MT-DETAIL, COL-DETAIL, RUNS (`CommentThread`) |
| `/api/v1/comments` | GET | RR-DETAIL, MT-DETAIL, COL-DETAIL, RUNS |
| `/api/v1/comments/{commentId}` | DELETE | RR-DETAIL, MT-DETAIL, COL-DETAIL, RUNS |

---

## 24. Export

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/export/registry-rules` | GET | RR-LIST (`ExportDialog`) |
| `/api/v1/export/registry-rules/{ruleId}` | GET | RR-DETAIL (`ExportDialog`) |
| `/api/v1/export/monitored-tables` | GET | MT-LIST (`ExportDialog`) |
| `/api/v1/export/monitored-tables/{bindingId}` | GET | MT-DETAIL (`ExportDialog`) |
| `/api/v1/export/data-products` | GET | COL-LIST (`ExportDialog`) |
| `/api/v1/export/data-products/{productId}` | GET | COL-DETAIL (`ExportDialog`) |

---

## 25. Marketplace & Versionamento

| Endpoint | Método | Usado em |
|----------|--------|---------|
| `/api/v1/marketplace/packs` | GET | MARKET |
| `/api/v1/version` | GET | GLOBAL (header user menu) |

---

## Resumo Quantitativo

| Domínio | Endpoints únicos |
|---------|-----------------|
| Auth & Usuário | 2 |
| Setup / Admin | 6 |
| Configuração | 30 |
| Discovery | 9 |
| Regras (legacy) | 12 |
| Registry Rules | 14 |
| Monitored Tables | 27 |
| Collections | 13 |
| Dry Runs | 8 |
| Profiler | 7 |
| Quarentena | 3 |
| Métricas & DQ Results | 15 |
| Genie | 7 |
| IA / Geração | 8 |
| Check Functions & Rule Test | 4 |
| Preview de Dados | 2 |
| Compute | 4 |
| Roles & RBAC | 7 |
| Permissões por Objeto | 7 |
| Agendamentos | 6 |
| Run Sets | 2 |
| Run Review Status | 4 |
| Comentários | 3 |
| Export | 6 |
| Marketplace & Versioning | 2 |
| **Total** | **~288** |
