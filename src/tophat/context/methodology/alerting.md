# Alerting System

## Platform
Alerts are defined via a Google Sheets validation tool. You fill in the sheet with the alert definition and the system builds/deploys the alert automatically.

## Alert Definition Schema

| Field | Description | Example |
|-------|-------------|---------|
| validation_name | Alias of the validation | `null-revenue` |
| description | Optional description | `The % of users with client exceptions is above 3.3%` |
| enabled | TRUE/FALSE — whether it's evaluated | TRUE |
| recovery_alert | Only alert on first failure + recovery (avoids spam) | TRUE |
| project_name | BQ project | `dwh-prod-tophat` |
| dataset_name | BQ dataset | `STD_tophat` |
| table_name | BQ table | `sys_gti_nodedup` |
| split_by_product | Calculate separately per product_id | FALSE |
| team | Owner team | `Monopoly GO` |
| slack_channel | Slack channel for alerts | `tophat_live_alarms` |
| email | Email for alerts | `team-bi-core@scopely.com` |
| validation_type | Always `aggregation expression` | `aggregation expression` |
| aggregation_expression | The metric to compute | `COUNT(DISTINCT user_id)` |
| dimension_1 | Optional first grouping dimension | `snapshot_date` |
| dimension_2 | Optional second grouping dimension | `platform_name` |
| where_condition | Additional filter | `build_type = 1 AND platform_name = 'ios'` |
| custom_query | Full custom SQL (overrides other configs) | See examples below |
| date_filter | Time field for temporal filtering | `collector_time` |
| frequency | How often to run | `1 h`, `4 h`, `24 h`, `15 min` |
| intraday_aggregation_minutes | Minutes to aggregate for intraday | `1 h`, `30 min` |
| force_full_scan_table | When date_filter is null and full table scan needed | FALSE |
| absolute_lower_threshold | Hard floor (alert if below) | `0` |
| absolute_upper_threshold | Hard ceiling (alert if above) | `1000` |
| relative_percentage_threshold | % variation vs avg (e.g., `5`, `5-`, `5+`) | `60-` means alert on 60% decrease |
| flow_validation | Group ID for multi-step flow alerts | `revenue` |
| flow_step_number | Step order (starting at 1) | `1` |
| flow_threshold | Max % difference allowed between steps | `5` |
| seasonality | Days between comparisons (0 = same hour prev periods) | `14` |
| data_points | Number of periods for average calculation (default 30) | `14` |

## Examples

### Rate-based alert (client exceptions)
```
validation_name: [Client Foundations] Client Exception Rate too high
aggregation_expression: SAFE_DIVIDE(COUNT(DISTINCT IF(action='desync',user_id,NULL)), COUNT(DISTINCT IF(action='active',user_id,NULL)))
date_filter: collector_time
frequency: 1 h
absolute_upper_threshold: 0.033
```

### Volume alert (reward link abuse)
```
validation_name: [COMMUNITY] - Lots of users getting too many rolls from Reward Links
table: dwh-prod-tophat.STD_tophat.sys_gti_nodedup
aggregation_expression: COUNT(DISTINCT user_id)
where_condition: build_type = 1 AND item_quantity >= 150 AND LOWER(transaction_subtype) = 'rewardlinkreward' AND LOWER(item_name) = 'roll'
date_filter: collector_time
frequency: 4 h
absolute_upper_threshold: 1000
```

### Relative threshold alert (roll interactions drop)
```
validation_name: [Core & Meta] Total Roll Interactions
aggregation_expression: COUNT(DISTINCT event_id)
dimension_1: sys_platform
where_condition: build_type = 1 AND turn_type = 'roll' AND sys_platform IN ('android','ios')
date_filter: collector_time
frequency: 1 h
relative_percentage_threshold: 60-
seasonality: 14
data_points: 14
```

### Custom query alert (missing data)
```
validation_name: [CS] - Missing data in table
custom_query: <full SQL returning validation_date, dimension_1_result, dimension_2_result, aggregation_result>
frequency: 24 h
absolute_upper_threshold: 0.9
```

## Designing Lifecycle Alerts

When designing alerts for new users or reactivations:
1. Define the metric clearly (e.g., daily reactivation volume, D7 retention rate)
2. Choose appropriate thresholds based on historical variance
3. Use `relative_percentage_threshold` with seasonality for metrics with weekly patterns
4. Use `recovery_alert: TRUE` to avoid alert fatigue
5. Set `data_points` to match the comparison window (14 for weekly seasonality, 30 for daily)
6. Always filter suspicious users in the `where_condition`
