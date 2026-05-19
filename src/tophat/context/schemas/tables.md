# BigQuery Table Schemas

Project: `dwh-prod-tophat`

---

## BIZ.v_f_main_user_kpis (VIEW)

**The primary user-level daily KPI view.** Grain: user_id × snapshot_date. Contains nested STRUCTs for KPI domains.

### Top-level
| Column | Type | Description |
|--------|------|-------------|
| snapshot_date | DATE | UTC date of KPI snapshot |
| user_id | STRING | Internal user identifier |
| product_id | INTEGER | Static product id (105) for TopHat |
| b_product_name | STRING | Business facing product name |

### v_f_user_rpt (core KPIs)

**Acquisition & Install**
| Column | Type | Description |
|--------|------|-------------|
| f_days_since_install | INTEGER | Days since first install |
| lt_first_channel | STRING | First lifetime marketing channel |
| lt_first_channel_type | STRING | First marketing channel type |
| lt_first_country | STRING | First country code |
| lt_first_country_name | STRING | First country name |
| lt_first_platform | STRING | First platform code |
| lt_first_platform_name | STRING | First platform name |
| lt_first_publisher_name | STRING | First publisher / network name |
| lt_first_store | STRING | First store / distribution channel |
| lt_first_install_time | TIMESTAMP | First install timestamp |

**Activity & Retention**
| Column | Type | Description |
|--------|------|-------------|
| f_dau | INTEGER | Daily active user flag |
| f_dau_previous_day | INTEGER | DAU previous day |
| is_active | BOOLEAN | Any qualifying activity on snapshot date |
| is_active_previous_day | BOOLEAN | Active previous day |
| is_active_14_days_ago | BOOLEAN | Active 14 days prior |
| is_active_web | BOOLEAN | Web active flag |
| is_active_mobile | BOOLEAN | Mobile active flag |
| is_daily_reactivated | BOOLEAN | Reactivated after inactivity window |
| is_rolling_mau | BOOLEAN | In rolling MAU window |
| f_days_since_first_activity | INTEGER | Days since first activity |
| f_days_since_prev_activity | INTEGER | Days between last two activity days |
| f_days_since_last_activity | INTEGER | Days since last activity |
| f_days_since_last_reactivation | INTEGER | Days since last reactivation |
| f_last_7d_active_days | INTEGER | Active days in trailing 7d |
| f_last_14d_active_days | INTEGER | Active days in trailing 14d |
| f_last_28d_active_days | INTEGER | Active days in trailing 28d |
| f_lt_active_days | INTEGER | Lifetime active days |
| f_session_duration | INTEGER | Session duration (seconds) snapshot day |
| f_sessions | INTEGER | Session count snapshot day |
| f_key_activity_events | INTEGER | Key activity events count |
| lt_first_activity_time | TIMESTAMP | First activity timestamp |
| activity_segment | STRING | Activity engagement segment label |
| f_churning_users | INTEGER | Users churning by inactivity rule |

**Monetization**
| Column | Type | Description |
|--------|------|-------------|
| f_iap_revenue | FLOAT | IAP revenue snapshot day |
| f_iap_revenue_web | FLOAT | Web IAP revenue snapshot day |
| f_iap_revenue_ios | FLOAT | iOS IAP revenue |
| f_iap_revenue_android | FLOAT | Android IAP revenue |
| f_lt_iap_revenue | FLOAT | Lifetime IAP revenue |
| f_lt_iap_revenue_web | FLOAT | Lifetime web IAP revenue |
| f_last_28d_iap_revenue | FLOAT | Trailing 28d IAP revenue |
| f_payments | INTEGER | Payments snapshot day |
| f_payments_web | INTEGER | Web payments snapshot day |
| f_lt_payments | INTEGER | Lifetime payments |
| f_lt_payments_web | INTEGER | Lifetime web payments |
| is_customer | BOOLEAN | Ever made a purchase |
| is_new_customer | BOOLEAN | New customer on snapshot date |
| is_payer | BOOLEAN | Has paid at least once (lifetime) |
| f_dap | INTEGER | Daily active payers |
| f_dac | INTEGER | Daily active customers |
| f_days_since_last_payment | INTEGER | Days since last payment |
| f_days_to_first_payment | INTEGER | Days from install to first payment |

