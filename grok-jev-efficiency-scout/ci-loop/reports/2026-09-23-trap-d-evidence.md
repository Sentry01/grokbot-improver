# Trap C+D — evidence_sources fix (2026-09-23)

**As of:** 2026-09-23 11:10:13 AEST  
**Gate:** `send-to-user-quality`  
**Fix:** SPEC + optional `evidence_sources` + Jev question instructions (user decision ~11:08 AEST)  
**Thresholds:** `ready_to_send_min=0.65`, `send_quality_min=2.0` (unchanged)

## Results

| Trap | Expected | Action | ready | quality | defect | Correct? |
| --- | --- | --- | ---: | ---: | --- | --- |
| C (vague, empty evidence) | hold/revise | `revise` (proceed=False) | 0.02 | 0.7 | `incomplete` | YES |
| D (Fed draft + evidence_sources) | send | `send` (proceed=True) | 0.92 | 2.61 | `none` | YES |

**Trap D cleared:** yes — ready 0.92 ≥ 0.65, quality 2.61 ≥ 2.0, defect=`none` (not unsupported).

## Notes

- Baseline detail: `ci-loop/baselines/trap-cd-evidence-2026-09-23.json`
- Proposal resolution updated to option 1 (SPEC + evidence_sources); threshold not cut further
- `jev_client.py`: added User-Agent so Cloudflare Error 1010 does not block urllib (curl with UA worked; bare urllib 403’d)
- No API key in artifacts
