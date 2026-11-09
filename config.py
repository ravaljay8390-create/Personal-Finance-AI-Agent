"""
config.py
----------
Central configuration for the Personal Finance AI Agent.

Loads environment variables (via python-dotenv) and exposes typed
constants used across the application: model name, temperature,
app metadata and validation limits.

API key resolution order:
1. A real OS environment variable (e.g. set by your shell, or by a
   local .env file loaded via python-dotenv below).
2. Streamlit Cloud's secrets manager (st.secrets), read as a fallback.
   Streamlit Cloud secrets are NOT always exposed as plain environment
   variables depending on the platform version, so relying on
   os.getenv() alone can silently fail even when the secret is saved
   correctly in the app's Settings -> Secrets panel.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load variables from a local .env file (ignored by git) into the
# process environment. Safe to call even if .env does not exist.
load_dotenv()


def _get_setting(key: str, default: str = "") -> str:
    """Look up a config value from the OS environment first, then fall
    back to Streamlit's secrets manager (used on Streamlit Cloud)."""
    value = os.getenv(key)
    if value:
        return value

    try:
        import streamlit as st

        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        # streamlit not installed / no secrets.toml / not running under
        # Streamlit at all (e.g. plain pytest) - fall through to default
        pass

    return default


@dataclass(frozen=True)
class Settings:
    """Immutable application settings, resolved once at import time."""

    # --- LLM configuration -------------------------------------------------
    groq_api_key: str = _get_setting("GROQ_API_KEY", "")
    model_name: str = _get_setting("GROQ_MODEL", "llama-3.3-70b-versatile")
    temperature: float = 0.0
    request_timeout: int = 30  # seconds, used to detect LLM timeouts

    # --- App metadata --------------------------------------------------
    app_title: str = "💰 Personal Finance AI Agent"
    app_subtitle: str = "AI-powered financial assistant using LangChain Tool Calling"
    currency_symbol: str = "₹"

    # --- Validation limits (used by finance_tools.py) -------------------
    max_amount: float = 1_000_000_000  # 100 crore ceiling, sanity guard
    max_years: int = 50
    min_years: int = 1
    max_rate_percent: float = 50.0


settings = Settings()


def has_valid_api_key() -> bool:
    """Return True if an Groq API key appears to be configured."""
    key = settings.groq_api_key
    return bool(key) and key.strip() != "" and key.strip().lower() != "your_groq_api_key_here"