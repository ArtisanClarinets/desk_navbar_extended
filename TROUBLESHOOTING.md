# Desk Navbar Extended - Installation & Troubleshooting Guide

## 🚨 **Resolving "Page not found" Error**

If you're experiencing the "Page desk-navbar-extended-settings not found" error, follow these steps:

### **Step 1: Verify App Installation**

```bash
# Check if app is installed on your site
bench --site [your-site-name] list-apps

# If desk_navbar_extended is not listed, install it:
bench --site [your-site-name] install-app desk_navbar_extended
```

### **Step 2: Create Missing Settings Singleton**

Run this in the Frappe console (`bench --site [your-site-name] console`):

```python
# Create the missing singleton if it doesn't exist
from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import get_settings_doc

try:
    settings = get_settings_doc()
    print("Settings singleton exists:", settings.name)
except Exception as e:
    print("Error:", e)
    # Manually create it
    import frappe
    doc = frappe.new_doc("Desk Navbar Extended Settings")
    doc.insert(ignore_permissions=True)
    print("Created settings singleton:", doc.name)
```

### **Step 3: Run Database Patches**

```bash
# Run any pending patches
bench --site [your-site-name] migrate

# Force run our specific patch if needed
bench --site [your-site-name] run-patch desk_navbar_extended.patches.v2_0.ensure_settings_singleton_exists
```

### **Step 4: Clear Cache & Restart**

```bash
# Clear all caches
bench --site [your-site-name] clear-cache

# Rebuild assets
bench build

# Restart services
bench restart
```

### **Step 5: Verify User Permissions**

Ensure your user has the "System Manager" role:

```python
# In Frappe console
import frappe
user = "[your-email@domain.com]"  # Replace with your email
roles = frappe.get_roles(user)
print("User roles:", roles)

# If System Manager is missing, add it:
if "System Manager" not in roles:
    frappe.get_doc("User", user).add_roles("System Manager")
    print("Added System Manager role")
```

---

## 📋 **Complete Fresh Installation Guide**

### **Prerequisites**
- Working Frappe/ERPNext instance
- Database access (MariaDB/MySQL)
- Bench setup completed

### **Installation Steps**

1. **Get the App**
   ```bash
   cd /path/to/your/frappe-bench
   bench get-app desk_navbar_extended [repository-url-or-path]
   ```

2. **Install on Site**
   ```bash
   bench --site [your-site-name] install-app desk_navbar_extended
   ```

3. **Verify Installation**
   ```bash
   # Check if all DocTypes were created
   bench --site [your-site-name] console
   ```
   
   In console:
   ```python
   import frappe
   doctypes = [
       "Desk Navbar Extended Settings",
       "Desk Navbar Feature Role", 
       "Desk Navbar Timezone",
       "Desk Navbar Pin",
       "Desk Navbar Saved Search",
       "Desk Navbar Search Metric"
   ]
   
   for dt in doctypes:
       exists = frappe.db.exists("DocType", dt)
       print(f"{dt}: {'✅' if exists else '❌'}")
   ```

4. **Build Assets**
   ```bash
   bench build
   ```

5. **Access Settings**
   Navigate to: `https://[your-site]/app/desk-navbar-extended-settings`

---

## 🔧 **Production Configuration Checklist**

### **Required Settings Review**

1. **Feature Toggles** (Enable as needed for your organization):
   - ✅ Enable Clock (recommended)
   - ✅ Enable Wide Awesomebar (recommended) 
   - ✅ Enable Smart Search Filters (recommended)
   - ✅ Enable Saved Searches (recommended)
   - ✅ Enable Quick Create (recommended)
   - ✅ Enable Pinned Items (recommended)
   - ✅ Enable Command Palette (recommended)
   - ⚠️ Enable Voice Search (requires external service)
   - ⚠️ Enable Voice Actions (requires external service)
   - ⚠️ Enable Usage Analytics (privacy considerations)

2. **Role-Based Access** (if needed):
   - Configure Feature Role Overrides table
   - Set specific features for specific roles
   - Test with different user roles

3. **External Services** (if using voice features):
   ```python
   # Add to site_config.json or common_site_config.json
   {
       "desk_navbar_transcription_endpoint": "https://your-speech-api.com/transcribe",
       "desk_navbar_transcription_api_key": "your-api-key"
   }
   ```

