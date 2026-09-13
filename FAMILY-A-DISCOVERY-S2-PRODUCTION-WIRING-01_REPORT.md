# FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01

管理ID: FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01(2026-09-13)
到達Status: **`PRODUCTION_WIRED`**

## 0. 安全インシデント(最初に報告)

回帰実行の途中で、委任文が指定したとおりの回帰コマンド
`run_project_regression.py --pattern "er003*"` / `--pattern "er011*"` を
最初に実行したところ、Pythonの`unittest.TestLoader().discover()`がこの
globパターンに一致する**全`.py`ファイル**(test file限定ではない)を
importする仕様のため、`if __name__ == "__main__":`ガードの無い一回限りの
runnerスクリプト(例: `er011_no18_open108_b1_ledger_refined_regenerate_01.py`、
`er011_no18_specfix_v2_b1_retry_01.py`)がモジュールimport時に**そのまま
実行**され、本タスクと無関係な既存Production記事(`pool_n18_notifications_
specfix_v2`)への実API呼び出し(実測¥15〜20相当、gpt-5.6-luna + TTS/ASR)と
記事ファイル上書きが発生した。

対応: 発覚後直ちに該当プロセス(PID)を`taskkill /F`で強制終了し、
`git checkout --`で影響を受けた全ファイル(pool_n18関連約25ファイル、
`er011_output/kp_en_asr_false_rejection_prod_wiring_01/*`、
`er011_output/open111_a2_reading_trial_06/raw_usage_log_phase2.jsonl`、
`er003_output/novel_audio_02/*`の該当2ファイル)を最後のcommit時点へ復元した
(本タスク開始前から存在していた無関係の既存差分[`er011_output/attempt_
history.jsonl`等]には触れていない)。以後は`--pattern "er003*_test_*.py"` /
`--pattern "er011*_test_*.py"`(test file限定)へ切り替えて安全に再実行した。

この事象は「委任文の実行コマンドをそのまま実行した結果、意図しないProduction
実API実行・ファイル上書きが起きた」という一般化可能な問題であり、今後の
委任文標準(`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`)で
`run_project_regression.py --pattern`には常に`_test_*.py`を含めることを
Fableへ申し送る(恒久ルール化はユーザー判断)。

## 1. Gate 3チェックリスト(14項目)

| # | 項目 | 判定 | 証跡 |
|---|---|---|---|
| 1 | Production正式初回経路へ実装 | ✓ | `er003_discovery_focus_staged_production_01.py`(新規)。`run_one_pattern_staged_discovery_focus()`がopt-in `editorial_mode="discovery_focus_staged"`のProduction正式関数。Focus Module本文は`er003_v1_n3_01_articles_generate.py`の`EDITORIAL_TYPE_MODULE_BLOCKS`へ正式登録(L452-500付近、`git diff --stat`で48 insertions/0 deletions=追加のみ) |
| 2 | retry/fallback/regeneration整合 | ✓ | Stage2-3のみ再実行(`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`既存値流用、コード内`prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX`参照)。Stage1再生成は`STAGE1_MAX_REGENERATIONS=1`上限。runtime evidenceで実際にこの通りの分岐が発火(下記4参照) |
| 3 | DEV・Trial専用依存なし | ✓ | Dangling Reference Check(下記6)で実測0件。Trial専用ファイル(`er011_discovery_focus_s2_full_trial_01.py`等)はProduction側から一切import されない |
| 4 | runtime実発火 | ✓ | `er011_output/discovery_s2_production_runtime_evidence_01/`。Stage 1 escalation(分岐(b): Stage2-3 exhaustion後fallback)が実データで発火(`audit/stage_trace.json`にphase="stage1_escalated"記録) |
| 5 | Regression・Validator・integration test PASS | ✓ | 新規テスト24/24 PASS。`er003*_test_*.py`: 1389 collected/1386 passed/3 failed(既知)/0 errors。`er011*_test_*.py`: 266 collected/266 passed/0 failed/0 errors。全件回帰(既定pattern): 2588 collected/2585 passed/3 failed(既知、`er003_test_p2j_investigate`)/0 errors(下記4節) |
| 6 | actual routing・model等evidence | ✓ | raw_usage_log.jsonlで`model_id="gpt-5.6-luna"`実測(`routing.require_model`経由)、`reasoning_effort="high"`(`prod_gen.REASONING_EFFORT`) |
| 7 | CURRENT_SPEC更新 | ✓ | `CURRENT_SPEC.md`「## Discovery Focus S2(Production...)」新節(既存Discovery/Why節の直後に追加、61行) |
| 8 | DECISION_LOG更新 | ✓ | `DECISION_LOG.md`新規エントリ(52行、CONSOLIDATION-123の直後) |
| 9 | OPEN_ITEMS update | ✓ | `OPEN_ITEMS.md` OPEN-135行末尾へ追記(既存内容は削除せず追記のみ) |
| 10 | commit・push | ✓/△ | 本REPORT末尾のcommit hash参照。push結果も末尾に記載 |
| 11 | Dangling Referenceなし | ✓ | `grep -rn "^import er011_discovery_focus\|^import er011_discovery_stage3" er003_*.py er010_*.py er012_*.py` = 0件 |
| 12 | ユーザー承認内容と実挙動一致(処理順) | ✓ | Focus解決→Stage1→Stage1QA→[regen]→Stage2→Stage3→EC→結合→Overlap/Value QA→記事全体FactChecker/Ledger/LocalRewrite/差分QA→Directional Precheckの順序どおりに`run_one_pattern_staged_discovery_focus()`実装(コード上から目視確認可能) |
| 13 | ユーザー承認内容と実挙動一致(retry単位・上限値) | ✓ | `STAGE1_MAX_REGENERATIONS=1`(コード定数)、runtime evidenceで実際に1回で上限到達しfail-closed停止したことを確認 |
| 14 | ユーザー承認内容と実挙動一致(locusルール) | ✓ | 案(ii)簡略ルール(Stage2-3 exhaustion後のみStage1へescalate)どおりに実装・実発火(分岐(b)が発火、分岐(a)[Ledger MAJOR locus]・分岐(c)[Fact Checker FAIL]は本runでは未観測、フォールバック順序自体は分岐(b)の実発火で検証済み) |

