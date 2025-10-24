/**
 * Command Palette - Universal command launcher (Ctrl+K/Cmd+K)
 */
(() => {
  frappe.provide("desk_navbar_extended.command_palette");

  let state = {
    isOpen: false,
    query: "",
    allResults: [],
    filteredResults: [],
    selectedIdx: 0,
    modal: null,
    input: null,
    list: null,
  };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.features?.command_palette) return;
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
            <input type="text" class="cmd-palette__input" placeholder="${__(
              "Type a command or search...",
            )}" autocomplete="off" spellcheck="false" />
            <kbd class="cmd-palette__kbd">ESC</kbd>
          </div>
          <div class="cmd-palette__body">
            <div class="cmd-palette__loading" hidden><div class="spinner-border spinner-border-sm"></div><span>${__(
              "Loading...",
            )}</span></div>
            <div class="cmd-palette__empty" hidden><p>${__(
              "No results found",
            )}</p></div>
            <div class="cmd-palette__results" role="listbox"></div>
          </div>
          <div class="cmd-palette__footer">
            <kbd>↑↓</kbd> ${__("Navigate")} <kbd>↵</kbd> ${__(
              "Select",
            )} <kbd>ESC</kbd> ${__("Close")}
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
      if (e.key === "ArrowDown") {
        e.preventDefault();
        navigate(1);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        navigate(-1);
      } else if (e.key === "Enter") {
        e.preventDefault();
        select();
      }
    });
    state.list.on("click", ".cmd-palette__item", function () {
      selectIdx($(this).data("idx"));
    });
  }

  async function toggle() {
    state.isOpen ? close() : open();
  }

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
        method:
          "desk_navbar_extended.api.command_palette.get_command_palette_sources",
        freeze: false,
      });
      state.allResults = buildResults(message);
      state.filteredResults = state.allResults;
      state.selectedIdx = 0;
      render();
    } catch (err) {
      console.error("[Command Palette] Load error:", err);
      showEmpty();
    }
  }

  function handleInput() {
    state.query = state.input.val().toLowerCase().trim();
    if (!state.query) {
      state.filteredResults = state.allResults;
      state.selectedIdx = 0;
      render();
      return;
    }
    state.filteredResults = state.allResults.filter(
      (r) =>
        (r.title || "").toLowerCase().includes(state.query) ||
        (r.description || "").toLowerCase().includes(state.query) ||
        (r.category || "").toLowerCase().includes(state.query),
    );
    state.selectedIdx = 0;
    render();
  }

  function render() {
    hideLoading();
    const items = state.filteredResults;
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
      html += `<div class="cmd-palette__category"><div class="cmd-palette__category-label">${__(
        cat,
      )}</div>`;
      catItems.forEach((item) => {
        const sel = item.idx === state.selectedIdx ? "is-selected" : "";
        html += `<div class="cmd-palette__item ${sel}" data-idx="${
          item.idx
        }" role="option" aria-selected="${item.idx === state.selectedIdx}">`;
        html += `<div class="cmd-palette__item-icon">${
          item.icon
            ? `<i class="${item.icon}"></i>`
            : item.doctype
            ? item.doctype.charAt(0)
            : "•"
        }</div>`;
        html += `<div class="cmd-palette__item-content"><div class="cmd-palette__item-title">${frappe.utils.escape_html(
          item.title || "",
        )}</div>`;
        if (item.description)
          html += `<div class="cmd-palette__item-desc">${frappe.utils.escape_html(
            item.description,
          )}</div>`;
        html += `</div></div>`;
      });
      html += `</div>`;
    });
    state.list.html(html);
  }

  function navigate(dir) {
    const max = state.filteredResults.length - 1;
    state.selectedIdx = Math.max(0, Math.min(max, state.selectedIdx + dir));
    updateSelection();
  }

  function updateSelection() {
    state.list.find(".cmd-palette__item").each((idx, el) => {
      const $el = $(el);
      const itemIdx = parseInt($el.data("idx"));
      $el
        .toggleClass("is-selected", itemIdx === state.selectedIdx)
        .attr("aria-selected", itemIdx === state.selectedIdx);
    });
    scrollToSelected();
  }

  function scrollToSelected() {
    const $sel = state.list.find(".is-selected");
    if ($sel.length)
      $sel[0].scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  function select() {
    selectIdx(state.selectedIdx);
  }

  function selectIdx(idx) {
    const result = state.filteredResults[idx];
    if (!result) return;
    close();
    if (result.route) frappe.set_route(result.route);
    else if (result.type === "saved_search" && result.data) {
      frappe.desk_navbar_extended.saved_searches?.applySearch(result.data.name);
    } else if (result.doctype && result.name)
      frappe.set_route("Form", result.doctype, result.name);
    else if (result.doctype) frappe.set_route("List", result.doctype);
  }

  function buildResults(message) {
    if (!message || typeof message !== "object") return [];
    const mapping = {
      doctypes: __("Doctypes"),
      saved_searches: __("Saved Searches"),
      pins: __("Pins"),
      recent: __("Recent"),
      quick_create: __("Quick Create"),
      help: __("Help"),
    };

    const results = [];
    Object.entries(message).forEach(([key, items]) => {
      if (!Array.isArray(items)) return;
      const category = mapping[key] || toTitle(key);
      items.forEach((item) => {
        results.push({
          ...item,
          category,
          title: item.title || item.label || item.value || "",
          description: item.description,
          doctype: item.doctype || (item.type === "doctype" ? item.value : item.doctype),
          name:
            item.name ||
            (item.type === "saved_search" ? item.value : item.name) ||
            item.docname,
          icon: item.icon || item.icon_class || null,
          route: item.route || null,
        });
      });
    });

    return results;
  }

  function toTitle(value) {
    return (value || "")
      .replace(/[_\-]+/g, " ")
      .split(" ")
      .filter(Boolean)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ") || "Other";
  }

  function showLoading() {
    state.modal.find(".cmd-palette__loading").removeAttr("hidden");
    state.list.hide();
  }
  function hideLoading() {
    state.modal.find(".cmd-palette__loading").attr("hidden", "");
    state.list.show();
  }
  function showEmpty() {
    state.modal.find(".cmd-palette__empty").removeAttr("hidden");
    state.list.hide();
  }
  function hideEmpty() {
    state.modal.find(".cmd-palette__empty").attr("hidden", "");
    state.list.show();
  }

  frappe.desk_navbar_extended.command_palette = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
