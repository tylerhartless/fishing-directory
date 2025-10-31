# Docker Development Setup

Complete guide to running the fishing directory with Docker Compose.

## Prerequisites

**Install Docker Desktop:**
1. Download: https://www.docker.com/products/docker-desktop/
2. Install Docker Desktop for Windows
3. Start Docker Desktop
4. Verify installation:
   ```bash
   docker --version
   docker-compose --version
   ```

---

## Quick Start (3 Commands)

```bash
# 1. Start all services
docker-compose up -d

# 2. Wait ~30 seconds for MySQL to initialize

# 3. Access phpMyAdmin
# Open browser: http://localhost:8080
```

That's it! Your database is ready.

---

## What Docker Compose Gives You

When you run `docker-compose up -d`, you get:

✅ **MySQL 8.0** - Running on `localhost:3306`
✅ **phpMyAdmin** - Running on `http://localhost:8080`
✅ **PHP 8.2 + Apache** - Running on `http://localhost:8000`
✅ **Auto-imported schema** - Database ready to use!

---

## Step-by-Step Setup

### 1. Start Docker Services

```bash
cd c:\Users\tyash\Desktop\fishing-directory
docker-compose up -d
```

**What this does:**
- Downloads MySQL and PHP images (first time only)
- Creates `fishing_directory` database
- Auto-imports `database/schema.sql`
- Starts all services in background (`-d` = detached)

**Expected output:**
```
Creating network "fishing-directory_fishing_network" ... done
Creating volume "fishing-directory_mysql_data" ... done
Creating fishing_directory_db ... done
Creating fishing_directory_phpmyadmin ... done
Creating fishing_directory_api ... done
```

### 2. Wait for MySQL Initialization

First startup takes ~30 seconds for MySQL to initialize.

**Check if ready:**
```bash
docker-compose logs mysql
```

Look for: `MySQL init process done. Ready for start up.`

### 3. Access phpMyAdmin

**URL:** http://localhost:8080

**Login:**
- Username: `fishing_user`
- Password: `fishing_password`

**Verify:**
- Click `fishing_directory` database in left sidebar
- You should see 4 tables:
  - fishing_spots
  - fish_habitat_structures
  - fishing_reports
  - spot_votes

---

## Configure Python Environment

### 1. Set up Python .env file

```bash
cd data-pipeline
copy .env.docker .env
```

Your `.env` file now has:
```env
DB_HOST=localhost
DB_USER=fishing_user
DB_PASSWORD=fishing_password
DB_NAME=fishing_directory
```

### 2. Create Python virtual environment

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Test database connection

```bash
python db_utils.py
```

**Expected output:**
```
✓ Connected to MySQL database: fishing_directory
Database connection test successful!
```

---

## Import Your Boat Ramps Data

Now you're ready to import!

```bash
# Make sure your CSV is in raw-data folder
cd data-pipeline
python process_boat_ramps.py
```

**Expected output:**
```
Reading data from: ../raw-data/tpwd_boat_ramps.csv
Found 2547 boat ramps to process
✓ Inserted 2547 rows into fishing_spots

==================================================
SUCCESS: Imported 2547 boat ramps
==================================================
```

### Verify in phpMyAdmin

1. Go to http://localhost:8080
2. Click `fishing_directory` → `fishing_spots`
3. Click "Browse"
4. You should see 2,547+ rows!

---

## Test the PHP API

### 1. The API is already running!

**Base URL:** http://localhost:8000

### 2. Test endpoints

**Get fishing reports:**
```
http://localhost:8000/reports.php?spot_id=1
```

**Get votes:**
```
http://localhost:8000/get-votes.php?spot_id=1
```

**Note:** For Docker, the API uses `config.docker.php` instead of `config.php`

---

## Useful Docker Commands

### View running containers
```bash
docker-compose ps
```

### View logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs mysql
docker-compose logs php

