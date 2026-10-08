## 管理ID

PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01(委任_03: Phase 1 単価登録+予算ガードfail-closed化 → Phase 2 定数7行+直書き修正 → Phase 3 Production E2E 1本・runtime evidence)。並行タスクあり: `FACTLOCK-WRITER-REDESIGN-TRIAL-01`(別agent。生成24本は完了済み、現在は盲検評価・集計中。SSOT/git権なし、書込先は`er052_output/factlock_writer_trial_01/`と`docs/pm/RESULT_PACKET_FACTLOCK.md`のみ)。本委任はそれらに触れない。

## 性質/到達上限Status/禁止事項

- 性質: Production配線(ユーザー判断7で方針APPROVED_FOR_PRODUCTION済み、Opus条件Cレビュー済み・M1〜M6/O1〜O3採用)。到達上限Status: `PRODUCTION_WIRED候補(Fable受入待ち)`。PRODUCTION_WIRED確定はFableがruntime evidenceを照合して判定する。本Agentは宣言しない。
- 変更範囲は計画書v2 §(委任_03編集一覧)に限定: (A)予算ガード4ファイルのfail-closed化、(B)routing契約定数7行、kp_explanation、`run_deviation_check`既定値+require_model(O1)、gather_topic/topic_adapter/coverage_gate(O2)、Fiction費用集計(M2)、(C)`pricing_snapshot.json`への6-luna単価追記、(D)必ず落ちるtest更新+単価網羅静的test新設。これ以外のProduction変更禁止(prompt・Checker・Fact Lock要素は一切入れない。Opus指示: 6-luna配線とFact Lock配線は別commit)。
- commit分割(必須): commit 1=Phase 1(単価追記+fail-closed化+静的test)、commit 2=Phase 2(定数+直書き+test更新)、commit 3=Phase 3 evidence+SSOT。切り戻しはcommit 2のrevertのみで成立する構成にする。
- 禁止: `git add -A`・amend・rebase・force push。`er052_output/factlock_writer_trial_01/`・`docs/pm/RESULT_PACKET_FACTLOCK.md`書込禁止。TTS実行禁止(E2Eは本文生成までで止める。音声段があるrunnerは`--no-audio`相当のオプションか、本文生成完了時点で終了するphase指定を使う。存在しなければ本文生成までのstage指定で実行し、TTSが避けられない場合はE2Eを実行せずSTOPして報告)。
- 費用: 上限¥30(Guardrail、Phase 3 E2E 1本+再実行1回分)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- STOP条件: 回帰テストに本変更起因の失敗が残る/E2Eで`ModelContractViolation`または単価未登録例外が出て原因が本変更の設計誤り/E2Eのraw_usageに5.6-lunaが残る工程がある(その場合は該当工程を特定し、修正せずSTOP報告)。
- Opus独立技術レビューGate: 条件C実施済み(反映済み)。本委任で新規該当なし。
- 時間見込み: 約2〜2.5時間(Phase 1 30分/Phase 2 40分/回帰 15分/Phase 3 E2E 20分/SSOT・報告 20分)。並列: 並行Trialの評価と同時進行(API・メモリ負荷は小)。直列: Phase 1→2→3(依存)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Readを基本、全文Readは構造変更時のみ。G-1: git出力は最小化。F-1: transcript退避不要。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ全文保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録(FAILでも継続)。
T-2: 本委任はTTSを伴わない(E2Eは本文生成まで。TTS実行禁止)。
T-3: 費用上限[Cap]は暴走防止Guardrailであり自動STOP閾値ではない(上記定型文)。

## ユーザー指示(原文)

「判断7(新規): 全6-luna化をProduction方針として進めてOK(ネガ判定は微妙(同等)、コストメリットが大きく止める理由がない)」(2026-10-08)。

## KPI provenance欄

- Phase 3受入(process別model_id実測・cost.json>0・予算ガード累計>0): fresh / production_formal_path(Family X Production runnerを正式入口から1記事実行)。E2E自己確認: Yes(fresh Production初回path。ただしTTS段は実行しない)。
- 回帰テスト結果: fresh。

## Opus台帳更新

`docs/pm/OPUS_FINDINGS_LEDGER.md` OF-063〜071 を FABLE_DECIDED→IMPLEMENTED(M1/M2/M4/M5/M6/O1/O2)、→EVIDENCED(M3: E2E実測後)、O3→IMPLEMENTED(SSOT記録)に更新。

## 事前指定Read一覧

