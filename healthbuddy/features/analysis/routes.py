"""Analysis API routes."""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request, session

from healthbuddy.features.analysis.service import run_health_analysis

logger = logging.getLogger(__name__)
analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.post("/api/analyze")
@analysis_bp.post("/api/analyze/")
def analyze():
    """Run symptom analysis and return structured section outputs."""
    if not session.get("patient_email"):
        return jsonify({"ok": False, "error": "Please log in to analyze symptoms."}), 401

    payload = request.get_json(silent=True) or {}
    user_input = str(payload.get("symptoms", "")).strip()
    if not user_input:
        return jsonify({"ok": False, "error": "Please describe your symptoms first."}), 400

    try:
        results = run_health_analysis(user_input)
        return jsonify({"ok": True, "results": results})
    except Exception as exc:
        logger.error("Error during health analysis: %s", exc, exc_info=True)
        return jsonify({"ok": False, "error": str(exc)}), 500

