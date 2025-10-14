"""Help/docs search API."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import (
    get_enabled_features_for_user,
)


@frappe.whitelist()
def search_help(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search help documentation and user manual."""
    features = get_enabled_features_for_user()
    if not features.get("help_search"):
        frappe.throw(_("Help search feature is disabled"), frappe.PermissionError)

    if not query or not query.strip():
        frappe.throw(_("Search query is required"))

    query = query.strip().lower()
    limit = min(int(limit or 10), 50)

    results = []

    # Search in Help Articles (if exists in workspace)
    if frappe.db.exists("DocType", "Help Article"):
        articles = frappe.get_all(
            "Help Article",
            filters=[
                ["title", "like", f"%{query}%"],
            ],
            or_filters=[
                ["content", "like", f"%{query}%"],
            ],
            fields=["name", "title", "category"],
            limit=limit,
        )

        for article in articles:
            results.append({
                "type": "help_article",
                "title": article.title,
                "route": f"/app/help-article/{article.name}",
                "icon": "octicon octicon-book",
                "description": f"Category: {article.category or 'General'}",
            })

    # Add external Frappe docs links based on query
    doc_suggestions = _get_frappe_doc_suggestions(query)
    results.extend(doc_suggestions)

    return results[:limit]


def _get_frappe_doc_suggestions(query: str) -> list[dict[str, Any]]:
    """Get relevant Frappe documentation links based on query."""
    suggestions = []
    
    # Common topics mapping
    topic_map = {
        "doctype": {
            "title": "Creating DocTypes",
            "url": "https://frappeframework.com/docs/v15/user/en/basics/doctypes",
        },
        "api": {
            "title": "API Documentation",
            "url": "https://frappeframework.com/docs/v15/user/en/api",
        },
        "workflow": {
            "title": "Workflow Guide",
            "url": "https://frappeframework.com/docs/v15/user/en/desk/workflows",
        },
        "permission": {
            "title": "Permission System",
            "url": "https://frappeframework.com/docs/v15/user/en/desk/users-and-permissions",
        },
        "report": {
            "title": "Creating Reports",
            "url": "https://frappeframework.com/docs/v15/user/en/desk/reports",
        },
    }

    for keyword, doc_info in topic_map.items():
        if keyword in query:
            suggestions.append({
                "type": "external_doc",
                "title": doc_info["title"],
                "route": doc_info["url"],
                "icon": "octicon octicon-link-external",
                "description": "Frappe Framework Documentation",
                "external": True,
            })

    return suggestions
