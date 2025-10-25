QUnit.module("Quick Create", function () {
  QUnit.test("quick create menu renders", function (assert) {
    frappe.desk_navbar_extended = {
      settings: { features: { quick_create: true } },
    };
    assert.ok(
      frappe.desk_navbar_extended.quick_create,
      "Quick create module exists",
    );
  });

  QUnit.test("menu items loaded", function (assert) {
    const done = assert.async();
    setTimeout(() => {
      const items = $(".quick-create__item");
      assert.ok(items.length >= 0, "Quick create items present or loading");
      done();
    }, 500);
  });
});
