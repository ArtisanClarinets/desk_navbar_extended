# Manual Feature Testing Checklist

**App**: Desk Navbar Extended v2.0  
**Site**: repair.artisanclarinets.com  
**Date**: October 25, 2025  
**Tester**: _____________

---

## Pre-Test Setup

- [ ] Cache cleared: `bench --site <site> clear-cache`
- [ ] Assets rebuilt: `bench build --app desk_navbar_extended`
- [ ] All features enabled in settings
- [ ] Browser console open (F12)
- [ ] Test user logged in

---

## Feature 1: Clock Display

**Settings Field**: `enable_clock`  
**Expected**: Clock dropdown in navbar

### Clock Display Test Steps

1. [ ] Look for "Show Time" in navbar dropdown (top-right user menu)
2. [ ] Click "Show Time"
3. [ ] **Expected**: Panel appears with:
   - Current time in user timezone
   - System time
   - Any configured additional timezones
   - Calendar excerpts (if enabled)

### Pass Criteria

- [ ] Clock panel displays
- [ ] Times update every second
- [ ] Time format matches settings (12h/24h)
- [ ] Panel closes when clicked outside

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 2: Voice Search

**Settings Field**: `enable_voice_search`  
**Expected**: Microphone button next to search bar

### Voice Search Test Steps

1. [ ] Look for 🎤 button next to awesomebar search input
2. [ ] Click microphone button
3. [ ] **Expected**: Recording starts (button changes state)
4. [ ] Speak a search term (e.g., "Sales Invoice")
5. [ ] Click button again to stop
6. [ ] **Expected**: Search triggered with transcribed text

### Pass Criteria

- [ ] Mic button visible and clickable
- [ ] Recording indicator shows
- [ ] Browser asks for mic permission (first time)
- [ ] Stop button works
- [ ] Status message updates
- [ ] ESC key cancels recording

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 3: Wide Awesomebar

**Settings Field**: `enable_wide_awesomebar`  
**Expected**: Search bar is wider (560px default)

### Wide Awesomebar Test Steps

1. [ ] Inspect awesomebar search input
2. [ ] **Expected**: Width is ~560px (or configured value)
3. [ ] Resize browser to <768px width
4. [ ] **Expected**: Awesomebar collapses (if mobile_collapse enabled)

### Pass Criteria

- [ ] Search bar is visibly wider than default
- [ ] Width matches setting (560px default)
- [ ] Mobile collapse works correctly
- [ ] No layout breaking

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 4: Smart Search Filters

**Settings Field**: `enable_smart_filters`  
**Expected**: Filter chips above search bar

### Smart Search Filters Test Steps

1. [ ] Look for filter UI above awesomebar
2. [ ] **Expected**: See:
   - DocType dropdown
   - Owner text input
   - Date range inputs (From/To)
   - Clear button
3. [ ] Select a DocType filter (e.g., "Sales Invoice")
4. [ ] Search for something
5. [ ] **Expected**: Results filtered by DocType

### Pass Criteria

- [ ] Filter bar displays correctly
- [ ] DocType dropdown populated
- [ ] Owner filter works
- [ ] Date range filters work
- [ ] Clear button resets all filters
- [ ] Filters apply to search results

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 5: Saved Searches

**Settings Field**: `enable_saved_searches`  
**Expected**: "Saved" dropdown button near search

### Saved Searches Test Steps

1. [ ] Look for "Saved" button (bookmark icon) near awesomebar
2. [ ] Enter a search query in awesomebar
3. [ ] Click "Saved" dropdown
4. [ ] Click "Save Current Search"
5. [ ] **Expected**: Prompt for search name
6. [ ] Enter name and save
7. [ ] **Expected**: Search appears in "Saved" dropdown
8. [ ] Click saved search
9. [ ] **Expected**: Search query loaded into awesomebar

### Pass Criteria

- [ ] Saved dropdown visible
- [ ] Save current search works
- [ ] Saved searches list displays
- [ ] Loading saved search works
- [ ] Delete saved search works
- [ ] Loading indicator shows during API calls

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 6: Quick Create

**Settings Field**: `enable_quick_create`  
**Expected**: "Quick Create" button in navbar

### Quick Create Test Steps

1. [ ] Look for "Quick Create" button (+ icon) near search
2. [ ] Click button
3. [ ] **Expected**: Dropdown menu of DocTypes
4. [ ] Click any DocType (e.g., "Sales Invoice")
5. [ ] **Expected**: New document form opens

### Pass Criteria

- [ ] Quick Create button visible
- [ ] Dropdown shows DocTypes user can create
- [ ] Icons display correctly
- [ ] Clicking DocType opens new form
- [ ] No console errors

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 7: Pins (Favorites Bar)

**Settings Field**: `enable_pins`  
**Expected**: Pin bar below breadcrumbs

### Pins Test Steps

