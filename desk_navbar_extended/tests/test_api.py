from __future__ import annotations

import base64
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestDeskNavbarExtendedAPI(FrappeTestCase):
    def test_get_settings_includes_feature_flags(self):
        settings = frappe.call("desk_navbar_extended.api.get_settings")
        self.assertIn("features", settings)
        self.assertIn("clock", settings)
        self.assertIn("awesomebar", settings)

    def test_log_search_metrics_persists_document(self):
        before = frappe.db.count("Desk Navbar Search Metric")
        frappe.call(
            "desk_navbar_extended.api.log_search_metrics",
            payload={
                "status": "success",
                "search_length": 5,
                "execution_ms": 42,
            }
        )
        after = frappe.db.count("Desk Navbar Search Metric")
        self.assertEqual(after, before + 1)

    def test_transcribe_audio_enqueues_background_job(self):
        payload = base64.b64encode(b"demo").decode()
        with patch("frappe.enqueue") as enqueue_mock:
            enqueue_mock.return_value = type("Job", (), {"id": "JOB-ID"})()
            response = frappe.call(
                "desk_navbar_extended.api.transcribe_audio",
                audio=payload,
                filename="sample.webm"
            )
        self.assertEqual(response["job_id"], "JOB-ID")

    def test_transcribe_audio_rejects_invalid_payload(self):
        with self.assertRaises(Exception):
            frappe.call(
                "desk_navbar_extended.api.transcribe_audio",
                audio="not-base64=="
            )
