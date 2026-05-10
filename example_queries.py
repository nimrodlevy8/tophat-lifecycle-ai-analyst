"""
Example queries for both agents
"""
from bigquery_agent import run_agent
from product_analyst_agent import run_product_analyst


# ── Generic BigQuery Agent examples ──────────────────────────────────────

def example_bigquery_names():
    run_agent(
        "Query the bigquery-public-data.usa_names.usa_1910_2013 dataset. "
        "Show me the top 10 most popular baby names in 2013. Create a bar chart."
    )

def example_bigquery_trend():
    run_agent(
        "Using the bigquery-public-data.usa_names.usa_1910_2013 dataset, "
        "analyze how the popularity of the name 'Emma' has changed from 1990 to 2013. "
        "Create a line chart showing the trend over time."
    )


# ── Monopoly GO! Product Analyst examples ────────────────────────────────

def example_retention_by_segment():
    run_product_analyst(
        "What does D1 and D7 retention look like by activity segment for the last 30 days?"
    )

def example_reactivation_funnel():
    run_product_analyst(
        "Show me the reactivation funnel — how many users came back last week, "
        "and what % survived to D7? Break down by inactivity length bucket."
    )

def example_arpdau_by_tenure():
    run_product_analyst(
        "Compare ARPDAU across tenure buckets for the current season. "
        "Are newer players monetizing differently?"
    )

def example_occasionals_performance():
    run_product_analyst(
        "How are Occasionals performing this month vs last month? "
        "Show retention, playtime, and segment migration rates."
    )


if __name__ == "__main__":
    print("Choose an agent and example:")
    print()
    print("── BigQuery Agent (generic) ──")
    print("  1. Top 10 baby names in 2013 (bar chart)")
    print("  2. Trend analysis for 'Emma' (line chart)")
    print()
    print("── Monopoly GO! Product Analyst ──")
    print("  3. Retention by activity segment")
    print("  4. Reactivation funnel by inactivity bucket")
    print("  5. ARPDAU by tenure bucket")
    print("  6. Occasionals month-over-month performance")
    print()
    print("  0. Exit")

    choice = input("\nEnter your choice (1-6): ").strip()

    examples = {
        "1": example_bigquery_names,
        "2": example_bigquery_trend,
        "3": example_retention_by_segment,
        "4": example_reactivation_funnel,
        "5": example_arpdau_by_tenure,
        "6": example_occasionals_performance,
    }

    if choice in examples:
        examples[choice]()
    else:
        print("Invalid choice or exiting.")
