# XRay Output Structure

Use this reference to produce XRay's visual explanation output.

## Mental Map First

Before explaining anything, generate a structured mental map of the source.

This is the most important section. It shows the anatomy of the content before the details.

The mental map is complete in every mode, including `short`.

## Section Title Rules

Use the most specific title:

```text
Mental map of the prompt
```

When the source is a prompt.

```text
Mental map of the document
```

When the source is a technical doc, contract, spec, PRD, report, or policy.

```text
Mental map of the article
```

When the source is an article, essay, post, or newsletter.

```text
Mental map of the content
```

When the type is unclear.

Use equivalent specific titles in the output language when the user explicitly asks for another language.

## Mental Map Format

Use a tree-style Markdown visual map.

Template:

```text
[Main topic]
|
|-- Context
|   |-- Prior point
|   |-- Decision already made
|   `-- Inherited problem
|
|-- Current problem
|   |-- Main pain
|   |-- Operational noise
|   `-- Risk if nothing changes
|
|-- Proposal
|   |-- New package / project / idea
|   `-- Main objective
|
|-- Scope
|   |-- Core items
|   `-- Additional items
|
|-- Out of scope
|   `-- What was explicitly excluded
|
|-- Rules
|   |-- Non-negotiables
|   |-- Technical constraints
|   `-- Operational decisions
|
|-- Acceptance
|   |-- Expected evidence
|   |-- Tests
|   `-- Closing criteria
|
`-- Next steps
    |-- What to document
    |-- What to report
    `-- Where to pause
```

Adapt the branches to the source. Do not force irrelevant branches, but preserve context, scope, rules, acceptance, risks, deferred items, and next steps when they exist.

## Mental Map Rules

- Preserve the hierarchy of the original content.
- Do not make this section too short.
- Do not flatten everything into generic bullets.
- Keep dependencies visible.
- Show context, scope, rules, acceptance, risks, deferred work, and next steps when present.
- If the content has phases, rounds, packages, or decisions, preserve them.
- If the source is messy, impose structure without inventing facts.
- If something is unclear, mark it clearly.

Example:

```text
`-- Ambiguous point
    `-- The content does not make clear whether this is required or optional
```

## Core Idea

After the mental map, explain the core idea in 2 to 5 short lines.

```text
The core idea is simple:

[Main idea in plain language]

In other words:

[Even simpler explanation]
```

## Visual Concept Map

Create a visual Markdown map showing the conceptual flow.

Simple format:

```text
[Original content]
        |
        v
[Core idea]
        |
        v
[How it works]
        |
        v
[Why it matters]
        |
        v
[Practical application]
```

Branching format:

```text
                    [Central theme]
                          |
                          v
        +-----------------+-----------------+
        |                 |                 |
        v                 v                 v
 [Concept A]       [Concept B]       [Concept C]
        |                 |                 |
        v                 v                 v
 [Impact]          [Example]         [Risk]
```

## Explanation By Parts

Break the content into clear blocks.

```text
## Part 1: [Part name]

What it means:
[Simple explanation]

Why it matters:
[Practical relevance]

Example:
[Concrete example]
```

Adapt section names to the output language.

## Descriptive Boxes

Use boxes only when they improve clarity.

```text
+----------------------------------------------+
| Main insight                                 |
+----------------------------------------------+
| The idea is not only [X].                    |
| The real idea is [Y].                        |
+----------------------------------------------+
```

```text
+----------------------------------------------+
| Common mistake                               |
+----------------------------------------------+
| The mistake is interpreting this as [X].     |
| The better reading is [Y].                   |
+----------------------------------------------+
```

## Analogies

Use analogies only when they make the content easier to understand.

Do not force analogies.

```text
Think of it as...

[Analogy]

In practice:

-> [Point 1]
-> [Point 2]
-> [Point 3]
```

## Practical Examples

Use practical examples when useful.

```text
### Simple example

Imagine that...
```

```text
### Technical example

In practice, this means that...
```

## Important Insights

Extract non-obvious insights.

```text
## Important insights

### Insight 1

[Insight]

### Insight 2

[Insight]

### Insight 3

[Insight]
```

Rules:

- Do not repeat the obvious summary.
- Focus on what is underneath the content.
- Explain tradeoffs.
- Explain why the content is structured this way.
- Explain hidden assumptions.
- Explain operational implications.

## What People Often Misunderstand

For prompts and specs, always include this section. For other content, include it when there is a real misunderstanding risk.

```text
## What people often misunderstand

Common mistake:

[Wrong interpretation]

Better reading:

[Better interpretation]
```

## Ultra-Short Version

End with a compact summary.

```text
## Ultra-short version

In one sentence:

[One sentence explanation]

In 3 bullets:

-> [Point 1]
-> [Point 2]
-> [Point 3]
```

## My Read

Use this only when the content benefits from judgment, strategic reading, or operator-level interpretation.

```text
## My read

[Direct strategic interpretation]

The main insight:

[Sharp takeaway]
```

## Mode Recipes

### Short

Use:

```text
1. Complete mental map
2. Core idea
3. 3-5 main points
4. Ultra-short version
```

Short mode never shrinks the mental map.

### Default

Use:

```text
1. Complete mental map
2. Core idea
3. Compact visual concept map
4. Explanation by parts
5. Important insights
6. Ultra-short version
```

Add other sections only when they materially improve understanding.

### Long

Use:

```text
1. Complete mental map
2. Core idea
3. Visual concept map
4. Explanation by parts
5. Descriptive boxes
6. Analogies, if useful
7. Practical examples
8. Important insights
9. What people misunderstand
10. Ultra-short version
11. My read, if useful
```

Long mode adds interpretation layers, not verbosity.
