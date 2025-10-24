import os
import sqlparse
import re
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# LangChain imports
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

from .database import get_engine, get_cached_schema, refresh_schema_cache

load_dotenv(find_dotenv())

# Load OpenAI model from environment
OPENAI_MODEL = os.getenv("OPEN_AI_MODEL")
OPENAI_API_KEY = os.getenv("OPEN_AI_API_KEY")

# Initialize LangChain components
def get_langchain_db():
    """Create LangChain SQLDatabase instance from SQLAlchemy engine"""
    engine = get_engine()
    if engine is None:
        raise ValueError("Database engine is None")
    return SQLDatabase(engine)

def get_llm():
    """Initialize OpenAI LLM - no temperature for GPT-5"""
    return ChatOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=1
    )

def generate_sql_query(n1_query: str):
    """Converts a natural language query to an SQL query using LangChain with cached schema"""
    try:
        llm = get_llm()
        
        # Get CACHED schema (no database call here!)
        schema_text = get_cached_schema()
        
        if schema_text is None:
            print("[ERROR] Schema not available. Please ensure database is connected.")
            return None
        
        print(f"[DEBUG] Using cached schema ({len(schema_text)} characters)")
        
        # Custom prompt template
        template = """
Given the following MySQL DDL, read and understand the schema carefully before generating the SQL query:

Generate a single SQL query that strictly adheres to these requirements:

1. Syntax & Style:
- Use standard MySQL 8.0+ syntax
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

Return the SQL query only, with no additional explanations or comments or any special characters.

Database Schema:
{schema}

User Request: {question}

Please provide only the SQL query without any explanations or additional text.
"""
        
        prompt = PromptTemplate(
            input_variables=["schema", "question"],
            template=template
        )
        
        # Create chain with custom prompt
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Generate SQL query (only LLM call, no schema fetch!)
        response = chain.invoke({
            "schema": schema_text,
            "question": n1_query
        })
        
        sql_query = response["text"].strip()
        print(f"[DEBUG] Generated SQL: {sql_query}")
        
        return sql_query
        
    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return None


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

        return {"result": fetched_results}
    except SQLAlchemyError as e:
        print(f"[ERROR] SQLAlchemyError: {e}")
        return None


def validate_sql_query(sql_query):
    """Validates the SQL query syntax before execution."""
    try:
        # Basic parsing validation
        parsed = sqlparse.parse(sql_query)
        if not parsed:
            return False, "Invalid SQL syntax."
        return True, None
    except Exception as e:
        return False, str(e)

# Additional utility functions

def get_schema_info():
    """Get cached schema information"""
    return get_cached_schema()


def get_table_names():
    """Get list of table names using LangChain"""
    try:
        db = get_langchain_db()
        return db.get_usable_table_names()
    except Exception as e:
        print(f"Error getting table names: {e}")
        return None


def force_refresh_schema():
    """Force refresh the schema cache (use after ALTER TABLE, CREATE TABLE, etc.)"""
    return refresh_schema_cache()


# Temporary debug code
if __name__ == "__main__":
    print("Testing LangChain integration with cached schema...")
    print("\n=== Table Names ===")
    print(get_table_names())
    print("\n=== Cached Schema Info ===")
    print(get_schema_info())