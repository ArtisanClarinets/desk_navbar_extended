/**
 * Keyboard Manager - Centralized keyboard shortcut handler
 */
(() => {
  frappe.provide("desk_navbar_extended.keyboard_manager");

  const shortcuts = {};

  function init() {
    console.log("[Keyboard Manager] Ready");
  }

  function register(key, handler, description) {
    shortcuts[key] = { handler, description };
  }

  function unregister(key) {
    delete shortcuts[key];
  }

  function showHelp() {
    const html = Object.entries(shortcuts)
      .map(
        ([key, { description }]) =>
          `<tr><td><kbd>${key}</kbd></td><td>${__(description)}</td></tr>`,
      )
      .join("");
    frappe.msgprint({
      title: __("Keyboard Shortcuts"),
      message: `<table class="table table-bordered"><thead><tr><th>Shortcut</th><th>Action</th></tr></thead><tbody>${html}</tbody></table>`,
    });
  }

  frappe.desk_navbar_extended.keyboard_manager = {
    init,
    register,
    unregister,
    showHelp,
  };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
