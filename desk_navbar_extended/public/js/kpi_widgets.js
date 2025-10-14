/**
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
