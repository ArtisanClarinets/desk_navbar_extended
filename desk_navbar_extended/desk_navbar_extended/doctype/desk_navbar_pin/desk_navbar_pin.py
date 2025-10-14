"""Server logic for Desk Navbar Pin."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class DeskNavbarPin(Document):
    """Desk Navbar Pin DocType."""

    def validate(self):
        """Validate pin."""
        if not self.route:
            frappe.throw(_("Route is required"))

        # Ensure route starts with /
        if not self.route.startswith("/"):
            self.route = f"/{self.route}"

        # Set default sequence if not provided
        if self.sequence is None:
            max_seq = frappe.db.get_value(
                "Desk Navbar Pin",
                {"owner": frappe.session.user},
                "MAX(sequence)",
            ) or 0
            self.sequence = max_seq + 1
