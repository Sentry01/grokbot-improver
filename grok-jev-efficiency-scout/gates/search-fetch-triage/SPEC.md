# Gate: search-fetch-triage

**Name:** Search / Fetch Result Triage  
**Slug:** `search-fetch-triage`  
**Rank / source:** #6 in `cool-use-cases.md`  
**Primary lever:** cost / latency

## Purpose

After search / list tools, score each hit cheaply and keep only useful evidence before deep Read/Fetch. Avoids stuffing every snippet into context.

## When to call

After search / list tools, before deep Read / WebFetch / browser extract. Batch map-reduce friendly (one call per hit or batched).

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `goal` | string | User / agent goal |
| `result_title` | string | Hit title |
| `snippet` | string | Short snippet |
| `source` | string | Origin domain / tool |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `keep` | `noul` | Keep for answer / deeper fetch |
| `utility` | `score` | irrelevant → weakly related → useful supporting → core evidence |

No free-text questions.

## Thresholds

- **Keep** if `keep.noul >= 0.55` **OR** `utility.score >= 1.5`
- Else **drop**
- Harness may still keep top-N by utility among keep decisions

## Fail mode

**Fail-open** → `keep` (prefer retaining candidates / top-N) on API error.

## Expected efficiency win

Cost + latency — cheap triage before expensive deep reads.
