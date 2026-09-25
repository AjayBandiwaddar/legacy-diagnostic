"""
Scans Python source files for references to deprecated/retired AWS services
and known-legacy SDK patterns. Rule-based (regex over source text), no ML.
"""
import os
import re

# boto3 client names for AWS services that are retired or deprecated.
# Extend before demo if you seed more examples.
DEPRECATED_SERVICES = {
    "sdb": "Amazon SimpleDB — retired service, no longer recommended for new use",
    "machinelearning": "Amazon Machine Learning — retired 2019, replaced by SageMaker",
    "importexport": "AWS Import/Export (Disk) — retired, replaced by Snowball",
    "opsworks": "AWS OpsWorks Stacks — deprecated in favor of Systems Manager",
}


def scan_file_for_deprecated_services(filepath):
    findings = []
    if not os.path.exists(filepath):
        return findings

    with open(filepath, "r") as f:
        content = f.read()

    for service, reason in DEPRECATED_SERVICES.items():
        pattern = rf"boto3\.client\(\s*['\"]" + re.escape(service) + r"['\"]"
        if re.search(pattern, content):
            findings.append({
                "type": "deprecated_aws_service",
                "detail": f"Uses '{service}' client — {reason}",
                "severity": "high",
                "file": os.path.basename(filepath),
            })

    return findings


def scan_directory_for_deprecated_services(dirpath):
    all_findings = []
    for root, _, files in os.walk(dirpath):
        for fname in files:
            if fname.endswith(".py"):
                all_findings.extend(
                    scan_file_for_deprecated_services(os.path.join(root, fname))
                )
    return all_findings


if __name__ == "__main__":
    import json
    results = scan_directory_for_deprecated_services("../sample_legacy_repo")
    print(json.dumps(results, indent=2))
