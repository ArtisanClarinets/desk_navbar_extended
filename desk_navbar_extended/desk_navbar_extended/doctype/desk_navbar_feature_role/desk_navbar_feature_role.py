from __future__ import annotations

import frappe
from frappe.model.document import Document


class DeskNavbarFeatureRole(Document):
    """Role override for Desk Navbar Extended features."""

    def validate(self) -> None:
        if not self.role:
            frappe.throw("Role is required for feature overrides.")
