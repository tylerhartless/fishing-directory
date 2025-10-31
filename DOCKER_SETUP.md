# Docker Development Setup

Complete guide to running the **entire** fishing directory stack with Docker Compose.

## Prerequisites

**Install Docker Desktop:**
1. Download: https://www.docker.com/products/docker-desktop/
2. Install Docker Desktop for Windows
3. Start Docker Desktop
4. Verify installation:
   ```bash
   docker --version
   docker compose version
   ```

---

## 🚀 Quick Start (One Command!)

```bash
# Start everything
docker compose up -d

# Wait ~60 seconds for all services to initialize

# Access the site
# Frontend: http://localhost:4321
# phpMyAdmin: http://localhost:8080
# API: http://localhost:8000
```

**That's it!** Everything runs in Docker now.

---

## What You Get

When you run `docker compose up -d`, you get **4 services**:

| Service | URL | Purpose |
|---------|-----|---------|
| **MySQL 8.0** | `localhost:3306` | Database |
| **phpMyAdmin** | http://localhost:8080 | Database GUI |
| **PHP API** | http://localhost:8000 | Backend API |
| **Astro Dev Server** | http://localhost:4321 | Frontend |

All services auto-start and connect to each other!

---

## Step-by-Step Setup

### 1. Start All Services

```bash
cd fishing-directory
docker compose up -d
```

**First time startup:**
- Downloads images (~2GB, one-time)
- Creates database
- Imports schema
- Installs npm packages
- Takes ~2-3 minutes

**Subsequent startups:** ~10 seconds

**Expected output:**
```
[+] Running 5/5
 ✔ Network fishing-directory_fishing_network  Created
 ✔ Container fishing_directory_db             Started
 ✔ Container fishing_directory_phpmyadmin     Started
 ✔ Container fishing_directory_api            Started
 ✔ Container fishing_directory_frontend       Started
```

### 2. Check Service Status

```bash
docker compose ps
```

**All services should show "Up":**
```
NAME                          STATUS
fishing_directory_db          Up (healthy)
fishing_directory_phpmyadmin  Up
fishing_directory_api         Up
fishing_directory_frontend    Up
```

### 3. Access Services

**Frontend (Astro):**
- URL: http://localhost:4321
- Auto-reloads on file changes
- Full hot module replacement (HMR)

**phpMyAdmin:**
- URL: http://localhost:8080
- Username: `fishing_user`
- Password: `fishing_password`
- Verify `fishing_directory` database exists

**API:**
- URL: http://localhost:8000/spots.php?limit=10
- Should return JSON (may be empty until you import data)

---

## Import Data (Python Still Runs on Host)

The database runs in Docker, but Python scripts run on your host machine:

### 1. Set up Python environment

```bash
cd data-pipeline

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure connection

```bash
copy .env.docker .env
```

Your `.env` should have:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=fishing_user
DB_PASSWORD=fishing_password
DB_NAME=fishing_directory
```

### 3. Test connection

```bash
python db_utils.py
```

Expected:
```
✓ Connected to MySQL database: fishing_directory
Database connection test successful!
```

### 4. Import data

```bash
# Import boat ramps (requires data file)
python process_boat_ramps.py

# Or test with sample
python adapters/texas_tpwd_adapter.py
```

---

## Development Workflow

### Daily Startup

```bash
docker compose up -d
```

All services start automatically. No need to run npm install or start dev servers manually!

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f astro
docker compose logs -f mysql
docker compose logs -f php
```

### Work on Frontend

Just edit files in `frontend/` - changes auto-reload thanks to HMR!

```bash
# No need to run npm manually, Docker handles it!
# Just edit files in frontend/src/
```

### Work on Backend API

Edit files in `backend/api/` - changes are instant (PHP doesn't need restart)

### Work on Data Pipeline

```bash
cd data-pipeline
venv\Scripts\activate
python process_boat_ramps.py
```

### Check Database

Two options:
1. **phpMyAdmin:** http://localhost:8080 (visual GUI)
2. **MySQL CLI:**
   ```bash
   docker exec -it fishing_directory_db mysql -u fishing_user -pfishing_password fishing_directory
   ```

### End of Day

```bash
# Stop all services (keeps data)
docker compose down

# Or stop and remove everything (⚠️ deletes database!)
docker compose down -v
```

---

## Useful Commands

### Restart a Service

```bash
# Restart Astro (if it crashes)
docker compose restart astro

# Restart all
docker compose restart
```

### Rebuild a Service

If you change docker-compose.yml:

```bash
docker compose up -d --build
```

### View Container Details

```bash
# See what's running
docker compose ps

# See resource usage
docker stats
```

### Access Container Shell

```bash
# MySQL shell
docker exec -it fishing_directory_db mysql -u fishing_user -pfishing_password fishing_directory

# Astro container shell
docker exec -it fishing_directory_frontend sh

# API container shell
docker exec -it fishing_directory_api bash
```

### Run Migrations

```bash
# Run SQL migration
docker exec -i fishing_directory_db mysql -u fishing_user -pfishing_password fishing_directory < data-pipeline/migrations/001_add_state_fields.sql

# Or via MySQL CLI
docker exec -it fishing_directory_db mysql -u fishing_user -pfishing_password fishing_directory
# Then paste SQL commands
```

---

## Troubleshooting

### Port Already in Use

**Error:** `Bind for 0.0.0.0:3306 failed: port is already allocated`

**Solution:** Change port in `docker-compose.yml`:

```yaml
mysql:
  ports:
    - "3307:3306"  # Changed from 3306
