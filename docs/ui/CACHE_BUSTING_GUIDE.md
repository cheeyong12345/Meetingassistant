# Browser Cache Clearing Guide

## Why Clear Cache?

When CSS/JavaScript files are updated, browsers may continue serving old cached versions. This prevents users from seeing the latest design changes.

## Quick Solution: Hard Refresh

### Windows/Linux:
- **Chrome/Edge/Firefox**: `Ctrl + Shift + R` or `Ctrl + F5`
- **Opera**: `Ctrl + F5`

### macOS:
- **Chrome/Safari**: `Cmd + Shift + R`
- **Firefox**: `Cmd + Shift + R` or `Cmd + F5`

### Mobile:
- **iOS Safari**: Settings > Safari > Clear History and Website Data
- **Chrome Mobile**: Menu > History > Clear browsing data

## Complete Cache Clear

### Chrome/Edge:
1. Press `Ctrl + Shift + Delete` (Windows) or `Cmd + Shift + Delete` (Mac)
2. Select "Cached images and files"
3. Choose "All time"
4. Click "Clear data"

### Firefox:
1. Press `Ctrl + Shift + Delete` (Windows) or `Cmd + Shift + Delete` (Mac)
2. Check "Cache"
3. Click "Clear Now"

### Safari:
1. Safari menu > Settings > Privacy
2. Click "Manage Website Data"
3. Click "Remove All"

## Developer Tools Method

1. **Open DevTools**: `F12` or `Right-click > Inspect`
2. **Open Network tab**
3. **Right-click Refresh button** > Select "Empty Cache and Hard Reload"

## For Developers: Automatic Cache-Busting

Add version query parameters to CSS/JS links in `/home/amd/Meetingassistant/templates/base.html`:

```html
<!-- Before -->
<link rel="stylesheet" href="/static/css/components.css">

<!-- After -->
<link rel="stylesheet" href="/static/css/components.css?v=2.0.1">
```

Update version number with each deployment.

## Verify Changes Loaded

1. Open DevTools (`F12`)
2. Go to Network tab
3. Refresh page (`Ctrl + Shift + R`)
4. Look for `components.css` in the list
5. Check "Status" column shows `200` (not `304`)
6. Click on `components.css` to view contents
7. Verify the WordPress accordion styles are present (lines 6-102)

## Server-Side Cache Headers (Flask)

Add cache control headers in your Flask app:

```python
from flask import Flask, make_response

@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    return response
```

## WordPress Accordion Styles Checklist

After clearing cache, verify these styles are applied:

✅ **Headers**: Light gray background (#f6f7f7)
✅ **Active header**: White background with blue left border (#2271b1)
✅ **Typography**: 14px, 600 weight, #1d2327 color
✅ **Padding**: 16px 20px
✅ **Icon rotation**: Down arrow rotates 180° when active
✅ **Border**: 1px solid #dcdcde between items

## Test the Fix

1. Clear browser cache completely
2. Navigate to dashboard
3. First accordion item (Meeting Control) should have:
   - White background on header
   - Blue left border (4px, #2271b1)
   - Chevron icon pointing up (rotated 180°)
   - Content visible
4. Other accordion items should have:
   - Light gray background (#f6f7f7)
   - No left border
   - Chevron pointing down
   - Content hidden

## Still Not Working?

1. **Check file contents**: Verify `/home/amd/Meetingassistant/static/css/components.css` has the WordPress styles
2. **Inspect element**: Right-click header > Inspect > Check computed styles
3. **Check console**: Look for CSS loading errors in DevTools Console
4. **Verify path**: Ensure `/static/css/components.css` URL returns correct file
5. **Restart Flask**: Stop and restart the Flask development server

## Files Modified

- `/home/amd/Meetingassistant/static/css/components.css` - Added `.form-help` class, `.form-switch` styles
- `/home/amd/Meetingassistant/templates/dashboard.html` - Added `active` class to first accordion item (line 21)
