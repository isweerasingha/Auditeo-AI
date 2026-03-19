"""Server entry point for running the FastAPI application."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "auditeo_ai.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

