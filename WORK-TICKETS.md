# WhereCanIFish.com - Work Tickets
**Pre-Launch Development Roadmap**

**Last Updated:** November 12, 2025
**Status:** Pre-Launch
**Estimate:** 129-167 hours total

---

## Design Philosophy

### Dark Mode: Terminal Aesthetic
- Neon green (`#39ff14`) accents
- Black backgrounds
- CRT scanlines
- Tech/cyberpunk vibe

### Light Mode: 1980s Fishing Magazine Ad
- **Colors from Tournament V-17 boat:**
  - Warm cream background `#f2ebe0`
  - Orange racing stripe `#e85d2a` (primary CTAs)
  - Red accent stripe `#c41e1a` (highlights)
  - Charcoal motor `#3a3a3a` (headers)
  - Black `#1a1a1a` (text, borders)

- **Design from vintage Bass Pro Shops ads:**
  - Bold ALL CAPS headlines
  - Structured catalog-style layouts
  - Thick borders (3-4px), double borders
  - Starbursts/badges ("NEW!", "POPULAR")
  - High contrast for outdoor readability
  - Large bold numbers for stats

### Mobile-First Approach
- Design for 320px-428px first
- Scale up to desktop (1024px+)
- Touch targets minimum 44px
- All interactions optimized for fingers, not mouse

---

## Sprint 0: Foundation & Audit

### TICKET-001: Repository Audit & CSS Analysis ✅ COMPLETE
**Estimate:** 1-2 hours
**Depends on:** None

**Description:**
Get repo access and perform comprehensive audit of current codebase state.

**Acceptance Criteria:**
- [x] Repo access obtained (GitHub URL or local path)
- [x] Complete CSS file structure documented
- [x] Import chains mapped (which files import what)
- [x] Duplicate styles identified across files
- [x] Component audit complete (shared vs custom styles)
- [x] Mobile-first assessment: identify mobile issues
- [x] Findings document created with refactoring priorities

---

### TICKET-002: Create GitHub Project & Issue Templates ✅ COMPLETE
**Estimate:** 30 minutes
**Depends on:** None

**Description:**
Set up project management infrastructure.

**Acceptance Criteria:**
- [x] GitHub project created
- [x] Issue templates defined (bug, feature, css, design)
- [x] Milestones created (Pre-Launch, Post-Launch, Future)
- [x] Labels configured (priority, type, platform)
- [x] This ticket list converted to actual GitHub issues

---

### TICKET-034: County Many-to-Many Relationship Schema 🔴 BLOCKER
**Estimate:** 4-6 hours
**Depends on:** TICKET-001
**Status:** Needs Review

**Description:**
Update spot data model to support association with multiple counties. Large water bodies often span multiple counties, and the current "Multiple Counties" label is ambiguous and poor for SEO.

**Acceptance Criteria:**

**Schema Update:**
- [x] Update `spots` table/model to support many-to-many relationship with counties
- [x] Create junction table (`spot_counties` and `counties` reference table)
- [x] Migration script to convert existing data (`migrations/002_county_many_to_many.sql`)
- [x] Handle spots currently labeled "Multiple Counties" (migration ready, actual mapping deferred to data pipeline work)
- [x] Data validation: junction table enforces relationships

**Spot Detail Page Display:**
- [x] Display all associated counties on spot page
- [x] Format: "Counties: Montgomery & Walker" or "Montgomery, Walker, & Travis"
- [x] Link each county name to its county page
- [x] Show primary county first, then alphabetically

**County Landing Page Display:**
- [x] Update county pages to query spots by many-to-many relationship
- [x] Spots appear on ALL relevant county pages (via API join)
- [x] API uses LEFT JOIN for backward compatibility
- [x] Performance optimized with proper indexes

**SEO Benefits:**
- [x] Remove ambiguous "Multiple Counties" label (ready for when data is mapped)
- [x] Each county page shows complete list of accessible spots
- [x] Better discoverability regardless of entry point

**Implementation Notes:**
- Migration file created: `migrations/002_county_many_to_many.sql`
- API updated: `backend/api/spots.php` now returns `counties` array
- Frontend updated: Helper functions in `database.ts` support both legacy and new format
- Spot detail pages: Show all counties with links
- Backward compatible: Legacy `county` field preserved
- Documentation: `migrations/README.md` explains process

**Data Migration:**
- [ ] Identify all spots currently labeled "Multiple Counties"
- [ ] Research and assign correct county associations
- [ ] Document data source for county boundaries
- [ ] Test migration on staging before production

**Testing:**
- [ ] Test large lake (multiple counties) displays correctly
- [ ] Test single county spot still works
- [ ] Test county page queries are efficient
- [ ] Verify no broken links

---

### TICKET-031: Astro Framework Best Practices Audit 🔴 BLOCKER
**Estimate:** 6-8 hours
**Depends on:** TICKET-001

**Description:**
Ensure we're maximizing Astro's capabilities for performance and UX.

**Acceptance Criteria:**

**Hybrid Rendering Model (SSG + ISR):**
- [ ] **SSG (Static Site Generation):** Pre-render at build time:
  - Homepage
  - All /state pages
  - All /county pages
  - /fishing-without-a-license landing page
  - Other static content pages (About, Contact, etc.)
- [ ] **ISR (Incremental Static Regeneration):** On-demand generation for:
  - Individual /spot/{spotName} detail pages
  - Generate just-in-time on first request
  - Cache at CDN edge for subsequent visitors
  - Document revalidation strategy
- [ ] Build time remains fast (<5 minutes) regardless of spot count
- [ ] Document hybrid approach and when to use each method

**View Transitions:**
- [ ] Implement Astro View Transitions API
- [ ] Add `<ViewTransitions />` to layout
- [ ] Define transition names for shared elements
- [ ] Test morph animations between pages
- [ ] Graceful fallback for unsupported browsers
- [ ] Works on iOS Safari and Chrome Android

**Islands Architecture:**
- [ ] Audit all interactive components
- [ ] Ensure client-side JS only loads where needed
- [ ] Use `client:load`, `client:idle`, `client:visible` appropriately
- [ ] Species voting = `client:visible` (load when scrolled to)
- [ ] Search widget = `client:load` (needed immediately)
- [ ] Map = `client:idle` (load after page interactive)
- [ ] Measure JS bundle size reduction

**Image Optimization:**
- [ ] Use `<Image />` component from `astro:assets`
- [ ] Automatic WebP/AVIF conversion
- [ ] Responsive images with srcset
- [ ] Lazy loading below fold

**Performance:**
- [ ] Lighthouse mobile score 95+
- [ ] TTI < 2s, FCP < 1s, LCP < 2.5s, CLS < 0.1
- [ ] Test on 3G network

**Documentation:**
- [ ] Document Astro patterns used
- [ ] When to use islands vs static
- [ ] View Transitions best practices
- [ ] Component hydration strategy
- [ ] Hybrid rendering model explained (SSG vs ISR)

---

## Sprint 1: CSS Architecture & Color Unification

### TICKET-003: Refactor Search Widget CSS (Mobile-First) ✅ COMPLETE
**Estimate:** 3-4 hours
**Depends on:** TICKET-001, TICKET-031

**Description:**
Remove bright green `#00ff00`, use retro-common.css classes, optimize for mobile.

**Acceptance Criteria:**
- [x] Replace custom button styles with `.retro-btn-search`
- [x] Replace custom input styles with `.retro-input`
- [x] Replace `#00ff00` with proper colors (`#39ff14` sparingly, `#d4a574` for labels)
- [x] Use retro-colors.css variables throughout
- [x] **MOBILE:** Full-width buttons, min 44px touch targets
- [x] **MOBILE:** Stack all elements vertically
- [x] **MOBILE:** Large readable text (VT323 scales well)
- [x] **DESKTOP:** Maintain layout, scale appropriately
- [x] Test on actual devices (iOS Safari, Chrome Android)
- [x] Test dark and light modes
- [x] No visual regressions

---

