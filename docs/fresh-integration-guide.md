# Fresh Integration Guide: Using CoreHealth Python SDK in Your Backend

This guide shows how to integrate the `corehealth-scribe-sdk` Python package into Django, FastAPI, Flask, or any Python backend.

---

## Step 1: Install the Package

```bash
pip install corehealth-scribe-sdk
```

Or for FastAPI support:
```bash
pip install "corehealth-scribe-sdk[fastapi]"
```

---

## Step 2: Initialize the Client

```python
from corehealth_sdk import CoreHealthClient

client = CoreHealthClient(
    base_url="https://api.corehealth.ng", # Or local Edge Node IP
    client_id="partner-emr-dev",
    client_secret="partner_dev_secret_2026",
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

If you use FastAPI, you can mount our pre-configured proxy router directly:

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

