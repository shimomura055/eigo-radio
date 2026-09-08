# FAMILY-A-POINT-OVERLAP-COUNTERMEASURE-PRE-AUDIT-01

管理ID: FAMILY-A-POINT-OVERLAP-COUNTERMEASURE-PRE-AUDIT-01(Lane A)。
種別: 読み取り専用の事前監査(編集・Trial実行・API呼び出し・Git操作なし)。

## 背景
Point Overlap Loop Budget到達(閾値0.40、`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`)が
高頻度([`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04_REPORT.md`]、
baseline A2で3 run中2 run(67%)がNG_REVIEW_REQUIRED、runtime evidence
`er011_output/daily_news_focus_layer_comparison_trial_04/a2/baseline/run{1,2,3}/
point_overlap_article_retry_log.json`で実測確認)。分散低減Trial案
(a) 初回Point生成Promptの語彙回避原則強化 / (b) Diagnostic Full Retry診断情報の
具体化、に入る前に既存対策の実装状況を確認した。

---

## 1〜2. 現行ProductionでOverlap NG時にWriterへ何を返しているか

### 経路(`er003_v1_n3_01_articles_generate.py::run_one_pattern()` 809-960行)
1. Writer初回生成(`_generate_and_compress_article`) →
2. `run_point_overlap_qa_and_regenerate()`(675-743行)でPoint One/Two×Full Story
   のlexical overlap(`er008_point_overlap_qa_18.py::flag_possible_paraphrase`、
   閾値`OVERLAP_FLAG_THRESHOLD=0.40`)+Point One×Point Two相互overlapを計算 →
3. `flagged`ならDiagnostic Full Retry(`build_diagnostic_retry_prompt()` 611-627行)
   でprompt末尾に診断sectionを追加し、Point Role Planningを再計画したうえで
   記事全体をWriterから再生成(最大`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`回、
   856-943行)。2回失敗すると`status="NG_REVIEW_REQUIRED"`で打ち切り、
   Fact Checker以降は実行しない(946-957行)。

### Writerへ実際に渡されるfeedbackの全文構造
`er009_diagnostic_full_retry_modules_12.py::DIAGNOSTIC_SECTION_TEMPLATE`(60-86行)。
実際に埋め込まれる値は`build_diagnostic_section()`(89-108行)が生成:

```
[Previous attempt — NG example of semantic overlap, do NOT patch or reuse]
...
Previous Full Story:
{previous_full_story}                          ← 前回のFull Story本文(逐語、全文)

Previous Point One (overlap_ratio={score}, flagged={bool}):
(Point One body from previous attempt)          ← ハードコードされた固定文字列(後述)
Diagnosis: shared content words with the Full Story: {shared_words[:12]}...
  Likely overlap type: {classify_overlap()の粗い分類}

Previous Point Two (同様)
...
Rules for this new attempt: (全文書き直し・Point単独/paraphraseのみでの修正禁止 等)
```

- `overlap_ratio`・`flagged`・`threshold`(0.40)・`shared_words`(実際に重複した
  content word一覧)は`er008_point_overlap_qa_18.py::flag_possible_paraphrase()`
  (75-80行)がそのまま返す値であり、Writerへ渡る診断は**単なる「NG」ではなく、
  スコア・重複した具体語・粗い重複タイプ分類(evidence/implication/cause/generic、
  `classify_overlap()` 34-48行)まで含む**。
- 実runtime evidence(`point_overlap_article_retry_log.json` attempt0、
  `daily_news_focus_layer_comparison_trial_04/a2/baseline/run1/`)で
  `shared_words=["attack","came","control","game","hanshin","hiroshima","home",
  "lead","montero","only","run","score","solo"]`, `overlap_ratio=0.5`を実際に
  確認した。

### 重要な欠落(コードの実装ギャップ、バグの疑い)
`build_diagnostic_section()`(96-104行)は`previous_point_one`/`previous_point_two`
引数に**ハードコードされたリテラル文字列**
`"(Point One body from previous attempt)"`/`"(Point Two body from previous
attempt)"`を渡しており、前回のPoint本文の実テキストはテンプレートへ
**一切埋め込まれていない**。Writerが実際に読めるのは前回のFull Story全文＋
overlapスコア・共有語一覧・粗い分類のみで、**前回Pointの逐語文自体は見えない**。
また、Point One×Point Two相互overlap(`cross_point_overlap`、`run_one_pattern`
863-865行の`lexical_flagged`判定は`before_overlap`(vs Full Story)のみを見ており、
`cross_point_overlap`(Point同士)のflagは`still_flagged`判定にも診断promptにも
使われていない)。この2点は既存実装の技術的ギャップとして記録するのみに留め、
本タスクでは修正していない。

---

## 3. 過去の関連管理ID・決定の時系列(Status付き)