### TICKET-004: Consolidate Home Page CSS (Mobile-First) ✅ COMPLETE
**Estimate:** 4-5 hours
**Depends on:** TICKET-001, TICKET-031

**Description:**
Move reusable home page styles to shared files, ensure mobile excellence.

**Acceptance Criteria:**
- [x] Duplicate styles moved to retro-common.css
- [x] Stat boxes use `.retro-card` class
- [x] County cards use 4-color border rotation (sage/rust/moss/tan)
- [x] **MOBILE:** Single column layout, cards full-width
- [x] **MOBILE:** Touch-friendly spacing (min 8px gaps)
- [x] **MOBILE:** Readable text sizes (16px minimum body)
- [x] **DESKTOP:** 2-3 column grid
- [x] Page-specific CSS reduced 30%+
- [x] Layout doesn't break at any viewport size
- [x] Test on actual devices

---

### TICKET-005: Site-Wide Color Audit & Cleanup ✅ COMPLETE
**Estimate:** 4-6 hours
**Depends on:** TICKET-003, TICKET-004

**Description:**
Remove all non-standard colors across entire site.

**Acceptance Criteria:**
- [x] Search all CSS for colors not in retro-colors.css
- [x] Replace with proper CSS variables
- [x] Document any intentional exceptions
- [x] Verify dark mode consistency (backgrounds, accents, borders, glows)
- [x] Verify light mode consistency (backgrounds, accents, borders, shadows)
- [x] Test all pages on mobile (320px-428px)
- [x] Test all pages on desktop (1024px+)

---

### TICKET-006: Page Header Standardization (Mobile-First) ✅ COMPLETE
**Estimate:** 2-3 hours
**Depends on:** TICKET-001

**Description:**
Ensure all pages use `.retro-page-header` correctly on all devices.

