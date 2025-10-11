(() => {
  frappe.provide("desk_navbar_extended.awesomebar");
  window.desk_navbar_extended = window.desk_navbar_extended || {};
  window.desk_navbar_extended.awesomebar = window.desk_navbar_extended.awesomebar || {};

  const analyticsState = {
    wrapped: false,
    settings: null,
    lastSearch: null,
  };

  function resolveAwesomebarInput() {
    const candidates = [
      "#navbar-search",
      ".navbar-search input",
      "input[data-element='awesome-bar']",
    ];
    for (const selector of candidates) {
      const node = document.querySelector(selector);
      if (node) return node;
    }
    if (frappe.search?.utils?.search_input) {
      return frappe.search.utils.search_input;
    }
    return null;
  }

  function applyWidth(width) {
    if (!width) return;
    document.documentElement.style.setProperty(
      "--desk-navbar-awesomebar-width",
      `${width}px`,
    );
  }

  function toggleMobileCollapse(enable) {
    const body = document.body;
    if (!body) return;
    const shouldCollapse = Boolean(enable) && window.innerWidth <= 768;
    body.classList.toggle("desk-navbar-awesomebar--collapsed", shouldCollapse);
  }

  function waitForSearch(callback, attempts = 0) {
    if (frappe.search?.utils?.search) {
      callback();
      return;
    }
    if (attempts > 20) return;
    setTimeout(() => waitForSearch(callback, attempts + 1), 150);
  }

  function logSearchMetrics(payload) {
    frappe.call({
      method: "desk_navbar_extended.api.log_search_metrics",
      args: { payload: JSON.stringify(payload) },
      freeze: false,
    });
  }

  function installAnalytics() {
    if (analyticsState.wrapped) return;
    waitForSearch(() => {
      const original = frappe.search.utils.search;
      if (original.__deskNavbarWrapped) return;
      frappe.search.utils.search = function deskNavbarInstrumentedSearch(value, ...rest) {
        const input = resolveAwesomebarInput();
        const started = performance.now();
        const length = typeof value === "string" ? value.length : (input?.value || "").length;
        analyticsState.lastSearch = { value, started };
        try {
          const result = original.call(this, value, ...rest);
          return Promise.resolve(result)
            .then((response) => {
              logSearchMetrics({
                status: "success",
                search_length: length,
                execution_ms: performance.now() - started,
              });
              return response;
            })
            .catch((error) => {
              logSearchMetrics({
                status: "error",
                search_length: length,
                execution_ms: performance.now() - started,
                error_message: error?.message,
              });
              throw error;
            });
        } catch (error) {
          logSearchMetrics({
            status: "error",
            search_length: length,
            execution_ms: performance.now() - started,
            error_message: error?.message,
          });
          throw error;
        }
      };
      frappe.search.utils.search.__deskNavbarWrapped = true;
      analyticsState.wrapped = true;
    });
  }

  window.desk_navbar_extended.awesomebar.init = (settings) => {
    analyticsState.settings = settings;
    applyWidth(settings.awesomebar.default_width);
    toggleMobileCollapse(settings.awesomebar.mobile_collapse);
    if (settings.features.usage_analytics) {
      installAnalytics();
    }

    window.addEventListener(
      "resize",
      frappe.utils.debounce(() => {
        toggleMobileCollapse(settings.awesomebar.mobile_collapse);
      }, 300),
    );
  };
})();
