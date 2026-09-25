"""
FastAPI backend for the Legacy System Health Diagnostic Agent demo.

Serves the UI and exposes a /scan endpoint that:
1. Runs the rule-based scanners against a target directory
2. Feeds results through the reasoning step (mock_agent for now)
3. Returns the prioritized roadmap as JSON

Run:
    pip install fastapi uvicorn boto3
    uvicorn main:app --reload

Then open http://127.0.0.1:8000
"""
import sys
import os
import json

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# make ../scanner importable
SCANNER_DIR = os.path.join(os.path.dirname(__file__), "..", "scanner")
sys.path.insert(0, SCANNER_DIR)

from dependency_scanner import scan_requirements
from deprecated_service_scanner import scan_directory_for_deprecated_services
from secrets_scanner import scan_directory_for_secrets
from mock_agent import mock_reasoning

import boto3

app = FastAPI(title="Legacy System Health Diagnostic Agent")

# --- Bedrock direct-call config ---
# Set USE_BEDROCK = True once your friend confirms model access + region.
# BEDROCK_MODEL_ID: whatever model got approved — examples:
#   "amazon.nova-pro-v1:0"
#   "meta.llama3-1-70b-instruct-v1:0"
#   "mistral.mistral-large-2407-v1:0"
# Converse API works the same across all of these, so this is the only
# line that needs to change based on which model your friend got approved.
USE_BEDROCK = False
BEDROCK_REGION = "us-east-1"
BEDROCK_MODEL_ID = "amazon.nova-pro-v1:0"  # placeholder — update once confirmed

bedrock_runtime = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION) if USE_BEDROCK else None

SYSTEM_PROMPT = """You are a legacy system diagnostic agent for enterprise codebases. You receive
a JSON list of findings from automated scanners (outdated dependencies,
deprecated AWS service usage, hardcoded secrets) and produce a prioritized,
explainable modernization roadmap.

For each finding:
1. Explain WHY it matters in one clear sentence — connect it to real
   consequence (security exposure, migration blocker, maintenance cost).
2. Assign a priority tier: CRITICAL, HIGH, MEDIUM, or LOW.
3. Suggest a concrete fix.

You MUST respond with ONLY valid JSON, no other text, in exactly this shape:
{
  "executive_summary": "2-3 sentence overview",
  "roadmap": [
    {
      "priority": "CRITICAL|HIGH|MEDIUM|LOW",
      "finding_type": "...",
      "file": "...",
      "what_it_is": "...",
      "why_it_matters": "...",
      "suggested_fix": "..."
    }
  ],
  "fix_first": "one sentence naming the single most urgent fix"
}

Do not include markdown formatting, code fences, or any text outside the JSON object."""


class ScanRequest(BaseModel):
    target_path: str = "../sample_legacy_repo"


def run_scan(target_dir):
    findings = []
    requirements_path = os.path.join(target_dir, "requirements.txt")
    findings.extend(scan_requirements(requirements_path))
    findings.extend(scan_directory_for_deprecated_services(target_dir))
    findings.extend(scan_directory_for_secrets(target_dir))
    return {"findings": findings}


def run_reasoning(scan_result):
    """
    Calls Bedrock directly via the Converse API when USE_BEDROCK is True.
    Falls back to the local mock reasoning otherwise, so the app never
    breaks if Bedrock isn't ready yet or a call fails.
    """
    if not USE_BEDROCK:
        return mock_reasoning(scan_result)

    user_message = (
        "Here are the scan findings for a target system. Produce the "
        "prioritized modernization roadmap as specified:\n\n"
        + json.dumps(scan_result, indent=2)
    )

    try:
        response = bedrock_runtime.converse(
            modelId=BEDROCK_MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[
                {"role": "user", "content": [{"text": user_message}]}
            ],
            inferenceConfig={"maxTokens": 2000, "temperature": 0.3},
        )
        output_text = response["output"]["message"]["content"][0]["text"]

        # strip accidental code fences if the model adds them anyway
        cleaned = output_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]

        return json.loads(cleaned)

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        # Model responded but not in the expected shape — fall back
        # gracefully rather than crashing the demo.
        return {
            "executive_summary": f"[Bedrock response could not be parsed: {e}] Falling back to local reasoning.",
            "roadmap": mock_reasoning(scan_result)["roadmap"],
            "fix_first": mock_reasoning(scan_result)["fix_first"],
        }
    except Exception as e:
        # Any AWS/network error — don't let it kill the demo, fall back.
        print(f"Bedrock call failed: {e}")
        return mock_reasoning(scan_result)


@app.post("/scan")
def scan_endpoint(req: ScanRequest):
    target_dir = os.path.join(os.path.dirname(__file__), req.target_path)
    target_dir = os.path.normpath(target_dir)

    if not os.path.isdir(target_dir):
        raise HTTPException(status_code=400, detail=f"Target path not found: {target_dir}")

    scan_result = run_scan(target_dir)
    roadmap = run_reasoning(scan_result)

    return {
        "raw_findings": scan_result,
        "roadmap": roadmap,
    }


@app.get("/")
def serve_index():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(index_path)


# serve any other static assets (css/js) if added later
app.mount("/static", StaticFiles(directory=os.path.dirname(__file__)), name="static")