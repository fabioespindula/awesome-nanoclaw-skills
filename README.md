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

| Skill | Description |
| --- | --- |
| [`awesome-updater`](skills/awesome-updater) | Central installer and default-on auto-updater for managed Awesome NanoClaw Skills. |
| [`nano-council`](skills/nano-council) | Five-advisor council for pressure-testing decisions, plans, and tradeoffs. |
| [`read-for-me`](skills/read-for-me) | Personal link analyst that reads URLs, states access/confidence, summarizes, scores relevance, categorizes, and suggests a non-destructive next action. |
| [`whisper-transcribe`](skills/whisper-transcribe) | Local audio/video transcription with faster-whisper and txt/srt/vtt output. |

## Quick Start

Clone the repository:

```bash
git clone https://github.com/fabioespindula/awesome-nanoclaw-skills.git
cd awesome-nanoclaw-skills
```

Choose a skill and review it before installing:

```bash
SKILL=nano-council
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
/council Should we ship the first version this week or wait until onboarding is better?
```

To install another skill, change `SKILL` to the folder name you want.

For local testing, you can copy every skill:

```bash
mkdir -p /path/to/nanoclaw/container/skills
rsync -a skills/ /path/to/nanoclaw/container/skills/
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

Current examples:

| Skill | Requirements |
| --- | --- |
| [`awesome-updater`](skills/awesome-updater) | Python 3.10+ and `git`. Network access is needed when checking GitHub for updates. |
| [`nano-council`](skills/nano-council) | NanoClaw agent runtime with skill loading. |
| [`read-for-me`](skills/read-for-me) | NanoClaw agent runtime with URL fetching or browsing tools. Optional memory/profile tools improve personalization but are not required. |
| [`whisper-transcribe`](skills/whisper-transcribe) | Python 3.10+, `faster-whisper`, and local media codec support. Some video formats may also require `ffmpeg`. |

## Safety

Review each `SKILL.md` before installing it. Skills may instruct agents to use tools, read files, run scripts, or follow workflows depending on your NanoClaw setup.

For production runtimes, install only the skills the agent needs and test each one before adding more.

## Auto Updates

Install skills through [`awesome-updater`](skills/awesome-updater) when you want managed updates. Managed skills get a `.awesome-skill.json` metadata file with update checks and auto-upgrade enabled by default.

Default behavior:

| Setting | Default | Effect |
| --- | --- | --- |
| `update_check` | `true` | Checks for newer commits, throttled to once per hour per skill. |
| `auto_upgrade` | `true` | Applies available updates without asking, after validation and backup. |
| `throttle_seconds` | `3600` | Avoids repeated network checks during frequent skill use. |

Bootstrap the updater first. This makes the central updater managed too, so it can update itself:

```bash
SKILLS_DIR=/path/to/nanoclaw/container/skills
python3 skills/awesome-updater/scripts/awesome_skills.py install awesome-updater \
  --source-dir "$PWD" \
  --skills-dir "$SKILLS_DIR"
```

Then install any managed skill through the updater:

```bash
python3 "$SKILLS_DIR/awesome-updater/scripts/awesome_skills.py" install nano-council \
  --source-dir "$PWD" \
  --skills-dir "$SKILLS_DIR"
```

Check and auto-upgrade an installed skill:

```bash
python3 "$SKILLS_DIR/awesome-updater/scripts/awesome_skills.py" check nano-council \
  --skills-dir "$SKILLS_DIR" \
  --auto
```

Managed skills should check `awesome-updater` first, then themselves. The updater validates the source skill, backs up the installed copy under `.awesome-backups/`, replaces the skill, and restores the backup if replacement fails.

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
    nano-council/
      SKILL.md
      references/
      assets/
      scripts/
    read-for-me/
      SKILL.md
      references/
      templates/
      scripts/
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
