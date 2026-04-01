"""OAuth helpers for Google login."""

from __future__ import annotations

import os

from flask import current_app


def _oauth_registry():
    """Create and cache the Authlib OAuth registry lazily."""
    oauth = current_app.extensions.get("healthbuddy_oauth")
    if oauth is not None:
        return oauth

    from authlib.integrations.flask_client import OAuth

    oauth = OAuth()
    oauth.init_app(current_app)
    current_app.extensions["healthbuddy_oauth"] = oauth

    google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
    google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    if google_client_id and google_client_secret:
        oauth.register(
            name="google",
            client_id=google_client_id,
            client_secret=google_client_secret,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    return oauth


def get_oauth_client(provider: str):
    """Return a configured OAuth client for the provider, if available."""
    provider = provider.lower()
    oauth = _oauth_registry()
    return getattr(oauth, provider, None)
