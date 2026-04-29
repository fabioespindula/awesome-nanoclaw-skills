#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

require_rg() {
  command -v rg >/dev/null 2>&1 || fail "ripgrep (rg) is required for validation"
}

require_file() {
  test -f "$1" || fail "missing required file: $1"
}

require_pattern() {
  local pattern="$1"
  shift
  rg -q "$pattern" "$@" || fail "missing pattern '$pattern' in $*"
}

require_rg

required_files=(
  "SKILL.md"
  "references/council-agents.md"
  "references/challenge-round.md"
  "references/synthesis-chair.md"
  "references/identity-shuffle.md"
  "references/sample-runs.md"
  "assets/templates/telegram-summary.md"
  "assets/templates/full-transcript.md"
  "docs/prd-nano-council.md"
  "docs/superpowers/plans/2026-04-29-nano-council.md"
)

for file in "${required_files[@]}"; do
  require_file "$file"
done

require_pattern '^name: nano-council$' SKILL.md
require_pattern '^description: Use when ' SKILL.md
require_pattern 'user-invocable: true' SKILL.md
require_pattern 'slash-command: /council' SKILL.md
require_pattern 'output: telegram-markdown' SKILL.md

for ref in \
  'references/council-agents.md' \
  'references/identity-shuffle.md' \
  'references/challenge-round.md' \
  'references/synthesis-chair.md' \
  'assets/templates/telegram-summary.md' \
  'assets/templates/full-transcript.md'; do
  require_pattern "$ref" SKILL.md
done

for advisor in 'Red Team' 'Axiom' 'Horizon' 'Streetlight' 'Operator'; do
  require_pattern "$advisor" references/council-agents.md SKILL.md docs/prd-nano-council.md
done

for behavior in 'Agent' 'Telegram' '/workspace/group/council' 'dominant language' 'anonymous' 'chairman'; do
  require_pattern "$behavior" SKILL.md references assets docs/prd-nano-council.md
done

for heading in \
  '## Recommendation' \
  '## Where They Agree' \
  '## Where They Disagree' \
  '## Blind Spots' \
  '## Advisor Snapshots' \
  '## Next Action'; do
  require_pattern "$heading" assets/templates/telegram-summary.md
done

for heading in \
  '## User Question' \
  '## Neutral Brief' \
  '## Context' \
  '## Advisor Responses' \
  '## Identity Map' \
  '## Anonymized Responses' \
  '## Peer Reviews' \
  '## Chairman Synthesis'; do
  require_pattern "$heading" assets/templates/full-transcript.md
done

for protection in \
  'Do not tell a reviewer' \
  'no identity map' \
  'Do not include the identity map'; do
  require_pattern "$protection" references/challenge-round.md references/identity-shuffle.md
done

if rg -n 'advisor-prompts|reviewer-prompts|chairman-prompts|anonymization\.md|examples\.md|telegram-report|(^|[^-])transcript\.md|report\.html|open on Mac|open ' SKILL.md references assets; then
  fail "forbidden old filename or browser-first output term found"
fi

if rg -n '\|' assets/templates/telegram-summary.md; then
  fail "telegram summary must avoid tables"
fi

printf 'Nano Council validation passed.\n'
