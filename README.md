# Corehealth by CorestreamNG — AI Scribe Python Backend SDK & FastAPI Proxy

> **Enterprise Python client for CoreHealth v2 Interoperability (openEHR & FHIR R4) and AI Scribe Session Management.**

The `corehealth-scribe-sdk` Python package provides a backend toolkit for healthcare platforms, hospital systems, and partner EMRs to manage ephemeral session tokens, proxy AI Scribe events, and exchange clinical data across openEHR, FHIR R4, and NDPA standards.

---

## Key Features

- **Compressed Scribe Catalog Protocol (CSCP)**: Built-in `CoreHealthClient.compress_catalog(items)` utility for compressing your EMR's products and services using compact `#CAT:id|type|name` DSL or gzip-base64. Delivers a 10x-15x reduction in token size (~3 tokens per item) for efficient LLM context injection.
- **Suggested Orders Deck & Prescriptions Staging**: Direct backend methods for catalog discovery (`get_categories`, `search_catalog_items`), processing voice transcripts with grounded catalogs (`process_dictation`), and signing consultations with clinician-approved orders (`sign_session`).
- **Dynamic Medical Taxonomy Conversion**: Losslessly convert clinical notes across doctor (`SOAP`, `Traditional Clerking`, `POMR`), nurse (`Focus DAR`, `SBAR`, `SOAPIE`), and maternity (`ANC`, `Labor`, `PNC`) formats via `convert_format()`.
- **Ephemeral Session & Zero Data Retention Guarantee**:
  - **Zero Persistent Storage in SDK Gateway**: No patient clinical data is stored or cached beyond the active in-memory request lifecycle.
  - **Capture the Callback**: If your application fails to capture the sign-off event or callback, the ephemeral session data terminates and a fresh session request is required.
  - **PII-Stripped Clinical Context (`patient_summary`)**: You can supply a de-identified patient brief (chronic history, allergies, baseline vitals) to guide the scribe. All context is sanitized per NDPA 2023 statutory standards.
- **Secure Token Minting**: Backend exchange of client credentials for short-lived session tokens (`SKT_...`) to keep API keys away from client browsers.
- **FastAPI / Starlette Proxy Router**: Pre-built router to mount in FastAPI applications with a single line of code (`app.include_router(create_scribe_router(client))`), complete with `/catalogs/items`, `/categories`, `/convert-format`, and `/signoff` endpoints.
- **Standardized Interoperability**: Direct client methods for querying openEHR Archetype Query Language (AQL) and searching/mutating HL7 FHIR R4 resources.
- **Statutory Privacy**: Integrates with Nigeria Data Protection Act (NDPA 2023) consent management and cross-border data transfer safeguards.

---

## Quickstart: Virtual Environment Setup & Reference Server

A complete FastAPI reference application demonstrating proxy token minting, catalog search, and consultation sign-off is included under `examples/fastapi-integration/`.

### 1. Create and Activate Virtual Environment (`venv`)

```bash
# Navigate to the reference example
cd examples/fastapi-integration

# Create isolated Python virtual environment (Python 3.10+)
python3 -m venv venv

# Activate virtual environment
# On Linux / macOS:
source venv/bin/activate
# On Windows (PowerShell):
# .\venv\Scripts\Activate.ps1
# On Windows (cmd):
# venv\Scripts\activate.bat

# Upgrade pip
pip install --upgrade pip
```

### 2. Configure Environment (`.env`)

```bash
# Copy example environment configuration
cp .env.example .env
```

Review `.env` to confirm target host and client credentials:

```ini
CH_BASE_URL=http://127.0.0.1:8000
CH_CLIENT_ID=partner-emr-dev
CH_CLIENT_SECRET=partner_dev_secret_2026
PORT=3002
```

### 3. Install Dependencies and Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start the reference proxy
python main.py
```

Open `http://localhost:3002` in your browser.

👉 **[Read the Complete Step-by-Step Example Walkthrough](./docs/running-the-example.md)**

---

## Documentation Directory

| Document | Purpose |
|---|---|
| 📖 **[Running the Example](./docs/running-the-example.md)** | Exhaustive step-by-step setup guide with venv and `.env` configuration. |
| 🚀 **[Fresh Integration Guide](./docs/fresh-integration-guide.md)** | How to use the Python SDK in Django, FastAPI, Flask, or background workers. |
| 🌐 **[Full Interoperability Guide](./docs/full-interoperability-guide.md)** | Complete guide to FHIR R4, openEHR ITS-REST, AQL, and NDPA APIs. |
| 📮 **[Postman Collection](./postman/CoreHealth-Interop-Collection.json)** | 25+ ready-to-run requests covering all interop & SDK endpoints. |
| 📑 **[OpenAPI 3.0 Specification](./openapi/corehealth-interop-openapi.json)** | Canonical machine-readable OpenAPI schema for the entire API. |

---

## Installation

Inside your activated virtual environment:

```bash
pip install corehealth-scribe-sdk
```

With FastAPI proxy router support:
```bash
pip install "corehealth-scribe-sdk[fastapi]"
```

For local development / editable installation:
```bash
pip install -e .
```

---

## 30-Second Example

```python
from corehealth_sdk import CoreHealthClient

client = CoreHealthClient(
    base_url="https://corehealth.corestream.ng",
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
