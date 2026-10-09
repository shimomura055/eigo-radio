# 委任_05 FACTLOCK-ASTRA-E2E-TRIAL-01 前提作業の実装+2腕runner+テスト+G0 dry-run(委任文全文)

管理ID: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_05(前提作業の実装+2腕runner+テスト+G0 dry-run、API生成支出¥0)。日付 2026-10-09。並行して委任_06(新6テーマのresearch→台帳→B3、旧4のB3再生成)が走っている。**委任_06の出力ディレクトリ `er052_output/factlock_astra_e2e_trial_01/stage_r/` には書き込まない。** git commit時にindex.lockで失敗したら10秒待って最大5回再試行。

## ユーザー決定(2026-10-09、実装の前提)
- 注記仕様 v2 固定(`B3_ANNOTATION_SPEC_v2.md`、sha256は `B3_SPEC_V2_SHA256.json`)。
- 旧4テーマは**凍結台帳を再利用しB3だけ新規生成**(D案)。新6は研究から。全10記事のB3を注記仕様v2で注記(別委任)。
- B1採用、M1 ON(Advancedのみ)、M3 ON、M2 OFF、Astra Standard同期、予算上限¥1,000、TTSは後回し。
- Fable判断済み: 注記者出力の形式FAILは同一テンプレで1回再委任後STOP/sha256はLF正規化後に計算/B1「1記事1回」枠はR2後FC MAJOR由来とEN段由来で共通/G1(META新腕)は検査通過なら本番runとして採用/ラウンド1(旧4)は単層4並列+自動降格、ラウンド2(新6)は3並列/予算計画は最悪約¥915。

