# Technical Debt & Optimization Opportunities

**Last Updated:** November 13, 2024  
**Status:** Active tracking document for non-critical improvements

---

## 🎯 Overview

This document tracks technical debt, optimization opportunities, and best practice improvements identified during codebase audits. Items here are **non-critical** and won't break functionality, but addressing them will improve maintainability, performance, and code quality.

**Quick Wins Completed:**
- ✅ Removed backup file from source control
- ✅ Added backup file patterns to `.gitignore`
- ✅ Wrapped all console.log statements in development-only checks

---

## 🟡 Medium Priority (Recommended for Next Sprint)

### 1. Replace Hardcoded RGBA Values with CSS Variables

**Status:** Not Started  
**Effort:** 2-3 hours  
**Impact:** High maintainability improvement

**Issue:**  
Despite defining comprehensive RGBA CSS variables in `retro-colors.css` (lines 100-186), many files still use hardcoded RGBA values:
- 54 instances of `rgba(0, 0, 0, ...)` across 8 files
- 51 instances of `rgba(168, 197, 168, ...)` across 7 files

**Why it matters:**
- Inconsistent theming
- Harder to update color schemes
- Duplicated values increase bundle size

**Solution:**
Create a search-and-replace script or manually update:

```bash
# Example replacements needed:
rgba(0, 0, 0, 0.3) → var(--rgba-black-30)
rgba(0, 0, 0, 0.15) → var(--rgba-black-15)
rgba(168, 197, 168, 0.4) → var(--rgba-sage-40)
rgba(168, 197, 168, 0.6) → var(--rgba-sage-60)
```

**Files affected:**
- `frontend/src/pages/texas/[county]/[slug].astro`
- `frontend/src/layouts/Layout.astro`
- `frontend/src/styles/retro-common.css`
- `frontend/src/styles/search-widget.css`
- `frontend/src/components/ResultsWidget.astro`
- `frontend/src/pages/texas/fishing-without-license.astro`
- `frontend/src/pages/index.astro`

**Estimated benefit:** Easier theme maintenance, smaller CSS after minification

---

### 2. Add Input Validation for County Parameter

**Status:** Not Started  
**Effort:** 30 minutes  
**Impact:** Security hardening

**Location:** `backend/api/spots.php` line 17

**Current code:**
```php
$county = isset($_GET['county']) ? htmlspecialchars($_GET['county'], ENT_QUOTES, 'UTF-8') : null;
```

**Issue:**  
While prepared statements prevent SQL injection, we should validate input format before processing.

**Recommended fix:**
```php
$county = isset($_GET['county']) ? trim($_GET['county']) : null;
if ($county !== null) {
    // Validate county name format (letters, spaces, hyphens only)
    if (!preg_match('/^[a-zA-Z\s\-]+$/', $county)) {
        send_json(['error' => 'Invalid county name format'], 400);
    }
    $county = htmlspecialchars($county, ENT_QUOTES, 'UTF-8');
}
```

**Estimated benefit:** Additional security layer, better error messages

---

### 3. Optimize Map Image Sizes

**Status:** Not Started  
**Effort:** 1-2 hours  
**Impact:** Performance & cost savings

**Location:** `frontend/src/pages/texas/[county]/[slug].astro` line 65

**Current:**
```typescript
// Always loads 900x600px images
const mapUrl = `...static/.../900x600?access_token=...`;
```

**Issue:**  
- Large images slow page loads on mobile
- Higher Mapbox API costs for unnecessary resolution
- Currently uses `loading="eager"` even for below-the-fold images

**Recommended fix:**
```typescript
// Responsive sizes
const mobileMapUrl = `...static/.../600x400?access_token=...`;
const desktopMapUrl = `...static/.../900x600?access_token=...`;

// In HTML:
<picture>
  <source media="(min-width: 768px)" srcset={desktopMapUrl} />
  <img src={mobileMapUrl} alt="..." loading="lazy" />
</picture>
```

**Estimated benefit:** 30-40% faster mobile load times, reduced API costs

---

### 4. Consider Splitting SearchWidget Component

**Status:** Not Started  
**Effort:** 4-6 hours (refactoring)  
**Impact:** Improved testability & maintainability

**Location:** `frontend/src/components/SearchWidget.tsx` (~850 lines)

**Issue:**  
Large component handles multiple concerns:
- Search form UI
- Geolocation logic
- Results display and filtering
- Infinite scroll
- Session storage persistence

**Recommended structure:**
```
components/
├── SearchWidget.tsx (orchestrator, ~200 lines)
├── SearchForm.tsx (form UI, ~150 lines)
├── SearchResults.tsx (results display, ~200 lines)
├── FilterPanel.tsx (filters, ~100 lines)
└── hooks/
    ├── useGeolocation.ts
    ├── useSearchPersistence.ts
    └── useInfiniteScroll.ts
```

**Benefits:**
- Easier to test individual pieces
- Reusable hooks for other components
- Clearer separation of concerns
- Faster development of new features

**Estimated benefit:** Easier maintenance when adding new search features

---

## 🟢 Low Priority (Future Refactoring)

### 5. Simplify Dark Mode Gradient

**Status:** Not Started  
**Effort:** 30 minutes  
**Impact:** Minor code cleanup

**Location:** `frontend/src/layouts/Layout.astro` lines 272-313

**Issue:**  
The `body::after` gradient has 30+ gradient stops that could be simplified to ~10 stops with no visual difference.

**Current:**
```css
background: linear-gradient(180deg,
  rgba(13, 31, 13, 0.6) 0%,
  rgba(13, 30, 13, 0.58) 5%,
  /* ... 28 more stops ... */
  transparent 150%
);
```

**Recommended:**
```css
background: linear-gradient(180deg,
  rgba(13, 31, 13, 0.6) 0%,
  rgba(16, 25, 16, 0.40) 50%,
  rgba(26, 26, 26, 0.10) 125%,
  transparent 150%
);
```

**Estimated benefit:** Smaller CSS bundle, easier to maintain

---

### 6. Create CSS Utility for Scanlines

**Status:** Not Started  
**Effort:** 1 hour  
**Impact:** DRY principle, easier maintenance

**Issue:**  
The scanline effect `repeating-linear-gradient` is duplicated across many components:
- `retro-common.css` (cards, sections, info boxes)
- `search-widget.css` (multiple locations)
- Individual component styles

**Current pattern (repeated ~10 times):**
```css
background: repeating-linear-gradient(
  0deg,
  rgba(0, 0, 0, 0.15) 0px,
  transparent 1px,
  transparent 2px,
  rgba(0, 0, 0, 0.15) 3px
);
```

**Recommended solution:**
```css
/* In retro-common.css */
.retro-scanlines::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    var(--rgba-black-15) 0px,
    transparent 1px,
    transparent 2px,
    var(--rgba-black-15) 3px
  );
  pointer-events: none;
  z-index: 1;
}

/* Light mode variant */
[data-theme="light"] .retro-scanlines::before {
  background: repeating-linear-gradient(
    0deg,
    var(--rgba-black-01) 0px,
    transparent 1px,
    transparent 2px,
    var(--rgba-black-01) 3px
  );
}
```

Then replace all instances with the `.retro-scanlines` class.

**Estimated benefit:** Single source of truth for scanline effect

---

### 7. Separate Dev and Production CORS Config

**Status:** Not Started  
**Effort:** 15 minutes  
**Impact:** Minor security improvement

**Location:** `backend/api/config.example.php` line 113

**Current code:**
```php
if (in_array($origin, $allowed_origins) || strpos($origin, 'localhost') !== false) {
    header('Access-Control-Allow-Origin: ' . $origin);
}
```

**Issue:**  
The `localhost` check applies in all environments, which is overly permissive for production.

**Recommended fix:**
```php
function set_cors_headers() {
    global $allowed_origins;
    $origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : '';
    
    // Development: Allow any localhost
    if (getenv('APP_ENV') === 'development' && strpos($origin, 'localhost') !== false) {
        header('Access-Control-Allow-Origin: ' . $origin);
        return;
    }
    
    // Production: Strict origin checking
    if (in_array($origin, $allowed_origins)) {
        header('Access-Control-Allow-Origin: ' . $origin);
    }
}
```

**Estimated benefit:** Slightly better security posture

---

### 8. Add Strict Types to PHP Files

**Status:** Not Started  
**Effort:** 15 minutes  
**Impact:** Better type safety, catch bugs earlier

**Issue:**  
PHP files don't use strict type declarations.

**Recommended fix:**
Add to the top of each PHP file (after opening `<?php`):
```php
<?php
declare(strict_types=1);

// rest of file...
```

**Files to update:**
- `backend/api/spots.php`
- `backend/api/get-heat-list.php`
- `backend/api/log-catch.php`
- `backend/api/submit-report.php`
- `backend/api/reports.php`
- `backend/api/county-stats.php`
- `backend/api/config.php`

**Estimated benefit:** Catch type errors early, more predictable code

---

### 9. Standardize Error Handling in PHP

**Status:** Not Started  
**Effort:** 30 minutes  
**Impact:** Consistent API responses

**Issue:**  
Some endpoints use `send_json(['error' => ...])`, others use `die(json_encode(...))`.

**Example inconsistency:**
```php
// config.php line 99 (old style)
die(json_encode(['error' => 'Database connection failed']));

// log-catch.php line 69 (new style)
send_json(['error' => 'Invalid catch_date format'], 400);
```

**Recommended fix:**
Replace all `die(json_encode(...))` with `send_json()` calls for consistency.

**Estimated benefit:** Easier to maintain, consistent error responses

---

### 10. Extract Magic Numbers to Constants

**Status:** Not Started  
**Effort:** 30 minutes  
**Impact:** Improved code readability

**Issue:**  
Magic numbers scattered throughout code make it hard to understand thresholds and limits.

**Examples:**
```typescript
// get-heat-list.php line 49
define('TIER_THRESHOLD_COMMON', 50);  // Good! Already done

// SearchWidget.tsx line 59 - should extract
const [searchRadius, setSearchRadius] = useState<number>(100); // Why 100?

// heat-list.js line 80 - should extract
const SHOWCASE_LIMIT = 3; // Good! Already done
```

