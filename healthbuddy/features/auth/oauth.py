"""OAuth helpers for Google and Facebook login."""

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

    facebook_app_id = os.environ.get("FACEBOOK_APP_ID")
    facebook_app_secret = os.environ.get("FACEBOOK_APP_SECRET")
    if facebook_app_id and facebook_app_secret:
        oauth.register(
            name="facebook",
            client_id=facebook_app_id,
            client_secret=facebook_app_secret,
            api_base_url="https://graph.facebook.com/",
            access_token_url="https://graph.facebook.com/oauth/access_token",
            authorize_url="https://www.facebook.com/dialog/oauth",
            client_kwargs={"scope": "email public_profile"},
        )

    return oauth


def get_oauth_client(provider: str):
    """Return a configured OAuth client for the provider, if available."""
    provider = provider.lower()
    oauth = _oauth_registry()
    return getattr(oauth, provider, None)
