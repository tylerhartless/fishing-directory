# Public Fishing Directory

A comprehensive, SEO-optimized directory of public fishing access points, starting with Texas and expanding nationwide.

## 🎣 Overview

This platform aggregates government fishing data (boat ramps, state parks, community fishing lakes) and user-submitted content into a searchable, fast-loading directory optimized for organic search traffic.

**Live Data:** 10,000+ fishing spots (and growing)
**Tech Stack:** Astro (SSG) + PHP API + MySQL + Python ETL
**Target:** 50,000+ monthly visitors via SEO

## Tech Stack

- **Frontend:** Astro (Static Site Generation)
- **Backend:** PHP + MySQL (Hostinger)
- **Data Processing:** Python ETL scripts
- **Maps:** Mapbox API
- **Hosting:** Hostinger (backend) + Netlify/Vercel (frontend)

## Project Structure

```
fishing-directory/
├── data-pipeline/          # Python ETL scripts for processing government data
├── frontend/               # Astro static site
├── backend/                # PHP API endpoints
├── raw-data/               # Downloaded CSV/GIS files (not in git)
├── processed-data/         # Cleaned data ready for import
└── database/               # SQL schema and migration scripts
```

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Python 3.8+
- Node.js 18+

### Setup (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/tylerhartless/fishing-directory.git
cd fishing-directory

# 2. Start Docker services
docker compose up -d

# 3. Set up Python environment
cd data-pipeline
cp .env.docker .env
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Import data (requires downloading TPWD data first)
python process_boat_ramps.py
python process_state_parks.py

# 5. Export for Astro
python export_for_astro.py

# 6. Start frontend dev server
cd ../frontend
npm install
npm run dev
```

**Access:**
- Frontend: http://localhost:4321
- phpMyAdmin: http://localhost:8080
- API: http://localhost:8000

## Data Sources

- TPWD Boat Ramps: https://tpwd.texas.gov/gis/resources/boat-access.phtml
- Community Fishing Lakes (CFL)
- River Access (RACA)
- Fish Habitat Structures
- Texas State Parks

## Development Roadmap

- [x] Phase 1: Foundation & Data Pipeline (Week 1-3)
- [ ] Phase 2: Frontend with Astro (Week 3-5)
- [ ] Phase 3: PHP Mini-API (Week 5-6)
- [ ] Phase 4: User Submissions (Week 7)
- [ ] Phase 5: SEO & Content (Week 8-9)
- [ ] Phase 6: Launch (Week 10+)

## Environment Variables

Create `.env` files in respective directories:

**data-pipeline/.env:**
```
DB_HOST=your-hostinger-host
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=fishing_directory
```

**frontend/.env:**
```
MAPBOX_TOKEN=your-mapbox-token
API_BASE_URL=https://yourdomain.com/api
```

## 📖 Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete setup guide
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Docker development instructions
- **[DATA_SOURCES.md](DATA_SOURCES.md)** - Where to get fishing data
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Business plan & architecture

## 📄 License

Copyright (c) 2025 - All Rights Reserved

See [LICENSE](LICENSE) for details.

---

**Built for scale. Optimized for SEO. Designed to win.** 🎣