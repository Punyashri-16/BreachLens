"""
Application entry point.

Run it with:  uvicorn app.main:app --reload
Then open:    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.database.connection import check_connection
from app.ai.client import is_available

app = FastAPI(
    title="Blast Radius API",
    description="Attack path analysis and business impact for a synthetic enterprise.",
    version="1.0.0",
)

# ------------------------------------------------------------------
# CORS
# The frontend runs on a different port during development, and the
# browser blocks cross-origin requests unless the server allows them.
# Vite defaults to 5173, Create React App to 3000, so allow both.
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    """Confirms the server is alive."""
    return {
        "status": "ok",
        "service": "Blast Radius API",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    """
    Reports what the server can actually reach right now.

    Useful during a demo: one request tells you whether MongoDB is up
    and whether the AI is configured.
    """
    try:
        check_connection()
        database = "connected"
    except Exception as error:
        print(f"Health check: database unreachable: {error}")
        database = "unreachable"

    return {
        "status": "ok",
        "database": database,
        "ai_configured": is_available(),
    }


@app.on_event("startup")
def on_startup():
    """Print the state of things when the server boots."""
    print("\n" + "=" * 50)
    print("Blast Radius API starting")
    try:
        check_connection()
        print("  MongoDB   : connected")
    except Exception:
        print("  MongoDB   : NOT REACHABLE — check the service is running")
    print(f"  Gemini    : {'configured' if is_available() else 'no key, using fallbacks'}")
    print("  Docs      : http://127.0.0.1:8000/docs")
    print("=" * 50 + "\n")