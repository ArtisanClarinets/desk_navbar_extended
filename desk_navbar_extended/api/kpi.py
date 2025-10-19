"""KPI widgets API."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.utils import flt

from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import (
    get_enabled_features_for_user,
)


@frappe.whitelist()
def get_kpi_data() -> list[dict[str, Any]]:
    """Get KPI widget data based on user roles and permissions."""
    features = get_enabled_features_for_user()
    if not features.get("kpi_widgets"):
        frappe.throw(_("KPI widgets feature is disabled"), frappe.PermissionError)

    kpis = []

    # Check roles and add relevant KPIs
    user_roles = frappe.get_roles(frappe.session.user)

    # Sales KPIs
    if "Sales User" in user_roles or "Sales Manager" in user_roles:
        if frappe.has_permission("Sales Order", "read"):
            try:
                # Open sales orders
                open_so = frappe.db.count(
                    "Sales Order", {"docstatus": 1, "status": ["!=", "Closed"]}
                )

                # Monthly sales
                from frappe.utils import get_first_day, nowdate

                first_day = get_first_day(nowdate())
                monthly_sales = frappe.db.sql(
                    """
                    SELECT COALESCE(SUM(grand_total), 0)
                    FROM `tabSales Order`
                    WHERE docstatus = 1 AND transaction_date >= %s
                    """,
                    (first_day,),
                )[0][0]

                kpis.append(
                    {
                        "id": "open_sales_orders",
                        "label": _("Open Sales Orders"),
                        "value": open_so,
                        "icon": "octicon octicon-note",
                        "color": "#3b82f6",
                        "route": "/app/sales-order",
                    }
                )

                kpis.append(
                    {
                        "id": "monthly_sales",
                        "label": _("Monthly Sales"),
                        "value": flt(monthly_sales, 2),
                        "format": "currency",
                        "icon": "octicon octicon-graph",
                        "color": "#10b981",
                    }
                )
            except Exception:  # noqa: BLE001
                pass

    # Purchase KPIs
    if "Purchase User" in user_roles or "Purchase Manager" in user_roles:
        if frappe.has_permission("Purchase Order", "read"):
            try:
                open_po = frappe.db.count(
                    "Purchase Order", {"docstatus": 1, "status": ["!=", "Closed"]}
                )
                kpis.append(
                    {
                        "id": "open_purchase_orders",
                        "label": _("Open Purchase Orders"),
                        "value": open_po,
                        "icon": "octicon octicon-package",
                        "color": "#f59e0b",
                        "route": "/app/purchase-order",
                    }
                )
            except Exception:  # noqa: BLE001
                pass

    # Stock KPIs
    if "Stock User" in user_roles or "Stock Manager" in user_roles:
        if frappe.has_permission("Item", "read"):
            try:
                low_stock_items = frappe.db.sql(
                    """
                    SELECT COUNT(DISTINCT item_code)
                    FROM `tabBin`
                    WHERE actual_qty <= reorder_level
                    """,
                )[0][0]

                kpis.append(
                    {
                        "id": "low_stock_items",
                        "label": _("Low Stock Items"),
                        "value": low_stock_items,
                        "icon": "octicon octicon-alert",
                        "color": "#ef4444",
                        "route": "/app/item",
                    }
                )
            except Exception:  # noqa: BLE001
                pass

    # Task/ToDo KPIs (for all users)
    if frappe.has_permission("ToDo", "read"):
        try:
            my_todos = frappe.db.count(
                "ToDo", {"allocated_to": frappe.session.user, "status": "Open"}
            )
            kpis.append(
                {
                    "id": "my_open_todos",
                    "label": _("My Open ToDos"),
                    "value": my_todos,
                    "icon": "octicon octicon-checklist",
                    "color": "#8b5cf6",
                    "route": "/app/todo",
                }
            )
        except Exception:  # noqa: BLE001
            pass

    return kpis
