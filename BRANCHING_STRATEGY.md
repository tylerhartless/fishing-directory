# Git Branching Strategy

## Branch Structure

```
main (production)     ← Auto-deploys to wherecanifish.com
└── develop           ← Daily work, testing, experiments
    └── feature/*     ← Individual features/fixes
```

## Quick Start

### Initial Setup (One Time)

```bash
# Create develop branch
git checkout -b develop
git push -u origin develop

# Set develop as your default working branch
git checkout develop
```

### Daily Workflow

```bash
# Always work on develop or feature branches
git checkout develop

# Make changes, test locally
npm run dev

# Commit your work
git add .
git commit -m "Add new feature"
git push origin develop

# When ready to deploy to production:
git checkout main
git merge develop
git push origin main  # This triggers auto-deployment!
```

---

## Branch Rules

### `main` Branch
- **Purpose:** Production code only
- **Protection:** Only merge when ready to deploy
- **Triggers:** Auto-deploys to Hostinger on every push
- **Rule:** Never work directly on main!

### `develop` Branch
- **Purpose:** Daily development work
- **Protection:** None (push freely)
- **Testing:** Test locally with `npm run dev`
- **Rule:** This is your default branch

### `feature/*` Branches
- **Purpose:** Individual features or experiments
- **Example:** `feature/add-louisiana-data`
- **Merge to:** `develop` first, then `main` when ready

---

## Example Workflows

### Scenario 1: Quick Fix

```bash
# On develop branch
git checkout develop

# Make the fix
vim frontend/src/pages/index.astro
npm run dev  # Test locally

# Commit
git add .
git commit -m "Fix homepage typo"
git push origin develop

# Deploy when ready
git checkout main
git merge develop
git push origin main  # Auto-deploys!
```

### Scenario 2: New Feature (Big Changes)

```bash
# Create feature branch from develop
git checkout develop
git checkout -b feature/add-search-filters

# Work on feature over multiple days
# ... make changes ...
git add .
git commit -m "Add county filter"
# ... more changes ...
git commit -m "Add type filter"

# Push feature branch (does NOT deploy)
git push origin feature/add-search-filters

# When feature is done, merge to develop
git checkout develop
git merge feature/add-search-filters
git push origin develop

# Test on develop, then deploy
git checkout main
git merge develop
git push origin main  # Auto-deploys!
```

### Scenario 3: Emergency Hotfix

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug

# Fix the bug
# ... make changes ...
git add .
git commit -m "Fix critical database connection bug"

# Merge to main and deploy immediately
git checkout main
git merge hotfix/critical-bug
git push origin main  # Auto-deploys!

# Also merge to develop so fix is in both branches
git checkout develop
git merge hotfix/critical-bug
git push origin develop
```

---

## Testing Before Deploying

### Local Testing (Always Do This)

```bash
# Start local dev server
cd frontend
npm run dev

# Visit http://localhost:4321
# Test your changes thoroughly
```

### Build Test (Before Deploying)

```bash
# Test the production build
npm run build
npm run preview

# If build succeeds, safe to merge to main
```

---

## Deployment Checklist

Before merging to `main`:

- [ ] Changes tested locally
- [ ] Production build succeeds
- [ ] No console errors
- [ ] Database changes documented
- [ ] API endpoints work
- [ ] Ready for users to see

---

## Protecting Main Branch (Recommended)

On GitHub:

1. **Go to:** Settings → Branches
2. **Add rule** for `main`
3. **Enable:**
   - Require pull request before merging
   - Require status checks to pass
   - No direct pushes to main

This forces you to use Pull Requests, which:
- Gives you a chance to review changes
- Allows you to test before deploying
- Creates a deployment history

---

## Pull Request Workflow (Optional but Recommended)

```bash
# Work on develop
git checkout develop
# ... make changes ...
git add .
git commit -m "Add new state data"
git push origin develop

# On GitHub, create Pull Request:
# develop → main

# Review the changes
# Merge PR when ready
# Auto-deploys!
```

---

## Common Commands

```bash
# Check what branch you're on
git branch

# Switch branches
git checkout develop
git checkout main

# See status
git status

# See recent commits
git log --oneline -10

# Undo last commit (before push)
git reset --soft HEAD~1

# Discard all local changes
git reset --hard origin/develop
```

---

## What NOT To Do

❌ **Never work directly on main**
```bash
git checkout main  # ❌ Don't do this for daily work!
# make changes
git push  # ❌ This deploys to production immediately!
```

✅ **Always work on develop**
```bash
git checkout develop  # ✅ Do this!
# make changes
git push  # ✅ Safe, doesn't deploy
```

❌ **Don't merge untested code to main**
```bash
git checkout main
git merge develop  # ❌ Without testing first!
```

✅ **Test before merging**
```bash
git checkout develop
npm run build  # ✅ Test build
git checkout main
git merge develop  # ✅ Safe!
```

---

## Current Workflow File

The GitHub Action in `.github/workflows/deploy-hostinger.yml` is configured to:

- ✅ Only deploy when pushing to `main`
- ✅ Ignore pushes to other branches
- ✅ Can be manually triggered from any branch

This means:
- Work on `develop` safely (no deployments)
- Merge to `main` only when ready to deploy
- Production stays stable

---

## Summary

**Daily work:**
```bash
git checkout develop
# ... work ...
git push origin develop  # Safe, doesn't deploy
```

**Deploy to production:**
```bash
git checkout main
git merge develop
git push origin main  # Deploys automatically!
```

**Rule of thumb:**
- develop = experiment freely
- main = production ready only

This keeps wherecanifish.com stable while you build! 🚀
