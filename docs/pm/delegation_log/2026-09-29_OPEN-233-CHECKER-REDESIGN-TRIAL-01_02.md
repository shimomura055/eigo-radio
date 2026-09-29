管理ID: OPEN-233-CHECKER-REDESIGN-TRIAL-01(委任_02: Trial 1 実行+結果分析+原因切り分け+改善案設計)
日付: 2026-09-29。作業ディレクトリ C:\Users\tensh\eigo-radio(Windows/PowerShell、python は既存の実行方法に従う)。

## 0. 前提(必ず最初に読む)
- docs/pm/PM_BRIEF.md の固定ヘッダ、docs/pm/PM_GOVERNANCE.md 8節(禁止事項)・9節。
- Phase A 成果物: docs/pm/design_open233_checker_redesign_trial_01.md、er051_open233_checker_trial_variant_01.py(+_test_01.py)、OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md、docs/pm/RESULT_PACKET_C233A.md、docs/pm/ACTIVE_TASK_C233A.md。
- 参照(必要箇所のみ Grep): docs/pm/design_gpt6_model_comparison_trial_01.md §3-3/§受入指標(L154〜L290)、GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md §Closeout C-2(単価)、er050_gpt6_checker_comparison_trial_01.py(harness 流用元)、er050_output/gpt6_checker_comparison_trial_01/(V0 実測 raw data)。
- 一時ファイルは docs/pm/ACTIVE_TASK_C233B.md / docs/pm/RESULT_PACKET_C233B.md を新規作成して使う(commit 禁止)。既存の *_C233A.md は削除・移動しない。

## 1. ユーザー更新判断(2026-09-29、逐語要旨。DECISION_LOG へ記録すること)
1. OPEN-233 Trial は「一度 Trial して結果が悪ければ終了」ではなく、総予算 **¥400** 内で Trial→分析→原因切り分け→改善案→再 Trial を Claude 側で合理的に改善できるところまで繰り返す。
2. QUALITY=Production 通過可(BLOCKING=fail-closed、QUALITY=通過、ACCEPTABLE=通過)は Trial 検証前提であり Production APPROVED ではない。QUALITY ログの Production 運用設計は Trial 後へ defer。
3. deterministic 昇格 Trial 対象: changed_actor/changed_number/changed_negation/changed_comparison の flag=true かつ LLM severity=MINOR → BLOCKING。false positive が出たら category 条件・Ledger 一致条件・scope・materiality を再検討し、単純ルールを押し通さない。
4. 過剰 BLOCK 改善が最重要。「必要なものは確実に止め、ユーザーの主要 Fact 理解を変えない差異で Production を止めない」。過剰品質による生産性喪失は許容しない。不要 BLOCK 率 baseline 75% → 目標 ≤25%。
5. schema variant(factual_constraint/writer_guidance/qualifier/basis/Ledger 観測整合/context evidence 等)を含めて Trial 可。Production schema は不変、Family X 限定 Trial variant。
6. Hormuz B-2 暫定 gold=QUALITY(Trial 用、最終 Production 仕様ではない)。
7. 対象モデル gpt-6-luna のみ。5.6 再比較不要。Sol 保留、Astra 対象外。
8. 「Phase A 終了後 Trial 実行前に STOP」は撤回。承認済み範囲内なら Phase A→Trial→分析→改善→再 Trial まで進めてよい。
9. Opus L2 は SafetyとProductivityのトレードオフ/不要 BLOCK が減らない/deterministic false positive/causality・scope・certainty 境界不安定/schema 抜け/結果解釈が非一意/fail-closed 思想との競合/Family 横断影響/同じ改善 2 回不達 のいずれかで投入(Fable が判断する。本委任では Opus を呼ばず、該当条件の有無を報告する)。
10. 都度確認なしで可: Trial 専用 Prompt/schema variant、post-hoc v2/v3 等、deterministic rule 改善、fixture/negative/regression fixture 追加、n 回反復、結果分析、改善 variant 再実行。すべて Trial/DEV 専用、Production 正式 path は変更しない。
11. USER_DECISION_REQUIRED(勝手に決めない): 新 Product 原則追加、未承認 Safety/Productivityトレードオフ、gold label 変更、BLOCKING 対象の大幅緩和、fail-closed 撤廃、Family X 以外への Production 展開、Production Prompt/schema/Validator 変更、GPT-6 Luna routing 変更、OPEN-233 の Production 正式採用、Human Review 常設。
12. 予算 ¥400(GPT-6 Luna Trial+Opus L2+再 Trial+追加 fixture 検証を含む)。各 iteration で今回費用/累計/残予算を記録。累計 ¥400 超え見込みで STOP。使い切る必要なし。
13. 最終目標: Safety(重大 fixture BLOCKING 維持率 100%)/Productivity(不要 BLOCK 率 ≤25%)/Stability(同一 input で判定が大きく揺れない)/QCD(量産可能な cost/latency/retry/STOP 率)。
14. 終了条件 A 目標達成→VALIDATED 候補 / B 技術的限界→USER_DECISION_REQUIRED / C 新 Product 判断→USER_DECISION_REQUIRED / D 予算上限→best variant+Evidence で STOP。
15. 再発防止: 改善内容を Prompt/schema/deterministic Validator/regression fixture/QA/SSOT/OPEN_ITEMS のどこで防ぐか整理。特に「過剰 BLOCK が将来モデル変更・Prompt 変更で復活しない regression fixture」を残す。

