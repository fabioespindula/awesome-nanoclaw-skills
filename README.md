# NanoClaw Skills

```txt
███╗   ██╗ █████╗ ███╗   ██╗ ██████╗  ██████╗██╗      █████╗ ██╗    ██╗
████╗  ██║██╔══██╗████╗  ██║██╔═══██╗██╔════╝██║     ██╔══██╗██║    ██║
██╔██╗ ██║███████║██╔██╗ ██║██║   ██║██║     ██║     ███████║██║ █╗ ██║
██║╚██╗██║██╔══██║██║╚██╗██║██║   ██║██║     ██║     ██╔══██║██║███╗██║
██║ ╚████║██║  ██║██║ ╚████║╚██████╔╝╚██████╗███████╗██║  ██║╚███╔███╔╝
╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝
                         S K I L L S
```

Reusable AI skills for NanoClaw.

NanoClaw Skills is a growing collection of modular skills for building sharper, more useful AI agents. Each skill is a small, portable bundle of instructions, prompts, references, and templates that gives an agent a specific capability.

Start small. Compose capabilities. Ship better agents.

## Available Skills

| Skill | Status | Description |
| --- | --- | --- |
| `nano-council` | alpha | Five-advisor council for pressure-testing decisions, plans, and tradeoffs. |

## Roadmap

| Skill | Description |
| --- | --- |
| `self-improving-agent` | Logs failures, extracts lessons, and improves future behavior over time. |
| `proactive-agent` | Anticipates needs using layered memory and context signals. |
| `deep-research-agent` | Performs academic-style research with source tracking and APA citations. |
| `humanize-ai-text` | Rewrites AI-generated text to sound more natural and human. |
| `morning-briefing` | Generates a daily briefing from connected context and priorities. |
| `whisper-transcribe` | Runs local audio transcription with faster-whisper. |
| `github-manager` | Manages repositories, issues, pull requests, and reviews through chat. |
| `obsidian-vault` | Reads, writes, searches, and organizes Obsidian notes. |
| `web-clipper` | Saves, summarizes, and categorizes links automatically. |
| `calendar-assistant` | Creates, reads, updates, and deletes calendar events through chat. |

## What Is A Skill?

A NanoClaw skill is a folder that usually contains:

```txt
skill-name/
  SKILL.md
  references/
  assets/
```

`SKILL.md` defines when the skill should trigger and how the agent should behave. The optional `references/` and `assets/` folders hold prompts, examples, templates, and support material.

Skills are prompt-native. No compilation step is required.

## Repository Structure

```txt
nanoclaw-skills/
  README.md
  skills/
    nano-council/
      SKILL.md
      references/
      assets/
```

## Featured Skill: `nano-council`

`nano-council` creates a structured council of five AI advisors:

- **Red Team** challenges assumptions and failure modes.
- **Axiom** reasons from first principles.
- **Horizon** expands the option space.
- **Streetlight** brings an outside-field perspective.
- **Operator** turns analysis into executable next steps.

The advisors answer independently, review anonymized responses, and then a chairman synthesis highlights agreement, disagreement, blind spots, and the recommended next action.

## Install Through Claude Over SSH

Use this when NanoClaw is running on a server and you want Claude Code inside the SSH session to install the skill for you.

1. SSH into the NanoClaw machine.
2. Open Claude Code from the NanoClaw repository root.
3. Paste this prompt:

```txt
Install the Nano Council container skill from:

https://github.com/fabioespindula/nanoclaw-skills

Steps:
- Clone or fetch the repo into /tmp/nanoclaw-skills.
- Copy skills/nano-council into container/skills/nano-council in this NanoClaw repo.
- Do not copy local council transcript outputs.
- Run ./scripts/validate-nano-council.sh from the copied skill directory if present.
- Commit the change with: add nano council skill.
- Restart NanoClaw if this environment requires it.
- Tell me the exact installed path and the Telegram test prompt to run.
```

Manual equivalent:

```bash
cd /path/to/nanoclaw
rm -rf /tmp/nanoclaw-skills
git clone git@github.com:fabioespindula/nanoclaw-skills.git /tmp/nanoclaw-skills
mkdir -p container/skills
rsync -a --delete /tmp/nanoclaw-skills/skills/nano-council/ container/skills/nano-council/
git add container/skills/nano-council
git commit -m "add nano council skill"
```

For Telegram use, install into `container/skills/nano-council/`, not only `.claude/skills/`. The container skill is what the agent sees at runtime.

## Example

```txt
/council Should we ship the first version this week or wait until onboarding is better?
```

Expected output:

- recommendation first
- where the advisors agree
- where they disagree
- blind spots
- practical next action

## Philosophy

Good agents do not need one giant prompt. They need focused capabilities with clear boundaries.

NanoClaw Skills is built around a few principles:

- small skills over monolithic agents
- explicit workflows over vague instructions
- useful disagreement over automatic agreement
- local-first tools when possible
- readable Markdown over hidden complexity

## Status

This project is early. The first public goal is to make `nano-council` stable, documented, and easy to install.

## Contributing

Contributions are welcome once the first release is public. Good skills should be:

- focused on one capability
- easy to inspect
- useful without private context
- documented with examples
- safe to run in a normal agent workflow

## License

MIT
