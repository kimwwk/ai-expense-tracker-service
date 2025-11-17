"""
FastAPI application entry point.
Defines the main application instance, middleware, and health check endpoint.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings

# Create FastAPI application
app = FastAPI(
    title="AI Expense Tracker Service API",
    description="REST API for expense tracking with CRUD operations for transactions, accounts, categories, and payees",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint.
    Returns the status of the API service.
    """
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0"
    }


# Routers
from src.routers import accounts, reference

app.include_router(accounts.router)
app.include_router(reference.router)
