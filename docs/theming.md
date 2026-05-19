# Theming Guide

AI Analyst uses a YAML-driven theme system for consistent, branded visualizations.
Themes control colors, typography, chart styling, and presentation defaults.

## Architecture

```
themes/
├── _base.yaml              # Default theme (always loaded first)
├── README.md               # Theme directory overview
├── analytics.css           # Marp theme for presentations (light mode)
├── analytics-dark.css      # Marp theme for presentations (dark mode)
├── analytics-light.css     # Marp theme alias
└── brands/
    ├── example/            # Reference theme (Acme Corp — teal/coral)
    │   ├── theme.yaml
    │   └── README.md
    └── monopoly-go/        # Active brand theme (MGO — purple/gold)
        ├── theme.yaml
        └── README.md
```

**Inheritance model:** Brand themes inherit from `_base.yaml` via deep merge.
Only override what you need — everything else falls back to the base theme.

## Base Theme Schema

The base theme (`themes/_base.yaml`) defines six top-level sections:

### `theme` — Metadata
```yaml
theme:
  name: "analytics"
  display_name: "Analytics (Default)"
  version: "1.0"
  description: "Clean, professional analytics theme based on SWD methodology"
```

### `colors` — Color Palettes

```yaml
colors:
  primary: "#4878CF"        # Key data, call-to-action
  secondary: "#6ACC65"      # Positive, growth
  accent: "#D65F5F"         # Alerts, negative, emphasis
  neutral: "#B0B0B0"        # Supporting, context
  background: "#F7F6F2"     # Chart/slide background
  text: "#333333"           # Body text
  text_light: "#666666"     # Captions, annotations

  categorical:              # Up to 8 distinct series colors (colorblind-safe)
    - "#4878CF"             # blue
    - "#6ACC65"             # green
    - "#B47CC7"             # purple
    - "#D65F5F"             # red
    - "#C4AD66"             # gold
    - "#77BEDB"             # light blue
    - "#D68E5C"             # orange
    - "#8C8C8C"             # gray

  sequential:               # Low-to-high gradient (for heatmaps, density)
    low: "#E8F4FD"
    mid: "#4878CF"
    high: "#1A3A6C"

  diverging:                # Negative/neutral/positive (for variance, change)
    negative: "#D65F5F"
    neutral: "#F7F6F2"
    positive: "#6ACC65"

  highlight:                # For SWD highlight_bar/highlight_line
    focus: "#4878CF"        # Draw attention to key data
    comparison: "#B0B0B0"   # De-emphasize supporting data
    alert: "#D65F5F"        # Flag problems or outliers
```

**Colorblind safety:** The default categorical palette avoids adjacent red-green
pairs. When creating brand themes, test with a colorblind simulator.

### `typography` — Font Settings
```yaml
typography:
  font_family: "Helvetica Neue, Helvetica, Arial, sans-serif"
  heading_font: "Helvetica Neue, Helvetica, Arial, sans-serif"
  monospace_font: "SF Mono, Menlo, Consolas, monospace"
  sizes:
    title: 18
    subtitle: 14
    body: 11
    caption: 9
    annotation: 9
    axis_label: 10
    tick_label: 9
  weights:
    title: "bold"
    subtitle: "normal"
    body: "normal"
    emphasis: "bold"
```

### `charts` — Matplotlib Defaults
```yaml
charts:
  figure:
    figsize: [10, 6]
    dpi: 150
    facecolor: "#F7F6F2"
  axes:
    facecolor: "#F7F6F2"
    grid: false
    spines:
      top: false
      right: false
      bottom: true
      left: true
    spine_color: "#CCCCCC"
  bar:
    default_color: "#B0B0B0"    # Context bars
    highlight_color: "#4878CF"  # Story bar
    edge_width: 0
  line:
    default_color: "#B0B0B0"    # Context lines
    highlight_color: "#4878CF"  # Story line
    width: 2.0
    highlight_width: 2.5
  annotations:
    font_size: 9
    color: "#333333"
    arrow_color: "#666666"
```

### `presentations` — Slide Defaults
```yaml
presentations:
  slide_background: "#FFFFFF"
  slide_text: "#333333"
  slide_accent: "#4878CF"
  dark:
    slide_background: "#1E1E2E"
    slide_text: "#CDD6F4"
    slide_accent: "#89B4FA"
```

### `export` — Output Settings
```yaml
export:
  chart_format: "png"
  chart_dpi: 150
  chart_bbox: "tight"
  chart_transparent: false
```

## Active Brand Theme: Monopoly GO!

The project uses the `monopoly-go` brand theme at `themes/brands/monopoly-go/`.
It overrides the base theme with the official MGO Data & Insights palette.

### Key overrides

| Field | Base (analytics) | MGO |
|---|---|---|
| `colors.primary` | `#4878CF` blue | `#3B3447` dark purple |
| `colors.secondary` | `#6ACC65` green | `#DBC585` gold |
| `colors.accent` | `#D65F5F` red | `#DF2728` alert red |
| `colors.background` | `#F7F6F2` off-white | `#FFFFFF` white |
| `typography.font_family` | Helvetica Neue | Quicksand |
| `typography.heading_font` | Helvetica Neue | Jost ExtraBold |
| `charts.bar.highlight_color` | `#4878CF` blue | `#3B3447` dark purple |
| `presentations.slide_accent` | `#4878CF` blue | `#DBC585` gold |

