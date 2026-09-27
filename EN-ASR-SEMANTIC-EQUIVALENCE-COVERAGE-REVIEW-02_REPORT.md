# EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_REPORT

管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02
日付: 2026-09-28
Phase: 1(原因分析+coverage再監査+設計案まで)
Status: **DESIGN_COMPLETED / Mandatory Opus L2 REVIEW PENDING**
性質: ¥0・API呼び出しなし・Production code変更なし・SSOT本体編集なし
(本REPORTは記載案のみ、`OPEN_ITEMS.md`/`CURRENT_SPEC.md`は未編集)。
設計全文: `docs/pm/design_en_asr_orthographic_equivalence_coverage_02.md`
先行SSOT: `EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT.md`、OPEN-184
(CLOSED、本件へ吸収済み)、OPEN-186(WIRING IN PROGRESS)。

## 背景
Phase A+B(`APPROVED_FOR_PRODUCTION`2026-09-27)配線後も、canonical
"Act One" vs ASR "Act 1" がValidator NGとなり、retry→cool-down→Local
Rewrite(本文改変)経由でしか合格しない事象が現行モデル・Flash-Lite
双方で再現した(`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-
X-01_REPORT.md` Phase 3、Gate項目14)。個別fixture追加ではなく、
包括対策として設計し直せるかを本Phaseで調査した。

## 主要な発見(コード実行・実データで確認済み)
1. Tier 1(`er021_en_asr_semantic_equivalence_production_01.py::
   tier1_numeric_equivalence()`)の数値語パーサ自体は"Act One"⇔"Act 1"
   を正しく等価と判定する(単独評価で確認)。**判定ロジックの誤りでは
   ない**。
2. 実際に失敗する原因は、同一segment内に同居する**無関係な**2つの
   表記差が、Tier 1の「セグメント全体のatom数完全一致」という
   all-or-nothing設計により、正しい判定ごと握りつぶされるため:
   (a) 打点略語(`U.S.`が4 atomへ分裂 vs `US`が1 atom)、
   (b) 裸digit+日付序数接尾辞(`13` vs `13th`)。
   いずれも**旧Validator(`er006_preprod_hardening_01_validation.py`)
   側には既に安全な対処が存在する**(`despaced()`ratio救済、
   `_DATE_ORDINAL_RE`の月名限定正規化)が、Tier 1は循環import回避のため
   独立実装しており、この2つを継承し損ねていた。
3. telemetry(`er021_output/.../telemetry.jsonl`、4,187件)を
   オフライン再分類。distinct 43件の`protected_number`NGのうち、
   本パターンに該当するのは実質1記事(Hormuz、複数run/phaseで計15回
   NG再掲)。残り大多数(27件)は正しく保護された真の値相違であり、
   **Tier1の既存安全性(false accept 0)は毀損されていない**ことも
   確認した。
4. Trial-01 corpus(68件、平均6語/最大17語)には打点略語・日付序数の
   fixtureが0件で、かつ「1文=1事象」設計だったため、複数事象同時発生
   時のみ顕在化する本件の脆弱性は構造的に検出され得なかった。

## 分類
- **(A)既承認範囲内の実装是正**(新しい意味等価カテゴリを追加しない):
  打点略語のatom結合前処理/日付文脈限定の序数接尾辞吸収(旧Validator
  ロジックの移植)/Tier1比較アルゴリズムを「全体zip」から
  「diff-anchored(SequenceMatcherでopごとに既存の許容基準を適用)」へ
  変更/hyphenated numeric・alphanumeric entityのハイフン吸収/
  meridiem略記のatom結合/Trial corpusへの長尺・複合fixture追加。
- **(B)新しい意味等価ルール(USER_DECISION_REQUIRED、採用しない)**:
  日付文脈以外での裸digit序数接尾辞の一般吸収(基数/序数の意味差を
  壊すため)/複合語分かち書きをTier1へ複製/ローマ数字小文字許容。

## 推奨設計案
案1(現状+個別パッチのみ)/案2(個別パッチ+diff-anchored比較への変更)/
案3(意味parse層の全面刷新)を比較し、**案2を推奨**。理由: 今回の実例を
確実に解消しつつ、変更範囲が`er021`内部のみ(呼び出しシグネチャ・
role gate・telemetry・Tier3救済ロジックは無変更)、新しい許容ルールを
一切追加しないため既存のNEGATIVE安全性を維持したまま、「未知の3つ目の
穴」による同種再発を構造的に防げる。詳細は設計書§3。

## 全経路確認
初回・retry・fallback・Local Rewrite前後・Secondary ASR cascade・
Human Review Lock直前は、いずれも単一wrapper(`classify_asr_match()`)
と単一role gate関数を経由しており、**配線の不整合は無い**。Tier1本体
の修正のみで全経路へ同時に効果が及ぶ(設計書§4)。

## 詳細
`docs/pm/design_en_asr_orthographic_equivalence_coverage_02.md`
(E-1原因分析、E-2 coverage matrix[23カテゴリ、実行結果付き]、E-3設計案
比較、E-4全経路確認表、分類A/B、Positive/Negative test設計、Opus L2
申し送り8点、SSOT記載案)。

## 次のステップ
Mandatory Opus L2レビュー(Fable発火)。本Phaseでは実装・Trial・
Production変更は一切行っていない。

---
Management-ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02
