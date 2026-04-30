#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCTOR_SCRIPT="$SKILL_DIR/scripts/whisper_transcribe.py"

SKILL_NAME="whisper-transcribe"
ANCHOR="# nanoclaw:install-extensions"
BEGIN_RE="# >>> nanoclaw:whisper-transcribe v1 BEGIN"
END_MARKER="# <<< nanoclaw:whisper-transcribe v1 END"
DEFAULT_HOST_CACHE_DIR="/var/lib/nanoclaw/whisper-cache"
DEFAULT_CONTAINER_HF_HOME="/workspace/.cache/huggingface"
DEFAULT_MODEL="small"
REQUIRED_COMPOSE_VERSION="2.20.0"
BACKUP_KEEP=3

usage() {
  cat <<'EOF'
Usage:
  setup-host.sh --init <nanoclaw-root> [flags]
  setup-host.sh --check <nanoclaw-root>
  setup-host.sh --apply <nanoclaw-root> [--force-overwrite] [--repair-anchor]
  setup-host.sh --rebuild <nanoclaw-root>
  setup-host.sh --warm-cache <nanoclaw-root> [model]

Init flags:
  --update
  --force
  --non-interactive
  --service <name>
  --dockerfile <path>
  --compose-file <path>
  --skills-dir <path>
  --host-cache-dir <path>
  --model <name>
EOF
}

die() {
  local code="$1"
  shift
  printf 'ERROR: %s\n' "$*" >&2
  exit "$code"
}

info() {
  printf '%s\n' "$*"
}

json_quote() {
  python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"
}

timestamp() {
  date +"%Y%m%d-%H%M%S"
}

require_root() {
  [[ -n "${ROOT:-}" ]] || die 3 "NanoClaw root is required."
  [[ -d "$ROOT" ]] || die 3 "NanoClaw root not found: $ROOT"
  ROOT="$(cd "$ROOT" && pwd)"
  NANOCLAW_DIR="$ROOT/.nanoclaw"
  MANIFEST="$NANOCLAW_DIR/host.json"
  EXAMPLE_MANIFEST="$NANOCLAW_DIR/host.example.json"
  SETUP_LOG="$NANOCLAW_DIR/setup.log"
}

append_log() {
  mkdir -p "$NANOCLAW_DIR"
  printf '%s %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*" >> "$SETUP_LOG"
}

prune_backups() {
  local original="$1"
  python3 - "$original" "$BACKUP_KEEP" "$SETUP_LOG" <<'PY'
from __future__ import annotations
import pathlib
import sys
from datetime import datetime, timezone

original = pathlib.Path(sys.argv[1])
keep = int(sys.argv[2])
log_path = pathlib.Path(sys.argv[3])
backups = sorted(original.parent.glob(original.name + ".bak.*"))
for path in backups[:-keep]:
    try:
        path.unlink()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as log:
            stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            log.write(f"{stamp} pruned backup {path}\n")
    except FileNotFoundError:
        pass
PY
}

backup_file() {
  local file="$1"
  [[ -f "$file" ]] || die 3 "Cannot back up missing file: $file"
  local backup="${file}.bak.$(timestamp)"
  cp "$file" "$backup"
  append_log "backup $file -> $backup"
  prune_backups "$file"
}

compose_version_ok() {
  local raw
  raw="$(docker compose version --short 2>/dev/null || true)"
  [[ -n "$raw" ]] || return 1
  python3 - "$raw" "$REQUIRED_COMPOSE_VERSION" <<'PY'
import re
import sys

def parts(version: str) -> tuple[int, int, int]:
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", version)
    if not match:
        return (0, 0, 0)
    return tuple(int(part or 0) for part in match.groups())

sys.exit(0 if parts(sys.argv[1]) >= parts(sys.argv[2]) else 1)
PY
}

require_compose_version() {
  command -v docker >/dev/null 2>&1 || die 3 "Docker is required on the NanoClaw host."
  compose_version_ok || die 3 "Docker Compose >= $REQUIRED_COMPOSE_VERSION is required for top-level include support."
}

