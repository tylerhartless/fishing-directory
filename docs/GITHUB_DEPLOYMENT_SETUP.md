# GitHub Actions Automated Deployment Setup

This will automatically deploy your site to Hostinger whenever you push to the `main` branch.

## Setup Steps (5 minutes)

### 1. Get Hostinger FTP Credentials

1. **Log into Hostinger hPanel**
2. **Go to:** Files → FTP Accounts
3. **Use the main FTP account** or create a new one
4. **Save these credentials:**
   ```
   FTP Server: ftp.wherecanifish.com (or IP address)
   FTP Username: u123456789
   FTP Password: [your password]
   ```

### 2. Add Secrets to GitHub

1. **Go to your GitHub repository**
   - https://github.com/YOUR_USERNAME/fishing-directory

2. **Navigate to:** Settings → Secrets and variables → Actions

3. **Click "New repository secret"** and add these secrets:

   **FTP_SERVER**
   ```
   ftp.wherecanifish.com
   ```

   **FTP_USERNAME**
   ```
   u123456789  (your actual FTP username)
   ```

   **FTP_PASSWORD**
   ```
   your_ftp_password_here
   ```

   **DB_HOST** (for future use)
   ```
   localhost
   ```

   **DB_USER** (for future use)
   ```
   your_database_username
   ```

   **DB_PASSWORD** (for future use)
   ```
   your_database_password
   ```

   **DB_NAME** (for future use)
   ```
   your_database_name
   ```

### 3. Commit and Push the Workflow

```bash
git add .github/workflows/deploy-hostinger.yml
git commit -m "Add automated deployment workflow"
git push origin main
```

### 4. Watch It Deploy!

1. **Go to:** GitHub → Actions tab
2. **Watch the deployment** run automatically
3. **Check the logs** for any errors
4. **Visit** https://wherecanifish.com when done!

---

## How It Works

### Automatic Deployment
- **Triggers:** Whenever you push to `main` branch
- **Watches:** Changes in `frontend/` or `backend/` folders
- **Deploys:** Via FTP to Hostinger

### What It Does
1. ✅ Checks out your code
2. ✅ Sets up Node.js and Python
3. ✅ Installs dependencies
4. ✅ Builds the frontend (1,102 pages)
5. ✅ Copies backend API files
6. ✅ Updates config.php with production settings
7. ✅ Uploads everything via FTP to Hostinger
8. ✅ Done in ~2-3 minutes!

### Manual Deployment
You can also trigger deployment manually:
1. Go to GitHub → Actions
2. Click "Deploy to Hostinger"
3. Click "Run workflow"
4. Select branch and run

---

## Future Improvements

### Option 1: Database Export (Advanced)
To export the database during deployment, you'd need:
- A way for GitHub to access your database (not recommended for security)
- OR: Keep `fishing-spots.json` in the repo and update it manually

### Option 2: Hostinger API (If Available)
Some hosts offer API deployment instead of FTP:
- Faster
- More secure
- Better logging

### Option 3: Deploy Previews
Add staging environment:
- `main` branch → Production (wherecanifish.com)
- `develop` branch → Staging (staging.wherecanifish.com)

---

## Workflow File Location

`.github/workflows/deploy-hostinger.yml`

## Editing the Workflow

To customize:
1. Edit `.github/workflows/deploy-hostinger.yml`
2. Commit and push
3. GitHub will use the new workflow on next push

---

## Troubleshooting

### Deployment Fails

**Check GitHub Actions logs:**
1. Go to Actions tab
2. Click the failed run
3. Expand the failed step
4. Read error messages

**Common Issues:**

**FTP Connection Failed**
- Check FTP credentials in GitHub Secrets
- Verify FTP server address
- Make sure FTP account is active in Hostinger

**Build Fails**
- Check Node.js version (should be 20)
- Check if dependencies are up to date
- Try building locally first

**Files Not Uploading**
- Check FTP permissions
- Verify `server-dir` path is correct (`./public_html/`)
- Check Hostinger disk space

### Manual Rollback

If deployment breaks the site:
1. Go to Hostinger File Manager
2. Restore from backup (Hostinger keeps daily backups)
3. Or: Upload from your local `deploy/` folder

---

## Cost

**GitHub Actions:** FREE for public repos
- 2,000 minutes/month free for private repos
- This workflow uses ~2-3 minutes per deployment

**Hostinger:** No extra cost - included with hosting

---

## Benefits

✅ **No manual uploads** - Push to GitHub, auto-deploys
✅ **Consistent deploys** - Same process every time
✅ **Deploy history** - See all deployments in Actions tab
✅ **Rollback easy** - Just revert commit and push
✅ **Fast** - 2-3 minutes from push to live
✅ **Reliable** - Runs on GitHub's infrastructure

---

## Next Steps

1. Set up GitHub Secrets (5 minutes)
2. Push the workflow file
3. Make a test change and push
4. Watch it deploy automatically!

Enjoy never having to manually upload files again! 🚀
