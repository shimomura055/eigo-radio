## 管理ID

OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04(委任_L2: 最終要素改善パターンP4の設計→要素Trial(7台帳、有料上限¥55)→評価。最後の要素ループ)
- 有料上限¥55(per-call ¥5)。DEV/Trial限定。
- 概要3行: P4(言い換え両方向R列挙+既存notes復帰+ハーネス欠陥修正)を作成。7台帳(A01は予算残次第)で1回実行。評価・rollback Gate・ファネルを出力。

## 性質/到達上限Status/禁止事項

- 性質: DEV改修+prompt設計+要素Trial+評価。到達上限は比較表・rollback Gate・所見(成立判定はFable)。
- 禁止: Production file変更/SSOT編集/git/特定fact_id・5テーマ固有語のprompt混入/件数目安記載/再実行(APIエラー・parse失敗のみ1回再試行)/評価基準の後付け変更。
- 概要3行: 衛生PASS必須。「元に戻す」は一般語として可。上限超過はSTOP。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

- E-1: 上限¥55。D-1: 実費はruns/cost_t04_l2.json。G-1/F-1: 該当なし。T-0: 簡略保存+check実行。T-2/T-3: 音声なし・対象外。
- 概要3行: 費用はprovenanceから集計。音声生成なし。T-0のみ。

## ユーザー指示(原文、要点)

- rollback Gate: 対象Factを自動捕捉し、Noteが「機能を取り下げた/機能のない状態へ戻した/機能そのものを復活・再提供した意味ではない」を保持。「全体停止ではない」「元に戻した」のみ、「復元ではない」型は不合格。
- ハードコード禁止。25%のために正しいNoteを機械的に落とさない。
- 概要3行: 上記を評価基準とする。基準は後付け変更しない。

## 事前指定Read一覧

- T04_element_trial_result.md、t04_funnel.md、patterns/P1p_gate_hm/*、gen_notes_p04.py、eval_notes_p04.py。
- 概要3行: 既存P1'の構成を読み、P4を新規ディレクトリに作成。gen_notes_p03.pyはstage1既存notes復帰の分岐のみ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 仮説H11〜H13はpattern.jsonのhypothesisに逐語。新規: patterns/P4_paraphrase、_common/stage1_prompt_p4.txt。
- 更新: gen_notes_p04.py(H13a〜e・cover record-only)、gen_notes_p03.py(1行)、prompt_lint_p04.py(common_stage1宣言)、eval_notes_p04.py(ファネル表示)、tests。
- 概要3行: 既存パターンの挙動は変えない。lintはP4の独自stage1単一仕様を_commonと照合。

## 実行コマンド全文

(概要3行: pytest、衛生、lint、run、eval、T-0。)

.venv/Scripts/python.exe -m pytest er052_output/open233_polysemy_trial_03/tests -q
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/prompt_hygiene_p03.py --patterns er052_output/open233_polysemy_trial_03/patterns --forbidden er052_output/open233_polysemy_trial_03/eval/forbidden_terms.txt
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/prompt_lint_p04.py --patterns er052_output/open233_polysemy_trial_03/patterns/P4_paraphrase
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/run_patterns_p03.py --patterns P4_paraphrase --slugs meta,hormuz,space_weapons,sewer,ai_control,A02,small_bag,A01 --parallel 3 --budget-jpy-per-call 5 --web-search none
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/eval_notes_p04.py --patterns P4_paraphrase --tag t04l2_ --labels er052_output/open233_polysemy_trial_03/eval/t04l2_labels.json
python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-07_OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04_L2.md --json-out docs/pm/delegation_log/2026-10-07_OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04_L2_check.json

## SSOT追記文

- なし。

## Git

- なし。

## 報告(RESULT_PACKET項目、12行以内)

- (1)H11〜H13実装・test・衛生・lint (2)P4結果とP1'/B2比較 (3)基準6項目 (4)rollback Gate (5)ファネル要点 (6)実費・累計 (7)所見2行 (8)T-0結果
- 概要3行: 上記8項目をRESULT_PACKETへ。詳細は結果md・eval/t04l2_*。
