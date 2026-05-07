# XRay Sample Runs

Use these examples for help mode, documentation, and validation.

## Help Mode

User:

```text
/xray help
```

Expected response shape:

```text
XRay turns content into a visual explanation.

Use it when you want to see structure, intent, assumptions, and practical meaning.

Commands:

/xray <content>
/xray short <content>
/xray long <content>
/visual-explain <content>

Examples:

/xray short Paste this contract and show the structure.
/xray long Explain this onboarding prompt.
/xray https://example.com/spec
```

## Short Mode

User:

```text
/xray short

The plan relaxes some pre-MVP technical debt, keeps YAML parsing and thesis-flow tests as high-priority, and reframes engineering score as learning-speed risk.
```

Expected behavior:

```text
## Mental map of the content

[Complete tree map, not shortened]

## Core idea

[2-5 lines]

## Main points

1. [Point]
2. [Point]
3. [Point]

## Ultra-short version

In one sentence:
[Sentence]

In 3 bullets:
-> [Point]
-> [Point]
-> [Point]
```

Validation point: the mental map remains complete even though the rest is short.

## Long Mode

User:

```text
/xray long

[Operating contract with roles, authorization gates, read-first files, and confirmation gate]
```

Expected behavior:

```text
## Mental map of the document

[Complete tree map, not shortened]

## Core idea

[Plain explanation]

## Visual concept map

[Flow diagram]

## Explanation by parts

[Breakdown by role, boundaries, workflow, and gates]

## Descriptive boxes

[Only boxes that clarify key rules]

## What people often misunderstand

Common mistake:
[Wrong reading]

Better reading:
[Better reading]

## Important insights

[Non-obvious insights]

## Ultra-short version

[One sentence and 3 bullets]

## My read

[Judgment only if useful]
```

Validation point: long mode adds interpretation layers, not filler.

## Default Mode

User:

```text
/xray https://example.com/spec
```

Expected behavior:

```text
## Mental map of the document

[Complete source structure]

## Core idea

[Core idea]

## Visual concept map

[Compact concept flow]

## Explanation by parts

[Only the parts needed to understand the spec]

## Important insights

[Useful implications]

## Ultra-short version

[Compact close]
```

Validation point: default mode chooses the smallest output that still explains the structure.
