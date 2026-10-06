# fact_safety_p01 (判定なし/照合材料)
regex: duplicated(checker L428-446 equivalent)

## summary
```json
{
 "n_facts_after": 15,
 "n_facts_before": 15,
 "ungrounded_token_total": 4,
 "facts_with_ungrounded": [
  "MMHC-001",
  "MMHC-012",
  "MMHC-013"
 ],
 "negation_delta_total": -4,
 "causal_delta_total": 0,
 "newlines_total_draft": 0,
 "newlines_total_verif": 0,
 "claim_chars_mean_after": 77.2,
 "claim_chars_mean_before": 92,
 "claim_chars_ratio_after_over_before": 0.839,
 "notes_chars_mean_after": 51.6,
 "notes_chars_mean_before": 172.2,
 "m4_flagged_facts": [
  "MMHC-005",
  "MMHC-015"
 ],
 "notes_with_arbitrary_prefix": {
  "MMHC-001": "語義",
  "MMHC-004": "語義",
  "MMHC-007": "語義",
  "MMHC-009": "語義",
  "MMHC-011": "順序"
 },
 "format_issue_count_after": 0,
 "format_issue_count_before": 0,
 "draft_fact_ids_missing_in_txt": [],
 "txt_fact_ids_missing_in_draft": [],
 "txt_fact_ids_missing_in_verif": []
}
```
- 書式違反(非ASCIIキー行/ブロック内空行等) After 0件 / Before 0件

## 未接地トークン(fact別)
- MMHC-001: {"claim": {"proper": ["アシスタント", "パーソナル"]}}
- MMHC-012: {"notes_for_writer": {"numbers": ["1"]}}
- MMHC-013: {"notes_for_writer": {"proper": ["テスト"]}}

## 否定語・因果語 増減(Before類似fact比)
| fact | Before類似(J) | 否定 B→A | 因果 B→A | M4flag | claim文字 |
|---|---|---|---|---|---|
| MMHC-001 | MUSE-HC-006(0.148) | 2→0 | 0→0 | False | 78 |
| MMHC-002 | MUSE-HC-004(0.264) | 1→0 | 0→0 | False | 84 |
| MMHC-003 | MUSE-HC-007(0.327) | 2→3 | 0→0 | False | 79 |
| MMHC-004 | MUSE-HC-006(0.088) | 2→0 | 0→0 | False | 64 |
| MMHC-005 | MUSE-HC-009(0.136) | 1→3 | 0→0 | True | 68 |
| MMHC-006 | MUSE-HC-011(0.214) | 1→1 | 0→0 | False | 79 |
| MMHC-007 | MUSE-HC-012(0.511) | 1→0 | 0→0 | False | 112 |
| MMHC-008 | MUSE-HC-008(0.309) | 4→0 | 1→0 | False | 73 |
| MMHC-009 | MUSE-HC-013(0.878) | 1→1 | 0→0 | False | 119 |
| MMHC-010 | MUSE-HC-014(0.152) | 0→2 | 0→0 | False | 63 |
| MMHC-011 | MUSE-HC-005(0.208) | 1→0 | 0→0 | False | 70 |
| MMHC-012 | MUSE-HC-009(0.167) | 1→1 | 0→1 | False | 68 |
| MMHC-013 | MUSE-HC-001(0.238) | 1→2 | 0→0 | False | 79 |
| MMHC-014 | MUSE-HC-014(0.118) | 0→2 | 0→0 | False | 70 |
| MMHC-015 | MUSE-HC-002(0.08) | 2→1 | 0→0 | True | 52 |