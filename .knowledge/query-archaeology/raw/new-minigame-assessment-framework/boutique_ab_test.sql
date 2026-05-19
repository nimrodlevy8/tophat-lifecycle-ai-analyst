with test as 
(select distinct case when variant_id in ('35e7932a-1d0a-4425-b3f9-c8c8180492e9') then 'Control'
            when variant_id in ('20a737f4-b6fe-499f-89c5-7de73a28c727') then 'Variant A'
            when variant_id in ('271f308b-11a9-4cf0-a8e0-58acc36666d6') then 'Variant B'
            when variant_id in ('cb6bfed8-1bb6-4a4c-80a4-2c45f5e345de') then 'Variant C'
            when variant_id in ('75f9e2fe-3c79-44b7-a8fc-c66af3418cd0') then 'Variant D'
            when variant_id in ('2ca2ecef-8544-4b15-9359-f464242e4199') then 'Variant E'
            when variant_id in ('9b0101f0-9920-4cd9-83c9-a9d59e1240e2') then 'Variant F'
            end as variant_name,
fac.user_id,
'Multivariate Test' as test_name, 
from `dwh-prod-tophat.STD_tophat.sys_abtest_assignment` fac 
where date(collector_time) >=  '2025-10-19'  
and test_id = '30c640a5-bcd4-4f59-87ef-fcb536981ca1'
and build_type = 1

union all 

select distinct case when variant_id in ('a363973a-0d35-4411-bcea-25d67bcfe224') then 'Control'
            when variant_id in ('e6ab67f0-a80b-46dd-a294-b87dd9ab9ddc') then 'Variant A'
            end as variant_name,
fac.user_id,
'Multi-ingredient Block Test' as test_name, 
from `dwh-prod-tophat.STD_tophat.sys_abtest_assignment` fac 
where date(collector_time) >=  '2025-12-01'  
and test_id = 'a2396a8e-ffed-43b9-9070-17aa3f5d4858'
and build_type = 1

union all 

select distinct case when variant_id in ('97937c69-1ec2-4ab3-928c-ff359277d284') then 'Control'
    when variant_id in ('81851d58-0781-4f40-b73e-378232567147') then 'Test Variant'
    end as variant_name, 
    user_id, 
    'Batch Block Tuning Test' as test_name, 
from `dwh-prod-tophat.STD_tophat.sys_abtest_assignment` 
where date(collector_time) >=  '2026-02-01'  
and test_id = 'fdaf06c9-f222-4d7c-8bf7-c415ede11b11'
and build_type = 1

union all 

select distinct case when variant_id in ('e2c96e6d-1682-4a48-adce-806bcd2257cc') then 'Control'
    when variant_id in ('102823c2-a5f4-44eb-8bef-6ad9bd8e816b') then 'Test Variant'
    end as variant_name, 
    user_id, 
    'Case Block Tuning Test' as test_name, 
from `dwh-prod-tophat.STD_tophat.sys_abtest_assignment` 
where date(collector_time) >=  '2026-02-01'  
and test_id = 'eba91561-1daf-43bc-a8c9-06aa677d64b9'
and build_type = 1
)

