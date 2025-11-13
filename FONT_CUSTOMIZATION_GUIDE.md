# Font Customization Guide

This guide explains how to easily change fonts across the entire WhereCanIFish.com website.

## 📍 Location

All font variables are centralized in:
```
frontend/src/styles/retro-colors.css
```

## 🎨 Font Variables

### Base Font Families (Lines 183-185)
**Semantic naming - works with ANY design style:**

```css
--font-primary: 'VT323', monospace;           /* Primary font used site-wide */
--font-accent: 'Press Start 2P', monospace;   /* Accent font for logo and special elements */
--font-system: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; /* System font fallback */
```

**Legacy aliases** (for backward compatibility):
```css
--font-terminal: var(--font-primary);
--font-display: var(--font-accent);
--font-body: var(--font-system);
```

### Font Sizes (Lines 193-201)
Consistent sizing across all components:

```css
--font-size-xs: 1rem;
--font-size-sm: 1.1rem;
--font-size-base: 1.2rem;
--font-size-md: 1.3rem;
--font-size-lg: 1.5rem;
--font-size-xl: 1.8rem;
--font-size-2xl: 2rem;
--font-size-3xl: 2.8rem;
--font-size-4xl: 3rem;
```

### Font Weights (Lines 204-208)
Semantic naming for weights:

```css
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
--font-weight-black: 900;
```

### Theme-Specific Typography (Lines 237-242, 277-281)

**Semantic variables that work with ANY design:**

#### Dark Mode
```css
--font-heading: var(--font-primary);      /* Font for all headings */
--font-body-text: var(--font-primary);    /* Font for body text, buttons, forms */
--weight-heading: var(--font-weight-normal);
--weight-body: var(--font-weight-normal);
--weight-emphasis: var(--font-weight-normal);  /* For bold/emphasized text */
```

#### Light Mode
```css
--font-heading: var(--font-primary);
--font-body-text: var(--font-primary);
--weight-heading: var(--font-weight-normal);
--weight-body: var(--font-weight-normal);
--weight-emphasis: var(--font-weight-bold);    /* Bolder for better readability */
```

## 🚀 How to Change Fonts

### Change All Fonts Site-Wide (Both Themes)

Update **line 183** in `retro-colors.css`:

```css
/* FROM: */
--font-primary: 'VT323', monospace;

/* TO: Any font you want! */
--font-primary: 'Inter', sans-serif;              /* Modern */
--font-primary: 'Georgia', serif;                 /* Classic */
--font-primary: 'Courier New', monospace;         /* Code style */
--font-primary: 'Merriweather', serif;            /* Editorial */
```

✨ That's it! The entire site updates instantly.

### Use Different Fonts for Light vs Dark Mode

**Theme-specific fonts - great for mixed aesthetics:**

```css
/* Dark mode - modern monospace */
[data-theme="dark"] {
  --font-heading: 'Roboto Mono', monospace;
  --font-body-text: 'Roboto Mono', monospace;
}

/* Light mode - elegant serif */
[data-theme="light"] {
  --font-heading: 'Georgia', serif;
  --font-body-text: 'Georgia', serif;
  --weight-body: var(--font-weight-medium);  /* Adjust weight for serif */
}
```

### Change Font Weights

Adjust readability and visual hierarchy:

```css
[data-theme="light"] {
  --weight-heading: var(--font-weight-bold);      /* Bolder headings */
  --weight-body: var(--font-weight-medium);       /* Medium body text */
  --weight-emphasis: var(--font-weight-black);    /* Heavy emphasis */
}
```

## 📝 Examples

### Example 1: Modern Sans-Serif (Both Themes)
```css
/* Line 183 - ONE change, entire site updates */
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-accent: 'Inter', sans-serif;
```

### Example 2: Classic Serif (Both Themes)
```css
/* Line 183 */
--font-primary: 'Georgia', 'Times New Roman', serif;
--font-accent: 'Georgia', serif;
```

