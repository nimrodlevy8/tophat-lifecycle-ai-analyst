SELECT 
  a.liveops_id, 
  a.liveops_id_cleaned, 
  c.minigame_type,
  c.start_date as event_start_date,   
  DATE_DIFF(c.end_date, c.start_date, DAY) event_duration_days, 
  case 
    when {{segmentation_type_selector}} = 'Last 7 Day Active Segment' then 
        case when e.f_last_7d_active_days between 1 and 4 then '1. 1-4 day active'
            when e.f_last_7d_active_days between 5 and 6 then '2. 5-6 day active'
            when e.f_last_7d_active_days = 7 then '3. regular' 
            else safe_cast(e.f_last_7d_active_days as string) end  
    when {{segmentation_type_selector}} = 'Liveops Segment' then 
        case when e.is_loyal_payer_first_day then '1. Loyal Payer'
            when e.is_regular_customer_first_day then '2. Regular Customer'
            when e.is_regular_first_day then '3. F2P Regular'
            else '4. Other' end 
    when {{segmentation_type_selector}} = 'Activity Segment' then 
      case when e.start_activity_segment = 'Always Regular' then '1. Always Regular'
            when e.start_activity_segment = 'Almost Regular' then '2. Almost Regular' 
            when e.start_activity_segment = 'Casual' then '3. Casual'
            when e.start_activity_segment = 'Volatile Activity' then '4. Volatile Activity'
            when e.start_activity_segment = 'Occasional' then '5. Occasional'
            when e.start_activity_segment = 'Funnel' then '6. Funnel'
            when e.start_activity_segment = 'Reactivation' then '7. Reactivation'
            when e.start_activity_segment = 'Returning Reactivation' then '8. Returning Reactivation'
            when e.start_activity_segment = 'Path to churn' then '9. Path to Churn' end 
    --when {{segmentation_type_selector}} = 'Social Score Bucket' then 
    --  COALESCE(ssb.social_score_bucket, 'N/A')
    --when {{segmentation_type_selector}} = 'Network Score Bucket' then 
    --  COALESCE(nsb.network_score_bucket, 'N/A')
    else 'None' end as player_type, 
  coalesce(e.start_tenure_segment, 'Attribute missing from d_minigame_user_attributes') as tenure_segment, 
  coalesce(e.is_cheater_first_day, false) as is_cheater, 
  CASE WHEN a.f_event_completion_time IS NOT NULL THEN true else false end as is_event_completer, 
  case when e.f_next_7d_active_days > e.f_last_7d_active_days then 'upgrade'
    when e.f_next_7d_active_days < e.f_last_7d_active_days then 'downgrade'
    when e.f_next_7d_active_days = e.f_last_7d_active_days then 'stay'
    else 'other' end as momentum_type, 
  --COALESCE(ssb.social_score_bucket, 'N/A') AS social_score_bucket,
  --COALESCE(nsb.network_score_bucket, 'N/A') AS network_score_bucket,

  -- Metrics 
  COUNT(a.user_id) as distinct_users, 
  COUNT(DISTINCT CASE WHEN coalesce(a.currency_sink,0) <> 0 then a.user_id end) distinct_event_players, 
  COUNT(DISTINCT d.user_id) as distinct_completers, 
  COALESCE(SUM(a.session_length_minute),0) as session_length_minute, 
  COALESCE(SUM(a.revenue), 0) as revenue, 
  COALESCE(SUM(CASE WHEN e.is_regular_customer_first_day THEN a.revenue ELSE 0 END)) as revenue_regular_customers, 
  COALESCE(SUM(CASE WHEN d.user_id IS NOT NULL THEN a.revenue END), 0) as completers_revenue, 
  COUNT(DISTINCT CASE WHEN COALESCE(a.revenue,0) > 0 THEN a.user_id END) as distinct_payers, 
  COUNT(DISTINCT CASE WHEN e.is_loyal_payer_first_day THEN a.user_id END) as distinct_loyal_payers, 
  COUNT(DISTINCT CASE WHEN e.is_regular_customer_first_day THEN a.user_id END) as distinct_regular_customers, 
  COUNT(DISTINCT CASE WHEN COALESCE(a.customer_days_active,0) > 0 THEN a.user_id END) as distinct_customers, 
  COUNT(DISTINCT CASE WHEN COALESCE(a.revenue,0) > 0 AND d.user_id IS NOT NULL THEN a.user_id END) as distinct_payers_completers, 
  COALESCE(SUM(a.free_rolls_source),0) as free_rolls_source, 
  COALESCE(SUM(a.rolls_sink),0) as rolls_sink, 
  COALESCE(SUM(a.rolls_source)) as rolls_source, 
  COALESCE(SUM(a.currency_sink),0) as currency_sink, 
  COALESCE(SUM(a.currency_source),0) as currency_source, 
  COALESCE(SUM(a.currency_sink_to_complete),0) as currency_sink_to_complete, 
  COALESCE(SUM(a.rolls_sink_to_complete),0) as roll_sink_to_complete,
  COALESCE(SUM(a.successful_payments),0) as successful_payments, 
  COALESCE(SUM(b.f_timestamp_last_currency_spent),0) as continuous_engagement_numerator, 
  COALESCE(SUM(a.sum_first_roll_balance)) AS sum_first_roll_balance, 
  COALESCE(SUM(a.sum_last_roll_balance)) AS sum_last_roll_balance,
  COUNT(DISTINCT CASE WHEN a.f_event_completion_time IS NOT NULL AND DATE_DIFF(DATE(a.f_event_completion_time),DATE(a.liveops_start_time) , DAY) < 2 THEN a.user_id END) as early_completers, 
  SUM(a.user_days_active) as user_days_active, 
  SUM(a.payer_days_active) as payer_days_active, 
  SUM(a.customer_days_active) as customer_days_active, 
  COUNT(DISTINCT CASE WHEN e.d7_returner THEN b.user_id END) as d7_returners, 
  COUNT(DISTINCT CASE WHEN (e.d7_returner) AND coalesce(a.currency_sink,0) <> 0 THEN b.user_id END) as event_player_d7_returners, 
  
