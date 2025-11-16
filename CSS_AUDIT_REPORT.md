# Comprehensive CSS Audit Report

**Generated:** $(date)  
**Scope:** All CSS files, layout files, page files, and component files in the frontend codebase

---

## Executive Summary

This audit analyzed:
- **3 CSS files** (retro-colors.css, retro-common.css, search-widget.css)
- **8 Astro page/layout files**
- **6 TSX component files**
- **1 HTML file** (maintenance.html)

### Key Findings

| Metric | Count |
|--------|-------|
| Total CSS Classes Defined | 193 |
| Total CSS IDs Defined | 3 |
| Total CSS Variables Defined | 198 |
| Total Variable Usages | 970 |
| Total Selectors | 488 |
| Class Usages in HTML/Astro Files | 164 |
| **Unused Classes** | **66** |
| **Unused Variables** | **40** |
| **Undefined Variables** | **2** |
| **Hardcoded Styles** | **2** |
| **Style Conflicts** | **83** |
| **Embedded Style Blocks** | **8** |

---

## 1. Hardcoded Styles Found

All CSS styling should come from CSS files. The following hardcoded inline styles were found:

### Issue #1: ResultsWidget.astro
- **File:** `frontend/src/components/ResultsWidget.astro`
- **Line:** 69
- **Style:** `display: none;`
- **Context:** `<div id="filter-panel" class="filter-panel" style="display: none;">`
- **Recommendation:** Move to CSS file using `.filter-panel[hidden]` or add a `.filter-panel-hidden` class

### Issue #2: SearchWidget.tsx
- **File:** `frontend/src/components/SearchWidget.tsx`
- **Line:** 809
- **Style:** Dynamic `animation-delay` based on index
- **Context:** `style={`animation-delay: ${Math.min(index * 0.05, 0.5)}s`}`
- **Recommendation:** This is **ACCEPTABLE** as it's a dynamic value calculated at runtime. Consider using CSS custom properties set via JavaScript if refactoring.

---

## 2. Embedded Style Blocks

The following files contain embedded `<style>` blocks that should ideally be moved to CSS files:

1. **Layout.astro** - Large embedded style block (lines 169-950)
   - Contains header, footer, navigation, theme toggle styles
   - **Size:** ~780 lines
   - **Recommendation:** Extract to `layout.css` or appropriate CSS file

2. **index.astro** - Homepage-specific styles (lines 55-102)
   - Contains search section and homepage content styles
   - **Recommendation:** Move to `retro-common.css` or create `homepage.css`

3. **texas.astro** - Texas page styles (lines 99-134)
   - Contains county card overrides
   - **Recommendation:** Move to `retro-common.css`

4. **states.astro** - States page styles (lines 133-150)
   - Contains state card overrides
   - **Recommendation:** Move to `retro-common.css`

5. **ResultsWidget.astro** - Component styles (lines 101-339)
   - Contains widget-specific styles
   - **Recommendation:** Move to `search-widget.css` or create `results-widget.css`

6. **maintenance.html** - Standalone maintenance page styles (lines 13-139)
   - **Note:** This is acceptable as it's a standalone file

---

## 3. Unused CSS Classes (66 total)

The following CSS classes are defined but never used in any HTML/Astro/TSX files:

