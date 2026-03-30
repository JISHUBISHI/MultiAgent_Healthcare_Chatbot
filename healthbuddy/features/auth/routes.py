"""Authentication API routes."""

from __future__ import annotations

import logging
from urllib.parse import urlencode

from flask import Blueprint, jsonify, redirect, request, session, url_for
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.security import check_password_hash, generate_password_hash

from healthbuddy.features.auth.oauth import get_oauth_client
from healthbuddy.features.auth.service import (
    auth_provider_status,
    clean_email,
    clean_patient_name,
    get_patient_collection,
    now_utc,
    patient_response,
    validate_email,
    validate_password,
)

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


def _social_redirect(status: str, provider: str, message: str):
    query = urlencode({"auth": status, "provider": provider, "message": message})
    default_anchor = "care-console" if status == "success" else "patient-access"
    target = session.pop("post_auth_redirect", None)
    if target:
      base, _, anchor = target.partition("#")
      base = base or url_for("frontend.index")
      anchor = anchor or default_anchor
      return redirect(f"{base}?{query}#{anchor}")
    return redirect(f"{url_for('frontend.index')}?{query}#{default_anchor}")


def _upsert_social_patient(provider: str, provider_user_id: str, name: str, email: str):
    patients, error = get_patient_collection()
    if error:
        raise RuntimeError(error)

    existing = patients.find_one({"email": email})
    social_id_field = f"{provider}_id"
    auth_methods = ["password"] if existing and "auth_methods" not in existing else list(existing.get("auth_methods", [])) if existing else []
    if provider not in auth_methods:
        auth_methods.append(provider)

    if existing:
        patients.update_one(
            {"_id": existing["_id"]},
            {
                "$set": {
                    "name": name or existing.get("name", ""),
                    social_id_field: provider_user_id,
                    "last_login_at": now_utc(),
                },
                "$addToSet": {"auth_methods": provider},
            },
        )
        existing["name"] = name or existing.get("name", "")
        existing["email"] = email
        existing[social_id_field] = provider_user_id
        return existing

    patient = {
        "name": name,
        "email": email,
        social_id_field: provider_user_id,
        "created_at": now_utc(),
        "auth_methods": auth_methods or [provider],
        "last_login_at": now_utc(),
    }
    patients.insert_one(patient)
    return patient


@auth_bp.get("/api/auth/config")
@auth_bp.get("/api/auth/config/")
def auth_config():
    """Return which auth options are available in this environment."""
    _, mongo_error = get_patient_collection()
    return jsonify(
        {
            "ok": True,
            "providers": auth_provider_status(),
            "mongodb_ready": mongo_error is None,
            "mongodb_error": mongo_error,
        }
    )


@auth_bp.post("/api/auth/register")
@auth_bp.post("/api/auth/register/")
def register_patient():
    """Register a new patient account in MongoDB."""
    patients, error = get_patient_collection()
    if error:
        return jsonify({"ok": False, "error": error}), 500

    payload = request.get_json(silent=True) or {}
    name = clean_patient_name(payload.get("name", ""))
    email = clean_email(payload.get("email", ""))
    password = str(payload.get("password", ""))
    confirm_password = str(payload.get("confirm_password", ""))

    if not name:
        return jsonify({"ok": False, "error": "Please enter your full name."}), 400
    if not email:
        return jsonify({"ok": False, "error": "Please enter your email address."}), 400
    if not validate_email(email):
        return jsonify({"ok": False, "error": "Please enter a valid email address."}), 400
    if not password:
        return jsonify({"ok": False, "error": "Please enter a password."}), 400
    if password != confirm_password:
        return jsonify({"ok": False, "error": "Password and confirm password must be the same."}), 400
    password_error = validate_password(password)
    if password_error:
        return jsonify({"ok": False, "error": password_error}), 400

    patient = {
        "name": name,
        "email": email,
        "password_hash": generate_password_hash(password),
        "created_at": now_utc(),
        "auth_methods": ["password"],
        "last_login_at": None,
    }
    try:
        patients.insert_one(patient)
    except DuplicateKeyError:
        return jsonify({"ok": False, "error": "An account with this email already exists."}), 409
    except PyMongoError as exc:
        logger.error("MongoDB insert failed: %s", exc, exc_info=True)
        return jsonify({"ok": False, "error": f"Unable to create account: {exc}"}), 500

    session["patient_email"] = email
    session["patient_name"] = name
    return jsonify({"ok": True, "message": "Registration successful.", "patient": {"name": name, "email": email}}), 201


