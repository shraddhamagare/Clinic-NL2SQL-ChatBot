import re
import sqlite3
import os
import logging
from typing import Optional

import pandas as pd
import plotly.express as px
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from dotenv import load_dotenv

load_dotenv()

from vanna_setup import get_agent, get_memory
from vanna.core.user import User, RequestContext

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Clinic NL2SQL Chatbot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "clinic.db")

# ── Models ────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str

    @validator("question")
    def validate_question(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty.")
        if len(v) > 500:
            raise ValueError("Question is too long (max 500 characters).")
        return v

class ChatResponse(BaseModel):
    message: str
    sql_query: Optional[str] = None
    columns: Optional[list] = None
    rows: Optional[list] = None
    row_count: Optional[int] = None
    chart: Optional[dict] = None
    chart_type: Optional[str] = None

# ── SQL Validation ────────────────────────────────────────────────────────────
FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|EXEC|EXECUTE|GRANT|REVOKE|SHUTDOWN)\b",
    re.IGNORECASE,
)
SYSTEM_TABLES = re.compile(r"\bsqlite_master\b|\bsqlite_sequence\b", re.IGNORECASE)

def validate_sql(sql: str):
    if not sql.strip().upper().startswith("SELECT"):
        return False, "Only SELECT queries are allowed."
    if FORBIDDEN.search(sql):
        return False, "Query contains forbidden keywords."
    if SYSTEM_TABLES.search(sql):
        return False, "Query accesses system tables."
    return True, ""

# ── Chart Generation ──────────────────────────────────────────────────────────
def try_chart(df: pd.DataFrame):
    try:
        if df.empty or len(df.columns) < 2:
            return None, None
        numeric = df.select_dtypes(include="number").columns.tolist()
        text    = df.select_dtypes(exclude="number").columns.tolist()
        if numeric and text:
            fig = px.bar(df, x=text[0], y=numeric[0])
            return fig.to_dict(), "bar"
        elif len(numeric) >= 2:
            fig = px.line(df, x=df.columns[0], y=numeric[0])
            return fig.to_dict(), "line"
    except Exception:
        pass
    return None, None

# ── /chat Endpoint ────────────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.question
    logger.info(f"Question: {question!r}")

    # 1. Get agent and send message
    try:
        agent = get_agent()
        user  = User(id="default_user", email="user@clinic.com", group_memberships=["users"])
        ctx   = RequestContext(user=user)
        result = await agent.send_message(message=question, request_context=ctx)
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return ChatResponse(message=f"Agent error: {str(e)}")

    # 2. Extract SQL and message from result
    sql_query = None
    message   = "Here are your results."

    if hasattr(result, 'components'):
        for component in result.components:
            if hasattr(component, 'sql'):
                sql_query = component.sql
            if hasattr(component, 'text'):
                message = component.text
    elif hasattr(result, 'sql'):
        sql_query = result.sql
    elif hasattr(result, 'message'):
        message = result.message

    if not sql_query:
        msg = str(result) if result else "I could not generate SQL for that question."
        return ChatResponse(message=msg)

    # 3. Validate SQL
    is_valid, error_msg = validate_sql(sql_query)
    if not is_valid:
        return ChatResponse(message=f"Query blocked: {error_msg}", sql_query=sql_query)

    # 4. Execute SQL
    try:
        conn = sqlite3.connect(DB_PATH)
        df   = pd.read_sql_query(sql_query, conn)
        conn.close()
    except Exception as e:
        return ChatResponse(message=f"Database error: {str(e)}", sql_query=sql_query)

    if df.empty:
        return ChatResponse(
            message="No data found.",
            sql_query=sql_query,
            columns=df.columns.tolist(),
            rows=[], row_count=0
        )

    chart_data, chart_type = try_chart(df)

    return ChatResponse(
        message=f"Found {len(df)} result(s).",
        sql_query=sql_query,
        columns=df.columns.tolist(),
        rows=df.values.tolist(),
        row_count=len(df),
        chart=chart_data,
        chart_type=chart_type,
    )

# ── /health Endpoint ──────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    db_status = "connected"
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
    except Exception:
        db_status = "error"

    return {
        "status": "ok",
        "database": db_status,
        "agent_memory_items": 15,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)