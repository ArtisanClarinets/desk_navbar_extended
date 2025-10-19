#!/usr/bin/env python3
"""
Production Readiness Checker for Desk Navbar Extended

This script performs comprehensive checks and fixes for the app to ensure
it's production-ready. Run this before deploying to production.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add the app to the Python path for imports
app_root = Path(__file__).parent
sys.path.insert(0, str(app_root))

try:
    import frappe
    from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import (
        get_settings_doc,
    )
    FRAPPE_AVAILABLE = True
except ImportError:
    FRAPPE_AVAILABLE = False
    print("⚠️  Frappe not available - some checks will be skipped")


class ProductionReadinessChecker:
    """Comprehensive production readiness checker."""
    
    def __init__(self, app_path: Path):
        self.app_path = app_path
        self.issues = []
        self.fixes_applied = []
        
    def log_issue(self, severity: str, component: str, message: str, fix_available: bool = False):
        """Log an issue with details."""
        self.issues.append({
            "severity": severity,  # CRITICAL, HIGH, MEDIUM, LOW
            "component": component,
            "message": message,
            "fix_available": fix_available
        })
        
    def log_fix(self, component: str, description: str):
        """Log a fix that was applied."""
        self.fixes_applied.append({
            "component": component,
            "description": description
        })
    
    def check_doctype_completeness(self):
        """Check all doctypes are properly configured."""
        print("🔍 Checking DocType completeness...")
        
        # Check Feature Role options
        feature_role_path = self.app_path / "desk_navbar_extended" / "desk_navbar_extended" / "doctype" / "desk_navbar_feature_role" / "desk_navbar_feature_role.json"
        if feature_role_path.exists():
            with open(feature_role_path) as f:
                data = json.load(f)
                
            feature_field = None
            for field in data.get("fields", []):
                if field.get("fieldname") == "feature":
                    feature_field = field
                    break
                    
            if feature_field:
                options = feature_field.get("options", "").split("\n")
                expected_features = [
                    "clock", "voice_search", "wide_awesomebar", "smart_filters", 
                    "saved_searches", "quick_create", "pins", "grouped_history",
                    "command_palette", "density_toggle", "notifications_center",
                    "kpi_widgets", "timezone_switcher", "voice_actions", 
                    "help_search", "layout_bookmarks"
                ]
                
                missing_features = [f for f in expected_features if f not in options]
                if missing_features:
                    self.log_issue("HIGH", "Feature Role DocType", 
                                 f"Missing feature options: {', '.join(missing_features)}", 
                                 fix_available=True)
                else:
                    print("✅ Feature Role DocType has all required options")
                expected_features = [
                    "clock", "voice_search", "wide_awesomebar", "smart_filters", 
                    "saved_searches", "quick_create", "pins", "grouped_history",
                    "command_palette", "density_toggle", "notifications_center",
                    "kpi_widgets", "timezone_switcher", "voice_actions", 
                    "help_search", "layout_bookmarks"
                ]
                
                missing_features = [f for f in expected_features if f not in options]
                if missing_features:
                    self.log_issue("HIGH", "Feature Role DocType", 
                                 f"Missing feature options: {', '.join(missing_features)}", 
                                 fix_available=True)
                else:
                    print("✅ Feature Role DocType has all required options")
                expected_features = [
                    "clock", "voice_search", "wide_awesomebar", "smart_filters", 
                    "saved_searches", "quick_create", "pins", "grouped_history",
                    "command_palette", "density_toggle", "notifications_center",
                    "kpi_widgets", "timezone_switcher", "voice_actions", 
                    "help_search", "layout_bookmarks"
                ]
                
                missing_features = [f for f in expected_features if f not in options]
                if missing_features:
                    self.log_issue("HIGH", "Feature Role DocType", 
                                 f"Missing feature options: {', '.join(missing_features)}", 
                                 fix_available=True)
                else:
                    print("✅ Feature Role DocType has all required options")
        
    def check_api_endpoints(self):
        """Check API endpoint availability and consistency."""
        print("🔍 Checking API endpoints...")
        
        api_path = self.app_path / "desk_navbar_extended" / "api"
        if not api_path.exists():
            self.log_issue("CRITICAL", "API", "API directory missing")
            return
            
        required_apis = ["pins.py", "saved_searches.py", "quick_create.py", "command_palette.py"]
        missing_apis = []
        
        for api_file in required_apis:
            if not (api_path / api_file).exists():
                missing_apis.append(api_file)
                
        if missing_apis:
            self.log_issue("HIGH", "API", f"Missing API modules: {', '.join(missing_apis)}")
    
    def check_frontend_files(self):
        """Check frontend JavaScript and CSS files."""
        print("🔍 Checking frontend files...")
        
        js_path = self.app_path / "desk_navbar_extended" / "public" / "js"
        css_path = self.app_path / "desk_navbar_extended" / "public" / "css"
        
        # Check required JS files from hooks.py
        required_js = [
            "desk_navbar_extended.js", "voice_search.js", "awesomebar_layout.js",
            "keyboard_manager.js", "command_palette.js", "search_filters.js",
            "saved_searches.js", "pins.js", "quick_create.js", "history.js",
            "notifications_center.js", "kpi_widgets.js", "help_search.js", "density_toggle.js"
        ]
        
        missing_js = []
        for js_file in required_js:
            if not (js_path / js_file).exists():
                missing_js.append(js_file)
                
        if missing_js:
            self.log_issue("HIGH", "Frontend", f"Missing JS files: {', '.join(missing_js)}")
            
        # Check CSS files
        required_css = ["awesomebar.css", "desk_navbar_extended.css"]
        missing_css = []
        for css_file in required_css:
            if not (css_path / css_file).exists():
                missing_css.append(css_file)
                
        if missing_css:
            self.log_issue("HIGH", "Frontend", f"Missing CSS files: {', '.join(missing_css)}")
    
    def check_database_state(self):
        """Check database state if Frappe is available."""
        if not FRAPPE_AVAILABLE:
            return
            
        print("🔍 Checking database state...")
        
        try:
            # Check if settings singleton exists
            settings = get_settings_doc()
            if settings:
                print("✅ Settings singleton exists")
            else:
                self.log_issue("CRITICAL", "Database", "Settings singleton missing", fix_available=True)
        except Exception as e:
            self.log_issue("CRITICAL", "Database", f"Cannot access settings: {e}", fix_available=True)
            
        # Check if all required DocTypes exist
        required_doctypes = [
            "Desk Navbar Extended Settings",
            "Desk Navbar Feature Role", 
            "Desk Navbar Timezone",
            "Desk Navbar Pin",
            "Desk Navbar Saved Search",
            "Desk Navbar Search Metric"
        ]
        
        for doctype in required_doctypes:
            if not frappe.db.exists("DocType", doctype):
                self.log_issue("CRITICAL", "Database", f"DocType '{doctype}' missing")
    
    def check_permissions(self):
        """Check DocType permissions."""
        print("🔍 Checking permissions...")
        
        # Check if System Manager has access to settings
        settings_path = self.app_path / "desk_navbar_extended" / "desk_navbar_extended" / "doctype" / "desk_navbar_extended_settings" / "desk_navbar_extended_settings.json"
        
        if settings_path.exists():
            with open(settings_path) as f:
                data = json.load(f)
                
            permissions = data.get("permissions", [])
            has_system_manager = any(p.get("role") == "System Manager" for p in permissions)
            
            if not has_system_manager:
                self.log_issue("HIGH", "Permissions", "System Manager role missing from settings permissions")
        
    def check_hooks_consistency(self):
        """Check hooks.py for consistency."""
        print("🔍 Checking hooks configuration...")
        
        hooks_path = self.app_path / "desk_navbar_extended" / "hooks.py"
        if not hooks_path.exists():
            self.log_issue("CRITICAL", "Hooks", "hooks.py missing")
            return
            
        with open(hooks_path) as f:
            content = f.read()
            
        # Check for after_install hook
        if "after_install" not in content:
            self.log_issue("HIGH", "Hooks", "after_install hook missing")
            
        # Check for app_include_css and app_include_js
        if "app_include_css" not in content:
            self.log_issue("MEDIUM", "Hooks", "app_include_css missing")
            
        if "app_include_js" not in content:
            self.log_issue("MEDIUM", "Hooks", "app_include_js missing")
    
    def check_translations(self):
        """Check translation files."""
        print("🔍 Checking translations...")
        
        translations_path = self.app_path / "desk_navbar_extended" / "translations"
        if not translations_path.exists():
            self.log_issue("MEDIUM", "Translations", "Translations directory missing")
            return
            
        en_csv = translations_path / "en.csv"
        if not en_csv.exists():
            self.log_issue("MEDIUM", "Translations", "English translations (en.csv) missing")
    
    def run_all_checks(self):
        """Run all production readiness checks."""
        print("🚀 Starting Production Readiness Check for Desk Navbar Extended\\n")
        
        self.check_doctype_completeness()
        self.check_api_endpoints()
        self.check_frontend_files()
        self.check_database_state()
        self.check_permissions()
        self.check_hooks_consistency()
        self.check_translations()
        
        self.print_report()
    
    def print_report(self):
        """Print comprehensive report."""
        print("\\n" + "="*60)
        print("📊 PRODUCTION READINESS REPORT")
        print("="*60)
        
        if not self.issues:
            print("✅ All checks passed! App is production-ready.")
            return
            
        # Group by severity
        by_severity = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}
        for issue in self.issues:
            by_severity[issue["severity"]].append(issue)
            
        total_issues = len(self.issues)
        critical_count = len(by_severity["CRITICAL"])
        high_count = len(by_severity["HIGH"])
        
        print(f"\\n📈 SUMMARY: {total_issues} issues found")
        print(f"   🔴 Critical: {critical_count}")
        print(f"   🟡 High: {high_count}")
        print(f"   🔵 Medium: {len(by_severity['MEDIUM'])}")
        print(f"   ⚪ Low: {len(by_severity['LOW'])}")
        
        for severity, issues in by_severity.items():
            if not issues:
                continue
                
            severity_icon = {"CRITICAL": "🔴", "HIGH": "🟡", "MEDIUM": "🔵", "LOW": "⚪"}
            print(f"\\n{severity_icon[severity]} {severity} ISSUES:")
            
            for issue in issues:
                fix_text = " [FIXABLE]" if issue["fix_available"] else ""
                print(f"   • {issue['component']}: {issue['message']}{fix_text}")
        
        print("\\n" + "="*60)
        if critical_count > 0:
            print("❌ CRITICAL issues must be resolved before production deployment!")
        elif high_count > 0:
            print("⚠️  HIGH priority issues should be resolved before production deployment.")
        else:
            print("✅ No critical issues found. Review medium/low priority items as needed.")
        print("="*60)


def main():
    """Main entry point."""
    app_path = Path(__file__).parent
    checker = ProductionReadinessChecker(app_path)
    checker.run_all_checks()


if __name__ == "__main__":
    main()