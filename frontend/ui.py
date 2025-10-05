import streamlit as st
import pandas as pd
import requests
import base64
import os
from dotenv import load_dotenv, find_dotenv
import re

# Load env from project root (finds nearest .env up the tree)
load_dotenv(find_dotenv())
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def connect_form():
    st.header("Database Connection")
    with st.form("db_form"):
        host = st.text_input("Host", value="localhost")
        user = st.text_input("User")
        password = st.text_input("Password", type="password")
        database = st.text_input("Database")
        port = st.number_input("Port", value=3306, min_value=1, max_value=65535)
        submitted = st.form_submit_button("Connect")
        if submitted:
            resp = requests.post(f"{API_URL}/connect_database", json={
                "host": host, "user": user, "password": password, "database": database, "port": port
            })
            if resp.ok and resp.json().get("status") == "success":
                st.session_state.connected = True
                st.success("Connected")
                st.rerun()
            else:
                st.error(resp.json())


def run():
    st.set_page_config(page_title="SQL Query Generator", layout="wide")
    st.title("SQL Query Generator")

    if "connected" not in st.session_state:
        st.session_state.connected = False

    if not st.session_state.connected:
        connect_form()
        return

    st.subheader("Generate / Execute SQL")
    query = st.text_area("Natural language query or SQL", height=100)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate SQL"):
            r = requests.post(f"{API_URL}/generate_sql", json={"query": query})
            st.code(r.json().get("sql_query", ""), language="sql")
    with col2:
        if st.button("Execute SQL"):
            if not query or not query.strip():
                st.warning("Please enter a query first.")
            else:
                with st.spinner("Executing query..."):
                    def is_likely_sql(text: str) -> bool:
                        # Check if it's actual SQL, not just starts with SQL-like words
                        text_stripped = (text or "").strip().upper()
                        # Must start with SQL keyword AND contain FROM/INTO/TABLE/SET
                        if any(text_stripped.startswith(kw) for kw in ["SELECT ", "INSERT ", "UPDATE ", "DELETE ", "WITH ", "SHOW ", "DESCRIBE ", "EXPLAIN "]):
                            return True
                        # CREATE/ALTER/DROP must be followed by TABLE/DATABASE/INDEX etc
                        if re.match(r"^(CREATE|ALTER|DROP)\s+(TABLE|DATABASE|INDEX|VIEW|PROCEDURE|FUNCTION)", text_stripped):
                            return True
                        return False

                    sql_to_run = query.strip()
                    
                    # ALWAYS generate SQL first if it doesn't look like SQL
                    if not is_likely_sql(sql_to_run):
                        st.info("Detected natural language query. Generating SQL...")
                        gr = requests.post(f"{API_URL}/generate_sql", json={"query": query})
                        if not gr.ok:
                            st.error(f"Failed to generate SQL. Status: {gr.status_code}")
                            return
                        response_data = gr.json() or {}
                        sql_to_run = response_data.get("sql_query", "").strip()
                        
                        if not sql_to_run or response_data.get("error"):
                            st.error(response_data.get("error") or "Failed to generate SQL.")
                            return
                        
                        st.markdown("**Generated SQL:**")
                        st.code(sql_to_run, language="sql")

                    # Now execute the SQL
                    st.info(f"Executing SQL query...")
                    r = requests.post(f"{API_URL}/execute_sql", json={"query": sql_to_run})
                    payload = r.json() if r.ok else {}
                    data = payload.get("results", [])
                    
                    if data:
                        st.success(f"✅ Query executed successfully! Found {len(data)} records.")
                        st.dataframe(pd.DataFrame(data), use_container_width=True)
                    else:
                        error_msg = payload.get("error", "No results returned.")
                        st.error(f"❌ {error_msg}")

    st.subheader("Generate Graph (API-driven)")
    chart_type = st.selectbox("Chart type", ["bar", "line", "pie", "scatter"]) 
    if st.button("Generate Graph Image"):
        def is_likely_sql(text: str) -> bool:
            text_stripped = (text or "").strip().upper()
            if any(text_stripped.startswith(kw) for kw in ["SELECT ", "INSERT ", "UPDATE ", "DELETE ", "WITH ", "SHOW ", "DESCRIBE ", "EXPLAIN "]):
                return True
            if re.match(r"^(CREATE|ALTER|DROP)\s+(TABLE|DATABASE|INDEX|VIEW|PROCEDURE|FUNCTION)", text_stripped):
                return True
            return False

        sql_for_graph = query
        if not is_likely_sql(query):
            gr = requests.post(f"{API_URL}/generate_sql", json={"query": query})
            if not gr.ok:
                st.error("Failed to generate SQL for graph.")
                return
            sql_for_graph = (gr.json() or {}).get("sql_query") or ""
            if not sql_for_graph:
                st.error((gr.json() or {}).get("error") or "Failed to generate SQL for graph.")
                return
            st.markdown("**Generated SQL for Graph:**")
            st.code(sql_for_graph, language="sql")

        r = requests.post(f"{API_URL}/generate_graph", json={"sql_query": sql_for_graph, "chart_type": chart_type})
        payload = r.json() if r.ok else {}
        img_b64 = payload.get("image_base64")
        if img_b64:
            st.image(base64.b64decode(img_b64))
        else:
            st.error(payload.get("error") or payload)


if __name__ == "__main__":
    run()


