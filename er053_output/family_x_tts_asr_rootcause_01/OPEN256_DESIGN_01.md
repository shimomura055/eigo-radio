# OPEN-256 設計メモ: Local Rewrite「全文性」検証の位置非依存化

管理ID: FAMILY-X-TTS-ASR-ROOTCAUSE-01 委任_23 / 対象: `er020_tts_retry_local_rewrite_01.py` `validate_candidate_is_full_segment()` のみ
状態: 実装・offline test済み。runtime evidence・SSOT更新は後続(PRODUCTION_WIREDではない)。

## 1. 旧ロジック
`rewritten[:15].strip().lower() == canonical[:15].strip().lower()` のみ。LLMが置換句だけを返す不具合の安全網だが、問題語が先頭15文字内(例 "Some Muse calls")だと正当な全文候補も拒否。副作用として、先頭が同じなら断片や途中切れでも通る(全文性は実は未検証)。

## 2. 7 Gateの構成(不変)
Luna QA 1-5(意味保存/role保持/Fact非矛盾/文脈接続/自然さ) + Gate6(変更が問題語周辺窓内 `check_locality`) + Gate7(unchanged_ratio>=0.7)。`all_seven_gates_pass = qa有 AND is_full_segment AND 7 Gate全True`。全文性は7 Gateの前段の独立条件で、本変更はこの1関数のみ。

## 3. 新方式(位置非依存)
全条件を満たす場合のみ全文性OK。判定理由はreason codeで返す。
| 順 | 条件 | reason(不合格時) | 目的 |
|---|---|---|---|
| 1 | 空でない | EMPTY | |
| 2 | 候補が原文の真部分文字列でない | FRAGMENT_SUBSTRING_OF_ORIGINAL | 置換句のみ/原文の一部のみ |
| 3 | 文字数比 >= 0.7 | TOO_SHORT_FRAGMENT | 断片・途中切れ・置換句のみ |
| 4 | 文字数比 <= 1.5 | TOO_LONG_OVER_EXPANDED | 過剰追記 |
| 5 | 文終端(. ! ? 。！？ …、閉じ引用/括弧は除外して判定)の有無が原文と一致 | TERMINAL_PUNCTUATION_MISMATCH | 不完全文 |
| 6 | 原文トークン保持率(difflib、位置非依存) >= 0.6 | LOW_ORIGINAL_COVERAGE_OVER_MODIFIED_OR_UNRELATED | 無関係文・過度変更 |
英語は単語トークン、ASCII語が無い(日本語等)場合は文字単位で保持率を計算。

## 4. しきい値の根拠(offline、API 0)
`er011_output/local_rewrite_recovery/**` の実候補90件(旧rule採択76/拒否14)で検証。
- 旧採択76: 保持率min 0.6875、文字数比 0.944-1.194、終端不一致0件。
- 旧拒否14(META comment_2候補5件 + Gemini 3.8 A/B trial の文頭置換9件): すべて実際は全文(保持率min 0.9167、文字数比 1.005-1.078)。
- よって 保持率>=0.6 / 文字数比 [0.7, 1.5] は、実採択を全て残しつつ断片を十分遠ざける(断片・置換句のみは文字数比 約0.2-0.5)。保持率床0.6はGate7(0.7)より緩いが、Gate7は独立に不変で適用されるため最終的な過度変更拒否は従来どおり0.7。
- 実記録に「置換句のみ」の旧拒否は無い(0件)ため、拒否側はsynthetic(新test)で検証。

## 5. 安全性が緩まない根拠
- 旧ruleが通していた「先頭一致だが断片/途中切れ/過剰追記」は新ruleで拒否される(厳格化)。
- 緩和されるのは「先頭15文字が違うが、全文・終端あり・原文と長さ同等・原文トークン大半保持」の候補のみ=正当な文頭置換。これらは依然として意味保存/Fact/自然さ/Gate6/Gate7/再TTS+ASR再検証を全て通る必要がある。
- 関数シグネチャ(bool返却)・呼出契約不変。診断用 `diagnose_candidate_full_segment()` を追加し、recordへ `full_segment_check`(ok/reason/length_ratio/orig_coverage)を追加(既存キーは不変)。

## 6. 範囲外
`er020_tts_local_rewrite_natural_english_qa_trial_02.py` にも同名旧関数があるがTrial専用でProduction経路から未使用のため不変更。

---
## 追記(委任_25、2026-10-11): Opus是正後の最終ルールと全Family影響表

### 7. 是正後の全文性検証(`diagnose_candidate_full_segment`、Production経路では `check_span=True`)
上記3節の6条件に加えて追加(順序は実装順):
| 追加条件 | reason | 目的 |
|---|---|---|
| 先頭の引用符/ラベル付加(`^\s*["“‘'(]` / `^\w+\s*\d*:\s`、原文側が同じ形なら対象外)を拒否 | LEADING_QUOTE_OR_LABEL_ADDED | 前置き・ラベル混入(除去せず拒否) |
| 原文の数字多重集合(ng span内の数字は除外)が候補に残る | NUMERIC_TOKEN_LOST | 窓内の数字脱落 |
| 候補の申告span(before->after)を原文へ適用した結果が候補全文とトークン一致 | SPAN_INCONSISTENT_UNDECLARED_CHANGE / SPAN_BEFORE_NOT_DECLARED | 窓内の申告外の追加・削除 |
英語TTS role専用。日本語経路は未対応(Gate7がASCII語のみ計数)。実記録90件replayで旧採択76件に誤拒否0(`OPEN256_REPLAY_01.md`)。

### 8. 全Family影響表(是正後差分の追記)
変更は共通primitive `er020_tts_retry_local_rewrite_01.build_full_candidate_records` 1箇所(呼出契約・戻り値の既存キー不変、recordに`full_segment_check`追加のみ)。
| 呼出元(Local Rewrite回復) | 対象 | 影響 |
|---|---|---|
| `er003_v1_crosslevel_audio_02_common._local_rewrite_recovery_for_english_segment_with_fallback` | A2/Family X等の英語本文segment | 全文性判定のみ変更(runtime evidence取得: open256_runtime_01) |
| `er003_v1_sing01_voice01_generate._local_rewrite_recovery_for_charon_english` | B1B charon英語 | 同上(同一primitive) |
| `er003_v1_sing01_news_tail_fix._local_rewrite_recovery_for_news_narration` | B1B news英語 | 同上 |
| `er003_v1_n3_01_tts_generate` | N3 | 同上 |
| 日本語経路(er007等) | 日本語 | 呼出なし(未対応のまま、変更なし) |
| `er020_tts_local_rewrite_natural_english_qa_trial_02.py` | Trial専用 | 未使用・不変更(同名旧関数は据え置き) |
Dangling Reference Check: 旧定数 `FULL_SEGMENT_PREFIX_CHECK_CHARS` への参照は Trial_02 自身の定義以外に0件。`er053_dangling_reference_check_01.py`+test 4件PASS(本変更に起因する孤立参照0)。
