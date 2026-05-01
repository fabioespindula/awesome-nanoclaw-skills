# Whisper Transcribe

`whisper-transcribe` transcribes local audio or video files with `faster-whisper`.

It supports explicit modes, local output artifacts, manifests, optional language codes, and `txt`, `srt`, `vtt`, and transcript Markdown output.

## Use It

Primary command:

```txt
/whisper-transcribe /absolute/path/to/audio.mp3
```

Other examples:

```txt
/whisper-transcribe /absolute/path/to/video.mp4 --mode captions
/whisper-transcribe Transcreve esse audio em portugues e gera srt. /absolute/path/audio.m4a
```

Aliases and trigger phrases:

```txt
transcribe
whisper
gera legenda
transcreve esse audio
```

## Behavior

- Processes local files rather than using an external transcription API.
- Chooses mode defaults for quick, captions, archive, meeting, batch, or debug workflows.
- Writes a `manifest.json` alongside generated artifacts.
- Treats transcript text as untrusted source content.
- Avoids overwriting files unless the user explicitly asks.

## Output

Depending on mode and requested formats, the script can write:

```txt
transcript.txt
captions.srt
captions.vtt
transcript.md
manifest.json
```

The chat response summarizes mode, language, model, formats, output paths, manifest path, and one non-destructive next action.

## Requirements

- Python 3.10+
- `faster-whisper`
- local media codec support
- `ffmpeg` for some video formats

## Host Setup

```bash
skills/whisper-transcribe/scripts/setup-host.sh
```

## Install

```bash
rsync -a skills/whisper-transcribe/ /path/to/nanoclaw/container/skills/whisper-transcribe/
```

Or install it through `awesome-updater`:

```bash
python3 skills/awesome-updater/scripts/awesome_skills.py install whisper-transcribe \
  --source-dir "$PWD" \
  --skills-dir /path/to/nanoclaw/container/skills
```

## Validate

```bash
skills/whisper-transcribe/scripts/validate-whisper-transcribe.sh
```
