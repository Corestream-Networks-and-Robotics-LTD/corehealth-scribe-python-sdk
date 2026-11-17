# Running the Python / FastAPI Reference Example

This guide walks you through setting up an isolated virtual environment (`venv`), configuring your environment variables via `.env`, and running the included FastAPI reference demo (`examples/fastapi-integration/`).

---

## Step 1: Create and Activate Virtual Environment (`venv`)

Always isolate project dependencies in a dedicated virtual environment.

### Linux / macOS

```bash
# Navigate to the reference example directory
cd examples/fastapi-integration

# Create a virtual environment using Python 3.10+
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip to latest version
pip install --upgrade pip
```

### Windows (PowerShell)

```powershell
cd examples\fastapi-integration
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### Windows (Command Prompt)

```cmd
cd examples\fastapi-integration
python -m venv venv
venv\Scripts\activate.bat
python -m pip install --upgrade pip
```

---

## Step 2: Configure Environment Variables (`.env`)

Copy the provided environment template to `.env`:

```bash
cp .env.example .env
```

Review `.env` and configure your CoreHealth connection parameters:

```ini
# CoreHealth Backend Base URL (Edge or Cloud)
CH_BASE_URL=http://127.0.0.1:8000

# Client Credentials (from CoreHealth Admin -> Hospital Configuration -> AI Scribe & SDK)
CH_CLIENT_ID=your_client_id_here
CH_CLIENT_SECRET=your_client_secret_here

# FastAPI Proxy Port
PORT=3002

# Default Consultation Context
CH_DEFAULT_LOCALE=en-NG
CH_DEFAULT_PATIENT_ID=492
CH_DEFAULT_ENCOUNTER_ID=1017
CH_DEFAULT_CLINICIAN_ID=38

# Token TTL in seconds (1 hour)
CH_TOKEN_TTL=3600
```

---

## Step 3: Install Dependencies

With your virtual environment active, install the FastAPI requirements and the local SDK package:

```bash
# Install FastAPI, Uvicorn, HTTPX, and python-dotenv
pip install -r requirements.txt

# (Optional) Install local SDK package in editable mode
pip install -e ../../
```

---

## Step 4: Start the FastAPI Server

Launch the reference proxy server:

```bash
python main.py
```

Output:
```text
====================================================
Starting FastAPI Reference Scribe Proxy on :3002
Open http://localhost:3002 in your browser
Connected to CoreHealth backend: http://127.0.0.1:8000
====================================================
```

---

## Step 5: Test in Browser & Verify Proxy APIs

1. Open `http://localhost:3002` in your browser.
2. The browser automatically calls the backend proxy endpoint (`/api/scribe/token`), which securely mints an ephemeral `SKT_` token using your client credentials without exposing secrets to client-side JavaScript.
3. Test speech dictation or click **Simulate Sample**, then click **Process Note** to test AI structuring with `gemini-2.5-flash`.
4. Review recommended clinical orders with piped dosages (e.g. `80/480mg | BD | 3 days | Oral`), stage additional orders, and click **Accept & Sign**.
5. Observe the dual-standard openEHR `COMPOSITION.encounter.v1` and HL7 FHIR R4 Transaction Bundle received back at the Python backend!

### Verify Endpoints via CLI

```bash
# Test token minting route
curl -s "http://localhost:3002/api/scribe/token?patient_id=492&encounter_id=1017" | jq .

# Test catalog category discovery
curl -s "http://localhost:3002/api/scribe/categories" | jq .

# Test clinical item search
curl -s "http://localhost:3002/api/scribe/catalogs/items?q=malaria" | jq .
```
