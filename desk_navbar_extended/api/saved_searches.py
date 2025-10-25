"""Saved searches CRUD API."""

from __future__ import annotations

import json
from typing import Any

import frappe
from frappe import _

from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import (
    get_enabled_features_for_user,
)


@frappe.whitelist()
def list_saved_searches() -> list[dict[str, Any]]:
    """List saved searches for current user + global searches."""
    features = get_enabled_features_for_user()
    if not features.get("saved_searches"):
        frappe.throw(_("Saved searches feature is disabled"), frappe.PermissionError)

    # Get user's own searches
    user_searches = frappe.get_all(
        "Desk Navbar Saved Search",
        filters={"owner": frappe.session.user, "is_global": 0},
        fields=["name", "title", "query", "doctype_filter", "filters_json", "modified"],
        order_by="title asc",
    )

    # Get global searches
    global_searches = frappe.get_all(
        "Desk Navbar Saved Search",
        filters={"is_global": 1},
        fields=["name", "title", "query", "doctype_filter", "filters_json", "modified"],
        order_by="title asc",
    )

    # Combine and sanitize
    all_searches = []
    for search in user_searches + global_searches:
        sanitized = {
            "name": search.name,
            "title": search.title,
            "query": search.query,
            "doctype_filter": search.doctype_filter,
            "is_global": search in global_searches,
            "modified": str(search.modified),
        }
        if search.filters_json:
            try:
                sanitized["filters"] = json.loads(search.filters_json)
            except Exception:  # noqa: BLE001
                sanitized["filters"] = {}
        else:
            sanitized["filters"] = {}

        all_searches.append(sanitized)

    return all_searches


@frappe.whitelist()
def create_saved_search(payload: str | dict[str, Any]) -> dict[str, Any]:
    """Create a new saved search."""
    features = get_enabled_features_for_user()
    if not features.get("saved_searches"):
        frappe.throw(_("Saved searches feature is disabled"), frappe.PermissionError)

    if isinstance(payload, str):
        data = json.loads(payload)
    else:
        data = payload

    if not data.get("title") or not data.get("query"):
        frappe.throw(_("Title and query are required"))

    # Check permissions for global searches
    if data.get("is_global") and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Only System Managers can create global searches"), frappe.PermissionError)

    doc = frappe.get_doc(
        {
            "doctype": "Desk Navbar Saved Search",
            "title": data.get("title"),
            "query": data.get("query"),
            "doctype_filter": data.get("doctype_filter"),
            "is_global": bool(data.get("is_global")),
            "filters_json": json.dumps(data.get("filters", {})) if data.get("filters") else None,
        }
    )
    doc.insert()

    return {
        "name": doc.name,
        "title": doc.title,
        "query": doc.query,
        "doctype_filter": doc.doctype_filter,
        "is_global": doc.is_global,
    }


@frappe.whitelist()
def update_saved_search(name: str, payload: str | dict[str, Any]) -> dict[str, Any]:
    """Update an existing saved search."""
    features = get_enabled_features_for_user()
    if not features.get("saved_searches"):
        frappe.throw(_("Saved searches feature is disabled"), frappe.PermissionError)

    if isinstance(payload, str):
        data = json.loads(payload)
    else:
        data = payload

    doc = frappe.get_doc("Desk Navbar Saved Search", name)

    # Check permissions
    if doc.owner != frappe.session.user and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

    # Check permissions for setting is_global flag
    if (
        "is_global" in data
        and data.get("is_global")
        and "System Manager" not in frappe.get_roles()
    ):
        frappe.throw(_("Only System Managers can create global searches"), frappe.PermissionError)

    # Update fields
    if "title" in data:
        doc.title = data["title"]
    if "query" in data:
        doc.query = data["query"]
    if "doctype_filter" in data:
        doc.doctype_filter = data["doctype_filter"]
    if "is_global" in data:
        doc.is_global = bool(data["is_global"])
    if "filters" in data:
        doc.filters_json = json.dumps(data["filters"])

    doc.save()

    return {
        "name": doc.name,
        "title": doc.title,
        "query": doc.query,
        "doctype_filter": doc.doctype_filter,
        "is_global": doc.is_global,
    }


@frappe.whitelist()
def delete_saved_search(name: str) -> dict[str, str]:
    """Delete a saved search."""
    features = get_enabled_features_for_user()
    if not features.get("saved_searches"):
        frappe.throw(_("Saved searches feature is disabled"), frappe.PermissionError)

    doc = frappe.get_doc("Desk Navbar Saved Search", name)

    # Check permissions
    if doc.owner != frappe.session.user and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

    frappe.delete_doc("Desk Navbar Saved Search", name)

    return {"status": "deleted", "name": name}
