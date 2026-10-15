# 委任文(全文保存・T-0): KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_02(2026-10-15、Fable→Sonnet)

(受領した委任文を逐語保存。Opus条件Cレビュー原文は末尾に別ファイル`er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/OPUS_REVIEW_C_01_VERBATIM.md`の全文を連結している。)

## 管理ID

`KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01`(KGCPW)委任_02(実装・test・harness・Regression。有料evidenceとSSOT本文更新は委任_03)。並行タスク: `PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01` Day3 委任_Eが同時進行中(編集対象は`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/`と`docs/pm/delegation_log/`のみ)。本委任はそれらに触れない。git `index.lock`衝突時は30秒待ち最大3回再試行。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式採用済み(`APPROVED_FOR_PRODUCTION`、2026-10-15)の修正版(corrected)gloss再整合工程の**Production配線実装**。設計正本=`er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/PRODUCTION_WIRING_DESIGN_01.md`(以下「設計」)+本委任の「Opus条件Cレビュー所見のFable採否表」(設計より優先)。
- 到達上限Status: 実装・unit/integration/golden test PASS・Regression新規failure 0・harness準備完了(`WIRED_PENDING_EVIDENCE`)。**`PRODUCTION_WIRED`は宣言しない**(runtime evidence=委任_03、最終判定=Fable)。
- Opus独立技術レビューGate: 条件C実施済み(本委任に原文と採否を添付。BLOCKER 0/MAJOR 6)。是正後の差分再レビューはFableが判断。
- **費用上限: JPY0(本委任は有料API 0)**。Regressionとtestは`OPENAI_API_KEY`を空にした環境で実行し、`raw_usage_log`等への新規書込0件を確認(Opus提案)。TTS実行なし。
- 禁止: git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f。承認範囲(ユーザー§1〜§3、設計§0)を超える仕様変更(特に: OPEN-359本体(b)(c)の消費側一般化、Adv解説phraseの`key_phrase`化[Opus M6]、A/B/C共有Gateへの関所追加)は**実装しない**(Fableがユーザーへ諮る)。Prompt本文(`build_user_message_corrected`・`DEVELOPER_MESSAGE`)・承認規則テンプレート・schema内容・retry回数は**無変更**(golden testで固定)。`human_review_queue.jsonl`/Human Review Lockは使わない。新Validator/Hook/管理機構の増設禁止(既存関数の拡張のみ)。
- 時間見込み: 約4h(golden先行0.3h/W1 ga+sc 1.0h/W2 er019+er026 1.0h/W3 test 1.0h/W4 harness 0.4h/Regression 0.3h)。並列化: W1とW2は別ファイルだが**同一Sonnet直列**(依存: sc→er019/er026の引数除去順)。Regressionは他suiteと同時に走らせない(共有state干渉、VALIDATION_03 §3-2)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。保存先: `docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01_02.md`(**全文保存**、Opus原文ブロックを含む)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし。harnessもTTSを呼ばない)
T-3: 費用上限JPY0(有料API 0)のためGuardrail文は委任_03で記載。

## ユーザー指示(原文)

委任_01に全文保存済み(`docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01_01.md`「ユーザー指示(原文)」節)。本委任で直接効く要点の逐語: 「修正版correctedを正式経路へ配線する。Production既定ONへ切り替える。旧legacy方式を撤去し、correctedと誤って共存しないようにする。Standard／Advanced、Family X／Zの対象経路へ適用する。DEV／Trial専用scriptだけに存在する状態を解消する。」「retry、fallback、regeneration、cache再利用、Human Review後の再開も含めて整合を確認する。失敗時に古いglossへfail-openしない。再整合が必要なKPだけを正しく対象にする。対象外KPのglossは変更しない。」「2回失敗時に非OK statusを返す。既存Audio Validation Gateで完成を禁止する。Family Zは既存FamilyZE2EStopを使用する。Advanced B1英語解説とページ表示への流出も防ぐ。HR報告書、run summary、stdout、STOP statusで例外を追跡できるようにする。」「OPEN-359など別件の不具合については、影響が今回の受入条件に及ぶ範囲で対応する。独断で大幅な仕様変更へ発展させない。」「技術的に自律解決可能な問題は、承認済み範囲・予算内で原因調査、修正、再検証する。」

## KPI provenance欄

本委任のtest/Regressionはすべて`synthetic`(mock/fake client)+`fresh`。実LLM evidenceは委任_03。E2E自己確認=No(本委任)。

## Opus台帳更新

本委任で`docs/pm/OPUS_FINDINGS_LEDGER.md`に**新規行を追加**する(編集権あり、追記のみ): 条件Cレビュー所見を`OF-KGCPW-01〜`として、台帳の既存10列形式(委任KGDC_02で揃えた列)で、**Opus原文の逐語要約(改変禁止)**+Fable採否(下表)+状態(`FABLE_DECIDED`→本委任で実装したものは`IMPLEMENTED`)を記録。既存OF-225〜235/OF-KGDC-01〜12の行は**変更しない**(遷移は委任_03でevidence後)。原文は`er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/OPUS_REVIEW_C_01_VERBATIM.md`へ**本委任文末尾のブロックをそのまま**保存(11-5)。

## Opus条件Cレビュー所見のFable採否表(設計より優先。「採用」は本委任で実装)

