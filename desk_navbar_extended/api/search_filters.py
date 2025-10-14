"""Smart search with filters API."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

import frappe
from frappe import _
from frappe.desk.search import search_link
from frappe.utils import cint, get_datetime, now_datetime

from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import (
    get_enabled_features_for_user,
)


@frappe.whitelist()
def search_with_filters(
    query: str,
    doctype: str | None = None,
    owner: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Search with advanced filters.
    
    Args:
        query: Search query string
        doctype: Optional DocType filter
        owner: Optional owner filter (email)
        date_from: Optional start date (ISO format)
        date_to: Optional end date (ISO format)
        limit: Maximum results (default 20, max 100)
    
    Returns:
        dict with results and metadata
    """
    features = get_enabled_features_for_user()
    if not features.get("smart_filters"):
        frappe.throw(_("Smart filters feature is disabled"), frappe.PermissionError)

    if not query or not query.strip():
        frappe.throw(_("Search query is required"))

    # Sanitize and validate inputs
    query = query.strip()
    limit = min(cint(limit) or 20, 100)

    # Build filters
    filters = {}
    start_time = now_datetime()

    def normalize_results(raw_results: list[dict[str, Any]], result_doctype: str | None) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for item in raw_results:
            docname = item.get("name") or item.get("value")
            normalized.append(
                {
                    **item,
                    "name": docname,
                    "value": docname,
                    "doctype": result_doctype or item.get("doctype"),
                }
            )
        return normalized

    try:
        if doctype:
            # Validate doctype exists and user has permission
            if not frappe.db.exists("DocType", doctype):
                frappe.throw(_("DocType {0} does not exist").format(doctype))
            
            if not frappe.has_permission(doctype, "read"):
                frappe.throw(
                    _("Insufficient permissions for DocType {0}").format(doctype),
                    frappe.PermissionError,
                )

            # Use search_link for specific doctype
            results = normalize_results(
                search_link(
                    doctype=doctype,
                    txt=query,
                    page_length=limit,
                ),
                doctype,
            )
            
            # Apply additional filters if provided
            if owner or date_from or date_to:
                filtered_results = []
                for result in results:
                    doc_name = result.get("name") or result.get("value")
                    if not doc_name:
                        continue
                    
                    try:
                        doc = frappe.get_doc(doctype, doc_name)
                        
                        # Owner filter
                        if owner and doc.owner != owner:
                            continue
                        
                        # Date filters
                        if date_from or date_to:
                            doc_date = get_datetime(doc.creation)
                            if date_from:
                                date_from_dt = get_datetime(date_from)
                                if doc_date < date_from_dt:
                                    continue
                            if date_to:
                                date_to_dt = get_datetime(date_to)
                                if doc_date > date_to_dt:
                                    continue
                        
                        filtered_results.append(result)
                    except Exception:  # noqa: BLE001
                        continue
                
                results = filtered_results[:limit]
        else:
            # Global search - search across common doctypes
            results = []
            common_doctypes = ["User", "Note", "ToDo", "Event", "Task"]

            for dt in common_doctypes:
                if frappe.has_permission(dt, "read"):
                    try:
                        dt_results = normalize_results(
                            search_link(
                                doctype=dt,
                                txt=query,
                                page_length=5,  # Limit per doctype
                            ),
                            dt,
                        )
                        results.extend(dt_results)
                        if len(results) >= limit:
                            break
                    except Exception:  # noqa: BLE001
                        continue
            
            results = results[:limit]
            
            # Apply owner/date filters if specified
            if owner or date_from or date_to:
                filtered_results = []
                for result in results:
                    try:
                        dt = result.get("doctype")
                        dn = result.get("name") or result.get("value")
                        if not dt or not dn:
                            continue
                        
                        doc = frappe.get_doc(dt, dn)
                        
                        if owner and doc.owner != owner:
                            continue
                        
                        if date_from or date_to:
                            doc_date = get_datetime(doc.creation)
                            if date_from:
                                date_from_dt = get_datetime(date_from)
                                if doc_date < date_from_dt:
                                    continue
                            if date_to:
                                date_to_dt = get_datetime(date_to)
                                if doc_date > date_to_dt:
                                    continue
                        
                        filtered_results.append(result)
                    except Exception:  # noqa: BLE001
                        continue
                
                results = filtered_results[:limit]

        execution_ms = (now_datetime() - start_time).total_seconds() * 1000

        # Log metrics if analytics enabled
        from desk_navbar_extended import api as main_api

        if features.get("usage_analytics"):
            main_api.log_search_metrics(
                {
                    "search_length": len(query),
                    "execution_ms": execution_ms,
                    "status": "success",
                }
            )

        return {
            "results": results,
            "query": query,
            "filters": {
                "doctype": doctype,
                "owner": owner,
                "date_from": date_from,
                "date_to": date_to,
            },
            "count": len(results),
            "execution_ms": execution_ms,
        }

    except frappe.PermissionError:
        raise
    except Exception as exc:  # noqa: BLE001
        frappe.logger("desk_navbar_extended").error(
            f"Search error: {str(exc)}", exc_info=True
        )
        
        if features.get("usage_analytics"):
            from desk_navbar_extended import api as main_api

            main_api.log_search_metrics(
                {
                    "search_length": len(query),
                    "execution_ms": (now_datetime() - start_time).total_seconds() * 1000,
                    "status": "error",
                    "error_message": str(exc)[:140],
                }
            )
        
        frappe.throw(_("Search failed: {0}").format(str(exc)))