# Follow logs (real-time)
docker-compose logs -f
```

### Stop services
```bash
docker-compose down
```

### Stop and remove all data (⚠️ deletes database!)
```bash
docker-compose down -v
```

### Restart a service
```bash
docker-compose restart mysql
docker-compose restart php
```

### Access MySQL CLI
```bash
docker exec -it fishing_directory_db mysql -u fishing_user -pfishing_password fishing_directory
```

Then run SQL:
```sql
SELECT COUNT(*) FROM fishing_spots;
SELECT * FROM fishing_spots LIMIT 5;
```

---

## Project Structure with Docker

```
fishing-directory/
├── docker-compose.yml        # Docker configuration
├── data-pipeline/
│   ├── .env                  # DB config (uses localhost:3306)
│   └── *.py                  # Python connects to Docker MySQL
├── backend/api/
│   ├── config.php            # For production
│   └── config.docker.php     # For Docker (uses 'mysql' host)
├── frontend/
│   └── ...                   # Run with npm (or add to docker-compose)
└── database/
    └── schema.sql            # Auto-imported on first start
```

---

## Troubleshooting

### Port 3306 already in use

**Solution:** Change MySQL port in `docker-compose.yml`:
```yaml
ports:
  - "3307:3306"  # Changed from 3306:3306
```

Then update `.env`:
```env
DB_HOST=localhost:3307
```

### Port 8080 already in use (phpMyAdmin)

**Solution:** Change port in `docker-compose.yml`:
```yaml
phpmyadmin:
  ports:
    - "8081:80"  # Changed from 8080:80
```

Then access: http://localhost:8081

### Database not initializing

**Check logs:**
```bash
docker-compose logs mysql
```

**Force recreate:**
```bash
docker-compose down -v
docker-compose up -d
```

### Can't connect from Python

**Check MySQL is running:**
```bash
docker-compose ps
```

**Verify .env settings:**
```env
DB_HOST=localhost  # NOT "mysql" - that's for inside Docker
DB_USER=fishing_user
DB_PASSWORD=fishing_password
```

### PHP API not working

**Check config file:**
Make sure you're using the Docker config:
```bash
cd backend/api
copy config.docker.php config.php
```

---

## Development Workflow

### Daily startup:
```bash
docker-compose up -d
```

### Work on data:
```bash
cd data-pipeline
venv\Scripts\activate
python process_boat_ramps.py
python process_state_parks.py
```

### Check database:
- phpMyAdmin: http://localhost:8080

### Test API:
- Visit: http://localhost:8000/reports.php?spot_id=1

### Work on frontend:
```bash
cd frontend
npm run dev
# Runs on http://localhost:4321
```

### End of day:
```bash
docker-compose down
```

---

## Advantages of Docker Setup

✅ **Isolated** - Doesn't conflict with other software
✅ **Consistent** - Same environment everywhere
✅ **Easy cleanup** - `docker-compose down -v` removes everything
✅ **Version controlled** - `docker-compose.yml` documents your setup
✅ **Quick setup** - One command to start everything
✅ **Production-like** - Similar to Hostinger environment

---

## Next Steps

1. ✅ Start Docker: `docker-compose up -d`
2. ✅ Verify phpMyAdmin: http://localhost:8080
3. ✅ Configure Python `.env`
4. ✅ Test connection: `python db_utils.py`
5. ✅ Import boat ramps: `python process_boat_ramps.py`
6. ✅ View data in phpMyAdmin
7. 🚀 Start building!

---

## When Ready to Deploy

Your Docker setup perfectly mirrors production:

**Local (Docker):**
- MySQL in container
- PHP in container
- Python connects to `localhost:3306`

**Production (Hostinger):**
- MySQL on Hostinger
- PHP on Hostinger
- Just change `.env` credentials

Same code, different config! 🎉

---

Ready to start? Run:

```bash
docker-compose up -d
```

Then let me know when you see the containers running!