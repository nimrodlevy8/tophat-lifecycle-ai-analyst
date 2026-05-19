# MGO Data & Insights Deck — Design System

Extracted from the official Monopoly GO! Data & Insights Deck Template (May 2025).
This file is the single source of truth for all presentation styling.

**Template file:** `.knowledge/templates/Copy of Monopoly GO! Data & Insights Deck Template - May 2025.pptx`

---

## Slide Dimensions

- **Width:** 20.0 inches (18,288,000 EMU)
- **Height:** 11.25 inches (10,287,000 EMU)
- **Aspect ratio:** 16:9 widescreen

---

## Typography

### Font Hierarchy

| Role | Font | Weight | Size | Color | Usage |
|------|------|--------|------|-------|-------|
| **Cover title** | Jost ExtraBold | 800 | 80pt | theme (dark purple) | Cover slide main text |
| **Section divider** | Jost ExtraBold | 800 | 80pt | #43384F | Section break slides |
| **Slide title** | Jost ExtraBold | 800 | 48pt | theme (dark) | Top of every content slide |
| **Section heading** | Jost | Bold | 26pt | #3B3447 | Numbered section headers within slides |
| **Textbox title** | Jost ExtraBold | 800 | 24-25pt | theme | Callout box headers |
| **Graph title** | Jost | Regular | 20pt | #3B3447 | Chart titles above visuals |
| **Body text** | Quicksand | Regular | 22pt | #3B3447 | General narrative text |
| **Body text (dense)** | Quicksand | Regular | 18-20pt | #3B3447 | A/B test decks, smaller layouts |
| **Supporting bold** | Quicksand | Bold/Medium | 22pt | #3B3447 | Key callout labels |
| **Quotes/guidance** | Quicksand | Regular | 19-22pt | #3B3447 | Italic guidance text |
| **Cover subtitle** | Proxima Nova | Regular | 22pt | theme | POC and date on cover |
| **Table headers** | Proxima Nova | Regular | 20pt | — | Table column headers |
| **Source line** | Quicksand | Regular | 16pt | #3B3447 | Data source attribution at bottom |

### Font Rules
- **Titles** always use **Jost** (ExtraBold for slide titles, Bold for section headers)
- **Body text** always uses **Quicksand** (Regular for narrative, Bold/Medium for emphasis)
- **Tables** use **Proxima Nova**
- Never mix: Jost is for structure, Quicksand is for content, Proxima Nova is for tabular data

### Font Fallbacks
If Jost/Quicksand/Proxima Nova are unavailable:
- Jost → Montserrat → Arial Bold
- Quicksand → Open Sans → Calibri
- Proxima Nova → Arial → Calibri

---

## Color Palette

### Primary Colors (Draw Attention)

| Swatch | Hex | Name | Usage |
|--------|-----|------|-------|
| Red | `#DF2728` | Alert Red | Negative metrics, warnings, "needs attention" |
| Green | `#63D200` | Success Green | Positive metrics, "on track" |
| Dark Purple | `#3B3447` | Primary Text | Main body text, headings, high-contrast elements |
| Gold | `#DBC585` | Accent Gold | Highlights, accents, category markers |
| Purple | `#CE9AFF` | Light Purple | Secondary category, differentiation |
| Olive | `#625C45` | Olive Brown | Tertiary category, muted accent |

### Secondary Colors (Create Contrast)

| Swatch | Hex | Name | Usage |
|--------|-----|------|-------|
| Cream | `#F8F5E5` | Warm Cream | Light backgrounds, callout fills |
| Light Green | `#B3E4BF` | Soft Green | Subtle positive indicators |
| Gray | `#CACACA` | Medium Gray | Borders, dividers, inactive elements |
| Light Gray | `#F7F6F3` | Off-White | Slide backgrounds, card backgrounds |

### Functional Colors

