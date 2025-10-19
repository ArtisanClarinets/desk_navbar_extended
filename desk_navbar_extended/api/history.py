"""Grouped recent activity API."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import frappe
from frappe import _
from frappe.utils import get_datetime

from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import (
    get_enabled_features_for_user,
)


@frappe.whitelist()
def get_recent_activity(limit: int = 20) -> dict[str, Any]:
    """Get recent activity grouped by app/doctype."""
    features = get_enabled_features_for_user()
    if not features.get("grouped_history"):
        frappe.throw(_("Grouped history feature is disabled"), frappe.PermissionError)

    limit = min(int(limit or 20), 100)

    # Get recently accessed documents
    recent_docs = frappe.get_all(
        "Activity Log",
        filters={
            "user": frappe.session.user,
            "status": "Success",
            "operation": ["in", ["read", "save"]],
        },
        fields=["reference_doctype", "reference_name", "creation"],
        order_by="creation desc",
        limit=limit * 2,  # Get more to filter and group
    )

    # Group by doctype
    grouped = defaultdict(list)
    seen = set()

    for doc in recent_docs:
        if not doc.reference_doctype or not doc.reference_name:
            continue

        # Skip duplicates
        key = f"{doc.reference_doctype}::{doc.reference_name}"
        if key in seen:
            continue
        seen.add(key)

        # Check if user still has access
        if not frappe.has_permission(doc.reference_doctype, "read"):
            continue

        try:
            # Get doc title
            meta = frappe.get_meta(doc.reference_doctype)
            title_field = meta.get_title_field()

            if title_field:
                title = frappe.db.get_value(
                    doc.reference_doctype,
                    doc.reference_name,
                    title_field,
                )
            else:
                title = doc.reference_name

            grouped[doc.reference_doctype].append(
                {
                    "doctype": doc.reference_doctype,
                    "name": doc.reference_name,
                    "title": title or doc.reference_name,
                    "modified": str(doc.creation),
                    "route": f"/app/{frappe.scrub(doc.reference_doctype)}/{doc.reference_name}",
                }
            )
        except Exception:  # noqa: BLE001
            continue

    # Build grouped response
    groups = []
    for doctype, items in sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True):
        # Limit items per group
        group_items = items[:5]

        meta = frappe.get_meta(doctype)
        groups.append(
            {
                "doctype": doctype,
                "label": _(doctype),
                "icon": meta.icon or "octicon octicon-file",
                "count": len(items),
                "items": group_items,
            }
        )

    # Also get flat list
    all_items = []
    for group in groups:
        all_items.extend(group["items"])

    return {
        "groups": groups[:10],  # Limit to 10 groups
        "items": all_items[:limit],  # Flat list limited
    }
