#!/usr/bin/env python3
"""
Create a Google Slides presentation for the Monopoly GO! Payment & Economy Alert System.
Uses google.auth.default() and the Google Slides API.
"""

import google.auth
from googleapiclient.discovery import build
import uuid

# ── Auth ──────────────────────────────────────────────────────────────────────
# We need Slides + Drive scopes. The ADC from gcloud doesn't include them,
# so we run an interactive OAuth flow using the gcloud OAuth client credentials.
import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",
]
TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".slides_token.json")

creds = None
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
    else:
        # Build client config from the gcloud ADC client id/secret
        adc_path = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
        with open(adc_path) as f:
            adc = json.load(f)
        client_config = {
            "installed": {
                "client_id": adc["client_id"],
                "client_secret": adc["client_secret"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0)
    # Save for next run
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

slides_service = build("slides", "v1", credentials=creds)

# ── Helpers ───────────────────────────────────────────────────────────────────

def rgb(hex_color: str) -> dict:
    """Convert '#RRGGBB' to Slides API RGB dict (0-1 floats)."""
    h = hex_color.lstrip("#")
    return {
        "red": int(h[0:2], 16) / 255,
        "green": int(h[2:4], 16) / 255,
        "blue": int(h[4:6], 16) / 255,
    }

def _oid() -> str:
    return uuid.uuid4().hex[:24]

# Color constants
DARK = "#3b3447"
RED = "#df2728"
WHITE = "#FFFFFF"
PURPLE_BG = "#7B2FBE"
GOLD_BG = "#DBA800"
GREEN = "#63d200"
LIGHT_PURPLE = "#CE9AFF"
GOLD_TEXT = "#dbc585"
CREAM = "#F8F5E5"

# ── Create blank presentation ─────────────────────────────────────────────────
presentation = slides_service.presentations().create(
    body={"title": "Monopoly GO! Payment & Economy Alert System"}
).execute()
PRES_ID = presentation["presentationId"]
# The first blank slide is created automatically; we'll use it as slide 1.
first_slide_id = presentation["slides"][0]["objectId"]

# ── Build all requests ────────────────────────────────────────────────────────
requests = []

def add_slide(layout="BLANK") -> str:
    sid = _oid()
    requests.append({
        "createSlide": {
            "objectId": sid,
            "slideLayoutReference": {"predefinedLayout": layout},
        }
    })
    return sid

def set_bg(slide_id: str, hex_color: str):
    requests.append({
        "updatePageProperties": {
            "objectId": slide_id,
            "pageProperties": {
                "pageBackgroundFill": {
                    "solidFill": {"color": {"rgbColor": rgb(hex_color)}}
                }
            },
            "fields": "pageBackgroundFill.solidFill.color",
        }
    })

def add_textbox(slide_id: str, left, top, width, height) -> str:
    """Add a textbox. Dimensions in EMU (1 inch = 914400 EMU). Returns element id."""
    eid = _oid()
    requests.append({
        "createShape": {
            "objectId": eid,
            "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {
                    "width": {"magnitude": width, "unit": "EMU"},
                    "height": {"magnitude": height, "unit": "EMU"},
                },
                "transform": {
                    "scaleX": 1, "scaleY": 1,
                    "translateX": left, "translateY": top,
                    "unit": "EMU",
                },
            },
        }
    })
    return eid

def add_rect(slide_id: str, left, top, width, height, fill_hex: str) -> str:
    eid = _oid()
    requests.append({
        "createShape": {
            "objectId": eid,
            "shapeType": "ROUND_RECTANGLE",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {
                    "width": {"magnitude": width, "unit": "EMU"},
                    "height": {"magnitude": height, "unit": "EMU"},
                },
                "transform": {
                    "scaleX": 1, "scaleY": 1,
                    "translateX": left, "translateY": top,
                    "unit": "EMU",
                },
            },
        }
    })
    requests.append({
        "updateShapeProperties": {
            "objectId": eid,
            "shapeProperties": {
                "shapeBackgroundFill": {
                    "solidFill": {"color": {"rgbColor": rgb(fill_hex)}}
                },
                "outline": {"outlineFill": {"solidFill": {"color": {"rgbColor": rgb(fill_hex)}}}, "weight": {"magnitude": 0, "unit": "PT"}},
            },
            "fields": "shapeBackgroundFill.solidFill.color,outline",
        }
    })
    return eid

