#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -B "$ROOT/scripts/whisper_transcribe.py" --help >/dev/null
python3 -B -m unittest "$ROOT/tests/test_whisper_transcribe.py"

echo "whisper-transcribe validation passed"