- `docs/pm/design_production_model_routing_gpt6_wiring_01.md`(v2)全文
- `docs/pm/RESULT_PACKET.md` 全文
- `er005_output/cost_baseline_01/pricing_snapshot.json` L185-230
- 編集対象(Grepで再確認してからRead): er012_e_family_entertainment_two_level_runner_01.py L105-147 / er019_family_x_entertainment_production_runner_01.py L240-276 / er003_v1_n3_01_advanced_adaptation_generate.py L375-405 / er003_v1_n3_01_standard_a2_generate.py L285-312 / er006_model_routing_contract_01.py L1-40 / er019_family_x_kp_explanation_01.py L38-48, L255-262 / er003_v1_en_direct_vfl_01_generate.py L50-60, L765-815 / gather_topic.py L1-40 / er002_topic_adapter.py L1-30 / er006_research_coverage_gate_01.py L1-25 / er026_family_z_fiction_production_runner_01.py L682-704 / er018_fiction_story_dna_e_axis_redesign_01.py L415-450
- test: er006_model_routing_contract_01_test.py 全文 / er052_all6_writer_trial_01_test_01.py L1-70 / 計画書§1-4の5.6固定期待値test一覧
- Family X Production runnerの入口と本文生成までで止めるオプション: er019_family_x_entertainment_production_runner_01.py のargparse部
- CURRENT_SPEC.md: Grep `ER-006-MODEL-ROUTING-CONTRACT-01|Model Routing` →該当節のみRead

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `except StopIteration|usd = 0\.0` 対象4ファイル → Production経路で単価未登録なら例外(PricingNotFoundError等、新設は最小・1箇所に定義して共有)へ変更。例外メッセージにmodel名を含める。
- Grep `gpt-5\.6-luna` 全*.py(output除外)→ 変更後にProduction経路に5.6リテラルが残っていないこと、Trial scriptは不変であることを件数で確認(変更前後の件数を記録)。
- Grep `WRITER_MODEL|SUPPORT_MODEL|RESEARCH_MODEL` in CURRENT_SPEC.md 該当節 → 「全工程gpt-6-luna(2026-10-08、ユーザー判断7、PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01)」へ更新し、旧「Writerは不変(Opus#15 K7)」記述には「2026-10-08判断7で上書き」と注記(削除しない)。
- DECISION_LOG追記位置: Grep `^## PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01` の直後に委任_03エントリ。追記索引行(L5形式)1行。
- OPEN_ITEMS OPEN-241: Status文字列を `APPROVED_FOR_PRODUCTION(配線完了・回帰PASS・E2E evidence取得・Fable受入待ち)` へ更新し、実測要約を1文追記。
- REPORT_LEDGER: 本件行を更新。
- ACTIVE_TASK.md固定ヘッダ: 管理ID/Status/APPROVED未配線欄を更新(OPEN-241は「配線完了・Fable受入待ち」)。

## 実行コマンド全文

cwd=`C:\Users\tensh\eigo-radio`、python=`.venv\Scripts\python.exe -X utf8`。

0. 委任文全文保存+検証: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-08_PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01_03.md --json-out docs\pm\delegation_log\2026-10-08_PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01_03.md_check.json`
1. Phase 1: pricing_snapshot.jsonにgpt-6-luna(Input 0.10/Cached 0.01/Output 0.50 $/1M、cache writes 0.125を別meter)を5.6と同書式で追記。予算ガード4ファイルをfail-closed化。静的test `er006_model_routing_pricing_coverage_test_01.py` 新設(PROCESS_MODEL_MAPの全OpenAI modelがsnapshotに単価を持つ)。pytest er006_model_routing_pricing_coverage_test_01.py er006_model_routing_contract_01_test.py -q PASS → commit 1。
2. Phase 2: 定数7行を"gpt-6-luna"へ(契約ファイル冒頭コメントに2026-10-08判断7の経緯を追記)。kp_explanation `MODEL = routing.SUPPORT_MODEL`。er003_v1_en_direct_vfl_01_generate.py: `MODEL = routing.WRITER_FACT_CHECK_MODEL`、run_deviation_check内で呼び出し前に`require_model("WRITER_FACT_CHECK", model)`(O1)。gather_topic/topic_adapter/coverage_gateをrouting参照へ(gather_topicはimport追加、`GATE_MODEL = routing.RESEARCH_MODEL`)。Fiction費用集計をrouting由来modelで単価を引く形へ(load_luna_pricing等の5.6専用を汎用化)。test更新。回帰全件: `.venv\Scripts\python.exe run_project_regression.py --pattern "er0*_test*.py"`(既存の正式コマンドがあればそれに従う)→ 全PASS(既知失敗は一覧化して理由を記録)→ commit 2。
3. Phase 3: Family X Production runnerを正式入口から1記事、本文生成まで実行(TTSなし)。テーマは既存の正式Production入力のうち過去に完走した1件を再利用(新規テーマ選定しない)。`--budget-jpy 15`。実測: raw_usage_logのprocess別model_id、cost.json total>0、予算ガード累計>0、STOP/完走、所要秒。結果 `er052_output/gpt6_wiring_e2e_01/E2E_EVIDENCE.md`。
4. SSOT反映(DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC該当節/REPORT_LEDGER/OPUS_FINDINGS_LEDGER/ACTIVE_TASK)→ commit 3 → push。

## SSOT追記文

DECISION_LOG委任_03エントリ案: 「実施内容: Phase 1 pricing_snapshot.jsonへgpt-6-luna単価追記(0.10/0.01/0.50、cache writes 0.125 $/1M)、予算ガード4箇所(er012_e/er019 runner/advanced_adaptation/standard_a2)を単価未登録で例外(fail-closed)化、単価網羅静的test新設[commit 1]。Phase 2 Model Routing契約7定数を全てgpt-6-lunaへ、kp_explanation/vfl01 run_deviation_check(O1)/gather_topic/topic_adapter/coverage_gate(O2)をrouting参照へ、Fiction費用集計をrouting由来modelへ(M2)、test更新[commit 2]。Phase 3 Family X Production E2E 1本(TTSなし): 実測=(結果)[commit 3]。回帰: (件数)PASS。運用規則: (O3)量産最初の10本でEN Advanced deviation STOP 3本以上または保留0.3/記事以上→条件D(QCD悪化)として見直し。旧Trial script(5.6前提89ファイル)は書き換えず、本日以降の再実行は`require_model_or_override`で5.6を明示指定。切り戻し: commit 2のrevert(単価追記・fail-closed化は戻さない)+常駐process再起動。Status: APPROVED_FOR_PRODUCTION(配線完了・Fable受入待ち)。PRODUCTION_WIRED確定はFable判定。Opus条件C M1〜M6/O1〜O3反映済み。」

## Git(明示add対象・コミットメッセージ・trailer)

編集権: CURRENT_SPEC.md(Model Routing該当節のみ)/DECISION_LOG.md/OPEN_ITEMS.md/docs/pm/REPORT_LEDGER.md/docs/pm/OPUS_FINDINGS_LEDGER.md/docs/pm/ACTIVE_TASK.md(PM_GOVERNANCE.mdは不可)。
- commit 1 明示add: pricing_snapshot.json, 予算ガード4ファイル, er006_model_routing_pricing_coverage_test_01.py, 委任文+check.json。メッセージ: 「PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 Phase1: gpt-6-luna単価登録+予算ガードfail-closed化+単価網羅test(Opus条件C M1)」
- commit 2 明示add: er006_model_routing_contract_01.py, er019_family_x_kp_explanation_01.py, er003_v1_en_direct_vfl_01_generate.py, gather_topic.py, er002_topic_adapter.py, er006_research_coverage_gate_01.py, er026..., er018..., 更新test群。メッセージ: 「PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 Phase2: Model Routing全工程gpt-6-luna化(ユーザー判断7)、直書き/Fiction費用集計/Fact Check既定値をrouting参照へ(M2/M4/O1/O2)、回帰N件PASS」。trailer: `Decision-ID: 判断7-2026-10-08` / `Rollback: revert this commit only`
- commit 3 明示add: er052_output/gpt6_wiring_e2e_01/**、SSOT群、REPORT_LEDGER、OPUS_FINDINGS_LEDGER。メッセージ: 「PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 Phase3: Production E2E 1本evidence(全工程model_id=6-luna・費用>0・予算ガード>0)+SSOT反映、実費¥X/¥30、Fable受入待ち」
- push origin main。git add -A禁止。

## 報告(RESULT_PACKET項目)

docs/pm/RESULT_PACKET.mdを上書き(ヘッダ: 管理ID・Status=APPROVED_FOR_PRODUCTION(配線完了・Fable受入待ち)[または停止理由]・実費/¥30・commit 1/2/3 hash)。本文: 1. 受入条件の実測表(process別model_id実測一覧[5.6残存の有無]、cost.json値、予算ガード累計、STOP/完走、所要秒、回帰件数PASS/FAIL、静的test PASS)。2. 変更ファイル一覧(ファイル:行、変更概要)と5.6リテラル件数の前後。3. 切り戻し手順の確定版(revert対象commit hash)。4. 問題・残作業(blockingか明示)。5. check_delegation_prompt結果1行、一覧外Readの理由。6. raw URL一覧。推奨は書かず事実のみ。
