# Monopoly GO! Brand Theme

Official analytics theme for Monopoly GO!, extracted from the MGO Data & Insights
Deck Template (May 2025).

## Palette

| Color | Hex | Role |
|---|---|---|
| Dark Purple | `#3B3447` | Primary text, headings, key chart series |
| Accent Gold | `#DBC585` | Highlights, accents, secondary series |
| Light Purple | `#CE9AFF` | Tertiary series, differentiation |
| Success Green | `#63D200` | Positive metrics |
| Alert Red | `#DF2728` | Negative metrics, warnings |
| Olive Brown | `#625C45` | Muted accent, captions |
| Medium Gray | `#CACACA` | Borders, reference lines, context |
| Warm Cream | `#F8F5E5` | Callout fills, light backgrounds |

## Typography

- **Titles:** Jost ExtraBold (48pt slide titles, 80pt cover/section)
- **Body:** Quicksand Regular (22pt standard, 18pt dense)
- **Tables:** Proxima Nova (20pt)
- **Fallbacks:** Jost -> Montserrat -> Arial Bold; Quicksand -> Open Sans -> Calibri

## Usage

Set as active theme in your dataset manifest:

```yaml
theme: monopoly-go
```

Or pass at runtime when invoking chart/deck agents.

## Source

Design system: `.knowledge/templates/design-system.md`
Template PPTX: `.knowledge/templates/Copy of Monopoly GO! Data & Insights Deck Template - May 2025.pptx`