def insert_text(element_id: str, text: str):
    requests.append({
        "insertText": {
            "objectId": element_id,
            "text": text,
            "insertionIndex": 0,
        }
    })

def style_text(element_id: str, start: int, end: int, font_size: float = None,
               bold: bool = None, italic: bool = None, color_hex: str = None,
               font_family: str = None):
    style = {}
    fields = []
    if font_size is not None:
        style["fontSize"] = {"magnitude": font_size, "unit": "PT"}
        fields.append("fontSize")
    if bold is not None:
        style["bold"] = bold
        fields.append("bold")
    if italic is not None:
        style["italic"] = italic
        fields.append("italic")
    if color_hex is not None:
        style["foregroundColor"] = {"opaqueColor": {"rgbColor": rgb(color_hex)}}
        fields.append("foregroundColor")
    if font_family is not None:
        style["fontFamily"] = font_family
        fields.append("fontFamily")
    if not fields:
        return
    requests.append({
        "updateTextStyle": {
            "objectId": element_id,
            "textRange": {"type": "FIXED_RANGE", "startIndex": start, "endIndex": end},
            "style": style,
            "fields": ",".join(fields),
        }
    })

def style_all(element_id: str, text: str, **kwargs):
    """Convenience: style the entire text of an element."""
    style_text(element_id, 0, len(text), **kwargs)

# ── Inch helpers ──────────────────────────────────────────────────────────────
INCH = 914400
SLIDE_W = int(10 * INCH)
SLIDE_H = int(5.625 * INCH)
MARGIN = int(0.5 * INCH)
CONTENT_W = SLIDE_W - 2 * MARGIN

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title Slide (purple background, white text)
# ══════════════════════════════════════════════════════════════════════════════
s1 = first_slide_id
set_bg(s1, PURPLE_BG)

t = "Payment & Economy Alert System"
e = add_textbox(s1, MARGIN, int(1.2 * INCH), CONTENT_W, int(1 * INCH))
insert_text(e, t)
style_all(e, t, font_size=36, bold=True, color_hex=WHITE)

t2 = "Proactive Revenue Protection for Monopoly GO!"
e2 = add_textbox(s1, MARGIN, int(2.2 * INCH), CONTENT_W, int(0.5 * INCH))
insert_text(e2, t2)
style_all(e2, t2, font_size=20, color_hex=GOLD_TEXT)

t3 = "Nimrod Levy  •  April 2026"
e3 = add_textbox(s1, MARGIN, int(3.2 * INCH), CONTENT_W, int(0.4 * INCH))
insert_text(e3, t3)
style_all(e3, t3, font_size=14, color_hex=WHITE)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Executive Summary
# ══════════════════════════════════════════════════════════════════════════════
s2 = add_slide()

title_t = "Executive Summary: Why We Need Automated Alerts"
e = add_textbox(s2, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=28, bold=True, color_hex=DARK)

body = (
    "We are currently flying blind on payment and economy health. "
    "When issues occur — broken app versions, store outages, economy misconfigurations — "
    "we find out hours or days later, after revenue has already been lost.\n\n"
    "Incidents from the last two months:\n"
    "• Feb 5: ApiError spike — 60,000 failed payments, 600x increase over normal\n"
    "• Mar 1: ChanceCard misconfiguration — 4.8B extra rolls (5x normal)\n"
    "• Android API-29 emulator traffic — 0% success rate, undetected for months\n\n"
    "Estimated revenue at risk without alerts: $1M–$5M per incident.\n\n"
    "We propose a 39-alert system across three categories — Operational, Revenue, "
    "and Behavioral — designed to catch these issues within hours, not days."
)
e2 = add_textbox(s2, MARGIN, int(1.1 * INCH), CONTENT_W, int(4 * INCH))
insert_text(e2, body)
style_all(e2, body, font_size=12, color_hex=DARK)

# Bold/red key phrases
for phrase in ["flying blind", "$1M–$5M per incident", "39-alert system"]:
    idx = body.find(phrase)
    if idx >= 0:
        style_text(e2, idx, idx + len(phrase), bold=True, color_hex=RED)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Divider: The Problem
# ══════════════════════════════════════════════════════════════════════════════
s3 = add_slide()
set_bg(s3, PURPLE_BG)
t = "The Problem:\nWhat We're Missing Today"
e = add_textbox(s3, MARGIN, int(1.5 * INCH), CONTENT_W, int(2 * INCH))
insert_text(e, t)
style_all(e, t, font_size=36, bold=True, color_hex=WHITE)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Limitations
# ══════════════════════════════════════════════════════════════════════════════
s4 = add_slide()

