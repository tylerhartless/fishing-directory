# Environment Variables Setup Guide

This document explains how to configure environment variables for different environments.

## Overview

The application uses environment variables for:
- Database credentials
- API keys (Mapbox, Nominatim)
- Deployment configuration (FTP)

## Local Development

### Frontend (Astro)

Create `frontend/.env` or `frontend/.env.local`:

```bash
# API endpoint (Docker or local)
PUBLIC_API_URL=http://localhost:8000/api

# Optional: Mapbox token for static maps
PUBLIC_MAPBOX_TOKEN=pk.your_mapbox_token_here

# Optional: Custom email for Nominatim geocoding
PUBLIC_NOMINATIM_EMAIL=your-email@example.com
```

**Note:** Variables prefixed with `PUBLIC_` are exposed to the browser.

### Backend (PHP)

1. Copy the example config:
```bash
cp backend/api/config.example.php backend/api/config.php
```

2. Edit `backend/api/config.php` with your local credentials:
```php
define('DB_HOST', 'mysql');  // Use 'mysql' for Docker, 'localhost' for local MySQL
define('DB_USER', 'fishing_user');
define('DB_PASS', 'fishing_password');
define('DB_NAME', 'fishing_directory');
```

**Note:** `config.php` is gitignored to prevent committing credentials.

### Data Pipeline (Python)

For Docker environment, use `data-pipeline/.env.docker`:
```bash
DB_HOST=localhost
DB_USER=fishing_user
DB_PASSWORD=fishing_password
DB_NAME=fishing_directory
DB_PORT=3306
```

For local/production, create `data-pipeline/.env`:
```bash
DB_HOST=your-database-host.com
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=fishing_directory
MAPBOX_TOKEN=pk.your_token  # Optional
```

## Production (GitHub Actions)

### Required GitHub Secrets

Navigate to: **Repository → Settings → Secrets and variables → Actions → New repository secret**

Add the following secrets:

#### Database Credentials
```
DB_HOST=your-hostinger-mysql-host.com
DB_USER=u123456789_fishing
DB_PASS=YourSecurePassword123!
DB_NAME=u123456789_fishing_dir
```

#### FTP Deployment
```
FTP_SERVER=ftp.yourdomain.com
FTP_USERNAME=your-ftp-username
FTP_PASSWORD=your-ftp-password
```

#### Frontend API Configuration
```
PUBLIC_API_URL=https://yourdomain.com/api
PUBLIC_MAPBOX_TOKEN=pk.your_mapbox_token  # Optional
```

### How Secrets Are Used

The GitHub Actions workflow (`.github/workflows/deploy-hostinger.yml`) uses these secrets to:

1. **Generate `.env.production`** for Astro build:
```yaml
- name: Create .env.production file
  run: |
    echo "PUBLIC_MAPBOX_TOKEN=${{ secrets.PUBLIC_MAPBOX_TOKEN }}" >> .env.production
    echo "PUBLIC_API_URL=${{ secrets.PUBLIC_API_URL }}" >> .env.production
```

2. **Generate `config.php`** for PHP backend:
```yaml
- name: Create production config.php
  run: |
    echo "<?php
    define('DB_HOST', '${{ secrets.DB_HOST }}');
    define('DB_USER', '${{ secrets.DB_USER }}');
    ...
    ?>" > ./deploy/public_html/api/config.php
```

3. **Deploy via FTP**:
```yaml
- name: Deploy to Hostinger via FTP
  uses: SamKirkland/FTP-Deploy-Action@v4.3.5
  with:
    server: ${{ secrets.FTP_SERVER }}
    username: ${{ secrets.FTP_USERNAME }}
    password: ${{ secrets.FTP_PASSWORD }}
```

## Manual Production Deployment

If deploying manually (not using GitHub Actions):

### 1. Create Frontend Environment

```bash
cd frontend
cat > .env.production << EOF
PUBLIC_API_URL=https://yourdomain.com/api
PUBLIC_MAPBOX_TOKEN=pk.your_token
PUBLIC_NOMINATIM_EMAIL=contact@yourdomain.com
EOF
```

### 2. Build Frontend

```bash
npm install
npm run build
```

### 3. Create Backend Config

Copy `backend/api/config.example.php` to `backend/api/config.php` and update with production database credentials.

### 4. Deploy

Upload files to your hosting provider:
- `frontend/dist/*` → `public_html/`
- `backend/api/*` → `public_html/api/`

## Using Build Scripts

The scripts in `/scripts` directory now use environment variables:

### `scripts/create_deployment_package.py`

This script reads from:
1. `data-pipeline/.env.docker` (for local Docker)
2. Current directory `.env` (fallback)

To use with custom credentials:

```bash
cd scripts

# Option 1: Create local .env
cat > .env << EOF
DB_HOST=localhost
DB_USER=fishing_user
DB_PASSWORD=fishing_password
DB_NAME=fishing_directory
DB_PORT=3306
EOF

# Option 2: Use Docker environment (default)
# Reads from ../data-pipeline/.env.docker automatically

# Run script
python create_deployment_package.py
```

## Environment Variable Precedence

### Frontend (Astro)
1. `.env.production` (production builds)
2. `.env.local` (local overrides, gitignored)
3. `.env` (shared, can be committed with dummy values)

### Python (Data Pipeline)
1. `.env` in current directory
2. `.env.docker` (for Docker)
3. `os.getenv()` with fallback defaults

### PHP (Backend)
- `config.php` (single source, never committed)
- Generated from `config.example.php` template

## Security Best Practices

### ✅ DO:
- Use GitHub Secrets for production credentials
- Add all credential files to `.gitignore`
- Use different passwords for dev/staging/prod
- Rotate credentials regularly
- Use `.env.example` files to document required variables

### ❌ DON'T:
- Commit `.env` files with real credentials
- Share credentials in pull requests or issues
- Use production credentials in local development
- Hardcode credentials in source files

## Troubleshooting

### Frontend build fails with "PUBLIC_API_URL is not defined"
- **Solution:** Create `.env.production` with required variables

### Python script can't connect to database
- **Solution:** Check `data-pipeline/.env` exists and has correct credentials
- **For Docker:** Ensure using `DB_HOST=localhost` (not `mysql`)

### PHP API returns "Database connection failed"
- **Solution:** Verify `backend/api/config.php` exists with correct credentials
- **For Docker:** Use `DB_HOST=mysql` (not `localhost`)

### GitHub Actions deployment fails
- **Solution:** Check all required secrets are set in repository settings
- Test FTP credentials manually first

## Reference

- Frontend env variables: [Astro Docs - Environment Variables](https://docs.astro.build/en/guides/environment-variables/)
- Python env variables: [python-dotenv](https://github.com/theskumar/python-dotenv)
- GitHub Secrets: [GitHub Docs - Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

**Last Updated:** 2025-11-04
