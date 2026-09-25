"""
FastAPI backend for the Legacy System Health Diagnostic Agent demo.

Serves the UI and exposes a /scan endpoint that:
1. Runs the rule-based scanners against a target directory
2. Feeds results through the reasoning step (mock_agent for now)
3. Returns the prioritized roadmap as JSON

To swap the mock reasoning for the real Bedrock agent once AWS access
clears: replace the `run_reasoning()` function body with a boto3
bedrock-agent-runtime invoke_agent call. The return shape must match
what mock_reasoning() currently returns so the frontend doesn't need
changes.

Run:
    pip install fastapi uvicorn
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

SCANNER_DIR = os.path.join(os.path.dirname(__file__), "..", "scanner")
sys.path.insert(0, SCANNER_DIR)

from dependency_scanner import scan_requirements
from deprecated_service_scanner import scan_directory_for_deprecated_services
from secrets_scanner import scan_directory_for_secrets
from mock_agent import mock_reasoning

app = FastAPI(title="Legacy System Health Diagnostic Agent")


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
    Swap point: replace this with a real Bedrock agent invocation once
    AWS access is confirmed. Must return the same shape as mock_reasoning().
    """
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


app.mount("/static", StaticFiles(directory=os.path.dirname(__file__)), name="static")