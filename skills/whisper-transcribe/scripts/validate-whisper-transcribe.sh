#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -B "$ROOT/scripts/whisper_transcribe.py" --help >/dev/null
python3 -B -m unittest "$ROOT/tests/test_whisper_transcribe.py"

required_files=(
  "$ROOT/SKILL.md"
  "$ROOT/references/mode-resolution.md"
  "$ROOT/references/transcript-safety.md"
  "$ROOT/references/output-policy.md"
  "$ROOT/references/context-adapter.md"
  "$ROOT/templates/transcription-brief.md"
)

for file in "${required_files[@]}"; do
  test -f "$file"
done

grep -q "Trust Boundary" "$ROOT/SKILL.md"
grep -q "Mode Resolution" "$ROOT/SKILL.md"
grep -q "Action Suggestions" "$ROOT/SKILL.md"
grep -q "manifest.json" "$ROOT/references/output-policy.md"
grep -q "forwarded" "$ROOT/references/context-adapter.md"
grep -q "untrusted source content" "$ROOT/references/transcript-safety.md"

echo "whisper-transcribe validation passed"
