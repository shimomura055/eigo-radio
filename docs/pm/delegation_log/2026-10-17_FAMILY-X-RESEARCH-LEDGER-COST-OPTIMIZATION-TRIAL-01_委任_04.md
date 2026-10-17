# 委任文(DELEGATION_STANDARD_TEMPLATE準拠)

## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_04(CP1: Trial専用harness実装+JPY0 dry-run。ユーザー正式承認[2026-10-17、(b)+任意A、累計上限JPY1,040]の原文保存。**有料実行なし・git書込みなし**)。本日=2026-10-17(JST)。前委任=委任_03(commit `9f579283f`、設計書v2・見積v2)。

## 性質/到達上限Status/禁止事項
- 性質: Trial専用コードの実装(`er082_*`、Production非接続)+API呼出0のdry-run/test。
- 到達上限Status: `CP1_HARNESS_READY_DRYRUN_PASS_PENDING_COMMIT`(Stage 1a有料実行は次委任。Fable確認後)。
- 費用: JPY0(有料API呼出禁止。dry-runはstub/保存済み出力のみ。もしOpenAI pricingの確認にネットワークが必要なら行わず「未確認」と記録)。
- 禁止: Production runner・Prompt・正式profile・retry/fallback/regenerationの変更(`er019_family_x_entertainment_production_runner_01.py`、`er012_e_family_entertainment_two_level_runner_01.py`、`er003_v1_en_direct_vfl_01_generate.py`、`er019_family_x_storyline_b3_fact_selection_01.py`、`er002_ja_web_research_r3.py`、`er053_*`、`er005_*`は読取のみ。実行前後でsha不変をtestで確認)/**monkey-patch禁止**(モジュール定数・関数の実行時差し替え不可。必要な差異は複製関数の引数で)/既存成果物(`er019_output/**`)への書込み(Trial領域 `er082_output/rlct_trial_01/` へ複製してから処理)/Master Audio Store・Review Queue既定root(`review_queue/post_en`)への書込み/Family A・B・C/git書込み(並行中のS3W 委任_03がcommit予定。「commitを伴う作業は同時に1件のみ」)/SSOT・`ACTIVE_TASK.md`の編集(文案のみ)/設計書v2からの逸脱(逸脱が必要なら理由を記しFable確認待ちにする。実装を進めてよいのは設計書どおりの部分のみ)。
- 並行タスク: S3W 委任_03(Production配線・実走・commit中)、同じrepoで `er019_family_x_style_profile_01.py`・audio runner・test・`er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3prod/`・`user_test/coffee_fxpw_e2e_01_s3prod/`・SSOTを編集中。これらに触れない。本委任の新規ファイルは `er082_*.py`・`er082_output/`・`docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/`・`docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_*` に限定。
- Opus Gate: 条件A実施済み(R-01〜16反映済み設計v2)。実装はその範囲内。
- 時間見込み: 実装3時間/dry-run・test 1時間 ≒ 4時間。単独。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3: 本委任は費用上限JPY0のためCap定型は該当なし。harnessに実装する予算guardは次のユーザー承認値を定数化する: 累計上限JPY1,040、Stage 1a上限493、Stage 1b上限493、任意A上限54。期待合計536。
T-0補足(厳守): (a)本委任文は**全文**(全節・全見出し・path省略なし・圧縮転記不可)を `docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_04.md` へ保存。直近4委任で要約保存が続いており、これは逸脱として記録されている。Writeツールで本文をそのまま書くこと。(b)下記「ユーザー指示(原文)」節を**一字一句そのまま** `docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_APPROVAL_USER.md` へ保存し、文字数・sha256を記録。`python`shimは壊れている(rc=49)ので `.venv\Scripts\python.exe` を使う。

## ユーザー指示(原文)
# Claude Code／Fableへの正式指示
## Research／Fact Ledger コスト最適化Trial — Stage 1全体＋任意A

**管理ID：FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01（継続）**

### 1. ユーザー正式判断

**選択肢(b)＋任意Aを承認する。**

- Stage 1a：Coffee＋訪日客統計
- Stage 1b：Disney+値上げ、OpenAI著作権訴訟、FOMC・住宅ローン金利
- 任意A：故障注入によるFact誤り検出力の確認

**承認費用：期待約¥536、累計上限¥1,040。**

Stage 1a・1bは別日で実行し、既存の日次予算ルールを遵守すること。

任意B（B3追加Take）、任意C（Risk Flagger影響比較）、Stage 2条件付き再検証は、今回の承認範囲に含めない。

今回の承認は**Trial実施と費用の承認**であり、改善仕様の正式Production採用ではない。

### 2. 実施前確認

既存の設計・見積を正本として使用する。

- `TRIAL_DESIGN_02.md`
- `COST_ESTIMATE_02.md`
- `OPUS_REVIEW_A_01_VERBATIM.md`
- `PRE_ANALYSIS_SEARCH_CAP_01.md`

Opus条件Aレビューの指摘16件（Blocking 3／Major 7／Minor 6）が設計に反映されていることを確認する。

不要な設計やTrial範囲の拡大は行わない。

### 3. Trial実施内容

5記事それぞれで、以下の4方式を比較する。

| 方式 | 内容 |
|---|---|
| 従来方式 | 全Fact検証 → B3選定 |
| 案1 | Fact単位の検索上限3回 → B3選定 |
| 案2 | B3選定 → 選定Factだけ独立検証 |
| 案1＋案2 | B3選定 → 選定Factだけ検証（検索上限3回） |

保存済みResearch下書きを再利用し、新しいResearchは実行しない。

既存の従来方式のB3が旧モデルによる場合は、比較条件を揃えるため、承認済みの現行Sol Writer設定で基準を生成する。

既存成果物を変更せず、Trial専用領域に複製して比較すること。

### 4. 重要な検証条件

**案1**

- 3回上限は未検証の暫定値として扱う。
- Web検索ツール呼出単位で計測する。
- 2回／3回／5回の机上比較と、実行結果を区別する。
- VERIFIED Factの喪失と検索費用削減を両方評価する。

**案2**

選定FactがREJECTEDとなった場合は、機械的に削除して確定せず、B3に再選定させる。

- 不合格理由をB3へ返す
- 必要なら他のFactを選ぶ
- 新たな選定Factを独立検証する
- 検証済みFactの結果は再利用する
- 再選定はTrial上、最大2回
- 上限到達時は無理にB3を確定しない

AMBIGUOUSとREJECTEDを区別し、既存Fact Lockの安全条件を維持する。

### 5. 任意A：故障注入テスト

**任意Aの実施を正式承認する。**

意図的に誤ったFactをTrial専用データへ注入し、検証機構が誤りを検出できるか確認する。

目的は、案1・案2・組合せ方式によって、Factの誤り検出力が低下しないかを評価すること。

- Productionデータには注入しない
- 元のResearch下書き・Ledger・B3を変更しない
- 誤FactがVERIFIEDとして通過していないか確認する
- 検出漏れがあれば重大NGとして報告する

故障注入テストの結果を、通常記事における誤り検出率の保証として扱わない。

### 6. 実行順序

1. Trial専用harness実装
2. JPY0 dry-run（CP1）
3. Stage 1a：Coffee＋訪日客統計
4. 中間費用・品質Gate確認
5. Stage 1b：残り3記事
6. 任意A：故障注入テスト
7. 全結果の集計
8. Fable独立レビュー
9. ユーザー報告後STOP

Stage 1bへの進行は、設計書の既存条件（Stage 1a実測／見積比1.3以下等）を満たすこと。

条件を満たさない場合は、ユーザー判断を求めてSTOPする。

### 7. 費用管理

**今回の累計上限：¥1,040。**

- Stage 1a上限：¥493
- Stage 1b上限：¥493
- 任意A上限：¥54

期待額は合計¥536。

各Stageの上限と全体上限の両方を守ること。

Web検索手数料を含めた実費を計測する。

日次¥1,000のsoft budgetを維持し、必要に応じて実行日を分割する。

費用上限に近づいた場合は、無理に続きを実行せずSTOPする。

事前見積と実測費用の差が大きい場合は、原因を記録すること。

### 8. 評価・報告

各記事・各方式について、以下を表形式で報告する。

- Research／Ledger／B3の実測費用
- Web検索呼出回数
- Fact判定の変化
- B3で選ばれたFact
- 最終B3構成の差
- ストーリーの品質・一貫性
- 再選定の回数・追加費用
- 故障注入テストの結果
- 従来方式比の削減額・削減率

5記事合計だけでなく、**記事別に効果がどれだけ異なるか**を明確にすること。

削減額と品質差を分けて評価し、70円／記事セットの目標に対する実際の寄与を説明すること。

### 9. Production変更禁止

今回の作業はTrial限定。

- Production runner・Prompt・正式profileを変更しない
- retry／fallback／regenerationを変更しない
- 未承認の検索上限・Select-then-VerifyをProductionへ導入しない
- Family A／B／Cの開発を行わない
- 他のFamily X Production E2EにTrial仕様を混入させない
- 無関係な改善Trialを追加しない

commitを伴う作業は同時に1件のみとする。

### 10. Trial終了・PM Gate

Trial終了時、案1・案2・案1＋案2をそれぞれ以下に分類する。

- `REJECTED`
- `VALIDATED`
- `USER_DECISION_REQUIRED`

**VALIDATEDはProduction採用を意味しない。**

ユーザー承認なしに`APPROVED_FOR_PRODUCTION`へ変更しないこと。

新方式についてはProduction配線を行わず、結果を報告してSTOPする。

Fableは、実測ログ・Fact品質・B3品質・費用・Opusレビュー条件と照合して独立受入を行うこと。

最終報告では、**コスト削減の実力と品質への影響**を最初に示し、採否判断に必要な情報を簡潔に整理すること。

(ユーザー原文ここまで)

## KPI provenance欄(24節)
dry-run: `synthetic`/`reuse`(保存済み出力をstubとして使用、API 0)。E2E自己確認: No。

## Opus台帳更新(11-5)
`docs/pm/OPUS_FINDINGS_LEDGER.md` OF-RLCT-R-01〜16: 本委任で実装した項目は `FABLE_DECIDED→IMPLEMENTED` へ(ただしSSOT編集権なしのため**文案のみ**RESULT_PACKETに記載。後続commit委任で反映)。

## 事前指定Read一覧
1. `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/TRIAL_DESIGN_02.md` 全文(実装の正本)。`COST_ESTIMATE_02.md` §Stage/上限値、`cost_estimate_02.json`(guard定数の出典)。
2. 複製元(読取のみ、該当範囲): `er012_e_family_entertainment_two_level_runner_01.py:183-227`(`run_verification_for_topic`: model/reasoning/tools/schema/developer message/`search_usage`抽出)、`er003_v1_en_direct_vfl_01_generate.py:137-170,228-309`(Researcher/Verifier Prompt、`build_verification_prompt`、`build_verified_ledger_text`、AMBIGUOUS規約)、`er002_ja_web_research_r3.py:65-81`(検索ログ平坦化の現状=新ログはraw `response.output`から取る)、`er019_family_x_storyline_b3_fact_selection_01.py:38-250`(B3 Prompt/`FACT_ID_LINE_RE`/`_call_once(extra_note)`/`run_storyline_b3_selection`の検証・retry構造)、`er019_family_x_entertainment_production_runner_01.py:97-141,274-345`(Ledger loop、`compute_stage_cost_breakdown`、budget guardの算式)、`er005_cost_logger`相当(Grep `def install|def record` in `er005_*.py`)、`er053_b3_deterministic_producer_01.py:843-919`(`produce_annotated_b3`の書込み先)、`er053_b3_annotation_contract_01.py`(Grep `def validate_annotated_b3`)、`er053_risk_flagger_production_01.py:166-196`(`parse_ledger_complete`)、`routing`(Grep `def require_model|WRITER_MODEL|FAMILY_X_STORYLINE_B3` in `er0*routing*.py`)。
3. 入力データ(読取のみ): 5記事の保存成果path(`ASSET_INVENTORY_01.md`の表から: `er019_output/coffee_prices/run_fxpw_01`、er052 stage_r の `inbound_tourism`/`streaming_price`/`openai_copyright`/`central_bank_mortgage` の各 run dir)。各dirの `research_ledger/`(draft json・verified_fact_ledger.txt・audit/verification_full_record.json)・`storyline_b3/`(selected_brief.md・fact_selection_evidence.json)・`raw_usage_log.jsonl`。
4. `er005_output/cost_baseline_01/pricing_snapshot.json`(単価)。

## 事前指定Grep一覧+追記位置・更新位置の手順
A. 実装(新規ファイルのみ。設計v2 §4-2/4-3/4-5/4-7/4-8に従う):
  - `er082_rlct_trial_01_lib.py`: (1)`verify_facts_trial(draft, fact_ids, prompt_text, out_dir, cap_per_fact=None)`=Production `run_verification_for_topic`の複製(model=`vfl01.MODEL`、reasoning/tools/schema/developer message同一、Promptのみ引数、raw responseの`web_search_call`を1件ずつ `web_search_calls.jsonl`[seq/action.type/queries/url/status]へ保存、`response.model`を記録)。(2)上限付きVerifier Prompt=既存`VERIFICATION_PROMPT_TEMPLATE`の複製+末尾に設計v2の上限指示文(Fact当たりweb_search呼出3回以内、超えたらAMBIGUOUS+理由。既存AMBIGUOUS規約と整合)。本文の差分はこの追加文のみ(diffをevidenceに保存)。(3)`select_b3_trial(ledger_text, out_dir, extra_note=None, allow_unverified=False)`=`run_storyline_b3_selection`と同じ検証・retry構造の複製、`FACT_ID_LINE_RE`相当を`[UNVERIFIED]`対応、`routing.require_model("FAMILY_X_STORYLINE_B3")`経由。(4)案2 loop `select_then_verify(draft, out_dir, max_reselect=2)`: 初回B3(全候補`[UNVERIFIED]`+Researcher`ambiguity`欄)→選定Factのみ検証→REJECTEDがあれば候補本文から外しextra_noteに理由+選定禁止+検証済みverdict一覧+未検証候補一覧→再B3→新規選定のみ検証(検証済みは再利用: key=fact_id×draft sha)→最大2回→未成立は`unresolved.json`で記録し確定ファイルを出さない。REJECTED IDが再選定されたら技術的失敗として記録。(5)最終Ledger=選定Factの検証済み分のみ `vfl01.build_verified_ledger_text` で組立。(6)予算guard: `cl.install("er082_output/rlct_trial_01/raw_usage_log.jsonl")`をプロセス開始時に必ず実行、呼出ごとに `compute_stage_cost_breakdown`同算式(web_search込み)で累計し、Stage上限(1a 493/1b 493/任意A 54)と累計上限1,040の両方で判定、超過見込みで例外STOP(確定ファイルを出さず`STOP_BUDGET.json`)。(7)入力複製: `copy_inputs(src_run, dst)`で draft/ledger/B3/evidence を `er082_output/rlct_trial_01/<article>/_inputs/` へ複製、以後は複製のみ参照。(8)整合: `sha_manifest(paths)`でProductionコード群+再利用成果物のsha一覧を実行前後に取り比較(`integrity_before/after.json`)。(9)Fact Lock/RF整合はJPY0: 複製dir上で `produce_annotated_b3`→`validate_annotated_b3`、`parse_ledger_complete`(RFのroot/出力は必ずer082配下)。(10)R-07測定: Storyline行が言及するFact(中心Fact)を抽出し、AMBIGUOUS Factを断定している件数を記録。(11)モデル記録: 各呼出の`response.model`、B3返却model。
  - `er082_rlct_trial_01_run.py`: CLI `--article <name> --method M0|M0b|M0p|M1|M2|M3 --stage 1a|1b|optA --dry-run`。`--dry-run`はAPIを呼ばず、stub応答(保存済み`verification_full_record.json`や`fact_selection_evidence.json`から合成)でパイプライン全体(複製→Prompt組立→ログ保存→予算計算→Ledger組立→契約検証→集計)を通す。
  - `er082_rlct_trial_01_inject.py`(任意A): M0/M0bの採用Factから数値・scope・日付を1か所改変した複製Factを2〜3件/記事生成(`_inputs/injected_facts.json`、元draftは不変)、上限なし/上限付きVerifierで検証、期待REJECTED。dry-runのみ本委任で実施。
  - `er082_rlct_trial_01_aggregate.py`: 記事×方式の表(費用[LLM/web_search別]、呼出数・クエリ数[種別別]、verdict遷移、選定Fact、Jaccard、再選定回数・費用、中心Fact断定件数、契約検証)をmd/jsonへ。
  - test `er082_rlct_trial_01_test_01.py`: (a)Production関連ファイルsha不変、(b)Trial Verifier Promptが既存Promptと上限文以外同一、(c)`[UNVERIFIED]`対応regex、(d)web_search 1回が費用に計上される(stubのusageで)、(e)REJECTED再選定の検知、(f)再選定上限到達で確定ファイルを出さない、(g)入力複製後に元dirへ書込みが無い(mtime/sha)、(h)budget guardがStage上限で止まる、(i)RF/producerの出力先がer082配下、(j)dry-runが5記事×4方式で完走。
B. dry-run実行(JPY0): 5記事×(M0/M0p/M1/M2/M3)+任意Aを `--dry-run` で実行、出力 `er082_output/rlct_trial_01/_dryrun/`。`integrity_before/after.json`一致、API呼出0(`raw_usage_log.jsonl`に課金行なし)を確認。
C. R-09 pricing確認: ネットワーク不可のため `pricing_snapshot.json` とrepo内の既存記録(Grep `web_search_call|open_page|per 1,000` in `er005_*.py`・`docs/`)のみで確認し、課金単位が確定できなければ「未確認」と記録、上限は種別ごとに記録する設計(設計v2どおり)。
D. 文案(編集はしない): DECISION_LOG(承認原文sha、CP1完了、Status)、OPEN_ITEMS OPEN-403(承認・CP1)、REGISTER #104=判断済み(承認(b)+任意A、上限1,040)、REPORT_LEDGER行、Opus台帳 R-01〜16→IMPLEMENTED、ACTIVE_TASK行。

## 実行コマンド全文
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_04.md --json-out docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_04.md_check.json`
- STOP確認: `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 --run-dir er082_output/rlct_trial_01`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er082_rlct_trial_01_test_*.py"`
- dry-run: `.venv\Scripts\python.exe er082_rlct_trial_01_run.py --dry-run --all-articles --all-methods --out er082_output/rlct_trial_01/_dryrun`(引数設計は上記Aに合わせる。全記事×全方式を1コマンドで回せるオプションを設ける)
- 任意A dry-run: `.venv\Scripts\python.exe er082_rlct_trial_01_inject.py --dry-run --article coffee_prices --out er082_output/rlct_trial_01/_dryrun/optA`
- secret scan: `.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(hits=0。add/commitはしない)
- 有料API・git書込みは一切実行しない。

## SSOT追記文
(編集権なし。文案のみ上記D。)

## Git(明示add対象・コミットメッセージ・trailer)
- **本委任ではgit書込みを行わない。** RESULT_PACKETに「commit対象ファイル一覧」(er082_*.py 4〜5本+test、`er082_output/rlct_trial_01/_dryrun/`の記録json/md、delegation_log 2件+_check.json、BAPE 委任_01の未commit分は含めない[別委任])とcommit message案「FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_04: ユーザー承認(b)+任意A保存+Trial専用harness実装(複製Verifier/B3・案2再選定loop・web_search込み予算guard・入力複製・整合sha・任意A注入)+JPY0 dry-run全記事×全方式PASS(Production不変)」を記載。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_RLCT4.md`(25行程度): T-0 2行(委任文全文保存の有無を正直に/承認原文path・文字数・sha)/実装ファイル一覧と設計v2の節対応(R-01〜16の実装状況表: 実装済み/dry-run検証済み/有料時に検証)/Trial Verifier Promptの差分(上限文全文)/test結果(a〜j)/dry-run結果(記事×方式の完走、API呼出0、integrity一致)/R-09 pricing確認結果/予算guard定数(1a 493/1b 493/optA 54/累計1,040)/Stage 1a実行コマンド案(次委任用、全文)/本日費用(確定約43.7+S3W進行中)/設計からの逸脱・未実装(あれば理由)/commit対象一覧・SSOT文案/4行(①既存仕様整合 ②Production到達経路の未承認機能=なし[er082は非接続、Grepで`er082`参照がProductionに無いこと] ③最終成果物・目的適合 ④撤去・残置=なし)/`判定整合:`行/判断候補(なし想定)/使用モデル(dry-runはAPIなし、本番想定モデル記載)。

## Fable自己チェック(送信前)
- [x] Read一覧に行範囲/Grepパターンあり [x] 追記位置手順あり [x] コマンドに引数実値あり [x] 禁止事項・費用(JPY0、guard定数)あり [x] 並行衝突回避(git書込み禁止・S3W path不可触)あり [x] Opus Gate判定(条件A済み・範囲内実装)あり [x] 時間見込みあり [x] 継続委任(前委任QDC: 設計v2完了・JPY0・次=CP1)