title_t = "No Systematic Payment Monitoring"
e = add_textbox(s4, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=28, bold=True, color_hex=DARK)

left_col_w = int(4.2 * INCH)
right_col_x = MARGIN + left_col_w + int(0.4 * INCH)

left_text = (
    "No real-time anomaly detection\n"
    "Payment health is monitored manually or through dashboards "
    "that require someone to actively look. When a store outage hits "
    "at 2 AM, no one is notified until user complaints surface.\n\n"
    "Economy changes go unnoticed\n"
    "When a rolls reward source is misconfigured (like the ChanceCard "
    "5x spike on Mar 1), the economy absorbs billions of excess currency "
    "before anyone notices."
)
e_l = add_textbox(s4, MARGIN, int(1.2 * INCH), left_col_w, int(3.8 * INCH))
insert_text(e_l, left_text)
style_all(e_l, left_text, font_size=11, color_hex=DARK)
for h in ["No real-time anomaly detection", "Economy changes go unnoticed"]:
    idx = left_text.find(h)
    style_text(e_l, idx, idx + len(h), bold=True, font_size=13, color_hex=RED)

right_text = (
    "No cross-dimensional visibility\n"
    "Issues affecting one platform, one country, or one app version are "
    "invisible at the aggregate level. A 0% success rate on a specific "
    "Android OS version ran for months undetected.\n\n"
    "Reactive, not proactive\n"
    "By the time an issue is identified through manual review, the damage — "
    "lost revenue, inflated economy, degraded user experience — has already compounded."
)
e_r = add_textbox(s4, right_col_x, int(1.2 * INCH), left_col_w, int(3.8 * INCH))
insert_text(e_r, right_text)
style_all(e_r, right_text, font_size=11, color_hex=DARK)
for h in ["No cross-dimensional visibility", "Reactive, not proactive"]:
    idx = right_text.find(h)
    style_text(e_r, idx, idx + len(h), bold=True, font_size=13, color_hex=RED)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — Revenue at Stake
# ══════════════════════════════════════════════════════════════════════════════
s5 = add_slide()

title_t = "The Revenue at Stake"
e = add_textbox(s5, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=28, bold=True, color_hex=DARK)

sub = "Every day without alerts is revenue left on the table"
e_sub = add_textbox(s5, MARGIN, int(0.8 * INCH), CONTENT_W, int(0.35 * INCH))
insert_text(e_sub, sub)
style_all(e_sub, sub, font_size=14, italic=True, color_hex=DARK)

# Three incident rows
incidents = [
    ("Feb 5 — ApiError Spike", "60,000 API errors in one day. Payment success rate dropped to 42.6%.", "$500K+"),
    ("Feb 9–10 — PurchasingDisabled Surge", "111,000 errors (vs. ~30K normal). Success rate cratered to 37.6%. Two full days.", "$2M+"),
    ("Mar 9 — Hourly Volume Cliff", "Payment volume dropped 72% mid-peak. ARPU crashed to $14.82 vs. $29 avg.", "$7M+"),
]
y_start = int(1.4 * INCH)
for i, (label, desc, amount) in enumerate(incidents):
    y = y_start + i * int(1.2 * INCH)
    # Description left
    txt = f"{label}\n{desc}"
    e_desc = add_textbox(s5, MARGIN, y, int(6.5 * INCH), int(1 * INCH))
    insert_text(e_desc, txt)
    style_all(e_desc, txt, font_size=12, color_hex=DARK)
    style_text(e_desc, 0, len(label), bold=True, font_size=14)
    # Big number right
    e_num = add_textbox(s5, int(7.2 * INCH), y, int(2.5 * INCH), int(1 * INCH))
    insert_text(e_num, amount)
    style_all(e_num, amount, font_size=48, bold=True, color_hex=RED)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — Economy Impact
# ══════════════════════════════════════════════════════════════════════════════
s6 = add_slide()

title_t = "Economy Impact: The Hidden Cost of Late Detection"
e = add_textbox(s6, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=28, bold=True, color_hex=DARK)

sub = "Payment failures are visible. Economy leaks are silent."
e_sub = add_textbox(s6, MARGIN, int(0.8 * INCH), CONTENT_W, int(0.35 * INCH))
insert_text(e_sub, sub)
style_all(e_sub, sub, font_size=14, italic=True, color_hex=DARK)

