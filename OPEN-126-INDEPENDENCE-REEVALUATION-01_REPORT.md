# OPEN-126-INDEPENDENCE-REEVALUATION-01 実行報告

**種別: read-only再評価。編集・API呼び出し・Git操作は一切実施していない。**
**対象: OPEN-126(レベル間[A2/B1]数字粒度が偶然割れる論点)が「24.1%問題」
(強化版Numeric Precision配線[2026-09-07]以前の古いArtifact残存)と独立か。**

## 1. 論点の定義(原文引用)

`OPEN-112-THEME2-AUDIO-REVIEW-FIX-02-PREVIEW-NUMERIC_REPORT.md` (c)より:

> (c) **レベル差として意図されたものか(仕様上の根拠)** — **明確な意図は
> 確認できなかった(仕様の穴)**。…実際に観測された差は、(i)A2とB2が
> 独立した別のWriter生成物であること、(ii)Editor自体が"judgment rule,
> not mechanical"な非決定的LLM判断であること、の組み合わせによる**偶発的な
> 結果**であり、「B1は精密・A2は概数」という方針がSSOTのどこかに明文で
> 決定されているわけではない。

選択肢(同報告より):
- **選択肢1**: 現状維持。Editorの判断に委ねmonitoring対象とする。
- **選択肢2**: レベル別ガイダンス明文化(「A2は概数優先、B1はより高い精度を
  許容してよい」を追記)。
- **選択肢3**: 記事内一貫性ルール(レベル間一致は求めず、同一Fact源内での
  丸め一貫性のみ明文化)。

論点の実体: 「同一記事・同一数値がA2では丸め、B1では小数(または逆)」の
ように、**Editorが独立に判断するため、レベル間で数字の粒度・表現形式が
偶然一致しないことがある」構造的懸念。24.1%問題(強化配線前の生成物に
未丸めの小数が残っていた事象)とは別に、**配線後もこの構造自体は解消されない
はず**、というのが(c)の理論的主張。

## 2. 実データ検索結果

除外指示どおり`er011_output/open112_trend_theme2_b_final_audio_rerun_04/a2/`
と`er011_output/open112_trend_theme2_a2_numeric_check_01/`は参照していない。

強化版配線(`ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-
WIRING-01`、2026-09-07)のRuntime evidence自体
(`er011_output/preview_role_numeric_precision_wiring_01/numeric_precision_
evidence.json`)が、**同一記事に対しA2・B1双方を強化後Editorで実際に生成した
Production関数呼び出しの実データ**であり、両者のPromptに新規ブロック
`NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK`(CEFR非依存の既定文言)
が**完全一致で挿入されていること**を確認した(prompt全文中の該当段落を
diff確認、一字一句同一)。

### 実データ例(1件、強化配線後・同一記事・同一Fact)

Fact: 「29歳以下男性の趣味を深める旅行 24.3%」(同一記事・同一Ledger値、
Theme2 Trend記事)。

| | B1(`b1_editor_result.raw_text`) | A2(`a2_editor_result.raw_text`) |
|---|---|---|
| 出力表現 | "hobby-focused travel **was also about one quarter**" | "hobby-focused travel **showed a similar level**" |
| 数量情報の有無 | 概数だが**数量(約1/4)を残す** | **数量を一切残さず**定性表現のみ |

同じrunで同じLedger値・同じ強化後Prompt(Numeric Precision既定ブロック含む)
を使ったにもかかわらず、B1は近似数量表現、A2は非数量的な定性表現という、
**情報粒度が異なる結果**になった(response_id: B1=`resp_0cdc3b6d…`、
A2=`resp_02edb3da…`、いずれも`model: gpt-5.6-luna`、2026-09-07生成、
`preview_role_numeric_precision_wiring_01`配下で確認可能)。

なお同一runの他のFact(25.2%→両者"about 25%"、44.7%→両者"about 45%"、
24.1%→両者"about 24%")は完全一致しており、粒度が割れたのはこの1件のみ。
つまり**強化配線は機能しており(未丸め小数の残存という24.1%問題型の欠陥は
このrunには存在しない)、それでもなお別種の粒度差(数量情報の有無)が
非決定的に発生した**。

## 3. 判定根拠

- この例は**両方とも強化配線後**(新Numeric Precision既定ブロックが
  Prompt本文に確認できる)生成物であり、「配線前の古いArtifact」に起因
  するものではない。24.1%問題(配線前生成物に未丸め小数が残存)とは
  **発生条件が異なる**。
- 一方で今回見つかった粒度差は、(c)が例示した「小数 vs 整数」そのもの
  ではなく、「近似数量表現 vs 数量を含まない定性表現」という**やや異なる
  現れ方**だった。しかし根本原因(A2/B2が独立したEditor呼び出し、
  judgment ruleの非決定性)は(c)の主張と完全に一致する。
- コード根拠: `NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK`
  ・COMMON_BLOCK_TEMPLATEともCEFR分岐を持たず、A2/B2は別ファイル・別呼び出し
  (`ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01_
  REPORT.md` 3-2節、"A2/B2いずれのWriter初回呼び出しにも共通で使われる箇所、
  レベル分岐は追加していない")であるため、構造的にレベル間で結果が独立に
  ぶれる可能性は強化配線後も除去されていないことがコードからも確認できる。

## 4. 判定

**(a) 独立論点として残す(実データ例あり)** — 上記1件を実データ根拠とする。
24.1%問題(古いArtifact残存)とは異なる原因・異なるタイミング(配線後も
発生しうる)で発生する、構造的に別種の懸念であることを確認した。

推奨: OPEN-126は「24.1%問題と同根のclose候補」ではなく、独立した
`USER_DECISION_REQUIRED`として残すべき。既存の選択肢1/2/3(現状維持/
レベル別ガイダンス明文化/記事内一貫性ルール)から選ぶユーザー判断が
必要。ただし実運用への影響は「音声制作を止めるほどの安全性問題ではない」
(Ledger Deviation Checkは両表現ともCOMPLIANT)ため、緊急対応ではなく
通常のmonitoring/バックログ扱いが妥当と考える。

## 5. 使用ファイル一覧(read-only参照のみ)

- `OPEN-112-THEME2-AUDIO-REVIEW-FIX-02-PREVIEW-NUMERIC_REPORT.md`
- `NUMERIC-PRECISION-RETROACTIVE-AUDIT-01_REPORT.md`
- `ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01_REPORT.md`
- `er011_output/preview_role_numeric_precision_wiring_01/numeric_precision_evidence.json`
- 編集・API呼び出し・Git操作: なし
