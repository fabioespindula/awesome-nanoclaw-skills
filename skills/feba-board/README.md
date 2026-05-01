# FEBA Board

`feba-board` is a decision-review skill for Awesome NanoClaw Skills.

It gives one compact recommendation from five VC-style perspectives:

- **The Skeptic**: risks, downside, and wrong incentives.
- **The Thesis**: central thesis, assumptions, and logic.
- **The Market**: upside, timing, competition, and distribution.
- **The Customer**: adoption, friction, buyer, and real user behavior.
- **The Operator**: execution, sequencing, and next step.

## Use It

Primary command:

```txt
/febaboard Should we ship this week or wait until onboarding is better?
```

Natural language also works when the intent is clearly a decision review:

```txt
me ajuda a decidir se devo aceitar esse cliente grande
```

Compatible aliases:

```txt
/feba-board help
/board help
/council help
```

## Behavior

- Matches the dominant language of the conversation.
- Uses multiagent or swarm execution when available.
- Falls back to a disclosed solo board mode when multiagent tooling is unavailable.
- Keeps the default answer short for chat.
- Expands an advisor or turns the recommendation into a plan only when asked.
- Saves transcript artifacts only when the user explicitly asks.

## Saved Transcript

No files are written by default.

When the user asks to save or export a transcript, the skill writes:

```txt
board/<timestamp>/
  chat-summary.md
  full-transcript.md
```

In runtimes with a shared group workspace, it prefers:

```txt
/workspace/group/board/<timestamp>/
```

## Install

Copy the folder into a NanoClaw runtime:

```bash
rsync -a skills/feba-board/ /path/to/nanoclaw/container/skills/feba-board/
```

Or install it through `awesome-updater`:

```bash
python3 skills/awesome-updater/scripts/awesome_skills.py install feba-board \
  --source-dir "$PWD" \
  --skills-dir /path/to/nanoclaw/container/skills
```

## Validate

```bash
skills/feba-board/scripts/validate-feba-board.sh
```