```

Then update `.env`:
```env
DB_HOST=localhost:3307
```

Common port conflicts:
- 3306 (MySQL) → use 3307
- 8080 (phpMyAdmin) → use 8081
- 8000 (PHP API) → use 8001
- 4321 (Astro) → use 4322

### Astro Won't Start

**Check logs:**
```bash
docker compose logs astro
```

**Common issues:**
- npm install failed → Fix package.json errors
- Port 4321 in use → Change port in docker-compose.yml
- Out of memory → Increase Docker Desktop RAM (Settings → Resources)

**Force rebuild:**
```bash
docker compose down
docker compose up -d --build astro
```

### MySQL Not Initializing

**Check logs:**
```bash
docker compose logs mysql
```

**Look for:** `MySQL init process done. Ready for start up.`

**If stuck:**
```bash
docker compose down -v  # ⚠️ Deletes data!
docker compose up -d
```

### Can't Connect from Python

**Verify Docker is running:**
```bash
docker compose ps
```

**Check .env file:**
```env
DB_HOST=localhost  # NOT "mysql"!
DB_PORT=3306       # Match docker-compose.yml
```

**Test connection:**
```bash
docker exec -it fishing_directory_db mysqladmin ping -u fishing_user -pfishing_password
```

### Astro Shows Blank Page

**Check API connection:**
- Astro tries to fetch from `http://localhost:8000`
- Make sure PHP container is running: `docker compose ps`
- Check API works: http://localhost:8000/spots.php?limit=5

**Check browser console:**
- Open DevTools (F12)
- Look for CORS or fetch errors
- API should allow localhost:4321

### Out of Disk Space

Docker images and volumes can take space.

**Clean up:**
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes (⚠️ careful!)
docker volume prune

# Nuclear option (removes EVERYTHING not running)
docker system prune -a --volumes
```

---

## File Structure with Docker

```
fishing-directory/
├── docker-compose.yml          # All services defined here
├── frontend/
│   ├── src/                    # Edit these, auto-reloads
│   ├── package.json
│   └── node_modules/           # In Docker container, not on host
├── backend/api/
│   ├── *.php                   # Edit these, instant changes
│   └── config.php              # Uses 'mysql' hostname
├── data-pipeline/
│   ├── .env                    # Points to localhost:3306
│   └── *.py                    # Run on host, connects to Docker MySQL
├── database/
│   └── schema.sql              # Auto-imported on first start
└── raw-data/
    └── *.csv                   # Your source data files
```

---

## Advantages of Full Docker Setup

✅ **One command** - Start everything with `docker compose up -d`
✅ **No manual installs** - No need to install Node, PHP, MySQL separately
✅ **Consistent** - Same environment on any machine
✅ **Isolated** - Doesn't conflict with other projects
✅ **Quick reset** - `docker compose down -v` starts fresh
✅ **Production-like** - Mimics real deployment
✅ **Auto-restart** - Containers restart if they crash
✅ **Hot reload** - Frontend changes auto-update

---

## Performance Tips

### Speed Up npm install

On Windows, npm in Docker can be slow. The `node_modules` volume helps, but you can also:

**Option 1: Keep node_modules in container (current setup)**
```yaml
volumes:
  - ./frontend:/app
  - /app/node_modules  # Don't sync node_modules
```

**Option 2: Run npm on host instead**
If Docker npm is too slow, you can still run Astro on host:
```bash
# In docker-compose.yml, remove the astro service
# Then run manually:
cd frontend && npm run dev
```

### Reduce Memory Usage

Edit Docker Desktop settings:
- Settings → Resources → Memory: 4GB minimum (8GB recommended)
- Settings → Resources → Swap: 1GB

### Speed Up Database

If importing large datasets is slow, increase MySQL buffer:

```yaml
mysql:
  command: --innodb-buffer-pool-size=512M
```

---

## Production Deployment

When ready to deploy:

**1. Build static frontend:**
```bash
cd frontend
npm run build
# Outputs to: frontend/dist/
```

**2. Upload to Hostinger:**
- Upload `frontend/dist/*` to `public_html/`
- Upload `backend/api/` to `public_html/api/`
- Update `backend/api/config.php` with Hostinger credentials

**3. Database:**
- Export from Docker: `docker exec fishing_directory_db mysqldump -u fishing_user -pfishing_password fishing_directory > backup.sql`
- Import to Hostinger via phpMyAdmin

Docker → Hostinger migration is seamless!

---

## Next Steps

**First time setup:**
1. ✅ `docker compose up -d`
2. ✅ Wait for services to start
3. ✅ Visit http://localhost:4321
4. ✅ Visit http://localhost:8080 (phpMyAdmin)
5. ✅ Set up Python: `cd data-pipeline && python -m venv venv`
6. ✅ Configure: `copy .env.docker .env`
7. ✅ Import data: `python process_boat_ramps.py`
8. 🎉 Start developing!

**Daily workflow:**
```bash
# Morning
docker compose up -d

# Work on frontend
# Just edit files in frontend/src/

# Work on data
cd data-pipeline
venv\Scripts\activate
python script.py

# Evening
docker compose down
```

---

**Everything in Docker. One command. Always works.** 🐳