| Purpose | Hex | Notes |
|---------|-----|-------|
| Primary text | `#3B3447` | Dark purple-gray, used everywhere |
| Section divider text | `#43384F` | Slightly darker, for impact slides |
| Slide background | `#FFFFFF` | White default |
| Accent background | `#F7F6F3` | Off-white for subtle contrast |
| Warm background | `#F8F5E5` | Cream for callout boxes |
| Highlight blue | `#26BEF7` | Sparingly, for interactive/link elements |
| Light blue | `#B3E4FB` | Soft blue accent |

### Chart Color Sequence
When building charts, use colors in this order:
1. `#3B3447` — primary series
2. `#DBC585` — secondary series (gold)
3. `#CE9AFF` — third series (purple)
4. `#63D200` — fourth series (green)
5. `#DF2728` — fifth series (red, or use for negative)
6. `#625C45` — sixth series (olive)
7. `#CACACA` — baseline/reference (gray)

### Traffic Light System
Used for analysis maturity status on performance reads:
- **Red** `#DF2728` + ❓ — Preliminary, needs more investigation
- **Orange/Gold** `#DBC585` + 🔨 — In progress, gaining confidence
- **Green** `#63D200` + ✓ — Complete, high confidence

---

## Layout Patterns

### Primary Layout: TITLE_10 (27 of 44 slides)

Standard content slide with title at top-left.

```
┌──────────────────────────────────────────┐
│ Slide Title (Jost ExtraBold 48pt)        │  ← y=0.4", x=0.4"
│                                          │
│  ┌─────────────────────────────────────┐ │
│  │                                     │ │  ← Content area starts y~2.0"
│  │         CHART / CONTENT             │ │
│  │                                     │ │
│  └─────────────────────────────────────┘ │
│                                          │
│  Supporting Message (Quicksand 22pt)     │  ← y~9.1"
│  Source: (Quicksand 16pt)                │  ← y~10.6"
└──────────────────────────────────────────┘
```

**Key positions (inches):**
- Title: x=0.4, y=0.4, w=15.1, h=1.1
- Content area: starts y=2.0, varies
- Supporting message: y=9.1, w=9.5, h=1.3
- Source line: y=10.6, w=14.5

### Section Divider: BLANK_4 (9 slides)

Large centered text on branded background.

```
┌──────────────────────────────────────────┐
│                                          │
│                                          │
│         Section Title                    │  ← Jost ExtraBold 80pt
│         (centered, large)                │     centered in slide
│                                          │
│                                          │
└──────────────────────────────────────────┘
```

**Key positions:** Text centered, typically x=3.8, y=3.6, w=12.4, h=4.0

### Two-Chart Layout

Side-by-side charts with individual titles and annotations.

```
┌──────────────────────────────────────────┐
│ Slide Title                              │
│                                          │
│  Graph Title 1          Graph Title 2    │  ← Jost 20pt
│  ┌──────────┐          ┌──────────┐     │
│  │  Chart 1  │          │  Chart 2  │    │  ← Each ~9.4" wide
│  └──────────┘          └──────────┘     │
│  Message 1              Message 2        │  ← Quicksand 22pt bold + 18pt
│  Source line                             │
└──────────────────────────────────────────┘
```

**Key positions:**
- Chart 1: x=0.4, y=2.4, w=9.4, h=6.3
- Chart 2: x=10.3, y=2.4, w=9.4, h=6.3
- Graph title 1: x=0.4, y=1.8
- Graph title 2: x=10.3, y=1.8

### Textbox / Callout Layout

3-column textbox cards.

```
┌──────────────────────────────────────────┐
│ Slide Title                              │
│                                          │
│  ┌──────┐  ┌──────┐  ┌──────┐          │
│  │TITLE │  │TITLE │  │TITLE │          │
│  │ body │  │ body │  │ body │          │  ← Each ~5.0" x 3.1"
│  └──────┘  └──────┘  └──────┘          │
│  ┌──────┐  ┌──────┐  ┌──────┐          │
│  │TITLE │  │TITLE │  │TITLE │          │
│  │ body │  │ body │  │ body │          │
│  └──────┘  └──────┘  └──────┘          │
└──────────────────────────────────────────┘
```

