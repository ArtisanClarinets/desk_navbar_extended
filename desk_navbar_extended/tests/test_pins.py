"""Tests for pins API."""

from __future__ import annotations

import frappe
from frappe.tests.utils import FrappeTestCase

from desk_navbar_extended.api import pins


class TestPins(FrappeTestCase):
    def setUp(self):
        # Enable pins feature
        settings = frappe.get_single("Desk Navbar Extended Settings")
        settings.enable_pins = 1
        settings.flags.ignore_permissions = True
        settings.save()

        # Clean up test data
        frappe.db.delete("Desk Navbar Pin", {"label": ["like", "Test%"]})

    def test_create_pin(self):
        """Test creating a pin."""
        result = pins.create_pin(
            {
                "label": "Test Pin",
                "route": "/app/user",
                "icon": "octicon octicon-star",
                "color": "#ff0000",
            }
        )

        self.assertEqual(result["label"], "Test Pin")
        self.assertEqual(result["route"], "/app/user")
        self.assertEqual(result["icon"], "octicon octicon-star")

    def test_list_pins(self):
        """Test listing pins."""
        # Create test pins
        pins.create_pin({"label": "Test List 1", "route": "/app/user"})
        pins.create_pin({"label": "Test List 2", "route": "/app/todo"})

        results = pins.list_pins()

        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 2)

    def test_delete_pin(self):
        """Test deleting a pin."""
        created = pins.create_pin(
            {
                "label": "Test Delete",
                "route": "/app/test",
            }
        )

        result = pins.delete_pin(created["name"])

        self.assertEqual(result["status"], "deleted")
        self.assertFalse(frappe.db.exists("Desk Navbar Pin", created["name"]))

    def test_reorder_pins(self):
        """Test reordering pins."""
        pin1 = pins.create_pin({"label": "Test Reorder 1", "route": "/app/1"})
        pin2 = pins.create_pin({"label": "Test Reorder 2", "route": "/app/2"})

        result = pins.reorder_pins(
            {
                "pins": [
                    {"name": pin1["name"], "sequence": 2},
                    {"name": pin2["name"], "sequence": 1},
                ]
            }
        )

        self.assertEqual(result["status"], "reordered")

        # Verify order changed
        updated_pin2 = frappe.get_doc("Desk Navbar Pin", pin2["name"])
        self.assertEqual(updated_pin2.sequence, 1)

    def test_pin_ownership(self):
        """Test that users can only delete their own pins."""
        # Create as Administrator
        created = pins.create_pin(
            {
                "label": "Test Ownership",
                "route": "/app/test",
            }
        )

        # Try to delete as different user
        frappe.set_user("Guest")

        with self.assertRaises(frappe.PermissionError):
            pins.delete_pin(created["name"])

        frappe.set_user("Administrator")

    def tearDown(self):
        # Clean up
        frappe.db.delete("Desk Navbar Pin", {"label": ["like", "Test%"]})
