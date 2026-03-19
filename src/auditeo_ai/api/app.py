"""
Auditeo AI API
"""

import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from auditeo_ai import __version__
from auditeo_ai.api.routes.audit import router as audit_router
from auditeo_ai.utils import get_logger, is_production
from auditeo_ai.utils.logger import correlation_id_ctx, ip_address_ctx

load_dotenv()

app = FastAPI(title="Auditeo AI API", version=__version__)


logger = get_logger("auditeo-ai")
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if is_production() else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def context_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    client_ip = request.client.host if request.client else "unknown"

    correlation_id_ctx.set(trace_id)
    ip_address_ctx.set(client_ip)

    response = await call_next(request)
    return response


@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("Root endpoint called")
    return {"message": "Auditeo AI API", "version": __version__}


@app.get("/health")
def health() -> dict[str, str]:
    """Health endpoint."""
    logger.info("Health check endpoint called")
    return {"status": "ok"}


app.include_router(audit_router, prefix="/api")
