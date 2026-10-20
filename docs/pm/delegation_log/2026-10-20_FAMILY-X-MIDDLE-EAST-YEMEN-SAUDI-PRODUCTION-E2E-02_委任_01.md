# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_01(ユーザー正式決定③: 中東記事を現行Production仕様のままResearchから再実行し、攻撃主体[Ansar Allah/フーシ派]がB3採用Factに含まれた試行のみ音声完成・試聴ページ公開まで連続実行。Research最大3回)。並行タスク: 同時刻に別agentが `FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_04`(SSOT Closeout、OPEN-423/425/427行・REGISTER #123/#125/#127・DECISION_LOG・REPORT_LEDGER・docs/research/FAMILY-X-RESEARCH-*/ を編集)を実行中。本委任は **OPEN-416行・REGISTER #112行・`docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02/`・`er019_output/middle_east_yemen_saudi/run_mey_02〜04`・audio out-dir・`user_test/middle_east_yemen_saudi_e2e_02/`** を担当し、OPEN-423/425/427・#123/#125/#127には触れない。ACTIVE_TASK.mdのヘッダ追記はS0完了後(開始5分以降)に、直前にファイルを再読してから先頭追記する。

## 性質/到達上限Status/禁止事項
- 性質: 正式Production経路の記事生成(text+audio)。新仕様探索ではない。到達Status: 記事=`AUDIO_COMPLETED_PAGES_PUBLISHED → USER_LISTENING_PENDING`(ユーザー試聴PASSは別Status)。3回とも不成立なら`STOP(B3未採用)`で報告(USER_DECISION_REQUIREDラベルはFableが付ける)。
- **費用/日次**: 当日(2026-10-20 JST)既使用JPY513.24(出典: RESULT_PACKET_XRFR3.md/daily_dev_cost_01 stub除外後)/残JPY486.76/本委任見積: 1試行text約JPY60(前回run_mey_01実測: Research 27.0[web_search 15回]+Ledger 9.1+B3 6.0+Writer R0-R2 11.7+Adv/Std/RF 2.7=56.6、再生成分23.3を除く)、不成立試行はResearch+Ledger+B3まで=約42、audio約JPY25(BAPE実測23.2)。最悪(Research3回+音声)=42+42+60+25≈JPY169。承認区分: C(ユーザー決定③で承認済みScope、案件見積300円以下、日次513+169<1,000)。改善見込み: 中(攻撃主体は前回もUN出典に存在=OPEN-425、Researcher claim化で脱落しただけ。Azure PL等は無関係)。
- T-3: 上限¥180(Guardrail、本委任の新規支出合算)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。**ただしユーザー指示§2「上限超過が見込まれる場合は超過前にSTOP」を優先: 次stage開始前に「既使用+次stage見積」が¥180を超える見込みなら、そのstageを開始せずSTOPして報告する**(ユーザー承認値優先、独自の厳格化はしない)。各stageの`--budget-jpy`はtext=110/audio=70(前回E2E-01と同値、run単位の内部ガード)。
- 禁止(ユーザー§1③・§2): 未承認のPrompt/仕様/閾値/コード変更・手動Fact挿入・Ledger/B3出力の手編集・`--regenerate-stage storyline_b3`による採用Factの再抽選(B3未採用時は必ずResearchから新run dirで再実行)・HR Lock/review_lock/STOP sentinelの迂回・`approve_regenerate`・有料runの再起動(26節: rc≠0や外部停止時は再起動せず報告。同一stageのresumeは runner既存のresume機構が明示的に許すときのみ、理由を記録)・Batch TTS・`git add -A`/`-u`/`stash`/`amend`/`rebase`/`reset --hard`/`checkout -f`・branch切替/新規branch・wav/mp3のer019_output配下commit(gitignore尊重。user_test配下の試聴用音声は既存BAPEページの方式に従う)。
- Opus独立技術レビューGate(11-3): 非該当(承認済みProduction経路の実行のみ。設計・実装変更なし)。
- 時間見込み: 1試行あたり text 25〜35分(Research 10/B3 3/Writer 10/Adv+Std 5)+audio 45〜60分(scaffold 12/TTS Adv 15/TTS Std 15/assemble 5/page+Playwright 10)。並列化: Research〜B3は直列(前工程出力依存)。B3採用判定後、Writer→Adv/Std実行中に試聴ページ生成script(`er019_bape_page_04.py`のMEY版)の準備・`user_test/`雛形・E2E_PLAN_02.md記録を並行で進める。TTS Adv/Stdはrunnerが同一run stateを更新するため直列(state競合)。Research試行同士は条件付き(不成立時のみ次を実行)なので並列にしない(費用原則3)。
- 修正範囲(D-1/11-8): コード修正なし。範囲外=受理面・閾値・方式の新設/拡大。もし実行中にrunner不具合(仕様文と実装の乖離)が判明したら修正せずSTOPして報告。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。(本件は新規記事なので全segment新規生成が正常。Master Audio Storeの固定shell再利用は既存機構どおり)
T-3: 上記「性質」欄の定型文を適用。

