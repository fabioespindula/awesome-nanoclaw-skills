# Runtime Setup Spec: Whisper Transcribe

## Summary
Add a safe NanoClaw runtime setup layer for `whisper-transcribe`. This complements `docs/prd-whisper-transcribe.md`; it does not change the transcription contract, output formats, manifest behavior, or transcript safety rules.

V1 goal: make dependency/setup failures understandable and fixable for NanoClaw Docker/VPS users without silent host mutation.

## Key Decisions
- Doctor is container-side by design; local/macOS doctor is degraded and CPU-only.
- Host setup is explicit through `scripts/setup-host.sh`; no silent installs.
- Detection uses `.nanoclaw/host.json` in the NanoClaw runtime root.
- Manifest uses `skills.whisper-transcribe.*` namespace.
- Cache uses bind mount: `/var/lib/nanoclaw/whisper-cache` -> `/workspace/.cache/huggingface`.
- Set only `HF_HOME`; let Hugging Face derive `HF_HUB_CACHE`.
- `ffmpeg`/`ffprobe` are required for NanoClaw V1.
- Pin runtime deps as skill constants: `faster-whisper==1.2.1`, `ctranslate2==4.7.1`.
- V1 supports Debian/Ubuntu base images only.
- Host requires Docker Compose `>= 2.20` for `include`.
- Compose patch uses top-level `include` pointing to `.nanoclaw/compose.whisper.yml`.
- Dockerfile patch requires anchor: `# nanoclaw:install-extensions`.
- Backups keep latest 3 per file and log pruning.

## Files
New:
- `skills/whisper-transcribe/docs/runtime-setup-spec.md`
- `skills/whisper-transcribe/scripts/setup-host.sh`
- `skills/whisper-transcribe/references/runtime-requirements.md`

Modified:
- `skills/whisper-transcribe/SKILL.md`
- `skills/whisper-transcribe/scripts/whisper_transcribe.py`
- `skills/whisper-transcribe/tests/test_whisper_transcribe.py`
- `skills/whisper-transcribe/scripts/validate-whisper-transcribe.sh`

## Manifest Schema
Runtime file: `.nanoclaw/host.json`, env-specific and gitignored.

Versionable template: `.nanoclaw/host.example.json`.

```json
{
  "schema_version": 1,
  "runtime": "nanoclaw",
  "compose_file": "docker-compose.yml",
  "service": "nanoclaw",
  "dockerfile": "container/Dockerfile",
  "skills_dir": "container/skills",
  "skills": {
    "whisper-transcribe": {
      "host_cache_dir": "/var/lib/nanoclaw/whisper-cache",
      "container_hf_home": "/workspace/.cache/huggingface",
      "model": "small"
    }
  }
}
```

Invalid/missing/unknown schema exits `3`.

## Public Interfaces
Doctor:
```bash
python3 scripts/whisper_transcribe.py --doctor
python3 scripts/whisper_transcribe.py --doctor --json
python3 scripts/whisper_transcribe.py --doctor --model large-v3
```

Setup primary modes:
```bash
bash scripts/setup-host.sh --init /path/to/nanoclaw
bash scripts/setup-host.sh --check /path/to/nanoclaw
bash scripts/setup-host.sh --apply /path/to/nanoclaw
bash scripts/setup-host.sh --rebuild /path/to/nanoclaw
bash scripts/setup-host.sh --warm-cache /path/to/nanoclaw small
```

Setup flags:
- `--init`, `--check`, `--apply`, `--rebuild`, `--warm-cache`: primary modes.
- `--update`: with `--init`, preserve current values and add missing fields.
- `--force`: with `--init`, recreate manifest from scratch.
- `--force-overwrite`: with `--apply`, replace user-modified marked block.
- `--repair-anchor`: with `--apply`, restore Dockerfile anchor if missing.
- `--non-interactive`: skip prompts and require explicit values.
- `--service`, `--dockerfile`, `--compose-file`, `--skills-dir`, `--host-cache-dir`, `--model`: explicit values for non-interactive init.

Host requirements:
- Docker Compose `>= 2.20`; `--init` and `--apply` fail with exit `3` if not met.
- Debian/Ubuntu base image for V1; non-Debian/Ubuntu exits `3`.

## Runtime Behavior
Shared exit codes:
- `0`: ready
- `1`: warning only
- `2`: required dependency missing
- `3`: invalid config/schema/drift/unsafe target
- `4`: host setup required
- `5`: model cache/download/network failure

