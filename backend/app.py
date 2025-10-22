from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.auth import router as auth_router
from .routers.query import router as query_router
from .routers.graph import router as graph_router


app = FastAPI()

# CORS for local dev (adjust in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(query_router)
app.include_router(graph_router)


@app.get("/")
async def root():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)


