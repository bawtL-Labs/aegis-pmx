#!/usr/bin/env python3
"""
Personality Matrix Service - Main entry point.

This module provides the main service entry point for the Personality Matrix
daemon, including FastAPI integration and systemd service compatibility.
"""

import asyncio
import logging
import os
import signal
import sys
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .core import PersonalityMatrix
from .models import (
    AudienceContext,
    ChannelContext,
    EventType,
    PersonalityConfig,
    StateUpdate,
)
from .api import create_api_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/sam-pmxd.log') if os.path.exists('/var/log') else logging.NullHandler(),
    ]
)

logger = logging.getLogger(__name__)


class PersonalityMatrixService:
    """Main service class for the Personality Matrix daemon."""
    
    def __init__(self, config: Optional[PersonalityConfig] = None):
        """
        Initialize the Personality Matrix service.
        
        Args:
            config: Optional configuration override
        """
        self.config = config or PersonalityConfig()
        self.pmx: Optional[PersonalityMatrix] = None
        self.app: Optional[FastAPI] = None
        self.server: Optional[uvicorn.Server] = None
        
        # Service state
        self._running = False
        self._shutdown_event = asyncio.Event()
        
        logger.info("Personality Matrix Service initialized")
    
    async def start(self, host: str = "0.0.0.0", port: int = 8001) -> None:
        """
        Start the Personality Matrix service.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        if self._running:
            logger.warning("Service is already running")
            return
        
        logger.info("Starting Personality Matrix service on %s:%d", host, port)
        
        try:
            # Initialize the personality matrix
            self.pmx = PersonalityMatrix(self.config)
            
            # Create FastAPI application
            self.app = self._create_fastapi_app()
            
            # Start the server
            config = uvicorn.Config(
                app=self.app,
                host=host,
                port=port,
                log_level="info",
                access_log=True,
            )
            
            self.server = uvicorn.Server(config)
            self._running = True
            
            # Set up signal handlers
            self._setup_signal_handlers()
            
            # Start the server
            await self.server.serve()
            
        except Exception as e:
            logger.error("Failed to start service: %s", e)
            raise
        finally:
            self._running = False
    
    async def stop(self) -> None:
        """Stop the Personality Matrix service."""
        if not self._running:
            logger.warning("Service is not running")
            return
        
        logger.info("Stopping Personality Matrix service")
        
        self._running = False
        self._shutdown_event.set()
        
        if self.server:
            self.server.should_exit = True
        
        logger.info("Personality Matrix service stopped")
    
    def _create_fastapi_app(self) -> FastAPI:
        """Create and configure the FastAPI application."""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            logger.info("Personality Matrix API starting up")
            yield
            # Shutdown
            logger.info("Personality Matrix API shutting down")
            if self.pmx:
                # Perform any cleanup here
                pass
        
        app = FastAPI(
            title="Personality Matrix API",
            description="API for Sam's Personality Matrix (PMX) component",
            version="1.0.0",
            lifespan=lifespan,
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add exception handlers
        app.add_exception_handler(ValidationError, self._validation_error_handler)
        app.add_exception_handler(Exception, self._general_error_handler)
        
        # Add API routes
        api_router = create_api_router(self.pmx)
        app.include_router(api_router, prefix="/pmx")
        
        # Add health check endpoint
        @app.get("/health")
        async def health_check():
            """Health check endpoint."""
            if not self.pmx:
                raise HTTPException(status_code=503, detail="Service not initialized")
            
            return {
                "status": "healthy",
                "service": "personality-matrix",
                "version": "1.0.0",
                "personality": self.pmx.get_personality_summary(),
            }
        
        # Add root endpoint
        @app.get("/")
        async def root():
            """Root endpoint with service information."""
            return {
                "service": "Personality Matrix (PMX)",
                "description": "Sam's autonomous AI personality management system",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/health",
                    "api": "/pmx",
                    "docs": "/docs",
                },
            }
        
        return app
    
    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info("Received signal %d, initiating shutdown", signum)
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _validation_error_handler(self, request: Request, exc: ValidationError) -> JSONResponse:
        """Handle validation errors."""
        logger.warning("Validation error: %s", exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "details": exc.errors(),
            }
        )
    
    async def _general_error_handler(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle general errors."""
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(exc) if os.getenv("DEBUG") else "An unexpected error occurred",
            }
        )


def main():
    """Main entry point for the Personality Matrix daemon."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Personality Matrix Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        os.environ["DEBUG"] = "1"
    
    # Load configuration if provided
    config = None
    if args.config:
        try:
            # Load configuration from file
            import json
            with open(args.config, 'r') as f:
                config_data = json.load(f)
            config = PersonalityConfig(**config_data)
            logger.info("Loaded configuration from %s", args.config)
        except Exception as e:
            logger.error("Failed to load configuration from %s: %s", args.config, e)
            sys.exit(1)
    
    # Create and run service
    service = PersonalityMatrixService(config)
    
    try:
        asyncio.run(service.start(args.host, args.port))
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down")
    except Exception as e:
        logger.error("Service failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()