FROM (
SELECT 
  t1.user_id, 
  t1.liveops_id, 
  MAX(t1.f_event_completion_time) f_event_completion_time, 
  MAX(t1.liveops_start_time) liveops_start_time, 
  case when t1.liveops_id like '%@%' 
        then concat(DATE(t1.liveops_start_time),replace(right(split(t1.liveops_id,'@')[1], length(split(t1.liveops_id,'@')[1]) -length(split(split(t1.liveops_id, '@')[1],'_')[0])),'SE_','')) 
        else t1.liveops_id end as liveops_id_cleaned,  

  ARRAY_AGG(t2.v_f_user_rpt.f_last_7d_active_days IGNORE NULLS ORDER BY t1.snapshot_date LIMIT 1)[SAFE_OFFSET(0)] as kpi_last_7d_active_days,
  ARRAY_AGG(t2.v_f_user_rpt.f_next_7d_active_days IGNORE NULLS ORDER BY t1.snapshot_date LIMIT 1)[SAFE_OFFSET(0)] as kpi_next_7d_active_days,

  COALESCE(SUM(t1.f_n_total_session_length_seconds / 60),0) as session_length_minute, 
  COALESCE(SUM(t1.f_iap_revenue), 0) as revenue, 
  COALESCE(SUM(t1.f_rolls_source_free),0) as free_rolls_source, 
  COALESCE(SUM(t1.f_rolls_sink),0) as rolls_sink, 
  COALESCE(SUM(t1.f_rolls_source)) as rolls_source, 
  COALESCE(SUM(t1.f_currency_sink),0) as currency_sink, 
  COALESCE(SUM(t1.f_currency_source),0) as currency_source, 
  COALESCE(SUM(case when date(t1.f_event_completion_time) = t1.snapshot_date then t1.f_currency_sink_to_complete end),0) as currency_sink_to_complete, 
  COALESCE(SUM(case when date(t1.f_event_completion_time) = t1.snapshot_date then t1.f_rolls_sink_to_complete end),0) as rolls_sink_to_complete,
  COALESCE(SUM(t1.f_successful_payments),0) as successful_payments, 
  COALESCE(SUM(t1.f_first_rolls_balance)) AS sum_first_roll_balance, 
  COALESCE(SUM(t1.f_last_rolls_balance)) AS sum_last_roll_balance,
  COUNT(DISTINCT t2.snapshot_date) as user_days_active, 
  COUNT(DISTINCT CASE WHEN COALESCE(t1.f_iap_revenue,0) > 0 THEN t2.snapshot_date END) as payer_days_active,
  COUNT(DISTINCT CASE WHEN t2.v_f_user_rpt.is_customer THEN t2.snapshot_date END) as customer_days_active,

FROM `dwh-prod-tophat.DM.fac_intraday_minigame_snapshot_daily` t1 
INNER JOIN `dwh-prod-tophat.BIZ.v_f_user_standard_kpis` t2 
  ON t1.user_id = t2.user_id AND t2.product_id = 105 AND t1.snapshot_date = t2.snapshot_date 

WHERE t1.snapshot_date >= current_date - 365 
  AND t1.snapshot_date < current_date 
  AND t2.snapshot_date >= current_date - 365 
  AND t2.snapshot_date < current_date 
GROUP BY ALL
### Below is the filter to limit number of liveops events I'm pulling
HAVING liveops_id_cleaned in ({{liveops_event_selector | array}})
) a 
LEFT JOIN `dwh-prod-tophat.BIZ.f_minigame_continuous_engagement` b 
  ON a.liveops_id = b.liveops_id AND a.user_id = b.user_id
LEFT JOIN `dwh-prod-tophat.BIZ.dim_intraday_live_minigames` c 
  ON a.liveops_id = c.liveops_id
LEFT JOIN `dwh-prod-tophat.DM.d_intraday_minigame_completers` d
  ON a.liveops_id = d.liveops_id AND a.user_id = d.user_id   
LEFT JOIN `dwh-prod-tophat.DM.d_minigame_user_attributes` e
  ON a.liveops_id = e.liveops_id and a.user_id = e.user_id 
  ### Bellow are parameters I want to limit/filter tenure_segment, cheater flag
WHERE coalesce(e.end_tenure_segment, 'Attribute missing from d_minigame_user_attributes') in ({{tenure_selector | array}})  
AND cast(coalesce(e.is_cheater_first_day, false) as int64) in ({{cheater_selector | array}})
GROUP BY ALL