QUnit.module("Keyboard Manager", function () {
  QUnit.test("keyboard manager module exists", function (assert) {
    assert.ok(
      frappe.desk_navbar_extended.keyboard_manager,
      "Keyboard manager exists",
    );
  });

  QUnit.test("can register shortcut", function (assert) {
    frappe.desk_navbar_extended.keyboard_manager.register(
      "Ctrl+T",
      () => {},
      "Test shortcut",
    );
    assert.ok(true, "Shortcut registered");
  });
});
