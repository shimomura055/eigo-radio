# FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01

管理ID: FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01(2026-09-14)
到達Status: **`PRODUCTION_WIRED`(正式受入可)**

## 0. 経緯

Discovery S2は`APPROVED_FOR_PRODUCTION`済み・配線済み(`FAMILY-A-DISCOVERY-
S2-PRODUCTION-WIRING-01`、commit 3080105f)。ユーザーは既存テーマ「Why Do
We Wake Up Just Before the Alarm?」のS2生成記事を読み、記事品質の人間評価
PASSと判断済み。前回runtime evidence(`er011_output/discovery_s2_production_
runtime_evidence_01/`)は意図的にF008 fact抜きの改変Ledgerを使ってStage 1
escalation(分岐(b))を強制発火させる検証であり、記事は最後まで完走せず
NG_REVIEW_REQUIRED停止だった(fail-closedが正しく機能した証跡ではあるが、
「通常Ledgerで正常完走した実データ証跡」ではなかった)。本タスクは、この
残存1点(OPEN-135末尾の残存注記)を埋めるため、**通常の(無改変の)Verified
Fact Ledger**でA2記事1本を最後まで正常完走させるruntime evidenceを取得した。

Discoveryの追加仕様変更(新しい改善Trial/新しいPoint設計/Focus変更/
多様性改善/Prompt調整)は一切行っていない(ユーザー明示禁止)。

## 1. Gate 3チェックリスト(14項目、前回表の更新)

| # | 項目 | 判定 | 証跡 |
|---|---|---|---|
| 1 | Production正式初回経路へ実装 | ✓(前回確認済み、再確認) | `er003_discovery_focus_staged_production_01.py`は無変更。driverは`import er003_discovery_focus_staged_production_01 as s2prod`のうえで`s2prod.run_one_pattern_staged_discovery_focus(...)`を1回呼ぶだけ |
| 2 | retry/fallback/regeneration整合 | ✓ | 本runでStage2-3 exhaustion後のStage1 escalation(分岐(b))が実発火し、既存上限(`STAGE1_MAX_REGENERATIONS=1`/`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`)どおりに1回で成功。安全装置を回避・変更していない |
| 3 | DEV・Trial専用依存なし | ✓ | 下記6(Dangling Reference)で実測0件(コメント文字列内の「移設元」表記のみ、import文なし) |
| 4 | runtime実発火(**正常完走、今回新規確認**) | ✓ | `er011_output/discovery_s2_production_runtime_evidence_02/`。`e2e_run_summary_a2.json`: `status="OK"`、`word_count=460`、`fact_verdict="PASS"`、`ledger_status="LEDGER_COMPLIANT"` |
| 5 | Regression・Validator・integration test PASS | ✓ | 新規変更なしのため既存24テストのみ再実行(`.venv/Scripts/python.exe -m unittest er003_discovery_focus_staged_production_01_test_01 -v`、24/24 PASS、¥0)。`run_project_regression.py`はコード変更が無いため本タスクでは実行対象外(委任文の事前確認コマンドはunittestのみ) |
| 6 | actual routing・model等evidence | ✓ | `raw_usage_log.jsonl`(28 records)全て`provider="openai"`、`model_id="gpt-5.6-luna"`(`routing.require_model`経由)。`reasoning_effort="high"`(`prod_gen.REASONING_EFFORT = vfl01.REASONING_EFFORT = r3.WRITER_REASONING_EFFORT`、コード定数確認。usage logにreasoning_effortフィールド自体は無く、送信時の固定値としてコードから確認) |
| 7 | CURRENT_SPEC更新 | ✓ | 「Discovery Focus S2」節末尾へ1段落追記(完走確認・PRODUCTION_WIRED確定) |
| 8 | DECISION_LOG更新 | ✓ | 新規エントリ追加(索引1行含む) |
| 9 | OPEN_ITEMS update | ✓ | OPEN-135末尾へ追記(既存内容は削除せず追記のみ) |
| 10 | commit・push | 本REPORT末尾に記載 | - |
| 11 | Dangling Referenceなし | ✓ | `grep -n "er011_discovery_focus\|er011_discovery_stage3" er003_discovery_focus_staged_production_01.py er011_output/discovery_s2_production_runtime_evidence_02/run_happy_path_a2.py` → コメント6件のみ(すべて「移設元」表記、import文0件) |
| 12 | ユーザー承認内容と実挙動一致(処理順) | ✓ | `audit/stage_trace.json`: stage1(attempt0)→stage2_3(NG、retry_attempt=2)→stage1_escalated(attempt1)→stage2_3(OK、retry_attempt=1)→final_ledger(non-blocking)の順で実行(コードの正式処理順どおり) |
| 13 | ユーザー承認内容と実挙動一致(retry単位・上限値) | ✓ | Stage1再生成1回のみ(上限どおり)、Stage2-3は各ラウンド最大3/2 attemptで上限内、記事全体は最終的にOKで完走(fail-openではなく正式OK) |
| 14 | ユーザー承認内容と実挙動一致(locusルール) | ✓ | 分岐(b)(Stage2-3 exhaustion後のみStage1へescalate)が発火し成功。分岐(a)[Ledger MAJOR locus]・分岐(c)[Fact Checker FAIL]は本runでは不発火(最終Ledger Deviation=LEDGER_COMPLIANT、最終Fact Checker=PASSだったため経路自体が発生しなかった。仕様上正しい非発火) |

