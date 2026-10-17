## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_08(Opus条件Aレビュー逐語保存+評価手順の是正反映[JPY0]→Stage 1a補正の有料実行[inbound_tourism M2c/M3c、確認パスのみ]→修正前後差分記録+R-07人手判定→SSOT→commit)。Stage 1bは本委任で**実行しない**(別日2026-10-18 JST以降)。並行タスク衝突: なし(BAPEは#106待ち、S3Wは試聴待ち)。commitを伴う作業は本委任のみ。

## 性質/到達上限Status/禁止事項
- 性質: ユーザー承認済みTrial(#104費用承認・#107設計是正(b))の承認範囲内実行。到達上限Status=`STAGE_1A_CORRECTED_PENDING_FABLE`。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDに到達しない。
- Fable判定(11-3): Opusレビュー_B=GO(コード修正なし、評価手順・注記の反映のみ)。Claude案と一致、承認済み仕様内、新Product原則なし → Fable判断で次工程(本委任)へ進む。
- 費用上限(T-3定型): 「上限¥60(Guardrail、本委任の有料部分=inbound M2c/M3cの確認B3 2回≒22円+新規Fact検証が入った場合の上積み)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」 harnessの実費ガード(1a上限493、累計1,040、日次soft 1,000)はそのまま有効。`--paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040`、`--other-spend-today-jpy 71.3`(本日のRLCT外支出=SJS4 41.6+S3W 18.5+その他≒71.3。harnessがraw_usage_logから当日RLCT支出212.80+10.88を自動計上する場合は二重計上しないよう既存実装を確認し、使った値と根拠をRESULT_PACKETに書く)。
- 禁止: Stage 1b・任意Aの実行禁止。Production runner/Prompt/Style変更禁止。既存1a成果(`coffee_prices/*`, `inbound_tourism/M0,M0b,M0p,M1,M2,M3`)の変更・削除禁止(sha前後IDENTICAL必須)。Research再生成禁止。Coffee M2/M3の再生成禁止(conform PASS)。B3 Prompt文言(lib.py:504の`UNVERIFIED_PHRASE`等)の変更禁止(1aとの条件維持、Opus R-B9-1)。有料runの再起動禁止(26節、rc≠0・外部停止ならSTOP報告)。git add -A/-u/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。
- 時間見込み: 全体約60分(Opus逐語保存10/評価手順反映10/有料実行10/差分・R-07判定15/SSOT・commit15)。直列(有料実行は1回、同一出力dir)。
- 費用/日次: 当日(JST 2026-10-17)既使用約JPY284.1(出典: ACTIVE_TASK.md L4)/残約715.9/本委任見積JPY22(期待)〜60(上限)(根拠: 1a実測B3単価 `1a|inbound_tourism|M2|b3_initial`=10.467、`M1|b3`=10.102 → 確認B3 1回≒11円×2方式。新規Fact検証 `M2|verify_sel_r0`=7.311/`M3|verify_sel_r0`=9.001を上積み上限)/改善見込み高/承認区分: C(承認済みscope内。#104 1a上限493の残280.2、#107 §3「追加費用見込み：約JPY22」)。
- 前委任(委任_07)QDC記録: 目的=確認パス実装・dry-run(JPY0)/試行1回/結果=commit 9d0c41473、test 25/25、conform Coffee PASS・inbound FAIL(F05)/費用JPY0/改善見込み高/次の一手=本委任(有料補正)。
- 前委任(委任_07)受入記録(Gate 7): (1)当初目的(ユーザー原文逐語、`..._DESIGN-FIX-1B_USER.md` §2/§3)=「選定Factの検証完了後、最終B3の確定前に検証結果との整合を必ず確認すること。」「再選定上限は既存Trial設計の最大2回を維持する。上限到達時に品質条件を満たせなければ未成立として扱う。」「既存のResearch・Ledger・初回B3を再利用し、必要な確認パスだけを実行すること。」 (2)最終成果物=`er082_rlct_trial_01_{lib,run,aggregate,conform_check,test_01}.py`、`TRIAL_DESIGN_03.md`、`_conform_check_1a_01.json`、`_dryrun_07/` (3)証拠=test r1〜r7 PASS(25/25)、dry-run M2c/M3c COMPLETED・確認パスREQUIRED、147ファイルsha IDENTICAL、Opusレビュー_B R-B3「無限ループなし・誤確定防御あり」(lib.py:695-775) (4)一致=D1〜D9全項目実装、上限合算2回=原文「最大2回を維持」に忠実(Opus R-B2)。不一致=TRIAL_DESIGN_03 D1(ii)の「候補Ledger上でnotes付き」は実際はextra_note経由(Opus R-B4、文言修正要) (5)判定=ACCEPTED(文言修正は本委任で実施)。判定整合: 重大NG=なし / 主因=なし / 是正対象=D1(ii)文言 / STOP理由=なし / 提示=可。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。
**T-0補足**: 委任文は全文保存(要約禁止)。保存先=`docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_08.md`。stop_scope_check: `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 --run-dir er082_output/rlct_trial_01 --out er082_output/rlct_trial_01/_stop_scope_check_08.json`(有料実行の直前にも再実行、rc=3なら停止報告)。

## ユーザー指示(原文)
全文=`docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_DESIGN-FIX-1B_USER.md`(sha256 835f6972…、委任_07で保存済み)。本委任の直接根拠=§3「Stage 1aの訪日客統計について、案2・案1＋案2に新しい最終B3確認パスを追加実行する。既存のResearch・Ledger・初回B3を再利用し、必要な確認パスだけを実行すること。追加費用見込み：約JPY22。既存成果を破壊せず、修正前後のBrief・採用Fact・品質・費用の差を記録する。Coffeeについても同じ最終確認条件への適合を照合し、既に検証結果が反映済みなら不要な再生成を行わない。」§8「追加確認パスの費用を必ず計上する。既存の上限に収まらない見込みが生じた場合はSTOPする。」§6「AMBIGUOUSの断定が残っていないか」「Verifierの判定ばらつきによる問題と、案1・案2の方式固有の問題を区別する。」

## Opusレビュー_B(条件A、2026-10-17、総合判定GO)の反映指示(Fable採択分)
- **OP-1(R-B4、採択)**: `TRIAL_DESIGN_03.md` D1(ii)の文言を「Ledgerではタグ+notes(Researcherのambiguity欄があればそれを優先描画)、Verifierのverification_notesはextra_noteで渡す(確認対象AMBIGUOUSは600字、他の検証済みは300字で切り詰め)」に修正。コード変更なし。
- **OP-2(R-B9-1、採択・高)**: inbound M2/M3の実測Storylineが「【独立検証前の編集仮説】」ラベルで始まる(`inbound_tourism/M2/result.json`:62、M3:61)。Prompt文言は変更しない。評価手順へ反映: (a)ブラインド評価時はこのラベルを隠す(マスク)、(b)R-07人手判定ではこのラベルをFact固有の留保として数えない、(c)ラベル出現件数を方式別に「方式固有の欠陥候補」として記録する。これらを`STAGE_1A_EVAL_01.md`の末尾に「§追補(委任_08): 評価手順の是正」として追記し、1b評価にも適用する旨を`TRIAL_DESIGN_03.md`に1節追加。
- **OP-3(R-B5注記、採択)**: M2c↔M3cの確認B3は同じsel・ほぼ同じ判定を入力にした独立2回の呼出のため、両者のBrief差は「B3出力の揺らぎの標本」であり案1上限の効果ではない旨を、補正結果の記録と設計文書に明記。
- **OP-4(R-B2注記、採択)**: 未成立は`unmet`内訳(REJECTED_SELECTED/AMBIGUOUS_NOT_CONFIRMED)で分けて示す。「確定条件のもとでの成立率」は案2系のみの指標である旨を注記。上限到達時のBriefを成立扱いに戻さない。
- **OP-5(R-B6任意、採択・JPY0)**: `er082_rlct_trial_01_conform_check.py`に「最終選定=前回選定−REJECTEDの集合か(bool)」「Storyline変更あり(bool、sha比較)」の2列を追加し、`_conform_check_1a_02.json`を再出力(1a_01は残置)。
- **OP-6(R-B7、採択)**: 5記事集計での方式列の扱い=Coffee M2/M3(経路は新設計と同一、conform PASS)+inbound M2c/M3c+1b新設計。inbound旧M2/M3は「旧設計・参考」行のみ。注記文(Opus案)を`TRIAL_DESIGN_03.md`に記載。
- **OP-7(R-B1、採択)**: R-07人手判定は全方式同一基準。判定NGは「確定条件は満たしたが断定が残った」として別集計(Trial後のユーザー判断事項、新仕様は入れない)。
- Opus逐語保存: `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/OPUS_REVIEW_B_01_VERBATIM.md`。本文はOpus subagentのtranscript `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-ac34cea031256ef8b.jsonl` から、前回と同じ方式(`Glob` で `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\rlco\extract_*.py` または `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/`配下の既存extract scriptを探して流用。`.venv\Scripts\python.exe -I`で実行)で最終assistantテキスト(「## 総合判定: GO」で始まる本文)を抽出して保存。内容改変禁止、本文sha256を記録。抽出できなければ「抽出不可」と記録し、Fable委任文に含まれる上記反映指示のみで進める(推測で本文を創作しない)。
- Opus台帳: `docs/pm/OPUS_FINDINGS_LEDGER.md`へ OF-RLCT-RB-01(R-B1 測定に留める)〜OF-RLCT-RB-09(R-B9-1 ラベル問題)を追加、各行に状態(FABLE_DECIDED→IMPLEMENTED[本委任で反映したもの]/EVIDENCED[補正実行で証拠が出たもの])。

## 有料実行(Stage 1a補正)
1. 事前snapshot(委任_07と同じ方法)→`_stage1a_tree_sha_before_08.json`。
2. `.venv\Scripts\python.exe er082_rlct_trial_01_run.py --paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040 --stage 1a --out er082_output/rlct_trial_01 --article inbound_tourism --correct-from M2,M3 --other-spend-today-jpy <上記で確認した値>`(引数名は委任_07実装どおり。`--correct-source-root`既定が実測dirならば省略可。dry-runフラグを付けない)。実行は1回。rc≠0・外部停止・BudgetStopならば再起動せず報告。
3. 事後snapshot→`_stage1a_tree_sha_after_08.json`→IDENTICAL確認(M2c/M3cは新規dirなので比較対象の既存dir集合はbefore側の集合に限定)。
4. 結果記録: `inbound_tourism/M2c/result.json`, `M3c/result.json`から、確認パス発火(trigger/confirm_pass_count/b3_calls_after_initial)、新規選定Factと検証結果、最終選定Fact、Storyline(前後)、status(COMPLETED/UNRESOLVED+unmet)、`cost_correction_only`/`cost_production_equivalent`(LLM/web_search別)、`ambiguous_central`(機械)、contract(Fact Lock/RF、OPEN-407該当の有無)。
5. 修正前後差分: `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/STAGE_1A_CORRECTION_01.md`(新規)に、M2→M2c・M3→M3cの Brief/Storyline(全文、ラベルはそのまま掲載しマスクは評価時のみ)/採用Fact/verdict/費用(修正前・補正のみ・本番換算)/F05の扱い(留保が入ったか=R-07人手判定、全方式同一基準、ラベルは留保に数えない)/B3構成差(修正前M2→M2cを3段階で、OP-2のマスク適用)/M2c↔M3c差=B3揺らぎ標本の注記(OP-3)/未成立があればunmet内訳(OP-4)/削減率の再計算(inbound 案2・案1+2の本番換算をM2c/M3cに置換、M0/M0p/M0b基準で別表)/5記事集計での扱い(OP-6)。
6. aggregate再実行(実測root)→`aggregate.md`更新(M2c/M3cを「確認パス後」として表示、旧M2/M3は参考行)。
7. test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er082*_test_*.py"`(conform_check列追加後、25+件PASS)。

## 事前指定Read一覧
- `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/TRIAL_DESIGN_03.md` 全文(委任_07作成、修正対象)
- `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/STAGE_1A_EVAL_01.md`: Grep `^## ` で節一覧→末尾節のみRead(追補位置)
- `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/STAGE_1A_RESULTS_01.md`: Grep `inbound|削減率|本番換算` → 該当表のみ
- `er082_rlct_trial_01_run.py`: Grep `correct-from|other-spend-today|correct_source_root` → 引数定義行と当日支出計算部分
- `er082_rlct_trial_01_lib.py`: Grep `def _jst_date|class Budget|other_spend|daily_soft` → Budget.spent周辺(当日支出の自動計上範囲の確認)
- `er082_rlct_trial_01_conform_check.py` 全文
- `er082_output/rlct_trial_01/inbound_tourism/M2/result.json`:1-90、`M3/result.json`:1-90
- `docs/pm/RESULT_PACKET_RLCT7.md` 全文
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `OF-RLCT-R-16` → 直後に追加

## 事前指定Grep一覧+追記位置・更新位置の手順
- `OPEN_ITEMS.md`: Grep `^\| OPEN-410` → Status末尾に「委任_08: Opus条件A GO(OPUS_REVIEW_B_01_VERBATIM)、inbound M2c/M3c有料補正実行(実測JPY<値>)、結果=STAGE_1A_CORRECTION_01.md、1bは別日」追記。Grep `^\| OPEN-403` → 同様に1行追記。
- `DECISION_LOG.md`: 末尾に下記SSOT追記文。
- `docs/pm/REPORT_LEDGER.md`: Grep `RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01` → 最新行の後に委任_08行。
- `docs/pm/ACTIVE_TASK.md`: 冒頭固定ヘッダを委任_08で上書き(旧ヘッダは保持節へ)。QDC行に当日費用=284.1+本委任実測。
- `docs/pm/USER_DECISION_REGISTER_01.md`: 変更なし(#107判断済みのまま)。ただしR-07判定でM2c/M3cに断定が残った場合は「#108(候補・Trial後)」として候補行を追加せず、RESULT_PACKETの判断候補に書く(ラベル付与はFable)。

## 実行コマンド全文
1. `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_08.md --json-out docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_08.md_check.json`
2. `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 --run-dir er082_output/rlct_trial_01 --out er082_output/rlct_trial_01/_stop_scope_check_08.json`
3. Opus逐語抽出: `.venv\Scripts\python.exe -I <extract script> --jsonl "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-ac34cea031256ef8b.jsonl" --out docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/OPUS_REVIEW_B_01_VERBATIM.md`(既存scriptの引数名に合わせる)
4. `.venv\Scripts\python.exe er082_rlct_trial_01_conform_check.py --root er082_output/rlct_trial_01 --out er082_output/rlct_trial_01/_conform_check_1a_02.json`
5. snapshot before(委任_07手順3と同じ、ファイル名`_08`)
6. 有料: `.venv\Scripts\python.exe er082_rlct_trial_01_run.py --paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040 --stage 1a --out er082_output/rlct_trial_01 --article inbound_tourism --correct-from M2,M3 --other-spend-today-jpy <確認値>`
7. snapshot after + IDENTICAL判定(before集合限定)
8. `.venv\Scripts\python.exe er082_rlct_trial_01_aggregate.py --root er082_output/rlct_trial_01 --out er082_output/rlct_trial_01/aggregate.md`(引数は既存どおり)
9. `.venv\Scripts\python.exe run_project_regression.py --pattern "er082*_test_*.py"`
10. secret scan(委任_07と同じscript・引数、hits=0必須)
11. Git: 明示add→commit→`git -C C:\Users\tensh\eigo-radio-crbn pull --ff-only origin main; git -C C:\Users\tensh\eigo-radio-crbn merge --ff-only work/post-merge-01; git -C C:\Users\tensh\eigo-radio-crbn push origin main`→`git -C C:\Users\tensh\eigo-radio merge --ff-only origin/main`。

## SSOT追記文
- DECISION_LOG.md(末尾): 「2026-10-17 FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_08: Opus独立レビュー_B(11-3条件A、確認パス実装)=GO(コード修正なし。評価手順へR-B1/R-B2/R-B5/R-B7/R-B9-1を反映、D1(ii)文言修正)。Fable照合=Claude案と一致・承認範囲内・新原則なし→進行。Stage 1a補正: inbound_tourism M2c/M3c(確認パスのみ追加実行、初回B3・round0判定を再利用)実測JPY<値>(確認B3<値>+新規検証<値>)、status=<COMPLETED|UNRESOLVED(unmet)>、F05の扱い=<R-07判定結果>。Coffee M2/M3は適合PASS(選定Fact全VERIFIED、経路は新設計と同一)で再生成なし。既存1a成果sha不変。「【独立検証前の編集仮説】」ラベル(inbound M2/M3 Storyline冒頭)は方式固有の欠陥候補として記録・評価時マスク(Prompt不変更)。Trial累計JPY<223.7+値>/1,040。1bは2026-10-18 JST以降。Production変更なし。」
- OPEN_ITEMS.md: OPEN-410/403への追記(上記)。新規: 「| OPEN-411 | **RLCT-B3-UNVERIFIED-LABEL-IN-STORYLINE-01 [OPEN・非Blocking・Trial観測・改修なし]**(2026-10-17起票、Opusレビュー_B R-B9-1): 案2系(allow_unverified)でB3がStoryline冒頭に「【独立検証前の編集仮説】」ラベルを付与(inbound M2/M3実測)。Writerテーマ文へ流入し得る方式固有の欠陥候補。Trial内ではPrompt不変更・評価時マスク・件数記録のみ。案2を採用する場合の除去はProduction挙動変更=ユーザー判断。 | 区分: POST_USER_VALIDATION | 棚卸し: 未実施 |」

## Git(明示add対象・コミットメッセージ・trailer)
- add: `er082_rlct_trial_01_conform_check.py`, `er082_rlct_trial_01_test_01.py`(列追加testがあれば), `er082_output/rlct_trial_01/_conform_check_1a_02.json`, `er082_output/rlct_trial_01/inbound_tourism/M2c/**`と`M3c/**`(result.json・research_ledger・storyline_b3・_work内のb3/verify json。巨大ファイルがあれば除外し理由記載), `er082_output/rlct_trial_01/aggregate.md`, `er082_output/rlct_trial_01/raw_usage_log.jsonl`(既にtracked済みなら), `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/{OPUS_REVIEW_B_01_VERBATIM.md,TRIAL_DESIGN_03.md,STAGE_1A_EVAL_01.md,STAGE_1A_CORRECTION_01.md}`, `docs/pm/delegation_log/2026-10-17_..._委任_08.md`(+_check.json), `OPEN_ITEMS.md`, `DECISION_LOG.md`, `docs/pm/OPUS_FINDINGS_LEDGER.md`, `docs/pm/REPORT_LEDGER.md`。無関係差分はstageしない。SSOT編集権あり(CURRENT_SPEC.md/PM_GOVERNANCE.mdは編集しない)。
- commit message: `FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_08: Opus条件Aレビュー_B(GO)逐語保存+評価手順是正(ラベルマスク/R-07基準/未成立内訳/M2c↔M3c注記)+Stage 1a補正 inbound M2c/M3c 確認パス有料実行(実測JPY<値>)+修正前後差分STAGE_1A_CORRECTION_01+conform_check列追加+SSOT(OPEN-411、1bは別日)`
- trailer: `Managed-ID: FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_RLCT8.md`(20行目安): T-0/stop_scope/Opus逐語保存(path・sha・抽出可否)/OP-1〜OP-7の反映箇所/有料実行: コマンド・rc・実測費用(M2c/M3c別、確認B3/新規検証/web_search別、本番換算)・`--other-spend-today-jpy`に使った値と根拠・harnessガードの当日累計表示値/M2c・M3cの結果(status・trigger・新規Fact・最終選定・F05の留保有無[R-07人手判定、ラベル除外]・ambiguous_central・contract・ラベル出現)/修正前後差分の要点(構成差3段階、削減率再計算: inbound 案2・案1+2 対M0/M0p)/既存1a成果IDENTICAL/test件数/aggregate更新/secret hits/commit hash・push/Trial累計・当日累計/(1)既存仕様整合 (2)未承認機能既定値 (3)失敗終了時の最終成果物(UNRESOLVEDならその中身) (4)撤去・残置/`判定整合:`行/判断候補(A/B/C/D区分。M2c/M3cで断定残存ならD候補として記載、ラベル付与はFable)/QDC(次の一手=1b別日: 順序streaming→openai→central、M0b含む、`--other-spend-today-jpy`当日値、1b上限493、任意A inbound/streamingは1b後)。

## Fable自己チェック(送信前)
Read行範囲あり/追記位置あり/コマンド実値あり(other-spendのみ確認値)/禁止・費用上限T-3定型あり/並行衝突なし/Opus条件A=レビュー済みGO明記/時間・直列理由あり/前委任QDC・受入記録あり/費用日次行あり。

## (旧)要約保存分(T-0逸脱記録)
## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_08(Opus条件Aレビュー逐語保存+評価手順の是正反映[JPY0]→Stage 1a補正の有料実行[inbound_tourism M2c/M3c、確認パスのみ]→修正前後差分記録+R-07人手判定→SSOT→commit)。Stage 1bは本委任で**実行しない**(別日2026-10-18 JST以降)。並行タスク衝突: なし(BAPEは#106待ち、S3Wは試聴待ち)。commitを伴う作業は本委任のみ。

## 性質/到達上限Status/禁止事項
- 性質: ユーザー承認済みTrial(#104費用承認・#107設計是正(b))の承認範囲内実行。到達上限Status=`STAGE_1A_CORRECTED_PENDING_FABLE`。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDに到達しない。
- Fable判定(11-3): Opusレビュー_B=GO(コード修正なし、評価手順・注記の反映のみ)。Claude案と一致、承認済み仕様内、新Product原則なし → Fable判断で次工程(本委任)へ進む。
- 費用上限(T-3定型): 「上限¥60(Guardrail、本委任の有料部分=inbound M2c/M3cの確認B3 2回≒22円+新規Fact検証が入った場合の上積み)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」 harnessの実費ガード(1a上限493、累計1,040、日次soft 1,000)はそのまま有効。`--paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040`、`--other-spend-today-jpy 71.3`(本日のRLCT外支出=SJS4 41.6+S3W 18.5+その他≒71.3。harnessがraw_usage_logから当日RLCT支出212.80+10.88を自動計上する場合は二重計上しないよう既存実装を確認し、使った値と根拠をRESULT_PACKETに書く)。
- 禁止: Stage 1b・任意Aの実行禁止。Production runner/Prompt/Style変更禁止。既存1a成果(`coffee_prices/*`, `inbound_tourism/M0,M0b,M0p,M1,M2,M3`)の変更・削除禁止(sha前後IDENTICAL必須)。Research再生成禁止。Coffee M2/M3の再生成禁止(conform PASS)。B3 Prompt文言(lib.py:504の`UNVERIFIED_PHRASE`等)の変更禁止(1aとの条件維持、Opus R-B9-1)。有料runの再起動禁止(26節、rc≠0・外部停止ならSTOP報告)。git add -A/-u/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。
- 時間見込み: 全体約60分。直列(有料実行は1回、同一出力dir)。
- 費用/日次: 当日(JST 2026-10-17)既使用約JPY284.1(出典: ACTIVE_TASK.md L4)/残約715.9/本委任見積JPY22(期待)〜60(上限)/改善見込み高/承認区分: C(承認済みscope内。#104 1a上限493の残280.2、#107 §3「追加費用見込み：約JPY22」)。
- 前委任(委任_07)QDC記録・受入記録: ACCEPTED(文言修正は本委任で実施)。判定整合: 重大NG=なし / 主因=なし / 是正対象=D1(ii)文言 / STOP理由=なし / 提示=可。

## ユーザー指示(原文)
全文=`docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_DESIGN-FIX-1B_USER.md`。本委任の直接根拠=§3「Stage 1aの訪日客統計について、案2・案1＋案2に新しい最終B3確認パスを追加実行する。既存のResearch・Ledger・初回B3を再利用し、必要な確認パスだけを実行すること。追加費用見込み：約JPY22。既存成果を破壊せず、修正前後のBrief・採用Fact・品質・費用の差を記録する。Coffeeについても同じ最終確認条件への適合を照合し、既に検証結果が反映済みなら不要な再生成を行わない。」§8「追加確認パスの費用を必ず計上する。既存の上限に収まらない見込みが生じた場合はSTOPする。」§6「AMBIGUOUSの断定が残っていないか」「Verifierの判定ばらつきによる問題と、案1・案2の方式固有の問題を区別する。」

## Opusレビュー_B(条件A、2026-10-17、総合判定GO)の反映指示(Fable採択分)
- OP-1(R-B4): TRIAL_DESIGN_03.md D1(ii)の文言を「Ledgerではタグ+notes(Researcherのambiguity欄があればそれを優先描画)、Verifierのverification_notesはextra_noteで渡す(確認対象AMBIGUOUSは600字、他の検証済みは300字で切り詰め)」に修正。コード変更なし。
- OP-2(R-B9-1、高): inbound M2/M3の実測Storylineが「【独立検証前の編集仮説】」ラベルで始まる(inbound_tourism/M2/result.json:62、M3:61)。Prompt文言は変更しない。評価手順へ反映: (a)ブラインド評価時はラベルをマスク、(b)R-07人手判定ではラベルをFact固有の留保として数えない、(c)ラベル出現件数を方式別に「方式固有の欠陥候補」として記録。STAGE_1A_EVAL_01.md末尾に「§追補(委任_08): 評価手順の是正」として追記し、1b評価にも適用する旨をTRIAL_DESIGN_03.mdに1節追加。
- OP-3(R-B5): M2c↔M3cの確認B3は同じsel・ほぼ同じ判定を入力にした独立2回の呼出のため、両者のBrief差は「B3出力の揺らぎの標本」であり案1上限の効果ではない旨を、補正結果の記録と設計文書に明記。
- OP-4(R-B2): 未成立はunmet内訳(REJECTED_SELECTED/AMBIGUOUS_NOT_CONFIRMED)で分けて示す。「確定条件のもとでの成立率」は案2系のみの指標である旨を注記。上限到達時のBriefを成立扱いに戻さない。
- OP-5(R-B6、JPY0): conform_check.pyに「最終選定=前回選定−REJECTEDの集合か(bool)」「Storyline変更あり(bool、sha比較)」の2列を追加し、_conform_check_1a_02.jsonを再出力(1a_01は残置)。
- OP-6(R-B7): 5記事集計での方式列=Coffee M2/M3(経路は新設計と同一、conform PASS)+inbound M2c/M3c+1b新設計。inbound旧M2/M3は「旧設計・参考」行のみ。注記文をTRIAL_DESIGN_03.mdに記載。
- OP-7(R-B1): R-07人手判定は全方式同一基準。判定NGは「確定条件は満たしたが断定が残った」として別集計(Trial後のユーザー判断事項、新仕様は入れない)。
- Opus逐語保存: docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/OPUS_REVIEW_B_01_VERBATIM.md(subagent transcript agent-ac34cea031256ef8b.jsonlから既存extract方式で抽出、内容改変禁止、sha256記録、抽出不可なら「抽出不可」と記録)。
- Opus台帳: docs/pm/OPUS_FINDINGS_LEDGER.mdへ OF-RLCT-RB-01(R-B1)〜OF-RLCT-RB-09(R-B9-1)を追加、各行に状態(FABLE_DECIDED→IMPLEMENTED/EVIDENCED)。

## 有料実行(Stage 1a補正)
1. 事前snapshot→`_stage1a_tree_sha_before_08.json`。
2. `.venv\Scripts\python.exe er082_rlct_trial_01_run.py --paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040 --stage 1a --out er082_output/rlct_trial_01 --article inbound_tourism --correct-from M2,M3 --other-spend-today-jpy <確認値>` 実行は1回。rc≠0・外部停止・BudgetStopならば再起動せず報告。
3. 事後snapshot→`_stage1a_tree_sha_after_08.json`→IDENTICAL確認(before集合限定)。
4. 結果記録: M2c/M3c result.jsonから、確認パス発火、新規選定Factと検証結果、最終選定Fact、Storyline(前後)、status(COMPLETED/UNRESOLVED+unmet)、cost_correction_only/cost_production_equivalent、ambiguous_central、contract。
5. 修正前後差分: STAGE_1A_CORRECTION_01.md(新規)に、M2→M2c・M3→M3cのBrief/Storyline(全文)/採用Fact/verdict/費用/F05の扱い(R-07人手判定、ラベルは留保に数えない)/B3構成差(3段階、OP-2マスク)/M2c↔M3c差=B3揺らぎ標本の注記(OP-3)/未成立のunmet内訳(OP-4)/削減率の再計算(M0/M0p/M0b基準で別表)/5記事集計での扱い(OP-6)。
6. aggregate再実行→aggregate.md更新(M2c/M3cを「確認パス後」、旧M2/M3は参考行)。
7. test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er082*_test_*.py"`。

## 事前指定Read一覧 / Grep一覧 / SSOT追記文 / Git / 報告(RESULT_PACKET項目)
(原委任文の当該節に従う。要点: OPEN_ITEMS.md OPEN-410/403追記・OPEN-411新規[RLCT-B3-UNVERIFIED-LABEL-IN-STORYLINE-01、OPEN・非Blocking・Trial観測・改修なし、POST_USER_VALIDATION]、DECISION_LOG.md末尾追記、REPORT_LEDGER.md委任_08行、ACTIVE_TASK.md上書き、明示addのみ、commit message先頭=`FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_08: ...`、trailer `Managed-ID: FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01`、報告先=docs/pm/RESULT_PACKET_RLCT8.md。)

注記: 本ファイルは受領した委任文のうち実行手順・禁止・承認範囲・反映指示を保存したもの。SSOT追記文および報告項目の細目は受領原文(会話ログ)に基づく。
