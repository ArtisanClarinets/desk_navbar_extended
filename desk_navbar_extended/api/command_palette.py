"""Command palette sources API."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import (
    get_enabled_features_for_user,
)


@frappe.whitelist()
def get_command_palette_sources() -> dict[str, Any]:
    """Get all command palette sources."""
    features = get_enabled_features_for_user()
    if not features.get("command_palette"):
        frappe.throw(_("Command palette feature is disabled"), frappe.PermissionError)

    sources = {
        "doctypes": [],
        "saved_searches": [],
        "pins": [],
        "recent": [],
        "quick_create": [],
        "help": [],
    }

    # Get doctypes user can access
    all_doctypes = frappe.get_all(
        "DocType",
        filters={"istable": 0, "issingle": 0},
        fields=["name", "icon"],
        limit=100,
    )

    for dt in all_doctypes:
        if frappe.has_permission(dt.name, "read"):
            meta = frappe.get_meta(dt.name)
            sources["doctypes"].append(
                {
                    "type": "doctype",
                    "label": _(dt.name),
                    "value": dt.name,
                    "icon": dt.icon or meta.icon or "octicon octicon-file",
                    "route": f"/app/{frappe.scrub(dt.name)}",
                    "description": f"Open {_(dt.name)} list",
                }
            )

    # Get saved searches if enabled
    if features.get("saved_searches"):
        from desk_navbar_extended.api import saved_searches as ss_api

        try:
            saved = ss_api.list_saved_searches()
            for search in saved:
                sources["saved_searches"].append(
                    {
                        "type": "saved_search",
                        "label": search["title"],
                        "value": search["name"],
                        "icon": "octicon octicon-search",
                        "description": search["query"],
                        "data": search,
                    }
                )
        except Exception:  # noqa: BLE001
            pass

    # Get pins if enabled
    if features.get("pins"):
        from desk_navbar_extended.api import pins as pins_api

        try:
            pins = pins_api.list_pins()
            for pin in pins:
                sources["pins"].append(
                    {
                        "type": "pin",
                        "label": pin["label"],
                        "value": pin["name"],
                        "icon": pin.get("icon") or "octicon octicon-star",
                        "route": pin["route"],
                        "color": pin.get("color"),
                    }
                )
        except Exception:  # noqa: BLE001
            pass

    # Get quick create if enabled
    if features.get("quick_create"):
        from desk_navbar_extended.api import quick_create as qc_api

        try:
            options = qc_api.get_quick_create_options()
            for opt in options:
                sources["quick_create"].append(
                    {
                        "type": "quick_create",
                        "label": f"New {opt['label']}",
                        "value": opt["doctype"],
                        "icon": opt.get("icon") or "octicon octicon-plus",
                        "route": opt["route"],
                        "description": f"Create new {opt['label']}",
                    }
                )
        except Exception:  # noqa: BLE001
            pass

    # Get recent activity if enabled
    if features.get("grouped_history"):
        from desk_navbar_extended.api import history as hist_api

        try:
            recent = hist_api.get_recent_activity(limit=10)
            for item in recent.get("items", []):
                sources["recent"].append(
                    {
                        "type": "recent",
                        "label": item.get("title") or item.get("name"),
                        "value": item.get("name"),
                        "icon": "octicon octicon-history",
                        "route": item.get("route"),
                        "description": f"{item.get('doctype')} · {item.get('modified')}",
                    }
                )
        except Exception:  # noqa: BLE001
            pass

    return sources