| 時期 | 管理ID | 内容 | Status |
|---|---|---|---|
| 2026-08-29 | ER-008-N8-QA-CONTENT-SPEED-HARDENING-18 | Point-Full Story lexical overlap QA新設(閾値0.45暫定) | PRODUCTION_WIRED |
| 2026-08-29 | ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19 | 閾値0.45→0.40へユーザー承認引き下げ | PRODUCTION_WIRED(暫定、恒久仕様ではないOpen Item扱い継続) |
| 2026-08-29 | ER-008-N8-FINAL-QA-HARDENING-21 Item 6 | Point-only regeneration(Pointだけ局所書き換え)実装→新Fact fabrication実例発見 | 導入後REJECTED(`POINT_ONLY_REGENERATION_ENABLED=False`でProduction自動経路から撤去、コード671-672行のコメント参照) |
| 2026-08-29 | ER-008-N8-FINAL-CLOSEOUT-24 | Point生成Promptへ「語彙や言い回しだけを変えた再説明の禁止」を最重要原則として追加 | PRODUCTION_WIRED(現行コード196-203行に現存) |
| 2026-08-31 | ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14 | Point Role Planning(0/3 PASS) vs Diagnostic Full Retry(3/3 PASS)をA/B比較しDiagnostic Full Retry採用確定 | PRODUCTION_WIRED |
| 2026-09-03頃 | ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01 | Point Role Planning(初回計画)・Point Value QA(意味論的判定)・Point同士のcross overlap検査を追加 | PRODUCTION_WIRED |
| 2026-09-05 | PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01 | OPEN-112の7論点のうち4件(Trend overclaim severity/**Point Overlap閾値0.40見直し**/Reference Digest/Point長さ目安)をユーザーが明示defer | `USER_DECISION_REQUIRED`(DEFERRED、却下ではない) |
| 2026-09-05〜09-08(複数回) | OPEN-112各Trial(09/10/12closeout等) | 残件4件の1つとして**「Diagnostic Full Retry診断語彙拡張」**を繰り返し記録(据え置き) | `DEFERRED`(未実装のまま継続、直近は2026-09-08 PM-CLOSEOUT-CONSOLIDATION-19でも同文言で再記録) |
| 2026-09-08 | FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04 | Focus Module接続とPoint Overlap高頻度NGは独立事象と観測(A-UDR-13として言及、まだOPEN_ITEMS.md正式登録なし) | 観測記録のみ、対策未実装 |

---

## 4. retry/fallback/regeneration経路とOverlapの扱い

- **Diagnostic Full Retry(記事全体、上限2)**: Overlap NG時の正式経路。上記の
  診断section付きpromptで記事全体をWriterへ再生成させる。
- **Local Rewrite(文単位)**: `er010_ledger_local_rewrite_09.py`が担う別機構で、
  対象は**Ledger Deviation Checker MAJOR**(Verified Fact Ledgerとの逸脱)であり、
  Point Overlap NGはLocal Rewriteのトリガーには**ならない**
  (`OPEN_ITEMS.md` OPEN-113行、DECISION_LOG該当箇所で役割分離を確認)。
- **Human Review再生成**: 2回のDiagnostic Full Retryでも解消しない場合、
  `status="NG_REVIEW_REQUIRED"`を返して以降のFact Checker/Ledger Deviation/
  Assemblyへ進めない(946-957行)。この後、自動的にどのHuman Reviewキュー
  ファイルへ書き込まれるかはコード上確認できず**不明**(本関数の戻り値を
  受け取った呼び出し側の扱いは今回の監査範囲外)。

---

## 5. 案(b)との差分

既存のDiagnostic Full Retry診断情報には**すでに** overlap_ratio・threshold・
flagged・shared_words(実際の重複語一覧)・粗い重複タイプ分類が含まれる
(単純な「NG」通知ではない)。一方、上記4節で述べた通り、
(i) 前回Pointの逐語文自体はテンプレートに埋め込まれていない(ハードコードされた
プレースホルダーのまま)、(ii) Point同士(Point One vs Point Two)のoverlap診断は
計算されているのに診断promptにもretry判定にも使われていない、という**具体的な
未実装ギャップ**が存在する。

案(b)「overlap診断情報をより具体的に返す」は、この2点を指しているなら
既存ギャップの穴埋めとして意味があるが、それ以外の「もっと具体的に」が
指す内容(例: 文単位でどの文とどの文が重複したか等)は既存のshared_words
(単語レベル)を超える新規実装になる。また、この方向性自体は
「Diagnostic Full Retry診断語彙拡張」として2026-09-05頃から複数回
OPEN Item/Trial候補としてDEFERRED状態のまま繰り返し記録されている既知項目
であり、**新規の発見ではない**。

