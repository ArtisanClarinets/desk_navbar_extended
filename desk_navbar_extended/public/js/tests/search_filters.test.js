QUnit.module("Search Filters", function (hooks) {
  hooks.beforeEach(function () {
    this.originalCall = frappe.call;
    this.originalSearch = frappe.search.utils.search;
    this.$search = $('<div id="navbar-search"></div>').appendTo("body");
    frappe.search.utils.search = function (...args) {
      return Promise.resolve({ args, source: "original" });
    };
    frappe.desk_navbar_extended = {
      settings: { features: { smart_filters: true } },
      search_filters: frappe.desk_navbar_extended.search_filters,
    };
  });

  hooks.afterEach(function () {
    frappe.call = this.originalCall;
    frappe.search.utils.search = this.originalSearch;
    this.$search.remove();
    $(".search-filters").remove();
  });

  QUnit.test("overrides search utils when filters active", function (assert) {
    const done = assert.async();
    frappe.call = () =>
      Promise.resolve({
        message: { results: [{ name: "TASK-0001" }] },
      });

    frappe.desk_navbar_extended.search_filters.init();

    setTimeout(() => {
      $(".search-filter--doctype select").val("Task").trigger("change");
      frappe.search.utils
        .search("plan")
        .then((result) => {
          assert.deepEqual(
            result,
            [{ name: "TASK-0001" }],
            "returns filtered results",
          );
          frappe.desk_navbar_extended.search_filters.applyFilters({
            doctype_filter: "Task",
            filters: { owner: "user@example.com" },
          });
          assert.strictEqual(
            $(".search-filter--owner input").val(),
            "user@example.com",
            "applyFilters hydrates owner",
          );
          done();
        })
        .catch((err) => {
          assert.ok(false, err);
          done();
        });
    }, 50);
  });
});