### T-0の実施方法(逐語保存。自分で打ち直さない=要旨化はFAIL)
`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-20_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_委任_01.md`
Nは最新のAgent tool-use(本委任文。管理IDに「E2E-02 委任_01」を含むもの)。隣接indexに別agentの委任文(XRFR 委任_04)があるので取り違えない。保存後にGrepで「E2E-02 委任_01」を含むことを確認し、sha256・文字数をRESULT_PACKETへ。
ユーザー指示原文(2026-10-20)は別agent(委任_04)が `docs/pm/delegation_log/2026-10-20_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_USER.md` へ保存する。本委任は作成しない(存在すれば参照のみ)。下記「ユーザー指示(原文)」を本委任の正とする。

## ユーザー指示(原文・2026-10-20、本委任は§1③・§2・§3・§4が対象)
--- 原文ここから ---
### ③ 中東記事：Researchから再実行し、音声完成まで進める

**現行Production仕様のまま、Researchから再実行する。**

重要な受入条件は、**攻撃主体（Ansar Allah／フーシ派）がB3の採用Factに含まれること**。

- B3が攻撃主体を採用した場合：そのままWriter → TTS → Audio QA → Assemblyまで進め、完成音声と試聴ページを作成する。
- B3が採用しなかった場合：その試行の音声化は行わず、Researchから再実行する。
- Research再実行は、**初回1回＋再試行最大2回＝合計最大3回**。
- 3回ともB3で攻撃主体が採用されなければSTOPし、原因・各試行の結果を報告する。
- 未承認のPrompt・仕様変更、手動Fact挿入、B3の採用Factの強制変更によって条件を満たしたことにしてはならない。

## 2. 実行時の留意点

- Research → Fact Ledger → B3 → Writer → 音声化の正式Production経路を使用する。
- 各試行で、Researcherが攻撃主体をFact化したか、Ledgerに登録されたか、B3が採用したかを区別して記録する。
- B3で攻撃主体が採用された時点で、Researchの追加試行は不要。
- 既存の品質Gateはすべて維持する。攻撃主体の採用だけで記事全体を無条件PASSにしない。
- Writer本文にも攻撃主体が正確に反映されていることを確認する。
- 既存の承認済みTTS仕様、retry／fallback／regeneration／resumeを維持する。
- 原稿のユーザー事前確認待ちは設けず、条件を満たせば音声完成まで連続実行する。
- 独立作業を並列化し、不要な待機・日付分割をしない。
- 予算は既存の個別承認枠と日次1,000円（JST）を遵守する。最大3回のResearchを含め費用を管理し、上限超過が見込まれる場合は超過前にSTOPする。

## 3. 完成条件・PM Gate

- 攻撃主体がB3の正式採用Factに含まれる。
- Writer本文にも正確に反映される。
- 全必須品質GateをPASSする。
- Standard／Advancedの対象音声が完成する。
- 完成音声・全文原稿・Key Phrasesを確認できる試聴ページを公開する。
- 正式Production経路のruntime evidenceを記録する。
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Gitを整合させる。
- Fableが実行証拠を確認し、独立評価する。

## 4. 最終報告

