QUnit.module("Command Palette", function() {
  QUnit.test("initializes when feature enabled", function(assert) {
    frappe.desk_navbar_extended = { settings: { enable_command_palette: true } };
    assert.ok(frappe.desk_navbar_extended.command_palette, "Command palette module exists");
  });

  QUnit.test("keyboard shortcut (Ctrl+K) opens palette", function(assert) {
    const done = assert.async();
    $(document).trigger($.Event("keydown", { ctrlKey: true, key: "k" }));
    setTimeout(() => {
      assert.ok($(".cmd-palette").length > 0, "Palette modal exists");
      done();
    }, 100);
  });

  QUnit.test("ESC key closes palette", function(assert) {
    const done = assert.async();
    $(document).trigger($.Event("keydown", { key: "Escape" }));
    setTimeout(() => {
      assert.ok($(".cmd-palette").attr("hidden") !== undefined || !$(".cmd-palette").is(":visible"), "Palette is hidden");
      done();
    }, 100);
  });
});
