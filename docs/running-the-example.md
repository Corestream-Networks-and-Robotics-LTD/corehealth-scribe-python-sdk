# Running the Python/FastAPI Reference Example

This guide walks you through running the included FastAPI reference demo (`examples/fastapi-integration/`) in under 2 minutes.

---

## Step 1: Navigate to the Example Directory

```bash
cd examples/fastapi-integration
```

---

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 3: Start the FastAPI Server

```bash
python main.py
```

Output:
```text
====================================================
Starting FastAPI Reference Scribe Proxy on :3002
Open http://localhost:3002 in your browser
====================================================
```

---

## Step 4: Test in Browser

1. Open `http://localhost:3002` in your browser.
2. The page calls the backend proxy route (`/api/scribe/token`) to securely acquire an ephemeral token without exposing your client credentials.
3. Test speech dictation or note entry, click **Accept & Sign**, and observe the verified openEHR & FHIR payload received back at the Python server!

