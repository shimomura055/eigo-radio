## 管理ID

OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03(委任_H1: 要素Trial(自動Note生成単体)の実行・評価ハーネス準備)
- ¥0(unit test・dry-runのみ)。
- 新規ファイルのみ(er052_output/open233_polysemy_trial_03/配下)。
- 並行委任F0・Opus出力には触らない。

## 性質/到達上限Status/禁止事項

- 性質: DEVツール実装(新規ファイルのみ)。
- 禁止: 有料API実行/Production file変更/SSOT編集/git/er052_output/open233_polysemy_trial_02/配下の変更(読込のみ)。
- 対象fact_idをprompt・生成ロジックへ入れない(評価スクリプト内の正解表としてのみ使用)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

- 該当なし(¥0)。
- T-0: 簡略保存+check_delegation_prompt.py実行。
- T-2/T-3: TTSなし・対象外。

## ユーザー指示(原文、要点)

- 有力な改善パターンが複数ある場合は小規模な要素Trialで比較(一体化/2段階化/判定条件の表現違い/Noteテンプレート/字数上限/exampleの有無)。2〜3パターン。
- 特定Fact ID・5記事へのハードコード禁止。
- 要素評価: 注意が必要なFactを拾えるか/拾いすぎないか/逆転リスクの表現が正しいか/原資料にない解釈を作っていないか/過度に長くないか/過学習でないか。

## 事前指定Read一覧

- gen_notes_p02.py(流用元)、P0a_article_selection.md(対象fact_id・既知誤読)、LEDGER_FREEZE_P02.json(5テーマのcontrol txtパス)。
- 読込のみ。上記以外へ拡大しない。
- 実際のtxtパスはledgers/<slug>/verified_fact_ledger_control.txtを使用。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 新規: tools/gen_notes_p03.py(--pattern、stage1必須・stage2任意で一体型/2段階型、{LEDGER_FACTS}/{MAX_CHARS}/{EXAMPLES}、prefix.txt、runs/<pattern>/<slug>/出力)。
- 新規: tools/eval_notes_p03.py(eval/targets.json=評価専用の正解表、パターン×テーマ表、label sheet)、eval/holdout.json(5テーマ以外1〜2本、実行しない)。
- 新規: tools/run_patterns_p03.py(並列バッチ、runs/batch_log.jsonl、dry-runのみ)、tests/test_p03_tools.py、patterns/example_pattern/stage1_prompt.txtのダミーのみ。

## 実行コマンド全文

.venv/Scripts/python.exe -m pytest er052_output/open233_polysemy_trial_03/tests/test_p03_tools.py -q
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/run_patterns_p03.py --patterns example_pattern --slugs meta --dry-run
python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03_H1.md --json-out docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03_H1_check.json

## SSOT追記文

- なし。

## Git

- なし。

## 報告(RESULT_PACKET項目、8行以内)

- (1)作成ファイル・行数 (2)test結果 (3)dry-run結果 (4)holdout候補テーマとパス (5)1パターン×5テーマの費用見込み (6)T-0結果
