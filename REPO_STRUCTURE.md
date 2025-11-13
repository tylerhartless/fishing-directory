# Repository Structure

This document provides a detailed overview of the fishing-directory repository organization.

## Root Directory

```
fishing-directory/
├── README.md                  # Project overview and quick start
├── LICENSE                    # Copyright and licensing
├── docker-compose.yml         # Multi-container Docker setup
├── .gitignore                 # Git ignore rules
├── frontend/                  # Frontend application (Astro)
├── backend/                   # Backend API (PHP)
├── data-pipeline/             # Data import pipeline (Python)
├── database/                  # Database schema files
├── docs/                      # Project documentation
├── scripts/                   # Build and deployment scripts
├── raw-data/                  # Source data files (gitignored)
├── processed-data/            # Processed data (gitignored)
└── deploy/                    # Deployment build output (gitignored)
```

## Frontend (`/frontend`)

Static site generated with Astro framework.

```
frontend/
├── package.json               # Node.js dependencies
├── package-lock.json          # Locked dependency versions
├── tsconfig.json              # TypeScript configuration
├── astro.config.mjs           # Astro build configuration
├── public/                    # Static assets (copied as-is)
└── src/
    ├── pages/                 # Route pages
    │   ├── index.astro        # Homepage
    │   ├── spots.astro        # Universal spots search
    │   ├── texas.astro        # Texas state page
    │   └── texas/
    │       └── [county]/[slug].astro  # Dynamic spot detail pages
    ├── layouts/
    │   └── Layout.astro       # Base HTML layout
    └── lib/
        └── database.ts        # Data fetching utilities
```

**Tech Stack:**
- Astro 5.15.3 (Static Site Generation)
- TypeScript
- Leaflet (maps)

**Environment Variables:**
- `PUBLIC_API_URL` - Backend API endpoint
- `PUBLIC_MAPBOX_TOKEN` - Mapbox API token (optional)
- `PUBLIC_NOMINATIM_EMAIL` - Contact email for Nominatim geocoding

## Backend (`/backend`)

PHP REST API with MySQL database.

```
backend/
├── README.md
└── api/
    ├── config.php             # Database credentials (gitignored, auto-generated)
    ├── config.example.php     # Configuration template for local dev
    ├── .htaccess              # Apache security and CORS rules
    ├── spots.php              # GET /api/spots - Fetch fishing spots
    ├── submit-report.php      # POST /api/submit-report - Submit fishing report
    ├── reports.php            # GET /api/reports - Get reports for a spot
    ├── get-heat-list.php      # GET /api/get-heat-list - Species prevalence data
    └── log-catch.php          # POST /api/log-catch - Log catches for heat list
```

**Tech Stack:**
- PHP 8.2
- MySQL 8.0
- Apache (mod_rewrite, mod_headers)

**Security Features:**
- Prepared statements (SQL injection prevention)
- Rate limiting (IP-based, hourly)
- IP address hashing (privacy)
- Input validation
- CORS origin validation

## Data Pipeline (`/data-pipeline`)

Python ETL framework for importing fishing data from multiple states.

```
data-pipeline/
├── requirements.txt           # Python dependencies
├── config.py                  # Database configuration
├── db_utils.py                # Database helper functions
├── etl_base.py                # Base adapter class
├── .env.example               # Environment variable template
├── .env.docker                # Docker environment variables
├── .gitignore
├── adapters/                  # State-specific data adapters
│   ├── __init__.py
│   ├── generic_csv_adapter.py
│   ├── texas_tpwd_adapter.py
│   ├── texas_lakes_adapter.py
│   ├── california_dfw_adapter.py
│   └── ... (12+ adapters)
├── migrations/                # Database schema migrations
│   ├── 001_add_state_fields.sql
│   ├── 002_add_community_lake_type.sql
│   └── ... (6+ migrations)
├── scripts/                   # Utility scripts
│   ├── apply_osm_enrichment.py
│   └── archive/
├── osm/                       # OpenStreetMap enrichment
├── data_corrections/          # Data quality fixes
└── docs/                      # Pipeline documentation
    ├── DATA_PIPELINE_ARCHITECTURE.md
    ├── DATA_QUALITY_RULES.md
    ├── OSM_SETUP_GUIDE.md
    └── ... (10+ docs)
```

**Tech Stack:**
- Python 3.8+
- pandas (data manipulation)
- mysql-connector-python (database)
- python-slugify (URL generation)

**Architecture:**
- Adapter pattern for multi-state support
- Standardized `FishingSpotData` model
- Automatic deduplication
- OSM enrichment integration

## Database (`/database`)

MySQL database schema and initialization.

```
database/
└── schema.sql                 # Complete database schema
```

**Tables:**
- `fishing_spots` - Main fishing locations table
- `fishing_reports` - User-submitted catch reports
- `spot_votes` - Community fish species voting
- `fish_habitat_structures` - Underwater attractors

## Documentation (`/docs`)

