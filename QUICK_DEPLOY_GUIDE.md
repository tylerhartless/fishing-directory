# Quick Deploy Guide

## Setup (Do Once)

### 1. Create Develop Branch
```bash
git checkout -b develop
git push -u origin develop
```

### 2. Add GitHub Secrets
Go to GitHub → Settings → Secrets → Add:
- `FTP_SERVER`: ftp.wherecanifish.com
- `FTP_USERNAME`: (your FTP username)
- `FTP_PASSWORD`: (your FTP password)

### 3. Push Workflow
```bash
git add .github/workflows/deploy-hostinger.yml
git commit -m "Add automated deployment"
git push origin main
```

---

## Daily Development

### Work on Develop (Safe - No Auto-Deploy)
```bash
# Make sure you're on develop
git checkout develop

# Make changes, test locally
npm run dev

# Commit and push (DOES NOT deploy)
git add .
git commit -m "Your changes"
git push origin develop
```

---

## Deploy to Production

### When Ready to Go Live
```bash
# Test locally first
npm run build
npm run preview

# Merge to main and push
git checkout main
git merge develop
git push origin main  # ← This auto-deploys!

# Go back to develop for more work
git checkout develop
```

---

## For Now (Manual Deployment)

Since you're still setting things up, **for this session only**:

1. **Upload manually** from `deploy/public_html/` to Hostinger
2. **Fix the 404 error** by replacing all files
3. **Test the site** works correctly
4. **Then** set up GitHub Actions for future deployments

---

## Immediate Action Items

**Right now:**
1. Delete everything in Hostinger `public_html/`
2. Upload entire `deploy/public_html/` contents
3. Clear browser cache, test site
4. Verify API works

**After site is working:**
1. Commit current state to git
2. Push to GitHub
3. Set up GitHub Secrets
4. Enable auto-deployment
5. Always work on `develop` branch

---

## Branch Quick Reference

| Branch | Purpose | Auto-Deploy? |
|--------|---------|--------------|
| `main` | Production | ✅ YES |
| `develop` | Daily work | ❌ NO |
| `feature/*` | Experiments | ❌ NO |

**Golden Rule:** Only push to `main` when ready to deploy!

---

## Current Status

✅ Frontend built with API fix
✅ Deployment package ready in `deploy/`
✅ GitHub Actions workflow created
✅ Branching strategy documented
⏳ Need to upload files to fix 404 error
⏳ Then set up GitHub Actions

You're almost there! Just need to do one final upload to fix the site.
