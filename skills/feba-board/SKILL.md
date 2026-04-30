---
name: feba-board
description: Use when the user invokes /board or /feba-board, uses the legacy /council alias, asks for a board, second opinion, advice, decision review, tradeoff analysis, planning pressure test, or strong natural-language help deciding something. FEBA Board gives five VC-style perspectives for important decisions and returns a compact chat-friendly recommendation with expansion and transcript saving only when requested.
user-invocable: true
metadata:
  slash-command: /board
  output: chat-friendly-board-review
  catalog:
    group: user-facing
    order: 10
    aliases:
      - board
      - feba-board
      - /board
      - /feba-board
      - /council
      - second opinion
      - conselho
      - me ajuda a decidir
      - pressure-test
    use_when: The user has a meaningful decision, plan, tradeoff, investment question, product question, or asks for a second opinion from a board.
    expected_output: Compact chat-friendly recommendation with board tensions, next action, optional advisor expansion, and transcript saving only on request.
    examples:
      - /board Should we ship this week or wait until onboarding is better?
      - /board Quero decidir se faco launch agora ou espero melhorar onboarding.
      - me ajuda a decidir se devo aceitar esse cliente grande
    readme_include: true
    readme_description: Five VC perspectives for important decisions, plans, and tradeoffs.
---

# FEBA Board

Use this skill to pressure-test an important decision with five VC-style advisor perspectives and one practical recommendation.

The default UX is natural-language-first and chat-friendly. Be brief by default, expand only when the user asks, and save transcripts only when explicitly requested.

## Managed Auto Update

If this skill is installed as a managed Awesome NanoClaw Skill and `../awesome-updater/scripts/awesome_skills.py` exists, run this before the normal workflow:

```bash
python3 ../awesome-updater/scripts/awesome_skills.py check awesome-updater --skills-dir .. || true
python3 ../awesome-updater/scripts/awesome_skills.py discover --skills-dir .. || true
python3 ../awesome-updater/scripts/awesome_skills.py check feba-board --skills-dir .. || true
```

Continue the board workflow if update checks fail because of network, GitHub, or local environment issues.

## Load References

- Read `references/board-agents.md` before producing board perspectives.
- Use `references/challenge-round.md` when multiagent or swarm execution is available.
- Use `references/identity-shuffle.md` only when anonymized peer critique is useful and available.
- Use `references/synthesis-chair.md` for the final synthesis style.
- Use `assets/templates/chat-summary.md` for the default user-facing answer.
- Use `assets/templates/full-transcript.md` only when the user explicitly asks to save or export a transcript.

## Triggers

Run this skill when the user invokes or strongly implies:

- `/board <question>`
- `/feba-board <question>`
- `/council <question>` as a legacy alias
- "board this"
- "me ajuda a decidir"
- "quero uma segunda opiniao"
- "me da conselhos"
- "pressure-test this"
- "qual plano voce recomenda?"
- "devo fazer X ou Y?"
- a meaningful decision, tradeoff, investment/product call, hiring call, launch call, pricing call, partnership call, or execution plan review

Do not run this skill for simple factual questions, routine coding tasks, or cases where the user is clearly asking for direct implementation rather than decision review.

## Help Mode

If the user invokes `/board help`, `/board ajuda`, `/board examples`, `/board exemplos`, `/feba-board help`, or the legacy `/council help`, explain usage instead of running the board.

The help response should include:

- what FEBA Board does;
- when to use it;
- command forms: `/board <question>`, `/feba-board <question>`, and legacy `/council <question>`;
- that natural language also works for strong decision-review intent;
- that the default answer is short;
- that the user can ask to expand one advisor, compare options, or save the transcript.
- curated examples;
- contextual examples when the visible conversation includes a current decision, plan, tradeoff, investment question, or product question.

Curated examples:

- `/board Should we ship this week or wait until onboarding is better?`
- `/board Quero decidir se faco launch agora ou espero melhorar onboarding.`
- `/board Pressure-test this acquisition thesis before we send the memo.`

## Language

Answer in the dominant language of the current conversation. If the conversation is mixed, follow the user's latest message. For Portuguese, use natural Brazilian Portuguese unless the user clearly uses another variant.

Do not translate slash commands, skill names, file paths, or advisor names.

## Runtime Mode

Prefer real multiagent or swarm execution when the runtime exposes a safe way to run independent advisors. If that is available:

1. run each advisor independently using `references/board-agents.md`;
2. optionally run the challenge round from `references/challenge-round.md`;
3. synthesize the final recommendation.

If multiagent execution is not available, run a solo board simulation using the same advisor prompts. Briefly state that the board is running in solo mode, then continue. Do not block the user just because multiagent tooling is unavailable.

## Board Protocol

1. Restate the decision in one compact sentence.
2. If the decision is under-specified, ask at most one clarifying question only when the missing information materially changes the recommendation. Otherwise proceed with explicit assumptions.
3. Produce five independent perspectives:
   - The Skeptic
   - The Thesis
   - The Market
   - The Customer
   - The Operator
4. Identify the real tension between the advisors, not five parallel summaries.
5. Give one recommendation, one reason, one risk to watch, and one next action.
6. Keep the default response concise enough for WhatsApp Business or Telegram.
7. Offer expansion choices only after the answer: expand an advisor, compare options, turn into a plan, or save transcript.

## Output Shape

Default response:

```md
**FEBA Board**
Decision: <one sentence>

Recommendation: <clear recommendation>

Board view:
- The Skeptic: <short point>
- The Thesis: <short point>
- The Market: <short point>
- The Customer: <short point>
- The Operator: <short point>

Tension: <where the disagreement matters>
Next action: <one concrete step>

Reply with `expand <advisor>`, `compare options`, `make a plan`, or `save transcript`.
```

Avoid long essays by default. If the user asks for depth, expand the requested advisor or produce the full board transcript.

## Transcript Saving

Do not save artifacts by default.

Save only when the user explicitly asks for phrases such as "save transcript", "export", "salva", "guardar", or "gera arquivo".

When saving, write artifacts under `/workspace/group/board/<timestamp>/` when that path exists. If it is unavailable, use the workspace-local `board/<timestamp>/` fallback and state the saved path.

Expected artifacts when saving:

- `chat-summary.md`: final user-facing answer using `assets/templates/chat-summary.md`
- `full-transcript.md`: decision brief, advisor outputs, optional challenge round, synthesis, assumptions, and next actions

Never save secrets, credentials, private URLs, or sensitive pasted content unless the user explicitly confirms that the transcript should include them.
