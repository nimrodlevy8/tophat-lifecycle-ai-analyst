WITH user_attraction_counts AS (
  SELECT
    user_id,
    liveops_id,
    CASE WHEN SUM(max_bar_attraction_points) >= 10000 THEN TRUE ELSE FALSE END AS is_total_progress_more_than_10000,
    COUNT(DISTINCT CASE WHEN attraction_id IS NOT NULL AND attraction_id != 'None' AND max_bar_attraction_points <= 16000 THEN attraction_id END) AS num_attractions_under_20pct,
    COUNT(DISTINCT CASE WHEN attraction_id IS NOT NULL AND attraction_id != 'None' AND max_bar_attraction_points > 16000 AND max_bar_attraction_points <= 40000 THEN attraction_id END) AS num_attractions_between_20_50pct,
    COUNT(DISTINCT CASE WHEN attraction_id IS NOT NULL AND attraction_id != 'None' AND max_bar_attraction_points > 40000 AND max_bar_attraction_points <= 64000 THEN attraction_id END) AS num_attractions_between_50_80pct,
    COUNT(DISTINCT CASE WHEN attraction_id IS NOT NULL AND attraction_id != 'None' AND max_bar_attraction_points > 64000 THEN attraction_id END) AS num_attractions_over_80pct,
    CASE WHEN SAFE_DIVIDE(SUM(player_contribution_attraction_points), SUM(max_bar_attraction_points)) <= 0.2 THEN '0. Less Than 20%'
        WHEN SAFE_DIVIDE(SUM(player_contribution_attraction_points), SUM(max_bar_attraction_points)) <= 0.5 THEN '1. 20% to 50%'
        WHEN SAFE_DIVIDE(SUM(player_contribution_attraction_points), SUM(max_bar_attraction_points)) <= 0.8 THEN '2. 50% to 80%'
        WHEN SAFE_DIVIDE(SUM(player_contribution_attraction_points), SUM(max_bar_attraction_points)) > 0.8 THEN '3. More Than 80%'
        ELSE '4. Other' END AS percent_total_participation, 
  FROM `dwh-prod-tophat-exp.looker_sandbox.coop_attraction_progression`
  GROUP BY ALL
)

SELECT
  a.liveops_id,
  a.liveops_id_cleaned,
  c.minigame_type,
  c.start_date AS event_start_date,
  DATE_DIFF(c.end_date, c.start_date, DAY) AS event_duration_days,
  CASE
    WHEN e.f_last_7d_active_days BETWEEN 1 AND 4 THEN '1. 1-4 day active'
    WHEN e.f_last_7d_active_days BETWEEN 5 AND 6 THEN '2. 5-6 day active'
    WHEN e.f_last_7d_active_days = 7 THEN '3. regular'
    ELSE SAFE_CAST(e.f_last_7d_active_days AS STRING)
  END AS player_type,
  COALESCE(e.start_tenure_segment, 'N/A') AS tenure_segment,
  COALESCE(e.is_cheater_first_day, false) AS is_cheater,
  CASE WHEN a.f_event_completion_time IS NOT NULL THEN true ELSE false END AS is_event_completer,
  ac.is_total_progress_more_than_10000, 
  COALESCE(ac.num_attractions_between_50_80pct,0) + COALESCE(ac.num_attractions_over_80pct,0) AS attractions_more_than_50pct, 
  COALESCE(ac.percent_total_participation, '0. Less Than 20%') as percent_total_participation,

  -- Additive metrics (aggregate at pivot level)
  COUNT(a.user_id) AS distinct_users,
  COUNT(DISTINCT CASE WHEN COALESCE(a.currency_sink, 0) <> 0 THEN a.user_id END) AS distinct_event_players,
  COUNT(DISTINCT d.user_id) AS distinct_completers,
  COALESCE(SUM(a.session_length_minute), 0) AS session_length_minute,
  COALESCE(SUM(a.revenue), 0) AS revenue,
  COUNT(DISTINCT CASE WHEN COALESCE(a.revenue, 0) > 0 THEN a.user_id END) AS distinct_payers,
  COALESCE(SUM(a.free_rolls_source), 0) AS free_rolls_source,
  COALESCE(SUM(a.rolls_sink), 0) AS rolls_sink,
  COALESCE(SUM(a.rolls_source)) AS rolls_source,
  COALESCE(SUM(a.currency_sink), 0) AS currency_sink,
  COALESCE(SUM(a.currency_source), 0) AS currency_source,
  COALESCE(SUM(a.currency_sink_to_complete), 0) AS currency_sink_to_complete,
  COALESCE(SUM(a.rolls_sink_to_complete), 0) AS roll_sink_to_complete,
  COALESCE(SUM(a.successful_payments), 0) AS successful_payments,
  COALESCE(SUM(b.f_timestamp_last_currency_spent), 0) AS continuous_engagement_numerator,
  COUNT(DISTINCT CASE WHEN a.f_event_completion_time IS NOT NULL AND DATE_DIFF(DATE(a.f_event_completion_time), DATE(a.liveops_start_time), DAY) < 2 THEN a.user_id END) AS early_completers,
  SUM(a.user_days_active) AS user_days_active,
  SUM(a.payer_days_active) AS payer_days_active,
  COUNT(DISTINCT CASE WHEN e.d7_returner THEN a.user_id END) AS d7_returners,
  COUNT(DISTINCT CASE WHEN e.d7_returner AND COALESCE(a.currency_sink, 0) <> 0 THEN a.user_id END) AS event_player_d7_returners,
  COUNT(DISTINCT CASE WHEN COALESCE(e.f_next_7d_active_days,0) < COALESCE(e.f_last_7d_active_days,0) AND COALESCE(a.currency_sink,0) <> 0 THEN a.user_id END ) lapsed_event_players, 

