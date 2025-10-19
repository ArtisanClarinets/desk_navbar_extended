"""Tests for search filters API."""

from __future__ import annotations

import frappe
from frappe.tests.utils import FrappeTestCase

from desk_navbar_extended.api import search_filters


class TestSearchFilters(FrappeTestCase):
    def setUp(self):
        # Enable smart filters feature
        settings = frappe.get_single("Desk Navbar Extended Settings")
        settings.enable_smart_filters = 1
        settings.flags.ignore_permissions = True
        settings.save()

    def test_search_with_filters_requires_query(self):
        """Test that search requires a query."""
        with self.assertRaises(frappe.ValidationError):
            search_filters.search_with_filters("")

    def test_search_with_doctype_filter(self):
        """Test search with doctype filter."""
        result = search_filters.search_with_filters(
            query="test",
            doctype="User",
            limit=5,
        )

        self.assertIn("results", result)
        self.assertIn("query", result)
        self.assertEqual(result["query"], "test")
        self.assertIsInstance(result["results"], list)

    def test_search_respects_permissions(self):
        """Test that search respects doctype permissions."""
        frappe.set_user("Guest")

        with self.assertRaises(frappe.PermissionError):
            search_filters.search_with_filters(
                query="test",
                doctype="User",
            )

        frappe.set_user("Administrator")

    def test_search_with_owner_filter(self):
        """Test search with owner filter."""
        result = search_filters.search_with_filters(
            query="test",
            owner="Administrator",
            limit=10,
        )

        self.assertIn("results", result)
        self.assertIn("filters", result)
        self.assertEqual(result["filters"]["owner"], "Administrator")

    def test_search_limit_enforced(self):
        """Test that search limit is enforced."""
        result = search_filters.search_with_filters(
            query="test",
            limit=1000,  # Request more than max
        )

        # Should be capped at 100
        self.assertLessEqual(result["count"], 100)

    def test_feature_flag_gating(self):
        """Test that feature flag gates access."""
        settings = frappe.get_single("Desk Navbar Extended Settings")
        settings.enable_smart_filters = 0
        settings.flags.ignore_permissions = True
        settings.save()

        with self.assertRaises(frappe.PermissionError):
            search_filters.search_with_filters(query="test")

        # Restore
        settings.enable_smart_filters = 1
        settings.flags.ignore_permissions = True
        settings.save()
