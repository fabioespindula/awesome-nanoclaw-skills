---
name: nanoskills
description: Use when the user invokes /nanoskills, asks what NanoClaw skills are available, wants a package-level skill catalog, asks how to use a skill, or asks for help/examples for any Awesome NanoClaw Skill. Lists every skill in the package, explains what each one does, and provides language-matched help with curated and conversation-aware examples.
user-invocable: true
metadata:
  slash-command: /nanoskills
  output: skill-catalog
  catalog:
    group: admin
    order: 10
    aliases:
      - skills
      - lista skills
      - help skills
      - catalog
    use_when: The user wants to discover available skills, understand what each one does, or get help and examples for a specific skill.
    expected_output: Language-matched package catalog or skill-specific help.
    examples:
      - /nanoskills
      - /nanoskills help board
      - /nanoskills help think-big
    readme_include: true
    readme_description: Package-level catalog and help for all Awesome NanoClaw Skills.
---

# NanoSkills

Use this skill as the package-level catalog and help system for Awesome NanoClaw Skills.

`/nanoskills` is discovery and documentation. It should be fast, friendly, offline-first, and written in the language of the current conversation.

The catalog is generated from this package's `skills/*/SKILL.md` frontmatter during repository validation. In a NanoClaw container, treat installed skill files as read-only and only list first-party Awesome NanoClaw Skills from the generated catalog files.

## Managed Auto Update

If this skill is installed as a managed Awesome NanoClaw Skill and `../awesome-updater/scripts/awesome_skills.py` exists, run this before the normal workflow:

```bash
python3 ../awesome-updater/scripts/awesome_skills.py check awesome-updater --skills-dir .. || true
python3 ../awesome-updater/scripts/awesome_skills.py discover --skills-dir .. || true
python3 ../awesome-updater/scripts/awesome_skills.py check nanoskills --skills-dir .. || true
```

Continue the normal workflow if the update or discover check fails because of network, GitHub, or local environment issues.

Do not run extra package-wide update checks during normal catalog or help responses beyond the shared managed preamble above. Listing skills should be based on local catalog files and should not require network access to produce the answer.

## Triggers

Run this skill when the user invokes or asks for:

- `/nanoskills`
- `/nanoskills list`
- `/nanoskills lista`
- `/nanoskills help`
- `/nanoskills help <skill-or-command>`
- `/nanoskills ajuda <skill-or-command>`
- "what skills are available?"
- "quais skills existem?"
- "como uso esses skills?"
- "help for the NanoClaw skills"

## Load References

- Read `references/catalog.md` before listing skills.
- Use `references/catalog.json` only as resolver metadata for skill-specific help.
- Do not list aliases from `catalog.json` in normal catalog or normal help output. Aliases are private routing metadata.
- If the generated catalog files are missing, fail closed: say the package catalog is unavailable and recommend updating or reinstalling `nanoskills`.
- Never scan sibling runtime skill folders, global Claude/Codex skill folders, external package folders, memory, inferred capabilities, or chat history to build the catalog.
- Use `templates/help-response.md` when explaining one skill.

## Language

Answer in the language of the current conversation. If the conversation is mixed, follow the user's latest message. For Portuguese, use natural Brazilian Portuguese unless the user clearly uses another variant.

Do not translate slash commands, skill folder names, file paths, or literal command examples.

## Command Router

Choose the response from the user's command:

| Input | Behavior |
| --- | --- |
| `/nanoskills` | Show the full package catalog. |
| `/nanoskills list` or `/nanoskills lista` | Show the full package catalog. |
| `/nanoskills help` or `/nanoskills ajuda` | Explain how to use `/nanoskills` itself and show how to request help for one skill. |
| `/nanoskills help <skill-or-command>` | Show detailed help for the requested skill. |
| `/nanoskills updates` or `/nanoskills status` | Explain the relationship with `awesome-updater` and show safe update/status commands. Use updater tooling only when the user clearly asks to discover, check, install, configure, or upgrade. |

Accept skill names, aliases, and slash commands when resolving help:

- Prefer canonical skill names and primary slash commands from the generated catalog.
- Use aliases from `references/catalog.json` only to resolve a user's requested help target.
- If an alias resolves to a skill, explain the canonical command for that skill and do not promote the alias as a public command.

If the target skill is ambiguous or unknown, show the catalog and ask the user to choose one by name or slash command.

## Catalog Output

For `/nanoskills`, produce a scannable catalog:

1. one short sentence explaining that this is the Awesome NanoClaw Skills package;
2. `User-facing skills` section;
3. `Admin and package skills` section;
4. for each skill:
   - slash command;
   - what it does;
   - when to use it;
   - expected output;
   - one compact example;
5. close with examples of help commands.

Keep the catalog clear and visually pleasant, but do not use tables when the current chat surface is likely Telegram or mobile chat.

The normal catalog output must include only primary slash commands from `references/catalog.md`. Do not add compatible aliases, legacy aliases, global commands, runtime commands, health-check commands, or capability summaries that are not present as primary commands in the generated catalog.

## Help Mode

For `/nanoskills help <skill>`, use `templates/help-response.md`.

Detailed help must include:

- what the skill does;
- when to use it;
- when not to use it, if important;
- command forms, using primary slash commands only unless the user explicitly asks about an alias;
- expected input;
- expected output;
- curated examples;
- contextual examples when the current conversation has useful context.

## Contextual Examples

Help examples are hybrid:

- Always include curated examples from `references/catalog.md` or the target skill's `SKILL.md`.
- Add a `Contextual examples` section only when the visible conversation gives enough concrete context to create useful examples.
- Contextual examples should adapt the user's current topic, objects, filenames, links, decisions, or tasks into valid slash-command examples.
- Do not quote secrets, tokens, private URLs, long transcripts, or sensitive conversation content.
- If context is weak, omit contextual examples instead of inventing generic personalization.

Examples:

- If the conversation is about launch timing, `/febaboard Devo lancar agora ou esperar melhorar onboarding?`
- If the conversation is about a repo architecture decision, `/rethink Essa arquitetura de comandos globais esta simples o suficiente?`
- If the conversation includes a URL, `/readthis <url>`

## Auto-Update Relationship

`/nanoskills` is not the updater. It should explain and route update-related intent without merging responsibilities.

- Use `/nanoskills` and `/nanoskills help <skill>` for discovery and usage help.
- Use `awesome-updater` for install, discover, check, config, backup, rollback, and auto-upgrade behavior.
- Normal catalog/help responses must not run extra package-wide checks beyond the shared managed preamble.
- If the user asks to check updates, use `awesome-updater` instructions or tooling when available.
- If the user asks for a pure explanation, do not run update commands.

## Output Rules

- Match the language of the current conversation.
- Keep answers concise but complete enough that a new user can choose the right skill.
- Prefer commands and examples over abstract explanation.
- Do not claim a skill is installed unless runtime evidence shows it is installed.
- Do not require private memory, user profiles, Supabase, ContextHub, or any non-public context.
- Do not save tasks, write memory, install dependencies, update skills, or modify files unless the user explicitly asks for that action.
