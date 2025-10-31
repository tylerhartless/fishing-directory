# Install Docker Desktop for Windows

Quick guide to get Docker running on your Windows machine.

## Step 1: Download Docker Desktop

1. **Visit:** https://www.docker.com/products/docker-desktop/
2. Click **"Download for Windows"**
3. Save the installer (DockerDesktopInstaller.exe)

## Step 2: Install Docker Desktop

1. **Run the installer** (DockerDesktopInstaller.exe)
2. **Configuration during install:**
   - ✅ Use WSL 2 instead of Hyper-V (recommended)
   - ✅ Add shortcut to desktop
3. Click **"OK"** and wait for installation
4. **Restart your computer** when prompted

## Step 3: Start Docker Desktop

1. **Launch Docker Desktop** from Start menu
2. **Accept the terms** if prompted
3. Wait for Docker to start (you'll see a whale icon in system tray)
4. When the whale icon stops animating, Docker is ready!

## Step 4: Verify Installation

Open PowerShell and run:

```powershell
docker --version
docker compose version
```

**Expected output:**
```
Docker version 24.x.x, build xxxxx
Docker Compose version v2.x.x
```

## Step 5: Test Docker Works

Run a test container:

```powershell
docker run hello-world
```

You should see: **"Hello from Docker!"**

---

## Troubleshooting

### WSL 2 Required

If you see an error about WSL 2:

1. Open PowerShell as Administrator
2. Run:
   ```powershell
   wsl --install
   ```
3. Restart computer
4. Start Docker Desktop again

### Virtualization Not Enabled

If you see "Virtualization must be enabled":

1. Restart computer
2. Enter BIOS (usually press F2, F10, or DEL during boot)
3. Enable "Virtualization Technology" or "VT-x"
4. Save and exit BIOS
5. Start Docker Desktop

### Docker Desktop Won't Start

1. Right-click Docker Desktop icon
2. Run as Administrator
3. Wait 1-2 minutes

---

## After Docker is Running

Once Docker Desktop is running, come back here and run:

```powershell
cd c:\Users\tyash\Desktop\fishing-directory

# Start all services (note: no hyphen in "docker compose")
docker compose up -d

# Wait 30 seconds for MySQL to initialize

# Check status
docker compose ps
```

You should see 3 containers running:
- fishing_directory_db (MySQL)
- fishing_directory_phpmyadmin
- fishing_directory_api (PHP)

Then access phpMyAdmin: http://localhost:8080

---

## Quick Reference

**Modern Docker Desktop commands (no hyphen):**
```powershell
docker compose up -d          # Start services
docker compose down           # Stop services
docker compose ps             # List running containers
docker compose logs           # View logs
docker compose restart mysql  # Restart a service
```

**Old docker-compose (with hyphen) vs New docker compose:**
- Old: `docker-compose up -d`
- New: `docker compose up -d` ✅ (Use this!)

Docker Desktop (newer versions) uses the built-in `docker compose` command.

---

## Alternative: Use XAMPP Instead

**Don't want to install Docker?** No problem!

You can use XAMPP instead - see [LOCAL_DEVELOPMENT_SETUP.md](LOCAL_DEVELOPMENT_SETUP.md)

**XAMPP is:**
- ✅ Simpler to install
- ✅ Traditional setup
- ✅ No virtualization required

**Docker is:**
- ✅ Cleaner/isolated
- ✅ Industry standard
- ✅ Easier to reset

Both work great! Choose what you're comfortable with.

---

Ready to install Docker Desktop? Let me know once it's running!