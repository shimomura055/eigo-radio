# RESULT_PACKET_FC7(一時ファイル)

管理ID: `EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07`
詳細: `EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07_REPORT.md`
(全14項目+SSOT追記案は当該REPORTの各節番号を参照。以下は要約のみ)

1. 候補一覧: home_robots 15件・bci 11件、`{theme}/provocation/candidates.json`
2. スケール/レンズ: A/B/C各3〜4件、D/E各1〜2件、組合せは非網羅
3. 相対ランキング: LLM強制ランキング(同順位禁止)、`{theme}/provocation/ranking.md`
4. 採用代表案: home_robots=CP-A3/CP-B3/CP-C2、bci=CP-A1/CP-B3/CP-C3(いずれも追加レンズなし)
5. 記事全文: REPORT 5節に6本全文転記、パスはREPORT参照
6. Intimate/Societal/Radicalの違い: REPORT 6節(引用比較)
7. Second-order/Inversion: home_robotsのE_inversionは僅差2位止まり、bciはC_radical優勢。4本目採用なし
8. CURRENT FACT 0件化: 6記事全て0件達成、Fact Checker A'は0件でも実行されコスト発生(¥11.36)、Layer1 Deviationは明示skip
9. Writer制約数: v7=5(v6と同数、項目2の定義文言のみ更新)
10. 人間評価7軸チェック表: `index.html`(home_robots/bci各1)に空欄設置、Sonnet補助列は別欄
11. 開発・Trial費: 合計¥23.26(home_robots約9.20/bci約14.06)、5区分はREPORT 11節
12. 量産単価: 未確定(理由REPORT 12節、参考値は記事1本平均¥2.27〜2.47)
13. 残る問題: REPORT 13節(B_societalが現在の延長に近い可能性/時刻誤検出等、未修正のまま記録)
14. Gate 1判定材料: REPORT 14節

分類: **VALIDATED**(Production採用ではない)
BCI実施: 実施した(条件成立、予算余裕・比較上有益と判断)
Framing QA v2決定的スキャン: 設計上利用可能だが時刻表記誤検出あり(REPORT 15節、参考記録のみ)
Family C残額: 実行前¥160.97 → 実行後残り約¥137.71(¥23.26消費、ハード上限内)
Artifact: `er013_output/family_c_future_trial_07/index.html`、
`er013_output/family_c_future_trial_07/bci/index.html`
commit対象候補: `er013_family_c_future_provocation_07.py` /
`er013_family_c_future_writer_07.py` / `er013_family_c_future_trial_07_run.py` /
`er013_family_c_future_qa_test_07.py` /
`EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07_REPORT.md` /
`er013_output/family_c_future_trial_07/**`(新規出力一式) /
`docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07.md` /
`docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07_check.json` /
`docs/pm/RESULT_PACKET_FC7.md`
T-0結果: PASS(reasons無し)
事前指定外Read: spark_gate_06.py全文/qa_02.py L104-269/qa_01・qa_02の`^def `Grep(理由はREPORT 17節)
STOP有無: なし

offline regression: `run_project_regression.py --pattern "er013*_test_*.py"` →
102件全PASS(既存88+新規14)
