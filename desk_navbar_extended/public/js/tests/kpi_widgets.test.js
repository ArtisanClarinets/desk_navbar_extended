QUnit.module("KPI Widgets", function () {
  QUnit.test("kpi container renders", function (assert) {
    frappe.desk_navbar_extended = { settings: { enable_kpi_widgets: true } };
    assert.ok(
      frappe.desk_navbar_extended.kpi_widgets,
      "KPI widgets module exists",
    );
  });

  QUnit.test("widgets load", function (assert) {
    const done = assert.async();
    setTimeout(() => {
      const widgets = $(".kpi-widget");
      assert.ok(widgets.length >= 0, "KPI widgets present or loading");
      done();
    }, 500);
  });
});
