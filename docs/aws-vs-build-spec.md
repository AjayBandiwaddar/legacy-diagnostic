# LSD — Legacy System Health Diagnostic Agent
## Work Split: AWS/Cloud Part vs Build Part

This doc is the single source of truth for who owns what. Follow it exactly — no overlap, no guessing.

---

## PART 1: AWS / CLOUD (Friend's part)

**Goal:** Stand up the cloud infrastructure so the agent has somewhere to run and something to call. You are NOT writing the diagnostic logic — you're building the pipes.

### Step 1 — Bedrock Model Access (do this FIRST, before anything else)
1. Go to AWS Console → Bedrock → Model access
2. Request access to **Anthropic Claude** (any Sonnet-class model available in your region)
3. This can take minutes to hours to approve — start it immediately, then move to Step 2 while waiting
4. Confirm region: use `us-east-1` or `us-west-2` — these have the most reliable Bedrock model availability

### Step 2 — Billing Safety Net
1. AWS Console → Billing → Budgets → Create budget
2. Set a **cost budget of $30**, alert threshold at 80%
3. Add your email for the alert
4. Do this before creating any other resource

### Step 3 — IAM Setup
1. Create an IAM role named `lsd-agent-execution-role`
2. Attach these policies:
   - `AmazonBedrockFullAccess` (or scope down to `bedrock:InvokeModel`, `bedrock:InvokeAgent` if you want to be tighter)
   - `AWSLambdaBasicExecutionRole`
   - Custom inline policy for Lambda-to-Lambda invoke if needed
3. Create a second role `lsd-lambda-role` for the Lambda functions specifically, trust policy = `lambda.amazonaws.com`

### Step 4 — Bedrock Agent Shell
1. Bedrock Console → Agents → Create Agent
2. Name: `lsd-diagnostic-agent`
3. Model: the Claude model you got access to in Step 1
4. Instructions (paste this as the agent's system instructions — the build-part person may refine this later, but get a working shell now):
   ```
   You are a legacy system diagnostic agent. You receive scan results about
   a codebase or infrastructure (outdated dependencies, deprecated services,
   security drift, undocumented tech debt) and produce a prioritized
   modernization roadmap with clear reasoning for each recommendation.
   ```
5. Leave action groups EMPTY for now — just get the agent creating and responding to a plain test message in the console test window. Confirm this works before moving on.
6. **Deliverable checkpoint:** screenshot or confirm — agent responds to a manual test prompt in the Bedrock console.

### Step 5 — Lambda Function Skeleton (the "action group" backend)
1. Create a Lambda function named `lsd-scanner-invoker`, runtime Python 3.12
2. Attach the `lsd-lambda-role` from Step 3
3. This Lambda will just be a **pass-through skeleton** for now — it receives an event, returns a hardcoded JSON response shaped like:
   ```json
   {
     "findings": [
       {"type": "outdated_dependency", "detail": "example", "severity": "high"}
     ]
   }
   ```
4. Deploy it. Test it manually in the Lambda console with a test event — confirm it returns the JSON above.
5. **Do not build real scanning logic here** — that's the build-part person's job. You're building the empty pipe first so it can be wired up fast later.

### Step 6 — Connect Lambda as Bedrock Agent Action Group
1. Back in Bedrock Agent console → Action groups → Add
2. Name: `scan-legacy-system`
3. Point it at the `lsd-scanner-invoker` Lambda from Step 5
4. Define the action group schema (OpenAPI-style) — minimal version:
   ```json
   {
     "openapi": "3.0.0",
     "info": {"title": "Legacy Scanner", "version": "1.0.0"},
     "paths": {
       "/scan": {
         "post": {
           "description": "Scans a target repo/system for legacy risk",
           "operationId": "scanSystem",
           "requestBody": {
             "content": {
               "application/json": {
                 "schema": {
                   "type": "object",
                   "properties": {"target": {"type": "string"}}
                 }
               }
             }
           },
           "responses": {
             "200": {"description": "Scan findings returned"}
           }
         }
       }
     }
   }
   ```
5. Save, prepare the agent (Bedrock has a "Prepare" step that must be run after every change)
6. Test in console: ask the agent to "scan the target system" — confirm it calls the Lambda and gets the hardcoded JSON back

### Step 7 — Handoff Point
Once Step 6 works end-to-end (agent → Lambda → hardcoded response → agent reasons over it), **you are done with the cloud plumbing**. Message the build-part person with:
- Agent ID and Agent Alias ID
- Lambda function ARN
- Confirmation that the round-trip works

### Step 8 — Deployment for Demo Day
1. Make sure the agent alias is set to a stable version (not just DRAFT) before demo time
2. Have the Bedrock console test window ready as a fallback if the UI has issues live
3. Keep the billing dashboard open during the demo prep window to watch spend

**AWS Part — do NOT touch:** scanner logic, UI, prompt engineering for reasoning quality, demo script. That's all Part 2.

---

## PART 2: BUILD (Your part)

**Goal:** Everything that makes the agent actually smart and the demo actually work.

### A. Diagnostic Scanner Logic
- Build rule-based (NOT ML) scanners that detect legacy risk in a sample repo:
  - Outdated dependencies (check `package.json` / `requirements.txt` versions against a known "old" threshold)
  - Deprecated AWS SDK calls or services referenced in code
  - Missing documentation / README staleness heuristics
  - Hardcoded secrets or config (simple regex pass)
- Output format MUST match what the Lambda skeleton expects (see Part 1, Step 5's JSON shape) so it drops in cleanly

### B. Replace the Lambda Skeleton's Hardcoded Response
- Once the AWS agent round-trip works (Part 1, Step 7 handoff), swap the hardcoded JSON in `lsd-scanner-invoker` for your real scanner output
- You'll need Lambda deploy access at that point — coordinate the handoff directly

### C. Prompt / Reasoning Quality
- Refine the agent's system instructions (from Part 1 Step 4) so the roadmap output is prioritized, specific, and TCS-relevant in tone
- Test with multiple seeded "legacy" repos to make sure reasoning holds up, not just on one lucky example

### D. Sample "Legacy" Demo Repo
- Seed a small repo with deliberately outdated deps, a deprecated AWS call, no docs — this is what gets scanned live in the demo

### E. UI
- Simple Streamlit or lightweight web front end
- Shows: input (target repo), scan findings, agent's reasoning trace, final prioritized roadmap
- Doesn't need to be fancy — needs to make the agent's reasoning visible, since that's the actual "wow" factor

### F. Demo Script + Deck
- Map findings directly to TCS's real legacy modernization business line
- Rehearse the live demo path end-to-end at least twice before presenting

---

## Critical Dependency
Part 2's item **B** (swapping Lambda's hardcoded response for real logic) cannot start until Part 1's **Step 7 handoff** is complete. Everything else in Part 2 (A, C, D, E, F) can run in parallel with Part 1 from hour zero.
