# Legacy System Health Diagnostic Agent
**Team LSD — Legacy Systems Diagnosticians**

An AWS Bedrock-powered agent that scans a codebase for legacy risk (outdated deps,
deprecated AWS usage, missing docs, hardcoded secrets) and produces a prioritized,
explainable modernization roadmap.

## Structure
```
lsd-legacy-diagnostic/
├── scanner/              # Rule-based diagnostic scanners (Ajay's part)
├── sample_legacy_repo/   # Deliberately outdated sample repo to scan for demo
├── lambda/                # AWS Lambda handler wiring scanner -> Bedrock agent
├── ui/                    # Demo front end
└── docs/                  # Problem statement, architecture, spec docs
```

## Status
- [ ] Scanner logic
- [ ] Sample legacy repo seeded
- [ ] Bedrock agent shell (AWS side)
- [ ] Lambda wired end-to-end
- [ ] UI
- [ ] Demo script

See `docs/` for the full project overview and the AWS-vs-build split spec.
