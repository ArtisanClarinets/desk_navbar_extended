QUnit.module("Keyboard Manager", function (hooks) {
  hooks.beforeEach(function () {
    frappe.desk_navbar_extended.keyboard_manager.init();
  });

  hooks.afterEach(function () {
    frappe.desk_navbar_extended.keyboard_manager.unregister("Ctrl+Y");
  });

  QUnit.test("executes registered shortcut", function (assert) {
    const done = assert.async();
    let fired = false;
    frappe.desk_navbar_extended.keyboard_manager.register(
      "Ctrl+Y",
      () => {
        fired = true;
      },
      "Demo action",
    );

    $(document).trigger(
      $.Event("keydown", { ctrlKey: true, key: "y", target: document.body }),
    );

    setTimeout(() => {
      assert.ok(fired, "handler invoked");
      done();
    }, 20);
  });
});
