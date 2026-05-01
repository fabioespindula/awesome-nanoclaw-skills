#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SKILL_DIR/../.." && pwd)"

cd "$SKILL_DIR"

fail() {
  printf 'FEBA Board validation failed: %s\n' "$*" >&2
  exit 1
}

require_file() {
  local path="$1"
  [[ -f "$path" ]] || fail "missing file: $path"
}

require_pattern() {
  local pattern="$1"
  shift
  local target
  for target in "$@"; do
    if [[ -e "$target" ]] && rg -q "$pattern" "$target"; then
      return 0
    fi
  done
  fail "missing pattern '$pattern' in: $*"
}

require_no_pattern() {
  local pattern="$1"
  shift
  if rg -n "$pattern" "$@"; then
    fail "forbidden pattern '$pattern' found"
  fi
}

required_files=(
  "SKILL.md"
  "README.md"
  "references/board-agents.md"
  "references/challenge-round.md"
  "references/identity-shuffle.md"
  "references/synthesis-chair.md"
  "references/sample-runs.md"
  "assets/templates/chat-summary.md"
  "assets/templates/full-transcript.md"
  "docs/prd-feba-board.md"
  "docs/superpowers/plans/2026-04-30-feba-board.md"
)

for file in "${required_files[@]}"; do
  require_file "$file"
done

require_pattern '^name: feba-board$' SKILL.md
require_pattern 'slash-command: /febaboard' SKILL.md
require_pattern '/febaboard' SKILL.md README.md references/sample-runs.md "$REPO_ROOT/README.md"
require_pattern '/feba-board' SKILL.md README.md docs/prd-feba-board.md
require_pattern '/board' SKILL.md README.md docs/prd-feba-board.md
require_pattern '/council' SKILL.md README.md docs/prd-feba-board.md
require_pattern 'legacy alias' SKILL.md README.md docs/prd-feba-board.md
require_pattern 'chat-friendly-board-review' SKILL.md
require_pattern 'assets/templates/chat-summary.md' SKILL.md references/synthesis-chair.md
require_pattern 'assets/templates/full-transcript.md' SKILL.md references/synthesis-chair.md
require_pattern '/workspace/group/board' SKILL.md docs/prd-feba-board.md

for advisor in \
  'The Skeptic' \
  'The Thesis' \
  'The Market' \
  'The Customer' \
  'The Operator'; do
  require_pattern "$advisor" SKILL.md README.md references/board-agents.md docs/prd-feba-board.md
done

for behavior in \
  'dominant language' \
  'multiagent' \
  'swarm' \
  'solo board' \
  'only when the user explicitly'; do
  require_pattern "$behavior" SKILL.md docs/prd-feba-board.md
done

for heading in \
  'Decision:' \
  'Recommendation:' \
  'Board view:' \
  'Tension:' \
  'Next action:'; do
  require_pattern "$heading" assets/templates/chat-summary.md
done

for heading in \
  'Decision Brief' \
  'Advisor Outputs' \
  'Challenge Round' \
  'Synthesis' \
  'User-Facing Summary'; do
  require_pattern "$heading" assets/templates/full-transcript.md
done

require_pattern 'feba-board' "$REPO_ROOT/README.md" "$REPO_ROOT/skills/nanoskills/references/catalog.md" "$REPO_ROOT/skills/nanoskills/references/catalog.json"
require_pattern 'FEBA Board' "$REPO_ROOT/README.md" "$REPO_ROOT/skills/nanoskills/references/catalog.md" "$REPO_ROOT/skills/nanoskills/references/catalog.json"

old_slug="$(printf 'nano-\143\157\165\156\143\151\154')"
old_title="$(printf 'Nano \103\157\165\156\143\151\154')"
require_no_pattern "$old_slug|$old_title" "$REPO_ROOT"

printf 'FEBA Board validation passed.\n'
