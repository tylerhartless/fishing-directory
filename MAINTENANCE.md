# Maintenance mode

This repo includes a simple maintenance-mode implementation for the frontend and backend. Use it when you need to temporarily take the site offline for upgrades or fixes.

How it works
- The PHP bootstrap in `backend/api/config.php` checks for a file named `MAINTENANCE` in several candidate locations (backend root, `deploy/public_html`, and the webserver `DOCUMENT_ROOT`). If present it returns HTTP 503 for API calls and serves `maintenance.html` for browser requests. It respects a `MAINTENANCE_WHITELIST` file containing one IP per line.
- The Apache rule in `deploy/public_html/.htaccess` will also redirect requests to `maintenance.html` with a 503 when `MAINTENANCE` exists. You can whitelist IPs by adding `SetEnvIf Remote_Addr "^1\.2\.3\.4$" allow_maintenance=1` lines.

Enable maintenance (Hostinger)
1. Connect via Hostinger File Manager or SFTP/FTP to your site root (usually `public_html`).
2. Create an empty file named `MAINTENANCE` in the document root (or upload the file from the repo's `deploy/public_html`):

   - Using File Manager: New file -> name `MAINTENANCE` (no extension).
   - Using SSH / SFTP: `touch public_html/MAINTENANCE`

3. (Optional) To allow your IP to access the site during maintenance, create `MAINTENANCE_WHITELIST` in the same location and add your IP on a single line. Example:

   203.0.113.42

4. Verify:
   - Browser: open your domain — you should see `maintenance.html` and HTTP status 503.
   - API: curl your API endpoint — you should get HTTP 503 and a JSON error.

Disable maintenance
- Delete the `MAINTENANCE` file (and optionally `MAINTENANCE_WHITELIST`) from your document root.

Notes
- The `.htaccess` rewrite rule provides a server-level shortcut. The PHP check ensures API endpoints return 503 even if they bypass the rewrite (useful if the API runs under a subdirectory or separate subdomain).
- The whitelist in PHP does exact IP match only. If you need CIDR support, expand the PHP logic or whitelist at the server/network level.
- Adjust the `maintenance.html` page to include an ETA, contact info, or status link.

If you want, I can also add a short script (or GitHub Action) to toggle maintenance on/off automatically during deploys.
