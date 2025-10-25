QUnit.module("Help Search", function (hooks) {
  hooks.beforeEach(function () {
    this.originalCall = frappe.call;
    frappe.desk_navbar_extended = {
      settings: { features: { help_search: true } },
      help_search: frappe.desk_navbar_extended.help_search,
    };
  });

  hooks.afterEach(function () {
    frappe.call = this.originalCall;
    $(".help-search-modal").remove();
  });

  QUnit.test("renders grouped help suggestions", function (assert) {
    const done = assert.async();
    frappe.call = () =>
      Promise.resolve({
        message: [
          {
            type: "help_article",
            title: "Usage",
            route: "/app/help-article/USG",
          },
          {
            type: "external_doc",
            title: "Docs",
            route: "https://example.com",
            external: true,
          },
        ],
      });

    frappe.desk_navbar_extended.help_search.init();
    $(document).trigger($.Event("keydown", { shiftKey: true, key: "?" }));

    setTimeout(() => {
      const $input = $(".help-search__search input");
      $input.val("test").trigger("input");

      setTimeout(() => {
        const categories = $(".help-category h6")
          .map((_, el) => $(el).text().trim())
          .get();
        assert.ok(
          categories.includes(__("Help Articles")),
          "articles rendered",
        );
        assert.ok(categories.includes(__("Documentation")), "docs rendered");
        assert.equal($(".help-result").length, 2, "results listed");
        done();
      }, 50);
    }, 50);
  });
});
