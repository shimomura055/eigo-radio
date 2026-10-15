# VALIDATION_OFF_01: gloss再整合flag既定OFF化(KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_02、2026-10-15)

Status: 既定OFF 実装・test・runtime evidence 取得済み。**PRODUCTION_WIRED判定待ち(Fable照合後)**。gloss再整合工程自体のProduction採用ではない(`APPROVED_FOR_PRODUCTION`は工程に付けない)。
根拠: ユーザー2026-10-15承認(案a: 安全措置としての既定値変更のみ)。Opus独立レビュー: 非該当(既定値変更1点)。

## 0. 変更(1点のみ)
`er003_key_words_gloss_alignment.py:42-45` `GLOSS_ALIGNMENT_ENABLED = os.environ.get("EIGO_KP_GLOSS_ALIGNMENT","0").strip().lower() in ("1","true","on","yes")`(旧: 既定"1"=ON、`0/false/off`でOFF)。import時評価は既存設計のまま(最小変更)。ロジック(corrected/legacy・Prompt・機械検査・HR報告書・Gate・Lock)は無変更。
明示ON: `EIGO_KP_GLOSS_ALIGNMENT=1` または `align_glosses(enabled=True)`/`preflight(True)`の明示引数(DEV/Trial)。`mode=corrected`はPython引数でのみ指定可(X/Z CLIにgloss関連optionなし=offcheck_01.json)。
注意(事実報告): corrected mode経路は`run_key_phrase_canonicalization`内で`enabled=True`を明示して呼ぶ既存設計(Trialが明示`gloss_alignment_mode="corrected"`を渡した時点で明示ON扱い)。本委任では変更していない。通常Production経路はlegacy既定で`enabled`未指定=本flag(既定OFF)に従う。

## 1. 隔離確認表(コード上)
| 経路 | 既定OFFを継承する根拠 | 確認 |
|---|---|---|
| 共通到達点 | `sc.run_key_phrase_canonicalization`(scaffold:736 legacy分岐)が`align_glosses(...)`を`enabled`未指定で呼び、`align_glosses`(gloss module:~421)が`enabled=None`時に`GLOSS_ALIGNMENT_ENABLED`を参照 | test `DefaultOffIsolation.test_scaffold_canonicalization_default_off_no_call_no_change_no_files` |
| `run_key_phrases`(scaffold:813) | `gloss_align.preflight()`が既定OFFで`None`(承認規則抽出も走らない) | offcheck_01.json `preflight_default: null` |
| Standard / Advanced | 両levelとも上記共通到達点経由(Family X: a2/b1b、Family Z: a2/b1b[Std/Adv]) | 同上 |
| Family X 正式runner(er019) | `run_theme_scaffold(*, gloss_alignment_mode="legacy")`、CLIにgloss option無し | offcheck_01.json、evidence_x(実runner実行) |
| Family Z 正式runner(er026) | `E2EContext.gloss_alignment_mode`既定legacy、`_kp_fn_for_ctx`既定は素の`run_kp_with_outer_retry`、CLIにgloss option無し | offcheck_01.json、evidence_z(mock runner) |
| 起動スクリプト(.ps1/.bat/.sh) | `EIGO_KP_GLOSS_ALIGNMENT`を設定するスクリプト無し(rg確認。参照は*.mdの説明文のみ) | rg結果 |
| Legacy A/B/C 等(`run_key_phrases`/`run_key_phrase_canonicalization`を呼ぶ旧runner・Trial script約65ファイル、`rg -l`) | 全て同じ共通到達点を通るため同じく既定OFF。個別改修なし(一覧のみ。`rg -n "run_key_phrases\(|run_key_phrase_canonicalization\(" --glob "*.py" -l`) | 共通到達点のtest |
| er071 Trial/証跡script | `enabled=True`/`preflight(True)`/`mode="corrected"`を明示するものは影響なし。`er071_completion_04_gloss_realign.py`等の`enabled`未指定の旧証跡scriptは今後`EIGO_KP_GLOSS_ALIGNMENT=1`が必要(再実行する場合のみ) | rg結果 |

