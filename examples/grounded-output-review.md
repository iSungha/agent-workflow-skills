# Fictional grounded-output review

All source and answer text below is invented for this example.

## Source packet

`S1`: “The demo library opens at 9:00 a.m. on weekdays. It is closed on public holidays.”

## Generated answer

“The demo library opens at 9:00 a.m. on weekdays. It also opens on public holidays.”

## Claim findings

| Claim | Evidence | Label | Reason |
| --- | --- | --- | --- |
| Opens at 9:00 a.m. on weekdays | S1 | Supported | Time and weekday scope match. |
| Opens on public holidays | S1 | Contradicted | The source says it is closed on public holidays. |

Result: one supported claim and one contradicted claim. Report both counts and preserve the critical error; a single average score would conceal the contradiction. This two-claim example does not estimate general system accuracy.