write_manifest() {
  mkdir -p "$NANOCLAW_DIR"
  python3 - "$MANIFEST" "$EXAMPLE_MANIFEST" <<PY
from __future__ import annotations
import json
import pathlib
import sys

manifest_path = pathlib.Path(sys.argv[1])
example_path = pathlib.Path(sys.argv[2])
data = {
    "schema_version": 1,
    "runtime": "nanoclaw",
    "compose_file": ${COMPOSE_FILE_JSON},
    "service": ${SERVICE_JSON},
    "dockerfile": ${DOCKERFILE_JSON},
    "skills_dir": ${SKILLS_DIR_JSON},
    "skills": {
        "whisper-transcribe": {
            "host_cache_dir": ${HOST_CACHE_DIR_JSON},
            "container_hf_home": ${CONTAINER_HF_HOME_JSON},
            "model": ${MODEL_JSON},
        }
    },
}
manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
example = json.loads(json.dumps(data))
example["skills"]["whisper-transcribe"]["host_cache_dir"] = "/var/lib/nanoclaw/whisper-cache"
example_path.write_text(json.dumps(example, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY
  append_log "wrote manifest $MANIFEST and template $EXAMPLE_MANIFEST"
}

ensure_gitignore() {
  local ignore="$NANOCLAW_DIR/.gitignore"
  mkdir -p "$NANOCLAW_DIR"
  touch "$ignore"
  if ! grep -qx 'host.json' "$ignore"; then
    printf 'host.json\n' >> "$ignore"
    append_log "updated $ignore"
  fi
}

validate_manifest() {
  [[ -f "$MANIFEST" ]] || die 3 "Manifest not found: $MANIFEST. Run --init first."
  python3 "$DOCTOR_SCRIPT" --validate-host-manifest "$MANIFEST" >/dev/null || die 3 "Invalid manifest: $MANIFEST"
}

load_manifest() {
  validate_manifest
  eval "$(
    python3 - "$MANIFEST" <<'PY'
from __future__ import annotations
import json
import shlex
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
skill = data["skills"]["whisper-transcribe"]
values = {
    "COMPOSE_FILE": data["compose_file"],
    "SERVICE": data["service"],
    "DOCKERFILE": data["dockerfile"],
    "SKILLS_DIR": data["skills_dir"],
    "HOST_CACHE_DIR": skill["host_cache_dir"],
    "CONTAINER_HF_HOME": skill["container_hf_home"],
    "MODEL": skill["model"],
}
for key, value in values.items():
    print(f"{key}={shlex.quote(str(value))}")
PY
  )"
  COMPOSE_PATH="$ROOT/$COMPOSE_FILE"
  DOCKERFILE_PATH="$ROOT/$DOCKERFILE"
  SKILL_RUNTIME_SCRIPT="$SKILLS_DIR/whisper-transcribe/scripts/whisper_transcribe.py"
}

prompt_default() {
  local var_name="$1"
  local prompt="$2"
  local default="$3"
  local value
  read -r -p "$prompt [$default]: " value
  printf -v "$var_name" '%s' "${value:-$default}"
}

init_mode() {
  require_root
  require_compose_version

  if [[ -f "$MANIFEST" && "$FORCE" != "true" && "$UPDATE" != "true" ]]; then
    die 3 "Manifest already exists: $MANIFEST. Use --update or --force."
  fi

  if [[ "$UPDATE" == "true" && -f "$MANIFEST" ]]; then
    load_manifest
    SERVICE_FLAG="${SERVICE_FLAG:-$SERVICE}"
    DOCKERFILE_FLAG="${DOCKERFILE_FLAG:-$DOCKERFILE}"
    COMPOSE_FILE_FLAG="${COMPOSE_FILE_FLAG:-$COMPOSE_FILE}"
    SKILLS_DIR_FLAG="${SKILLS_DIR_FLAG:-$SKILLS_DIR}"
    HOST_CACHE_DIR_FLAG="${HOST_CACHE_DIR_FLAG:-$HOST_CACHE_DIR}"
    MODEL_FLAG="${MODEL_FLAG:-$MODEL}"
  fi

  if [[ "$NON_INTERACTIVE" == "true" ]]; then
    [[ -n "${SERVICE_FLAG:-}" ]] || die 3 "--service is required with --non-interactive"
    [[ -n "${DOCKERFILE_FLAG:-}" ]] || die 3 "--dockerfile is required with --non-interactive"
    [[ -n "${COMPOSE_FILE_FLAG:-}" ]] || die 3 "--compose-file is required with --non-interactive"
    [[ -n "${SKILLS_DIR_FLAG:-}" ]] || die 3 "--skills-dir is required with --non-interactive"
    [[ -n "${HOST_CACHE_DIR_FLAG:-}" ]] || die 3 "--host-cache-dir is required with --non-interactive"
    [[ -n "${MODEL_FLAG:-}" ]] || die 3 "--model is required with --non-interactive"
  else
    info "NanoClaw Whisper Transcribe setup init"
    prompt_default SERVICE_FLAG "Compose service running NanoClaw" "${SERVICE_FLAG:-nanoclaw}"
    prompt_default COMPOSE_FILE_FLAG "Compose file" "${COMPOSE_FILE_FLAG:-docker-compose.yml}"
    prompt_default DOCKERFILE_FLAG "Dockerfile" "${DOCKERFILE_FLAG:-container/Dockerfile}"
    prompt_default SKILLS_DIR_FLAG "Skills dir" "${SKILLS_DIR_FLAG:-container/skills}"
    prompt_default HOST_CACHE_DIR_FLAG "Host Whisper cache dir" "${HOST_CACHE_DIR_FLAG:-$DEFAULT_HOST_CACHE_DIR}"
    prompt_default MODEL_FLAG "Default Whisper model" "${MODEL_FLAG:-$DEFAULT_MODEL}"
  fi

  [[ -f "$ROOT/$COMPOSE_FILE_FLAG" ]] || die 3 "Compose file not found: $ROOT/$COMPOSE_FILE_FLAG"
  [[ -f "$ROOT/$DOCKERFILE_FLAG" ]] || die 3 "Dockerfile not found: $ROOT/$DOCKERFILE_FLAG"
  [[ -d "$ROOT/$SKILLS_DIR_FLAG" ]] || die 3 "Skills dir not found: $ROOT/$SKILLS_DIR_FLAG"

  SERVICE_JSON="$(json_quote "$SERVICE_FLAG")"
  COMPOSE_FILE_JSON="$(json_quote "$COMPOSE_FILE_FLAG")"
  DOCKERFILE_JSON="$(json_quote "$DOCKERFILE_FLAG")"
  SKILLS_DIR_JSON="$(json_quote "$SKILLS_DIR_FLAG")"
  HOST_CACHE_DIR_JSON="$(json_quote "$HOST_CACHE_DIR_FLAG")"
  CONTAINER_HF_HOME_JSON="$(json_quote "$DEFAULT_CONTAINER_HF_HOME")"
  MODEL_JSON="$(json_quote "$MODEL_FLAG")"
  write_manifest
  ensure_gitignore

  local dockerfile_path="$ROOT/$DOCKERFILE_FLAG"
  if ! grep -qxF "$ANCHOR" "$dockerfile_path"; then
    backup_file "$dockerfile_path"
    printf '\n%s\n' "$ANCHOR" >> "$dockerfile_path"
    append_log "added Dockerfile anchor $dockerfile_path"
  fi

  info "Ready. Next: bash $SKILLS_DIR_FLAG/whisper-transcribe/scripts/setup-host.sh --check $ROOT"
}

compose() {
  docker compose -f "$COMPOSE_PATH" "$@"
}

run_doctor_exec() {
  compose exec -T "$SERVICE" python3 "$SKILL_RUNTIME_SCRIPT" --doctor --json --model "$MODEL"
}

run_doctor_once() {
  compose run --rm "$SERVICE" python3 "$SKILL_RUNTIME_SCRIPT" --doctor --json --model "$MODEL"
}

check_base_image() {
  local os_release
  set +e
  os_release="$(compose run --rm "$SERVICE" sh -lc 'cat /etc/os-release' 2>/dev/null)"
  local code=$?
  set -e
  [[ "$code" -eq 0 ]] || die 3 "Could not inspect container base image with docker compose run."
  if ! printf '%s\n' "$os_release" | grep -Eiq '^(ID|ID_LIKE)=.*(debian|ubuntu)'; then
    die 3 "Whisper setup v1 supports Debian/Ubuntu base images only."
  fi
}

check_mode() {
  require_root
  load_manifest
  require_compose_version
  check_base_image
  run_doctor_exec
}

canonical_hash() {
  python3 -c 'import hashlib,sys; data="\n".join(line.rstrip() for line in sys.stdin.read().replace("\r\n","\n").replace("\r","\n").split("\n")).rstrip("\n")+"\n"; print(hashlib.sha256(data.encode()).hexdigest())'
}

block_content_hash() {
  local file="$1"
  python3 - "$file" <<'PY' | canonical_hash
from __future__ import annotations
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()
inside = False
content: list[str] = []
for line in lines:
    if line.startswith("# >>> nanoclaw:whisper-transcribe v1 BEGIN"):
        inside = True
        continue
    if line == "# <<< nanoclaw:whisper-transcribe v1 END":
        break
    if inside:
        content.append(line)
print("\n".join(content))
PY
}

marker_hash() {
  local file="$1"
  grep -m1 "$BEGIN_RE" "$file" | sed -E 's/.*sha256=([a-f0-9]+).*/\1/' || true
}

replace_or_insert_docker_block() {
  local content="$1"
  [[ -n "$content" ]] || return 0
  if ! grep -qxF "$ANCHOR" "$DOCKERFILE_PATH"; then
    if [[ "$REPAIR_ANCHOR" == "true" ]]; then
      backup_file "$DOCKERFILE_PATH"
      printf '\n%s\n' "$ANCHOR" >> "$DOCKERFILE_PATH"
      append_log "repaired Dockerfile anchor $DOCKERFILE_PATH"
    else
      die 3 "Dockerfile anchor missing: $ANCHOR. Run --apply --repair-anchor to restore it."
    fi
  fi

  local hash
  hash="$(printf '%s\n' "$content" | canonical_hash)"
  local block
  block="# >>> nanoclaw:whisper-transcribe v1 BEGIN sha256=$hash"$'\n'"$content"$'\n'"$END_MARKER"

  if grep -q "$BEGIN_RE" "$DOCKERFILE_PATH"; then
    local expected actual
    expected="$(marker_hash "$DOCKERFILE_PATH")"
    actual="$(block_content_hash "$DOCKERFILE_PATH")"
    if [[ "$expected" != "$actual" && "$FORCE_OVERWRITE" != "true" ]]; then
      die 3 "Dockerfile whisper block drift detected. Use --force-overwrite to replace it."
    fi
  fi

  backup_file "$DOCKERFILE_PATH"
  python3 - "$DOCKERFILE_PATH" "$ANCHOR" "$block" <<'PY'
from __future__ import annotations
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
anchor = sys.argv[2]
block = sys.argv[3].splitlines()
lines = path.read_text(encoding="utf-8").splitlines()
out: list[str] = []
i = 0
replaced = False
while i < len(lines):
    if lines[i].startswith("# >>> nanoclaw:whisper-transcribe v1 BEGIN"):
        out.extend(block)
        replaced = True
        i += 1
        while i < len(lines) and lines[i] != "# <<< nanoclaw:whisper-transcribe v1 END":
            i += 1
        if i < len(lines):
            i += 1
        continue
    out.append(lines[i])
    if lines[i] == anchor and not replaced:
        out.extend(block)
        replaced = True
    i += 1
path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
PY
  append_log "patched Dockerfile $DOCKERFILE_PATH"
}

ensure_compose_include() {
  local block
  block="# >>> nanoclaw:whisper-transcribe v1 BEGIN"$'\n''include:'$'\n''  - ./.nanoclaw/compose.whisper.yml'$'\n'"$END_MARKER"

  if grep -q "$BEGIN_RE" "$COMPOSE_PATH"; then
    local existing
    existing="$(python3 - "$COMPOSE_PATH" <<'PY'
from __future__ import annotations
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()
inside = False
out = []
for line in lines:
    if line.startswith("# >>> nanoclaw:whisper-transcribe v1 BEGIN"):
        inside = True
    if inside:
        out.append(line)
    if inside and line == "# <<< nanoclaw:whisper-transcribe v1 END":
        break
print("\n".join(out))
PY
)"
    if [[ "$existing" != "$block" && "$FORCE_OVERWRITE" != "true" ]]; then
      die 3 "Compose whisper include block drift detected. Use --force-overwrite to replace it."
    fi
  fi

  backup_file "$COMPOSE_PATH"
  python3 - "$COMPOSE_PATH" "$block" <<'PY'
from __future__ import annotations
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
block = sys.argv[2].splitlines()
lines = path.read_text(encoding="utf-8").splitlines()
out: list[str] = []
i = 0
replaced = False
while i < len(lines):
    if lines[i].startswith("# >>> nanoclaw:whisper-transcribe v1 BEGIN"):
        out.extend(block)
        replaced = True
        i += 1
        while i < len(lines) and lines[i] != "# <<< nanoclaw:whisper-transcribe v1 END":
            i += 1
        if i < len(lines):
            i += 1
        continue
    out.append(lines[i])
    i += 1
if not replaced:
    out = block + [""] + out
path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
PY
  append_log "patched compose include $COMPOSE_PATH"
}