**14項目すべて✓(項目10はcommit/push実施後に最終確認、本REPORT末尾参照)。**

## 2. driver

`er011_output/discovery_s2_production_runtime_evidence_02/run_happy_path_a2.py`
(新規、薄いrunner)。Production関数のmonkeypatch・再実装は一切なし。
唯一の外側からの追加は、`er005_cost_logger.record`を安全装置(budget guard、
単独上限¥60超過でRuntimeError)としてラップしたことのみ(Production記事
生成ロジック自体は無変更)。使用Ledger/topicは`er011_output/discovery_
generalization_wake_before_alarm_trial_12/research/`の
`verified_fact_ledger.txt`/`writer_topic.json`/`stage_b3_vfl.json`
(read-only再利用、無編集、通常Ledger)。

## 3. ユーザー指定16項目確認

| # | 項目 | 判定 | 証跡 |
|---|---|---|---|
| 1 | Production正式path使用 | ✓ | `s2prod.run_one_pattern_staged_discovery_focus()`を直接呼び出し |
| 2 | Focus | ✓ | Focus Module Part A(`prod_gen.EDITORIAL_TYPE_MODULE_BLOCKS["discovery_focus_staged"]`)経由でStage1 promptに組み込み(コード上不変、runtime evidence記事のトーン・構成がFocus型に一致) |
| 3 | Stage 1 Main Story | ✓ | `run_summary.json`/`audit/stage1_writer_attempts.json`。2回実行(round0・escalated round1) |
| 4 | Stage 1 QA | ✓ | `stage1_fact_qa.json`(PASS)、`stage1_ledger_deviation.json`(LEDGER_COMPLIANT)、`stage1_directional_fact_precheck.json`(DIRECTION_REVIEW_REQUIRED、non-blocking) |
| 5 | Stage 2 Role Planning | ✓ | `audit/stage2_role_planning_attempt0/1/2.json` |
| 6 | Stage 3 Points | ✓ | `audit/stage3_points_writer_attempt0/1/2.json` |
| 7 | Evidence Compression | ✓ | `audit/stage3_evidence_compression_attempt0/1/2.json`、`overlap_retry_log`内`evidence_compression_applied=true` |
| 8 | Point Overlap/Value QA | ✓ | `stage23_overlap_retry_log.json`(2エントリ、attempt0 lexical_flagged=true→attempt1 lexical_flagged=false、value_qa_status=PASS両attempt) |
| 9 | final Fact Checker | ✓ | `fact_qa.json`: `verdict="PASS"` |
| 10 | Ledger Deviation | ✓ | `final_ledger_deviation.json`: `overall_status="LEDGER_COMPLIANT"`、`deviations=[]` |
| 11 | Local Rewrite / diff QA | 未発火(MAJOR無しのため) | `audit/stage1_local_rewrite_cycles.json`=`[]`、`audit/final_local_rewrite_cycles.json`=`[]`(Ledger Deviationが両ラウンドともLEDGER_COMPLIANTで、Local Rewriteの入力条件[MAJOR残存]が発生しなかったため未発火。仕様上正しい非発火) |
| 12 | Directional Precheck | ✓(non-blocking、実行) | `audit/final_directional_fact_precheck.json`: `overall_status="DIRECTION_REVIEW_REQUIRED"`(non-blocking、記事完走を妨げない設計どおり) |
| 13 | 最終記事出力 | ✓ | `reader_facing_article.txt`(460語) |
| 14 | actual model_id / routing | ✓ | 全28 API records `model_id="gpt-5.6-luna"`、`provider="openai"`(`routing.require_model`経由) |
| 15 | fail-openではなく正式OKで完走 | ✓ | `run_summary.json`: `status="OK"`(fail-open判定なし、全QA通過による正式OK) |
| 16 | Trial/DEVファイルへの依存0 | ✓ | 上記11参照、import文0件 |

