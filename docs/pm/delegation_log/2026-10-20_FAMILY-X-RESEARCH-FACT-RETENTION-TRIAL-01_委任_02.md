# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_02(設計v02[基準(a')採用・検索込み比較腕の追加・S-check廃止]→方式比較本走[検索なし全方式×3題材×2 sample+検索込みE0/A/D×2 sample]→創作照合→Ledger→B3接続確認→Closeout[ユーザー§7の8項目順]+SSOT[OPEN-427/REGISTER #127]+付帯: `daily_dev_cost_01.py`のdry-run stub計上バグ修正)。2026-10-20。
並行タスク衝突確認: 並行委任なし(PLWP1完了 de807485c、XRFR 委任_01完了 179fbd01c)。SSOT編集権: あり(`OPEN_ITEMS.md`新規OPEN-427、`DECISION_LOG.md`末尾、`docs/pm/USER_DECISION_REGISTER_01.md`新規#127、`docs/pm/REPORT_LEDGER.md`)。`CURRENT_SPEC.md`は編集しない(Production非変更)。

## Fableの照合結果と決定(前提)
- 委任_01所見: 検索なし・同一出典ではE0(現行Prompt)の重要Fact保持は9/12=0.75で、Production(検索込み)の0/6を**部分再現にとどまる**。脱落は全て抽出・構造化段階、検証は検知せず。差の主因候補=検索tool統合そのもの(素材量119K tok・断片化・推論配分)。費用構造: Production Research+Ledger検証JPY36.1/記事のうち検索20回分JPY32.0(89%)。
- **決定1(基準)**: 事前登録基準(a)はE0=0.75では達成不能のため、候補実走前に**(a')「KEY保持≥0.917(11/12)またはE0比+0.17以上(2観測以上)」**へ改訂(設計書§9にv02として理由・日時を記録。他の指標・閾値は不変、全方式に同一適用)。
- **決定2(Production忠実性)**: 検索なし比較だけでは採否判断に足りないため、**検索込み比較腕**を追加: Production経路と同一の`run_researcher_for_topic`(web_search tool固定)でE0/A/D(A=Prompt第5・6観点、D=A+検証1行)を中東題材で各2 sample(計6 run、約JPY27/run≈JPY162)。採点: 各runが実際に引用した出典を無料HTTPで取得し、「空港攻撃の主体(Ansar Allah)」「紅海・海上交易路/イエメン戦況の文脈」が**その出典に明示されている場合に**Ledger draftへ保持されたか(M-A1/M-B3相当)を出典逐語照合で判定(gold_02との重なりがある出典はgold採点も併用)。検索回数(`web_search_call_count`)・token・費用・時間を記録し、**Prompt変更で検索回数が増えないか**を主要コスト指標にする。S-check(約54)は本腕に吸収し廃止。
- **決定3(構成・費用)**: 検索なし=E0/A/B/C/D/E×{mey,muse,coffee}×2 sample(約JPY39)+検索込み6 run(約162)+Ledger→B3接続(候補最良1方式のLedgerで`er083_c1_positive_control_01_run.py`系のB3呼出2回、約15)=約JPY216。Cap ¥230。案件合算(委任_01 4.245+216)≈220≤300→承認区分C(ユーザー費用承認不要)。当日実費累計約314.5+PLWP1 28.6=約343、+230でも1,000内。
- **決定4(Opus)**: 任意レビューは行わない(事前登録済み・今日の枠はOpus_Jで使用)。Production採用提案時は条件C必須(別委任)。
- 禁止: Production Prompt/schema/Researcher/Verifier/B3/Writerの変更。追加Web検索は**検索込み腕のProduction経路内で発生するもののみ**(harness側から別途検索しない)。架空Fact・創作(採点は出典逐語照合、未判定が残れば最終ラベル不可)。結果を見てからの基準変更(v02は実走前commit)。`git add -A/-u/-f`・amend・rebase・force push・stash。有料runの再起動は、harness側原因で費用重複が無いことを確認できた場合に限り1回まで(開示必須)。
- 修正範囲の線引き(11-8): 付帯の`docs/pm/tools/daily_dev_cost_01.py`修正=PMツールの不具合(`usage_source=SYNTHETIC_DRYRUN_STUB`行を実費に計上)の是正で範囲内。Production非関与。

## 性質/到達上限Status/禁止事項
- 性質: Trial本走(Trial専用経路+Production関数の読み取り専用呼出)+Closeout+PMツール修正。
- 到達上限Status: `XRFR_TRIAL_CLOSEOUT_PENDING_FABLE`(方式別のVALIDATED候補/REJECTED/判断候補はevalが機械判定、最終ラベルはFable。Production採用はユーザーのみ)。
- 費用/日次: 当日実費約343(出典RESULT_PACKET_XRFR1.md+PLWP1)/本委任見積JPY約216/承認区分C。
- T-3: 上限¥230(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。**検索込み腕で1 runの検索回数がProduction実績(20回)の2倍を超える等の異常はその時点でSTOP**。案件合算300円超見込みでSTOP(7-7)。
- 時間見込み: 全体4〜5h(v02 20分/検索なし本走30分[並列]/検索込み6 run 40分[並列2〜3]/出典取得・採点60分/B3接続20分/Closeout 60分/SSOT・ツール修正・報告40分)。並列化: 検索なしと検索込みは独立に並列。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**保存は打ち直さずsession JSONLから抽出**(管理ID行に`FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_02`を含む最初のAgent prompt。index走査で特定できなければJSONL行を直接抽出)→`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_02.md`。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): 本委任はTTSを伴わない。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 定型文は上記に記載済み。

## ユーザー指示(原文、該当部抜粋。全文=`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_USER.md`、sha256 3314feb6…)
> 単一Promptへの決め打ちは禁止。異なる改善アプローチを比較し、**1回のTrialで採否判断に足る結果を取得できるよう設計すること。**
> **改善によって無駄なWeb検索やLLM呼出が増える方式は、原則として採用候補にしない。** …**コスト測定は、共通条件・同一出典で比較すること。** 1. 既に取得した出典を再利用できる場合、追加Web検索を行わない。2. Promptや構造化方法の改善だけで解決できるなら、検索工程を増やさない。… 5. Trial費用と量産時の恒常費用を区別する。6. … **70円／記事セット**という全体原価目標への影響も示す。
> **品質が同等なら、追加検索・追加LLM呼出が少なく、安価で速い方式を優先する。** … 重要なコスト増加を伴う方式は、自動的にProduction採用候補としない。
> ## 6. 受入条件 - 中東記事の主体・背景に関する欠落が改善される。- 出典にない事実・動機・因果関係を作らない。- 別題材でも情報保持の改善が確認できる。- Ledgerへの登録とB3からの利用可能性が確認できる。- 現行比の品質・検索回数・LLM費用・処理時間が比較できる。- 無駄な検索・再検証の増加がない、または必要性と削減不能な理由が説明されている。- Productionの正式経路には未承認変更を加えない。
> ## 7. 最終報告 1. **最も推奨する改善方式と、その理由** 2. 現行方式と改善候補の品質比較 3. **Web検索回数・LLM呼出・量産単価・処理時間の比較** 4. 中東記事での欠落改善結果（Before／Afterの具体的Fact） 5. 別記事での一般化結果 6. Ledger→B3接続確認 7. 未解決問題・リスク 8. Production採用に必要なユーザー判断
> 改善候補はTrial終了時に `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED` へ分類する。`VALIDATED` であっても正式Productionへ自動配線しない。

## 作業
W1. 設計v02: `TRIAL_DESIGN_01.md`に§9 v02(決定1〜3の反映: 基準(a')、検索込み腕の定義・採点規則・異常STOP条件、S-check廃止、費用表更新)を追記し、`design_matrix_01.json`/判定閾値jsonを同期。**実走前にcommit**。
W2. 検索なし本走: E0(既存2 sampleを再利用、再実行しない)+A/B/C/D/E×{mey,muse,coffee}×2 sample(`_run.py`、`--budget-jpy 45`)。eval: KEY/SEC保持率、CTRL、不要Fact数、創作フラグ→出典逐語照合(全件SUPPORTED/UNSUPPORTED/未判定)、token・費用・時間。
W3. 検索込み腕: Trial専用wrapper(`er085_research_fact_retention_trial_01_search_arm.py`新規)から`er012_e_family_entertainment_two_level_runner_01.run_researcher_for_topic`を**Production既定と同一引数**で呼ぶ(E0=Prompt不変、A/D=Prompt差分のみ、出力先はTrial dir、Production run dir・Ledgerへ書かない。検証はDのみ`run_verification_for_topic`も呼ぶ[独立再検索が発生するため費用に含める])。各run 2 sample、`--budget-jpy 170`。各runの引用出典URLを抽出→無料HTTP取得→主体・文脈の明示有無を逐語照合→保持判定。検索回数・token・費用・時間を表に。
W4. Ledger→B3接続: 検索なし/検索込みの結果で最良1方式のmey Ledger draftをTrial用Ledger(Production schema検証PASS)に変換し、`er083_c1_positive_control_01_run.py`系で現行B3を2 call(`--budget-jpy 15`)→主体Fact(M-A1相当)が採用されるか。
W5. Closeout `TRIAL_CLOSEOUT_01.md`(ユーザー§7の8項目順): 1推奨方式と理由/2品質比較表(方式×題材×指標、検索なし・検索込み別)/3コスト比較表(検索回数・追加LLM呼出・token・1記事恒常費用・70円目標への%・処理時間)/4中東Before/After(具体Fact文の対比、出典逐語)/5一般化(muse/coffee)/6Ledger→B3/7未解決・リスク(検索なし/込みの乖離、検索出典揺れ、gold限界、Production同等性)/8Production採用に必要なユーザー判断(採用方式・配線方式[共用Prompt builder→Family X限定経路か全Family]・条件Cレビュー)。方式別Status候補。
W6. 付帯: `docs/pm/tools/daily_dev_cost_01.py`で`usage_source`が`SYNTHETIC_DRYRUN_STUB`(およびdry-run系)の行を実費から除外(別枠で件数・金額を表示)、`daily_dev_cost_01_test.py`に正負例を追加、修正前後の当日値を記録。
W7. SSOT: OPEN-427(新規: 本Trial統合Status・費用・方式別候補Status・Production非変更)、DECISION_LOG末尾(v02決定・結果・Fable決定)、REGISTER #127(判断済み: Trial実施承認。Production採用は別判断)、REPORT_LEDGER。OPEN-425へ「是正Trial=OPEN-427」参照1行。ACTIVE_TASK先頭ヘッダ。

## 事前指定Read一覧
- `docs/research/FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01/TRIAL_DESIGN_01.md`・`design_matrix_01.json`・`gold_02.json`・`BASELINE_REPRO_01.md`・`adjudication_01.json`(全体)
- `docs/pm/RESULT_PACKET_XRFR1.md`(全体)
- `er085_research_fact_retention_trial_01_{lib,run,eval,test_01,cost_reconcile}.py`(全体)
- `er012_e_family_entertainment_two_level_runner_01.py`:175-230(Researcher/検証の呼出シグネチャ・出力先)
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `def build_researcher_prompt|def build_verification_prompt|web_search`→該当範囲
- `er083_c1_positive_control_01_run.py`: Grep `def |ledger|b3`(B3呼出の再利用点)
- `docs/pm/tools/daily_dev_cost_01.py`(全体、小)、`daily_dev_cost_01_test.py`(全体)
- `OPEN_ITEMS.md`: Grep `^- OPEN-42[5-7]`、`docs/pm/USER_DECISION_REGISTER_01.md`: Grep `^- #12[5-7]`(末尾番号確認)

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep `web_search_call_count|usage|response_id` in `er085_research_fact_retention_trial_01_lib.py`・`er012_e_family_entertainment_two_level_runner_01.py`→検索回数・tokenの記録点。
- Grep `usage_source|SYNTHETIC` in `docs/pm/tools/daily_dev_cost_01.py`・`er005_cost_logger.py`→除外実装点。
- `OPEN_ITEMS.md`: Grep `^- OPEN-426`→直後にOPEN-427。Grep `^- OPEN-425`→行末に参照1行。REGISTER: Grep `^- #126`→直後に#127。DECISION_LOG末尾。REPORT_LEDGER: Grep `FAMILY-X-RESEARCH-FACT-RETENTION`→更新。
- `docs/pm/ACTIVE_TASK.md`先頭ヘッダ5行以内。

## 実行コマンド全文
- 抽出/T-0: `.venv\Scripts\python.exe docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 0 --out docs\pm\delegation_log\_extract_try_0.md`(index走査) → `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_02.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_02.md_check.json`
- test(実走前): `.venv\Scripts\python.exe -m pytest er085_research_fact_retention_trial_01_test_01.py docs\pm\tools\daily_dev_cost_01_test.py -q`
- 検索なし本走: `.venv\Scripts\python.exe er085_research_fact_retention_trial_01_run.py --design docs\research\FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01\design_matrix_01.json --variants A,B,C,D,E --topics mey,muse,coffee --samples 2 --out er085_output\research_fact_retention_trial_01 --budget-jpy 45`(先に`--dry-run`)
- 検索込み腕: `.venv\Scripts\python.exe er085_research_fact_retention_trial_01_search_arm.py --variants E0,A,D --topic mey --samples 2 --out er085_output\research_fact_retention_trial_01\search_arm --budget-jpy 170`(先に`--dry-run`、実引数は実装に合わせ記録)
- 出典取得: `curl.exe -L -s -A "Mozilla/5.0" -o C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\xrfr2\src_01.html "<URL>"`
- eval: `.venv\Scripts\python.exe er085_research_fact_retention_trial_01_eval.py --out er085_output\research_fact_retention_trial_01 --report docs\research\FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01\COMPARISON_RESULT_01.md`
- B3接続: `.venv\Scripts\python.exe er083_c1_positive_control_01_run.py --design docs\research\FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01\b3_link_matrix_01.json --out er085_output\research_fact_retention_trial_01\b3_link --budget-jpy 15 --paid-run-approved-by-fable "Fable 2026-10-20 XRFR 委任_02 Cap230"`(matrixは本委任で作成、実引数は実装に合わせる)
- 費用: `.venv\Scripts\python.exe docs\pm\tools\daily_dev_cost_01.py --date 2026-10-20`(修正前後)
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain`→明示add→commit→push(origin/main HEADへff-only、`git log --oneline -3 origin/main`で到達確認)

## SSOT追記文
W7のとおり(実値で埋める。方式別Statusは「eval機械判定=<X>(Fable最終ラベル待ち)」)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1(実走前): 設計v02・matrix・閾値json・search_arm.py・test・委任文。msg: `FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_02: 設計v02(基準a'・検索込み腕E0/A/D・S-check廃止)+search_arm harness+test(API 0)`
- commit 2: 本走結果(検索なし/検索込み)・出典照合・eval・B3接続(出典全文はcommitしない)。msg: `… 委任_02: 方式比較本走(検索なし<n> call+検索込み<n> run、実費JPY<v>)+創作照合+Ledger→B3接続`
- commit 3: Closeout+`daily_dev_cost_01.py`修正+test。msg: `… 委任_02: Closeout(推奨方式=<X>、eval判定)+daily_dev_cost dry-run stub除外修正`
- commit 4: SSOT。msg: `… 委任_02: SSOT(OPEN-427/425参照/DECISION_LOG/REGISTER #127/REPORT_LEDGER)`
- trailer: `Delegation: FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01/委任_02`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_XRFR2.md`: (1)T-0 (2)v02の変更点 (3)検索なし結果表(方式×題材: KEY/SEC/CTRL/不要Fact/創作/費用/時間) (4)検索込み結果表(方式×sample: 検索回数/token/費用/時間/主体・文脈保持/引用出典) (5)創作照合(UNSUPPORTED件数、未判定件数) (6)B3接続結果 (7)方式別候補Statusと推奨方式・理由(コスト優先原則の適用) (8)Before/Afterの具体Fact文 (9)費用(本委任実費・案件合算・当日累計[修正後ツール値]) (10)daily_dev_cost修正の差分とtest (11)SSOT差分 (12)Git (13)判断候補(ラベル無し。Production採用に必要な判断・配線方式の選択肢) (14)再開の有無 (15)一覧外Read理由。判定整合行1行。