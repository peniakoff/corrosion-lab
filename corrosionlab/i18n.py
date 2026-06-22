"""Lightweight internationalization for CorrosionLab."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

Locale = Literal["pl", "en"]
SUPPORTED_LOCALES: tuple[Locale, ...] = ("pl", "en")
DEFAULT_LOCALE: Locale = "pl"

_LOCALES_DIR = Path(__file__).resolve().parent / "locales"
_fallback_locale: Locale = DEFAULT_LOCALE


def _flatten_messages(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(_flatten_messages(value, full_key))
        else:
            flat[full_key] = value
    return flat


@lru_cache(maxsize=len(SUPPORTED_LOCALES))
def _load_catalog(locale: Locale) -> dict[str, Any]:
    path = _LOCALES_DIR / f"{locale}.json"
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return _flatten_messages(data)


def map_browser_locale_tag(tag: str | None) -> Locale:
    """Map a browser locale tag (e.g. en-US) to a supported locale."""
    if not tag:
        return DEFAULT_LOCALE
    normalized = tag.lower().replace("_", "-")
    if normalized.startswith("pl"):
        return "pl"
    if normalized.startswith("en"):
        return "en"
    return "en"


def detect_browser_locale() -> Locale:
    """Detect locale from Streamlit browser context."""
    try:
        import streamlit as st

        tag = getattr(st.context, "locale", None)
        return map_browser_locale_tag(tag)
    except Exception:
        return DEFAULT_LOCALE


def get_locale() -> Locale:
    """Return the active locale from session state or fallback."""
    try:
        import streamlit as st

        locale = st.session_state.get("locale")
        if locale in SUPPORTED_LOCALES:
            return locale
    except Exception:
        pass
    return _fallback_locale


def set_locale(locale: Locale) -> None:
    """Set active locale in session state or module fallback."""
    global _fallback_locale
    if locale not in SUPPORTED_LOCALES:
        raise ValueError(f"Unsupported locale: {locale}")
    try:
        import streamlit as st

        st.session_state.locale = locale
    except Exception:
        _fallback_locale = locale


def t(key: str, locale: Locale | None = None, **kwargs: Any) -> str:
    """Translate a message key with optional interpolation."""
    active = locale or get_locale()
    catalog = _load_catalog(active)
    message = catalog.get(key)
    if message is None:
        fallback = _load_catalog(DEFAULT_LOCALE)
        message = fallback.get(key, key)
    if not isinstance(message, str):
        return key
    if kwargs:
        try:
            return message.format(**kwargs)
        except KeyError:
            return message
    return message


class LocalizedError(ValueError):
    """Exception carrying an i18n message key and format kwargs."""

    def __init__(self, message_key: str, **kwargs: Any):
        self.message_key = message_key
        self.kwargs = kwargs
        super().__init__(message_key)


def format_error(exc: LocalizedError, locale: Locale | None = None) -> str:
    """Format a localized exception message."""
    return t(f"errors.{exc.message_key}", locale=locale, **exc.kwargs)


def get_message(key: str, locale: Locale | None = None) -> Any:
    """Return a catalog entry (string, list, or other)."""
    active = locale or get_locale()
    catalog = _load_catalog(active)
    message = catalog.get(key)
    if message is None:
        fallback = _load_catalog(DEFAULT_LOCALE)
        message = fallback.get(key, key)
    return message
