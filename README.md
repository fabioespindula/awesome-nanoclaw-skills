# Awesome NanoClaw Skills

```txt
░█▀█░█░█░█▀▀░█▀▀░█▀█░█▄█░█▀▀
░█▀█░█▄█░█▀▀░▀▀█░█░█░█░█░█▀▀
░▀░▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀▀▀

░█▀█░█▀█░█▀█░█▀█░█▀▀░█░░░█▀█░█░█░░░█▀▀░█░█░▀█▀░█░░░█░░░█▀▀
░█░█░█▀█░█░█░█░█░█░░░█░░░█▀█░█▄█░░░▀▀█░█▀▄░░█░░█░░░█░░░▀▀█
░▀░▀░▀░▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀░▀░░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀
```

Curated, security-conscious AI skills for NanoClaw agents.

This repository curates small, portable skill folders that can be copied into a NanoClaw runtime. Each skill contains a `SKILL.md` file plus optional references, templates, scripts, and assets.

Use this repository to add focused capabilities to an agent without turning the main system prompt into a giant instruction block.

## Available Skills

<!-- BEGIN GENERATED AVAILABLE SKILLS -->
| Skill | Description |
| --- | --- |
| [feba-board](skills/feba-board) | Five VC perspectives for important decisions, plans, and tradeoffs. |
| [read-for-me](skills/read-for-me) | Context-aware URL briefs with confidence and safe next steps. |
| [rethink](skills/rethink) | Reframe plans, ideas, and decisions before committing. |
| [think-big](skills/think-big) | Strategic future scans with signals, scenarios, risks, and opportunities. |
| [whisper-transcribe](skills/whisper-transcribe) | Local faster-whisper transcription with modes, manifest, and txt/srt/vtt/md output. |
| [nanoskills](skills/nanoskills) | Package-level catalog and help for all Awesome NanoClaw Skills. |
<!-- END GENERATED AVAILABLE SKILLS -->

## Quick Start

Clone the repository:

```bash
git clone https://github.com/fabioespindula/awesome-nanoclaw-skills.git
cd awesome-nanoclaw-skills
```

Choose a skill and review it before installing:

```bash
SKILL=feba-board
less "skills/$SKILL/SKILL.md"
```

Install one skill into a NanoClaw container runtime:

```bash
mkdir -p /path/to/nanoclaw/container/skills
rsync -a "skills/$SKILL/" "/path/to/nanoclaw/container/skills/$SKILL/"
```

Restart NanoClaw if your runtime requires it.

Try it:

```txt
/nanoskills
/febaboard Should we ship the first version this week or wait until onboarding is better?
```

To install another skill, change `SKILL` to the folder name you want.

For local testing, you can copy every skill:

```bash
mkdir -p /path/to/nanoclaw/container/skills
rsync -a skills/ /path/to/nanoclaw/container/skills/
```

Discover and learn skills from inside chat:

```txt
/nanoskills
/nanoskills help think-big
/febaboard help
```

## What Is a Skill?

A NanoClaw skill is a folder that gives an agent a focused capability:

```txt
skill-name/
  SKILL.md
  references/
  assets/
  scripts/
```

`SKILL.md` defines when the skill should trigger and how the agent should behave. Optional folders can include examples, templates, prompts, scripts, and supporting material.

Each skill should make clear:

- what it does
- when to use it
- how to install or run it
- what requirements it has
- one or more example prompts

Skills are prompt-native. No compilation step is required.

## Requirements

This collection assumes a NanoClaw runtime that can load skill folders from `container/skills/`.

Some skills may require local tools or model dependencies. Check each skill folder before installing it into a production runtime.

Current skill requirements:

| Skill | Requirements |
| --- | --- |
| [feba-board](skills/feba-board) | NanoClaw runtime with this skill installed; no external tools required. |
| [read-for-me](skills/read-for-me) | NanoClaw runtime with URL fetching or browsing tools. Optional memory/profile tools improve personalization but are not required. |
| [rethink](skills/rethink) | NanoClaw runtime; browser or research tools only when the decision depends on current facts. |
| [think-big](skills/think-big) | NanoClaw runtime; browser or research tools for current sources. |
| [whisper-transcribe](skills/whisper-transcribe) | Python 3.10+, `faster-whisper`, and local media codec support. Some video formats may also require `ffmpeg`. |
| [nanoskills](skills/nanoskills) | NanoClaw runtime with skill loading and local access to this package's generated catalog. |

Managed updates use [`awesome-updater`](skills/awesome-updater), which requires Python 3.10+, `git`, and network access for GitHub checks and first-party skill discovery.

## Safety

Review each `SKILL.md` before installing it. Skills may instruct agents to use tools, read files, run scripts, or follow workflows depending on your NanoClaw setup.

For production runtimes, install only the skills the agent needs and test each one before adding more.

## Auto Updates

[`awesome-updater`](skills/awesome-updater) is the management tool for installing, validating, backing up, and auto-updating managed skills. It is infrastructure for this collection, not a user-facing skill in the list above.

[`nanoskills`](skills/nanoskills) is the discovery and help layer. It lists the full package and explains how to use each skill. It can route update-related questions to `awesome-updater`, but the catalog/help logic itself stays fast, offline, and non-mutating.

Install skills through `awesome-updater` when you want managed updates. Managed skills get a `.awesome-skill.json` metadata file with update checks, content hashes, and auto-upgrade enabled by default.

