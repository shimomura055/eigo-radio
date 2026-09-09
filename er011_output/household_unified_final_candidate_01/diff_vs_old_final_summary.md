# HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01 — 旧完成版との差分要約

比較対象(旧完成版、いずれも無変更・本タスクでは一切編集していない):
- 旧A2: `er003_output/n3_01/household/a2/article.md`(FIX-01手動編集版、Ledger v1系当時)
- 旧B1B: `er003_output/n3_01/household/fact03_fix_02/b1b/article.md`
  (HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03[OPEN-138]、Ledger v5
  でtopic_intro HUMAN_APPROVED済みの最終形、player: `er011_output/
  open138_household_fact03_b1b_minimal_fix_03/player.html`)

新候補(本タスクで新規生成、Ledger v5+`cautionary_constrained`条件):
- 新A2/B1B: `er011_output/household_unified_final_candidate_01/{a2,b1b}/article.md`

## 語数

| | 旧完成版 | 新候補 | 差分 |
|---|---|---|---|
| A2 | 391語 | 379語 | -12語 |
| B1B | 355語 | 399語 | +44語 |

## 保険文(外部情報源確認を促す独立した一文、regex検出)

FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10のPart A検出regex
(`(check|consult|ask|see|refer to|look at|read|follow)` + 80文字以内 +
`(instructions|manuals|guides|manufacturers|makers|professionals|experts|
labels|packagings|packages)`)で静的走査。

| | 旧完成版 | 新候補 |
|---|---|---|
| A2 | 0件 | 0件 |
| B1B | 0件 | 0件 |

**所見**: 現在公開されている旧完成版(A2/B1B)自体には、本regexで検出される
独立した保険文は元々存在しなかった(Trial-10で問題が確認されたのは
Discovery Trial-07の別run[A2 baseline/discovery_focus]であり、公開済み旧
完成版はその実例ではない)。したがって本項目では新旧の差は「0→0」で、
Part B文言による直接の改善実証にはならない(退行もしていない)。

## Point切り口(構成・アプローチ)

- **旧A2**: 「2つのドロワー設定」を先に説明し、章立ては(1)スライダー=空気の
  ドア、(2)冷蔵に向かない食品(トマト・バナナ・じゃがいも等)。KitchenAid/
  Whirlpoolの社名を挙げて高湿度/低湿度の推奨を補強。
- **新A2**: 「スライダーに聞くべき質問(水を保つか、ガスを逃すか)」という
  診断的な切り口を明示的なPoint Oneの軸として提示し、Point Twoで
  「冷蔵庫に入れる前に、そもそも冷蔵に向く食品かを先に判断する」という
  順序(保管場所→設定)を明確化。社名(KitchenAid/Whirlpool)は使用せず
  Ledgerの一般的な記述に留めている。
- **旧B1B(FIX-03)**: 「fruit-or-vegetable rule can mislead」の実例として
  **いちご**(strawberries、メーカーにより高湿度/低湿度が分かれる)を挙げる。
- **新B1B**: いちごの実例は使わず、「Sort by the risk, not by the food
  group」という診断的な見出しでリスク基準(エチレン放出 vs 水分喪失)を
  一般化して説明し、「保管場所を先に決めてから設定を選ぶ」という同じ
  順序をPoint Twoで明示。

**所見**: 両者とも診断的("何が問題かを見極める")な構成へ寄せている点は
共通するが、新候補は保管場所の判断(冷蔵か常温か)をPoint Twoで明示的に
先出しする構成が旧版より一段強調されている。旧B1Bのいちご実例(FACT-03の
「メーカー間で見解が分かれる」争点)は新候補では扱われていない
(Ledger v5でも参照可能な事実だが、Writerがこの記事回では選ばなかった)。

## FACT-03/FACT-04の扱い

- **旧A2**(Ledger v1系当時に生成、その後Ledger側はv2〜v5まで複数回修正
  されたが記事側は無変更のまま)は、りんご・洋梨に加えてバナナ・トマトにも
  言及する形跡はない(元々りんご・洋梨・葉物中心)。FACT-04(トマト・
  バナナは常温)とも矛盾しない。
- **旧B1B(FIX-03)**は、Ledger v5(バナナ・トマトをFACT-03の低湿度ドロワー
  適合例から除外し、FACT-04[常温保存]との内部矛盾を解消した版)の下で
  再検証済みで、りんご・洋梨のみを低湿度の例として使用。
- **新A2/B1B**も同じLedger v5を参照し、低湿度の例はりんご・洋梨のみ
  (バナナ・トマトは「冷蔵ではなく常温保存」という文脈でのみ登場)。FACT-03/
  04間の矛盾は生じていない(Ledger Deviation Checker: 両レベルとも
  `LEDGER_COMPLIANT`、deviations=0)。

**所見**: FACT-03/04の内部整合という観点では、新候補は旧B1B(FIX-03)と
同水準(Ledger v5準拠、矛盾なし)。旧A2はそもそもFACT-03の対象食品
(バナナ・トマト)に触れていないため、この観点での実質的な差は無い。

## QA到達状況(参考、旧完成版は当時のQA記録が本タスクの範囲外のため
再掲していない。新候補のみ)

| | A2 | B1B |
|---|---|---|
| fact_verdict | PASS | PASS |
| ledger_status | LEDGER_COMPLIANT(0件) | LEDGER_COMPLIANT(0件) |
| Point Overlap記事全体retry回数(上限2) | 1回(retry後解消) | 0回 |
| directional_fact_precheck | PASS | PASS |
| Audio Validation Gate opt-in(ON経路) | PASS | PASS |

## 結論(この差分要約の範囲)

新候補は旧完成版と同じLedger v5・同じFACT-03/04整合を保ちつつ、
Part B案1(cautionary_constrained)を適用した記事として新規に生成された。
保険文の有無という観点では新旧とも0件で差が出なかった(旧完成版が元々
この問題の実例ではなかったため)。Point切り口は旧版と異なる新しい文章
(いちご実例の有無等)であり、旧完成版の「置き換え」ではなく「独立した
新しい候補」である。Production採用可否・旧完成版との差し替えの是非は
ユーザー判断事項(USER_DECISION_REQUIRED)。
