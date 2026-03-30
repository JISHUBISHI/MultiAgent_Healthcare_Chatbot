"""Frontend and static asset routes."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, Response, current_app, make_response, request, send_from_directory

frontend_bp = Blueprint("frontend", __name__)


def frontend_file_exists(asset_path: str) -> bool:
    """Safely check whether a frontend asset exists inside the project root."""
    base_dir = Path(current_app.config["BASE_DIR"])
    candidate = (base_dir / asset_path).resolve()
    try:
        candidate.relative_to(base_dir)
    except ValueError:
        return False
    return candidate.is_file()


def no_store_file_response(filename: str):
    """Serve a file with no-store headers."""
    base_dir = current_app.config["BASE_DIR"]
    response = make_response(send_from_directory(base_dir, filename))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@frontend_bp.get("/")
def index():
    """Serve the main HTML interface."""
    return no_store_file_response("index.html")


@frontend_bp.get("/favicon.ico")
def favicon():
    """Serve the favicon used by the HTML app."""
    return send_from_directory(current_app.config["BASE_DIR"], "healthbuddy-app.ico")


@frontend_bp.get("/service-worker.js")
def service_worker():
    """Serve the service worker without caching during development."""
    return no_store_file_response("service-worker.js")


@frontend_bp.post("/api/install-desktop")
def install_desktop():
    """Explain that cloud deployments must use a downloadable installer."""
    return (
        {
            "ok": False,
            "error": "Direct install is not supported from the server. Download the HealthBuddy installer and run it locally.",
        },
        400,
    )


@frontend_bp.get("/download/healthbuddy-installer.bat")
def download_installer():
    """Download a Windows batch installer that creates a local shortcut."""
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
    return Response(script, mimetype="text/plain", headers={"Content-Disposition": 'attachment; filename="healthbuddy-installer.bat"'})


@frontend_bp.get("/<path:asset_path>")
def serve_frontend_asset(asset_path: str):
    """Serve frontend assets from the project root and fall back to index.html."""
    base_dir = current_app.config["BASE_DIR"]
    if frontend_file_exists(asset_path):
        return send_from_directory(base_dir, asset_path)
    return send_from_directory(base_dir, "index.html")

