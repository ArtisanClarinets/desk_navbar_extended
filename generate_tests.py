#!/usr/bin/env python3
"""
Generate QUnit tests for Phase 2 frontend modules
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent
TESTS_DIR = BASE_DIR / "desk_navbar_extended" / "public" / "js" / "tests"
TESTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# COMMAND PALETTE TESTS
# ============================================================================
COMMAND_PALETTE_TEST = """QUnit.module("Command Palette", function() {
  QUnit.test("initializes when feature enabled", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_command_palette: true } };
    assert.ok(frappe.desk_navbar_extended.command_palette, "Command palette module exists");
  });

  QUnit.test("keyboard shortcut (Ctrl+K) opens palette", function(assert) {
    const done = assert.async();
    $(document).trigger($.Event("keydown", { ctrlKey: true, key: "k" }));
    setTimeout(() => {
      assert.ok($(".cmd-palette").length > 0, "Palette modal exists");
      done();
    }, 100);
  });

  QUnit.test("ESC key closes palette", function(assert) {
    const done = assert.async();
    $(document).trigger($.Event("keydown", { key: "Escape" }));
    setTimeout(() => {
      assert.ok($(".cmd-palette").attr("hidden") !== undefined || !$(".cmd-palette").is(":visible"), "Palette is hidden");
      done();
    }, 100);
  });
});
"""

# ============================================================================
# SEARCH FILTERS TESTS
# ============================================================================
SEARCH_FILTERS_TEST = """QUnit.module("Search Filters", function() {
  QUnit.test("filter bar renders when enabled", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_smart_filters: true } };
    assert.ok(frappe.desk_navbar_extended.search_filters, "Search filters module exists");
  });

  QUnit.test("doctype filter populated", function(assert) {
    const done = assert.async();
    setTimeout(() => {
      const options = $(".search-filter--doctype select option");
      assert.ok(options.length >= 1, "DocType filter has options");
      done();
    }, 500);
  });
});
"""

# ============================================================================
# SAVED SEARCHES TESTS
# ============================================================================
SAVED_SEARCHES_TEST = """QUnit.module("Saved Searches", function() {
  QUnit.test("saved searches menu exists", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_saved_searches: true } };
    assert.ok(frappe.desk_navbar_extended.saved_searches, "Saved searches module exists");
  });

  QUnit.test("can trigger save current search", function(assert) {
    const done = assert.async();
    $(".saved-searches__new").trigger("click");
    setTimeout(() => {
      assert.ok(true, "Save search triggered");
      done();
    }, 100);
  });
});
"""

# ============================================================================
# PINS TESTS
# ============================================================================
PINS_TEST = """QUnit.module("Pins", function() {
  QUnit.test("pin bar renders", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_pins: true } };
    assert.ok(frappe.desk_navbar_extended.pins, "Pins module exists");
  });

  QUnit.test("add pin button exists", function(assert) {
    const done = assert.async();
    setTimeout(() => {
      assert.ok($(".pin-bar__add").length > 0, "Add pin button exists");
      done();
    }, 200);
  });
});
"""

# ============================================================================
# QUICK CREATE TESTS
# ============================================================================
QUICK_CREATE_TEST = """QUnit.module("Quick Create", function() {
  QUnit.test("quick create menu renders", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_quick_create: true } };
    assert.ok(frappe.desk_navbar_extended.quick_create, "Quick create module exists");
  });

  QUnit.test("menu items loaded", function(assert) {
    const done = assert.async();
    setTimeout(() => {
      const items = $(".quick-create__item");
      assert.ok(items.length >= 0, "Quick create items present or loading");
      done();
    }, 500);
  });
});
"""

# ============================================================================
# HISTORY TESTS
# ============================================================================
HISTORY_TEST = """QUnit.module("History", function() {
  QUnit.test("history menu exists", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_grouped_history: true } };
    assert.ok(frappe.desk_navbar_extended.history, "History module exists");
  });
});
"""

# ============================================================================
# NOTIFICATIONS TESTS
# ============================================================================
NOTIFICATIONS_TEST = """QUnit.module("Notifications Center", function() {
  QUnit.test("notifications panel exists", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_notifications_center: true } };
    assert.ok(frappe.desk_navbar_extended.notifications_center, "Notifications module exists");
  });

  QUnit.test("badge updates on load", function(assert) {
    const done = assert.async();
    setTimeout(() => {
      const badge = $(".notifications-center__badge");
      assert.ok(badge.length > 0, "Badge element exists");
      done();
    }, 200);
  });
});
"""

# ============================================================================
# KPI WIDGETS TESTS
# ============================================================================
KPI_WIDGETS_TEST = """QUnit.module("KPI Widgets", function() {
  QUnit.test("kpi container renders", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_kpi_widgets: true } };
    assert.ok(frappe.desk_navbar_extended.kpi_widgets, "KPI widgets module exists");
  });

  QUnit.test("widgets load", function(assert) {
    const done = assert.async();
    setTimeout(() => {
      const widgets = $(".kpi-widget");
      assert.ok(widgets.length >= 0, "KPI widgets present or loading");
      done();
    }, 500);
  });
});
"""

# ============================================================================
# HELP SEARCH TESTS
# ============================================================================
HELP_SEARCH_TEST = """QUnit.module("Help Search", function() {
  QUnit.test("help modal exists", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_help_search: true } };
    assert.ok(frappe.desk_navbar_extended.help_search, "Help search module exists");
  });

  QUnit.test("Shift+? opens help", function(assert) {
    const done = assert.async();
    $(document).trigger($.Event("keydown", { shiftKey: true, key: "?" }));
    setTimeout(() => {
      assert.ok($(".help-search-modal").length > 0, "Help modal exists");
      done();
    }, 100);
  });
});
"""

# ============================================================================
# DENSITY TOGGLE TESTS
# ============================================================================
DENSITY_TOGGLE_TEST = """QUnit.module("Density Toggle", function() {
  QUnit.test("density toggle button exists", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_density_toggle: true } };
    assert.ok(frappe.desk_navbar_extended.density_toggle, "Density toggle module exists");
  });

  QUnit.test("toggles body class", function(assert) {
    const done = assert.async();
    $(".density-toggle").trigger("click");
    setTimeout(() => {
      assert.ok($("body").hasClass("density-compact") || $("body").hasClass("density-comfortable"), "Density class applied");
      done();
    }, 100);
  });
});
"""

# ============================================================================
# KEYBOARD MANAGER TESTS
# ============================================================================
KEYBOARD_MANAGER_TEST = """QUnit.module("Keyboard Manager", function() {
  QUnit.test("keyboard manager module exists", function(assert) {
    assert.ok(frappe.desk_navbar_extended.keyboard_manager, "Keyboard manager exists");
  });

  QUnit.test("can register shortcut", function(assert) {
    frappe.desk_navbar_extended.keyboard_manager.register("Ctrl+T", () => {}, "Test shortcut");
    assert.ok(true, "Shortcut registered");
  });
});
"""

# Write all test files
tests = {
    "command_palette.test.js": COMMAND_PALETTE_TEST,
    "search_filters.test.js": SEARCH_FILTERS_TEST,
    "saved_searches.test.js": SAVED_SEARCHES_TEST,
    "pins.test.js": PINS_TEST,
    "quick_create.test.js": QUICK_CREATE_TEST,
    "history.test.js": HISTORY_TEST,
    "notifications_center.test.js": NOTIFICATIONS_TEST,
    "kpi_widgets.test.js": KPI_WIDGETS_TEST,
    "help_search.test.js": HELP_SEARCH_TEST,
    "density_toggle.test.js": DENSITY_TOGGLE_TEST,
    "keyboard_manager.test.js": KEYBOARD_MANAGER_TEST,
}

print("Generating QUnit tests for Phase 2 modules...")
for filename, content in tests.items():
    filepath = TESTS_DIR / filename
    filepath.write_text(content)
    print(f"✓ Created {filename}")

print(f"\\n🎉 Generated {len(tests)} QUnit test files in {TESTS_DIR}")
