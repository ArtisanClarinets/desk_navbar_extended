## Desk Navbar Extended

Tweaks in Desk's Navbar to boost Productivity

[![Try on Frappe Cloud](./.github/assets/try-on-fc.png)](https://frappecloud.com/marketplace/apps/desk_navbar_extended?referrer=a6d8da54)

### Features

**Core Features** (Already Implemented):
1. **Enterprise desk clock** – configurable via *Desk Navbar Extended Settings* with role-scoped toggles, additional world clocks, and live calendar excerpts in the navbar dropdown.
2. **Production voice search** – microphone control adjacent to the awesomebar with Web Speech API integration, MediaRecorder fallback, and background transcription queueing.
3. **Configurable awesomebar layout** – width, mobile collapse behaviour, and optional analytics instrumentation exposed through the settings singleton and dedicated metrics dashboard.
4. **Telemetry workspace** – administrators receive a workspace card summarising `Desk Navbar Search Metric` entries with realtime alerts when error rates spike.

**New Power Features** (v2.0):
5. **Smart Search Filters** – Advanced search with DocType, owner, and date filtering
6. **Saved Searches** – Save and reuse frequent searches with global sharing capability
7. **Pinned Items** – Quick-access favorites bar with drag-to-reorder
8. **Quick Create Menu** – One-click access to create common documents
9. **Grouped History** – Recent activity organized by DocType/app
10. **Command Palette** – Keyboard-driven fuzzy search (Ctrl+K)
11. **Notifications Center** – Centralized notification management with quick actions
12. **Role-Based Feature Toggles** – Granular feature control per role
13. **KPI Widgets** – Glanceable metrics in navbar (role-based)
14. **Timezone Switcher** – Multi-timezone support with visual indicators
15. **Help/Docs Search** – Integrated documentation search
16. **Density Toggle** – Compact/expanded UI mode (coming soon)
17. **Layout Bookmarks** – Save/restore workspace layouts (coming soon)
18. **Voice Actions** – Voice-activated commands (coming soon)

See [FEATURES.md](./FEATURES.md) for detailed documentation.

![](./.github/assets/same-time_zone.png)
*When User & Site TimeZones Match*

![](./.github/assets/different-time_zone.png)
*When User & Site TimeZones are Different*

![](./.github/assets/wider-awesomebar.png)

### Configuration

All capabilities are managed through **Desk Navbar Extended Settings** (single doctype). Key options include:

- Enable or disable the clock, voice search, and wide awesomebar features per role.
- Choose 12h/24h formatting, calendar excerpts, and add unlimited custom time zones with colour accents.
- Configure awesomebar width, mobile collapse, and opt-in usage analytics.

Voice search background transcription expects the following environment variables in `site_config.json`:

- `desk_navbar_transcription_endpoint` – HTTPS endpoint that receives base64 audio payloads.
- `desk_navbar_transcription_api_key` – API token forwarded to the external transcription service.

Without these values the job logs a warning and retains the recording for manual follow-up.

### Testing

Run the Python tests inside a bench with the app installed:

```bash
bench --site test_site run-tests --app desk_navbar_extended desk_navbar_extended.tests.test_api
```

For client-side assertions, include `desk_navbar_extended/public/js/tests/voice_search.test.js` in your QUnit bundle.

### Post-Patch Actions

1. Clear caches and rebuild assets:

   ```bash
   bench --site <yoursite> clear-cache
   bench build --apps desk_navbar_extended
   bench restart
   ```

2. Seed or re-seed the navbar action safely:

   ```bash
   bench --site <yoursite> execute "from desk_navbar_extended.setup import add_clock_navbar_item; add_clock_navbar_item()"
   ```

### Manual QA Checklist

- Open Desk, expand the user menu, and click **Show Time** – the clock panel should appear or hide without closing the dropdown.
- Leave the dropdown, wait a few minutes, reopen it – any visible clock panel should refresh automatically.
- If voice search is enabled, clicking the microphone must no longer trigger 403/404 responses and should leave the UI stable if transcription is not configured.

### Security / Compliance Checklist

- All whitelisted endpoints disallow guest access and validate payload sizes and formats.
- Sensitive operations log via `frappe.logger("desk_navbar_extended")` without exposing credentials.
- Feature flags default to safe values through the singleton settings document.

#### License

MIT
