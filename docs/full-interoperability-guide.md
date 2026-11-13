# Full Interoperability Guide: openEHR, FHIR R4 & NDPA

CoreHealth v2 provides comprehensive interoperability endpoints across four major healthcare data standards:

1. **HL7 FHIR R4** (RESTful resources with LOINC, WHO ATC, and ICD-10 bindings)
2. **openEHR ITS-REST** (Archetypes, Templates, Compositions, and Archetype Query Language / AQL)
3. **OpenEMR Compatibility & C-CDA XML** (Standard endpoints for legacy migration and continuity of care)
4. **NDPA 2023 Statutory Privacy** (Nigeria Data Protection Act affirmative consent & deterministic pseudonymization)

---

## 1. Authentication for Interoperability Endpoints

All endpoints under `/api/fhir/r4/*`, `/api/openehr/v1/*`, and `/api/ndpa/v1/*` are guarded by `interop.auth` middleware:

1. **Sanctum Bearer Token**: `Authorization: Bearer <token>`
   - Acquire via `POST /sanctum/token` with user credentials.
2. **SHA-256 Basic Auth**: `Authorization: Basic <base64(user:secret)>`
   - Configured in `services.interop.basic_user` and `services.interop.basic_secret` for machine-to-machine replication pipelines.
3. **Public Exemption**: `/api/fhir/r4/metadata` (CapabilityStatement) is open per FHIR Foundation specifications.

---

## 2. HL7 FHIR R4 Standard Workflows

### Search Patients
```http
GET /api/fhir/r4/Patient?name=Oladipo
Authorization: Bearer {{token}}
Accept: application/fhir+json
```

### Record Vital Signs (Observation with LOINC 55284-4)
```http
POST /api/fhir/r4/Observation
Authorization: Bearer {{token}}
Content-Type: application/fhir+json

{
  "resourceType": "Observation",
  "status": "final",
  "code": {
    "coding": [{ "system": "http://loinc.org", "code": "55284-4", "display": "Blood pressure panel" }]
  },
  "subject": { "reference": "Patient/492" },
  "component": [
    {
      "code": { "coding": [{ "system": "http://loinc.org", "code": "8480-6", "display": "Systolic" }] },
      "valueQuantity": { "value": 128, "unit": "mm[Hg]", "system": "http://unitsofmeasure.org" }
    },
    {
      "code": { "coding": [{ "system": "http://loinc.org", "code": "8462-4", "display": "Diastolic" }] },
      "valueQuantity": { "value": 82, "unit": "mm[Hg]", "system": "http://unitsofmeasure.org" }
    }
  ]
}
```

### Prescribe Medication (MedicationRequest with WHO ATC)
```http
POST /api/fhir/r4/MedicationRequest
Authorization: Bearer {{token}}
Content-Type: application/fhir+json

{
  "resourceType": "MedicationRequest",
  "status": "active",
  "intent": "order",
  "medicationCodeableConcept": {
    "coding": [{ "system": "http://www.whocc.no/atc", "code": "A10BA02", "display": "Metformin" }]
  },
  "subject": { "reference": "Patient/492" },
  "encounter": { "reference": "Encounter/1017" },
  "dosageInstruction": [{ "text": "500mg BD with meals" }]
}
```

---

## 3. openEHR ITS-REST & Archetype Query Language (AQL)

### Create EHR Record
```http
POST /api/openehr/v1/ehr
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "subject": {
    "externalRef": {
      "id": "PATIENT-492",
      "namespace": "corehealth",
      "type": "PERSON"
    }
  }
}
```

### Run AQL Query
Retrieve blood pressure trends across all encounters:
```http
POST /api/openehr/v1/query/aql
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "q": "SELECT e/ehr_id/value, o/data[at0001]/events[at0006]/data[at0003]/items[at0004]/value/magnitude AS systolic, o/data[at0001]/events[at0006]/data[at0003]/items[at0005]/value/magnitude AS diastolic FROM EHR e CONTAINS OBSERVATION o[openEHR-EHR-OBSERVATION.blood_pressure.v2]",
  "offset": 0,
  "fetch": 20
}
```

---

## 4. Statutory NDPA 2023 Consent Management

### Record Explicit Consent
```http
POST /api/ndpa/v1/consent
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "patient_id": 492,
  "consent_type": "TREATMENT",
  "ndpa_lawful_basis": "EXPLICIT_CONSENT",
  "notes": "Patient consented to routine EHR processing and clinical observations."
}
```

---

## 5. Postman Collection & OpenAPI Specification

- **Postman Collection**: Located in this repo at `postman/CoreHealth-Interop-Collection.json`. Import into Postman to run all 25+ requests with pre-built tests and automated token extraction.
- **OpenAPI 3.0 Specification**: Located in this repo at `openapi/corehealth-interop-openapi.json`. Import into Swagger, Postman, or generate SDK client code via OpenAPI Generator.
