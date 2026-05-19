# Analysis Standards

## Approach
- Be hypothesis-driven. Ask the questions before running into analysis. Know what's being asked and the logic behind it.
- Answer product questions first. Exploration/deviation is fine but main questions take priority.
- Every analysis must be critical on results. If something is unknown, say it's unknown. If there's no clear conclusion, say so. Never fabricate or satisfy the prompt.

## Quantification & Recommendations
- If things are good or bad, quantify it.
- Provide a recommendation and bottom line.
- Commentary on each chart: explain what the chart shows AND the conclusions.

## Segmentation
- Explain what led to a segmentation choice and why it matters.
- If using a new segmentation not from established context, justify and approve it before using in analysis.

## Normalization
- Totals are fine for general reporting. For performance/behavior analysis, normalize.
- If audience shifts between timeframes, raw totals are misleading (e.g., total revenue from reactivations drops because reactivation volume dropped — that doesn't tell you anything about per-user performance).

## Population Filtering
- Always filter out: `publisher_name = 'untrusted_device'`, `is_cheater = true`, suspicious users.
- But always show BOTH views (with and without) so contamination is visible.
- Report % of population these excluded users represent.

## Thresholds & Caution
- Anything showing >20% increase or decrease is a big deal. Double-check before presenting to stakeholders.
- Don't jump to conclusions. Check yourself. Maintain business and product orientation on what the data shows.
