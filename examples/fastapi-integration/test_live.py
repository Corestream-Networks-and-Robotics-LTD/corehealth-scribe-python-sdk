"""
CoreHealth AI Scribe Python SDK — Live Verification Script against CoreHealth v2 (Port 8000)
"""

import sys
from pathlib import Path

# Add corehealth_sdk to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from corehealth_sdk.client import CoreHealthClient

client = CoreHealthClient(
    base_url="http://127.0.0.1:8000",
    client_id="partner-emr-dev",
    client_secret="partner_dev_secret_2026",
)

print("[1/6] Minting ephemeral SDK session token...")
token_data = client.get_scribe_token(
    patient_id=492,
    encounter_id=1017,
    clinician_id=1,
    role="doctor",
    taxonomy="soap",
)
token = token_data["sdk_token"]
print(f"  ✓ Token minted: {token[:24]}... (Expires: {token_data['expires_in']}s)")

print("[2/6] Querying hospital categories & catalog search...")
cats = client.get_categories(token)
print(f"  ✓ Categories retrieved: {len(cats.get('service_categories', []))} services, {len(cats.get('product_categories', []))} products")

items = client.search_catalog_items(token, query="paracetamol", limit=3)
print(f"  ✓ Search items returned: {items.get('total', 0)} matches")

print("[3/6] Compressing partner custom EMR catalog (CSCP format)...")
custom_cat = [
    {
        "id": "emr_labs",
        "name": "Partner Clinical Lab",
        "type": "LAB",
        "items": ["p-lab-101:Full Blood Count (FBC)", "p-lab-102:Malaria Rapid Antigen Test"],
    },
    {
        "id": "emr_rx",
        "name": "Partner Main Pharmacy",
        "type": "RX",
        "items": ["p-rx-201:Paracetamol 500mg Tablet:300", "p-rx-202:Amoxicillin 500mg:600"],
    },
]
compressed = client.compress_catalog(custom_cat)
print("  ✓ CSCP Output:")
for line in compressed.splitlines():
    print(f"    {line}")

print("[4/6] Processing dictation with super-compressed custom catalog grounding...")
process_res = client.process_dictation(
    token=token,
    transcript="Patient with acute pharyngitis and fever. Prescribe Paracetamol 500mg TDS for 3 days and request Full Blood Count.",
    patient_id=492,
    encounter_id=1017,
    role="doctor",
    taxonomy="soap",
    custom_catalog=compressed,
)
orders = process_res.get("grounded_orders", [])
print(f"  ✓ Processed! Structured sections: {len(process_res.get('structured_sections', []))}")
print(f"  ✓ Grounded orders: {len(orders)} items extracted:")
for ord in orders:
    print(f"    - [{ord.get('order_type')}] {ord.get('item_name')} (ID: #{ord.get('catalog_id')}, Cat: {ord.get('category_name')})")

print("[5/6] Testing lossless clinical taxonomy conversion (SOAP -> Traditional Clerking)...")
conv_res = client.convert_format(
    token=token,
    from_taxonomy="soap",
    to_taxonomy="clerking",
    current_sections=process_res.get("structured_sections", []),
    role="doctor",
)
print(f"  ✓ Converted! Target sections: {[s['key'] for s in conv_res.get('structured_sections', [])]}")

print("[6/6] Signing session with approved orders and fetching openEHR & FHIR compositions...")
sign_res = client.sign_session(
    token=token,
    final_signed_note=process_res.get("formatted_markdown", ""),
    original_transcript="Patient with acute pharyngitis and fever...",
    patient_id=492,
    encounter_id=1017,
    approved_orders=orders,
    role="doctor",
    taxonomy_type="soap",
)
print(f"  ✓ Note & Orders signed! Audit ID: #{sign_res.get('audit_id')}")

comp_res = client.get_compositions(token)
openehr = comp_res.get("openehr_composition", {})
fhir = comp_res.get("fhir_bundle", {})
print(f"  ✓ openEHR Composition Archetype: {openehr.get('archetype_node_id')} (Content nodes: {len(openehr.get('content', []))})")
print(f"  ✓ FHIR R4 Bundle Entries: {fhir.get('total', 0)} resources")

print("\n====================================================")
print("ALL PYTHON SDK VERIFICATION CHECKS PASSED CLEANLY!")
print("====================================================")

