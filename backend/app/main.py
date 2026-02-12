from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from app.routes import qualify, validate, generate_tad
from app.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Architecture Assistant API",
    description="Generate Technical Architecture Documents (TAD) using AI",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ambitious-cliff-03a95d40f.1.azurestaticapps.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("AI Architecture Assistant API starting up")

# Include routers
app.include_router(qualify.router, prefix="/api", tags=["Qualification"])
app.include_router(validate.router, prefix="/api", tags=["Validation"])
app.include_router(generate_tad.router, prefix="/api", tags=["TAD Generation"])


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "AI Architecture Assistant API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Initialize Config and log startup event"""
    try:
        # Config is already initialized as singleton, just log status
        logger.info(f"Configuration initialized - Environment: {config.environment}")
        if config.is_production:
            logger.info(f"Using Azure Key Vault: {config.key_vault_name}")
        else:
            logger.info("Using local environment variables")
        
        logger.info("Application startup complete")
        logger.info("API documentation available at /docs")
    except Exception as e:
        logger.error(f"Failed to initialize configuration: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown event"""
    logger.info("Application shutting down")
