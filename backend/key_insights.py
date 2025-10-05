import os
import openai
import pandas as pd
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPEN_AI_API_KEY")


def generate_key_insights(df: pd.DataFrame, chart_type: str = None) -> str | None:
    """
    Generate concise key insights from the data
    
    Args:
        df: pandas DataFrame containing the query results
        chart_type: Optional chart type for context (bar, line, pie, scatter)
    
    Returns:
        String containing 3-4 bullet-pointed insights, or None if generation fails
    """
    try:
        if df.empty:
            return "No data available for analysis."
        
        # Get basic info about the dataset
        row_count = len(df)
        col_count = len(df.columns)
        columns = df.columns.tolist()
        
        # Get a preview of the data (first 3 rows)
        csv_preview = df.head(3).to_csv(index=False)
        
        # Get summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        summary_stats = ""
        if numeric_cols:
            summary_stats = df[numeric_cols].describe().to_string()
        
        # Build context-aware prompt
        chart_context = f"The data will be visualized as a {chart_type} chart." if chart_type else ""
        
        prompt = f"""
Analyze this dataset and provide 3-4 concise, actionable insights.

Dataset Info:
- Rows: {row_count}, Columns: {col_count}
- Column names: {', '.join(columns)}
{chart_context}

Data Preview (first 3 rows):
{csv_preview}

{f"Summary Statistics:{summary_stats}" if summary_stats else ""}

Provide exactly 3-4 short insights (1-2 sentences each). Focus on:
1. Key trends or patterns
2. Notable values (highest, lowest, or interesting outliers)
3. Business implications or actionable takeaways

Format as bullet points starting with •
Keep each insight concise and specific to this data.
"""
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a data analyst providing brief, actionable insights. Be concise and specific."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        insights = response.choices[0].message.content.strip()
        return insights
        
    except Exception as e:
        print(f"[ERROR] Failed to generate insights: {e}")
        return None
