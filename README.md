# Corehealth by CorestreamNG — AI Scribe Python Backend SDK & FastAPI Proxy

> **Enterprise Python client for CoreHealth v2 Interoperability (openEHR & FHIR R4) and AI Scribe Session Management.**

The `corehealth-scribe-sdk` Python package provides a backend toolkit for healthcare platforms, hospital systems, and partner EMRs to manage ephemeral session tokens, proxy AI Scribe events, and exchange clinical data across openEHR, FHIR R4, and NDPA standards.

---

## Key Features

- **Ephemeral Session & Zero Data Retention Guarantee**:
  - **Zero Persistent Storage in SDK Gateway**: No patient clinical data is stored or cached beyond the active in-memory request lifecycle.
  - **Capture the Callback**: If your application fails to capture the sign-off event or callback, the ephemeral session data terminates and a fresh session request is required.
  - **PII-Stripped Clinical Context (`patient_summary`)**: You can supply a de-identified patient brief (chronic history, allergies, baseline vitals) to guide the scribe. All context is sanitized per NDPA 2023 statutory standards.
- **Secure Token Minting**: Backend exchange of client credentials for short-lived session tokens (`SKT_...`) to keep API keys away from client browsers.
- **FastAPI / Starlette Proxy Router**: Pre-built router to mount in FastAPI applications with a single line of code (`app.include_router(create_scribe_router(client))`).
- **Standardized Interoperability**: Direct client methods for querying openEHR Archetype Query Language (AQL) and searching/mutating HL7 FHIR R4 resources.
- **Statutory Privacy**: Integrates with Nigeria Data Protection Act (NDPA 2023) consent management and cross-border data transfer safeguards.

---

## Quickstart: Run the Reference Example

A working FastAPI reference application is included in `examples/fastapi-integration/`:

```bash
cd examples/fastapi-integration
pip install -r requirements.txt
python main.py
```
Open `http://localhost:3002` in your browser!

👉 **[Read the Step-by-Step Example Walkthrough](./docs/running-the-example.md)**

---

## Documentation Directory

| Document | Purpose |
|---|---|
| 📖 **[Running the Example](./docs/running-the-example.md)** | Step-by-step guide to running the FastAPI reference demo. |
| 🚀 **[Fresh Integration Guide](./docs/fresh-integration-guide.md)** | How to use the Python SDK in Django, FastAPI, Flask, or background workers. |
| 🌐 **[Full Interoperability Guide](./docs/full-interoperability-guide.md)** | Complete guide to FHIR R4, openEHR ITS-REST, AQL, and NDPA APIs. |
| 📮 **[Postman Collection](./postman/CoreHealth-Interop-Collection.json)** | 25+ ready-to-run requests covering all interop & SDK endpoints. |
| 📑 **[OpenAPI 3.0 Specification](./openapi/corehealth-interop-openapi.json)** | Canonical machine-readable OpenAPI schema for the entire API. |

---

## Installation

```bash
pip install corehealth-scribe-sdk
```

With FastAPI proxy support:
```bash
pip install "corehealth-scribe-sdk[fastapi]"
```

---

## 30-Second Example

```python
from corehealth_sdk import CoreHealthClient

client = CoreHealthClient(
    base_url="https://api.corehealth.ng",
    client_id="partner-emr-dev",
    client_secret="partner_dev_secret_2026",
)

# Mint ephemeral token for browser session
session = client.get_scribe_token(patient_id=492, encounter_id=1017)
print("Session Token:", session["sdk_token"])

# Fetch compositions after consultation sign-off
compositions = client.get_compositions(token=session["sdk_token"])
print("openEHR Composition:", compositions["openehr_composition"])
print("FHIR R4 Bundle:", compositions["fhir_bundle"])
```

---

## Repository Structure

```
├── corehealth_sdk/                # Python package source code
│   ├── __init__.py
│   ├── client.py                  # CoreHealthClient implementation
│   └── fastapi_proxy.py           # Pre-built FastAPI proxy router
├── examples/
│   └── fastapi-integration/       # Working reference application
│       ├── main.py
│       ├── index.html
│       └── requirements.txt
├── docs/                          # Developer guides & technical references
│   ├── running-the-example.md
│   ├── fresh-integration-guide.md
│   └── full-interoperability-guide.md
├── openapi/
│   └── corehealth-interop-openapi.json
├── postman/
│   └── CoreHealth-Interop-Collection.json
├── pyproject.toml
├── setup.py
└── README.md
```

---

## License

Apache-2.0 © 2026 Corehealth by CorestreamNG <hello@corestream.ng>
