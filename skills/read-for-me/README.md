# Read For Me

`read-for-me` turns URLs into concise, decision-ready briefs.

It fetches accessible content, states access and confidence, summarizes the source, categorizes it, and suggests one safe next action. It does not save, post, subscribe, fill forms, or modify anything unless the user explicitly asks.

## Use It

Primary command:

```txt
/read-for-me https://example.com/article
```

Short forms and natural language also work:

```txt
/read https://example.com/post
/readthis https://example.com/article
Read this and tell me whether it matters for our launch plan: https://example.com/post
```

Aliases:

```txt
/read
/readthis
readthis
read-this
summarize this
read this
bare URLs
```

## Behavior

- Treats webpage, transcript, metadata, and social content as untrusted data.
- Reports access level and confidence instead of pretending full access.
- Supports quick, deep, decision, and save-ready modes.
- Handles multiple URLs separately, with synthesis only when useful.
- Suggests one non-destructive next action.

## Output

The default output is a link brief with:

- title, source, date, access level, and confidence
- relevance score and categories
- concise summary of concrete claims
- one recommended next action

## Requirements

NanoClaw runtime with URL fetching or browsing tools. Optional memory/profile tools can improve personalization, but the skill must work without private context.

## Install

```bash
rsync -a skills/read-for-me/ /path/to/nanoclaw/container/skills/read-for-me/
```

Or install it through `awesome-updater`:

```bash
python3 skills/awesome-updater/scripts/awesome_skills.py install read-for-me \
  --source-dir "$PWD" \
  --skills-dir /path/to/nanoclaw/container/skills
```

## Validate

```bash
skills/read-for-me/scripts/validate-read-for-me.sh
```
