"""
B12 Submission Script

What this script does:
----------------------
This script prepares and sends a signed POST request to B12's submission endpoint.
It is designed to run inside a CI environment (e.g., GitHub Actions) so that the
submission can be verified via the action run link.


Steps performed by this script:
------------------------------
1. Collect user and repository details
2. Generate a timestamp in ISO 8601 format
3. Build a JSON payload with required fields
4. Convert payload into canonical JSON (sorted keys, compact format)
5. Generate HMAC-SHA256 signature of the JSON body
6. Send POST request with signature header
7. Print receipt returned by the API
"""

import json
import hmac
import hashlib
import logging
import requests
from datetime import datetime, timezone

logger = logging.getLogger("__name__")

NAME = "suraj"
EMAIL = "suraj.dev.work@gmail.com"
RESUME_LINK = "https://drive.google.com/file/d/1Z-IADOzusaPIGKP_SgW3_a6Md21R2s1Z/view"
REPOSITORY_LINK = "https://github.com/Suraj-AI-Engg/b12-test"

SECRET = b"hello-there-from-b12"

action_run_link = "https://github.com/Suraj-AI-Engg/b12-test/actions/runs/24878035258"

# Generate current time in ISO 8601 format with milliseconds and 'Z' (UTC)
timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

payload = {
    "action_run_link": action_run_link,
    "email": EMAIL,
    "name": NAME,
    "repository_link": REPOSITORY_LINK,
    "resume_link": RESUME_LINK,
    "timestamp": timestamp,
}

# === CANONICAL JSON CONVERSION ===
# Important requirements:
# - Keys must be sorted alphabetically
# - No extra whitespace
# This ensures consistent hashing/signing
json_body = json.dumps(payload, separators=(",", ":"), sort_keys=True)

# We sign the raw JSON string using the secret key
signature = hmac.new(SECRET, json_body.encode("utf-8"), hashlib.sha256).hexdigest()
signature_header = f"sha256={signature}"

url = "https://b12.io/apply/submission"
headers = {
    "Content-Type": "application/json",
    "X-Signature-256": signature_header,
}

response = requests.post(url, data=json_body.encode("utf-8"), headers=headers)
if response.status_code == 200:
    try:
        data = response.json()
        receipt = data.get("receipt")
        logger.info(f"Submission successful! Receipt: {receipt}")
    except Exception as ex:
        logger.exception(f"Success, but failed to parse JSON: {response.text}, Error: {ex}")
else:
    logger.error(f"Request failed: {response}")
