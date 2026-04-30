---
name: nano-council
description: Use when the user invokes /council, says council this, pressure-test this, asks to consult a council or conselho, wants divergent decision review, planning pressure tests, option comparison, or blind-spot analysis.
user-invocable: true
metadata:
  slash-command: /council
  output: telegram-markdown
---

# Nano Council

Use this skill to run a compact advisory council before giving a final answer. It is best for strategic decisions, implementation plans, product choices, architecture tradeoffs, and any request where the user wants disagreement instead of a single agreeable answer.

## Managed Auto Update

If this skill is installed as a managed Awesome NanoClaw Skill and `../awesome-updater/scripts/awesome_skills.py` exists, run this before the normal workflow:

```bash
python3 ../awesome-updater/scripts/awesome_skills.py check awesome-updater --skills-dir .. || true
python3 ../awesome-updater/scripts/awesome_skills.py discover --skills-dir .. || true
python3 ../awesome-updater/scripts/awesome_skills.py check nano-council --skills-dir .. || true
```

Continue the normal workflow if the update or discover check fails because of network, GitHub, or local environment issues.

The council answer is the answer. Do not give a solo answer first and then append a council-themed note.

## Load References

- Read `references/council-agents.md` before spawning the five advisors.
- Read `references/identity-shuffle.md` before peer review.
- Read `references/challenge-round.md` before asking advisors to review anonymized answers.
- Read `references/synthesis-chair.md` before writing the final synthesis.
- Use `assets/templates/telegram-summary.md` for user-facing output.
- Use `assets/templates/full-transcript.md` when saving the complete run.

## Triggers

Run the council when the user uses:

- `/council <question>`
- `council this`
- `pressure-test this`
- `convoque o conselho`
- `testa essa decisao`
- `quero opinioes divergentes`

If the user asks a normal coding or factual question without a council trigger, do not run this skill.

If the trigger says `this` or `essa decisao`, use the immediately preceding user content as the question. If there is no recoverable target, ask one short clarification instead of inventing the question.

## Language

Answer in the dominant language of the user's input. If the input is Portuguese, all advisor outputs, peer reviews, and the chairman synthesis should be in Portuguese. Preserve technical terms in English when that is clearer.

For mixed Portuguese/English input, default to Portuguese when the surrounding prose is Portuguese. Use Brazilian Portuguese unless the user clearly uses another variant.

## Help Mode

If the user invokes `/council help`, `/council ajuda`, `/council examples`, `/council exemplos`, or asks how to use this skill, explain usage instead of running the council.

The help response should include:

- what Nano Council does;
- when to use it;
- when not to use it;
- command forms: `/council <question>` and `/nanoskills help council`;
- what input the user should provide;
- what output the user gets;
- curated examples;
- contextual examples when the visible conversation gives enough concrete context.

Curated examples:

- `/council Should we ship the first version this week or wait until onboarding is better?`
- `/council Quero decidir se faco launch agora ou espero melhorar onboarding.`
- `/council Pressure-test this architecture before we build it.`

## Protocol

1. Restate the user question neutrally in one paragraph.
2. Capture only the context needed to answer. For code work, prefer local files and tests over broad speculation.
3. Use NanoClaw's `Agent` tool to spawn five independent advisors with the same neutral brief:
   - Red Team
   - Axiom
   - Horizon
   - Streetlight
   - Operator
4. Each advisor answers independently in 150-300 words. Do not show peer responses during this round. If `Agent` is unavailable, do not simulate independent advisors; state that the council requires `Agent` and ask whether to continue with a normal solo analysis.
5. Anonymize and shuffle the five answers as Response A-E.
6. Run anonymous peer review with the `Agent` tool. Default to five neutral reviewers. Each reviewer ranks and critiques the anonymized responses without knowing author identities. If tool limits force fewer reviewers, use at least three and state the reduced review count in the transcript.
7. As chairman, synthesize the final answer:
   - where the council agrees
   - where it disagrees
   - blind spots
   - recommended decision
   - first practical action
8. Send the final result directly in Telegram-friendly Markdown. Do not require a browser or local HTML launch.
9. If filesystem access is available, save artifacts under `/workspace/group/council/<timestamp>/`. If that path is unavailable, use the workspace-local `council/<timestamp>/` fallback and state the saved path.

## Transcript Artifacts

Use timestamp format `YYYYMMDD-HHMMSS` in the active timezone.

Save:

- `full-transcript.md`: complete run using `assets/templates/full-transcript.md`
- `telegram-summary.md`: final user-facing answer using `assets/templates/telegram-summary.md`

The complete transcript must include the original question, neutral brief, context used, named advisor responses, identity map, anonymized responses, peer reviews, and chairman synthesis. Do not save anything to long-term memory unless the user explicitly asks.

## Output Rules

- Put the chairman recommendation at the top.
- Keep Telegram output scannable: short sections, no huge tables.
- Do not expose hidden chain-of-thought. Summarize reasoning, evidence, assumptions, and tradeoffs.
- Do not overstate consensus. If the advisors disagree, preserve the disagreement.
- For implementation tasks, end with concrete next steps rather than abstract advice.
