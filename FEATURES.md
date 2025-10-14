# Desk Navbar Extended - Feature Documentation

## Overview

Desk Navbar Extended provides a comprehensive set of power-user features for Frappe v15, enhancing productivity and user experience with Fortune 500-level polish.

## Feature List

### 1. Smart Search Filters ✅
**Status**: Implemented  
**API**: `desk_navbar_extended.api.search_filters.search_with_filters`

Advanced search with filtering by:
- DocType
- Owner
- Date range (creation)
- Custom filters via JSON

**Usage**:
```javascript
frappe.call({
  method: "desk_navbar_extended.api.search_filters.search_with_filters",
  args: {
    query: "invoice",
    doctype: "Sales Invoice",
    owner: "user@example.com",
    date_from: "2024-01-01",
    limit: 20
  }
});
```

**Features**:
- Permission-aware filtering
- Execution time tracking
- Analytics integration
- Rate limiting via client debounce

---

### 2. Saved Searches ✅
**Status**: Implemented  
**DocType**: `Desk Navbar Saved Search`  
**API**: `desk_navbar_extended.api.saved_searches`

Save frequently-used searches for quick access.

**Endpoints**:
- `list_saved_searches()` - Get user + global searches
- `create_saved_search(payload)` - Create new search
- `update_saved_search(name, payload)` - Update existing
- `delete_saved_search(name)` - Delete search

**Permissions**:
- Users can CRUD their own searches
- System Managers can create global searches

---

### 3. Pinned Items ✅
**Status**: Implemented  
**DocType**: `Desk Navbar Pin`  
**API**: `desk_navbar_extended.api.pins`

Pin frequently-accessed pages/documents for quick navigation.

**Endpoints**:
- `list_pins()` - Get user's pins
- `create_pin(payload)` - Create new pin
- `delete_pin(name)` - Delete pin
- `reorder_pins(payload)` - Reorder by sequence

**Features**:
- Drag-to-reorder support (client-side)
- Custom icons and colors
- User-scoped (no global pins)

---

### 4. Quick Create Menu ✅
**Status**: Implemented  
**API**: `desk_navbar_extended.api.quick_create.get_quick_create_options`

One-click access to create common documents.

**Configuration**:
- Auto-detects based on user permissions
- Configurable via Settings: `quick_create_doctypes` (comma-separated)
- Default list includes: Note, ToDo, Event, Task, Contact, Lead, Customer, etc.

**Returns**:
```json
[
  {
    "doctype": "Sales Order",
    "label": "Sales Order",
    "icon": "octicon octicon-file",
    "route": "/app/sales-order/new"
  }
]
```

---

### 5. Grouped History ✅
**Status**: Implemented  
**API**: `desk_navbar_extended.api.history.get_recent_activity`

View recent activity grouped by DocType/app.

**Features**:
- Groups by DocType with item counts
- Limits items per group (5 max)
- Permission-aware
- Leverages Activity Log

**Response Structure**:
```json
{
  "groups": [
    {
      "doctype": "Sales Order",
      "label": "Sales Order",
      "icon": "octicon octicon-file",
      "count": 10,
      "items": [...]
    }
  ],
  "items": [...]  // Flat list
}
```

---

### 6. Command Palette (Ctrl+K) 🚧
**Status**: Partially Implemented  
**API**: `desk_navbar_extended.api.command_palette.get_command_palette_sources`

Keyboard-driven fuzzy search for all actions.

**Sources**:
- DocTypes (all accessible)
- Saved Searches
- Pins
- Quick Create options
- Recent activity
- Help articles

**Client-side**: `desk_navbar_extended/public/js/command_palette.js`

---

### 7. Density Toggle 📋
**Status**: Backend Ready, Client Pending  
**Feature**: Toggle between compact and expanded UI density

**Implementation**:
- User preference stored in User Settings
- CSS class toggling on body
- Affects list views, forms, sidebars

---

### 8. Notifications Center ✅
**Status**: Implemented  
**API**: `desk_navbar_extended.api.notifications`

Centralized notification management.

**Endpoints**:
- `get_notifications(limit)` - Get user notifications
- `mark_as_read(names)` - Mark specific as read
- `mark_all_as_read()` - Mark all as read

**Features**:
- Unread count tracking
- Real-time updates (websocket-ready)
- Quick actions

---

### 9. Role-Based Feature Toggles ✅
**Status**: Implemented  
**DocType**: `Desk Navbar Feature Role`

Enable/disable features per role.

**Usage**:
1. Enable `enable_role_toggles` in Settings
2. Add role overrides in `feature_roles` table
3. Features automatically gated per user

**Controller**: `get_enabled_features_for_user(user)` handles resolution

---

### 10. KPI Widgets ✅
**Status**: Implemented  
**API**: `desk_navbar_extended.api.kpi.get_kpi_data`

Glanceable metrics in navbar.

**Role-Based KPIs**:
- **Sales**: Open Sales Orders, Monthly Sales
- **Purchase**: Open Purchase Orders
- **Stock**: Low Stock Items
- **All Users**: My Open ToDos

**Features**:
- Refresh interval configurable (default: 300s)
- Permission-aware
- Colored indicators
- Click-through to lists

---

### 11. Timezone Switcher ✅
**Status**: Already Implemented  
Uses existing `Desk Navbar Timezone` child table.

