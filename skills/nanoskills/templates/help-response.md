# Help Response Template

Use this shape for `/nanoskills help <skill>` and for individual skill help modes.

Keep the heading and prose in the language of the current conversation. Keep command names literal.

## Shape

```md
## <Skill Name>

<One-sentence purpose.>

Use when:
- <case 1>
- <case 2>
- <case 3>

Do not use when:
- <only include if the boundary matters>

Commands:
- `/<command> <input>`
- `/nanoskills help <skill>`

What to provide:
- <input expectation>

What you get:
- <output expectation>

Examples:
- `<curated example 1>`
- `<curated example 2>`
- `<curated example 3>`

Contextual examples:
- `<adapted from visible conversation context>`
```

## Rules

- Include `Contextual examples` only when the conversation has enough concrete context.
- Do not include sensitive details from conversation history.
- Use 2-4 examples total unless the user asks for more.
- Prefer examples that look directly usable in chat.
- If the skill has dependencies, mention them under `What to provide` or `What you get`, not as a long setup guide.
