# Public Fishing Directory

A comprehensive directory of public fishing access points across the United States. Built with a scalable ETL pipeline for importing data from multiple states and sources.

## Tech Stack

- **Frontend:** Astro (Static Site Generation) with client-side search
- **Backend API:** PHP + MySQL
- **Data Pipeline:** Python with adapter pattern for multi-state support
- **Development:** Docker Compose for local environment

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
- Python 3.8+
- Node.js 18+

### 1. Start Development Environment

```bash
# Clone repository
git clone https://github.com/tylerhartless/fishing-directory.git
cd fishing-directory

# Start Docker containers (MySQL, PHP, phpMyAdmin)
docker compose up -d
```

**Services:**
- MySQL: `localhost:3306`
- PHP API: `http://localhost:8000`
- phpMyAdmin: `http://localhost:8080`

### 2. Import Data

```bash
cd data-pipeline

# Set up Python environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt

# Configure for Docker
cp .env.docker .env

# Import Texas boat ramps (example)
# First, download data from https://tpwd.texas.gov/gis/resources/boat-access.phtml
# Save as: raw-data/tpwd_boat_ramps.csv
python process_boat_ramps.py
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:4321

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
- **Static Site Generation:** Fast page loads, great SEO
- **Client-Side Search:** Filter 2,000+ spots instantly
- **Responsive Design:** Mobile-friendly spot cards
- **Dynamic Rendering:** JavaScript-based for static hosting

### API
- **RESTful Endpoints:** JSON responses for spot data
- **CORS Enabled:** Works with any frontend
- **Optimized Queries:** Indexed for performance

## Documentation

- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Docker configuration details
- **[DATA_SOURCES.md](DATA_SOURCES.md)** - Where to find state fishing data
- **[data-pipeline/SCALING_GUIDE.md](data-pipeline/SCALING_GUIDE.md)** - Complete guide for adding states

## Current Data

- **Texas:** 2,234 boat ramps from TPWD
- **More states:** Ready to add with adapter framework

## Development Workflow

1. **Find Data Source** - State wildlife agency CSV/JSON
2. **Create/Configure Adapter** - Map columns or write custom adapter
3. **Import Data** - Run Python script to load into MySQL
4. **Test Frontend** - Verify spots display correctly
5. **Deploy** - Build static site and push to production

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
