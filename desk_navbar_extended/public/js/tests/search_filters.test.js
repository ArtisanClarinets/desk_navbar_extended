QUnit.module("Search Filters", function () {
  QUnit.test("filter bar renders when enabled", function (assert) {
    frappe.desk_navbar_extended = { settings: { enable_smart_filters: true } };
    assert.ok(
      frappe.desk_navbar_extended.search_filters,
      "Search filters module exists",
    );
  });

  QUnit.test("doctype filter populated", function (assert) {
    const done = assert.async();
    setTimeout(() => {
      const options = $(".search-filter--doctype select option");
      assert.ok(options.length >= 1, "DocType filter has options");
      done();
    }, 500);
  });
});
