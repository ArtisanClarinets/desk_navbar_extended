"""Quick create options API."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import (
    get_enabled_features_for_user,
    get_settings_doc,
)


@frappe.whitelist()
def get_quick_create_options() -> list[dict[str, Any]]:
    """Get quick create options based on user permissions."""
    features = get_enabled_features_for_user()
    if not features.get("quick_create"):
        frappe.throw(_("Quick create feature is disabled"), frappe.PermissionError)

    settings = get_settings_doc()

    # Check if custom doctypes are configured
    configured_doctypes = []
    if settings.quick_create_doctypes:
        configured_doctypes = [
            dt.strip() for dt in settings.quick_create_doctypes.split(",") if dt.strip()
        ]

    if configured_doctypes:
        # Use configured list
        doctypes = configured_doctypes
    else:
        # Auto-detect common doctypes the user can create
        common_doctypes = [
            "Note",
            "ToDo",
            "Event",
            "Task",
            "Contact",
            "Lead",
            "Customer",
            "Supplier",
            "Item",
            "Sales Order",
            "Purchase Order",
            "Sales Invoice",
            "Purchase Invoice",
            "Payment Entry",
            "Journal Entry",
            "Stock Entry",
            "Delivery Note",
            "Purchase Receipt",
        ]
        doctypes = common_doctypes

    # Filter by permission
    options = []
    for doctype in doctypes:
        if frappe.db.exists("DocType", doctype) and frappe.has_permission(doctype, "create"):
            meta = frappe.get_meta(doctype)
            options.append(
                {
                    "doctype": doctype,
                    "label": _(doctype),
                    "icon": meta.icon or "octicon octicon-file",
                    "route": f"/app/{frappe.scrub(doctype)}/new",
                }
            )

    return options
