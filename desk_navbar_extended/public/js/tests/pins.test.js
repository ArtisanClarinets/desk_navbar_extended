QUnit.module("Pins", function (hooks) {
  hooks.beforeEach(function () {
    this.originalCall = frappe.call;
    this.originalDialog = frappe.ui.Dialog;
    this.$breadcrumbs = $('<div id="navbar-breadcrumbs"></div>').appendTo(
      "body",
    );
    frappe.desk_navbar_extended = {
      settings: { features: { pins: true } },
      pins: frappe.desk_navbar_extended.pins,
    };
  });

  hooks.afterEach(function () {
    frappe.call = this.originalCall;
    frappe.ui.Dialog = this.originalDialog;
    this.$breadcrumbs.remove();
  });

  QUnit.test("renders icons and creates pins with payload", function (assert) {
    const done = assert.async();
    const calls = [];
    const responses = [
      {
        message: [
          {
            name: "PIN-1",
            label: "Inbox",
            route: "/app/inbox",
            icon: "fa fa-inbox",
          },
        ],
      },
      { message: { name: "PIN-2" } },
      { message: [] },
    ];

    frappe.call = (opts) => {
      calls.push(opts);
      return Promise.resolve(responses.shift());
    };

    frappe.ui.Dialog = function (opts) {
      this.opts = opts;
      this.show = () => {
        Promise.resolve(
          opts.primary_action({
            label: "Important",
            doctype: "Task",
            doc_name: "TASK-0001",
            icon: "fa fa-flag",
          }),
        );
      };
      this.hide = () => {};
    };

    frappe.desk_navbar_extended.pins.init();

    setTimeout(() => {
      const iconClass = $(".pin-item i").attr("class");
      assert.strictEqual(
        iconClass,
        "fa fa-inbox",
        "pin uses icon from payload",
      );

      $(".pin-bar__add").trigger("click");

      setTimeout(() => {
        const createCall = calls.find(
          (call) => call.method === "desk_navbar_extended.api.pins.create_pin",
        );
        assert.deepEqual(
          createCall.args,
          {
            payload: {
              label: "Important",
              route: "/app/task/TASK-0001",
              icon: "fa fa-flag",
            },
          },
          "create_pin called with wrapped payload",
        );
        done();
      }, 50);
    }, 50);
  });
});
