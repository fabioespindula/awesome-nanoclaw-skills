# FEBA Board PRD

## Summary

FEBA Board is a NanoClaw skill for high-signal decision review. It gives the user five VC-style perspectives, a compact recommendation, and optional expansion without turning every decision into a long report.

The skill name is `feba-board`. The primary command is `/board`. The legacy `/council` alias remains supported only for compatibility.

## Goals

1. Make decision review feel natural in chat, WhatsApp Business, and Telegram.
2. Support both slash commands and strong natural-language decision intent.
3. Return a short recommendation by default.
4. Use real multiagent or swarm execution when available.
5. Fall back to a transparent solo board mode when multiagent execution is unavailable.
6. Save transcripts only when the user explicitly asks.
7. Keep the roster stable and memorable.

## Non-Goals

- Replacing full investment memos.
- Running broad research without explicit request or current-source need.
- Saving artifacts by default.
- Forcing a multiagent dependency in runtimes that do not expose one.
- Expanding every advisor response unless the user asks.

## User Triggers

- `/board <question>`
- `/feba-board <question>`
- `/council <question>` as a legacy alias
- "me ajuda a decidir"
- "quero uma segunda opiniao"
- "pressure-test this"
- "devo fazer X ou Y?"
- strong decision, tradeoff, plan, investment, launch, pricing, hiring, partnership, or execution-review intent

## Roster

- **The Skeptic**: risks, downside, and wrong incentives.
- **The Thesis**: central thesis, assumptions, and logic.
- **The Market**: upside, timing, competition, and distribution.
- **The Customer**: adoption, friction, buyer, and real user behavior.
- **The Operator**: execution, sequencing, and next step.

## Runtime Behavior

1. Detect decision-review intent.
2. Match the user's dominant language.
3. Ask at most one clarifying question only when necessary.
4. Try multiagent or swarm execution when safely available.
5. Use solo board mode when multiagent execution is unavailable and state that briefly.
6. Produce five advisor views and one synthesis.
7. Keep the default answer compact.
8. Offer expansion options.
9. Save transcript only after an explicit user request.

## Default Output

The default response includes:

- decision restatement;
- recommendation;
- one short line per advisor;
- the key tension;
- one next action;
- optional expansion commands.

## Transcript Saving

No files are written by default.

When the user explicitly asks to save or export, write:

```txt
/workspace/group/board/<timestamp>/
  chat-summary.md
  full-transcript.md
```

If `/workspace/group/board/` is unavailable, use:

```txt
./board/<timestamp>/
  chat-summary.md
  full-transcript.md
```

## Acceptance Criteria

- `SKILL.md` declares `name: feba-board`.
- `SKILL.md` declares `slash-command: /board`.
- `/council` appears only as a documented legacy alias.
- The roster contains The Skeptic, The Thesis, The Market, The Customer, and The Operator.
- The default behavior is short, language-matched, and chat-friendly.
- Multiagent or swarm execution is preferred when available.
- Solo fallback is allowed and disclosed.
- Transcript artifacts are saved only on explicit request.
- README, catalog, updater examples, docs, templates, and validators reference FEBA Board.
- No old product or folder name remains in repository search results.