| ID | 所見(要旨) | Fable採否 | 実装内容 |
|---|---|---|---|
| OF-KGCPW-01 (論点1) | golden testは撤去前HEADで先に作る/対象=`responses.create`全kwargs/shaは`sort_keys`なし | **採用** | **最初に**(コード変更前、HEAD `64d3ec975`状態で)fake clientを`make_alignment_fn(..., client=fake)`に渡し、Std/Advの代表入力(P1型1件+P2型1件を同一callに含む固定item集合、`mode="corrected"`明示+`EIGO_KP_GLOSS_ALIGNMENT=1`)で捕捉したkwargs(model・reasoning・text.format全体・input)を`json.dumps(ensure_ascii=False)`(sort_keysなし)→sha256を`.../gloss_alignment_production_wiring_01/golden/alignment_request_golden_01.json`(kwargs本文+sha)へ保存。撤去後に同じ入力で同じshaを要求するtest `test_alignment_request_bytes_match_golden`を追加 |
| OF-KGCPW-02 (論点1) | corrected本体がartifact/戻り値に`"mode": corrected`を書く(ga:836/846/866/886)、`GLOSS_ALIGNMENT_VERSION`がlegacyと同値 | **採用** | `mode`フィールド削除。`GLOSS_ALIGNMENT_VERSION = "ER-003-KP-GLOSS-ALIGN-02"`へ更新(旧版artifactと区別)。§2-4 Grepに`GLOSS_ALIGNMENT_MODE_CORRECTED`/`"mode": `を追加 |
| OF-KGCPW-03 (論点4 M4) | X: HR報告がメモリ上の`final_merged`から作られ、途中attemptでHR→次attemptで失敗(`final_merged=None`)だと報告書・event・stdoutが出ない。`--stage all`ではRuntimeErrorが最終行より先 | **採用** | `run_key_phrases`(sc:821-835)をZ(`_gloss_hr_gate`、er026:1205)と同じく**ディスク上の`keywords_canonicalized.json`を読んで**HR判定・報告する形へ(`final_merged`が無ければartifactを読む。artifactも無ければ報告なしでよい)。er019 `main`の最終行出力を`try/finally`化 |
| OF-KGCPW-04 (論点4) | `kp.get("status")`だけだとNG_REVIEW_REQUIREDとHR重複時にgloss停止が隠れる。X main末尾でHR残ならrc=2(任意) | **採用(両方)** | X summary level別に`kp_run_status`(top-level status)と**別キー`gloss_alignment_run_status`**(`collect_unresolved`非空なら`STOPPED_GLOSS_ALIGNMENT_FAILED`)を記録。main末尾でいずれかのlevelにHR未解決があればrc=2(Zと一致)。既存testへの影響をGrepで確認し更新 |
| OF-KGCPW-05 (論点4) | `print_gloss_hr_final_line`が報告書ファイルの有無で判定→resolve後も誤報 | **採用** | 判定をartifactの`collect_unresolved`へ変更(報告書は履歴として残す) |
| OF-KGCPW-06 (論点5 M1) | X解説cache: 旧bundle再利用はfail-open。`gloss_alignment_status`付きitemが1件でもあれば`gloss_signature`一致必須(欠落も不一致)、署名に`key_phrase`も含める | **採用**(Sonnet案を置換) | er019:912-934を修正。status無しartifact(pre-ON/対象0件)は従来署名で互換 |
| OF-KGCPW-07 (論点5) | Z `kp_expl_b1b`署名はSonnet案(status持ちitemがあればgloss含有)が妥当 | **採用** | er026:1259-1262 |
| OF-KGCPW-08 (論点5 M2) | ON化前成果物の決定論的「未評価検出」: 消費・再利用時に`select_alignment_targets(items)`を評価し、対象なのに`gloss_alignment_status`が無ければSTOP(`--regenerate-stage kp_*`要求)。X TTS関所・Z stage_kp再利用後に適用 | **採用** | 新関数は`ga.collect_unevaluated(kp_items)`(既存`collect_unresolved`の隣、LLM 0)として追加し、X `_gloss_alignment_hr_unresolved`とZ `_gloss_hr_gate`/`load_level_inputs`から呼ぶ。停止理由文言に「ON化前・未評価。`--regenerate-stage kp_<lv>`(Z)/KP成果物削除後再生成(X)」を含める。対象0件は通過 |
| OF-KGCPW-09 (論点5 M3) | Z: `--regenerate-stage kp_*`→HR→resolve→同指定で再実行するとsnapshot復元がスキップ(er026:1234)/`_gloss_hr_gate`のraise前に`install_kp_assets`/`mark_stale_descendants`が走らず旧assetが残る | **採用** | 未消費snapshotがあればregenerate指定時でも優先復元。raise前に`install_kp_assets`+`mark_stale_descendants`を呼ぶ(er062:515-520の順序を確認) |
| OF-KGCPW-10 (論点8) | 約65 scriptの既定ON波及は許容。呼出元opt-inは不採用。「完成禁止の保証はX/Zのみ」をSSOTに明記。共有Gateへの関所追加は任意 | **採用(明記のみ)**。共有Gate関所は**実装しない**(A/B/C read-only方針との整合はFable→ユーザー) | 委任_03のCURRENT_SPEC文案に含める(本委任ではRESULT_PACKETに文案) |
| OF-KGCPW-11 (論点9) | kill switchはimport時評価のまま。両runnerがrun開始時に実効値(ON/OFF)と取得元をstdout+summaryへ記録。運用は「プロセス環境変数のみ」 | **採用** | `ga.flag_effective()`→`{"enabled": bool, "raw": str|None, "source": "env"|"default"}`を追加しX/Z開始時に1行print+summary記録。OFF時は設計§3の`[GLOSS-ALIGN][WARN] DISABLED ...`警告 |
| OF-KGCPW-12 (論点10 M5) | 失敗注入は案B'(harnessが`make_alignment_fn`をwrapし本物をfake `client=`で呼ぶ)。E7はE4の合成対象artifactを連結しないとNO_TARGETSで証拠にならない。「fresh初回path」とは主張しない | **採用** | harnessはB'方式。E4→E7連結は委任_03の実行計画に反映(本委任ではharnessに「合成対象artifactを生成→同run dirで続行」モードを用意) |
| OF-KGCPW-13 (論点11) | 旧Trial script 6本は冒頭`raise SystemExit("HISTORICAL ...")`(注記だけだと有料APIを叩いてから落ちる) | **採用** | 6本の冒頭(import直後・副作用前)に`raise SystemExit(...)`+理由コメント。T3 mock 27シナリオは`er003_test_key_words_gloss_alignment.py`(または新規`er003_test_kp_gloss_alignment_stop_paths.py`、どちらかをSonnetが決め理由を記録)へ移植 |
| OF-KGCPW-14 (論点12) | `HR_RESOLVE_PROCEDURE_01.md`のファイル名参照(ga:946/992、er019:532/1563)/docstring「legacy artifactは常に[]」(ga:901、er019:519/1554)/legacyの`"FAILED"`を`collect_unresolved`と`resolve_gloss`が認識しない | **採用** | 手順書を`docs/pm/runbooks/KP_GLOSS_ALIGNMENT_HR_RESOLVE_01.md`へ**コピー**(原本は履歴として残す)し現行化(「Trial専用」「legacyでは発生しない」を削除、既定ON・flag・rc・未評価検出を追記)、コード内参照を新pathへ。docstring更新。`"FAILED"`を未解決として扱う(`collect_unresolved`)+`resolve_gloss`の受理状態に追加 |
| OF-KGCPW-15 (論点3) | 条件差は小。E4でStd/Adv各1回+整合済み対照itemを同一callに混ぜる | **採用** | 委任_03の実行計画へ(本委任ではharness入力の固定item集合に反映) |
| OF-KGCPW-16 (論点6) | 監視指標(対象率15%超/attempt≥2/HR即時/align費用0.6円超/DISABLED run/所要60秒超 等) | **採用(記録)** | 本委任ではX/Z summaryに`gloss_alignment_metrics`(level別: targets/items, attempts_max, status, cost_jpy, elapsed_sec)を記録するだけ(アラート機構は作らない。閾値はSSOT文案に記載、委任_03) |
| OF-KGCPW-17 (論点7) | OPEN-359(b)(c)は別承認が妥当。「放棄attemptのartifactがTTSへ進む」はOPEN-359本体 | **採用(別承認)** | 実装しない。integration test「NG_REVIEW_REQUIRED+HR itemでX TTS/assembleが止まり、`gloss_alignment_run_status`が出る」のみ追加 |
| OF-KGCPW-18 (追加 M6) | Adv解説LLMのphraseがdisplay_phrase(候補)でglossと食い違う(既存構造、再整合対象に集中) | **不採用(本委任)→ユーザー判断へ** | 実装しない。RESULT_PACKETに事実(ファイル:行)を転記 |
| OF-KGCPW-19 (追加 MINOR) | 再生成後TTSを飛ばしてassembleすると旧音声で通過/`--level both`でa2 HRがb1b assembleを巻き添え | **後者のみ採用** | assembleのlevel loopで例外をlevel単位に捕捉し、健全levelは続行、HR levelはBLOCKED記録(既存の`EPISODE_BLOCKED_BY_*`形式)。前者はOPEN候補としてRESULT_PACKETに記載(実装しない) |