1. [ ] Look for horizontal pin bar below navbar breadcrumbs
2. [ ] **Expected**: See "+ Add Pin" button
3. [ ] Click "+ Add Pin"
4. [ ] **Expected**: Dialog with fields:
   - Label (required)
   - DocType (required)
   - Document Name (optional)
   - Custom Route (optional)
   - Icon (default: fa fa-star)
5. [ ] Fill in and save
6. [ ] **Expected**: Pin appears in bar
7. [ ] Click pin
8. [ ] **Expected**: Navigate to pinned item
9. [ ] Hover over pin, click X button
10. [ ] **Expected**: Pin removed

### Pass Criteria

- [ ] Pin bar visible
- [ ] Add pin dialog works
- [ ] Pin displays correctly with icon
- [ ] Clicking pin navigates
- [ ] Delete pin works
- [ ] Pins persist on page reload

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 8: Grouped History

**Settings Field**: `enable_grouped_history`  
**Expected**: "History" dropdown in navbar

### Grouped History Test Steps

1. [ ] Look for "History" button (clock icon) in navbar
2. [ ] Click button
3. [ ] **Expected**: Dropdown shows recent activity grouped by DocType
4. [ ] Navigate to a few documents
5. [ ] Click History button again
6. [ ] **Expected**: Recent items appear, grouped by DocType

### Pass Criteria

- [ ] History dropdown visible
- [ ] Items grouped by DocType/app
- [ ] Shows icons for each group
- [ ] Badge shows count per group
- [ ] Clicking item navigates to document
- [ ] Recent items appear first

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 9: Command Palette

**Settings Field**: `enable_command_palette`  
**Expected**: Ctrl+K opens command palette

### Command Palette Test Steps

1. [ ] Press **Ctrl+K** (Windows/Linux) or **Cmd+K** (Mac)
2. [ ] **Expected**: Modal opens with:
   - Search input (focused)
   - Search icon
   - ESC hint
3. [ ] Type "sales" or any search term
4. [ ] **Expected**: Fuzzy search results appear
5. [ ] Use ↑↓ arrow keys to navigate
6. [ ] Press Enter to select
7. [ ] **Expected**: Navigate to selected item
8. [ ] Press Ctrl+K again, then ESC
9. [ ] **Expected**: Modal closes

### Pass Criteria

- [ ] Ctrl+K/Cmd+K opens palette
- [ ] Search input auto-focused
- [ ] Fuzzy search works
- [ ] Arrow key navigation works
- [ ] Enter key selects item
- [ ] ESC key closes palette
- [ ] Results grouped by category
- [ ] Backdrop blur effect

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 10: Density Toggle

**Settings Field**: `enable_density_toggle`  
**Expected**: Density toggle button in navbar

### Density Toggle Test Steps

1. [ ] Look for density toggle button (compress icon) in navbar-right
2. [ ] Click button
3. [ ] **Expected**: UI switches to compact mode
   - Smaller padding
   - Tighter spacing
   - Body has `.density-compact` class
4. [ ] Click button again
5. [ ] **Expected**: UI switches back to comfortable mode
   - Body has `.density-comfortable` class

### Pass Criteria

- [ ] Toggle button visible
- [ ] Icon changes between compress/expand
- [ ] Clicking toggles body class
- [ ] Preference saves to localStorage
- [ ] Preference persists on page reload
- [ ] All UI elements adapt to density

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 11: Notifications Center

**Settings Field**: `enable_notifications_center`  
**Expected**: Bell icon in navbar

### Notifications Center Test Steps

1. [ ] Look for bell icon (fa-bell) in navbar-right
2. [ ] **Expected**: Badge shows unread count (if any)
3. [ ] Click bell icon
4. [ ] **Expected**: Dropdown panel shows:
   - "Notifications" header
   - "Mark all read" button
   - List of notifications
5. [ ] Click "Mark read" on a notification
6. [ ] **Expected**: Notification marked read, badge updates
7. [ ] Click "Mark all read"
8. [ ] **Expected**: All notifications marked, badge disappears

### Pass Criteria

- [ ] Bell icon visible
- [ ] Unread count badge accurate
- [ ] Notifications list displays
- [ ] Mark read works
- [ ] Mark all read works
- [ ] Empty state shows if no notifications

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 12: KPI Widgets

**Settings Field**: `enable_kpi_widgets`  
**Expected**: KPI widgets in navbar (if configured)

### KPI Widgets Test Steps

1. [ ] Look for KPI widgets before breadcrumbs
2. [ ] **Expected**: Widgets show:
   - Icon
   - Value/metric
   - Label
3. [ ] Click a KPI widget
4. [ ] **Expected**: Navigate to configured route
5. [ ] Wait configured refresh interval (default 5 min)
6. [ ] **Expected**: KPI values auto-refresh

### Pass Criteria

- [ ] KPI container displays
- [ ] Widgets render correctly
- [ ] Icons and values visible
- [ ] Clicking navigates to route
- [ ] Auto-refresh works
- [ ] Loading states handled

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 13: Help Search

