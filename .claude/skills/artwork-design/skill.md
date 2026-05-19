---
name: artwork-design
description: |
  Apply this skill whenever creating icons, badges, illustrations, artwork, or graphic elements
  for slides, decks, documents, or branding. Trigger on requests like "create an icon",
  "make a badge", "design a visual", "add artwork", "create an illustration", or when any
  agent needs to generate non-chart visual assets (logos, badges, decorative graphics,
  infographic elements). Also apply when placing or compositing existing brand assets into
  new compositions. This skill ensures all generated artwork matches the user's approved
  design direction: real brand assets, clean icon style, modern typography, and high-quality
  rendering via supersampling.
---

# Skill: Artwork & Icon Design

## Purpose

Ensure all generated artwork, icons, badges, and non-chart visual assets are high-quality,
on-brand, and follow the user's approved design style.

## When to Use

Apply whenever:
- Creating icons, badges, or branding elements for slides/decks
- Compositing brand assets into new visuals
- Generating infographic-style illustrations
- Adding decorative or explanatory graphics to presentations
- Any non-chart image that needs to be created programmatically

## Design Principles

### 1. Always Use Real Brand Assets

**NEVER** draw custom logos, characters, or brand elements from scratch.
- Use existing assets from `.knowledge/templates/assets/` (mgo_logo.png, mgo_artwork.png, mgo_brand_mark.png)
- Composite and enhance — don't recreate
- If a brand asset doesn't exist, ask the user to provide one

### 2. Icon Style Reference

All icons and small illustrations should follow the style of:
- `.knowledge/templates/assets/line_example_1.png` — clean bar chart with connected-dot line overlay
- `.knowledge/templates/assets/line_example_2.png` — dashboard-style icon with bars, pie chart, clean arrow

**Key characteristics of approved icon style:**
- Clean, flat design with minimal gradients
- Bold outlines (not thin/wispy)
- Connected dots with straight line segments (not curves)
- Bars with slight rounding, ascending pattern
- Magnifying glass = investigation/analysis
- No messy curves, no upward-pointing arrows, no jagged lines
- Compact composition — elements close together, not scattered

### 3. Color Palette (Monopoly-Aligned)

| Color | Hex | Usage |
|-------|-----|-------|
| Charcoal | #3B3447 | Primary outlines, text, line chart dots |
| Navy | #37456E | Bar fills (first bars) |
| Warm Red | #C83232 | Bar fills (middle bars), accent |
| Rich Gold | #C8A53C | Bar fills (last/tallest bars), sparkle accents |
| MGO Gold | #DBC585 | Highlights, subtle accents |
| Cream | #FFF8EB | Magnifying glass fill, light backgrounds |
| Hat Green | #3C7850 | Sparingly, for MGO character reference |

**Avoid:** Neon colors, saturated tech blues/purples, rainbow palettes, bright yellow matching the logo text.

### 4. Typography for Badges/Labels

- **Font:** Segoe UI Light (thin, modern)
- **Style:** Letter-spaced, all caps
- **Color:** Charcoal (#3B3447) — understated, doesn't compete with brand assets
- **Never:** Impact, bold gold text, outlined/shadowed text that mimics the game logo

### 5. Rendering Quality

Always use **4x supersampling** to avoid pixelation:

```python
SCALE = 4  # Draw at 4x resolution

# Create canvas at 4x
canvas_w, canvas_h = final_w * SCALE, final_h * SCALE
canvas = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 0))

# ... draw everything at SCALE coordinates ...

# Downsample for smooth anti-aliased output
final = canvas.resize((final_w, final_h), Image.LANCZOS)
final.save(output_path, "PNG")
```

### 6. Composition Rules

- Keep elements compact and close together
- Text should be tight below the icon, not floating far away
- Center elements relative to the overall composition
- Use transparent backgrounds (RGBA) for flexible placement
- Target sizes: badges ~440x260px, inline icons ~200x200px

### 7. AI/Analytics Visual Elements

When representing "AI" or "analytics" visually:
- **Bars:** 3-5 ascending bars in navy → red → gold gradient
- **Line:** Connected dots with straight segments on top of bars (NOT curves)
- **Magnifying glass:** Small, to the side, with mini-chart inside
- **Sparkles:** Small 4-pointed stars in gold, 2-3 max, subtle
- **No arrows** pointing up — the ascending bars already communicate growth

## Existing Badge Assets

| Asset | Path | Description |
|-------|------|-------------|
| AI Badge (Logo) | `.knowledge/templates/assets/ai_powered_badge.png` | MGO logo + analytics icon + "AI POWERED / ANALYSIS" |
| AI Badge (Artwork) | `.knowledge/templates/assets/ai_powered_badge_v2.png` | Mr. Monopoly + analytics icon + "AI POWERED / ANALYSIS" |

**Regeneration script:** `scripts/make_badge.py` — modify and rerun to update badges.

## Reference Samples

Keep these files as the canonical style reference:
- `.knowledge/templates/assets/line_example_1.png` — bar chart + connected dot line
- `.knowledge/templates/assets/line_example_2.png` — dashboard icon with bars + arrow

## Anti-Patterns (NEVER Do)

- Drawing custom logos, characters, or top hats from scratch
- Using Pillow at 1x resolution (always 4x supersample)
- Bright/neon tech colors that clash with Monopoly palette
- Bold Impact-style text or gold text that competes with the logo
- Curved/wavy trend lines (use straight connected segments)
- Upward-pointing arrows
- Scattered elements with too much whitespace between them
- Low-contrast, faded elements that become unreadable at small sizes