### Component Classes
- `amenities-empty-message` - Used in spot detail pages
- `btn-cancel`, `btn-submit` - Form buttons (may be used in modals)
- `btn-filter-toggle` - Filter toggle button
- `checkbox-label` - Checkbox styling
- `common`, `rare`, `uncommon`, `unreported` - Species list classes
- `controls-row` - Layout class
- `display-none` - Utility class
- `filter-section-title` - Filter section heading
- `flex-wrap` - Utility class
- `font-heading` - Utility class
- `font-size-sm` - Utility class
- `form-actions`, `form-group` - Form layout classes
- `gap-sm` - Utility class
- `heat-list` - Species heat list container
- `location-icon`, `location-prompt`, `location-title` - Search widget location section
- `mb-sm`, `mt-md`, `mt-xl` - Margin utility classes
- `modal-close`, `modal-content`, `modal-header`, `modal-overlay` - Modal component classes
- `no-reports-message` - Empty state message
- `result-count` - Results count display
- `results-controls` - Results controls container
- `retro-breadcrumb` - Breadcrumb navigation (commented out in CSS)
- `retro-btn-secondary` - Secondary button variant
- `retro-card`, `retro-card-moss`, `retro-card-rust`, `retro-card-sage`, `retro-card-tan` - Card variants
- `retro-grid-auto`, `retro-grid-spots` - Grid layout classes
- `retro-heading`, `retro-heading-lg`, `retro-heading-md`, `retro-heading-sm` - Heading utility classes
- `retro-input`, `retro-select` - Form input classes
- `retro-notice`, `retro-notice-error`, `retro-notice-info`, `retro-notice-success` - Notice component classes
- `scrolled-from-bottom`, `scrolled-from-top` - Scroll state classes (added dynamically)
- `search-form-header`, `search-label` - Search form elements
- `show-more-btn`, `show-more-container` - Show more button and container
- `species-list`, `species-list-emoji`, `species-list-icon`, `species-list-item`, `species-list-more`, `species-list-name`, `species-list-showcase`, `species-list-tier` - Species list component classes
- `text-right` - Utility class

**Note:** Some of these classes may be:
- Added dynamically via JavaScript (e.g., `scrolled-from-bottom`, `common`, `rare`)
- Used in dynamically generated content
- Part of reusable components not yet used
- Left over from removed features (e.g., `retro-breadcrumb`)

**Recommendation:** Review each class manually to verify if it's truly unused before removing.

---

## 4. Unused CSS Variables (40 total)

The following CSS custom properties are defined but never referenced with `var()`:

### Color Variables
- `--accent-dark-brown` - Dark brown for light mode headers
- `--badge-lake-border-light`, `--badge-park-border-light`, `--badge-pier-border-light`, `--badge-public-border-light`, `--badge-river-border-light` - Light mode badge border colors
- `--earth-clay`, `--earth-olive`, `--earth-terracotta` - Earth tone colors

### Layout Variables
- `--container-padding-desktop` - Desktop container padding (used: `--container-padding-desktop-inner`)

### Typography Variables
- `--font-body` - Legacy alias (uses `--font-primary`)
- `--font-display` - Legacy alias (uses `--font-accent`)
- `--font-terminal` - Legacy alias (uses `--font-primary`)
- `--font-size-4xl` - Extra large font size
- `--font-weight-black` - Black font weight (900)
- `--font-weight-medium` - Medium font weight (500)

**Recommendation:**
- Legacy aliases can be removed if not used in JavaScript
- Badge border light variables may be needed for future styling
- Consider if `--font-size-4xl` and `--font-weight-medium` should be removed or used

---

## 5. Undefined Variables (2 total)

These variables are used with `var()` but never defined:

1. **`--rgba-black-25`** - Used in multiple places for box shadows
   - **Used in:** retro-common.css (lines 190, 863, 1026) - Light mode box shadows
   - **Note:** Variables for 01, 02, 03, 05, 10, 15, 20, 30, 40, 50, 60, 80 exist, but 25 is missing
   - **Recommendation:** Add `--rgba-black-25: rgba(0, 0, 0, 0.25);` to retro-colors.css in the rgba-black section (between lines 107-108)

2. **`--rgba-sand-50`** - Used for sand color with opacity
   - **Used in:** retro-common.css (lines 1506, 1552: `text-shadow: 0 0 8px var(--rgba-sand-50);`)
   - **Note:** `--rgba-sand-30`, `--rgba-sand-40`, and `--rgba-sand-60` exist, but `--rgba-sand-50` is missing
   - **Recommendation:** Add `--rgba-sand-50: rgba(212, 165, 116, 0.5);` to retro-colors.css in the rgba-sand section (line ~157)

**Recommendation:** Add missing variable definitions or fix variable names if typos.

---

## 6. Style Conflicts (83 total)

The following selectors are defined multiple times across different files, which can cause style conflicts:

