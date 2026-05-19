---
name: explore
description: |
  Quick, interactive data exploration without the full pipeline. Use this skill whenever a user wants to explore data, understand what's in a dataset, browse tables or columns, check data distributions, spot patterns, or get familiar with data before analysis. Trigger on phrases like "/explore", "let me explore the data", "what's in this dataset?", "show me what data we have", "browse the data", "what tables are available?", "what columns does X have?", "show me a sample of the data", "what does the distribution look like?", "explore this table", or any request to understand data structure, contents, or patterns before diving into formal analysis. This is especially important after connecting a new dataset or when the user wants to poke around without committing to a specific analytical question yet.
---

# Skill: Explore Data

## Purpose
Quick, interactive data exploration without the full pipeline. Lets users
poke around the active dataset — preview tables, check distributions, spot
patterns, and form hypotheses before committing to a formal analysis.

## When to Use
- User says `/explore` or "let me explore the data" or "what's in this dataset?"
- After connecting a new dataset, before any formal analysis
- When the user wants to understand data shape without a specific question

## Invocation
`/explore` — explore the active dataset
`/explore {table}` — focus on a specific table
`/explore {table} {column}` — deep-dive into a specific column

## Instructions

### Step 1: Load Context (with Fallback)

**Try to load formal context first:**
1. Check if `.knowledge/active.yaml` exists
2. If yes, read it to identify the active dataset name
3. Read `.knowledge/datasets/{active}/schema.md` for table/column reference
4. Read `.knowledge/datasets/{active}/quirks.md` for known gotchas

**If .knowledge/ files don't exist (common for new users), fall back:**
1. Look for data in these locations (in order):
   - `data/practice/*.csv` (practice datasets)
   - `data/examples/*.csv` (example datasets)
   - `tests/fixtures/*.csv` (test data)
2. Use the first location where data is found
3. Infer schema by reading a sample of the data
4. Proceed with exploration using discovered data

**If no data found anywhere:**
- Prompt: "No dataset found. Use `/connect-data` to add one, or point me to your data files."
- Do NOT proceed with hypothetical exploration

### Step 2: Choose Exploration Mode

**Mode A: Dataset overview** (no table specified)

Goal: Give the user a mental map of what data exists and what questions they can answer.

Deliver:
1. **List all tables** with row counts and date ranges (if temporal data exists)
2. **Highlight 3-5 most analytically useful tables** based on:
   - Row count (more rows = more statistical power)
   - Temporal coverage (wider date ranges enable trend analysis)
   - Join potential (foreign keys connecting tables)
3. **Show entity relationships** (e.g., customers → orders → products)
4. **Suggest 3 starting questions** that are:
   - Specific to this dataset (use actual table/column names)
   - Answerable with available data
   - Business-relevant (revenue, conversion, retention, segments)

**Mode B: Table exploration** (table specified)

Goal: Help the user understand one table's structure, quality, and analytical potential.

Deliver:
1. **Column list** with data types and null rates
2. **5 random sample rows** to show actual data
3. **Summary statistics by column type:**
   - Numeric: min, max, mean, median
   - Categorical: top 5 values with counts
   - Date: earliest, latest, coverage (% of days with data)
4. **Quality flags** - Report ANY of these issues:
   - Columns with >5% nulls (specify which columns and %)
   - Low cardinality categoricals (only 1-2 unique values)
   - Suspicious values (negatives where impossible, future dates, outlier extremes)
   - Data type mismatches (dates stored as strings)
5. **Analytical potential** - What analyses would this table support?

**Mode C: Column deep-dive** (table + column specified)

Goal: Understand the distribution, quality, and business meaning of one column.

Deliver:
1. **Full distribution visualization:**
   - Numeric: histogram with SWD styling (use `swd_style()`)
   - Categorical: horizontal bar chart (top 10-20 values, SWD styled)
   - Date: coverage heatmap by week
2. **Null analysis:**
   - Null count and percentage
   - Pattern: random (scattered) vs systematic (clustered in time/segments)
3. **Outlier detection (numeric only):**
   - Use IQR method (values > Q3 + 1.5*IQR or < Q1 - 1.5*IQR)
   - Report count, range, and business plausibility
   - Flag if outliers represent >10% of data (unusual)
4. **Business context:**
   - What does this column measure?
   - What's a "normal" value vs an extreme?
   - Revenue impact if this metric improves/degrades
5. **Related columns for cross-analysis** - Suggest 2-3 other columns to slice/segment by

### Step 3: Interactive Follow-Up

After presenting results, ALWAYS offer 2-3 **specific, actionable** next steps.

Good examples (use actual names from the data):
- "Want to see how {column} varies by {dimension}?" (segmentation)
- "Orders show a 9.5% cancellation rate. Want to investigate root causes?"
- "You have high-value outliers (>$500 orders). Want to profile that customer segment?"
- "This funnel data looks ready for conversion analysis. Run `/run-pipeline`?"

Avoid generic suggestions like "Want to analyze more?" — make them specific to findings.

### Step 4: Save Exploration Notes (CRITICAL)

After completing exploration, **always** write a summary file to `working/explore_notes_{YYYYMMDD}.md`.

Include:
- **Tables examined:** List with timestamps
- **Key observations:** 3-5 bullet points of most important findings
- **Quality flags:** List any blockers or warnings discovered
- **Suggested next steps:** Copy the interactive suggestions from Step 3

**Why this matters:** Subsequent agents (Question Framing, Hypothesis Generation, Data Explorer) can read these notes to avoid redundant work and build on your findings.

**Format:**
```markdown
## Tables Examined
- {table_name} (explored {date})

## Key Observations
- {observation 1}
- {observation 2}

## Quality Flags
- ⚠️ {issue description}
- ✅ {positive finding}

## Suggested Next Steps
1. {suggestion 1}
2. {suggestion 2}
```

## Rules

1. **Keep it fast** — No more than 3-4 queries per exploration step. Users want speed, not exhaustive profiling.

2. **Always apply `swd_style()`** if generating any chart. Call it BEFORE creating the chart.

3. **Never modify data** during exploration. Read-only operations only.

4. **Always cite table and column names** in output. Users need to know what you're referencing.

5. **Mention data source explicitly** - Tell the user where data came from:
   - "Using data from data/practice/ (local CSV files)"
   - "Connected to MotherDuck database"
   - "Reading from {specific file path}"

6. **Use actual data** - Never provide hypothetical/generic exploration. If data doesn't exist, say so clearly and stop.

## Edge Cases

- **Empty table (0 rows):** Report row count = 0, suggest checking data load process, do NOT attempt distribution analysis

- **Table not found:** Use fuzzy matching to suggest closest match:
  - User typed "order" → suggest "orders" or "order_items"
  - Show available table names to help user correct

- **Column has 100% nulls:** Flag as BLOCKER, suggest checking data pipeline, do NOT attempt distribution analysis

- **Very wide table (>50 columns):** Group columns by semantic category (IDs, metrics, dimensions, dates), show summary counts per category instead of listing all 50+

- **Date column stored as VARCHAR/text:** Flag in quality section, remind user to cast as `::DATE` or `CAST(... AS DATE)` in SQL queries

- **Mixed data sources:** If some tables are in DuckDB and others are CSVs, mention this explicitly so user understands why queries might behave differently
