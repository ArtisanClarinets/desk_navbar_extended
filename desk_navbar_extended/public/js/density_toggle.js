/**
 * Density Toggle - Compact/comfortable view mode
 */
(() => {
  frappe.provide("desk_navbar_extended.density_toggle");

  const DENSITY_KEY = "desk-navbar-density";
  let state = { density: "comfortable", toggle: null };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.enable_density_toggle) return;
    loadPreference();
    buildToggle();
    applyDensity();
    console.log("[Density Toggle] Ready");
  }

  function loadPreference() {
    state.density = localStorage.getItem(DENSITY_KEY) || "comfortable";
  }

  function buildToggle() {
    const html = `
      <button class="btn btn-sm btn-default density-toggle" title="${__("Toggle density")}" aria-label="${__("Toggle density mode")}" role="button">
        <i class="fa fa-compress" aria-hidden="true"></i>
      </button>`;
    $(".navbar-right").prepend(html);
    state.toggle = $(".density-toggle");
    state.toggle.on("click", toggle);
    updateIcon();
  }

  function toggle() {
    state.density = state.density === "comfortable" ? "compact" : "comfortable";
    localStorage.setItem(DENSITY_KEY, state.density);
    applyDensity();
    updateIcon();
  }

  function applyDensity() {
    $("body")
      .removeClass("density-comfortable density-compact")
      .addClass(`density-${state.density}`);
  }

  function updateIcon() {
    const icon = state.density === "compact" ? "fa-expand" : "fa-compress";
    state.toggle.find("i").attr("class", `fa ${icon}`);
  }

  frappe.desk_navbar_extended.density_toggle = { init };

  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