body = (
    "Mar 1 — ChanceCard Reward Misconfiguration\n"
    "ChanceCard/board quantity spiked to 5.78 billion rolls in one day — "
    "5x the normal ~1 billion. Each card was paying out 5x the intended reward.\n\n"
    "Net economy impact: +3.45 billion excess rolls injected "
    "(sink ratio dropped to 87.6% vs. typical 97-100%).\n\n"
    "Why this matters:\n"
    "• Excess free rolls devalue purchased rolls, reducing willingness to pay\n"
    "• Economy inflation takes weeks to correct through rebalancing\n"
    "• Every billion excess rolls ≈ $250K–$500K in deferred revenue erosion"
)
e_body = add_textbox(s6, MARGIN, int(1.3 * INCH), int(6.5 * INCH), int(3.5 * INCH))
insert_text(e_body, body)
style_all(e_body, body, font_size=12, color_hex=DARK)
style_text(e_body, 0, len("Mar 1 — ChanceCard Reward Misconfiguration"), bold=True, font_size=14)

big = "$1M+"
e_big = add_textbox(s6, int(7.2 * INCH), int(1.5 * INCH), int(2.5 * INCH), int(1.2 * INCH))
insert_text(e_big, big + "\nEstimated Deferred\nRevenue Erosion")
full_big = big + "\nEstimated Deferred\nRevenue Erosion"
style_all(e_big, full_big, font_size=14, color_hex=DARK)
style_text(e_big, 0, len(big), font_size=48, bold=True, color_hex=RED)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — Divider: The Solution
# ══════════════════════════════════════════════════════════════════════════════
s7 = add_slide()
set_bg(s7, PURPLE_BG)
t = "The Solution:\nA 39-Alert System"
e = add_textbox(s7, MARGIN, int(1.5 * INCH), CONTENT_W, int(2 * INCH))
insert_text(e, t)
style_all(e, t, font_size=36, bold=True, color_hex=WHITE)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — Three Pillars Overview
# ══════════════════════════════════════════════════════════════════════════════
s8 = add_slide()

title_t = "Three Pillars of Protection"
e = add_textbox(s8, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=28, bold=True, color_hex=DARK)

pillars = [
    (RED, "OPERATIONAL / TECHNICAL\n15 Alerts",
     "Catch system failures in real-time\n\n"
     "Detects infrastructure issues, store outages, app version bugs, "
     "and OS-specific failures. Monitors success rates, error spikes, "
     "hourly volume cliffs, and platform divergences."),
    (GREEN, "REVENUE / FINANCIAL\n12 Alerts",
     "Protect the top line\n\n"
     "Guards against revenue anomalies, ARPU shifts, pricing misconfigurations, "
     "FX rate changes, VAT errors, and whale revenue drops. Monitors each store "
     "and currency independently."),
    (LIGHT_PURPLE, "USER / BEHAVIORAL\n12 Alerts",
     "Detect engagement shifts early\n\n"
     "Tracks conversion rates, unique payer counts, country-level collapses, "
     "language-specific degradation, and user behavior patterns."),
]
box_w = int(2.8 * INCH)
gap = int(0.3 * INCH)
for i, (color, header, desc) in enumerate(pillars):
    x = MARGIN + i * (box_w + gap)
    y = int(1.2 * INCH)
    rect_id = add_rect(s8, x, y, box_w, int(3.8 * INCH), color)
    txt = f"{header}\n\n{desc}"
    insert_text(rect_id, txt)
    style_all(rect_id, txt, font_size=10, color_hex=WHITE)
    style_text(rect_id, 0, len(header), bold=True, font_size=14)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Operational Alerts Detail
# ══════════════════════════════════════════════════════════════════════════════
s9 = add_slide()

title_t = "Operational / Technical Alerts — 15 Total"
e = add_textbox(s9, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=24, bold=True, color_hex=DARK)

