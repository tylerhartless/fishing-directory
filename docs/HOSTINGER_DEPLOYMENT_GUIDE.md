# Hostinger Deployment Guide - wherecanifish.com

**Estimated time: 15-20 minutes**

Your deployment package is ready in the `deploy/` folder!

## Pre-Deployment Checklist

- [ ] Hostinger account active
- [ ] wherecanifish.com domain pointed to Hostinger
- [ ] Access to Hostinger cPanel/hPanel
- [ ] MySQL database credentials from Hostinger

---

## Step 1: Create MySQL Database (5 minutes)

1. **Log into Hostinger hPanel**
   - Go to https://hpanel.hostinger.com

2. **Navigate to Databases**
   - Click on "Databases" → "MySQL Databases"

3. **Create New Database**
   - Database name: `u123456789_fishing` (or similar - Hostinger adds prefix)
   - Click "Create"

4. **Create Database User**
   - Username: `u123456789_fish` (or similar)
   - Password: Generate strong password (save it!)
   - Click "Create User"

5. **Grant Privileges**
   - Select the user
   - Select the database
   - Grant "ALL PRIVILEGES"
   - Click "Add"

6. **Save These Credentials!**
   ```
   DB_HOST: localhost
   DB_USER: u123456789_fish
   DB_PASS: [your generated password]
   DB_NAME: u123456789_fishing
   ```

---

## Step 2: Import Database (5 minutes)

1. **Open phpMyAdmin**
   - In hPanel, go to "Databases" → "phpMyAdmin"
   - Login using your database credentials

2. **Select Your Database**
   - Click on your database name in the left sidebar

3. **Import SQL File**
   - Click the "Import" tab at the top
   - Click "Choose File"
   - Select `deploy/database.sql` (1.9 MB)
   - Scroll down and click "Import"
   - Wait for success message

4. **Verify Import**
   - Click on your database in the left sidebar
   - You should see tables:
     - fishing_spots (1,099 rows)
     - fishing_reports
     - spot_votes
     - fish_habitat_structures

---

## Step 3: Configure Backend API (2 minutes)

1. **Edit config.php**
   - On your computer, open `deploy/public_html/api/config.php`
   - Update these lines with YOUR database credentials:

   ```php
   define('DB_HOST', 'localhost');
   define('DB_USER', 'u123456789_fish');      // YOUR username
   define('DB_PASS', 'YOUR_PASSWORD_HERE');    // YOUR password
   define('DB_NAME', 'u123456789_fishing');    // YOUR database name
   ```

   - Save the file

---

## Step 4: Upload Files (5-10 minutes)

### Option A: File Manager (Recommended for beginners)

1. **Open File Manager**
   - In hPanel, go to "Files" → "File Manager"

2. **Navigate to public_html**
   - Click on `public_html` folder
   - **DELETE** any default files (index.html, etc.)

3. **Upload Files**
   - Click "Upload" button
   - Drag and drop the ENTIRE contents of `deploy/public_html/` folder
   - This includes:
     - All HTML files
     - \_assets/ folder
     - api/ folder
     - data/ folder
     - .htaccess file (make sure this uploads!)
   - Wait for upload to complete (~5-10 minutes for 1,102 files)

4. **Verify Upload**
   - You should see:
     ```
     public_html/
       ├── index.html
       ├── texas/
       ├── spots/
       ├── api/
       ├── data/
       ├── _assets/
       └── .htaccess
     ```

### Option B: FTP (Faster for large uploads)

1. **Get FTP Credentials**
   - In hPanel, go to "Files" → "FTP Accounts"
   - Use the main FTP account or create a new one

2. **Connect with FileZilla** (or any FTP client)
   - Host: ftp.wherecanifish.com
   - Username: (from Hostinger)
   - Password: (from Hostinger)
   - Port: 21

3. **Upload**
   - Navigate to `/public_html` on remote
   - Delete any default files
   - Upload entire contents of `deploy/public_html/`

---

## Step 5: Configure Domain & SSL (2 minutes)

