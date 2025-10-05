import os
import io
import base64
import openai
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPEN_AI_API_KEY")


def convert_dataframe_to_csv(df: pd.DataFrame) -> str:
    return df.to_csv(index=False)


def generate_data_extraction_script(csv_data: str, chart_type: str) -> str | None:
    """Generate Python script to extract data from CSV using pandas"""
    csv_lines = csv_data.split('\n')
    csv_preview = '\n'.join(csv_lines[:min(4, len(csv_lines))])  # Header + first 3 data rows
    total_rows = len(csv_lines) - 1  # Subtract 1 for header

    prompt = f"""
    Generate a Python script that reads CSV data from a variable named `csv_data`.
    
    CSV Data Preview (showing first few rows of {total_rows} total rows):
    {csv_preview}
    
    CRITICAL REQUIREMENTS:
    1. Use: from io import StringIO
    2. Use: df = pd.read_csv(StringIO(csv_data))
    3. Handle CSV parsing correctly - the data has headers and multiple columns
    4. Extract information and create a result dictionary
    5. IMPORTANT: The CSV contains {total_rows} total rows of data, not just the preview shown
    
    The script should:
    1. Import StringIO from io module
    2. Read CSV data using pd.read_csv(StringIO(csv_data))
    3. Extract column headers using df.columns.tolist()
    4. Identify numeric and categorical columns
    5. Create a result dictionary with the extracted information
    
    Return ONLY the Python code. The code should create a variable called 'result' containing:
    - 'headers': list of column names
    - 'data': the DataFrame
    - 'numeric_cols': list of numeric column names  
    - 'categorical_cols': list of categorical column names
    - 'shape': tuple of (rows, columns)
    
    Example structure:
    result = {{
        'headers': df.columns.tolist(),
        'data': df,
        'numeric_cols': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_cols': df.select_dtypes(include=['object']).columns.tolist(),
        'shape': df.shape
    }}
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data processing expert. Generate pandas code to extract data from CSV."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )
        generated_code = response.choices[0].message.content.strip()
        if "```python" in generated_code:
            generated_code = generated_code.split("```python")[1].split("```")[0]
        elif "```" in generated_code:
            generated_code = generated_code.split("```")[1].split("```")[0]
        return generated_code
    except Exception:
        return None


def generate_graph_creation_script(extracted_data: dict, chart_type: str) -> str | None:
    """Generate script to create the actual graph"""
    prompt = f"""
Create a {chart_type} chart using matplotlib with the following data structure:

AVAILABLE VARIABLES:
- df: The main DataFrame containing the data
- extracted_data: Dictionary with keys: {list(extracted_data.keys()) if extracted_data else 'None'}

DATA STRUCTURE:
{extracted_data}

CRITICAL REQUIREMENTS:
1. Access the main DataFrame using: df = extracted_data['data']
2. Create figure: fig, ax = plt.subplots(figsize=(16, 10))
3. Use the COMPLETE dataset - all rows and appropriate columns
4. Variable names available: df, plt, pd, np, extracted_data
5. The 'fig' variable MUST be created and remain accessible
6. Add proper labels, title, and styling
7. End with: plt.tight_layout()
8. DO NOT use plt.show() or return statements
    
    Chart Type Guidelines:
    - BAR: Use ax.bar() with categorical data on x-axis, numeric on y-axis
    - LINE: Use ax.plot() with markers for trends over categories/time
    - PIE: Use ax.pie() for proportions
    - SCATTER: Use ax.scatter() for correlations between numeric columns
    
    Return ONLY the Python code that creates the chart.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a graph generation expert. Generate matplotlib code to create graphs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1500
        )
        generated_code = response.choices[0].message.content.strip()
        if "```python" in generated_code:
            generated_code = generated_code.split("```python")[1].split("```")[0]
        elif "```" in generated_code:
            generated_code = generated_code.split("```")[1].split("```")[0]
        return generated_code
    except Exception:
        return None


def render_figure_to_png_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def generate_graph_png_base64(df: pd.DataFrame, chart_type: str, chart_name: str) -> str | None:
    try:
        # Step 1: Convert to CSV
        csv_data = convert_dataframe_to_csv(df)
        extraction_script = generate_data_extraction_script(csv_data, chart_type)
        if not extraction_script:
            return None

        # Step 2: Execute extraction script
        safe_globals = {
            'pd': pd,
            'np': np,
            'csv_data': csv_data,
            'StringIO': __import__('io').StringIO,
            'result': None
        }
        exec(extraction_script, safe_globals)
        extracted_data = safe_globals.get('result') or {}
        if not isinstance(extracted_data, dict) or 'data' not in extracted_data:
            return None

        # Step 3: Generate graph creation script
        graph_script = generate_graph_creation_script(extracted_data, chart_type)
        if not graph_script:
            return None

        # Step 4: Execute graph creation
        graph_globals = {
            'plt': plt,
            'pd': pd,
            'np': np,
            'extracted_data': extracted_data,
            'df': extracted_data['data'],
            'fig': None
        }
        plt.rcParams['figure.figsize'] = (14, 8)
        plt.rcParams['font.size'] = 12
        exec(graph_script, graph_globals)
        fig = graph_globals.get('fig')
        if fig is None:
            return None
        fig.set_size_inches(14, 8)
        return render_figure_to_png_base64(fig)
    except Exception:
        return None