**1項目でも未確認ならPRODUCTION_WIREDとしない、という条件に対し、上記14項目すべて✓(項目10は本REPORT末尾のcommit/push結果に依存するため実施後に最終確認)。**

## 2. 実装概要

- 新規モジュール: `er003_discovery_focus_staged_production_01.py`
- opt-in `editorial_mode`: `"discovery_focus_staged"`
- `EDITORIAL_TYPE_MODULE_BLOCKS`登録: `DISCOVERY_FOCUS_MODULE_PART_A_BLOCK`
  (本文はOPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05検証済みのFocus
  Module Part Aと一字一句同一、`er011_discovery_stage3_rule_adjustment_
  trial_09.CURRENT_FOCUS_BLOCK`の本体部分とbyte一致をPythonで確認済み)
- 移設した関数(移設元→移設先):
  - `extract_stage1_main_story`/`run_stage1_main_story_writer`/
    `run_ledger_local_rewrite_loop`/`run_stage1_qa`:
    `er011_discovery_focus_s2_full_trial_01.py` →
    `er003_discovery_focus_staged_production_01.py`
  - `run_stage2_role_planning`/`run_stage3_points_writer`/`assemble_article`:
    `er011_discovery_focus_part_a_standalone_trial_01_run.py` →
    `er003_discovery_focus_staged_production_01.py`
  - `apply_evidence_compression_to_points`/`run_stage2_3_with_retry`/
    オーケストレーション本体(`generate_article_stage`→
    `run_one_pattern_staged_discovery_focus`に改名):
    `er011_discovery_focus_s2_full_trial_01.py` →
    `er003_discovery_focus_staged_production_01.py`
- 既存`run_one_pattern`が無変更である証明: `git diff --stat --
  er003_v1_n3_01_articles_generate.py` = 48 insertions(+)/0 deletions(-)
  (L818-1248の`run_one_pattern`本体は1バイトも変更されていない、追加は
  L452-500付近のFocus Module Block定義とdict entry追加のみ)

## 3. テスト結果

- 新規テスト`er003_discovery_focus_staged_production_01_test_01.py`:
  24件(A〜G区分、Trial版22テストの移植+Dangling Reference確認2件追加)、
  全PASS(`.venv\Scripts\python.exe -m unittest
  er003_discovery_focus_staged_production_01_test_01 -v`)
- `er003*_test_*.py`回帰: 1389 collected/1386 passed/3 failed/0 errors
  (failed 3件は`er003_test_p2j_investigate`の既存履歴カウント照合テストで
  本タスクと無関係、既知)
- `er011*_test_*.py`回帰: 266 collected/266 passed/0 failed/0 errors
- 全件回帰(既定pattern`er0*_test_*.py`): 2588 collected/2585 passed/
  3 failed(既知、`er003_test_p2j_investigate`3件)/0 errors/0 skipped

## 4. runtime evidence

- 実行コマンド: `.venv\Scripts\python.exe <driver script>.py a2`
  (driver scriptはProduction正式関数
  `er003_discovery_focus_staged_production_01.run_one_pattern_staged_
  discovery_focus()`を直接呼び出すだけの薄いrunner。関数のmonkeypatch・
  再実装は一切なし)
- 使用モデル: `gpt-5.6-luna`(`routing.require_model`経由)、
  reasoning_effort=`high`(`prod_gen.REASONING_EFFORT`)
