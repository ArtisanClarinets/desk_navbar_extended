/**
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
      const { message } = await frappe.call({
        method: "desk_navbar_extended.api.history.get_recent_activity",
        args: { limit: 20 },
        freeze: false,
      });
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
    state.groups.forEach((group) => {
      html += `<div class="history-group">`;
      html += `<div class="history-group__header"><i class="${
        group.icon || "fa fa-file"
      }"></i> ${__(group.doctype)} <span class="badge">${
        group.count
      }</span></div>`;
      html += `<div class="history-group__items">`;
      group.items.forEach((item) => {
        html += `<a class="dropdown-item history-item" href="${item.route}">`;
        html += `<span class="history-item__name">${frappe.utils.escape_html(
          item.doc_name,
        )}</span>`;
        html += `<span class="history-item__time text-muted">${comment_when(
          item.modified,
        )}</span>`;
        html += `</a>`;
      });
      html += `</div></div>`;
    });
    state.menu.html(html);
  }

  function showLoading() {
    $(".history-menu__loading").show();
    state.menu.hide();
  }
  function hideLoading() {
    $(".history-menu__loading").hide();
    state.menu.show();
  }

  frappe.desk_navbar_extended.history = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
