"""
Mock API client — returns fake data so the Streamlit UI can be tested
without a running backend or Databricks connection.

Usage:
    DQX_MOCK=true streamlit run streamlit_app.py
"""


class DQXMockClient:

    # ── Auth & user ───────────────────────────────────────────────────────────

    def get_current_user(self) -> dict:
        return {
            "user_name": "dev@mock.local",
            "display_name": "Dev Mock",
            "email": "dev@mock.local",
            "groups": [{"display": "admins"}, {"display": "data-engineers"}],
        }

    def get_current_user_role(self) -> dict:
        return {"role": "ADMIN"}

    # ── Home ──────────────────────────────────────────────────────────────────

    def get_home_stats(self) -> dict:
        return {
            "monitored_tables": 12,
            "active_rules": 87,
            "collections": 4,
            "avg_dq_score": "94.3%",
        }

    # ── Setup & version ───────────────────────────────────────────────────────

    def get_setup_status(self) -> dict:
        return {"status": "READY"}

    def get_version(self) -> dict:
        return {"version": "0.0.0-mock"}

    # ── Config ────────────────────────────────────────────────────────────────

    def get_config(self) -> dict:
        return {}

    def update_config(self, data: dict) -> dict:
        return data

    def get_label_definitions(self) -> list:
        return [
            {"key": "domain", "values": ["finance", "sales", "hr"]},
            {"key": "criticality", "values": ["high", "medium", "low"]},
        ]

    def update_label_definitions(self, data: dict) -> dict:
        return data

    def get_workspace_host(self) -> dict:
        return {"host": "https://mock.azuredatabricks.net"}

    def get_ai_settings(self) -> dict:
        return {"enabled": True, "endpoint": "mock-endpoint"}

    def update_ai_settings(self, data: dict) -> dict:
        return data

    def get_approvals_mode(self) -> dict:
        return {"mode": "OPTIONAL", "require_draft_run": False}

    def update_approvals_mode(self, data: dict) -> dict:
        return data

    def get_run_review_statuses(self) -> list:
        return ["Approved", "Rejected", "Pending review"]

    def update_run_review_statuses(self, data: dict) -> dict:
        return data

    def get_rules_registry_settings(self) -> dict:
        return {"auto_upgrade": False, "pass_threshold": 0.95, "tag_auto_assign": True}

    def update_rules_registry_settings(self, data: dict) -> dict:
        return data

    def get_global_results_settings(self) -> dict:
        return {}

    def update_global_results_settings(self, data: dict) -> dict:
        return data

    def get_timezone_settings(self) -> dict:
        return {"timezone": "America/Sao_Paulo"}

    def update_timezone_settings(self, data: dict) -> dict:
        return data

    def get_retention_settings(self) -> dict:
        return {"run_results_days": 90, "profiler_results_days": 30, "comments_days": 365}

    def update_retention_settings(self, data: dict) -> dict:
        return data

    def get_compute_settings(self) -> dict:
        return {"warehouse_id": "warehouse-001", "cluster_id": None, "grant_access": True}

    def update_compute_settings(self, data: dict) -> dict:
        return data

    def get_sample_limits(self) -> dict:
        return {"dry_run_sample_rows": 10000, "profiler_sample_rows": 50000}

    def update_sample_limits(self, data: dict) -> dict:
        return data

    def get_draft_run_gate(self) -> dict:
        return {"enabled": False}

    def update_draft_run_gate(self, data: dict) -> dict:
        return data

    def get_share_tables_settings(self) -> dict:
        return {"enabled": True}

    def update_share_tables_settings(self, data: dict) -> dict:
        return data

    def list_compute_warehouses(self) -> list:
        return [
            {"id": "warehouse-001", "name": "DQX Warehouse (Small)", "state": "RUNNING"},
            {"id": "warehouse-002", "name": "Shared Warehouse", "state": "STOPPED"},
        ]

    def list_compute_clusters(self) -> list:
        return [
            {"id": "cluster-001", "name": "DQX Job Cluster", "state": "RUNNING"},
        ]

    def list_custom_metrics(self) -> list:
        return [
            {"id": "cm-001", "name": "pct_nulls", "sql": "SELECT COUNT(*) FILTER (WHERE col IS NULL) * 100.0 / COUNT(*) FROM {table}", "description": "Percentual de nulos"},
            {"id": "cm-002", "name": "row_count", "sql": "SELECT COUNT(*) FROM {table}", "description": "Contagem de linhas"},
        ]

    def create_custom_metric(self, data: dict) -> dict:
        return {"id": "cm-new", **data}

    def update_custom_metric(self, metric_id: str, data: dict) -> dict:
        return {"id": metric_id, **data}

    def delete_custom_metric(self, metric_id: str) -> None:
        pass

    def reset_database(self) -> dict:
        return {"status": "ok", "message": "Banco de dados resetado com sucesso."}

    def deploy_demo(self) -> dict:
        return {"status": "ok", "message": "Demo implantada com sucesso."}

    # ── Discovery ─────────────────────────────────────────────────────────────

    def list_catalogs(self) -> list:
        return ["main", "hive_metastore", "dqx"]

    def list_schemas(self, catalog: str) -> list:
        return ["default", "sales", "finance", "hr"]

    def list_tables(self, catalog: str, schema: str) -> list:
        return ["orders", "customers", "products", "transactions"]

    def list_columns(self, catalog: str, schema: str, table: str) -> list:
        return [
            {"name": "id", "type": "bigint"},
            {"name": "created_at", "type": "timestamp"},
            {"name": "status", "type": "string"},
            {"name": "amount", "type": "double"},
        ]

    # ── Registry Rules ────────────────────────────────────────────────────────

    def list_registry_rules(self, **params) -> list:
        return [
            {
                "id": "rule-001",
                "name": "not_null_id",
                "status": "APPROVED",
                "severity": "CRITICAL",
                "description": "ID must not be null",
                "created_at": "2025-01-10",
            },
            {
                "id": "rule-002",
                "name": "valid_status",
                "status": "DRAFT",
                "severity": "HIGH",
                "description": "Status must be one of allowed values",
                "created_at": "2025-02-15",
            },
            {
                "id": "rule-003",
                "name": "amount_positive",
                "status": "SUBMITTED",
                "severity": "MEDIUM",
                "description": "Amount must be greater than zero",
                "created_at": "2025-03-01",
            },
        ]

    def get_registry_rule(self, rule_id: str) -> dict:
        return {
            "id": rule_id,
            "name": "mock_rule",
            "status": "APPROVED",
            "severity": "HIGH",
            "description": "Mock rule for testing",
        }

    def create_registry_rule(self, data: dict) -> dict:
        return {"id": "rule-new", **data}

    def update_registry_rule(self, rule_id: str, data: dict) -> dict:
        return {"id": rule_id, **data}

    def delete_registry_rule(self, rule_id: str) -> None:
        pass

    def submit_registry_rule(self, rule_id: str) -> dict:
        return {"id": rule_id, "status": "SUBMITTED"}

    def approve_registry_rule(self, rule_id: str, rationale: str = "") -> dict:
        return {"id": rule_id, "status": "APPROVED"}

    def reject_registry_rule(self, rule_id: str, rationale: str = "") -> dict:
        return {"id": rule_id, "status": "REJECTED"}

    def deprecate_registry_rule(self, rule_id: str) -> dict:
        return {"id": rule_id, "status": "DEPRECATED"}

    def get_registry_rule_versions(self, rule_id: str) -> list:
        return [
            {"version": 2, "status": "APPROVED", "created_at": "2025-03-01"},
            {"version": 1, "status": "DEPRECATED", "created_at": "2025-01-10"},
        ]

    def batch_import_registry_rules(self, data: dict) -> dict:
        return {"imported": 3, "skipped": 0}

    # ── Monitored Tables ──────────────────────────────────────────────────────

    def list_monitored_tables(self, **params) -> list:
        return [
            {
                "binding_id": "mt-001",
                "table_fqn": "main.sales.orders",
                "status": "APPROVED",
                "dq_score": 97.2,
                "last_run": "2025-09-20",
            },
            {
                "binding_id": "mt-002",
                "table_fqn": "main.finance.transactions",
                "status": "DRAFT",
                "dq_score": 84.5,
                "last_run": "2025-09-19",
            },
            {
                "binding_id": "mt-003",
                "table_fqn": "main.hr.employees",
                "status": "SUBMITTED",
                "dq_score": 91.0,
                "last_run": "2025-09-18",
            },
        ]

    def get_monitored_table(self, binding_id: str) -> dict:
        return {
            "binding_id": binding_id,
            "table_fqn": "main.sales.orders",
            "status": "APPROVED",
            "dq_score": 97.2,
            "schedule": "0 6 * * *",
            "applied_rules": [
                {"rule_id": "rule-001", "name": "not_null_id", "severity": "CRITICAL", "status": "APPROVED", "pinned_version": None},
                {"rule_id": "rule-002", "name": "valid_status", "severity": "HIGH", "status": "APPROVED", "pinned_version": 1},
            ],
        }

    def apply_rule_to_table(self, binding_id: str, rule_id: str) -> dict:
        return {"binding_id": binding_id, "rule_id": rule_id, "status": "applied"}

    def remove_rule_from_table(self, binding_id: str, rule_id: str) -> dict:
        return {"binding_id": binding_id, "rule_id": rule_id, "status": "removed"}

    def update_table_schedule(self, binding_id: str, data: dict) -> dict:
        return {"binding_id": binding_id, **data}

    def list_table_versions(self, binding_id: str) -> list:
        return [
            {"version": 3, "status": "APPROVED", "created_at": "2025-09-01", "rules_count": 2},
            {"version": 2, "status": "APPROVED", "created_at": "2025-07-15", "rules_count": 1},
            {"version": 1, "status": "DEPRECATED", "created_at": "2025-05-01", "rules_count": 1},
        ]

    def list_table_runs(self, binding_id: str) -> list:
        return [
            {"run_id": "run-001", "status": "SUCCEEDED", "started_at": "2025-09-20T10:00:00", "dq_score": 97.2, "checks_passed": 42, "checks_failed": 2},
            {"run_id": "run-002", "status": "SUCCEEDED", "started_at": "2025-09-19T10:00:00", "dq_score": 95.8, "checks_passed": 40, "checks_failed": 4},
            {"run_id": "run-003", "status": "FAILED",    "started_at": "2025-09-18T10:00:00", "dq_score": None, "checks_passed": 0,  "checks_failed": 0},
        ]

    def create_monitored_table(self, data: dict) -> dict:
        return {"binding_id": "mt-new", **data}

    def delete_monitored_table(self, binding_id: str) -> None:
        pass

    def run_monitored_table(self, binding_id: str) -> dict:
        return {"run_id": "run-mock-001", "status": "RUNNING"}

    def submit_monitored_table(self, binding_id: str) -> dict:
        return {"binding_id": binding_id, "status": "SUBMITTED"}

    def approve_monitored_table(self, binding_id: str, rationale: str = "") -> dict:
        return {"binding_id": binding_id, "status": "APPROVED"}

    def reject_monitored_table(self, binding_id: str, rationale: str = "") -> dict:
        return {"binding_id": binding_id, "status": "REJECTED"}

    def revert_monitored_table(self, binding_id: str) -> dict:
        return {"binding_id": binding_id, "status": "DRAFT"}

    # ── Collections ───────────────────────────────────────────────────────────

    def list_collections(self, **params) -> list:
        return [
            {
                "product_id": "col-001",
                "name": "Sales Data Product",
                "status": "APPROVED",
                "dq_score": 95.1,
                "table_count": 3,
            },
            {
                "product_id": "col-002",
                "name": "Finance Analytics",
                "status": "DRAFT",
                "dq_score": 88.4,
                "table_count": 2,
            },
        ]

    def get_collection(self, product_id: str) -> dict:
        return {
            "product_id": product_id,
            "name": "Sales Data Product",
            "description": "Agrupa tabelas do domínio de vendas para validação conjunta.",
            "status": "APPROVED",
            "dq_score": 95.1,
            "schedule": "0 7 * * 1",
            "last_run": "2025-09-20",
        }

    def create_collection(self, data: dict) -> dict:
        return {"product_id": "col-new", **data}

    def update_collection(self, product_id: str, data: dict) -> dict:
        return {"product_id": product_id, **data}

    def delete_collection(self, product_id: str) -> None:
        pass

    def run_collection(self, product_id: str) -> dict:
        return {"run_id": "run-mock-col-001", "status": "RUNNING"}

    def submit_collection(self, product_id: str) -> dict:
        return {"product_id": product_id, "status": "SUBMITTED"}

    def approve_collection(self, product_id: str, rationale: str = "") -> dict:
        return {"product_id": product_id, "status": "APPROVED"}

    def reject_collection(self, product_id: str, rationale: str = "") -> dict:
        return {"product_id": product_id, "status": "REJECTED"}

    def revert_collection(self, product_id: str) -> dict:
        return {"product_id": product_id, "status": "DRAFT"}

    def list_collection_tables(self, product_id: str) -> list:
        return [
            {"binding_id": "mt-001", "table_fqn": "main.sales.orders", "status": "APPROVED", "dq_score": 97.2},
            {"binding_id": "mt-002", "table_fqn": "main.finance.transactions", "status": "APPROVED", "dq_score": 84.5},
        ]

    def add_table_to_collection(self, product_id: str, binding_id: str) -> dict:
        return {"product_id": product_id, "binding_id": binding_id}

    def remove_table_from_collection(self, product_id: str, binding_id: str) -> dict:
        return {"product_id": product_id, "binding_id": binding_id}

    def update_collection_schedule(self, product_id: str, data: dict) -> dict:
        return {"product_id": product_id, **data}

    def list_collection_runs(self, product_id: str) -> list:
        return [
            {"run_id": "run-col-001", "status": "SUCCEEDED", "started_at": "2025-09-20T10:00:00", "dq_score": 94.5, "checks_passed": 80, "checks_failed": 5},
            {"run_id": "run-col-002", "status": "SUCCEEDED", "started_at": "2025-09-19T10:00:00", "dq_score": 91.2, "checks_passed": 75, "checks_failed": 9},
            {"run_id": "run-col-003", "status": "FAILED",    "started_at": "2025-09-18T10:00:00", "dq_score": None, "checks_passed": 0,  "checks_failed": 0},
        ]

    def list_collection_versions(self, product_id: str) -> list:
        return [
            {"version": 2, "status": "APPROVED", "created_at": "2025-09-01", "table_count": 2},
            {"version": 1, "status": "DEPRECATED", "created_at": "2025-07-01", "table_count": 1},
        ]

    # ── Dry Runs ──────────────────────────────────────────────────────────────

    def list_dry_runs(self, **params) -> list:
        return [
            {
                "run_id": "run-001",
                "table_fqn": "main.sales.orders",
                "status": "SUCCEEDED",
                "started_at": "2025-09-20T10:00:00",
                "dq_score": 97.2,
            },
            {
                "run_id": "run-002",
                "table_fqn": "main.finance.transactions",
                "status": "FAILED",
                "started_at": "2025-09-19T14:30:00",
                "dq_score": 72.1,
            },
        ]

    def get_run_status(self, run_id: str) -> dict:
        return {"run_id": run_id, "status": "SUCCEEDED"}

    def get_run_results(self, run_id: str) -> dict:
        return {"run_id": run_id, "dq_score": 97.2, "checks_passed": 42, "checks_failed": 2}

    def submit_dry_run(self, data: dict) -> dict:
        return {"run_id": "run-new", "status": "RUNNING"}

    # ── Profiler ──────────────────────────────────────────────────────────────

    def submit_profile_run(self, data: dict) -> dict:
        return {"run_id": "prof-new", "status": "RUNNING"}

    def list_profiler_runs(self, **params) -> list:
        return [
            {"run_id": "prof-001", "table_fqn": "main.sales.orders", "status": "SUCCEEDED", "started_at": "2025-09-20T08:00:00", "dq_score": None},
            {"run_id": "prof-002", "table_fqn": "main.hr.employees", "status": "SUCCEEDED", "started_at": "2025-09-19T08:00:00", "dq_score": None},
        ]

    def get_profiler_run_status(self, run_id: str) -> dict:
        return {"run_id": run_id, "status": "SUCCEEDED"}

    def get_profiler_run_results(self, run_id: str) -> dict:
        return {
            "run_id": run_id,
            "table_fqn": "main.sales.orders",
            "status": "SUCCEEDED",
            "row_count": 48_230,
            "columns_profiled": 4,
            "columns": [
                {
                    "name": "id",
                    "type": "bigint",
                    "null_pct": 0.0,
                    "unique_pct": 100.0,
                    "min": 1,
                    "max": 48_230,
                    "mean": 24_115.0,
                    "stddev": 13_930.0,
                    "candidates": [
                        {"check": "is_not_null", "rationale": "Nenhum valor nulo detectado (0%)", "confidence": 0.99},
                        {"check": "is_unique", "rationale": "Todos os 48.230 valores são únicos", "confidence": 0.99},
                    ],
                },
                {
                    "name": "status",
                    "type": "string",
                    "null_pct": 0.2,
                    "unique_pct": 0.01,
                    "min": None,
                    "max": None,
                    "mean": None,
                    "stddev": None,
                    "top_values": ["ACTIVE", "CLOSED", "PENDING"],
                    "candidates": [
                        {"check": "is_in_list", "rationale": "99.8% dos valores estão em {'ACTIVE','CLOSED','PENDING'}", "confidence": 0.95},
                    ],
                },
                {
                    "name": "amount",
                    "type": "double",
                    "null_pct": 1.1,
                    "unique_pct": 87.3,
                    "min": 0.01,
                    "max": 99_999.99,
                    "mean": 1_234.56,
                    "stddev": 2_301.44,
                    "candidates": [
                        {"check": "is_in_range", "rationale": "98.9% dos valores entre 0.01 e 99999.99", "confidence": 0.88},
                    ],
                },
                {
                    "name": "created_at",
                    "type": "timestamp",
                    "null_pct": 0.0,
                    "unique_pct": 99.8,
                    "min": "2020-01-01",
                    "max": "2025-09-20",
                    "mean": None,
                    "stddev": None,
                    "candidates": [
                        {"check": "is_not_null", "rationale": "Nenhum valor nulo detectado (0%)", "confidence": 0.99},
                    ],
                },
            ],
        }

    # ── DQ Results ────────────────────────────────────────────────────────────

    def get_global_results(self, **params) -> dict:
        return {
            "avg_score": 93.7,
            "tables_monitored": 12,
            "checks_failed": 14,
            "runs_today": 5,
            "trend": [91.2, 92.5, 93.1, 93.7],
            "trend_labels": ["Jun", "Jul", "Ago", "Set"],
            "by_severity": {"CRITICAL": 2, "HIGH": 5, "MEDIUM": 12, "LOW": 8},
        }

    def get_table_results(self, table_fqn: str, **params) -> dict:
        return {"table_fqn": table_fqn, "dq_score": 95.0}

    # ── Roles & RBAC ──────────────────────────────────────────────────────────

    def list_role_mappings(self) -> list:
        return [
            {"id": "rm-001", "group": "admins", "role": "ADMIN"},
            {"id": "rm-002", "group": "data-engineers", "role": "RULE_AUTHOR"},
        ]

    def create_role_mapping(self, data: dict) -> dict:
        return {"id": "rm-new", **data}

    def delete_role_mapping(self, mapping_id: str) -> None:
        pass

    def list_workspace_groups(self) -> list:
        return ["admins", "data-engineers", "analysts", "viewers"]

    def list_available_roles(self) -> list:
        return ["ADMIN", "RULE_APPROVER", "RULE_AUTHOR", "VIEWER"]

    # ── Marketplace ───────────────────────────────────────────────────────────

    def list_marketplace_packs(self) -> list:
        return [
            {
                "id": "pack-001",
                "name": "Financial Data Quality",
                "description": "Rules for financial datasets",
                "rule_count": 15,
            },
            {
                "id": "pack-002",
                "name": "PII Compliance",
                "description": "Rules to detect and validate PII fields",
                "rule_count": 8,
            },
            {
                "id": "pack-003",
                "name": "E-Commerce Basics",
                "description": "Standard rules for e-commerce tables",
                "rule_count": 22,
            },
        ]

    # ── Check Functions ───────────────────────────────────────────────────────

    def list_check_functions(self) -> list:
        return [
            {"name": "is_not_null", "description": "Column must not be null"},
            {"name": "is_unique", "description": "Column values must be unique"},
            {"name": "is_in_range", "description": "Numeric value within min/max range"},
            {"name": "matches_regex", "description": "Value matches a regular expression"},
            {"name": "is_in_list", "description": "Value is one of an allowed list"},
        ]

    # ── Comments ──────────────────────────────────────────────────────────────

    def list_comments(self, entity_type: str, entity_id: str) -> list:
        return [
            {"id": "c-001", "author": "alice@mock.local", "text": "Looks good!", "created_at": "2025-09-15"},
            {"id": "c-002", "author": "bob@mock.local", "text": "Approved after review.", "created_at": "2025-09-16"},
        ]

    def add_comment(self, data: dict) -> dict:
        return {"id": "c-new", **data}

    def delete_comment(self, comment_id: str) -> None:
        pass

    # ── Schedules ─────────────────────────────────────────────────────────────

    def list_schedules(self) -> list:
        return [
            {"name": "daily-sales", "cron": "0 6 * * *", "enabled": True},
            {"name": "weekly-finance", "cron": "0 8 * * 1", "enabled": True},
        ]

    def get_schedule(self, name: str) -> dict:
        return {"name": name, "cron": "0 6 * * *", "enabled": True}

    def update_schedule(self, name: str, data: dict) -> dict:
        return {"name": name, **data}

    def delete_schedule(self, name: str) -> None:
        pass

    # ── AI ────────────────────────────────────────────────────────────────────

    def generate_checks(self, data: dict) -> dict:
        prompt = data.get("prompt", "")
        col = data.get("column", "id")
        return {
            "yaml": f"- check:\n    function: is_not_null\n    column: {col}\n  criticality: critical\n  name: not_null_{col}\n"
        }

    def ai_write_sql(self, data: dict) -> dict:
        col = data.get("column", "id")
        return {"sql": f"SELECT * FROM {{table}} WHERE {col} IS NOT NULL AND {col} > 0"}

    def ai_improve_sql(self, data: dict) -> dict:
        sql = data.get("sql", "")
        return {"sql": sql + "\n-- LIMIT 1000  /* Adicionado para melhor performance */"}

    def ai_explain_sql(self, data: dict) -> dict:
        return {"explanation": "Esta expressão SQL valida que os valores da coluna não são nulos e satisfazem a condição definida. Registros que violam a regra são retornados como falhas."}

    def check_rule_duplicates(self, data: dict) -> dict:
        return {"duplicates": [], "has_duplicates": False}

    def generate_rules_from_contract(self, data: dict) -> dict:
        return {
            "rules": [
                {"name": "not_null_id", "severity": "CRITICAL", "check_function": "is_not_null", "column": "id", "description": "ID must not be null"},
                {"name": "unique_id", "severity": "HIGH", "check_function": "is_unique", "column": "id", "description": "ID must be unique"},
                {"name": "valid_status", "severity": "MEDIUM", "check_function": "is_in_list", "column": "status", "description": "Status must be a valid value"},
            ]
        }

    def export_registry_rules(self, rule_ids: list = None) -> str:
        return "- check:\n    function: is_not_null\n    column: id\n  criticality: critical\n  name: not_null_id\n"

    def list_ai_serving_endpoints(self) -> list:
        return ["databricks-meta-llama-3-3-70b-instruct", "databricks-dbrx-instruct"]

    def submit_analytics_query(self, question: str, context: dict = None) -> dict:
        import uuid, time
        job_id = f"job-{uuid.uuid4().hex[:8]}"
        # Simula resposta imediata (em produção seria assíncrono)
        q = question.lower()

        if "score" in q or "qualidade" in q:
            result = {
                "type": "metrics",
                "data": {
                    "metrics": [
                        {"label": "DQ Score Global", "value": "93.7%", "delta": "+1.2%"},
                        {"label": "Tabelas Monitoradas", "value": 12},
                        {"label": "Checks com Falha", "value": 14, "delta": "-3"},
                    ]
                },
                "message": "Aqui estão as métricas globais de qualidade de dados:",
            }
        elif "tendên" in q or "trend" in q or "histórico" in q:
            result = {
                "type": "chart",
                "chart_type": "line",
                "data": {
                    "labels": ["Jun", "Jul", "Ago", "Set"],
                    "series": [
                        {"name": "DQ Score", "values": [90.1, 91.5, 92.8, 93.7]},
                    ],
                },
                "message": "Tendência do DQ Score nos últimos 4 meses:",
            }
        elif "falha" in q or "erro" in q or "check" in q:
            result = {
                "type": "table",
                "data": {
                    "columns": ["Tabela", "Regra", "Severidade", "Falhas"],
                    "rows": [
                        ["main.sales.orders", "not_null_id", "CRITICAL", 3],
                        ["main.finance.transactions", "amount_positive", "HIGH", 8],
                        ["main.hr.employees", "valid_status", "MEDIUM", 3],
                    ],
                },
                "message": "Checks com falha nas últimas 24h:",
            }
        elif "tabela" in q or "monitorad" in q:
            result = {
                "type": "chart",
                "chart_type": "bar",
                "data": {
                    "labels": ["main.sales.orders", "main.finance.transactions", "main.hr.employees"],
                    "series": [{"name": "DQ Score (%)", "values": [97.2, 84.5, 91.0]}],
                },
                "message": "DQ Score por tabela monitorada:",
            }
        elif "severidade" in q or "crítico" in q or "critical" in q:
            result = {
                "type": "mixed",
                "parts": [
                    {
                        "type": "chart",
                        "chart_type": "bar",
                        "data": {
                            "labels": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                            "series": [{"name": "Falhas", "values": [2, 5, 12, 8]}],
                        },
                    },
                    {
                        "type": "metrics",
                        "data": {
                            "metrics": [
                                {"label": "CRITICAL", "value": 2, "delta": "+1"},
                                {"label": "HIGH", "value": 5},
                                {"label": "MEDIUM", "value": 12, "delta": "-2"},
                            ]
                        },
                    },
                ],
                "message": "Distribuição de falhas por severidade:",
            }
        else:
            result = {
                "type": "text",
                "message": (
                    "Posso responder consultas sobre:\n\n"
                    "- **DQ Score** global e por tabela\n"
                    "- **Tendências** históricas de qualidade\n"
                    "- **Checks com falha** por tabela, regra ou severidade\n"
                    "- **Comparativos** entre collections\n\n"
                    "Tente perguntar: *Qual o DQ Score global?* ou *Quais checks falharam hoje?*"
                ),
            }

        return {
            "job_id": job_id,
            "status": "SUCCEEDED",
            "result": result,
        }

    def get_analytics_query_status(self, job_id: str) -> dict:
        return {"job_id": job_id, "status": "SUCCEEDED"}

    def submit_analytics_feedback(self, job_id: str, rating: str, comment: str = "") -> dict:
        return {"job_id": job_id, "rating": rating, "recorded": True}

    def list_mentionable_entities(self) -> dict:
        return {
            "tables": [
                {"id": "mt-001", "label": "main.sales.orders", "type": "table"},
                {"id": "mt-002", "label": "main.finance.transactions", "type": "table"},
                {"id": "mt-003", "label": "main.hr.employees", "type": "table"},
            ],
            "rules": [
                {"id": "rule-001", "label": "not_null_id", "type": "rule"},
                {"id": "rule-002", "label": "valid_status", "type": "rule"},
                {"id": "rule-003", "label": "amount_positive", "type": "rule"},
            ],
            "collections": [
                {"id": "col-001", "label": "Sales Data Product", "type": "collection"},
                {"id": "col-002", "label": "Finance Analytics", "type": "collection"},
            ],
        }

    # ── Permissões por objeto ─────────────────────────────────────────────────────

    def list_object_grants(self, object_type: str, object_id: str) -> list:
        return [
            {"principal": "alice@mock.local", "permission": "VIEW", "granted_by": "admin@mock.local"},
            {"principal": "bob@mock.local", "permission": "MODIFY", "granted_by": "admin@mock.local"},
        ]

    def add_object_grant(self, object_type: str, object_id: str, data: dict) -> dict:
        return {"principal": data.get("principal"), "permission": data.get("permission")}

    def remove_object_grant(self, object_type: str, object_id: str, principal: str) -> None:
        pass

    def search_principals(self, query: str) -> list:
        all_p = ["alice@mock.local", "bob@mock.local", "carol@mock.local", "admins", "data-engineers"]
        return [p for p in all_p if query.lower() in p.lower()] if query else all_p

    # ── Diff de revisão ───────────────────────────────────────────────────────────

    def get_collection_review_changes(self, product_id: str) -> dict:
        return {
            "before": {"name": "Sales Data Product", "table_count": 1, "status": "APPROVED"},
            "after": {"name": "Sales Data Product", "table_count": 2, "status": "SUBMITTED"},
            "changed_fields": ["table_count"],
        }

    # ── Quarentena ────────────────────────────────────────────────────────────────

    def get_quarantine_records(self, run_id: str, limit: int = 100) -> list:
        return [
            {"row_id": 1001, "table": "main.sales.orders", "check": "not_null_id", "severity": "CRITICAL", "value": None, "reason": "Valor nulo detectado"},
            {"row_id": 2042, "table": "main.sales.orders", "check": "amount_positive", "severity": "HIGH", "value": -50.0, "reason": "Valor negativo"},
            {"row_id": 3108, "table": "main.sales.orders", "check": "valid_status", "severity": "MEDIUM", "value": "UNKNOWN", "reason": "Valor fora da lista permitida"},
        ]

    def get_quarantine_count(self, run_id: str) -> dict:
        return {"count": 3, "by_severity": {"CRITICAL": 1, "HIGH": 1, "MEDIUM": 1}}

    def export_quarantine(self, run_id: str) -> str:
        return "row_id,table,check,severity,value,reason\n1001,main.sales.orders,not_null_id,CRITICAL,,Valor nulo detectado\n2042,main.sales.orders,amount_positive,HIGH,-50.0,Valor negativo\n"

    def ai_chat(self, messages: list, endpoint: str = None) -> dict:
        last = messages[-1].get("content", "") if messages else ""
        responses = {
            "regra": "Para criar uma regra de qualidade, acesse **Registry de Regras → + Nova Regra**. Você pode usar o modo DQX Native (formulário guiado) ou SQL direto. Qual tipo de validação você precisa?",
            "nulo": "Para validar campos nulos, use a função `is_not_null` no modo DQX Native:\n```yaml\n- check:\n    function: is_not_null\n    column: nome_coluna\n  criticality: critical\n```",
            "score": "O **DQ Score** é calculado como a proporção de checks aprovados sobre o total. Um score de 95% significa que 95% dos registros passaram em todas as validações configuradas.",
            "collection": "Uma **Collection** agrupa múltiplas tabelas monitoradas para validação conjunta. Útil para domínios como *Sales* ou *Finance* onde as regras precisam ser executadas em conjunto.",
        }
        for kw, resp in responses.items():
            if kw in last.lower():
                return {"role": "assistant", "content": resp}
        return {
            "role": "assistant",
            "content": (
                "Sou o assistente DQX Studio. Posso ajudar você a:\n\n"
                "- **Criar regras** de qualidade de dados\n"
                "- **Entender** funções de validação disponíveis\n"
                "- **Configurar** tabelas monitoradas e collections\n"
                "- **Interpretar** resultados e DQ scores\n\n"
                "Como posso ajudar?"
            ),
        }