## 事前指定Read一覧

1. 設計 全文(§1〜§13、約270行)
2. `er003_key_words_gloss_alignment.py`: 36-60、160-230、410-535、590-680、760-900、1010-1120(Grepで再特定可)
3. `er003_v1_n3_01_scaffold_generate.py`: 683-746、805-950
4. `er019_family_x_audio_production_runner_01.py`: 334-430、510-540、595-625、870-975、1270-1320、1545-1590、1785-1795、2000-2012、2340-2365、2450-2526
5. `er026_family_z_fiction_production_runner_01.py`: 60-70、925-935、1160-1300
6. `er062_family_z_writer_01.py`: 470-525、925-1040
7. `er003_test_key_words_gloss_alignment.py`: Grep `^class |def test_` → 構成、`DefaultOffIsolation`/`ModeSeparation`/`ScaffoldCorrected`節全文
8. `er071_gloss_alignment_correction_01_t3_mock.py`: Grep `def scenario|SCENARIOS|def run_` → 27シナリオの一覧と各シナリオの検証点(移植元)
9. `er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/HR_RESOLVE_PROCEDURE_01.md` 全文(runbook化の原本)
10. `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `OF-KGDC-01` → 行形式(列順)の確認
11. `er006_model_routing_contract_01.py`:45-95(A2/B1 SUPPORTのmodel)

## 事前指定Grep一覧+追記位置・更新位置の手順

- 撤去残置(設計§2-4の4本+`GLOSS_ALIGNMENT_MODE_CORRECTED|"mode": `)を実装後に実行し全0件をRESULT_PACKETへ(コマンドと結果行数)。
- 既存testで`key_phrases_status`/summary形/rc/`gloss_alignment_mode`に依存するもの: `rg -n "gloss_alignment_mode|key_phrases_status|scaffold_run_summary|returncode|rc ==" --glob "er019*_test*.py" --glob "er026*_test*.py" --glob "er003*_test*.py" --glob "er062*_test*.py" --glob "er063*_test*.py"` → 更新対象。
- `HR_RESOLVE_PROCEDURE_01` 参照: `rg -n "HR_RESOLVE_PROCEDURE_01" --glob "*.py" --glob "*.md" --glob "!er071_output/**"` → 新pathへ更新(er071_output配下の過去文書は変更しない)。
- 旧Trial script 6本: `rg -l "gloss_alignment_mode|resolve_mode|GLOSS_ALIGNMENT_MODE" er071_*.py` → T3 mock以外にSystemExit。
- 実効flag/summary: 追記位置はX `run_theme_scaffold`直前のmain(er019)とZ `main`のrun開始ログ付近(er026、既存のrun_launch_log書込みの近く)。
- `.gitignore`: `git check-ignore -v docs/pm/runbooks/KP_GLOSS_ALIGNMENT_HR_RESOLVE_01.md`で追跡可能か確認(ignoreなら`docs/pm/`直下の既存追跡ディレクトリに置く。強制addはしない)。

## 実行コマンド全文

(すべて`.venv\Scripts\python.exe`。有料API 0を担保するため、test/Regressionは**PowerShellで`$env:OPENAI_API_KEY=""`を設定した同一セッション**で実行し、実行前後で`git status --porcelain -- "**/raw_usage_log.jsonl" er005_output er030_output er006_output er011_output er021_output er025_output`の差分が増えないことを確認)
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01_02.md --json-out docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01_02_check.json`
- STOP確認: `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 --run-dir er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01 --out er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/stop_scope_check_kgcpw2.json`
- golden作成(コード変更前): `.venv\Scripts\python.exe er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/golden/make_alignment_request_golden_01.py --out er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/golden/alignment_request_golden_01.json`(新規script。`EIGO_KP_GLOSS_ALIGNMENT=1`を内部で設定、fake clientで`responses.create`のkwargsを捕捉、API 0)
- unit: `.venv\Scripts\python.exe -m pytest er003_test_key_words_gloss_alignment.py -q`(+新規testファイルがあればそれも)
- Regression(直列・単独): `.venv\Scripts\python.exe run_project_regression.py --pattern "er003*_test_*.py"` → `--pattern "er019*_test_*.py"` → `--pattern "er026*_test_*.py"` → `--pattern "er062*_test_*.py"` → `--pattern "er063*_test_*.py"` → `--pattern "er030*_test_*.py"` → `.venv\Scripts\python.exe -m pytest er008_audio_validation_gate_05_test.py -q`(run_project_regression.pyの実際の引数は`--help`で確認して合わせ、実コマンドを報告。既存failure集合=er003 4件/er026 7件[VALIDATION_03 §3-2]との差分で評価)
- harness自己検証(API 0): `.venv\Scripts\python.exe er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/evidence/harness_kgcpw_01.py --self-test`(fake clientで2回失敗→HRまで通ることを確認。X/Zの正式runner関数をin-processで駆動。TTS段は呼ばない)
- 残置Grep: 設計§2-4の4コマンド+`rg -n "GLOSS_ALIGNMENT_MODE_CORRECTED|\"mode\": " er003_key_words_gloss_alignment.py er003_v1_n3_01_scaffold_generate.py er019_family_x_audio_production_runner_01.py er026_family_z_fiction_production_runner_01.py`
- git: `git status --porcelain`(作業前後、add対象のみ確認)、`git log --oneline -3`

