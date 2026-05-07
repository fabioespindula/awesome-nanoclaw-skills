# Awesome NanoClaw Skills

Curated, security-conscious AI skills for NanoClaw agents.

This repository curates small, portable skill folders that can be copied into a NanoClaw runtime. Each skill contains a `SKILL.md` file plus optional references, templates, scripts, and assets.

Use this repository to add focused capabilities to an agent without turning the main system prompt into a giant instruction block.

## Available Skills

<!-- BEGIN GENERATED AVAILABLE SKILLS -->
### User-Facing Skills

| Skill | Description |
| --- | --- |
| [feba-board](skills/feba-board) | Five VC perspectives for important decisions, plans, and tradeoffs. |
| [read-for-me](skills/read-for-me) | Context-aware URL briefs with confidence and safe next steps. |
| [rethink](skills/rethink) | Reframe plans, ideas, and decisions before committing. |
| [think-big](skills/think-big) | Strategic future scans with signals, scenarios, risks, and opportunities. |
| [whisper-transcribe](skills/whisper-transcribe) | Local faster-whisper transcription with modes, manifest, and txt/srt/vtt/md output. |

### Admin / Package Skills

| Skill | Description |
| --- | --- |
| [nanoskills](skills/nanoskills) | Package-level catalog and help for all Awesome NanoClaw Skills. |
| [awesome-updater](skills/awesome-updater) | Managed install, discovery, backup, rollback, and auto-update infrastructure. |
<!-- END GENERATED AVAILABLE SKILLS -->

## Quick Start

Clone the repository and copy the skill folders you want into your NanoClaw runtime.

## What Is a Skill?

A NanoClaw skill is a folder that gives an agent a focused capability through a `SKILL.md` contract and optional supporting files.