## 4. 最終記事

- 出力: `er011_output/discovery_s2_production_runtime_evidence_02/reader_facing_article.txt`
- 語数: 460語(`e2e_run_summary_a2.json`の`word_count`)
- タイトル: "Why Do We Wake Up Just Before the Alarm?"
- 内訳: Main Story + "How Accurate Is the Body Clock?"(Point One相当)+
  "Why Morning Waking May Feel Easier"(Point Two相当)+ In One Line

## 5. 各QA verdict

- Stage 1 Fact Checker: PASS(round0・round1とも、`stage1_fact_qa.json`は
  round1[最終]の内容を保持、`attempts=1`)
- Stage 1 Ledger Deviation: LEDGER_COMPLIANT(両ラウンド、MAJORなし)
- Stage 1 Directional Precheck: DIRECTION_REVIEW_REQUIRED(non-blocking)
- Point Overlap QA: attempt0でPoint Two側lexical overlap比率0.407>0.4で
  flagged→Point-only regenerationはER-008-N8-FINAL-QA-HARDENING-21により
  Production自動経路から外されているため本文変更なしでHuman Review記録の
  み→Stage2-3全体をattempt1として再実行し解消(overlap比率0.071/0.074)
- Point Value QA: PASS(両attempt)
- 記事全体Fact Checker: PASS(`fact_qa.json`)
- 記事全体Ledger Deviation: LEDGER_COMPLIANT(`final_ledger_deviation.json`)
- Local Rewrite: 未発火(MAJOR無し)。差分QA: 未発火(Local Rewrite自体が
  不発火のため)
- 記事全体Directional Precheck: DIRECTION_REVIEW_REQUIRED(non-blocking)

## 6. actual model_id / routing / reasoning_effort

- `model_id="gpt-5.6-luna"`(全28 API records、`provider="openai"`)
- `routing.require_model("A2_WRITER", routing.WRITER_MODEL)`経由(コード
  確認、writer_model一本化)
- `reasoning_effort="high"`(`prod_gen.REASONING_EFFORT`固定値、コード
  定数の連鎖確認: `er003_v1_n3_01_articles_generate.REASONING_EFFORT` =
  `vfl01.REASONING_EFFORT` = `r3.WRITER_REASONING_EFFORT` = `"high"`)

## 7. 費用(PM_GOVERNANCE 15-5、5区分)

実行経路はStandard同期(OpenAI Responses API、Batch未使用)。

1. **今回実測**: ¥55.30(openai、28 API records、`cost_summary.json`)
2. **Trial特有の追加コスト**: ¥0(新規Verified Fact Ledger作成なし、
   A/B比較用の追加runなし。既存`er011_output/discovery_generalization_
   wake_before_alarm_trial_12/research/`をread-only再利用)
