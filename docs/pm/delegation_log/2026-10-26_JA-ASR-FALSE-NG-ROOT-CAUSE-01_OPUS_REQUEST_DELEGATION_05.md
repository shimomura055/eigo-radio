# Opus必須レビュー(11-3 条件C、短縮)｜JA-ASR-FALSE-NG-ROOT-CAUSE-01 便乗PASS是正E4のProduction適用前確認

## 前提
あなたの前回レビュー(`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/OPUS_REVIEW_01_OPEN333.md`)を受け、E3(P-1なし・値ガード多層防御)はProduction適用済み(commit `7953f5969`、`OPEN333_APPLY_RESULT_01.md`)。P-1はユーザー判断へ分離。本件は論点5(R-4)のE4。

## 読むもの(論点を絞る。追加探索可)
`OPUS_REVIEW_REQUEST_02_OPEN333_E4.md`(5論点)→ `OPEN333_E4_DESIGN_01.md`・`OPEN333_E4_EVAL_01.md`・`OPEN333_E4_APPLY_PLAN_01.md`・`OPEN333_E4_PREREGISTERED_01.md`・`proto_open333_fix_06.py`。Production: `er011_ja_asr_variant_layer_01.py`(304-306 `_cascade`、366-384 Candidate E)、`er007_ja_secondary_asr_01.py`(361-383 `_orthographic_reading_confirmed`、551-604 A4 signals)、`er078_asr_unified_judge_01.py`(148 A4、639-662 P1→P2→P3)。

## Sonnetの結論(要約)
- E4=Candidate Eの `_pass` 直前で、`protected.content_diffs` にcascade_eligible差分(entity_like/濁点差)が残っていれば既存 `_cascade()`(`ASR_VALIDATION_UNCERTAIN`)を返す1箇所(+14行)、rollback定数 `CANDIDATE_E_CASCADE_DIFF_RETURN=True`、fail-closed(例外→_cascade)、監視field `asr_judgement.candidate_e_cascade_return`。
- 評価1,638行: 非PASS→PASS 0、PASS→Cascade 74(合成neg 46・cost 24・実データ4=読み違い疑い2+正常等価表記2)、固有名詞負例PASS 46→0、ctrl変化0、決定性OK。Secondary受理の変化0(`ORTHOGRAPHIC_VARIANT_CONFIRMED`は混在diffsで開かない)。
- E4-N(数値entryでE3拒否→Cascade)は、拒否→Cascade 44行が全てHEADで `NG_EXCLUDED/p2_exclusion:A4_C2_HOMOGRAPH`(2026-10-11ユーザー逐語採用のA4)で、実効=A4解除=最終PASS到達可能性の拡大 → 見送り推奨(実データ影響0)。
- Fableの暫定判断: E4のみ適用、E4-N見送り(A4に触れるため採るならユーザー判断)。

## 論点(各々 同意/条件付き/不同意 と根拠、必要な修正M-n)
1. 既存 `_cascade` の再利用・1箇所の変更で、承認済み「entity_like/濁点差はCascade」へ戻す是正として十分か。新規PASS経路が開かない(Secondary側の許容集合EXACT/NORMALIZEDのまま、`ORTHOGRAPHIC_VARIANT_CONFIRMED`が混在diffsで閉じる)ことの確認。
2. E4後のUNCERTAINでA4 signalsが計算されない(TRUE_CONTENT_MISMATCH時のみ計算される既存構造)点の許容可否。安全側か。
3. E4-N見送り(A4解除に相当)の整理は妥当か。
4. E4の範囲(cascade_eligible全般 vs entity_like限定)。
5. 監視(1run 3件超で報告・初期3〜5 runでAzure一致率集計)と、`is_entity_like_mismatch_ja` が混在diffsでFalseになる副作用の扱い。
6. 適用計画(proto↔Production一致全キー・OFF=HEAD一致・回帰・注入発火確認)に欠けがあれば。

簡潔に。採用可否はFable/ユーザーが判断する。