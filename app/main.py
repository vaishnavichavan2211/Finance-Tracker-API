"""
Finance Tracker Backend — Main Application Entry Point
======================================================
This is where FastAPI boots up. We register all route groups (routers)
and apply global settings like CORS, title, and description.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.routers import auth, users, records, analytics

# ── Auto-create tables if they don't exist yet ──────────────────────────────
# In production you'd use Alembic migrations instead, but this keeps
# things simple for beginners.
Base.metadata.create_all(bind=engine)

# ── Build the FastAPI app ────────────────────────────────────────────────────
app = FastAPI(
    title="💰 Finance Tracker API",
    description=(
        "A role-based personal finance tracking system. "
        "Manage income/expenses, filter records, and view analytics. "
        "Roles: **Admin** | **Analyst** | **Viewer**"
    ),
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)

# ── CORS — allow any frontend to talk to this API ───────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Tighten this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register route groups ────────────────────────────────────────────────────
app.include_router(auth.router,      prefix="/api/v1/auth",      tags=["🔐 Auth"])
app.include_router(users.router,     prefix="/api/v1/users",     tags=["👤 Users"])
app.include_router(records.router,   prefix="/api/v1/records",   tags=["📝 Financial Records"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["📊 Analytics"])


@app.get("/", tags=["🏠 Root"])
def root():
    """Health check — confirms the API is running."""
    return {
        "message": "Finance Tracker API is running!",
        "docs": "/docs",
        "version": "1.0.0",
    }
