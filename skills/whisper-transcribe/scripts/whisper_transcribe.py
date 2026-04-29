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

    unknown = sorted(set(values) - SUPPORTED_FORMATS - {"all"})
    if unknown:
        raise ValueError(f"unsupported output format: {', '.join(unknown)}")

    if "all" in values:
        return ["txt", "srt", "vtt"]
    return list(dict.fromkeys(values))


def format_timestamp(seconds: float, separator: str) -> str:
    milliseconds = int(round(max(seconds, 0.0) * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"


def write_txt(path: Path, segments: Iterable[Segment]) -> None:
    lines = [segment.text.strip() for segment in segments if segment.text.strip()]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


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
    path.write_text("\n\n".join(blocks).strip() + ("\n" if blocks else ""), encoding="utf-8")


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


def workspace_base() -> Path:
    if DEFAULT_WORKSPACE_OUTPUT.exists() or DEFAULT_WORKSPACE_OUTPUT.parent.exists():
        return DEFAULT_WORKSPACE_OUTPUT
    return Path.cwd() / "transcripts"


def resolve_output_dir(source: Path, output_dir: str | None, workspace_output: bool) -> Path:
    if output_dir:
        return Path(output_dir).expanduser().resolve()

    if workspace_output or not source_parent_is_writable(source):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return (workspace_base() / f"{safe_stem(source)}-{timestamp}").resolve()

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

    return {
        "source": str(source),
        "outputs": outputs,
        "formats": formats,
        "language": getattr(info, "language", args.language),
        "language_probability": getattr(info, "language_probability", None),
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
