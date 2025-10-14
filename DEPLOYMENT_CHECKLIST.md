# Deployment Checklist - Desk Navbar Extended v2.0

## Pre-Deployment

### Code Quality
- [x] All tests passing (20/20)
- [x] Code formatted (black, isort, flake8)
- [x] No TODO comments
- [x] No placeholder code
- [x] Security audit complete
- [x] Documentation complete

### Testing
- [x] Unit tests pass on dev environment
- [ ] Unit tests pass on staging environment
- [ ] Manual testing complete
- [ ] Performance benchmarks acceptable
- [ ] Mobile responsive verified
- [ ] Browser compatibility tested

### Backup & Safety
- [ ] Production database backed up
- [ ] Rollback plan documented
- [ ] Feature flags tested (enable/disable)
- [ ] Monitoring alerts configured

---

## Deployment Steps

### 1. Pull Latest Code
```bash
cd /home/frappe/frappe-bench/apps/desk_navbar_extended
git pull origin main
```

### 2. Run Migration
```bash
cd /home/frappe/frappe-bench
bench --site <production-site> migrate
```

**Expected Output**:
- ✅ Migration script executes successfully
- ✅ New feature flags added to Settings
- ✅ New DocTypes created
- ✅ No errors in migration log

### 3. Build Assets
```bash
bench build --app desk_navbar_extended
```

### 4. Restart Services
```bash
# Option A: Supervisor (zero-downtime)
sudo supervisorctl restart <bench-name>:frappe-bench-web
sudo supervisorctl restart <bench-name>:frappe-bench-workers

# Option B: Bench (simpler, brief downtime)
bench restart
```

---

## Post-Deployment Verification

### Immediate Checks (0-5 minutes)

#### 1. Site Accessibility
- [ ] Site loads without errors
- [ ] No console errors in browser
- [ ] Desk loads properly

#### 2. Settings Verification
```bash
bench --site <site> console
```
```python
from desk_navbar_extended.api import get_settings
settings = get_settings()
print(f"Features loaded: {len(settings['features'])}")
# Expected: 18 features
```

#### 3. Feature Flags
- [ ] All new features visible in Settings
- [ ] Can toggle features on/off
- [ ] Changes take effect immediately

#### 4. API Endpoints
Test via console:
```python
# Test search filters
from desk_navbar_extended.api import search_filters
result = search_filters.search_with_filters(query="test", limit=5)
print(f"Search returned {result['count']} results")

# Test saved searches
from desk_navbar_extended.api import saved_searches
searches = saved_searches.list_saved_searches()
print(f"Saved searches accessible: {len(searches)}")

# Test pins
from desk_navbar_extended.api import pins
user_pins = pins.list_pins()
print(f"Pins accessible: {len(user_pins)}")
```

### Monitoring (First Hour)

#### Error Rates
```sql
-- Check for errors in telemetry
SELECT 
  COUNT(*) as total_searches,
  SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors,
  ROUND(SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as error_rate
FROM `tabDesk Navbar Search Metric`
WHERE creation >= DATE_SUB(NOW(), INTERVAL 1 HOUR);
```

**Expected**: Error rate < 5%

#### Performance
```sql
-- Check API performance
SELECT 
  AVG(execution_ms) as avg_ms,
  MAX(execution_ms) as max_ms,
  MIN(execution_ms) as min_ms
FROM `tabDesk Navbar Search Metric`
WHERE creation >= DATE_SUB(NOW(), INTERVAL 1 HOUR);
```

**Expected**: avg_ms < 200, max_ms < 1000

#### Usage
```sql
-- Check feature adoption
SELECT COUNT(DISTINCT owner) as active_users
FROM `tabDesk Navbar Saved Search`
WHERE creation >= DATE_SUB(NOW(), INTERVAL 1 DAY);
```

### Extended Monitoring (First 24 Hours)

- [ ] No increase in error logs
- [ ] Performance metrics within acceptable range
- [ ] User feedback collected
- [ ] Feature adoption tracked
- [ ] No security incidents

---

## Rollback Procedure

### If Critical Issues Arise

#### Option 1: Disable Features (Recommended)
```bash
bench --site <site> console
```
```python
settings = frappe.get_single("Desk Navbar Extended Settings")

# Disable problematic features
settings.enable_smart_filters = 0
settings.enable_saved_searches = 0
settings.enable_pins = 0
# ... disable others as needed

settings.flags.ignore_permissions = True
settings.save()
frappe.db.commit()
```

#### Option 2: Code Rollback (If Necessary)
```bash
# Revert to previous version
cd /home/frappe/frappe-bench/apps/desk_navbar_extended
git log --oneline -10  # Find previous commit
git checkout <previous-commit-hash>

# Rebuild and restart
bench build --app desk_navbar_extended
bench restart
```

**Note**: Code rollback is rarely needed since features can be disabled individually.

---

## User Communication

### Announcement Template

**Subject**: New Features Available - Desk Navbar Extended v2.0

**Body**:
```
Hi Team,

We've just deployed Desk Navbar Extended v2.0, bringing 14 new productivity features:

✨ New Features:
- Smart Search Filters - Find documents faster with advanced filtering
- Saved Searches - Save your frequent searches for quick access
- Quick Create - One-click document creation
- Pinned Items - Pin your most-used pages
- KPI Widgets - See key metrics at a glance
- And 9 more!

📖 Learn More:
- Feature Documentation: [link to FEATURES.md]
- Quick Start Guide: [link to docs]

🔧 Configuration:
System Managers can enable/disable features in:
Desk > Desk Navbar Extended Settings

All features are enabled by default except:
- KPI Widgets (opt-in)
- Voice Actions (coming soon)
- Layout Bookmarks (coming soon)

Questions? Reply to this email or create a support ticket.

Happy productivity!
- IT Team
```

---

## Success Criteria

Deployment is considered successful when:

- [x] ✅ All tests passing (20/20)
- [ ] ⏳ Migration completed without errors
- [ ] ⏳ Site accessible and functional
- [ ] ⏳ No critical errors in first hour
- [ ] ⏳ Performance within acceptable range
- [ ] ⏳ Error rate < 5%
- [ ] ⏳ Users able to access new features
- [ ] ⏳ Settings configurable
- [ ] ⏳ No security incidents
- [ ] ⏳ Positive user feedback

---

## Emergency Contacts

- **Primary**: [Your Name/Email]
- **Backup**: [Backup Contact]
- **Frappe Support**: support@frappe.io
- **Community**: https://discuss.frappe.io/

---

## Notes

- **Estimated Downtime**: < 2 minutes (during restart only)
- **Best Deployment Time**: Off-peak hours or maintenance window
- **Required Permissions**: Bench access, database backup permissions
- **Database Changes**: Yes (new DocTypes, settings migration)
- **Breaking Changes**: None
- **Backward Compatibility**: 100%

---

## Post-Deployment Tasks

### Week 1
- [ ] Monitor error rates daily
- [ ] Collect user feedback
- [ ] Document common issues
- [ ] Create FAQ if needed

### Week 2-4
- [ ] Analyze feature adoption metrics
- [ ] Optimize based on usage patterns
- [ ] Plan Phase 2 features
- [ ] Consider user requests

---

## Lessons Learned

(To be filled after deployment)

- What went well?
- What could be improved?
- Unexpected issues?
- User feedback themes?
