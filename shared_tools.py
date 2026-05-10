"""
Shared tools and clients used by all agents
"""
import os
import json
from datetime import datetime
import anthropic
from anthropic import beta_tool
from google.cloud import bigquery
import google.auth
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

load_dotenv()


def get_bigquery_client():
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("Please set GCP_PROJECT_ID environment variable")
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    return bigquery.Client(credentials=credentials, project=project_id)


bq_client = get_bigquery_client()
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


@beta_tool
def query_bigquery(
    sql_query: str,
    description: str = "Query results"
) -> str:
    """
    Execute a SQL query against BigQuery and return the results.

    Args:
        sql_query: The SQL query to execute
        description: A brief description of what this query does

    Returns:
        JSON string containing the query results
    """
    try:
        print(f"\n🔍 Executing BigQuery: {description}")
        print(f"SQL: {sql_query}\n")

        query_job = bq_client.query(sql_query)
        results = query_job.result()
        df = results.to_dataframe()

        MAX_ROWS = 500
        truncated = len(df) > MAX_ROWS
        display_df = df.head(MAX_ROWS) if truncated else df

        result_data = {
            "row_count": len(df),
            "rows_returned": len(display_df),
            "truncated": truncated,
            "columns": df.columns.tolist(),
            "data": display_df.to_dict('records'),
            "summary_stats": df.describe().to_dict() if len(df) > 0 else {}
        }

        output = json.dumps(result_data, indent=2, default=str)

        MAX_CHARS = 100_000
        if len(output) > MAX_CHARS:
            further_limit = max(10, MAX_ROWS // 4)
            display_df = df.head(further_limit)
            result_data["rows_returned"] = len(display_df)
            result_data["truncated"] = True
            result_data["data"] = display_df.to_dict('records')
            result_data["note"] = f"Results were large; showing first {further_limit} rows. Use more specific queries or aggregations to reduce data size."
            output = json.dumps(result_data, indent=2, default=str)

        return output

    except Exception as e:
        error_msg = f"Error executing BigQuery: {str(e)}"
        print(f"❌ {error_msg}")
        return json.dumps({"error": error_msg})


@beta_tool
def create_visualization(
    data_json: str,
    chart_type: str,
    x_column: str,
    y_column: str,
    title: str,
    filename: str = None
) -> str:
    """
    Create a visualization from data and save it to a file.

    Args:
        data_json: JSON string containing the data (from query_bigquery)
        chart_type: Type of chart ('bar', 'line', 'scatter', 'pie', 'heatmap', 'grouped_bar', 'stacked_bar')
        x_column: Column name for x-axis
        y_column: Column name for y-axis
        title: Chart title
        filename: Output filename (default: auto-generated)

    Returns:
        Path to the saved chart file
    """
    try:
        data = json.loads(data_json)
        if "error" in data:
            return f"Cannot create visualization: {data['error']}"

        df = pd.DataFrame(data["data"])

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chart_{chart_type}_{timestamp}.png"

        sns.set_style("whitegrid")
        plt.figure(figsize=(12, 6))

        if chart_type == "bar":
            plt.bar(df[x_column], df[y_column])
            plt.xlabel(x_column)
            plt.ylabel(y_column)
        elif chart_type == "line":
            plt.plot(df[x_column], df[y_column], marker='o')
            plt.xlabel(x_column)
            plt.ylabel(y_column)
        elif chart_type == "scatter":
            plt.scatter(df[x_column], df[y_column])
            plt.xlabel(x_column)
            plt.ylabel(y_column)
        elif chart_type == "pie":
            plt.pie(df[y_column], labels=df[x_column], autopct='%1.1f%%')
        elif chart_type == "heatmap":
            pivot = df.pivot_table(index=x_column, columns=y_column, aggfunc='size', fill_value=0)
            sns.heatmap(pivot, annot=True, fmt='g', cmap='YlOrRd')
        elif chart_type in ("grouped_bar", "stacked_bar"):
            pivot = df.pivot_table(index=x_column, columns=y_column, aggfunc='sum', fill_value=0)
            pivot.plot(kind='bar', stacked=(chart_type == "stacked_bar"), ax=plt.gca())
            plt.xlabel(x_column)
        else:
            return f"Unsupported chart type: {chart_type}"

        plt.title(title)
        plt.tight_layout()

        output_path = os.path.join(os.getcwd(), filename)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"📊 Chart saved to: {output_path}")
        return f"Chart successfully saved to: {output_path}"

    except Exception as e:
        error_msg = f"Error creating visualization: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg
