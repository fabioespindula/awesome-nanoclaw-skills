#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$ROOT/../.." && pwd)"

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

require_file() {
  test -f "$1" || fail "missing required file: $1"
}

require_pattern() {
  local pattern="$1"
  shift
  rg -q "$pattern" "$@" || fail "missing pattern '$pattern' in $*"
}

command -v rg >/dev/null 2>&1 || fail "ripgrep (rg) is required for validation"

require_file "$ROOT/SKILL.md"
require_file "$ROOT/references/catalog.md"
require_file "$ROOT/templates/help-response.md"

require_pattern '^name: nanoskills$' "$ROOT/SKILL.md"
require_pattern '^description: Use when ' "$ROOT/SKILL.md"
require_pattern 'user-invocable: true' "$ROOT/SKILL.md"
require_pattern 'slash-command: /nanoskills' "$ROOT/SKILL.md"
require_pattern 'references/catalog.md' "$ROOT/SKILL.md"
require_pattern 'templates/help-response.md' "$ROOT/SKILL.md"
require_pattern 'Contextual examples' "$ROOT/SKILL.md" "$ROOT/templates/help-response.md"
require_pattern 'Do not run extra package-wide update checks during normal catalog or help responses' "$ROOT/SKILL.md"

for skill in "$REPO_ROOT"/skills/*; do
  test -d "$skill" || continue
  name="$(basename "$skill")"
  require_file "$skill/SKILL.md"
  require_pattern "$name" "$ROOT/references/catalog.md" "$ROOT/SKILL.md" "$REPO_ROOT/README.md"
done

for command in \
  '/nanoskills' \
  '/council' \
  '/read-for-me' \
  '/rethink' \
  '/think-big' \
  '/whisper-transcribe' \
  '/awesome-updater'; do
  require_pattern "$command" "$ROOT/references/catalog.md" "$ROOT/SKILL.md" "$REPO_ROOT/README.md" "$REPO_ROOT/skills"
done

for skill_md in "$REPO_ROOT"/skills/*/SKILL.md; do
  skill_name="$(basename "$(dirname "$skill_md")")"
  if [[ "$skill_name" == "nanoskills" ]]; then
    continue
  fi
  require_pattern '## Help Mode' "$skill_md"
  require_pattern 'curated examples' "$skill_md"
  require_pattern 'contextual examples' "$skill_md"
done

printf 'nanoskills validation passed.\n'
