# BigQuery AI Agent

An AI-powered agent that connects to Google BigQuery, runs SQL queries, analyzes data, and generates insights with visualizations using Claude.

## Features

- 🔍 **Natural Language Queries**: Ask questions in plain English
- 📊 **Automatic Visualization**: Generates charts based on your data
- 🤖 **AI-Powered Analysis**: Claude analyzes results and provides insights
- 🔧 **Custom Tools**: BigQuery query tool and visualization tool
- 📈 **Data Analysis**: Statistical summaries and trend analysis

## Architecture

This agent uses the **Claude API with Tool Use** pattern:

1. **Custom BigQuery Tool**: Executes SQL queries against your BigQuery datasets
2. **Visualization Tool**: Creates charts using matplotlib and seaborn
3. **Tool Runner (Beta)**: Automatically handles the agentic loop
4. **Claude Opus 4.6**: Analyzes data and generates insights

## Prerequisites

- Python 3.8 or higher
- Google Cloud account with BigQuery enabled
- Service account with BigQuery permissions
- Claude API key

## Setup

### 1. Install Python Dependencies

```bash
cd ~/bigquery-ai-agent
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** > **Service Accounts**
3. Click **Create Service Account**
4. Grant these roles:
   - **BigQuery Data Viewer**
   - **BigQuery Job User**
5. Create and download a JSON key file
6. Save it somewhere secure (e.g., `~/gcp-keys/bigquery-key.json`)

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
ANTHROPIC_API_KEY=sk-ant-...
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### 4. Verify Setup

Test your BigQuery connection:

```bash
python3 -c "
from google.cloud import bigquery
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

load_dotenv()
credentials = service_account.Credentials.from_service_account_file(
    os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
)
client = bigquery.Client(credentials=credentials, project=os.getenv('GCP_PROJECT_ID'))
print('✅ BigQuery connection successful!')
"
```

## Usage

### Basic Usage

Run the agent with a natural language query:

```bash
python3 bigquery_agent.py
```

The script will prompt you for a query or use a default example.

### Example Queries

```python
# Query public dataset
"Query the bigquery-public-data.usa_names.usa_1910_2013 dataset and show me the top 10 most popular baby names in 2013. Create a bar chart."

# Trend analysis
"Analyze the trend of the name 'Emma' over time from the usa_names dataset. Create a line chart showing the count by year."

# Your own tables
"Query my sales_data.transactions table and show me total revenue by product category for the last month. Create a pie chart."
```

### Programmatic Usage

```python
from bigquery_agent import run_agent

# Run a query
run_agent("Show me the top 10 customers by revenue from my customers table")
```

## Example Output

```
================================================================================
BigQuery AI Agent
================================================================================
Query: Query the usa_names dataset and show me the top 10 most popular baby
names in 2013. Create a bar chart.

🔍 Executing BigQuery: Top 10 baby names in 2013
SQL: SELECT name, SUM(number) as total
     FROM `bigquery-public-data.usa_names.usa_1910_2013`
     WHERE year = 2013
     GROUP BY name
     ORDER BY total DESC
     LIMIT 10

💭 Claude's Analysis:

Based on the query results, here are the top 10 most popular baby names in 2013:

1. **Noah** - 18,268 babies
2. **Emma** - 20,799 babies
3. **Liam** - 18,281 babies
4. **Olivia** - 18,256 babies
5. **Mason** - 17,092 babies

The data shows Emma was the most popular name overall, with Noah leading
for boys. Let me create a visualization for you.

📊 Chart saved to: /Users/you/bigquery-ai-agent/chart_bar_20240115_143022.png