**Recommended additions:**
```typescript
// SearchWidget.tsx
const DEFAULT_SEARCH_RADIUS = 100; // miles
const DEFAULT_DISPLAY_COUNT = 20;
const INFINITE_SCROLL_INCREMENT = 20;
```

**Estimated benefit:** Self-documenting code, easier to adjust thresholds

---

### 11. Update Theme Toggle ARIA Label Dynamically

**Status:** Not Started  
**Effort:** 15 minutes  
**Impact:** Minor accessibility improvement

**Location:** `frontend/src/layouts/Layout.astro` line 84

**Current:**
```html
<button id="theme-toggle" class="theme-toggle" aria-label="Toggle dark mode">
```

**Issue:**  
The `aria-label` is static, but button content changes between moon (☾) and sun (☀).

**Recommended fix:**
```javascript
// In theme toggle script
const setTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  
  // Update aria-label
  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.setAttribute('aria-label', 
      theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
    );
  }
};
```

**Estimated benefit:** Better screen reader experience

---

### 12. Enable Compression in Apache

**Status:** Not Started  
**Effort:** 15 minutes  
**Impact:** Faster page loads

**Location:** `docker-compose.yml` or Apache config

**Issue:**  
No mention of gzip/brotli compression for static assets.

**Recommended fix:**
Create `backend/api/.htaccess`:
```apache
# Enable compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Enable gzip compression
<IfModule mod_gzip.c>
  mod_gzip_on Yes
  mod_gzip_item_include file \.(html?|txt|css|js|json)$
</IfModule>
```

**Estimated benefit:** 20-30% smaller transfer sizes

---

### 13. Create .env.example File

**Status:** Not Started  
**Effort:** 10 minutes  
**Impact:** Better developer onboarding

**Issue:**  
New developers don't know what environment variables to set.

**Recommended file:** `frontend/.env.example`
```bash
# Frontend Configuration
PUBLIC_API_URL=http://localhost:8000/api
PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
PUBLIC_NOMINATIM_EMAIL=your@email.com

# Site URL (for production builds)
PUBLIC_SITE_URL=https://wherecanifish.com

# Staging URL (for staging builds)
# PUBLIC_SITE_URL=https://staging.wherecanifish.com
```

And `backend/.env.example`:
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fishing_directory
DB_USER=fishing_user
DB_PASSWORD=your_password_here

# Environment
APP_ENV=development

# CORS Allowed Origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:4321,http://localhost:3000
```

**Estimated benefit:** Faster onboarding, fewer setup issues

---

## 📊 Priority Matrix

| Task | Priority | Effort | Impact | When |
|------|----------|--------|--------|------|
| Replace RGBA with CSS vars | Medium | 2-3h | High | Next sprint |
| Add county validation | Medium | 30m | Medium | Next sprint |
| Optimize map sizes | Medium | 1-2h | High | Next sprint |
| Split SearchWidget | Medium | 4-6h | High | When adding features |
| Simplify gradients | Low | 30m | Low | During refactor |
| CSS scanline utility | Low | 1h | Medium | During CSS cleanup |
| Separate CORS config | Low | 15m | Low | Before launch |
| Add PHP strict types | Low | 15m | Low | During maintenance |
| Standardize errors | Low | 30m | Low | During maintenance |
| Extract magic numbers | Low | 30m | Low | During refactor |
| Update aria-label | Low | 15m | Low | During a11y review |
| Enable compression | Low | 15m | Medium | Before launch |
| Create .env.example | Low | 10m | Low | Before launch |

---

## 🎯 Recommended Roadmap

### Sprint 1 (Week 1-2)
- Replace hardcoded RGBA values with CSS variables
- Add input validation for county parameter
- Optimize map image sizes

### Sprint 2 (Week 3-4)
- Enable compression in Apache
- Create .env.example files
- Separate dev/prod CORS config

### Sprint 3 (During next feature development)
- Split SearchWidget component when adding new search features
- Extract magic numbers to constants
- Update theme toggle aria-label

### Ongoing Maintenance
- Add PHP strict types as files are touched
- Standardize error handling as endpoints are updated
- Simplify CSS gradients during CSS refactoring sessions

---

## ✅ Completed Quick Wins

- **2024-11-13:** Deleted `index.astro.backup` file from source control
- **2024-11-13:** Added `.backup`, `.bak`, and `*~` patterns to `.gitignore`
- **2024-11-13:** Wrapped all `console.log` statements (19 instances) in `isDev` checks across:
  - `frontend/src/lib/database.ts` (8 instances)
  - `frontend/src/components/SearchWidget.tsx` (5 instances)
  - Other components (6 instances)

---

## 📝 Notes

- **Do not prematurely optimize:** The site functions perfectly as-is. These are maintenance items.
- **Test after changes:** While these are non-breaking changes, always test in development first.
- **Track progress:** Update this document as items are completed.
- **Review quarterly:** Re-evaluate priorities as the codebase evolves.

---

**Maintained by:** Development Team  
**Next Review:** February 2025

