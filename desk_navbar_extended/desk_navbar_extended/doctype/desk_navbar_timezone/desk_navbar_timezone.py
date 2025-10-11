from __future__ import annotations

import frappe
import pytz
from frappe.model.document import Document


class DeskNavbarTimezone(Document):
    """Additional timezone configuration row."""

    def validate(self) -> None:
        if self.time_zone:
            try:
                pytz.timezone(self.time_zone)
            except Exception as exc:  # noqa: BLE001
                frappe.throw(f"Invalid time zone: {exc}")
