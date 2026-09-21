from typing import Any, Optional

import requests
import streamlit as st


class APIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(message)


class DQXClient:
    """HTTP client for the DQX Studio FastAPI backend (/api/v1/*)."""

    def __init__(self, base_url: str, token: str):
        self._base = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-Forwarded-Access-Token": token,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    # ── HTTP primitives ───────────────────────────────────────────────────────

    def _url(self, path: str) -> str:
        return f"{self._base}/api/v1{path}"

    def _handle(self, r: requests.Response) -> Any:
        if r.status_code == 401:
            raise APIError(401, "Não autorizado. Token inválido ou expirado.")
        if r.status_code == 403:
            raise APIError(403, "Sem permissão para realizar esta operação.")
        if r.status_code == 503:
            raise APIError(503, "Aplicação ainda em configuração. Aguarde o setup concluir.")
        r.raise_for_status()
        return r.json() if r.content else None

    def get(self, path: str, params: Optional[dict] = None) -> Any:
        return self._handle(self._session.get(self._url(path), params=params, timeout=30))

    def post(self, path: str, json: Optional[dict] = None, **kwargs) -> Any:
        return self._handle(self._session.post(self._url(path), json=json, timeout=60, **kwargs))

    def put(self, path: str, json: Optional[dict] = None) -> Any:
        return self._handle(self._session.put(self._url(path), json=json, timeout=30))

    def delete(self, path: str) -> Any:
        return self._handle(self._session.delete(self._url(path), timeout=30))

    # ── Auth & user ───────────────────────────────────────────────────────────

    def get_current_user(self) -> dict:
        return self.get("/current-user")

    def get_current_user_role(self) -> dict:
        return self.get("/current-user/role")

    # ── Home ──────────────────────────────────────────────────────────────────

    def get_home_stats(self) -> dict:
        return self.get("/home/stats")

    # ── Setup & version ───────────────────────────────────────────────────────

    def get_setup_status(self) -> dict:
        return self.get("/setup/status")

    def get_version(self) -> dict:
        return self.get("/version")

    # ── Config ────────────────────────────────────────────────────────────────

    def get_config(self) -> dict:
        return self.get("/config")

    def update_config(self, data: dict) -> dict:
        return self.put("/config", json=data)

    def get_label_definitions(self) -> dict:
        return self.get("/config/label-definitions")

    def update_label_definitions(self, data: dict) -> dict:
        return self.put("/config/label-definitions", json=data)

    def get_workspace_host(self) -> dict:
        return self.get("/config/workspace-host")

    def get_ai_settings(self) -> dict:
        return self.get("/config/ai-settings")

    def update_ai_settings(self, data: dict) -> dict:
        return self.put("/config/ai-settings", json=data)

    def get_approvals_mode(self) -> dict:
        return self.get("/config/approvals-mode")

    def get_run_review_statuses(self) -> dict:
        return self.get("/config/run-review-statuses")

    def get_rules_registry_settings(self) -> dict:
        return self.get("/config/rules-registry-settings")

    def get_global_results_settings(self) -> dict:
        return self.get("/config/global-results-settings")

    # ── Discovery ─────────────────────────────────────────────────────────────

    def list_catalogs(self) -> list:
        return self.get("/discovery/catalogs")

    def list_schemas(self, catalog: str) -> list:
        return self.get("/discovery/schemas", params={"catalog": catalog})

    def list_tables(self, catalog: str, schema: str) -> list:
        return self.get("/discovery/tables", params={"catalog": catalog, "schema": schema})

    def list_columns(self, catalog: str, schema: str, table: str) -> list:
        return self.get(
            "/discovery/columns",
            params={"catalog": catalog, "schema": schema, "table": table},
        )

    # ── Registry Rules ────────────────────────────────────────────────────────

    def list_registry_rules(self, **params) -> list:
        return self.get("/registry-rules", params=params or None)

    def get_registry_rule(self, rule_id: str) -> dict:
        return self.get(f"/registry-rules/{rule_id}")

    def create_registry_rule(self, data: dict) -> dict:
        return self.post("/registry-rules", json=data)

    def update_registry_rule(self, rule_id: str, data: dict) -> dict:
        return self.put(f"/registry-rules/{rule_id}", json=data)

    def delete_registry_rule(self, rule_id: str) -> None:
        self.delete(f"/registry-rules/{rule_id}")

    def submit_registry_rule(self, rule_id: str) -> dict:
        return self.post(f"/registry-rules/{rule_id}/submit")

    def approve_registry_rule(self, rule_id: str, rationale: str = "") -> dict:
        return self.post(f"/registry-rules/{rule_id}/approve", json={"rationale": rationale})

    def reject_registry_rule(self, rule_id: str, rationale: str = "") -> dict:
        return self.post(f"/registry-rules/{rule_id}/reject", json={"rationale": rationale})

    def deprecate_registry_rule(self, rule_id: str) -> dict:
        return self.post(f"/registry-rules/{rule_id}/deprecate")

    def get_registry_rule_versions(self, rule_id: str) -> list:
        return self.get(f"/registry-rules/{rule_id}/versions")

    def batch_import_registry_rules(self, data: dict) -> dict:
        return self.post("/registry-rules/batch-import", json=data)

    # ── Monitored Tables ──────────────────────────────────────────────────────

    def list_monitored_tables(self, **params) -> list:
        return self.get("/monitored-tables", params=params or None)

    def get_monitored_table(self, binding_id: str) -> dict:
        return self.get(f"/monitored-tables/{binding_id}")

    def create_monitored_table(self, data: dict) -> dict:
        return self.post("/monitored-tables", json=data)

    def delete_monitored_table(self, binding_id: str) -> None:
        self.delete(f"/monitored-tables/{binding_id}")

    def run_monitored_table(self, binding_id: str) -> dict:
        return self.post(f"/monitored-tables/{binding_id}/run")

    def submit_monitored_table(self, binding_id: str) -> dict:
        return self.post(f"/monitored-tables/{binding_id}/submit")

    def approve_monitored_table(self, binding_id: str, rationale: str = "") -> dict:
        return self.post(f"/monitored-tables/{binding_id}/approve", json={"rationale": rationale})

    def reject_monitored_table(self, binding_id: str, rationale: str = "") -> dict:
        return self.post(f"/monitored-tables/{binding_id}/reject", json={"rationale": rationale})

    def revert_monitored_table(self, binding_id: str) -> dict:
        return self.post(f"/monitored-tables/{binding_id}/revert")

    # ── Collections / Data Products ───────────────────────────────────────────

    def list_collections(self, **params) -> list:
        return self.get("/data-products", params=params or None)

    def get_collection(self, product_id: str) -> dict:
        return self.get(f"/data-products/{product_id}")

    def create_collection(self, data: dict) -> dict:
        return self.post("/data-products", json=data)

    def update_collection(self, product_id: str, data: dict) -> dict:
        return self.put(f"/data-products/{product_id}", json=data)

    def delete_collection(self, product_id: str) -> None:
        self.delete(f"/data-products/{product_id}")

    def run_collection(self, product_id: str) -> dict:
        return self.post(f"/data-products/{product_id}/run")

    def submit_collection(self, product_id: str) -> dict:
        return self.post(f"/data-products/{product_id}/submit")

    def approve_collection(self, product_id: str, rationale: str = "") -> dict:
        return self.post(f"/data-products/{product_id}/approve", json={"rationale": rationale})

    def reject_collection(self, product_id: str, rationale: str = "") -> dict:
        return self.post(f"/data-products/{product_id}/reject", json={"rationale": rationale})

    # ── Dry Runs ──────────────────────────────────────────────────────────────

    def list_dry_runs(self, **params) -> list:
        return self.get("/dryrun/runs", params=params or None)

    def get_run_status(self, run_id: str) -> dict:
        return self.get(f"/dryrun/runs/{run_id}/status")

    def get_run_results(self, run_id: str) -> dict:
        return self.get(f"/dryrun/results/{run_id}")

    def submit_dry_run(self, data: dict) -> dict:
        return self.post("/dryrun", json=data)

    # ── Profiler ──────────────────────────────────────────────────────────────

    def submit_profile_run(self, data: dict) -> dict:
        return self.post("/profiler/runs", json=data)

    def list_profiler_runs(self, **params) -> list:
        return self.get("/profiler/runs", params=params or None)

    def get_profiler_run_status(self, run_id: str) -> dict:
        return self.get(f"/profiler/runs/{run_id}/status")

    def get_profiler_run_results(self, run_id: str) -> dict:
        return self.get(f"/profiler/runs/{run_id}/results")

    # ── DQ Results ────────────────────────────────────────────────────────────

    def get_global_results(self, **params) -> dict:
        return self.get("/dq-results/global", params=params or None)

    def get_table_results(self, table_fqn: str, **params) -> dict:
        return self.get(f"/dq-results/tables/{table_fqn}", params=params or None)

    # ── Roles & RBAC ──────────────────────────────────────────────────────────

    def list_role_mappings(self) -> list:
        return self.get("/roles/mappings")

    def create_role_mapping(self, data: dict) -> dict:
        return self.post("/roles/mappings", json=data)

    def delete_role_mapping(self, mapping_id: str) -> None:
        self.delete(f"/roles/mappings/{mapping_id}")

    def list_workspace_groups(self) -> list:
        return self.get("/roles/workspace-groups")

    def list_available_roles(self) -> list:
        return self.get("/roles/available")

    # ── Marketplace ───────────────────────────────────────────────────────────

    def list_marketplace_packs(self) -> list:
        return self.get("/marketplace/packs")

    # ── Check Functions ───────────────────────────────────────────────────────

    def list_check_functions(self) -> list:
        return self.get("/check-functions")

    # ── Comments ──────────────────────────────────────────────────────────────

    def list_comments(self, entity_type: str, entity_id: str) -> list:
        return self.get("/comments", params={"entity_type": entity_type, "entity_id": entity_id})

    def add_comment(self, data: dict) -> dict:
        return self.post("/comments", json=data)

    def delete_comment(self, comment_id: str) -> None:
        self.delete(f"/comments/{comment_id}")

    # ── Schedules ─────────────────────────────────────────────────────────────

    def list_schedules(self) -> list:
        return self.get("/schedules")

    def get_schedule(self, name: str) -> dict:
        return self.get(f"/schedules/{name}")

    def update_schedule(self, name: str, data: dict) -> dict:
        return self.put(f"/schedules/{name}", json=data)

    def delete_schedule(self, name: str) -> None:
        self.delete(f"/schedules/{name}")

    # ── AI ────────────────────────────────────────────────────────────────────

    def generate_checks(self, data: dict) -> dict:
        return self.post("/ai/generate-checks", json=data)

    def list_ai_serving_endpoints(self) -> list:
        return self.get("/ai/serving-endpoints")