1. **中東記事は完成したか／試聴URL**
2. Research試行回数（最大3回）と各回の結果
3. 攻撃主体のFact化 → Ledger登録 → B3採用 → Writer反映の証拠
4. Standard／Advancedの音声品質Gate結果
5. 実費、量産単価への影響、所要時間
6. Production経路・SSOT・Git反映状況
7. 未解決事項と必要なユーザー判断（ある場合のみ）

**今回の目的は、新しいResearch仕様を探索することではなく、現行の承認済みProduction仕様で、攻撃主体を正しく含んだ中東記事を完成させること。**
--- 原文ここまで ---

## 受入条件の事前固定(Fable。実走前にE2E_PLAN_02.md §0へ転記し、以後変更しない)
- **攻撃主体Fact**の定義: Fact本文(英語/日本語いずれでも)が、サウジ領内(リヤド/アブハ空港・Aramco施設等)またはイエメン周辺への当該期間の攻撃について、その実行主体または犯行声明主体として Houthi / Houthis / Houthi movement / Ansar Allah / Ansarallah / フーシ派 / アンサール・アッラー のいずれかを明示するもの。帰属付き(「〜が犯行声明」「サウジ主導連合軍/国連によれば〜」)で構わず、むしろ帰属は保持されるべき。単に「フーシ派支配地域」等の場所言及のみ、または攻撃と結びつかない言及は**該当しない**。
- 判定の3段階を分けて記録: (i) Researcher Fact化=`research_ledger/`のResearcher出力(facts配列)に攻撃主体Factがあるか(Fact ID列挙)/(ii) Ledger登録=`verified_fact_ledger.*`でVERIFIEDか(AMBIGUOUS/REJECTEDなら理由)/(iii) B3採用=`storyline_b3/fact_selection_evidence.json`のselected(採用)側に該当Fact IDがあるか。(iii)がYesのときのみ下流へ進む。
- Writer反映=b1b/a2の本文(`writer_run_summary.json`/article.md/parts.json)に攻撃主体が、Ledgerの帰属を保った形で登場すること(Grep `Houthi|Ansar ?Allah|Ansarallah`、不一致例: 帰属の脱落・主体のすり替え・断定への格上げ)。B3採用済みなのにWriter本文に無い場合のみ、既存機構 `--stage writer --regenerate-stage writer`(以後advanced/standardも各1回再実行)を**1回だけ**許可(Prompt不変、§14の正式手順と同じ)。それでも無ければSTOPし報告。
- 「攻撃主体の採用だけで無条件PASSにしない」: 既存Gate(Fact Lock/記号Validator/IOL spec_ok/RF候補/AUW/Audio Validation Gate/style_profile_gate/key_phrase_source_gate)は従来どおり。RF候補があれば件数・内容を記録(前回§13同様、合否判定はFable)。HR/Lock/BLOCKが発火したら迂回せずSTOPして報告。
- 日付・帰属のCP(前回§14で確認した観点): Ledger外の具体描写0件、数字の帰属、本文中の時点明示の有無を記録(合否はFable)。

## 工程(E2E-01 §4/§13・BAPE §4/§13を転用。theme/slug/run/labelのみ変更)
共通: 各stage前に `.venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 --run-dir er019_output\middle_east_yemen_saudi\run_mey_0N --out er019_output\middle_east_yemen_saudi\run_mey_0N\audit\stop_scope_<stage>.json`(rc=3なら中止)。全runnerコマンドに `TTS_EXECUTION_MODE=STANDARD`。PowerShellなら `$env:TTS_EXECUTION_MODE="STANDARD"; $env:PYTHONIOENCODING="utf-8"` を先頭に。console出力は `run_mey_0N/console_<stage>.txt` へTee。
THEME=`中東情勢が悪化、イエメン・サウジ周辺で攻撃続く`(前回と同一文字列、英語補助文なし)。slug=`middle_east_yemen_saudi`。run=試行1 `run_mey_02`/試行2 `run_mey_03`/試行3 `run_mey_04`。run-label=`MEY-E2E-02-T1`/`-T2`/`-T3`。out-dir=`er019_output/middle_east_yemen_saudi/run_mey_0N`(実走前非存在を確認。`run_mey_01`は読取のみ、改変禁止)。

