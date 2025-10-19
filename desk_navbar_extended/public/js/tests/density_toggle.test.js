QUnit.module("Density Toggle", function () {
  QUnit.test("density toggle button exists", function (assert) {
    frappe.desk_navbar_extended = { settings: { enable_density_toggle: true } };
    assert.ok(
      frappe.desk_navbar_extended.density_toggle,
      "Density toggle module exists",
    );
  });

  QUnit.test("toggles body class", function (assert) {
    const done = assert.async();
    $(".density-toggle").trigger("click");
    setTimeout(() => {
      assert.ok(
        $("body").hasClass("density-compact") ||
          $("body").hasClass("density-comfortable"),
        "Density class applied",
      );
      done();
    }, 100);
  });
});
