#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SKILL_DIR/../.." && pwd)"

cd "$SKILL_DIR"

fail() {
  printf 'rethink validation failed: %s\n' "$*" >&2
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

command -v rg >/dev/null 2>&1 || fail "ripgrep (rg) is required for validation"

required_files=(
  "SKILL.md"
  "references/decision-lenses.md"
  "references/context-adapter.md"
  "references/sample-runs.md"
  "agents/openai.yaml"
)

for file in "${required_files[@]}"; do
  require_file "$file"
done

require_pattern '^name: rethink$' SKILL.md
require_pattern '^description: >-' SKILL.md
require_pattern 'user-invocable: true' SKILL.md
require_pattern 'slash-command: /rethink' SKILL.md
require_pattern 'output: decision-review' SKILL.md
require_pattern 'catalog:' SKILL.md
require_pattern 'group: user-facing' SKILL.md
require_pattern 'order: 30' SKILL.md
require_pattern 'readme_include: true' SKILL.md

for ref in \
  'references/context-adapter.md' \
  'references/decision-lenses.md' \
  'references/sample-runs.md'; do
  require_pattern "$ref" SKILL.md
done

for concept in \
  'Decision object' \
  'Hidden Assumptions' \
  'Real Alternatives' \
  'failure modes' \
  'Reversibility' \
  'Recommendation' \
  'Next move'; do
  require_pattern "$concept" SKILL.md references
done

for posture in \
  'clarify' \
  'pressure' \
  'expand' \
  'simplify' \
  'decide'; do
  require_pattern "$posture" SKILL.md references/sample-runs.md
done

for behavior in \
  'visible conversation' \
  'Do not use saved memory' \
  'first-pass rethink' \
  'Do not quote secrets' \
  'Do not create tasks' \
  'think-big' \
  'concrete object' \
  'broad theme'; do
  require_pattern "$behavior" SKILL.md references
done

for sample in \
  'Launch Timing' \
  'Product Versus Service' \
  'Architecture Tradeoff' \
  'Broad Theme Boundary' \
  'Help Mode' \
  'small cohort' \
  'rollback criteria' \
  'contractually isolated' \
  'auto-update' \
  'opt-out'; do
  require_pattern "$sample" references/sample-runs.md
done

private_context="Context""Hub"
private_db="Supa""base"
private_task_table="public""\.tasks"
private_memory_table="public""\.memorias"
private_company_one="home""you"
private_company_two="feba""-capital"
private_pattern="${private_context}|${private_db}|${private_task_table}|${private_memory_table}|${private_company_one}|${private_company_two}"
require_no_pattern "$private_pattern" SKILL.md references agents

python3 -B "$REPO_ROOT/skills/nanoskills/scripts/generate_catalog.py" --check --repo-root "$REPO_ROOT" --skills-dir "$REPO_ROOT/skills"

printf 'rethink validation passed.\n'
