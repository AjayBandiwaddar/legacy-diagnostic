# Demo Script — Legacy System Health Diagnostic Agent
**Team LSD — Legacy Systems Diagnosticians**

Keep this to ~4-5 minutes total. Practice the live demo portion at least twice
before presenting — nothing kills momentum like fumbling a live click.

---

## 1. Open with the problem (30 seconds)

> "Enterprises like TCS manage hundreds of client systems, and most of them
> carry years of accumulated technical debt — outdated dependencies,
> deprecated cloud services, exposed credentials. Today, finding this stuff
> is manual: engineers audit code by hand, findings live in spreadsheets,
> and there's no consistent way to decide what to fix first.
>
> We built an agent that does this automatically — and doesn't just flag
> problems, it explains *why they matter* and *what to do about them*, the
> way a senior engineer would."

## 2. Show the architecture (30 seconds — use the diagram/slide, not code)

> "Three parts: rule-based scanners find the raw issues. AWS Bedrock
> reasons over those findings — prioritizing, explaining consequence,
> not just restating facts. And a live interface shows that reasoning
> transparently, not as a black-box score."

## 3. Live demo (2-2.5 minutes)

1. Open the UI (`http://127.0.0.1:8000`)
2. Point out the target path is a deliberately seeded "legacy" sample repo
3. Click **Run Diagnostic Scan** — narrate while it loads:
   > "This is scanning real code right now — checking dependency versions,
   > deprecated AWS SDK usage, and hardcoded secrets."
4. When results appear, walk through:
   - The **executive summary** — one line, the overall picture
   - The **fix first** callout — "if judges remember one thing about this
     repo, it's this"
   - Scroll through 2-3 **CRITICAL** findings — read one `why_it_matters`
     line aloud, since that's the actual differentiator (not just "found a
     problem" but "here's why it's dangerous")
   - Point out the color-coded priority tiers — CRITICAL/HIGH/MEDIUM/LOW

**If Bedrock is live by demo time:** mention explicitly —
> "This reasoning you're seeing is coming live from AWS Bedrock, not a
> canned script."

**If still on the mock/fallback reasoning layer:** don't hide it, own it
confidently —
> "The reasoning layer here is running on our own prioritization logic
> right now — the full pipeline is built end-to-end and wired to call
> Bedrock directly, which our teammate has been getting access to in
> parallel."
Judges respect honesty about scope far more than a claim that falls apart
under a follow-up question.

## 4. Tie back to TCS (30 seconds)

> "Legacy modernization is one of TCS's core service lines. A tool like
> this is exactly the kind of AI-augmented service delivery that could
> plausibly speed up real client audits — faster, more consistent, and the
> reasoning is transparent enough that junior engineers can learn from it,
> not just trust a mystery score."

## 5. Close (15 seconds)

> "Built end-to-end in 24 hours — scanners, AI reasoning, and a live
> interface, all on AWS. Happy to take questions."

---

## Anticipated judge questions — have answers ready

- **"How does this scale beyond Python?"**
  → "Scanners are modular — the dependency, deprecated-service, and
  secrets checks all take a directory in, JSON findings out. Adding a
  Node.js or Java scanner is the same pattern, not a rebuild."

- **"How do you avoid false positives?"**
  → "The scanners flag broadly on purpose — the reasoning layer is
  what filters severity by context (e.g. a secret in a test file vs.
  production code), not the raw scanner output."

- **"What's the actual AWS cost at scale?"**
  → Have your Bedrock/Lambda/Cost Explorer cost estimate ready if you
  discussed this earlier (~$25-35 worst case for a hackathon-scale demo;
  frame per-scan cost at production scale as low since it's mostly a
  single reasoning call per scan).

- **"Why rule-based scanners instead of ML detection?"**
  → "Determinism and speed — rule-based checks are instant and auditable.
  The AI value-add is in the reasoning and prioritization layer, not in
  guessing whether something is outdated."