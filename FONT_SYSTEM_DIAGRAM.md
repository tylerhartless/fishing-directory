# Font System Architecture

## 🏗️ Font Variable Hierarchy (Semantic & Theme-Agnostic)

```
┌──────────────────────────────────────────────────────────┐
│         :root (Base Variables - Semantic Naming)         │
│   frontend/src/styles/retro-colors.css (Lines 183-208)  │
├──────────────────────────────────────────────────────────┤
│  --font-primary: 'VT323', monospace  ⭐ MAIN CONTROL     │
│  --font-accent: 'Press Start 2P', monospace              │
│  --font-system: System fonts                             │
│                                                           │
│  --font-size-xs through --font-size-4xl                  │
│  --font-weight-normal through --font-weight-black        │
│                                                           │
│  Legacy Aliases (backward compatibility):                │
│  --font-terminal → var(--font-primary)                   │
│  --font-display → var(--font-accent)                     │
│  --font-body → var(--font-system)                        │
└──────────────────────────────────────────────────────────┘
                           ↓
         ┌─────────────────┴─────────────────┐
         ↓                                     ↓
┌────────────────────┐              ┌─────────────────────┐
│   DARK MODE        │              │   LIGHT MODE        │
│   (Lines 237-242)  │              │   (Lines 277-281)   │
├────────────────────┤              ├─────────────────────┤
│ ANY design style!  │              │ ANY design style!   │
├────────────────────┤              ├─────────────────────┤
│ --font-heading     │              │ --font-heading      │
│ --font-body-text   │              │ --font-body-text    │
│ --weight-heading   │              │ --weight-heading    │
│ --weight-body      │              │ --weight-body       │
│ --weight-emphasis  │              │ --weight-emphasis   │
└────────────────────┘              └─────────────────────┘
         ↓                                     ↓
┌──────────────────────────────────────────────────────────┐
│            Applied Throughout CSS                         │
├──────────────────────────────────────────────────────────┤
│  • Headings use: var(--font-heading)                     │
│  • Body text uses: var(--font-body-text)                 │
│  • Buttons use: var(--font-body-text)                    │
│  • Forms use: var(--font-body-text)                      │
│  • Cards use: var(--font-body-text)                      │
│  • Emphasis uses: var(--weight-emphasis)                 │
└──────────────────────────────────────────────────────────┘
```

## 🎯 Single Point of Control

### To Change Site-Wide Font:

**Edit ONE line** in `frontend/src/styles/retro-colors.css`:

```css
/* Line 183 - Works for ANY design style! */
--font-primary: 'YOUR_NEW_FONT', fallback-family;
```

**Examples:**
```css
--font-primary: 'Inter', sans-serif;              /* Modern & clean */
--font-primary: 'Georgia', serif;                 /* Classic & elegant */
--font-primary: 'Courier New', monospace;         /* Code style */
--font-primary: 'Merriweather', serif;            /* Editorial */
```

### Effect:
✅ All headings update instantly
✅ All body text updates instantly
✅ All buttons update instantly
✅ All forms update instantly
✅ All cards update instantly
✅ Both light AND dark mode update
✅ Works with ANY font style (not just "terminal"!)  

---

## 🔄 Font Application Flow

```
User Changes Variable → CSS Variables Update → DOM Re-renders → All Text Updates
     (1 line)              (Automatic)          (Instant)        (Site-wide)
```

## 📊 Font Variable Usage Map

**Semantic Variables (Theme-Agnostic):**

| Component | Variable Used | Controlled By | Defined In |
|-----------|--------------|---------------|------------|
| **Page Headers** | `--font-heading` | Dark/Light theme | retro-common.css |
| **Body Text** | `--font-body-text` | Dark/Light theme | retro-common.css |
| **Buttons** | `--font-body-text` | Dark/Light theme | retro-common.css |
| **Forms/Inputs** | `--font-body-text` | Dark/Light theme | retro-common.css |
| **Cards** | `--font-body-text` | Dark/Light theme | search-widget.css |
| **Breadcrumbs** | `--font-body-text` | Dark/Light theme | retro-common.css |
| **Badges** | `--font-body-text` | Dark/Light theme | retro-common.css |
| **Logo** | `--font-accent` | Base variable | Layout.astro |
| **Footer** | `--font-body-text` | Dark/Light theme | Layout.astro |
| **Emphasis/Bold** | `--weight-emphasis` | Dark/Light theme | All components |