## 事前指定Read
- `er052_output/factlock_astra_e2e_trial_01/DESIGN_E2E_01.md`(v2、特に§2フロー・§3影の対照・§4前提作業(a)〜(n)・§5実行計画・G0照合)、`PREREGISTRATION_01.md`(v2.1)、`B3_ANNOTATION_SPEC_v2.md` §6照合(注記版briefとJSON `fact_selection_evidence.json` の扱い)。
- `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_03_result.md`(前提作業一覧 v2 の対象ファイル・行)。
- コード: `er019_family_x_entertainment_production_runner_01.py`(L92 research分岐、L332-393 R2再利用分岐、JSON読取L336-339)、`er019_family_x_ja_writer_o_r1_r2_01.py`、`er012_e_family_entertainment_two_level_runner_01.py`(M1分岐L418付近、案B L397-435/L509-579、must-fix L613-679、PricingNotFoundError L106-118)、`er052_factlock_writer_trial_01_run.py`(Fact Lock R0 harness、R0_PROMPT L72-79、`original_must_fix`、tag strip、phase2タグ残存箇所)、`er052_output/factlock_writer_trial_01/astra_revise_matrix_01/tools/run_matrix.py`(Astra呼び出し: model gpt-6-astra、reasoning high、系列Xユーザーメッセージ逐語、previous_response_id不使用)、`er052_open233_e2e_acceptance_01.py`・`er050_gpt6_checker_comparison_trial_01.py` L133-151(動的fixture)、`er052_open233_stage1_reclassify_01.py`(M3)、`er006_model_routing_contract_01.py`、`er005_output/cost_baseline_01/pricing_snapshot.json`、`er005_cost_logger*`(費用台帳)、`efam.assert_budget_ok`。
- 単価正本: `er052_output/factlock_writer_trial_01/astra_pricing_01/extracted_pricing.json`(gpt-6-astra Standard input 10.00 / cached 1.00 / cache write 12.50 / output 50.00 USD/1M、Batch・Flex 50%、取得2026-10-08 16:38 JST、出典 https://platform.openai.com/docs/pricing)。USD/JPY=160。

## 実装内容(設計書§4の前提作業。各項目を完了・未完了で報告)
(a) **astra単価登録**(**別commit**、commit message「gpt-6-astra単価登録(Standard 10/1/12.5/50、出典pricing page 2026-10-08)」): `pricing_snapshot.json` と routing contract のcoverage testへ登録、出典URL・取得時刻・sha256を併記。Fableは本委任文で登録を事前承認する(確認済み単価のため)。登録後に `PricingNotFoundError` が解消することをテストで確認。Batch/Flex単価は登録しない(Standardのみ、本Trialで使う分だけ)。
(b) R0復唱検出(R0と最終JA、両腕、約20行、記録のみ)。
(c) phase2 JA再生成のタグ残存修正(B1に必要、30〜50行): Fact Lock R0に `original_must_fix` を付けた再生成でもタグ付き本文が後段へ流れないよう、EN段へ渡す直前のstripを単一経路に。
(c2) B1回復経路+カウンタ(80〜120行): EN段 `ja_source MAJOR`(JA_RECHECK)またはR2後FC MAJOR発火時、新腕は Fact Lock R0(must-fix付)→Astra R1→R2→後処理→EN再実行を1記事1回、Trial全体3回(環境変数で上限、超過はSTOP記録)。
(d) M1 Standard分岐は実装しない。Standard attempt1 MAJORを `open243_majors_only_in_summary` で要約/本文に分類しログ(約20行)。
(e) 記号後変換(`dash_to_comma`、`normalize_ellipsis_pause_ja`)+`strip_markdown` をAstra R2直後・FC前に組込(約40行)。記号Gateは記録のみ。
(f) **2腕runner本体(新規ファイル `er052_factlock_astra_e2e_runner_01.py`、450〜600行)+テスト(`er052_factlock_astra_e2e_runner_01_test.py`、約250行)**: テーマごとに台帳・B3を共有、腕ごとにsubprocess分離・環境変数分離(新腕: `OPEN243_M1=1`、`OPEN233_RECLASSIFY_PROTECT_FLAGS=changed_actor`、承認スイッチ `OPEN233_APPROVED_FLOW_SWITCHES`・`FLOOR_MODE=number_only`。旧腕: フラグ全OFF、同承認スイッチ)、書込はtmp→rename、stage完了マーカー・追記専用費用台帳で再開可能、Checkerは動的fixture(`baseline_parsed=None`)、新腕はAstra R2を `ja_writer/revision2.md` に置いてer019の再利用分岐へ乗せる(JSON `fact_selection_evidence.json` の `selected_fact_brief_text` も注記版/原文で正しく渡す)、G0照合(台帳sha256・B3 md/JSONのsha256・strip後一致・宇宙兵器台帳一致)、M1/M3影の対照ログ(両腕、設計書§3)、新規具体主張(ii)検出器を両腕のJA最終本文へ、`shadow_stop`、初回JA_RECHECK率、人手介入必要率の集計欄。
(g) web_search課金計上の再確認スクリプト(約20行)。
(k) 横断予算予約(worker別台帳合計+実行中見込み予約、各API段前に判定、累計¥1,000 hard stop・¥800アラート、astra分は請求照合まで×1.5係数、60〜80行)。
(m) 旧4テーマでresearch/B3のAPI呼び出し(web_search含む)を検出したら即停止(約30行)。※旧4のB3再生成は委任_06が別経路で行う。runnerは「台帳・B3が揃った状態」から開始し、research/B3段を**呼ばない**。
(i) 集計スクリプト(§81と同じ集計表フォーマット+追加指標、約200行)。
- 失敗方針・Waste検知・即停止条件は設計書§5どおり。
- 単体テスト全件PASS(既存の関連テスト `er052_open243_m123_trial_test_01.py` 等も回帰PASS)。

## G0 dry-run(¥0、API stub)
- 新規runnerをAPI stubで、旧4テーマ(凍結台帳+**委任_06が生成するB3が未着なら仮B3=凍結B3**で代用し、代用した旨を記録)×2腕×2レベルがG0照合→JA→EN→Checker→集計まで通ることを確認。出力は `er052_output/factlock_astra_e2e_trial_01/g0_dryrun/`。provenance・費用台帳・再開マーカー・影ログの欄が埋まること(値はstub)。
- 旧4の即停止検出(m)が、research呼び出しをstubで発生させた時に止まることをテスト。

## 禁止事項
- API生成呼び出し禁止(¥0。dry-runは全てstub)。既存Prompt文言の変更禁止(Fact Lock R0_PROMPT・Standard A2プロンプト・系列Xメッセージ逐語)。`CURRENT_SPEC.md`・`OPEN_ITEMS.md` 編集禁止。Production runnerの既定挙動を変えない(全て環境変数/フラグ既定OFF、既存テストPASS)。
- 未確認数値を確定値として書かない。

## 記録・Git
- 委任文全文を `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_05.md`、check結果、最終報告を `_05_result.md` と `docs/pm/RESULT_PACKET.md`。
- `docs/pm/ACTIVE_TASK.md` 固定ヘッダ更新(委任_05=IMPL_READY/G0_PASS or FAIL)。`DECISION_LOG.md` 末尾にD案・自律実行の範囲(G2テキスト完走まで、TTS後回し、¥1,000)のユーザー決定を1節追記。`docs/pm/REPORT_LEDGER.md` 1行。
- commit: (a)単価登録は別commit、それ以外は1 commit。明示的`git add`のみ(`git add -A`禁止)、push、hash+raw URL報告。

## 報告形式(result.md)
1. 成果物・commit hash(2つ)・raw URL、テスト件数/結果、既存テスト回帰結果
2. 前提作業(a)〜(m)の完了/未完了と差分の要点
3. G0 dry-run結果(通過stage、照合結果、代用した入力)
4. 実行時に必要な環境変数・コマンド全文(G1カナリア用、G2 round1/round2用)
5. 未確認・Fable判断要(実行前に解決すべき事項を優先順で)
6. 所要時間・API支出(¥0)
