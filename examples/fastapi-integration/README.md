# FastAPI Reference Integration for CoreHealth AI Scribe

This directory contains a complete, self-contained reference application demonstrating how partner healthcare systems and EMR backends integrate the `corehealth-scribe-sdk` Python package.

---

## Architecture Overview

```
Browser (Partner EMR Frontend)
       │
       ▼ (Fetch ephemeral token)
FastAPI Proxy Server (main.py on :3002) ─── holds client_secret in .env
       │
       ▼ (Exchange credentials for SKT_ JWT)
CoreHealth Cloud / Edge Backend (:8000)
```

The FastAPI backend securely holds your client credentials (`CH_CLIENT_ID` and `CH_CLIENT_SECRET`) in an environment file (`.env`). It mounts the pre-built `create_scribe_router` to proxy authentication, token minting, catalog search, format conversion, and sign-off events without exposing secret keys to client browsers.

---

## 1. Virtual Environment Setup (`venv`)

Always isolate dependencies inside a dedicated Python virtual environment.

### Linux / macOS

```bash
# Navigate to the example directory
cd examples/fastapi-integration

# Create a clean virtual environment using Python 3.10+
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip to latest standard
pip install --upgrade pip
```

### Windows (PowerShell)

```powershell
# Navigate to the example directory
cd examples\fastapi-integration

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
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

## 2. Environment Configuration (`.env`)

1. Copy the provided `.env.example` template to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and verify or customize your parameters:

   ```ini
   # CoreHealth Edge or Cloud backend URL (without trailing slash)
   CH_BASE_URL=http://127.0.0.1:8000

   # Client Credentials issued in CoreHealth Admin -> Hospital Configuration -> AI Scribe & SDK
   CH_CLIENT_ID=your_client_id_here
   CH_CLIENT_SECRET=your_client_secret_here

   # FastAPI server port
   PORT=3002

   # Consultation context defaults
   CH_DEFAULT_LOCALE=en-NG
   CH_DEFAULT_PATIENT_ID=492
   CH_DEFAULT_ENCOUNTER_ID=1017
   CH_DEFAULT_CLINICIAN_ID=38
   ```

> [!NOTE]
> When integrating with CoreHealth Cloud in production, change `CH_BASE_URL` to `https://corehealth.corestream.ng` and provide your production `CH_CLIENT_ID` and `CH_CLIENT_SECRET`.

---

## 3. Install Dependencies

Install the FastAPI server requirements and the local SDK package:

```bash
# Install FastAPI and proxy dependencies
pip install -r requirements.txt

# (Optional) Install the parent corehealth_sdk package in editable mode
pip install -e ../../
```

---

## 4. Run the Reference Server

Launch the application using Uvicorn or the Python entrypoint:

```bash
python main.py
```

Or via direct Uvicorn CLI:

```bash
uvicorn main:app --reload --port 3002
```

The console will output:

```
====================================================
Starting FastAPI Reference Scribe Proxy on :3002
Open http://localhost:3002 in your browser
Connected to CoreHealth backend: http://127.0.0.1:8000
====================================================
```

Open `http://localhost:3002` in your browser to interact with the full consultation and dictation workflow.

---

## 5. Verify Proxy API Endpoints

Once running, you can test the proxy routes via curl or OpenAPI documentation at `http://localhost:3002/docs`:

```bash
# Test token minting
curl -X GET "http://localhost:3002/api/scribe/token?patient_id=492&encounter_id=1017"

# Test catalog category discovery
curl -X GET "http://localhost:3002/api/scribe/categories"

# Test catalog item search
curl -X GET "http://localhost:3002/api/scribe/catalogs/items?q=malaria"
```