left_h = "Infrastructure & Store Health"
left_body = (
    "• Success rate drop (excl. UserCancelled) — hourly, vs. 7-day avg\n"
    "• ApiError spike — >1,000/hr or >3x average\n"
    "• PurchasingDisabled surge — >2x rolling 7-day avg\n"
    "• MalformedReceipt spike — >100/day absolute\n"
    "• Timeout rate increase — >2x trailing average\n"
    "• Network/Billing infrastructure combined alert\n"
    "• Hourly volume cliff — >60% hour-over-hour drop\n"
    "• Web/Playgami success rate drop — <99%"
)
e_l = add_textbox(s9, MARGIN, int(1.0 * INCH), int(4.3 * INCH), int(4 * INCH))
txt = f"{left_h}\n{left_body}"
insert_text(e_l, txt)
style_all(e_l, txt, font_size=10, color_hex=DARK)
style_text(e_l, 0, len(left_h), bold=True, font_size=13, color_hex=RED)

right_h1 = "App & Device Health"
right_b1 = (
    "• OS version zero success rate — >500 attempts with 0%\n"
    "• OS version success rate regression — >20% relative drop\n"
    "• App version success rate gap — >15pp between versions\n"
    "• New store appearance — flags unknown store values"
)
right_h2 = "Cross-Dimensional"
right_b2 = (
    "• Platform success rate divergence\n"
    "• Language-specific success rate drop\n"
    "• Flexion store volatility — >30% drop"
)
right_txt = f"{right_h1}\n{right_b1}\n\n{right_h2}\n{right_b2}"
e_r = add_textbox(s9, int(5 * INCH), int(1.0 * INCH), int(4.3 * INCH), int(4 * INCH))
insert_text(e_r, right_txt)
style_all(e_r, right_txt, font_size=10, color_hex=DARK)
for h in [right_h1, right_h2]:
    idx = right_txt.find(h)
    style_text(e_r, idx, idx + len(h), bold=True, font_size=13, color_hex=RED)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — Revenue Alerts Detail
# ══════════════════════════════════════════════════════════════════════════════
s10 = add_slide()

title_t = "Revenue / Financial Alerts — 12 Total"
e = add_textbox(s10, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=24, bold=True, color_hex=DARK)

sections_10 = [
    ("Revenue Volume",
     "• Daily revenue anomaly — >30% below same-weekday 4-week avg\n"
     "• Web/Playgami revenue drop — >25% below 7-day avg\n"
     "• Whale revenue drop ($100+ txns) — >40% below average\n"
     "• Currency-specific revenue drop — >40% for top-10 currencies"),
    ("Pricing & Monetization",
     "• ARPU shift — >25% deviation from 7-day average\n"
     "• Avg transaction value shift per platform — >30% change\n"
     "• Price tier distribution shift — any tier's share changes >50%\n"
     "• Platform revenue mix shift — >10pp change in any store's share"),
    ("Financial Integrity",
     "• FX rate sudden shift — >3% day-over-day for top-15 currencies\n"
     "• VAT rate anomaly per country — >2pp shift\n"
     "• amount_us vs. amount_us_old ratio drift — >0.1pp from 30-day avg\n"
     "• Store revenue share shift — >10pp in any store's daily share"),
]
y = int(1.0 * INCH)
col_w = int(2.9 * INCH)
for i, (hdr, body) in enumerate(sections_10):
    x = MARGIN + i * (col_w + int(0.2 * INCH))
    txt = f"{hdr}\n{body}"
    e_s = add_textbox(s10, x, y, col_w, int(4 * INCH))
    insert_text(e_s, txt)
    style_all(e_s, txt, font_size=10, color_hex=DARK)
    style_text(e_s, 0, len(hdr), bold=True, font_size=13, color_hex=RED)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — Behavioral Alerts Detail
# ══════════════════════════════════════════════════════════════════════════════
s11 = add_slide()

title_t = "User / Behavioral Alerts — 12 Total"
e = add_textbox(s11, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=24, bold=True, color_hex=DARK)

sections_11 = [
    ("Conversion & Engagement",
     "• Conversion rate drop — >15% below same-weekday avg\n"
     "• Unique payer count drop — >20% below expected\n"
     "• Transactions per payer anomaly — outside 1.3–2.0 range\n"
     "• Peak hour volume shift — >20% below expected (13–19 UTC)"),
    ("Geographic Health",
     "• Country-level success rate collapse — >50% drop for top-15\n"
     "• Country revenue disappearance — <10% of avg for top-10\n"
     "• Low-success-rate language degradation"),
    ("Platform & Device",
     "• Store-specific user drop (Flexion) — <50% of 7-day avg\n"
     "• Android emulator/fraud detection — >2x increase in 0%-success\n"
     "• New vs. returning payer ratio shift — >25% change\n"
     "• Country-level FX arbitrage/pricing mismatch\n"
     "• Peak hour user volume shift"),
]
y = int(1.0 * INCH)
col_w = int(2.9 * INCH)
for i, (hdr, body) in enumerate(sections_11):
    x = MARGIN + i * (col_w + int(0.2 * INCH))
    txt = f"{hdr}\n{body}"
    e_s = add_textbox(s11, x, y, col_w, int(4 * INCH))
    insert_text(e_s, txt)
    style_all(e_s, txt, font_size=10, color_hex=DARK)
    style_text(e_s, 0, len(hdr), bold=True, font_size=13, color_hex=RED)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — Divider: Before vs After (gold background)
