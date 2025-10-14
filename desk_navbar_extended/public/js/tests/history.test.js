QUnit.module("History", function() {
  QUnit.test("history menu exists", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_grouped_history: true } };
    assert.ok(frappe.desk_navbar_extended.history, "History module exists");
  });
});
