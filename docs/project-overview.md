# Project Overview

## Team
**LSD — Legacy Systems Diagnosticians**

## Project Name
**Legacy System Health Diagnostic Agent**

*(working alt names, if you want options: "SystemDoc," "LegacyLens," "DebtRadar" — but the current name is clear and on-brand for the team name, so it's a safe default)*

## Problem Statement

Enterprises — and especially large IT services providers like TCS managing hundreds of client systems — carry enormous amounts of legacy technical debt: outdated dependencies, deprecated cloud service usage, undocumented systems, and quiet security drift that accumulates over years of maintenance.

Today, identifying this debt is largely manual: engineers audit code and infrastructure by hand, findings live in scattered spreadsheets or tribal knowledge, and there's no consistent, reasoned way to prioritize *what to fix first* versus what to leave alone. This is slow, inconsistent across teams, and doesn't scale across the sheer number of systems a company like TCS manages for its clients.

**The gap:** there is no lightweight, autonomous tool that scans a system, reasons about *why* something matters (not just flags it), and produces a prioritized, explainable modernization roadmap — the way a senior engineer would, but instantly and consistently.

## Solution

**Legacy System Health Diagnostic Agent** is an autonomous AI agent, built on AWS Bedrock, that:

1. **Scans** a target codebase or system using a set of rule-based diagnostic checks — outdated dependencies, deprecated AWS service usage, missing documentation, hardcoded secrets, and other legacy risk signals.
2. **Reasons** over the raw findings using a Claude-powered Bedrock Agent — not just listing problems, but explaining *why* each one matters and how it compounds risk (security exposure, maintenance cost, migration blockers).
3. **Prioritizes** the findings into a clear, actionable modernization roadmap — what to fix first, what can wait, and why — instead of leaving engineers to manually triage a flat list of issues.
4. **Presents** the reasoning transparently through a simple interface, so the output is something a team lead can actually read and act on, not a black-box score.

### Why this matters for TCS specifically
Legacy modernization is one of TCS's core service lines — helping enterprise clients migrate and modernize aging systems is a huge, ongoing part of the business. A tool like this demonstrates exactly the kind of AI-augmented service delivery that could plausibly get built into TCS's actual client engagements: faster audits, consistent prioritization, and reasoning that junior engineers can learn from rather than a mysterious automated score.

### Architecture (one-line summary)
Sample repo/system → rule-based scanners → AWS Lambda → Bedrock Agent (Claude) reasons over findings → prioritized roadmap → simple UI displaying the reasoning trace and final recommendations.

### What makes this a strong hackathon entry
- **Genuinely agentic**, not just a wrapper around an LLM call — it scans, reasons, and prioritizes in a multi-step chain
- **Cloud-native by design** — AWS Bedrock, Lambda, IAM are core to the architecture, not bolted on
- **Directly maps to TCS's real business**, so the pitch writes itself
- **Explainable**, which matters more to enterprise judges than raw accuracy — they want to trust the reasoning, not just see a score
