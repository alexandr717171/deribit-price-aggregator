"""
Main entry point for the Deribit Data FastAPI application.

This module initializes the FastAPI app, configures global settings,
and connects the API routers. It serves as the central hub for
handling incoming HTTP requests.
"""

from fastapi import FastAPI


from app_deribit.app_fastapi.routers.routers import api_router

# Optional: Root endpoint to check if the server is running
app = FastAPI(
    title="Deribit Data API",
    description="API for accessing Deribit index prices.",
    version="1.0.0",
)
# Include the prices router with the /api prefix
app.include_router(api_router, prefix="/api")