# What repeats in the current requests

These measurements use the already committed full CSBG captures. They describe
the current runtime, not a new optimized run. [profile.json](profile.json) records
per-window values; [profile.py](profile.py) reconstructs them without provider calls.

| Whole chapter | Normal windows | Section windows |
|---|---:|---:|
| Requests | 6 | 27 |
| Focus-source characters | 135,797 | 135,797 |
| Provider-recorded input tokens | 70,772 | 121,039 |
| Provider-recorded output tokens | 58,413 | 81,119 |
| Prompt-content characters | 227,961 | 417,533 |
| Compact serialized schema characters | 68,628 | 308,826 |
| Repeated instruction text characters | 42,696 | 192,132 |
| Repeated compact section-index characters | 8,790 | 39,555 |
| Passage-catalog characters | 173,452 | 172,235 |

The core instruction text is 7,116 characters, the compact section-index JSON is
1,465, and the compact schema JSON is 11,438 per call. The windows agent reports
7,120 for the entire instruction prefix including separator newlines and 1,523
for the index with its prose label; these are compatible boundary definitions.

Do not add the character figures to token counts or assume a fixed conversion.
The schema's wire representation is not proof of its exact model-context encoding.
The provider's input-token counters, however, establish that the same source uses
50,267 more input tokens with the current section schedule. Context and focus
boundaries also differ, so not all of this delta is attributed to one header.

Eight section requests contain fewer than 2,400 focus characters. Each still
reports roughly 3,000–3,856 input tokens. The preamble call is not empty: it extracts
one codification/history statement. Silently dropping it would change the selected
content scope. Section notes are likewise source content, not free-to-delete noise.

## Smaller source presentation is a separate, untested candidate

The model selects `F`/`C` IDs. Local code already retains every passage's exact
coordinates. Replacing model-visible `{start,end,text}` values with text-only
values under the same IDs would reduce the B catalog's compact representation
from 172,235 to 143,053 characters: **29,182 characters**, or 7.0% of current prompt
content characters. This omits no selected source text and changes no local
coordinate table. It has not been sent to the model, so it is not a measured token
or quality improvement. Any test must retain enough section identity to interpret
local references; removing all section context is a different intervention.

Do not strip CUE descriptions as a shortcut. Their effect is not equivalent to
removing duplicated machine coordinates, and the live omission study shows that
apparently smaller schemas can change the model's segmentation behavior.

## Existing caching and optional non-urgent transport

The saved B run reported 4,600 cached input tokens out of 121,039. Google's current
documentation says implicit caching is automatic and lists a 4,096-token threshold
for Gemini 3.8 Flash. Many small CSBG calls fall below that total. Common-prefix
placement and sending related requests close together can help, but cache hits
are not guaranteed. Do not pad prompts or add a cache-management subsystem merely
to meet the threshold. [Official caching guidance](https://ai.google.dev/gemini-api/docs/caching)

For non-urgent corpus work, Google's Batch API accepts independent structured-
output requests at 50% of standard cost with a target turnaround of 24 hours.
That preserves one logical model request per window; one batch submission is not
one model call. It changes delivery time and billing, not the amount of source or
generated meaning. This repository has no qualified batch extraction adapter, and
the investigation did not submit a batch job. It would add job/result/error handling,
so implement it only when a real non-urgent workload warrants that complexity.
[Official Batch API guidance](https://ai.google.dev/gemini-api/docs/batch-api)

Provider documentation was checked September 14, 2026. Neither external feature's
cost or speed benefit was measured by this experiment.
