# Skill: Season (Album) Comparison

## When to Apply

Trigger this skill whenever the user asks about:
- Season-over-season comparison, album comparison
- "How does this album compare to the last one?"
- RTP by season, balance by album, sink per user across albums
- Progression-normalized comparisons

## Core Concept

Seasons in MGO are defined by **albums** (from `DM.dim_album`). Each album has a start_date and end_date. The key challenge: albums have different lengths, so you must normalize comparisons.

**Two comparison modes:**
1. **Same progression %**: Compare albums at the same % of completion (e.g., both at 40% through)
2. **Full season**: Compare completed albums end-to-end (current season is incomplete)

## Album Metadata

```sql
SELECT album_id, album_name, start_date, end_date
FROM `dwh-prod-tophat.DM.dim_album`
WHERE SAFE_CAST(prestige AS INT64) = 0  -- only base albums
  AND lower(album_id) NOT LIKE '%tsl%'
  AND lower(album_id) != 'syrupbonusset1'
ORDER BY start_date DESC
```

## Current Album Detection

```sql
SELECT album_name, start_date, end_date,
    DATE_DIFF(CURRENT_DATE(), DATE(start_date), DAY) / 
    NULLIF(DATE_DIFF(DATE(end_date), DATE(start_date), DAY), 0) AS days_passed_share
FROM `dwh-prod-tophat.DM.dim_album`
WHERE CURRENT_DATE() BETWEEN start_date AND end_date
  AND lower(album_id) NOT LIKE '%tsl%'
  AND lower(album_id) != 'syrupbonusset1'
LIMIT 1
```

## Progression-Normalized Comparison Pattern

For fair comparison, limit all albums to the same progression % as the current album's age:

```sql
-- For each album, only include days where:
DATE_DIFF(DATE(transaction_date), DATE(album.start_date), DAY) / 
DATE_DIFF(DATE(album.end_date), DATE(album.start_date), DAY) 
<= (current album's days_passed_share)
```

This means if the current album is 60% through, only compare the first 60% of older albums.

## Season RTP Comparison Query Structure

1. Define target albums (current + comparison picks)
2. Compute date bounds for partition pruning
3. Pre-filter KPI (active users, segment filter, cheater exclusion)
4. Join `fac_sinks_n_sources` with source classifier and album windows
5. Aggregate source/sink by album and l1_vertical
6. Compute RTP = source_val / sink_val per (album, vertical)

## Segment Filter

The dashboard supports filtering by player segment (LP, RC, Regular, ROP) for season comparison. This uses:

```sql
CASE
    WHEN v_f_user_rpt.is_loyal_payer THEN '3.LP'
    WHEN v_f_user_rpt.is_regular_customer THEN '2.RC'
    WHEN v_f_user_rpt.is_regular THEN '1.Regular'
    ELSE '0.ROP'
END IN ({segment_filter})
```

## Source per User by Season

A key decomposition: `SUM(source_val) / SUM(sink_users)` gives source per active user per vertical.

## Sink per User by Season

`SUM(sink_val) / SUM(sink_users)` gives engagement intensity.

## Presentation Standards

- Bar charts with albums on x-axis, colored by vertical
- Side-by-side: "RTP comparison same progress %" vs "Full season comparison"
- Line charts for progression-% curves (x = album progress 0-100%, y = RTP or balance, colored by album)
- Always note which albums are complete vs. in-progress
- When current season is included, annotate that it's partial data

## Known Recent Albums

(From the dashboard dropdowns as of the YAML snapshot):
PetsAlbum, ButterAlbum, CozyComfortsAlbum, BonAppetit2025, SummerEscape2025, HotDogAlbum2025, MovieNight2025