## 2. Fable 判定(Phase A の★要確認 6 件の解決。設計書へ「Phase A 要確認事項の解決(Fable 判定)」節として追記し、REPORT にも反映)
- (1) A-1: 再実行不可のため参考記録のみ、BLOCKING 維持率の分母から除外(REPORT に明示開示)。
- (2) gold: **既存暫定 gold を変更しない**(ユーザー判断: Claude は gold を書き換えない)。不要 BLOCK 率の定義は design_gpt6_model_comparison_trial_01.md L258 の既存定義「B 群 4 件(B1/B2_hormuz/B3/B4)のうち BLOCKING(MAJOR 相当)のまま判定された件数 / 4」を維持(baseline 75%・目標 ≤25% と同一根拠)。B3/B4 に対する Part B の「BLOCKING 妥当」異見は gold 変更ではなく**リスク欄に記録**し、Trial 結果で「≤25% 達成に B3/B4 の通過が不可欠」かつ「その通過が Safety 上不当と分析される」場合のみ、終了時に gold 再判断(ユーザー判断 11)として報告する。B1=ACCEPTABLE 候補(暫定)。
- (3) B2_hormuz=QUALITY 暫定のまま。最終化は Trial 後(ユーザー判断 6)。
- (4) Meta_run03_standard: negative control。fact_id 010/012 いずれでも「実逸脱を BLOCKING と判定」すれば検出成功とし、fact_id 差異は観測として記録する(gold 変更なし)。
- (5) Guardrail: Trial 1(本委任)単体 ¥50、Step 別上限は Phase A 案(Step1 ¥8/Step2 ¥6/Step3 ¥12)をそのまま採用。総枠 ¥400。
- (6) V2/V3 は両方実行する(差が出ない可能性は承知の上で観測データを取る)。
- (7) 実行前 STOP は行わない(ユーザー判断 8)。

## 3. Trial 1 実行(本委任のスコープ)
### 3-1. 事前記録(実行前に ACTIVE_TASK_C233B.md へ)
対象 fixture 数(Step 別)、variant 別想定 call 数(Phase A: Step1 34/Step2 10/Step3 20、合計最大 64、V0/V1 は 0 call)、retry 上限(API error 時 1 fixture あたり最大 2 回、それ以上は当該 fixture を ERROR 記録して続行)、想定費用 ¥16.4、Guardrail ¥50/Step 別上限、モデル gpt-6-luna・reasoning="high"、Contract 非経由の Trial 専用 harness。
### 3-2. 実行
- V0/V1: 既存 er050_output の raw data へ er051 の classify を適用(0 call)。
- V2/V3: Step1(重大群 12 fixture+changed_actor n=5)→ Step2(境界群 5 fixture)→ Step3(Step1/2 で最良の variant 1 つのみ、Hormuz run_03 4 fixture × n=5)。Step1 で Safety 100% 未達の variant は以後打ち切り(Trial 全体は続行)。
- 出力先: er051_output/open233_checker_trial_01/trial_01/ 配下(raw response/usage ログ、fixture 別 severity_final/action/basis/rule_id、summary_step1/2/3.json、cost.json)。
- 費用は usage の実測 token × 公式単価(gpt-6-luna In $0.10/Cached $0.01/Out $0.50 per 1M、reasoning は output 側)× ¥156.88 で算出。推測禁止。Step ごとに累計を確認し、Step 上限超過見込みで当該 Step を STOP。
- API key は環境変数のみ。key 本文を表示/log/commit/REPORT に一切書かない。Production Master Store・Production path・er003/er012/er019 の Production コードは一切変更しない。
### 3-3. 集計(variant 別)
Safety(重大群 BLOCKING 維持率、分母から A-1 除外)、changed_actor n=5 の昇格結果(MINOR→BLOCKING の件数、deterministic false positive 有無)、Productivity(不要 BLOCK 率 = B1/B2/B3/B4 中 BLOCKING 数/4)、Meta_run03_standard 検出可否、Stability(Step3 n=5 の判定一致率、V0 の 90% と比較)、QCD(1 call あたり cost/latency、retry 回数、ERROR 数、V0 比)。

