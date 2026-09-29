管理ID: OPEN-233-CHECKER-REDESIGN-TRIAL-01(委任_04: Opus L2 所見の逐語保存+Stability n=20 実測+negative claim 候補抽出。**設計変更・variant 実装・gold/指標変更は禁止**)
日付: 2026-09-29。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 前提
- docs/pm/PM_BRIEF.md 固定ヘッダ、docs/pm/PM_GOVERNANCE.md 8節。
- 直前成果: docs/pm/RESULT_PACKET_C233C.md、OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md §9/§10、docs/pm/design_open233_checker_redesign_trial_01.md、er051_open233_checker_trial_variant_01.py、er051_open233_checker_trial_02_run.py、er051_output/open233_checker_trial_01/trial_02/。
- 一時ファイル: docs/pm/ACTIVE_TASK_C233D.md / docs/pm/RESULT_PACKET_C233D.md(新規、commit 禁止)。既存 *_C233A/B/C は削除・移動しない。
- 累計費用 ¥22.1167/総枠 ¥400、残 ¥377.8833。本委任 Guardrail ¥40。

## 1. Fable 判定(本委任の位置づけ)
Opus L2 レビュー #1 により、不要 BLOCK 率の指標定義と gold(B1 claim 分割/B3 確定/B4 分母除外/目標値)の再判断が **USER_DECISION_REQUIRED** と判明した。したがって本委任では **C1(materiality 軸 V6)/C2(一般常識許容規定 V5-A)/V4-B/V5-C/notes schema 分離/Family 横断変更/gold・指標変更のいずれも実装・実行しない**。ユーザー判断に依存しない以下 3 作業のみ行う。

## 2. 作業 A(¥0): Opus L2 所見の逐語保存
- docs/pm/opus_l2_review_open233_checker_trial_01.md を新規作成し、Opus L2レビュー#1全文を一字も変えず保存する(見出し・表・Evidence行を含む。要約・省略禁止)。冒頭に「管理ID/日付 2026-09-29/種別 L2設計レビュー#1/read-only/Fable委任/本文逐語」のヘッダのみ付ける。
- REPORT §11「Opus L2 レビュー #1(委任_04 で逐語保存)」を追加し、上記ファイルへのポインタと、Fable 判定(USER_DECISION_REQUIRED 該当: 指標定義・gold 再判断/C1 は事前了承要/V5-C 不採用推奨/notes 分離不採用推奨/HOOK_CLAUSE 衝突は Family 横断時の必須確認)を箇条書きで記す。設計書にも §5-補として同ポインタを追記。

## 3. 作業 B(有料、測定のみ): Stability/recall の n=20 実測
- 対象 fixture: `hormuz_run03_standard`(gold=BLOCKING、HF-009 changed_scope)と `Meta_run03_standard`(gold=BLOCKING、negative control)の 2 件。既存 sha256 と一致することを確認。
- variant: **V0(現行 Production Prompt/schema そのまま、post-hoc も現行相当。er051 の V0 経路)と V4-A の 2 variant**。各 fixture × 各 variant × n=20 = 80 call。モデル gpt-6-luna、reasoning="high"、Contract 非経由、既存 harness を流用(新規 run script は er051_open233_checker_trial_03_stability_run.py として追加可。variant ファイルの Prompt/schema/rule は変更しない)。
- 想定費用: Trial 2 Step3 実測(20 call ¥4.90≈¥0.245/call)から約 ¥20(上限 ¥30、超過見込みで STOP)。retry 上限 fixture あたり 2 回。実行前に ACTIVE_TASK_C233D.md へ対象 fixture 数・call 数・retry 上限・想定費用・Guardrail を記録。
- 出力先 er051_output/open233_checker_trial_01/trial_03_stability_n20/。
- 集計(fixture × variant): 検出率(deviations 非空かつ gold claim を捕捉した回数/20)、gold claim 捕捉時の severity/category 一致率、非検出回の reasoning_tokens 分布、二項 95% 信頼区間(Wilson)、V0 vs V4-A の差の検定(Fisher 正確検定、両側 p 値)、cost/latency 平均。「有意差あり/なし」を数値付きで明記し、Opus 論点 4 の推定(単発 recall 60〜85%)と照合する。
- API key は環境変数のみ、表示/log/commit/REPORT 禁止。保存 json に prompt 本文を含めない(prompt_sha256 のみ)。Production ファイル(er003_*/er006_*/er012_*/er019_*)・Master Store は変更しない。

## 4. 作業 C(¥0): negative claim 候補の抽出(gold 確定はしない)
- Opus 論点 5 推奨 1 に従い、er019_output/ 配下の Family X Production 実行(family_x_refresh_e2e_01/meta/run_03、family_x_b3_production_wiring_01 等)で **retry を経て最終的に LEDGER_COMPLIANT になった記事本文**から、Ledger に明示されていない「一般常識レベルの背景説明・条件付き一般論・心理一般論」に該当する claim 候補を 10〜20 件、claim 単位で抽出する(fixture 化はせず、候補表のみ)。各候補に: 出典 run/段階、claim 本文、関連 Ledger fact_id、Checker が通した根拠(該当 deviation_check json の抜粋)、Opus 分類案(ACCEPTABLE/QUALITY)、sha256 を付す。
- 併せて Opus 論点 2 の claim 単位評価表(B1-a/b/c、B2、B3、B4-a/b/c/d)を「gold 候補表(ユーザー確認待ち)」として設計書 §2 の gold 表の**下に別表**として追加する(既存 gold 表は変更しない)。
- 「現行 fixture 単位定義での下限 50%」の算術(Opus 論点 2)を設計書へ再掲する。

