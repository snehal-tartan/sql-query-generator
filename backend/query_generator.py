import os
import openai
import sqlparse
import re
from .database import get_engine, get_schema
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPEN_AI_API_KEY")


def clean_sql_output(response_text):
    """Removes markdown formatting from the SQL output."""
    clean_query = re.sub(r'```sql\n(.*?)```', r'\1', response_text, flags=re.DOTALL)
    clean_query = re.sub(r'```\n(.*?)```', r'\1', clean_query, flags=re.DOTALL)
    sql_match = re.search(r"\bSELECT[\s\S]*?;", clean_query, re.IGNORECASE)
    return sql_match.group(0) if sql_match else clean_query.strip()


def validate_sql_query(sql_query):
    """Validates the SQL query syntax before execution."""
    try:
        parsed = sqlparse.parse(sql_query)
        if not parsed:
            return False, "Invalid SQL syntax."
        return True, None
    except Exception as e:
        return False, str(e)
    

def generate_sql_query(n1_query: str):
    """Converts a natural language query to an SQL query"""
    schema = get_schema()
    if not schema:
        print("Warning: Empty schema retrieved from database")
    schema_text = "\n".join([f"{table}: {', '.join(columns)}" for table, columns in schema.items()])

    prompt = f"""
    Given the following MySQL DDL, read and understand the schema carefully before generating the SQL query:

Generate a single SQL query that strictly adheres to these requirements:

1. Syntax & Style:
- Use standard MySQL 8.0+ syntax
- Format with proper indentation and line breaks
- Include explicit table aliases (e.g., `customers c`)
- End with a semicolon

2. JOIN Requirements:
- Use explicit JOIN types (INNER, LEFT, RIGHT, etc.)
- Include complete JOIN conditions with all relevant keys
- Avoid implicit/comma joins

3. Column Specifications:
- Qualify all columns with table aliases
- Provide meaningful column aliases for calculations/expressions
- Maintain column naming consistency (snake_case)

4. Filtering & Organization:
- Include appropriate WHERE clauses for filtering
- Use proper GROUP BY if aggregating
- Add HAVING for aggregate filters if needed
- Include ORDER BY when sequence matters

If the request is unclear, invalid, or unrelated to SQL query generation, respond only with:
ERROR: Please provide the specific request or details about the SQL query you need.

Return the SQL query only, with no additional explanations or comments.

    Database Schema:
    {schema_text}

    User Request: {n1_query}

    Please provide only the SQL query without any explanations or additional text.
    """

    def _call_model(model_name: str):
        return openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a SQL optimization expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

    try:
        try_order = ["gpt-4o", "gpt-4", "gpt-4o-mini", "gpt-3.5-turbo"]
        last_err = None
        for model_name in try_order:
            try:
                response = _call_model(model_name)
                raw_sql_query = response.choices[0].message.content.strip()
                print(f"[DEBUG] Model {model_name} returned: {raw_sql_query[:200]}")
                clean_query = clean_sql_output(raw_sql_query)
                print(f"[DEBUG] Cleaned SQL: {clean_query}")
                if clean_query:
                    return clean_query
            except Exception as inner_e:
                last_err = inner_e
                continue
        if last_err:
            print(f"Error generating SQL query (all models failed): {last_err}")
        return None
    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return None
    

def suggest_index(sql_query: str):
    """Suggests indexes for the executed SQL query"""
    engine = get_engine()
    if engine is None:
        return "Database not connected. Cannot generate execution plan."

    try:
        with engine.connect() as connection:
            explain_query = f"EXPLAIN {sql_query}"
            result = connection.execute(text(explain_query))
            execution_plan = result.fetchall()
        return "consider adding an index on Frequency used WHERE condition"
    except Exception as e:
        return f"Could not generate execution plan: {e}"


def execute_query(sql_query: str):
    """Executes the SQL query and returns the results."""
    print(f"[DEBUG] Executing SQL: {sql_query}")
    engine = get_engine()
    if engine is None:
        print("[ERROR] Database engine is None")
        return None

    is_valid, error_msg = validate_sql_query(sql_query)
    if not is_valid:
        print(f"[ERROR] SQL validation failed: {error_msg}")
        return None
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            try:
                fetched_results = result.fetchall()
                print(f"[DEBUG] Fetched {len(fetched_results)} rows")
            except Exception:
                print("[DEBUG] fetchall() not supported, returning empty list")
                fetched_results = []

        index_suggestion = suggest_index(sql_query)
        return {"result": fetched_results, "optimization_tips": index_suggestion}
    except SQLAlchemyError as e:
        print(f"[ERROR] SQLAlchemyError: {e}")
        return None


