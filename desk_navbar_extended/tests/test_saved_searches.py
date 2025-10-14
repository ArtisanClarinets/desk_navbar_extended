"""Tests for saved searches API."""

from __future__ import annotations

import frappe
from frappe.tests.utils import FrappeTestCase

from desk_navbar_extended.api import saved_searches


class TestSavedSearches(FrappeTestCase):
    def setUp(self):
        # Enable saved searches feature
        settings = frappe.get_single("Desk Navbar Extended Settings")
        settings.enable_saved_searches = 1
        settings.flags.ignore_permissions = True
        settings.save()

        # Clean up test data
        frappe.db.delete("Desk Navbar Saved Search", {"title": ["like", "Test%"]})

    def test_create_saved_search(self):
        """Test creating a saved search."""
        result = saved_searches.create_saved_search({
            "title": "Test Search",
            "query": "test query",
            "doctype_filter": "User",
        })
        
        self.assertEqual(result["title"], "Test Search")
        self.assertEqual(result["query"], "test query")
        self.assertEqual(result["doctype_filter"], "User")
        self.assertFalse(result["is_global"])

    def test_list_saved_searches(self):
        """Test listing saved searches."""
        # Create a test search
        saved_searches.create_saved_search({
            "title": "Test List",
            "query": "list test",
        })
        
        results = saved_searches.list_saved_searches()
        
        self.assertIsInstance(results, list)
        found = any(s["title"] == "Test List" for s in results)
        self.assertTrue(found)

    def test_update_saved_search(self):
        """Test updating a saved search."""
        # Create
        created = saved_searches.create_saved_search({
            "title": "Test Update",
            "query": "original query",
        })
        
        # Update
        updated = saved_searches.update_saved_search(
            created["name"],
            {"query": "updated query"}
        )
        
        self.assertEqual(updated["query"], "updated query")

    def test_delete_saved_search(self):
        """Test deleting a saved search."""
        # Create
        created = saved_searches.create_saved_search({
            "title": "Test Delete",
            "query": "delete test",
        })
        
        # Delete
        result = saved_searches.delete_saved_search(created["name"])
        
        self.assertEqual(result["status"], "deleted")
        self.assertFalse(frappe.db.exists("Desk Navbar Saved Search", created["name"]))

    def test_global_search_requires_system_manager(self):
        """Test that global searches require System Manager role."""
        # Create test user if doesn't exist
        if not frappe.db.exists("User", "test@example.com"):
            test_user = frappe.get_doc({
                "doctype": "User",
                "email": "test@example.com",
                "first_name": "Test",
                "send_welcome_email": 0,
            })
            test_user.flags.ignore_permissions = True
            test_user.insert()
        
        frappe.set_user("test@example.com")
        
        with self.assertRaises(frappe.PermissionError):
            saved_searches.create_saved_search({
                "title": "Test Global",
                "query": "global test",
                "is_global": 1,
            })
        
        frappe.set_user("Administrator")

    def tearDown(self):
        # Clean up
        frappe.db.delete("Desk Navbar Saved Search", {"title": ["like", "Test%"]})
