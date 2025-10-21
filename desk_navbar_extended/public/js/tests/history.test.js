QUnit.module("History", function (hooks) {
  hooks.beforeEach(function () {
    this.originalCall = frappe.call;
    this.$navbar = $('<div class="navbar-right"></div>').appendTo("body");
    frappe.desk_navbar_extended = {
      settings: { enable_grouped_history: true },
      history: frappe.desk_navbar_extended.history,
    };
  });

  hooks.afterEach(function () {
    frappe.call = this.originalCall;
    this.$navbar.remove();
  });

  QUnit.test("renders grouped history response", function (assert) {
    const done = assert.async();
    const now = frappe.datetime?.now_datetime
      ? frappe.datetime.now_datetime()
      : new Date().toISOString();
    frappe.call = () =>
      Promise.resolve({
        message: {
          groups: [
            {
              doctype: "ToDo",
              label: "ToDo",
              icon: "fa fa-check",
              count: 1,
              items: [
                {
                  title: "Follow up",
                  modified: now,
                  route: "/app/todo/TODO-0001",
                },
              ],
            },
          ],
        },
      });

    frappe.desk_navbar_extended.history.init();

    setTimeout(() => {
      const groups = $(".history-group");
      assert.equal(groups.length, 1, "history group rendered");
      assert.ok(groups.find(".history-item").length, "history items rendered");
      done();
    }, 50);
  });
});