## 4. 結果分析・原因切り分け・改善案(本委任のスコープ、Trial 2 は実行しない)
- B 群で BLOCKING のまま残った各件について: claim 内容、category flag、origin、matched_notes_id、qualifier/basis/observation_consistent 等 schema variant 出力、LLM 理由文を並べ、**原因分類**(a. Prompt の判定基準 b. schema の情報不足 c. deterministic rule d. context handling/notes_for_writer の渡し方 e. gold の曖昧さ)を 1 件ずつ付ける。
- Safety 側: 重大群で降格・見逃しがあれば同様に原因分類。deterministic 昇格の false positive があれば、ユーザー判断 3 に従い category/Ledger 一致/scope/materiality の条件案を検討。
- Stability 側: 揺れた fixture の揺れ方(severity か category か claim 選択か)。
- 改善案: 目標未達なら **V4 の設計案**(Prompt 差分/schema 追加項目/rule 条件/context handling の変更点、各変更が Safety に与える影響評価、追加すべき regression/negative fixture 一覧)を設計書へ追記する(実装・実行はしない。実装は次の委任)。目標達成なら「再発防止(ユーザー判断 15)」の整理を行う。
- ユーザー判断 9 の Opus L2 投入条件のうち該当するものを列挙し、Opus に問うべき論点を 3〜5 個に絞って提案する。
- ユーザー判断 11 に触れる事項が生じたか明記(生じていれば内容を特定し、STOP 扱いとして報告。生じていなければ「なし」と明記)。

## 5. 事後確認
- python -m unittest er051_open233_checker_trial_variant_01_test_01(全 PASS)、Production 定数 3 件の sha256 不変を再確認。
- git diff --stat で Production ファイル(er003_*/er006_*/er012_*/er019_*)に変更がないことを確認して REPORT に記載。

## 6. 記録・Git
- REPORT: OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md へ「Trial 1(委任_02)」章を追記(実行条件、結果表、分析、改善案、費用: 今回/累計/残(Phase A ¥0、Opus 使用 0 回)、Opus 条件該当、ユーザー判断 11 該当有無、Status)。
- 設計書: 上記 §2 Fable 判定節、Trial 1 結果・V4 案節を追記。
- SSOT(1 agent のみ編集、最小限): DECISION_LOG.md にユーザー更新判断 1〜15 と Fable 判定(§2)を 1 エントリ追加。OPEN_ITEMS.md の OPEN-233 行に Trial 1 の Status/累計費用へのポインタを追記(本文肥大化を避ける)。CURRENT_SPEC.md は変更しない(Production 変更なしのため)。REPORT_LEDGER は文案のみ提示し編集しない。
- delegation_log: docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-REDESIGN-TRIAL-01_02.md を作成し check_delegation_prompt.py を実行(FAIL は既知・non-blocking、結果を記録)。
- commit: 変更ファイルをパス指定で git add(git add -A 禁止)。commit message に Management-ID trailer。ACTIVE_TASK*/RESULT_PACKET*/.env は絶対に add しない。push で競合時は git merge origin/main のみ(reset/amend/rebase/force push/stash/rm/git clean/削除/移動 禁止)。er051_output 配下の Trial 出力 json は commit 対象(raw response に API key が含まれないことを確認してから)。
- 報告(RESULT_PACKET_C233B.md と handback): 【現在の状態】【Trial 1 実行条件】【Safety 結果】【不要 BLOCK 率】【Stability 結果】【QCD】【deterministic 昇格の結果と false positive】【B 群残存 BLOCKING の原因分類(1 件ずつ)】【改善案 V4(設計のみ)】【追加 regression/negative fixture 案】【Opus L2 投入条件の該当】【ユーザー判断 11 該当有無】【Dangling Reference / Production 無変更確認】【費用: 今回/累計/残予算(¥400)】【Git(commit hash・raw URL)】【Status】。Status は TRIAL1_DONE_TARGET_MET / TRIAL1_DONE_IMPROVEMENT_PROPOSED / STOPPED(理由) / USER_DECISION_REQUIRED のいずれか。

## 7. STOP 条件(本委任)
Trial 1 累計 ¥50 超え見込み/API error が 3 fixture 連続/harness 不具合で結果が信頼できない/Production ファイルへ変更が入った/ユーザー判断 11 該当。STOP 時は理由・それまでの結果・費用を報告して終了(自動 retry しない)。
