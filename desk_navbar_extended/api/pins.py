"""Pin management API."""

from __future__ import annotations

import json
from typing import Any

import frappe
from frappe import _

from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import (
    get_enabled_features_for_user,
)


@frappe.whitelist()
def list_pins() -> list[dict[str, Any]]:
    """List pins for current user."""
    features = get_enabled_features_for_user()
    if not features.get("pins"):
        frappe.throw(_("Pins feature is disabled"), frappe.PermissionError)

    pins = frappe.get_all(
        "Desk Navbar Pin",
        filters={"owner": frappe.session.user},
        fields=["name", "label", "route", "icon", "color", "sequence"],
        order_by="sequence asc",
    )

    return pins


@frappe.whitelist()
def create_pin(payload: str | dict[str, Any]) -> dict[str, Any]:
    """Create a new pin."""
    features = get_enabled_features_for_user()
    if not features.get("pins"):
        frappe.throw(_("Pins feature is disabled"), frappe.PermissionError)

    if isinstance(payload, str):
        data = json.loads(payload)
    else:
        data = payload

    if not data.get("label") or not data.get("route"):
        frappe.throw(_("Label and route are required"))

    doc = frappe.get_doc(
        {
            "doctype": "Desk Navbar Pin",
            "label": data.get("label"),
            "route": data.get("route"),
            "icon": data.get("icon"),
            "color": data.get("color"),
            "sequence": data.get("sequence", 0),
        }
    )
    doc.insert()

    return {
        "name": doc.name,
        "label": doc.label,
        "route": doc.route,
        "icon": doc.icon,
        "color": doc.color,
        "sequence": doc.sequence,
    }


@frappe.whitelist()
def delete_pin(name: str) -> dict[str, str]:
    """Delete a pin."""
    features = get_enabled_features_for_user()
    if not features.get("pins"):
        frappe.throw(_("Pins feature is disabled"), frappe.PermissionError)

    doc = frappe.get_doc("Desk Navbar Pin", name)

    # Check ownership
    if doc.owner != frappe.session.user:
        frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

    frappe.delete_doc("Desk Navbar Pin", name)

    return {"status": "deleted", "name": name}


@frappe.whitelist()
def reorder_pins(payload: str | dict[str, Any]) -> dict[str, str]:
    """Reorder pins by updating sequence."""
    features = get_enabled_features_for_user()
    if not features.get("pins"):
        frappe.throw(_("Pins feature is disabled"), frappe.PermissionError)

    if isinstance(payload, str):
        data = json.loads(payload)
    else:
        data = payload

    # Expect format: {"pins": [{"name": "DNP-0001", "sequence": 1}, ...]}
    pins_data = data.get("pins", [])
    if not pins_data:
        frappe.throw(_("Pins data is required"))

    for pin_data in pins_data:
        name = pin_data.get("name")
        sequence = pin_data.get("sequence")

        if not name or sequence is None:
            continue

        doc = frappe.get_doc("Desk Navbar Pin", name)

        # Check ownership
        if doc.owner != frappe.session.user:
            continue

        doc.db_set("sequence", sequence, update_modified=False)

    return {"status": "reordered", "count": len(pins_data)}
