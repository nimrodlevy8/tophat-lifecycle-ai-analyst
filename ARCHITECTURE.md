# BigQuery AI Agent - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Query                            │
│          "Show top 10 products by revenue"                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Claude Opus 4.6                            │
│                                                              │
│  - Understands natural language                              │
│  - Plans multi-step analysis                                 │
│  - Writes SQL queries                                        │
│  - Interprets results                                        │
│  - Generates insights                                        │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             │ Tool Call 1                │ Tool Call 2
             ▼                            ▼
┌──────────────────────────┐   ┌──────────────────────────────┐
│  query_bigquery()        │   │  create_visualization()      │
│                          │   │                              │
│  - Execute SQL           │   │  - Parse data                │
│  - Return results        │   │  - Generate charts           │
│  - Format as JSON        │   │  - Save to file              │
└──────────┬───────────────┘   └──────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────────┐   ┌──────────────────────────────┐
│   Google BigQuery        │   │   Matplotlib/Seaborn         │
│                          │   │                              │
│  - Execute queries       │   │  - Bar charts                │
│  - Return data           │   │  - Line charts               │
│  - Handle large datasets │   │  - Pie charts                │
└──────────────────────────┘   │  - Scatter plots             │
                               └──────────────────────────────┘
```

## Component Details

### 1. User Interface Layer

**Input**: Natural language queries
- "Show me sales by region"
- "Analyze customer churn rate"
- "Create a dashboard of top metrics"

**Output**:
- Analysis text
- Generated visualizations
- Actionable insights

### 2. Claude AI Agent

**Model**: Claude Opus 4.6
- Context window: 200K tokens (1M in beta)
- Max output: 128K tokens
- Adaptive thinking enabled

**Capabilities**:
- SQL query generation
- Data analysis
- Pattern recognition
- Insight generation
- Recommendation synthesis

**Tool Runner (Beta)**:
- Automatically manages tool execution
- Handles multi-step workflows
- No manual loop required

### 3. BigQuery Tool

```python
@beta_tool
def query_bigquery(sql_query: str, description: str) -> str:
    """Execute SQL against BigQuery"""
```

**Features**:
- Execute arbitrary SQL
- Return results as JSON
- Include summary statistics
- Error handling

**Authentication**:
- Service account credentials
- OAuth 2.0
- Project-scoped access

### 4. Visualization Tool

```python
@beta_tool
def create_visualization(
    data_json: str,
    chart_type: str,
    x_column: str,
    y_column: str,
    title: str,
    filename: str = None
) -> str:
```

**Supported Chart Types**:
- Bar charts
- Line charts
- Scatter plots
- Pie charts

**Output**:
- High-resolution PNG (300 DPI)
- Publication-quality styling
- Auto-generated filenames

## Data Flow

### Example: "Top 10 Products by Revenue"

```
1. User Query
   ↓
2. Claude interprets → "Need sales data grouped by product"
   ↓
3. Tool Call: query_bigquery(
      sql_query="SELECT product, SUM(revenue) FROM sales GROUP BY product LIMIT 10",
      description="Top products"
   )
   ↓
4. BigQuery executes → Returns JSON data
   ↓
5. Claude analyzes results → Identifies insights
   ↓
6. Tool Call: create_visualization(
      data_json=results,
      chart_type="bar",
      x_column="product",
      y_column="revenue",
      title="Top 10 Products by Revenue"
   )
   ↓
7. Chart generated and saved
   ↓
8. Claude provides final analysis with insights
```

## Tool Runner Flow

```python
# Automatic agentic loop
runner = client.beta.messages.tool_runner(
    model="claude-opus-4-6",
    tools=[query_bigquery, create_visualization],
    messages=[{"role": "user", "content": user_query}]
)

# Iterates automatically until task complete
for message in runner:
    # Process each message from Claude
    pass