The bar chart clearly shows Emma and Noah as the dominant names, with a
gradual decrease in popularity for subsequent names. This reflects broader
naming trends where a few names capture significant market share.
================================================================================
```

## Advanced Features

### Custom Queries for Your Data

The agent can query any BigQuery table you have access to:

```python
run_agent("""
Query my company's sales_data.transactions table.
Calculate total revenue by product category for Q4 2024.
Show trends over the months October, November, and December.
Create a line chart comparing categories over time.
""")
```

### Multi-Step Analysis

Claude automatically breaks down complex requests:

```python
run_agent("""
1. Query our user_analytics table to find our top 10 power users
2. Calculate their average session duration and feature usage
3. Create visualizations showing engagement patterns
4. Provide recommendations for user retention
""")
```

### Working with Large Datasets

The agent handles pagination and aggregation:

```python
run_agent("""
Analyze our 10M+ row events table.
Find the top 5 events by frequency this month.
Show hourly distribution and create a heatmap.
""")
```

## How It Works

### 1. Tool Definitions

The agent has two custom tools defined using the `@beta_tool` decorator:

```python
@beta_tool
def query_bigquery(sql_query: str, description: str = "Query results") -> str:
    """Execute a SQL query against BigQuery"""
    # Executes query and returns results as JSON

@beta_tool
def create_visualization(data_json: str, chart_type: str, ...) -> str:
    """Create charts from data"""
    # Generates matplotlib charts
```

### 2. Agentic Loop

The tool runner automatically:
- Calls the BigQuery tool when Claude needs data
- Executes the queries and returns results
- Calls the visualization tool to create charts
- Continues until Claude has answered the question

```python
runner = claude_client.beta.messages.tool_runner(
    model="claude-opus-4-6",
    tools=[query_bigquery, create_visualization],
    messages=[{"role": "user", "content": user_query}],
)
```

### 3. Claude's Analysis

Claude:
- Writes SQL queries to get the needed data
- Analyzes the results
- Identifies patterns and insights
- Generates visualizations
- Provides actionable recommendations

## Troubleshooting

### Authentication Errors

```
google.auth.exceptions.DefaultCredentialsError
```

**Solution**: Make sure `GOOGLE_APPLICATION_CREDENTIALS` points to a valid service account JSON file.

### Permission Denied

```
403 Access Denied: BigQuery BigQuery: Permission denied
```

**Solution**: Ensure your service account has these roles:
- `roles/bigquery.dataViewer`
- `roles/bigquery.jobUser`

### Table Not Found

```
404 Not found: Table project:dataset.table
```

**Solution**: Use fully qualified table names:
```sql
`project-id.dataset.table`
```

For public datasets:
```sql
`bigquery-public-data.dataset.table`
```

## Cost Considerations

- **BigQuery**: You pay for query processing (first 1 TB/month is free)
- **Claude API**: ~$5 per million input tokens, ~$25 per million output tokens
- **Tool Runner**: Automatically manages the conversation loop efficiently

## Security Best Practices

1. **Never commit credentials**: Keep `.env` in `.gitignore`
2. **Use least privilege**: Grant only necessary BigQuery permissions
3. **Rotate keys regularly**: Regenerate service account keys periodically
4. **Monitor usage**: Set up billing alerts in Google Cloud Console

## Next Steps

### Add More Tools

Extend the agent with additional capabilities:

```python
@beta_tool
def export_to_sheets(data: str, spreadsheet_name: str) -> str:
    """Export results to Google Sheets"""
    # Implementation here

@beta_tool
def send_email_report(analysis: str, recipients: list) -> str:
    """Email analysis results"""
    # Implementation here
```

### Build a Web Interface

Create a Streamlit or Flask app:

```python
import streamlit as st
from bigquery_agent import run_agent

st.title("BigQuery AI Agent")
query = st.text_area("Ask a question about your data")
if st.button("Analyze"):
    run_agent(query)
```

### Schedule Regular Reports

Use cron or Airflow to run automated analyses:

```bash
# Daily sales report
0 9 * * * cd ~/bigquery-ai-agent && python3 bigquery_agent.py "Generate daily sales summary"
```

## Resources

- [Claude API Documentation](https://docs.anthropic.com/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)

## License

MIT
