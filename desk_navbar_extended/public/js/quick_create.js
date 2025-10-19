/**
 * Quick Create - Fast access to create common DocTypes
 */
(() => {
  frappe.provide("desk_navbar_extended.quick_create");

  let state = { options: [], menu: null };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.enable_quick_create) return;
    buildMenu();
    loadOptions();
    console.log("[Quick Create] Ready");
  }

  function buildMenu() {
    const html = `
      <div class="quick-create">
        <div class="dropdown">
          <button class="btn btn-sm btn-primary dropdown-toggle" data-toggle="dropdown">
            <i class="fa fa-plus"></i> ${__("Quick Create")}
          </button>
          <div class="dropdown-menu quick-create__menu"></div>
        </div>
      </div>`;
    $("#navbar-search").before(html);
    state.menu = $(".quick-create__menu");
  }

  async function loadOptions() {
    try {
      const { message } = await frappe.call({
        method:
          "desk_navbar_extended.api.quick_create.get_quick_create_options",
        freeze: false,
      });
      state.options = message || [];
      render();
    } catch (err) {
      console.error("[Quick Create] Load error:", err);
    }
  }

  function render() {
    let html = "";
    state.options.forEach((opt) => {
      html += `<a class="dropdown-item quick-create__item" data-doctype="${opt.doctype}" href="#">`;
      html += `<i class="${opt.icon || "fa fa-file"}"></i> ${__(
        opt.label || opt.doctype,
      )}`;
      html += `</a>`;
    });
    state.menu.html(html);
    state.menu.find(".quick-create__item").on("click", function (e) {
      e.preventDefault();
      frappe.new_doc($(this).data("doctype"));
    });
  }

  frappe.desk_navbar_extended.quick_create = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
