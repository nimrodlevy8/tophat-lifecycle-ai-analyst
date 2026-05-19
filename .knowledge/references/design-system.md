# MGO Analytics Design System

Extracted from team slide decks. Apply these standards to all charts,
presentations, and visual artifacts produced by this tool.

---

## Slide Dimensions

| Context | Size | Notes |
|---------|------|-------|
| Standard presentation | 20" × 11.2" (widescreen 16:9) | All formal readouts and analyses |
| Compact / Google Slides | 10" × 5.6" | Half-size variant, same aspect ratio |

---

## Typography

### Font Stack

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| **Titles** | Jost ExtraBold | 800 | Slide titles, section headers, cover titles |
| **Subtitles** | Jost / Jost SemiBold | 400-600 | Sub-headers, graph titles, variant labels |
| **Body** | Quicksand / Quicksand Medium | 400-500 | Bullet points, callouts, supporting text |
| **Cover metadata** | Proxima Nova | 400 | "Point of Contact" and "Date" on cover slides |

### Size Scale

| Element | Size (20" slides) | Size (10" slides) |
|---------|-------------------|-------------------|
| Cover title | 80pt | 56pt |
| Section divider title | 80pt | 38pt |
| Slide title | 46-48pt | 22-24pt |
| Subtitle / graph title | 26-32pt | 11-13pt |
| Body text / callouts | 20-26pt | 8-12pt |
| Supporting annotations | 16-18pt | 7-8pt |
| Data footnotes / filters | 10pt | 6pt |
| Summary body | 23-26pt | 12pt |

---

## Color Palette

### Primary Colors

| Hex | Name | Usage |
|-----|------|-------|
| `#3B3447` | **Dark Purple** | Primary text, graph titles, callout text |
| `#DBC585` | **Gold** | Primary accent, highlight, brand color |

### Draw Attention

| Hex | Name | Usage |
|-----|------|-------|
| `#DF2728` | **Red** | Alert, negative performance, attention |
| `#CE9AFF` | **Lavender** | Secondary accent, differentiation |

### Secondary Colors — Create Contrast

| Hex | Name | Usage |
|-----|------|-------|
| `#625C45` | **Dark Olive** | Secondary chart series, muted contrast |
| `#CACACA` | **Gray** | De-emphasized elements, gridlines, context series |

### Backgrounds

| Hex | Name | Usage |
|-----|------|-------|
| `#F7F6F3` | **Off-White** | Slide background (content slides) |
| `#F8F5E5` | **Cream** | Alternate background, warm tone |

### Positive / Status

| Hex | Name | Usage |
|-----|------|-------|
| `#B3E4BF` | **Light Green** | Positive indicator, background |
| `#63D200` | **Green** | Strong positive, completion, success |
| `#38761D` | **Dark Green** | Positive revenue headlines in weekly updates |

### Weekly Update Accent Colors

| Hex | Name | Usage |
|-----|------|-------|
| `#B45F06` | **Amber** | Cover slide date in weekly KPI decks |
| `#660000` | **Burgundy** | Section divider titles in weekly KPI decks ("KPIs", "Reactivations") |

### Annotation Colors

| Hex | Name | Usage |
|-----|------|-------|
| `#980000` | **Dark Red** | Percentage point annotations ("+8 ppt") |
| `#FF0000` | **Bright Red** | Important notes, warnings, follow-up items |
| `#595959` | **Medium Gray** | Chart labels, secondary text |
| `#000000` | **Black** | Data source footnotes |

---

## Chart Style Rules

When generating matplotlib/seaborn charts for MGO analytics:

1. **Apply SWD style first** (`swd_style()` from helpers), then override colors:
   - Primary series: `#3B3447` (dark purple)
   - Highlight / focus series: `#DBC585` (gold)
   - Alert / negative: `#DF2728` (red)
   - De-emphasized / context: `#CACACA` (gray)
   - Positive trend: `#63D200` (green)

2. **Font in charts**: Use the closest available system font to Quicksand
   for axis labels and annotations. Titles in bold weight.

3. **Annotation style**: Use `#980000` for percentage-point callouts
   (e.g., "+8 ppt") placed near the data point.

4. **Background**: White or `#F7F6F3` — never dark backgrounds in charts.

5. **Grid**: Light gray (`#CACACA`) horizontal gridlines only.

---

## Slide Layout Patterns

### Cover Slide
- Title: Jost ExtraBold 80pt, left-aligned
- Game art image: right side (~8.8" × 8.8")
- Monopoly GO logo: bottom-right (~7.4" × 3.7")
- "Point of Contact: {name}" in Proxima Nova 22pt
- "Date: {date}" in Proxima Nova 22pt

### Section Divider
- Title: Jost ExtraBold 80pt, centered or left
- Optional subtitle: Jost 27-43pt below title
- Optional game art background image
- Dark or branded background

### Content Slide
- Slide title: Jost ExtraBold 46-48pt, top-left
- Chart/image: large, ~13-16" wide
- Callouts: Quicksand Medium 16-21pt, color `#3B3447`
  - Key insight in bold (Quicksand Bold or Jost ExtraBold)
  - Supporting detail in regular weight
- Data footnote: bottom, Quicksand 10pt
  - Standard: "*data exd cheaters & internal" or "Excl. Cheaters and D30-"

### Summary Slide
- Title: "Summary" or "Executive Summary" in Jost ExtraBold
- Numbered findings: Jost Bold 26pt for headers, Quicksand 20-22pt for detail
- Key findings in bold, supporting context in regular

### Conclusion Slide
- Title: "Conclusion:" in Jost ExtraBold 80pt
- Finding text: Jost 43pt below
- Game art image right side

### Next Steps Slide
- Title: "Next Steps" or "Follow-ups Update"
- Categorized: "To do" / "Working on" / "Done" sections
- Items in Quicksand 21pt, completed items in bold

---

## Traffic Light System

Used to communicate confidence level of findings:

| Icon | Level | Meaning | When |
|------|-------|---------|------|
| Red question mark | Preliminary | Directional signal, not confirmed | Start of investigation |
| Orange hammer | Emerging | Likely cause identified, validation in progress | Mid-investigation |
| Green check | Confirmed | Robust findings, confident recommendation | Investigation complete |

*Indicates confidence in the insight, not whether the result is positive or negative.*

---

## Standard Data Footnotes

Always include at the bottom of content slides:
- `*data exd cheaters & internal` — short form
- `Excl. Cheaters and D30-, Including both completers and non-completers` — long form
- Specify segment filters if applicable

---

## Source Files

Reference decks stored at:
- `.knowledge/references/readouts/` — D1/D7 feature readout examples
- `.knowledge/references/analyses/` — deep-dive analysis examples
- `.knowledge/references/weekly-updates/` — exec weekly KPI meeting examples
