QUnit.module("Help Search", function () {
  QUnit.test("help modal exists", function (assert) {
    frappe.desk_navbar_extended = { settings: { enable_help_search: true } };
    assert.ok(
      frappe.desk_navbar_extended.help_search,
      "Help search module exists",
    );
  });

  QUnit.test("Shift+? opens help", function (assert) {
    const done = assert.async();
    $(document).trigger($.Event("keydown", { shiftKey: true, key: "?" }));
    setTimeout(() => {
      assert.ok($(".help-search-modal").length > 0, "Help modal exists");
      done();
    }, 100);
  });
});