### **Security Review**

1. **Permissions Check**:
   - Settings accessible only to System Managers ✅
   - Pin/Search data isolated per user ✅
   - No guest access to sensitive endpoints ✅

2. **Input Validation**:
   - All API endpoints validate inputs ✅
   - Rate limiting on search metrics ✅
   - File upload restrictions for voice ✅

3. **Data Privacy**:
   - Search metrics anonymized ✅
   - Voice data requires explicit consent ✅
   - Usage analytics can be disabled ✅

### **Performance Optimization**

1. **Caching Strategy**:
   - Settings cached for 5 minutes ✅
   - Timezone data cached for 1 minute ✅
   - Frontend uses sessionStorage ✅

2. **Asset Optimization**:
   - CSS/JS files properly minified in production
   - Assets served with proper cache headers
   - Consider CDN for static assets

3. **Database Optimization**:
   - Indexes on search metrics table
   - Regular cleanup of old metrics
   - Monitor pin/search data growth

---

## 🚨 **Common Issues & Solutions**

### **Issue: JavaScript Console Errors**

**Symptoms**: Features not working, JS errors in browser console

**Solutions**:
```bash
# 1. Rebuild assets
bench build

# 2. Clear browser cache
# 3. Check for missing JS files in browser Network tab

# 4. Verify all JS files exist:
ls -la apps/desk_navbar_extended/desk_navbar_extended/public/js/
```

### **Issue: CSS Styling Problems**

**Symptoms**: Layout broken, missing styles

**Solutions**:
```bash
# 1. Check CSS files exist
ls -la apps/desk_navbar_extended/desk_navbar_extended/public/css/

# 2. Verify CSS is included in hooks.py
grep -n "app_include_css" apps/desk_navbar_extended/desk_navbar_extended/hooks.py

# 3. Clear cache and rebuild
bench --site [site] clear-cache
bench build
```

### **Issue: Features Not Appearing**

**Symptoms**: New features not showing in UI

**Solutions**:
1. Check feature is enabled in settings
2. Verify user has required role permissions
3. Check browser console for JS errors
4. Ensure frontend modules are loaded

### **Issue: Database Errors**

**Symptoms**: DocType not found, database table errors

**Solutions**:
```bash
# 1. Check if DocTypes exist
bench --site [site] console
```

```python
import frappe
frappe.db.get_list("DocType", filters={"module": "Desk Navbar Extended"})
```

```bash
# 2. Re-run installation if DocTypes missing
bench --site [site] reinstall-app desk_navbar_extended

# 3. Check database tables directly
bench --site [site] mariadb
```

```sql
SHOW TABLES LIKE '%desk_navbar%';
```

---

## 📊 **Monitoring & Maintenance**

### **Health Checks**

Run the production readiness checker regularly:

```bash
cd apps/desk_navbar_extended
python3 check_production_readiness.py
```

### **Regular Maintenance Tasks**

1. **Weekly**:
   - Review search metrics for errors
   - Check disk space usage for uploaded voice files
   - Monitor JavaScript error rates

2. **Monthly**:
   - Clean up old search metrics (>90 days)
   - Review user feedback on new features
   - Update feature toggles based on usage

3. **Quarterly**:
   - Review role-based access controls
   - Security audit of external integrations
   - Performance analysis and optimization

### **Logging & Debugging**

Enable debug logging:

```python
# In site_config.json
{
    "logging": 1,
    "log_level": "DEBUG"
}
```

Check logs:
```bash
tail -f logs/[site].log | grep desk_navbar_extended
```

---

## 🆘 **Emergency Procedures**

### **Disable App Quickly**

If the app causes issues:

```bash
# 1. Remove from hooks (temporarily)
# Comment out app_include_js and app_include_css in hooks.py

# 2. Rebuild without the app assets
bench build

# 3. Restart services  
bench restart
```

### **Rollback Installation**

```bash
# Complete removal (DESTRUCTIVE - will lose all data)
bench --site [site] uninstall-app desk_navbar_extended
```

### **Restore from Backup**

```bash
# If you have a backup before installation
bench --site [site] restore [backup-file]
```

---

**Need More Help?**

- Check the app logs: `logs/[site].log`
- Review browser console errors
- Verify all files exist and permissions are correct
- Test with a fresh user account
- Run the production readiness checker for comprehensive diagnostics