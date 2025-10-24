/**
 * Saved Searches - Save and reuse search queries
 */
(() => {
  frappe.provide("desk_navbar_extended.saved_searches");

  let state = { searches: [], menu: null, dropdown: null };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.features?.saved_searches) return;
    buildMenu();
    loadSearches();
    console.log("[Saved Searches] Ready");
  }

  function buildMenu() {
    const html = `
      <div class="saved-searches">
        <div class="dropdown">
          <button class="btn btn-sm btn-default dropdown-toggle" data-toggle="dropdown">
            <i class="fa fa-bookmark"></i> ${__("Saved")}
          </button>
          <div class="dropdown-menu saved-searches__menu">
            <div class="saved-searches__loading">${__("Loading...")}</div>
            <div class="saved-searches__empty" hidden>${__(
              "No saved searches",
            )}</div>
            <div class="saved-searches__list"></div>
            <div class="dropdown-divider"></div>
            <a class="dropdown-item saved-searches__new" href="#"><i class="fa fa-plus"></i> ${__(
              "Save Current Search",
            )}</a>
          </div>
        </div>
      </div>`;
    $("#navbar-search").before(html);
    state.menu = $(".saved-searches");
    state.dropdown = state.menu.find(".saved-searches__menu");
    bindEvents();
  }

  function bindEvents() {
    state.menu.find(".saved-searches__new").on("click", (e) => {
      e.preventDefault();
      saveCurrentSearch();
    });
    state.dropdown.on("click", ".saved-search-item", function () {
      applySearch($(this).data("id"));
    });
    state.dropdown.on("click", ".saved-search-item__delete", function (e) {
      e.stopPropagation();
      deleteSearch($(this).closest(".saved-search-item").data("id"));
    });
  }

  async function loadSearches() {
    showLoading();
    try {
      const { message } = await frappe.call({
        method: "desk_navbar_extended.api.saved_searches.list_saved_searches",
        freeze: false,
      });
      state.searches = Array.isArray(message) ? message : [];
      render();
    } catch (err) {
      console.error("[Saved Searches] Load error:", err);
      hideLoading();
    }
  }

  function render() {
    hideLoading();
    if (!state.searches.length) {
      showEmpty();
      return;
    }
    hideEmpty();
    let html = "";
    state.searches.forEach((s) => {
      html += `<a class="dropdown-item saved-search-item" data-id="${s.name}" href="#">`;
      html += `<span class="saved-search-item__title">${frappe.utils.escape_html(
        s.title,
      )}</span>`;
      if (s.doctype_filter)
        html += `<span class="saved-search-item__doctype text-muted">${frappe.utils.escape_html(
          s.doctype_filter,
        )}</span>`;
      html += `<button class="btn btn-xs btn-link saved-search-item__delete" title="${__(
        "Delete",
      )}"><i class="fa fa-trash"></i></button>`;
      html += `</a>`;
    });
    state.dropdown.find(".saved-searches__list").html(html);
  }

  async function saveCurrentSearch() {
    const query = $("#navbar-search input").val();
    if (!query) {
      frappe.show_alert(__("No search query to save"));
      return;
    }
    const name = await frappe.prompt({
      label: __("Search Name"),
      fieldtype: "Data",
      reqd: 1,
    });
    if (!name) return;
    const payload = {
      title: name,
      query,
    };
    try {
      await frappe.call({
        method: "desk_navbar_extended.api.saved_searches.create_saved_search",
        args: { payload },
      });
      frappe.show_alert({ message: __("Search saved"), indicator: "green" });
      loadSearches();
    } catch (err) {
      console.error("[Saved Searches] Save error:", err);
      frappe.show_alert({
        message: __("Failed to save search"),
        indicator: "red",
      });
    }
  }

  function applySearch(id) {
    const search = state.searches.find((s) => s.name === id);
    if (!search) return;

    $("#navbar-search input").val(search.query).trigger("input");

    if (search.filters && frappe.desk_navbar_extended?.search_filters) {
      try {
        frappe.desk_navbar_extended.search_filters.applyFilters(search);
      } catch (err) {
        console.warn("[Saved Searches] Unable to apply advanced filters", err);
      }
    }
  }

  async function deleteSearch(id) {
    if (!confirm(__("Delete this saved search?"))) return;
    try {
      await frappe.call({
        method: "desk_navbar_extended.api.saved_searches.delete_saved_search",
        args: { name: id },
      });
      frappe.show_alert({ message: __("Search deleted"), indicator: "green" });
      loadSearches();
    } catch (err) {
      console.error("[Saved Searches] Delete error:", err);
      frappe.show_alert({ message: __("Failed to delete"), indicator: "red" });
    }
  }

  function showLoading() {
    state.dropdown.find(".saved-searches__loading").show();
    state.dropdown.find(".saved-searches__list").hide();
  }
  function hideLoading() {
    state.dropdown.find(".saved-searches__loading").hide();
    state.dropdown.find(".saved-searches__list").show();
  }
  function showEmpty() {
    state.dropdown.find(".saved-searches__empty").removeAttr("hidden");
  }
  function hideEmpty() {
    state.dropdown.find(".saved-searches__empty").attr("hidden", "");
  }

  frappe.desk_navbar_extended.saved_searches = { init, applySearch };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
