
# FEATURE_PLAN.md — Desk Navbar Extended (Frappe v15)

> **Purpose**: Ship a production‑ready, toggleable set of navbar power‑features without assumptions, dummy data, or breaking existing UX. All new logic is gated by a **single Settings singleton** and verified by automated tests.

**App**: `desk_navbar_extended`  
**Key modules**:
- Server: `desk_navbar_extended/api.py`, `desk_navbar_extended/desk_navbar_extended/doctype/**`
- Client: `desk_navbar_extended/public/js/{desk_navbar_extended.js, awesomebar_layout.js, voice_search.js}`
- Styles: `desk_navbar_extended/public/css/awesomebar.css`
- Tests: `desk_navbar_extended/tests/test_api.py`, `desk_navbar_extended/public/js/tests/**`

---

## 0) Main Settings (Single Source of Truth)

**DocType**: `Desk Navbar Extended Settings` (singleton)  
**Controller**: `desk_navbar_extended/desk_navbar_extended/doctype/desk_navbar_extended_settings/desk_navbar_extended_settings.py`

### 0.1 Fields to add (all **Check**, default "0" unless noted)
| Fieldname | Label | Default | Notes |
|---|---|---|---|
| enable_smart_filters | Enable Smart Search Filters | 1 | Adds filter UI + filtered search endpoint |
| enable_saved_searches | Enable Saved Searches | 1 | Per‑user quick filters |
| enable_quick_create | Enable Quick Create | 1 | Shortcut launcher for common DocTypes |
| enable_pins | Enable Pinned Items | 1 | Favorites bar |
| enable_grouped_history | Enable Grouped History | 1 | Groups by app/doctype |
| enable_command_palette | Enable Command Palette (Ctrl+K) | 1 | Modal fuzzy actions |
| enable_density_toggle | Enable Compact/Expanded Toggle | 1 | User preference stored per user |
| enable_notifications_center | Enable Notifications Center | 1 | Lists + quick actions |
| enable_role_toggles | Enable Role‑Based Feature Toggles | 1 | Uses `Desk Navbar Feature Role` |
| enable_kpi_widgets | Enable KPI Widgets in Navbar | 0 | Glanceable metrics |
| enable_timezone_switcher | Enable Timezone Switcher | 1 | Uses `Desk Navbar Timezone` |
| enable_voice_actions | Enable Voice Action Commands | 0 | Extends `voice_search.js` |
| enable_help_search | Enable Help/Docs Search | 1 | Frappe docs + translations |
| enable_layout_bookmarks | Enable Layout Bookmarks | 0 | Save/restore desk layout |
| enable_usage_analytics | Enable Usage Analytics | 0 | Already present (log events) |

> **Implementation**: Update the Settings JSON to include the above, and expose them via the controller helper `get_enabled_features_for_user()` and `api.get_settings()` payload. Respect role overrides with `Desk Navbar Feature Role`.

### 0.2 Role Overrides
Use existing child table **`Desk Navbar Feature Role`** to enable/disable specific features per role. The controller should compute the final feature map per user.

### 0.3 Controller helper (reference)
- `desk_navbar_extended_settings.py` should export:
  - `def get_enabled_features_for_user(user: str | None = None) -> dict:` returning a dict keyed by the `enable_*` flags resolved for the current user, considering role overrides.
- `api.get_settings()` must include `{"features": <map>}` and any dependent configuration.

### 0.4 Tests (settings)
- Add server tests to assert that:
  - Defaults load and feature map returns expected booleans.
  - Role overrides enable/disable a feature properly for a user with that role.
  - `api.get_settings()` includes all feature keys.

**Commands**:
```bash
bench --site artisanclarinets.localhost migrate
bench --site artisanclarinets.localhost run-tests --app desk_navbar_extended
```

---

## 1) Smart Search Filters (type / DocType / date / owner)

**Benefit**: Faster narrowing of results directly from the awesomebar.

**Server**
- **Endpoint**: `@frappe.whitelist()` `search_with_filters(query: str, doctype: str|None, owner: str|None, date_from: date|None, date_to: date|None, limit: int = 20)`
  - Validate inputs; deny wide‑open owner/date filters without a base `query`.
  - Use `frappe.get_list` or `frappe.desk.search.search_link` style utilities with filters; enforce user permissions.
  - Gate with `enable_smart_filters` and return `403` if disabled.
- **Telemetry**: Log to `Desk Navbar Search Metric` (`status`, `execution_ms`, `search_length`).

**Client**
- Files: `public/js/awesomebar_layout.js`, `public/js/desk_navbar_extended.js`
- Add filter chips (doctype, owner, date range) with debounce on input; call the new endpoint.
- Respect `features.smart_filters` from `get_settings()` to show/hide UI.

**Tests**
- Server tests covering filtered queries and permission scoping.
- JS QUnit test for filter chip parsing and request payload formatting.

**Security**
- Enforce DocType read permissions on any filtered search.
- Rate‑limit via simple debounce client‑side and server execution time logging.

