QUnit.module("Notifications Center", function () {
  QUnit.test("notifications panel exists", function (assert) {
    frappe.desk_navbar_extended = {
      settings: { enable_notifications_center: true },
    };
    assert.ok(
      frappe.desk_navbar_extended.notifications_center,
      "Notifications module exists",
    );
  });

  QUnit.test("badge updates on load", function (assert) {
    const done = assert.async();
    setTimeout(() => {
      const badge = $(".notifications-center__badge");
      assert.ok(badge.length > 0, "Badge element exists");
      done();
    }, 200);
  });
});
