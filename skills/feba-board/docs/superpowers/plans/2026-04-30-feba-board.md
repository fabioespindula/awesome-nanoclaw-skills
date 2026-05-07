# FEBA Board v2 Implementation Plan

## Summary

Rename and harden the decision-review skill as FEBA Board. The runtime folder is `skills/feba-board`, the primary command is `/febaboard`, `/feba-board` remains compatible, and `/council` remains only as a documented legacy alias.

## Desired Behavior

- Trigger from `/febaboard`, `/feba-board`, compatible `/board`, legacy `/council`, or strong natural-language decision-review intent.
- Match the dominant language of the conversation.
- Prefer multiagent or swarm execution when available.
- Fall back to disclosed solo board mode when multiagent execution is unavailable.
- Keep the default answer compact enough for chat.
- Expand only when the user asks.
- Save transcript only when the user explicitly requests it.

## Board Roster

- The Skeptic: risks, downside, and wrong incentives.
- The Thesis: central thesis, assumptions, and logic.
- The Market: upside, timing, competition, and distribution.
- The Customer: adoption, friction, buyer, and real user behavior.
- The Operator: execution, sequencing, and next step.

## Files

- `SKILL.md`: metadata, triggers, workflow, runtime behavior.
- `README.md`: skill-level documentation.
- `references/board-agents.md`: advisor roles and prompt guidance.
- `references/challenge-round.md`: optional multiagent critique pass.
- `references/identity-shuffle.md`: optional anonymized critique process.
- `references/synthesis-chair.md`: synthesis lead rules.
- `references/sample-runs.md`: examples.
- `assets/templates/chat-summary.md`: default user-facing answer shape.
- `assets/templates/full-transcript.md`: saved transcript shape.
- `docs/prd-feba-board.md`: product requirements.
- `scripts/validate-feba-board.sh`: static validation.

## Validation

Run:

```bash
skills/feba-board/scripts/validate-feba-board.sh
python3 skills/nanoskills/scripts/generate_catalog.py --check --repo-root . --skills-dir skills
old_slug="$(printf 'nano-\143\157\165\156\143\151\154')"
old_title="$(printf 'Nano \103\157\165\156\143\151\154')"
rg "$old_slug|$old_title"
```

Expected:

- FEBA Board validator passes.
- Catalog and README generated blocks are synchronized.
- The final old-name search returns zero matches.

## Manual Runbook

1. `/febaboard Should we ship this week or wait until onboarding is better?`
2. `help me decide whether to accept this large customer`
3. `/council help`
4. Ask to expand one advisor.
5. Ask to save transcript and verify only then that files are written.
