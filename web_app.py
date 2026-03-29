"""
Flask web app that connects the HealthBuddy HTML frontend to the healthcare backend.
"""

from __future__ import annotations

import os
import logging
from pathlib import Path

from flask import Response, Flask, jsonify, request, send_from_directory
from flask_cors import CORS

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
app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")
CORS(app)

_workflow = None
_workflow_error = None


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


@app.get("/")
def index():
    """Serve the main HTML interface."""
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/api/health")
def health():
    """Simple readiness endpoint."""
    _, error = get_workflow()
    if error:
        return jsonify({"ok": False, "error": error}), 500
    return jsonify({"ok": True, "name": "HealthBuddy"})


@app.post("/api/analyze")
def analyze():
    """Run symptom analysis and return structured section outputs."""
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


