# Challenge Round

Use this file for the anonymous peer-review stage after the five independent advisor answers exist.

Use NanoClaw's `Agent` tool for peer review. Default to five neutral review agents. If the runtime cannot support five, use three reviewers rather than skipping review.

## Reviewer Input

Each reviewer receives:

- the neutral user question
- relevant context
- five anonymized responses labeled Response A-E
- no identity map

Do not tell a reviewer which response they wrote. If the reviewer suspects authorship, instruct them to ignore that and review only content quality.
Do not include the identity map, advisor names, role names, or role-specific headings in any reviewer packet.

## Reviewer Prompt

```text
You are reviewing anonymized council responses.

Language: match the user's dominant language.
Do not speculate about who wrote each response.
Do not rewrite the whole answer.

For each Response A-E, score 1-5:
- insight
- correctness
- actionability
- risk coverage

Then provide:
1. Top 2 responses and why.
2. Weakest response and why.
3. Best single idea across all responses.
4. Biggest unresolved blind spot.
5. One sentence the chairman should not ignore.

User question:
<QUESTION>

Responses:
<ANONYMIZED_RESPONSES>
```

## Review Output Format

```markdown
## Scores

| Response | Insight | Correctness | Actionability | Risk Coverage |
| --- | ---: | ---: | ---: | ---: |
| A |  |  |  |  |
| B |  |  |  |  |
| C |  |  |  |  |
| D |  |  |  |  |
| E |  |  |  |  |

## Ranking

Top 2:
Weakest:

## Notes

Best idea:
Blind spot:
Do not ignore:
```

## Aggregation Guidance

Aggregate peer review by anonymized response label first. Only map labels back to advisor names after scoring is complete. Use reviewer scores as evidence, not as a vote that automatically decides the final answer.

If reviewers disagree sharply, preserve that disagreement for the chairman instead of averaging it away.
