# Whisper Transcribe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a NanoClaw skill that transcribes local audio/video files with `faster-whisper`, writes `txt`, `srt`, and/or `vtt` files, and returns a concise chat summary.

**Architecture:** The skill is a thin Markdown orchestration layer around one deterministic Python helper. `SKILL.md` handles trigger rules, dependency behavior, user-facing summaries, and when to choose source-adjacent versus workspace output. `scripts/whisper_transcribe.py` owns transcription, subtitle formatting, output paths, and JSON reporting; tests cover deterministic formatting and path logic without requiring a model download.

**Tech Stack:** NanoClaw skill Markdown, Python 3.9+, `faster-whisper`, CTranslate2, PyAV, shell validation, `unittest`.

---

## File Structure

- Create: `skills/whisper-transcribe/SKILL.md` - skill metadata, triggers, workflow, output rules.
- Create: `skills/whisper-transcribe/scripts/whisper_transcribe.py` - deterministic local transcription CLI.
- Create: `skills/whisper-transcribe/scripts/validate-whisper-transcribe.sh` - syntax and unit-test validation.
- Create: `skills/whisper-transcribe/tests/test_whisper_transcribe.py` - deterministic tests for parsing, timestamps, and output destinations.
- Modify: `README.md` - move `whisper-transcribe` from Roadmap to Available Skills after implementation.

### Task 1: Add Skill Skeleton

**Files:**
- Create: `skills/whisper-transcribe/SKILL.md`

- [ ] **Step 1: Create implementation directories**

Run:

```bash
mkdir -p skills/whisper-transcribe/scripts skills/whisper-transcribe/tests
```

Expected: command exits 0.

- [ ] **Step 2: Create the root skill file**

Create `skills/whisper-transcribe/SKILL.md` with:

```markdown
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
- Do not use cloud transcription APIs.
- Do not require a browser or HTML report.
```

- [ ] **Step 3: Validate skill metadata**

Run:

```bash
rg -n "name: whisper-transcribe|faster-whisper|txt-srt-vtt|workspace-output" skills/whisper-transcribe/SKILL.md
```

Expected: all four strings are found.

### Task 2: Add The Transcription Helper

**Files:**
- Create: `skills/whisper-transcribe/scripts/whisper_transcribe.py`

- [ ] **Step 1: Create the helper script**

Create `skills/whisper-transcribe/scripts/whisper_transcribe.py` with:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


SUPPORTED_FORMATS = {"txt", "srt", "vtt"}
DEFAULT_WORKSPACE_OUTPUT = Path("/workspace/group/transcripts")


@dataclass(frozen=True)
class Segment:
    index: int
    start: float
    end: float
    text: str


