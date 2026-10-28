# WIRING_DESIGN_01 (NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_01a)

Status: 設計(実装前)。作成中。本ファイル§3(候補JSON schema)を先行確定し、並行01b(`PROMPT_TRIAL_01.md` / `prompt_trial_01.json`)が参照する。残節は順次追記。

## §3 ニュアンス解説 候補JSON schema (v1・先行確定)

1記事×1レベルにつき `nuance_candidate_<family>_<article>_<level>.json` を1ファイル。候補は0〜1件(`candidate` が null なら候補なし)。

```json
{
  "schema": "nuance_candidate_v1",
  "family": "X|Y|Z",
  "article_id": "string",
  "level": "standard|advanced",
  "generated_at": "ISO8601",
  "candidate": null,
  "no_candidate_reason": "string|null",
  "kp_word_basis": {"status": "confirmed|provisional", "items": ["expr1", "..."], "source_path": "string"},
  "model": "string",
  "prompt_sha": "sha256 hex of the full prompt template",
  "usage": {"input_tokens": 0, "output_tokens": 0, "cost_jpy": 0.0}
}
```

`candidate` が非nullのとき:

```json
{
  "expression": "英語表現(例: 'quite' vs 'rather')。解説の中心的な学習対象",
  "focus": "学習上の焦点を1行(日本語)。重複判定の主入力",
  "explanation_ja": "日本語解説(Part 1の1項目相当、目安120〜260字)",
  "quote_en": "本文からの英語引用(逐語。本文に実在すること)",
  "quote_ja": "quote_enの和訳",
  "overlap_check": {
    "verdict": "pass|fail",
    "stage1_structural": {"verdict": "pass|fail", "matched": ["..."]},
    "stage2_llm": {"verdict": "pass|fail|skipped", "reason": "string", "model": "string"},
    "reason": "最終判断の理由(日本語1〜2文)",
    "against": [{"item": "KP/Word表現", "kind": "kp|word", "same_focus": false, "note": "string"}]
  }
}
```

規則:
- `overlap_check.verdict == "fail"` の候補はHR提示前に破棄し、`candidate=null`・`no_candidate_reason="overlap_ng"`にする(代替の自動補充なし)。破棄前の候補は `rejected_candidate_audit`(別キー、HRには出さない)に監査用に残す。
- `against[]` は比較したKP/Word全件(最大5件)を列挙する。
- 01bの暫定schemaが異なる場合は、フィールド名の差分を01bのPROMPT_TRIAL_01.mdに明記すること。