**Base Font Control:**

| Base Variable | Controls | Used For |
|---------------|----------|----------|
| `--font-primary` | Site-wide font | ⭐ ALL text (headings, body, buttons, forms) |
| `--font-accent` | Special elements | Logo and accent elements |
| `--font-system` | System fallback | Fallback if custom fonts fail |

## 🎨 Theme-Specific Customization

### Scenario: Different fonts for each theme

**Semantic variables make this super clean:**

```css
/* Dark Mode: Retro monospace feel */
[data-theme="dark"] {
  --font-heading: 'Courier New', monospace;
  --font-body-text: 'Courier New', monospace;
  --weight-heading: var(--font-weight-normal);
  --weight-body: var(--font-weight-normal);
  --weight-emphasis: var(--font-weight-normal);
}

/* Light Mode: Modern sans-serif */
[data-theme="light"] {
  --font-heading: 'Inter', sans-serif;
  --font-body-text: 'Inter', sans-serif;
  --weight-heading: var(--font-weight-bold);
  --weight-body: var(--font-weight-medium);
  --weight-emphasis: var(--font-weight-bold);
}
```

**Result:**
- 🌙 Dark mode: Monospace terminal aesthetic
- ☀️ Light mode: Clean modern sans-serif
- ✅ Variable names make sense regardless of font choice!

## 💡 Pro Tips

### 1. Font Loading
Add fonts to `frontend/src/layouts/Layout.astro` (lines 29-32) before using them:

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
```

### 2. Fallback Fonts
Always include fallbacks:

```css
--font-terminal: 'VT323', 'Courier New', monospace;
                 ^primary  ^fallback     ^generic
```

### 3. Font Display
Use `&display=swap` in Google Fonts URLs for better performance:

```
?family=Inter&display=swap
```

### 4. Testing
After changes, test:
- ✅ Dark mode
- ✅ Light mode  
- ✅ Mobile view
- ✅ Desktop view
- ✅ All page types (home, listings, detail)

## 🔧 Quick Font Swap Examples

### Example 1: Modern Sans-Serif (Site-Wide)
```css
/* Line 183 - ONE change */
--font-primary: 'Inter', -apple-system, sans-serif;
```

### Example 2: Classic Serif (Site-Wide)
```css
/* Line 183 - ONE change */
--font-primary: 'Merriweather', 'Georgia', serif;
```

### Example 3: Theme-Specific Fonts
```css
/* Different font per theme */
[data-theme="dark"] {
  --font-body-text: 'Roboto Mono', monospace;
}

[data-theme="light"] {
  --font-body-text: 'Roboto', sans-serif;
  --weight-body: var(--font-weight-medium);
}
```

### Example 4: Editorial/Magazine Style
```css
/* Line 183 */
--font-primary: 'Spectral', 'Georgia', serif;
--font-accent: 'Playfair Display', serif;

/* Adjust weights for readability */
[data-theme="light"] {
  --weight-body: var(--font-weight-medium);
  --weight-emphasis: var(--font-weight-bold);
}
```

---

## 📝 Summary

**Before this system:**
- Had to update ~50+ CSS files
- Risk of missing instances
- Inconsistent across themes
- Time-consuming updates
- ❌ Theme-specific variable names (--font-terminal)

**After this system:**
- ✅ Update 1 variable (--font-primary)
- ✅ Guaranteed consistency
- ✅ Theme-specific control
- ✅ Instant site-wide changes
- ✅ Semantic naming works for ANY design style!

**Why semantic naming matters:**

| Old (Theme-Specific) | New (Semantic) | Why Better? |
|---------------------|----------------|-------------|
| `--font-terminal` | `--font-primary` | ✅ Works for terminal, modern, serif, ANY style |
| `--theme-font-heading` | `--font-heading` | ✅ Shorter, clearer |
| `--theme-font-body` | `--font-body-text` | ✅ More descriptive |
| `--theme-font-weight-bold` | `--weight-emphasis` | ✅ Semantic purpose, not just weight |

**Location of all controls:**
```
frontend/src/styles/retro-colors.css
Lines 183-190 (base fonts - includes legacy aliases)
Lines 193-201 (font sizes)
Lines 204-208 (font weights)
Lines 237-242 (dark mode typography)
Lines 277-281 (light mode typography)
```

✨ **Change fonts in seconds, not hours!**
🎨 **Variable names that make sense for ANY design!**