write_managed_compose() {
  mkdir -p "$NANOCLAW_DIR"
  local managed="$NANOCLAW_DIR/compose.whisper.yml"
  cat > "$managed" <<EOF
services:
  $SERVICE:
    volumes:
      - $HOST_CACHE_DIR:$CONTAINER_HF_HOME
    environment:
      HF_HOME: $CONTAINER_HF_HOME
EOF
  append_log "wrote managed compose $managed"
}

dockerfile_patch_content() {
  local doctor_json="$1"
  DOCTOR_JSON="$doctor_json" python3 - "$CONTAINER_HF_HOME" <<'PY'
from __future__ import annotations
import json
import os
import sys

container_hf_home = sys.argv[1]
data = json.loads(os.environ["DOCTOR_JSON"])
caps = data.get("capabilities", {})
lines: list[str] = []
ffmpeg_ok = caps.get("ffmpeg", {}).get("ok") and caps.get("ffprobe", {}).get("ok")
packages_ok = caps.get("faster_whisper", {}).get("ok") and caps.get("ctranslate2", {}).get("ok")
hf_home_ok = caps.get("hf_home", {}).get("ok") and caps.get("hf_home", {}).get("source") == "env"
if not ffmpeg_ok:
    lines.extend([
        "RUN apt-get update \\",
        "    && apt-get install -y --no-install-recommends ffmpeg \\",
        "    && rm -rf /var/lib/apt/lists/*",
    ])
if not packages_ok:
    lines.append("RUN pip install --no-cache-dir faster-whisper==1.2.1 ctranslate2==4.7.1")
if not hf_home_ok:
    lines.append(f"ENV HF_HOME={container_hf_home}")
print("\n".join(lines))
PY
}

