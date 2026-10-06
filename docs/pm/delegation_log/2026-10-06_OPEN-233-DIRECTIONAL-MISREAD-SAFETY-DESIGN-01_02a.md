## 管理ID

OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(委任_02a: 設計案のtrigger条件を保存データへ機械適用する反実仮想replay。¥0、データ集計のみ。委任_02はAPI側中断のため分割再開)。並行タスク: 委任_02b(設計doc前半を`docs/pm/design_open233_directional_misread_safety_01.md`へ執筆中)。**本委任は設計docを書かない・読まない。git操作・SSOT編集・runner/checker変更をしない。** 書き込み先: `er052_output/open233_directional_misread_offline_01/`(新規: `trigger_replay_01.py`・`trigger_replay_01.json`・`trigger_replay_01.md`)、`docs/pm/RESULT_PACKET_DESIGN_A.md`(新規)、`docs/pm/delegation_log/`。

**作業方式(必須)**: `Write`/`Edit`で小分け(1回40行以内)、Bash heredoc不使用。説明・考察は書かない(数表と事実のみ)。T-0の委任文保存はWriteを2分割して逐語保存。時間目安25分。

## 性質/到達上限Status/禁止事項

- 性質: ¥0反実仮想(frozen/reuseデータの決定論的集計)。到達上限: 集計表完成。
- 禁止: 有料API(LLM呼び出し禁止)/コード・prompt・runner変更/設計判断の記述(事実の表のみ)/gold変更。
- Opus Gate: 非該当(集計)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read(runner全文Read禁止)。G-1: git出力不使用。F-1: transcript退避不要。T-1: 事前指定Read/Grep一覧に従う(一覧外は理由を記録)。T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2(2026-09-25): TTSなし。T-2追記(7-5): TTSなし。T-3(2026-09-26): ¥0のため適用対象外。

## ユーザー指示(原文、要点)

> ¥0で先に検証すること: 可能な限り既存artifactを使い、今回HC-012/A5-0等の既知方向反転gold/過去の否定・比較・方向系gold/正常なのに旧機械判定が誤爆した代表例、へ候補設計を反実仮想適用する。最低限、今回HC-012を捕捉できるか/既知goldを維持できるか/正常文を再び大量に重大化しないか/追加確認へ送る件数がどの程度になるか、を比較する。

## KPI provenance欄

frozen/reuse: 新仕様9 run(`er052_output/open233_prod_e2e_02/runs/`+`labels/labels_merged.json`)、旧9 run(`er052_output/open233_e2e_acceptance_01/runs/`+旧35件ラベル`er052_output/open233_floor_selectivity_offline_01/floor_fire_analysis_01.json`)、段階A 42 run(`er052_output/open233_stage1_stageA_01/`、Stage 1のみ)。trigger件数=決定論的集計【確認】。専用確認の結果は未実行(件数のみ)。

## Opus台帳更新

該当なし。

## trigger条件(3案、機械適用する定義)

- **T-A(決定論センサー)**: Stage 1の決定論検査由来候補(`sub_reasons`に`negation_polarity_mismatch`/`number_not_in_fact`/`quote_not_in_ledger`等の決定論種別を含む、または`detected_by`が決定論)で、かつ後段AI(Stage 2)の最終判定が非BLOCKING(ACCEPTABLE/QUALITY)のもの。→専用確認へ送る件数。
- **T-B(決定論×AI食い違い)**: T-Aのうち、Stage 1 AI(r3/r5)が当該文をSUPPORTED判定していた(「決定論で戻した」)もの。
- **T-C(極性・方向語彙)**: Stage 2へ渡った全候補のうち、claim_textまたはLedger該当factに方向・極性を表す語(rollback/roll back/restore/reinstate/withdraw/resume/suspend/stop/start/halt/pause/increase/decrease/rise/fall/expand/shrink/allow/ban/prohibit/approve/reject/add/remove/cancel/revive/put back/bring back/return/reverse)またはnot/no/never等の否定語を含み、Stage 2が非BLOCKINGのもの(語彙は検出用の近似であり設計の正本ではない旨を注記)。
- 各案につき、(1)trigger件数(run別・全体・件/記事、新9 run/旧9 run/段階A[Stage 2判定が無い段階AはT-Cの語彙条件のみで「候補中の該当件数」])、(2)新9 runのラベル済み123件での内訳(真に重大Y/軽微/問題なし/UNDECIDABLE)、(3)HC-012(meta_run03_advanced cycle1「restored the human concierge…」)がtriggerされるか、(4)goldの扱い: 新9 runの重大4件(B3/HC-011/HF-009/HC-012)と旧35件の正当6件のうちtriggerされる件数、段階AのSC gold 6件(定義: runner `SAFETY_CRITICAL_CLAIM_DEFS` L9817付近のtext_substring/pattern)に一致する候補がT-Cでtriggerされる件数、(5)旧floor誤爆24件のうちtriggerされる件数(専用確認が「一致」と返せば通過する前提の処理件数)。

## 事前指定Read一覧

1. `er052_output/open233_prod_e2e_02/runs/meta_run03_advanced.json`: L320-L400(HC-012 claimの記録構造: `dev.issue`「決定論検査で戻した: negation_polarity_mismatch」、`stage1_coverage.sub_reasons`、`materiality`、`llm_materiality`)。この構造を全run共通として機械抽出する。
2. `er052_output/open233_prod_e2e_02/labels/labels_merged.json`: 構造確認(キー形式)。
3. `er052_output/open233_floor_selectivity_offline_01/floor_fire_analysis_01.json`: 構造確認(旧35件のrun/cycle/claim_text/label)。
4. `er052_output/open233_floor_selectivity_offline_01/floor_fire_analysis_01.py`: Grep `def load|def iter|stage2_results|cycles` →run jsonの走査ロジック(再利用)。
5. `er052_open233_self_recovery_flow_runner_01.py`: Grep `SAFETY_CRITICAL_CLAIM_DEFS` →定義ブロック(L9817付近、gold 6件のtext_substring/pattern)。
6. `er052_output/open233_stage1_stageA_01/`: 集約jsonの構造(Grep `claim_text|sub_reasons|routes|flags` で候補の形式を確認)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- run json内: Grep `"sub_reasons"|"detected_by"|"llm_materiality"|"materiality"|"routes"` →抽出キーの確認。段階A: 候補の`sub_reasons`/`routes`/`flags`キー。
- 追記位置: 新規ファイルのみ。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02a.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02a.md_check.json`
2. script作成(関数単位の小分けWrite)→実行: `.venv\Scripts\python.exe er052_output\open233_directional_misread_offline_01\trigger_replay_01.py --new-runs er052_output\open233_prod_e2e_02\runs --old-runs er052_output\open233_e2e_acceptance_01\runs --stagea er052_output\open233_stage1_stageA_01 --labels er052_output\open233_prod_e2e_02\labels\labels_merged.json --old-labels er052_output\open233_floor_selectivity_offline_01\floor_fire_analysis_01.json --out-dir er052_output\open233_directional_misread_offline_01`
3. 出力`trigger_replay_01.md`: 表(1)〜(5)を案別に。HC-012行は個別に明示。
4. git操作なし。

## SSOT追記文

なし。

## Git

git操作なし。SSOT編集権なし。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_DESIGN_A.md`へ: 1. T-0結果。2. 表(1)〜(5)の要約(案別のtrigger件数/記事、HC-012捕捉可否、gold trigger件数、誤trigger見込み件数)。3. 抽出できなかった項目と理由。4. 一覧外Read理由。5. 成果物パス。最終報告は10行以内、考察なし。