def safe_stem(path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", path.stem.strip())
    return stem.strip("-._") or "transcript"


def parse_formats(raw: str) -> list[str]:
    values = [part.strip().lower() for part in raw.split(",") if part.strip()]
    if not values:
        raise ValueError("at least one output format is required")
    if "all" in values:
        return ["txt", "srt", "vtt"]
    unknown = sorted(set(values) - SUPPORTED_FORMATS)
    if unknown:
        raise ValueError(f"unsupported output format: {', '.join(unknown)}")
    return list(dict.fromkeys(values))


def format_timestamp(seconds: float, separator: str) -> str:
    milliseconds = int(round(max(seconds, 0.0) * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"


def write_txt(path: Path, segments: Iterable[Segment]) -> None:
    path.write_text(
        "\n".join(segment.text.strip() for segment in segments if segment.text.strip()) + "\n",
        encoding="utf-8",
    )


def write_srt(path: Path, segments: Iterable[Segment]) -> None:
    blocks = []
    for segment in segments:
        blocks.append(
            "\n".join(
                [
                    str(segment.index),
                    f"{format_timestamp(segment.start, ',')} --> {format_timestamp(segment.end, ',')}",
                    segment.text.strip(),
                ]
            )
        )
    path.write_text("\n\n".join(blocks).strip() + "\n", encoding="utf-8")


def write_vtt(path: Path, segments: Iterable[Segment]) -> None:
    blocks = ["WEBVTT"]
    for segment in segments:
        blocks.append(
            "\n".join(
                [
                    f"{format_timestamp(segment.start, '.')} --> {format_timestamp(segment.end, '.')}",
                    segment.text.strip(),
                ]
            )
        )
    path.write_text("\n\n".join(blocks).strip() + "\n", encoding="utf-8")


def source_parent_is_writable(source: Path) -> bool:
    parent = source.parent if source.parent != Path("") else Path.cwd()
    return parent.exists() and os.access(parent, os.W_OK)


def resolve_output_dir(source: Path, output_dir: str | None, workspace_output: bool) -> Path:
    if output_dir:
        return Path(output_dir).expanduser().resolve()

    if workspace_output or not source_parent_is_writable(source):
        base = DEFAULT_WORKSPACE_OUTPUT
        if not base.exists():
            base = Path.cwd() / "transcripts"
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return (base / f"{safe_stem(source)}-{timestamp}").resolve()

    return source.parent.resolve()


def infer_device(requested: str) -> str:
    if requested != "auto":
        return requested
    try:
        import ctranslate2

        return "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
    except Exception:
        return "cpu"


def infer_compute_type(requested: str, device: str) -> str:
    if requested != "auto":
        return requested
    return "float16" if device == "cuda" else "int8"


def load_faster_whisper():
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper is not installed. Install it with: python3 -m pip install faster-whisper"
        ) from exc
    return WhisperModel


def transcribe(args: argparse.Namespace) -> dict:
    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"source file not found: {source}")
    if not source.is_file():
        raise ValueError(f"source path is not a file: {source}")

    formats = parse_formats(args.formats)
    output_dir = resolve_output_dir(source, args.output_dir, args.workspace_output)
    output_dir.mkdir(parents=True, exist_ok=True)

    device = infer_device(args.device)
    compute_type = infer_compute_type(args.compute_type, device)
    model_name = args.model or os.environ.get("WHISPER_MODEL", "small")

    WhisperModel = load_faster_whisper()
    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    generated_segments, info = model.transcribe(
        str(source),
        language=args.language,
        beam_size=args.beam_size,
        vad_filter=not args.no_vad,
        task="transcribe",
    )
    segments = [
        Segment(index=index, start=item.start, end=item.end, text=item.text)
        for index, item in enumerate(generated_segments, start=1)
    ]

    writers = {"txt": write_txt, "srt": write_srt, "vtt": write_vtt}
    outputs: dict[str, str] = {}
    for fmt in formats:
        target = output_dir / f"{safe_stem(source)}.{fmt}"
        writers[fmt](target, segments)
        outputs[fmt] = str(target)

    language_probability = getattr(info, "language_probability", None)
    return {
        "source": str(source),
        "outputs": outputs,
        "formats": formats,
        "language": getattr(info, "language", args.language),
        "language_probability": language_probability,
        "language_mode": "user-specified" if args.language else "auto-detected",
        "model": model_name,
        "device": device,
        "compute_type": compute_type,
        "duration_seconds": getattr(info, "duration", None),
        "segment_count": len(segments),
        "warnings": [],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transcribe a local audio/video file with faster-whisper.")
    parser.add_argument("source", help="Local audio or video file path.")
    parser.add_argument("--formats", default="txt", help="Comma-separated output formats: txt,srt,vtt,all.")
    parser.add_argument("--language", help="Optional Whisper language code such as pt, en, es, fr, or it.")
    parser.add_argument("--output-dir", help="Directory for output files.")
    parser.add_argument("--workspace-output", action="store_true", help="Write under the workspace transcript folder.")
    parser.add_argument("--model", default=os.environ.get("WHISPER_MODEL", "small"), help="faster-whisper model name.")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"], help="Inference device.")
    parser.add_argument("--compute-type", default="auto", help="CTranslate2 compute type, or auto.")
    parser.add_argument("--beam-size", type=int, default=5, help="Beam size for transcription.")
    parser.add_argument("--no-vad", action="store_true", help="Disable VAD filtering.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        summary = transcribe(args)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, **summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Make the helper executable**

Run:

```bash
chmod +x skills/whisper-transcribe/scripts/whisper_transcribe.py
```

Expected: command exits 0.

- [ ] **Step 3: Verify syntax**

Run:

```bash
python3 -m py_compile skills/whisper-transcribe/scripts/whisper_transcribe.py
```

Expected: command exits 0.

### Task 3: Add Deterministic Unit Tests

**Files:**
- Create: `skills/whisper-transcribe/tests/test_whisper_transcribe.py`

- [ ] **Step 1: Create unit tests**

Create `skills/whisper-transcribe/tests/test_whisper_transcribe.py` with:

```python
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "whisper_transcribe.py"
SPEC = importlib.util.spec_from_file_location("whisper_transcribe", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class WhisperTranscribeTests(unittest.TestCase):
    def test_parse_formats_supports_all(self) -> None:
        self.assertEqual(MODULE.parse_formats("all"), ["txt", "srt", "vtt"])

    def test_parse_formats_deduplicates_and_preserves_order(self) -> None:
        self.assertEqual(MODULE.parse_formats("vtt,txt,vtt"), ["vtt", "txt"])

    def test_parse_formats_rejects_unknown_format(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported output format"):
            MODULE.parse_formats("txt,pdf")

    def test_srt_timestamp_uses_comma_milliseconds(self) -> None:
        self.assertEqual(MODULE.format_timestamp(3661.234, ","), "01:01:01,234")

    def test_vtt_timestamp_uses_dot_milliseconds(self) -> None:
        self.assertEqual(MODULE.format_timestamp(61.2, "."), "00:01:01.200")

    def test_safe_stem_removes_unsafe_characters(self) -> None:
        self.assertEqual(MODULE.safe_stem(Path("My Recording 01!.mp4")), "My-Recording-01")

    def test_explicit_output_dir_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "meeting.mp3"
            source.write_bytes(b"")
            target = MODULE.resolve_output_dir(source, str(Path(tmp) / "out"), False)
            self.assertEqual(target, (Path(tmp) / "out").resolve())

    def test_workspace_output_creates_named_child_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "meeting audio.mp3"
            source.write_bytes(b"")
            cwd = Path.cwd()
            original_workspace = MODULE.DEFAULT_WORKSPACE_OUTPUT
            try:
                MODULE.DEFAULT_WORKSPACE_OUTPUT = Path(tmp) / "not-created-workspace-root"
                os.chdir(tmp)
                target = MODULE.resolve_output_dir(source, None, True)
            finally:
                os.chdir(cwd)
                MODULE.DEFAULT_WORKSPACE_OUTPUT = original_workspace
            self.assertEqual(target.parent, (Path(tmp) / "transcripts").resolve())
            self.assertRegex(target.name, r"meeting-audio-\d{8}-\d{6}")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run unit tests**

Run:

```bash
python3 -m unittest skills/whisper-transcribe/tests/test_whisper_transcribe.py
```

Expected: all tests pass without requiring `faster-whisper` to be installed.

### Task 4: Add Validation Script

**Files:**
- Create: `skills/whisper-transcribe/scripts/validate-whisper-transcribe.sh`

- [ ] **Step 1: Create validation script**

Create `skills/whisper-transcribe/scripts/validate-whisper-transcribe.sh` with:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m py_compile "$ROOT/scripts/whisper_transcribe.py"
python3 -m unittest "$ROOT/tests/test_whisper_transcribe.py"

echo "whisper-transcribe validation passed"
```

- [ ] **Step 2: Make validation script executable**

Run:

```bash
chmod +x skills/whisper-transcribe/scripts/validate-whisper-transcribe.sh
```

Expected: command exits 0.

- [ ] **Step 3: Run validation**

Run:

```bash
skills/whisper-transcribe/scripts/validate-whisper-transcribe.sh
```

Expected:

```text
whisper-transcribe validation passed
```

### Task 5: Verify The Runtime Path With A Real Media File

**Files:**
- No file changes.

- [ ] **Step 1: Confirm dependency availability**

Run:

```bash
python3 -c "import faster_whisper; print(faster_whisper.__version__)"
```

Expected: prints the installed package version. If it fails, ask the user before installing:

```bash
python3 -m pip install faster-whisper
```

- [ ] **Step 2: Run a manual transcription smoke test**

Use a known local media file from the user's workspace:

```bash
python3 skills/whisper-transcribe/scripts/whisper_transcribe.py "/absolute/path/to/local-media-file.mp3" --model tiny --formats all --workspace-output > /tmp/whisper-transcribe-summary.json
```

Expected: `/tmp/whisper-transcribe-summary.json` is JSON with `"ok": true`, `outputs.txt`, `outputs.srt`, `outputs.vtt`, a language code, duration, and segment count.

- [ ] **Step 3: Inspect generated outputs**

Run:

```bash
python3 -m json.tool /tmp/whisper-transcribe-summary.json
```

Expected fields:

```json
{
  "ok": true,
  "source": "/absolute/path/to/local-media-file.mp3",
  "outputs": {
    "txt": "...",
    "srt": "...",
    "vtt": "..."
  },
  "language_mode": "auto-detected"
}
```

### Task 6: Update Repository Index

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Move the skill to Available Skills**

In `README.md`, add this row under Available Skills:

```markdown
| `whisper-transcribe` | alpha | Local audio/video transcription with faster-whisper and txt/srt/vtt output. |
```

- [ ] **Step 2: Remove the roadmap duplicate**

Remove this row from Roadmap:

```markdown
| `whisper-transcribe` | Runs local audio transcription with faster-whisper. |
```

- [ ] **Step 3: Verify README mentions the skill once in each intended context**

Run:

```bash
rg -n "whisper-transcribe" README.md
```

Expected: one Available Skills row and no Roadmap row for `whisper-transcribe`.

### Task 7: Final Verification

**Files:**
- No file changes.

- [ ] **Step 1: Run validation script**

Run:

```bash
skills/whisper-transcribe/scripts/validate-whisper-transcribe.sh
```

Expected:

```text
whisper-transcribe validation passed
```

- [ ] **Step 2: Check implementation file list**

Run:

```bash
find skills/whisper-transcribe -maxdepth 3 -type f | sort
```

Expected:

```text
skills/whisper-transcribe/SKILL.md
skills/whisper-transcribe/docs/prd-whisper-transcribe.md
skills/whisper-transcribe/docs/superpowers/plans/2026-04-29-whisper-transcribe.md
skills/whisper-transcribe/scripts/validate-whisper-transcribe.sh
skills/whisper-transcribe/scripts/whisper_transcribe.py
skills/whisper-transcribe/tests/test_whisper_transcribe.py
```

- [ ] **Step 3: Confirm no accidental browser or cloud dependency**

Run:

```bash
! rg -n "open |report\\.html|OpenAI|AssemblyAI|Deepgram|cloud transcription|http" skills/whisper-transcribe/SKILL.md skills/whisper-transcribe/scripts skills/whisper-transcribe/tests
```

Expected: command exits 0.

## Self-Review Checklist

- The PRD goals map to concrete tasks: local transcription, language, formats, output destination, concise summary, dependency handling, validation.
- No implementation files are created during the PRD-only phase.
- The future implementation has deterministic tests that do not require a model download.
- The manual smoke test is separated from unit validation because it may need a cached or downloaded model.
