# Identity Shuffle

Use this process to make peer review anonymous.

## Inputs

```text
advisor_responses = [
  { advisor: "Red Team", content: "..." },
  { advisor: "Axiom", content: "..." },
  { advisor: "Horizon", content: "..." },
  { advisor: "Streetlight", content: "..." },
  { advisor: "Operator", content: "..." }
]
```

## Process

1. Validate that all five responses exist.
2. Remove advisor names and role-specific headings from the review packet.
3. Shuffle the five response objects. Do not preserve roster order as Response A-E.
4. Assign labels `Response A` through `Response E`.
5. Store the identity map privately for chairman synthesis.
6. Send only the anonymized packet to reviewers.
7. Aggregate reviewer scores and comments by anonymous label.
8. Rejoin anonymous labels to advisor identities only after peer review is complete.

If a response contains a self-identifying sentence such as "As Red Team", remove that phrase before review while preserving the substantive content.

## Identity Map Format

Save this privately in the transcript when filesystem access is available:

```markdown
# Identity Map

| Anonymous Label | Advisor |
| --- | --- |
| Response A |  |
| Response B |  |
| Response C |  |
| Response D |  |
| Response E |  |
```

Do not include the identity map in the user-facing Telegram summary.
Do not tell a reviewer any advisor identity before peer review is complete.

## Fallback

If there is no filesystem access, keep the identity map only in session state until the chairman synthesis is complete.
