"""
Scans Python source files for likely hardcoded secrets/credentials.
Regex-based pattern matching, no ML. Intentionally broad — false positives
are acceptable for a hackathon demo (flag first, agent reasons about severity).
"""
import os
import re

SECRET_PATTERNS = [
    ("AWS Access Key ID", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS Secret Key (variable name)", re.compile(r"(?i)aws_secret_access_key\s*=\s*['\"][^'\"]+['\"]")),
    ("Generic API Key (variable name)", re.compile(r"(?i)api_key\s*=\s*['\"][^'\"]{10,}['\"]")),
    ("Password (variable name)", re.compile(r"(?i)(password|passwd)\s*=\s*['\"][^'\"]+['\"]")),
    ("Stripe-style secret key", re.compile(r"sk-live-[A-Za-z0-9]{16,}")),
]


def scan_file_for_secrets(filepath):
    findings = []
    if not os.path.exists(filepath):
        return findings

    with open(filepath, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines, start=1):
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append({
                    "type": "hardcoded_secret",
                    "detail": f"Possible {label} hardcoded at line {i}",
                    "severity": "high",
                    "file": os.path.basename(filepath),
                })

    return findings


def scan_directory_for_secrets(dirpath):
    all_findings = []
    for root, _, files in os.walk(dirpath):
        for fname in files:
            if fname.endswith(".py"):
                all_findings.extend(
                    scan_file_for_secrets(os.path.join(root, fname))
                )
    return all_findings


if __name__ == "__main__":
    import json
    results = scan_directory_for_secrets("../sample_legacy_repo")
    print(json.dumps(results, indent=2))