**Textbox styling:**
- Title: Jost ExtraBold 24pt
- Body: Quicksand 18-22pt
- Card size: ~5.0" x 3.1"
- Spacing: ~0.4" between cards

### Data Callout Boxes

Use callout boxes to highlight key data points on chart slides. Place them
adjacent to the chart, pointing at the relevant data area.

```python
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def add_data_callout(slide, text, left, top, width=Inches(3.5), height=Inches(1.2)):
    """Add a cream-background callout box highlighting a key data point.
    
    Use these to annotate charts on slides — similar to the template's
    textbox callout pattern. Place adjacent to charts, not overlapping them.
    """
    txBox = slide.shapes.add_textbox(left, top, width, height)
    
    # Cream background fill (#F8F5E5)
    fill = txBox.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0xF8, 0xF5, 0xE5)
    
    # Gold left border accent
    txBox.line.color.rgb = RGBColor(0xDB, 0xC5, 0x85)
    txBox.line.width = Pt(3)
    
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.name = 'Quicksand'
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x3B, 0x34, 0x47)
    
    return txBox
```

**Callout placement rules:**
- Place callouts to the RIGHT or BELOW the chart, never overlapping it
- Use for the single most important data point per chart
- Maximum 1-2 callouts per slide
- Text must be short: one number + one sentence (e.g., "-18% — Mobile conversion dropped after the iOS 18 update")
- Background: Warm Cream (#F8F5E5) with Gold (#DBC585) left border accent

---

## Deck Narrative Structures

The template defines five deck types. Use the one that best matches the analysis:

### 1. Standard Analytics Deck
1. Executive Summary: The Core Insight
2. Deep Dive: The Evidence Behind the Insight
3. Recommendations: What to Do With the Insight
4. Annex: Supporting Details & FAQs

### 2. Exploratory Analysis Deck
1. Executive Summary: The Key Discovery
2. Methodology: How We Explored the Question
3. Deep Dive: What We Found
4. Recommendations & Next Steps

### 3. Performance Read Deck
1. Executive Summary: How Did It Perform?
2. Context & Setup: What Was Run and Why
3. Deep Dive: What Worked, What Didn't
4. Recommendations: What to Double Down On or Fix

### 4. A/B Test Read Deck
1. Executive Summary: What Did the Test Tell Us?
2. Test Setup: What We Tested and Why
3. Results: What Happened in the Data
4. Interpretation: What It Means for the Business
5. Recommendations & Next Steps

### 5. New Measurement Framework Deck
1. Executive Summary: Why We're Updating How We Measure
2. Limitations of the Current Framework
3. Overview of the New Framework
4. Application Example: Before vs After
5. Rollout Plan: How We'll Transition

---

## Template Usage with python-pptx

When building .pptx output, always load from the template:

```python
from pptx import Presentation

# Load the template — preserves master, layouts, fonts, and branding
prs = Presentation('.knowledge/templates/Copy of Monopoly GO! Data & Insights Deck Template - May 2025.pptx')

# CANONICAL LAYOUTS — use these exclusively:
cover_layout = prs.slide_layouts[5]                      # BLANK_2 — cover slide
content_layout = prs.slide_masters[1].slide_layouts[36]  # TITLE_10 — ALL content slides

# CRITICAL: TITLE_10 is on slide master 1 (index 1), NOT master 0.
#   prs.slide_master (singular) = master 0 = only 33 layouts, no TITLE_10
#   prs.slide_masters[1] (plural, index 1) = master 1 = 100 layouts, TITLE_10 at idx 36
# Never use prs.slide_master.slide_layouts[36] — it raises IndexError.

# TITLE_10 has built-in brand mark at (17.0", 0.4") — do NOT add brand mark manually.
# BLANK_2 does NOT have brand mark — add it manually on cover if needed.

# NEVER use Layout 0 (TITLE) — it has large artwork causing text overlap.
# NEVER use BLANK layouts for content slides — always use TITLE_10.

# IMPORTANT: Remove template example slides before saving.
# Delete slides from the end backward to avoid index shifting.
```

### Applying Fonts Programmatically

```python
from pptx.util import Pt
from pptx.dml.color import RGBColor

# Title
run.font.name = 'Jost ExtraBold'
run.font.size = Pt(48)
# No explicit color needed — inherits from theme (dark purple)

# Body text
run.font.name = 'Quicksand'
run.font.size = Pt(22)
run.font.color.rgb = RGBColor(0x3B, 0x34, 0x47)

# Section heading
run.font.name = 'Jost'
run.font.size = Pt(26)
run.font.bold = True
run.font.color.rgb = RGBColor(0x3B, 0x34, 0x47)

# Graph title
run.font.name = 'Jost'
run.font.size = Pt(20)
run.font.color.rgb = RGBColor(0x3B, 0x34, 0x47)

# Table header
run.font.name = 'Proxima Nova'
run.font.size = Pt(20)
```

---

## Extracted Brand Assets

Pre-extracted from the template PPTX for programmatic use:

| Asset | File | Size | Usage |
|-------|------|------|-------|
| **MGO Logo** | `.knowledge/templates/assets/mgo_logo.png` | 7.40" x 3.70" | Cover slide — top-right |
| **MGO Brand Mark** | `.knowledge/templates/assets/mgo_brand_mark.png` | ~2.11" x 0.50" | Content slides — top-right corner |
| **MGO Artwork** | `.knowledge/templates/assets/mgo_artwork.png` | 8.80" x 8.80" | Cover slide — left background |
| **AI Badge (Logo)** | `.knowledge/templates/assets/ai_powered_badge.png` | 440x260px | Cover/intro slides — MGO logo + analytics icon + "AI POWERED / ANALYSIS" |
| **AI Badge (Artwork)** | `.knowledge/templates/assets/ai_powered_badge_v2.png` | 440x220px | Cover/intro slides — Mr. Monopoly + analytics icon + "AI POWERED / ANALYSIS" |

### Brand Mark Placement on Content Slides

Every content slide (not cover, not section divider) must include the MGO brand mark
in the top-right corner:

```python
from pptx.util import Inches

BRAND_MARK = '.knowledge/templates/assets/mgo_brand_mark.png'

# Place on every content slide — top-right corner
# Position matches the template's Layout 22 (TITLE_ONLY)
slide.shapes.add_picture(
    BRAND_MARK,
    left=Inches(17.4),   # right-aligned
    top=Inches(0.5),     # top margin
    width=Inches(2.11),  # original size — do NOT scale
    height=Inches(0.50),
)
```

---

## Required Elements

Every deck MUST include:
1. **Cover slide** — Title, point of contact, date. Use layout 0 (TITLE).
2. **Brand mark** — On every content slide, top-right corner (mgo_brand_mark.png, 2.11" x 0.50")
3. **Traffic light badge** — On performance reads and exploration decks
4. **Source attribution** — On every slide with data ("Source Data: ...")
5. **Creator attribution** — Name and date on cover
6. **Numbered sections** — Match the deck type structure above

## Image Placement Rules

1. **No text-over-image overlap.** No text element may sit on top of any
   image. If an image is placed on a slide, all text must be positioned in
   a separate region with no bounding-box overlap.
2. **Content slides use brand mark only.** Only `mgo_brand_mark.png` (small,
   2.11" x 0.50", top-right corner) is placed on content slides. Do NOT
   place `mgo_artwork.png` or `mgo_logo.png` on content slides — they are
   large background/decorative images that conflict with text.
3. **Cover slide images are optional.** The MGO artwork and logo may appear
   on the cover slide only if they do not overlap with the title or subtitle
   text. When building programmatically, omit them to avoid layout conflicts.
4. **Chart images must not overlap text.** When inserting chart PNGs, ensure
   the chart bounding box does not intersect any textbox. Leave at least
   0.2" clearance between image and text edges.
