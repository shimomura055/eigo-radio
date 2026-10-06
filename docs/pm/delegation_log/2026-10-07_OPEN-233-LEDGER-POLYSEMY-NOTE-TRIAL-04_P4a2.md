# 委任文(簡略保存) OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04 委任_P4a-2

## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04(委任_P4a-2)。必須修正9件をP1/P2/P3へ反映(P1'/P2'/P3)、要素Trial実行(有料上限130円、per-call 5円)、評価。
並行委任P4b-2(er052_output/open233_polysemy_trial_04/runs/*、er052_open233_polysemy_nb_dev_01.py)には触れない。
固定ブロック: E-1 上限130円 / D-1 実費はer052_output/open233_polysemy_trial_03/runs/cost_t04.json / G-1,F-1 該当なし / T-2 音声生成なし / T-3 対象外。

## 性質/到達上限Status/禁止事項
性質: DEV改修+要素Trial実行+評価。到達上限: 比較表・rollback Gate結果・所見(成立判定はFable)。
禁止: Production file変更/SSOT編集/git/特定fact_id・5テーマ固有語のprompt混入/件数目安のprompt記載/試行錯誤的再実行(各パターン1回)/評価基準の後付け変更/良いrunの選択。
独立レビューGate: 本委任は独立レビュー後の必須修正反映の実行(新規レビューなし)。時間見込み・並列化: 実装後に16+4job並列実行(parallel 3/4)。

## 事前指定Read一覧
er052_output/open233_polysemy_trial_03/patterns/_common/stage1_prompt.txt、patterns/P1_gate_hm/*、P2_stable/*、P3_writer_compress/*、tools/gen_notes_p04.py・eval_notes_p04.py・prompt_lint_p04.py、eval/targets.json・holdout.json、docs/pm/opus_l2_review_pt03_design_01.md(参考)。
実施: 上記を全て読み、gen_notes_p03.py・run_patterns_p03.py・eval_notes_p03.py・既存tests・ledger txtも追加で確認した。
新規: patterns/P1p_gate_hm・P2p_stable(P3は既存ディレクトリを更新)。

## 事前指定Grep一覧+追記位置・更新位置の手順
必須修正1〜9(一般規則のみ、rollback/Meta等の固有語はprompt・patternsへ書かない): (1)pred_direction_explicit・素通り (2)R/変化後状態のvague語lint (3)P2'(判定役常時) (4)stage1で既存notes伏せ・cover call別建て (5)判定役固定基準+blocking_word+限定語low→medium (6)表記'..'形式・英語は台帳実在のみ (7)r_echo照合 (8)lint禁止語+prompt hash (9)rollback_gate_labels.md。
更新位置: tools/gen_notes_p04.py(全面改修)、gen_notes_p03.py(stage1既存notes伏せ・cover読込)、prompt_lint_p04.py、eval_notes_p04.py、patterns/*、eval/rollback_gate_labels.md、tests/test_p04_tools.py。
追記: eval/t04_*(label sheet・funnel・eval_table・labels)、runs/cost_t04.json、docs/pm/polysemy_trial_04/T04_element_trial_result.md。

## 実行コマンド全文
- .venv/Scripts/python.exe -m pytest C:/Users/tensh/eigo-radio/er052_output/open233_polysemy_trial_03/tests -q  (結果: 45 passed)
- .venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/prompt_hygiene_p03.py --patterns er052_output/open233_polysemy_trial_03/patterns --forbidden er052_output/open233_polysemy_trial_03/eval/forbidden_terms.txt  (PASS)
- .venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/prompt_lint_p04.py --patterns er052_output/open233_polysemy_trial_03/patterns/P1p_gate_hm er052_output/open233_polysemy_trial_03/patterns/P2p_stable er052_output/open233_polysemy_trial_03/patterns/P3_writer_compress  (PASS)
- .venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/run_patterns_p03.py --patterns P1p_gate_hm,P2p_stable --slugs meta,hormuz,space_weapons,sewer,ai_control,A02,small_bag,A01 --parallel 3 --budget-jpy-per-call 5 --web-search none
- .venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/run_patterns_p03.py --patterns P3_writer_compress --slugs meta,hormuz,space_weapons,sewer --parallel 4 --budget-jpy-per-call 5 --web-search none  (ai_controlは予算上限130円のため省略)
- .venv/Scripts/python.exe C:/Users/tensh/eigo-radio/er052_output/open233_polysemy_trial_03/eval/t04_labels.py
- .venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/eval_notes_p04.py --patterns P1p_gate_hm,P2p_stable,P3_writer_compress --tag t04_ --labels er052_output/open233_polysemy_trial_03/eval/t04_labels.json

## SSOT追記文
なし(SSOT編集禁止。結果はFableが反映)。

## Git
なし(git操作禁止、未実施)。

## 報告
結果要約は docs/pm/polysemy_trial_04/T04_element_trial_result.md と最終報告(SubagentHandback)に記載。
要点: 実費124.19円(上限130)、累計284.32円。捕捉 P1' 2/14・P2' 3/14・P3 3/11(4台帳)、rollback Gateは全パターン合格なし(軸ずれ/未捕捉)、基準6項目は全パターンで未達(付与率のみOK)。
T-0: 本ファイルを保存し check_delegation_prompt.py を実行(結果は _check.json)。RESULT_PACKET.mdは並行委任P4eの結果が入っていたため上書きしていない(最終報告で代替)。
