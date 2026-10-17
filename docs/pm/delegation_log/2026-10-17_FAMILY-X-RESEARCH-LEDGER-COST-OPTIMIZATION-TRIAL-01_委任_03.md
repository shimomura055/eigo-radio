# 委任文(DELEGATION_STANDARD_TEMPLATE準拠)

## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_03(Opus条件Aレビューの逐語保存+Fable決定の設計書反映[TRIAL_DESIGN_02]+費用見積改訂[COST_ESTIMATE_02]+Opus台帳+SSOT+commit。JPY0・実装なし)。本日=2026-10-17(JST)。前委任=委任_02(commit `b8a0032bc`)。

## 性質/到達上限Status/禁止事項
- 性質: 設計書・見積の改訂と記録。harness実装(CP1)は本委任では行わない(次委任)。有料実行はユーザー費用承認(#104)後。
- 到達上限Status: `TRIAL_DESIGN_REVISED_COST_APPROVAL_PENDING`。
- 禁止: Production code・Prompt変更/`CURRENT_SPEC.md`編集/有料API/Opusレビュー本文の改変(逐語保存)/Fable決定の変更(下記「Fable決定」をそのまま反映。異論があれば反映はしたうえでRESULT_PACKETに意見を書く)/`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f/無関係dirty差分のadd。
- 並行タスク: S3W 委任_01(git書込みなし。`er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3_support_01/`・`user_test/coffee_fxpw_e2e_01_s3/`・`er019_coffee_s3_*.py`・`docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-*`)。これらを読まない・addしない。commitは本委任のみ。
- Opus Gate(11-3): 条件A実施済み(本委任で反映)。再レビューは内容が変わった場合のみ(本委任の改訂はOpus指摘の反映であり再レビュー不要。Fable判断)。
- 時間見込み: 60分、単独。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3: 費用上限JPY0のためCap定型は該当なし。
T-0補足: 本委任文は**全文**を `docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_03.md` へ保存(要約・path省略不可)。`python`shimは壊れている(rc=49)ので `.venv\Scripts\python.exe` を使う。

## ユーザー指示(原文)
保存済み: `docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_USER.md`(sha256 e6bc729b…)。

## Opusレビュー原文の取得(逐語)
- Opus subagent transcript: `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-a28bc9701cb8c8f22.jsonl`(全文Read禁止)。scratchpad `rlco\extract_rlct_02.py` 系の抽出scriptを流用し、`## Opus独立技術レビュー結果: RLCT Trial設計` で始まり `OF-RLCT-R-16` と `Fableがユーザーへ上げるべき判断事項` を含む最長文字列を `.venv\Scripts\python.exe -I` で抽出 → `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/OPUS_REVIEW_A_01_VERBATIM.md`(先頭1行の注記のみ付加、本文無改変、sha256を記録)。抽出できなければSTOP報告(要約で代用しない)。

## Fable決定(OF-RLCT-R-01〜R-16への採否。設計書v2にこのまま反映する)
- R-01 採用: Trial専用の検証関数を複製(model/reasoning/tools/schema/developer messageは既存と同一、Promptのみ引数、raw responseから呼出単位ログ[action.type/queries/順序/URL]を保存)。M0'/M1/M2/M3の新規検証は全て同関数経由。**monkey-patch禁止**を設計書に明記。
- R-02 採用: 予算guardはweb_search費用込み(`compute_stage_cost_breakdown`と同算式)を呼出ごとに判定、承認額超過見込みでSTOP。プロセス開始時に `cl.install("er082_output/rlct_trial_01/raw_usage_log.jsonl")`。dry-runで「web_search 1回が費用計上される」test。
- R-03 採用: 再利用入力(draft/ledger/B3)は `er082_output/rlct_trial_01/<article>/<method>/` へ複製してから処理。sha不変チェックの対象を「Productionコード+再利用する既存成果物」に拡大(実行前後)。RF実行時(Stage 3)は `root=` にer082配下を明示。
- R-04 採用: M0'(同日・上限なし再検証)をStage 1へ(Coffee・inbound・streaming)。openai/centralはM1の呼出ログで上限非拘束を確認できればM1をM0'代替、拘束した場合のみStage 2で追加。判定基準=M0'(M0とM0'の差=Web更新+ばらつき、M0'とM1の差=上限効果)。
- R-05 採用: 費用表を①Trial追加支出(承認管理用)と②本番換算費用(Research+検証+B3+再選定、共有・再利用分も帰属)に分離。M3にはM2初回B3実費を帰属。
- R-06 採用: Trial版選定関数を `run_storyline_b3_selection` と同じ検証・retry構造で複製。ID抽出regexは`[UNVERIFIED]`対応。再選定時の本文タグはその時点の状態、REJECTEDは候補本文から外しextra_noteに理由+選定禁止を明記、REJECTED IDが選ばれたら技術的失敗として検知(B3による再評価は維持)。draft描画欄=`build_verified_ledger_text`と同じ欄+Researcherの`ambiguity`、事前固定・記録。
- R-07 採用(測定のみ): 「中心Fact」=Storyline行が言及するFactと定義し、全方式で①Storyline行/Selected BriefがAMBIGUOUS Factを断定している件数、②M0/M0b比を記録。0でなければTrial後にユーザー判断事項(再生成ルール追加は新仕様のため設計には入れない)。
- R-08 採用: 既知欠陥×方式を(a)選定され検出/(b)選定され見逃し=NG/(c)非選定(最終台帳・Briefに不含を確認)の3値で記録。**故障注入プローブは「任意・別小実験」として設計し費用を別行で見積**(M0/M0bの採用Factの数値・scope・日付を1か所改変した複製2〜3件を上限なし/上限付きVerifierに検証させ期待REJECTED。B3比較には混ぜない)。採否はユーザー費用承認に含めて提示。
- R-09 採用: CP1で公式pricing(web_search_call課金単位、open_page/findの扱い)を確認。課金単位なら上限はweb_search_call全件で定義。未確認なら種別ごとに記録し、遵守率と費用影響を別々に報告。(a)ソフト上限=「上限指示Promptという介入」の効果として測定、報告に「hard capではない」と遵守率を併記。PRE_ANALYSISの「Fact別が初めて復元可能」は「呼出単位ログにより推定精度が上がる(Fact対応は依然heuristic)」に修正。(b)Fact別API分割・`max_tool_calls`系は主比較に入れない(安全柵としてのみ検討、存在・挙動は未確認と明記)。
- R-10 採用: M0/M0bペアをブラインド判定対象に混ぜる。品質はM0との一対比較(良い/同等/悪い)×3観点(面白さ・一貫性・事実整合)。判定ルール事前登録(例: M0-M0b差が中程度以上の記事では方式差が中程度以下なら方式効果と認めない)。案2出力のREJECTED痕跡によるブラインド限界を記録。
- R-11 記録: JPY0範囲は`parse_ledger_complete`+契約検証。Stage 3(任意)でCoffee・inboundのM0記事に全台帳/縮小台帳の両方でRFを実行しflag差を見る(費用を別行で見積、承認に含めて提示)。`[UNVERIFIED]`を台帳に混ぜる案は不可。
- R-12 採用: 初回B3共有は維持(報告でM3構成差がM2と相関することを明示)。M2/M3で同Factの判定差を上限効果とみなすのは、そのFactでM2呼出数が上限超過の場合のみ。任意: Coffee・inboundでM2初回B3を追加1回(約JPY25、別行で見積)。
- R-13 採用: 見積に技術retry余裕(B3/Verifier各1回分)、inboundの再選定をほぼ確実(p=1)として期待値に計上、比例縮小仮定は未検証と明記、M0'追加分を計上。日次1,000円判定は余裕を持つ(本日使用済みは41.6+S3W Phase A実測[未確定なら「約JPY3見込み」と注記])。
- R-14 採用: 1aの冒頭でCoffee M2を1本だけ流しharness結合確認(smoke)。1a→1b進行条件を事前定義(上限遵守率の記録が取れている/再選定loopが仕様どおり動作/実測費用÷見積≦1.3/Production・再利用成果物sha不変)。1bの先頭=streaming。
- R-15 採用: 5記事は差し替えない(理由を設計書に転記)。
- R-16 採用: 新規検証は`vfl01.MODEL`、各呼出の`response.model`を記録しM0の`model_id_actual`と一致をCP1で確認。B3は`routing.require_model("FAMILY_X_STORYLINE_B3")`経由で返却modelを照合。報告に使用モデル記載(25節)。

## 事前指定Read一覧
1. `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/TRIAL_DESIGN_01.md` 全文、`COST_ESTIMATE_01.md` 全文、`cost_estimate_calc_01.py` 全文(改訂の元)。
2. `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/PRE_ANALYSIS_SEARCH_CAP_01.md`: Grep `初めて復元可能` → R-09の文言修正箇所。
3. `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `OF-FXPW-R-12|^## |^\| ID` → 書式と末尾位置。
4. `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#104` → 更新位置。

## 事前指定Grep一覧+追記位置・更新位置の手順
- 新規 `TRIAL_DESIGN_02.md`: v1の構成(4-1〜4-8+相乗効果所見)を保ちつつ、上記Fable決定を各節に反映。冒頭に「v2: Opus条件Aレビュー(OPUS_REVIEW_A_01_VERBATIM.md)反映版。Fable決定=OF-RLCT-R-01〜16採用(R-07/R-11は測定・記録のみ)。有料実行はユーザー費用承認#104後。CP1(harness実装・JPY0 dry-run)は承認待ちと並行可」。v1は残す(先頭に「v2に置換、履歴」注記を1行追加)。
- `PRE_ANALYSIS_SEARCH_CAP_01.md`: R-09の文言修正(該当文のみ、訂正注記付き)。
- 新規 `COST_ESTIMATE_02.md`+`cost_estimate_calc_02.py`/`cost_estimate_02.json`: 表①Trial追加支出(Stage 1必須=4方式+M0b+M0'[3記事]+smoke+技術retry余裕+inbound再選定p=1; 任意行=故障注入プローブ[記事あたり検証2〜3件、Verifier呼出費を既存実測から算出]/M2初回B3追加[Coffee・inbound、約25]/Stage 3 RF比較[Coffee・inbound、W-1なし=RFのみの費用を既存実測から]; Stage 2条件付き=openai/central M0')、1a(Coffee+inbound)と1b(streaming→openai→central)の分割、期待/上限、本日使用済み・日次残額、7-7/7-9判定。表②本番換算費用(記事×方式、Research実測+検証+B3+再選定、削減率の算出式)。全仮定を列挙、出典付き。
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: OF-RLCT-R-01〜R-16を追加(RAISED→FABLE_DECIDED、決定内容1行、反映先=TRIAL_DESIGN_02 節番号)。
- SSOT(編集権あり): `DECISION_LOG.md`(Grep `RLCT|COST-OPTIMIZATION-TRIAL-01` 最終出現の後)に「委任_03: Opus条件Aレビュー受領(verbatim sha)、Fable決定R-01〜16採用、設計v2・見積v2(数値)、Status=TRIAL_DESIGN_REVISED_COST_APPROVAL_PENDING、CP1はJPY0で承認待ちと並行可」。`docs/pm/REPORT_LEDGER.md` 行追加。`docs/pm/USER_DECISION_REGISTER_01.md` #104の金額を見積v2の値へ更新(必須/任意の内訳を明記)。`docs/pm/ACTIVE_TASK.md` ヘッダ更新(addなし)。

## 実行コマンド全文
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_03.md --json-out docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_03.md_check.json`
- Opus抽出: `.venv\Scripts\python.exe -I "C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\rlco\extract_rlct_02.py" --jsonl "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-a28bc9701cb8c8f22.jsonl" --start "## Opus独立技術レビュー結果: RLCT Trial設計" --must "OF-RLCT-R-16" --out "C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\OPUS_REVIEW_A_01_VERBATIM.md"`(scriptの引数名が異なる場合は同等に合わせる)
- 見積: `.venv\Scripts\python.exe -I docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/cost_estimate_calc_02.py --pricing er005_output/cost_baseline_01/pricing_snapshot.json --base docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/cost_estimate_01.json --out docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/cost_estimate_02.json`
- secret scan: `.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(hits=0)
- git: `git status --porcelain -- docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_03.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md docs/pm/OPUS_FINDINGS_LEDGER.md` → 明示add → commit → push。

## SSOT追記文
上記のとおり(実値で埋める)。

## Git(明示add対象・コミットメッセージ・trailer)
- SSOT編集権: あり(`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`。`OPEN_ITEMS.md`は今回変更不要、`CURRENT_SPEC.md`・`PM_GOVERNANCE.md`は編集しない)。
- 明示add: `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/{OPUS_REVIEW_A_01_VERBATIM.md,TRIAL_DESIGN_01.md,TRIAL_DESIGN_02.md,PRE_ANALYSIS_SEARCH_CAP_01.md,COST_ESTIMATE_02.md,cost_estimate_calc_02.py,cost_estimate_02.json}`、`docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_03.md`(+_check.json)、`DECISION_LOG.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`。
- commit message: 「FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_03: Opus条件Aレビュー逐語保存+Fable決定(OF-RLCT-R-01〜16採用)反映の設計書v2+費用見積v2(Trial追加支出/本番換算の分離、M0'・プローブ・1a/1b)+Opus台帳+SSOT(JPY0、実装なし、費用承認#104待ち)」
- push: `work/post-merge-01`でcommit → `C:\Users\tensh\eigo-radio-crbn`で `git pull --ff-only origin main; git merge --ff-only work/post-merge-01; git push origin main` → 主dirで `git merge --ff-only origin/main`。conflictは停止して報告。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_RLCT3.md`(20行程度): T-0/Opus verbatim保存(文字数・sha)/設計v2の主な変更点(節ごと1行)/見積v2の要約表(1a・1b・必須合計・任意行[プローブ/M2 B3追加/Stage 3 RF]・Stage 2・期待/上限・本日使用済み・日次残額・7-7判定)/本番換算表の要点(記事×方式の削減率)/Opus台帳追加/SSOT位置/commit hash・push・raw URL/4行/`判定整合:`行/判断候補(#104の金額確定版のみ。任意行は選択肢として)。Fable決定に対する意見があれば「意見」欄に(反映はしたうえで)。

## Fable自己チェック(送信前)
- [x] Read一覧・Grep追記位置あり [x] コマンド実値あり [x] 禁止・費用(JPY0)あり [x] 並行衝突回避(S3W path不可触・commit単独)あり [x] Opus判定(条件A実施済み・反映)あり [x] 時間見込みあり [x] 継続委任(前委任QDC: ファイル化完了・JPY0・次=設計v2→費用承認)

## 実行時の補足(worker記録)
- Opus抽出は引数が異なる(extract_rlct_02.pyはヘッダを自動付加する形式)ため、同等のscript `scratchpad/rlco/extract_rlct_03.py` を作成して注記1行のみ付加で抽出。
- `PRE_ANALYSIS_SEARCH_CAP_01.md` には「初めて復元可能」の文字列が無く(該当文はTRIAL_DESIGN_01.md:21)、PRE_ANALYSIS側は同趣旨の記述(L47)に訂正注記を追加した。
