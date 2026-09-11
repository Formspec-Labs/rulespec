# Full-title XML reader scaling

**Both pinned titles completed with exact source-map checks. Full-title processing is feasible on this machine, but too costly to repeat for every reference or click.** The reader remains a whole-input preparation step; reuse its result or deliberately select smaller pinned source units with native title context.

| One process per title | Title 49 | Title 40 |
| --- | ---: | ---: |
| Input XML | 33.2 MB | 157.0 MB |
| Native nodes | 327,447 | 1,890,968 |
| Source-map entries | 219,625 | 1,314,169 |
| Reader elapsed | 1.59 s | 8.81 s |
| Reader CPU | 1.54 s | 8.60 s |
| Reader maximum RSS | 724.5 MB | 3,394.2 MB |
| Whole-probe maximum RSS | 724.5 MB | 3,616.6 MB |
| Whole-probe elapsed | 2.14 s | 11.32 s |
| Source-map reconstruction | Exact | Exact |

RSS is resident memory; Darwin reports these values in bytes. The whole probe includes authenticated file loading, reading, source-map verification and measurement overhead. Reader peak is sampled immediately after the reader returns. Inputs and results remain in process memory then; the full XML was never copied to an output artifact.

## Headroom and bounds

The host has 48 GiB RAM and 14 logical CPUs. Before testing, `memory_pressure -Q` reported 39% available, while swap already held about 19.2 GiB and load averaged about 19. Title 49's completed 691 MiB resident peak supported cautiously proceeding to Title 40. Each process exited before the next ran; titles were never held together by this probe.

Title 40's in-process memory-pressure snapshot reported 34% available. `/usr/bin/time -l` reported zero process swaps for both. System swap usage moved while unrelated workloads were active; that change cannot be attributed to this reader. No failed/refused run occurred. These are single observations under contemporaneous load, not capacity or latency promises.

The larger title has 4.73 times the input bytes and 5.77 times the nodes. Reader time increased 5.53 times and sampled peak RSS 4.68 times. This does not show an obvious quadratic increase. Code inspection finds one traversal plus binary lookups from node source intervals into the map: proportional to text/node work with a per-node logarithmic map lookup. It retains an XML tree, source/visible strings, nodes and maps, so low CPU complexity does not imply low memory use.

## Loading implication

- Do not parse the complete title once per citation. Prepare/index a selected source once per bounded session and reuse it.
- Do not make several full titles a mandatory concurrent input to ordinary extraction. A single 157 MB title used about 3.4 GB resident memory during reading on this run.
- A smaller exact section input is useful only if its original title/version context and source selector remain explicit. A bare section number does not establish its title or edition.
- This measurement does not require introducing a cache service, new parser or corpus rebuild. It informs the existing optional source-body loading choice.

The source module hashes in both run receipts match the frozen candidate from `upstream/source-freeze.json`. Later source edits are outside these measurements. Root was notified after Title 40 exited that the freeze was released for the separate native-address helper work.

## Reproducible evidence

- [Title 49 receipt](title-49.json), [OS process measurements](title-49.time.txt)
- [Title 40 receipt](title-40.json), [OS process measurements](title-40.time.txt)
- [Ratios and interpretation](comparison.json)
- `probe.py`: existing RefSpec reader and `read_verified_file_pin`; no network/model calls, full-title copies, builds, installs or commits.

Each receipt includes original source path, complete publisher manifest row, verified SHA-256/byte length, exact reader-module hashes, Python/platform, memory/load preflight, timings, RSS and source-map counts. Start receipts and logs preserve partial-run evidence should a future fresh run fail. Existing output files are refused rather than overwritten.
