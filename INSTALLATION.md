# Installation & Testing Guide

## Installation

### New Installation

```bash
# Get the app
cd /home/frappe/frappe-bench
bench get-app desk_navbar_extended .

# Create a new site (or use existing)
bench new-site <site-name> --db-root-password <pwd> --admin-password <pwd>

# Install the app
bench --site <site-name> install-app desk_navbar_extended

# Build assets
bench build --app desk_navbar_extended

# Restart
bench restart
```

### Upgrading from v1.x

```bash
# Pull latest changes
cd /home/frappe/frappe-bench/apps/desk_navbar_extended
git pull

# Run migrate to apply new features
bench --site <site-name> migrate

# Build assets
bench build --app desk_navbar_extended

# Restart
bench restart
```

The migration will automatically:
- Add new feature flags to Settings
- Create new DocTypes (Saved Search, Pin)
- Set sensible defaults (all features enabled except KPI, voice actions, layout bookmarks)

---

## Configuration

After installation, configure via **Desk > Desk Navbar Extended Settings**.

### Enable/Disable Features

All features have `enable_*` checkboxes:
- ✅ Enabled by default: Smart Filters, Saved Searches, Quick Create, Pins, Grouped History, Command Palette, Density Toggle, Notifications Center, Role Toggles, Timezone Switcher, Help Search
- ❌ Disabled by default: KPI Widgets, Voice Actions, Layout Bookmarks

### Role-Based Overrides

1. Enable **Enable Role-Based Feature Toggles**
2. In **Feature Role Overrides** table, add rows:
   ```
   Feature: smart_filters
   Role: Sales User
   ```

Users with that role will have the feature enabled (assuming global setting is also enabled).

### Quick Create Configuration

**Option 1**: Auto-detect (leave `Quick Create DocTypes` blank)  
- Shows common doctypes user has create permission for

**Option 2**: Custom list (comma-separated in `Quick Create DocTypes`)  
```
Sales Order, Purchase Order, Customer, Supplier, Item
```

### KPI Configuration

Set **KPI Refresh Interval** (seconds) to control how often widgets refresh (default: 300 = 5 minutes).

---

## Testing

### Run All Tests

```bash
# Full test suite
bench --site <site-name> run-tests --app desk_navbar_extended

# Specific test file
bench --site <site-name> run-tests --app desk_navbar_extended --module desk_navbar_extended.tests.test_search_filters
```

### Manual Testing Checklist

#### 1. Smart Search Filters
- [ ] Open desk
- [ ] Search for "user" in awesomebar
- [ ] Verify results appear
- [ ] (If UI implemented) Apply doctype filter
- [ ] (If UI implemented) Apply owner filter

#### 2. Saved Searches
- [ ] Create saved search via API:
  ```javascript
  frappe.call({
    method: "desk_navbar_extended.api.saved_searches.create_saved_search",
    args: {
      payload: {
        title: "My Invoices",
        query: "invoice",
        doctype_filter: "Sales Invoice"
      }
    }
  });
  ```
- [ ] List saved searches:
  ```javascript
  frappe.call({
    method: "desk_navbar_extended.api.saved_searches.list_saved_searches"
  });
  ```
- [ ] Verify saved search appears in list
- [ ] Delete saved search

#### 3. Pins
- [ ] Create pin:
  ```javascript
  frappe.call({
    method: "desk_navbar_extended.api.pins.create_pin",
    args: {
      payload: {
        label: "Sales Dashboard",
        route: "/app/sales-analytics",
        icon: "octicon octicon-graph",
        color: "#3b82f6"
      }
    }
  });
  ```
- [ ] List pins and verify
- [ ] Reorder pins
- [ ] Delete pin

#### 4. Quick Create
- [ ] Get quick create options:
  ```javascript
  frappe.call({
    method: "desk_navbar_extended.api.quick_create.get_quick_create_options"
  });
  ```
- [ ] Verify returns only doctypes user can create
- [ ] Test with restricted user (fewer permissions)

#### 5. Grouped History
- [ ] Access some documents (Sales Orders, Customers, etc.)
- [ ] Call get_recent_activity:
  ```javascript
  frappe.call({
    method: "desk_navbar_extended.api.history.get_recent_activity",
    args: { limit: 20 }
  });
  ```
- [ ] Verify groups by doctype
- [ ] Verify items have proper titles/routes

#### 6. Command Palette
- [ ] Get sources:
  ```javascript
  frappe.call({
    method: "desk_navbar_extended.api.command_palette.get_command_palette_sources"
  });
  ```
- [ ] Verify contains doctypes, saved searches, pins, recent, etc.
- [ ] (If UI ready) Press Ctrl+K and test fuzzy search

#### 7. Notifications Center
- [ ] Create a notification (via any standard Frappe flow)
- [ ] Get notifications:
  ```javascript
  frappe.call({
    method: "desk_navbar_extended.api.notifications.get_notifications",
    args: { limit: 10 }
  });
  ```
