# Backend API

PHP-based REST API for dynamic features (fishing reports, user submissions, votes).

## Setup on Hostinger

### 1. Upload Files

Upload the `api/` folder to your Hostinger account:

```
public_html/
└── api/
    ├── config.php
    ├── reports.php
    ├── submit-report.php
    ├── get-heat-list.php
    └── log-catch.php
```

### 2. Configure Database Connection

Edit `api/config.php` and update:

```php
define('DB_HOST', 'your-hostinger-mysql-host.com');
define('DB_USER', 'your_database_user');
define('DB_PASS', 'your_database_password');
define('DB_NAME', 'fishing_directory');
```

Also update `$allowed_origins` with your frontend domain.

### 3. Test Endpoints

Visit these URLs to test:

- `https://yourdomain.com/api/reports.php?spot_id=1`
- `https://yourdomain.com/api/get-heat-list.php?spot_id=1`
- `https://yourdomain.com/api/log-catch.php` (POST JSON payload)

You should see JSON responses.

## API Endpoints

### GET /api/reports.php

Get fishing reports for a spot.

**Parameters:**
- `spot_id` (int, required)

**Response:**
```json
{
  "success": true,
  "count": 2,
  "reports": [
    {
      "fish_species": "Largemouth Bass",
      "catch_count": 3,
      "report_date": "2025-10-30",
      "notes": "Great morning fishing",
      "submitted_date": "2025-10-30"
    }
  ]
}
```

### POST /api/submit-report.php

Submit a new fishing report.

**Body (JSON):**
```json
{
  "spot_id": 123,
  "fish_species": "Catfish",
  "catch_count": 2,
  "report_date": "2025-10-30",
  "notes": "Caught on live bait"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Report submitted for review",
  "report_id": 456
}
```

**Rate Limits:**
- 3 submissions per hour per IP

### GET /api/get-heat-list.php

Get the species prevalence (heat list) for a fishing spot.

**Parameters:**
- `spot_id` (int, required)

**Response:**
```json
{
  "success": true,
  "species": [
    {
      "id": 1,
      "common_name": "Largemouth Bass",
      "icon": "🎣",
      "tier": "common",
      "has_reports": true,
      "report_count": 4,
      "total_score": 120.5
    }
  ]
}
```

### POST /api/log-catch.php

Log a catch for the Species Prevalence System.

**Body (JSON):**
```json
{
  "spot_id": 123,
  "species_id": 5,
  "catch_date": "2025-11-12"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Catch logged successfully",
  "report_id": 789
}
```

**Rate Limits:**
- 5 catches per hour per IP (staging relaxed to 10)

## Security Features

1. **CORS Protection** - Only allowed domains can access API
2. **Rate Limiting** - Prevents spam (3 reports/hour, 5 catches/hour; staging uses relaxed limits)
3. **Input Validation** - All inputs sanitized
4. **Prepared Statements** - SQL injection prevention
5. **Privacy** - IP addresses are hashed, not stored
6. **Content Moderation** - Reports require approval

## Moderation

All fishing reports are submitted with `is_approved=0`. You'll need to:

1. Log into phpMyAdmin
2. Review pending reports:
   ```sql
   SELECT * FROM fishing_reports WHERE is_approved = 0
   ```
3. Approve legitimate reports:
   ```sql
   UPDATE fishing_reports SET is_approved = 1 WHERE id = 123
   ```

Or build a simple admin panel (future feature).

## Troubleshooting

**Problem:** "Database connection failed"
**Solution:** Check `config.php` credentials, verify database exists

**Problem:** CORS errors in browser console
**Solution:** Add your frontend domain to `$allowed_origins` in `config.php`

**Problem:** "Too many submissions"
**Solution:** This is rate limiting working. Wait 1 hour or adjust `RATE_LIMIT_SUBMISSIONS` in `config.php`
