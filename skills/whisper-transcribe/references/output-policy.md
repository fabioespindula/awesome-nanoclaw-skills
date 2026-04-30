# Output Policy

The script writes selected transcript artifacts and always writes `manifest.json`.

## Formats

- `txt`: plain transcript, one segment per line.
- `srt`: subtitle blocks with comma millisecond timestamps.
- `vtt`: WebVTT subtitle blocks.
- `transcript-md`: Markdown transcript with metadata and transcript text.
- `all`: `txt,srt,vtt,transcript-md`.

## Destinations

Single-file default: write next to the source file when writable.

Workspace output: write under `/workspace/group/transcripts/<safe-stem>-<timestamp>/` when that workspace exists or can be created. If unavailable, use `./transcripts/<safe-stem>-<timestamp>/`.

Batch output: write all outputs and the consolidated `manifest.json` under one run folder. Prefer `--workspace-output` for batch runs.

Explicit output: write under `--output-dir`.

## Overwrite

Overwrite is false by default. If an output file or `manifest.json` already exists, the script fails before replacing it. Use `--overwrite` only when the user explicitly asks to replace existing artifacts.

## Manifest

`manifest.json` should include:

- run id and created timestamp
- mode and batch flag
- formats and output directory
- manifest path
- one source entry per media file
- source origin and origin confidence
- language, probability, model, device, compute type
- duration, segment count, word timestamp flag, word count
- access level, transcription confidence, transcript readiness
- output paths
