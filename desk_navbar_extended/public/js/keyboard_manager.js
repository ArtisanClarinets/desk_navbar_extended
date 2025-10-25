/**
 * Keyboard Manager - Centralized keyboard shortcut handler
 */
(() => {
  frappe.provide("desk_navbar_extended.keyboard_manager");

  const shortcuts = new Map();
  let isBound = false;

  function init() {
    if (isBound) return;
    $(document).on("keydown.desk_navbar_shortcuts", handleKeydown);
    isBound = true;
    console.log("[Keyboard Manager] Ready");
  }

  function register(combo, handler, description, options = {}) {
    const normalized = normalizeCombo(combo);
    if (!normalized || typeof handler !== "function") {
      console.warn("[Keyboard Manager] Invalid shortcut registration", combo);
      return;
    }
    shortcuts.set(normalized, {
      handler,
      description,
      combo: normalized,
      preventDefault: options.preventDefault !== false,
    });
  }

  function unregister(combo) {
    const normalized = normalizeCombo(combo);
    if (!normalized) return;
    shortcuts.delete(normalized);
  }

  function showHelp() {
    const rows = Array.from(shortcuts.values())
      .sort((a, b) => a.combo.localeCompare(b.combo))
      .map(
        ({ combo, description }) =>
          `<tr><td><kbd>${formatCombo(combo)}</kbd></td><td>${__(
            description || "",
          )}</td></tr>`,
      )
      .join("");
    frappe.msgprint({
      title: __("Keyboard Shortcuts"),
      message: `<table class="table table-bordered"><thead><tr><th>Shortcut</th><th>Action</th></tr></thead><tbody>${rows}</tbody></table>`,
    });
  }

  function handleKeydown(event) {
    if (shouldIgnoreEvent(event)) return;
    const combo = serializeEvent(event);
    if (!combo) return;
    const shortcut = shortcuts.get(combo);
    if (!shortcut) return;
    if (shortcut.preventDefault) {
      event.preventDefault();
      event.stopPropagation();
    }
    shortcut.handler(event);
  }

  function shouldIgnoreEvent(event) {
    const target = event.target;
    if (!target) return false;
    const tag = target.tagName;
    if (!tag) return false;
    const editable =
      target.isContentEditable ||
      ["INPUT", "TEXTAREA", "SELECT"].includes(tag) ||
      target.getAttribute?.("role") === "textbox";
    return editable;
  }

  function serializeEvent(event) {
    const parts = [];
    if (event.ctrlKey) parts.push("ctrl");
    if (event.metaKey) parts.push("meta");
    if (event.altKey) parts.push("alt");
    if (event.shiftKey) parts.push("shift");

    const key = normalizeKey(event.key);
    if (!key) return null;

    parts.sort(modifierSort);
    parts.push(key);
    return parts.join("+");
  }

  function normalizeCombo(combo) {
    if (!combo) return null;
    const alias = {
      command: "meta",
      cmd: "meta",
      option: "alt",
      control: "ctrl",
      ctrl: "ctrl",
      meta: "meta",
      shift: "shift",
      alt: "alt",
      super: "meta",
    };

    const parts = combo
      .split("+")
      .map((part) => part.trim().toLowerCase())
      .filter(Boolean);

    const modifiers = new Set();
    let key = null;

    parts.forEach((part) => {
      const mapped = alias[part] || part;
      if (["ctrl", "meta", "alt", "shift"].includes(mapped)) {
        modifiers.add(mapped);
      } else {
        key = normalizeKey(mapped);
      }
    });

    if (!key) return null;
    const ordered = Array.from(modifiers).sort(modifierSort);
    ordered.push(key);
    return ordered.join("+");
  }

  function normalizeKey(key) {
    if (!key) return null;
    const map = {
      esc: "escape",
      arrowup: "arrowup",
      arrowdown: "arrowdown",
      arrowleft: "arrowleft",
      arrowright: "arrowright",
      " ": "space",
      spacebar: "space",
      enter: "enter",
      return: "enter",
    };
    const lower = key.toLowerCase();
    if (map[lower]) return map[lower];
    if (lower.length === 1) return lower;
    return lower;
  }

  function modifierSort(a, b) {
    const order = ["ctrl", "meta", "alt", "shift"];
    return order.indexOf(a) - order.indexOf(b);
  }

  function formatCombo(combo) {
    return combo
      .split("+")
      .map((part) =>
        part.length === 1 ? part.toUpperCase() : part.toUpperCase(),
      )
      .join("+");
  }

  frappe.desk_navbar_extended.keyboard_manager = {
    init,
    register,
    unregister,
    showHelp,
  };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
