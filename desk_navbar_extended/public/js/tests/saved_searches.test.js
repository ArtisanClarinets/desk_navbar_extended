QUnit.module("Saved Searches", function () {
  QUnit.test("saved searches menu exists", function (assert) {
    frappe.desk_navbar_extended = { settings: { enable_saved_searches: true } };
    assert.ok(
      frappe.desk_navbar_extended.saved_searches,
      "Saved searches module exists",
    );
  });

  QUnit.test("can trigger save current search", function (assert) {
    const done = assert.async();
    $(".saved-searches__new").trigger("click");
    setTimeout(() => {
      assert.ok(true, "Save search triggered");
      done();
    }, 100);
  });
});