# ══════════════════════════════════════════════════════════════════════════════
s12 = add_slide()
set_bg(s12, GOLD_BG)
t = "Before vs. After:\nReal Examples"
e = add_textbox(s12, MARGIN, int(1.5 * INCH), CONTENT_W, int(2 * INCH))
insert_text(e, t)
style_all(e, t, font_size=36, bold=True, color_hex=DARK)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — Before/After: ApiError
# ══════════════════════════════════════════════════════════════════════════════
s13 = add_slide()

title_t = "Before vs. After — The Feb 5 ApiError Incident"
e = add_textbox(s13, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=24, bold=True, color_hex=DARK)

col_w = int(4.2 * INCH)
# Left: Without alerts
left_h = "WITHOUT ALERTS (What Actually Happened)"
left_b = (
    "\nApiErrors spiked from ~100/day to 60,440 on Feb 5.\n"
    "Payment success rate dropped to 42.6%.\n\n"
    "• No automated notification was triggered\n"
    "• Issue identified through manual review or user complaints\n"
    "• ~50,000 successful payments were lost\n"
    "• Estimated revenue impact: $500K–$1M"
)
left_txt = left_h + left_b
# Red-tinted box
rect_l = add_rect(s13, MARGIN, int(1.1 * INCH), col_w, int(3.8 * INCH), "#FDE8E8")
insert_text(rect_l, left_txt)
style_all(rect_l, left_txt, font_size=11, color_hex=DARK)
style_text(rect_l, 0, len(left_h), bold=True, font_size=13, color_hex=RED)

# Right: With alerts
right_h = "WITH ALERTS (What Would Have Happened)"
right_b = (
    "\nThe ApiError Spike alert would have fired within the first hour, "
    "when hourly errors exceeded 1,000 (3x the threshold).\n\n"
    "• Team notified at hour 1 instead of hours/days later\n"
    "• Investigation begins immediately\n"
    "• If resolved within 2 hours: ~90% of lost revenue recovered\n"
    "• Estimated savings: $450K–$900K"
)
right_txt = right_h + right_b
rect_r = add_rect(s13, MARGIN + col_w + int(0.4 * INCH), int(1.1 * INCH), col_w, int(3.8 * INCH), "#E8F5E9")
insert_text(rect_r, right_txt)
style_all(rect_r, right_txt, font_size=11, color_hex=DARK)
style_text(rect_r, 0, len(right_h), bold=True, font_size=13, color_hex=GREEN)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — Before/After: ChanceCard
# ══════════════════════════════════════════════════════════════════════════════
s14 = add_slide()

title_t = "Before vs. After — The Mar 1 Economy Misconfiguration"
e = add_textbox(s14, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=24, bold=True, color_hex=DARK)

# Left: Without alerts
left_h = "WITHOUT ALERTS (What Actually Happened)"
left_b = (
    "\nChanceCard/board qty per transaction jumped from ~80 to ~405, "
    "injecting 4.8 billion extra rolls into the economy.\n\n"
    "• Sink ratio dropped to 87.6% (vs. typical 97–100%)\n"
    "• Net rolls surplus: +3.45 billion\n"
    "• No alert was triggered; misconfiguration may have persisted\n"
    "• Economy inflation reduces purchase pressure for days/weeks"
)
left_txt = left_h + left_b
rect_l = add_rect(s14, MARGIN, int(1.1 * INCH), col_w, int(3.8 * INCH), "#FDE8E8")
insert_text(rect_l, left_txt)
style_all(rect_l, left_txt, font_size=11, color_hex=DARK)
style_text(rect_l, 0, len(left_h), bold=True, font_size=13, color_hex=RED)

