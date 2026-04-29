# Nano Council PRD

## Summary

Nano Council adapts the LLM Council idea into a NanoClaw/Claude skill that gives the user five deliberately different AI advisor perspectives, anonymous peer review, and one chairman synthesis delivered as Telegram-friendly Markdown.

The goal is not to copy the reference skill verbatim. The goal is to preserve the useful protocol while making the naming, paths, output format, and bilingual behavior native to NanoClaw.

## Problem

Single-agent answers can become too agreeable, especially when the user is evaluating a plan, decision, or implementation path. The skill should create structured disagreement without requiring the user to manually prompt five different perspectives.

## Users

- Fabio, using NanoClaw through Telegram or a similar chat surface.
- Future NanoClaw operators who need a reusable decision-review skill.

## Goals

1. Provide a `/council` workflow that spawns five independent advisors.
2. Use distinct advisor names and prompts so the skill does not look like a direct copy of the reference.
3. Preserve the seven-step council protocol: neutral brief, independent answers, anonymization, peer review, synthesis, output, transcript.
4. Deliver the final answer directly as Telegram-friendly Markdown.
5. Match the user's dominant language, including Portuguese.
6. Save full transcript files under `/workspace/group/council/<timestamp>/` when available.

## Non-Goals

- No browser dependency.
- No local HTML report as the primary output.
- No external API model orchestration in this version.
- No compiled code or package install requirement.
- No automatic long-term memory save.

## Advisor Roster

| Advisor | Purpose |
| --- | --- |
| Red Team | Challenges assumptions and failure modes. |
| Axiom | Reasons from first principles. |
| Horizon | Expands the option space. |
| Streetlight | Brings outside-field perspective. |
| Operator | Converts analysis into execution. |

## Functional Requirements

### FR1: Invocation

The skill must trigger on:

- `/council`
- `council this`
- `pressure-test this`
- `convoque o conselho`
- `testa essa decisao`
- equivalent user intent asking for divergent advisory review

### FR2: Advisor Round

The orchestrator must spawn five advisors independently using NanoClaw's `Agent` tool. Each advisor receives the same neutral brief and relevant context. Each response should be 150-300 words.

### FR3: Anonymous Peer Review

The orchestrator must remove advisor identities, shuffle responses, relabel them as Response A-E, and run anonymous peer review before final synthesis.

### FR4: Chairman Synthesis

The main session acts as chairman. It reads advisor responses and peer-review results, then produces:

- recommendation
- agreement
- disagreement
- blind spots
- advisor snapshots when useful
- next action

### FR5: Telegram Output

The user-facing output must be Markdown that works in a narrow chat interface. It must not rely on HTML, a browser, or Mac `open`.

### FR6: Transcript

When filesystem access exists, save a transcript to:

```text
/workspace/group/council/<timestamp>/
```

If that path does not exist, fall back to:

```text
./council/<timestamp>/
```

The transcript should include the original question, neutral brief, context, advisor responses, identity map, anonymized responses, peer reviews, and chairman synthesis.

### FR7: Language Matching

The skill must answer in the dominant language of the user's input. If the input is Portuguese, the entire workflow should produce Portuguese outputs while preserving technical English terms when useful.

## Acceptance Criteria

- `SKILL.md` exists and declares `name: nano-council`.
- The support files use renamed NanoClaw-specific filenames:
  - `references/council-agents.md`
  - `references/challenge-round.md`
  - `references/synthesis-chair.md`
  - `references/identity-shuffle.md`
  - `references/sample-runs.md`
  - `assets/templates/telegram-summary.md`
  - `assets/templates/full-transcript.md`
- `SKILL.md` references all support files by their new names.
- No file requires `report.html` or `open` as the primary output path.
- The advisor roster uses Red Team, Axiom, Horizon, Streetlight, and Operator.
- The output template starts with the chairman recommendation.
- The PRD and implementation plan are stored in `docs/`.

## Risks

- NanoClaw's exact skill metadata fields may differ from Claude Code's. Mitigation: keep frontmatter simple and treat extra fields as optional metadata.
- Telegram Markdown support may vary by bot implementation. Mitigation: avoid complex tables in user-facing output.
- Anonymous peer review can be weakened if advisor styles are too recognizable. Mitigation: remove names and role-specific headings before review.
- Transcript writing can fail if `/workspace/group` is unavailable. Mitigation: document and use a workspace-local fallback.

## Open Questions

1. Should NanoClaw expose `/council` through a separate slash-command registry file, or is `SKILL.md` metadata enough?
2. Should the transcript be sent back to the user as a file/link, or only saved silently?
3. Should peer review include all five reviewers, or a cheaper three-reviewer mode for low-stakes prompts?

