# RUN_CHECK: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 委任_02 実行記録

- 完了run: 18/18、driver_result finished_at=2026-10-07T20:13:40、driver state={'reruns': 2, 'consec_fail': 0, 'stop': None, 'mem_event': False, 'mem_runs': [], 'gate_stops_first': 2}
- 降格履歴(workers): [{'workers': 4, 'todo': 18, 't': '19:20:45'}]
- Gate STOP(1回目)数=2、再実行数=2、infra連続失敗=0、失敗dir=['er052_output/open233_control_checker_polysemy_trial_01/runs\\meta\\nb\\rep6_failed_a1', 'er052_output/open233_control_checker_polysemy_trial_01/runs\\meta\\nb\\rep9_failed_a1']
- 失敗/非0 attempt: {'meta/nb/rep6': [('phase2', 1, 1, 'WRITER_GATE_STOP')], 'meta/nb/rep9': [('phase2', 1, 1, 'WRITER_GATE_STOP')]}
- メモリ(memmon): python子プロセス最大WS=309MB、最大Private=1290MB、OS空き物理最小=2949MB、python同時最大=20。1455/MemoryError検知=なし
- 費用: phase1(B3+JA)=99.062円、EN=27.918円、Checker=60.81円、完了18本総額=187.791円(平均10.433・最大18.496)、ディスク全体(失敗試行含む)=195.541円

## run別
| run | phase1 | EN | Checker | 計 | final_state | cycles | Rewrite件数 |
|---|---|---|---|---|---|---|---|
| meta/nb/rep1 | 5.201 | 0.83 | 2.1912 | 8.2222 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 |
| meta/nb/rep2 | 8.023 | 4.809 | 5.6643 | 18.4963 | RESOLVED_REWRITE_THEN_DOWNGRADE | 2 | 3 |
| meta/nb/rep3 | 7.268 | 1.166 | 4.6034 | 13.0374 | RESOLVED_REWRITE_THEN_DOWNGRADE | 2 | 1 |
| meta/nb/rep4 | 3.687 | 1.507 | 2.3772 | 7.5712 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 |
| meta/nb/rep5 | 8.878 | 4.65 | 1.9566 | 15.4846 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 |
| meta/nb/rep6 | 5.542 | 1.026 | 5.4086 | 11.9766 | RESOLVED_REWRITE_THEN_DOWNGRADE | 3 | 1 |
| meta/nb/rep7 | 7.387 | 1.336 | 2.6301 | 11.3531 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 |
| meta/nb/rep8 | 5.699 | 0.966 | 2.298 | 8.963 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 |
| meta/nb/rep9 | 3.412 | 1.289 | 2.6597 | 7.3607 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 |
| meta/nb/rep10 | 5.065 | 0.727 | 2.3777 | 8.1697 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 |
| hormuz/control/rep1 | 6.145 | 1.357 | 2.7024 | 10.2044 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 |
| hormuz/control/rep2 | 5.675 | 1.22 | 2.224 | 9.119 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 |
| space_weapons/control/rep1 | 5.362 | 1.399 | 4.5392 | 11.3002 | STAGE4_ESCALATION | 3 | 2 |
| space_weapons/control/rep2 | 3.958 | 1.053 | 6.3306 | 11.3416 | RESOLVED_REWRITE_THEN_DOWNGRADE | 4 | 2 |
| sewer/control/rep1 | 4.286 | 1.326 | 2.9925 | 8.6045 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 |
| sewer/control/rep2 | 5.065 | 0.695 | 2.1375 | 7.8975 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 |
| ai_control/control/rep1 | 4.491 | 1.598 | 4.9083 | 10.9973 | RESOLVED_REWRITE_THEN_DOWNGRADE | 2 | 1 |
| ai_control/control/rep2 | 3.918 | 0.964 | 2.8092 | 7.6912 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 |

Checker発火(Rewrite>0)run数=6/18、Rewrite総件数=10

## Meta Note到達(brief転記、check_brief_transfer.py)
| run | HC-012選択 | 多義Note到達 | 既存notes到達 | 両方 | transfer_block_sha | research_calls |
|---|---|---|---|---|---|---|
| meta/nb/rep1 | False | False | False | False | abd16d9a073c | 0 |
| meta/nb/rep2 | False | False | False | False | abd16d9a073c | 0 |
| meta/nb/rep3 | False | False | False | False | abd16d9a073c | 0 |
| meta/nb/rep4 | False | False | False | False | abd16d9a073c | 0 |
| meta/nb/rep5 | False | False | False | False | abd16d9a073c | 0 |
| meta/nb/rep6 | False | False | False | False | abd16d9a073c | 0 |
| meta/nb/rep7 | False | False | False | False | abd16d9a073c | 0 |
| meta/nb/rep8 | False | False | False | False | abd16d9a073c | 0 |
| meta/nb/rep9 | True | True | False | False | abd16d9a073c | 0 |
| meta/nb/rep10 | True | False | False | False | abd16d9a073c | 0 |

HC-012選択=2/10、多義Note到達=1/10、両方到達=0/10

## Note到達の補足(自前の逐語検出、`runs/note_reach_verbatim.json`)
- check_brief_transfer.py(E2E_02流用)は台帳fact ID(MUSE-HC-012)で照合するため、briefが「ID無し箇条書き」の場合に見落とす(旧規則は多義Noteのみ転記し既存notesは転記しない仕様のため「両方」判定は元々満たせない=0/10は旧規則の仕様どおり)。上表の「HC-012選択False」はID表記が無いだけで、選択されていない意味ではない。
- brief本文の逐語検査: 多義Note全文がbriefに存在=**10/10**(各1箇所)。直前行がロールバック/ミス言及のHC-012相当fact文=**9/10**(rep1〜9)。rep10は、Noteが冒頭「Storyline:」行の直前(brief 8行目)に置かれ、HC-012 factの直後(11行目)ではない(隣接せず。Note到達はするが位置が離れている)。
- 既存notes(「『サービス全体を停止した』とは書かない」)はbriefに無し=0/10(旧規則は多義Noteのみ引き継ぐ。0/12当時と同一条件)。
- ID付きでHC-012が見えるのは rep4/9/10 のみ(briefの書式差)。

## 補足: 失敗試行dirの移動
Gate STOP(1回目、ともにphase2でJA_RECHECK_REQUIRED/JA_FACT_CHECK_STOP)のdir `meta/nb/rep6_failed_a1`・`rep9_failed_a1`は、評価パック生成scriptが `rep*` globで数値変換するため、`er052_output/open233_control_checker_polysemy_trial_01/failed_attempts/meta/` へ移動(内容不変)。費用集計(ディスク全体195.541円)は移動前に取得済み。