apply_mode() {
  require_root
  load_manifest
  require_compose_version
  [[ -f "$COMPOSE_PATH" ]] || die 3 "Compose file not found: $COMPOSE_PATH"
  [[ -f "$DOCKERFILE_PATH" ]] || die 3 "Dockerfile not found: $DOCKERFILE_PATH"
  check_base_image

  mkdir -p "$HOST_CACHE_DIR" || die 4 "Cannot create host cache dir: $HOST_CACHE_DIR"

  local doctor_json doctor_code
  set +e
  doctor_json="$(run_doctor_once 2>/dev/null)"
  doctor_code=$?
  set -e
  if [[ -z "$doctor_json" ]]; then
    die 4 "Could not run container doctor. Rebuild or inspect the NanoClaw service."
  fi

  local content
  content="$(dockerfile_patch_content "$doctor_json")"
  replace_or_insert_docker_block "$content"
  ensure_compose_include
  write_managed_compose
  append_log "apply completed doctor_exit=$doctor_code"
  info "Applied Whisper Transcribe host setup. Next: bash $SKILLS_DIR/whisper-transcribe/scripts/setup-host.sh --rebuild $ROOT"
}

rebuild_mode() {
  require_root
  load_manifest
  require_compose_version
  compose build "$SERVICE"
  compose up -d "$SERVICE"
}

