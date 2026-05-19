---
name: chart-to-drive
description: |
  Standardized workflow for uploading local chart PNGs to Google Drive and making them available for insertion into Google Docs and Slides. Use this skill whenever you need to insert charts into Google Docs or Google Slides, when the google-doc-creator or google-slides-creator agents need chart URLs, when building presentations or reports with embedded visualizations, when user asks to "upload charts", "add images to the doc", "put charts in slides", "make charts available for Google", or any time you have chart PNG files that need to be referenced in Google Workspace documents. This skill eliminates repeated boilerplate of Drive upload + domain permissions + URL construction. Always use this skill before calling insert_doc_image or createImage APIs — those require domain-shared Drive URLs, which this skill produces. Also use when you see errors like "image URL not accessible" or "permission denied" during doc/slide creation — those usually mean charts weren't properly uploaded to Drive first.
---

# Skill: Chart-to-Drive Uploader

## Purpose

Standardized workflow for uploading local chart PNGs to Google Drive and making
them available for insertion into Google Docs and Slides. Eliminates the repeated
boilerplate of Drive upload + permissions + URL construction.

## When to Apply

Automatically whenever:
- Chart PNGs need to be inserted into Google Docs or Google Slides
- The `google-doc-creator` or `google-slides-creator` agent needs chart URLs
- User asks to "upload charts" or "add images to the doc/slides"
- User encounters "permission denied" or "image URL not accessible" errors when
  building Google Workspace documents — this usually means charts weren't uploaded
  to Drive first

**When NOT to use this skill:**
- For single-image uploads where you just need one Drive URL (use `mcp__google-docs__upload_image_to_drive` directly)
- When building Google Docs via the python-docx → upload workflow (that embeds images in the .docx file, no Drive URLs needed)

---

## Workflow

### Step 1: Collect chart files

Identify all chart PNGs that need uploading. Standard location: `outputs/charts/`.

```python
import os
chart_dir = "outputs/charts"
charts = [(f, os.path.join(chart_dir, f)) for f in sorted(os.listdir(chart_dir)) if f.endswith('.png')]
```

### Step 2: Upload all charts to Google Drive

Upload each chart directly to Google Drive using the MCP tool. This gives you
a permanent, domain-accessible URL without any external intermediary.

For each chart, call:
```
mcp__google-docs__upload_image_to_drive(
    file_path="{absolute_filepath}"
)
```

After upload, set domain-restricted sharing (Scopely org only):
```
mcp__google-workspace__set_drive_file_permissions(
    user_google_email="alireza.hamidi@scopely.com",
    file_id="{drive_file_id}",
    role="reader",
    type="domain",
    domain="scopely.com"
)
```

**NEVER set `type: "anyone"`.** All Drive files must be restricted to the
scopely.com domain. The returned `url` works for Google Docs/Slides APIs
because both the file and the requesting service are within the same domain.

**Optional:** Create a folder first for organization:
```
mcp__google-workspace__create_drive_folder(
    user_google_email="alireza.hamidi@scopely.com",
    folder_name="{dataset_name} - Charts"
)
```

### Step 3: Build the URL map

Return a mapping of chart filename to Drive URL:

```python
chart_map = {
    "01_height_crossover.png": {
        "drive_id": "1abc...",
        "drive_url": "https://drive.google.com/uc?id=1abc...&export=download"
    },
    ...
}
```

**For Google Docs:** Use `drive_url` (permanent, works with `insert_doc_image`)
**For Google Slides:** Use `drive_url` (permanent, works with `createImage`)

---

## URL Format Reference

| Target | URL Format | Notes |
|--------|-----------|-------|
| Google Docs `insert_doc_image` | `https://drive.google.com/uc?id={ID}&export=download` | Domain-shared (scopely.com) |
| Google Slides `createImage` | `https://drive.google.com/uc?id={ID}&export=download` | Domain-shared (scopely.com) |
| Direct Drive view | `https://drive.google.com/file/d/{ID}/view` | Not for API insertion |

---

## Rules

1. **Upload directly to Google Drive.** Never use external intermediary services.
   All data must stay within Scopely boundaries (local machine ↔ Scopely Google Cloud).

2. **Set domain-restricted permissions (scopely.com).** Never set files to
   public/anyone. Always use `type: "domain"` with `domain: "scopely.com"`.
   This ensures only Scopely users can access the files while still allowing
   Google Docs/Slides API to reference them within the org.

3. **Print the chart map.** Always output the full filename → drive_id mapping
   so subsequent agents can reference charts by name.

4. **Check for existing uploads.** Before re-uploading, search Drive for files
   with the same name in the expected folder. If you find existing files with
   matching names uploaded in the last 24 hours, reuse those Drive IDs instead
   of creating duplicates. Only re-upload if the file is missing or very old.

---

## Error Recovery

If Drive upload returns "permission denied" or "authentication failed":
- Verify Google Workspace MCP authentication status
- Run `mcp__google-docs__authorize_google_docs()` to re-authenticate
- Retry the upload after successful auth

If `upload_image_to_drive` is unavailable:
- Use `mcp__google-workspace__create_drive_file` with a local file path
- Manually set permissions via `mcp__google-workspace__set_drive_file_permissions`
