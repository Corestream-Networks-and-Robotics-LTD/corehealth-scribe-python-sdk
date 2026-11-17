# Fresh Integration Guide: Using CoreHealth Python SDK in Your Backend

This guide demonstrates how to integrate the `corehealth-scribe-sdk` Python package into Django, FastAPI, Flask, or background worker services.

---

## Step 1: Virtual Environment & Package Installation

Always initialize a dedicated virtual environment:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1

# Install SDK from Git repository
pip install git+https://github.com/Corestream-Networks-and-Robotics-LTD/corehealth-scribe-python-sdk.git

# Or with FastAPI proxy support:
pip install "corehealth-scribe-sdk[fastapi] @ git+https://github.com/Corestream-Networks-and-Robotics-LTD/corehealth-scribe-python-sdk.git@main" python-dotenv
```

---

## Step 2: Environment Configuration (`.env`)

Create a `.env` file in your project root using the standard parameters:

```ini
CH_BASE_URL=https://corehealth.corestream.ng
CH_CLIENT_ID=your-client-id
CH_CLIENT_SECRET=your-client-secret
```

Load your environment variables securely:

```python
import os
from dotenv import load_dotenv

load_dotenv()

CH_BASE_URL = os.getenv("CH_BASE_URL", "https://corehealth.corestream.ng")
CH_CLIENT_ID = os.getenv("CH_CLIENT_ID")
CH_CLIENT_SECRET = os.getenv("CH_CLIENT_SECRET")
```

---

## Step 3: Initialize the Client

```python
from corehealth_sdk import CoreHealthClient

client = CoreHealthClient(
    base_url=CH_BASE_URL,
    client_id=CH_CLIENT_ID,
    client_secret=CH_CLIENT_SECRET,
)
```

---

## Step 3: Mint Ephemeral Tokens for Browser Encounters

When a doctor opens an encounter in your system, create a token for that session:

```python
token_data = client.get_scribe_token(
    patient_id=492,
    encounter_id=1017,
    clinician_id=38,
    scope="scribe:process scribe:sign interop:compositions",
    ttl=3600
)

# Return this token to your frontend JavaScript client:
# token_data['sdk_token'] -> "SKT_eyJ..."
```

---

## Step 4: One-Line Mounting in FastAPI Backends

If you use FastAPI, mount the pre-configured proxy router directly:

```python
from fastapi import FastAPI
from corehealth_sdk import CoreHealthClient
from corehealth_sdk.fastapi_proxy import create_scribe_router

app = FastAPI()
client = CoreHealthClient(...)

# Exposes /api/scribe/token and /api/scribe/encounters/{id}/signoff
app.include_router(create_scribe_router(client, prefix="/api/scribe"))
```

---

## Step 5: Querying openEHR & FHIR Directly in Python

You can also use the Python SDK to query epidemiological data or manage EHR records:

```python
# Run an AQL query
bp_trends = client.query_aql(
    aql="SELECT o/data[at0001]/events[at0006]/data[at0003]/items[at0004]/value/magnitude AS systolic FROM EHR e CONTAINS OBSERVATION o[openEHR-EHR-OBSERVATION.blood_pressure.v2]",
    token=token_data['sdk_token']
)

# Search FHIR Patients
patients = client.search_patients_fhir(name="Oladipo", token=token_data['sdk_token'])
```

