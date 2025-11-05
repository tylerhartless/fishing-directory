# Maintenance Mode

This repo includes a simple maintenance mode implementation for the frontend and backend. Use it when you need to temporarily take the site offline for upgrades or fixes.

## How It Works

When a file named `MAINTENANCE` exists in the document root:
- **Browser requests**: Redirected to `maintenance.html` with HTTP 503 status
- **API requests**: Return JSON error with HTTP 503 status
- **Headers**: Include `Retry-After: 3600` (suggest retry in 1 hour)

The maintenance check happens in two places:
1. **Apache .htaccess**: Redirects browser requests to maintenance.html
2. **PHP config.php**: Returns 503 JSON responses for API endpoints

## Option 1: GitHub Actions (Recommended - No Server Access Needed!)

The easiest way to enable/disable maintenance mode is via GitHub Actions workflows.

### Production Site

Go to: **GitHub Actions → Toggle Production Maintenance Mode**

1. Click **Run workflow**
2. Select action:
   - **enable** - Put site into maintenance mode
   - **disable** - Take site out of maintenance mode
3. Click **Run workflow**

The workflow will automatically:
- Enable: Upload a `MAINTENANCE` file via FTP
- Disable: Delete the `MAINTENANCE` file via FTP

### Staging Site

Go to: **GitHub Actions → Toggle Staging Maintenance Mode**

Same steps as above, but for the staging environment.

## Option 2: Manual (Hostinger File Manager)

If you prefer manual control:

### Enable Maintenance
1. Connect to Hostinger File Manager
2. Navigate to `public_html`
3. Create a new file named `MAINTENANCE` (no extension)
4. Leave the file empty

### Disable Maintenance
1. Connect to Hostinger File Manager
2. Navigate to `public_html`
3. Delete the `MAINTENANCE` file

## Option 3: FTP/SFTP

### Enable Maintenance
```bash
# Create empty MAINTENANCE file
touch MAINTENANCE

# Upload via FTP
ftp YOUR_FTP_SERVER
> cd public_html
> put MAINTENANCE
> quit
```

### Disable Maintenance
```bash
# Connect and delete via FTP
ftp YOUR_FTP_SERVER
> cd public_html
> delete MAINTENANCE
> quit
```

## Verification

After enabling maintenance mode:

**Browser Test:**
```bash
curl -I https://wherecanifish.com
# Should return: HTTP/1.1 503 Service Unavailable
```

**API Test:**
```bash
curl https://wherecanifish.com/api/reports.php
# Should return: {"error":"Site is temporarily down...","maintenance":true}
```

**Visual Test:**
- Open https://wherecanifish.com in your browser
- You should see the maintenance page

## Implementation Details

### File Locations
- Maintenance flag: `/public_html/MAINTENANCE`
- Maintenance page: `/public_html/maintenance.html`

### Response Codes
- **HTTP 503**: Service Unavailable
- **Retry-After**: 3600 seconds (1 hour)

### Maintenance Page
The maintenance page can be customized at `deploy/public_html/maintenance.html`

## Notes

- No IP whitelisting - maintenance mode affects all visitors
- The `MAINTENANCE` file should be empty (the file's existence is the trigger)
- Both .htaccess and PHP check for the file for complete coverage
- Changes take effect immediately
- The maintenance page is styled to match your site's design

## Troubleshooting

**Maintenance mode not working?**
1. Check file name is exactly `MAINTENANCE` (no extension)
2. Check file is in `/public_html/` directory
3. Clear your browser cache
4. Check GitHub Actions logs if using workflows

**Can't disable maintenance mode?**
1. Make sure you deleted the file (not just renamed it)
2. Check file permissions if using FTP
3. Use GitHub Actions workflow to disable if file access is blocked

**GitHub Actions failing?**
1. Check FTP credentials are correct in GitHub Secrets
2. Verify FTP server address and paths
3. Check GitHub Actions logs for specific error messages
