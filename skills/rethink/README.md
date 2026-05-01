# Rethink

`rethink` reframes a concrete plan, idea, or decision before the user commits to it.

It is not generic advice mode. It clarifies the real question, hidden assumptions, alternatives, risks, reversibility, timing, and the most defensible next move.

## Use It

Primary command:

```txt
/rethink Should I build the global skill catalog as a separate skill or inside the updater?
```

Other examples:

```txt
/rethink Esse plano de launch esta grande demais para a primeira versao?
/rethink Help me decide between hiring now or keeping the team small.
```

Aliases and trigger phrases:

```txt
rethink
step back
gut-check
pressure-test
simplify this
decide
```

## Behavior

- Works best on a concrete decision or commitment.
- Challenges assumptions without turning every answer into a debate.
- Compares real alternatives instead of only improving the current plan.
- Marks uncertainty clearly for personal, strategic, financial, legal, medical, or fast-moving topics.
- Does not execute side effects unless the user explicitly asks after the rethink.

## Output

The default output is a concise decision review with:

- the real question
- current frame and hidden assumptions
- practical alternatives
- failure and rescue map
- recommendation and next move

## Requirements

NanoClaw runtime. Browser or research tools are useful only when the decision depends on current facts.

## Install

```bash
rsync -a skills/rethink/ /path/to/nanoclaw/container/skills/rethink/
```

Or install it through `awesome-updater`:

```bash
python3 skills/awesome-updater/scripts/awesome_skills.py install rethink \
  --source-dir "$PWD" \
  --skills-dir /path/to/nanoclaw/container/skills
```

## Validate

```bash
skills/rethink/scripts/validate-rethink.sh
```
