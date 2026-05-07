# NanoSkills Catalog

This file is generated from `skills/*/SKILL.md` frontmatter. Do not edit it by hand.

Only list skills from this generated catalog. Do not merge global runtime skills, external skills, or inferred capabilities.

Answer in the language of the current conversation. Keep skill names and slash commands literal.

## User-Facing Skills

### feba-board

- Slash command: `/febaboard`
- What it does: Five VC perspectives for important decisions, plans, and tradeoffs.
- Use when: The user has a meaningful decision, plan, tradeoff, investment question, product question, or asks for a second opinion from a board.
- Output: Compact chat-friendly recommendation with board tensions, next action, optional advisor expansion, and transcript saving only on request.
- Curated examples:
  - `/febaboard Should we ship this week or wait until onboarding is better?`
  - `/febaboard Help me decide whether to launch now or wait until onboarding is better.`
  - `help me decide whether to accept this large customer`

### read-for-me

- Slash command: `/read-for-me`
- What it does: Context-aware URL briefs with confidence and safe next steps.
- Use when: The user sends links, asks what a link says, asks whether a source matters, or wants a quick decision-ready summary.
- Output: Link brief with title, source, date, access level, confidence, relevance score, categories, and next action.
- Curated examples:
  - `/read-for-me https://example.com/article`
  - `/readthis https://example.com/article`
  - `Read this and tell me whether it matters for our launch plan: https://example.com/post`
  - `/read Analyze this link and tell me what changes for the project. https://example.com`

### rethink

- Slash command: `/rethink`
- What it does: Reframe plans, ideas, and decisions before committing.
- Use when: The user has a specific decision, product idea, architecture plan, career or life choice, or company direction and wants better decision quality.
- Output: Concise decision review with real question, assumptions, alternatives, risks, recommendation, and next move.
- Curated examples:
  - `/rethink Should I build the global skill catalog as a separate skill or inside the updater?`
  - `/rethink Is this launch plan too big for the first version?`
  - `/rethink Help me decide between hiring now or keeping the team small.`

### think-big

- Slash command: `/think-big`
- What it does: Strategic future scans with signals, scenarios, risks, and opportunities.
- Use when: The user wants to open the possibility space around a broad market, product, technology, society, career, company, or behavior theme.
- Output: Strategic exploration with framing, signals, scenarios, opportunities, risks, and useful provocations.
- Curated examples:
  - `/think-big future of AI-first CRMs`
  - `/think-big future of agent marketplaces`
  - `/think-big What happens to checkout experiences when agents buy for users?`

### whisper-transcribe

- Slash command: `/whisper-transcribe`
- What it does: Local faster-whisper transcription with modes, manifest, and txt/srt/vtt/md output.
- Use when: The user has a local media file and wants transcription, captions, subtitles, meeting text, or archive-ready transcript artifacts.
- Output: Saved transcript and caption artifacts plus a concise chat summary with mode, language, model, formats, output paths, manifest, and suggested next action.
- Curated examples:
  - `/whisper-transcribe /absolute/path/to/audio.mp3`
  - `/whisper-transcribe /absolute/path/to/video.mp4 --mode captions`
  - `/whisper-transcribe Transcribe this audio and generate SRT. /absolute/path/audio.m4a`

## Admin / Package Skills

### nanoskills

- Slash command: `/nanoskills`
- What it does: Package-level catalog and help for all Awesome NanoClaw Skills.
- Use when: The user wants to discover available skills, understand what each one does, or get help and examples for a specific skill.
- Output: Language-matched package catalog or skill-specific help.
- Curated examples:
  - `/nanoskills`
  - `/nanoskills help board`
  - `/nanoskills help think-big`

### awesome-updater

- Slash command: `/awesome-updater`
- What it does: Managed install, discovery, backup, rollback, and auto-update infrastructure.
- Use when: The user wants lifecycle operations rather than usage help.
- Output: Update, install, config, backup, rollback, or discovery status based on the updater JSON summary.
- Curated examples:
  - `/awesome-updater help`
  - `/nanoskills updates`
  - `/awesome-updater discover`
  - `/awesome-updater check feba-board`

## Catalog Grouping

Show these skills under `User-Facing Skills`:

- feba-board
- read-for-me
- rethink
- think-big
- whisper-transcribe

Show these skills under `Admin / Package Skills`:

- nanoskills
- awesome-updater

If this file is missing or stale in a NanoClaw container, `/nanoskills` should fail closed and ask for the package catalog to be updated or reinstalled.
