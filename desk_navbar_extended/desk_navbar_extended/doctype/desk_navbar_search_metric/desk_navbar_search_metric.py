"""DocType utilities for Desk Navbar Search Metric."""

from __future__ import annotations

from hashlib import sha256

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class DeskNavbarSearchMetric(Document):
    """Persist anonymized search telemetry for administrators."""

    def before_insert(self) -> None:
        self.event_ts = self.event_ts or now_datetime()
        if self.error_message:
            self.error_message = self.error_message[:140]
        actor = frappe.session.user or "Guest"
        self.actor_hash = sha256(actor.encode()).hexdigest()

