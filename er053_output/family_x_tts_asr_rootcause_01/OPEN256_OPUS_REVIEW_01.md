# OPEN-256 Opus独立レビュー(条件付き同意)転記

管理ID: FAMILY-X-TTS-ASR-ROOTCAUSE-01 / 委任_25(2026-10-11)。Fableから渡された要旨の転記(原文全文ではなく要旨+残条件)。
対象: 委任_23(commit cb94f3cb)の `validate_candidate_is_full_segment` 位置非依存化。

## 結論
条件付き同意。旧「先頭15文字一致」は文頭付近の変更を機械的に止める柵でもあったため、新ルールでは問題span±3 token窓(Gate6)内に限り、機械的な素通りが生じる。

## 指摘
- (A) 前置き・ラベル・引用符の付加が素通りする。例: `Here is the rewrite: Some calls through Muse ...`、先頭 `"` のみ付加。
- (B) 窓内の事実句削除・数字脱落が素通りする。`_WORD_RE=[A-Za-z']+` は数字を数えないため、`In 2024, Muse calls...` -> `Calls through Muse rose sharply.` が通る。
- 保持率0.6は英語ではGate7(0.7)と同尺度のため実害なし。
- 日本語は現経路に存在せず、Gate7がASCII語のみ計数するため純日本語は常に不合格。synthetic(日本語)検証は経路妥当性を示さない。

## 残条件(必須/推奨)
1. 必須: 窓内の追加・削除に機械的上限(span整合 or 編集予算。実記録90件のreplayで誤拒否が出ない案を採用)
2. 必須: 数値保持(原文の数字多重集合。ng span内の数字は除外)
3. 推奨: 先頭の引用符・ラベルは拒否(除去して通さない)
4. 推奨(緩和方向のため実施せず、OPEN候補として記録のみ): 短文の字数比緩和
5. 推奨: docstringに「英語TTS role専用、日本語経路は未対応」を明記

## 対応状況(委任_25)
1=span整合を採用(`check_span_consistency`) / 2=`check_numeric_preservation` / 3=`LEADING_QUOTE_OR_LABEL_ADDED` / 5=docstring明記 / 4=不実施(OPEN候補)。
replay・runtime結果は `OPEN256_REPLAY_01.md`、`open256_runtime_01/`。
