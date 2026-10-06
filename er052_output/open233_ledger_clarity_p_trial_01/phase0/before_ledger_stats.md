# fact_safety_p01 (判定なし/照合材料)
regex: duplicated(checker L428-446 equivalent)

## summary
```json
{
 "n_facts_after": 15,
 "n_facts_before": 15,
 "ungrounded_token_total": 14,
 "facts_with_ungrounded": [
  "MUSE-HC-002",
  "MUSE-HC-003",
  "MUSE-HC-004",
  "MUSE-HC-010",
  "MUSE-HC-011",
  "MUSE-HC-013",
  "MUSE-HC-014",
  "MUSE-HC-015"
 ],
 "negation_delta_total": 0,
 "causal_delta_total": 0,
 "newlines_total_draft": 0,
 "newlines_total_verif": 0,
 "claim_chars_mean_after": 92,
 "claim_chars_mean_before": 92,
 "claim_chars_ratio_after_over_before": 1.0,
 "notes_chars_mean_after": 172.2,
 "notes_chars_mean_before": 172.2,
 "m4_flagged_facts": [],
 "notes_with_arbitrary_prefix": {},
 "format_issue_count_after": 0,
 "format_issue_count_before": 0,
 "draft_fact_ids_missing_in_txt": [],
 "txt_fact_ids_missing_in_draft": [],
 "txt_fact_ids_missing_in_verif": []
}
```
- 書式違反(非ASCIIキー行/ブロック内空行等) After 0件 / Before 0件

## 未接地トークン(fact別)
- MUSE-HC-002: {"claim": {"proper": ["マシン"]}, "conditions": {"proper": ["サービス"]}}
- MUSE-HC-003: {"claim": {"proper": ["Secure", "エージェント"]}, "notes_for_writer": {"proper": ["コンシェルジュ"]}}
- MUSE-HC-004: {"claim": {"proper": ["ユーザー"]}, "notes_for_writer": {"proper": ["ページ"]}}
- MUSE-HC-010: {"claim": {"proper": ["ユーザー"]}}
- MUSE-HC-011: {"conditions": {"proper": ["ケース"]}}
- MUSE-HC-013: {"claim": {"proper": ["テスト"]}, "notes_for_writer": {"proper": ["ユーザー"]}}
- MUSE-HC-014: {"notes_for_writer": {"proper": ["コンシェルジュ", "ロールバック"]}}
- MUSE-HC-015: {"claim": {"proper": ["アクセス"]}}

## 否定語・因果語 増減(Before類似fact比)
| fact | Before類似(J) | 否定 B→A | 因果 B→A | M4flag | claim文字 |
|---|---|---|---|---|---|
| MUSE-HC-001 | MUSE-HC-001(1.0) | 1→1 | 0→0 | False | 76 |
| MUSE-HC-002 | MUSE-HC-002(1.0) | 2→2 | 0→0 | False | 93 |
| MUSE-HC-003 | MUSE-HC-003(1.0) | 2→2 | 0→0 | False | 119 |
| MUSE-HC-004 | MUSE-HC-004(1.0) | 1→1 | 0→0 | False | 82 |
| MUSE-HC-005 | MUSE-HC-005(1.0) | 1→1 | 0→0 | False | 93 |
| MUSE-HC-006 | MUSE-HC-006(1.0) | 2→2 | 0→0 | False | 110 |
| MUSE-HC-007 | MUSE-HC-007(1.0) | 2→2 | 0→0 | False | 91 |
| MUSE-HC-008 | MUSE-HC-008(1.0) | 4→4 | 1→1 | False | 101 |
| MUSE-HC-009 | MUSE-HC-009(1.0) | 1→1 | 0→0 | False | 92 |
| MUSE-HC-010 | MUSE-HC-010(1.0) | 2→2 | 0→0 | False | 94 |
| MUSE-HC-011 | MUSE-HC-011(1.0) | 1→1 | 0→0 | False | 72 |
| MUSE-HC-012 | MUSE-HC-012(1.0) | 1→1 | 0→0 | False | 102 |
| MUSE-HC-013 | MUSE-HC-013(1.0) | 1→1 | 0→0 | False | 103 |
| MUSE-HC-014 | MUSE-HC-014(1.0) | 0→0 | 0→0 | False | 67 |
| MUSE-HC-015 | MUSE-HC-015(1.0) | 1→1 | 0→0 | False | 85 |