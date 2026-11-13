"""
CoreHealth AI Scribe & Interoperability API Client
"""

from typing import Any, Dict, List, Optional
import httpx


class CoreHealthClient:
    """Client for CoreHealth v2 Interoperability and AI Scribe SDK Gateway."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout

    # -------------------------------------------------------------------------
    # AI Scribe Session Management
    # -------------------------------------------------------------------------

    def get_scribe_token(
        self,
        patient_id: Optional[int] = None,
        encounter_id: Optional[int] = None,
        clinician_id: Optional[int] = None,
        scope: str = "scribe:process scribe:sign interop:compositions",
        ttl: int = 3600,
        locale: str = "en-NG",
    ) -> Dict[str, Any]:
        """Mint an ephemeral SKT_ session token for the browser client."""
        if not self.client_id or not self.client_secret:
            raise ValueError("client_id and client_secret are required to mint an SDK session token.")

        url = f"{self.base_url}/api/sdk/auth/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "clinician_id": clinician_id,
            "scope": scope,
            "ttl": ttl,
            "locale": locale,
        }

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=payload, headers={"Accept": "application/json"})
            resp.raise_for_status()
            return resp.json()

    def get_session_status(self, token: str) -> Dict[str, Any]:
        """Query real-time status of a Scribe session."""
        url = f"{self.base_url}/api/sdk/scribe/session/{token}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()

    def process_dictation(
        self,
        token: str,
        transcript: str,
        patient_id: Optional[int] = None,
        encounter_id: Optional[int] = None,
        patient_summary: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process dictated text into structured SOAP sections and extracted orders."""
        url = f"{self.base_url}/api/sdk/scribe/process"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "transcript": transcript,
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "patient_summary": patient_summary,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

    def sign_session(
        self,
        token: str,
        final_signed_note: str,
        original_transcript: Optional[str] = None,
        patient_id: Optional[int] = None,
        encounter_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Sign and archive a consultation note."""
        url = f"{self.base_url}/api/sdk/scribe/sign"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "final_signed_note": final_signed_note,
            "original_transcript": original_transcript,
            "patient_id": patient_id,
            "encounter_id": encounter_id,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

    def get_compositions(self, token: str, cross_border: bool = False) -> Dict[str, Any]:
        """Fetch openEHR COMPOSITION and HL7 FHIR R4 Bundle after note sign-off."""
        url = f"{self.base_url}/api/sdk/scribe/session/{token}/compositions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {"cross_border": cross_border}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

    def get_fhir_bundle(self, token: str) -> Dict[str, Any]:
        """Fetch HL7 FHIR R4 Transaction Bundle only."""
        url = f"{self.base_url}/api/sdk/scribe/session/{token}/fhir-bundle"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers)
            resp.raise_for_status()
            return resp.json()

    def revoke_token(self, token: str) -> Dict[str, Any]:
        """Revoke an active session token."""
        url = f"{self.base_url}/api/sdk/auth/revoke"
        payload = {"token": token}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=payload, headers={"Accept": "application/json"})
            resp.raise_for_status()
            return resp.json()

    # -------------------------------------------------------------------------
    # Core Interoperability (openEHR & FHIR R4)
    # -------------------------------------------------------------------------

    def query_aql(self, aql: str, token: str) -> Dict[str, Any]:
        """Execute an openEHR Archetype Query Language (AQL) query."""
        url = f"{self.base_url}/api/openehr/v1/query/aql"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json={"q": aql}, headers=headers)
            resp.raise_for_status()
            return resp.json()

    def search_patients_fhir(self, name: str, token: str) -> Dict[str, Any]:
        """Search patients via HL7 FHIR R4 Patient endpoint."""
        url = f"{self.base_url}/api/fhir/r4/Patient"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/fhir+json",
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, params={"name": name}, headers=headers)
            resp.raise_for_status()
            return resp.json()

