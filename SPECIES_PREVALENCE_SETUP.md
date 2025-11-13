# Species Prevalence System (Heat List) - Setup Guide

This document explains how to set up and configure the Species Prevalence System (Heat List) feature.

## Overview

The Species Prevalence System replaces the old voting system with a time-decay based approach that:
- Shows users the most relevant fish species for each spot
- Prevents gaming the system through automatic time-decay scoring
- Dynamically backfills unreported species to guide new users
- Provides an intuitive "heat list" UI with Common/Uncommon/Rare/Unreported tiers

---

## 🔴 What Was Removed

1. **Old "Add Your Fishing Report" button** (replaced by "Log a Catch")
2. **Old "What Fish Are Here?" voting section** (replaced by Heat List)

---

## 📋 Implementation Checklist

### 1. Database Migration

Apply the migration to create new tables:

```bash
cd /home/user/fishing-directory
mysql -u root -p fishing_directory < migrations/003_species_prevalence_system.sql
```

This creates:
- `master_species` - Regional species list with priority order
- `potential_species` - Junction table linking spots to species
- `catch_reports` - User catch data with time-decay scoring
- Trigger to auto-populate species for new spots

**Verification:**

```sql
-- Check tables were created
SHOW TABLES LIKE '%species%';
SHOW TABLES LIKE 'catch_reports';

-- Check Texas species were populated (should return 30 rows)
SELECT COUNT(*) FROM master_species WHERE region = 'TX';

-- Check existing spots got potential_species (should be ~177 spots × 30 species = 5,310 rows)
SELECT COUNT(*) FROM potential_species;
```

---

### 2. Backend API Setup

The following API endpoints are now available:

#### `POST /api/log-catch.php`
- Logs a user catch
- Rate limit: 5 catches per hour per IP
- Validates species is in spot's potential_species list
- Validates date is within last 30 days

**Test:**
```bash
curl -X POST http://localhost:8000/api/log-catch.php \
  -H "Content-Type: application/json" \
  -d '{
    "spot_id": 1,
    "species_id": 1,
    "catch_date": "2025-11-12"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Catch logged successfully",
  "report_id": 123
}
```

#### `GET /api/get-heat-list.php?spot_id=1`
- Returns all potential species for a spot with their scores and tiers
- Species are sorted: reported first (by score DESC), then unreported (by priority)

**Test:**
```bash
curl http://localhost:8000/api/get-heat-list.php?spot_id=1
```

---

### 3. Time-Decay Cron Job

The decay script applies a 5% weekly decay to all catch scores to keep rankings fresh.

**Manual Test:**
```bash
cd /home/user/fishing-directory/backend/scripts
php decay-scores.php
```

**Expected Output:**
```
=== Species Prevalence Time-Decay Script ===
Started at: 2025-11-12 14:30:00

Found 45 reports to decay.

Report ID 12: 10.00 → 9.50 (-5.0%)
Report ID 34: 8.50 → 8.08 (-4.9%)
...

=== Decay Complete ===
Reports updated: 42
Reports deleted: 3
Finished at: 2025-11-12 14:30:02
```

**Setup Daily Cron Job:**

1. Make script executable:
```bash
chmod +x /home/user/fishing-directory/backend/scripts/decay-scores.php
```

2. Add to crontab (runs daily at 2 AM):
```bash
crontab -e
```

Add this line:
```
0 2 * * * /usr/bin/php /home/user/fishing-directory/backend/scripts/decay-scores.php >> /var/log/decay-scores.log 2>&1
```

**Verify Cron Job:**
```bash
crontab -l  # List cron jobs
tail -f /var/log/decay-scores.log  # Watch logs
```

---

### 4. Frontend Changes

The spot page now includes:

**New Section:** "What's Biting Here?" Heat List
- Shows top 7 species (reported + backfilled)
- Click species to log a catch
- "Show all" button to expand full list
- Color-coded tiers: Red (Common), Orange (Uncommon), Blue (Rare), Gray (Unreported)

**New Button:** "🎣 Log a Catch"
- Opens modal with species dropdown
- Validates date within last 30 days
- Shows success notification

**Files Modified:**
- `/frontend/src/pages/texas/[county]/[slug].astro` - Updated spot page UI
- `/frontend/public/js/heat-list.js` - New JavaScript for heat list functionality

**Files Deprecated:**
- `/frontend/public/js/load-spot-content.js` - No longer used (kept for reference)

---

## 🧪 Testing the Feature

### Test Scenario A: Brand New Spot

1. Find a spot with no catch reports
2. Visit the spot page
3. **Expected:** Heat list shows top 5-7 unreported species (by priority) with "[+] Be the first!" labels
4. Click a species → Modal opens with species pre-selected
5. Submit catch → Success notification → Heat list reloads with species now showing as "Rare" (blue)

### Test Scenario B: Spot with Reports

