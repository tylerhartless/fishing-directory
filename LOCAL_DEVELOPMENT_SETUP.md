# Local Development Setup (No Domain Required!)

You can develop everything locally without buying a domain. Here are your options:

## Option 1: XAMPP (Recommended - Easiest)

XAMPP gives you MySQL + PHP on your local machine.

### Step 1: Download & Install XAMPP

1. **Download:** https://www.apachefriends.org/download.html
2. Choose **Windows version**
3. Run the installer
4. **Select components:** Make sure these are checked:
   - ✅ Apache
   - ✅ MySQL
   - ✅ PHP
   - ✅ phpMyAdmin
5. Install to default location: `C:\xampp`
6. Click **Finish**

### Step 2: Start MySQL

1. Open **XAMPP Control Panel**
   - Search for "XAMPP" in Windows Start menu
2. Click **"Start"** next to **MySQL**
   - It should turn green
3. You now have MySQL running locally!

### Step 3: Access phpMyAdmin

1. In XAMPP Control Panel, click **"Admin"** next to MySQL
   - OR go to: http://localhost/phpmyadmin
2. You should see phpMyAdmin interface

### Step 4: Create Database

1. In phpMyAdmin, click **"New"** in the left sidebar
2. **Database name:** `fishing_directory`
3. **Collation:** `utf8mb4_unicode_ci`
4. Click **"Create"**

### Step 5: Import Schema

1. Click on `fishing_directory` database in left sidebar
2. Click **"Import"** tab
3. **Choose File:** Browse to `database/schema.sql`
4. Click **"Go"**
5. ✓ Success! You should see 4 tables created

### Step 6: Note Your Local Credentials

For local XAMPP, the default credentials are:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=fishing_directory
```

**Note:** Default XAMPP has NO password for root user (blank)

---

## Option 2: MySQL Workbench (If you want a GUI)

### Download MySQL Workbench

1. Visit: https://dev.mysql.com/downloads/workbench/
2. Download Windows version
3. Install MySQL Server when prompted (if not already installed)

### During MySQL Server Installation:

- **Root Password:** Set a password (remember it!)
- **Port:** 3306 (default)
- **Authentication:** Use Strong Password Encryption

### Create Database:

1. Open MySQL Workbench
2. Connect to local instance
3. Run this SQL:
   ```sql
   CREATE DATABASE fishing_directory
   CHARACTER SET utf8mb4
   COLLATE utf8mb4_unicode_ci;
   ```
4. Then import `schema.sql` file

---

## Option 3: Free Cloud Database (PlanetScale)

If you want a cloud database without buying hosting:

### PlanetScale (Free Tier)

1. Visit: https://planetscale.com
2. Sign up (free tier: 5GB storage, 1 billion row reads/month)
3. Create database: `fishing_directory`
4. Get connection string
5. Works great with your Python scripts

**Pros:**
- Free tier is generous
- Can use from anywhere
- Production-ready

**Cons:**
- Requires internet connection
- Migration to Hostinger later

---

## Recommended Setup (XAMPP)

Let's go with XAMPP since it's easiest and gives you PHP too for testing the API.

### Complete Setup Steps:

**1. Install XAMPP**
```
Download from: https://www.apachefriends.org
Install with MySQL + PHP + phpMyAdmin
```

**2. Start MySQL**
```
Open XAMPP Control Panel
Click "Start" next to MySQL
```

**3. Create Database**
```
Go to: http://localhost/phpmyadmin
Create database: fishing_directory
Import: database/schema.sql
```

**4. Configure Python .env**
```bash
cd data-pipeline
copy .env.example .env
```

Edit `.env`:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=fishing_directory
```

**5. Test Connection**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python db_utils.py
```

You should see:
```
✓ Connected to MySQL database: fishing_directory
Database connection test successful!
```

**6. Import Your Boat Ramps!**
```bash
# Make sure tpwd_boat_ramps.csv is in raw-data/ folder
python process_boat_ramps.py
```

---

## Setting Up Local PHP API (Optional for now)

Once XAMPP is running, you can test the PHP API locally:

**1. Copy API files to XAMPP**
```bash
# Copy backend/api folder to XAMPP's htdocs
xcopy backend\api C:\xampp\htdocs\api\ /E /I
```

**2. Edit API config**

Edit `C:\xampp\htdocs\api\config.php`:
```php
define('DB_HOST', 'localhost');
define('DB_USER', 'root');
define('DB_PASS', '');
define('DB_NAME', 'fishing_directory');
```

**3. Start Apache in XAMPP**
- In XAMPP Control Panel, click "Start" next to Apache

**4. Test API**
- Go to: http://localhost/api/reports.php?spot_id=1
- You should see JSON response

---

## When to Move to Hostinger?

**Develop Locally Now:**
- Import all your data
- Build and test the Astro frontend
- Perfect your design
- Get 1,000+ spots working great

**Move to Hostinger When:**
- You've decided on a domain name
- You're ready to go live
- Everything works perfectly locally

**Migration is Easy:**
1. Export database from phpMyAdmin (SQL dump)
2. Buy domain + Hostinger
3. Import SQL dump to Hostinger
4. Upload PHP files
5. Deploy Astro static files

---

## Domain Name Ideas (For When You're Ready)

Think about these while you develop:

**Fishing-Focused:**
- publicfishingspots.com
- findmyfishingspot.com
- fishingaccessmap.com
- freefishingspots.com

**Location-Focused:**
- txfishingspots.com (start Texas-specific)
- usfishingaccess.com
- fishingdirectory.com

**Action-Focused:**
- whereto.fish
- gofish.guide
- findfish.now

**Check availability at:** https://www.namecheap.com

**Pro Tip:** Buy a .com if available, it's still the most trusted extension for SEO

---

## Your Next Steps (Right Now)

1. ✅ Download XAMPP
2. ✅ Install XAMPP
3. ✅ Start MySQL in XAMPP Control Panel
4. ✅ Open http://localhost/phpmyadmin
5. ✅ Create `fishing_directory` database
6. ✅ Import `database/schema.sql`
7. ✅ Set up Python environment
8. ✅ Configure `.env` with localhost credentials
9. ✅ Test connection: `python db_utils.py`
10. ✅ Import boat ramps: `python process_boat_ramps.py`

---

## Troubleshooting XAMPP

### MySQL won't start
**Solution:** Port 3306 might be in use
- Open XAMPP Control Panel
- Click "Config" next to MySQL → "my.ini"
- Change port from 3306 to 3307
- Update `.env` to use port 3307:
  ```env
  DB_HOST=localhost:3307
  ```

### Apache won't start (if needed for PHP API)
**Solution:** Port 80 might be in use (Skype, IIS, etc.)
- Stop Skype or other services using port 80
- Or change Apache to port 8080 in config

### Can't access phpMyAdmin
**Solution:**
- Make sure both Apache AND MySQL are running in XAMPP
- Go to http://localhost/phpmyadmin (not https)

---

## Summary

✅ **No domain needed yet!**
✅ **Use XAMPP for local MySQL + PHP**
✅ **Develop everything locally first**
✅ **Perfect your site before spending money**
✅ **Easy migration to Hostinger later**

Ready to install XAMPP? Let me know if you need help with any step!