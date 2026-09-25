"""
Main entry point for the diagnostic scanner. Runs all rule-based checks
against a target directory and returns findings in the exact shape the
Bedrock agent's Lambda action group expects:

{
  "findings": [
    {"type": "...", "detail": "...", "severity": "high|medium|low", "file": "..."}
  ]
}

Usage:
    python scan.py <path_to_target_repo>
"""
import sys
import json
import os

from dependency_scanner import scan_requirements
from deprecated_service_scanner import scan_directory_for_deprecated_services
from secrets_scanner import scan_directory_for_secrets


def run_full_scan(target_dir):
    findings = []

    requirements_path = os.path.join(target_dir, "requirements.txt")
    findings.extend(scan_requirements(requirements_path))
    findings.extend(scan_directory_for_deprecated_services(target_dir))
    findings.extend(scan_directory_for_secrets(target_dir))

    return {"findings": findings}


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "../sample_legacy_repo"
    result = run_full_scan(target)
    print(json.dumps(result, indent=2))
    print(f"\nTotal findings: {len(result['findings'])}", file=sys.stderr)