| # | 工程 | コマンド(N=2/3/4) | STOP/Gate |
|---|---|---|---|
| S0 | 実走前JPY0 | `.venv\Scripts\python.exe docs\pm\tools\daily_dev_cost_01.py --date 2026-10-20`(当日既使用を再確認、513.24と大きく違えば理由調査)/出力dir非存在/`er019_family_x_entertainment_production_runner_01.py --help`と`er019_family_x_audio_production_runner_01.py --help`で引数実在確認/`git status --porcelain`で作業前状態を記録 | 未達=開始しない |
| S1 | Research+Verified Fact Ledger | `.venv\Scripts\python.exe er019_family_x_entertainment_production_runner_01.py --theme "中東情勢が悪化、イエメン・サウジ周辺で攻撃続く" --slug middle_east_yemen_saudi --out-dir er019_output/middle_east_yemen_saudi/run_mey_0N --run-label MEY-E2E-02-TN --budget-jpy 110 --stage research` | `research_ledger/runtime_evidence.json` `reused:false`・web_search回数・facts数・VERIFIED数を記録。**ここで(i)(ii)を判定・記録** |
| S2 | B3(Sol) | 同 `--stage storyline_b3` | model_id確認。**(iii)判定**: 採用=S3へ/未採用=本runは凍結(STOP sentinelは置かず、`run_mey_0N/NOT_ADOPTED.md`に(i)(ii)(iii)の証拠と選定理由[B3の除外理由文]を記録)→N+1で S1から(最大N=4)。 |
| S3 | W-1 R0→R1→R2 | 同 `--stage writer` | 記号Validator STOP |
| S4 | Advanced+IOL+RF b1b | 同 `--stage advanced` | IOL spec_ok=false=STOP |
| S5 | Standard+RF a2 | 同 `--stage standard` | text終端。Writer反映確認(上記)。 |
| S6 | 音声plan(JPY0) | `.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug middle_east_yemen_saudi --run run_mey_0N --level both --stage plan` | `audit/style_profile.json` profile fx_20261017・6 role sha(SUPPORT_JA 060c08fd…/FULL_STORY 3a680861…/PREVIEW 8862317f…/KP_EXPLANATION_EN 05180006…/KP_EN 9d905cfe…/KP_JA_MEANING b12c8721…)一致、`--tts-backend`省略=既定speech_metadata_flash_lite |
| S7 | KP scaffold | 同 `--stage scaffold --level both --budget-jpy 70` | gloss HR待ち=STOP。M2→fallback発生は必ず報告 |
| S8 | TTS Adv | 同 `--stage tts --level b1b --budget-jpy 70` | review_lock/`STOPPED` segment=STOP |
| S9 | TTS Std | 同 `--stage tts --level a2 --budget-jpy 70` | 同上。Std fallback記録 |
| S10 | AUW+Assembly | 同 `--stage assemble --level both` | Audio Validation Gate/M3 Style Gate。BLOCK=迂回せずSTOP |
| S11 | 試聴ページ | 同 `--stage player` → `er019_bape_page_04.py`を読み、MEY用に `er019_mey_page_02.py`(新規、pathとタイトルのみ差替え、ロジック同一)を作成して `user_test/middle_east_yemen_saudi_e2e_02/index.html` を生成(完成音声Std/Adv・全文原稿Std/Adv[Preview/Full Story/Comment/KP含む]・Key Phrases[英語+日本語意味/英語解説]を1ページで確認可能)→commit/push→`https://shimomura055.github.io/eigo-radio/user_test/middle_east_yemen_saudi_e2e_02/index.html` HTTP200+Playwright実再生(BAPE §13と同じ: 全音声再生OK・seek OK・console error 0・秒数一致)、evidence=`audit/pages_play_evidence_02.json` | Gate 7 |

S2で未採用→次試行のとき、次試行S1開始前に「既使用(本委任新規支出合算)+次試行見積(research+ledger+B3≈42、採用時はさらに+text 18+audio 25)」を計算して記録し、¥180超過見込みならSTOP(ユーザー§2)。

