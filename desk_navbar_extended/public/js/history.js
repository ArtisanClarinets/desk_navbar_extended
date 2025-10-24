/**
 * History - Grouped recent activity
 */
(() => {
  frappe.provide("desk_navbar_extended.history");

  let state = { groups: [], menu: null };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.features?.grouped_history) return;
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
      const groups = Array.isArray(message?.groups) ? message.groups : [];
      if (!groups.length && Array.isArray(message?.items)) {
        state.groups = buildFallbackGroups(message.items);
      } else {
        state.groups = groups;
      }
      render();
    } catch (err) {
      console.error("[History] Load error:", err);
      hideLoading();
    }
  }

  function buildFallbackGroups(items) {
    const grouped = {};
    items.forEach((item) => {
      if (!item?.doctype) return;
      if (!grouped[item.doctype]) {
        grouped[item.doctype] = {
          doctype: item.doctype,
          label: item.label || __(item.doctype),
          icon: item.icon || "fa fa-file",
          items: [],
        };
      }
      grouped[item.doctype].items.push(item);
    });
    return Object.values(grouped).map((group) => ({
      ...group,
      count: group.items.length,
    }));
  }

  function render() {
    hideLoading();
    if (!state.menu) return;
    if (!state.groups.length) {
      state.menu.html(
        `<div class="history-menu__empty text-muted">${__("No recent activity")}</div>`,
      );
      return;
    }

    let html = "";
    state.groups.forEach((group) => {
      const icon = group.icon || "fa fa-file";
      const label = frappe.utils.escape_html(group.label || group.doctype || "");
      html += `<div class="history-group">`;
      html += `<div class="history-group__header"><i class="${icon}"></i> ${label} <span class="badge">${
        group.count || group.items?.length || 0
      }</span></div>`;
      html += `<div class="history-group__items">`;
      (group.items || []).forEach((item) => {
        const title = frappe.utils.escape_html(item.title || item.name || item.doc_name || "");
        html += `<a class="dropdown-item history-item" href="${item.route || "#"}">`;
        html += `<span class="history-item__name">${title}</span>`;
        if (item.modified)
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
