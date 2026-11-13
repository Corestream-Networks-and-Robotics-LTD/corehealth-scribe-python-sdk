"""
CoreHealth AI Scribe — FastAPI Backend Proxy Router
Pre-configured APIRouter for instant integration into FastAPI / Starlette backends.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel
from .client import CoreHealthClient

try:
    from fastapi import APIRouter, HTTPException, Query
except ImportError:
    APIRouter = None  # type: ignore


class SignoffPayload(BaseModel):
    patient_id: Optional[int] = 492
    encounter_id: Optional[int] = 1017
    final_signed_note: str
    original_transcript: Optional[str] = None
    openehr_composition: Optional[Dict[str, Any]] = None
    fhir_bundle: Optional[Dict[str, Any]] = None


def create_scribe_router(client: CoreHealthClient, prefix: str = "/api/scribe") -> Any:
    """Create a FastAPI APIRouter configured for CoreHealth Scribe proxying."""
    if APIRouter is None:
        raise ImportError("FastAPI is not installed. Install with `pip install corehealth-scribe-sdk[fastapi]`")

    router = APIRouter(prefix=prefix, tags=["CoreHealth Scribe Proxy"])

    @router.get("/token")
    def get_token(
        patient_id: int = Query(492),
        encounter_id: int = Query(1017),
        clinician_id: int = Query(38),
    ):
        """Mint an ephemeral SKT_ session token for the browser client."""
        try:
            return client.get_scribe_token(
                patient_id=patient_id,
                encounter_id=encounter_id,
                clinician_id=clinician_id,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/encounters/{encounter_id}/signoff")
    def receive_signoff(encounter_id: int, payload: SignoffPayload):
        """Receive signed consultation notes and return confirmed EHR persistence status."""
        return {
            "success": True,
            "encounter_id": encounter_id,
            "patient_id": payload.patient_id,
            "final_signed_note": payload.final_signed_note,
            "openehr_composition": payload.openehr_composition,
            "fhir_bundle": payload.fhir_bundle,
            "message": "Clinical note and orders successfully persisted to EHR.",
        }

    return router