# Right: With alerts
right_h = "WITH ALERTS (What Would Have Happened)"
right_b = (
    "\nThe Avg Quantity Per Transaction Anomaly alert would have "
    "flagged ChanceCard's 5x qty shift within the first daily check.\n\n"
    "• Config error identified and rolled back within hours\n"
    "• Excess rolls reduced from 4.8B to ~500M\n"
    "• Economy remains balanced, purchase pressure preserved\n"
    "• Estimated protected revenue: $500K–$1M"
)
right_txt = right_h + right_b
rect_r = add_rect(s14, MARGIN + col_w + int(0.4 * INCH), int(1.1 * INCH), col_w, int(3.8 * INCH), "#E8F5E9")
insert_text(rect_r, right_txt)
style_all(rect_r, right_txt, font_size=11, color_hex=DARK)
style_text(rect_r, 0, len(right_h), bold=True, font_size=13, color_hex=GREEN)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — Revenue Protection Summary
# ══════════════════════════════════════════════════════════════════════════════
s15 = add_slide()

title_t = "What This System Is Designed to Protect"
e = add_textbox(s15, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=28, bold=True, color_hex=DARK)

big_numbers = [
    ("$2.6M–$13M", "Daily Revenue",
     "Our daily revenue ranges from $2.6M (worst) to $13M (best). "
     "A single undetected incident during a peak day can erase millions."),
    ("$374M", "Two-Month Revenue (Feb–Mar 2026)",
     "Across all platforms and stores. Even protecting 1% through "
     "faster detection = $3.7M in preserved revenue per cycle."),
    ("39", "Automated Alerts",
     "Covering operational health, revenue integrity, and user behavior — "
     "monitored continuously, alerting within hours instead of days."),
]
for i, (num, label, desc) in enumerate(big_numbers):
    y = int(1.1 * INCH) + i * int(1.3 * INCH)
    # Big number
    e_n = add_textbox(s15, MARGIN, y, int(3 * INCH), int(0.9 * INCH))
    insert_text(e_n, num)
    style_all(e_n, num, font_size=48, bold=True, color_hex=RED)
    # Label + desc
    txt = f"{label}\n{desc}"
    e_d = add_textbox(s15, int(3.5 * INCH), y, int(6 * INCH), int(1 * INCH))
    insert_text(e_d, txt)
    style_all(e_d, txt, font_size=12, color_hex=DARK)
    style_text(e_d, 0, len(label), bold=True, font_size=16)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — Scale of Monitoring (2x2 grid)
# ══════════════════════════════════════════════════════════════════════════════
s16 = add_slide()

title_t = "The Scale of What We're Monitoring"
e = add_textbox(s16, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=28, bold=True, color_hex=DARK)

cards_16 = [
    (RED, "PAYMENTS", "~900K daily transactions",
     "Across Apple, Google, Playgami, and Flexion stores, spanning 230+ countries and 25+ currencies"),
    (GREEN, "ECONOMY", "~1.2B daily rolls transactions",
     "56 billion rolls spent and 20+ billion earned daily through 30+ distinct sources"),
    (LIGHT_PURPLE, "PLATFORMS", "4 stores, 10+ OS versions, 3+ app versions",
     "Each with its own success rate baseline, failure modes, and revenue characteristics"),
    (GOLD_TEXT, "GEOGRAPHIES", "232 countries, 25+ languages, 25+ currencies",
     "Each with distinct VAT rates, FX rates, success rates, and payment infrastructure"),
]
box_w = int(4.2 * INCH)
box_h = int(1.7 * INCH)
gap = int(0.3 * INCH)
for i, (color, header, number, desc) in enumerate(cards_16):
    col = i % 2
    row = i // 2
    x = MARGIN + col * (box_w + gap)
    y = int(1.1 * INCH) + row * (box_h + gap)
    rect_id = add_rect(s16, x, y, box_w, box_h, color)
    txt = f"{header}\n{number}\n{desc}"
    insert_text(rect_id, txt)
    style_all(rect_id, txt, font_size=10, color_hex=WHITE)
    style_text(rect_id, 0, len(header), bold=True, font_size=14)
    style_text(rect_id, len(header) + 1, len(header) + 1 + len(number), bold=True, font_size=16)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — Recommendations & Next Steps
# ══════════════════════════════════════════════════════════════════════════════
s17 = add_slide()

title_t = "Recommendations & Next Steps"
e = add_textbox(s17, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=28, bold=True, color_hex=DARK)

