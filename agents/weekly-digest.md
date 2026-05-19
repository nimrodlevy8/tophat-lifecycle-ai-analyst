# Weekly Analytics Digest Agent

## Purpose
Generate a concise, executive-ready weekly summary email (as markdown) for
SVPs and executives, summarizing deliverables from two analytics verticals:
**New Minigame Vertical Analytics** (Alireza's team) and **LRK Vertical
Analytics** (Liz's team).

## When to Invoke
- Every week (typically Thursday/Friday), when the user provides links to
  that week's artifacts (Google Slides decks, Google Docs).
- User says `/weekly-digest` or "create the weekly summary".

## Inputs
| Variable | Description |
|----------|-------------|
| `{{LINKS}}` | List of Google Slides/Docs URLs provided by the user |
| `{{TEAM_MAPPING}}` | Which links belong to which team (user specifies, or infer from content) |
| `{{WEEK_OF}}` | Week label, e.g., "w/o Apr 14" (default: current Monday's date) |

## Workflow

### Step 1: Fetch Documents
For each link provided:
1. Extract the document ID from the URL.
   - Slides: `https://docs.google.com/presentation/d/{ID}/...` → ID
   - Docs: `https://docs.google.com/document/d/{ID}/...` → ID
2. Fetch content using the `gws` CLI:
   - **Slides:** `gws slides presentations get --params '{"presentationId":"ID"}' 2>/dev/null`
   - **Docs:** `gws docs documents get --params '{"documentId":"ID"}' 2>/dev/null`
3. Extract text using the helper scripts:
   - **Slides:** pipe through `python working/extract_slides_text.py`
   - **Docs:** pipe through `python working/extract_doc_text.py`
4. Use the actual Python path: `/c/Users/alireza.hamidi/AppData/Local/Programs/Python/Python314/python.exe`

### Step 2: Classify by Team
- If the user specifies which links belong to which team, use that.
- Otherwise, infer from content:
  - **New Minigame Vertical:** Minigame readouts (Coop, Racers, Adventures,
    Boutique, Carnival, etc.), health assessments, feature analyses for
    minigames. Contributors: Alireza Hamidi, Anna Zheng, Manuel Arroyo.
  - **LRK Vertical:** Go!Chat, Diminishing Returns, Storybooks, Pity Counter,
    economy tests, album-related work. Contributor: Liz and her team.

### Step 3: Summarize Each Artifact
For each document, extract:
1. **Project name** — from the title slide or document heading
2. **Point of contact** — from the cover slide or doc header
3. **Key findings** — 2-4 bullet points capturing the most executive-relevant
   insights. Focus on: what changed, by how much, what it means, what's
   recommended.
4. **Status** — shipped/in-progress/WIP if stated
5. **Link** — the original Google URL

### Step 3b: Extract Embedded Links (Docs only)
For Google Docs, also extract embedded hyperlinks using the JSON extractor:
```
gws docs documents get --params '{"documentId":"ID"}' 2>/dev/null | python -c "
import json, sys
data = json.load(sys.stdin)
body = data.get('body', {}).get('content', [])
def extract_links(elements):
    for el in elements:
        if 'paragraph' in el:
            for pe in el['paragraph'].get('elements', []):
                if 'textRun' in pe:
                    tr = pe['textRun']
                    link = tr.get('textStyle', {}).get('link', {}).get('url', '')
                    text = tr.get('content', '').strip()
                    if link and text:
                        print(f'{text} -> {link}')
        if 'table' in el:
            for row in el['table'].get('tableRows', []):
                for cell in row.get('tableCells', []):
                    extract_links(cell.get('content', []))
extract_links(body)
"
```
Inline these links into the summary where relevant (dashboards, Hex apps, etc.).

### Step 4: Draft the Email
Use this template structure:

```
**Subject: Weekly Analytics Digest -- Minigame Verticals ({{WEEK_OF}})**

---

Hi all,

Below is this week's summary from the **New Minigame Vertical Analytics**
and **LRK Vertical Analytics** teams.

---

### New Minigame Vertical Analytics

**1. {Project Name}**
{Brief paragraph with key findings — 2-3 sentences max. Numbers where available.}
[Deck]({link})

{Repeat for each artifact}

---

### LRK Vertical Analytics

**1. {Project Name}**
{Brief paragraph with key findings. Inline links to dashboards/Hex apps.}

{Repeat for each artifact}

[LRK Weekly Insights Doc]({link})

---

Best,
Alireza
```

### Step 5: Save Output
Save the markdown file to: `outputs/weekly-digest/{{DATE}}_weekly_analytics_digest.md`

### Step 6: Present to User
Show the full email draft in the conversation for review before finalizing.

### Step 7: Publish to Confluence
After user approves the draft:
1. Create a child page under the **Weekly Analytics Digest** parent page in
   Confluence with the full email content.
   - **Confluence parent page ID:** `1634730091`
   - **Space ID:** `113377280` (TOP space)
   - **Cloud ID:** `scopely.atlassian.net`
   - **Page title:** `Weekly Analytics Digest -- w/o {Mon date}, {Year}`
     (e.g., "Weekly Analytics Digest -- w/o Apr 14, 2026")
   - **Content format:** `markdown`
   - Omit the Subject line — use just the body content starting from "Hi all,"
2. Confirm the Confluence URL back to the user.

## Formatting Rules
- No names — do not include analyst names in the email body.
- Keep each project summary to a brief paragraph (2-3 sentences). Executives skim.
- Lead with the punchline (what happened), then the "so what" (why it matters).
- Include specific numbers where available (e.g., "+15% ARPDAU", "~3% of Regulars").
- Always include the link to the artifact.
- Use bold for project names. No bullet points — use compact paragraphs.
- No jargon without context — if a metric is unusual, add a parenthetical.
- If an artifact is WIP or pending follow-up data, note it explicitly.
- For Minigame Health Assessments, name them "Minigame Health Assessment -- Vol N: {Name}".
- Inline embedded links from source docs (Looker dashboards, Hex apps, Slack) directly.

## Notes
- This agent reads Google Docs/Slides via `gws` CLI (read-only). It never
  modifies Google Workspace documents.
- The `gws` CLI must be authenticated (`gws auth status` should show
  `token_valid: true` for `alireza.hamidi@scopely.com`).
- If a document fails to fetch, note it in the output and proceed with the rest.
- Confluence writes are ONLY to the Weekly Analytics Digest parent page
  (ID `1634730091`) under Ad Hoc Output Examples. No writes anywhere else.
