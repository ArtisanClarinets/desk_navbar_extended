QUnit.module("Notifications Center", function (hooks) {
  hooks.beforeEach(function () {
    this.originalCall = frappe.call;
    this.$navbar = $('<div class="navbar-right"></div>').appendTo("body");
    frappe.desk_navbar_extended = {
      settings: { enable_notifications_center: true },
      notifications_center: frappe.desk_navbar_extended.notifications_center,
    };
  });

  hooks.afterEach(function () {
    frappe.call = this.originalCall;
    this.$navbar.remove();
  });

  QUnit.test("consumes unread_count and marks items", function (assert) {
    const done = assert.async();
    const calls = [];
    const now = frappe.datetime?.now_datetime
      ? frappe.datetime.now_datetime()
      : new Date().toISOString();
    const responses = [
      {
        message: {
          notifications: [
            {
              name: "NOTIF-001",
              subject: "New Task",
              read: 0,
              creation: now,
            },
          ],
          unread_count: 1,
        },
      },
      { message: { count: 1 } },
      { message: { notifications: [], unread_count: 0 } },
    ];

    frappe.call = (opts) => {
      calls.push(opts);
      return Promise.resolve(responses.shift());
    };

    frappe.desk_navbar_extended.notifications_center.init();

    setTimeout(() => {
      const badgeText = $(".notifications-center__badge").text().trim();
      assert.strictEqual(badgeText, "1", "badge shows unread count");
      $(".notification-item__mark").trigger("click");

      setTimeout(() => {
        const markCall = calls.find(
          (call) =>
            call.method ===
            "desk_navbar_extended.api.notifications.mark_as_read",
        );
        assert.deepEqual(
          markCall.args,
          { payload: { names: ["NOTIF-001"] } },
          "mark_as_read called with payload list",
        );
        done();
      }, 50);
    }, 50);
  });
});