## 実装の必須事項(設計§2〜§5+採否表。順序厳守)

0. **golden先行**(OF-01)。golden JSONをcommitに含める。
1. ga: legacy撤去(設計§2-1)、corrected唯一schema(内容・`name`不変)、`align_glosses`=corrected本体、`GLOSS_ALIGNMENT_ENABLED`既定ON+判定反転(`0/false/off/no`でOFF)、`flag_effective()`、`collect_unevaluated()`、`"FAILED"`認識、`mode`フィールド削除、VERSION `-02`、runbook参照更新、docstring更新。「legacy」語0件。
2. sc: `gloss_alignment_mode`引数と分岐の全撤去、`run_key_phrases`のHR判定をディスクartifact基準に(OF-03)。
3. er019: 無条件化、summary `kp_run_status`/`gloss_alignment_run_status`/`gloss_alignment_flag`/`gloss_alignment_metrics`、rc=2、最終行try/finally+`collect_unresolved`基準、解説cache署名(status持ちなら`gloss_signature`必須、`key_phrase`含む)、未評価検出、assembleのlevel単位捕捉。
4. er026: 無条件化、`stage_kp`冒頭`ga.preflight()`、署名(status持ちならgloss含有)、未評価検出、snapshot優先復元、raise前`install_kp_assets`+`mark_stale_descendants`、実効flag記録、metrics。
5. test: 旧test整理(削除/書換の実数を報告)、Opus提案のtest一覧(本委任文「Opus原文」§5)を**全件**実装(E4/E7連結・実効flag・実LLM系を除く)、`DefaultOffIsolation`は「既定ON」反転+「明示OFF時のno-op」に書換、`mapping_gate`固定、`gloss_alignment_mode`引数が存在しないことの固定、T3 27シナリオ移植。
6. harness(B'方式)+旧Trial script 6本のSystemExit。
7. Regression直列。既存failure集合と比較。
8. 残置Grep全0件。

## SSOT追記文

本委任ではCURRENT_SPEC/DECISION_LOG/OPEN_ITEMS本文を編集しない(委任_03)。ただし`docs/pm/OPUS_FINDINGS_LEDGER.md`へOF-KGCPW-01〜19を追記(上表+原文要約)。`docs/pm/ACTIVE_TASK.md`固定ヘッダ: 管理ID=KGCPW 委任_02/Status=配線実装中→完了時`WIRED_PENDING_EVIDENCE`/UDR-blocking=なし/UDR-deferred=Day3設計承認済み(実装中)、OPEN-359本体(b)(c)、Adv解説phrase(OF-KGCPW-18)、A/B/C共有Gate関所/APPROVED未配線=gloss corrected(配線中)、OPEN-151ほか/量産run凍結=evidence完了まで/STOP条件(固定)=前回同じ/次アクション=委任_03 evidence/未回答報告=Day3進捗、KGCPW進捗/報告単位Status=委任_02。`docs/pm/REPORT_LEDGER.md`末尾1行。CURRENT_SPEC向け文案(「完成禁止の保証はX/Zのみ」「kill switchはプロセス環境変数のみ」「監視指標と閾値」「VERSION -02」)はRESULT_PACKETに記載。

## Git(明示add対象・コミットメッセージ・trailer)

SSOT編集権: `docs/pm/OPUS_FINDINGS_LEDGER.md`・`docs/pm/REPORT_LEDGER.md`=**あり**(追記のみ)。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`=**なし**(文案のみ)。
明示add: 変更した`er003_key_words_gloss_alignment.py`、`er003_v1_n3_01_scaffold_generate.py`、`er019_family_x_audio_production_runner_01.py`、`er026_family_z_fiction_production_runner_01.py`、(必要なら)`er062_family_z_writer_01.py`、`er003_test_key_words_gloss_alignment.py`(+新規test)、更新した既存test、旧Trial script 6本、`docs/pm/runbooks/KP_GLOSS_ALIGNMENT_HR_RESOLVE_01.md`、`er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/{golden/*,evidence/harness_kgcpw_01.py,OPUS_REVIEW_C_01_VERBATIM.md,IMPLEMENTATION_02.md,stop_scope_check_kgcpw2.json,regression_02/*.log}`、`docs/pm/OPUS_FINDINGS_LEDGER.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/delegation_log/..._02.md`(+`_check.json`)。**Regression中に更新される共有state(er005/er006/er011/er021/er025/er030配下・`**/raw_usage_log.jsonl`)はaddしない。** Day3成果物(`docs/research/**`)に触れない。
コミットは2回: (1)golden先行commit「KGCPW 委任_02a: 撤去前HEADでcorrected API request golden(sha)を固定」、(2)本体「KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_02: corrected唯一化・legacy撤去・既定ON(kill switch=プロセス環境変数)・X/Z無条件配線・Opus条件C所見OF-KGCPW-01〜17是正(ディスク基準HR報告/rc=2/解説cache署名/未評価検出/Z snapshot優先/FAILED認識/runbook)・T3 27シナリオ移植・harness B'・Regression新規failure 0。evidence/SSOT本文は委任_03、JPY0」。push to origin/main。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_KGCPW2.md`へ: (1)T-0/STOP確認 (2)golden: 撤去前sha・撤去後test結果(同一sha) (3)撤去実績(関数/分岐/定数/引数/test削除・書換の実数、「legacy」0件、残置Grep5本の結果) (4)採否表OF-KGCPW-01〜19の各実装状況(実装済み/未実装理由、ファイル:行) (5)test件数(before/after、新規一覧)、unit結果、Regression各suiteの結果と既存failure集合との差分、API 0の証拠(共有state差分なし) (6)harness自己検証結果(X/Z 2回失敗→HR→関所停止、TTS 0) (7)rc=2化・assemble level単位捕捉の既存testへの影響 (8)CURRENT_SPEC/OPEN_ITEMS/DECISION_LOG文案 (9)commit hash×2・push結果・raw URL(主要変更ファイル) (10)確認できなかった事項(推定/事実) (11)委任文からの逸脱 (12)委任_03(evidence)への申し送り: E1〜E10の実行コマンド確定版(harnessのオプション含む)、E7費用見積に必要なclip数の数え方。

Fableは(2)(3)(4)(6)を自分で照合する(受領≠受入)。行番号・観測値を省略しないこと。

## Opus条件Cレビュー原文(逐語。`OPUS_REVIEW_C_01_VERBATIM.md`へそのまま保存すること)

(下記は`OPUS_REVIEW_C_01_VERBATIM.md`の全文と同一。)

## KGCPW Opus条件C独立レビュー(実装前の安全性確認。採用可否は判断しません)

## 1. 総括
- **BLOCKER 0件 / MAJOR 6件**(M1〜M6)、MINORは複数。
- 判定は**「是正後に進めてよい」**です。設計の骨格(mode廃止とcorrected唯一化、既定ON、kill switch残置、artifact直読みの関所)は妥当です。
- 新規記事を初回から作る経路で、不整合glossが完成物へ流れる反例は見つかりませんでした。OPEN-359の論証(gloss HRの関所は迂回されない)も、第一義(不整合glossが完成物へ流れない)では成立します。
- 一方、**再利用経路(cache・コピーしたrun・`--regenerate-stage`・ON化前の成果物)**と**HR通知の網羅性**に穴があります。どれも数行で直せるので、委任_02の実装セルに含めることを推奨します。
- 以下「安全側(1)」=不整合glossが完成物へ流れない、「安全側(2)」=承認済み仕様が動く、の意味で使います。

## 2. 論点別

**論点1 legacy撤去・golden test・mode廃止・接尾辞: MINOR**
- mode廃止に反対理由はありません。`_corrected`接尾辞を残す判断も妥当です。
- 撤去順序の罠が1つあります。legacy schemaがcorrected schemaのdeepcopy元です(ga:631-641)。現在のproperty順は`rank, current_gloss_consistent, japanese_gloss, qa_reflects…, reasoning, added_word_mappings`(末尾に追加)です。strict schemaでは出力の生成順がこの順に従うため、順序は挙動に効きます。
- golden testの作り方を3点指定すべきです。
  - (a)**撤去前のHEADで先に作る**(mode="corrected"で記録し、撤去後に同じshaを要求する)。
  - (b)対象はmessage文字列だけでなく、fake clientで捕捉した`responses.create`の全kwargs(model・reasoning.effort・`text.format`全体・input)。
  - (c)shaは`json.dumps`を**sort_keysなし**で取る(順序の変化を検出するため)。
- 見落としが1点あります。corrected本体はartifactと戻り値に`"mode": GLOSS_ALIGNMENT_MODE_CORRECTED`を書いています(ga:836/846/866/886)。§2で定数を削除し、§2-4のgrep(`"corrected"`が0件)を満たすには、このフィールドを消すか置き換える必要がありますが、設計に記載がありません。
- さらに`GLOSS_ALIGNMENT_VERSION`はlegacyとcorrectedで同じ値(`ER-003-KP-GLOSS-ALIGN-01`)です。実在するCoffee artifactにはlegacyで再整合した痕跡があります(er019_output/.../coffee_prices__run_m2p0_n01_01/a2/key_phrases/keywords_canonicalized.json:145-146)。
- 代替案: modeフィールドを削除し、**versionを`-02`へ上げる**。旧版の成果物と区別できるようにするためです。

**論点2 撤去範囲: OK(撤去しすぎは無し)**
- correctedが依存しているもの(`_norm_tilde_space`、`_extra_tokens`、`kp_adds_words_beyond_display`、`DEVELOPER_MESSAGE`、`STATUS_*`)は残す側に入っています。
- `gloss_alignment_fallback*`、`gloss_review_hint`を読む外部コードはありません(canonicalizationは自分で書くのみ)。
- 撤去漏れは上記のmodeフィールドと`make_alignment_fn`の既定schema(ga:212、設計に記載済み)だけです。
- grepの追加を推奨: `GLOSS_ALIGNMENT_MODE_CORRECTED`、`"mode": `。

**論点3 正しいglossの不要な書換え: OK(条件差は小さい)**
- モデルはTrialと同一です。A2_SUPPORTもB1_SUPPORTも`gpt-6-luna`(er006_model_routing_contract_01.py:50,89-90)、effortは既定のhigh(ga:199)。
- 対象選定は決定論的なので同一。retry上限も同じ2回です。
- 差は2点です。(i)Productionは1記事の全対象を1 callにまとめる(Trialはパターン別に投入)。(ii)入力本文がlevelごと(Std/Adv)の記事本文。
- どちらも書換え率への影響は小さいと推定しますが、E4で「Std/Adv各1回+整合済みの対照item」を同じcallに混ぜて確認すれば足ります。

**論点4 完成禁止・X rc=0・迂回路: MAJOR(M4、安全側(2))+MINOR**
- 第一義(安全側(1))は満たします。TTS B1(er019:967)、A2(1282)、assemble(1582/1790。Gateの早期return[assemble:472-473]より前)、ページ(2009)は、すべてartifactを直接読みます。
- `--only-segments`、`--stage`の個別起動、`--stage all`、`kp=None`の各経路でも迂回はありません。B1解説LLMはHR判定の後でしか呼ばれません(er019:967→972)。
- **M4(通知の欠落)**: `run_key_phrases`はHR報告を「最終attemptのメモリ上のmerged」から作ります(sc:824-831)。
  - 途中のattemptでHRが出た後に、次のattemptでselection失敗・canonicalization非PASS・cost cap超過になると、`final_merged=None`になり報告が出ません。
  - ところがディスク上には前のattemptのartifact(HR itemを含む)が残ります(sc:713-714は非PASS時に書かない)。消費側はこれを読んで止まるため安全側(1)はOKですが、**HR報告書・event・最終stdoutが一つも出ない**停止になります。停止理由には存在しない報告書名が表示されます。
  - さらに`--stage all`/`assemble`では`_assert_no_gloss_alignment_hr`のRuntimeError(er019:1560)が`print_gloss_hr_final_line`(2520)より先に発生するため、最終stdoutの1行が出ません。
  - 是正(≈5行): (a)Zと同じく**ディスク上のartifactを読んで**HR判定・報告する(Zはer026:1205で実施済み)。(b)最終行の出力を`try/finally`化する。
- X rc=0について: `kp_run_status`をsummaryに記録し、最終stdoutが必ず出るなら「STOP status」要件は満たすと言えます。ただし`kp.get("status")`だけでは、NG_REVIEW_REQUIREDとHRが重なった場合にgloss停止が隠れます(sc:833は既存status優先)。
  - 推奨: `gloss_alignment_run_status`を別キーにする。
  - 任意: main末尾でHRが残っていればrc=2(Zと一致、≈3行)。
- 誤報(MINOR): `resolve_gloss`はHR報告書を消しません(ga:1068-1118)。このため`print_gloss_hr_final_line`(er019:2355、報告書ファイルの有無で判定)が**解消後も「停止中」を出し続けます**。判定をartifactの`collect_unresolved`に変えるべきです。

**論点5 後続工程とcache: MAJOR×3(M1〜M3)**
- **(a) X解説cache = M1(安全側(1))**: Sonnet案の「`gloss_signature`の無い旧bundleは再利用」はfail-openです。
  - 完成済みrunをコピーしてKPを再生成し(E7がまさにこの手順)、display_phraseの並びが同じなら、旧gloss入力で作った解説が再利用されます。
  - なおHR→resolveの経路では旧bundleがNoneで上書きされる(er019:876-896)ため、穴は「コピー+再生成」経路に限られます。
  - 代替案(Zと同じ規則): artifactに`gloss_alignment_status`を持つitemが1件でもあれば`gloss_signature`の一致を必須にする(欠落も不一致扱い)。無ければ従来の署名。
  - 併せて署名に**`key_phrase`も入れる**べきです。既存の穴として、表示候補が同じでcanonicalizationの結果だけ変わるケースを検出できません(er019:921)。
- **(b) Z `kp_expl_b1b`署名: Sonnet案(statusを持つitemがあればgloss含有)が妥当**です。代替案(署名は従来のまま、明示的な再生成に任せる)は危険です。`--regenerate-stage kp_b1b`→HR→resolve→再実行の経路で、display列が同じなら旧gloss入力の解説が再利用されます。既存Melos runは状態フィールドが無いので互換は保たれます。
- **(c) ON化前の成果物 = M2(安全側(1))**: 「残存リスクとして報告」だけで済ませず、**決定論的な未評価検出**を推奨します(≈10行、LLM 0)。
  - 内容: flag ONで消費・再利用する時点で`select_alignment_targets(items)`を評価し、「対象なのに`gloss_alignment_status`が無いitem」があればSTOPして`--regenerate-stage kp_*`を要求する。
  - 適用箇所: XのTTS関所、Zの`stage_kp`再利用後。
  - 効果: 対象0件の成果物(約93%)は互換のまま。対象ありのON化前成果物、legacyの旧プロンプトで再整合されたCoffee artifactも同様に、fail-closedになります。
  - 代替案(kp stageの入力shaにversionを含める)は全run一律でSTOPになり、過剰です。
- **M3(Zの再生成時HR、安全側(2)、一部(1))**: `--regenerate-stage kp_*`でHR停止した場合の問題です。
  - (i)再開時に`ctx.regenerate_stage == kp_lv`だとsnapshot復元がスキップされ(er026:1234)、人間の確定値を捨てて選定をやり直します(E6がZで失敗します)。
  - (ii)runner内の例外で止まるため、`install_kp_assets`も`mark_stale_descendants`も走りません(er062:515-520)。インストール済みの**旧artifact**(ON化前)が残り、`--stage tts_*`を単独で起動するとload_level_inputsが旧KP・旧glossで通過します(安全側(1)の穴。ON化前の成果物の範囲)。
  - 是正: 未消費のsnapshotがあればregenerate指定時でも優先復元する。`_gloss_hr_gate`でraiseする前に`install_kp_assets`を呼ぶ(各1〜2行)。

**論点6 QDC監視: OK(指標の提案)**
- level単位の`gloss_alignment_status`分布(NO_TARGETS/ALIGN_PASS/HR/DISABLED)。
- 対象率: 基準約7%。直近20記事levelで15%超ならアラート。
- attempt≥2の発生: 基準0/145。1件でもあれば当該バッチで報告。
- HR: 1件で即時報告(既存)。
- 対象内のREALIGNED比率。
- 1記事セットあたりのalign費用: 0.6円超ならアラート。
- DISABLEDのProduction run: 1件でもあればアラート。
- 記録のみの機械検査で`uncovered`が出た率(将来gate化を判断する材料)。
- level単位のalign所要秒: 60秒超ならアラート。

**論点7 OPEN-359: 結論OK、反例は通知面のみ(M4)**
- gloss不整合KPが完成版へ流れる反例は**ありません**。
  - retryループ: どのattemptのartifactも「整合済み/NO_TARGETS/HR」のどれかで、不整合のまま通るartifactは生まれません。
  - canonicalization非PASS・`kp=None`・`--only-segments`・stage順・解説LLMの位置も迂回なし。
- ただし通知の欠落(M4)と、「放棄されたattemptのartifactがTTSへ進む」(redundancy NGのKP集合。OPEN-359の本体と同類)は残ります。
- 「今回は(a)のみ、(b)(c)は別承認」は技術的に妥当です。受入条件(gloss)は(b)(c)なしで満たし、(b)(c)は冗長NG・記号NGのKPを止めるという仕様変更だからです。
- ただしM4の「ディスク上のartifactでHR判定」は、gloss通知の受入範囲として今回含めるべきです。

**論点8 既定ONの波及(約65 script): MINOR(許容+明文化)**
- A/B/C系の消費側(er003_v1_n3_01_tts_generate.py等)には関所がありません(`collect_unresolved`はX/Zのみ。Grepで確認)。
- HR時は旧glossで完成しますが、これは現状(OFF)と同じ結果で、悪化はしません。
- 呼出元ごとのopt-inは、DEV専用化の再発や引数ミスによるOFF化の危険があるため**不採用を推奨**します。
- 「完成禁止の保証はX/Zのみ」とSSOTに明記してください。
- 任意の代替案: 共有の`verify_episode_audio_validation_gate`の早期return(assemble:472)より前に`collect_unresolved`を1か所入れる。全Familyに効く集中関所になりますが、A/B/C read-onlyとの整合はFableが判断してください。
- 旧Trial scriptを再実行すると実APIを叩く点にも注意(論点11)。

**論点9 kill switch: OK+MINOR**
- import時評価のままでよいです(call時評価に変えるとtestのmonkeypatch資産を壊し、途中で切り替わる危険もあります)。
- 読込順の差は事実として確認できました。Zはer026:63でvfl01(import時に`load_dotenv`)をscaffold(65)より先にimportするため、`.env`指定が効く見込みです。Xはsc(er019:47)がvfl01(main内2457)より先で、効かない可能性があります(推移的import次第で未確定)。
- 是正: 両runnerがrun開始時に**実効値(ON/OFF)と取得元**をstdoutとsummaryへ必ず記録する。運用では「プロセス環境変数のみ」と定める。

**論点10 失敗注入・E2Eの主張: MAJOR(M5、evidence)**
- 案Cは妥当ですが、より単純で同等の方法があります(案B')。harnessが`ga.make_alignment_fn`をwrapし、**本物の`make_alignment_fn`をfake `client=`付きで呼ぶ**方式です(引数は既にあります、ga:198)。
  - モデル照合・usage・JSON解析・retry・HRまで本物を通り、他のOpenAI呼出を横取りする心配もありません。
- **M5**: E7は自然発生の対象が出る確率が約7%で、ほぼNO_TARGETSになります。これでは「再整合済みglossが完成音声とページへ届く」証拠になりません。
  - 対策: E4の合成対象artifact(実LLMで再整合済み)をE7のTTS→assemble→playerへつなぐ(provenance=synthetic入力+production_formal_path)。
  - 解説の`reused_from_previous_run=false`も確認する。
- E7はコピーしたrunの差分再生成なので、「fresh Production初回path」とは主張できません(「KP段〜KP TTS〜assembleはfresh、他segmentは再利用」と書くべきです)。

**論点11 旧Trial script: OK+MINOR**
- T3の27シナリオをtestへ移植するのは必須で、妥当です。
- 他の6本はコメント注記ではなく、**冒頭で`raise SystemExit("HISTORICAL…")`**にするのが安全です。注記だけだと、legacyのシンボルに届く前にselection等の有料APIを叩いてからクラッシュしえます。

**論点12 Dangling Reference: MINOR(追加検出)**
- (1)`HR_RESOLVE_PROCEDURE_01.md`のファイル名だけを参照する文字列がコード内にあります(ga:946/992、er019:532/1563)。手順書を移すなら同時に更新が必要です。
- (2)docstringの「legacy artifactは常に[]」(ga:901、er019:519/1554)。
- (3)SSOT内の`GLOSS_ALIGNMENT_FAILED_NOTICE.md`/fallback(i)記述はGrepで要確認。
- (4)legacyの`gloss_alignment_status="FAILED"`(ga:388/395)を`collect_unresolved`が認識しません(ga:905)。現在ディスク上に該当0件(Grep確認)ですが、`"FAILED"`も未解決として扱う1行の防御を推奨します。`resolve_gloss`の受理状態にも追加してください。

## 3. チェック表(12観点+条件C 6点)
| 観点 | 判定 |
|---|---|
| 1 必要性 | 必要(承認済み仕様の配線) |
| 2 単純化 | mode廃止で単純化。失敗注入は案B'がより単純 |
| 3 既存流用 | 関所・HR報告とも既存を流用。Zの`_gloss_hr_gate`方式(ディスク直読み)をXへ揃える |
| 4 情報喪失 | M4: HR判定がメモリ上の値に依存し、ディスク上の実体と食い違う |
| 5 不要LLM | 対象itemのみ。解説の再生成はM1是正で必要時のみ |
| 6 非決定性 | 対象選定は決定論的。LLMは対象時のみ |
| 7 HR増 | 約0.2%未満。解消後の誤報(論点4)は要是正 |
| 8 不要Rewrite | Trial 0/32。golden testで固定 |
| 9 コスト | +0.014〜0.08円。E7の上限は事前算出 |
| 10 retry整合 | 本体はOK。Zの再生成×HR再開が不整合(M3) |
| 11 Failure安全 | 新規初回経路は安全側(1)。再利用経路はM1〜M3 |
| 12 再発防止 | 未評価検出(M2)で構造的に塞げる |
| C-1 Trial専用化 | mode廃止で解消 |
| C-2 全体矛盾 | A/B/Cは関所なし(明文化) |
| C-3 初回/retry/fallback一致 | 一致。再生成経路のみM3 |
| C-4 Dangling | 論点12 |
| C-5 Failure安全 | 上記11と同じ |
| C-6 QCD新問題 | 小。監視指標は論点6 |

## 4. 設計文書に無い追加所見
- **MAJOR(M6、範囲外・別OPEN推奨)**: Adv英語解説LLMの「phrase」は**display_phrase(候補)**で、glossは参考情報です(er019_family_x_kp_explanation_01.py:152-155。Zもer026:1269で同じ)。
  - 再整合後は「phrase "based on" × 参考訳『インタビューをもとにした』」という食い違った入力になります。完成音声も「EN: based on interviews → 解説: based onの解説 → EN再掲」となります。
  - これは元からある構造ですが、再整合の対象item(約7%)にまさに集中します。解説のphraseは`key_phrase`にすべきか、別件としてユーザー判断が必要です。
- MINOR: 完成済みrunでKPを再生成した後、TTSを飛ばしてassembleすると、旧音声で通過します(Gateはstatusのみ見て、テキストとartifactを照合しない)。元からある問題です。
- MINOR: `--level both`でa2がHRになるとassembleの例外でb1bのassembleも止まります(er019:2507-2511)。健全なlevelが巻き添えになります。

## 5. 委任_02で必ず入れるべきtest・evidence
- golden test: 撤去前に作成し、`responses.create`の全kwargsのsha(順序込み)を固定する。
- attempt0でHR→attempt1でselection失敗の場合に、ディスク上のartifactからHR報告・event・最終行が出る(M4)。
- `--stage all`でHRがあるとき、最終stdoutの1行が出る。
- NG_REVIEW_REQUIRED+HR itemでX TTS/assembleが止まり、summaryに`gloss_alignment_run_status`が出る。
- X解説cache: 旧bundle+status付きartifactで再生成され、key_phraseの変化でも再生成される(M1)。
- Z署名: status無し→従来署名(Melos互換)、status有り→gloss含有。
- 未評価検出: 対象ありでstatus無し→STOP、対象0件→通過(X/Z)(M2)。
- Zの`--regenerate-stage kp_a2`→HR→resolve→同じ指定で再実行するとsnapshotから復元し、インストール済みの旧assetでTTSが通らない(M3)。
- `resolve_gloss`後に最終行の誤報が出ない。
- legacyの`"FAILED"`をartifactから検出し停止する。
- Production呼出元が`mapping_gate=True`を渡さない、引数`gloss_alignment_mode`が存在しない、を固定する。
- 実効flag値の記録(ON/OFF、取得元)。
- E8はOPENAI_API_KEYを空にして実行し、raw usage 0件を確認する(実API誤呼出の検出)。
- E4の合成対象artifactをE7へ連結し、解説の`reused_from_previous_run=false`を確認する(M5)。

## 6. 配線後も残るリスクと報告方法
- (1)実LLMでのretry/HR経路は未発火(0/145)。HR経路の証拠は失敗注入のみ。
- (2)完成禁止の保証はX/Zのみ(A/B/Cは関所なし)。
- (3)ON化前の既存完成物(Melos run_e2e_01/02、Coffee。Coffeeにはlegacyで再整合したglossあり)は再評価していない。M2を入れれば再利用時に止まる。
- (4)OPEN-359本体(冗長NG・記号NGのKPがXで完成へ進む)は未解決。
- (5)Adv解説がdisplay_phrase基準である件(M6)。
- (6)kill switchの`.env`経由はXで効かない可能性。
- 報告では「安全側(1)は新規初回経路で成立」と「再利用経路・既存完成物は対象外または是正後」を分けて書いてください。`PRODUCTION_WIRED`の根拠にE2E(合成対象を連結したもの)が含まれるかを明示し、TrialのVALIDATEDと混同しないでください。

## 7. 追加で読んだファイルと答え切れなかった点
- 自己申告: (e)の手順に反し、一部は読む前の1行宣言をせずに読みました。
- 追加で読んだもの(計約45k文字): er019の範囲外(770-880、1935-2000、2365-2526)、約25k文字/er003_key_words_canonicalization.py:707-752、約3k文字/er019_family_x_kp_explanation_01.py:140-164とGrep、約2k文字/er062:470-522、約3k文字/OPEN_ITEMS.md 865行、約2.5k文字/Grep多数: routing、artifactの`gloss_alignment_status`の実在確認、test呼出元、er026のimport順
- DESIGN_DRAFT_01とHR_RESOLVE_PROCEDURE_01は読んでいません。A'構造は再レビュー対象外のため。
- 答え切れなかった点: Xの推移的importで`load_dotenv`がga importより先に走るか。SSOT内のlegacy記述の有無。Z mainの終了時stdoutの文言。

(Fable付記: 上記はopus-consultantの最終回答を逐語転記したもの。Fableは本委任前に`"mode": `フィールド4箇所(ga:836/846/866/886)・`final_merged`経路(sc:825-828)・`HR_RESOLVE_PROCEDURE_01`参照(ga:946/992)をGrepで実在確認済み。)
