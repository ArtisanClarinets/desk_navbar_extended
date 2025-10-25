"""
Ensure Desk Navbar Extended Settings singleton exists with proper defaults.

This patch addresses installations where the singleton was not properly created
during initial installation or was accidentally deleted.
"""

from __future__ import annotations

import frappe


def execute() -> None:
    """Create missing settings singleton with proper defaults."""

    if not frappe.db.table_exists("tabDesk Navbar Extended Settings"):
        frappe.logger("desk_navbar_extended").warning(
            "Desk Navbar Extended Settings table does not exist, skipping patch"
        )
        return

    # Import here to avoid circular imports during patch execution
    from desk_navbar_extended.desk_navbar_extended.setup import seed_default_settings

    try:
        seed_default_settings()
        frappe.logger("desk_navbar_extended").info(
            "Successfully ensured settings singleton exists"
        )
    except Exception as e:
        frappe.logger("desk_navbar_extended").error(
            f"Failed to create settings singleton: {e}",
            exc_info=True,
        )
        # Re-raise to fail the patch if critical
        raise
