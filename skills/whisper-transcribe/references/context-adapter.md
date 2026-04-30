# Context Adapter

Use available context to set source metadata without inventing facts.

Priority order:

1. Current user request.
2. Runtime attachment metadata from Telegram, Slack, Discord, or another chat surface.
3. Forwarding metadata such as Telegram `forward_origin`, `forward_from`, or `forward_date`.
4. File path, filename, caption, or adjacent chat text.
5. Workspace instructions such as `AGENTS.md` or `CLAUDE.md`, if relevant.
6. No extra context.

## Source Origin

Use these values:

- `forwarded`: runtime metadata explicitly says the media was forwarded.
- `inferred-forwarded`: filename, caption, or chat text strongly suggests forwarding, but platform metadata is unavailable.
- `direct-upload`: runtime metadata says the user uploaded or attached it directly.
- `local-file`: user gave a normal local file path.
- `unknown`: no reliable origin information.

## Origin Confidence

- `explicit`: comes from platform/runtime metadata.
- `inferred`: comes from filename, caption, or chat wording.
- `unknown`: no reliable basis.

Do not label audio as forwarded based only on the audio content. The transcript can say "this was forwarded", but that is a speaker claim, not transport metadata.