### Example 3: Mixed Aesthetic (Different Per Theme)
**Perfect when you want totally different vibes:**

```css
/* Dark mode - retro terminal feel */
[data-theme="dark"] {
  --font-heading: 'VT323', monospace;
  --font-body-text: 'VT323', monospace;
  --weight-emphasis: var(--font-weight-normal);
}

/* Light mode - elegant modern feel */
[data-theme="light"] {
  --font-heading: 'Inter', sans-serif;
  --font-body-text: 'Inter', sans-serif;
  --weight-heading: var(--font-weight-bold);
  --weight-body: var(--font-weight-medium);
  --weight-emphasis: var(--font-weight-bold);
}
```

### Example 4: Editorial Style
```css
/* Line 183 */
--font-primary: 'Merriweather', 'Georgia', serif;
--font-accent: 'Playfair Display', serif;

/* Make light mode more readable with increased weight */
[data-theme="light"] {
  --weight-body: var(--font-weight-medium);
  --weight-emphasis: var(--font-weight-bold);
}
```

## 🔤 Adding New Fonts

If using Google Fonts or custom fonts, add them to `Layout.astro` (lines 29-32):

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=YOUR_FONT:wght@400;500;700&display=swap" rel="stylesheet">
```

Then reference in CSS (line 183):
```css
--font-primary: 'YOUR_FONT', sans-serif;
```

## ⚡ Quick Reference

**Semantic Variables (Theme-Agnostic):**

| Variable | Current Value | Used For |
|----------|---------------|----------|
| `--font-primary` | 'VT323' | Main site-wide font |
| `--font-accent` | 'Press Start 2P' | Logo and special accents |
| `--font-system` | System fonts | System fallback |
| `--font-heading` | var(--font-primary) | All headings (theme-aware) |
| `--font-body-text` | var(--font-primary) | Body text, forms, buttons (theme-aware) |
| `--weight-heading` | 400 | Heading weight (theme-aware) |
| `--weight-body` | 400 | Body text weight (theme-aware) |
| `--weight-emphasis` | 400/700 | Bold/emphasized text (theme-aware) |

**Legacy Variables (Deprecated):**
- `--font-terminal` → Use `--font-primary`
- `--font-display` → Use `--font-accent`
- `--font-body` → Use `--font-system`

## 🎯 Testing Changes

After changing fonts:

1. Save `frontend/src/styles/retro-colors.css`
2. Refresh your browser
3. Toggle between light and dark modes
4. Check all pages:
   - ✅ Homepage
   - ✅ State listings
   - ✅ County listings  
   - ✅ Spot detail pages
5. Verify elements:
   - ✅ Page headers
   - ✅ Body text
   - ✅ Buttons
   - ✅ Forms
   - ✅ Cards
   - ✅ Breadcrumbs

## 📚 Font Recommendations

**Retro/Terminal/Code:**
- VT323 (current default)
- Courier New
- IBM Plex Mono
- Source Code Pro
- Fira Code

**Modern Sans-Serif:**
- Inter ⭐ (highly recommended)
- Roboto
- Open Sans
- Lato
- Work Sans

**Classic Serif:**
- Georgia
- Merriweather
- Playfair Display
- Crimson Text
- Lora

**Editorial/Magazine:**
- Spectral
- Libre Baskerville
- Cormorant Garamond

**Display/Accent:**
- Bebas Neue
- Oswald
- Archivo Black

---

## 🎨 Why Semantic Naming?

**Old way** (theme-specific):
```css
--font-terminal: 'VT323'  /* ❌ What if you don't want terminal fonts? */
```

**New way** (semantic):
```css
--font-primary: 'Inter'   /* ✅ Works for ANY design style */
```

The semantic names (`--font-primary`, `--font-heading`, `--font-body-text`) work whether you're using:
- Terminal fonts
- Modern sans-serif
- Classic serif
- Editorial styles
- Display fonts
- Or anything else!

**Note:** Font variables automatically apply throughout the entire CSS. Change `--font-primary` once, and the entire site updates instantly!

