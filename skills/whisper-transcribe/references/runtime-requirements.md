# Runtime Requirements

Use this reference when Whisper Transcribe fails dependency checks or when the user asks how to prepare a NanoClaw runtime.

## Required Runtime

- NanoClaw Docker runtime with skills under `container/skills`.
- Debian/Ubuntu-based image for v1.
- Docker Compose `>= 2.20` on the host.
- Python 3.10+ in the container.
- `ffmpeg` and `ffprobe` in the container.
- `faster-whisper==1.2.1` and `ctranslate2==4.7.1` in the container.
- Persistent Hugging Face cache mounted from `/var/lib/nanoclaw/whisper-cache` to `/workspace/.cache/huggingface`.

## First-Time Setup

From the NanoClaw runtime root:

```bash
bash container/skills/whisper-transcribe/scripts/setup-host.sh --init .
bash container/skills/whisper-transcribe/scripts/setup-host.sh --check .
bash container/skills/whisper-transcribe/scripts/setup-host.sh --apply .
bash container/skills/whisper-transcribe/scripts/setup-host.sh --rebuild .
bash container/skills/whisper-transcribe/scripts/setup-host.sh --warm-cache . small
```

`--init` creates `.nanoclaw/host.json` for this host. The file is environment-specific and should not be committed. Commit `.nanoclaw/host.example.json` if the runtime repo needs a template.

## Doctor

Run inside the skill directory:

```bash
python3 scripts/whisper_transcribe.py --doctor
python3 scripts/whisper_transcribe.py --doctor --json
```

The doctor is designed for the container. When run on macOS/local Python it reports degraded CPU-only validation and may show missing dependencies that actually belong in the container.

## Cache And Disk

The model cache should persist across rebuilds. Default paths:

- host: `/var/lib/nanoclaw/whisper-cache`
- container: `/workspace/.cache/huggingface`
- env: `HF_HOME=/workspace/.cache/huggingface`

Conservative free-space targets:

- `small`: 2GB
- `medium`: 4GB
- `large-v3`: 8GB

If the cache exists but is not writable, fix ownership for the UID/GID used by the container before transcribing.

## Safety

The setup assistant never installs host dependencies silently. It writes host/container files only when the user runs `setup-host.sh --apply`, creates backups first, and logs changes to `.nanoclaw/setup.log`.
