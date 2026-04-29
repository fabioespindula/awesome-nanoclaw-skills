#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -B "$ROOT/scripts/awesome_skills.py" --help >/dev/null
python3 -B -m unittest "$ROOT/tests/test_awesome_skills.py"

echo "awesome-updater validation passed"
