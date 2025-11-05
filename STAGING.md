# Staging Environment Setup

This document describes how to set up and use the staging environment for wherecanifish.com.

## Overview

The staging environment allows you to test changes before deploying to production. It uses:
- **URL:** https://staging.wherecanifish.com
- **Branch:** `staging`
- **Workflow:** `.github/workflows/deploy-staging.yml`

## Setup Steps

### 1. Hostinger Configuration

You've already set up the subdomain `staging.wherecanifish.com` in Hostinger. Next steps:

1. **Create a staging database** in Hostinger:
   - Go to Hostinger control panel → Databases → MySQL Databases
   - Create a new database (e.g., `u123456789_staging_fish`)
   - Create a new database user or use existing credentials
   - Note down: DB_HOST, DB_USER, DB_PASS, DB_NAME

2. **Import the production database schema** (optional):
   - Export your production database schema
   - Import it into the staging database
   - This gives you a copy of production data to test with

3. **Create staging FTP credentials** (or use same as production):
   - Note down the FTP server, username, and password for the staging subdomain
   - Hostinger may provide the same FTP credentials but different server directories

### 2. GitHub Secrets Configuration

Add the following secrets to your GitHub repository:

Go to: **Repository Settings → Secrets and variables → Actions → New repository secret**

**Staging Database Secrets:**
- `STAGING_DB_HOST` - Your staging database host (e.g., `localhost` or specific host)
- `STAGING_DB_USER` - Your staging database username
- `STAGING_DB_PASS` - Your staging database password
- `STAGING_DB_NAME` - Your staging database name

**Staging FTP Secrets:**
- `STAGING_FTP_SERVER` - FTP server for staging (likely same as production)
- `STAGING_FTP_USERNAME` - FTP username for staging
- `STAGING_FTP_PASSWORD` - FTP password for staging

**Staging API Configuration:**
- `STAGING_API_URL` - The staging API URL: `https://staging.wherecanifish.com/api`

**Reuse Production Secrets:**
- `PUBLIC_MAPBOX_TOKEN` - Already configured (same for staging and production)

### 3. Create the Staging Branch

```bash
# Create and switch to the staging branch
git checkout -b staging

# Push the staging branch to GitHub
git push -u origin staging
```

### 4. Test the Deployment

Once the branch is created and secrets are configured:

1. **Make a test change** to the staging branch
2. **Push to staging:** Changes will automatically deploy via GitHub Actions
3. **Verify:** Visit https://staging.wherecanifish.com

## Workflow Usage

### Automatic Deployments

The staging workflow automatically deploys when:
- You push changes to the `staging` branch
- Changes affect `frontend/**` or `backend/**` directories

### Manual Deployments

You can manually trigger a staging deployment:
1. Go to: **GitHub Actions → Deploy to Staging**
2. Click **Run workflow**
3. Select the `staging` branch
4. Click **Run workflow**

### Testing New Features

Typical workflow for testing new features:

```bash
# Create a feature branch from main
git checkout main
git pull origin main
git checkout -b feature/my-new-feature

# Make your changes
# ... edit files ...

# Commit changes
git add .
git commit -m "Add new feature"

# Merge into staging for testing
git checkout staging
git merge feature/my-new-feature
git push origin staging

# Wait for deployment, test at https://staging.wherecanifish.com

# If tests pass, merge to main for production
git checkout main
git merge feature/my-new-feature
git push origin main
```

### Promoting Staging to Production

When staging tests pass and you're ready for production:

```bash
# Merge staging into main
git checkout main
git pull origin main
git merge staging
git push origin main
```

This will trigger the production deployment workflow.

## Key Differences: Staging vs Production

| Feature | Staging | Production |
|---------|---------|------------|
| **URL** | staging.wherecanifish.com | wherecanifish.com |
| **Branch** | `staging` | `main` |
| **Database** | Separate staging DB | Production DB |
| **Rate Limits** | More relaxed (10 submissions, 50 votes) | Stricter (3 submissions, 10 votes) |
| **CORS** | Allows localhost + staging domain | Production domains only |
| **Purpose** | Testing and QA | Live user traffic |

## Staging Configuration Highlights

The staging environment has these differences from production:

- **Relaxed rate limits** for easier testing
- **CORS allows localhost** for local development testing
- **Separate database** so tests don't affect production data
- **Same API structure** to ensure accurate testing

## Troubleshooting

### Deployment Fails

1. **Check GitHub Secrets:** Ensure all staging secrets are configured
2. **Check GitHub Actions logs:** Go to Actions tab and view the failed workflow
3. **Verify Hostinger setup:** Ensure the staging subdomain is properly configured
4. **Check FTP paths:** Staging should deploy to `/public_html/` under staging subdomain

### Site Doesn't Load

1. **Check DNS:** Ensure `staging.wherecanifish.com` resolves correctly
2. **Check Hostinger:** Verify the subdomain is pointing to the right directory
3. **Check deployment:** Verify files were uploaded via FTP in the GitHub Actions log

### API Errors

1. **Check database connection:** Verify staging database credentials
2. **Check API URL:** Ensure `STAGING_API_URL` is correct in GitHub secrets
3. **Check CORS:** Staging allows `https://staging.wherecanifish.com` and `http://localhost:4321`

## Maintenance Mode

To enable maintenance mode on staging:

1. **Create MAINTENANCE file** in `/public_html/` on staging via FTP
2. **Optional: Create MAINTENANCE_WHITELIST** with allowed IPs (one per line)
3. **To disable:** Delete the MAINTENANCE file

## Next Steps

1. ✅ Staging workflow created
2. ✅ Astro config updated for environment support
3. ⏳ Add GitHub secrets (you need to do this)
4. ⏳ Create staging branch (will be created next)
5. ⏳ Test deployment
6. ⏳ Set up staging database in Hostinger

## Questions?

- Check GitHub Actions logs for deployment issues
- Review the workflow file: `.github/workflows/deploy-staging.yml`
- Compare with production: `.github/workflows/deploy-hostinger.yml`