### MGO categorical palette (chart series order)
1. `#3B3447` — dark purple (primary)
2. `#DBC585` — gold
3. `#CE9AFF` — light purple
4. `#63D200` — success green
5. `#DF2728` — alert red
6. `#625C45` — olive brown
7. `#CACACA` — medium gray (reference)

### MGO-specific extras
The MGO theme adds a `functional` color block not in the base schema:
```yaml
colors:
  functional:
    cream: "#F8F5E5"          # Callout fills
    light_green: "#B3E4BF"    # Subtle positive indicators
    off_white: "#F7F6F3"      # Card backgrounds
    highlight_blue: "#26BEF7" # Interactive elements
    section_text: "#43384F"   # Section divider text
```

Source: `.knowledge/templates/design-system.md`

## Creating a Brand Theme

### 1. Create the directory
```bash
mkdir -p themes/brands/your-org
```

### 2. Create `theme.yaml`

Only override what differs from `_base.yaml`:

```yaml
# themes/brands/your-org/theme.yaml
theme:
  name: "your-org"
  display_name: "Your Org Analytics"

colors:
  primary: "#1B4D89"
  secondary: "#2EAD6D"
  accent: "#E87C3E"
  categorical:
    - "#1B4D89"
    - "#E87C3E"
    - "#2EAD6D"
    - "#8B5CF6"
    - "#F59E0B"
    - "#06B6D4"
    - "#EC4899"
    - "#6B7280"
  highlight:
    focus: "#1B4D89"
    comparison: "#B0B0B0"
    alert: "#E87C3E"

typography:
  font_family: "Inter, sans-serif"
```

### 3. Add a README (optional)
Document the palette, fonts, and source (brand guidelines, style guide, etc.).

### 4. Activate
Set in your dataset manifest or pass at runtime:
```yaml
theme: your-org
```

## Using Themes in Code

### Loading a theme
```python
from helpers.theme_loader import load_theme, get_color

# Load base theme
theme = load_theme()

# Load brand theme (merges on top of base)
theme = load_theme("monopoly-go")

# Access colors (supports dot notation)
primary = get_color(theme, "colors.primary")
```

### Applying to charts
```python
from helpers.chart_helpers import swd_style, highlight_bar
from helpers.chart_palette import apply_theme_colors

theme = load_theme("monopoly-go")
apply_theme_colors(theme)

fig, ax = highlight_bar(
    data, x="category", y="value",
    highlight="Target Category"
)
```

### Using the palette
```python
from helpers.chart_palette import (
    highlight_palette, categorical_colors, palette_for_n
)

highlights = highlight_palette(theme)   # focus, comparison, alert
colors = categorical_colors(theme)      # up to 8 series
colors = palette_for_n(theme, n=12)     # extended via interpolation
```

### Chart-level theme application
```python
from helpers.chart_helpers import swd_style

swd_style(theme="monopoly-go")

# All charts in this session use MGO colors
fig1, ax1 = highlight_bar(data1, x="a", y="b", highlight="Target")
fig2, ax2 = highlight_line(data2, x="date", y="metric", highlight="2024-Q4")
```

## WCAG Compliance

All theme colors should meet WCAG 2.1 AA contrast requirements:

- **Text on background:** Minimum 4.5:1 contrast ratio
- **Large text on background:** Minimum 3:1 contrast ratio
- **UI components:** Minimum 3:1 contrast ratio

```python
from helpers.chart_palette import ensure_contrast

text_color = ensure_contrast(
    foreground="#3B3447",
    background="#FFFFFF",
    min_ratio=4.5
)
```

Test with: [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
or [Coblis Colorblind Simulator](https://www.color-blindness.com/coblis-color-blindness-simulator/)

## Theme System Files

| File | Purpose |
|---|---|
| `themes/_base.yaml` | Default theme definition |
| `themes/brands/monopoly-go/theme.yaml` | Active MGO brand overrides |
| `themes/brands/example/theme.yaml` | Reference brand (Acme Corp) |
| `helpers/theme_loader.py` | Theme loading, caching, deep merge |
| `helpers/chart_palette.py` | Palette generation, contrast checking |
| `helpers/chart_helpers.py` | Chart creation with theme integration |
| `themes/analytics.css` | Marp presentation theme (light) |
| `themes/analytics-dark.css` | Marp presentation theme (dark) |
| `.knowledge/templates/design-system.md` | MGO deck template spec (source of truth) |

## Troubleshooting

**Charts not picking up theme colors:**
- Ensure `swd_style(theme="monopoly-go")` is called before creating figures
- Check that `themes/brands/monopoly-go/theme.yaml` exists
- Theme name must match directory name exactly (case-sensitive)

**Font not rendering:**
- Install Jost and Quicksand on the system, or use fallbacks
- Clear matplotlib font cache: `rm -rf ~/.matplotlib/fontlist-*.json`
- MGO fallbacks: Jost -> Montserrat -> Arial Bold; Quicksand -> Open Sans -> Calibri

**Theme changes not appearing:**
- Clear cache: `from helpers.theme_loader import clear_cache; clear_cache()`
- Restart the Python session (cache is in-memory)

**Categorical palette runs out of colors:**
- Use `palette_for_n(theme, n=12)` for extended palettes
- Simplify the visualization or use small multiples

## See Also

- `themes/README.md` — Theme directory overview
- `themes/brands/monopoly-go/README.md` — MGO palette quick reference
- `helpers/chart_style_guide.md` — SWD chart methodology
- `.claude/skills/visualization-patterns/skill.md` — Visualization best practices
- `.claude/skills/presentation-themes/skill.md` — Deck theming guide
