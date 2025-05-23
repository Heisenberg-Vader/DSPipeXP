from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.tasks import BackgroundTasks
from app.core.testing import run_startup_tests
from app.api.endpoints import router as api_router
import logging
import asyncio

logger = logging.getLogger(__name__)

app = FastAPI(
    title="DSPipeXP API",
    description="Music recommendation system API",
    version="1.0.0",
    debug=True  # Enable debug mode
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
setup_logging()

# Include all routes under /api/v1
logger.debug("Registering API routes...")
app.include_router(api_router, prefix="/api/v1")

# Initialize background tasks
background_tasks = BackgroundTasks(app)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    try:
        # Log all registered routes
        logger.debug("Registered routes:")
        for route in app.routes:
            logger.debug(f"  {route.methods} {route.path}")
            
        # Start background tasks
        await background_tasks.start()
        logger.info("Application started successfully")
        
        # Run endpoint tests in the background
        asyncio.create_task(run_startup_tests(app))
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    try:
        # Stop background tasks
        await background_tasks.stop()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        raise

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Music Recommendation System API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
