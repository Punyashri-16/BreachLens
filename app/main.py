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