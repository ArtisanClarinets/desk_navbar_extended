#!/usr/bin/env python3
"""
Phase 2 Frontend Generator
Generates all production-ready frontend modules for desk_navbar_extended v2.0
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
JS_DIR = BASE_DIR / "desk_navbar_extended" / "public" / "js"
CSS_DIR = BASE_DIR / "desk_navbar_extended" / "public" / "css"

JS_DIR.mkdir(parents=True, exist_ok=True)
CSS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# COMMAND PALETTE
# ============================================================================
COMMAND_PALETTE = """/**
 * Command Palette - Universal command launcher (Ctrl+K/Cmd+K)
 */
(() => {
  frappe.provide("desk_navbar_extended.command_palette");

  let state = { isOpen: false, query: "", results: [], selectedIdx: 0, modal: null, input: null, list: null };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.enable_command_palette) return;
    setupKeyboard();
    buildModal();
    console.log("[Command Palette] Ready");
  }

  function setupKeyboard() {
    $(document).on("keydown.cmdpal", (e) => {
      const isMac = navigator.platform.toUpperCase().includes("MAC");
      if ((isMac ? e.metaKey : e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        toggle();
      }
      if (e.key === "Escape" && state.isOpen) {
        e.preventDefault();
        close();
      }
    });
  }

  function buildModal() {
    const html = `
      <div class="cmd-palette" role="dialog" aria-modal="true" hidden>
        <div class="cmd-palette__backdrop"></div>
        <div class="cmd-palette__modal">
          <div class="cmd-palette__header">
            <svg class="cmd-palette__icon" width="20" height="20" fill="none"><circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="1.5"/><path d="M15 15l4 4" stroke="currentColor" stroke-width="1.5"/></svg>
            <input type="text" class="cmd-palette__input" placeholder="${__("Type a command or search...")}" autocomplete="off" spellcheck="false" />
            <kbd class="cmd-palette__kbd">ESC</kbd>
          </div>
          <div class="cmd-palette__body">
            <div class="cmd-palette__loading" hidden><div class="spinner-border spinner-border-sm"></div><span>${__("Loading...")}</span></div>
            <div class="cmd-palette__empty" hidden><p>${__("No results found")}</p></div>
            <div class="cmd-palette__results" role="listbox"></div>
          </div>
          <div class="cmd-palette__footer">
            <kbd>↑↓</kbd> ${__("Navigate")} <kbd>↵</kbd> ${__("Select")} <kbd>ESC</kbd> ${__("Close")}
          </div>
        </div>
      </div>`;
    $("body").append(html);
    state.modal = $(".cmd-palette");
    state.input = state.modal.find(".cmd-palette__input");
    state.list = state.modal.find(".cmd-palette__results");
    bindEvents();
  }

  function bindEvents() {
    state.modal.find(".cmd-palette__backdrop").on("click", close);
    state.input.on("input", handleInput);
    state.input.on("keydown", (e) => {
      if (e.key === "ArrowDown") { e.preventDefault(); navigate(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); navigate(-1); }
      else if (e.key === "Enter") { e.preventDefault(); select(); }
    });
    state.list.on("click", ".cmd-palette__item", function() { selectIdx($(this).data("idx")); });
  }

  async function toggle() { state.isOpen ? close() : open(); }

  async function open() {
    state.isOpen = true;
    state.modal.removeAttr("hidden");
    state.input.val("").focus();
    state.query = "";
    state.selectedIdx = 0;
    $("body").css("overflow", "hidden");
    await loadCommands();
  }

  function close() {
    state.isOpen = false;
    state.modal.attr("hidden", "");
    $("body").css("overflow", "");
  }

  async function loadCommands() {
    showLoading();
    try {
      const { message } = await frappe.call({
        method: "desk_navbar_extended.api.command_palette.get_command_palette_sources",
        freeze: false,
      });
      state.results = message?.all_results || [];
      render(state.results);
    } catch (err) {
      console.error("[Command Palette] Load error:", err);
      showEmpty();
    }
  }

  function handleInput() {
    state.query = state.input.val().toLowerCase().trim();
    if (!state.query) {
      render(state.results);
      return;
    }
    const filtered = state.results.filter(r =>
      (r.title || "").toLowerCase().includes(state.query) ||
      (r.description || "").toLowerCase().includes(state.query) ||
      (r.category || "").toLowerCase().includes(state.query)
    );
    state.selectedIdx = 0;
    render(filtered);
  }

  function render(items) {
    hideLoading();
    if (!items || items.length === 0) {
      showEmpty();
      return;
    }
    hideEmpty();
    const grouped = items.reduce((acc, item, idx) => {
      const cat = item.category || "Other";
      if (!acc[cat]) acc[cat] = [];
      acc[cat].push({ ...item, idx });
      return acc;
    }, {});
    let html = "";
    Object.entries(grouped).forEach(([cat, catItems]) => {
      html += `<div class="cmd-palette__category"><div class="cmd-palette__category-label">${__(cat)}</div>`;
      catItems.forEach(item => {
        const sel = item.idx === state.selectedIdx ? "is-selected" : "";
        html += `<div class="cmd-palette__item ${sel}" data-idx="${item.idx}" role="option" aria-selected="${item.idx === state.selectedIdx}">`;
        html += `<div class="cmd-palette__item-icon">${item.icon_class ? `<i class="${item.icon_class}"></i>` : (item.doctype ? item.doctype.charAt(0) : "•")}</div>`;
        html += `<div class="cmd-palette__item-content"><div class="cmd-palette__item-title">${frappe.utils.escape_html(item.title || "")}</div>`;
        if (item.description) html += `<div class="cmd-palette__item-desc">${frappe.utils.escape_html(item.description)}</div>`;
        html += `</div></div>`;
      });
      html += `</div>`;
    });
    state.list.html(html);
  }

  function navigate(dir) {
    const max = state.results.length - 1;
    state.selectedIdx = Math.max(0, Math.min(max, state.selectedIdx + dir));
    updateSelection();
  }

  function updateSelection() {
    state.list.find(".cmd-palette__item").each((idx, el) => {
      const $el = $(el);
      const itemIdx = parseInt($el.data("idx"));
      $el.toggleClass("is-selected", itemIdx === state.selectedIdx).attr("aria-selected", itemIdx === state.selectedIdx);
    });
    scrollToSelected();
  }

  function scrollToSelected() {
    const $sel = state.list.find(".is-selected");
    if ($sel.length) $sel[0].scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  function select() { selectIdx(state.selectedIdx); }

  function selectIdx(idx) {
    const result = state.results[idx];
    if (!result) return;
    close();
    if (result.route) frappe.set_route(result.route);
    else if (result.doctype && result.name) frappe.set_route("Form", result.doctype, result.name);
    else if (result.doctype) frappe.set_route("List", result.doctype);
    else if (result.action && typeof result.action === "function") result.action();
  }

  function showLoading() { state.modal.find(".cmd-palette__loading").removeAttr("hidden"); state.list.hide(); }
  function hideLoading() { state.modal.find(".cmd-palette__loading").attr("hidden", ""); state.list.show(); }
  function showEmpty() { state.modal.find(".cmd-palette__empty").removeAttr("hidden"); state.list.hide(); }
  function hideEmpty() { state.modal.find(".cmd-palette__empty").attr("hidden", ""); state.list.show(); }

  frappe.desk_navbar_extended.command_palette = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
"""

# ============================================================================
# SEARCH FILTERS
# ============================================================================
SEARCH_FILTERS = """/**
 * Smart Search Filters - Enhanced awesomebar search
 */
(() => {
  frappe.provide("desk_navbar_extended.search_filters");

  let state = { filters: { doctype: null, owner: null, date_from: null, date_to: null }, filterBar: null };

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
            <input type="text" class="form-control form-control-sm" placeholder="${__("Any user")}" />
          </div>
          <div class="search-filter search-filter--dates">
            <label>${__("From:")}</label>
            <input type="date" class="form-control form-control-sm search-filter__date-from" />
            <label>${__("To:")}</label>
            <input type="date" class="form-control form-control-sm search-filter__date-to" />
          </div>
          <button class="btn btn-sm btn-secondary search-filters__clear">${__("Clear")}</button>
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
      const { message } = await frappe.call({ method: "frappe.desk.search.get_names_for_mentions", freeze: false });
      const select = state.filterBar.find(".search-filter--doctype select");
      (message || []).forEach(dt => select.append(`<option value="${dt}">${dt}</option>`));
    } catch (err) {
      console.error("[Search Filters] DocTypes load error:", err);
    }
  }

  function updateFilters() {
    state.filters.doctype = state.filterBar.find(".search-filter--doctype select").val() || null;
    state.filters.owner = state.filterBar.find(".search-filter--owner input").val().trim() || null;
    state.filters.date_from = state.filterBar.find(".search-filter__date-from").val() || null;
    state.filters.date_to = state.filterBar.find(".search-filter__date-to").val() || null;
  }

  function clearFilters() {
    state.filterBar.find("select").val("");
    state.filterBar.find("input").val("");
    state.filters = { doctype: null, owner: null, date_from: null, date_to: null };
  }

  function hookIntoAwesomebar() {
    const originalSearch = frappe.search.search;
    frappe.search.search = function(query, doctype, ...args) {
      if (state.filters.doctype || state.filters.owner || state.filters.date_from || state.filters.date_to) {
        return customSearch(query);
      }
      return originalSearch.call(this, query, doctype, ...args);
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
      return message || [];
    } catch (err) {
      console.error("[Search Filters] Search error:", err);
      return [];
    }
  }

  frappe.desk_navbar_extended.search_filters = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
"""

# ============================================================================
# SAVED SEARCHES
# ============================================================================
SAVED_SEARCHES = """/**
 * Saved Searches - Save and reuse search queries
 */
(() => {
  frappe.provide("desk_navbar_extended.saved_searches");

  let state = { searches: [], menu: null, dropdown: null };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.enable_saved_searches) return;
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
            <div class="saved-searches__empty" hidden>${__("No saved searches")}</div>
            <div class="saved-searches__list"></div>
            <div class="dropdown-divider"></div>
            <a class="dropdown-item saved-searches__new" href="#"><i class="fa fa-plus"></i> ${__("Save Current Search")}</a>
          </div>
        </div>
      </div>`;
    $("#navbar-search").before(html);
    state.menu = $(".saved-searches");
    state.dropdown = state.menu.find(".saved-searches__menu");
    bindEvents();
  }

  function bindEvents() {
    state.menu.find(".saved-searches__new").on("click", (e) => { e.preventDefault(); saveCurrentSearch(); });
    state.dropdown.on("click", ".saved-search-item", function() { applySearch($(this).data("id")); });
    state.dropdown.on("click", ".saved-search-item__delete", function(e) { e.stopPropagation(); deleteSearch($(this).closest(".saved-search-item").data("id")); });
  }

  async function loadSearches() {
    showLoading();
    try {
      const { message } = await frappe.call({ method: "desk_navbar_extended.api.saved_searches.list_saved_searches", freeze: false });
      state.searches = message || [];
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
    state.searches.forEach(s => {
      html += `<a class="dropdown-item saved-search-item" data-id="${s.name}" href="#">`;
      html += `<span class="saved-search-item__title">${frappe.utils.escape_html(s.search_name)}</span>`;
      html += `<button class="btn btn-xs btn-link saved-search-item__delete" title="${__("Delete")}"><i class="fa fa-trash"></i></button>`;
      html += `</a>`;
    });
    state.dropdown.find(".saved-searches__list").html(html);
  }

  async function saveCurrentSearch() {
    const query = $("#navbar-search input").val();
    if (!query) { frappe.show_alert(__("No search query to save")); return; }
    const name = await frappe.prompt({ label: __("Search Name"), fieldtype: "Data", reqd: 1 });
    if (!name) return;
    try {
      await frappe.call({
        method: "desk_navbar_extended.api.saved_searches.create_saved_search",
        args: { search_name: name, query_text: query },
      });
      frappe.show_alert({ message: __("Search saved"), indicator: "green" });
      loadSearches();
    } catch (err) {
      console.error("[Saved Searches] Save error:", err);
      frappe.show_alert({ message: __("Failed to save search"), indicator: "red" });
    }
  }

  function applySearch(id) {
    const search = state.searches.find(s => s.name === id);
    if (search) $("#navbar-search input").val(search.query_text).trigger("input");
  }

  async function deleteSearch(id) {
    if (!confirm(__("Delete this saved search?"))) return;
    try {
      await frappe.call({ method: "desk_navbar_extended.api.saved_searches.delete_saved_search", args: { name: id } });
      frappe.show_alert({ message: __("Search deleted"), indicator: "green" });
      loadSearches();
    } catch (err) {
      console.error("[Saved Searches] Delete error:", err);
      frappe.show_alert({ message: __("Failed to delete"), indicator: "red" });
    }
  }

  function showLoading() { state.dropdown.find(".saved-searches__loading").show(); state.dropdown.find(".saved-searches__list").hide(); }
  function hideLoading() { state.dropdown.find(".saved-searches__loading").hide(); state.dropdown.find(".saved-searches__list").show(); }
  function showEmpty() { state.dropdown.find(".saved-searches__empty").removeAttr("hidden"); }
  function hideEmpty() { state.dropdown.find(".saved-searches__empty").attr("hidden", ""); }

  frappe.desk_navbar_extended.saved_searches = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
"""

# ============================================================================
# PINS
# ============================================================================
PINS = """/**
 * Pins - Quick access bar for frequently used items
 */
(() => {
  frappe.provide("desk_navbar_extended.pins");

  let state = { pins: [], bar: null };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.enable_pins) return;
    buildPinBar();
    loadPins();
    console.log("[Pins] Ready");
  }

  function buildPinBar() {
    const html = `
      <div class="pin-bar">
        <div class="pin-bar__items"></div>
        <button class="btn btn-xs btn-default pin-bar__add" title="${__("Add Pin")}">
          <i class="fa fa-plus"></i>
        </button>
      </div>`;
    $("#navbar-breadcrumbs").after(html);
    state.bar = $(".pin-bar");
    state.bar.find(".pin-bar__add").on("click", addPin);
  }

  async function loadPins() {
    try {
      const { message } = await frappe.call({ method: "desk_navbar_extended.api.pins.list_pins", freeze: false });
      state.pins = message || [];
      render();
    } catch (err) {
      console.error("[Pins] Load error:", err);
    }
  }

  function render() {
    let html = "";
    state.pins.forEach(pin => {
      html += `<div class="pin-item" data-name="${pin.name}">`;
      html += `<a href="${pin.route}" class="pin-item__link">`;
      html += `<i class="${pin.icon_class || 'fa fa-star'}"></i>`;
      html += `<span>${frappe.utils.escape_html(pin.label)}</span>`;
      html += `</a>`;
      html += `<button class="pin-item__delete" title="${__("Remove")}"><i class="fa fa-times"></i></button>`;
      html += `</div>`;
    });
    state.bar.find(".pin-bar__items").html(html);
    state.bar.find(".pin-item__delete").on("click", function() { deletePin($(this).closest(".pin-item").data("name")); });
  }

  async function addPin() {
    const d = new frappe.ui.Dialog({
      title: __("Add Pin"),
      fields: [
        { label: __("Label"), fieldname: "label", fieldtype: "Data", reqd: 1 },
        { label: __("DocType"), fieldname: "doctype", fieldtype: "Link", options: "DocType", reqd: 1 },
        { label: __("Document Name"), fieldname: "doc_name", fieldtype: "Data" },
        { label: __("Icon Class"), fieldname: "icon_class", fieldtype: "Data", default: "fa fa-star" },
      ],
      primary_action_label: __("Add"),
      primary_action: async (values) => {
        try {
          await frappe.call({
            method: "desk_navbar_extended.api.pins.create_pin",
            args: values,
          });
          frappe.show_alert({ message: __("Pin added"), indicator: "green" });
          d.hide();
          loadPins();
        } catch (err) {
          console.error("[Pins] Create error:", err);
          frappe.show_alert({ message: __("Failed to add pin"), indicator: "red" });
        }
      },
    });
    d.show();
  }

  async function deletePin(name) {
    if (!confirm(__("Remove this pin?"))) return;
    try {
      await frappe.call({ method: "desk_navbar_extended.api.pins.delete_pin", args: { name } });
      frappe.show_alert({ message: __("Pin removed"), indicator: "green" });
      loadPins();
    } catch (err) {
      console.error("[Pins] Delete error:", err);
      frappe.show_alert({ message: __("Failed to remove pin"), indicator: "red" });
    }
  }

  frappe.desk_navbar_extended.pins = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
"""

# ============================================================================
# QUICK CREATE
# ============================================================================
QUICK_CREATE = """/**
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
      const { message } = await frappe.call({ method: "desk_navbar_extended.api.quick_create.get_quick_create_options", freeze: false });
      state.options = message || [];
      render();
    } catch (err) {
      console.error("[Quick Create] Load error:", err);
    }
  }

  function render() {
    let html = "";
    state.options.forEach(opt => {
      html += `<a class="dropdown-item quick-create__item" data-doctype="${opt.doctype}" href="#">`;
      html += `<i class="${opt.icon || 'fa fa-file'}"></i> ${__(opt.label || opt.doctype)}`;
      html += `</a>`;
    });
    state.menu.html(html);
    state.menu.find(".quick-create__item").on("click", function(e) {
      e.preventDefault();
      frappe.new_doc($(this).data("doctype"));
    });
  }

  frappe.desk_navbar_extended.quick_create = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
"""

# ============================================================================
# HISTORY
# ============================================================================
HISTORY = """/**
 * History - Grouped recent activity
 */
(() => {
  frappe.provide("desk_navbar_extended.history");

  let state = { groups: [], menu: null };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.enable_grouped_history) return;
    buildMenu();
    loadHistory();
    console.log("[History] Ready");
  }

  function buildMenu() {
    const html = `
      <div class="history-menu">
        <div class="dropdown">
          <button class="btn btn-sm btn-default dropdown-toggle" data-toggle="dropdown">
            <i class="fa fa-clock-o"></i> ${__("History")}
          </button>
          <div class="dropdown-menu dropdown-menu-right history-menu__dropdown">
            <div class="history-menu__loading">${__("Loading...")}</div>
            <div class="history-menu__groups"></div>
          </div>
        </div>
      </div>`;
    $(".navbar-right").prepend(html);
    state.menu = $(".history-menu__groups");
  }

  async function loadHistory() {
    showLoading();
    try {
      const { message } = await frappe.call({ method: "desk_navbar_extended.api.history.get_recent_activity", args: { limit: 20 }, freeze: false });
      state.groups = message?.by_doctype || [];
      render();
    } catch (err) {
      console.error("[History] Load error:", err);
      hideLoading();
    }
  }

  function render() {
    hideLoading();
    let html = "";
    state.groups.forEach(group => {
      html += `<div class="history-group">`;
      html += `<div class="history-group__header"><i class="${group.icon || 'fa fa-file'}"></i> ${__(group.doctype)} <span class="badge">${group.count}</span></div>`;
      html += `<div class="history-group__items">`;
      group.items.forEach(item => {
        html += `<a class="dropdown-item history-item" href="${item.route}">`;
        html += `<span class="history-item__name">${frappe.utils.escape_html(item.doc_name)}</span>`;
        html += `<span class="history-item__time text-muted">${comment_when(item.modified)}</span>`;
        html += `</a>`;
      });
      html += `</div></div>`;
    });
    state.menu.html(html);
  }

  function showLoading() { $(".history-menu__loading").show(); state.menu.hide(); }
  function hideLoading() { $(".history-menu__loading").hide(); state.menu.show(); }

  frappe.desk_navbar_extended.history = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
"""

# ============================================================================
# NOTIFICATIONS CENTER
# ============================================================================
NOTIFICATIONS = """/**
 * Notifications Center - Enhanced notifications with filtering
 */
(() => {
  frappe.provide("desk_navbar_extended.notifications_center");

  let state = { notifications: [], panel: null, badge: null };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.enable_notifications_center) return;
    buildPanel();
    loadNotifications();
    console.log("[Notifications] Ready");
  }

  function buildPanel() {
    const html = `
      <div class="notifications-center">
        <div class="dropdown">
          <button class="btn btn-sm btn-default dropdown-toggle" data-toggle="dropdown">
            <i class="fa fa-bell"></i>
            <span class="badge badge-danger notifications-center__badge" hidden>0</span>
          </button>
          <div class="dropdown-menu dropdown-menu-right notifications-center__panel">
            <div class="notifications-center__header">
              <h6>${__("Notifications")}</h6>
              <button class="btn btn-xs btn-link notifications-center__mark-all">${__("Mark all read")}</button>
            </div>
            <div class="notifications-center__loading">${__("Loading...")}</div>
            <div class="notifications-center__list"></div>
          </div>
        </div>
      </div>`;
    $(".navbar-right").prepend(html);
    state.panel = $(".notifications-center__panel");
    state.badge = $(".notifications-center__badge");
    state.panel.find(".notifications-center__mark-all").on("click", markAllRead);
  }

  async function loadNotifications() {
    showLoading();
    try {
      const { message } = await frappe.call({ method: "desk_navbar_extended.api.notifications.get_notifications", freeze: false });
      state.notifications = message || [];
      render();
      updateBadge();
    } catch (err) {
      console.error("[Notifications] Load error:", err);
      hideLoading();
    }
  }

  function render() {
    hideLoading();
    let html = "";
    if (!state.notifications.length) {
      html = `<div class="notifications-center__empty">${__("No notifications")}</div>`;
    } else {
      state.notifications.forEach(notif => {
        const unread = notif.read ? "" : "is-unread";
        html += `<div class="notification-item ${unread}" data-name="${notif.name}">`;
        html += `<div class="notification-item__content">`;
        html += `<div class="notification-item__subject">${frappe.utils.escape_html(notif.subject)}</div>`;
        html += `<div class="notification-item__time text-muted">${comment_when(notif.creation)}</div>`;
        html += `</div>`;
        if (!notif.read) html += `<button class="btn btn-xs btn-link notification-item__mark">${__("Mark read")}</button>`;
        html += `</div>`;
      });
    }
    state.panel.find(".notifications-center__list").html(html);
    state.panel.find(".notification-item__mark").on("click", function() { markRead($(this).closest(".notification-item").data("name")); });
  }

  function updateBadge() {
    const unread = state.notifications.filter(n => !n.read).length;
    if (unread > 0) {
      state.badge.text(unread).removeAttr("hidden");
    } else {
      state.badge.attr("hidden", "");
    }
  }

  async function markRead(name) {
    try {
      await frappe.call({ method: "desk_navbar_extended.api.notifications.mark_as_read", args: { name }, freeze: false });
      loadNotifications();
    } catch (err) {
      console.error("[Notifications] Mark read error:", err);
    }
  }

  async function markAllRead() {
    try {
      await frappe.call({ method: "desk_navbar_extended.api.notifications.mark_all_as_read", freeze: false });
      loadNotifications();
    } catch (err) {
      console.error("[Notifications] Mark all error:", err);
    }
  }

  function showLoading() { state.panel.find(".notifications-center__loading").show(); state.panel.find(".notifications-center__list").hide(); }
  function hideLoading() { state.panel.find(".notifications-center__loading").hide(); state.panel.find(".notifications-center__list").show(); }

  frappe.desk_navbar_extended.notifications_center = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
"""

# ============================================================================
# KPI WIDGETS
# ============================================================================
KPI_WIDGETS = """/**
 * KPI Widgets - Role-based dashboard widgets
 */
(() => {
  frappe.provide("desk_navbar_extended.kpi_widgets");

  let state = { kpis: [], container: null, refreshInterval: null };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.enable_kpi_widgets) return;
    buildContainer();
    loadKPIs();
    startAutoRefresh();
    console.log("[KPI Widgets] Ready");
  }

  function buildContainer() {
    const html = `<div class="kpi-widgets"></div>`;
    $("#navbar-breadcrumbs").before(html);
    state.container = $(".kpi-widgets");
  }

  async function loadKPIs() {
    try {
      const { message } = await frappe.call({ method: "desk_navbar_extended.api.kpi.get_kpi_data", freeze: false });
      state.kpis = message || [];
      render();
    } catch (err) {
      console.error("[KPI Widgets] Load error:", err);
    }
  }

  function render() {
    let html = "";
    state.kpis.forEach(kpi => {
      html += `<div class="kpi-widget" data-route="${kpi.route || ''}">`;
      html += `<div class="kpi-widget__icon"><i class="${kpi.icon || 'fa fa-bar-chart'}"></i></div>`;
      html += `<div class="kpi-widget__content">`;
      html += `<div class="kpi-widget__value">${kpi.value}</div>`;
      html += `<div class="kpi-widget__label">${__(kpi.label)}</div>`;
      html += `</div></div>`;
    });
    state.container.html(html);
    state.container.find(".kpi-widget").on("click", function() {
      const route = $(this).data("route");
      if (route) frappe.set_route(route);
    });
  }

  function startAutoRefresh() {
    const interval = frappe.desk_navbar_extended?.settings?.kpi_refresh_interval || 300;
    state.refreshInterval = setInterval(loadKPIs, interval * 1000);
  }

  frappe.desk_navbar_extended.kpi_widgets = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
"""

# ============================================================================
# HELP SEARCH
# ============================================================================
HELP_SEARCH = """/**
 * Help Search - Context-aware help documentation
 */
(() => {
  frappe.provide("desk_navbar_extended.help_search");

  let state = { modal: null, input: null, results: null };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.enable_help_search) return;
    buildModal();
    setupKeyboard();
    console.log("[Help Search] Ready");
  }

  function setupKeyboard() {
    $(document).on("keydown.helpsearch", (e) => {
      if (e.shiftKey && e.key === "?") {
        e.preventDefault();
        open();
      }
    });
  }

  function buildModal() {
    const html = `
      <div class="help-search-modal" hidden>
        <div class="help-search__backdrop"></div>
        <div class="help-search__container">
          <div class="help-search__header">
            <h5>${__("Help & Documentation")}</h5>
            <button class="btn btn-sm btn-link help-search__close">&times;</button>
          </div>
          <div class="help-search__search">
            <input type="text" class="form-control" placeholder="${__("Search help articles...")}" />
          </div>
          <div class="help-search__results"></div>
        </div>
      </div>`;
    $("body").append(html);
    state.modal = $(".help-search-modal");
    state.input = state.modal.find(".help-search__search input");
    state.results = state.modal.find(".help-search__results");
    bindEvents();
  }

  function bindEvents() {
    state.modal.find(".help-search__backdrop, .help-search__close").on("click", close);
    state.input.on("input", frappe.utils.debounce(search, 300));
  }

  function open() {
    state.modal.removeAttr("hidden");
    state.input.val("").focus();
    $("body").css("overflow", "hidden");
  }

  function close() {
    state.modal.attr("hidden", "");
    $("body").css("overflow", "");
  }

  async function search() {
    const query = state.input.val().trim();
    if (!query) {
      state.results.html("");
      return;
    }
    try {
      const { message } = await frappe.call({
        method: "desk_navbar_extended.api.help.search_help",
        args: { query, limit: 10 },
        freeze: false,
      });
      renderResults(message || {});
    } catch (err) {
      console.error("[Help Search] Search error:", err);
    }
  }

  function renderResults(data) {
    let html = "";
    if (data.articles && data.articles.length) {
      html += `<div class="help-category"><h6>${__("Help Articles")}</h6>`;
      data.articles.forEach(art => {
        html += `<a class="help-result" href="${art.route}">`;
        html += `<i class="fa fa-book"></i> ${frappe.utils.escape_html(art.title)}`;
        html += `</a>`;
      });
      html += `</div>`;
    }
    if (data.external_docs && data.external_docs.length) {
      html += `<div class="help-category"><h6>${__("Documentation")}</h6>`;
      data.external_docs.forEach(doc => {
        html += `<a class="help-result" href="${doc.url}" target="_blank">`;
        html += `<i class="fa fa-external-link"></i> ${frappe.utils.escape_html(doc.title)}`;
        html += `</a>`;
      });
      html += `</div>`;
    }
    if (!html) html = `<div class="help-empty">${__("No results found")}</div>`;
    state.results.html(html);
  }

  frappe.desk_navbar_extended.help_search = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
"""

# ============================================================================
# DENSITY TOGGLE
# ============================================================================
DENSITY_TOGGLE = """/**
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
      <button class="btn btn-sm btn-default density-toggle" title="${__("Toggle density")}">
        <i class="fa fa-compress"></i>
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
    $("body").removeClass("density-comfortable density-compact").addClass(\`density-\${state.density}\`);
  }

  function updateIcon() {
    const icon = state.density === "compact" ? "fa-expand" : "fa-compress";
    state.toggle.find("i").attr("class", \`fa \${icon}\`);
  }

  frappe.desk_navbar_extended.density_toggle = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
"""

# ============================================================================
# KEYBOARD MANAGER
# ============================================================================
KEYBOARD_MANAGER = """/**
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
    const html = Object.entries(shortcuts).map(([key, { description }]) =>
      \`<tr><td><kbd>\${key}</kbd></td><td>\${__(description)}</td></tr>\`
    ).join("");
    frappe.msgprint({
      title: __("Keyboard Shortcuts"),
      message: \`<table class="table table-bordered"><thead><tr><th>Shortcut</th><th>Action</th></tr></thead><tbody>\${html}</tbody></table>\`,
    });
  }

  frappe.desk_navbar_extended.keyboard_manager = { init, register, unregister, showHelp };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
"""

# Write all files
print("Generating Phase 2 frontend modules...")

files = {
    "command_palette.js": COMMAND_PALETTE,
    "search_filters.js": SEARCH_FILTERS,
    "saved_searches.js": SAVED_SEARCHES,
    "pins.js": PINS,
    "quick_create.js": QUICK_CREATE,
    "history.js": HISTORY,
    "notifications_center.js": NOTIFICATIONS,
    "kpi_widgets.js": KPI_WIDGETS,
    "help_search.js": HELP_SEARCH,
    "density_toggle.js": DENSITY_TOGGLE,
    "keyboard_manager.js": KEYBOARD_MANAGER,
}

for filename, content in files.items():
    filepath = JS_DIR / filename
    filepath.write_text(content)
    print(f"✓ Created {filename}")

print(f"\\nGenerated {len(files)} JavaScript modules in {JS_DIR}")


# ============================================================================
# COMPREHENSIVE CSS
# ============================================================================
CSS_CONTENT = """/**
 * Desk Navbar Extended - Comprehensive Styles
 * Apple-inspired design system with responsive behavior
 */

:root {
  --dne-primary: #2490ef;
  --dne-success: #28a745;
  --dne-danger: #dc3545;
  --dne-warning: #ffc107;
  --dne-text: #32333;
  --dne-text-muted: #8d99a6;
  --dne-border: #d1d8dd;
  --dne-bg: #ffffff;
  --dne-bg-hover: #f5f7fa;
  --dne-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  --dne-shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
  --dne-radius: 6px;
  --dne-transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

[data-theme="dark"] {
  --dne-text: #ffffff;
  --dne-text-muted: #8d99a6;
  --dne-border: #2e3338;
  --dne-bg: #1c1e21;
  --dne-bg-hover: #2a2d31;
  --dne-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  --dne-shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
}

/* ================================================================
   COMMAND PALETTE
   ================================================================ */

.cmd-palette {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10000;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
}

.cmd-palette__backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  animation: fadeIn 0.15s ease;
}

.cmd-palette__modal {
  position: relative;
  width: 90%;
  max-width: 640px;
  background: var(--dne-bg);
  border-radius: var(--dne-radius);
  box-shadow: var(--dne-shadow-lg);
  animation: slideDown 0.2s ease;
  overflow: hidden;
}

.cmd-palette__header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid var(--dne-border);
}

.cmd-palette__icon {
  color: var(--dne-text-muted);
  flex-shrink: 0;
}

.cmd-palette__input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  color: var(--dne-text);
  background: transparent;
}

.cmd-palette__input::placeholder {
  color: var(--dne-text-muted);
}

.cmd-palette__kbd {
  padding: 4px 8px;
  background: var(--dne-bg-hover);
  border: 1px solid var(--dne-border);
  border-radius: 4px;
  font-size: 11px;
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  color: var(--dne-text-muted);
}

.cmd-palette__body {
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
}

.cmd-palette__loading,
.cmd-palette__empty {
  padding: 48px 24px;
  text-align: center;
  color: var(--dne-text-muted);
}

.cmd-palette__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.cmd-palette__empty svg {
  color: var(--dne-text-muted);
  opacity: 0.3;
  margin-bottom: 12px;
}

.cmd-palette__category {
  margin-bottom: 16px;
}

.cmd-palette__category-label {
  padding: 8px 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--dne-text-muted);
}

.cmd-palette__item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: var(--dne-radius);
  cursor: pointer;
  transition: all var(--dne-transition);
}

.cmd-palette__item:hover,
.cmd-palette__item.is-selected {
  background: var(--dne-bg-hover);
}

.cmd-palette__item-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--dne-primary);
  color: white;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.cmd-palette__item-content {
  flex: 1;
  min-width: 0;
}

.cmd-palette__item-title {
  font-weight: 500;
  color: var(--dne-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cmd-palette__item-desc {
  font-size: 13px;
  color: var(--dne-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cmd-palette__footer {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  border-top: 1px solid var(--dne-border);
  font-size: 12px;
  color: var(--dne-text-muted);
}

.cmd-palette__hint {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ================================================================
   SEARCH FILTERS
   ================================================================ */

.search-filters {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--dne-bg);
  border-bottom: 1px solid var(--dne-border);
}

.search-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-filter label {
  font-size: 13px;
  font-weight: 500;
  color: var(--dne-text);
  margin: 0;
}

.search-filter select,
.search-filter input {
  width: auto;
  max-width: 200px;
}

.search-filters__clear {
  margin-left: auto;
}

/* ================================================================
   SAVED SEARCHES
   ================================================================ */

.saved-searches {
  display: inline-block;
  margin-right: 12px;
}

.saved-searches__menu {
  min-width: 280px;
}

.saved-search-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
}

.saved-search-item:hover {
  background: var(--dne-bg-hover);
}

.saved-search-item__title {
  flex: 1;
}

.saved-search-item__delete {
  opacity: 0;
  transition: opacity var(--dne-transition);
}

.saved-search-item:hover .saved-search-item__delete {
  opacity: 1;
}

/* ================================================================
   PINS
   ================================================================ */

.pin-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--dne-bg);
  border-bottom: 1px solid var(--dne-border);
}

.pin-bar__items {
  display: flex;
  gap: 8px;
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: thin;
}

.pin-item {
  display: flex;
  align-items: center;
  background: var(--dne-bg-hover);
  border-radius: var(--dne-radius);
  padding: 6px 12px;
  transition: all var(--dne-transition);
  cursor: grab;
  white-space: nowrap;
}

.pin-item:hover {
  background: var(--dne-primary);
  color: white;
}

.pin-item__link {
  display: flex;
  align-items: center;
  gap: 6px;
  color: inherit;
  text-decoration: none;
}

.pin-item__delete {
  margin-left: 8px;
  padding: 2px 6px;
  background: none;
  border: none;
  opacity: 0;
  transition: opacity var(--dne-transition);
}

.pin-item:hover .pin-item__delete {
  opacity: 1;
}

/* ================================================================
   QUICK CREATE
   ================================================================ */

.quick-create {
  display: inline-block;
  margin-right: 12px;
}

.quick-create__menu {
  min-width: 240px;
}

.quick-create__item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  transition: all var(--dne-transition);
}

.quick-create__item:hover {
  background: var(--dne-bg-hover);
}

/* ================================================================
   HISTORY
   ================================================================ */

.history-menu__dropdown {
  min-width: 320px;
  max-height: 480px;
  overflow-y: auto;
}

.history-group {
  margin-bottom: 12px;
}

.history-group__header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-weight: 600;
  font-size: 13px;
  color: var(--dne-text);
  background: var(--dne-bg-hover);
  border-radius: var(--dne-radius);
}

.history-group__header .badge {
  margin-left: auto;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px 8px 40px;
  transition: all var(--dne-transition);
}

.history-item:hover {
  background: var(--dne-bg-hover);
}

.history-item__name {
  font-weight: 500;
}

.history-item__time {
  font-size: 12px;
}

/* ================================================================
   NOTIFICATIONS CENTER
   ================================================================ */

.notifications-center__badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  font-size: 10px;
  line-height: 18px;
  border-radius: 9px;
}

.notifications-center__panel {
  min-width: 380px;
  max-height: 520px;
}

.notifications-center__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--dne-border);
}

.notifications-center__header h6 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.notifications-center__list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--dne-border);
  transition: all var(--dne-transition);
}

.notification-item:hover {
  background: var(--dne-bg-hover);
}

.notification-item.is-unread {
  background: rgba(36, 144, 239, 0.05);
  border-left: 3px solid var(--dne-primary);
}

.notification-item__content {
  flex: 1;
}

.notification-item__subject {
  font-weight: 500;
  color: var(--dne-text);
  margin-bottom: 4px;
}

.notification-item__time {
  font-size: 12px;
}

/* ================================================================
   KPI WIDGETS
   ================================================================ */

.kpi-widgets {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--dne-bg);
  border-bottom: 1px solid var(--dne-border);
  overflow-x: auto;
}

.kpi-widget {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--dne-bg-hover);
  border-radius: var(--dne-radius);
  min-width: 160px;
  cursor: pointer;
  transition: all var(--dne-transition);
}

.kpi-widget:hover {
  background: var(--dne-primary);
  color: white;
  transform: translateY(-2px);
  box-shadow: var(--dne-shadow);
}

.kpi-widget__icon {
  font-size: 32px;
  opacity: 0.8;
}

.kpi-widget__value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
}

.kpi-widget__label {
  font-size: 12px;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ================================================================
   HELP SEARCH
   ================================================================ */

.help-search-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.help-search__backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.help-search__container {
  position: relative;
  width: 100%;
  max-width: 700px;
  background: var(--dne-bg);
  border-radius: var(--dne-radius);
  box-shadow: var(--dne-shadow-lg);
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.help-search__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid var(--dne-border);
}

.help-search__header h5 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.help-search__search {
  padding: 16px 20px;
  border-bottom: 1px solid var(--dne-border);
}

.help-search__results {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.help-category {
  margin-bottom: 24px;
}

.help-category h6 {
  font-size: 14px;
  font-weight: 600;
  color: var(--dne-text-muted);
  margin-bottom: 12px;
}

.help-result {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: var(--dne-radius);
  text-decoration: none;
  color: var(--dne-text);
  transition: all var(--dne-transition);
}

.help-result:hover {
  background: var(--dne-bg-hover);
}

.help-empty {
  text-align: center;
  padding: 48px 24px;
  color: var(--dne-text-muted);
}

/* ================================================================
   DENSITY TOGGLE
   ================================================================ */

body.density-compact {
  font-size: 13px;
}

body.density-compact .navbar {
  min-height: 40px;
}

body.density-compact .btn {
  padding: 4px 8px;
  font-size: 12px;
}

body.density-compact .form-control {
  padding: 4px 8px;
  font-size: 13px;
}

body.density-compact .card {
  margin-bottom: 12px;
}

/* ================================================================
   MOBILE RESPONSIVE
   ================================================================ */

@media (max-width: 768px) {
  .cmd-palette__modal {
    width: 95%;
    max-height: 90vh;
  }

  .search-filters {
    flex-wrap: wrap;
  }

  .search-filter {
    flex: 1 1 auto;
  }

  .pin-bar__items {
    flex-wrap: nowrap;
    overflow-x: scroll;
  }

  .kpi-widgets {
    flex-wrap: nowrap;
    overflow-x: scroll;
  }

  .notifications-center__panel,
  .history-menu__dropdown {
    min-width: 100vw;
    max-width: 100vw;
    left: 0 !important;
    right: 0 !important;
    border-radius: 0;
  }

  .help-search__container {
    max-width: 100%;
    max-height: 100%;
    border-radius: 0;
  }
}

/* ================================================================
   ANIMATIONS
   ================================================================ */

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ================================================================
   ACCESSIBILITY
   ================================================================ */

.cmd-palette:focus-visible,
.help-search-modal:focus-visible {
  outline: 2px solid var(--dne-primary);
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* ================================================================
   UTILITIES
   ================================================================ */

.command-palette-open,
.help-search-open {
  overflow: hidden;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

body.command-palette-open {
  overflow: hidden;
}
"""

# Write CSS file
css_path = CSS_DIR / "desk_navbar_extended.css"
css_path.write_text(CSS_CONTENT)
print(f"\\n✓ Created desk_navbar_extended.css ({len(CSS_CONTENT)} bytes)")
print(f"\\n🎉 All Phase 2 frontend assets generated successfully!")
print(f"   - {len(files)} JavaScript modules")
print(f"   - 1 comprehensive CSS file")
print(f"\\nNext steps:")
print(f"   1. Update desk_navbar_extended.js to initialize all modules")
print(f"   2. Update hooks.py to register all assets")
print(f"   3. Run: bench build --app desk_navbar_extended")
