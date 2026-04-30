#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.metadata as importlib_metadata
import json
import os
import platform
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable


SUPPORTED_FORMATS = {"txt", "srt", "vtt", "transcript-md"}
ALL_FORMATS = ["txt", "srt", "vtt", "transcript-md"]
SUPPORTED_MODES = {"quick", "captions", "archive", "meeting", "batch", "debug"}
SKILL_NAME = "whisper-transcribe"
REQUIRED_FASTER_WHISPER_VERSION = "1.2.1"
REQUIRED_CTRANSLATE2_VERSION = "4.7.1"
DEFAULT_MODEL = "small"
DEFAULT_CONTAINER_HF_HOME = Path("/workspace/.cache/huggingface")
EXIT_READY = 0
EXIT_WARNING = 1
EXIT_MISSING_REQUIRED = 2
EXIT_INVALID_CONFIG = 3
EXIT_HOST_SETUP_REQUIRED = 4
EXIT_MODEL_CACHE_FAILURE = 5
MODEL_FREE_SPACE_GB = {
    "tiny": 1.0,
    "base": 1.0,
    "small": 2.0,
    "medium": 4.0,
    "large-v2": 8.0,
    "large-v3": 8.0,
    "turbo": 4.0,
    "distil-large-v3": 5.0,
}
ERROR_GUIDE = {
    "missing-faster-whisper": {
        "cause": "The faster-whisper Python package is not installed in this runtime.",
        "next_command": "bash scripts/setup-host.sh --check /path/to/nanoclaw",
    },
    "wrong-python-package-version": {
        "cause": "The installed faster-whisper or ctranslate2 version does not match the pinned skill runtime.",
        "next_command": "bash scripts/setup-host.sh --apply /path/to/nanoclaw",
    },
    "missing-ffmpeg": {
        "cause": "ffmpeg or ffprobe is missing from the NanoClaw image.",
        "next_command": "bash scripts/setup-host.sh --apply /path/to/nanoclaw",
    },
    "unwritable-hf-home": {
        "cause": "HF_HOME is missing, not a directory, or not writable by the effective container user.",
        "next_command": "Fix the cache bind mount or run bash scripts/setup-host.sh --apply /path/to/nanoclaw",
    },
    "insufficient-disk": {
        "cause": "The selected model needs more free cache disk than is currently available.",
        "next_command": "Free disk in the Whisper cache path or choose a smaller --model.",
    },
    "huggingface-network": {
        "cause": "The runtime could not reach Hugging Face because of DNS, timeout, or network policy.",
        "next_command": "Retry bash scripts/setup-host.sh --warm-cache /path/to/nanoclaw <model>",
    },
    "model-unavailable": {
        "cause": "The selected model is unavailable locally and could not be downloaded.",
        "next_command": "Check the model name or warm the cache with a known model such as small.",
    },
    "media-decode-failure": {
        "cause": "The media file could not be decoded by the runtime.",
        "next_command": "Run doctor, confirm ffmpeg is installed, or convert the media to mp3/mp4.",
    },
    "output-exists": {
        "cause": "A transcript output path already exists and --overwrite was not requested.",
        "next_command": "Choose a new output folder or rerun with --overwrite.",
    },
    "output-permission-denied": {
        "cause": "The runtime cannot write transcript artifacts to the target directory.",
        "next_command": "Use --workspace-output or choose a writable --output-dir.",
    },
    "unsupported-gpu": {
        "cause": "CUDA/GPU was requested but is unavailable or unsupported in this runtime.",
        "next_command": "Use --device cpu or rebuild the runtime with compatible CUDA libraries.",
    },
}
MODE_DEFAULT_FORMATS = {
    "quick": ["txt"],
    "captions": ["srt", "vtt"],
    "archive": ALL_FORMATS,
    "meeting": ["txt", "transcript-md"],
    "batch": ["txt"],
    "debug": ["txt", "transcript-md"],
}
DEFAULT_WORKSPACE_OUTPUT = Path("/workspace/group/transcripts")


@dataclass(frozen=True)
class Word:
    start: float
    end: float
    word: str
    probability: float | None = None


