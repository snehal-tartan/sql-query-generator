from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
from ..database import is_connected
from ..query_generator import execute_query
from ..graph_generator import generate_graph_png_base64
from ..key_insights import generate_key_insights


router = APIRouter(prefix="", tags=["graph"])


class GraphRequest(BaseModel):
    sql_query: str
    chart_type: str
    chart_name: str | None = None


@router.post("/generate_graph")
async def generate_graph_route(request: GraphRequest):
    if not is_connected():
        raise HTTPException(status_code=400, detail="Database not connected. Please connect to database first.")

    exec_result = execute_query(request.sql_query)
    if exec_result is None:
        return {"error": "Error executing the SQL query."}

    rows = exec_result["result"]
    if hasattr(rows, "__iter__") and rows:
        # Convert row sequence to DataFrame
        serialized_rows = []
        for row in rows:
            if hasattr(row, "_mapping"):
                serialized_rows.append(dict(row._mapping))
            else:
                try:
                    serialized_rows.append(dict(row))
                except Exception:
                    serialized_rows.append({"values": list(row)})
        df = pd.DataFrame(serialized_rows)
    else:
        df = pd.DataFrame()

    img_b64 = generate_graph_png_base64(df, request.chart_type, request.chart_name or request.chart_type)
    if not img_b64:
        return {"error": "Failed to generate graph image."}
    
    # Generate key insights from the data
    insights = generate_key_insights(df, request.chart_type)
    
    return {
        "image_base64": img_b64,
        "insights": insights or "Unable to generate insights at this time."
    }