@auth_bp.get("/api/auth/login")
@auth_bp.get("/api/auth/login/")
@auth_bp.post("/api/auth/login")
@auth_bp.post("/api/auth/login/")
def login_patient():
    """Authenticate an existing patient against MongoDB."""
    if request.method == "GET":
        return jsonify(
            {
                "ok": False,
                "error": "Login must be submitted with POST. Refresh the page to load the latest login form.",
            }
        ), 400

    patients, error = get_patient_collection()
    if error:
        return jsonify({"ok": False, "error": error}), 500

    payload = request.get_json(silent=True) or {}
    email = clean_email(payload.get("email", ""))
    password = str(payload.get("password", ""))

    if not email or not password:
        return jsonify({"ok": False, "error": "Please enter both email and password."}), 400
    if not validate_email(email):
        return jsonify({"ok": False, "error": "Please enter a valid email address."}), 400

    patient = patients.find_one({"email": email})
    if not patient or not check_password_hash(patient.get("password_hash", ""), password):
        return jsonify({"ok": False, "error": "Invalid email or password."}), 401

    patients.update_one({"_id": patient["_id"]}, {"$set": {"last_login_at": now_utc()}})
    session["patient_email"] = patient["email"]
    session["patient_name"] = patient.get("name", "")
    return jsonify({"ok": True, "message": "Login successful.", "patient": patient_response(patient)})


@auth_bp.post("/api/auth/logout")
@auth_bp.post("/api/auth/logout/")
def logout_patient():
    """Clear the current patient session."""
    session.pop("patient_email", None)
    session.pop("patient_name", None)
    return jsonify({"ok": True, "message": "Logged out successfully."})


@auth_bp.post("/api/auth/social/<provider>")
@auth_bp.post("/api/auth/social/<provider>/")
def social_login(provider: str):
    """Placeholder endpoint for social providers until OAuth credentials are configured."""
    provider = provider.lower()
    providers = auth_provider_status()
    if provider not in {"google", "facebook"}:
        return jsonify({"ok": False, "error": f"Unsupported social provider: {provider}"}), 404
    if not providers[provider]:
        return jsonify(
            {
                "ok": False,
                "error": f"{provider.title()} login is not configured yet. Add the provider client ID and secret first.",
            }
        ), 501
    return jsonify(
        {
            "ok": False,
            "error": f"{provider.title()} OAuth configuration exists, but the redirect flow has not been wired in yet.",
        }
    ), 501


@auth_bp.get("/api/auth/me")
@auth_bp.get("/api/auth/me/")
def current_patient():
    """Return the currently authenticated patient, if any."""
    email = session.get("patient_email")
    if not email:
        return jsonify({"ok": True, "authenticated": False, "patient": None})

    patients, error = get_patient_collection()
    if error:
        return jsonify({"ok": False, "error": error}), 500

    patient = patients.find_one({"email": email})
    if not patient:
        session.pop("patient_email", None)
        session.pop("patient_name", None)
        return jsonify({"ok": True, "authenticated": False, "patient": None})

    return jsonify({"ok": True, "authenticated": True, "patient": patient_response(patient)})


@auth_bp.get("/api/auth/social/<provider>/start")
@auth_bp.get("/api/auth/social/<provider>/start/")
def social_login_start(provider: str):
    """Start the OAuth flow for a supported social provider."""
    provider = provider.lower()
    providers = auth_provider_status()
    if provider not in {"google", "facebook"}:
        return _social_redirect("error", provider, f"Unsupported social provider: {provider}")
    if not providers.get(provider):
        return _social_redirect("error", provider, f"{provider.title()} login is not configured yet.")

    client = get_oauth_client(provider)
    if client is None:
        return _social_redirect("error", provider, f"{provider.title()} OAuth client is unavailable.")

    session["post_auth_redirect"] = request.args.get("next") or f"{url_for('frontend.index')}#care-console"
    redirect_uri = url_for("auth.social_login_callback", provider=provider, _external=True)
    return client.authorize_redirect(redirect_uri)


@auth_bp.get("/api/auth/social/<provider>/callback")
@auth_bp.get("/api/auth/social/<provider>/callback/")
def social_login_callback(provider: str):
    """Finish the OAuth flow and create or sign in the patient."""
    provider = provider.lower()
    try:
        client = get_oauth_client(provider)
        if client is None:
            return _social_redirect("error", provider, f"{provider.title()} OAuth client is unavailable.")

        token = client.authorize_access_token()
        if provider == "google":
            userinfo = token.get("userinfo") or client.get("userinfo").json()
            email = clean_email(userinfo.get("email", ""))
            name = clean_patient_name(userinfo.get("name", "") or userinfo.get("given_name", ""))
            provider_user_id = str(userinfo.get("sub", ""))
        else:
            userinfo = client.get("me?fields=id,name,email").json()
            email = clean_email(userinfo.get("email", ""))
            name = clean_patient_name(userinfo.get("name", ""))
            provider_user_id = str(userinfo.get("id", ""))

        if not provider_user_id:
            return _social_redirect("error", provider, f"{provider.title()} did not return a valid user id.")
        if not email or not validate_email(email):
            return _social_redirect("error", provider, f"{provider.title()} login requires a valid email address.")

        patient = _upsert_social_patient(provider, provider_user_id, name, email)
        session["patient_email"] = patient["email"]
        session["patient_name"] = patient.get("name", "")
        return _social_redirect("success", provider, f"Signed in with {provider.title()} successfully.")
    except Exception as exc:
        logger.error("%s OAuth failed: %s", provider.title(), exc, exc_info=True)
        return _social_redirect("error", provider, f"{provider.title()} login failed. Please try again.")
