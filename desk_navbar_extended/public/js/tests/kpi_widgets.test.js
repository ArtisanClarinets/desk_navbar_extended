QUnit.module("KPI Widgets", function (hooks) {
  hooks.beforeEach(function () {
    this.originalCall = frappe.call;
    this.originalInterval = window.setInterval;
    this.$breadcrumbs = $('<div id="navbar-breadcrumbs"></div>').appendTo(
      "body",
    );
    this.lastDelay = null;
    window.setInterval = (fn, delay) => {
      this.lastDelay = delay;
      return 1;
    };
    frappe.call = () => Promise.resolve({ message: [] });
    frappe.desk_navbar_extended = {
      settings: {
        features: { kpi_widgets: true },
        kpi: { refresh_interval: 120 },
      },
      kpi_widgets: frappe.desk_navbar_extended.kpi_widgets,
    };
  });

  hooks.afterEach(function () {
    frappe.call = this.originalCall;
    window.setInterval = this.originalInterval;
    this.$breadcrumbs.remove();
    $(".kpi-widgets").remove();
  });

  QUnit.test("respects configured refresh interval", function (assert) {
    frappe.desk_navbar_extended.kpi_widgets.init();
    assert.strictEqual(
      this.lastDelay,
      120000,
      "interval uses configured seconds",
    );
  });
});
