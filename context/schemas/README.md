# BigQuery Schemas

This directory contains schema documentation for every BigQuery table the analyst queries.

## How to Add a Schema

For each table, create a file named after the table (e.g., `player_activity.md`) with:

```markdown
# dataset.table_name

## Description
What this table contains, how often it's updated, what grain it's at (one row per user per day? per event?).

## Schema
| Column | Type | Description |
|--------|------|-------------|
| user_id | STRING | Unique player identifier |
| event_date | DATE | Partition key, date of activity |
| ... | ... | ... |

## Partitioning & Clustering
- Partitioned by: event_date
- Clustered by: user_id, activity_segment

## Common Joins
- Joins to `other_table` on `user_id`
- Joins to `experiment_assignments` on `user_id` + `date`

## Row Count / Size
- ~X rows per day
- Total size: ~Y TB

## Gotchas
- Any known issues, delays, quirks
```

## How to Export Schemas

Run this in your terminal for each key table:
```bash
bq show --schema --format=prettyjson project:dataset.table_name
```

Or from the BigQuery console: open the table → Schema tab → copy the column definitions.

## Priority Tables to Document

The analyst needs schemas for tables covering:
1. **Player activity** (DAU, sessions, playtime)
2. **Revenue / transactions** (purchases, ARPDAU)
3. **Retention** (cohort tables or event-based)
4. **Experiments** (assignment + exposure tables)
5. **Segments** (activity segment, tenure, geo assignment)
6. **Game events** (rolls, board progression, feature participation)
7. **Social** (friends, social score, ASN)
8. **Economy** (rolls/cash earn and spend)
9. **Reactivation** (churn/return tracking)
10. **Albums / stickers** (collection progress)
