from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..database import is_connected
from ..query_generator import generate_sql_query, execute_query
import pandas as pd
from io import StringIO


router = APIRouter(prefix="", tags=["query"])


class QueryRequest(BaseModel):
    query: str


@router.post("/generate_sql")
async def generate_sql(request: QueryRequest):
    if not is_connected():
        raise HTTPException(status_code=400, detail="Database not connected. Please connect to database first.")
    sql_query = generate_sql_query(request.query)
    if not sql_query:
        return {"error": "Failed to generate SQL query."}
    return {"sql_query": sql_query}


@router.post("/execute_sql")
async def execute_sql(request: QueryRequest):
    if not is_connected():
        raise HTTPException(status_code=400, detail="Database not connected. Please connect to database first.")
    
    print(f"[ROUTER DEBUG] Received query: {request.query[:100]}")
    results = execute_query(request.query)
    
    if results is None:
        print("[ROUTER ERROR] execute_query returned None")
        return {"error": "Error executing the SQL query. Check backend logs for details."}

    # Convert SQLAlchemy Row objects to dicts for JSON serialization
    raw_rows = results.get("result", [])
    print(f"[ROUTER DEBUG] Raw rows type: {type(raw_rows)}, count: {len(raw_rows) if raw_rows else 0}")
    
    serialized_rows = []
    for row in raw_rows:
        if hasattr(row, "_mapping"):
            serialized_rows.append(dict(row._mapping))
        else:
            try:
                serialized_rows.append(dict(row))
            except Exception as e:
                print(f"[ROUTER WARNING] Failed to dict(row): {e}, falling back to list")
                serialized_rows.append({"values": list(row)})

    print(f"[ROUTER DEBUG] Returning {len(serialized_rows)} serialized rows")
    return {"results": serialized_rows, "optimization_tips": results.get("optimization_tips", "")}


@router.post("/download_csv")
async def download_csv(request: QueryRequest):
    if not is_connected():
        raise HTTPException(status_code=400, detail="Database not connected. Please connect to database first.")
    
    results = execute_query(request.query)
    
    if results is None:
        raise HTTPException(status_code=500, detail="Error executing the SQL query.")
    
    # Convert SQLAlchemy Row objects to dicts
    raw_rows = results.get("result", [])
    serialized_rows = []
    for row in raw_rows:
        if hasattr(row, "_mapping"):
            serialized_rows.append(dict(row._mapping))
        else:
            try:
                serialized_rows.append(dict(row))
            except Exception:
                serialized_rows.append({"values": list(row)})
    
    if not serialized_rows:
        raise HTTPException(status_code=404, detail="No data to download.")
    
    # Convert to DataFrame and then to CSV
    df = pd.DataFrame(serialized_rows)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=query_results.csv"}
    )


