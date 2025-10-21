/**
 * Smart Search Filters - Enhanced awesomebar search
 */
(() => {
  frappe.provide("desk_navbar_extended.search_filters");

  let state = {
    filters: { doctype: null, owner: null, date_from: null, date_to: null },
    filterBar: null,
    originalSearch: null,
  };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.enable_smart_filters) return;
    buildFilterBar();
    hookIntoAwesomebar();
    console.log("[Search Filters] Ready");
  }

  function buildFilterBar() {
    const html = `
      <div class="search-filters">
        <div class="search-filters__chips">
          <div class="search-filter search-filter--doctype">
            <label>${__("DocType:")}</label>
            <select class="form-control form-control-sm">
              <option value="">${__("All")}</option>
            </select>
          </div>
          <div class="search-filter search-filter--owner">
            <label>${__("Owner:")}</label>
            <input type="text" class="form-control form-control-sm" placeholder="${__(
              "Any user",
            )}" />
          </div>
          <div class="search-filter search-filter--dates">
            <label>${__("From:")}</label>
            <input type="date" class="form-control form-control-sm search-filter__date-from" />
            <label>${__("To:")}</label>
            <input type="date" class="form-control form-control-sm search-filter__date-to" />
          </div>
          <button class="btn btn-sm btn-secondary search-filters__clear">${__(
            "Clear",
          )}</button>
        </div>
      </div>`;
    $("#navbar-search").before(html);
    state.filterBar = $(".search-filters");
    bindEvents();
    loadDoctypes();
  }

  function bindEvents() {
    state.filterBar.find("select, input").on("change", updateFilters);
    state.filterBar.find(".search-filters__clear").on("click", clearFilters);
  }

  async function loadDoctypes() {
    try {
      const { message } = await frappe.call({
        method: "frappe.desk.search.get_names_for_mentions",
        freeze: false,
      });
      const select = state.filterBar.find(".search-filter--doctype select");
      (message || []).forEach((dt) =>
        select.append(`<option value="${dt}">${dt}</option>`),
      );
    } catch (err) {
      console.error("[Search Filters] DocTypes load error:", err);
    }
  }

  function updateFilters() {
    state.filters.doctype =
      state.filterBar.find(".search-filter--doctype select").val() || null;
    state.filters.owner =
      state.filterBar.find(".search-filter--owner input").val().trim() || null;
    state.filters.date_from =
      state.filterBar.find(".search-filter__date-from").val() || null;
    state.filters.date_to =
      state.filterBar.find(".search-filter__date-to").val() || null;
  }

  function clearFilters() {
    state.filterBar.find("select").val("");
    state.filterBar.find("input").val("");
    state.filters = {
      doctype: null,
      owner: null,
      date_from: null,
      date_to: null,
    };
    updateFilters();
  }

  function hookIntoAwesomebar() {
    const searchUtils = frappe.search?.utils;
    if (!searchUtils?.search || state.originalSearch) return;

    state.originalSearch = searchUtils.search.bind(searchUtils);

    searchUtils.search = function (query, doctype, ...args) {
      if (
        state.filters.doctype ||
        state.filters.owner ||
        state.filters.date_from ||
        state.filters.date_to
      ) {
        return customSearch(query).catch(() =>
          state.originalSearch.call(searchUtils, query, doctype, ...args),
        );
      }
      return state.originalSearch.call(searchUtils, query, doctype, ...args);
    };
  }

  async function customSearch(query) {
    try {
      const { message } = await frappe.call({
        method: "desk_navbar_extended.api.search_filters.search_with_filters",
        args: {
          query,
          doctype: state.filters.doctype,
          owner: state.filters.owner,
          date_from: state.filters.date_from,
          date_to: state.filters.date_to,
          limit: 20,
        },
        freeze: false,
      });
      return message?.results || [];
    } catch (err) {
      console.error("[Search Filters] Search error:", err);
      return [];
    }
  }

  function applyFilters(search) {
    if (!state.filterBar) return;
    const filters = search.filters || {};

    state.filterBar
      .find(".search-filter--doctype select")
      .val(search.doctype_filter || "");
    state.filterBar
      .find(".search-filter--owner input")
      .val(filters.owner || "");
    state.filterBar
      .find(".search-filter__date-from")
      .val(filters.date_from || "");
    state.filterBar
      .find(".search-filter__date-to")
      .val(filters.date_to || "");

    updateFilters();
  }

  frappe.desk_navbar_extended.search_filters = { init, applyFilters };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
