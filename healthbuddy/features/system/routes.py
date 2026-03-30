"""System routes such as health checks and API error handling."""

from __future__ import annotations

from flask import Blueprint, jsonify, request, session

from healthbuddy.features.analysis.service import get_workflow
from healthbuddy.features.auth.service import auth_provider_status, get_patient_collection

system_bp = Blueprint("system", __name__)


@system_bp.get("/api/health")
@system_bp.get("/api/health/")
def health():
    """Simple readiness endpoint."""
    _, workflow_error = get_workflow()
    _, mongo_error = get_patient_collection()
    return jsonify(
        {
            "ok": True,
            "name": "HealthBuddy",
            "services": {
                "workflow": {"ok": workflow_error is None, "error": workflow_error},
                "mongodb": {"ok": mongo_error is None, "error": mongo_error},
                "auth": {"ok": mongo_error is None, "providers": auth_provider_status()},
            },
            "authenticated": bool(session.get("patient_email")),
        }
    )


def api_not_found(path: str):
    return jsonify({"ok": False, "error": f"API route not found: {path}"}), 404


def api_method_not_allowed(path: str):
    return jsonify({"ok": False, "error": f"Method not allowed for API route: {path}"}), 405