Default behavior:

| Setting | Default | Effect |
| --- | --- | --- |
| `update_check` | `true` | Checks for newer commits, throttled to once per hour per skill. |
| `auto_upgrade` | `true` | Applies available updates without asking, after validation and backup. |
| `discover_new` | `true` | Installs newly added first-party skills from this curated package. |
| `throttle_seconds` | `3600` | Avoids repeated network checks during frequent skill use. |
| `discover_throttle_seconds` | `3600` | Avoids repeated package-wide discovery during frequent skill use. |
| `hash_algorithm` | `sha256` | Detects updates by exact per-skill content rather than whole-repo commits. |

Bootstrap the updater first. This makes the central updater managed too, so it can update itself:

```bash
SKILLS_DIR=/path/to/nanoclaw/container/skills
python3 skills/awesome-updater/scripts/awesome_skills.py install awesome-updater \
  --source-dir "$PWD" \
  --skills-dir "$SKILLS_DIR"
```

Then install any managed skill through the updater:

```bash
python3 "$SKILLS_DIR/awesome-updater/scripts/awesome_skills.py" install feba-board \
  --source-dir "$PWD" \
  --skills-dir "$SKILLS_DIR"
```

Discover newly added curated skills and check existing managed skills:

```bash
python3 "$SKILLS_DIR/awesome-updater/scripts/awesome_skills.py" discover \
  --skills-dir "$SKILLS_DIR"
```

Check and auto-upgrade an installed skill:

```bash
python3 "$SKILLS_DIR/awesome-updater/scripts/awesome_skills.py" check feba-board \
  --skills-dir "$SKILLS_DIR" \
  --auto
```

Preview an update without writing files:

```bash
python3 "$SKILLS_DIR/awesome-updater/scripts/awesome_skills.py" check feba-board \
  --skills-dir "$SKILLS_DIR" \
  --source-dir "$PWD" \
  --auto \
  --force \
  --dry-run
```

Inspect managed and unmanaged skill state:

```bash
python3 "$SKILLS_DIR/awesome-updater/scripts/awesome_skills.py" status \
  --skills-dir "$SKILLS_DIR" \
  --source-dir "$PWD"
```

Managed skills should check `awesome-updater` first, run the throttled `discover` sync, then check themselves. The updater validates source skills, compares exact skill content hashes, backs up installed copies under `.awesome-backups/`, replaces only changed managed skills, skips unmanaged existing folders, and restores the failed skill's backup if replacement fails.

For host-level automatic discovery, run the same `discover` command from cron, launchd, or your scheduler about once per hour. The command is throttled, so preamble and host triggers can coexist safely.

## Skill Backlog

These are candidate skills. If you want one of them next, open an issue or comment with your use case.

| Skill | Description |
| --- | --- |
| `skill-auditor` | Audits NanoClaw and OpenClaw skills for unsafe commands, secret exfiltration, risky install steps, and undocumented network access. |
| `web-clipper` | Saves, summarizes, tags, and organizes links sent from chat channels such as Telegram and WhatsApp. |
| `morning-briefing` | Generates a daily briefing from saved context, priorities, calendars, tasks, and relevant external signals. |
| `meeting-assistant` | Turns meeting audio, transcripts, notes, and chat context into summaries, decisions, action items, and follow-ups. |
| `firecrawl-research` | Uses Firecrawl-backed crawling and extraction to produce sourced research briefs from websites and docs. |
| `self-improving-agent` | Captures mistakes, preferences, and lessons learned so future agent runs can improve with reviewable updates. |
| `mcp-bridge` | Helps connect NanoClaw skills to MCP servers and external tool providers through safe setup workflows. |
| `skill-porting-kit` | Converts or adapts OpenClaw, Claude Code, Codex, Cursor, and other `SKILL.md`-compatible skills for NanoClaw. |
| `notion-knowledge-base` | Reads, writes, searches, and organizes Notion pages, tasks, and lightweight knowledge bases. |
| `context7-docs` | Pulls current developer documentation into coding workflows using Context7-style doc retrieval. |

## Repository Structure

```txt
awesome-nanoclaw-skills/
  README.md
  LICENSE
  skills/
    awesome-updater/
      SKILL.md
      scripts/
      tests/
    nanoskills/
      SKILL.md
      references/
      templates/
      scripts/
    feba-board/
      SKILL.md
      references/
      assets/
      scripts/
    read-for-me/
      SKILL.md
      references/
      templates/
      scripts/
    rethink/
      SKILL.md
      references/
    think-big/
      SKILL.md
      references/
    whisper-transcribe/
      SKILL.md
      scripts/
      tests/
```

## Project Status

These skills are usable today, but the collection is still early. Interfaces, prompts, scripts, and folder conventions may change before a v1.0 release.

## Philosophy

Good agents do not need one giant prompt. They need focused capabilities with clear boundaries.

The collection is built around a few principles:

- small skills over monolithic agents
- explicit workflows over vague instructions
- useful disagreement over automatic agreement
- local-first tools when possible
- readable Markdown over hidden complexity

## Contributing

Issues and suggestions are welcome.

Pull requests are welcome for:

- documentation fixes
- new examples
- improvements to existing skills

New skill proposals should be opened as an issue first.

Good skills should be:

- focused on one capability
- easy to inspect
- useful without private context
- documented with examples
- safe to run in a normal agent workflow

## License

MIT. See [LICENSE](LICENSE).
