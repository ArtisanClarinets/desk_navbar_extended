QUnit.module("Saved Searches", function (hooks) {
  hooks.beforeEach(function () {
    this.originalCall = frappe.call;
    this.originalPrompt = frappe.prompt;
    this.$search = $('<div id="navbar-search"><input type="text" /></div>').appendTo("body");
    frappe.prompt = () => Promise.resolve("Team Tasks");
    const applySpy = function () {
      applySpy.called = true;
    };
    applySpy.called = false;
    frappe.desk_navbar_extended = {
      settings: { features: { saved_searches: true } },
      saved_searches: frappe.desk_navbar_extended.saved_searches,
      search_filters: { applyFilters: applySpy },
    };
    this.applySpy = applySpy;
  });

  hooks.afterEach(function () {
    frappe.call = this.originalCall;
    frappe.prompt = this.originalPrompt;
    this.$search.remove();
  });

  QUnit.test("lists saved searches and applies filters", function (assert) {
    const done = assert.async();
    const calls = [];
    const responses = [
      {
        message: [
          {
            name: "SEARCH-1",
            title: "Open Tasks",
            query: "task",
            doctype_filter: "Task",
            filters: { owner: "user@example.com" },
          },
        ],
      },
      { message: { name: "SEARCH-2" } },
      { message: [] },
    ];

    frappe.call = (opts) => {
      calls.push(opts);
      return Promise.resolve(responses.shift());
    };

    frappe.desk_navbar_extended.saved_searches.init();

    setTimeout(() => {
      $(".saved-search-item").trigger("click");
      assert.strictEqual(
        $("#navbar-search input").val(),
        "task",
        "applies saved search query",
      );
      assert.ok(this.applySpy.called, "applyFilters invoked");

      $("#navbar-search input").val("current");
      $(".saved-searches__new").trigger("click");

      setTimeout(() => {
        const createCall = calls.find(
          (call) =>
            call.method ===
            "desk_navbar_extended.api.saved_searches.create_saved_search",
        );
        assert.deepEqual(
          createCall.args,
          { payload: { title: "Team Tasks", query: "current" } },
          "create_saved_search wraps payload",
        );
        done();
      }, 50);
    }, 50);
  });
});
