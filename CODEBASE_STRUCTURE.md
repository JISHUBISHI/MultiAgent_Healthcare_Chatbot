# Codebase Structure

The project now has a feature-oriented package under `healthbuddy/`.

## Main areas

- `healthbuddy/app.py`
  - Flask application factory and blueprint registration
- `healthbuddy/core/`
  - shared client and environment setup
- `healthbuddy/features/auth/`
  - MongoDB patient auth helpers and auth routes
- `healthbuddy/features/analysis/`
  - LangGraph workflow, analysis service, and analysis routes
- `healthbuddy/features/frontend/`
  - HTML entry route, static assets, and installer download route
- `healthbuddy/features/system/`
  - health endpoint and API error helpers

## Runtime entrypoints

- `wsgi.py`
  - production entrypoint for Gunicorn
- `web_app.py`
  - legacy Flask entrypoint
- `app.py`
  - Streamlit app entrypoint

## Compatibility files

The original top-level modules are kept so existing imports still work while the app moves toward the feature package layout.