## 2. test(`er003_test_key_words_gloss_alignment.py`、76 passed)
既存testは各classに`@_explicit_on`(各testでmodule flagを明示ONにし終了時に復元)を付与して「明示ON経路」を維持。`test_default_flag_on_and_default_mode_keep`は`test_default_mode_keep`へ改題(ON前提のassert削除)。新設`DefaultOffIsolation`(5件):
- `test_env_unset_is_off_and_explicit_values`: 新規subprocessでenv未設定/`0`/空=False、`1`/`true`=True
- `test_default_noop_legacy_and_corrected`: mode None/legacy/corrected全てstatus=DISABLED・mergedは同一object・attempts空・API fn呼出0・out_dirにartifact/HR報告書なし・`preflight()`=None
- `test_scaffold_default_off_makes_no_alignment_call`: `make_alignment_fn`をAssertionErrorにpatchして未生成
- `test_scaffold_canonicalization_default_off_no_call_no_change_no_files`: Production関数`sc.run_key_phrase_canonicalization`でmode None/legacyとも`gloss_alignment_status=DISABLED`、`make_alignment_fn`呼出0、保存gloss不変(『～をもとにした』)、`gloss_alignment_status`item記録なし、GLOSS/HUMAN_REVIEW名のファイルなし
- `test_explicit_on_still_works`: `enabled=True`で動作(API 1回)

## 3. runtime evidence
### 3-1. Family X 正式runner(er019): **fresh**(実LLM)、KP段のみ、E2E自己確認=No(TTS/assemble含まず)
- 使用モデル: Production既定のKP routing(db_hybrid + canonicalization + redundancy QA、openai系)。評価Trialではなく既存Production配線のそのままの実行(最新モデル原則の適用対象外=Production line、モデル選定は別判断)。
- 入力: 既存Coffee run dir `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01` から`entry_point.json`/`plan_run_result.json`/`a2/{a2_support_texts,parts,segment_plan}.json`/`a2/audit`のみ**コピー**(元dirは未編集)した `evidence_x/run_off_01/`。
- コマンド(STOP範囲: `docs/pm/delegation_log/*STOP_NOTICE*`はMelos用と別スコープ[Melos E2E/STOP-NOTICE-SCOPE]で本タスクのX/KP段対象外、`<run>/STOP`/`STOP_ALL`なしを確認してから実行):
  `env -u EIGO_KP_GLOSS_ALIGNMENT TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_v5_ms_01 --level a2 --stage scaffold --scaffold-only kp --out-dir er071_output/m2p0_n01_production_wiring_01/gloss_alignment_default_off_01/evidence_x/run_off_01 --budget-jpy 3`
- 結果: rc=0、`key phrase status=CANONICALIZATION_PASS`、費用JPY1.83(上限3以内、内訳: KP選定+canonicalization+redundancy QA 1回retry[通常の外側retry])。`raw_usage_log.jsonl` 6件は全て stage=scaffold(KP選定/canon/QA)で、gloss再整合のstageタグ`kp_gloss_alignment`は0件。`key_phrases/`にgloss alignment artifact・HR報告書・NOTICE・`gloss_alignment_*`ファイルなし。stdout: `evidence_x/runner_stdout.log`。
- 限界: 本runでは`gloss_alignment_status="DISABLED"`はsummaryに記録されない(既存artifactに記録箇所なし、記録は追加していない)。OFF=API 0回は「alignmentタグ0件+alignment artifact 0」で示し、直接のstatus=DISABLEDは上記test(Production関数経由)で固定。
### 3-2. Family Z 正式runner(er026 `--mode mock`): **synthetic**(mock、費用0)、KP段まで、E2E自己確認=No
- コマンド: `env -u EIGO_KP_GLOSS_ALIGNMENT TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er026_family_z_fiction_production_runner_01.py --story melos --slug kga2_off --run run_kga2_off_01 --mode mock --stage all --stop-after kp --tts-execution-mode STANDARD`(出力は新規dir `melos/run_kga2_off_01_mock`として生成→`evidence_z/run_kga2_off_01_mock/`へ移動。既存Melos完成物dirは未編集)
- 結果: rc=0、stages=seed_check,writer,std_adjust,plan,support,kp、`spent_jpy: 0.0`、mock API呼出18件(kp 3件)。gloss alignment artifact/HR報告書/NOTICE/event ファイルなし(`find -iname "*gloss*"`/`*HUMAN_REVIEW*` 0件)。
- 限界: Zのmock runnerは`kp_fn`を内蔵ダミー(`mock_kp_fn`)に固定するためKP実処理(=gloss再整合呼出箇所)自体を通らない。そのためZは(a)mock runnerでstage_kpまで完走+alignment成果物0、(b)`offcheck_01.json`(Z `E2EContext`既定legacy・`_kp_fn_for_ctx`既定が素の`run_kp_with_outer_retry`・flag=False・`align_glosses`既定=DISABLED・API fn非呼出)、(c)共通到達点のtest、の三点で示す。Zの実LLM KP runは今回行っていない(KPの実処理はX実runで同一の共通到達点を通過済み)。
### 3-3. offcheck_01(`evidence_z/offcheck_01.py`/`.json`)
`GLOSS_ALIGNMENT_ENABLED=false`、`GLOSS_ALIGNMENT_MODE=legacy`、`preflight()=null`、X/Zともmode既定legacy、`align_glosses`既定status=DISABLED(fn呼出時AssertionErrorでも発火せず)。

