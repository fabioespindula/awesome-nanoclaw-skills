---
name: awesome-updater
description: Use when installing, discovering, checking, configuring, or auto-updating Awesome NanoClaw Skills. Provides safe default-on auto-upgrades and first-party skill discovery with metadata, throttling, backups, validation, and rollback.
user-invocable: true
metadata:
  slash-command: /awesome-updater
  output: update-status
  default_auto_upgrade: true
  default_update_check: true
  source: fabioespindula/awesome-nanoclaw-skills
  catalog:
    group: admin
    order: 20
    aliases:
      - updater
      - updates
      - auto-update
      - managed skills
    use_when: The user wants lifecycle operations rather than usage help.
    expected_output: Update, install, config, backup, rollback, or discovery status based on the updater JSON summary.
    examples:
      - /awesome-updater help
      - /nanoskills updates
      - /awesome-updater discover
      - /awesome-updater check feba-board
    readme_include: false
    readme_description: Managed install, discovery, backup, rollback, and auto-update infrastructure.
---

# Awesome Updater

Use this skill to install and keep Awesome NanoClaw Skills up to date.

The updater is intentionally central: individual skills should not each reimplement update logic. Installed skills carry a `.awesome-skill.json` metadata file, and this skill's script reads that metadata to check for content-level skill updates, discover newly added first-party skills, apply updates, and preserve rollback backups.

## Defaults

- `update_check`: `true`
- `auto_upgrade`: `true`
- `discover_new`: `true`
- `branch`: `main`
- hash algorithm: `sha256` over exact skill file bytes and normalized relative paths
- update throttle: one update check per skill per hour unless `--force` is used
- discover throttle: one package-wide discover per hour unless `--force` is used

Auto-upgrade and first-party discovery are on by default for security: fixes to unsafe instructions, dependencies, validation logic, install procedures, or newly published curated skills should reach installed agents without requiring manual action.

Update decisions are based on the managed skill's content hash, not only on the repository commit. A repository commit that changes another skill should update `last_seen_commit` provenance but must not replace or back up an unchanged skill.

## Help Mode

If the user invokes `/awesome-updater help`, `/awesome-updater ajuda`, `/awesome-updater examples`, `/awesome-updater exemplos`, or asks how to use this skill, explain usage instead of installing, checking, or configuring anything.

The help response should include:

- what Awesome Updater does;
- when to use it;
- what it can modify;
- command forms for install, discover, check, config, and `/nanoskills updates`;
- what input the user should provide;
- what output the user gets;
- curated examples;
- contextual examples when the visible conversation includes a useful skill name or runtime skills directory.

Curated examples:

- `/awesome-updater help`
- `/nanoskills updates`
- `/awesome-updater discover`
- `/awesome-updater check feba-board`

## Safety Model

Before replacing a skill, the updater:

1. acquires a lock so only one update runs at a time
2. verifies the source skill exists and contains `SKILL.md`
3. rejects symlinks in the source skill
4. backs up the installed skill under `.awesome-backups/`
5. copies the new skill into place
6. writes updated `.awesome-skill.json` metadata with `metadata_version: 2`, `hash_algorithm: sha256`, `installed_hash`, and `last_seen_hash`
7. restores the backup if replacement fails

The updater only manages skills that contain `.awesome-skill.json`. If a skill has no metadata, do not auto-update it; install it through this updater first.

Discovery follows the trusted first-party package model: it syncs skills that are present in the configured Awesome NanoClaw Skills source repository. It does not install arbitrary third-party skills from unknown sources. Existing unmanaged skill folders are skipped instead of overwritten. Discovery is best-effort: if one skill update fails, that skill is restored from its own backup and other successful skill updates are kept.

## Command Patterns

Bootstrap the updater into a NanoClaw runtime:

```bash
python3 scripts/awesome_skills.py install awesome-updater   --source-dir /path/to/awesome-nanoclaw-skills   --skills-dir /path/to/nanoclaw/container/skills
```

Install a skill into a NanoClaw runtime:

```bash
python3 scripts/awesome_skills.py install feba-board   --source-dir /path/to/awesome-nanoclaw-skills   --skills-dir /path/to/nanoclaw/container/skills
```

Discover newly added curated skills and check existing managed skills:

```bash
python3 scripts/awesome_skills.py discover   --skills-dir /path/to/nanoclaw/container/skills
```

Check and auto-upgrade one installed skill:

```bash
python3 scripts/awesome_skills.py check feba-board   --skills-dir /path/to/nanoclaw/container/skills   --auto
```

Preview an update without writing metadata, backups, or skill files:

```bash
python3 scripts/awesome_skills.py check feba-board   --skills-dir /path/to/nanoclaw/container/skills   --auto   --force   --dry-run
```

Show read-only managed skill status:

```bash
python3 scripts/awesome_skills.py status   --skills-dir /path/to/nanoclaw/container/skills   --source-dir /path/to/awesome-nanoclaw-skills
```

Force a check, ignoring the one-hour throttle:

```bash
python3 scripts/awesome_skills.py check feba-board   --skills-dir /path/to/nanoclaw/container/skills   --auto   --force
```

Change config for one installed skill:

```bash
python3 scripts/awesome_skills.py config feba-board   --skills-dir /path/to/nanoclaw/container/skills   --set auto_upgrade=false
```

Disable first-party skill discovery from the package config stored on `awesome-updater`:

```bash
python3 scripts/awesome_skills.py config awesome-updater   --skills-dir /path/to/nanoclaw/container/skills   --set discover_new=false
```

## Preamble For Managed Skills

Managed skills can include this lightweight preamble before their normal workflow:

```bash
python3 /path/to/container/skills/awesome-updater/scripts/awesome_skills.py check awesome-updater   --skills-dir /path/to/container/skills || true
python3 /path/to/container/skills/awesome-updater/scripts/awesome_skills.py discover   --skills-dir /path/to/container/skills || true
python3 /path/to/container/skills/awesome-updater/scripts/awesome_skills.py check <skill-name>   --skills-dir /path/to/container/skills || true
```

If the check or discover step fails because of network or GitHub availability, continue the original skill workflow. Update failures should not block normal use unless the user explicitly asked to update.

## Output Rules

- Return the JSON summary from the script when the user asks for update status.
- Mention whether skills were discovered, already current, changed by content hash, would upgrade in dry-run, upgraded, throttled, skipped by config, skipped because unmanaged, or restored from backup.
- Treat `status` and `--dry-run` as read-only inspection. They must not write metadata, create backups, or replace skills.
- Do not expose tokens or environment variables.
- Do not auto-update skills without `.awesome-skill.json` metadata.