## 5. 記録・Git
- REPORT §11(作業 A)、§12「Stability n=20 実測(委任_04)」、§13「negative claim 候補表・claim 単位 gold 候補表(ユーザー確認待ち)」を追記。費用欄: 今回/累計/残(Opus 使用回数 1 を併記)。
- SSOT(最小限、1 agent のみ): OPEN_ITEMS.md OPEN-233 行に「Status=USER_DECISION_REQUIRED(指標定義・gold 再判断)、Opus L2 #1 所見ポインタ、累計費用」を追記。DECISION_LOG.md に Fable 判定(§1)を 1 エントリ追加。CURRENT_SPEC.md 不変。REPORT_LEDGER は文案のみ。
- delegation_log: docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-REDESIGN-TRIAL-01_04.md 作成+check_delegation_prompt.py 実行(FAIL 既知・non-blocking)。
- commit: パス指定 git add(-A 禁止)、Management-ID trailer、ACTIVE_TASK*/RESULT_PACKET*/.env は add しない。競合時 git merge origin/main のみ(reset/amend/rebase/force push/stash/rm/git clean/削除/移動 禁止)。
- 事後確認: mock test 全 PASS、Production 定数 3 件 sha256 不変、git diff --stat で Production ファイル無変更。
- 報告(RESULT_PACKET_C233D.md と handback): 【現在の状態】【作業 A 保存先】【n=20 実測結果表(fixture×variant: 検出率・95%CI・p 値・severity/category 一致率・cost/latency)】【Opus 論点 4 推定との照合】【negative claim 候補件数と保存先】【claim 単位 gold 候補表の保存先】【ユーザー判断 11 該当有無(該当=指標定義・gold 再判断、Fable 判定済み)】【Dangling Reference/Production 無変更確認】【費用: 今回/累計/残予算(¥400)】【Git(hash・raw URL)】【Status=USER_DECISION_REQUIRED】。

## 6. STOP 条件
本委任累計 ¥40 超え見込み/API error 3 fixture 連続/harness 不具合/Production ファイル変更発生。STOP 時は理由・結果・費用を報告(自動 retry しない)。

## 7. 実行結果サマリ(委任完了後、事実記録)

- 作業A: `docs/pm/opus_l2_review_open233_checker_trial_01.md`新規作成(Opus L2レビュー#1全文逐語保存)。REPORT§11・設計書§5-補にポインタ追記。
- 作業B: hormuz_run03_standard/Meta_run03_standard×V0/V4A、n=20、80 call、¥23.5636、error 0で完走(実行中に1回メモリ不足でbackgroundプロセスがkillされたため、`--resume`機能を追加し既存成功run[66/80]を再課金せず残り14 callのみ再実行)。検出率: hormuz V0=100%(20/20)・V4A=85%(17/20)、Meta V0=90%(18/20)・V4A=100%(20/20)。Fisher正確検定でV0-V4A間の差は全て有意でない(hormuz p=0.2308、Meta p=0.4872、併合p=1.0)。Trial 2(n=5)の「90%→80%」低下は再現せず。非検出回のreasoning_tokensは検出回平均より高い(思考量不足では説明できないというOpus所見を再確認)。詳細: REPORT§12。
- 作業C: negative claim候補16件を`er019_output/`配下のLEDGER_COMPLIANT記事(retry後、¥0)から抽出、`docs/pm/negative_claim_candidates_open233_01.md`に保存。claim単位gold候補表(Opus論点2のB1-a/b/c等)を設計書§2-補へ追加(既存gold表は変更せず別表)。詳細: REPORT§13。
- SSOT: OPEN_ITEMS.md OPEN-233行に追記7、DECISION_LOG.mdに本委任エントリを1件追加。
- 費用: 委任_04合計¥23.5636(80 call、error 0)。累計¥45.6803(Trial1¥7.2882+委任_03¥14.8285+委任_04¥23.5636)/総枠¥400、残¥354.3197。
- Production/Dangling Reference: `git diff --stat`でProductionファイル無変更確認。mock test 37件全件PASS。DEVIATION_PROMPT_TEMPLATE/DEVIATION_DEVELOPER_MESSAGE/DEVIATION_JSON_SCHEMAの3定数sha256はPhase A記録と完全一致。API key漏洩なし。
- Status: `USER_DECISION_REQUIRED`(指標定義・gold再判断)。
- 詳細: `docs/pm/opus_l2_review_open233_checker_trial_01.md`、`docs/pm/negative_claim_candidates_open233_01.md`、`docs/pm/design_open233_checker_redesign_trial_01.md`§2-補/§5-補、`OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md`§11〜§13、`DECISION_LOG.md`同日「OPEN-233-CHECKER-REDESIGN-TRIAL-01: Opus L2レビュー#1逐語保存+Stability n=20実測+negative claim候補抽出」エントリ。
