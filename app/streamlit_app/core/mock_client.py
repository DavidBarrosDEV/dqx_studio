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
        return {"mode": "OPTIONAL"}

    def get_run_review_statuses(self) -> list:
        return ["Approved", "Rejected", "Pending review"]

    def get_rules_registry_settings(self) -> dict:
        return {"auto_upgrade": False, "pass_threshold": 0.95}

    def get_global_results_settings(self) -> dict:
        return {}

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
        }

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
            "name": "Mock Collection",
            "status": "APPROVED",
            "dq_score": 95.1,
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
        return []

    def get_profiler_run_status(self, run_id: str) -> dict:
        return {"run_id": run_id, "status": "SUCCEEDED"}

    def get_profiler_run_results(self, run_id: str) -> dict:
        return {"run_id": run_id, "columns_profiled": 12}

    # ── DQ Results ────────────────────────────────────────────────────────────

    def get_global_results(self, **params) -> dict:
        return {
            "avg_score": 93.7,
            "trend": [91.2, 92.5, 93.1, 93.7],
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
        return {
            "yaml": "- check:\n    function: is_not_null\n    column: id\n  criticality: critical\n"
        }

    def list_ai_serving_endpoints(self) -> list:
        return ["databricks-meta-llama-3-3-70b-instruct", "databricks-dbrx-instruct"]