- [ ] Verify unread_count is correct
- [ ] Mark as read
- [ ] Verify count decreases

#### 8. KPI Widgets
- [ ] Enable KPI Widgets in Settings
- [ ] Get KPI data:
  ```javascript
  frappe.call({
    method: "desk_navbar_extended.api.kpi.get_kpi_data"
  });
  ```
- [ ] Verify returns role-appropriate KPIs
- [ ] Test with different roles (Sales User, Purchase User, etc.)

#### 9. Help Search
- [ ] Search help:
  ```javascript
  frappe.call({
    method: "desk_navbar_extended.api.help.search_help",
    args: { query: "doctype", limit: 10 }
  });
  ```
- [ ] Verify returns relevant Frappe doc links

#### 10. Feature Gating
- [ ] Disable a feature in Settings
- [ ] Try to call its API
- [ ] Verify throws `PermissionError`
- [ ] Re-enable and verify works

---

## Performance Testing

### Load Testing

```python
# Create load test script: test_load.py
import frappe

def test_search_performance():
    for i in range(100):
        frappe.call(
            "desk_navbar_extended.api.search_filters.search_with_filters",
            query="test",
            limit=20
        )

# Run via bench console
bench --site <site-name> console
>>> from test_load import test_search_performance
>>> test_search_performance()
```

Expected:
- Each search < 100ms
- No memory leaks
- Cache hits after first call

### Analytics

Enable usage analytics in Settings, then:

```sql
-- Check telemetry data
SELECT 
  AVG(execution_ms) as avg_time,
  MAX(execution_ms) as max_time,
  COUNT(*) as total_searches,
  SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors
FROM `tabDesk Navbar Search Metric`
WHERE creation >= DATE_SUB(NOW(), INTERVAL 1 HOUR);
```

---

## Troubleshooting

### Issue: Features not appearing

**Solution**:
1. Check Settings: `bench --site <site-name> console`
   ```python
   >>> settings = frappe.get_single("Desk Navbar Extended Settings")
   >>> print(settings.as_dict())
   ```
2. Verify feature flags are set to 1
3. Run migration: `bench --site <site-name> migrate`

### Issue: Permission errors

**Solution**:
1. Check user roles
2. Verify DocType permissions (User Settings > Role Permissions Manager)
3. Check feature role overrides in Settings

### Issue: Tests failing

**Solution**:
1. Ensure test site has `allow_tests` enabled:
   ```bash
   bench --site <site-name> set-config allow_tests true
   ```
2. Reinstall app:
   ```bash
   bench --site <site-name> reinstall-app desk_navbar_extended
   ```
3. Run tests with verbose output:
   ```bash
   bench --site <site-name> run-tests --app desk_navbar_extended --verbose
   ```

### Issue: Assets not loading

**Solution**:
```bash
bench build --app desk_navbar_extended --force
bench clear-cache
bench restart
```

---

## Development

### Adding a New Feature

1. **Backend**:
   - Add feature flag to Settings JSON
   - Create API module in `desk_navbar_extended/api/`
   - Add permission checks and feature gating
   - Write tests in `desk_navbar_extended/tests/`

2. **Frontend**:
   - Create JS module in `desk_navbar_extended/public/js/`
   - Check feature flag via `get_settings()`
   - Add CSS in `desk_navbar_extended/public/css/`
   - Write QUnit tests in `desk_navbar_extended/public/js/tests/`

3. **Documentation**:
   - Update FEATURES.md
   - Add to README.md
   - Create migration if needed

### Code Quality

```bash
# Format Python
cd /home/frappe/frappe-bench/apps/desk_navbar_extended
black desk_navbar_extended/
isort desk_navbar_extended/

# Lint
flake8 desk_navbar_extended/

# Pre-commit hooks (if configured)
pre-commit run --all-files
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed and formatted
- [ ] Documentation updated
- [ ] Migration tested on staging
- [ ] Performance benchmarks acceptable
- [ ] Security audit complete
- [ ] Backup taken

### Deployment Steps

```bash
# 1. Pull latest code
cd /home/frappe/frappe-bench/apps/desk_navbar_extended
git pull origin main

# 2. Run migration
bench --site <production-site> migrate

# 3. Build assets
bench build --app desk_navbar_extended

# 4. Restart (zero-downtime)
sudo supervisorctl restart <bench-name>:frappe-bench-web
sudo supervisorctl restart <bench-name>:frappe-bench-workers
```

### Post-Deployment Verification

```bash
# Check logs
tail -f /home/frappe/frappe-bench/logs/*.log

# Verify features
bench --site <production-site> console
>>> from desk_navbar_extended.api import get_settings
>>> settings = get_settings()
>>> print(settings['features'])
```

---

## Support

- **Documentation**: [FEATURES.md](./FEATURES.md)
- **Issues**: GitHub Issues
- **Frappe Forum**: [Discuss](https://discuss.frappe.io/)
