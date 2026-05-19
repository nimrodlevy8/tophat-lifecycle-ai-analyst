SELECT DISTINCT
    minigame_type,
    liveops_id,
    date(start_time) event_start_date,
    date(end_time) AS event_end_date,
    case when liveops_id like '%@%' 
        then concat(date(start_time),replace(right(split(liveops_id,'@')[1], length(split(liveops_id,'@')[1]) -length(split(split(liveops_id, '@')[1],'_')[0])),'SE_','')) 
        else liveops_id end as liveops_id_cleaned,
    ROW_NUMBER() OVER(ORDER BY start_time ASC) AS event_seq_number
FROM `dwh-prod-tophat.BIZ.dim_intraday_live_minigames`
WHERE TRUE
    AND liveops_id NOT LIKE '%Internal%' -- EXCLUDING INTERNAL TESTS
    AND minigame_type IN ('tycoon_race')
    AND lower(liveops_id) NOT LIKE '%tsl%'
    AND lower(liveops_id) NOT LIKE '%darklaunch%'
    AND (lower(liveops_id) NOT LIKE '%variant%' OR liveops_id = 'RaceCup_WL13_variant_C@07022025_SE_TycoonRacers_WWL_13_Variant_C')
    AND lower(liveops_id) NOT LIKE '%cheater%'
    AND date(start_time) > date('2024-11-25')

order by 
    liveops_id_cleaned;

competition_users as (
 SELECT
        *

    FROM
        `dwh-prod-tophat-exp.looker_sandbox.competition_users`);


SELECT
    liveops_id,
    liveops_id_cleaned,
    case 
        when {{segmentation_type_selector1}} = 'Last 7 Day Active Segment' then active_days
        when {{segmentation_type_selector1}} = 'Liveops Segment' then liveops_segment
        when {{segmentation_type_selector1}} = 'Activity Segment' then activity_segment
    ELSE 'None' END AS player_type,
    COUNT(DISTINCT user_id) AS player_count,
    COUNT(DISTINCT CASE WHEN race_mode = 'solo' THEN user_id END)/COUNT(DISTINCT user_id) AS solo_percentage

FROM
    competition_users
WHERE TRUE
    AND liveops_id_cleaned IN ({{liveops_id_cleaned | array}})
    AND is_cheater = FALSE
GROUP BY    
    ALL
ORDER BY
    liveops_id_cleaned;


SELECT
    *
FROM
    (SELECT
        liveops_id,
        liveops_id_cleaned,
        event_seq_number,
        race_mode,
        case 
            when {{segmentation_type_selector1}} = 'Last 7 Day Active Segment' then active_days
            when {{segmentation_type_selector1}} = 'Liveops Segment' then liveops_segment
            when {{segmentation_type_selector1}} = 'Activity Segment' then activity_segment
            ELSE 'None' END AS player_type,
        COUNT(DISTINCT t1.user_id) AS player_count,
        -- ARPU
        SAFE_DIVIDE(SUM(t1.revenue), COUNT(DISTINCT t1.user_id)) AS arpu_event,
        SAFE_DIVIDE(SUM(t1.revenue_event_start_to_28_days_after), COUNT(DISTINCT t1.user_id)) AS arpu_event_start_to_28_days_after,
        SAFE_DIVIDE(COUNT(DISTINCT CASE WHEN t1.revenue > 0 THEN user_id END),COUNT(DISTINCT t1.user_id)) AS conversion_rate,

        APPROX_QUANTILES(t1.rolls_sink, 100)[OFFSET(50)] AS rolls_sink_median,
        APPROX_QUANTILES(t1.rolls_sink, 100)[OFFSET(90)] AS rolls_sink_percentile_90,
        -- APPROX_QUANTILES(t1.revenue, 100)[OFFSET(50)] AS revenue_median,
        -- APPROX_QUANTILES(t2.revenue, 100)[OFFSET(50)] AS event_1_revenue_median,
        -- APPROX_QUANTILES(t3.revenue, 100)[OFFSET(50)] AS event_2_revenue_median,
        -- APPROX_QUANTILES(t4.revenue, 100)[OFFSET(50)] AS event_3_revenue_median,
        APPROX_QUANTILES(t1.revenue, 100)[OFFSET(90)] AS revenue_percentile_90,
        APPROX_QUANTILES(t1.revenue_event_start_to_28_days_after, 100)[OFFSET(90)] AS revenue_event_start_to_28_days_after_percentile_90,
        APPROX_QUANTILES(t1.currency_sink, 100)[OFFSET(50)] AS currency_sink_median,
        APPROX_QUANTILES(t1.currency_sink, 100)[OFFSET(90)] AS currency_sink_percentile_90,
        APPROX_QUANTILES(t1.first_rolls_balance, 100)[OFFSET(50)] AS first_rolls_balance_median,
        APPROX_QUANTILES(t1.last_rolls_balance, 100)[OFFSET(50)] AS last_rolls_balance_median,
        AVG(rolls_per_currency_source) AS average_rolls_per_currency_source,
        AVG(team_podium_position) AS average_podium_position,

        -- racer related:
        AVG(team_mmr) AS average_team_mmr,
        -- AVG(previous_currency_eb) AS average_last_previous_currency_eb,

        -- momentum rate & 7 day return rate
        -- COUNT(DISTINCT CASE WHEN t1.momentum_type IN ('upgrade','stay') THEN t1.user_id END) AS momentum_upgrade_count,
        SAFE_DIVIDE(COUNT(DISTINCT CASE WHEN t1.momentum_type IN ('upgrade','stay') THEN t1.user_id END), COUNT(DISTINCT t1.user_id)) AS momentum_rate,
        
        -- SAFE_DIVIDE(COUNT(DISTINCT CASE WHEN t2.momentum_type IN ('upgrade','stay') THEN t2.user_id END), COUNT(DISTINCT t2.user_id)) AS event_1_momentum_rate,
        -- SAFE_DIVIDE(COUNT(DISTINCT CASE WHEN t3.momentum_type IN ('upgrade','stay') THEN t3.user_id END), COUNT(DISTINCT t3.user_id)) AS event_2_momentum_rate,
        -- SAFE_DIVIDE(COUNT(DISTINCT CASE WHEN t4.momentum_type IN ('upgrade','stay') THEN t4.user_id END), COUNT(DISTINCT t4.user_id)) AS event_3_momentum_rate,

        -- COUNT(DISTINCT CASE WHEN t1.d7_returner = TRUE THEN t1.user_id END) as d7_returners, 
        SAFE_DIVIDE(COUNT(DISTINCT CASE WHEN t1.d7_returner = TRUE THEN t1.user_id END),COUNT(DISTINCT t1.user_id)) AS d7_return_rate,
        -- SAFE_DIVIDE(COUNT(DISTINCT CASE WHEN t2.d7_returner = TRUE THEN t2.user_id END), COUNT(DISTINCT t2.user_id)) AS event_1_d7_return_rate,
        -- SAFE_DIVIDE(COUNT(DISTINCT CASE WHEN t3.d7_returner = TRUE THEN t3.user_id END), COUNT(DISTINCT t3.user_id)) AS event_2_d7_return_rate,
        -- SAFE_DIVIDE(COUNT(DISTINCT CASE WHEN t4.d7_returner = TRUE THEN t4.user_id END), COUNT(DISTINCT t4.user_id)) AS event_3_d7_return_rate  


    FROM
        competition_users t1
    WHERE TRUE
        AND liveops_id_cleaned IN ({{liveops_id_cleaned | array}})
        AND is_cheater = FALSE
    GROUP BY    
        ALL) t1
