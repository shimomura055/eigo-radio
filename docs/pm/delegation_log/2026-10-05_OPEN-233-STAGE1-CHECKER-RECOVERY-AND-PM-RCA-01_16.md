# 委任_16 OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / COST-FEASIBILITY-CHECK-01(量産総原価と+¥2達成可能性の¥0分析)

## 管理ID
OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / COST-FEASIBILITY-CHECK-01(委任_16、¥0分析、ユーザー追加指示2026-10-05)。並行タスクなし。

## 性質/禁止事項
- 有料API禁止。コード・Prompt・gold・fixture変更禁止。Production正式path変更禁止。SSOT編集はDECISION_LOG.md(ユーザー指示原文の逐語記録+Fable評価欄は空け)、OPEN_ITEMS.md本管理ID行、REPORT_LEDGER.md1行のみ。git add -A/stash/amend禁止。ACTIVE_TASK.md/RESULT_PACKET.mdはaddしない。1回の書き込み2,500文字以下、長文はappend_decision_log_from_sources_01.pyで転写。
- 数値規律: 実測(出典パス付き)と推計(式・前提)を全表で列分離。根拠のない「○%」禁止。成功確率は「高い/十分ある/五分五分/低い/判断不能」+根拠。
- Safety制約: 重大Fact検出を減らす・Safety-critical除外・gold変更・Checker甘化は「採れない削減策」に分類し改善案に入れない。
- T-0: 本委任ログ全文保存、check PASS後commit。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## 重要な前提(Fableから)
- KPIの分母は「Standard+Advanced 1記事セット」。これまでのTrialの/run・/記事は英語記事1本(1レベル)単位。セット換算(Stage 1〜Rewriteがセット内で何回走るか)を配線設計(production_wiring_gap_open233_01.md §2 P1〜P5、e2e_plan_open233_stage1_loop2_01.md)から確定し根拠明記、不明なら両方併記。
- 差し引き可能な置換処理は、配線設計上実際に廃止・置換されると示せるもののみ(現行英語Stage 1 V4A deviation check、Family X全文再生成等)。JA側検査・モデル世代差は差し引かない(Opus#17 §6、kpi_cost_baseline_open233_stage1_01.md)。
- 新フロー実測: Stage 1 r3 medium 0.447+r5 high 0.785=約1.23円/記事(混合未測定=推計)、候補約21.8/記事、Stage 2 fit 2式併記、Rewrite+Recheck約0.31円/回、rep30 Rewrite 20/38 run・cycle>=2 4/38、出口3'-R全文約0.22円、Stage 1内訳(reasoning57%/可視出力33%/入力10%)。
- 削減レバー候補(a)Stage 2出力短縮(ユーザー承認構成のため承認要明記)(b)Stage 2重複候補除去・束ね(c)Stage 1 SUPPORTED逐語引用省略(d)prompt caching(e)r3/r5入力共通化・1call2判定(f)決定論事前処理(g)Stage 2判定reuse(h)Recheck範囲限定(i)Human Review/STAGE4費用。各: 推定削減額/Safety影響/実装規模/Trial費用、実効性順。採れない策: r5 effort引下げ、r5-V、片経路化、候補上限、Safety-critical除外、gold変更、Checker甘化。
- 時間見積は実作業時間で¥0分析/実装/限定Trial/最終E2Eに分けレンジ。費用: 残98.29円、ループ3(実装0円+限定Trial+E2E 20 run約62円(48〜86))が収まるか不足額を先に示す。

## 作業
1. 最新Production仕様のStandard+Advanced 1セット原価の実測集計(er019_output配下raw_usage_log.jsonl、スクリプトer052_output/open233_kpi_recovery_02_offline_01/agg_production_set_cost_01.{py,json,md})。ログに無い項目は実測不能と明記。
2. 品質チェック純増(外数): 新フロー費用−置換処理費用、通常と上振れ、ベース X+純増 Y=合計 Z/セット。
3. +¥2達成可能性の技術評価(レバー表、改善幅、Safety上採れない策)。
4. 開発時間・追加費用(レンジ)。
5. Fable評価のための3択(+¥2狙いでループ3続行/技術的にかなり厳しい/判断不能)の根拠整理(結論はFableが書く)。
6. 文書docs/pm/cost_feasibility_open233_stage1_01.md(§1〜§5)。SSOT: DECISION_LOG(原文逐語+「Fable評価: 後記」)、OPEN_ITEMS本管理ID行、REPORT_LEDGER 1行。
7. commit/push(明示add)。メッセージ: OPEN-233 COST-FEASIBILITY-CHECK-01: 最新Production 1セット原価実測【¥X】+品質チェック純増【¥Y】=【¥Z】、+¥2達成の技術評価(レバー表・改善幅・時間・追加費用)、ユーザー指示逐語記録(委任_16、¥0)

## 事前指定Read一覧
docs/pm/kpi_cost_baseline_open233_stage1_01.md、docs/pm/e2e_plan_open233_stage1_loop2_01.md(費用節)、er052_output/open233_kpi_recovery_02_offline_01/{loop2_cost_structure_01.md, stageA_candidate_composition_01.md, agg_production_baseline_cost_01.md, agg_v4a_stage1_actual_cost_01.md, agg_cost_recalc_models_01.md}、er052_output/open233_stage1_loop2_garm_01/loop2_trial_summary_03.md、docs/pm/design_open233_stage1_loop2_01.md 費用節・§9、docs/pm/opus_l2_review_open233_stage1_loop2_17.md §5/§6/§9。

## 事前指定Grep一覧+追記位置・更新位置の手順
docs/pm/production_wiring_gap_open233_01.md: P1|P2|P3|P4|P5|廃止|置換|全文再生成|Standard|Advanced。er019_output/**/raw_usage_log.jsonl: stage名ユニーク値(Python)。DECISION_LOG.md: 約¥40|1記事あたり総コスト|Standard同期|Batch。CURRENT_SPEC.md: TTS.*単価|Batch|Standard同期。OPEN_ITEMS本管理ID行、REPORT_LEDGER末尾、DECISION_LOG末尾。追記位置: DECISION_LOG末尾に新節、OPEN_ITEMS本管理ID行にサブID進捗追記、REPORT_LEDGER末尾に1行。

## 実行コマンド全文
T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_16.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_16.md_check.json
集計: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\agg_production_set_cost_01.py
転写: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\append_decision_log_from_sources_01.py --block T:<見出しファイル> --block F:<path>@<start>@<end>
Git: git status --porcelain、明示add、commit、git push origin main、git log --oneline -1。

## SSOT追記文
DECISION_LOG.md末尾の見出し: 「## OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / COST-FEASIBILITY-CHECK-01(2026-10-05、ユーザー追加指示: 量産総原価と+¥2達成可能性の¥0分析)」+下記原文逐語+「Fable評価: 後記」。OPEN_ITEMS本管理ID行: 「COST-FEASIBILITY-CHECK-01(委任_16): ベース¥X/純増¥Y/合計¥Z、改善幅¥、必要額¥、材料整理済み→Fable評価待ち」。REPORT_LEDGER: 1行。

## Git(明示add対象・コミットメッセージ・trailer)
明示addのみ(ACTIVE_TASK/RESULT_PACKETは除外)。メッセージは作業7記載。trailer: Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>

## 報告
(1)結論8行以内(ベース/純増/合計、通常・上振れ、セット換算の根拠、改善幅、時間、必要額)、(2)表: 原価内訳(実測/推計列)、レバー表、採れない策、(3)3択を支持・否定する事実、(4)SSOT・T-0・commit・push・raw URL、一覧外Read、確認/推測、(5)Fableへの論点。

## ユーザー指示(原文、逐語。DECISION_LOGへそのまま転写)
````
Claude Code 追加指示
管理ID：OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / COST-FEASIBILITY-CHECK-01
今回、ユーザーはKPI変更の判断をする前に、まず量産時の総コストと、平均追加+¥2以内を達成できる現実性を確認したい。
新しいTrialを始める前に、既存実測・既存ログ・現在の設計から可能な限り ¥0分析を優先して、以下2点を明確に回答すること。
1. 品質仕様を正式採用した場合の量産価格
最新Production仕様を前提として、Standard + Advancedの1記事セットについて、
品質仕様導入後の量産総原価はいくらになる見込みか
を算出する。
必ず以下を分ける。
- 最新仕様のベース記事生成費
- 今回のOPEN-233品質チェックによる純増分
- 合計
- 通常時の平均見込み
- retry / Rewrite等が発生した場合の上振れ
- 現行Productionで置換される処理の費用は二重計上せず差し引く
過去の「約¥40/記事」をそのまま使わず、現時点の最新Production仕様で再確認すること。
今回の品質チェックは外数表示し、
ベース ¥X + 品質チェック純増 ¥Y = 合計 ¥Z / Standard+Advanced 1セット

という形でPMが理解できるようにする。
推計値と実測値は明確に区別すること。
2. 品質チェック平均+¥2以内を達成できる見込み
現行KPI：
平均追加費用 +¥2 / Standard+Advanced 1記事セット以内
について、以下を技術的に評価する。
必ず答えること
1. 達成可能性
   - 現時点で達成可能と見るか
   - 難しいが現実的に狙えるのか
   - 構造的にかなり厳しいのか
単なる印象ではなく、現在の実測値・候補数・Stage別費用を根拠にする。
2. 残る技術的ハードル
   - Stage 1のSafetyを維持したままどこを削れるか
   - Stage 2の候補数比例コストをどこまで削れそうか
   - batch化、出力短縮、重複除去、決定論処理、判定reuse等のうち実効性が高いもの
   - 逆に、Safety KPIを壊すため採れない削減策
3. +¥2達成までの改善幅
   - 現状の純増見込み
   - +¥2に入れるためあと何円/記事下げる必要があるか
   - その削減がどのStageから可能と考えるか
4. 必要な開発時間
   - 「○時間」または「半日/1日程度」など、実作業時間の見込み
   - ¥0分析
   - 実装
   - 限定Trial
   - 最終E2E
     を分けて見積もる
時間が不確実ならレンジで示す。
5. 必要追加費用
   - 残予算 約¥98.29
   - この範囲で、ループ3改善＋最終E2Eまで現実的に完了できるか
   - 足りない可能性があれば、必要額を先に示す
6. 成功確率を数字で捏造しない
   - 十分な根拠がなければ「○%」とは言わない。
   - 代わりに「高い / 十分ある / 五分五分 / 低い」等も、根拠を明示して使う。
   - 不確実なら「まだ判断不能」とする。
3. 特に確認すべきこと
今回、Safetyを落としてコストKPIを達成する案は禁止。
つまり、
- 重大Factの検出を減らす
- Safety-criticalを除外する
- goldを都合よく変える
- Checkerを甘くして候補数を減らす
ことはコスト改善として認めない。
改善対象は、
Safetyを維持したまま、不要な候補・重複処理・冗長なLLM出力・不要callを減らすこと

である。
4. 今回の到達点
この確認ではまだProduction変更をしない。
また、ユーザーへKPI緩和を提案する前に、
本当に+¥2が技術的に難しいのか、それともループ3で十分狙えるのか
を明らかにすること。
通常の技術分析・費用計算はユーザー判断に戻さず実施してよい。
分析後、
- +¥2達成を狙ってループ3を続行する価値が十分ある
- 技術的にかなり厳しい
- 追加情報がないと判断不能
のどれかを、根拠付きでFableがPM評価すること。
````