---

### 12. Voice Actions 🚧
**Status**: Partially Implemented  
Extends existing `voice_search.js` with action commands.

**Planned Actions**:
- "Create new [DocType]"
- "Open [DocType]"
- "Search for [query]"

---

### 13. Help/Docs Search ✅
**Status**: Implemented  
**API**: `desk_navbar_extended.api.help.search_help`

Search internal Help Articles and Frappe documentation.

**Features**:
- Searches Help Article DocType (if exists)
- Keyword-based external doc suggestions
- Links to official Frappe v15 docs

---

### 14. Layout Bookmarks 📋
**Status**: Backend Ready, Client Pending  
Save and restore workspace layouts.

**Planned Features**:
- Save current open tabs/windows
- Name and organize bookmarks
- Quick restore

---

## Configuration

All features are controlled via the **Desk Navbar Extended Settings** singleton.

### Global Settings
- `enable_*` flags for each feature
- `enable_role_toggles` to enable role-based overrides
- `enable_usage_analytics` for telemetry

### Feature-Specific Settings
- **Quick Create**: `quick_create_doctypes` (comma-separated list)
- **KPI**: `kpi_refresh_interval` (seconds)
- **Clock**: Various time/timezone settings
- **Awesomebar**: Width and mobile behavior

### Role Overrides
Add entries to `feature_roles` child table:
```
Feature: smart_filters
Role: Sales User
```

---

## API Reference

### Main Settings Endpoint
```javascript
frappe.call({
  method: "desk_navbar_extended.api.get_settings"
}).then(r => {
  const features = r.message.features;
  // features.smart_filters, features.pins, etc.
});
```

### Feature-Specific Endpoints

All endpoints check feature flags and permissions automatically.

**Search Filters**:
```python
desk_navbar_extended.api.search_filters.search_with_filters(query, doctype, owner, date_from, date_to, limit)
```

**Saved Searches**:
```python
desk_navbar_extended.api.saved_searches.list_saved_searches()
desk_navbar_extended.api.saved_searches.create_saved_search(payload)
desk_navbar_extended.api.saved_searches.update_saved_search(name, payload)
desk_navbar_extended.api.saved_searches.delete_saved_search(name)
```

**Pins**:
```python
desk_navbar_extended.api.pins.list_pins()
desk_navbar_extended.api.pins.create_pin(payload)
desk_navbar_extended.api.pins.delete_pin(name)
desk_navbar_extended.api.pins.reorder_pins(payload)
```

**Quick Create**:
```python
desk_navbar_extended.api.quick_create.get_quick_create_options()
```

**History**:
```python
desk_navbar_extended.api.history.get_recent_activity(limit)
```

**Command Palette**:
```python
desk_navbar_extended.api.command_palette.get_command_palette_sources()
```

**Notifications**:
```python
desk_navbar_extended.api.notifications.get_notifications(limit)
desk_navbar_extended.api.notifications.mark_as_read(names)
desk_navbar_extended.api.notifications.mark_all_as_read()
```

**KPI**:
```python
desk_navbar_extended.api.kpi.get_kpi_data()
```

**Help**:
```python
desk_navbar_extended.api.help.search_help(query, limit)
```

---

## Testing

Run tests:
```bash
bench --site <site> run-tests --app desk_navbar_extended
```

### Test Coverage
- ✅ `test_api.py` - Core API tests
- ✅ `test_search_filters.py` - Search filter tests
- ✅ `test_saved_searches.py` - Saved search CRUD tests
- ✅ `test_pins.py` - Pin management tests

---

## Mobile Responsiveness

All features are designed mobile-first:
- Touch-friendly UI elements (min 44x44px tap targets)
- Responsive layouts via CSS Grid/Flexbox
- Swipe gestures for pin reordering
- Collapsible panels on narrow screens
- Awesomebar collapses based on `awesomebar_mobile_collapse` setting

---

## Performance Considerations

1. **Caching**: Settings cached in sessionStorage (5min TTL)
2. **Lazy Loading**: Command palette sources loaded on-demand
3. **Debouncing**: Search inputs debounced (300ms)
4. **Pagination**: All list endpoints support limits
5. **Indexing**: All DocTypes have appropriate database indexes
6. **Analytics**: Telemetry logs asynchronously, doesn't block UX

---

## Security

- All endpoints use `@frappe.whitelist()` with permission checks
- Feature flags prevent unauthorized access
- DocType permissions respected throughout
- SQL injection prevention via parameterized queries
- XSS prevention via Frappe's built-in escaping
- CSRF protection via Frappe's token system

---

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation support
- Focus indicators
- Screen reader announcements for dynamic content
- Color contrast WCAG AA compliant

---

## Future Roadmap

### Phase 2 (Planned)
- Full client-side command palette UI
- Density toggle implementation
- Layout bookmarks
- Voice action commands
- Advanced KPI customization
- Dashboard widgets

### Phase 3 (Future)
- AI-powered search suggestions
- Collaborative pins/searches
- Advanced analytics dashboard
- Custom KPI builder
- Integration with external tools

---

## Support

For issues or feature requests:
1. Check existing GitHub issues
2. Create new issue with:
   - Feature name
   - Steps to reproduce (if bug)
   - Expected vs actual behavior
   - Screenshots if applicable

---

## License

Same as Frappe Framework (MIT)
