"""
CoreHealth AI Scribe — FastAPI Reference Integration Server
Run with: uvicorn main:app --reload --port 3002
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import sys

# Ensure local corehealth_sdk package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from corehealth_sdk.client import CoreHealthClient
from corehealth_sdk.fastapi_proxy import create_scribe_router

app = FastAPI(
    title="Partner EMR Consultation Portal",
    description="Reference EMR backend demonstrating CoreHealth AI Scribe Python SDK integration",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize CoreHealth Client (holds client credentials securely in backend)
CH_BASE_URL = os.getenv("CH_BASE_URL", "http://127.0.0.1:8000")
CLIENT_ID = os.getenv("CH_CLIENT_ID", "partner-emr-dev")
CLIENT_SECRET = os.getenv("CH_CLIENT_SECRET", "partner_dev_secret_2026")

client = CoreHealthClient(
    base_url=CH_BASE_URL,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
)

# Mount the pre-built Scribe proxy router
app.include_router(create_scribe_router(client, prefix="/api/scribe"))


@app.get("/", response_class=HTMLResponse)
def serve_consultation_screen():
    """Serve the partner consultation screen embedding the Scribe Studio."""
    html_path = Path(__file__).parent / "index.html"
    return html_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    import uvicorn
    print("====================================================")
    print("Starting FastAPI Reference Scribe Proxy on :3002")
    print("Open http://localhost:3002 in your browser")
    print("====================================================")
    uvicorn.run(app, host="0.0.0.0", port=3002)

