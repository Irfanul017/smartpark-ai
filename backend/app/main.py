"""FastAPI entry point for SmartPark AI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_database
from app.routers import ai, allocation, auth, parking, simulation


app = FastAPI(
    title="SmartPark AI API",
    description="Intelligent parking-slot allocation system API.",
    version="0.1.0",
)

# Development origins used by the Vite frontend. Expand this list for deployed clients.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite tables are created for the development/demo environment. Migration tooling
# can replace this bootstrap when the project moves to PostgreSQL.
init_database()

app.include_router(auth.router)
app.include_router(parking.router)
app.include_router(allocation.router)
app.include_router(ai.router)
app.include_router(simulation.router)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    """Return the application identity and running status."""
    return {"project": "SmartPark AI", "status": "running"}


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return a lightweight service health status."""
    return {"status": "healthy"}