Project documentation organized by topic.

```
docs/
├── DOCKER_SETUP.md            # Docker development guide
├── QUICK_DEPLOY_GUIDE.md      # Fast deployment instructions
├── HOSTINGER_DEPLOYMENT_GUIDE.md  # Production hosting guide
├── GITHUB_DEPLOYMENT_SETUP.md     # CI/CD configuration
├── DATA_SOURCES.md            # Where to find fishing data
├── MAINTENANCE.md             # Maintenance tasks
├── NEXT_STEPS.md              # Future roadmap
├── DEPLOYMENT_READY.md        # Pre-deployment checklist
├── BRANCHING_STRATEGY.md      # Git workflow
└── CLEANUP_PLAN.md            # Technical debt tracking
```

## Scripts (`/scripts`)

Build and deployment automation scripts.

```
scripts/
├── create_deployment_package.py   # Build production package
├── export_db_for_hostinger.py     # Export database for hosting
└── export_for_build.py            # Export data for static build
```

**Usage:** Run from scripts/ directory
```bash
cd scripts
python create_deployment_package.py
```

## Data Directories

### Raw Data (`/raw-data`)
Source data files from state agencies (gitignored).

```
raw-data/
├── .gitkeep
├── texas_boat_ramps.csv
├── texas_state_parks.geojson
└── ... (source files)
```

### Processed Data (`/processed-data`)
Cleaned and transformed data (gitignored).

```
processed-data/
├── .gitkeep
└── spots.json                 # Exported for frontend build
```

## Deployment (`/deploy`)

Build output for production deployment (gitignored).

```
deploy/
├── public_html/               # Upload this to web hosting
│   ├── index.html
│   ├── _astro/                # Astro assets
│   ├── api/                   # Backend API
│   └── ...
└── database.sql               # Import via phpMyAdmin
```

## Docker Services

Defined in `docker-compose.yml`:

1. **mysql** - MySQL 8.0 database
   - Port: 3306
   - Auto-initializes with schema.sql
   - Persistent volume

2. **phpmyadmin** - Database management UI
   - Port: 8080
   - http://localhost:8080

3. **php** - PHP 8.2 with Apache
   - Port: 8000
   - Backend API at http://localhost:8000/api
   - Live reload via volume mount

4. **astro** - Node.js 18 with Astro dev server
   - Port: 4321
   - Frontend at http://localhost:4321
   - Hot module replacement

## GitHub Workflows (`.github/workflows/`)

```
.github/workflows/
└── deploy-hostinger.yml       # Automated deployment to production
```

**Triggers:**
- Push to `main` branch (frontend/** or backend/**)
- Manual workflow dispatch

**Secrets Required:**
- `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`
- `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`
- `PUBLIC_MAPBOX_TOKEN`, `PUBLIC_API_URL`

## Environment Variables

### Frontend (Astro)
Create `frontend/.env.production`:
```
PUBLIC_API_URL=https://yourdomain.com/api
PUBLIC_MAPBOX_TOKEN=pk.xxx
PUBLIC_NOMINATIM_EMAIL=contact@yourdomain.com
```

### Backend (PHP)
Create `backend/api/config.php` (or use GitHub Actions to generate):
- See `backend/api/config.example.php` for template

### Data Pipeline (Python)
Create `data-pipeline/.env`:
```
DB_HOST=localhost
DB_USER=fishing_user
DB_PASSWORD=fishing_password
DB_NAME=fishing_directory
MAPBOX_TOKEN=pk.xxx (optional)
```

## File Naming Conventions

- **Markdown docs:** `SCREAMING_SNAKE_CASE.md`
- **Python files:** `snake_case.py`
- **PHP files:** `kebab-case.php`
- **JavaScript/TypeScript:** `camelCase.ts` or `PascalCase.astro`
- **Config files:** `lowercase.config.js`

## Ignored Files (`.gitignore`)

Key patterns:
- Environment files: `.env`, `.env.local`, `.env.production`
- Build output: `dist/`, `deploy/`, `node_modules/`
- Data files: `raw-data/*.csv`, `processed-data/*.json`
- Credentials: `backend/api/config.php`
- Database: `*.sql.gz`, `mysql-data/`

## Development Workflow

1. **Start Docker:** `docker compose up -d`
2. **Import data:** Run Python adapters
3. **Develop frontend:** Edit files in `frontend/src`
4. **Develop backend:** Edit files in `backend/api`
5. **Test locally:** http://localhost:4321
6. **Deploy:** Push to `main` branch (auto-deploys via GitHub Actions)

## Production Deployment

The production site is deployed to Hostinger via FTP:
- Frontend: Static Astro build
- Backend: PHP API files
- Database: MySQL via phpMyAdmin import

See [docs/HOSTINGER_DEPLOYMENT_GUIDE.md](docs/HOSTINGER_DEPLOYMENT_GUIDE.md) for details.

---

**Last Updated:** 2025-11-04
