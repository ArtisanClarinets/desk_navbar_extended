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
    if (!frappe.desk_navbar_extended?.settings?.features?.smart_filters) return;
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
    // Keep select & date inputs using change
    state.filterBar
      .find(".search-filter--doctype select, .search-filter__date-from, .search-filter__date-to")
      .on("change", updateFilters);

    // Owner input: wire a debounced mention-style source and accessible suggestion list
    const ownerInput = state.filterBar.find(".search-filter--owner input");
    const ownerSource = get_mention_source();

    // Create suggestion box container
    const suggestionBox = $("<div class='sfe-suggestion-box' role='listbox' aria-hidden='true'></div>");
    suggestionBox.css({ position: "absolute", zIndex: 2000, display: "none" });
    $(document.body).append(suggestionBox);

    // renderList implementation expected by get_mention_source
    function renderOwnerList(items, search_term) {
      suggestionBox.empty();
      if (!items || !items.length) {
        suggestionBox.hide().attr("aria-hidden", "true");
        return;
      }
      items.forEach((it, idx) => {
        const label = it.label || it.value || (typeof it === "string" ? it : "");
        const el = $(`<div role='option' data-idx='${idx}' class='sfe-suggestion-item'>${frappe.utils.escape_html(label)}</div>`);
        el.on("mousedown", function (ev) {
          // mousedown to avoid losing focus before click
          ev.preventDefault();
          ownerInput.val(label).trigger("change");
          closeSuggestions();
        });
        suggestionBox.append(el);
      });
      positionSuggestionBox();
      suggestionBox.show().attr("aria-hidden", "false");
      activeIndex = -1;
    }

    function positionSuggestionBox() {
      const off = ownerInput.offset();
      suggestionBox.css({ top: off.top + ownerInput.outerHeight(), left: off.left, minWidth: ownerInput.outerWidth() });
    }

    let activeIndex = -1;
    function highlight(index) {
      suggestionBox.children().removeClass("sfe-active");
      if (index >= 0) {
        const child = suggestionBox.children().eq(index);
        child.addClass("sfe-active");
        activeIndex = index;
      } else {
        activeIndex = -1;
      }
    }

    function closeSuggestions() {
      suggestionBox.hide().attr("aria-hidden", "true");
      highlight(-1);
    }

    ownerInput.on("input", function () {
      const q = $(this).val().trim();
      // call ownerSource; it will call renderOwnerList when ready
      ownerSource(q, renderOwnerList);
      updateFilters();
    });

    ownerInput.on("focus", function () {
      // reposition when focused
      positionSuggestionBox();
      const q = $(this).val().trim();
      ownerSource(q, renderOwnerList);
    });

    ownerInput.on("keydown", function (e) {
      const items = suggestionBox.children();
      if (!items.length || suggestionBox.is(":hidden")) return;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        highlight((activeIndex + 1) % items.length);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        highlight((activeIndex - 1 + items.length) % items.length);
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (activeIndex >= 0) {
          const sel = items.eq(activeIndex);
          sel.trigger("mousedown");
        }
      } else if (e.key === "Escape") {
        e.preventDefault();
        closeSuggestions();
      }
    });

    // Close suggestions on outside click
    $(document).on("click.sfe", function (ev) {
      if (!$(ev.target).closest(suggestionBox).length && !$(ev.target).is(ownerInput)) {
        closeSuggestions();
      }
    });

    // Clear button
    state.filterBar.find(".search-filters__clear").on("click", function () {
      clearFilters();
      closeSuggestions();
    });
  }

  async function loadDoctypes() {
    try {
      // Use xcall with explicit search_term to match Frappe v15 pattern and avoid
      // TypeError when server expects a search_term parameter.
      const method = "frappe.desk.search.get_names_for_mentions";
      const values = await frappe.xcall(method, { search_term: "" });
      const select = state.filterBar.find(".search-filter--doctype select");
      (values || []).forEach((dt) => select.append(`<option value="${dt}">${dt}</option>`));
    } catch (err) {
      console.error("[Search Filters] DocTypes load error:", err);
    }
  }

  // Provide a mention-style source function similar to Frappe v15's
  // `get_mention_options()` so any autocomplete or mention widgets can call it
  // safely and consistently.
  function get_mention_source(mention_search_method) {
    const method = mention_search_method || "frappe.desk.search.get_names_for_mentions";
    return frappe.utils.debounce(async function (search_term, renderList) {
      try {
        const values = await frappe.xcall(method, { search_term });
        // If server returns simple strings, normalize to objects expected by renderList
        const normalized = (values || []).map((v) => (typeof v === "string" ? { value: v } : v));
        // renderList expects (items, search_term)
        renderList(normalized, search_term);
      } catch (e) {
        // Don't surface a hard error to the caller; pass empty list
        renderList([], search_term);
      }
    }, 300);
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
    state.filterBar.find(".search-filter__date-to").val(filters.date_to || "");

    updateFilters();
  }

  frappe.desk_navbar_extended.search_filters = { init, applyFilters };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
