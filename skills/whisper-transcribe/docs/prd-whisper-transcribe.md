# Whisper Transcribe PRD

## Summary

Whisper Transcribe is a NanoClaw skill that transcribes local audio and video files with `faster-whisper`, writes transcript artifacts as `txt`, `srt`, and/or `vtt`, and returns a concise chat summary with the detected or selected language and saved output paths.

The skill is local-first. It should not send media to an external transcription API. It should use a deterministic helper script for file handling and subtitle formatting, while `SKILL.md` stays focused on invocation, dependency checks, user communication, and workflow decisions.

## Problem

NanoClaw needs a repeatable way to transcribe local recordings from chat without requiring the user to remember Python snippets, subtitle formats, model options, or output path conventions. A generic agent can call `faster-whisper`, but it may produce inconsistent filenames, omit subtitles, fail to summarize saved outputs, or accidentally rely on cloud services.

## Users

- Fabio, using NanoClaw through chat to transcribe local recordings.
- NanoClaw operators who need a portable local transcription skill.
- Future agents that need transcript files as inputs for summaries, meeting notes, subtitles, or downstream analysis.

## Goals

1. Transcribe local audio and video files through `faster-whisper`.
2. Accept a user-provided language code or let `faster-whisper` detect the language.
3. Support `txt`, `srt`, and `vtt` outputs, including multiple formats in one run.
4. Save outputs next to the source file by default when that location is writable.
5. Save outputs under a workspace transcript folder when requested or when the source directory is not writable.
6. Return a concise chat summary with source file, model, language, duration, formats, output paths, and any warnings.
7. Fail with actionable dependency and file errors.
8. Keep the skill portable and inspectable: Markdown instructions plus a small Python helper and deterministic tests.

## Non-Goals

- No remote URL download in the first version.
- No cloud transcription APIs.
- No speaker diarization or speaker labels.
- No translation workflow by default.
- No subtitle editing UI.
- No automatic long-term memory save.
- No browser or HTML report requirement.
- No automatic dependency installation unless the user explicitly approves it.

## Runtime Model

The implemented skill should use:

- `SKILL.md` for trigger rules, NanoClaw workflow, dependency checks, and user-facing summary rules.
- `scripts/whisper_transcribe.py` for deterministic local transcription and output writing.
- `tests/test_whisper_transcribe.py` for formatter, format parsing, and path resolution tests that do not require downloading a Whisper model.
- `scripts/validate-whisper-transcribe.sh` for syntax and unit-test validation.

The helper script should print a single JSON summary to stdout so the agent can produce a short chat response without scraping human-oriented terminal logs.

## Invocation

The skill should trigger when the user asks to transcribe, caption, subtitle, or convert speech to text from a local audio or video file, including examples like:

- `transcribe /path/to/file.mp3`
- `transcreve esse audio`
- `make subtitles for ./meeting.mp4`
- `gera srt e vtt desse video`
- `whisper this file in Portuguese`

If the request does not identify a local path and no file attachment/path is available in context, the skill should ask one short clarification for the file path.

## Source File Requirements

The source must be a local file path visible to the agent. Supported extensions should not be hard-coded too narrowly because PyAV/faster-whisper can decode many media containers. The skill should still reject paths that do not exist or point to directories.

The script should pass the source path directly to `faster-whisper`. Per the upstream project, audio decoding is handled by PyAV, which bundles FFmpeg libraries in its package.

## Output Destination

Default behavior:

1. If the source directory is writable, save outputs next to the source file.
2. If the source directory is not writable, save under the workspace transcript folder.

Workspace output behavior:

1. If `/workspace/group/transcripts` exists or can be created, use it.
2. Otherwise use `./transcripts` from the current working directory.
3. Create one child directory per run using `<safe-source-stem>-<YYYYMMDD-HHMMSS>`.

Explicit output behavior:

- If the user provides an output directory, save all requested formats there.
- If multiple source files are supported later, each source should get a separate child directory to avoid filename collisions. Multi-file support is out of scope for the first version.

## Output Formats

The helper must support:

- `txt`: plain transcript text, one segment per line.
- `srt`: numbered subtitle blocks with comma millisecond timestamps.
- `vtt`: `WEBVTT` header and subtitle blocks with dot millisecond timestamps.