select *, 
sum(users) over (partition by liveops_id,  test_name, variant_name rows between unbounded preceding and unbounded following) as total_users_per_variant, 
sum(users) over (partition by liveops_id,  player_type rows between unbounded preceding and unbounded following) as total_users_per_player_type, 
sum(users) over (partition by liveops_id, test_name, variant_name, player_type rows between unbounded preceding and unbounded following) as total_users_per_player_type_variant, 
from (
select count(distinct user_id) as users, 
    -sum(rolls_to_complete) as sum_rolls_to_complete, 
    -sum(currency_to_complete) as sum_curr_to_complete, 
    case when rolls_to_complete < -80000 then 80000 
    when rolls_to_complete > -1000 then 1000 else -rolls_to_complete_bucketed end as rolls_sink_to_complete,
    case when currency_to_complete < -80000 then 80000 
    when currency_to_complete > -10 then 10 else -currency_to_complete_bucketed end as currency_sink_to_complete,
  liveops_id, 
  player_type, 
  liveops_id_cleaned, 
  --is_cheater, 
  --tenure_segment, 
  minigame_type, 
  test_name, 
  variant_name, 
  --event_completer, 
from (
    select distinct t1.user_id, 
        sum(t1.rolls_to_complete) rolls_to_complete, 
        sum(t1.currency_to_complete) currency_to_complete, 
        floor(sum(t1.rolls_to_complete)/1000)*1000 rolls_to_complete_bucketed, 
        floor(sum(t1.currency_to_complete)/10)*10 currency_to_complete_bucketed, 
        sum(t1.currency_sink) currency_sink,
        t1.liveops_id, 
        ### segmentation_type_selector defines how I segment players, values are either Liveops_Segment, Last 7 Day Active Segment, or in future I may add to them
        case when {{segmentation_type_selector}} = 'Liveops Segment' then 
                case when t2.is_loyal_payer_first_day then 'Loyal Payer'
                    when t2.is_regular_customer_first_day then 'Regular Customer'
                    when t2.is_regular_first_day then 'Regular'
                    else 'Other' end 
            when {{segmentation_type_selector}} = 'Last 7 Day Active Segment' then 
                case when t2.f_last_7d_active_days between 1 and 4 then '1-4 day active'
                    when t2.f_last_7d_active_days between 5 and 6 then '5-6 day active'
                    when t2.f_last_7d_active_days = 7 then 'regular' else cast(t2.f_last_7d_active_days as string) end 
            when {{segmentation_type_selector}} = 'ROW' then 'ROW'
            when {{segmentation_type_selector}} = 'AB Test Name' then coalesce(t3.test_name, 'ROW')
            when {{segmentation_type_selector}} = 'AB Test Variant' then coalesce(t3.variant_name, 'Control')
            end as player_type,             
        sum(t1.rolls_sink) roll_sink,
        sum(t1.currency_source) currency_source, 
        t1.liveops_id_cleaned, 
        t2.start_tenure_segment as tenure_segment, 
        t2.is_cheater_first_day as is_cheater, 
        t1.minigame_type,
        t2.is_regular_first_day as is_regular, 
        t2.is_loyal_payer_first_day as is_loya_payer, 
        t1.is_event_completer as event_completer, 
        coalesce(t3.test_name, 'ROW') as test_name, 
        coalesce(t3.variant_name, 'Control') as variant_name, 
    from 
        (select user_id, 
            t1.liveops_id, 
            date(t2.start_time) as start_date, 
            date(t2.end_time) as end_date, 
            t2.minigame_type, 
            CASE WHEN t1.f_event_completion_time IS NOT NULL THEN true else false end as is_event_completer,
            concat(date(t2.start_time),replace(right(split(t1.liveops_id,'@')[1], length(split(t1.liveops_id,'@')[1]) -length(split(split(t1.liveops_id, '@')[1],'_')[0])),'SE_','')) as liveops_id_cleaned,
            coalesce(min(f_rolls_sink_to_complete),0) rolls_to_complete, 
            coalesce(min(f_currency_sink_to_complete),0) currency_to_complete,
            coalesce(sum(f_currency_sink),0) currency_sink,
            coalesce(sum(f_currency_source),0) currency_source, 
            coalesce(sum(f_rolls_sink),0) rolls_sink
        from `dwh-prod-tophat.DM.fac_intraday_minigame_snapshot_daily` t1 
        left join `dwh-prod-tophat.BIZ.dim_intraday_live_minigames` t2 
        on t1.liveops_id = t2.liveops_id
        group by all
    ) t1 
    left join `dwh-prod-tophat.DM.d_minigame_user_attributes` t2 
    on t1.user_id = t2.user_id and t1.liveops_id = t2.liveops_id
    left join test t3 
    on t1.user_id = t3.user_id
    group by all
)
where liveops_id_cleaned in ({{liveops_event_selector | array}})
and is_cheater in ({{cheater_selector | array}})
and tenure_segment in ({{tenure_selector | array}})
and minigame_type in ({{minigame_type | array}})
and test_name in ({{ab_test_name_selector | array}})
and variant_name in ({{ab_test_variant_selector | array}})
group by all
)