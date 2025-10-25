/**
 * Notifications Center - Enhanced notifications with filtering
 */
(() => {
  frappe.provide("desk_navbar_extended.notifications_center");

  let state = { notifications: [], panel: null, badge: null, unreadCount: 0 };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.features?.notifications_center)
      return;
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
              <button class="btn btn-xs btn-link notifications-center__mark-all">${__(
                "Mark all read",
              )}</button>
            </div>
            <div class="notifications-center__loading">${__("Loading...")}</div>
            <div class="notifications-center__list"></div>
          </div>
        </div>
      </div>`;
    $(".navbar-right").prepend(html);
    state.panel = $(".notifications-center__panel");
    state.badge = $(".notifications-center__badge");
    state.panel
      .find(".notifications-center__mark-all")
      .on("click", markAllRead);
  }

  async function loadNotifications() {
    showLoading();
    try {
      const { message } = await frappe.call({
        method: "desk_navbar_extended.api.notifications.get_notifications",
        freeze: false,
      });
      state.notifications = Array.isArray(message?.notifications)
        ? message.notifications
        : [];
      const unread = Number.parseInt(message?.unread_count, 10);
      state.unreadCount = Number.isFinite(unread) ? unread : 0;
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
      html = `<div class="notifications-center__empty">${__(
        "No notifications",
      )}</div>`;
    } else {
      state.notifications.forEach((notif) => {
        const unread = notif.read ? "" : "is-unread";
        html += `<div class="notification-item ${unread}" data-name="${notif.name}">`;
        html += `<div class="notification-item__content">`;
        html += `<div class="notification-item__subject">${frappe.utils.escape_html(
          notif.subject,
        )}</div>`;
        html += `<div class="notification-item__time text-muted">${comment_when(
          notif.creation,
        )}</div>`;
        html += `</div>`;
        if (!notif.read)
          html += `<button class="btn btn-xs btn-link notification-item__mark">${__(
            "Mark read",
          )}</button>`;
        html += `</div>`;
      });
    }
    state.panel.find(".notifications-center__list").html(html);
    state.panel.find(".notification-item__mark").on("click", function () {
      markRead($(this).closest(".notification-item").data("name"));
    });
  }

  function updateBadge() {
    const unread =
      typeof state.unreadCount === "number"
        ? state.unreadCount
        : state.notifications.filter((n) => !n.read).length;
    if (unread > 0) {
      state.badge.text(unread).removeAttr("hidden");
    } else {
      state.badge.attr("hidden", "");
    }
  }

  async function markRead(name) {
    try {
      const { message } = await frappe.call({
        method: "desk_navbar_extended.api.notifications.mark_as_read",
        args: { payload: { names: [name] } },
        freeze: false,
      });
      if (message?.count) {
        state.unreadCount = Math.max(
          (state.unreadCount || 1) - message.count,
          0,
        );
      }
      await loadNotifications();
    } catch (err) {
      console.error("[Notifications] Mark read error:", err);
    }
  }

  async function markAllRead() {
    try {
      await frappe.call({
        method: "desk_navbar_extended.api.notifications.mark_all_as_read",
        freeze: false,
      });
      loadNotifications();
    } catch (err) {
      console.error("[Notifications] Mark all error:", err);
    }
  }

  function showLoading() {
    state.panel.find(".notifications-center__loading").show();
    state.panel.find(".notifications-center__list").hide();
  }
  function hideLoading() {
    state.panel.find(".notifications-center__loading").hide();
    state.panel.find(".notifications-center__list").show();
  }

  frappe.desk_navbar_extended.notifications_center = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