Default format should be `txt`. If the user asks for subtitles, default to `srt` and `vtt`. If the user asks for "all formats", write all three.

## Language Handling

If the user provides a language, pass it as a Whisper language code through `language=<code>`. If no language is provided, let `faster-whisper` detect it and report `info.language` and `info.language_probability` in the JSON summary.

The chat summary should distinguish:

- `language: auto-detected pt (0.97)`
- `language: user-specified en`

The first version should not convert natural-language language names into codes unless the mapping is obvious from the user request, such as Portuguese to `pt`, English to `en`, Spanish to `es`, French to `fr`, or Italian to `it`.

## Model And Performance Defaults

Default model should be `small`, overridable by user request or `WHISPER_MODEL`.

Default device should be `auto`:

- Use CUDA when available.
- Otherwise use CPU.

Default compute type should be `auto`:

- `float16` on CUDA.
- `int8` on CPU.

The chat summary should include model, device, and compute type because these explain speed and quality tradeoffs.

## Functional Requirements

### FR1: Triggering

The skill must trigger for local transcription, subtitle, and speech-to-text requests.

### FR2: Local Path Validation

The skill must verify that the source path exists and is a file before transcription starts.

### FR3: Dependency Check

If `faster-whisper` is unavailable, the skill must fail with a concise install command and must not pretend transcription completed.

### FR4: Language

The skill must accept a language code when provided and must otherwise rely on automatic detection.

### FR5: Format Selection

The skill must write `txt`, `srt`, and/or `vtt` according to the user request. Unknown formats must fail before model loading.

### FR6: Output Path Selection

The skill must save next to the source file by default when possible, and must support a workspace output directory mode.

### FR7: Subtitle Timestamp Formatting

The script must format SRT timestamps as `HH:MM:SS,mmm` and VTT timestamps as `HH:MM:SS.mmm`.

### FR8: JSON Summary

The script must print JSON with at least: source path, output paths, formats, language, language probability, model, device, compute type, duration seconds, segment count, and warnings.

### FR9: Chat Summary

The agent must return a concise Markdown summary, not the full transcript, unless the user explicitly asks for transcript text in chat.

### FR10: No Hidden Cloud Dependency

The skill must not use remote transcription APIs. Model downloads from the model provider are acceptable only as normal `faster-whisper` model loading behavior and should be mentioned if a model is not cached.

## Acceptance Criteria

- `skills/whisper-transcribe/SKILL.md` exists and declares `name: whisper-transcribe`.
- `SKILL.md` instructs the agent to use `scripts/whisper_transcribe.py`.
- `scripts/whisper_transcribe.py` accepts a local source path and supports `--formats txt`, `--formats srt`, `--formats vtt`, and `--formats all`.
- The script supports optional `--language`.
- The script supports explicit `--output-dir` and `--workspace-output`.
- The script writes selected outputs and prints a JSON summary.
- SRT and VTT timestamp formatting is covered by tests.
- Format parsing and output destination behavior are covered by tests.
- `scripts/validate-whisper-transcribe.sh` runs syntax and unit tests.
- The skill returns a concise chat summary with saved paths.
- No implementation file requires a browser, HTML report, or external transcription API.

## Risks

- First-run model download can be slow or blocked by network policy. Mitigation: surface the model name and explain that cached local models avoid repeated downloads.
- CPU transcription can be slow for long videos. Mitigation: expose model, device, and compute options and default to `small` for a practical quality/speed balance.
- Subtitle text can be too long per cue. Mitigation: start with segment-level subtitles and leave line wrapping as a later improvement.
- Language names can be ambiguous. Mitigation: accept explicit Whisper language codes and only map obvious language names.
- Video containers can expose decoding edge cases. Mitigation: rely on PyAV/faster-whisper and report the underlying error without inventing a transcript.

## Open Questions

1. Should workspace output always be preferred inside NanoClaw containers, even when the source directory is writable?
2. Should the first implementation support batch transcription for multiple files, or keep v1 strictly single-file?
3. Should "subtitles" default to both `srt` and `vtt`, or only `srt`?
4. Should the skill support `task=translate` later as a separate explicit mode?

## External References

- SYSTRAN `faster-whisper` README: https://github.com/SYSTRAN/faster-whisper
- `WhisperModel.transcribe` source: https://github.com/SYSTRAN/faster-whisper/blob/master/faster_whisper/transcribe.py