## 4. Regression(`regression/`)
| suite | 結果 | 備考 |
|---|---|---|
| `er003_test_key_words_gloss_alignment.py` | 76 passed | |
| er003*_test_*.py | 1664件/1660 pass/3 fail+1 error | 既存failure集合と同一(`er003_test_bad`のfixture意図的fail、`er003_test_p2j_investigate`の算術3件+import STOPガード1件)。KGDC 委任_02 `regression/PREEXISTING_FAILURES_CHECK.md`の集合と一致 |
| er019*_test_*.py | 421/421 | 新規failure 0 |
| er026*_test_*.py | 並列run: 86件/78 pass/8 fail。順次run: 86/79/7 | 7件はKGDCの既存7件(cs_audit 4+post_slowdown 3)と同一。並列時のみ増える`test_shared_state_files_unchanged_by_mock_run`は並列起因(順次で通る=PREEXISTING記載どおり)。ログ: reg_er026.txt / reg_er026_sequential.txt |
| er030*_test*.py | 108/108(`_test_`形37件+`_test*`形で108) | reg_er030.txt / reg_er030_wide.txt |
| er063*_test_*.py | 59/59 | |
新規failure 0。

## 5. 費用
JPY1.83(Family X KP段 fresh run のみ。KPのみ上限JPY3以内)。Z mock=0、TTS実行なし。

## 6. 未解決/Fable判断事項
- `PRODUCTION_WIRED`宣言(evidence取得済み・判定待ち)。
- 旧`enabled`未指定の証跡script(`er071_completion_04_gloss_realign.py`/`_census_replay.py`)を再実行する場合は`EIGO_KP_GLOSS_ALIGNMENT=1`が必要になった(運用メモ)。
- corrected modeは`enabled=True`をscaffold内で明示する既存設計(上記注意)。flagと独立にcorrectedを動かせるのは、Python引数で`gloss_alignment_mode="corrected"`を明示した場合のみ。flag必須にする追加変更は本委任の範囲外のため行っていない(必要ならFable判断)。

## 6'. (委任_03追記)Family Z 正式runner 実LLM evidence: **fresh**(Production既定kp_fn、実LLM)、KP段のみ、E2E自己確認=No
- 使用モデル: Production既定のKP routing(`gpt-6-luna`、cost_log.jsonlのmodel_id)。評価Trialではない(Production line、モデル選定は別判断)。TTS実行なし(`--stage kp`で停止、`TTS_EXECUTION_MODE=STANDARD`)。
- 入力: Melos `run_e2e_02` を **コピー** した新規run `er026_output/family_z_production_e2e_01/melos/run_kga3_off_z_01`(wav・cost_log・stage_log・launch_log・sentinel logは除外してコピー。`run_e2e_01`/`run_e2e_02`は一切未編集。runnerはout_dir固定規約のためこの場所に生成され、証跡を `evidence_z_real/run_off_z_01/` へ複写)。
- 事前STOP確認: `tools/stop_scope_check_01.py --managed-id KP-GLOSS-ALIGNMENT-PRODUCTION-01 --run-dir <上記run>` -> rc=0(stop=false。2026-10-12 Melos STOP_NOTICEは旧書式で対象run限定のため非適用)。`STOP`/`STOP_ALL`なし。結果: `evidence_z_real/run_off_z_01/stop_scope_check_z_real.json`。
- コマンド(1回のみ起動、rc=0): `env -u EIGO_KP_GLOSS_ALIGNMENT TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er026_family_z_fiction_production_runner_01.py --story melos --slug melos --run run_kga3_off_z_01 --mode real --stage kp --regenerate-stage kp_a2 --approved-budget-jpy 6 --tts-execution-mode STANDARD`(PowerShell相当: `$env:TTS_EXECUTION_MODE="STANDARD"; Remove-Item Env:EIGO_KP_GLOSS_ALIGNMENT -ErrorAction SilentlyContinue; ...`)。`--approved-budget-jpy 6`はrunner内部のstage見積guard(kp/2=JPY5)を通すための値で、実費用Guardrailは委任のJPY3(実績JPY1.1191)。b1bはprovenance sha一致でcache再利用(API 0)、a2のみ`--regenerate-stage kp_a2`で実LLM再生成。
- 実kp_fn=Production既定と同一の根拠: real contextは`hooks`を設定しない(`build_real_context`)ため`_kp_fn_for_ctx`(runner:1164〜1175)は`ctx.hooks.get("kp_fn")`=None、`gloss_alignment_mode`既定legacy -> `w62.run_kp_with_outer_retry`(素のProduction既定)を返す。`stage_kp`(runner:1222〜)がそれを`w62.run_kp_stage(..., kp_fn=_kp_fn_for_ctx(ctx))`で実行。
- 結果: rc=0、`spent_jpy=1.1191`(stdout: `runner_z_stdout.log`)。`cost_log.jsonl` 3件は全て stage=`kp`(selection/canonicalization/redundancy QA、gpt-6-luna)で、`kp_gloss_alignment`タグ **0件**(run dir全体を`grep -rl kp_gloss_alignment`でも0件)。`a2_result.json`に`gloss_alignment_status: "DISABLED"`、`gloss_alignment_cost_jpy: null`、`gloss_alignment_fallback: null` -> 再整合関数は呼ばれたがflag OFFでno-op(Zの正式経路が`align_glosses`呼出箇所を通過したことの直接証拠)。gloss/HUMAN_REVIEW/NOTICE名のartifact **0件**。
- provenance区分: runner summaryは`gloss_alignment_mode`を記録しない(既存仕様、追加せず)。legacy既定は`E2EContext.gloss_alignment_mode="legacy"`(コード既定)とstatus=DISABLEDで示す。flag状態はenv未設定(`env -u`)+DISABLED結果による。
- 限界: a2のみ実LLM(b1bはcache)。TTS以降は未実行(E2E自己確認=No)。

