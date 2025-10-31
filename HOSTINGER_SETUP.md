# Hostinger Database Setup Guide

Follow these steps to set up your MySQL database on Hostinger.

## Step 1: Log into Hostinger

1. Go to https://hostinger.com
2. Click "Login" (top right)
3. Enter your credentials
4. You should land on the **hPanel** dashboard

---

## Step 2: Create MySQL Database

### From hPanel Dashboard:

1. Look for **"Databases"** section in the left sidebar
2. Click **"MySQL Databases"**

### Create the Database:

1. Click **"Create New Database"** (or similar button)
2. **Database Name:** Enter `fishing_directory`
   - Note: Hostinger may add a prefix like `u123456789_fishing_directory`
   - That's fine - just remember the full name
3. Click **"Create"**

### Create Database User (if needed):

Some Hostinger plans auto-create a user, others require manual creation:

1. If prompted, create a new MySQL user:
   - **Username:** `fishing_user` (or similar)
   - **Password:** Generate a strong password (save this!)
2. Click **"Create User"**

### Grant Permissions:

1. Find the section: **"Add User to Database"**
2. Select your user: `fishing_user`
3. Select your database: `fishing_directory`
4. **Privileges:** Select **ALL PRIVILEGES**
5. Click **"Add"** or **"Grant"**

---

## Step 3: Note Your Database Credentials

**Write these down - you'll need them!**

```
DB_HOST: [usually something like mysql123.hostinger.com]
DB_NAME: [your database name, e.g., u123456789_fishing_directory]
DB_USER: [your username, e.g., u123456789_fishing_user]
DB_PASSWORD: [the password you just created]
```

**Where to find DB_HOST:**
- In the MySQL Databases page, look for "Hostname" or "Server"
- Usually looks like: `mysql123.hostinger.com` or similar

---

## Step 4: Access phpMyAdmin

### Open phpMyAdmin:

1. In the MySQL Databases section, find **"Manage"** next to your database
2. Click **"Manage"** → this opens **phpMyAdmin**
3. Or look for a direct **"phpMyAdmin"** button in hPanel

### You're in! You should see:
- Left sidebar with your database name
- Currently it's empty (no tables yet)

---

## Step 5: Import the Database Schema

### Upload schema.sql:

1. In phpMyAdmin, click on your database name in the left sidebar
   - It should highlight/select it
2. Click the **"Import"** tab at the top
3. Click **"Choose File"**
4. Navigate to: `c:\Users\tyash\Desktop\fishing-directory\database\schema.sql`
5. Select the file
6. Scroll down and click **"Go"** or **"Import"**

### Wait for Success Message:

You should see: ✓ **"Import has been successfully finished"**

---

## Step 6: Verify Tables Were Created

### Check the Tables:

1. In the left sidebar, click your database name
2. You should now see **4 tables**:
   - `fishing_spots`
   - `fish_habitat_structures`
   - `fishing_reports`
   - `spot_votes`

3. Click on `fishing_spots` to view its structure
   - You should see columns: id, name, slug, latitude, longitude, etc.

### Quick Test Query:

1. Click the **"SQL"** tab at the top
2. Enter this query:
   ```sql
   SELECT COUNT(*) FROM fishing_spots;
   ```
3. Click **"Go"**
4. Result should show: **1** row (the sample data we included)

---

## Step 7: Configure Your Local `.env` File

Now that you have your database credentials, let's configure your Python environment.

### Navigate to data-pipeline folder:

```bash
cd c:\Users\tyash\Desktop\fishing-directory\data-pipeline
```

### Copy the example .env file:

```bash
copy .env.example .env
```

### Edit `.env` file:

Open `data-pipeline/.env` in a text editor and fill in your credentials:

```env
# Hostinger MySQL Database
DB_HOST=mysql123.hostinger.com
DB_USER=u123456789_fishing_user
DB_PASSWORD=your_password_here
DB_NAME=u123456789_fishing_directory

# Optional: for geocoding addresses if coordinates are missing
# MAPBOX_TOKEN=your_mapbox_token
```

**Replace with YOUR actual values from Step 3!**

---

## Step 8: Test Database Connection

### Install Python dependencies (if you haven't):

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Test the connection:

```bash
python db_utils.py
```

**Expected Output:**
```
✓ Connected to MySQL database: u123456789_fishing_directory
Database connection test successful!
```

**If you see errors:**
- Double-check your credentials in `.env`
- Make sure the database exists in Hostinger
- Verify the hostname is correct
- Check if you need to whitelist your IP (some Hostinger plans require this)

---

## Troubleshooting

### Error: "Access denied for user"
**Solution:**
- Check username and password in `.env`
- Verify user has permissions to the database
- Re-grant permissions in phpMyAdmin

### Error: "Unknown database"
**Solution:**
- Check database name in `.env` (include any prefix)
- Verify database exists in Hostinger

### Error: "Can't connect to MySQL server"
**Solution:**
- Check DB_HOST in `.env`
- Verify your internet connection
- Some Hostinger plans require IP whitelisting:
  - In hPanel → MySQL Databases → Remote MySQL
  - Add your IP address

### Error: "SSL connection error"
**Solution:**
Add to your `.env`:
```
DB_SSL=false
```

Then update `config.py` to handle SSL if needed.

---

## ✅ Success Checklist

Before moving to the next step, verify:

- [ ] Database created in Hostinger
- [ ] User created and has ALL PRIVILEGES
- [ ] schema.sql imported successfully
- [ ] 4 tables visible in phpMyAdmin
- [ ] `.env` file configured with correct credentials
- [ ] `python db_utils.py` runs without errors

---

## Next Steps

Once your database is set up and tested:

1. **Import boat ramps data:**
   ```bash
   python process_boat_ramps.py
   ```

2. **Import state parks:**
   ```bash
   python process_state_parks.py
   ```

3. **Verify data in phpMyAdmin:**
   ```sql
   SELECT COUNT(*) FROM fishing_spots;
   ```
   Should show 2,500+ spots!

---

## Quick Reference

**Hostinger hPanel:** https://hpanel.hostinger.com
**phpMyAdmin:** Access via hPanel → MySQL Databases → Manage

**Important Files:**
- Database schema: `database/schema.sql`
- Python config: `data-pipeline/.env`
- Connection test: `data-pipeline/db_utils.py`

---

Need help? Let me know where you get stuck!
