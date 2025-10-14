# Keyboard Shortcuts Reference

## Desk Navbar Extended v2.0 - Complete Keyboard Shortcuts Guide

This document provides a comprehensive list of all keyboard shortcuts available in Desk Navbar Extended v2.0.

---

## Global Shortcuts

### Command Palette
- **Ctrl+K** (Windows/Linux) or **Cmd+K** (Mac) - Open Command Palette
- **ESC** - Close Command Palette
- **↑ / ↓** - Navigate results
- **Enter** - Select highlighted result
- **Type to search** - Fuzzy search across commands

### Help Search
- **Shift+?** - Open Help Search Modal
- **ESC** - Close Help Modal
- **Type to search** - Search help articles and documentation

---

## Navigation Shortcuts

### Quick Create
Accessible via dropdown menu or Command Palette:
- **Ctrl+K** → Type DocType name → **Enter** to create new document

### Pins
- Click pin items for instant navigation
- Drag to reorder (desktop)
- **+ button** to add new pin

### History
- Access via dropdown in navbar
- Grouped by DocType for easier scanning
- Click any recent item to navigate

---

## Search & Filtering

### Smart Search Filters
Active filters apply automatically to awesomebar search:
- **DocType Filter** - Select from dropdown
- **Owner Filter** - Filter by user
- **Date Range** - Filter by creation/modification date
- **Clear button** - Reset all filters

### Saved Searches
- **Save** - Click "Save Current Search" in dropdown
- **Apply** - Click saved search to apply to awesomebar
- **Delete** - Hover and click trash icon

---

## Productivity Features

### Density Toggle
- **Click toggle button** in navbar to switch between:
  - **Comfortable** - Standard spacing (default)
  - **Compact** - Reduced padding for information density

Preference is saved in localStorage per browser.

### KPI Widgets
- **Click widget** - Navigate to filtered list view
- Auto-refresh every 5 minutes (configurable)
- Role-based widget display

### Notifications Center
- **Click notification** - Navigate to relevant document
- **Mark as Read** - Individual notification
- **Mark All as Read** - Bulk action
- Badge shows unread count

---

## Command Palette Categories

When you open Command Palette (**Ctrl+K**), you'll see results grouped by:

1. **DocTypes** - All doctypes you have access to
2. **Recent Items** - Your recent activity
3. **Saved Searches** - Your saved search queries
4. **Pins** - Your pinned items
5. **Help** - Help articles and documentation

---

## Tips & Tricks

### Fuzzy Search
The Command Palette uses fuzzy matching:
- Type **"salo"** to find **"Sales Order"**
- Type **"cusdoc"** to find **"Customer Doctype"**
- Type **"inv"** to match **"Invoice", "Inventory", "Investigation"**

### Quick Workflows
1. **Fast Document Creation**: **Ctrl+K** → Type doctype → **Enter**
2. **Recent Document Access**: **Ctrl+K** → Type document name → **Enter**
3. **Help Lookup**: **Shift+?** → Type topic → **Enter**

### Mobile Gestures
- **Tap** - Activate any button/menu
- **Swipe** - Scroll through KPI widgets or pin bar
- **Long press** - Context menu on pins (if enabled)

---

## Customization

### Enable/Disable Features
Go to **Desk Navbar Extended Settings** to toggle:
- ☑ Command Palette
- ☑ Smart Search Filters
- ☑ Saved Searches
- ☑ Pins
- ☑ Quick Create Menu
- ☑ Grouped History
- ☑ Notifications Center
- ☑ KPI Widgets
- ☑ Help Search
- ☑ Density Toggle

### Role-Based Overrides
System Managers can configure role-specific feature access in Settings.

---

## Accessibility

All features support:
- **ARIA labels** for screen readers
- **Keyboard-only navigation** (no mouse required)
- **Focus indicators** for visible navigation state
- **Reduced motion** respects `prefers-reduced-motion`

---

## Performance Notes

- **Caching**: Settings cached for 5 minutes in sessionStorage
- **Lazy Loading**: Modules initialize only when enabled
- **Debouncing**: Search inputs debounced to reduce API calls
- **Smart Rendering**: Only visible items rendered in long lists

---

## Troubleshooting

### Keyboard shortcuts not working?
1. Check if feature is enabled in Settings
2. Clear browser cache and reload (**Ctrl+Shift+R**)
3. Check browser console for errors (**F12**)

### Command Palette empty?
1. Verify API connectivity
2. Check permissions for doctype access
3. Confirm background job workers running

### Slow performance?
1. Enable Density Toggle for compact mode
2. Disable unused features in Settings
3. Check network latency (API calls)

---

## Support & Feedback

For issues, feature requests, or contributions:
- **GitHub**: [https://github.com/ArtisanClarinets/desk_navbar_extended]
- **Documentation**: See `FEATURES.md` and `INSTALLATION.md`
- **Email**: [thompson.d.r.92@gmail.com]

---

**Last Updated**: 2025-10-14  
**Version**: 2.0.0  
**Compatibility**: Frappe v15+