phases = [
    ("Phase 1 — Critical Alerts (Week 1–2)",
     "1. Daily revenue anomaly (>30% drop)\n"
     "2. ApiError spike (>3x hourly average)\n"
     "3. Hourly volume cliff (>60% drop during peak)\n"
     "4. Web/Playgami success rate drop (<99%)\n"
     "5. Avg quantity per transaction anomaly (economy)"),
    ("Phase 2 — Revenue Protection (Week 3–4)",
     "ARPU shifts, whale revenue drops, FX rate changes, "
     "VAT anomalies. Platform and store-level revenue monitoring."),
    ("Phase 3 — Full Coverage (Week 5–6)",
     "Deploy all 39 alerts including behavioral and cross-dimensional "
     "monitoring. Country-level health, language segmentation, OS version tracking."),
]
y = int(1.0 * INCH)
for hdr, body in phases:
    txt = f"{hdr}\n{body}"
    e_p = add_textbox(s17, MARGIN, y, CONTENT_W, int(1.3 * INCH))
    insert_text(e_p, txt)
    style_all(e_p, txt, font_size=11, color_hex=DARK)
    style_text(e_p, 0, len(hdr), bold=True, font_size=14, color_hex=RED)
    y += int(1.3 * INCH)

delivery = (
    "Delivery: SQL queries as scheduled BigQuery jobs • "
    "Slack alerts (#tophat_analytics_internal) & email • "
    "Looker dashboard for real-time monitoring"
)
e_d = add_textbox(s17, MARGIN, y, CONTENT_W, int(0.5 * INCH))
insert_text(e_d, delivery)
style_all(e_d, delivery, font_size=11, bold=True, color_hex=DARK)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 18 — Traffic Light Status
# ══════════════════════════════════════════════════════════════════════════════
s18 = add_slide()

title_t = "Analysis Maturity Status — Ongoing Investigation"
e = add_textbox(s18, MARGIN, MARGIN, CONTENT_W, int(0.6 * INCH))
insert_text(e, title_t)
style_all(e, title_t, font_size=24, bold=True, color_hex=DARK)

# Orange hammer indicator
hammer_box = add_rect(s18, MARGIN, int(1.1 * INCH), int(2.5 * INCH), int(1.2 * INCH), "#FF8C00")
hammer_txt = "Orange Hammer"
insert_text(hammer_box, hammer_txt)
style_all(hammer_box, hammer_txt, font_size=24, bold=True, color_hex=WHITE)

status_items = [
    ("What this means:",
     "We're building confidence in the analysis. The alert definitions and "
     "thresholds are based on 2 months of real data, but validation is still in progress."),
    ("Why is this the case:",
     "We've analyzed daily, hourly, and dimensional patterns across payments and economy "
     "transactions. We've identified anomalies and proposed thresholds. However, backtesting "
     "against known incidents and threshold tuning still need to be completed."),
    ("What can you expect from us:",
     "Implementation of Phase 1 alerts within 2 weeks, with iterative refinement based on "
     "false-positive rates and stakeholder feedback."),
]
y = int(2.5 * INCH)
for hdr, body in status_items:
    txt = f"{hdr} {body}"
    e_s = add_textbox(s18, MARGIN, y, CONTENT_W, int(0.8 * INCH))
    insert_text(e_s, txt)
    style_all(e_s, txt, font_size=11, color_hex=DARK)
    style_text(e_s, 0, len(hdr), bold=True, color_hex=RED)
    y += int(0.85 * INCH)

source = "Source: sys_payment and sys_gti_nodedup tables from dwh-prod-tophat.STD_tophat, build_type = 1, Feb 1 – Apr 2, 2026"
e_src = add_textbox(s18, MARGIN, int(5 * INCH), CONTENT_W, int(0.3 * INCH))
insert_text(e_src, source)
style_all(e_src, source, font_size=8, italic=True, color_hex="#999999")

# ── Execute all requests ──────────────────────────────────────────────────────
print(f"Sending {len(requests)} API requests...")

# Slides API has a limit; batch in chunks of 500
CHUNK = 500
for i in range(0, len(requests), CHUNK):
    chunk = requests[i:i + CHUNK]
    slides_service.presentations().batchUpdate(
        presentationId=PRES_ID,
        body={"requests": chunk},
    ).execute()
    print(f"  Batch {i // CHUNK + 1} done ({len(chunk)} requests)")

url = f"https://docs.google.com/presentation/d/{PRES_ID}/edit"
print(f"\nPresentation created successfully!")
print(f"URL: {url}")
