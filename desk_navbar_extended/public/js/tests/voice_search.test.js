QUnit.module("Desk Navbar Extended Voice Search", () => {
  QUnit.test("voice module exposes init function", (assert) => {
    assert.expect(1);
    assert.equal(typeof window.desk_navbar_extended.voice.init, "function");
  });
});