**Settings Field**: `enable_help_search`  
**Expected**: Shift+? opens help modal

### Help Search Test Steps

1. [ ] Press **Shift+?** (Shift and question mark)
2. [ ] **Expected**: Help modal opens with:
   - "Help & Documentation" header
   - Search input
   - Close button (×)
3. [ ] Type a search term (e.g., "invoice")
4. [ ] **Expected**: Help articles appear
5. [ ] Click a help article
6. [ ] **Expected**: Article opens (internal or external)
7. [ ] Click close button or backdrop
8. [ ] **Expected**: Modal closes

### Pass Criteria

- [ ] Shift+? opens modal
- [ ] Search input works
- [ ] Results display correctly
- [ ] Results grouped by type (articles, docs, links)
- [ ] External links open in new tab
- [ ] Modal closes properly
- [ ] No scroll issues

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Feature 14: Usage Analytics

**Settings Field**: `enable_usage_analytics`  
**Expected**: Search metrics captured silently

### Usage Analytics Test Steps

1. [ ] Perform several searches in awesomebar
2. [ ] Open **Desk Navbar Search Metric** DocType list
3. [ ] **Expected**: Recent searches logged with:
   - Timestamp
   - Search length
   - Execution time (ms)
   - Status (success/error)
4. [ ] Cause a search error (network timeout, etc.)
5. [ ] **Expected**: Error logged with error message

### Pass Criteria

- [ ] Metrics logged silently (no UI impact)
- [ ] Timestamp accurate
- [ ] Search length captured
- [ ] Execution time captured
- [ ] Success/error status correct
- [ ] Error messages truncated to 140 chars
- [ ] No performance impact on search
- [ ] Actor hash anonymized

### Issues Found

```
Issue #:
Description:
Severity: [ ] P0  [ ] P1  [ ] P2  [ ] P3
```

---

## Browser Console Check

Open browser console (F12) and check for:

### Errors

```
[ ] No console errors
[ ] No 404s (missing files)
[ ] No API failures (500 errors)
[ ] No unhandled promise rejections

List any errors found:
1. 
2.
3.
```

### Warnings

```
[ ] No excessive warnings
[ ] No deprecation warnings

List any warnings:
1.
2.
```

### Network Tab

```
[ ] All JS files load successfully
[ ] All API calls return 200
[ ] No unnecessary duplicate calls
[ ] Response times acceptable (<500ms)
```

---

## Settings Toggle Test

### Enable/Disable Test

1. [ ] Go to **Desk Navbar Extended Settings**
2. [ ] Disable `enable_command_palette`
3. [ ] Save and reload page
4. [ ] **Expected**: Ctrl+K does nothing
5. [ ] Re-enable `enable_command_palette`
6. [ ] Save and reload
7. [ ] **Expected**: Ctrl+K works again

Repeat for 3 other features:

- [ ] Feature: _________________ (PASS/FAIL)
- [ ] Feature: _________________ (PASS/FAIL)
- [ ] Feature: _________________ (PASS/FAIL)

---

## Role-Based Access Test

### Test with Non-Admin User

1. [ ] Create test user with limited roles
2. [ ] Configure role overrides in settings (optional)
3. [ ] Log in as test user
4. [ ] Verify feature visibility matches permissions

---

## Mobile/Responsive Test

### Desktop (1920px)

- [ ] All features visible
- [ ] No layout issues
- [ ] Proper spacing

### Tablet (768px)

- [ ] Layout adapts correctly
- [ ] Awesomebar collapses (if enabled)
- [ ] Touch targets adequate

### Mobile (375px)

- [ ] Critical features accessible
- [ ] No horizontal scroll
- [ ] Touch-friendly

---

## Performance Test

### Page Load

- [ ] Open site with network throttling (Fast 3G)
- [ ] Measure time to interactive
- [ ] **Target**: <100ms additional load time

### Runtime Performance

- [ ] Open Chrome DevTools Performance
- [ ] Record 10 seconds of interaction
- [ ] Check for:
  - [ ] No memory leaks
  - [ ] Smooth 60fps scrolling
  - [ ] No long tasks (>50ms)

---

## Final Checklist

- [ ] All 14 features tested individually
- [ ] All features work as expected
- [ ] No console errors
- [ ] Settings toggles work
- [ ] Performance acceptable
- [ ] Mobile responsive
- [ ] Documentation accurate

---

## Summary

**Total Features Tested**: ___/ 14  
**Features Passing**:___ / 14  
**Critical Issues (P0)**: ___  
**High Priority Issues (P1)**:___  
**Medium Issues (P2)**: ___  
**Low Issues (P3)**:___

**Overall Status**: [ ] PASS  [ ] FAIL  [ ] PASS WITH ISSUES

**Production Ready**: [ ] YES  [ ] NO  [ ] WITH CAVEATS

---

## Tester Sign-off

**Name**: _______________________  
**Date**: _______________________  
**Signature**: ___________________
