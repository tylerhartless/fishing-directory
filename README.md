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

### 3. Done!

Visit `http://localhost:4321` - everything is running!

- Edit frontend files → auto-reloads
- Edit backend PHP → auto-reloads
- Everything stays in sync via Docker volumes

## Adding New States

The ETL pipeline is designed to scale to all 50 states. See the [fishing-data-pipeline](https://github.com/tylerhartless/fishing-data-pipeline) repository for complete documentation on adding new state data sources.

## Key Features

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
