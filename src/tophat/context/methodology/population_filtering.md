# Population Filtering Rules

## Mandatory: Suspicious User Exclusion

ALL queries involving reactivations or new users (funnel analysis) MUST filter out suspicious users.

### Two sources of suspicious users:

1. **Suspicious at creation** — `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation`
   - Join on `user_id`
   - Flag: `is_ever_suspicious_at_creation = TRUE`

2. **Untrusted devices** — `dwh-prod-core.pub.v_d_publisher`
   - Join on `lt_first_publisher_name = publisher_name`
   - Flag: `publisher_name = 'untrusted devices'`

### Standard Implementation

```sql
LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` AS f_suspicious_at_creation 
  ON f_suspicious_at_creation.user_id = <main_table>.user_id
LEFT JOIN `dwh-prod-core.pub.v_d_publisher` AS v_d_publisher 
  ON <main_table>.lt_first_publisher_name = v_d_publisher.publisher_name
```

### Flagging (show both views)
```sql
CASE WHEN (f_suspicious_at_creation.is_ever_suspicious_at_creation 
       OR v_d_publisher.publisher_name = 'untrusted devices') 
     THEN 'suspicious' ELSE 'rest' END AS suspicious
```

### Rule
- Always show BOTH views (suspicious vs rest) so contamination % is visible
- For performance analysis, use the 'rest' population as the clean view
- Report the % of total population that is suspicious
