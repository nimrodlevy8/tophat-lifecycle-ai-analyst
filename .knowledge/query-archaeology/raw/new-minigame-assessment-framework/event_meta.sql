    SELECT DISTINCT
    minigame_type,
    liveops_id,
    date(start_time) event_start_date,
    date(end_time) AS event_end_date,
    case when liveops_id like '%@%' 
        then concat(date(start_time),replace(right(split(liveops_id,'@')[1], length(split(liveops_id,'@')[1]) -length(split(split(liveops_id, '@')[1],'_')[0])),'SE_','')) 
        else liveops_id end as liveops_id_cleaned,
  FROM `dwh-prod-tophat.BIZ.dim_intraday_live_minigames`
  WHERE TRUE
    AND liveops_id NOT LIKE '%Internal%' -- EXCLUDING INTERNAL TESTS
    ### Filter what minigames I want, values are adventure, coop_event, prize_drop, minigame_dig, boutique, tycoon_race, carnival_games
    AND minigame_type IN ({{minigame_type | array}})
    order by liveops_id_cleaned