@dataclass(frozen=True)
class Segment:
    index: int
    start: float
    end: float
    text: str
    words: list[Word] = field(default_factory=list)


def package_version(package: str) -> str | None:
    try:
        return importlib_metadata.version(package)
    except importlib_metadata.PackageNotFoundError:
        return None


def command_available(name: str) -> bool:
    return shutil.which(name) is not None


def is_container_runtime() -> bool:
    if Path("/.dockerenv").exists():
        return True
    try:
        cgroup = Path("/proc/1/cgroup").read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return any(marker in cgroup for marker in ("docker", "containerd", "kubepods", "podman"))


def validate_host_manifest(data: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest must be a JSON object"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("runtime") != "nanoclaw":
        errors.append("runtime must be nanoclaw")
    for key in ("compose_file", "service", "dockerfile", "skills_dir"):
        if not isinstance(data.get(key), str) or not data.get(key):
            errors.append(f"{key} must be a non-empty string")
    skills = data.get("skills")
    if not isinstance(skills, dict):
        errors.append("skills must be an object")
        return errors
    whisper = skills.get(SKILL_NAME)
    if not isinstance(whisper, dict):
        errors.append(f"skills.{SKILL_NAME} must be an object")
        return errors
    for key in ("host_cache_dir", "container_hf_home", "model"):
        if not isinstance(whisper.get(key), str) or not whisper.get(key):
            errors.append(f"skills.{SKILL_NAME}.{key} must be a non-empty string")
    return errors


def closest_existing_parent(path: Path) -> Path | None:
    current = path
    while not current.exists():
        if current.parent == current:
            return None
        current = current.parent
    return current if current.is_dir() else current.parent


def writable_directory(path: Path) -> tuple[bool, str | None]:
    if not path.exists():
        return False, "path does not exist"
    if not path.is_dir():
        return False, "path is not a directory"
    try:
        with tempfile.NamedTemporaryFile(prefix=".whisper-doctor-", dir=path):
            pass
    except OSError as exc:
        return False, str(exc)
    return True, None


def disk_free_gb(path: Path) -> float | None:
    target = closest_existing_parent(path)
    if target is None:
        return None
    try:
        usage = shutil.disk_usage(target)
    except OSError:
        return None
    return usage.free / (1024**3)


def model_required_space_gb(model: str) -> float:
    return MODEL_FREE_SPACE_GB.get(model, 8.0 if "large" in model else 4.0)


def issue(code: str, message: str) -> dict:
    guide = ERROR_GUIDE.get(code, {})
    return {
        "code": code,
        "message": message,
        "cause": guide.get("cause", message),
        "next_command": guide.get("next_command", "Run doctor after fixing the environment."),
    }


def doctor_exit_code(report: dict) -> int:
    issues = report["issues"]
    if not issues:
        return EXIT_WARNING if report["warnings"] else EXIT_READY
    model_cache_codes = {"insufficient-disk", "huggingface-network", "model-unavailable"}
    if any(item["code"] in model_cache_codes for item in issues):
        return EXIT_MODEL_CACHE_FAILURE
    if report["runtime"]["inside_container"]:
        return EXIT_HOST_SETUP_REQUIRED
    return EXIT_MISSING_REQUIRED


def run_doctor(args: argparse.Namespace) -> dict:
    model = args.model or os.environ.get("WHISPER_MODEL", DEFAULT_MODEL)
    inside_container = is_container_runtime()
    hf_home = Path(os.environ.get("HF_HOME", str(Path.home() / ".cache" / "huggingface"))).expanduser()
    requested_device = getattr(args, "device", "auto")
    checks: list[dict] = []
    issues: list[dict] = []
    warnings: list[dict] = []

    runtime = {
        "inside_container": inside_container,
        "platform": sys.platform,
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "mode": "container" if inside_container else "local-degraded",
    }
    if not inside_container:
        warnings.append(
            {
                "code": "local-degraded-doctor",
                "message": "Local doctor: CPU validation only, GPU/Metal not tested.",
            }
        )

    capabilities: dict[str, dict] = {}
    packages = {
        "faster-whisper": REQUIRED_FASTER_WHISPER_VERSION,
        "ctranslate2": REQUIRED_CTRANSLATE2_VERSION,
    }
    for package, required in packages.items():
        installed = package_version(package)
        ok = installed == required
        capabilities[package.replace("-", "_")] = {
            "ok": ok,
            "installed": installed,
            "required": required,
        }
        checks.append({"name": package, "ok": ok, "installed": installed, "required": required})
        if installed is None and package == "faster-whisper":
            issues.append(issue("missing-faster-whisper", f"{package} is not installed"))
        elif installed is None:
            issues.append(issue("wrong-python-package-version", f"{package} is not installed"))
        elif installed != required:
            issues.append(
                issue("wrong-python-package-version", f"{package}=={installed} does not match required {required}")
            )

    for command in ("ffmpeg", "ffprobe"):
        path = shutil.which(command)
        ok = path is not None
        capabilities[command] = {"ok": ok, "path": path}
        checks.append({"name": command, "ok": ok, "path": path})
        if not ok:
            issues.append(issue("missing-ffmpeg", f"{command} is not available on PATH"))

    writable, write_error = writable_directory(hf_home)
    capabilities["hf_home"] = {
        "ok": writable,
        "path": str(hf_home),
        "source": "env" if os.environ.get("HF_HOME") else "default",
        "error": write_error,
    }
    checks.append({"name": "HF_HOME", "ok": writable, "path": str(hf_home), "error": write_error})
    if not writable:
        issues.append(issue("unwritable-hf-home", f"HF_HOME is not writable: {hf_home} ({write_error})"))

    free_gb = disk_free_gb(hf_home)
    required_gb = model_required_space_gb(model)
    disk_ok = free_gb is not None and free_gb >= required_gb
    capabilities["model_disk"] = {
        "ok": disk_ok,
        "model": model,
        "free_gb": round(free_gb, 2) if free_gb is not None else None,
        "required_gb": required_gb,
    }
    checks.append({"name": "model_disk", **capabilities["model_disk"]})
    if not disk_ok:
        issues.append(
            issue(
                "insufficient-disk",
                f"model {model} needs about {required_gb:g}GB free in cache; available: {free_gb}",
            )
        )

    if requested_device == "cuda":
        cuda_ok = False
        cuda_error = None
        try:
            import ctranslate2

            cuda_ok = ctranslate2.get_cuda_device_count() > 0
        except Exception as exc:
            cuda_error = str(exc)
        capabilities["cuda"] = {"ok": cuda_ok, "error": cuda_error}
        checks.append({"name": "cuda", "ok": cuda_ok, "error": cuda_error})
        if not cuda_ok:
            issues.append(issue("unsupported-gpu", "CUDA was requested but no usable CUDA device was detected"))

    report = {
        "ok": False,
        "exit_code": EXIT_READY,
        "skill": SKILL_NAME,
        "model": model,
        "runtime": runtime,
        "capabilities": capabilities,
        "checks": checks,
        "issues": issues,
        "warnings": warnings,
    }
    report["exit_code"] = doctor_exit_code(report)
    report["ok"] = report["exit_code"] == EXIT_READY
    return report


def format_doctor_report(report: dict) -> str:
    lines = [
        "Whisper Transcribe doctor",
        f"Status: {'ready' if report['ok'] else 'not ready'}",
        f"Runtime: {report['runtime']['mode']} ({report['runtime']['platform']}, {report['runtime']['machine']})",
        f"Model: {report['model']}",
        "",
        "Checks:",
    ]
    for item in report["checks"]:
        state = "OK" if item.get("ok") else "FAIL"
        detail = item.get("installed") or item.get("path") or item.get("error") or ""
        lines.append(f"- {state}: {item['name']} {detail}".rstrip())
    if report["warnings"]:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {item['message']}" for item in report["warnings"])
    if report["issues"]:
        lines.extend(["", "Issues:"])
        for item in report["issues"]:
            lines.append(f"- {item['message']}")
            lines.append(f"  Cause: {item['cause']}")
            lines.append(f"  Next: {item['next_command']}")
    return "\n".join(lines) + "\n"


def safe_stem(path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", path.stem.strip())
    return stem.strip("-._") or "transcript"


def parse_formats(raw: str | None, mode: str = "quick") -> list[str]:
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"unsupported mode: {mode}")
    if raw is None or not raw.strip():
        return list(MODE_DEFAULT_FORMATS[mode])

    values = [part.strip().lower() for part in raw.split(",") if part.strip()]
    if not values:
        return list(MODE_DEFAULT_FORMATS[mode])

    unknown = sorted(set(values) - SUPPORTED_FORMATS - {"all"})
    if unknown:
        raise ValueError(f"unsupported output format: {', '.join(unknown)}")

    if "all" in values:
        return list(ALL_FORMATS)
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


def write_transcript_md(path: Path, segments: Iterable[Segment], metadata: dict) -> None:
    lines = [
        "# Transcript",
        "",
        "## Metadata",
        "",
        f"- Source: `{metadata.get('source', '')}`",
        f"- Mode: `{metadata.get('mode', '')}`",
        f"- Language: `{metadata.get('language', '')}`",
        f"- Language mode: `{metadata.get('language_mode', '')}`",
        f"- Model: `{metadata.get('model', '')}`",
        f"- Duration seconds: `{metadata.get('duration_seconds', '')}`",
        f"- Access: `{metadata.get('access_level', '')}`",
        f"- Confidence: `{metadata.get('transcription_confidence', '')}`",
        f"- Transcript readiness: `{metadata.get('transcript_readiness', 0)}/3`",
        "",
        "## Transcript",
        "",
    ]
    lines.extend(segment.text.strip() for segment in segments if segment.text.strip())
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def source_parent_is_writable(source: Path) -> bool:
    parent = source.parent if source.parent != Path("") else Path.cwd()
    return parent.exists() and os.access(parent, os.W_OK)


def workspace_base() -> Path:
    if DEFAULT_WORKSPACE_OUTPUT.exists() or DEFAULT_WORKSPACE_OUTPUT.parent.exists():
        return DEFAULT_WORKSPACE_OUTPUT
    return Path.cwd() / "transcripts"


def resolve_output_dir(
    source: Path,
    output_dir: str | None,
    workspace_output: bool,
    run_id: str | None = None,
    batch_mode: bool = False,
) -> Path:
    if output_dir:
        return Path(output_dir).expanduser().resolve()

    if workspace_output or batch_mode or not source_parent_is_writable(source):
        label = "batch" if batch_mode else safe_stem(source)
        timestamp = run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
        return (workspace_base() / f"{label}-{timestamp}").resolve()

    return source.parent.resolve()


def output_path_for(output_dir: Path, source: Path, fmt: str) -> Path:
    if fmt == "transcript-md":
        return output_dir / f"{safe_stem(source)}.transcript.md"
    return output_dir / f"{safe_stem(source)}.{fmt}"


def ensure_writable_output(path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {path}. Use --overwrite to replace it.")


def planned_output_paths(sources: list[Path], output_dir: Path, formats: list[str]) -> list[Path]:
    paths = [output_dir / "manifest.json"]
    for source in sources:
        paths.extend(output_path_for(output_dir, source, fmt) for fmt in formats)
    return paths


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
            "faster-whisper is not installed in this runtime. Run: "
            "python3 scripts/whisper_transcribe.py --doctor --json. "
            "For NanoClaw containers, run: bash scripts/setup-host.sh --check /path/to/nanoclaw"
        ) from exc
    return WhisperModel


def extract_words(item) -> list[Word]:
    raw_words = getattr(item, "words", None) or []
    return [
        Word(
            start=getattr(word, "start", 0.0),
            end=getattr(word, "end", 0.0),
            word=getattr(word, "word", ""),
            probability=getattr(word, "probability", None),
        )
        for word in raw_words
    ]


def transcription_confidence(info, segments: list[Segment]) -> str:
    if not segments:
        return "low"
    probability = getattr(info, "language_probability", None)
    if probability is None:
        return "medium"
    if probability >= 0.9:
        return "high"
    if probability >= 0.6:
        return "medium"
    return "low"


def transcript_readiness(info, segments: list[Segment]) -> int:
    if not segments:
        return 1
    confidence = transcription_confidence(info, segments)
    if confidence == "high":
        return 3
    if confidence == "medium":
        return 2
    return 1


def build_source_manifest(
    source: Path,
    output_dir: Path,
    outputs: dict[str, str],
    formats: list[str],
    info,
    segments: list[Segment],
    options,
    created_at: str,
) -> dict:
    language = getattr(info, "language", getattr(options, "language", None))
    return {
        "source": str(source),
        "source_name": source.name,
        "source_origin": getattr(options, "source_origin", "unknown"),
        "origin_confidence": getattr(options, "origin_confidence", "unknown"),
        "source_note": getattr(options, "source_note", ""),
        "access_level": "full local media",
        "output_dir": str(output_dir),
        "outputs": outputs,
        "formats": formats,
        "language": language,
        "language_probability": getattr(info, "language_probability", None),
        "language_mode": "user-specified" if getattr(options, "language", None) else "auto-detected",
        "model": getattr(options, "model", None),
        "device": getattr(options, "device", None),
        "compute_type": getattr(options, "compute_type", None),
        "mode": getattr(options, "mode", "quick"),
        "duration_seconds": getattr(info, "duration", None),
        "segment_count": len(segments),
        "word_timestamps": bool(getattr(options, "word_timestamps", False)),
        "word_count": sum(len(segment.words) for segment in segments),
        "transcription_confidence": transcription_confidence(info, segments),
        "transcript_readiness": transcript_readiness(info, segments),
        "created_at": created_at,
        "warnings": [],
    }


def write_manifest(path: Path, manifest: dict, overwrite: bool) -> None:
    ensure_writable_output(path, overwrite)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_sources(sources: list[str]) -> list[Path]:
    paths = [Path(source).expanduser().resolve() for source in sources]
    for source in paths:
        if not source.exists():
            raise FileNotFoundError(f"source file not found: {source}")
        if not source.is_file():
            raise ValueError(f"source path is not a file: {source}")
    return paths


def transcribe_one(source: Path, output_dir: Path, formats: list[str], model, info_options, overwrite: bool) -> dict:
    generated_segments, info = model.transcribe(
        str(source),
        language=info_options.language,
        beam_size=info_options.beam_size,
        vad_filter=not info_options.no_vad,
        task="transcribe",
        word_timestamps=info_options.word_timestamps,
    )
    segments = [
        Segment(index=index, start=item.start, end=item.end, text=item.text, words=extract_words(item))
        for index, item in enumerate(generated_segments, start=1)
    ]

    outputs: dict[str, str] = {}
    for fmt in formats:
        target = output_path_for(output_dir, source, fmt)
        ensure_writable_output(target, overwrite)
        if fmt == "txt":
            write_txt(target, segments)
        elif fmt == "srt":
            write_srt(target, segments)
        elif fmt == "vtt":
            write_vtt(target, segments)
        elif fmt == "transcript-md":
            partial_manifest = build_source_manifest(
                source=source,
                output_dir=output_dir,
                outputs={},
                formats=formats,
                info=info,
                segments=segments,
                options=info_options,
                created_at=info_options.created_at,
            )
            write_transcript_md(target, segments, partial_manifest)
        outputs[fmt] = str(target)

    source_manifest = build_source_manifest(
        source=source,
        output_dir=output_dir,
        outputs=outputs,
        formats=formats,
        info=info,
        segments=segments,
        options=info_options,
        created_at=info_options.created_at,
    )
    return source_manifest


def transcribe(args: argparse.Namespace) -> dict:
    sources = validate_sources(args.sources)
    args.mode = args.mode or ("batch" if len(sources) > 1 else "quick")
    formats = parse_formats(args.formats, args.mode)
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    created_at = datetime.now().isoformat(timespec="seconds")

    batch_mode = len(sources) > 1 or args.mode == "batch"
    output_root = resolve_output_dir(sources[0], args.output_dir, args.workspace_output, run_id, batch_mode)
    output_root.mkdir(parents=True, exist_ok=True)
    for target in planned_output_paths(sources, output_root, formats):
        ensure_writable_output(target, args.overwrite)

    device = infer_device(args.device)
    compute_type = infer_compute_type(args.compute_type, device)
    model_name = args.model or os.environ.get("WHISPER_MODEL", "small")

    WhisperModel = load_faster_whisper()
    model = WhisperModel(model_name, device=device, compute_type=compute_type)

    info_options = argparse.Namespace(**vars(args))
    info_options.model = model_name
    info_options.device = device
    info_options.compute_type = compute_type
    info_options.created_at = created_at

    source_manifests = [
        transcribe_one(source, output_root, formats, model, info_options, args.overwrite)
        for source in sources
    ]

    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "created_at": created_at,
        "mode": args.mode,
        "batch": batch_mode,
        "formats": formats,
        "output_dir": str(output_root),
        "manifest_path": str(output_root / "manifest.json"),
        "source_count": len(source_manifests),
        "sources": source_manifests,
        "warnings": [],
    }

    if len(source_manifests) == 1:
        single = source_manifests[0]
        manifest.update(
            {
                "source": single["source"],
                "outputs": single["outputs"],
                "language": single["language"],
                "language_probability": single["language_probability"],
                "language_mode": single["language_mode"],
                "model": single["model"],
                "device": single["device"],
                "compute_type": single["compute_type"],
                "duration_seconds": single["duration_seconds"],
                "segment_count": single["segment_count"],
                "source_origin": single["source_origin"],
                "origin_confidence": single["origin_confidence"],
                "access_level": single["access_level"],
                "transcription_confidence": single["transcription_confidence"],
                "transcript_readiness": single["transcript_readiness"],
            }
        )

    write_manifest(output_root / "manifest.json", manifest, args.overwrite)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transcribe local audio/video files with faster-whisper.")
    parser.add_argument("sources", nargs="*", help="One or more local audio or video file paths.")
    parser.add_argument("--doctor", action="store_true", help="Run runtime dependency diagnostics instead of transcribing.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON for doctor output.")
    parser.add_argument("--validate-host-manifest", help=argparse.SUPPRESS)
    parser.add_argument("--mode", choices=sorted(SUPPORTED_MODES), help="Workflow mode.")
    parser.add_argument("--formats", help="Comma-separated output formats: txt,srt,vtt,transcript-md,all.")
    parser.add_argument("--language", help="Optional Whisper language code such as pt, en, es, fr, or it.")
    parser.add_argument("--output-dir", help="Directory for output files.")
    parser.add_argument("--workspace-output", action="store_true", help="Write under the workspace transcript folder.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing output files.")
    parser.add_argument("--model", default=os.environ.get("WHISPER_MODEL", "small"), help="faster-whisper model name.")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"], help="Inference device.")
    parser.add_argument("--compute-type", default="auto", help="CTranslate2 compute type, or auto.")
    parser.add_argument("--beam-size", type=int, default=5, help="Beam size for transcription.")
    parser.add_argument("--no-vad", action="store_true", help="Disable VAD filtering.")
    parser.add_argument("--word-timestamps", action="store_true", help="Request word timestamps from faster-whisper.")
    parser.add_argument(
        "--source-origin",
        default="unknown",
        choices=["unknown", "direct-upload", "forwarded", "inferred-forwarded", "local-file"],
        help="Where the media came from when runtime metadata is available.",
    )
    parser.add_argument(
        "--origin-confidence",
        default="unknown",
        choices=["unknown", "explicit", "inferred"],
        help="Whether source origin came from platform metadata or inference.",
    )
    parser.add_argument("--source-note", default="", help="Short note about attachment or forwarding metadata.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.validate_host_manifest:
        try:
            data = json.loads(Path(args.validate_host_manifest).read_text(encoding="utf-8"))
        except Exception as exc:
            print(json.dumps({"ok": False, "errors": [str(exc)]}, ensure_ascii=False), file=sys.stderr)
            return EXIT_INVALID_CONFIG
        errors = validate_host_manifest(data)
        result = {"ok": not errors, "errors": errors}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return EXIT_READY if not errors else EXIT_INVALID_CONFIG
    if args.doctor:
        report = run_doctor(args)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(format_doctor_report(report), end="")
        return int(report["exit_code"])
    if not args.sources:
        parser.error("at least one source file is required unless --doctor is used")
    try:
        summary = transcribe(args)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, **summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