`setup-host.sh --check` runs doctor through Docker Compose and maps the same exit codes.

`--warm-cache` uses `docker compose run --rm <service>` so it does not require host Python deps or a running container.

Capability gating: `--apply` must run doctor first. If doctor reports a capability already satisfied, such as `ffmpeg` present in the image, `--apply` does not insert a marked block for that capability. Setup only patches missing capabilities.

Required doctor error patterns:
1. missing `faster-whisper`
2. wrong `faster-whisper` or `ctranslate2` version
3. missing `ffmpeg` or `ffprobe`
4. unwritable `HF_HOME` for effective UID/GID
5. insufficient disk for selected model
6. Hugging Face DNS or timeout
7. model unavailable or offline
8. PyAV/media decode failure
9. output path exists without `--overwrite`
10. permission denied writing transcript output
11. unsupported CUDA/GPU

Each pattern must map to cause and next command.

## Marked Blocks
Marker syntax:

```text
# >>> nanoclaw:whisper-transcribe v1 BEGIN sha256=<canonical-content-hash>
...content...
# <<< nanoclaw:whisper-transcribe v1 END
```

Hash is computed over content lines after canonicalization: normalize LF and strip trailing whitespace. Mismatch on `--apply` triggers drift stop unless `--force-overwrite`.

Dockerfile anchor:

```dockerfile
# nanoclaw:install-extensions
```

Dockerfile block inserted at that anchor:

```dockerfile
# >>> nanoclaw:whisper-transcribe v1 BEGIN sha256=<...>
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir faster-whisper==1.2.1 ctranslate2==4.7.1
ENV HF_HOME=/workspace/.cache/huggingface
# <<< nanoclaw:whisper-transcribe v1 END
```

User Compose top-level block:

```yaml
# >>> nanoclaw:whisper-transcribe v1 BEGIN
include:
  - ./.nanoclaw/compose.whisper.yml
# <<< nanoclaw:whisper-transcribe v1 END
```

Managed `.nanoclaw/compose.whisper.yml`, rewritten on every `--apply`:

```yaml
services:
  nanoclaw:
    volumes:
      - /var/lib/nanoclaw/whisper-cache:/workspace/.cache/huggingface
    environment:
      HF_HOME: /workspace/.cache/huggingface
```

Compose include block goes at top level before `services:`.

## Cross References
- PRD FR3 changes from "print pip install" to "route through doctor/setup guidance".
- `SKILL.md` Dependency Behavior points to `--doctor` and `setup-host.sh`.
- `SKILL.md` Help Mode mentions setup/check commands.
- Existing managed auto-update remains; updater integration is future contract only in V1.

## Updater Integration
V1 does not require changing `awesome-updater`.

Future contract: updater may return a `post_install` notice when a skill has `scripts/setup-host.sh`:
- `setup_required: true`
- `check_command`
- `apply_command`
- `docs_path: references/runtime-requirements.md`

Updater must never run host setup automatically.

## Out Of Scope V1
- Alpine support
- schema v2 migration
- GPU/CUDA validation
- Metal/macOS GPU validation
- multi-service setup
- patching Compose overlays
- changing transcription semantics
- automatic updater-run host setup

## Test Plan
- Unit tests for doctor JSON, exit codes, schema validation, degraded local mode.
- Temp fixture NanoClaw roots for host manifest/setup tests.
- Shell tests for `--init`, `--check`, `--apply`, `--update`, `--force`, `--repair-anchor`.
- Idempotency and drift tests for Dockerfile/Compose blocks.
- Backup retention and `.nanoclaw/setup.log` tests.
- Cache permission and disk-space tests.
- Validation script must pass without `faster-whisper`.
- Gated E2E: clean Docker fixture -> init -> check -> apply -> rebuild -> warm-cache -> transcribe tiny audio.

## Implementation Order
1. Write `runtime-setup-spec.md`.
2. Add manifest reader/validator.
3. Add doctor mode.
4. Add `setup-host.sh --init` and `--check`.
5. Add marked block engine and Compose include writer.
6. Add `--apply`, backups, audit log.
7. Add `--rebuild`, `--warm-cache`, non-interactive flags.
8. Add docs and future updater contract.
9. Add gated E2E.

## References Verified
- `faster-whisper` latest verified as `1.2.1`: https://pypi.org/project/faster-whisper/
- `ctranslate2` latest verified as `4.7.1`: https://pypi.org/project/ctranslate2/
- Hugging Face `HF_HOME` and derived `HF_HUB_CACHE`: https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables
