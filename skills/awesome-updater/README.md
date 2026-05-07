# Awesome Updater

`awesome-updater` installs, discovers, checks, backs up, rolls back, and auto-updates managed Awesome NanoClaw Skills.

It is an admin/package skill, not a normal analysis skill. Its job is lifecycle management for skill folders in a NanoClaw runtime.

## Use It

Primary command:

```txt
/awesome-updater help
```

Other examples:

```txt
/nanoskills updates
/awesome-updater discover
/awesome-updater check feba-board
```

Aliases and trigger phrases:

```txt
updater
updates
auto-update
managed skills
```

## Defaults

| Setting | Default | Effect |
| --- | --- | --- |
| `update_check` | `true` | Checks for newer commits, throttled to once per hour per skill. |
| `auto_upgrade` | `true` | Applies available updates without asking, after validation and backup. |
| `discover_new` | `true` | Installs newly added first-party skills from this curated package. |
| `throttle_seconds` | `3600` | Avoids repeated network checks during frequent skill use. |
| `discover_throttle_seconds` | `3600` | Avoids repeated package-wide discovery during frequent skill use. |
| `hash_algorithm` | `sha256` | Detects updates by exact per-skill content rather than whole-repo commits. |

## Safety Model

Before replacing a skill, the updater verifies the source, rejects symlinks, backs up the installed copy, writes managed metadata, and restores the backup if replacement fails.

Only skills with `.awesome-skill.json` metadata are managed. Existing unmanaged folders are skipped instead of overwritten.

## Install

Bootstrap the updater first:

```bash
SKILLS_DIR=/path/to/nanoclaw/container/skills
python3 skills/awesome-updater/scripts/awesome_skills.py install awesome-updater \
  --source-dir "$PWD" \
  --skills-dir "$SKILLS_DIR"
```

Then install a managed skill:

```bash
python3 "$SKILLS_DIR/awesome-updater/scripts/awesome_skills.py" install feba-board \
  --source-dir "$PWD" \
  --skills-dir "$SKILLS_DIR"
```

## Check Status

```bash
python3 "$SKILLS_DIR/awesome-updater/scripts/awesome_skills.py" status \
  --skills-dir "$SKILLS_DIR" \
  --source-dir "$PWD"
```

## Validate

```bash
skills/awesome-updater/scripts/validate-awesome-updater.sh
```
