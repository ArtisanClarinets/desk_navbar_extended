/**
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
            <input type="text" class="form-control" placeholder="${__(
              "Search help articles...",
            )}" />
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
    state.modal
      .find(".help-search__backdrop, .help-search__close")
      .on("click", close);
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
      renderResults(Array.isArray(message) ? message : []);
    } catch (err) {
      console.error("[Help Search] Search error:", err);
    }
  }

  function renderResults(items) {
    if (!items.length) {
      state.results.html(`<div class="help-empty">${__("No results found")}</div>`);
      return;
    }

    const grouped = items.reduce((acc, item) => {
      const type = item.type || "other";
      acc[type] = acc[type] || [];
      acc[type].push(item);
      return acc;
    }, {});

    const labels = {
      help_article: __("Help Articles"),
      external_doc: __("Documentation"),
      quick_link: __("Links"),
      other: __("Suggestions"),
    };

    let html = "";
    Object.entries(grouped).forEach(([type, entries]) => {
      html += `<div class="help-category"><h6>${labels[type] || labels.other}</h6>`;
      entries.forEach((entry) => {
        const isExternal = Boolean(entry.external);
        const href = entry.route || entry.url || "#";
        const icon = entry.icon || (isExternal ? "fa fa-external-link" : "fa fa-book");
        const attrs = isExternal ? " target=\"_blank\" rel=\"noopener\"" : "";
        html += `<a class="help-result" href="${href}"${attrs}>`;
        html += `<i class="${icon}"></i> ${frappe.utils.escape_html(entry.title || "")}`;
        if (entry.description)
          html += `<div class="help-result__desc text-muted">${frappe.utils.escape_html(
            entry.description,
          )}</div>`;
        html += `</a>`;
      });
      html += `</div>`;
    });

    state.results.html(html);
  }

  frappe.desk_navbar_extended.help_search = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
