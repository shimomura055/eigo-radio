# 委任_03: Phase 2 是正反映→事前登録確定→Trial実装(Trial専用)→実行→評価→報告(B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01、2026-10-10)

範囲: Trial専用。Production code・Production Prompt・CURRENT_SPEC変更なし。後段AI追加なし。checkout/stash/branch切替なし(main)。出力先 `er052_output/b3_fact_instruction_separation_trial_01/`。
費用: JPY21.67(Cap JPY60)、48 call(B3 36 = C1 18 + A' 18、R0 12 = D 6 + C0 6)、技術retry 0。モデル=gpt-6-luna(B3・R0)。

## 実施内容
1. Opus是正R3: INVESTIGATION_01.mdを是正(Ledger段の`[AMBIGUOUS - …]`タグとVerifier由来文の付与、space F-017は推定、semiconductor B3新規は仮説、notes由来7確定+1推定)。
2. R4: D-min/D-full/Dtag previewを9テーマ(C0 ids)でJPY0実施(`preview_02/`, `preview_summary_02.json`)。D-full Facts総文字数はD-minの1.616倍。指示調検出器`IMP`の再現率10/10を確認(過剰だった「禁止」「限定する」「明示する」は事前登録前に削除)。
3. PREREGISTRATION_02.md確定(sha256 `c3118eb6d28f6a78…`、`frozen_inputs_02.json`に記録)、DESIGN_02.md、PROMPT_DIFF.md(A'のPrompt差分3箇所のみ)。
4. 実行: C1 hormuz rep1を先行1 call(JPY0.358、実測再見積: 36 call約JPY17)→残り35 callを6 process並列(C1/A' x テーマ3群)→評価→D-full採用候補規則適用(E5: 49→20、E1=0、1.616倍≤1.7、目視で指示調なし)→E9を3 process並列(12 call)。
5. 評価: `b3sep_eval_01.py`(E1-E8/E10)、`b3sep_eval_e9_01.py`(E9)。E1は腕名を伏せた63出力(C1/A'/D-min)を全件目視(`eval/blind_outputs_02.md`+`blind_key_02.json`)→開封。E9は12本の記事を通読。

## 実行環境メモ
- repo rootの`py`(system Python 3.14)はscipy未導入でvfl01をimportできない。`.venv/Scripts/python.exe -X utf8`で実行した(pip install不使用)。
- 3 process群の並列実行は費用ログprocess別raw usage(`runs/_raw_usage/`)+台帳`cost_ledger_b3sep_01.jsonl`追記。

## 事前登録からの逸脱・補足(結果を見た基準変更ではないもの)
- E1b(補足指標: 台帳内部語・ID・Storyline重複)を人手目視の後に追加(事前登録外、補足と明記)。
- E9はJA Fact Check(旧Checker)を呼ばない構成(`full_ledger_text=None`)。R0のみの挙動測定に絞るため。
- D-fullのE4(b)(因果接続語)は事前登録の厳格基準に不達。事後に基準を緩めず、そのまま報告(台帳scope/conditions由来で説明不能な増加0を併記)。
- IMP regexは人手目視で3/8を見逃した。事前登録どおり人手を正本とした。

## STOP条件
該当なし(cap未到達、B3入力は凍結sha一致、新LLM工程不要、Research/Ledger仕様変更不要、評価script不具合なし、結果を見たPrompt修正なし)。

## 成果物・要点
`er052_output/b3_fact_instruction_separation_trial_01/RESULT_01.md`(9点・詳細・Status提案)、`HUMAN_CHECK_B3SEP_01.md`、`PREREGISTRATION_02.md`、`cost_ledger_b3sep_01.jsonl`、REPORT §122、DECISION_LOG末尾2エントリ、OPEN-248更新、REPORT_LEDGER。Status提案=VALIDATED(Trial限定、案D)、Production採用はUSER_DECISION_REQUIRED。