**Loyalty & Segments**
| Column | Type | Description |
|--------|------|-------------|
| is_regular | BOOLEAN | Regular user flag |
| is_regular_customer | BOOLEAN | Regular customer flag |
| is_loyal_payer | BOOLEAN | Loyal payer flag |
| is_vip | BOOLEAN | VIP flag |
| f_regulars | INTEGER | Regular users population |
| f_regular_customers | INTEGER | Regular customers population |
| f_new_regulars | INTEGER | New regulars on snapshot date |
| f_new_regular_customers | INTEGER | New regular customers |
| f_reactivated_regular_customers | INTEGER | Reactivated regular customers |

### dim_user_snapshot (gameplay progression)

| Column | Type | Description |
|--------|------|-------------|
| last_board_level | FLOAT | Current board level |
| first_board_level | FLOAT | First board level reached |
| f_rolls | INTEGER | Rolls consumed snapshot day |
| f_rolls_spent | FLOAT | Rolls spent snapshot day |
| f_rolls_spent_7D | FLOAT | Rolls spent trailing 7d |
| f_rolls_spent_14D | FLOAT | Rolls spent trailing 14d |
| f_rolls_spent_28D | FLOAT | Rolls spent trailing 28d |
| rolls_end_balance | INTEGER | Ending rolls balance |
| f_boards_completed | INTEGER | Boards completed |
| f_shutdowns | INTEGER | Shutdowns performed |
| f_bank_heists | INTEGER | Bank heists performed |
| f_sticker_packs_opened | INTEGER | Sticker packs opened |
| f_stickers_sourced | FLOAT | Stickers sourced |
| n_friends | INTEGER | Friend count |
| sets_completed | INTEGER | Collection sets completed |
| is_rtue_active | BOOLEAN | RTUE feature active |
| is_rtue_cooldown | BOOLEAN | RTUE cooldown |
| is_ftue_minigame_active | STRING | FTUE minigame active state |
| churn_tag | STRING | Churn classification label |

### v_d_country (geography)
| Column | Type | Description |
|--------|------|-------------|
| geo_tier | STRING | Geographic tier |
| country_name | STRING | Country name |
| region | STRING | Region grouping |
| market | STRING | Market classification |

### v_d_rpt_tenure (tenure)
| Column | Type | Description |
|--------|------|-------------|
| tenure_segment | STRING | Tenure segment label |
| from_tenure_days | INTEGER | Lower bound days for segment |

### v_d_rpt_lt_spend (lifetime spend)
| Column | Type | Description |
|--------|------|-------------|
| lt_spend_segment | STRING | Lifetime spend segment |
| from_f_lt_spend | INTEGER | Lower bound spend for segment |

---

## DM.fac_sinks_n_sources (TABLE, ~1T rows)

**Economy transaction fact table.** Every currency sink/source event. Grain: user × item × transaction × date.

| Column | Type | Description |
|--------|------|-------------|
| transaction_date | DATE | Date of transaction (partition key) |
| user_id | STRING | User identifier |
| item_id | STRING | Item identifier |
| item_quantity | INTEGER | Quantity (negative = sink, positive = source) |
| item_balance | INTEGER | Balance after transaction |
| reference_type | STRING | High-level event category (Quest, Purchase, etc.) |
| reference_subtype | STRING | Detailed event subtype |
| transaction_type | STRING | Transaction type (iap, gifting, etc.) |
| transaction_subtype | STRING | Detailed transaction subtype |
| reference_event_id | STRING | Specific event that triggered transaction |
| sink_source | STRING | 'sink' or 'source' |
| num_transactions | INTEGER | Aggregated transaction count |
| sk_item_id | INTEGER | FK to lkp_item_commodity |
| sk_economy_reference | INTEGER | FK to dim_economy_reference |
| sk_economy_transaction | INTEGER | FK to dim_economy_transaction |
| reference_id.board_level | STRING | Board level context |
| reference_id.roll_ev | STRING | Roll exchange value context |
| product_id | INTEGER | Product id (105) |

