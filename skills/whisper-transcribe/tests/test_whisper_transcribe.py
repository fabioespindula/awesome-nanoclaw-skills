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

    def test_parse_formats_rejects_unknown_format_even_with_all(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported output format"):
            MODULE.parse_formats("all,pdf")

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


if __name__ == "__main__":
    unittest.main()
