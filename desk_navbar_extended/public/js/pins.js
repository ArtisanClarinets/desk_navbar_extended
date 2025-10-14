/**
 * Pins - Quick access bar for frequently used items
 */
(() => {
  frappe.provide("desk_navbar_extended.pins");

  let state = { pins: [], bar: null };

  function init() {
    if (!frappe.desk_navbar_extended?.settings?.enable_pins) return;
    buildPinBar();
    loadPins();
    console.log("[Pins] Ready");
  }

  function buildPinBar() {
    const html = `
      <div class="pin-bar">
        <div class="pin-bar__items"></div>
        <button class="btn btn-xs btn-default pin-bar__add" title="${__("Add Pin")}">
          <i class="fa fa-plus"></i>
        </button>
      </div>`;
    $("#navbar-breadcrumbs").after(html);
    state.bar = $(".pin-bar");
    state.bar.find(".pin-bar__add").on("click", addPin);
  }

  async function loadPins() {
    try {
      const { message } = await frappe.call({ method: "desk_navbar_extended.api.pins.list_pins", freeze: false });
      state.pins = message || [];
      render();
    } catch (err) {
      console.error("[Pins] Load error:", err);
    }
  }

  function render() {
    let html = "";
    state.pins.forEach(pin => {
      html += `<div class="pin-item" data-name="${pin.name}">`;
      html += `<a href="${pin.route}" class="pin-item__link">`;
      html += `<i class="${pin.icon_class || 'fa fa-star'}"></i>`;
      html += `<span>${frappe.utils.escape_html(pin.label)}</span>`;
      html += `</a>`;
      html += `<button class="pin-item__delete" title="${__("Remove")}"><i class="fa fa-times"></i></button>`;
      html += `</div>`;
    });
    state.bar.find(".pin-bar__items").html(html);
    state.bar.find(".pin-item__delete").on("click", function() { deletePin($(this).closest(".pin-item").data("name")); });
  }

  async function addPin() {
    const d = new frappe.ui.Dialog({
      title: __("Add Pin"),
      fields: [
        { label: __("Label"), fieldname: "label", fieldtype: "Data", reqd: 1 },
        { label: __("DocType"), fieldname: "doctype", fieldtype: "Link", options: "DocType", reqd: 1 },
        { label: __("Document Name"), fieldname: "doc_name", fieldtype: "Data" },
        { label: __("Icon Class"), fieldname: "icon_class", fieldtype: "Data", default: "fa fa-star" },
      ],
      primary_action_label: __("Add"),
      primary_action: async (values) => {
        try {
          await frappe.call({
            method: "desk_navbar_extended.api.pins.create_pin",
            args: values,
          });
          frappe.show_alert({ message: __("Pin added"), indicator: "green" });
          d.hide();
          loadPins();
        } catch (err) {
          console.error("[Pins] Create error:", err);
          frappe.show_alert({ message: __("Failed to add pin"), indicator: "red" });
        }
      },
    });
    d.show();
  }

  async function deletePin(name) {
    if (!confirm(__("Remove this pin?"))) return;
    try {
      await frappe.call({ method: "desk_navbar_extended.api.pins.delete_pin", args: { name } });
      frappe.show_alert({ message: __("Pin removed"), indicator: "green" });
      loadPins();
    } catch (err) {
      console.error("[Pins] Delete error:", err);
      frappe.show_alert({ message: __("Failed to remove pin"), indicator: "red" });
    }
  }

  frappe.desk_navbar_extended.pins = { init };
  $(document).on("frappe.desk_navbar_extended.ready", init);
})();
