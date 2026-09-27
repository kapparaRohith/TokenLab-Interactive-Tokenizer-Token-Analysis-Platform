"""
FastAPI application factory.
- Creates the app, configures CORS, registers routers.
- Owns the singleton service instances and pre-loads Tiktoken encodings on startup.
"""
from __future__ import annotations

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import SUPPORTED_ENCODINGS
from app.routes import tokenize as tokenize_router
from app.schemas import HealthResponseSchema
from app.services.custom_tokenizer_service import custom_tokenizer_service  # noqa: F401 — singleton init
from app.services.tiktoken_service import tiktoken_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load all Tiktoken encodings at startup to avoid first-request latency."""
    logger.info("Tokenizer Application starting up — pre-loading Tiktoken encodings...")
    for enc_name in SUPPORTED_ENCODINGS:
        try:
            tiktoken_service.get_encoding(enc_name)
            logger.info("Loaded encoding: %s", enc_name)
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to pre-load encoding %s: %s", enc_name, exc)
    logger.info("Startup complete. All encodings ready.")
    yield
    logger.info("Tokenizer Application shutting down.")


app = FastAPI(
    title="Tokenizer Application",
    description="Visualize Tiktoken and Custom tokenization of text and files.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the Vite dev server origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler — never expose stack traces
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s", request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."},
    )


# Routes
app.include_router(tokenize_router.router)


@app.get("/health", response_model=HealthResponseSchema)
async def health() -> HealthResponseSchema:
    """Health check endpoint."""
    return HealthResponseSchema(status="ok")
