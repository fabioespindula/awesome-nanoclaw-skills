# Mode Resolution

Choose one mode before running the script.

| Mode | Use When | Default Formats | Suggested Next Action |
| --- | --- | --- | --- |
| `quick` | User asks for normal transcription of one file. | `txt` | `Done` |
| `captions` | User asks for subtitles, captions, SRT, VTT, or video captions. | `srt,vtt` | `Generate captions` |
| `archive` | User asks to save everything, preserve an artifact, or create a reusable transcript package. | `all` | `Archive transcript` |
| `meeting` | User says meeting, call, voice note, decisions, action items, summary, pauta, ata, or follow-up. | `txt,transcript-md` | `Summarize meeting` |
| `batch` | User provides multiple local media files. | `txt` | `Review batch manifest` |
| `debug` | User asks why transcription failed, wants diagnostics, or is testing setup. | `txt,transcript-md` | `Inspect manifest` |

If multiple modes seem plausible, pick the mode that matches the requested output, not the file type. For example, a video can use `quick` if the user only wants text, and an audio file can use `captions` if the user asks for SRT.

Do not ask for mode unless the user's intent changes the result and cannot be inferred from the request.
