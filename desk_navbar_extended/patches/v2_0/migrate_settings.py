"""Migration script to add new feature flags to existing installations."""

from __future__ import annotations

import frappe


def execute():
    """Add new feature flags to Desk Navbar Extended Settings."""
    
    if not frappe.db.exists("DocType", "Desk Navbar Extended Settings"):
        return

    settings = frappe.get_single("Desk Navbar Extended Settings")
    
    # New feature flags with defaults
    new_fields = {
        "enable_smart_filters": 1,
        "enable_saved_searches": 1,
        "enable_quick_create": 1,
        "enable_pins": 1,
        "enable_grouped_history": 1,
        "enable_command_palette": 1,
        "enable_density_toggle": 1,
        "enable_notifications_center": 1,
        "enable_role_toggles": 1,
        "enable_kpi_widgets": 0,
        "enable_timezone_switcher": 1,
        "enable_voice_actions": 0,
        "enable_help_search": 1,
        "enable_layout_bookmarks": 0,
        "kpi_refresh_interval": 300,
    }
    
    updated = False
    for field, default_value in new_fields.items():
        if not hasattr(settings, field) or settings.get(field) is None:
            settings.set(field, default_value)
            updated = True
    
    if updated:
        settings.flags.ignore_permissions = True
        settings.flags.ignore_mandatory = True
        settings.save()
        
        frappe.db.commit()
        
        print("✅ Migrated Desk Navbar Extended Settings with new feature flags")