## 記録(docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02/E2E_PLAN_02.md を新規作成)
§0 受入条件の事前固定(上記を転記)/§1 開始条件チェック(S0結果)/§2 試行ごとの記録表(試行N: run dir・Research facts数・web_search回数・(i)Fact ID・(ii)VERIFIED可否・(iii)B3採用可否+選定/除外理由の引用・費用)/§3 採用試行の下流記録(E2E-01 §13の書式: Writer/Adv/Std・RF候補・HR/Lock・タイトル・In One Line・Writer反映Grep結果・Ledger外描写突合)/§4 音声工程記録(BAPE §13の書式: KP・AUW結果・減速・style gate・assemble秒数・PL weight 2.0が記録されていればその値)/§5 費用(工程別JPY、出典=cost.json/raw_usage_log/`er019_mey_cost_01.py`流用。15節5区分: 1記事総コスト/Standard同期/Batch換算/異常retry由来/Trial特有=なし。中東記事の案件累計=E2E-01 text 79.881+本委任)/§6 所要時間(stageごと開始・終了時刻)/§7 runtime evidence一覧(model_id・reused:false・profile sha・backend・AUW gate json path)。

## SSOT(本委任の編集権: OPEN_ITEMS.md OPEN-416行のみ・USER_DECISION_REGISTER_01.md #112行のみ・DECISION_LOG.md新規エントリ1件・REPORT_LEDGER.md行追加。CURRENT_SPEC.mdは仕様不変のため編集しない[記事個別の登録節があれば報告のみ])
- 音声完成・ページ公開後(または3回不成立STOP後)に編集。OPEN-416行: Status角括弧を完成時 `[AUDIO_COMPLETED_PAGES_PUBLISHED・USER_LISTENING_PENDING(E2E-02 run_mey_0N、ユーザー2026-10-20決定③)]`/不成立時 `[STOP(Research3回でB3攻撃主体未採用)・判断候補あり]` へ置換し、行末に試行回数・採用Fact ID・試聴URL・費用・E2E_PLAN_02.md参照を追記。#112行: 「判断済み 2026-10-20(決定③: Researchから再実行・B3攻撃主体採用を受入条件・音声完成まで連続実行)」+結果1行。DECISION_LOG: 決定③の記録+実行結果。REPORT_LEDGER: 本委任行。
- 並行agentとの共有プロトコル: 編集直前に`git status --porcelain <file>`と担当行の再Grep、担当行以外を触らない、編集後すぐ`git add <明示パス>`→commit。`index.lock`があれば30秒待って再試行(削除しない)。`git diff --cached --stat`で自分のファイルだけがstageされていることを確認(他agent分が混ざっていたら`git restore --staged`で外す)。

## 事前指定Read/Grep一覧
- `docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01/E2E_PLAN_01.md`: L21-75(工程・費用・STOP)、L108-149(前回実走記録・CP・§15)。
- `docs/research/FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01/E2E_PLAN_01.md`: L37-58(音声工程)、L153-161(音声実走記録・ページ・Playwright)。
- `er019_bape_page_04.py`: 全文(ページ生成scriptの流用元)。`er019_mey_cost_01.py`: 全文(費用集計流用元)。
- `docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/RESEARCH_GAP_ROOT_CAUSE_01.md`: Grep `Houthi|Ansar|攻撃主体` → 該当行(前回どの出典に攻撃主体があり、どこで脱落したかの把握のみ。Prompt変更はしない)。
- `er019_output/middle_east_yemen_saudi/run_mey_01/storyline_b3/fact_selection_evidence.json`: 構造確認(採用/除外キー名の把握)。
- `er019_output/middle_east_yemen_saudi/run_mey_01/research_ledger/`: ファイル一覧とruntime_evidence.jsonのキー(読取のみ)。
- `OPEN_ITEMS.md`: Grep `^OPEN-416 \|` → 該当行のみ。`docs/pm/USER_DECISION_REGISTER_01.md`: Grep `^- #112\(`。`DECISION_LOG.md`: Grep `^## ` head 3(書式のみ)。`docs/pm/REPORT_LEDGER.md`: 末尾15行。
- `docs/pm/ACTIVE_TASK.md`: 先頭10行(ヘッダ書式確認。S0後に再読してから追記)。
- `user_test/boredom_aggression_bape_e2e_01/index.html`: 構造確認(全文可、小さい場合)。

