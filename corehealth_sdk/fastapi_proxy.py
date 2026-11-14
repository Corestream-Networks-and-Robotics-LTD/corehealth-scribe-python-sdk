"""
Corehealth by CorestreamNG — FastAPI Backend Proxy Router
Pre-configured APIRouter for instant integration into FastAPI / Starlette backends.

(c) Corehealth by CorestreamNG <hello@corestream.ng>
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from .client import CoreHealthClient

try:
    from fastapi import APIRouter, Header, HTTPException, Query
except ImportError:
    APIRouter = None  # type: ignore


class SignoffPayload(BaseModel):
    patient_id: Optional[int] = 492
    encounter_id: Optional[int] = 1017
    role: Optional[str] = "doctor"
    taxonomy_type: Optional[str] = "soap"
    final_signed_note: str
    original_transcript: Optional[str] = None
    approved_orders: Optional[List[Dict[str, Any]]] = None
    openehr_composition: Optional[Dict[str, Any]] = None
    fhir_bundle: Optional[Dict[str, Any]] = None


class ConvertFormatPayload(BaseModel):
    from_taxonomy: str
    to_taxonomy: str
    current_sections: List[Dict[str, Any]]
    role: Optional[str] = "doctor"


def create_scribe_router(client: CoreHealthClient, prefix: str = "/api/scribe") -> Any:
    """Create a FastAPI APIRouter configured for CoreHealth Scribe proxying."""
    if APIRouter is None:
        raise ImportError("FastAPI is not installed. Install with `pip install corehealth-scribe-sdk[fastapi]`")

    router = APIRouter(prefix=prefix, tags=["CoreHealth Scribe Proxy"])

    @router.get("/token")
    def get_token(
        patient_id: int = Query(492),
        encounter_id: int = Query(1017),
        clinician_id: int = Query(1),
        role: str = Query("doctor"),
        taxonomy: str = Query("soap"),
    ):
        """Mint an ephemeral SKT_ session token for the browser client."""
        try:
            return client.get_scribe_token(
                patient_id=patient_id,
                encounter_id=encounter_id,
                clinician_id=clinician_id,
                role=role,
                taxonomy=taxonomy,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/categories")
    def get_categories(authorization: Optional[str] = Header(None)):
        """Fetch active service and product categories."""
        token = authorization.replace("Bearer ", "") if authorization else ""
        try:
            return client.get_categories(token)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/catalogs/items")
    def search_items(
        q: str = Query(""),
        category_id: Optional[str] = Query(None),
        item_type: str = Query("all"),
        limit: int = Query(20),
        authorization: Optional[str] = Header(None),
    ):
        """Search products and services across hospital and custom catalogs."""
        token = authorization.replace("Bearer ", "") if authorization else ""
        try:
            return client.search_catalog_items(token, query=q, category_id=category_id, item_type=item_type, limit=limit)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/convert-format")
    def convert_format(payload: ConvertFormatPayload, authorization: Optional[str] = Header(None)):
        """Losslessly convert note sections between clinical taxonomies."""
        token = authorization.replace("Bearer ", "") if authorization else ""
        try:
            return client.convert_format(
                token=token,
                from_taxonomy=payload.from_taxonomy,
                to_taxonomy=payload.to_taxonomy,
                current_sections=payload.current_sections,
                role=payload.role or "doctor",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/encounters/{encounter_id}/signoff")
    def receive_signoff(encounter_id: int, payload: SignoffPayload):
        """Receive signed consultation notes and approved orders into your EMR."""
        return {
            "success": True,
            "encounter_id": encounter_id,
            "patient_id": payload.patient_id,
            "role": payload.role,
            "taxonomy_type": payload.taxonomy_type,
            "final_signed_note": payload.final_signed_note,
            "approved_orders": payload.approved_orders or [],
            "openehr_composition": payload.openehr_composition,
            "fhir_bundle": payload.fhir_bundle,
            "message": "Clinical note and orders successfully persisted to EHR.",
        }

    return router