WHERE TRUE
    AND player_type IS NOT NULL
    AND player_type != '0'
    -- AND player_type NOT LIKE '%Other%'
GROUP BY ALL
ORDER BY    
    event_seq_number ASC;


-- 5 recent events, see how players flow from each category to the other
-- 1. Team & 1-4 days active
-- 2. Team & 5-6 days active
-- 3. Team & 7 days active
-- 1. Solo & 1-4 days active
-- 2. Solo & 5-6 days active
-- 3. Solo & 7 days active
WITH
players AS (
    SELECT DISTINCT
        user_id,
        liveops_id_cleaned,
        event_seq_number,
        race_mode,
        active_days,
        CONCAT(active_days, ' & ', race_mode) AS player_category
    FROM
        `dwh-prod-tophat-exp.looker_sandbox.racer_inequality_users`
    WHERE
        liveops_id_cleaned IN ('2026-01-21_Racers_WWL23',
                                '2026-01-07_Racers_WWL22',
                                '2025-12-10_Racers_WWL21',
                                '2026-02-04_Racers_WWL24',
                                '2026-03-04_Racers_WWL25')
        AND active_days IN ('1. 1-4 day active','2. 5-6 day active','3. regular')
)
SELECT
    player_category,
    COALESCE(player_category_1, '9.Churned') AS player_category_1,
    COALESCE(player_category_2, '9.Churned') AS player_category_2,
    COALESCE(player_category_3, '9.Churned') AS player_category_3,
    COALESCE(player_category_4, '9.Churned') AS player_category_4,
    COUNT(DISTINCT user_id) AS player_count
FROM
    (SELECT
        t1.*,
        t2.player_category AS player_category_1,
        t3.player_category AS player_category_2,
        t4.player_category AS player_category_3,
        t5.player_category AS player_category_4
    FROM
        (SELECT
            *
        FROM
            players
        WHERE
            liveops_id_cleaned = '2025-12-10_Racers_WWL21') t1
    LEFT JOIN
        players t2
    ON
        t1.user_id = t2.user_id
        AND t2.event_seq_number - t1.event_seq_number = 1
    LEFT JOIN
        players t3
    ON
        t1.user_id = t3.user_id
        AND t3.event_seq_number - t1.event_seq_number = 2
    LEFT JOIN
        players t4
    ON
        t1.user_id = t4.user_id
        AND t4.event_seq_number - t1.event_seq_number = 3
    LEFT JOIN
        players t5
    ON
        t1.user_id = t5.user_id
        AND t5.event_seq_number - t1.event_seq_number = 4)
GROUP BY
    ALL ;




