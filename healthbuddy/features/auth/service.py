"""Authentication and MongoDB access helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import os
import re
import ssl
from urllib.parse import quote_plus, unquote_plus, urlsplit, urlunsplit

import certifi
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)
EMAIL_RE = re.compile(r"^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$", re.I)
_mongo_client = None
_mongo_error = None


def normalize_mongodb_uri(mongo_uri: str) -> str:
    """Clean and normalize MongoDB URIs copied from .env files or Atlas."""
    mongo_uri = str(mongo_uri or "").strip()
    if mongo_uri.startswith("MONGODB_URI="):
        mongo_uri = mongo_uri.split("=", 1)[1].strip()

    if (mongo_uri.startswith('"') and mongo_uri.endswith('"')) or (mongo_uri.startswith("'") and mongo_uri.endswith("'")):
        mongo_uri = mongo_uri[1:-1].strip()

    if not mongo_uri:
        return mongo_uri

    if not (mongo_uri.startswith("mongodb://") or mongo_uri.startswith("mongodb+srv://")):
        raise ValueError(
            "Invalid MONGODB_URI. In Render, paste only the MongoDB connection string itself, starting with "
            "'mongodb://' or 'mongodb+srv://'. Do not paste 'MONGODB_URI=' or surrounding quotes."
        )

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
    return urlunsplit((parts.scheme, f"{encoded_userinfo}@{hostinfo}", parts.path, parts.query, parts.fragment))


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

        # Build a TLS context that forces TLS 1.2+ and uses the certifi CA bundle.
        # This avoids the TLSV1_ALERT_INTERNAL_ERROR that occurs when the OS CA
        # store is missing or the TLS negotiation falls back to an unsupported version.
        tls_ctx = ssl.create_default_context(cafile=certifi.where())
        tls_ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        tls_ctx.check_hostname = True
        tls_ctx.verify_mode = ssl.CERT_REQUIRED

        client_options = {
            "serverSelectionTimeoutMS": 10000,   # extended for Render cold-start
            "connectTimeoutMS": 20000,
            "socketTimeoutMS": 20000,
            "tls": True,
            "tlsCAFile": certifi.where(),        # explicit CA bundle
            "retryWrites": True,
            "retryReads": True,
            "maxPoolSize": 5,                    # safe for Atlas free-tier (100 conn limit)
            "appname": os.environ.get("MONGODB_APP_NAME", "healthbuddy"),
        }
        _mongo_client = MongoClient(mongo_uri, **client_options)
        _mongo_client.admin.command("ping")
        db_name = os.environ.get("MONGODB_DB", "healthbuddy")
        collection = _mongo_client[db_name]["patients"]
        collection.create_index("email", unique=True)
        _mongo_error = None
        logger.info("MongoDB connection established successfully.")
        return collection, None
    except ServerSelectionTimeoutError as exc:
        # Timeout usually means Render's IP is not whitelisted in Atlas Network Access.
        logger.error("MongoDB server selection timed out: %s", exc)
        _mongo_error = (
            "Cannot reach MongoDB Atlas. Most likely cause: Render's outbound IP is not "
            "whitelisted in Atlas → Network Access. Add 0.0.0.0/0 (allow all) temporarily "
            "to confirm, then restrict to Render's static IPs. Details: %s" % exc
        )
        return None, _mongo_error
    except (PyMongoError, ValueError) as exc:
        error_str = str(exc)
        if "SSL" in error_str or "TLS" in error_str or "certificate" in error_str.lower():
            msg = (
                "MongoDB TLS/SSL handshake failed. Ensure 'certifi' is installed and up-to-date "
                "(pip install --upgrade certifi), the Atlas URI uses 'mongodb+srv://', and the "
                "Render runtime has ca-certificates installed. Details: %s" % exc
            )
        else:
            msg = (
                "MongoDB connection failed. Verify the Atlas URI, allow Render/hosting traffic "
                "in Atlas Network Access, and ensure TLS certificates are available in the "
                "runtime. Details: %s" % exc
            )
        logger.error(msg, exc_info=True)
        _mongo_error = msg
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
    }


def patient_response(patient: dict) -> dict:
    return {"name": patient.get("name", ""), "email": patient.get("email", "")}


def now_utc():
    return datetime.now(timezone.utc)
