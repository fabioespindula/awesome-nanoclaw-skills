# NanoSkills Catalog

This file is the package-level source for `/nanoskills` catalog and help responses.

Answer in the language of the current conversation. Keep skill names and slash commands literal.

## User-Facing Skills

### nano-council

- Slash command: `/council`
- Aliases: `council`, `conselho`, `pressure-test`, `testa essa decisao`
- What it does: runs a five-advisor council for divergent decision review, planning pressure tests, option comparison, and blind-spot analysis.
- Use when: the user wants disagreement, a decision pressure test, a plan review, or a sharper recommendation before acting.
- Output: Telegram-friendly Markdown with recommendation, agreement, disagreement, blind spots, advisor snapshots, and next action.
- Curated examples:
  - `/council Should we ship the first version this week or wait until onboarding is better?`
  - `/council Quero decidir se faco launch agora ou espero melhorar onboarding.`
  - `/council Pressure-test this architecture before we build it.`

### read-for-me

- Slash command: `/read-for-me`
- Aliases: `read`, `summarize this`, `read this`, `analisa esse link`, bare URLs
- What it does: turns one or more URLs into concise, sourced, context-aware briefs with access level, confidence, relevance, category, and one non-destructive next action.
- Use when: the user sends links, asks what a link says, asks whether a source matters, or wants a quick decision-ready summary.
- Output: link brief with title/source/date when available, summary bullets, confidence, relevance score, categories, and next action.
- Curated examples:
  - `/read-for-me https://example.com/article`
  - `Read this and tell me whether it matters for our launch plan: https://example.com/post`
  - `/read-for-me Analisa esse link e me diz o que muda para o projeto. https://example.com`

### rethink

- Slash command: `/rethink`
- Aliases: `rethink`, `step back`, `gut-check`, `pressure-test`, `simplify this`, `decide`
- What it does: reframes a concrete plan, idea, or decision before commitment.
- Use when: the user has a specific decision, product idea, architecture plan, career/life choice, or company direction and wants better decision quality.
- Output: concise decision review with real question, assumptions, alternatives, risks, recommendation, and next move.
- Curated examples:
  - `/rethink Should I build the global skill catalog as a separate skill or inside the updater?`
  - `/rethink Esse plano de launch esta grande demais para a primeira versao?`
  - `/rethink Help me decide between hiring now or keeping the team small.`

### think-big

- Slash command: `/think-big`
- Aliases: `think big`, `pensar grande`, `future of`, `where is this going`, `opportunity scan`
- What it does: explores broad themes through signals, mechanisms, scenarios, contrarian takes, second-order effects, and opportunities.
- Use when: the user wants to open the possibility space around a broad market, product, technology, society, career, company, or behavior theme.
- Output: strategic exploration with framing, signals, scenarios, opportunities, risks, and useful provocations.
- Curated examples:
  - `/think-big future of AI-first CRMs`
  - `/think-big pensar grande sobre marketplaces de agentes`
  - `/think-big What happens to checkout experiences when agents buy for users?`

### whisper-transcribe

- Slash command: `/whisper-transcribe`
- Aliases: `transcribe`, `whisper`, `gera legenda`, `transcreve esse audio`
- What it does: transcribes local audio/video files with `faster-whisper`, with txt/srt/vtt/transcript-md output and manifest metadata.
- Use when: the user has a local media file and wants transcription, captions, subtitles, meeting text, or archive-ready transcript artifacts.
- Output: saved transcript/caption artifacts plus a concise chat summary with mode, language, model, formats, output paths, manifest, and suggested next action.
- Curated examples:
  - `/whisper-transcribe /absolute/path/to/audio.mp3`
  - `/whisper-transcribe /absolute/path/to/video.mp4 --mode captions`
  - `/whisper-transcribe Transcreve esse audio em portugues e gera srt. /absolute/path/audio.m4a`

## Admin And Package Skills

### nanoskills

- Slash command: `/nanoskills`
- Aliases: `skills`, `lista skills`, `help skills`, `catalog`
- What it does: lists and explains every skill in the Awesome NanoClaw Skills package.
- Use when: the user wants to discover available skills, understand what each one does, or get help and examples for a specific skill.
- Output: language-matched package catalog or skill-specific help.
- Curated examples:
  - `/nanoskills`
  - `/nanoskills help council`
  - `/nanoskills help think-big`

### awesome-updater

- Slash command: `/awesome-updater`
- Aliases: `updater`, `updates`, `auto-update`, `managed skills`
- What it does: installs, discovers, configures, checks, backs up, rolls forward, and auto-updates managed Awesome NanoClaw Skills.
- Use when: the user wants lifecycle operations rather than usage help.
- Output: update/install/config status, usually based on the JSON summary returned by the updater script.
- Curated examples:
  - `/awesome-updater help`
  - `/nanoskills updates`
  - `/awesome-updater discover`
  - `/awesome-updater check nano-council`

## Catalog Grouping

Show these skills under `User-facing skills`:

- nano-council
- read-for-me
- rethink
- think-big
- whisper-transcribe

Show these under `Admin and package skills`:

- nanoskills
- awesome-updater

If a future skill is added and this file has not been updated, say the catalog may be outdated and suggest checking the repository's `skills/` folder.