Common conflicting selectors include:
- Pseudo-classes (`:hover`, `:focus`, `:active`)
- Light mode overrides (`[data-theme="light"] .*`)
- Media query selectors
- Element selectors with modifiers

**Note:** Many of these conflicts are intentional (e.g., theme-specific overrides, responsive breakpoints). However, review to ensure no unintended conflicts exist.

---

## 7. CSS Variable Reference Map

All CSS variables are cataloged with their definitions and usages. Key findings:

### Most Used Variables
- `--rgba-sage-*` variants (high usage for borders, backgrounds)
- `--rgba-black-*` variants (high usage for shadows, overlays)
- `--theme-*` variables (theme-specific colors)
- `--font-*` variables (typography)

### Variable Organization
- **Root level:** Base color palette, typography, spacing
- **Dark mode (`[data-theme="dark"]`):** Dark theme overrides
- **Light mode (`[data-theme="light"]`):** Light theme overrides
- **Media queries:** Responsive font sizing

### Variable Conflicts
No conflicts found - all variables are properly scoped.

---

## 8. Recommendations

### High Priority
1. **Remove hardcoded styles:**
   - Move `style="display: none;"` from ResultsWidget.astro to CSS
   - Keep SearchWidget.tsx dynamic style (acceptable)

2. **Extract embedded styles:**
   - Move Layout.astro styles to dedicated CSS file
   - Consolidate page-specific styles into main CSS files

3. **Fix undefined variables:**
   - Add `--rgba-black-25` definition
   - Verify `--accent-dark-orange` definition

### Medium Priority
4. **Review unused classes:**
   - Manually verify each unused class
   - Remove truly unused classes
   - Document classes used by JavaScript

5. **Clean up unused variables:**
   - Remove legacy variable aliases
   - Remove truly unused color/spacing variables
   - Keep variables that may be used in future

6. **Document dynamic classes:**
   - Document classes added via JavaScript
   - Consider using data attributes instead

### Low Priority
7. **Organize CSS files:**
   - Consider splitting large CSS files
   - Group related styles together
   - Add section comments

8. **Review style conflicts:**
   - Ensure intentional conflicts are well-documented
   - Fix any unintended conflicts

---

## 9. Files Analyzed

### CSS Files
- `frontend/src/styles/retro-colors.css` (455 lines)
- `frontend/src/styles/retro-common.css` (2048 lines)
- `frontend/src/styles/search-widget.css` (2282 lines)

### Layout Files
- `frontend/src/layouts/Layout.astro`

### Page Files
- `frontend/src/pages/index.astro`
- `frontend/src/pages/states.astro`
- `frontend/src/pages/texas.astro`
- `frontend/src/pages/texas/[county]/index.astro`
- `frontend/src/pages/texas/[county]/[slug].astro`
- `frontend/src/pages/texas/fishing-without-license.astro`

### Component Files
- `frontend/src/components/ResultsWidget.astro`
- `frontend/src/components/SearchWidget.tsx`
- `frontend/src/components/CountyListing.tsx`
- `frontend/src/components/DynamicSubtitle.tsx`
- `frontend/src/components/SpecialLandingPageCallout.tsx`
- `frontend/src/components/ValuePropositionBadges.tsx`
- `frontend/src/components/WhatEachListingIncludes.tsx`

### HTML Files
- `frontend/public/maintenance.html`

---

## Conclusion

The CSS audit reveals a well-organized system with extensive use of CSS custom properties. The main issues are:

1. **Hardcoded styles** - Only 2 instances, one of which is acceptable
2. **Embedded styles** - 8 embedded style blocks that should be moved to CSS files
3. **Unused classes** - 66 classes that may be unused (require manual verification)
4. **Unused variables** - 40 variables that may be unused (mostly legacy aliases)
5. **Undefined variables** - 2 variables used but not defined

The codebase follows good CSS practices with extensive use of CSS variables for theming. Most "unused" classes are likely used dynamically via JavaScript or are part of reusable components.

**Next Steps:**
1. Fix hardcoded styles and undefined variables
2. Extract embedded styles to CSS files
3. Manually review unused classes and variables
4. Document classes used dynamically by JavaScript

