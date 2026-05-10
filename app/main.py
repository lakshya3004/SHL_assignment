import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging


def create_application() -> FastAPI:
    """
    Initialize the FastAPI application with configuration, middleware, and routers.
    """
    # Initialize logging
    setup_logging()
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="AI-powered SHL Assessment Recommender API",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    # In production, specific origins should be defined in settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware for request timing and logging
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Method: {request.method} Path: {request.url.path} "
            f"Status: {response.status_code} Duration: {process_time:.2f}ms"
        )
        return response

    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    Initialize services, load vector stores, etc.
    """
    logger.info("Starting up SHL Recommender Service...")
    # TODO: Initialize RAG service, load FAISS index, etc.
    # try:
    #     await rag_service.initialize()
    # except Exception as e:
    #     logger.critical(f"Failed to initialize services: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    Clean up resources.
    """
    logger.info("Shutting down SHL Recommender Service...")
