"""Installation helpers for Desk Navbar Extended."""

from __future__ import annotations

import frappe
from frappe.utils import cint

from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import (
    get_settings_doc,
)

NAVBAR_ITEM_LABEL = "Show Time"
NAVBAR_ACTION = "frappe.desk_navbar_extended.show_clock"

NAVBAR_EXTND_ITEMS = [
    {
        "item_label": NAVBAR_ITEM_LABEL,
        "item_type": "Action",
        "action": NAVBAR_ACTION,
        "is_standard": 0,
        "idx": 1,
    },
    {
        "item_type": "Separator",
        "is_standard": 0,
        "idx": 2,
    },
]


def seed_default_settings() -> None:
    """Ensure the singleton settings record exists with sensible defaults."""

    # First ensure the singleton exists
    try:
        settings_doc = frappe.get_single("Desk Navbar Extended Settings")
    except frappe.DoesNotExistError:
        settings_doc = frappe.new_doc("Desk Navbar Extended Settings")
        settings_doc.insert(ignore_permissions=True)

    defaults = {
        "enable_clock": 1,
        "enable_voice_search": 0,
        "enable_wide_awesomebar": 1,
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
        "enable_help_search": 1,
        "clock_time_format": "12h",
        "show_calendar_excerpts": 1,
        "timezone_event_limit": 3,
        "awesomebar_default_width": 560,
        "awesomebar_mobile_collapse": 1,
        "enable_usage_analytics": 0,
        "kpi_refresh_interval": 300,
    }

    # Update values only if they're not already set
    for fieldname, value in defaults.items():
        existing = settings_doc.get(fieldname)
        if existing is None or (isinstance(existing, (int, bool)) and not existing):
            settings_doc.set(fieldname, value)

    settings_doc.save(ignore_permissions=True)
    frappe.db.commit()

    frappe.logger("desk_navbar_extended").info(
        "Settings singleton initialized successfully", extra={"method": "seed_default_settings"}
    )


def add_clock_navbar_item() -> None:
    if frappe.db.exists("Navbar Item", {"action": NAVBAR_ACTION}):
        return

    navbar_settings = frappe.get_single("Navbar Settings")
    for ni in navbar_settings.settings_dropdown:
        ni.idx = cint(ni.idx) + len(NAVBAR_EXTND_ITEMS)
    navbar_settings.extend("settings_dropdown", NAVBAR_EXTND_ITEMS)
    navbar_settings.save()
    frappe.db.commit()


def remove_clock_navbar_item() -> None:
    if not frappe.db.exists("Navbar Item", {"action": NAVBAR_ACTION}):
        return

    patch_flag = frappe.flags.in_patch
    frappe.flags.in_patch = True
    navbar_settings = frappe.get_single("Navbar Settings")

    for i, ni in enumerate(list(navbar_settings.settings_dropdown)):
        if getattr(ni, "action", None) == NAVBAR_ACTION or ni.item_label == NAVBAR_ITEM_LABEL:
            navbar_settings.settings_dropdown.pop(i)
            if len(navbar_settings.settings_dropdown) > i and (
                navbar_settings.settings_dropdown[i].item_type == "Separator"
            ):
                navbar_settings.settings_dropdown.pop(i)
            elif i > 0 and (navbar_settings.settings_dropdown[i - 1].item_type == "Separator"):
                navbar_settings.settings_dropdown.pop(i - 1)
            break
    navbar_settings.save()
    frappe.db.commit()
    frappe.flags.in_patch = patch_flag


def after_install() -> None:
    seed_default_settings()
    settings = get_settings_doc()
    if settings.enable_clock:
        add_clock_navbar_item()


def after_uninstall() -> None:
    remove_clock_navbar_item()
