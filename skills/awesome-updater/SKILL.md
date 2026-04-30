---
name: awesome-updater
description: Use when installing, checking, configuring, or auto-updating Awesome NanoClaw Skills. Provides safe default-on auto-upgrades with metadata, throttling, backups, validation, and rollback.
user-invocable: true
metadata:
  slash-command: /awesome-updater
  default_auto_upgrade: true
  default_update_check: true
  source: fabioespindula/awesome-nanoclaw-skills
---

# Awesome Updater

Use this skill to install and keep Awesome NanoClaw Skills up to date.

The updater is intentionally central: individual skills should not each reimplement update logic. Installed skills carry a `.awesome-skill.json` metadata file, and this skill's script reads that metadata to check for new versions, apply updates, and preserve rollback backups.

## Defaults

- `update_check`: `true`
- `auto_upgrade`: `true`
- `branch`: `main`
- throttle: one update check per skill per hour unless `--force` is used

Auto-upgrade is on by default for security: fixes to unsafe instructions, dependencies, validation logic, or install procedures should reach installed agents without requiring manual action.

## Help Mode

If the user invokes `/awesome-updater help`, `/awesome-updater ajuda`, `/awesome-updater examples`, `/awesome-updater exemplos`, or asks how to use this skill, explain usage instead of installing, checking, or configuring anything.

The help response should include:

- what Awesome Updater does;
- when to use it;
- what it can modify;
- command forms for install, check, config, and `/nanoskills updates`;
- what input the user should provide;
- what output the user gets;
- curated examples;
- contextual examples when the visible conversation includes a useful skill name or runtime skills directory.

Curated examples:

- `/awesome-updater help`
- `/nanoskills updates`
- `/awesome-updater check nano-council`

## Safety Model

Before replacing a skill, the updater:

1. acquires a lock so only one update runs at a time
2. verifies the source skill exists and contains `SKILL.md`
3. rejects symlinks in the source skill
4. backs up the installed skill under `.awesome-backups/`
5. copies the new skill into place
6. writes updated `.awesome-skill.json` metadata
7. restores the backup if replacement fails

The updater only manages skills that contain `.awesome-skill.json`. If a skill has no metadata, do not auto-update it; install it through this updater first.

## Command Patterns

Bootstrap the updater into a NanoClaw runtime:

```bash
python3 scripts/awesome_skills.py install awesome-updater   --source-dir /path/to/awesome-nanoclaw-skills   --skills-dir /path/to/nanoclaw/container/skills
```

Install a skill into a NanoClaw runtime:

```bash
python3 scripts/awesome_skills.py install nano-council   --source-dir /path/to/awesome-nanoclaw-skills   --skills-dir /path/to/nanoclaw/container/skills
```

Check and auto-upgrade one installed skill:

```bash
python3 scripts/awesome_skills.py check nano-council   --skills-dir /path/to/nanoclaw/container/skills   --auto
```

Force a check, ignoring the one-hour throttle:

```bash
python3 scripts/awesome_skills.py check nano-council   --skills-dir /path/to/nanoclaw/container/skills   --auto   --force
```

Change config for one installed skill:

```bash
python3 scripts/awesome_skills.py config nano-council   --skills-dir /path/to/nanoclaw/container/skills   --set auto_upgrade=false
```

## Preamble For Managed Skills

Managed skills can include this lightweight preamble before their normal workflow:

```bash
python3 /path/to/container/skills/awesome-updater/scripts/awesome_skills.py check awesome-updater   --skills-dir /path/to/container/skills   --auto || true
python3 /path/to/container/skills/awesome-updater/scripts/awesome_skills.py check <skill-name>   --skills-dir /path/to/container/skills   --auto || true
```

If the check fails because of network or GitHub availability, continue the original skill workflow. Update failures should not block normal use unless the user explicitly asked to update.

## Output Rules

- Return the JSON summary from the script when the user asks for update status.
- Mention whether the skill was already current, upgraded, throttled, skipped by config, or restored from backup.
- Do not expose tokens or environment variables.
- Do not auto-update skills without `.awesome-skill.json` metadata.
