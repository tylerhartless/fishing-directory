# Getting Started Guide

This guide will walk you through setting up the Public Fishing Directory from scratch.

## Prerequisites

- Python 3.8+ (for data processing)
- Node.js 18+ (for Astro frontend)
- MySQL database (Hostinger account recommended)
- Mapbox account (free tier) for maps

## Step-by-Step Setup

### Phase 1: Database Setup (15 minutes)

1. **Create MySQL Database on Hostinger**
   - Log into Hostinger control panel
   - Create new MySQL database named `fishing_directory`
   - Note down:
     - Database host
     - Database user
     - Database password

2. **Import Database Schema**
   - Open phpMyAdmin from Hostinger
   - Select your `fishing_directory` database
   - Click "Import"
   - Upload `database/schema.sql`
   - Click "Go"

3. **Verify Tables Created**
   ```sql
   SHOW TABLES;
   ```
   You should see: `fishing_spots`, `fish_habitat_structures`, `fishing_reports`, `spot_votes`

### Phase 2: Data Pipeline Setup (30 minutes)

1. **Set Up Python Environment**
   ```bash
   cd data-pipeline
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Mac/Linux
   source venv/bin/activate

   pip install -r requirements.txt
   ```

2. **Configure Database Connection**
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   ```
   DB_HOST=your-hostinger-host.mysql.com
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=fishing_directory
   ```

3. **Test Database Connection**
   ```bash
   python db_utils.py
   ```
   You should see: "Database connection test successful!"

4. **Download TPWD Data** (Texas as first state)
   - Visit: https://tpwd.texas.gov/gis/resources/boat-access.phtml
   - Download boat ramps CSV
   - Save to `raw-data/tpwd_boat_ramps.csv`

5. **Run ETL Scripts**
   ```bash
   # Import boat ramps
   python process_boat_ramps.py

   # Import state parks
   python process_state_parks.py
   ```

   You should see output like:
   ```
   SUCCESS: Imported 2,547 boat ramps
   ```

### Phase 3: Backend API Setup (20 minutes)

1. **Upload PHP Files to Hostinger**
   - Using File Manager or FTP:
   - Upload `backend/api/` folder to `public_html/api/`

2. **Configure API**
   Edit `public_html/api/config.php`:
   ```php
   define('DB_HOST', 'your-hostinger-host.mysql.com');
   define('DB_USER', 'your_db_user');
   define('DB_PASS', 'your_db_password');
   define('DB_NAME', 'fishing_directory');

   $allowed_origins = [
       'http://localhost:4321',  // Dev
       'https://yourdomain.com'  // Production
   ];
   ```

3. **Test API Endpoints**
   Visit in browser:
   - `https://yourdomain.com/api/reports.php?spot_id=1`

   You should see JSON response.

### Phase 4: Frontend Setup (20 minutes)

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   ```
   PUBLIC_MAPBOX_TOKEN=pk.eyJ1I...  # Get from mapbox.com
   PUBLIC_API_URL=https://yourdomain.com/api
   PUBLIC_SITE_URL=https://yourdomain.com
   ```

3. **Create Sample Data for Development**

   Since Astro needs data at build time, export your database:

   ```bash
   cd data-pipeline
   python export_for_astro.py  # (Create this script)
   ```

   Or manually export from phpMyAdmin:
   - Export `fishing_spots` table as JSON
   - Save to `frontend/public/data/fishing-spots.json`

4. **Start Dev Server**
   ```bash
   npm run dev
   ```

   Open http://localhost:4321

### Phase 5: Build & Deploy (30 minutes)

1. **Build Static Site**
   ```bash
   cd frontend
   npm run build
   ```

   This generates static files in `dist/`

2. **Deploy Options**

   **Option A: Netlify (Recommended for Frontend)**
   - Push code to GitHub
   - Connect Netlify to your repo
   - Build command: `cd frontend && npm run build`
   - Publish directory: `frontend/dist`
   - Add environment variables in Netlify dashboard

   **Option B: Vercel**
   - Similar to Netlify
   - Auto-detects Astro

   **Option C: Hostinger (Static Files)**
   - Upload `frontend/dist/*` to `public_html/`
   - Note: API stays in `public_html/api/`

3. **Set Up Custom Domain**
   - Configure DNS in Hostinger
   - Update `astro.config.mjs` with your domain
   - Update `PUBLIC_SITE_URL` in `.env`

## Verification Checklist

- [ ] Database tables created successfully
- [ ] At least 1000 fishing spots imported
- [ ] API endpoints return valid JSON
- [ ] Frontend builds without errors
- [ ] Homepage loads correctly
- [ ] Individual spot pages display maps and info
- [ ] Fishing reports submission works
- [ ] Vote system works
- [ ] Site is live on custom domain

## Next Steps

### Immediate (Week 1)
1. Import more TPWD datasets (RACA, CFL, habitat structures)
2. Test all features thoroughly
3. Submit sitemap to Google Search Console
4. Write first 3 blog posts

### Short Term (Month 1)
1. Add more Texas data sources
2. Implement search functionality
3. Build simple admin panel for moderation
4. Engage with fishing communities

### Long Term (Months 2-6)
1. Add second state (Florida, Louisiana, etc.)
2. Monetize with ads (AdSense, Ezoic)
3. Add affiliate links (fishing gear)
4. Reach 50k monthly visitors

## Common Issues

### "Database connection failed"
- Check `config.php` credentials
- Verify database exists in Hostinger
- Check if IP is allowed (Hostinger may have IP restrictions)

### "ModuleNotFoundError" in Python
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Astro build fails
- Check that `fishing-spots.json` exists in `public/data/`
- Verify all environment variables are set
- Check for syntax errors in `.astro` files

### Maps not showing
- Verify Mapbox token is correct
- Check browser console for errors
- Ensure token is added to `.env` as `PUBLIC_MAPBOX_TOKEN`

### CORS errors
- Add your frontend domain to `$allowed_origins` in `api/config.php`
- Make sure `set_cors_headers()` is called in each endpoint

## Getting Help

- Check `README.md` in each directory
- Review `data-pipeline/README.md` for ETL issues
- Review `backend/README.md` for API issues
- Check Astro docs: https://docs.astro.build

## Resources

- **TPWD Data**: https://tpwd.texas.gov/gis/resources/
- **Mapbox Docs**: https://docs.mapbox.com/
- **Astro Docs**: https://docs.astro.build/
- **MySQL Docs**: https://dev.mysql.com/doc/

---

**Pro Tip:** Start small! Get 100 perfect fishing spot pages live before scaling to 10,000. Quality > Quantity for SEO.

Good luck building your fishing directory!