```

**Advantages**:
- No manual loop management
- Automatic tool execution
- Built-in error handling
- Type-safe tool inputs

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Environment Variables                      │
│                                                              │
│  ANTHROPIC_API_KEY          → Claude API                     │
│  GCP_PROJECT_ID             → BigQuery Project               │
│  GOOGLE_APPLICATION_CREDS   → Service Account Key            │
└─────────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  Credential Management                       │
│                                                              │
│  • Service account with minimal permissions                  │
│  • Keys stored outside version control                       │
│  • Scoped BigQuery access only                               │
└─────────────────────────────────────────────────────────────┘
```

**Best Practices**:
1. Use service accounts (not user credentials)
2. Grant least privilege access
3. Store credentials in `.env` (never commit)
4. Rotate keys regularly
5. Monitor BigQuery usage

## Extension Points

### Add New Tools

```python
@beta_tool
def export_to_sheets(data_json: str, sheet_name: str) -> str:
    """Export results to Google Sheets"""
    # Implementation
    pass

@beta_tool
def send_slack_notification(message: str, channel: str) -> str:
    """Send results to Slack"""
    # Implementation
    pass
```

### Add Data Sources

- PostgreSQL
- MySQL
- Snowflake
- Databricks
- CSV files
- APIs

### Add Output Formats

- PDF reports
- PowerPoint slides
- Excel workbooks
- Interactive dashboards
- Email summaries

## Performance Considerations

### BigQuery Query Optimization

```sql
-- Use partitioned tables
SELECT * FROM `project.dataset.table`
WHERE _PARTITIONDATE = '2024-01-01'

-- Limit data scanned
SELECT specific_columns FROM table
WHERE filter_condition
LIMIT 1000

-- Use clustering
SELECT * FROM `project.dataset.clustered_table`
WHERE cluster_column = 'value'
```

### Cost Management

**BigQuery**:
- First 1 TB/month free
- $5 per TB after
- Use query dry run to estimate costs

**Claude API**:
- Opus 4.6: $5 input / $25 output per 1M tokens
- Average query: 2K-10K tokens
- Use prompt caching for repeated context

### Scalability

- BigQuery handles datasets up to petabytes
- Claude handles up to 200K token context
- Tool runner manages conversation efficiently
- Visualizations generated locally

## Monitoring & Observability

```python
# Add logging
import logging
logging.basicConfig(level=logging.INFO)

# Track costs
def log_query_cost(bytes_billed):
    cost = bytes_billed / 1e12 * 5  # $5 per TB
    logging.info(f"Query cost: ${cost:.4f}")

# Monitor API usage
def log_api_tokens(response):
    logging.info(f"Tokens: {response.usage.input_tokens} in, "
                f"{response.usage.output_tokens} out")
```

## Testing Strategy

### Unit Tests
- Test each tool individually
- Mock BigQuery responses
- Verify chart generation

### Integration Tests
- Test full agent workflows
- Use test datasets
- Validate end-to-end flows

### Example
```python
def test_query_bigquery():
    result = query_bigquery(
        "SELECT 1 as test",
        "test query"
    )
    assert "data" in json.loads(result)
```

## Deployment Options

### 1. Local Development
```bash
python3 bigquery_agent.py
```

### 2. Web Application
```python
# Streamlit
import streamlit as st
st.text_input("Query:")
```

### 3. API Service
```python
# FastAPI
from fastapi import FastAPI
app = FastAPI()

@app.post("/analyze")
def analyze(query: str):
    return run_agent(query)
```

### 4. Scheduled Jobs
```bash
# Cron
0 9 * * * cd ~/bigquery-ai-agent && python3 daily_report.py
```

### 5. Slack Bot
```python
# Slack integration
@slack_app.event("message")
def handle_message(event):
    run_agent(event["text"])
```

## Future Enhancements

1. **Multi-modal output**: Generate PowerPoint, PDF reports
2. **Real-time dashboards**: Streaming data updates
3. **Collaborative analysis**: Multiple users, shared context
4. **Advanced ML**: Predictions, forecasting, anomaly detection
5. **Voice interface**: Natural language voice queries
6. **Mobile app**: On-the-go data access

## References

- [Claude API Documentation](https://docs.anthropic.com/)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [Tool Use Patterns](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Python Tool Runner (Beta)](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
