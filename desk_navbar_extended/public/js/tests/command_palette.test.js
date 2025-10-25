QUnit.module("Command Palette", function (hooks) {
  hooks.beforeEach(function () {
    this.originalCall = frappe.call;
    frappe.desk_navbar_extended = {
      settings: { features: { command_palette: true } },
      command_palette: frappe.desk_navbar_extended.command_palette,
      saved_searches: {
        applySearch: function (name) {
          this.last = name;
        },
      },
    };
    this.applyStub = frappe.desk_navbar_extended.saved_searches;
  });

  hooks.afterEach(function () {
    frappe.call = this.originalCall;
    $(".cmd-palette").remove();
  });

  QUnit.test("aggregates sources and selects saved search", function (assert) {
    const done = assert.async();
    const response = {
      doctypes: [
        {
          type: "doctype",
          label: "Task",
          value: "Task",
          icon: "fa fa-check",
          route: "/app/task",
        },
      ],
      saved_searches: [
        {
          type: "saved_search",
          label: "My Search",
          value: "SEARCH-1",
          data: { name: "SEARCH-1" },
        },
      ],
    };

    frappe.call = () => Promise.resolve({ message: response });

    frappe.desk_navbar_extended.command_palette.init();
    $(document).trigger($.Event("keydown", { ctrlKey: true, key: "k" }));

    setTimeout(() => {
      const categories = $(".cmd-palette__category-label")
        .map((_, el) => $(el).text().trim())
        .get();
      assert.deepEqual(
        categories,
        [__("Doctypes"), __("Saved Searches")],
        "categories rendered",
      );

      $(".cmd-palette__item").last().trigger("click");

      setTimeout(() => {
        assert.strictEqual(
          frappe.desk_navbar_extended.saved_searches.last,
          "SEARCH-1",
          "saved search applied on select",
        );
        done();
      }, 50);
    }, 50);
  });
});