FROM (
  SELECT
    t1.user_id,
    t1.liveops_id,
    MAX(t1.f_event_completion_time) AS f_event_completion_time,
    MAX(t1.liveops_start_time) AS liveops_start_time,
    CASE WHEN t1.liveops_id LIKE '%@%'
      THEN CONCAT(DATE(t1.liveops_start_time), REPLACE(RIGHT(SPLIT(t1.liveops_id,'@')[1], LENGTH(SPLIT(t1.liveops_id,'@')[1]) - LENGTH(SPLIT(SPLIT(t1.liveops_id, '@')[1],'_')[0])), 'SE_', ''))
      ELSE t1.liveops_id END AS liveops_id_cleaned,
    COALESCE(SUM(t1.f_n_total_session_length_seconds / 60), 0) AS session_length_minute,
    COALESCE(SUM(t1.f_iap_revenue), 0) AS revenue,
    COALESCE(SUM(t1.f_rolls_source_free), 0) AS free_rolls_source,
    COALESCE(SUM(t1.f_rolls_sink), 0) AS rolls_sink,
    COALESCE(SUM(t1.f_rolls_source)) AS rolls_source,
    COALESCE(SUM(t1.f_currency_sink), 0) AS currency_sink,
    COALESCE(SUM(t1.f_currency_source), 0) AS currency_source,
    COALESCE(SUM(CASE WHEN DATE(t1.f_event_completion_time) = t1.snapshot_date THEN t1.f_currency_sink_to_complete END), 0) AS currency_sink_to_complete,
    COALESCE(SUM(CASE WHEN DATE(t1.f_event_completion_time) = t1.snapshot_date THEN t1.f_rolls_sink_to_complete END), 0) AS rolls_sink_to_complete,
    COALESCE(SUM(t1.f_successful_payments), 0) AS successful_payments,
    COALESCE(SUM(t1.f_first_rolls_balance)) AS sum_first_roll_balance,
    COALESCE(SUM(t1.f_last_rolls_balance)) AS sum_last_roll_balance,
    COUNT(DISTINCT t1.snapshot_date) AS user_days_active,
    COUNT(DISTINCT CASE WHEN COALESCE(t1.f_iap_revenue, 0) > 0 THEN t1.snapshot_date END) AS payer_days_active,
  FROM `dwh-prod-tophat.DM.fac_intraday_minigame_snapshot_daily` t1
  WHERE t1.snapshot_date >= '2025-01-01'
  GROUP BY ALL
) a
LEFT JOIN `dwh-prod-tophat.BIZ.f_minigame_continuous_engagement` b
  ON a.liveops_id = b.liveops_id AND a.user_id = b.user_id
LEFT JOIN `dwh-prod-tophat.BIZ.dim_intraday_live_minigames` c
  ON a.liveops_id = c.liveops_id
LEFT JOIN `dwh-prod-tophat.DM.d_intraday_minigame_completers` d
  ON a.liveops_id = d.liveops_id AND a.user_id = d.user_id
LEFT JOIN `dwh-prod-tophat.DM.d_minigame_user_attributes` e
  ON a.liveops_id = e.liveops_id AND a.user_id = e.user_id
LEFT JOIN user_attraction_counts ac
  ON a.liveops_id = ac.liveops_id AND a.user_id = ac.user_id
GROUP BY ALL
## should take input for the following filters to limit the data
HAVING liveops_id_cleaned in ({{liveops_event_selector | array}})
AND coalesce(tenure_segment, 'Attribute missing from d_minigame_user_attributes') in ({{tenure_selector | array}})  
AND cast(coalesce(is_cheater, false) as int64) in ({{cheater_selector | array}})
AND (player_type in ({{activity_segment_selector | array}}) or {{segmentation_type_selector}} = 'None')