## 7'. (委任_03追記)flag一元化(唯一のkill switch)
- 変更: `er003_key_words_gloss_alignment.py`に`flag_enabled()`を新設(`GLOSS_ALIGNMENT_ENABLED`を返す)。`er003_v1_n3_01_scaffold_generate.py:734`のcorrected分岐の`enabled=True`直書きを`enabled=gloss_align.flag_enabled()`へ置換。これで`gloss_alignment_mode="corrected"`でも`EIGO_KP_GLOSS_ALIGNMENT=1`が無ければ`status=DISABLED`・API 0・artifact不変。legacy挙動・再整合ロジックは無変更。
- Trial側: `er071_gloss_alignment_correction_01_trial.py`/`_t3_mock.py`の先頭(import前)で`os.environ["EIGO_KP_GLOSS_ALIGNMENT"]="1"`を明示設定し「Trial: gloss alignment explicitly ON」を出力(setdefaultではない)。
- test: `DefaultOffIsolation`に2件追加(`test_corrected_mode_without_flag_is_disabled_no_call`=mode=corrected+flag OFF -> DISABLED・fake fn 0 call・make_alignment_fn 0 call・GLOSS/HUMAN_REVIEW file 0、`test_corrected_mode_with_flag_runs`=flag ON -> 実行)。`pytest er003_test_key_words_gloss_alignment.py` 78 passed。
- T3 mock再実行(JPY0、`gloss_alignment_correction_01/trial_t3_rerun_01/`): 27/27 PASS。
- Regression(`regression/reg3_*.txt`): er003* 1667件/1663 pass/3 fail+1 error(既存集合と同一: `er003_test_bad`fixture意図fail+`er003_test_p2j_investigate`4件)、er026* 86件/79 pass/7 fail(既存7件=cs_audit 4+post_slowdown 3と同一)、er019* 421/421。新規failure 0。
- 費用: Z KP a2 JPY1.1191のみ(上限3内)。TTS 0。

## 8. Fable判定(2026-10-15): PRODUCTION_WIRED(委任_04記録)
既定OFF安全措置のみ。gloss再整合工程自体は未採用(APPROVED_FOR_PRODUCTIONを付けない)。既定OFFは品質改善完了ではない。

| 受入条件 | 充足evidence |
|---|---|
| ① 明示ONなしで実行されない | unit test 78 PASS+flag一元化(委任_03、mode=correctedもflag必須) |
| ② OFF時API 0・gloss不変・HR成果物0 | test+X/Z実LLM evidence |
| ③ Std/Adv・X/Z・runner約65本・起動スクリプトの隔離 | 静的確認表+X(er019 KP段 実LLM、`kp_gloss_alignment`タグ0)+Z(er026 real KP段、a2_result.json `gloss_alignment_status="DISABLED"`、タグ0) |
| ④ 明示ONのDEV/Trialで動作 | test+Trial script明示ON+T3 27/27 |
| ⑤ test・runtime evidence | 上記(委任_02 c21cce27a・委任_03 e80360add) |
| ⑥ SSOT/Git | 反映済み |

- 残置物: `er026_output/family_z_production_e2e_01/melos/run_kga3_off_z_01`(git管理外、Z evidence用コピー、削除せず残置)。
- 未記録事項: runner summaryに`gloss_alignment_mode`欄なし(既存仕様、追加せず)。
