# NanoSkills Catalog

This file is generated from `skills/*/SKILL.md` frontmatter. Do not edit it by hand.

Answer in the language of the current conversation. Keep skill names and slash commands literal.

## User-Facing Skills

### nano-council

- Slash command: `/council`
- Aliases: `council`, `conselho`, `pressure-test`, `testa essa decisao`
- What it does: Five-advisor council for pressure-testing decisions, plans, and tradeoffs.
- Use when: The user wants disagreement, a decision pressure test, a plan review, or a sharper recommendation before acting.
- Output: Telegram-friendly Markdown with recommendation, agreement, disagreement, blind spots, advisor snapshots, and next action.
- Curated examples:
  - `/council Should we ship the first version this week or wait until onboarding is better?`
  - `/council Quero decidir se faco launch agora ou espero melhorar onboarding.`
  - `/council Pressure-test this architecture before we build it.`

### read-for-me

- Slash command: `/read-for-me`
- Aliases: `read`, `summarize this`, `read this`, `analisa esse link`, `bare URLs`
- What it does: Context-aware URL briefs with confidence and safe next steps.
- Use when: The user sends links, asks what a link says, asks whether a source matters, or wants a quick decision-ready summary.
- Output: Link brief with title, source, date, access level, confidence, relevance score, categories, and next action.
- Curated examples:
  - `/read-for-me https://example.com/article`
  - `Read this and tell me whether it matters for our launch plan: https://example.com/post`
  - `/read-for-me Analisa esse link e me diz o que muda para o projeto. https://example.com`

### rethink

- Slash command: `/rethink`
- Aliases: `rethink`, `step back`, `gut-check`, `pressure-test`, `simplify this`, `decide`
- What it does: Reframe plans, ideas, and decisions before committing.
- Use when: The user has a specific decision, product idea, architecture plan, career or life choice, or company direction and wants better decision quality.
- Output: Concise decision review with real question, assumptions, alternatives, risks, recommendation, and next move.
- Curated examples:
  - `/rethink Should I build the global skill catalog as a separate skill or inside the updater?`
  - `/rethink Esse plano de launch esta grande demais para a primeira versao?`
  - `/rethink Help me decide between hiring now or keeping the team small.`

### think-big

- Slash command: `/think-big`
- Aliases: `think big`, `pensar grande`, `future of`, `where is this going`, `opportunity scan`
- What it does: Strategic future scans with signals, scenarios, risks, and opportunities.
- Use when: The user wants to open the possibility space around a broad market, product, technology, society, career, company, or behavior theme.
- Output: Strategic exploration with framing, signals, scenarios, opportunities, risks, and useful provocations.
- Curated examples:
  - `/think-big future of AI-first CRMs`
  - `/think-big pensar grande sobre marketplaces de agentes`
  - `/think-big What happens to checkout experiences when agents buy for users?`

### whisper-transcribe

- Slash command: `/whisper-transcribe`
- Aliases: `transcribe`, `whisper`, `gera legenda`, `transcreve esse audio`
- What it does: Local faster-whisper transcription with modes, manifest, and txt/srt/vtt/md output.
- Use when: The user has a local media file and wants transcription, captions, subtitles, meeting text, or archive-ready transcript artifacts.
- Output: Saved transcript and caption artifacts plus a concise chat summary with mode, language, model, formats, output paths, manifest, and suggested next action.
- Curated examples:
  - `/whisper-transcribe /absolute/path/to/audio.mp3`
  - `/whisper-transcribe /absolute/path/to/video.mp4 --mode captions`
  - `/whisper-transcribe Transcreve esse audio em portugues e gera srt. /absolute/path/audio.m4a`

## Admin And Package Skills

### nanoskills

- Slash command: `/nanoskills`
- Aliases: `skills`, `lista skills`, `help skills`, `catalog`
- What it does: Package-level catalog and help for all Awesome NanoClaw Skills.
- Use when: The user wants to discover available skills, understand what each one does, or get help and examples for a specific skill.
- Output: Language-matched package catalog or skill-specific help.
- Curated examples:
  - `/nanoskills`
  - `/nanoskills help council`
  - `/nanoskills help think-big`

### awesome-updater

- Slash command: `/awesome-updater`
- Aliases: `updater`, `updates`, `auto-update`, `managed skills`
- What it does: Managed install, discovery, backup, rollback, and auto-update infrastructure.
- Use when: The user wants lifecycle operations rather than usage help.
- Output: Update, install, config, backup, rollback, or discovery status based on the updater JSON summary.
- Curated examples:
  - `/awesome-updater help`
  - `/nanoskills updates`
  - `/awesome-updater discover`
  - `/awesome-updater check nano-council`

## Catalog Grouping

Show these skills under `User-Facing Skills`:

- nano-council
- read-for-me
- rethink
- think-big
- whisper-transcribe

Show these skills under `Admin And Package Skills`:

- nanoskills
- awesome-updater

If this file is missing or stale in a NanoClaw container, `/nanoskills` may generate a read-only fallback from local `SKILL.md` files.