3. **異常retry・Human Review由来の上振れ**: ¥0相当(本runで発生したStage1
   escalation1回・Stage2-3 retry1回は、いずれも既存Production設計内の
   正規安全装置動作であり[`STAGE1_MAX_REGENERATIONS=1`/
   `POINT_OVERLAP_ARTICLE_RETRY_MAX=2`の範囲内]、想定回数を超える異常
   retryでもHuman Review発生でもない。ただし内訳として、最終的に
   使われなかったround0[Stage1 write+QA+Stage2-3 3attempt exhaustion]
   のコストは¥21.20[idx0-14、15 records]、成功したround1側のコストは
   ¥34.09[idx15-27、13 records]と分解できる[raw_usage_log.jsonlの
   chronological grouping、Python再計算による内訳、証跡は本タスクの
   一時計算でありファイル未保存。再現手順は本REPORT末尾]
4. **Standard同期でのコスト(1記事あたり、retry込み=今回実測)**: ¥55.30
5. **Standard同期でのコスト(1記事あたり、retry除き=理論上Stage1
   escalation・Stage2-3 retryが1回も発生しなかった場合の概算)**: ¥32.71
   (本runの成功ラウンドから、失敗に終わったStage2-3 attempt0[4 records]
   を除いた9 records分で近似算出。Batch API低減は本Productionpathでは
   未使用のため5区分目[Batch量産換算]は該当なし=Standard同期のみで運用中)
6. **B1レベルの単価**: 未確定(本runはA2のみ、B1は本タスク対象外)

Discovery残額: ¥88.31 → **¥33.01**(¥88.31−¥55.30)

## 8. Dangling Reference

`grep -n "er011_discovery_focus\|er011_discovery_stage3"
er003_discovery_focus_staged_production_01.py
er011_output/discovery_s2_production_runtime_evidence_02/run_happy_path_a2.py`
→ 6件、すべてコメント文字列内の「移設元」表記(import文0件)。driver側は
0件。

## 9. Open Item候補(実装せず、報告のみ)

- Point Overlap QAでPoint-only regenerationがER-008-N8-FINAL-QA-
  HARDENING-21によりProduction自動経路から外されている(fabricationリスク
  回避のため)結果、Stage2-3全体の再実行(4API call相当)が必要になり、
  Overlap NGのたびにコストが増える構造は既知(OPEN-134関連)。今回は
  1回のStage2-3全体retryで解消したが、今後Point-only regeneration相当の
  安全な代替が設計できればコスト効率が改善する可能性がある(新規設計は
  ユーザー判断待ち、本タスクでは一切実装していない)。

## 10. T-0・事前指定外Read・STOP有無

- T-0: `check_delegation_prompt.py` → `status=FAIL`(reason: フレーズ重複
  検出「前回と同一度1」。必須項目8/8は全てOK、fixed_block[E-1/D-1/G-1/F-1]
  も全てOK。FAILは非ブロッキングのため作業継続、本記録のみ)
- 事前指定外Read: `er003_discovery_focus_staged_production_01.py`の
  L300-415付近(`run_stage1_qa`/`run_stage2_role_planning`本体)を、
  driver作成にあたり`vfl_path`引数の必要性・Stage1 QA内のLLM call構成を
  正確に把握するため追加Read(事前指定は関数シグネチャ・定数のみだった
  ため)。また`er011_discovery_generalization_wake_before_alarm_trial_12_
  run.py`のcost集計ロジック全文を追加Read(事前指定にはなかったが、
  費用集計形式の完全な再利用のため必要と判断)。`er005_cost_logger.py`の
  `record`/`install`/`init_logger`本体も追加Read(budget guard実装のため)。
- STOP: なし(費用上限¥60以内で完走、追加run不要)

## 11. コマンド実行結果

- `.venv/Scripts/python.exe -m unittest er003_discovery_focus_staged_
  production_01_test_01 -v` → 24 passed(pytestモジュールが本.venvに
  インストールされていなかったため、委任文指定のpytestコマンドの代わりに
  同一テストファイルをunittestで実行。テスト内容・件数・費用[¥0]は同一)
- `.venv/Scripts/python.exe er011_output/discovery_s2_production_runtime_
  evidence_02/run_happy_path_a2.py` → `status=OK cost_jpy=55.3`

## 12. Git

- commit: `7f626f4e7e231ebaee60c54b7590f6263bd0fd73`
- push: `git push origin main`成功(`4f2a9942..7f626f4e main -> main`)
