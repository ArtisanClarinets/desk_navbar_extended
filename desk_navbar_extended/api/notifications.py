"""Notifications center API."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import (
    get_enabled_features_for_user,
)


@frappe.whitelist()
def get_notifications(limit: int = 20) -> dict[str, Any]:
    """Get notifications for current user."""
    features = get_enabled_features_for_user()
    if not features.get("notifications_center"):
        frappe.throw(_("Notifications center feature is disabled"), frappe.PermissionError)

    limit = min(int(limit or 20), 100)

    # Get user's notifications
    notifications = frappe.get_all(
        "Notification Log",
        filters={"for_user": frappe.session.user},
        fields=["name", "subject", "type", "document_type", "document_name", "read", "creation"],
        order_by="creation desc",
        limit=limit,
    )

    # Count unread
    unread_count = frappe.db.count(
        "Notification Log",
        filters={"for_user": frappe.session.user, "read": 0},
    )

    return {
        "notifications": notifications,
        "unread_count": unread_count,
        "total": len(notifications),
    }


@frappe.whitelist()
def mark_as_read(names: str | list[str]) -> dict[str, str]:
    """Mark notifications as read."""
    features = get_enabled_features_for_user()
    if not features.get("notifications_center"):
        frappe.throw(_("Notifications center feature is disabled"), frappe.PermissionError)

    if isinstance(names, str):
        import json
        names = json.loads(names)

    for name in names:
        doc = frappe.get_doc("Notification Log", name)
        if doc.for_user == frappe.session.user:
            doc.db_set("read", 1, update_modified=False)

    return {"status": "success", "count": len(names)}


@frappe.whitelist()
def mark_all_as_read() -> dict[str, str]:
    """Mark all notifications as read for current user."""
    features = get_enabled_features_for_user()
    if not features.get("notifications_center"):
        frappe.throw(_("Notifications center feature is disabled"), frappe.PermissionError)

    frappe.db.sql(
        """
        UPDATE `tabNotification Log`
        SET `read` = 1
        WHERE `for_user` = %s AND `read` = 0
        """,
        (frappe.session.user,),
    )

    return {"status": "success"}
