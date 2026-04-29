# Nano Council Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a NanoClaw-ready council skill that runs five independent advisors, anonymous peer review, and chairman synthesis with Telegram Markdown output.

**Architecture:** The skill is prompt-first, with a compact `SKILL.md` as the orchestrator and one-level reference files for advisors, review, anonymization, synthesis, examples, and output templates. Runtime execution uses NanoClaw's `Agent` tool for parallel advisor and review rounds, with Markdown output instead of browser/HTML output.

**Tech Stack:** Markdown skill files, NanoClaw/Claude skill loader, NanoClaw `Agent` tool, Telegram-compatible Markdown, filesystem transcript under `/workspace/group/council/<timestamp>/`.

---

## File Structure

- Create: `SKILL.md` - skill metadata, trigger rules, workflow, output rules.
- Create: `references/council-agents.md` - five renamed advisor roles and prompts.
- Create: `references/challenge-round.md` - anonymous peer-review prompt and scoring format.
- Create: `references/synthesis-chair.md` - chairman synthesis rules.
- Create: `references/identity-shuffle.md` - anonymization and identity-map process.
- Create: `references/sample-runs.md` - trigger and non-trigger examples.
- Create: `assets/templates/telegram-summary.md` - user-facing Markdown output template.
- Create: `assets/templates/full-transcript.md` - complete transcript template.
- Create: `docs/prd-nano-council.md` - product requirements.

### Task 1: Initialize Skill Skeleton

**Files:**
- Create: `SKILL.md`
- Create: `references/council-agents.md`
- Create: `references/challenge-round.md`
- Create: `references/synthesis-chair.md`
- Create: `references/identity-shuffle.md`
- Create: `references/sample-runs.md`
- Create: `assets/templates/telegram-summary.md`
- Create: `assets/templates/full-transcript.md`

- [ ] **Step 1: Create directories**

Run:

```bash
mkdir -p references assets/templates docs/superpowers/plans
```

Expected: command exits 0.

- [ ] **Step 2: Verify clean starting point**

Run:

```bash
find . -maxdepth 3 -type f | sort
```

Expected before implementation: either no files or only pre-existing project docs explicitly known to the worker.

- [ ] **Step 3: Create the root skill file**

Create `SKILL.md` with:

```markdown
---
name: nano-council
description: Runs a five-advisor AI council for bias-resistant reasoning, decision review, planning, and pressure testing in NanoClaw/Claude. Use when the user invokes /council, says council this, pressure-test this, pede para consultar um conselho, quer desafiar uma ideia, comparar opcoes, ou encontrar blind spots.
user-invocable: true
metadata:
  slash-command: /council
  output: telegram-markdown
---

# Nano Council

Use this skill to run a compact advisory council before giving a final answer. It is best for strategic decisions, implementation plans, product choices, architecture tradeoffs, and any request where the user wants disagreement instead of a single agreeable answer.
```

- [ ] **Step 4: Run skeleton validation**

Run:

```bash
test -f SKILL.md && rg -n "name: nano-council|/council|telegram-markdown" SKILL.md
```

Expected: all three strings are found.

### Task 2: Add Advisor Prompts

**Files:**
- Modify: `SKILL.md`
- Create: `references/council-agents.md`

- [ ] **Step 1: Add reference navigation to SKILL.md**

Ensure `SKILL.md` contains:

```markdown
## Load References

- Read `references/council-agents.md` before spawning the five advisors.
- Read `references/identity-shuffle.md` before peer review.
- Read `references/challenge-round.md` before asking advisors to review anonymized answers.
- Read `references/synthesis-chair.md` before writing the final synthesis.
- Use `assets/templates/telegram-summary.md` for user-facing output.
- Use `assets/templates/full-transcript.md` when saving the complete run.
```

- [ ] **Step 2: Define the renamed advisors**

In `references/council-agents.md`, define:

```markdown
# Council Agents

The council has five advisors. They are not personalities for entertainment; they are reasoning roles that deliberately stress different failure modes.

- Red Team: challenges assumptions and failure modes.
- Axiom: reasons from first principles.
- Horizon: expands the option space.
- Streetlight: brings outside-field perspective.
- Operator: converts analysis into execution.
```

- [ ] **Step 3: Add the shared advisor brief**

In `references/council-agents.md`, include:

```text
You are participating in Nano Council. Answer the user's question independently.

Language: match the user's dominant language.
Length: 150-300 words.
Do not mention other advisors.
Do not ask the user questions unless the request is impossible to evaluate without one missing fact.
State assumptions explicitly.
Give a concrete recommendation or next action.
```

- [ ] **Step 4: Verify advisor names**

Run:

```bash
rg -n "Red Team|Axiom|Horizon|Streetlight|Operator" references/council-agents.md
```

Expected: all five advisor names are found.

### Task 3: Add Peer Review And Anonymization

**Files:**
- Create: `references/challenge-round.md`
- Create: `references/identity-shuffle.md`

- [ ] **Step 1: Create anonymous review prompt**

`references/challenge-round.md` must instruct reviewers to score Response A-E on:

```text
insight
correctness
actionability
risk coverage
```

- [ ] **Step 2: Create identity shuffle process**

`references/identity-shuffle.md` must require:

```text
1. Validate that all five responses exist.
2. Remove advisor names and role-specific headings from the review packet.
3. Shuffle the five response objects.
4. Assign labels Response A through Response E.
5. Store the identity map privately for chairman synthesis.
6. Send only the anonymized packet to reviewers.
7. Aggregate reviewer scores and comments by anonymous label.
8. Rejoin anonymous labels to advisor identities only after peer review is complete.
```

