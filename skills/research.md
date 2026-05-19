# Research

Hypothesis-driven exploration for questions like "what drives X?", "what would happen if Y?", "where's the opportunity in Z?". Research is more open-ended than a deep dive — you may not know the answer structure going in.

## Methodology

### 1. Frame the Research Question
- What are we trying to learn?
- Why does it matter? What decision will this inform?
- What's our prior belief / hypothesis?

### 2. Identify Data Sources
- Which BigQuery tables are relevant?
- Is there prior analysis in `context/past-analysis/` that provides a starting point?
- Are there external benchmarks or industry norms to compare against?

### 3. Exploratory Analysis
- Start with descriptive statistics to understand distributions.
- Look for natural clusters, breakpoints, or segments in the data.
- Correlate the variable of interest with known outcome metrics.
- Don't anchor on the first pattern you find — check at least 2-3 alternative explanations.

### 4. Hypothesis Testing
- For each hypothesis: define what the data would look like if true vs. false.
- Run the appropriate analysis (correlation, regression, segment comparison, funnel analysis).
- Report effect sizes, not just significance.

### 5. Opportunity Sizing
When relevant, quantify the opportunity:
- How many users are affected?
- What's the potential metric lift if addressed?
- How does it compare to other known opportunities?

### 6. Synthesis
- Which hypotheses were supported vs. refuted?
- What's the most important finding?
- What should we do next? (Experiment? Build? Monitor? Research further?)

## Output Format
1. **Research question** (1-2 sentences)
2. **Hypotheses** (numbered list of what we expected)
3. **Findings** (per hypothesis: supported/refuted/inconclusive + evidence)
4. **Opportunity sizing** (if applicable)
5. **Recommendation** (what to do with these findings)
6. **Open questions** (what we still don't know)

<!-- TODO: Add examples of research questions the team has explored -->
<!-- Feed me: past research decks, opportunity sizing frameworks, examples of hypothesis-driven analyses -->
