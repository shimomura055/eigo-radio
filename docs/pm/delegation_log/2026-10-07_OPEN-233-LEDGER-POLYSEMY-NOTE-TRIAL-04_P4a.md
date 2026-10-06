## 管理ID

OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04(委任_P4a: stage1 prompt欠陥の修正(単一仕様化)+パターンP1/P2/P3の作成+評価器拡張+holdout準備、¥0)
- ¥0。新規/DEVファイルのみ。並行レビューは読取専用。
- 概要3行: 旧stage1の新旧連結欠陥を単一仕様へ修正。P1/P2/P3と評価器(rollback Gate・安定性・holdout)を作成。unit test・衛生・lint・dry-runで確認。

## 性質/到達上限Status/禁止事項

- 性質: prompt修正・DEV改修(新規/DEVファイルのみ)。
- 禁止: 有料API/Production file変更/SSOT編集/git/5テーマ固有語・特定fact_idのprompt混入/件数目安のprompt記載/評価基準の後付け変更。
- 概要3行: 到達上限はTrial準備まで。衛生チェックPASS必須。Production非接続。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

- 該当なし(¥0)。T-0: 簡略保存+check_delegation_prompt.py実行。T-2/T-3: 音声生成なし・対象外。
- 概要3行: 有料実行なし。音声生成なし。T-0のみ実施。

## ユーザー指示(原文、要点)

- 新旧Prompt連結ミスを解消し単一仕様を確認。2〜3パターンを比較(判定閾値/2段階判定/既存notes/圧縮前後の判定順序/stage1安定化/字数)。ハードコード禁止。
- 合格条件: 捕捉9/14以上、付与率25%以下、holdout誤付与1以下、捏造0、内容一致70%以上、迎合なし。rollback別枠Gate(意味関係の保持、『全体停止ではない』のみ・『復元ではない』は不可)。
- 25%以下にするためだけに正しい重要Noteを機械的に落とす設計にしない。

## 事前指定Read一覧

- B2のstage1/stage2/examples/pattern.json、B3のstage1_5、Aのstage1、gen_notes_p03.py、eval_notes_p03.py、targets.json、l3_labels.py、L3_element_trial_result.md。
- 概要3行: 既存パターンの読込のみ。変更は新規ファイル中心。gen_notes_p03.pyのみ新モード分岐を追加。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 新規: patterns/_common/stage1_prompt.txt、P1_gate_hm/P2_stable/P3_writer_compress、tools/gen_notes_p04.py・eval_notes_p04.py・prompt_lint_p04.py、tests/test_p04_tools.py。
- 更新: eval/holdout.json(A01追加・expected_max)、eval/targets.json(gate_fact)、tools/gen_notes_p03.py(新モード分岐のみ)。
- 概要3行: 単一仕様はlintで機械確認。R採用規則はコード側pick。holdoutはP0a棚卸しの未使用テーマA01。

## 実行コマンド全文

(概要3行: unit test、衛生、lint、dry-run、T-0の5本。)

.venv/Scripts/python.exe -m pytest er052_output/open233_polysemy_trial_03/tests/test_p04_tools.py -q
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/prompt_hygiene_p03.py --patterns er052_output/open233_polysemy_trial_03/patterns --forbidden er052_output/open233_polysemy_trial_03/eval/forbidden_terms.txt
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/prompt_lint_p04.py --patterns er052_output/open233_polysemy_trial_03/patterns/P1_gate_hm er052_output/open233_polysemy_trial_03/patterns/P2_stable er052_output/open233_polysemy_trial_03/patterns/P3_writer_compress
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/run_patterns_p03.py --patterns P1_gate_hm --slugs meta --dry-run
python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-07_OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04_P4a.md --json-out docs/pm/delegation_log/2026-10-07_OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04_P4a_check.json

## SSOT追記文

- なし。

## Git

- なし。

## 報告(RESULT_PACKET項目、10行以内)

- (1)修正後stage1の構成とlint結果 (2)R採用規則 (3)P1/P2/P3の差分と仮説 (4)rollback Gate機械チェック条件 (5)holdout追加テーマと期待値 (6)test・衛生結果 (7)dry-run結果 (8)費用見込み (9)T-0結果
- 概要3行: 上記9項目をRESULT_PACKETへ。詳細は本ファイルと報告に記載。
