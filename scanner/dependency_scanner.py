"""
Checks requirements.txt for known-outdated package versions.
Rule-based, no ML: compares against a hand-maintained "known old" threshold table.
Extend KNOWN_MIN_VERSIONS as needed before the demo.
"""
import re
import os

KNOWN_MIN_VERSIONS = {
    "django": (3, 2, 0),
    "requests": (2, 25, 0),
    "flask": (2, 0, 0),
    "boto3": (1, 26, 0),
    "pyyaml": (5, 4, 0),
    "jinja2": (3, 0, 0),
    "numpy": (1, 20, 0),
    "paramiko": (2, 9, 0),
    "cryptography": (3, 4, 0),
}


def _parse_version(v):
    parts = re.findall(r"\d+", v)
    return tuple(int(p) for p in parts[:3]) if parts else (0, 0, 0)


def scan_requirements(filepath):
    findings = []
    if not os.path.exists(filepath):
        return findings

    with open(filepath, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"([A-Za-z0-9_\-\.]+)\s*==\s*([0-9][A-Za-z0-9\.\-]*)", line)
        if not match:
            continue
        pkg, version = match.group(1).lower(), match.group(2)
        min_version = KNOWN_MIN_VERSIONS.get(pkg)
        if min_version is None:
            continue
        current = _parse_version(version)
        if current < min_version:
            severity = "high" if current[0] < min_version[0] else "medium"
            findings.append({
                "type": "outdated_dependency",
                "detail": f"{pkg}=={version} is below recommended minimum "
                          f"{'.'.join(map(str, min_version))}",
                "severity": severity,
                "file": os.path.basename(filepath),
            })

    return findings


if __name__ == "__main__":
    import json
    results = scan_requirements("../sample_legacy_repo/requirements.txt")
    print(json.dumps(results, indent=2))