> **Warning:** ~1T rows. Always filter by transaction_date and aggregate.

---

## BIZ.fac_revenue_funnel (TABLE, ~2.5B rows)

**Offer funnel from impression → tap → payment.** Grain: user × offer × date.

| Column | Type | Description |
|--------|------|-------------|
| snapshot_date | DATE | Date of interaction (partition) |
| user_id | STRING | User identifier |
| offer_id | STRING | Offer identifier |
| flow_name | STRING | UI flow (offer_popup, decoy_offer_flow, etc.) |
| offer_category | STRING | Business category |
| offer_impressions | INTEGER | Times offer shown |
| game_sku | STRING | SKU for the item/bundle |
| offer_placement | STRING | Location/context of offer |
| offer_taps | INTEGER | Taps on offer |
| offer_taps_to_purchase | INTEGER | Taps on purchase button |
| offer_taps_close_button | INTEGER | Taps on close |
| total_payments | INTEGER | Payment attempts |
| successful_payments | INTEGER | Successful payments |
| unsuccessful_payments_cancelled | INTEGER | Cancelled payments |
| total_amount_usd | FLOAT | Revenue USD (excl. VAT) |
| segment | STRING | User segment for offer |

---

## dwh-prod-tophat.BIZ.f_rev_web_payments_funnel (TABLE, ~654M rows)

**Web payments transaction table (daily updates).** Main table for web revenue analysis. Project: `dwh-prod-tophat`.

| Column | Type | Description |
|--------|------|-------------|
| collector_date | TIMESTAMP | Collection date (partition key) |
| collector_time | TIMESTAMP | Event timestamp |
| user_id | STRING | User identifier |
| payment_id | STRING | Payment event ID |
| success | BOOLEAN | Payment succeeded |
| error | STRING | Error message if failed |
| payment_type | STRING | Payment type (e.g., IAP) |
| amount_us | FLOAT | Amount in USD |
| amount_us_excl_vat | FLOAT | Amount USD excl. VAT |
| amount_local | FLOAT | Amount in local currency |
| local_currency_type | STRING | Local currency code |
| offer_id | STRING | Offer associated with payment |
| store_sku | STRING | App store SKU |
| game_sku | STRING | Internal game SKU |
| formatted_game_sku | STRING | Formatted game SKU |
| platform_name | STRING | Platform (iOS, Android) |
| store | STRING | Store/platform of payment |
| country | STRING | Country |
| country_iso_code | STRING | Country ISO code |
| session_id | STRING | Session ID |
| is_lt_first_purchase | BOOLEAN | Is this the user's first-ever purchase |
| offer_limit_available | STRING | Offer limit available |
| offer_cap | STRING | Offer cap |
| v_f_user_rpt | RECORD | User reporting attributes (same struct as v_f_main_user_kpis) |
| dim_user_snapshot | RECORD | User snapshot (board level, net worth, etc.) |
| sk_payment_event_timestamp | STRING | Surrogate key (payment_id + event_id + collector_time) |

> Use `dwh-prod-tophat.BIZ.f_rev_web_payments_funnel`.

---

## BIZ.v_star_album_daily (VIEW)

**Sticker album daily metrics per user per album.** Grain: user × album × snapshot_date.

| Column | Type | Description |
|--------|------|-------------|
| snapshot_date | DATE | Date |
| user_id | STRING | User |
| album_id | STRING | Album identifier |
| prestige | INTEGER | Current prestige level |
| unique_sticker_source | INTEGER | Unique stickers obtained today |
| total_sticker_source | FLOAT | Total stickers obtained today |
| total_new_stickers_source | FLOAT | New stickers (first time) today |
| total_sticker_packs_source | FLOAT | Sticker packs opened |
| total_payments | INTEGER | Payments today |
| total_revenue | FLOAT | Revenue today |
| total_roll_sink | FLOAT | Rolls spent today |
| album_prestige_completion_rate | FLOAT | % completion of current prestige |
| days_since_album_started | INTEGER | Days since album start |
| album_progression_rate | FLOAT | Proportion of album duration elapsed (0-1) |
| has_completed_album_prestige_today | BOOLEAN | Completed prestige today |
| album_prestige_phase | STRING | Current phase |