---

## 2) Saved Searches / Quick Filters

**Benefit**: One‑click access to frequent queries, per‑user.

**Data Model**
- New DocType: `Desk Navbar Saved Search` (fields: `title (Data)`, `query (Small Text)`, `doctype (Link: DocType, optional)`, `filters (JSON)`, `is_global (Check, default 0)`).
  - Permissions: Owner can CRUD own; `System Manager` can set `is_global=1`.

**Server**
- Endpoints (all gated by `enable_saved_searches`):
  - `list_saved_searches()` – returns user + global records (sanitized).
  - `create_saved_search(payload)` – validate and insert.
  - `delete_saved_search(name)` – owner or `System Manager` only.

**Client**
- Files: `public/js/desk_navbar_extended.js`
- Render a dropdown near the awesomebar; select applies filters & runs search.

**Tests**
- Server CRUD tests with permission checks.
- JS: render list and apply selection (stub endpoint in test).

---

## 3) Quick‑Create Menu (common DocTypes)

**Benefit**: Reduce clicks to create frequent documents.

**Server**
- No server endpoint strictly required; use standard form routing.
- Optional endpoint `quick_create_options()` returning allowed doctypes per role (gated by `enable_quick_create`).

**Client**
- Files: `public/js/desk_navbar_extended.js`
- Launcher button opens a list of role‑allowed DocTypes; call `frappe.new_doc(doctype)` or route to `Form/{Doctype}/New {Doctype}`.

**Security**
- Filter by `frappe.has_permission(doctype, "create")` on server when building options.

**Tests**
- Server unit test for options filtering by role.
- JS QUnit test: UI opens & routes correctly.

---

## 4) Pinned / Favorites Bar

**Benefit**: Persistent, user‑level quick links to pages/records.

**Data Model**
- New DocType: `Desk Navbar Pin` (fields: `label (Data)`, `route (Data)`, `icon (Data)`, `color (Color)`, `sequence (Int)`).
  - Owner has CRUD; no global pins by default.

**Server**
- Endpoints (gated by `enable_pins`): `list_pins()`, `create_pin(payload)`, `delete_pin(name)`, `reorder(payload)` (update `sequence`).

**Client**
- Files: `public/js/desk_navbar_extended.js`
- Render a horizontal bar; support drag‑reorder and click to navigate.

**Tests**
- CRUD and ordering tests; UI rendering and navigation click test.

---

## 5) Recent + Grouped History (by app / DocType)

**Benefit**: Easier context switching.

**Server**
- Endpoint: `recent_activity_grouped(limit=20)` (gated by `enable_grouped_history`).
  - Build from `frappe.desk.form.load.get_open_count` and user recent routes; group by app/doctype.

**Client**
- Files: `public/js/awesomebar_layout.js`
- Collapsible sections per group.

**Tests**
- Server grouping logic unit test; JS rendering test.

---

## 6) Keyboard Shortcuts / Command Palette (Ctrl+K)

**Benefit**: Power‑user navigation & actions.

**Client**
- Files: `public/js/desk_navbar_extended.js`
- Bind `Ctrl/Cmd+K` to open a modal palette; fuzzy‑search actions: open doctype, saved search, pin, recent, quick‑create, help. Gate with `enable_command_palette`.

**Server**
- Optional endpoint `command_palette_sources()` aggregating items; enforce permissions.

**Tests**
- JS: keyboard handler and fuzzy search source test.

**Accessibility**
- Aria roles, focus trap, escape key to close.

---

## 7) Compact/Expanded Theme Toggle

**Benefit**: Control navbar density.

**Client**
- Files: `public/js/desk_navbar_extended.js`, `public/css/awesomebar.css`
- Toggle `data-navbar-density="compact|comfortable"` on `<body>` and scope CSS.

**Server**
- Persist user preference in a per‑user key using `frappe.db.set_value("User", user, "desk_navbar_density", value)` or a small `User Setting` child doctype in this app.
- Gate with `enable_density_toggle`.

**Tests**
- JS toggling test; server persistence test.

---

## 8) Notifications Center with Quick‑Actions

**Benefit**: Central actionable alerts.

**Server**
- Endpoint: `list_notifications(limit=20)`; use Frappe notifications APIs to list items user has access to.
- Endpoint: `act_on_notification(docname, action)` to mark read / route action (e.g., close ToDo).
- Gate with `enable_notifications_center`.

**Client**
- Files: `public/js/desk_navbar_extended.js`
- Dropdown panel with tabs (All / Unread / Assigned to Me).

**Tests**
- Server: ensure only permitted docs returned.
- JS: rendering & action click test.

**Security**
- Strict permission checks per notification record.

---

## 9) Role‑Based Feature Toggles

**Benefit**: Declutter for personas.

**Data Model**
- Existing child table `Desk Navbar Feature Role` with fields: `feature (Select)`, `role (Link Role)`.
  - Extend `feature` options to include new features listed in §0.1.

