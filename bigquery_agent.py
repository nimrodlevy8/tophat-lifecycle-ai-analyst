"""
BigQuery AI Agent - Generic data querying, insights, and visualizations
"""
import sys
from shared_tools import claude_client, query_bigquery, create_visualization


def run_agent(user_query: str) -> None:
    print(f"\n{'='*80}")
    print(f"BigQuery AI Agent")
    print(f"{'='*80}")
    print(f"Query: {user_query}\n")

    system_prompt = """You are an expert data analyst with access to BigQuery.

Your role is to:
1. Understand the user's data analysis request
2. Query BigQuery to get the necessary data
3. Analyze the results and generate insights
4. Create visualizations when appropriate
5. Provide clear, actionable recommendations

When writing SQL queries:
- Use standard SQL syntax
- Be specific about which dataset and table to query
- Include appropriate WHERE clauses and aggregations
- Limit results to a reasonable size (e.g., TOP 100) unless asked otherwise

When creating visualizations:
- Choose the appropriate chart type for the data
- Use clear, descriptive titles
- Label axes properly

Always explain your findings in clear, business-friendly language."""

    runner = claude_client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        system=system_prompt,
        tools=[query_bigquery, create_visualization],
        messages=[{"role": "user", "content": user_query}],
    )

    print("\n💭 Claude's Analysis:\n")
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                print()

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    example_queries = [
        "Query the bigquery-public-data.usa_names.usa_1910_2013 dataset and "
        "show me the top 10 most popular baby names in 2013. Create a bar chart.",

        "Analyze the trend of the name 'Emma' over time from the same dataset. "
        "Create a line chart showing the count by year.",
    ]

    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        print("\nExample Queries:")
        for i, query in enumerate(example_queries, 1):
            print(f"{i}. {query}")
        print("\n" + "="*80)
        user_input = input("\nEnter your query (or press Enter for example 1): ").strip()
        if not user_input:
            user_input = example_queries[0]

    run_agent(user_input)