## 実行コマンド全文
上表のとおり(python=`.venv\Scripts\python.exe`)。T-0 check: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-20_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_委任_01.md --json-out docs/pm/delegation_log/2026-10-20_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_委任_01_check.json`。secret scan: `.venv\Scripts\python.exe tools/secret_scan_01.py --staged`(hits=0必須)。Playwright確認はBAPE委任_04で使った方法(`audit/pages_play_evidence_04.json`生成script。Grep `pages_play_evidence` で特定)を流用。

## ACTIVE_TASK.mdヘッダ(S0後、先頭追記1回+完了時に同ブロックのStatus行だけ更新)
```
# ACTIVE_TASK(委任_01 [MEY E2E-02 Research再実行〜音声完成] 先頭追記 2026-10-20)
管理ID: FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_01 / Status: <進行stage>
UDR-blocking: なし(#112=決定③で判断済み)。APPROVED未配線: なし。STOP条件: B3攻撃主体未採用3回/HR・Lock・BLOCK発火/rc≠0(再起動禁止)/新規支出¥180超過見込み。
QDC: 見込み=中 進捗=<> 当日費用=2026-10-20 <累計>/1,000(S0時点513.24) 次=<>
承認済み指示: docs/pm/delegation_log/2026-10-20_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_USER.md §1③/§2/§3
報告=docs/pm/RESULT_PACKET_MEY2.md、記録=docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02/E2E_PLAN_02.md
```

## Git(明示add対象・コミットメッセージ)
commitは工程の区切りごと(最低: (1)T-0+E2E_PLAN_02 §0〜§1、(2)text工程完了[run_mey_0N配下の json/md/txt。wav/mp3/大容量は除外、gitignore尊重。`raw_usage_log.jsonl`等で他runの既存差分`M`が多数あるファイル[manifest.json/reuse_telemetry.jsonl/human_review_queue.jsonl等]はstageしない=BAPE §13と同運用]、(3)音声工程+試聴ページ+`er019_mey_page_02.py`、(4)SSOT)。メッセージ例: `FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_01: 試行1 text工程(Research/Ledger/B3採用F__/Writer)` 等、事実を含める。push先は直近commit 6e1efec39と同じ(`git branch --show-current`・`git log -1 --format=%D`で確認、branch切替・新規作成禁止)。push後にraw.githubusercontent.com URLを列挙。試聴ページのpushはGitHub Pages反映待ち(数分)後にHTTP200確認。

## 報告(docs/pm/RESULT_PACKET_MEY2.md へ上書き作成。ユーザー§4の1〜7の順で、各項目に証拠path)
1. 完成可否・試聴URL(HTTP200・Playwright結果)。2. 試行回数と各回結果((i)(ii)(iii)を分けた表、採用Fact IDと原文、未採用時のB3除外理由の引用)。3. Fact化→Ledger→B3→Writer反映の証拠(ファイル:キー/行、Writer本文の該当文を引用、帰属の保持可否)。4. Std/Advの音声Gate結果(AUW PASS/PASS_WITH_WARNING/NG件数・HR 0確認・減速・style gate・KP source gate、PL weight 2.0記録の有無)。5. 実費(工程別・出典・本委任新規支出合算・中東記事案件累計[79.881+今回]・当日累計[daily_dev_cost再実行値]・Batch換算・70円目標との差)と所要時間(stage別)。6. Production経路evidence(model_id・backend・profile・reused:false)・SSOT編集行の新旧・commit hash・raw URL。7. 未解決事項・判断候補(RF候補・PASS_WITH_WARNING clipの事後試聴リスト・その他)。加えて T-0結果行、並行agentとのgit競合の有無、26節(再起動)該当の有無を必ず明記。
Fableが受入判定・ユーザー報告を行う。USER_DECISION_REQUIREDラベルは付けず「判断候補」と書く。