---
name: data-inspect
description: |
  Show dataset schema, tables, columns, and list all connected datasets. Handles `/data`, `/data {table}`, and `/datasets`. Trigger on "what tables?", "show schema", "what datasets?", "list datasets", "what data?", "show me my data sources", or any request to inspect/browse data structure or see available datasets.
---

# Skill: Data Inspect

## Purpose
Show the active dataset's schema — tables, columns, row counts, and relationships. Optionally drill into a specific table.

## When to Use
Invoke as `/data` to see the full schema summary, or `/data {table}` to see column details for a specific table.

## Instructions

### CRITICAL: Always Start Here

**Before doing ANYTHING else:**
1. Read `.knowledge/active.yaml` to determine the active dataset name
2. If no active dataset exists, jump to Mode 3 (No Active Dataset)
3. Otherwise, read `.knowledge/datasets/{active}/schema.md` for schema information

**Why this matters:** Users often have multiple datasets connected. You MUST use the active one from the config file, never guess or use a different dataset.

---

### Mode 1: `/data` (full schema overview)

**When:** User invokes `/data` or asks "what tables do I have?" / "show me the schema"

**Steps:**
1. ✅ Confirm you've already read `.knowledge/active.yaml` and `schema.md` (see above)
2. Extract from schema.md:
   - Dataset display name
   - Connection type and location
   - Table list with: name, row count, column count, primary key
3. Display in this condensed format:

```
Active Dataset: {display_name}
Connection: {type} ({database}.{schema} or file path)

Tables:
  users          ~50,000 rows   8 columns   user_id (PK)
  products           500 rows   7 columns   product_id (PK)
  events        ~6.5M rows     9 columns   event_id (PK)
  sessions       ~1.4M rows    8 columns   session_id (PK)
  orders        ~30-50K rows   6 columns   order_id (PK)
  order_items         — rows   4 columns   order_id + product_id (composite PK)

Use `/data {table}` for column details.
```

**Format notes:**
- Left-align table names
- Show approximate row counts (use `~` for estimates)
- Show column count
- Show primary key or composite key
- Keep it visually scannable — this is a quick reference, not exhaustive detail

---

### Mode 2: `/data {table}` (table detail)

**When:** User invokes `/data {table}` or asks "what columns are in X?" / "show me the X table structure"

**Steps:**
1. ✅ Confirm you've already read `.knowledge/active.yaml` and `schema.md` (see above)
2. Find the section for the requested table in schema.md
3. **If table doesn't exist:** Jump to Mode 4 (Table Not Found)
4. **If table exists:** Display:
   - Table name and description
   - Row count
   - Full column listing: name, type, nullable, description
   - Primary key(s)
   - Foreign key relationships (both FROM this table and TO this table)
   - Any important notes about the table (grain, completeness, quirks)

**Format example:**
```
Active Dataset: NovaMart
Table: users

Description: User dimension table with demographics and signup info

Row count: ~25,000 rows
Primary Key: user_id

Columns:
  user_id          BIGINT       NOT NULL    Unique user identifier
  email            VARCHAR      NOT NULL    User email address
  signup_date      DATE         NULL        Date user first registered
  country          VARCHAR      NULL        User's country
  membership_tier  VARCHAR      NULL        Premium, Standard, Free

Relationships:
  ← orders.customer_id          (one user, many orders)
  ← events.user_id              (one user, many events)
  → memberships.user_id         (join for membership details)

Use `/data {another_table}` to inspect another table.
```

---

### Mode 3: No Active Dataset

**When:** `.knowledge/active.yaml` has no `active_dataset` field OR the dataset directory doesn't exist

**Display:**
```
No active dataset configured.

To get started:
• Run `/connect-data` to connect a new dataset
• Run `/datasets` to see all available datasets
• Run `/switch-dataset {name}` to activate an existing dataset
```

**Do NOT:** Try to query databases, load CSV files, or guess which data source to use. Without an active dataset, halt and prompt the user.

---

### Mode 4: Table Not Found

**When:** User requests `/data {table}` but the table doesn't exist in the active dataset's schema.md

**Steps:**
1. Confirm the table truly doesn't exist (check schema.md thoroughly, look for typos/case differences)
2. Display a helpful error message:

```
Table '{table}' not found in {dataset_name}.

Available tables:
  users, orders, products, events, sessions

Did you mean:
• /data {closest_match}
• /switch-dataset {other_dataset} if you're looking for different data
• /connect-data if the table should exist but isn't loaded

Use `/data` to see the full schema.
```

**Do NOT:** Query databases or try to load data from other sources. The skill reads from cached schema files only.

---

### Mode 5: `/datasets` (list all connected datasets)

**When:** User invokes `/datasets` or asks "what datasets do I have?" / "list datasets" / "show my data sources"

**Steps:**
1. Check `data_sources.yaml` for registered sources; if empty, scan `.knowledge/datasets/` directories
2. Read `.knowledge/active.yaml` for the active dataset pointer
3. For each dataset, read `.knowledge/datasets/{name}/manifest.yaml` for: display_name, connection type, table_count, date_range
4. Display:

```
Connected Datasets:

  * your_dataset (active)
    Your Dataset Name — {table_count} tables, {date_range}
    Connection: {type} ({database})

  - {other_dataset}
    {display_name} — {table_count} tables
    Connection: {type} ({details})

Commands:
  /switch-dataset {name}  — switch active dataset
  /connect-data           — connect a new dataset
  /data                   — inspect active dataset schema
```

Mark the active dataset with `*`. Never display credentials.

---

## Anti-Patterns

1. **Never query the database just to show schema** — read from the cached schema.md file for speed. Schema files are pre-generated during dataset connection and profiling.

2. **Never show the full schema.md raw** — always format into the condensed table view. Users want quick scannable reference, not walls of markdown.

3. **Never guess which dataset to use** — ALWAYS read `.knowledge/active.yaml` first. Do not load data from other directories like `data/sales/` or `data/practice/` unless that's explicitly what active.yaml points to.

4. **Never query actual data** — this skill shows structure only (schema, relationships). For data exploration, use the `/explore` skill or Data Explorer agent.

5. **Never fabricate table information** — if schema.md doesn't have row counts, say "~rows not profiled". If descriptions are missing, show what's available. Don't make up details.
