# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01 委任_02(Opusレビュー_I逐語保存+必須修正M1〜M5のharness反映[JPY0]→Phase B実走: R1(B3 計7 call: Baseline×2/C1×2/C3×2/C2×1)→機械チェック+盲検評価→R2(有望候補最大2の下流W-1+BaselineのW-1再走1本)→必要時のみR3改善ループ1周→Trial Closeout文書。**Trial専用経路(er083)、Production非変更、到達上限VALIDATED(範囲限定)、Fable枠JPY150(期待約97/上限約142)**)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: Trial harness修正+有料Trial実走+評価+Closeout文書。
- 到達上限Status: `B3BG_TRIAL_CLOSEOUT_PENDING_FABLE`(VALIDATED/REJECTEDの最終分類はFable。Production採用・配線・過去テーマ展開は範囲外)。
- 禁止: Production module(B3/runner/producer/契約/Writer)の変更/`run_mey_01`配下の書込み/Research再実行/音声化・試聴ページ/仕様文への固有事例・Fact ID混入/候補の無駄な増殖(R3は1周まで)/有料runの自動再起動(26節。失敗はそのまま記録)/枠JPY150超過見込み時の続行(超過前にSTOP報告)/並行agent(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_03: er006/er003_v1_n3/crosslevel/er020/er063/er011、CURRENT_SPEC LR節)の担当ファイル編集。
- 固定ブロック: **E-1**(Opus_I必須修正M1〜M5と推奨実走構成を`TRIAL_DESIGN_01.md`へ§8として反映してから実走。TRIAL_DESIGN §4 rubricをM3で改訂)/**D-1**(修正範囲=Trial harness(er083)のみ。読込効率: Production fileは指定行のみ)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。**並行agentあり(FZAQ 委任_03)**: 共有SSOT(OPEN_ITEMS/DECISION_LOG/USER_DECISION_REGISTER/REPORT_LEDGER)は「編集直前に`git status --porcelain <file>`でclean確認(dirtyなら60秒間隔最大10回待つ)→再読→自分の行のみ編集→直ちにadd→commit」、`.git/index.lock`待ち再試行、non-ffは`pull --ff-only`後再試行、conflictはSTOP。ACTIVE_TASKは先頭に自ブロック追記(gitignore))/**F-1**(Fable枠JPY150[7-7: 承認済みScope内・300円以下=自律]。中東記事E2E Cap180とは別勘定。`--budget-jpy`はR1=70、R2=50、R3=30をプロセス単位で分割(並列時の非原子性対策)。実費は実cost log行(B3 theme `NEWS_FAMILY_X_B3_FACT_SELECTION_PRODUCTION_01`を含む、M1修正後)から集計し出典付き報告。当日累計(daily_dev_cost)も報告)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01_委任_02.md`へ保存し`check_delegation_prompt.py`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_B3BG2.md`)。`TTS_EXECUTION_MODE=STANDARD`を環境に明示(音声stageは起動しない)。

## Fable決定(Opus_I照合結果)
Opus_I=GO_WITH_CHANGES、ユーザー判断事項なし。M1〜M5を全て採用、推奨実走構成を採用。C2は対照n=1のみ(W-1・改善ループ対象外)。軸2は「判定の正しさ」(M3)で評価し「不足明示・不補完」を正式な成功として扱う。VALIDATEDの範囲は「非侵食・欠落時の不補完・帰属と動機の区別」に限定され、「必要なときに追加する」能力(陽性対照)は本Ledgerでは検証できないことをCloseoutに明記。

## 作業要件
1. **Opus_I逐語保存**: `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-a7f9101642d202644.jsonl`→`C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01\OPUS_REVIEW_I_01_VERBATIM.md`(`--index 0`、文字数・sha256)。
2. **M1(予算ガード/費用集計のバグ)**: Production B3 `_call_once`が内側で`THEME_TAG=NEWS_FAMILY_X_B3_FACT_SELECTION_PRODUCTION_01`を設定し外側themeを上書きする(`er005_cost_logger.py:42-51`)ため、`lib.py:155 TRIAL_THEMES`にこのthemeが無いとBudgetGuard・集計がB3実費を0円と数える。修正: Trial専用cost logに記録された実API行を全て数える(またはB3 THEME_TAGを集計対象に加え、Trial run dir配下のlogに限定)。test: 実cost logger経由の行が集計されること(stubでthemeを直接書かない形で再現)。
3. **M2(下限2件との相互作用)**: `COMMON_GUARD`に一般文言追記「【背景補完】で追加したFactは、上記『最低2件』に数えません。背景補完の前に、最低2件の条件を満たす選定を完了してください。」`analyze_selection`に`core_selected_ids`(補完除く)・`core_verified_n`・`min2_met_only_via_supplement`を追加し、Trueは軸1・軸3で「問題」。最終結果が初回/再評価どちらのcallかを記録。test追加。
4. **M3(rubric改訂)**: 軸2=「判定の正しさ」: 適切=Ledgerに直接述べるFactがある前提は補完/無い前提(動機・サウジ攻撃の帰属)を不足として明示し補わない。問題=F01/F11を「なぜ」の回答として扱う、F09/F10を「誰が」の回答として扱う、不足を記録しない。有望=軸1維持∧軸2適切∧軸3〜5問題なし。「不足明示型」は正式な成功。盲検パックの「採用Fact: …」ID行を除去し内容要約に置換(`eval.py:106`)。読者テストQ1は「主体は発表で特定されていない」と記事が明示する場合をLedger裏付けの正答として扱う(ただしそのためだけのF02/F03追加は軸3減点)。
5. **M4(C3文言)**: 一般文言で追加「挙げてよい疑問は、それが解けないと読者がStorylineの文意を取れない、または誤解するものに限ります。『もっと知りたい』『次に気になる』疑問は対象外です。」「各疑問に型(誰が/なぜ/何の流れの一部か)を付け、Factがその型の内容を自身の記述として述べている場合に限り、回答とみなします。状況や経緯を述べるFactは『なぜ』への回答になりません。」C1/C3共通に任意改善3文(「採用Factで既に部分的に示されている前提は欠落とみなさない」「判定に迷う場合は追加しない」「推測すれば言えるFactは直接述べていない扱い」)を追加。固有事例混入0を機械確認。
6. **M5(複数サンプル)**: `run.py`に`--sample N`(出力先`<article>/<candidate>/s<N>`)、`eval.collect`を複数サンプル対応。判定規則を事前固定: 補完挙動と`core_selected_ids`が2サンプルで一貫し、かつBaseline再走2本の観測範囲から外れる場合に限り「補助指示の効果」とみなす。Baselineの下流W-1再走は、軸1判定が候補と1段階以内の差なら必須。sidecar中核数値集合の候補vs Baseline機械差分(0円)を追加。
7. **test**: 既存79件+M1/M2/M5の新規testを全PASS。dry-run(モック)で再確認。
8. **R1実走(並列可、各プロセス`--budget-jpy 70`を分割: 例 Baseline/C1/C3各20、C2 10)**: Baseline×2(s1,s2)、C1×2、C3×2、C2×1 = 計7 call(再評価・retryで増える分は記録)。期待約53円/上限約68円。各runの選定ID・core_selected_ids・補完Fact・理由・【背景確認】note・再評価有無・`min2_met_only_via_supplement`・費用・model_id実測を記録。
9. **機械チェック+盲検評価**: `eval.py`で比較表、固有事例混入0、中核数値差分。盲検パック(候補名伏せ)を作り、別の評価観点で5軸×3段階を付ける(評価者=本agentでよいが、候補名を伏せたパックを先に生成しkeyは後で照合する手順を守る。汎用性(軸5)は固定チェックリスト[固有語依存/当テーマ構造依存/過剰補完の分岐]で経済・科学ニュースの思考実験を記録)。有望候補の判定(M3基準)。
10. **R2**: 有望候補(最大2、代表sample各1)の下流W-1 JA Writer(`writer_probe.py`、一時out-dir)+BaselineのW-1再走1本(軸1判定が1段階以内の差なら必須。差が大きければ省略可だが理由記録)。約44円。日本語記事全文をBaselineと並べた比較ファイル`ARTICLE_COMPARISON_01.md`(候補名・採用Fact付き)を作る。読者テストQ1/Q2を記事に対して実施。
11. **R3(必要時のみ1周)**: 有望候補が無く、失敗原因が文言で是正できると分析できる場合のみ、修正候補1本×B3 2 sample+W-1 1本(約30円)。単なる言い換えの反復はしない。改善見込みが低ければR3を行わず終了。
12. **Closeout文書**: `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01\TRIAL_CLOSEOUT_01.md`にユーザー§5の順(1結論と分類案VALIDATED[範囲限定]/REJECTED/UDR候補、2仕様差分、3採用FactのBefore/After[「誰が・なぜ」関連Factの扱い]、4ストーリー性への影響、5記事テキスト比較[全文はARTICLE_COMPARISON_01.mdへ]、6QCD[実費・量産時の追加コスト(B3 1 call増分と再評価確率)・処理時間]、7未解決事項・リスク[Ledger欠落=陽性対照なし/VALIDATED範囲限定/本番化に必要なschema・契約・下限算入規則の変更/不足明示が記事に反映されない構造(producerがLedgerから決定論的に組立)/C2網羅傾向])。Fable最終分類欄は空けておく。
13. **SSOT**: OPEN-423 Status更新(Trial結果要約・費用・分類案)。DECISION_LOG末尾(Opus_I結果・Fable決定・実走結果)。REPORT_LEDGER 1行。ACTIVE_TASK先頭ヘッダ。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01\TRIAL_DESIGN_01.md`、`C:\Users\tensh\eigo-radio\er083_b3_background_fact_trial_01_{lib,run,eval,writer_probe,test_01}.py`
- `C:\Users\tensh\eigo-radio\er005_cost_logger.py` L30-60、`C:\Users\tensh\eigo-radio\er019_family_x_storyline_b3_fact_selection_01.py` L170-190・L245-260
- `C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\{storyline_b3\fact_selection_evidence.json, ja_writer\revision2.md, cost.json}`(読取のみ)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `rg -n "TRIAL_THEMES|THEME_TAG|BudgetGuard" C:\Users\tensh\eigo-radio\er083_b3_background_fact_trial_01_lib.py C:\Users\tensh\eigo-radio\er019_family_x_storyline_b3_fact_selection_01.py`
- `OPEN_ITEMS.md`: `OPEN-423`→Status更新。`DECISION_LOG.md`末尾。`docs/pm/REPORT_LEDGER.md` 1行。`docs/pm/ACTIVE_TASK.md`先頭。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01_委任_02.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01_委任_02.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-a7f9101642d202644.jsonl" --role assistant --index 0 --tool-use-name SubagentHandback --tool-input-field message --out C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01\OPUS_REVIEW_I_01_VERBATIM.md`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\stop_scope_check_01.py --managed-id FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01 --run-dir C:\Users\tensh\eigo-radio\er083_output\b3_background_fact_trial_01 --out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_B3BG2_stop_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m pytest C:\Users\tensh\eigo-radio\er083_b3_background_fact_trial_01_test_01.py C:\Users\tensh\eigo-radio\er019_family_x_b3_min2_test_01.py C:\Users\tensh\eigo-radio\er019_family_x_b3_production_wiring_01_test_01.py -q`
- R1(例、候補・sampleごとに1プロセス。実引数): `set TTS_EXECUTION_MODE=STANDARD && C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er083_b3_background_fact_trial_01_run.py --article middle_east_yemen_saudi --ledger C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\research_ledger\verified_fact_ledger.txt --theme "中東情勢が悪化、イエメン・サウジ周辺で攻撃続く" --candidate baseline --sample 1 --out-root C:\Users\tensh\eigo-radio\er083_output\b3_background_fact_trial_01 --budget-jpy 20`(`--candidate baseline|C1|C3`×`--sample 1|2`、`--candidate C2 --sample 1 --budget-jpy 10`)
- 評価: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er083_b3_background_fact_trial_01_eval.py --out-root C:\Users\tensh\eigo-radio\er083_output\b3_background_fact_trial_01 --article middle_east_yemen_saudi --out C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01\R1_EVAL_01.md --blind-pack C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01\R1_BLIND_PACK_01.md`
- R2(例): `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er083_b3_background_fact_trial_01_writer_probe.py --run-dir C:\Users\tensh\eigo-radio\er083_output\b3_background_fact_trial_01\middle_east_yemen_saudi\<candidate>\s<N> --budget-jpy 17`
- 費用集計: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er083_b3_background_fact_trial_01_eval.py --cost-summary --out-root C:\Users\tensh\eigo-radio\er083_output\b3_background_fact_trial_01`と`C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\daily_dev_cost_01.py --date 2026-10-19`(存在する実パスに合わせ、実行全文を記載)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`

## SSOT追記文(要点)
- OPEN-423: 「Opus_I GO_WITH_CHANGES(M1〜M5反映)。R1 7 call/R2 W-1 N本/R3有無。結果要約(採用FactのBefore/After、不足明示の有無、軸1〜5)。実費JPY<実測>/150。分類案=<VALIDATED(範囲限定)/REJECTED>、Fable最終分類待ち。Production採用未承認、過去テーマ展開は範囲外」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1(JPY0段階): Opus_I逐語、harness修正+test、TRIAL_DESIGN §8、delegation_log。msg: `FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01 委任_02: Opus_I必須修正M1〜M5(費用集計バグ/下限2件非算入/rubric改訂/C3文言/複数sample)+test、Opus_I逐語保存(JPY0)`
- commit 2(実走後): `er083_output/b3_background_fact_trial_01/**`(wav等の大容量なし想定)、R1_EVAL/R1_BLIND_PACK/ARTICLE_COMPARISON/TRIAL_CLOSEOUT。msg: `FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01 委任_02: Phase B実走(R1 B3 7 call・R2 W-1 N本・R3有無)+盲検評価+Closeout文書(実費JPY<実測>/150、Production非変更)`
- commit 3: SSOT。

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_B3BG2.md`)
4行: (1)整合(M1〜M5反映表、Production非変更のgit diff 0行、固有事例混入0)(2)Production到達経路=変更なし(3)成果物とcommit sha、R1結果表(候補×sample: 採用ID/core/補完/不足明示/再評価/費用)、Baseline揺れの観測範囲、盲検評価5軸、有望候補の有無とM3基準の根拠、R2記事比較の要点(Q1/Q2)、R3有無、実費(R1/R2/R3別・合計/150、出典行)、当日累計、分類案と限界(陽性対照なし)(4)撤去/残置(一時out-dir、モック出力)。`判定整合:`・`判断候補:`(本番化に必要なschema/契約/算入規則=次段階の論点として列挙)・T-0 check・自己チェック(再起動0/Production不変/枠内/音声0)。
