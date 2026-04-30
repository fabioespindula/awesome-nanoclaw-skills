# Source Handling

Use this reference to label how much of the source was actually accessible. Be explicit before summarizing.

## Access Levels

| Access | Use When |
| --- | --- |
| `full article` | The main text, metadata, and enough body content were fetched directly from the source. |
| `partial` | Some meaningful source content was available, but sections were missing, truncated, script-rendered, or blocked. |
| `snippets only` | Only search snippets, previews, metadata, OpenGraph cards, or secondary snippets were available. |
| `transcript` | A video/audio transcript was available and used as the primary source. |
| `blocked` | The source could not be accessed and no reliable alternative content was found. |

## Confidence

| Confidence | Use When |
| --- | --- |
| `high` | Based on full article content or a usable transcript from the source. |
| `medium` | Based on partial source content plus credible metadata or reliable secondary context. |
| `low` | Based on snippets, previews, social metadata, or uncertain secondary sources only. |

## Fallback Behavior

- If paywalled, blocked, or script-rendered, say so.
- Try reasonable alternative sources only when available through the runtime: publisher snippets, archived metadata, transcripts, or reputable secondary coverage.
- Never imply the full source was read when it was not.
- For video, distinguish transcript-based analysis from visual analysis.
- For social posts, separate the post's claim from external verification.
- For undated sources, mark the date as unavailable and avoid calling it current.

## Required Source Note Examples

```md
Access: full article
Confidence: high
Source note: Summary is based on the original page content.
```

```md
Access: snippets only
Confidence: low
Source note: Original article appears blocked or unavailable. Summary is based on visible metadata/snippets, not the full text.
```

```md
Access: transcript
Confidence: high
Source note: Analysis is based on the video transcript, not visual inspection.
```
