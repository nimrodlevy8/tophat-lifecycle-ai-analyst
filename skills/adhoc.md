# Ad Hoc Question Answering

Fast, accurate answers to stakeholder questions. This is the most common function — someone on Lifecycle or EE pings you with a question and needs an answer, not a project.

## Methodology

1. **Clarify the question**: Restate it to confirm scope. Identify the metric, time range, and segments involved.
2. **Check metric definitions**: Look up `context/methodology/metric_definitions.md` to use canonical definitions.
3. **Find or adapt a template**: Check `context/templates/` for an existing query that fits. Adapt rather than write from scratch.
4. **Query BigQuery**: Run the query. Include relevant segment cuts (tenure, activity segment, geo) unless the stakeholder asked for aggregate only.
5. **Interpret**: Don't just return numbers. Compare to benchmarks (`context/domain/benchmarks.md`), call out anything surprising, and note if the result is directionally actionable.
6. **Respond concisely**: Lead with the answer in 1-2 sentences. Follow with the data table/chart. Add a brief "what this means" if the implication isn't obvious.

## Guidelines
- Speed matters. Don't over-engineer the query or analysis.
- If the answer requires >2 queries, consider whether this is actually a deep dive.
- Default time range: last 30 days, unless specified.
- Always show sample sizes alongside rates/percentages.
- If the data doesn't exist or the question is ambiguous, say so immediately rather than guessing.

<!-- TODO: Add common stakeholder question patterns and their standard query approaches -->
<!-- Feed me: examples of ad hoc questions you've answered, with the queries you used -->
