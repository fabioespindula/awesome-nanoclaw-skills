---
name: whisper-transcribe
description: Use when the user wants to transcribe, caption, subtitle, or convert speech to text from a local audio or video file using faster-whisper. Supports txt, srt, and vtt output, optional language codes, local workspace output, and concise chat summaries.
user-invocable: true
metadata:
  output: txt-srt-vtt
  engine: faster-whisper
---

# Whisper Transcribe

Use this skill to transcribe local audio or video files with `faster-whisper`.

## Triggers

Run this skill when the user asks to:

- transcribe a local audio or video file
- create captions or subtitles from a local file
- create `txt`, `srt`, or `vtt` transcript output
- convert a local recording to text
- "transcreve esse audio", "gera legenda", or equivalent Portuguese intent

If the user does not provide a local file path and no attached file path is available in the conversation, ask one short question for the path.

## Workflow

1. Identify exactly one local source file path.
2. Decide output formats:
   - default to `txt`
   - use `srt,vtt` when the user asks for subtitles or captions
   - use `all` when the user asks for all transcript formats
3. Decide language:
   - pass `--language <code>` when the user gives a clear Whisper language code
   - map obvious language names only: Portuguese `pt`, English `en`, Spanish `es`, French `fr`, Italian `it`
   - omit `--language` when the user wants auto-detection or does not specify a language
4. Decide destination:
   - default: next to the source file
   - use `--workspace-output` when the user asks for workspace output or when source-adjacent output is not appropriate
   - use `--output-dir <path>` when the user provides an explicit output folder
5. Run `scripts/whisper_transcribe.py` from this skill directory.
6. Read the JSON summary printed to stdout.
7. Reply with a concise Markdown summary containing source, detected or selected language, model, formats, output paths, and warnings.

## Command Pattern

From `skills/whisper-transcribe`:

```bash
python3 scripts/whisper_transcribe.py "/absolute/path/to/media.mp4" --formats txt,srt,vtt
```

With language and workspace output:

```bash
python3 scripts/whisper_transcribe.py "/absolute/path/to/media.mp4" --language pt --formats all --workspace-output
```

## Dependency Behavior

If `faster-whisper` is missing, do not transcribe. Tell the user:

```bash
python3 -m pip install faster-whisper
```

Do not install dependencies without explicit approval.

## Output Rules

- Do not paste the full transcript in chat unless the user explicitly asks.
- Include all saved output paths.
- Include language as either `auto-detected <code> (<probability>)` or `user-specified <code>`.
- Include duration and segment count when available.
- Mention that first run may download the selected model if the JSON summary includes a model-cache warning or model loading error.
- Use only local transcription through `faster-whisper`.
- Do not require a browser or HTML report.