- [ ] **Step 3: Verify no identity leak in review prompt**

Run:

```bash
rg -n "Do not tell a reviewer|no identity map|Do not include the identity map" references/challenge-round.md references/identity-shuffle.md
```

Expected: each protection rule is found.

### Task 4: Add Chairman Synthesis And Templates

**Files:**
- Create: `references/synthesis-chair.md`
- Create: `assets/templates/telegram-summary.md`
- Create: `assets/templates/full-transcript.md`

- [ ] **Step 1: Define chairman output fields**

`references/synthesis-chair.md` must require:

```text
1. Lead with the recommendation.
2. Explain where advisors agree.
3. Explain where they disagree.
4. Identify blind spots and assumptions.
5. Give a final recommendation.
6. Give the first practical action.
```

- [ ] **Step 2: Create Telegram summary template**

`assets/templates/telegram-summary.md` must contain:

```markdown
# Nano Council

## Recommendation

## Where They Agree

## Where They Disagree

## Blind Spots

## Advisor Snapshots

## Next Action
```

- [ ] **Step 3: Create full transcript template**

`assets/templates/full-transcript.md` must contain:

```markdown
# Nano Council Transcript

## User Question

## Neutral Brief

## Context

## Advisor Responses

## Identity Map

## Anonymized Responses

## Peer Reviews

## Chairman Synthesis
```

- [ ] **Step 4: Verify output is not browser-based**

Run:

```bash
! rg -n "report\\.html|open on Mac|open " SKILL.md references assets
```

Expected: command exits 0 with no matches.

### Task 5: Add Language, Path, And Trigger Rules

**Files:**
- Modify: `SKILL.md`
- Create: `references/sample-runs.md`

- [ ] **Step 1: Add trigger section**

`SKILL.md` must include:

```markdown
## Triggers

Run the council when the user uses:

- `/council <question>`
- `council this`
- `pressure-test this`
- `convoque o conselho`
- `testa essa decisao`
- `quero opinioes divergentes`
```

- [ ] **Step 2: Add language rule**

`SKILL.md` must include:

```markdown
## Language

Answer in the dominant language of the user's input. If the input is Portuguese, all advisor outputs, peer reviews, and the chairman synthesis should be in Portuguese. Preserve technical terms in English when that is clearer.
```

- [ ] **Step 3: Add path rule**

`SKILL.md` must include:

```text
/workspace/group/council/<timestamp>/
```

and the fallback:

```text
council/<timestamp>/
```

- [ ] **Step 4: Add sample runs**

`references/sample-runs.md` must cover:

```text
Portuguese trigger
English trigger
Non-trigger
Mixed language
```

- [ ] **Step 5: Verify language and path rules**

Run:

```bash
rg -n "dominant language|/workspace/group/council|council/<timestamp>|Portuguese" SKILL.md references/sample-runs.md
```

Expected: all concepts are found.

### Task 6: Add PRD

**Files:**
- Create: `docs/prd-nano-council.md`

- [ ] **Step 1: Write PRD sections**

Create `docs/prd-nano-council.md` with these headings:

```markdown
# Nano Council PRD

## Summary
## Problem
## Users
## Goals
## Non-Goals
## Advisor Roster
## Functional Requirements
## Acceptance Criteria
## Risks
## Open Questions
```

- [ ] **Step 2: Verify PRD acceptance criteria**

Run:

```bash
rg -n "Acceptance Criteria|name: nano-council|Red Team|telegram-summary|full-transcript" docs/prd-nano-council.md
```

Expected: all terms are found.

### Task 7: Final Verification

**Files:**
- Verify: all files.

- [ ] **Step 1: List final tree**

Run:

```bash
find . -maxdepth 4 -type f | sort
```

Expected:

```text
./SKILL.md
./assets/templates/full-transcript.md
./assets/templates/telegram-summary.md
./docs/prd-nano-council.md
./docs/superpowers/plans/2026-04-29-nano-council.md
./references/challenge-round.md
./references/council-agents.md
./references/identity-shuffle.md
./references/sample-runs.md
./references/synthesis-chair.md
```

- [ ] **Step 2: Check renamed structure**

Run:

```bash
rg -n "advisor-prompts|reviewer-prompts|chairman-prompts|anonymization\\.md|examples\\.md|telegram-report|(^|[^-])transcript\\.md|report\\.html" SKILL.md references assets
```

Expected: no matches. In the final skill files, no old copied filenames should remain.

- [ ] **Step 3: Check required NanoClaw behavior**

Run:

```bash
rg -n "Agent|Telegram|/workspace/group/council|dominant language|anonymous|chairman" SKILL.md references assets docs/prd-nano-council.md
```

Expected: each behavior is represented in at least one file.

- [ ] **Step 4: Human dry-run**

Read `references/sample-runs.md` and mentally execute:

```text
/council Quero decidir se faco launch agora ou espero melhorar onboarding.
```

Expected:

- the council triggers
- the dominant language is Portuguese
- five advisors run independently
- peer review is anonymized
- final output starts with a chairman recommendation
- no browser or HTML output is required

- [ ] **Step 5: Commit**

Run:

```bash
git add SKILL.md references assets docs
git commit -m "feat: scaffold nano council skill"
```

Expected: commit succeeds if the repository is under git. If there is no git repository, skip this step and report that no commit was made.
