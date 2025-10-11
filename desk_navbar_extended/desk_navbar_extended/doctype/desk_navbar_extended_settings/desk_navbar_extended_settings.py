"""Server logic for Desk Navbar Extended Settings."""

from __future__ import annotations

import frappe


def get_settings_doc() -> frappe.model.document.Document:
    """Return the singleton settings document, creating it if missing."""

    try:
        return frappe.get_single("Desk Navbar Extended Settings")
    except frappe.DoesNotExistError:
        doc = frappe.new_doc("Desk Navbar Extended Settings")
        doc.insert(ignore_permissions=True)
        return doc


def get_enabled_features_for_user(user: str | None = None) -> dict[str, bool]:
    """Return a map of enabled features for the given user respecting role overrides."""

    user = user or frappe.session.user
    settings = get_settings_doc()
    role_overrides = {}
    for row in settings.feature_roles:
        feature_key = (row.feature or "").strip().lower().replace(" ", "_")
        if not feature_key:
            continue
        role_overrides.setdefault(feature_key, set()).add(row.role)

    def is_enabled(fieldname: str) -> bool:
        enabled = bool(settings.get(fieldname))
        overrides = role_overrides.get(fieldname.replace("enable_", ""), set())
        if not overrides:
            return enabled
        user_roles = set(frappe.get_roles(user))
        return bool(user_roles.intersection(overrides)) and enabled

    return {
        "clock": is_enabled("enable_clock"),
        "voice_search": is_enabled("enable_voice_search"),
        "wide_awesomebar": is_enabled("enable_wide_awesomebar"),
        "usage_analytics": bool(settings.enable_usage_analytics),
    }

