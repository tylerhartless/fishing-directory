# Public Fishing Directory

A comprehensive directory of public fishing access points across the United States. Built with a scalable ETL pipeline for importing data from multiple states and sources.

## Tech Stack

- **Frontend:** Astro (Static Site Generation) with client-side search
- **Backend API:** PHP + MySQL
- **Data Pipeline:** Separate repository ([fishing-data-pipeline](https://github.com/tylerhartless/fishing-data-pipeline))
- **Development & Deployment:** Docker Compose (entire stack runs in containers)

## Project Structure

```
fishing-directory/
├── frontend/              # Astro static site
├── backend/               # PHP API endpoints
│   └── api/               # RESTful API endpoints
├── docs/                  # Project documentation
├── scripts/               # Build and deployment scripts
└── docker-compose.yml     # Local development environment (frontend + API only)
```

**Note:** Data pipeline has been moved to a [separate repository](https://github.com/tylerhartless/fishing-data-pipeline) for better organization and reusability across future state expansions.

## Quick Start

### Prerequisites
- Docker Desktop
- Python 3.8+ (for running data import scripts outside of Docker)

### 1. Start the Entire Stack with One Command

```bash
# Clone repository
git clone https://github.com/tylerhartless/fishing-directory.git
cd fishing-directory

# Start all services - everything runs in Docker!
docker compose up -d

# Wait ~60 seconds for first-time setup
```

**Services running in containers:**
- Frontend: `http://localhost:4321` (Astro dev server with hot reload)
- PHP API: `http://localhost:8000` (backend API)

**No manual installation needed!** Node.js, npm, PHP - all handled by Docker.

### 2. Set Up Database

For local development, you'll need a MySQL database. You have two options:

**Option A: Use the data pipeline repository's database:**
```bash
cd ../
git clone https://github.com/tylerhartless/fishing-data-pipeline.git
cd fishing-data-pipeline
docker compose up -d  # Starts MySQL + phpMyAdmin
```

**Option B: Use an external MySQL database** (Hostinger, AWS RDS, etc.)
```bash
# Configure .env in backend/api/ with your database credentials
```

### 3. Import Data (Optional)

To populate the database with fishing spot data, see the [fishing-data-pipeline](https://github.com/tylerhartless/fishing-data-pipeline) repository.

### 4. Apply Database Migrations

If using the Species Prevalence System (Heat List), apply the migration:

```bash
mysql -u root -p fishing_directory < migrations/003_species_prevalence_system.sql
```

This creates the species prevalence tables and populates regional species data. See [SPECIES_PREVALENCE_SETUP.md](SPECIES_PREVALENCE_SETUP.md) for complete setup instructions.

### 5. Done!

Visit `http://localhost:4321` - everything is running!

- Edit frontend files → auto-reloads
- Edit backend PHP → auto-reloads
- Everything stays in sync via Docker volumes

## Adding New States

The ETL pipeline is designed to scale to all 50 states. See the [fishing-data-pipeline](https://github.com/tylerhartless/fishing-data-pipeline) repository for complete documentation on adding new state data sources.

## Key Features

### Frontend Features

#### Search & Discovery
- **Geolocation Search:** Use current location to find nearby fishing spots with distance calculations
- **Text Search:** Search by city, zip code, or location name with geocoding via OpenStreetMap Nominatim
- **Client-Side Filtering:** Filter 1,000+ fishing spots instantly by:
  - Spot type (lakes, river access, public waters, state parks, fishing piers)
  - Search radius (10, 25, 50, 100, 200 miles)
- **Infinite Scroll:** Progressive loading of results as you scroll
- **Search State Persistence:** Search results saved in session storage for page navigation
- **Autocomplete Suggestions:** Quick suggestions for common Texas cities

#### Navigation & Browsing
- **State-Level Browsing:** Browse all states with spot counts and county statistics
- **County-Level Browsing:** Browse fishing spots by county with filtering
- **Spot Detail Pages:** Individual pages for each fishing spot with:
  - Static map images (Mapbox) with theme-aware switching (light/dark)
  - GPS coordinates with copy-to-clipboard functionality
  - Amenities display (boat ramps, piers, restrooms, parking, etc.)
  - Water body information
  - Multi-county support for spots spanning multiple counties
  - Breadcrumb navigation
  - Schema.org structured data for SEO

#### Interactive Features
- **Species Prevalence System (Heat List):**
  - Time-decay based species ranking system that shows which fish are most commonly caught
  - Four-tier classification: Common (≥5000 score), Uncommon (≥1000), Rare (>0), Unreported (0)
  - Dynamic backfilling: Shows top unreported species to guide new users
  - Click any species to log a catch
  - Scores automatically decay 5% weekly to keep rankings fresh
  - Prevents gaming through automatic time-based decay
- **Catch Logging System:**
  - Log catches directly from the heat list interface
  - Validates species availability for each spot
  - Validates catch dates (within last 30 days, not in future)
  - Rate limiting (5 catches per hour per IP)
- **Fishing Reports System:**
  - View recent fishing reports for each spot
  - Submit new fishing reports (requires moderation)
  - Rate limiting (3 submissions per hour per IP)
- **Dynamic Content Loading:** Heat list, reports, and catch data loaded via API on spot detail pages

#### Special Pages
- **Fishing Without License Guide:** Comprehensive guide to Texas state parks where fishing licenses aren't required
- **State Parks Directory:** Filtered view of all Texas state parks with fishing access

#### UI/UX Features
- **Retro Terminal Theme:** CRT-inspired design with light/dark mode support
- **Responsive Design:** Mobile-first, works on all screen sizes
- **Theme Switching:** Automatic theme detection with manual override
- **Smooth Animations:** Transition effects and loading states
- **Accessibility:** Semantic HTML, ARIA labels, keyboard navigation

### Backend API Features

#### RESTful Endpoints

**GET `/api/spots.php`**
- Retrieve fishing spots with pagination
- Parameters:
  - `limit` (int): Number of spots to return (default: 10)
  - `county` (string): Filter by county name
  - `include_boat_ramps` (boolean): Include boat ramps (default: false)
- Returns: JSON with spot data including coordinates, amenities, spot type, counties
- Supports both legacy single-county and new multi-county data models

**GET `/api/county-stats.php`**
- Get county statistics for a state
- Parameters:
  - `state` (string): Two-letter state code (default: TX)
  - `limit` (int): Number of counties to return (default: 10)
- Returns: JSON with county names, slugs, spot counts

**GET `/api/reports.php`**
- Get fishing reports for a specific spot
- Parameters:
  - `spot_id` (int, required): Fishing spot ID
- Returns: JSON with approved fishing reports including species, catch count, dates, notes

**POST `/api/submit-report.php`**
- Submit a new fishing report
- Body (JSON):
  - `spot_id` (int, required)
  - `fish_species` (string, required)
  - `catch_count` (int, required)
  - `report_date` (string, required): ISO date format
  - `notes` (string, optional)
- Returns: JSON with success status and report ID
- Security: Rate limiting (3/hour), IP hashing, content moderation

**GET `/api/get-heat-list.php`**
- Get species prevalence heat list for a spot (Species Prevalence System)
- Parameters:
  - `spot_id` (int, required): Fishing spot ID
- Returns: JSON with all potential species for the spot, including:
  - Species details (id, common_name, icon, priority_order)
  - Score data (total_score, report_count)
  - Tier classification (common, uncommon, rare, unreported)
  - Sorting: Reported species by score (DESC), then unreported by priority
- Tier thresholds:
  - Common: score ≥ 5000
  - Uncommon: score ≥ 1000 and < 5000
  - Rare: score > 0 and < 1000
  - Unreported: score = 0

**POST `/api/log-catch.php`**
- Log a catch for the Species Prevalence System
- Body (JSON):
  - `spot_id` (int, required)
  - `species_id` (int, required): Master species ID
  - `catch_date` (string, required): Date in YYYY-MM-DD format (must be within last 30 days, not in future)
- Returns: JSON with success status and report_id
- Security: Rate limiting (5/hour), IP hashing, species validation, date validation
- Scoring: Each catch starts with base_score of 10.00, decays 5% weekly

#### Security Features
- **CORS Protection:** Only allowed domains can access API
- **Rate Limiting:** Prevents spam (3 reports/hour, 5 catches/hour, 10 votes/hour)
- **Input Validation:** All inputs sanitized and validated
- **Prepared Statements:** SQL injection prevention
- **Privacy:** IP addresses hashed, not stored in plain text
- **Content Moderation:** Reports require approval before display
- **Species Validation:** Catches only accepted for species in spot's potential_species list
- **Date Validation:** Catch dates validated (within 30 days, not in future)

### Pages & Routes

#### Static Pages (Astro SSG)
- **`/`** - Homepage with search widget and value propositions
- **`/states`** - Browse all states with spot counts
- **`/texas`** - Texas state page with county listings
- **`/texas/fishing-without-license`** - Guide to license-free fishing in state parks
- **`/texas/[county]`** - County-level spot listings (dynamic routes)
- **`/texas/[county]/[slug]`** - Individual spot detail pages (dynamic routes)

#### Dynamic Features
- All spot detail pages include client-side JavaScript for:
  - Loading and displaying Species Prevalence Heat List
  - Logging catches via interactive species list
  - Loading fishing reports
  - Copying coordinates to clipboard
  - Theme-aware map image switching

### Components

#### React/Preact Components (Client-Side)
- **`SearchWidget`** - Main search interface with geolocation and text search
- **`DynamicSubtitle`** - Dynamic subtitle based on user location
- **`ValuePropositionBadges`** - Feature highlights on homepage
- **`SpecialLandingPageCallout`** - State-specific callouts (e.g., no-license fishing)
- **`WhatEachListingIncludes`** - Information about listing details
- **`CountyListing`** - Dynamic county listings based on detected state

#### JavaScript Modules (Client-Side)
- **`heat-list.js`** - Species Prevalence System UI handler
  - Loads and displays heat list with tier-based styling
  - Handles catch logging interface
  - Manages show-all species expansion
  - Interactive species item clicks

#### Astro Components (Server-Side)
- **`ResultsWidget`** - Reusable results display with filtering and infinite scroll
- **`Layout`** - Base HTML layout with meta tags, theme support, and navigation

### Data Structure

#### Fishing Spot Data
Each spot includes:
- Basic info: name, slug, description
- Location: latitude, longitude, county (single or multi-county), state
- Classification: spot_type (lake, river_access, state_park, fishing_pier, etc.)
- Water body: water_body_name
- Amenities: JSON object with boolean flags (boat_ramp, parking, restrooms, lighting, fish_cleaning, boat_trailer_parking, camping, fishing_pier, picnic_area)
- Metadata: is_verified, is_parent, parent_spot_id
- SEO: meta_title, meta_description

#### Database Schema
- Supports both legacy single-county and new many-to-many county relationships
- Migration-ready: API automatically detects schema version
- Optimized queries with proper indexing
- **Species Prevalence System Tables:**
  - `master_species` - Regional species list with priority order and icons
  - `potential_species` - Junction table linking spots to available species
  - `catch_reports` - User catch data with time-decay scoring (base_score, current_score, last_decay_date)
- **Time-Decay System:** Scores decay 5% weekly via cron job (`backend/scripts/decay-scores.php`)

## Documentation

### Setup & Deployment
- **[docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md)** - Docker configuration details
- **[docs/QUICK_DEPLOY_GUIDE.md](docs/QUICK_DEPLOY_GUIDE.md)** - Fast deployment instructions
- **[docs/HOSTINGER_DEPLOYMENT_GUIDE.md](docs/HOSTINGER_DEPLOYMENT_GUIDE.md)** - Production deployment guide
- **[docs/GITHUB_DEPLOYMENT_SETUP.md](docs/GITHUB_DEPLOYMENT_SETUP.md)** - GitHub Actions CI/CD setup

### Data & Pipeline
- **[fishing-data-pipeline](https://github.com/tylerhartless/fishing-data-pipeline)** - Separate repository for ETL and data management
- **[docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)** - Where to find state fishing data

### Maintenance
- **[docs/MAINTENANCE.md](docs/MAINTENANCE.md)** - Ongoing maintenance tasks
- **[docs/NEXT_STEPS.md](docs/NEXT_STEPS.md)** - Planned features and improvements

## Configuration

### Environment Variables

#### Frontend (`.env` or `astro.config.mjs`)
- `PUBLIC_API_URL` - API base URL (defaults to `http://localhost:8000/api` for local dev)
- `PUBLIC_MAPBOX_TOKEN` - Mapbox access token for static map images
- `PUBLIC_NOMINATIM_EMAIL` - Email for OpenStreetMap Nominatim geocoding API (required for geocoding)

#### Backend (`backend/api/config.php`)
- `DB_HOST` - MySQL database host
- `DB_USER` - Database username
- `DB_PASS` - Database password
- `DB_NAME` - Database name
- `$allowed_origins` - Array of allowed CORS origins

### API Configuration

The backend API automatically detects database schema version:
- **Legacy Mode:** Single county field per spot
- **Migration Mode:** Many-to-many county relationships via junction tables

Both modes are supported simultaneously for smooth migrations.

## Current Data

- **Texas:** 1,000+ public fishing spots including:
  - State parks with fishing access
  - Public lakes and reservoirs
  - Community fishing lakes
  - Neighborhood fishing programs
  - River access points
  - Boat ramps
- **More states:** Ready to add with adapter framework

## Development Workflow

1. **Import Data** - Use the [fishing-data-pipeline](https://github.com/tylerhartless/fishing-data-pipeline) repository
2. **Develop Frontend** - Make changes to the Astro site in `frontend/`
3. **Test** - Verify at http://localhost:4321 (auto-reloads)
4. **Deploy** - Push to production

## Contributing

To add a new state:

1. See the [fishing-data-pipeline](https://github.com/tylerhartless/fishing-data-pipeline) repository for data import instructions
2. Add state page in `frontend/src/pages/`
3. Update homepage with new state

## License

Copyright (c) 2025 - All Rights Reserved

---

**Built for scale. Optimized for SEO.** 🎣