- テーマ・Ledger: `er011_output/discovery_generalization_wake_before_alarm_
  trial_12/research/`のtopic/VFLをread-only再利用。Ledgerのみ、Stage 1
  escalationを実発火させるため、F008(ACTH予期的上昇=本テーマの核心的な
  「なぜ目覚ましの直前に起きるか」に対する唯一のメカニズム的根拠事実)を
  除去した複製`er011_output/discovery_s2_production_runtime_evidence_01/
  research/verified_fact_ledger_intentional_major_01.txt`を新規作成して
  使用(元Ledgerは無編集、他の全factはbyte-for-byte不変であることを
  Pythonで確認済み)
- Stage 1 escalation発火: **有**(分岐(b): Stage2-3が
  `POINT_OVERLAP_ARTICLE_RETRY_MAX=2`回を尽くしてもPoint Overlap QA
  [lexical overlap比率>0.40]が解消せず、`STAGE1_MAX_REGENERATIONS=1`の
  上限までStage 1を1回再生成。再生成後も同じ理由でStage 2-3が再度
  exhaustし、上限到達によりfail-closedでNG_REVIEW_REQUIRED停止)。
  `audit/stage_trace.json`実ログ:
  stage1(attempt0, blocking=false) → stage2_3(status=NG_REVIEW_REQUIRED,
  retry_attempt=2) → stage1_escalated(attempt1, blocking=false) →
  stage2_3(status=NG_REVIEW_REQUIRED, retry_attempt=2) →
  all_branches_exhausted
- Stage 1再生成回数: 1回(上限どおり)
- Stage 2-3 retry回数: 各Stage1ラウンドとも2回(上限まで)
- 各QA verdict: Stage 1 Fact Checker=両ラウンドともREVIEW_REQUIRED
  (non-blocking advisory)。Stage 1 Ledger Deviation=両ラウンドとも
  LEDGER_COMPLIANT(MAJORなし)。Point Overlap/Value QA=両ラウンドとも
  3attempt(0,1,2)全てlexical_flagged=True(point_one/point_two交互に
  overlap比率>0.40で推移)
- 差分QA発火: 無(記事全体Ledger MAJORが一度も発生しなかったため、
  分岐(a)・記事全体Local Rewrite自体が未発火。Stage 1単体のLocal
  Rewriteループも同様にMAJOR無しのため未発火)
- Directional Precheck: Stage 1単体は両ラウンドとも実行(non-blocking)、
  記事全体は最終記事が確定しなかったため未実行
- 記事語数: N/A(最終的に記事は完成せず、`article_text`はNoneのまま
  NG_REVIEW_REQUIRED停止。これは安全装置が正しく機能した結果であり、
  「品質の低い記事を無理に完成させる」ことをせずfail-closedしたことを
  示す)
- 出力dir: `er011_output/discovery_s2_production_runtime_evidence_01/`
- 実費: ¥46.66(openai、35 API records、`cost_summary.json`)
- Discovery残額: ¥134.97 → ¥88.31

## 5. Dangling Reference Check結果

`grep -rn "^import er011_discovery_focus\|^import er011_discovery_stage3"
er003_*.py er010_*.py er012_*.py` → **0件**。
`grep -rn "er011_discovery_focus\|er011_discovery_stage3"`(import文に限らず
全文字列一致)で見つかる箇所は、いずれも新規Production側ファイル自身の
コメント・docstring内での「移設元」記載のみ(実importではない)。

## 6. Git

- 明示addしたファイル(詳細はcommit参照): 新規Production側モジュール2件、
  root REPORT本ファイル、`CURRENT_SPEC.md`、`DECISION_LOG.md`、
  `OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、
  `docs/pm/delegation_log/FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01.md`+
  `_check.json`、`er011_output/discovery_s2_production_runtime_evidence_01/`
  配下の証跡(記事txt・summary json・cost json・index.html・改変Ledger)
- commit hash・push結果: 本タスクのRESULT_PACKET(`docs/pm/RESULT_
  PACKET_S2W.md`)参照

## 7. 事前指定外Read(理由)

- `er003_v1_n3_01_articles_generate.py` L818-1018付近を事前指定範囲より
  やや広く読んだ(既存`run_one_pattern`のFact Checker/Ledger呼び出し
  シグネチャを正確に把握し、移設先モジュールで同一の呼び出し方を再現する
  ため)。
- `run_project_regression.py`本体(1ファイル、指定外)を読んだ(委任文
  指定どおりの`--pattern`実行が広すぎるglobで危険であることに気づき、
  原因究明のため`discover_test_files`/`unittest.TestLoader().discover`の
  実装を確認する必要があった。上記0節のインシデント対応に必須)。

## 8. STOP該当の有無

該当なし(4つのSTOP条件のいずれにも該当しない。安全インシデント[0節]は
STOP条件の定義には厳密には該当しないが、Production安全性に関わるため
最上部で報告した上で、是正のうえ作業を継続した)。