**判定: 部分重複(既存の"診断語彙拡張"Open Itemとほぼ同一の方向性。ただし
「前回Point本文自体が渡っていない」「cross_point_overlapがretry判定に
使われていない」という具体的な実装ギャップは、Trialというより先に
バグ修正候補として切り分けて検討する余地がある)。**

---

## 6. 案(a)との差分

初回Point生成Prompt(`er003_v1_n3_01_articles_generate.py` 196-232行)には、
既に以下が**「最重要」表記付きで**存在する:

> 【最重要・言い換えによる重複の禁止(ER-008-N8-FINAL-CLOSEOUT-24で強化)】
> Main Storyで既に説明した中心的なlogic・結論を、語彙や言い回しだけを変えて
> もう一度説明することは、たとえ表面上の単語が違っていても「本文の再説明」に
> 該当し、禁止です

さらにER-011-NO18で追加された一段強い規定:

> Point One・Point Twoは、Full Story・もう一方のPointと語彙が重複していなければ
> それでよいわけではありません。以下のようなPointは、たとえ語彙が違っていても
> 禁止です: …Full Storyの要約・言い換えに留まるPoint…

案(a)「Full Storyの語彙・言い回しを避ける既存原則の強化」は、**すでに
最重要レベルで明文化・かつ語彙一致の有無に関わらず禁止するところまで
既存で規定済み**の原則を指している。にもかかわらずbaseline NG率が67%と
高いことから、問題は原則の強度・文言不足ではなく、(i) 地名・スコア等の
トピック固有語(Hanshin/Hiroshima/score等)が正当な理由で共有され
overlap_ratioを押し上げてしまう構造的な性質、または(ii) 意味的に本当に
新しい切り口を作ること自体の難度、のいずれかである可能性が高い(実測
`shared_words`にトピック名詞が多数含まれることから推測、確定的な原因分析は
本監査の範囲外)。

**判定: 既存と実質重複(「強化」の余地があるとすれば、トピック固有語の扱い
[proper noun例外化等]という既存文言がカバーしていない新しい角度に限られ、
単純な語彙回避指示の反復強化は効果が薄い可能性が高い)。**

---

## 7. 見落としチェック(REJECTED/DEFERRED既往案)

- **Point-only regeneration**(Pointだけの局所書き換え): ER-008-N8-19導入後、
  ER-008-N8-FINAL-QA-HARDENING-21 Item 6でNew Fact fabrication実例が確認され
  Production自動経路から撤去(`POINT_ONLY_REGENERATION_ENABLED=False`)。理由:
  「Full Story/他方のPoint/Fact Ledgerとの整合性チェックが薄く、Fact Checker
  頼みの二段構えになっていた」(コード653-672行コメント)。
- **Point Overlap閾値0.40自体の見直し**: 2026-09-05にユーザーが明示deferの対象
  として記録(却下ではなく先送り)。今回の案(a)/(b)とは別軸(スコア判定の
  閾値そのものを動かす話であり、prompt強化やdiagnostic詳細化とは独立)。

他に「重複内容をWriterへfeedbackし記事全体を書き直させる」という設計自体が
REJECTEDになった記録は見当たらなかった(Diagnostic Full Retryはこの設計の
正式採用形としてPRODUCTION_WIREDのまま維持されている)。

---

## 8. 総合判定

| 項目 | 既存対策 | 今回案 | 差分 | 追加Trial要否 |
|---|---|---|---|---|
| (a) Point生成Prompt語彙回避強化 | 「最重要」表記付きで既存(語彙一致の有無を問わない禁止まで踏み込み済み) | 同方向の文言強化 | ほぼ無し | **不要**(STOP推奨。効果があるとすればトピック固有語の扱いという別角度の検討) |
| (b) Diagnostic情報の具体化 | ratio/threshold/shared_words/粗分類は既存。ただし前回Point本文自体・cross_point_overlapは診断に未使用(実装ギャップ) | 「診断語彙拡張」として既に2026-09-05頃からDEFERREDのOpen Item | 上記2つの具体的ギャップのみが真の差分 | **Trialより先に、まず実装ギャップ(前回Point本文の埋め込み漏れ・cross_point_overlap未使用)の扱いをユーザーに確認することを推奨(STOP推奨)。それでも変わらない場合のみ、次段階で「文単位のoverlap特定」等の真に新しい情報拡張をTrial化する余地はある** |

**STOP推奨**: 両案とも、指示された分散低減という目的に対し「既存対策の
再提示」に近く、追加Trialへ進む前に(1)案(a)/(b)ともに既存対策と重複する
ことをユーザー/Fableへ報告し、(2)真に新しい角度(トピック固有語の除外扱い、
前回Point本文のtemplateへの埋め込み、cross_point_overlapのretry判定への
反映)を対象とするかどうかの判断を仰ぐべきと判定する。
