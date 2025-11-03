# Public Fishing Directory

A comprehensive directory of public fishing access points across the United States. Built with a scalable ETL pipeline for importing data from multiple states and sources.

## Tech Stack

- **Frontend:** Astro (Static Site Generation) with client-side search
- **Backend API:** PHP + MySQL
- **Data Pipeline:** Python with adapter pattern for multi-state support
- **Development & Deployment:** Docker Compose (entire stack runs in containers)

## Project Structure

```
fishing-directory/
├── frontend/              # Astro static site
├── backend/               # PHP API endpoints
├── data-pipeline/         # Python ETL framework
│   ├── adapters/          # State-specific data adapters
│   ├── migrations/        # Database schema updates
│   └── SCALING_GUIDE.md   # Guide for adding new states
├── raw-data/              # Source data files (gitignored)
└── docker-compose.yml     # Local development environment
```

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

**All services running in containers:**
- Frontend: `http://localhost:4321` (Astro dev server with hot reload)
- MySQL: `localhost:3306` (database)
- PHP API: `http://localhost:8000` (backend API)
- phpMyAdmin: `http://localhost:8080` (database GUI)

**No manual installation needed!** Node.js, npm, PHP, MySQL - all handled by Docker.

### 2. Import Data (Python scripts run on host machine)

```bash
cd data-pipeline

# Set up Python environment (only needed for import scripts)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt

# Run any adapter to import data
cd adapters
python texas_lakes_adapter.py
python texas_state_parks_combined_adapter.py
# ... etc
```

### 3. Done!

Visit `http://localhost:4321` - everything is running!

- Edit frontend files → auto-reloads
- Edit backend PHP → auto-reloads
- Everything stays in sync via Docker volumes

## Adding New States

The ETL pipeline is designed to scale to all 50 states. See [data-pipeline/SCALING_GUIDE.md](data-pipeline/SCALING_GUIDE.md) for details.

### Quick Example - Generic CSV:

```python
from adapters import GenericCSVAdapter

column_map = {
    'name': 'Site_Name',
    'latitude': 'Lat',
    'longitude': 'Lon',
    'county': 'County',
    'water_body': 'Waterbody'
}

adapter = GenericCSVAdapter("Colorado_Parks", "CO", column_map)
adapter.process_and_import('colorado_fishing.csv')
```

No custom code required for simple CSV files!

## Key Features

### Scalable ETL Pipeline
- **Adapter Pattern:** Add new states without code duplication
- **Standardized Format:** All data transformed to common structure
- **Flexible Input:** Supports CSV, JSON, APIs, web scraping
- **Error Handling:** Validates data, skips bad rows, logs issues

### Frontend
- **Search-First Design:** Prominent search bar as main interface
- **Client-Side Filtering:** Filter 1,000+ Texas fishing spots instantly
- **Responsive Design:** Mobile-friendly spot cards
- **Interactive Results:** Scrollable list view with expandable details
- **Future:** Map integration for visual location browsing

### API
- **RESTful Endpoints:** JSON responses for spot data
- **CORS Enabled:** Works with any frontend
- **Optimized Queries:** Indexed for performance

## Documentation

- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Docker configuration details
- **[DATA_SOURCES.md](DATA_SOURCES.md)** - Where to find state fishing data
- **[data-pipeline/SCALING_GUIDE.md](data-pipeline/SCALING_GUIDE.md)** - Complete guide for adding states

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

1. **Find Data Source** - State wildlife agency CSV/JSON/API
2. **Create/Configure Adapter** - Map columns or write custom adapter
3. **Import Data** - Run Python script to load into MySQL via Docker
4. **Test** - Verify spots display correctly at http://localhost:4321
5. **Deploy** - Push to production (entire stack runs in Docker containers)

## Database Schema

Run migrations to add new fields:

```bash
cd data-pipeline
mysql -u fishing_user -p fishing_directory < migrations/001_add_state_fields.sql
```

## Contributing

To add a new state:

1. Find the state's fishing access data source
2. Create an adapter in `data-pipeline/adapters/`
3. Import the data
4. Add state page in `frontend/src/pages/`
5. Update homepage with new state

## License

Copyright (c) 2025 - All Rights Reserved

---

**Built for scale. Optimized for SEO.** 🎣
