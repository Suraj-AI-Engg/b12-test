import json
import hmac
import hashlib
import requests
from datetime import datetime, timezone
import os

# === CONFIG (EDIT THESE) ===
NAME = "suraj"
EMAIL = "suran.dev@gmail.com"
RESUME_LINK = "https://pdf-or-html-or-linkedin.example.com"
REPOSITORY_LINK = "https://github.com/Suraj-AI-Engg/b12-test"

# Signing secret (treat like a secret in real scenarios)
SECRET = b"hello-there-from-b12"

# === BUILD ACTION RUN LINK (for GitHub Actions) ===
run_id = os.getenv("GITHUB_RUN_ID")
repo = os.getenv("GITHUB_REPOSITORY")

action_run_link = f"https://github.com/{repo}/actions/runs/{run_id}"

# === GENERATE ISO 8601 TIMESTAMP ===
timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

# === BUILD PAYLOAD ===
payload = {
    "action_run_link": action_run_link,
    "email": EMAIL,
    "name": NAME,
    "repository_link": REPOSITORY_LINK,
    "resume_link": RESUME_LINK,
    "timestamp": timestamp,
}

# === CANONICAL JSON (sorted keys, no whitespace) ===
json_body = json.dumps(payload, separators=(",", ":"), sort_keys=True)

# === CREATE HMAC-SHA256 SIGNATURE ===
signature = hmac.new(SECRET, json_body.encode("utf-8"), hashlib.sha256).hexdigest()
signature_header = f"sha256={signature}"

# === SEND POST REQUEST ===
url = "https://b12.io/apply/submission"

headers = {
    "Content-Type": "application/json",
    "X-Signature-256": signature_header,
}

response = requests.post(url, data=json_body.encode("utf-8"), headers=headers)

# === HANDLE RESPONSE ===
if response.status_code == 200:
    try:
        data = response.json()
        receipt = data.get("receipt")
        print(f"Submission successful! Receipt: {receipt}")
    except Exception:
        print("Success, but failed to parse JSON:", response.text)
else:
    print(f"Request failed: {response.status_code}")
    print(response.text)
