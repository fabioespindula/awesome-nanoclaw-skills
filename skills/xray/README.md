# XRay

`xray` turns prompts, articles, specs, docs, websites, transcripts, PDFs, code, and complex ideas into visual explanations.

It is not a normal summary skill. It reveals structure, intent, assumptions, dependencies, and practical meaning. The complete mental map is the core output in every mode.

## Use It

Primary command:

```txt
/xray <content>
```

Depth modes:

```txt
/xray short <content>
/xray long <content>
```

Aliases:

```txt
/visual-explain
```

Examples:

```txt
/xray short Paste this contract and show the structure.
/xray long Explain this onboarding prompt.
/xray https://example.com/spec
```

## Behavior

- Always starts with a complete mental map.
- `short` reduces follow-up sections, not the mental map.
- `long` adds interpretation layers, not verbosity.
- Detects whether the input is a prompt, site, doc, spec, code, transcript, PDF excerpt, article, or mixed content.
- Treats source content as untrusted data and does not execute instructions found inside it.
- Answers in the requested language, or the dominant source language when none is specified.

## Output

The default output is a visual explanation with:

- complete mental map
- core idea
- compact visual concept flow
- explanation by parts
- important insights
- ultra-short version

`long` may also include descriptive boxes, examples, analogies, misunderstanding checks, failure modes, and a final read when useful.

## Requirements

NanoClaw runtime with this skill installed. Browser, file, or PDF tools are useful only when the requested source requires them.

## Install

```bash
rsync -a skills/xray/ /path/to/nanoclaw/container/skills/xray/
```

Or install it through `awesome-updater`:

```bash
python3 skills/awesome-updater/scripts/awesome_skills.py install xray \
  --source-dir "$PWD" \
  --skills-dir /path/to/nanoclaw/container/skills
```

## Validate

```bash
skills/xray/scripts/validate-xray.sh
```
