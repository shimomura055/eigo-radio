# REUSE_INDEX_01: Writer「Detective」単語回避 Trial 成果物の再利用索引(委任_02、2026-10-21)

- 性質: Trial Closeout用の索引のみ(新規分析なし)。ユーザー決定(2026-10-21): Pattern A/B/C全てProduction採用見送り。原文=`docs/pm/delegation_log/2026-10-21_FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01_CLOSEOUT_USER.md`。
- 表記: 以下のpathはすべてリポジトリ相対。`<P>`=`er086_output/writer_detective_avoidance_trial_01/<A|A_rerun1|B|C>`(Aは初回=本文未完成、A_rerun1=同一条件の再生成=評価対象のA)。Baseline=`er019_output/middle_east_yemen_saudi/run_mey_02`(変更なし)。
- 相関と因果は区別する。以下は観測の所在のみで、追加指示と結果の因果は未確定。

## 対応表(ユーザー原文§3の項目1〜9)
| # | 項目 | path | 内容 |
|---|---|---|---|
| 1 | Baseline原稿 | `er019_output/middle_east_yemen_saudi/run_mey_02/ja_writer/{original,revision1,revision2}.md`、`.../b1b/article.md`(Advanced)、`.../a2/article.md`(Standard) | Baselineの JA R0/R1/R2・Advanced・Standard 全文 |
| 1 | Pattern A原稿 | `<P>=A_rerun1`: `ja_writer/{original,revision1,revision2}.md`、`b1b/article.md`、`a2/article.md` | 評価対象のA(再生成分) |
| 1 | Pattern A初回(STOP) | `er086_output/writer_detective_avoidance_trial_01/A/ja_writer/audit/rejected_w1_r2_symbol.md`、`A/ja_writer/factlock/` | 初回はProduction JA記号QAでSTOP、本文未完成(Advanced/Standardなし) |
| 1 | Pattern B原稿 | `B/ja_writer/{original,revision1,revision2}.md`、`B/b1b/article.md`、`B/a2/article.md` | B全工程 |
| 1 | Pattern C原稿 | `C/ja_writer/{original,revision1,revision2}.md`、`C/b1b/article.md`、`C/a2/article.md` | C全工程 |
| 2 | 各Patternの正確なPrompt差分 | 文言: `er086_writer_detective_avoidance_trial_01_lib.py` L24〜(定数`PATTERN_TEXT`、A/B/C)、設計=`TRIAL_DESIGN_01.md` §2(注入点)・§3、注入位置=`design_matrix_01.json::injected_stages` | 追加指示は全Patternで同一の6工程・同一位置に挿入 |
| 2 | 実際にLLMへ渡したPrompt全文 | `A/prompt_dump/{A_r0,A_r1,A_r2,A_r2_symbol_rerun}.txt`、`A_rerun1/prompt_dump/`、`B/prompt_dump/`、`C/prompt_dump/{C_r0,C_r1,C_r2,C_adv_translation,C_adv_in_one_line,C_standard,C_standard_2}.txt`、各`trial_run_summary.json`(`pattern_text`・`pattern_text_sha256`) | 各`prompt_dump`に`contains_pattern_text`の確認結果あり |
| 3 | R0/R1/R2/Advanced/Standard工程別結果 | `COMPARISON_RESULT_01.md` §1(工程別detective件数)・§5(工程別QCD)、各`<P>/cost.json::by_stage_jpy`、`<P>/writer_run_summary.json`、`<P>/ja_writer/runtime_evidence.json` | R0〜R2はja_writer、Advanced=`b1b/`、Standard=`a2/` |
| 4 | Fact Ledger | `<P>/research_ledger/{verified_fact_ledger.txt,fact_ledger_draft.json,fact_ledger_verification.json}`(各Patternへbyte複製、sha一致=`<P>/input_copy_evidence.json::sha_match`)。元=`er019_output/middle_east_yemen_saudi/run_mey_02/research_ledger/` | 比較入力のFact Ledger |
| 4 | B3(storyline) | `<P>/storyline_b3/{selected_brief.md,selected_brief_annotated.md,writer_constraints.txt,full_ledger.json,annotation.json}`。元=`.../run_mey_02/storyline_b3/` | B3比較入力(複製、同一sha) |
| 4 | 実行条件 | `TRIAL_DESIGN_01.md` §3(実行コマンド)・§7(費用)、`design_matrix_01.json`、`<P>/trial_run_summary.json`(budget_jpy=40.0・rf_run=false等)、harness=`er086_writer_detective_avoidance_trial_01_{lib,run,eval,page,test_01}.py` | 同一モデル・工程・retry設定、RF未実行(共有review_queueを汚さないため) |
| 5 | Detective出現件数 | `COMPARISON_RESULT_01.md` §1、`eval/results.json` | Baseline: Adv2/Std2(JA R2『探偵』2)、A/B/C: 0/0。類似語観測=同§2 |
| 6 | 事実誤り・品質懸念の具体例と根拠 | `COMPARISON_RESULT_01.md` §4、`manual_fact_review_01.json`(Sonnet通読の件別根拠)、`eval/judgment_fact_{Adv,Std}_{Baseline,A,B,C}.json`(LLM事実検査の生応答) | A: 帰属欠落1件、B: 因果創作1件、C: 重大0・軽微懸念(『other side's bases』等)。いずれも追加指示との因果は未確定 |
| 7 | LLM評価 | `COMPARISON_RESULT_01.md` §3、`eval/results.json`、`eval/judgment_ent_{Adv,Std}_run{1,2}.json`、評価Prompt=`judge_prompts_01.json` | gpt-6-luna、ラベル伏せ・ランダム順・2回 |
| 7 | 人間の通読評価 | ユーザー通読所見は`docs/pm/delegation_log/2026-10-21_FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01_CLOSEOUT_USER.md` §2③(Cは説明的・反復的、原因は未確定)。Sonnet通読所見=`TRIAL_CLOSEOUT_01.md`「結果要約」注③ | ユーザー通読の詳細メモ(別ファイル)は未保存=上記原文の記述のみ |
| 7 | Fable評価 | `TRIAL_CLOSEOUT_01.md`末尾「最終ラベル・ユーザー決定」節 | C=VALIDATED(試験評価・n=1)/B=NOT_VALIDATED/A=REJECTED |
| 8 | 使用モデル | JA R0/R1/R2=`gpt-6.1-sol`、Advanced(2呼出)/Standard=`gpt-6-luna`(`<P>/raw_usage_log.jsonl::model_id`、Cで確認)。評価LLM=`gpt-6-luna` | 生成はProductionと同一のモデル・工程 |
| 8 | 実費 | 合計JPY55.7(生成53.9+判定1.8、出典OPEN-429)。Pattern別Writer実費=`<P>/cost.json`(A初回14.221・A_rerun1 13.742・B 14.086・C 11.847、Baseline参考13.275) | |
| 8 | 生成回数 | A初回4呼出(R0/R1/R2/R2記号QA再実行でSTOP)、A_rerun1/B/C=各6呼出(R0・R1・R2・Advanced2・Standard1)。Pattern Aのみ計2回生成、B/Cは各1回 | `<P>/raw_usage_log.jsonl`の行数 |
| 8 | 所要時間 | `<P>/writer_run_summary.json::elapsed_seconds`(A_rerun1 18.091/39.972、B 17.005/21.698、C 13.684/21.948、いずれも当該ファイル内の2値)。A初回・Trial全体の壁時計時間・各値が指す工程名は**未記録(ログに無く推定値は書かない)** | |
| 9 | 比較ページ | `user_test/writer_detective_trial_01/index.html` / https://shimomura055.github.io/eigo-radio/user_test/writer_detective_trial_01/index.html | |
| 9 | 関連生成ログ・証拠 | `<P>/raw_usage_log.jsonl`、`eval/raw_usage_log.jsonl`、`<P>/input_copy_evidence.json`、`COMPARISON_RESULT_01.md`、`TRIAL_CLOSEOUT_01.md` | |
| 9 | commit | 65a1080d5(T-0+原文+設計+harness+test)、b1d2e91d0(A/B/C生成結果+評価+比較ページ)、c7eba790b(委任_01 Closeout+OPEN-429)、本Closeoutは委任_02のcommit | |

## 未保存・限界(事実のみ)
- 所要時間: A初回およびTrial全体の壁時計は未記録。
- ユーザー通読の詳細メモ: 未保存(ユーザー指示原文§2③の記述のみ)。
- Risk Flagger(RF)は未実行(共有review_queue保護のため)。Entertainment評価はluna単独。各Patternはn=1。

## 再検討時の出発点
- 将来再検討する場合は、本索引の保存済み結果(入力・Prompt・出力・評価の対応)を出発点とする。同一Trialを最初からやり直す必要はない。
- ユーザーはDetectiveという単語を避けたい意向自体は撤回していない。今回はA/B/C全てProduction採用を見送り、現行Writer Prompt・Production経路は変更していない。
- 未承認の改善作業・追加Trial・再生成は自動再開しない。再開・Production採用はユーザーの明示承認による。