warm_cache_mode() {
  require_root
  load_manifest
  require_compose_version
  local model="${WARM_MODEL:-$MODEL}"
  compose run --rm -e "HF_HOME=$CONTAINER_HF_HOME" "$SERVICE" python3 - "$model" <<'PY'
from faster_whisper import WhisperModel
import sys

WhisperModel(sys.argv[1])
print(f"warmed faster-whisper model: {sys.argv[1]}")
PY
}

MODE="${1:-}"
[[ -n "$MODE" ]] || { usage; exit 2; }
if [[ "$MODE" == "--help" || "$MODE" == "-h" ]]; then
  usage
  exit 0
fi
shift || true

ROOT="${1:-}"
if [[ "$MODE" == "--init" || "$MODE" == "--check" || "$MODE" == "--apply" || "$MODE" == "--rebuild" || "$MODE" == "--warm-cache" ]]; then
  [[ -n "$ROOT" ]] || die 3 "NanoClaw root is required."
  shift || true
else
  usage
  exit 2
fi

WARM_MODEL=""
if [[ "$MODE" == "--warm-cache" && "${1:-}" != "" && "${1:-}" != --* ]]; then
  WARM_MODEL="$1"
  shift
fi

UPDATE=false
FORCE=false
FORCE_OVERWRITE=false
REPAIR_ANCHOR=false
NON_INTERACTIVE=false
SERVICE_FLAG=""
DOCKERFILE_FLAG=""
COMPOSE_FILE_FLAG=""
SKILLS_DIR_FLAG=""
HOST_CACHE_DIR_FLAG=""
MODEL_FLAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --update) UPDATE=true; shift ;;
    --force) FORCE=true; shift ;;
    --force-overwrite) FORCE_OVERWRITE=true; shift ;;
    --repair-anchor) REPAIR_ANCHOR=true; shift ;;
    --non-interactive) NON_INTERACTIVE=true; shift ;;
    --service) SERVICE_FLAG="${2:-}"; shift 2 ;;
    --dockerfile) DOCKERFILE_FLAG="${2:-}"; shift 2 ;;
    --compose-file) COMPOSE_FILE_FLAG="${2:-}"; shift 2 ;;
    --skills-dir) SKILLS_DIR_FLAG="${2:-}"; shift 2 ;;
    --host-cache-dir) HOST_CACHE_DIR_FLAG="${2:-}"; shift 2 ;;
    --model) MODEL_FLAG="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) die 3 "Unknown flag: $1" ;;
  esac
done

case "$MODE" in
  --init) init_mode ;;
  --check) check_mode ;;
  --apply) apply_mode ;;
  --rebuild) rebuild_mode ;;
  --warm-cache) warm_cache_mode ;;
esac
