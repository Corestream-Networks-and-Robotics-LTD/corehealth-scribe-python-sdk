"""
Corehealth by CorestreamNG — AI Scribe & Interoperability API Client
(c) Corehealth by CorestreamNG <hello@corestream.ng>
"""

import json
from typing import Any, Dict, List, Optional, Union
import urllib.request
import urllib.parse
import urllib.error

try:
    import requests
except ImportError:
    requests = None


class CoreHealthClient:
    """Client for Corehealth by CorestreamNG Interoperability & AI Scribe SDK Gateway."""

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
    # Internal HTTP Request Helper (Supports requests with urllib fallback)
    # -------------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        req_headers = {"Accept": "application/json"}
        if json_data is not None:
            req_headers["Content-Type"] = "application/json"
        if headers:
            req_headers.update(headers)

        if requests is not None:
            resp = requests.request(
                method=method.upper(),
                url=url,
                headers=req_headers,
                params=params,
                json=json_data,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()

        # Fallback to standard library urllib
        if params:
            query_str = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            url = f"{url}?{query_str}" if query_str else url

        data_bytes = json.dumps(json_data).encode("utf-8") if json_data is not None else None
        req = urllib.request.Request(url, data=data_bytes, headers=req_headers, method=method.upper())

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                err_json = json.loads(err_body)
                raise RuntimeError(f"HTTP {e.code}: {err_json.get('message', err_body)}")
            except json.JSONDecodeError:
                raise RuntimeError(f"HTTP {e.code}: {err_body}")

    # -------------------------------------------------------------------------
    # Catalog Compression Utilities
    # -------------------------------------------------------------------------

    @staticmethod
    def compress_catalog(categories: List[Dict[str, Any]]) -> str:
        """
        Super-Compress partner EMR categories and items into CSCP format.
        Compresses 500+ hospital items into ~1,500 LLM tokens (10x-15x smaller than raw JSON).
        """
        lines = []
        for cat in categories:
            cat_id = cat.get("id", "cat")
            cat_type = cat.get("type", "SERVICE").upper()
            cat_name = cat.get("name", cat_id)
            lines.append(f"#CAT:{cat_id}|{cat_type}|{cat_name}")

            items = cat.get("items", [])
            item_tokens = []
            for it in items:
                if isinstance(it, str):
                    item_tokens.append(it)
                elif isinstance(it, dict):
                    i_id = it.get("id") or it.get("catalog_id") or ""
                    i_name = it.get("name") or it.get("item_name") or ""
                    i_code = it.get("code") or ""
                    i_price = it.get("price") or it.get("unit_price") or ""
                    if i_price != "" and i_code != "":
                        item_tokens.append(f"{i_id}:{i_code}:{i_name}:{i_price}")
                    elif i_code != "":
                        item_tokens.append(f"{i_id}:{i_code}:{i_name}")
                    else:
                        item_tokens.append(f"{i_id}:{i_name}")
            if item_tokens:
                lines.append("|".join(item_tokens))
        return "\n".join(lines)

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
        role: str = "doctor",
        taxonomy: str = "soap",
    ) -> Dict[str, Any]:
        """Mint an ephemeral SKT_ session token for the browser client."""
        if not self.client_id or not self.client_secret:
            raise ValueError("client_id and client_secret are required to mint an SDK session token.")

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "clinician_id": clinician_id,
            "scope": scope,
            "ttl": ttl,
            "locale": locale,
            "role": role,
            "taxonomy": taxonomy,
        }

        data = self._request("POST", "/api/sdk/auth/token", json_data=payload)
        data["corehealth_base_url"] = self.base_url
        return data

    def get_categories(self, token: str) -> Dict[str, Any]:
        """Fetch active service and product categories with queue mappings."""
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("GET", "/api/sdk/catalogs/categories", headers=headers)

    def search_catalog_items(
        self,
        token: str,
        query: str = "",
        category_id: Optional[Union[int, str]] = None,
        item_type: str = "all",
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Search products and services across hospital and custom catalogs."""
        headers = {"Authorization": f"Bearer {token}"}
        params = {"q": query, "type": item_type, "limit": limit}
        if category_id:
            params["category_id"] = str(category_id)
        return self._request("GET", "/api/sdk/catalogs/items", headers=headers, params=params)

    def convert_format(
        self,
        token: str,
        from_taxonomy: str,
        to_taxonomy: str,
        current_sections: List[Dict[str, Any]],
        role: str = "doctor",
    ) -> Dict[str, Any]:
        """Convert structured notes losslessly between clinical taxonomies."""
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "from_taxonomy": from_taxonomy,
            "to_taxonomy": to_taxonomy,
            "current_sections": current_sections,
            "role": role,
        }
        return self._request("POST", "/api/sdk/scribe/convert-format", headers=headers, json_data=payload)

    def process_dictation(
        self,
        token: str,
        transcript: str,
        patient_id: Optional[int] = None,
        encounter_id: Optional[int] = None,
        patient_summary: Optional[str] = None,
        role: str = "doctor",
        taxonomy: str = "soap",
        custom_catalog: Optional[Union[str, List[Dict[str, Any]]]] = None,
        existing_sections: Optional[List[Dict[str, Any]]] = None,
        existing_orders: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Process consultation dictation into structured sections and grounded clinical orders.
        """
        headers = {"Authorization": f"Bearer {token}"}
        payload: Dict[str, Any] = {
            "transcript": transcript,
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "patient_summary": patient_summary,
            "role": role,
            "taxonomy": taxonomy,
            "existing_sections": existing_sections or [],
            "existing_orders": existing_orders or [],
        }
        if custom_catalog:
            payload["custom_catalog"] = (
                self.compress_catalog(custom_catalog)
                if isinstance(custom_catalog, list)
                else custom_catalog
            )

        return self._request("POST", "/api/sdk/scribe/process", headers=headers, json_data=payload)

    def sign_session(
        self,
        token: str,
        final_signed_note: str,
        original_transcript: Optional[str] = None,
        patient_id: Optional[int] = None,
        encounter_id: Optional[int] = None,
        approved_orders: Optional[List[Dict[str, Any]]] = None,
        role: str = "doctor",
        taxonomy_type: str = "soap",
    ) -> Dict[str, Any]:
        """Sign and commit structured consultation note and approved orders."""
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "final_signed_note": final_signed_note,
            "original_transcript": original_transcript,
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "approved_orders": approved_orders or [],
            "role": role,
            "taxonomy_type": taxonomy_type,
        }
        return self._request("POST", "/api/sdk/scribe/sign", headers=headers, json_data=payload)

    def get_compositions(self, token: str, cross_border: bool = False) -> Dict[str, Any]:
        """Fetch canonical openEHR COMPOSITION and HL7 FHIR R4 Bundle after sign-off."""
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"cross_border": cross_border}
        return self._request("POST", "/api/sdk/scribe/compositions", headers=headers, json_data=payload)

    def get_fhir_bundle(self, token: str) -> Dict[str, Any]:
        """Fetch HL7 FHIR R4 Transaction Bundle only."""
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("POST", "/api/sdk/scribe/fhir-bundle", headers=headers)

    def revoke_token(self, token: str) -> Dict[str, Any]:
        """Revoke an active session token."""
        payload = {"token": token}
        return self._request("POST", "/api/sdk/auth/revoke", json_data=payload)

    # -------------------------------------------------------------------------
    # Core Interoperability (openEHR & FHIR R4)
    # -------------------------------------------------------------------------

    def query_aql(self, aql: str, token: str) -> Dict[str, Any]:
        """Execute an openEHR Archetype Query Language (AQL) query."""
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("POST", "/api/openehr/v1/query/aql", headers=headers, json_data={"q": aql})

    def search_patients_fhir(self, name: str, token: str) -> Dict[str, Any]:
        """Search patients via HL7 FHIR R4 Patient endpoint."""
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/fhir+json"}
        return self._request("GET", "/api/fhir/r4/Patient", headers=headers, params={"name": name})