---

## BIZ.dim_intraday_live_minigames (TABLE, ~442 rows)

**Dimension table for live minigame events.** One row per event.

| Column | Type | Description |
|--------|------|-------------|
| sk_liveops_event | INTEGER | Surrogate key (partition) |
| liveops_id | STRING | Event business ID |
| start_time | TIMESTAMP | Event start |
| start_date | DATE | Event start date |
| end_time | TIMESTAMP | Event end |
| end_date | DATE | Event end date |
| minigame_type | STRING | Type: tycoon_race, coop_event, minigame_dig, prize_drop, carnival_games, adventure, boutique |
| event_type | STRING | Event category |
| mg_currency | STRING | Associated currency |

---

## STD_tophat.sys_payment (VIEW)

**Raw payment events.** One row per payment attempt.

| Column | Type | Description |
|--------|------|-------------|
| collector_time | TIMESTAMP | Server receipt time |
| collector_date | TIMESTAMP | Server receipt date |
| user_id | STRING | User |
| payment_id | STRING | Payment identifier |
| success | BOOLEAN | Payment succeeded |
| payment_type | STRING | Payment type |
| amount_us | FLOAT | Amount USD |
| amount_us_excl_vat | FLOAT | Amount USD excl. VAT |
| offer_id | STRING | Offer triggering payment |
| game_sku | STRING | Game SKU purchased |
| store_sku | STRING | Store SKU |
| platform_name | STRING | Platform |
| country | STRING | Country |

---

## STD_tophat.sys_app_open (VIEW)

**App open events.** One row per app open.

| Column | Type | Description |
|--------|------|-------------|
| collector_time | TIMESTAMP | Server time |
| user_id | STRING | User |
| is_warm_start | BOOLEAN | Warm vs cold start |
| deeplink_id | STRING | Deeplink that triggered open |
| platform_name | STRING | Platform |
| country | STRING | Country |
| session_id | STRING | Session identifier |

---

## STD_tophat.sys_fte_flow (VIEW)

**First-time experience (FTUE) flow events.** One row per tutorial step.

| Column | Type | Description |
|--------|------|-------------|
| collector_time | TIMESTAMP | Server time |
| user_id | STRING | User |
| tutorial_name | STRING | Tutorial name |
| tutorial_module | STRING | Module |
| step | FLOAT | Step number |
| step_name | STRING | Step name |
| duration | FLOAT | Time spent on step |
| skipped | BOOLEAN | Step was skipped |
| fte_complete | BOOLEAN | Full FTE completed |
| tutorial_type | STRING | Tutorial type |
| step_order | INTEGER | Canonical step ordering |

---

## STD_tophat.sys_ui (VIEW)

**UI interaction events.** Screens, taps, flows.

| Column | Type | Description |
|--------|------|-------------|
| collector_time | TIMESTAMP | Server time |
| user_id | STRING | User |
| screen_id | STRING | Screen ID |
| screen_name | STRING | Screen name |
| screen_type | STRING | Type |
| screen_category | STRING | Category |
| interaction_type | STRING | Interaction type |
| interaction_object | STRING | Object interacted with |
| flow_name | STRING | Flow name |
| flow_order | FLOAT | Step in flow |
| platform_name | STRING | Platform |

---

## STD_tophat.sys_gti (VIEW)

**Game transaction inventory events.** Every item grant/spend with full context.

| Column | Type | Description |
|--------|------|-------------|
| collector_time | TIMESTAMP | Server time |
| user_id | STRING | User |
| item_id | STRING | Item identifier |
| item_name | STRING | Item name |
| item_category | STRING | Category |
| item_rarity | STRING | Rarity |
| item_quantity | FLOAT | Quantity (pos=gain, neg=spend) |
| item_balance | FLOAT | Balance after |
| transaction_type | STRING | Transaction type |
| transaction_subtype | STRING | Subtype |
| reference_type | STRING | Reference type |
| reference_subtype | STRING | Reference subtype |
| reference_id | STRING | Reference event ID |

