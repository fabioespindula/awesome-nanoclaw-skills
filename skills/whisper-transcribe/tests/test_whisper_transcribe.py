from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
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
        self.assertEqual(MODULE.parse_formats("all"), ["txt", "srt", "vtt", "transcript-md"])

    def test_parse_formats_supports_transcript_md(self) -> None:
        self.assertEqual(MODULE.parse_formats("txt,transcript-md"), ["txt", "transcript-md"])

    def test_parse_formats_deduplicates_and_preserves_order(self) -> None:
        self.assertEqual(MODULE.parse_formats("vtt,txt,vtt"), ["vtt", "txt"])

    def test_parse_formats_rejects_unknown_format(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported output format"):
            MODULE.parse_formats("txt,pdf")

    def test_parse_formats_rejects_unknown_format_even_with_all(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported output format"):
            MODULE.parse_formats("all,pdf")

    def test_default_formats_follow_mode(self) -> None:
        self.assertEqual(MODULE.parse_formats(None, "quick"), ["txt"])
        self.assertEqual(MODULE.parse_formats(None, "captions"), ["srt", "vtt"])
        self.assertEqual(MODULE.parse_formats(None, "archive"), ["txt", "srt", "vtt", "transcript-md"])
        self.assertEqual(MODULE.parse_formats(None, "meeting"), ["txt", "transcript-md"])

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

    def test_workspace_output_uses_workspace_base_when_parent_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "meeting audio.mp3"
            source.write_bytes(b"")
            original_workspace = MODULE.DEFAULT_WORKSPACE_OUTPUT
            try:
                MODULE.DEFAULT_WORKSPACE_OUTPUT = Path(tmp) / "workspace-root"
                target = MODULE.resolve_output_dir(source, None, True)
            finally:
                MODULE.DEFAULT_WORKSPACE_OUTPUT = original_workspace
            self.assertEqual(target.parent, (Path(tmp) / "workspace-root").resolve())
            self.assertRegex(target.name, r"meeting-audio-\d{8}-\d{6}")

    def test_workspace_output_falls_back_when_workspace_parent_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "meeting audio.mp3"
            source.write_bytes(b"")
            cwd = Path.cwd()
            original_workspace = MODULE.DEFAULT_WORKSPACE_OUTPUT
            try:
                MODULE.DEFAULT_WORKSPACE_OUTPUT = Path(tmp) / "missing" / "workspace-root"
                os.chdir(tmp)
                target = MODULE.resolve_output_dir(source, None, True)
            finally:
                os.chdir(cwd)
                MODULE.DEFAULT_WORKSPACE_OUTPUT = original_workspace
            self.assertEqual(target.parent, (Path(tmp) / "transcripts").resolve())
            self.assertRegex(target.name, r"meeting-audio-\d{8}-\d{6}")

    def test_batch_output_uses_one_run_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "first.mp3"
            source.write_bytes(b"")
            original_workspace = MODULE.DEFAULT_WORKSPACE_OUTPUT
            try:
                MODULE.DEFAULT_WORKSPACE_OUTPUT = Path(tmp) / "workspace-root"
                target = MODULE.resolve_output_dir(source, None, False, "20260430-120000", batch_mode=True)
            finally:
                MODULE.DEFAULT_WORKSPACE_OUTPUT = original_workspace
            self.assertEqual(target, (Path(tmp) / "workspace-root" / "batch-20260430-120000").resolve())

    def test_output_path_for_transcript_md(self) -> None:
        target = MODULE.output_path_for(Path("/tmp/out"), Path("My Audio.mp3"), "transcript-md")
        self.assertEqual(target, Path("/tmp/out/My-Audio.transcript.md"))

    def test_existing_output_requires_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "existing.txt"
            target.write_text("old", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "already exists"):
                MODULE.ensure_writable_output(target, overwrite=False)
            MODULE.ensure_writable_output(target, overwrite=True)

    def test_planned_output_paths_include_manifest_before_writes(self) -> None:
        paths = MODULE.planned_output_paths(
            sources=[Path("/tmp/a.mp3"), Path("/tmp/b.mp3")],
            output_dir=Path("/tmp/out"),
            formats=["txt", "transcript-md"],
        )
        self.assertEqual(paths[0], Path("/tmp/out/manifest.json"))
        self.assertIn(Path("/tmp/out/a.txt"), paths)
        self.assertIn(Path("/tmp/out/b.transcript.md"), paths)

    def test_write_transcript_md_includes_metadata_and_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "meeting.transcript.md"
            segments = [MODULE.Segment(index=1, start=0.0, end=1.5, text=" Hello there ")]
            metadata = {
                "source": "/tmp/meeting.mp3",
                "mode": "meeting",
                "language": "pt",
                "language_mode": "auto-detected",
                "model": "tiny",
                "duration_seconds": 1.5,
                "access_level": "full local media",
                "transcript_readiness": 3,
                "transcription_confidence": "high",
            }
            MODULE.write_transcript_md(target, segments, metadata)
            content = target.read_text(encoding="utf-8")
            self.assertIn("# Transcript", content)
            self.assertIn("Source: `/tmp/meeting.mp3`", content)
            self.assertIn("Transcript readiness: `3/3`", content)
            self.assertIn("Hello there", content)

    def test_build_source_manifest_keeps_forward_metadata(self) -> None:
        manifest = MODULE.build_source_manifest(
            source=Path("/tmp/audio.mp3"),
            output_dir=Path("/tmp/out"),
            outputs={"txt": "/tmp/out/audio.txt"},
            formats=["txt"],
            info=SimpleNamespace(language="pt", language_probability=0.95, duration=12.0),
            segments=[MODULE.Segment(index=1, start=0.0, end=2.0, text="Oi")],
            options=SimpleNamespace(
                language=None,
                model="tiny",
                device="cpu",
                compute_type="int8",
                mode="meeting",
                word_timestamps=True,
                source_origin="forwarded",
                origin_confidence="explicit",
                source_note="Telegram forward metadata was present",
            ),
            created_at="2026-04-30T12:00:00",
        )
        self.assertEqual(manifest["source_origin"], "forwarded")
        self.assertEqual(manifest["origin_confidence"], "explicit")
        self.assertEqual(manifest["source_note"], "Telegram forward metadata was present")
        self.assertEqual(manifest["transcript_readiness"], 3)
        self.assertEqual(manifest["transcription_confidence"], "high")
        self.assertTrue(manifest["word_timestamps"])

    def test_parser_accepts_multiple_sources_and_modes(self) -> None:
        args = MODULE.build_parser().parse_args(
            ["a.mp3", "b.mp3", "--mode", "batch", "--formats", "transcript-md", "--word-timestamps"]
        )
        self.assertEqual(args.sources, ["a.mp3", "b.mp3"])
        self.assertEqual(args.mode, "batch")
        self.assertTrue(args.word_timestamps)


if __name__ == "__main__":
    unittest.main()