1. Submit 12+ catches for "Largemouth Bass" at a spot (score: 120 points)
2. Submit 1 catch for "Catfish" (score: 10 points)
3. Visit the spot page
4. **Expected:**
   - Bass shows as "Uncommon" (orange) at top
   - Catfish shows as "Rare" (blue) below Bass
   - Next 3-5 spots filled with unreported species
   - "Show all X remaining species..." button present

### Test Scenario C: Time Decay

1. Insert test catch with old date:
```sql
INSERT INTO catch_reports (fishing_spot_id, master_species_id, user_ip_hash, catch_date, base_score, current_score, last_decay_date)
VALUES (1, 1, 'test_hash', '2025-10-01', 10.00, 10.00, '2025-10-01');
```

2. Run decay script:
```bash
php backend/scripts/decay-scores.php
```

3. **Expected:** Score drops from 10.00 → 9.50 (5% weekly decay)

### Test Scenario D: Rate Limiting

1. Submit 5 catches rapidly from same IP
2. **Expected:** All succeed
3. Submit 6th catch
4. **Expected:** Error "Rate limit exceeded. Max 5 catches per hour."

---

## 🎯 Tier Thresholds

| Tier | Score Range | Color | Indicator |
|------|-------------|-------|-----------|
| **Common** | ≥ 5000 | Red | ● |
| **Uncommon** | 1000 - 4999 | Orange | ● |
| **Rare** | 1 - 999 | Blue | ● |
| **Unreported** | 0 | Gray | [+] |

**Example Progression:**
- Day 0: User logs 1 catch = 10 points (Rare)
- Week 52: If no new catches, score = 0.72 points (still Rare, but fading)
- Week 72: Score expires (< 0.01), report deleted

---

## 📊 Database Schema

```
master_species (id, common_name, scientific_name, region, priority_order, icon)
    ↓
potential_species (fishing_spot_id, master_species_id)
    ↓
catch_reports (fishing_spot_id, master_species_id, current_score, last_decay_date)
```

**Key Points:**
- `master_species.priority_order` determines backfill order (1 = most common)
- `potential_species` is auto-populated via trigger when spot is created
- `catch_reports.current_score` decays weekly, gets deleted when < 0.01

---

## 🔧 Troubleshooting

### Issue: "Species not available for this fishing spot"

**Cause:** Species not in `potential_species` for that spot

**Fix:**
```sql
-- Check what species are available for spot ID 1
SELECT ms.common_name
FROM potential_species ps
JOIN master_species ms ON ps.master_species_id = ms.id
WHERE ps.fishing_spot_id = 1;

-- If missing, re-run population query from migration
INSERT INTO potential_species (fishing_spot_id, master_species_id)
SELECT 1, ms.id FROM master_species ms WHERE ms.region = 'TX';
```

### Issue: Heat list not loading

**Check:**
1. Browser console for JavaScript errors
2. API endpoint: `http://localhost:8000/api/get-heat-list.php?spot_id=1`
3. Database connection in `/backend/api/config.php`

### Issue: Decay script not running

**Check:**
1. Cron job is active: `crontab -l`
2. PHP executable path: `which php`
3. File permissions: `ls -la backend/scripts/decay-scores.php`
4. Error logs: `tail -f /var/log/decay-scores.log`

---

## 🚀 Next Steps

1. **Monitor Performance:** Watch for slow queries on `catch_reports` table
2. **Add Indexes:** If queries slow down, add composite indexes
3. **Expand Regions:** Add species for other states (LA, OK, AR, etc.)
4. **Analytics:** Track which species are most logged, adjust priorities

---

## 📝 Files Changed

### New Files
- `migrations/003_species_prevalence_system.sql`
- `backend/api/log-catch.php`
- `backend/api/get-heat-list.php`
- `backend/scripts/decay-scores.php`
- `frontend/public/js/heat-list.js`

### Modified Files
- `frontend/src/pages/texas/[county]/[slug].astro`

### Deprecated Files
- `backend/api/submit-report.php` (old report system, still works)
- `backend/api/vote.php` (old voting system, still works)
- `frontend/public/js/load-spot-content.js` (replaced by heat-list.js)

---

## ✅ Acceptance Criteria Met

- ✅ AC #1: Master species list with priority order
- ✅ AC #2: Potential species auto-populated on spot creation
- ✅ AC #3: "Log a Catch" button with species dropdown
- ✅ AC #4: Time-decay scoring (5% weekly)
- ✅ AC #5: Heat list tiers (Common/Uncommon/Rare/Unreported)
- ✅ AC #6: Dynamic list with backfill and "Show All" button
- ✅ Removed old "Add Your Fishing Report" button
- ✅ Removed old species vote buttons

---

**Questions?** Check the database migration file for detailed comments, or review the API endpoint documentation in each PHP file.