---

## STD_tophat.game_liveops (VIEW)

**Live operations player events.** Enrollment, progress, completion.

| Column | Type | Description |
|--------|------|-------------|
| collector_time | TIMESTAMP | Server time |
| user_id | STRING | User |
| liveops_id | STRING | Event ID |
| liveops_name | STRING | Event name |
| liveops_type | STRING | Type |
| liveops_subtype | STRING | Subtype |
| action_type | STRING | Action (enroll, progress, complete, etc.) |
| points_scored | FLOAT | Points earned |
| points_total | FLOAT | Total points |
| current_milestone | FLOAT | Current milestone |
| is_completed | BOOLEAN | Event completed |
| shard_id | STRING | Shard/group ID |
| rank | FLOAT | Rank in shard |

---

## STD_tophat.game_goal (VIEW)

**Game goal events.** Goals, objectives, completions.

| Column | Type | Description |
|--------|------|-------------|
| collector_time | TIMESTAMP | Server time |
| user_id | STRING | User |
| liveops_id | STRING | Associated liveops event |
| goal_id | STRING | Goal identifier |
| goal_title | STRING | Goal title |
| action_type | STRING | Action type |
| game_type | STRING | Game type |
| difficulty_level | STRING | Difficulty |
| user_segment | STRING | Segment |
| milestone_id | STRING | Milestone ID |
| milestone_order | FLOAT | Milestone order |

---

## STD_tophat.game_milestone (VIEW)

**Milestone progress events.**

| Column | Type | Description |
|--------|------|-------------|
| collector_time | TIMESTAMP | Server time |
| user_id | STRING | User |
| liveops_id | STRING | Event ID |
| milestone_id | STRING | Milestone ID |
| milestone_name | STRING | Name |
| milestone_order | FLOAT | Order |
| milestone_currency | FLOAT | Currency earned at milestone |
| milestone_currency_needed | FLOAT | Currency needed |
| milestone_currency_total | FLOAT | Total currency accumulated |
| action_type | STRING | Action |
| game_mode | STRING | Game mode |
| user_segment | STRING | Segment |

---

## pub.v_d_monopoly_go_events_calendar (VIEW)

**Game events calendar.** Holidays, promotions, releases.

| Column | Type | Description |
|--------|------|-------------|
| event_name | STRING | Event name |
| event_start_date | DATE | Start |
| event_end_date | DATE | End |
| event_type | STRING | Type |
| event_category | STRING | Category |
| event_category_2 | STRING | Secondary category |
| country_name_iso2 | STRING | Country (if geo-specific) |
| event_description | STRING | Description |

---

## tophat_transform.CALENDAR (TABLE, ~4K rows)

**Date dimension table.**

| Column | Type | Description |
|--------|------|-------------|
| Date | DATE | Calendar date |
| Year | INTEGER | Year |
| Week | INTEGER | Week number |
| Month | INTEGER | Month number |
| Month_Name | STRING | Month name |
| Quarter | STRING | Quarter |
| Day_Of_Week | INTEGER | Day of week (1-7) |
| Day_Of_Week_Name | STRING | Day name |
| Is_Weekday | BOOLEAN | Weekday flag |

---

## Query Access Patterns

- STD_tophat views are **event-level** (raw telemetry). Filter by `collector_date` or partition.
- BIZ views are **aggregated/enriched**. Filter by `snapshot_date`.
- DM tables are **intermediate fact tables**. Filter by partition column.
- All tables use project prefix `dwh-prod-tophat` (e.g., `dwh-prod-tophat.BIZ.v_f_main_user_kpis`).
- Access nested STRUCT fields with dot notation: `v_f_user_rpt.f_dau`, `v_d_country.geo_tier`
- Do NOT use `BIZ.v_f_user_standard_kpis` — use `BIZ.v_f_main_user_kpis` instead (same data, better maintained).
