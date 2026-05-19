# Analysis Workflow

## Phase 1: One-Pager (BEFORE any analysis begins)

Every analysis must start with a one-pager document that is shared/approved before any queries are run. The one-pager includes:

### Required Sections
1. **Title & Point of Contact** — Analysis name, analyst, date, stakeholder(s)
2. **Background & Context** — Why this analysis is needed, what triggered it
3. **Product Questions** — The specific questions this analysis will answer (numbered list)
4. **Hypotheses** — What we expect to find and why (each tied to a product question)
5. **Methodology** — How we plan to answer each question:
   - Data sources / tables
   - Population definition & filters
   - Metrics & their definitions
   - Segmentation approach
   - Time windows
   - Statistical methods (if applicable)
6. **Success Criteria** — What would a "clear answer" look like for each question
7. **Scope & Limitations** — What this analysis will NOT cover, known data gaps
8. **Timeline** — Expected delivery date

### One-Pager Rules
- Must be reviewed before analysis starts
- Product questions drive the entire analysis — everything flows from them
- Hypotheses are not conclusions — they are testable statements
- If during analysis you need to deviate from the plan, update the one-pager first

---

## Phase 2: Analysis Execution

Follow the methodology in `analysis_standards.md` and `manager_directives.md`.

---

## Phase 3: Deliverables Folder

When the analysis is complete, ALL artifacts must be organized in a single folder. The folder should contain:

### Required Contents
1. **One-Pager** — The original scoping document (with any updates noted)
2. **Deck / Report** — Following the deck template structure from `deck_template.md`
3. **SQL Queries** — All queries used, documented with comments explaining what each does
4. **Hex Project** — Link to the Hex notebook (or the notebook itself if delivered outside Hex)
5. **Data Sources** — Links to any spreadsheets, Looker dashboards, or external data used
6. **GDD / Test Details** — Link to the relevant GDD, Playgami console, or test configuration (if AB test)
7. **Supporting Materials** — Any additional context docs, prior analysis references, stakeholder inputs

### Folder Naming Convention
`[YYYY-MM-DD] - [Analysis Title] - [Status]`

Example: `2026-05-10 - Reactivation D7 Lever Analysis - Green Check`

### Delivery
- Primary platform: **Hex** (all deliverables go into Hex when possible)
- Fallback: Web page exportable/downloadable as PDF
- Share with stakeholders AND #tophat_analytics_internal