**Controller**
- `get_enabled_features_for_user()` merges global flags with role overrides.
- Gate all endpoints and client UI based on this map.

**Tests**
- Add unit test per feature ensuring override works.

---

## 10) Saved Dashboard Widgets / KPI in Navbar

**Benefit**: Glanceable metrics without leaving the page.

**Data Model**
- New DocType: `Desk Navbar KPI` (fields: `label (Data)`, `sql (Code)`, `value_field (Data)`, `format (Select: number, currency, percent)`, `refresh_cron (Data, optional)`).
  - Only `System Manager` can create/edit; users can subscribe to visibility via `Desk Navbar Extended Settings` or a per‑user preference.

**Server**
- Endpoint: `list_kpis()` returns only **whitelisted, safe** KPIs; executes read‑only queries with parameterization; deny dangerous SQL.
- Gate with `enable_kpi_widgets` and role.

**Client**
- Files: `public/js/desk_navbar_extended.js`
- Minimal tiles rendered inline; manual refresh button.

**Security**
- Use a safe query executor. Never allow arbitrary SQL from users.

**Tests**
- Server: safe execution, role filtering.
- JS: tile render test.

---

## 11) Quick Timezone Switcher (existing doctype)

**Benefit**: Easier global collaboration.

**Data Model**
- Existing DocType `Desk Navbar Timezone` (fields: `city_label`, `time_zone`, `color`).

**Server**
- Ensure `api.get_timezone_overview()` supports the quick dropdown list of configured zones.
- Gate with `enable_timezone_switcher` and `enable_clock`.

**Client**
- Files: `public/js/desk_navbar_extended.js`
- Dropdown to change displayed zone; no global system change.

**Tests**
- Server list test; JS selection updates clock display.

---

## 12) Voice Command Expansion (voice → run actions)

**Benefit**: Hands‑free navigation and actions.

**Client**
- Files: `public/js/voice_search.js`
- Map phrases (e.g., "open sales invoice", "new task") to routed actions; only when `enable_voice_actions` and browser permission granted.

**Server**
- Reuse existing `transcribe_audio` background job path when configured via `frappe.conf`. If not configured, **skip gracefully** (no stubs).

**Tests**
- JS: command parsing → correct action; ensure disabled when flag off.

**Accessibility**
- Visual feedback; keyboard alternative exists.

---

## 13) Contextual Help / Documentation Search

**Benefit**: Faster onboarding and self‑help.

**Server**
- Endpoint: `search_help(q: str, limit=10)` querying official Frappe docs index or local help files (translations folder) if available.
- Gate with `enable_help_search`.

**Client**
- Files: `public/js/desk_navbar_extended.js`
- Help icon opens a small panel; fuzzy list of results linking to pages.

**Tests**
- Server: simple search across help sources.
- JS: panel open/close and navigation test.

---

## 14) Save UI Layouts / Bookmarks (per‑user)

**Benefit**: Restore a custom workspace layout quickly.

**Data Model**
- New DocType: `Desk Navbar Layout Bookmark` (fields: `title (Data)`, `payload (JSON)`, `is_default (Check)`).

**Server**
- Endpoints `list_layouts()`, `save_layout(payload)`, `apply_layout(name)` gated by `enable_layout_bookmarks`.
- Validate payload schema (only supported keys).

**Client**
- Files: `public/js/desk_navbar_extended.js`
- Save/restore buttons; confirm before override if `is_default` exists.

**Tests**
- Server JSON schema validation tests; JS: save/restore flow.

---

## 15) Telemetry & Analytics (existing Search Metric)

If `enable_usage_analytics` is on:
- Continue writing events to **`Desk Navbar Search Metric`** with minimal, anonymized payload (e.g., hash actor id). Never log PII or full queries unless explicitly approved.

**Tests**: Existing `test_api.py` can be extended for new event types.

---

## Wiring & Gating (Summary)

- **Settings → Controller → API → Client** is the enforcement chain.
- Every endpoint **must** early‑return `403` if its feature flag is disabled.
- Every UI component checks `window.deskNavbarExtended.features` loaded from `api.get_settings()`.

---

## Migrations & Fixtures

- New DocTypes: add JSON under `desk_navbar_extended/desk_navbar_extended/doctype/<doctype>/<doctype>.json` with controllers as needed.
- Update `hooks.py` fixtures if you decide to export role overrides or translations.
- Run `bench migrate` to install schema changes.

**Commands**
```bash
bench --site artisanclarinets.localhost migrate
bench --site artisanclarinets.localhost build
bench --site artisanclarinets.localhost set-config allow_tests true
bench --site artisanclarinets.localhost run-tests --app desk_navbar_extended
```

---

## Acceptance Criteria (per feature)

- Respect feature flag and role overrides.
- Enforce permissions on server results; no unscoped listings.
- No external calls unless configured in `frappe.conf`; skip gracefully otherwise.
- Tests passing (server + JS) and lint/format clean.
- No performance regressions in typing or rendering; use debounce and request cancellation.
