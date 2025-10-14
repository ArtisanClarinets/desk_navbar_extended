"""Server logic for Desk Navbar Saved Search."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_fullname


class DeskNavbarSavedSearch(Document):
    """Desk Navbar Saved Search DocType."""

    def before_insert(self):
        """Set owner fullname before insert."""
        self.owner_fullname = get_fullname(frappe.session.user)

    def validate(self):
        """Validate saved search."""
        if self.is_global and not frappe.has_permission(
            self.doctype, "write", user=frappe.session.user
        ):
            if "System Manager" not in frappe.get_roles(frappe.session.user):
                frappe.throw(
                    _("Only System Manager can create global saved searches"),
                    frappe.PermissionError,
                )

        # Validate filters_json if present
        if self.filters_json:
            try:
                import json

                json.loads(self.filters_json)
            except Exception as exc:  # noqa: BLE001
                frappe.throw(_("Invalid JSON in filters: {0}").format(str(exc)))

    def on_update(self):
        """Update owner fullname on update."""
        if not self.owner_fullname:
            self.db_set("owner_fullname", get_fullname(self.owner))