**Acceptance Criteria:**
- [x] Audit all pages for header usage
- [x] Add `.retro-page-header` to pages missing it
- [x] Verify h1 colors: `#ffffff` (dark) / `#3a2820` (light)
- [x] Verify subtitle colors: `#a8c5a8` (dark) / `#2d2d2d` (light)
- [x] **MOBILE:** Header text scales down appropriately
- [x] **MOBILE:** Adequate padding (don't touch edges)
- [x] **MOBILE:** Breadcrumbs wrap or scroll horizontally
- [x] **DESKTOP:** Full-size headers
- [x] Verify gradient behavior (show/hide correctly)
- [x] Consistent spacing across all pages

---

### TICKET-032: Refine Light Mode Colors (Boat-Inspired) ✅ COMPLETE
**Estimate:** 4-5 hours
**Depends on:** TICKET-001, TICKET-005

**Description:**
Update light mode palette to match Tournament V-17 racing stripes.

**Acceptance Criteria:**
- [x] Update retro-colors.css with boat stripe colors
- [x] Warm cream background `#f2ebe0` (already done, verify)
- [x] Orange `#e85d2a` (racing stripe) for CTAs and primary accents
- [x] Red `#c41e1a` (thin stripe) for secondary accents
- [x] Charcoal `#3a3a3a` (motor cowling) for headers
- [x] Black `#1a1a1a` for text and borders
- [x] Apply consistently across all components
- [x] Test all pages in light mode
- [x] Compare side-by-side with boat reference photos

---

### TICKET-033: Light Mode Vintage Ad Aesthetic 🔴 BLOCKER
**Estimate:** 8-10 hours
**Depends on:** TICKET-032, TICKET-005
**Status:** Needs Review

**Description:**
Make light mode look like a 1980s Bass Pro Shops catalog advertisement.

**Acceptance Criteria:**

**Typography:**
- [x] Bold, ALL CAPS headlines (like "TOURNAMENT V-17" in ad)
- [x] High contrast for print legibility
- [x] VT323 for headers, system font for body
- [x] Large bold numbers for stats/pricing style
- [x] Letterpress effect on headers (subtle shadow below)

**Layout:**
- [x] Structured catalog-style grids
- [x] Boxy, square corners (no border-radius)
- [x] Generous padding (print ad whitespace)
- [x] Clear sections with borders

**Borders & Elements:**
- [x] Thick borders: 4px solid
- [x] Double borders for emphasis (via pseudo-elements)
- [x] Orange/red racing stripe accents

**Colors Applied:**
- [x] Warm cream backgrounds (from boat stripe)
- [x] Orange CTAs and highlights (racing stripe)
- [x] Red accents (thin racing stripe)
- [x] Charcoal headers (motor)
- [x] Black borders and text (stripe outlines)

**Components:**
- [x] Buttons: Orange gradient with black border, glossy decal style
- [x] Cards: White background on cream, thick borders, left orange accent stripe
- [x] Headers: Charcoal with orange bottom border (racing stripe style)
- [x] Stats boxes: Bold numbers, catalog pricing style

**NOT Included:**
- [x] ❌ Aluminum/metallic texture effects
- [x] ❌ Boat rivet details
- [x] ❌ Chrome hardware accents
- [x] ✅ Just colors and vintage ad layout style

**Testing:**
- [x] Applied consistently across all components
- [x] High contrast for outdoor readability
- [x] Warm, inviting, nostalgic feel achieved

---

### TICKET-007: Create CSS Usage Documentation 🟢 MEDIUM
**Estimate:** 1-2 hours  
**Depends on:** TICKET-005

**Description:**  
Document when to use shared vs custom styles.

**Acceptance Criteria:**
- [ ] CSS architecture guide written
- [ ] Mobile-first approach documented
- [ ] When to use retro-common classes explained
- [ ] When custom component CSS is acceptable
- [ ] Color variable naming conventions documented
- [ ] Examples of correct usage patterns
- [ ] Responsive breakpoint standards documented
- [ ] Add to repo README or docs folder

---

## Sprint 2: Critical Bug Fixes

### TICKET-008: Fix Location Search Hang Bug (Mobile & Desktop) 🔴 BLOCKER
**Estimate:** 2-3 hours  
**Depends on:** None

**Description:**  
"Use Current Location" button hangs when pressed second time.

**Acceptance Criteria:**
- [ ] Bug reproduced on mobile and desktop
- [ ] Root cause identified
- [ ] Geolocation state properly reset between searches
- [ ] Event listener cleanup implemented
- [ ] Test multiple consecutive uses on mobile
- [ ] Test rapid tapping on touchscreen
- [ ] Test on iOS Safari and Chrome Android
- [ ] No console errors

---

### TICKET-009: Fix Fish Species API on Staging 🔴 BLOCKER
**Estimate:** 2-4 hours  
**Depends on:** None

**Description:**  
Fish species API works locally but fails on staging.wherecanifish.com.

**Acceptance Criteria:**
- [ ] Debug staging console errors (CORS, network, etc.)
- [ ] Verify environment variables in staging deployment
- [ ] Check API endpoint URLs (localhost vs production)
- [ ] Test API directly from staging server (curl/fetch)
- [ ] Review Astro build logs for API failures
- [ ] Confirm data displays correctly on staging
- [ ] Test on mobile browsers
- [ ] Document fix in code comments

---

### TICKET-010: Implement Dark Mode Map Switching (Mobile-First) 🔴 BLOCKER
**Estimate:** 4-5 hours  
**Depends on:** None

**Description:**  
Maps don't switch to dark tiles when dark mode is active on spot pages.

**Acceptance Criteria:**
- [ ] Dark mode: Mapbox dark-v11 style
- [ ] Light mode: Mapbox outdoors-v12 style
- [ ] Map switches when theme toggle clicked
- [ ] Zoom set to 14.5 for both modes
- [ ] **MOBILE:** Map height 300px
- [ ] **MOBILE:** Touch-friendly zoom controls
- [ ] **MOBILE:** Map centers properly on small screens
- [ ] **DESKTOP:** Map height 400px
- [ ] Map markers themed (`#39ff14` dark, `#e85d2a` light)
- [ ] Debounce theme toggle (300-500ms) to prevent excess Mapbox API calls
- [ ] Test on actual mobile devices

---

## Sprint 3: Spot Page Redesign (Mobile-First)

### TICKET-011: Build Spot Page Base Layout (Mobile-First) 🟡 PENDING REVIEW
**Estimate:** 8-10 hours
**Depends on:** TICKET-031, TICKET-033
**Status:** On feature branch, pending review

**Description:**  
Create new terminal-style spot page layout, designed mobile-first, leveraging Astro SSG.

**Acceptance Criteria:**

**MOBILE (320px-428px):**
- [ ] Header with breadcrumbs (terminal style `>_`, wraps or scrolls)
- [ ] Full-width map section (300px height)
- [ ] GPS coordinates section: stacked layout, full-width buttons
- [ ] Location details: single column, key-value pairs
- [ ] Amenities grid: 1-2 columns max
- [ ] Fish species list: single column
- [ ] Nearby spots: single column, full-width cards
- [ ] All touch targets min 44px
- [ ] Adequate spacing for thumbs

**DESKTOP (1024px+):**
- [ ] Map 400px height
- [ ] GPS buttons side-by-side
- [ ] Amenities 2-3 columns
- [ ] Nearby spots 2-3 columns

**All Sections:**
- [ ] Use `.retro-section` class
- [ ] Terminal-style headers: `>> SECTION_NAME`
- [ ] VT323 font for headers
- [ ] Proper scanlines overlay
- [ ] Theme-appropriate shadows/glows

**Astro Optimization:**
- [ ] Pre-render all spot pages at build time (SSG)
- [ ] Generate static HTML with data baked in
- [ ] Only interactive components hydrate client-side
- [ ] Document which parts are static vs islands

**Testing:**
- [ ] Test on actual mobile devices
- [ ] Test dark and light modes
- [ ] Lighthouse score 95+

---

### TICKET-012: Add Spot Page Interactivity (Astro Islands) 🟡 PENDING REVIEW
**Estimate:** 4-5 hours
**Depends on:** TICKET-011, TICKET-031
**Status:** On feature branch, pending review

**Description:**  
Add JavaScript functionality using Astro's islands architecture to minimize bundle size.

**Acceptance Criteria:**

**Astro Islands Strategy:**
- [ ] GPS copy/directions: `client:load` (needed immediately)
- [ ] Map component: `client:idle` (load after page interactive)
- [ ] Species voting: `client:visible` (load when scrolled to)
- [ ] "I Fish Here" button: `client:load` or `client:visible` (decide)
- [ ] Measure JS bundle size (aim for <50kb initial)

**GPS Functionality:**
- [ ] Copy button works (navigator.clipboard.writeText)
- [ ] **MOBILE:** Copy success message large and visible
- [ ] **MOBILE:** Haptic feedback on copy (if available via Vibration API)
- [ ] Success message fades out after 2 seconds

**Directions:**
- [ ] Directions button extracts lat/lon from display
- [ ] Builds Google Maps URL
- [ ] **MOBILE:** Opens Google Maps app
- [ ] **DESKTOP:** Opens Google Maps in new tab

**Map:**
- [ ] Initializes with correct zoom (14.5)
- [ ] Theme matches current theme
- [ ] Updates on theme toggle
- [ ] **MOBILE:** Renders performantly on slower devices
- [ ] **MOBILE:** Touch gestures work (pinch zoom, pan)

**Error Handling:**
- [ ] Handle clipboard API failure gracefully
- [ ] Handle geolocation errors
- [ ] Handle map load failures

**Testing:**
- [ ] Test on actual devices
- [ ] Test all interactive elements
- [ ] Verify small JS bundle

---

### TICKET-013: Implement "I Fish Here" Check-In System (Mobile-First) 🔴 BLOCKER
**Estimate:** 6-8 hours
**Depends on:** TICKET-011

**Description:**
Add community engagement button for spot relevancy with time decay algorithm to prevent gaming. Anonymous check-ins with optional account upsell for favorites feature (post-launch).

**User Flow:**
1. User clicks "I Fish Here" button
2. Check-in recorded (anonymous, no signup required)
3. Optional follow-up: "What did you catch today?" → Species voting (TICKET-014)
4. Success toast: "Checked in! [Want to save favorites? Sign up]" (post-launch feature)

**Acceptance Criteria:**

**UI (Mobile-First):**
- [ ] **MOBILE:** Large, prominent button (min 44px height)
- [ ] **MOBILE:** Full-width on small screens
- [ ] **MOBILE:** Haptic feedback on tap (Vibration API)
- [ ] Button styled to match terminal theme
- [ ] Button text: "I Fish Here" (final copy)
- [ ] **DESKTOP:** Smaller button, inline placement
- [ ] After check-in, optionally show species voting interface

**Backend (Anonymous + Hybrid Ready):**
- [ ] Database schema: `check_ins` table (id, spot_id, user_id NULL, fingerprint_hash, created_at)
- [ ] API endpoint to record check-in
- [ ] Multi-layer rate limiting (anonymous users):
  - Cookie fingerprint (stops casual repeat votes)
  - IP address hash (stops same-session abuse)
  - 1 check-in per fingerprint per spot per week
- [ ] Schema ready for optional user_id (future accounts feature)

**Fingerprinting Strategy:**
- [ ] Generate fingerprint: hash(IP + User-Agent + Cookie ID)
- [ ] Store fingerprint cookie (30 day expiry)
- [ ] Query by fingerprint OR user_id (NULL for anonymous)

**Relevancy Algorithm:**
- [ ] Time decay formula: `score = sum(check-ins * 0.95^days_old)`
- [ ] Batch job runs daily to recalculate scores
- [ ] Store calculated score in `spots` table
- [ ] Use score to boost spots in search results

**Display (Anti-Gaming):**
- [ ] Show aggregated score, NOT raw count
- [ ] Phrasing: "Popular with anglers" or "12 anglers fish here recently"
- [ ] Visual indicator (subtle, not gamified)
- [ ] NEVER show exact numbers that can be gamed

**Testing:**
- [ ] Test on actual devices
- [ ] Verify rate limiting works (try same fingerprint twice)
- [ ] Test time decay calculation
- [ ] Verify search result boosting
- [ ] Test cookie persistence across sessions

---

### TICKET-014: Species Heat List System (Catch Reports) ✅ COMPLETE
**Estimate:** 8-10 hours
**Depends on:** TICKET-011
**Status:** COMPLETE - Implemented
**Completed:** November 2025

**Description:**
Community-driven species prevalence system ("Heat List") using time-decayed catch reports. Users log actual catches with dates, and the system automatically applies weekly decay to keep data fresh. Displays species in tiers (Common/Uncommon/Rare/Unreported) based on aggregated scores.

**🔥 REPLACES:** Old "Add Your Fishing Report" button and "What Fish Are Here?" voting section

**Implementation Summary:**

**Database Schema:** ✅ COMPLETE
- [x] `master_species` table - 29 Texas species with icons and priority order
- [x] `potential_species` junction table - Links spots to their geographically relevant species
- [x] `catch_reports` table - Stores catch data with time-decay scoring
  - Fields: `fishing_spot_id`, `master_species_id`, `user_ip_hash`, `catch_date`
  - Scoring: `base_score` (default 10.00), `current_score`, `last_decay_date`
- [x] Auto-trigger: New spots automatically populated with all potential species
- [x] Migration: `migrations/003_species_prevalence_system.sql`

**Backend APIs:** ✅ COMPLETE
- [x] `POST /api/log-catch.php` - Logs a catch report
  - Validates spot exists and species is valid for that spot
  - Rate limiting: 5 catches per hour per IP (hashed for privacy)
  - Validates catch date (within last 30 days, not future)
  - Returns success with report_id
- [x] `GET /api/get-heat-list.php?spot_id=X` - Returns heat list for a spot
  - Returns all potential species with scores and tiers
  - Calculates tier based on total_score (Common/Uncommon/Rare/Unreported)
  - Sorts: Reported species first (by score DESC), then unreported (by priority)

**Time-Decay System:** ✅ COMPLETE
- [x] Decay formula: `score * (0.95 ^ weeks_elapsed)` (5% decay per week)
- [x] Script: `backend/scripts/decay-scores.php`
- [x] Runs daily to update all catch report scores
- [x] Deletes reports when score drops below 0.01 (essentially expired)
- [x] Windows automation ready: `run-decay.bat` and `run-decay.ps1`
- [x] Documentation: `backend/scripts/WINDOWS_TASK_SCHEDULER_SETUP.md`

**Tier Thresholds (Configurable in API):**
- [x] **Common:** score >= 50 (5+ recent catches)
- [x] **Uncommon:** score >= 20 and < 50 (2-4 recent catches)
- [x] **Rare:** score > 0 and < 20 (1 recent catch)
- [x] **Unreported:** score = 0 (no catches)
- [x] Note: Thresholds set low for launch, can be increased as data accumulates

**Frontend UI:** ✅ COMPLETE
- [x] Heat List component: `frontend/public/js/heat-list.js`
- [x] Integrated into spot detail pages: `[slug].astro`
- [x] Displays top 3 species prominently, "Show more" for the rest
- [x] Tier indicators with color coding (red/orange/blue/gray)
- [x] Species icons (fish emoji or SVG fallback)
- [x] "Log a Catch" modal for each species
- [x] Responsive design (mobile-first)

**User Flow:**
1. User visits fishing spot detail page
2. Sees "Heat List" section with reported species (or "No catches reported yet")
3. Clicks any species (or "+" for unreported species)
4. Modal appears: "Log a catch" with date picker (last 30 days)
5. Submits catch
6. Heat list refreshes to show updated scores/tiers
7. Success message displayed

**Anti-Gaming Measures:**
- [x] Automatic time decay (5% per week) prevents old data from dominating
- [x] Display tiers (Common/Uncommon/Rare), NOT raw scores or counts
- [x] Rate limiting: 5 catches per hour prevents spam
- [x] IP hashing for privacy-preserving rate limits
- [x] Date validation: Must be within last 30 days
- [x] Species validation: Only species in `potential_species` can be logged

**Testing:** ✅ COMPLETE
- [x] Tested catch logging flow
- [x] Verified rate limiting works
- [x] Tested time decay script (manual execution)
- [x] Verified tier thresholds display correctly
- [x] Tested on spot detail pages
- [x] Verified potential_species auto-population for new spots

**Documentation:** ✅ COMPLETE
- [x] Setup guide: `SPECIES_PREVALENCE_SETUP.md`
- [x] Implementation status: `SPECIES_PREVALENCE_IMPLEMENTATION_STATUS.md`
- [x] Migration file: `migrations/003_species_prevalence_system.sql`
- [x] Windows Task Scheduler guide for automation

**Future Integration with TICKET-013:**
- [ ] When "I Fish Here" check-ins are implemented, optionally prompt: "What did you catch?"
- [ ] Both check-in score and species scores contribute to overall spot relevancy
- [ ] Unified spot activity score boosts spots in search results

---

## Sprint 4: Listing Pages & Cards (Mobile-First)

### TICKET-015: Make Spot Cards More Clickable (Mobile-First) ✅ COMPLETE
**Estimate:** 4-5 hours
**Depends on:** None
**Completed:** 2025-11-12

**Description:**  
Improve card hover states and clickability, optimized for mobile touch.

**Acceptance Criteria:**

**Mobile-First:**
- [ ] **MOBILE:** Full-width cards, adequate height
- [ ] **MOBILE:** Touch feedback (scale down slightly 0.98 on press)
- [ ] **MOBILE:** No hover-only interactions
- [ ] **MOBILE:** Large tap targets (entire card clickable)
- [ ] **MOBILE:** Arrow indicator (→) always visible

**Desktop Enhancement:**
- [ ] Enhanced hover effects (lift, glow/shadow increase)
- [ ] Arrow appears on hover
- [ ] Smooth transitions (200ms)

**Universal:**
- [ ] Active/pressed state feedback
- [ ] Ensure entire card is clickable (`<a>` tag, not `<div>`)
- [ ] Focus indicator visible for keyboard navigation
- [ ] Animation respects `prefers-reduced-motion`

**Apply To:**
- [ ] Home page county cards
- [ ] County page spot listings
- [ ] Search results
- [ ] "Nearby spots" on spot pages

**Testing:**
- [ ] Test on actual touch devices
- [ ] Test keyboard navigation
- [ ] Verify consistent across all contexts

---

### TICKET-016: Design Unified Listing Page Layout (Mobile-First) ✅ COMPLETE
**Estimate:** 8-10 hours
**Depends on:** TICKET-015
**Completed:** 2025-11-12

**Description:**
Create standard template for all spot listing pages, mobile-optimized.

**Acceptance Criteria:**

**MOBILE (320px-428px):**
- [ ] Single column card layout
- [ ] Collapsible filter panel (drawer or accordion)
- [ ] Sticky "Filter" button at top
- [ ] Sort dropdown full-width
- [ ] Result count prominent
- [ ] Infinite scroll (better than pagination on mobile)
- [ ] Cards stacked vertically, adequate spacing
- [ ] Touch-optimized controls

**DESKTOP (1024px+):**
- [ ] 2-3 column card grid
- [ ] Sidebar filters (always visible)
- [ ] Traditional pagination

**Components:**
- [ ] Terminal-style page header: `>> FISHING_SPOTS_IN_[LOCATION]`
- [ ] Result count display
- [ ] Filter/sort controls in `.retro-section`
- [ ] Results grid using `.retro-grid-spots`
- [ ] Cards use enhanced clickability from TICKET-015
- [ ] Empty state designed
- [ ] Loading skeleton cards

**Apply To:**
- [ ] `/spots` - main directory
- [ ] `/texas/[county]` - county pages
- [ ] Search results page

**Testing:**
- [ ] Test on actual devices
- [ ] Test dark and light modes
- [ ] Verify filters/sort work
- [ ] Test infinite scroll performance

---

### TICKET-035: State Park "No License Required" Feature ✅ COMPLETE
**Estimate:** 5-7 hours
**Depends on:** TICKET-015, TICKET-016
**Completed:** 2025-11-12

**Description:**
Highlight that fishing at Texas State Parks doesn't require a fishing license. Add visual indicators to spot cards and update search filter logic to make this benefit discoverable.

**Acceptance Criteria:**

**Data Model:**
- [ ] Add `is_state_park` boolean field to spots table/model
- [ ] Identify and flag all existing state park spots
- [ ] Data validation in spot submission form

**Spot Card Visual Indicator:**
- [ ] Design prominent badge/icon for "No License Required"
- [ ] Badge styles: terminal aesthetic for dark mode, vintage ad style for light mode
- [ ] Badge position: top-right corner or below spot name
- [ ] Badge text: "Fishing License Not Required" or "No License Needed"
- [ ] Apply to ALL spot card contexts:
  - Search results
  - County page listings
  - Home page featured spots (if applicable)
  - "Nearby spots" on spot detail pages

**Search Filter Update:**
- [ ] Relabel "State Park" filter to be more descriptive
- [ ] New label: "State Parks (No License Required)" or similar
- [ ] Filter correctly queries `is_state_park` field
- [ ] Filter works in combination with other filters
- [ ] Update filter UI to emphasize this benefit

**Spot Detail Page:**
- [ ] Display "No License Required" prominently on state park spot pages
- [ ] Add informational text explaining this benefit
- [ ] Consider adding state park badge/banner at top of page

**Mobile Optimization:**
- [ ] Badge readable on small screens
- [ ] Badge doesn't interfere with card clickability
- [ ] Filter label doesn't truncate on mobile

**SEO:**
- [ ] Add "no fishing license required" to state park spot meta descriptions
- [ ] Update schema markup to include this feature
- [ ] Consider adding structured data

**Testing:**
- [ ] Verify all state parks have badge
- [ ] Verify non-state parks don't have badge
- [ ] Test filter returns only state parks
- [ ] Test on actual devices
- [ ] Test dark and light modes

---

### TICKET-017: Implement Search-to-Results Animations (Astro View Transitions) 🟡 HIGH
**Estimate:** 4-6 hours  
**Depends on:** TICKET-016, TICKET-031

**Description:**  
Use Astro's View Transitions API for smooth page navigation between search and results.

**Acceptance Criteria:**

**Astro Implementation:**
- [ ] Use Astro View Transitions API (preferred approach)
- [ ] Add `<ViewTransitions />` to Layout.astro
- [ ] Define transition names:
  - `transition:name="search-container"` on search widget
  - `transition:name="search-container"` on results header (morph)
  - `transition:name="background"` for continuous gradient
- [ ] Fallback: Simple cross-fade for unsupported browsers

**Animation Sequence:**
1. **Search Submission (0-200ms):**
   - [ ] Form disables, loading state
   - [ ] Button text: "SEARCH" → "SEARCHING..."
   - [ ] Spinner animation

2. **Page Transition (200-400ms):**
   - [ ] Search widget fade out (200ms)
   - [ ] Loading messages: "SEARCHING...", "LOADING_RESULTS..."
   - [ ] Background dims

3. **Results Appearance (400-700ms):**
   - [ ] Results header fade in (200ms)
   - [ ] Result count animates up
   - [ ] **MOBILE:** First 6 cards cascade in (50ms stagger)
   - [ ] **DESKTOP:** First 9 cards cascade in (50ms stagger)

4. **Interactive (700ms+):**
   - [ ] Fully interactive
   - [ ] Total perceived time: ~1 second

**Performance:**
- [ ] **MOBILE:** Lighter animations (performance consideration)
- [ ] **MOBILE:** Respect device performance (throttle on low-end devices)
- [ ] Skeleton cards show if data loading >500ms
- [ ] Respect `prefers-reduced-motion`

**Testing:**
- [ ] Test on actual mobile devices (iOS Safari support?)
- [ ] Test back/forward navigation
- [ ] Test rapid navigation
- [ ] Measure performance impact

---

## Sprint 5: User Spot Submissions (Mobile-First)

### TICKET-018: Build Spot Submission Form (Mobile-First) 🔴 BLOCKER
**Estimate:** 8-10 hours  
**Depends on:** None

**Description:**  
Create user spot submission interface, optimized for mobile where most users will submit.

**Acceptance Criteria:**

**Route & Access:**
- [ ] Route: `/submit-spot`
- [ ] Add link in main navigation
- [ ] Add CTA on home page
- [ ] Add "Know a spot?" button on county pages

**MOBILE (320px-428px):**
- [ ] Full-width form
- [ ] Large input fields (easy to tap, min 44px)
- [ ] Stacked layout (one column)
- [ ] Map picker optimized for touch
- [ ] Address autocomplete works with mobile keyboards
- [ ] Camera integration ready (future photos)
- [ ] Bottom sticky "Submit" button
- [ ] Form validates on blur (don't wait for submit)

**DESKTOP:**
- [ ] Two-column layout possible
- [ ] Side-by-side map and form

**Form Fields (Required):**
- [ ] Spot name (text input, 3-100 chars)
- [ ] Location (three methods):
  - Address search (Google Places Autocomplete)
  - Manual lat/lon input (decimal degrees)
  - **MOBILE:** Tap map to set location
- [ ] Public access confirmation checkbox (required)

**Form Fields (Optional):**
- [ ] Water body name
- [ ] Amenities checkboxes (boat ramp, parking, pier, etc.)
- [ ] Access notes (textarea, 500 char limit)

**Validation:**
- [ ] All required fields filled
- [ ] Coordinates valid (reasonable bounds for Texas)
- [ ] Duplicate check: search for spots within 100m
- [ ] "A spot already exists nearby" warning with option to continue
- [ ] Public access checkbox must be checked

**Submission Flow:**
- [ ] Preview screen: "Does this look correct?"
- [ ] Show spot on map
- [ ] Show all entered details
- [ ] Edit or Confirm buttons
- [ ] Submit to database
- [ ] "Thank you" message: "Your submission is under review"

**Styling:**
- [ ] Terminal aesthetic matching site
- [ ] Header: `>> SUBMIT_FISHING_SPOT`
- [ ] All fields styled with `.retro-input`
- [ ] Buttons styled with `.retro-btn-search`

**Testing:**
- [ ] Test on actual mobile devices
- [ ] Test all input types work correctly
- [ ] Test address autocomplete
- [ ] Test map tap location
- [ ] Test validation rules

---

### TICKET-019: Build Submission Review Pipeline 🔴 BLOCKER
**Estimate:** 6-8 hours  
**Depends on:** None

**Description:**  
Admin interface for reviewing and approving user-submitted spots.

**Acceptance Criteria:**

**Admin Queue:**
- [ ] Queue of pending submissions
- [ ] Show: spot name, location, submitter, date
- [ ] Map view of submitted location
- [ ] Full details of submission

**Duplicate Detection:**
- [ ] Check for existing spots within 100m
- [ ] Show existing nearby spots
- [ ] Highlight if very close (potential duplicate)

**Review Actions:**
- [ ] Approve button
- [ ] Reject button (with reason dropdown)
- [ ] Edit before approval (fix typos, add data)
- [ ] Add moderation notes

**Approval Flow:**
- [ ] Approved spots added to main database
- [ ] Flag as "user-submitted" in database
- [ ] Show "Community Spot" badge on spot page
- [ ] Optional: Credit submitter (if they want)
- [ ] Email notification to submitter (approved)

**Rejection Flow:**
- [ ] Rejection reasons:
  - Not publicly accessible
  - Duplicate of existing spot
  - Invalid location
  - Spam/inappropriate
- [ ] Email notification to submitter (rejected with reason)
- [ ] Keep record for analytics

**Admin Panel:**
- [ ] Desktop-first (admin typically on desktop)
- [ ] Mobile usable but not primary
- [ ] Simple, functional interface

**Testing:**
- [ ] Test approval flow
- [ ] Test rejection flow
- [ ] Test edit before approval
- [ ] Verify emails sent

---

### TICKET-020: Duplicate Detection System 🟡 HIGH
**Estimate:** 4-5 hours  
**Depends on:** TICKET-018

**Description:**  
Prevent duplicate spot submissions with intelligent proximity detection.

**Acceptance Criteria:**

**During Submission:**
- [ ] Check submissions against existing spots
- [ ] Distance threshold: 100m radius
- [ ] Show nearby spots to submitter
- [ ] Ask: "Is this the same spot?"
- [ ] Allow override if user confirms it's different

**In Admin Review:**
- [ ] Flag submissions near existing spots
- [ ] Show distance to nearest spots
- [ ] Admin can merge duplicates
- [ ] Merge preserves all data (combine amenities, etc.)

**Logging:**
- [ ] Log all duplicate detection attempts
- [ ] Track how many are true duplicates vs false positives
- [ ] Use data to tune 100m threshold if needed

**Testing:**
- [ ] Test with spots very close together (10m apart)
- [ ] Test with spots just under threshold (95m apart)
- [ ] Test with spots clearly different (200m apart)

---

## Sprint 6: SEO & Polish

### TICKET-021: Implement SEO Basics 🟡 HIGH
**Estimate:** 4-5 hours
**Depends on:** None

**Description:**
Set up essential SEO infrastructure for "fishing spots near me" queries.

**Acceptance Criteria:**

**Meta Tags:**
- [ ] All pages have proper meta titles
- [ ] County pages: "[X] Fishing Spots in [County], TX | GPS Coordinates"
- [ ] Spot pages: "[Spot Name] | [County] TX Fishing Location"
- [ ] Meta descriptions include "near me" language naturally
- [ ] Descriptions under 160 characters

**Schema Markup:**
- [ ] Add TouristAttraction schema to spot pages
- [ ] Include GPS coordinates in schema
- [ ] Include amenities as features
- [ ] Include address information
- [ ] Test with Google's Rich Results Tool

**Technical SEO:**
- [ ] XML sitemap generated with all pages
- [ ] Submit sitemap to Google Search Console
- [ ] robots.txt properly configured
- [ ] Canonical tags on all pages
- [ ] Open Graph tags for social sharing
- [ ] Twitter card tags
- [ ] Mobile-specific meta tags (viewport, etc.)

**Google Search Console:**
- [ ] Create account/project
- [ ] Verify domain ownership
- [ ] Submit sitemap
- [ ] Set up email alerts for errors

**Testing:**
- [ ] Validate all meta tags
- [ ] Test schema markup
- [ ] Verify sitemap accessible

---

### TICKET-036: Geotargeted "Near Me" Landing Page 🟡 HIGH
**Estimate:** 6-8 hours
**Depends on:** TICKET-021, TICKET-031

**Description:**
Create a dynamic landing page targeting "fishing spots near me" and similar local-intent search queries. Uses browser geolocation to show personalized results.

**Acceptance Criteria:**

**Route & Setup:**
- [ ] Create route: `/near-me` or `/fishing-spots-near-me`
- [ ] Use Astro SSG for page shell
- [ ] Client-side geolocation hydration with `client:load`

**Geolocation Functionality:**
- [ ] Request browser geolocation permission on page load
- [ ] Clear permission prompt with explanation of benefit
- [ ] Loading state while waiting for permission/location

**Success State (Permission Granted):**
- [ ] Display user's approximate location (city/region, not exact coords)
- [ ] Show list of fishing spots sorted by distance
- [ ] Display distance from user to each spot (e.g., "2.3 miles away")
- [ ] Use spot cards from TICKET-015 (enhanced clickability)
- [ ] Show 20-30 spots initially with "Load more" button
- [ ] Map view showing user location and nearby spots

**Fallback State (Permission Denied):**
- [ ] Clear, friendly message explaining fallback
- [ ] Prominent search bar: "Enter your city or zip code"
- [ ] Autocomplete for Texas cities and zip codes
- [ ] Submit redirects to search results with location filter

**Mobile Optimization:**
- [ ] Geolocation more reliable on mobile (GPS available)
- [ ] Large, clear permission prompt message
- [ ] Distance displayed prominently on cards
- [ ] Touch-friendly search bar in fallback
- [ ] Map optimized for mobile viewing

**SEO Optimization:**
- [ ] Meta title: "Fishing Spots Near Me | Find Local Texas Fishing Locations"
- [ ] Meta description: "Discover fishing spots near your location..."
- [ ] Schema markup for local search
- [ ] Include "near me" keyword naturally in content
- [ ] Link to popular city/county pages

**Content:**
- [ ] Hero section: "Find Fishing Spots Near You"
- [ ] Brief explanation of how it works
- [ ] Privacy note: "We don't store your location"
- [ ] Link to privacy policy

**Testing:**
- [ ] Test geolocation on actual mobile devices (iOS/Android)
- [ ] Test permission denial flow
- [ ] Test in private/incognito mode
- [ ] Verify distance calculations accurate
- [ ] Test on actual devices in different locations

---

### TICKET-037: "No License" Thematic Landing Page 🟡 HIGH
**Estimate:** 4-6 hours
**Depends on:** TICKET-021, TICKET-035

**Description:**
Create a content-driven static landing page targeting users searching for fishing locations that don't require a license. This page serves as a comprehensive guide and SEO magnet for this high-value query.

**Acceptance Criteria:**

**Route & Setup:**
- [ ] Create route: `/fishing-without-a-license` or `/no-license-fishing`
- [ ] Fully static page (Astro SSG)
- [ ] Pre-rendered at build time with all state park data

**SEO Optimization:**
- [ ] Meta title: "Where Can I Fish Without a License in Texas? | State Parks Guide"
- [ ] Meta description: "Complete list of Texas fishing locations where no license is required..."
- [ ] Target keywords:
  - "where can I fish without a license"
  - "no license fishing spots"
  - "free fishing locations texas"
  - "fishing without license texas"
- [ ] Schema markup: Article or Guide
- [ ] Optimized URL structure
- [ ] Internal links to all state park spot pages

**Page Content:**
- [ ] **Hero Section:**
  - Headline: "Fish Texas State Parks - No License Required"
  - Subheading explaining the benefit
  - Call-to-action: Browse all state park spots
- [ ] **Informational Section:**
  - Explain Texas law: State parks exempt from fishing license requirement
  - Clarify any conditions or restrictions
  - Link to official TPWD source
- [ ] **Complete List of State Parks:**
  - All state park fishing spots listed
  - Organized by region or alphabetically
  - Each entry links to full spot page
  - Include county for each spot
  - Brief description of what makes each spot unique
- [ ] **FAQ Section:**
  - "Do I need a license to fish at state parks?"
  - "Are there any restrictions?"
  - "What other locations don't require a license?"
  - "Do I need a state park entrance pass?"

**Visual Design:**
- [ ] Terminal aesthetic (dark mode)
- [ ] Vintage ad aesthetic (light mode)
- [ ] Prominent badges: "NO LICENSE REQUIRED"
- [ ] Use state park imagery
- [ ] Map showing all state park locations

**Spot Card Display:**
- [ ] Use enhanced spot cards from TICKET-015
- [ ] Display "No License Required" badge from TICKET-035
- [ ] Grid layout: responsive columns
- [ ] Filter/sort options: by region, by county, by popularity

**Internal Linking:**
- [ ] Link from home page (prominent placement)
- [ ] Link from navigation menu
- [ ] Link from search widget (e.g., "Looking for no-license fishing?")
- [ ] Link from state park spot pages (cross-promotion)
- [ ] Add to footer

**Testing:**
- [ ] Verify all state parks listed
- [ ] Verify all links work
- [ ] Test on actual devices
- [ ] Validate SEO with tools
- [ ] Check page load performance

---

### TICKET-022: Performance Optimization (Mobile-First) 🟡 HIGH
**Estimate:** 6-8 hours  
**Depends on:** None

**Description:**  
Ensure fast load times on mobile networks (3G, 4G).

**Acceptance Criteria:**

**Performance Targets:**
- [ ] **MOBILE:** Page loads <3s on 3G
- [ ] Lighthouse mobile score 90+
- [ ] Core Web Vitals pass:
  - LCP (Largest Contentful Paint) < 2.5s
  - FID (First Input Delay) < 100ms
  - CLS (Cumulative Layout Shift) < 0.1

**Optimizations:**
- [ ] Images optimized (WebP format, responsive sizes)
- [ ] Lazy load images below fold
- [ ] CSS minified and inlined for critical path
- [ ] JavaScript code-split by route
- [ ] Fonts optimized (preload VT323)
- [ ] Reduce initial bundle size
- [ ] Use Astro's built-in optimizations

**Testing:**
- [ ] Test on actual 3G connection
- [ ] Test on slow 4G
- [ ] Use Chrome DevTools throttling
- [ ] Monitor real user metrics (after launch)

---

### TICKET-023: Accessibility Audit (Mobile-First) 🟡 HIGH
**Estimate:** 4-5 hours  
**Depends on:** None

**Description:**  
Ensure site is accessible on all devices and for users with disabilities.

**Acceptance Criteria:**

**Mobile Accessibility:**
- [ ] Touch targets minimum 44px x 44px
- [ ] Pinch zoom not disabled (allow users to zoom)
- [ ] Adequate spacing between interactive elements
- [ ] Text readable without zoom (16px minimum)

**Visual Accessibility:**
- [ ] Color contrast passes WCAG AA standard
- [ ] Text readable in both dark and light modes
- [ ] Focus indicators clearly visible
- [ ] No color-only information (use icons + color)

**Keyboard Navigation:**
- [ ] All interactive elements keyboard accessible
- [ ] Logical tab order
- [ ] Skip links present for screen readers
- [ ] No keyboard traps

**Screen Readers:**
- [ ] Test with VoiceOver (iOS)
- [ ] Test with TalkBack (Android)
- [ ] Alt text on all images
- [ ] Form labels properly associated
- [ ] ARIA labels where needed
- [ ] Semantic HTML structure

**Forms:**
- [ ] Labels associated with inputs
- [ ] Error messages announced
- [ ] Required fields marked
- [ ] Validation clear and helpful

**Testing:**
- [ ] Test with actual assistive technologies
- [ ] Lighthouse accessibility score 95+
- [ ] Manual keyboard navigation test
- [ ] Screen reader walkthrough

---

## Sprint 7: Marketing & Launch Prep

### TICKET-024: Branding & Marketing Strategy 🟡 HIGH
**Estimate:** 4-6 hours  
**Depends on:** None

**Description:**  
Plan and execute launch marketing to fishing community.

**Acceptance Criteria:**

**Brand Definition:**
- [ ] Define brand voice and messaging
- [ ] Value proposition: Free GPS coords, community data, public access
- [ ] Target audience: Casual to serious anglers, Texas focus initially

**Fishing YouTuber Outreach:**
- [ ] Research relevant channels:
  - Bass fishing channels
  - Saltwater fishing
  - Texas-specific fishing channels
  - Fishing tips/education channels
- [ ] Create list of 20-30 YouTubers to contact
- [ ] Prepare pitch email template:
  - Introduce site
  - Highlight value proposition
  - Offer early access or featured spot
  - Ask for mention/review/link
- [ ] Send personalized emails
- [ ] Track responses and follow-ups

**Reddit Strategy:**
- [ ] r/fishing - general fishing community
- [ ] r/bassfishing - bass anglers
- [ ] r/texas - Texas-specific
- [ ] r/houston, r/austin, etc. - city subreddits
- [ ] Create post announcing launch
- [ ] Engage with comments authentically
- [ ] Don't spam - provide value

**Facebook Groups:**
- [ ] Research local fishing groups (Texas)
- [ ] Join groups (follow rules)
- [ ] Introduce site to admins first
- [ ] Post announcement (if allowed)
- [ ] Engage with members' questions

**Other Channels:**
- [ ] Press release draft (local fishing publications)
- [ ] Launch announcement copy (social media)
- [ ] Email to early testers/beta users
- [ ] Consider: Instagram fishing community
- [ ] Consider: TikTok fishing creators

**Social Media Accounts:**
- [ ] Decide if creating accounts (optional for MVP)
- [ ] If yes: Instagram, Facebook, Twitter/X
- [ ] If no: Focus on organic/community marketing

---

### TICKET-025: Analytics & Tracking Setup 🟡 HIGH
**Estimate:** 3-4 hours  
**Depends on:** None

**Description:**  
Set up analytics to measure success and understand user behavior.

**Acceptance Criteria:**

**Google Analytics 4:**
- [ ] GA4 property created
- [ ] Tracking code installed on all pages
- [ ] Test tracking works in development

**Event Tracking:**
- [ ] Spot searches (search term, location)
- [ ] Spot views (which spots popular)
- [ ] "I Fish Here" button clicks
- [ ] Species report submissions
- [ ] User spot submissions
- [ ] Directions button clicks
- [ ] GPS coordinates copy

**Mobile-Specific:**
- [ ] Track mobile vs desktop usage
- [ ] Track screen sizes
- [ ] Track mobile browsers (iOS Safari vs Chrome Android)
- [ ] Track touch vs mouse interactions

**Conversion Funnels:**
- [ ] Define key funnels:
  - Home → Search → Results → Spot View
  - Spot View → "I Fish Here" conversion
  - Spot View → Species Report
  - Home → Submit Spot → Complete Submission
- [ ] Set up funnel tracking in GA4

**Dashboard:**
- [ ] Create custom dashboard with key metrics
- [ ] Share access with team

**Privacy:**
- [ ] Privacy policy updated (mention analytics)
- [ ] Cookie consent banner (if needed, check regulations)
- [ ] Anonymize IP addresses (privacy best practice)

**Testing:**
- [ ] Test all events fire correctly
- [ ] Verify funnel tracking
- [ ] Check real-time reports

---

### TICKET-026: Pre-Launch Testing Checklist 🔴 BLOCKER
**Estimate:** 4-6 hours  
**Depends on:** ALL PREVIOUS TICKETS

**Description:**  
Comprehensive testing before launch to ensure everything works.

**Pre-Requisite:**
- [ ] **ALL previous tickets completed and verified**

**Mobile Testing (Actual Devices):**
- [ ] iPhone (iOS Safari) - multiple screen sizes if possible
- [ ] Android (Chrome) - multiple manufacturers
- [ ] Android (Samsung Internet) - if common in Texas
- [ ] Test screen sizes: 320px, 375px, 390px, 428px

**Desktop Testing:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest, if Mac available)
- [ ] Edge (latest)
- [ ] Test resolutions: 1024px, 1280px, 1920px, 2560px

**Critical User Flows:**
- [ ] Search for spots (location and manual)
- [ ] View spot details (all sections render)
- [ ] Submit a spot (complete full flow)
- [ ] Report species on spot (vote works)
- [ ] Click "I Fish Here" (works and rate-limited)
- [ ] Copy GPS coordinates (copies to clipboard)
- [ ] Get directions (opens Maps app/website)
- [ ] Theme toggle (dark/light switch smoothly)

**Technical Checks:**
- [ ] No console errors on any page
- [ ] No broken images or 404s
- [ ] Forms validate correctly
- [ ] Maps load and display correctly
- [ ] Theme switching works smoothly
- [ ] Animations respect `prefers-reduced-motion`

**Performance:**
- [ ] Lighthouse mobile score 90+ on key pages
- [ ] Core Web Vitals pass (LCP, FID, CLS)
- [ ] Test on actual 3G connection
- [ ] No layout shift during page load

**SEO:**
- [ ] All meta tags present and correct
- [ ] Schema markup valid
- [ ] Sitemap accessible
- [ ] Google Search Console configured

**Analytics:**
- [ ] All events fire correctly
- [ ] Funnels track properly
- [ ] Real-time reports working

**Content:**
- [ ] All pages have correct content
- [ ] No placeholder text (lorem ipsum)
- [ ] All links work
- [ ] Footer links work (privacy policy, etc.)

**Staging Test:**
- [ ] Full test on staging.wherecanifish.com
- [ ] Everything works exactly as local
- [ ] Fish species API works on staging (TICKET-009)
- [ ] Maps work on staging
- [ ] Forms submit correctly

**Final Checks:**
- [ ] Legal: Privacy policy, terms of service (if needed)
- [ ] Contact: Support email/form working
- [ ] Backup: Database backup process in place
- [ ] Monitoring: Error tracking set up (Sentry, etc.)

**Sign-Off:**
- [ ] You personally tested everything
- [ ] Wife tested and approved
- [ ] No critical bugs remaining
- [ ] Ready for real users

**🚀 LAUNCH READY**

---

## Post-Launch (Deferred)

### TICKET-030: Optional User Accounts & Favorites
**Timeline:** Post-launch (when users request it)
**Estimate:** 15-25 hours
**Depends on:** TICKET-013, TICKET-014 (must be working anonymously first)

**Description:**
Add optional user accounts to enable favorite spots, contribution tracking, and notifications. Anonymous check-ins and species voting continue to work without accounts.

**Why Post-Launch:**
- Don't block MVP on auth complexity
- Validate that users actually want this feature first
- Users asking "Can I save my favorites?" = perfect timing signal

**Acceptance Criteria:**

**Authentication System:**
- [ ] Email + password signup
- [ ] Email verification (prevent spam accounts)
- [ ] Login/logout flow
- [ ] Password reset via email
- [ ] Session management (JWT or server-side sessions)
- [ ] "Remember me" option

**Account Features:**
- [ ] **Favorite Spots:**
  - Heart icon on spot pages to save favorites
  - "My Favorites" page showing saved spots
  - Quick access from navigation
- [ ] **Contribution History:**
  - "My Check-Ins" - spots you've visited
  - "My Species Reports" - species you've reported
  - Stats: "You've checked in to 12 spots"
- [ ] **Personal Map:**
  - Map showing all spots you've checked into
  - Visual heatmap of your fishing activity
- [ ] **Notifications (optional):**
  - Email when someone reports new species at your favorite spot
  - Weekly digest of activity at favorites
  - Opt-in only, not default

**Migration from Anonymous:**
- [ ] When user signs up, prompt: "Claim your previous check-ins?"
- [ ] Match by fingerprint hash from last 30 days
- [ ] Migrate anonymous check-ins to user account
- [ ] Update `user_id` field in `check_ins` and `species_votes` tables

**Hybrid Mode (Anonymous + Logged In):**
- [ ] Anonymous users: Rate limit by fingerprint (existing behavior)
- [ ] Logged in users: Rate limit by user_id + show favorites/history
- [ ] Both modes contribute equally to spot relevancy scores
- [ ] No special weight for logged-in votes (prevent gaming)

**UI Changes:**
- [ ] "Sign Up" and "Log In" buttons in navigation
- [ ] After anonymous check-in, show: "Checked in! [Save this spot?]" → signup prompt
- [ ] Account dropdown menu (desktop) or account page (mobile)
- [ ] Profile page with stats and favorites

**Privacy & Security:**
- [ ] Privacy policy updated
- [ ] Secure password hashing (bcrypt)
- [ ] HTTPS required for login
- [ ] Rate limit login attempts (prevent brute force)
- [ ] Email unsubscribe for notifications

**Testing:**
- [ ] Test signup, login, logout flows
- [ ] Test password reset
- [ ] Test favorite spots (add/remove)
- [ ] Test migration from anonymous to account
- [ ] Test that anonymous mode still works
- [ ] Security audit (SQL injection, XSS, CSRF)

---

### TICKET-027: Data Pipeline Abstraction
**Timeline:** When adding second state (Florida, Louisiana, etc.)
**Estimate:** 20-30 hours

Extract data pipeline into standalone tool, separate from website codebase.

---

### TICKET-028: Airtable Integration
**Timeline:** When scaling data operations
**Estimate:** 15-20 hours

Use Airtable as source of truth for raw fishing data, run validation/deduplication scripts.

---

### TICKET-029: Advanced Animations & Polish
**Timeline:** Post-launch enhancement
**Estimate:** 10-15 hours

Page transitions, scroll animations, micro-interactions (Phase 2 & 3 from animation plan).

---

## Critical Path to Launch

**Must complete in this order:**

1. **Sprint 0:** TICKET-001, TICKET-031 (Foundation)
2. **Sprint 1:** TICKET-003, 004, 005, 006, 032, 033 (CSS & Colors)
3. **Sprint 2:** TICKET-008, 009, 010 (Bug Fixes)
4. **Sprint 3:** TICKET-011, 012, ~~TICKET-014~~ ✅, TICKET-013 (Spot Pages)
5. **Sprint 4:** TICKET-015, 016, 017 (Listings)
6. **Sprint 5:** TICKET-018, 019, 020 (User Submissions)
7. **Sprint 6:** TICKET-021, 022, 023 (SEO & Polish)
8. **Sprint 7:** TICKET-024, 025, 026 (Marketing & Testing)
9. **🚀 LAUNCH**

**Note:** TICKET-014 (Species Heat List) is complete. TICKET-013 (I Fish Here check-ins) will integrate with it to create unified spot relevancy system.

---

## Total Effort Estimate

**Total:** 129-167 hours

**New Scope Items Added (19-27 hours):**
- TICKET-034: County Many-to-Many Relationship Schema (4-6 hours)
- TICKET-035: State Park "No License Required" Feature (5-7 hours)
- TICKET-036: Geotargeted "Near Me" Landing Page (6-8 hours)
- TICKET-037: "No License" Thematic Landing Page (4-6 hours)

**Timeline Estimates:**
- Full-time (40 hrs/week): 3.5-4.5 weeks
- Part-time (20 hrs/week): 7-9 weeks
- Side project (10 hrs/week): 13-17 weeks

---

## Design Reference Images

Store in `/docs/design-references/`:
- `tournament-v17-ad.jpg` - Magazine ad for typography/layout inspiration
- `boat-side-stripes.jpg` - Racing stripes for color palette
- `boat-motor.jpg` - Mariner motor for color palette

---

## Scope Clarifications & Open Questions

### Page Definition: /spots vs. /search
**Status:** Needs design team clarification
**Impact:** TICKET-016

The current ambiguity between the `/spots` page and the search results page needs to be resolved during the layout redesign. The design and product team should provide a clear definition and user flow for these pages to clarify their distinct purposes.

**Possible Approaches:**
- `/spots` → Browsable directory of all spots (full catalog)
- `/search` → Explicit search results page with filters applied
- Alternative: Combine into single page with different states

**Action:** Clarify with design/product team before implementing TICKET-016

---

## Questions to Resolve

1. ~~**"I Fish Here":** Anonymous or require account?~~ ✅ **RESOLVED:** Anonymous (MVP), optional accounts post-launch (TICKET-030)
2. ~~**Species voting:** Anonymous or require account?~~ ✅ **RESOLVED:** Anonymous (MVP), optional accounts post-launch (TICKET-030)
3. **User submissions:** Email verification required? *(Recommend: No for MVP, yes if spam becomes issue)*
4. **Analytics:** Cookie consent banner needed? (Check Texas/US regulations)
5. **Landing page routes:** Finalize exact URLs for new landing pages (TICKET-036, TICKET-037)

---

**Document Version:** 3.3
**Last Updated:** November 13, 2025
**Status:** Ready for implementation

**Changelog v3.3:**
- **MAJOR:** Updated TICKET-014 to reflect actual implementation (Species Heat List System)
- TICKET-014 marked COMPLETE - Heat List with catch reports fully implemented
- Heat List uses time-decay scoring (5% per week), tier-based display (Common/Uncommon/Rare/Unreported)
- Backend: `catch_reports` table, `log-catch.php` & `get-heat-list.php` APIs
- Frontend: `heat-list.js` component integrated into spot pages
- Time-decay script: `backend/scripts/decay-scores.php` with Windows Task Scheduler automation
- Future integration: Will connect with TICKET-013 check-ins for unified spot relevancy

**Changelog v3.2:**
- Reopened TICKET-033 & TICKET-034 for additional review
- Updated Sprint 3 tickets (TICKET-011, 012) to "Pending Review" status - on feature branch
- Marked Sprint 4 complete: TICKET-015, 016, 035
- TICKET-013 ("I Fish Here" check-ins) still in active development

**Changelog v3.1:**
- **MAJOR:** Updated TICKET-013 & TICKET-014 to use anonymous check-ins/voting (no accounts required for MVP)
- **MAJOR:** Merged fishing reports into unified check-in + species voting system
- **MAJOR:** Added anti-gaming display requirements (show confidence levels, NOT raw counts)
- Added TICKET-030: Optional User Accounts & Favorites (post-launch)
- Specified fingerprinting strategy for anonymous rate limiting
- Added migration path from anonymous to logged-in users
- Removed separate "Add Your Fishing Report" feature (replaced by integrated system)
- Resolved Questions #1 and #2 (anonymous for MVP)
- Updated database schemas to support hybrid anonymous/logged-in mode

**Changelog v3.0:**
- Added TICKET-034: County Many-to-Many Relationship Schema (data integrity)
- Added TICKET-035: State Park "No License Required" Feature (UI/UX enhancement)
- Added TICKET-036: Geotargeted "Near Me" Landing Page (SEO strategy)
- Added TICKET-037: "No License" Thematic Landing Page (SEO strategy)
- Updated TICKET-031: Explicitly defined Hybrid Rendering Model (SSG + ISR)
- Added Scope Clarifications section for /spots vs /search
- Updated total estimate: 129-167 hours (was 110-140 hours)
