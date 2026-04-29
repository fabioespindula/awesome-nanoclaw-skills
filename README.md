# Awesome NanoClaw Skills

```txt
███╗   ██╗ █████╗ ███╗   ██╗ ██████╗  ██████╗██╗      █████╗ ██╗    ██╗
████╗  ██║██╔══██╗████╗  ██║██╔═══██╗██╔════╝██║     ██╔══██╗██║    ██║
██╔██╗ ██║███████║██╔██╗ ██║██║   ██║██║     ██║     ███████║██║ █╗ ██║
██║╚██╗██║██╔══██║██║╚██╗██║██║   ██║██║     ██║     ██╔══██║██║███╗██║
██║ ╚████║██║  ██║██║ ╚████║╚██████╔╝╚██████╗███████╗██║  ██║╚███╔███╔╝
╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝
                         S K I L L S
```

Curated, security-conscious AI skills for NanoClaw agents.

This repository curates small, portable skill folders that can be copied into a NanoClaw runtime. Each skill contains a `SKILL.md` file plus optional references, templates, scripts, and assets.

Use this repository to add focused capabilities to an agent without turning the main system prompt into a giant instruction block.

## Available Skills

| Skill | Description |
| --- | --- |
| [`nano-council`](skills/nano-council) | Five-advisor council for pressure-testing decisions, plans, and tradeoffs. |
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
| [`nano-council`](skills/nano-council) | NanoClaw agent runtime with skill loading. |
| [`whisper-transcribe`](skills/whisper-transcribe) | Python 3.10+, `faster-whisper`, and local media codec support. Some video formats may also require `ffmpeg`. |

## Safety

Review each `SKILL.md` before installing it. Skills may instruct agents to use tools, read files, run scripts, or follow workflows depending on your NanoClaw setup.

For production runtimes, install only the skills the agent needs and test each one before adding more.

## Skill Backlog

These are candidate skills. If you want one of them next, open an issue or comment with your use case.

| Skill | Description |
| --- | --- |
| `deep-research-agent` | Research workflow with source tracking and citation formatting. |
| `github-manager` | GitHub issues, pull requests, and repository maintenance through chat. |
| `morning-briefing` | Daily briefing from connected context and priorities. |
| `self-improving-agent` | Logs failures, extracts lessons, and improves future behavior over time. |
| `proactive-agent` | Anticipates needs using layered memory and context signals. |
| `calendar-assistant` | Calendar workflows through chat. |
| `obsidian-vault` | Reads, writes, searches, and organizes Obsidian notes. |
| `web-clipper` | Saves, summarizes, and categorizes links automatically. |
| `editorial-rewriter` | Rewrites drafts for clarity, tone, and plain-language readability. |

## Repository Structure

```txt
awesome-nanoclaw-skills/
  README.md
  LICENSE
  skills/
    nano-council/
      SKILL.md
      references/
      assets/
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
