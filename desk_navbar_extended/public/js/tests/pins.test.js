QUnit.module("Pins", function() {
  QUnit.test("pin bar renders", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_pins: true } };
    assert.ok(frappe.desk_navbar_extended.pins, "Pins module exists");
  });

  QUnit.test("add pin button exists", function(assert) {
    const done = assert.async();
    setTimeout(() => {
      assert.ok($(".pin-bar__add").length > 0, "Add pin button exists");
      done();
    }, 200);
  });
});
