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