1. **Point Domain**
   - In hPanel, go to "Domains"
   - Add wherecanifish.com
   - Hostinger will provide nameservers or auto-configure if domain was purchased through them

2. **Enable SSL (HTTPS)**
   - In hPanel, go to "Domains" → "SSL"
   - Click "Install SSL" for wherecanifish.com
   - Select "Free Let's Encrypt SSL"
   - Wait 10-15 minutes for SSL to activate

3. **Force HTTPS** (after SSL is active)
   - Edit `public_html/.htaccess`
   - Uncomment these lines (remove the # symbols):
     ```apache
     # RewriteCond %{HTTPS} off
     # RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
     ```
   - Save

---

## Step 6: Test Your Site! (2 minutes)

1. **Visit Your Site**
   - Go to https://wherecanifish.com
   - You should see the homepage!

2. **Test Pages**
   - Homepage: https://wherecanifish.com
   - Texas page: https://wherecanifish.com/texas
   - Spots listing: https://wherecanifish.com/spots
   - Example spot: https://wherecanifish.com/texas/travis/lake-travis-travis-0755

3. **Test API**
   - Open browser console (F12)
   - On any spot page, check if fishing reports load
   - Check Network tab for any API errors

4. **Common Issues**
   - **500 Error**: Check config.php database credentials
   - **403 Error**: Check file permissions (should be 644 for files, 755 for folders)
   - **404 for API**: Make sure api/.htaccess uploaded correctly
   - **CSS not loading**: Clear browser cache, check \_assets/ folder uploaded

---

## Troubleshooting

### Database Connection Errors

If you see "Database connection failed":

1. Double-check config.php credentials match exactly
2. Verify database user has ALL PRIVILEGES
3. Try connecting via phpMyAdmin with same credentials

### File Permissions

If PHP files won't execute:

```bash
# Via File Manager, select files and set:
Files: 644
Folders: 755
```

### API CORS Errors

If API calls fail from frontend:

1. Check that config.php has correct allowed_origins
2. Should include:
   ```php
   'https://wherecanifish.com',
   'https://www.wherecanifish.com'
   ```

---

## Performance Optimization (Optional)

### Enable Caching

In hPanel:
- Go to "Advanced" → "Cache"
- Enable all caching options

### Enable CDN

In hPanel:
- Go to "Advanced" → "CDN"
- Enable Cloudflare integration (free)

---

## Post-Deployment

### Monitor Your Site

1. **Set up Google Analytics**
   - Add tracking code to frontend if desired

2. **Check Error Logs**
   - In hPanel: "Advanced" → "Error Logs"
   - Check for any PHP errors

3. **Test Database**
   - Try submitting a fishing report
   - Try voting on a spot
   - Verify data saves correctly

---

## Your Site Is Live!

Congratulations! wherecanifish.com is now live with:

- ✅ 1,099 fishing spots across Texas
- ✅ Interactive maps
- ✅ Fishing reports system
- ✅ Community voting
- ✅ Fast static site (1,102 pages)
- ✅ Small database (3.5 MB)
- ✅ SSL/HTTPS enabled

---

## Need Help?

**Hostinger Support:**
- 24/7 live chat in hPanel
- Knowledge base: https://support.hostinger.com

**Common Hostinger Docs:**
- How to upload website: https://support.hostinger.com/en/articles/1583355
- MySQL database setup: https://support.hostinger.com/en/articles/1583240
- SSL certificate setup: https://support.hostinger.com/en/articles/1583273

---

## What's Next?

While I'm offline (until Thursday), you can:

1. **Add Google Maps API Key** (optional)
   - Get free key from Google Cloud Console
   - Add to frontend environment variables

2. **Customize Site**
   - Edit content in Astro pages
   - Rebuild with `npm run build`
   - Re-upload changed files

3. **Add More States**
   - Follow data pipeline process
   - OSM enrichment is all set up
   - Just need to acquire state data

4. **Monitor Traffic**
   - Check Hostinger analytics
   - Set up Google Search Console

Enjoy your new site! 🎣
