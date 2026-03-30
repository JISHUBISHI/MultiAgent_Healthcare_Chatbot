"""
Flask web app that connects the HealthBuddy HTML frontend to the healthcare backend.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import os
from pathlib import Path
import re
from urllib.parse import quote_plus, unquote_plus, urlsplit, urlunsplit

from flask import Response, Flask, jsonify, make_response, request, send_from_directory, session
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.security import check_password_hash, generate_password_hash

from agents import AgentState, create_workflow
from config import get_api_keys, initialize_clients
from dotenv import load_dotenv

load_dotenv()

# Configure basic logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "healthbuddy-dev-secret-key")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_ENV") == "production"
CORS(app)

_workflow = None
_workflow_error = None
_mongo_client = None
_mongo_error = None
EMAIL_RE = re.compile(r"^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$", re.I)


def normalize_mongodb_uri(mongo_uri: str) -> str:
    """URL-encode MongoDB credentials when users paste raw Atlas URIs."""
    if "://" not in mongo_uri or "@" not in mongo_uri:
        return mongo_uri

    parts = urlsplit(mongo_uri)
    if "@" not in parts.netloc:
        return mongo_uri

    userinfo, hostinfo = parts.netloc.rsplit("@", 1)
    if ":" not in userinfo:
        return mongo_uri

    username, password = userinfo.split(":", 1)
    encoded_userinfo = f"{quote_plus(unquote_plus(username))}:{quote_plus(unquote_plus(password))}"
    return urlunsplit(
        (parts.scheme, f"{encoded_userinfo}@{hostinfo}", parts.path, parts.query, parts.fragment)
    )


def get_patient_collection():
    """Initialize and cache the MongoDB patients collection."""
    global _mongo_client, _mongo_error
    if _mongo_client is not None and _mongo_error is None:
        db_name = os.environ.get("MONGODB_DB", "healthbuddy")
        return _mongo_client[db_name]["patients"], None

    mongo_uri = os.environ.get("MONGODB_URI", "").strip()
    if not mongo_uri:
        _mongo_error = "Missing MONGODB_URI in the environment."
        return None, _mongo_error

    try:
        mongo_uri = normalize_mongodb_uri(mongo_uri)
        _mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        _mongo_client.admin.command("ping")
        db_name = os.environ.get("MONGODB_DB", "healthbuddy")
        collection = _mongo_client[db_name]["patients"]
        collection.create_index("email", unique=True)
        _mongo_error = None
        return collection, None
    except PyMongoError as exc:
        logger.error("MongoDB connection failed: %s", exc, exc_info=True)
        _mongo_error = f"MongoDB connection failed: {exc}"
        return None, _mongo_error


def clean_patient_name(value: str) -> str:
    return " ".join(str(value).strip().split())


def clean_email(value: str) -> str:
    return str(value).strip().lower()


def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.fullmatch(email))


def validate_password(password: str) -> str | None:
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must include at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must include at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must include at least one number."
    return None


def auth_provider_status() -> dict:
    return {
        "google": bool(os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET")),
        "facebook": bool(os.environ.get("FACEBOOK_APP_ID") and os.environ.get("FACEBOOK_APP_SECRET")),
    }


def patient_response(patient: dict) -> dict:
    return {
        "name": patient.get("name", ""),
        "email": patient.get("email", ""),
    }


def get_workflow():
    """Initialize and cache the LangGraph workflow."""
    global _workflow, _workflow_error
    if _workflow is not None or _workflow_error is not None:
        return _workflow, _workflow_error

    groq_api_key, tavily_api_key = get_api_keys()
    if not groq_api_key or not tavily_api_key:
        _workflow_error = "Missing GROQ_API_KEY or TAVILY_API_KEY in the environment."
        return None, _workflow_error

    llm, tavily_client, error = initialize_clients()
    if error:
        _workflow_error = error
        return None, _workflow_error

    _workflow = create_workflow(llm, tavily_client)
    return _workflow, None


def run_health_analysis(user_input: str) -> dict:
    """Run the full healthcare workflow for the provided symptoms."""
    workflow, error = get_workflow()
    if error:
        raise RuntimeError(error)

    initial_state: AgentState = {
        "user_input": user_input,
        "symptom_analysis": "",
        "medication_advice": "",
        "home_remedies": "",
        "diet_lifestyle": "",
        "doctor_recommendations": "",
        "error": "",
    }
    return workflow.invoke(initial_state)


def frontend_file_exists(asset_path: str) -> bool:
    """Safely check whether a frontend asset exists inside the project root."""
    candidate = (BASE_DIR / asset_path).resolve()
    try:
        candidate.relative_to(BASE_DIR)
    except ValueError:
        return False
    return candidate.is_file()


@app.get("/")
def index():
    """Serve the main HTML interface."""
    response = make_response(send_from_directory(BASE_DIR, "index.html"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/favicon.ico")
def favicon():
    """Serve the favicon used by the HTML app."""
    return send_from_directory(BASE_DIR, "healthbuddy-app.ico")


@app.get("/service-worker.js")
def service_worker():
    """Serve the service worker without caching during development."""
    response = make_response(send_from_directory(BASE_DIR, "service-worker.js"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/api/health")
@app.get("/api/health/")
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


@app.get("/api/auth/config")
@app.get("/api/auth/config/")
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


@app.post("/api/auth/register")
@app.post("/api/auth/register/")
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
        "created_at": datetime.now(timezone.utc),
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
    return jsonify(
        {
            "ok": True,
            "message": "Registration successful.",
            "patient": {"name": name, "email": email},
        }
    ), 201


@app.get("/api/auth/login")
@app.get("/api/auth/login/")
@app.post("/api/auth/login")
@app.post("/api/auth/login/")
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

    patients.update_one({"_id": patient["_id"]}, {"$set": {"last_login_at": datetime.now(timezone.utc)}})
    session["patient_email"] = patient["email"]
    session["patient_name"] = patient.get("name", "")
    return jsonify(
        {
            "ok": True,
            "message": "Login successful.",
            "patient": patient_response(patient),
        }
    )


@app.post("/api/auth/logout")
@app.post("/api/auth/logout/")
def logout_patient():
    """Clear the current patient session."""
    session.pop("patient_email", None)
    session.pop("patient_name", None)
    return jsonify({"ok": True, "message": "Logged out successfully."})


@app.post("/api/auth/social/<provider>")
@app.post("/api/auth/social/<provider>/")
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


@app.get("/api/auth/me")
@app.get("/api/auth/me/")
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


@app.post("/api/analyze")
@app.post("/api/analyze/")
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
        logger.error(f"Error during health analysis: {str(exc)}", exc_info=True)
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.errorhandler(404)
def handle_not_found(error):
    """Return JSON for API 404s instead of an HTML error page."""
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": f"API route not found: {request.path}"}), 404
    return error


@app.errorhandler(405)
def handle_method_not_allowed(error):
    """Return JSON for API method errors instead of an HTML error page."""
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": f"Method not allowed for API route: {request.path}"}), 405
    return error


@app.post("/api/install-desktop")
def install_desktop():
    """Explain that cloud deployments must use a downloadable installer."""
    return jsonify(
        {
            "ok": False,
            "error": "Direct install is not supported from the server. Download the HealthBuddy installer and run it locally.",
        }
    ), 400


@app.get("/download/healthbuddy-installer.bat")
def download_installer():
    """Download a Windows batch installer that installs HealthBuddy under the user's C: drive profile."""
    base_url = request.host_url.rstrip("/")
    icon_url = f"{base_url}/healthbuddy-app.ico"
    app_url = f"{base_url}/"
    script = f"""@echo off
setlocal
set "INSTALL_DIR=%LOCALAPPDATA%\\HealthBuddy"
set "ICON_PATH=%INSTALL_DIR%\\healthbuddy-app.ico"
set "LAUNCHER_PATH=%INSTALL_DIR%\\HealthBuddy.cmd"
set "APP_URL={app_url}"
set "ICON_URL={icon_url}"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri '%ICON_URL%' -OutFile '%ICON_PATH%'"

if exist "%ProgramFiles%\\Microsoft\\Edge\\Application\\msedge.exe" (
  > "%LAUNCHER_PATH%" echo @echo off
  >> "%LAUNCHER_PATH%" echo start "" "%ProgramFiles%\\Microsoft\\Edge\\Application\\msedge.exe" --app=%APP_URL%
) else if exist "%ProgramFiles(x86)%\\Microsoft\\Edge\\Application\\msedge.exe" (
  > "%LAUNCHER_PATH%" echo @echo off
  >> "%LAUNCHER_PATH%" echo start "" "%ProgramFiles(x86)%\\Microsoft\\Edge\\Application\\msedge.exe" --app=%APP_URL%
) else (
  > "%LAUNCHER_PATH%" echo @echo off
  >> "%LAUNCHER_PATH%" echo start "" %APP_URL%
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$WshShell = New-Object -ComObject WScript.Shell; " ^
  "$DesktopShortcut = $WshShell.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'),'HealthBuddy.lnk')); " ^
  "$DesktopShortcut.TargetPath = '%LAUNCHER_PATH%'; " ^
  "$DesktopShortcut.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$DesktopShortcut.IconLocation = '%ICON_PATH%'; " ^
  "$DesktopShortcut.Save(); " ^
  "$StartShortcut = $WshShell.CreateShortcut([System.IO.Path]::Combine($env:APPDATA,'Microsoft\\Windows\\Start Menu\\Programs\\HealthBuddy.lnk')); " ^
  "$StartShortcut.TargetPath = '%LAUNCHER_PATH%'; " ^
  "$StartShortcut.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$StartShortcut.IconLocation = '%ICON_PATH%'; " ^
  "$StartShortcut.Save()"

echo.
echo HealthBuddy installed successfully.
echo Installed to: %INSTALL_DIR%
echo Desktop shortcut created.
pause
"""
    return Response(
        script,
        mimetype="text/plain",
        headers={
            "Content-Disposition": 'attachment; filename="healthbuddy-installer.bat"'
        },
    )


@app.get("/<path:asset_path>")
def serve_frontend_asset(asset_path: str):
    """Serve frontend assets from the project root and fall back to index.html."""
    if frontend_file_exists(asset_path):
        return send_from_directory(BASE_DIR, asset_path)
    return send_from_directory(BASE_DIR, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


