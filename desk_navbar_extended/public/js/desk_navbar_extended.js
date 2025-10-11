(() => {
  frappe.provide("desk_navbar_extended");
  window.desk_navbar_extended = window.desk_navbar_extended || {};

  const CLOCK_ACTION = "frappe.desk_navbar_extended.show_clock";
  const CLOCK_ATTR = "data-desk-nav-extended";
  const CLOCK_ATTR_VALUE = "clock";
  const SETTINGS_CACHE_KEY = "desk-navbar-extended-settings";
  const SETTINGS_CACHE_TTL = 5 * 60 * 1000; // 5 minutes
  const TIMEZONE_CACHE_KEY = "desk-navbar-extended-timezones";
  const TIMEZONE_CACHE_TTL = 60 * 1000; // 1 minute

  const state = {
    settings: null,
    clockContainer: null,
    clockNodes: {},
    timezoneSnapshot: null,
    clockInterval: null,
    lastRendered: 0,
  };

  frappe.desk_navbar_extended = frappe.desk_navbar_extended || {};
  frappe.desk_navbar_extended.show_clock = () => false;

  function safeJSONParse(payload) {
    try {
      return JSON.parse(payload);
    } catch (err) {
      return null;
    }
  }

  function cacheWrite(key, value) {
    if (!window.sessionStorage) return;
    window.sessionStorage.setItem(
      key,
      JSON.stringify({ value, timestamp: Date.now() }),
    );
  }

  function cacheRead(key, ttl) {
    if (!window.sessionStorage) return null;
    const cached = safeJSONParse(window.sessionStorage.getItem(key));
    if (!cached) return null;
    if (Date.now() - cached.timestamp > ttl) return null;
    return cached.value;
  }

  async function fetchSettings(force = false) {
    if (!force && state.settings) return state.settings;

    if (!force) {
      const cached = cacheRead(SETTINGS_CACHE_KEY, SETTINGS_CACHE_TTL);
      if (cached) {
        state.settings = cached;
        return state.settings;
      }
    }

    const { message } = await frappe.call({
      method: "desk_navbar_extended.api.get_settings",
    });
    const normalized = JSON.parse(JSON.stringify(message || {}));
    state.settings = normalized;
    cacheWrite(SETTINGS_CACHE_KEY, normalized);
    return state.settings;
  }

  function findClockNode() {
    return document.querySelector(`[data-action="${CLOCK_ACTION}"]`);
  }

  function ensureClockContainer() {
    const node = findClockNode();
    if (!node) {
      return null;
    }
    if (!node.hasAttribute(CLOCK_ATTR)) {
      node.setAttribute(CLOCK_ATTR, CLOCK_ATTR_VALUE);
    }
    node.classList.add("desk-navbar-extended-clock-toggle");
    return node;
  }

  function formatTime(date, format) {
    const hours24 = date.getHours();
    const hours12 = hours24 % 12 === 0 ? 12 : hours24 % 12;
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
    if (format === "24h") {
      return `${String(hours24).padStart(2, "0")}:${minutes}:${seconds}`;
    }
    const suffix = hours24 >= 12 ? "PM" : "AM";
    return `${String(hours12).padStart(2, "0")}:${minutes}:${seconds} ${suffix}`;
  }

  function buildClockMarkup(snapshot) {
    if (!state.clockContainer) return;
    state.clockContainer.innerHTML = "";
    state.clockNodes = {};

    const wrapper = document.createElement("div");
    wrapper.className = "desk-navbar-extended-clock";

    snapshot.zones.forEach((zone) => {
      const row = document.createElement("div");
      row.className = "desk-navbar-extended-clock__zone";
      if (zone.color) {
        row.style.setProperty("--desk-navbar-extended-accent", zone.color);
      }

      const label = document.createElement("div");
      label.className = "desk-navbar-extended-clock__label";
      label.textContent = zone.label;
      row.appendChild(label);

      const time = document.createElement("div");
      time.className = "desk-navbar-extended-clock__time";
      time.setAttribute("role", "text");
      time.dataset.zoneKey = zone.key;
      row.appendChild(time);
      state.clockNodes[zone.key] = time;

      wrapper.appendChild(row);
    });

    if (snapshot.events && snapshot.events.length) {
      const eventsHeader = document.createElement("div");
      eventsHeader.className = "desk-navbar-extended-clock__events-header";
      eventsHeader.textContent = __("Upcoming Events");
      wrapper.appendChild(eventsHeader);

      const list = document.createElement("ul");
      list.className = "desk-navbar-extended-clock__events";
      snapshot.events.forEach((event) => {
        const item = document.createElement("li");
        item.className = "desk-navbar-extended-clock__event";
        const title = document.createElement("span");
        title.className = "desk-navbar-extended-clock__event-subject";
        title.textContent = event.subject;
        item.appendChild(title);
        if (event.starts_on) {
          const starts = new Date(event.starts_on);
          const meta = document.createElement("span");
          meta.className = "desk-navbar-extended-clock__event-meta";
          meta.textContent = frappe.datetime.str_to_user(starts.toISOString());
          item.appendChild(meta);
        }
        list.appendChild(item);
      });
      wrapper.appendChild(list);
    }

    state.clockContainer.appendChild(wrapper);
  }

  function updateClockTick() {
    if (!state.timezoneSnapshot) return;
    const offset = Date.now() - state.timezoneSnapshot.syncTime;
    const format = state.settings.clock.time_format;

    state.timezoneSnapshot.zones.forEach((zone) => {
      const baseline = zone.baseTime.getTime();
      const current = new Date(baseline + offset);
      const node = state.clockNodes[zone.key];
      if (node) {
        node.textContent = formatTime(current, format);
      }
    });

    if (Date.now() - state.timezoneSnapshot.syncTime > TIMEZONE_CACHE_TTL) {
      bootstrapClock(true).catch((error) => {
        console.error("Failed to refresh timezone overview", error); // eslint-disable-line no-console
      });
    }
  }

  async function fetchTimezoneSnapshot(force = false) {
    if (!force && state.timezoneSnapshot && Date.now() - state.timezoneSnapshot.syncTime < TIMEZONE_CACHE_TTL) {
      return state.timezoneSnapshot;
    }

    if (!force) {
      const cached = cacheRead(TIMEZONE_CACHE_KEY, TIMEZONE_CACHE_TTL);
      if (cached) {
        const snapshot = deserializeTimezoneSnapshot(cached);
        state.timezoneSnapshot = snapshot;
        return snapshot;
      }
    }

    const { message } = await frappe.call({
      method: "desk_navbar_extended.api.get_timezone_overview",
    });
    const normalized = JSON.parse(JSON.stringify(message || {}));
    const snapshot = deserializeTimezoneSnapshot(normalized);
    state.timezoneSnapshot = snapshot;
    cacheWrite(TIMEZONE_CACHE_KEY, normalized);
    return snapshot;
  }

  function deserializeTimezoneSnapshot(payload) {
    const fetchedAt = payload.fetched_at ? Date.parse(payload.fetched_at) : Date.now();
    return {
      syncTime: fetchedAt,
      zones: (payload.zones || []).map((zone) => ({
        ...zone,
        baseTime: new Date(zone.current_time || fetchedAt),
      })),
      events: payload.events || [],
    };
  }

  async function bootstrapClock(forceFetch = false) {
    state.clockContainer = ensureClockContainer();
    if (!state.clockContainer) {
      return;
    }
    const snapshot = await fetchTimezoneSnapshot(forceFetch);
    buildClockMarkup(snapshot);
    updateClockTick();
    if (!state.clockInterval) {
      state.clockInterval = setInterval(updateClockTick, 1000);
    }
  }

  function whenClockActionAvailable(callback, attempts = 0) {
    const node = findClockNode();
    if (node) {
      callback(node);
      return;
    }
    if (attempts > 20) return;
    window.requestAnimationFrame(() => whenClockActionAvailable(callback, attempts + 1));
  }

  async function init() {
    const settings = await fetchSettings();
    if (settings.features.clock) {
      whenClockActionAvailable(() => {
        bootstrapClock();
      });
    }
    if (settings.features.voice_search && window.desk_navbar_extended?.voice) {
      window.desk_navbar_extended.voice.init(settings);
    }
    if (settings.features.wide_awesomebar && window.desk_navbar_extended?.awesomebar) {
      window.desk_navbar_extended.awesomebar.init(settings);
    }
  }

  frappe.ready(() => {
    init().catch((error) => {
      console.error("Failed to initialize Desk Navbar Extended", error); // eslint-disable-line no-console
    });
  });
})();
