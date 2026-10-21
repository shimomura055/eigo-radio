# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_01(過去Trial事前Gate→[否定的結果なしの場合のみ]設計→Trial専用harness→既存記事A成果物での検証[丸める/丸めない]→B3不変・Writer伝達・Fact Safety検査→仕様変更案→Trial記録。到達上限=`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`の材料[最終ラベルはFable]。VALIDATEDでもProduction採用・配線はしない)。
並行agent: `FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_07`(読み取り調査)。SSOT共有プロトコル(OPEN_ITEMS新規行/REPORT_LEDGER/ACTIVE_TASK: 編集直前`git status --porcelain`+再Grep→自分の行だけ→即add/commit、index.lock 30秒待ち)。**`git add -f`は絶対に使わない**(ACTIVE_TASK/RESULT_PACKETはgitignore対象のままローカルのみ)。

## 性質/到達上限Status/禁止事項
- 性質: Trial(Trial専用経路、ProductionのPrompt・コード・routing変更禁止)。目的=「機械的に選定済みの中核数値について、厳密値維持か概数化かをB3が判断し、Writerへ正確に伝える」機能の**必要最小限の仕様変更案を確立**。
- 変更許可範囲(ユーザー§3の表を厳守): Research/Ledger=禁止、B3のFact選定・優先順位・構成判断=禁止、中核数値の機械選定・件数上限・優先順位=禁止、**選定済み中核数値の丸め要否判断=唯一の新機能**、B3→Writer伝達=丸め判断を伝える最小変更のみ、Writer執筆仕様=新情報受け取りの最小接続のみ、Fact Checker/Validator=禁止、Production経路=禁止。構成は「Fact選定+中核数値マーキングを固定した後に丸め判断を実行」。
- 費用: 見積=丸め判断LLM(B3と同モデルgpt-6.1-sol、記事A 1回+丸めないケース数件≒JPY3〜8)+Writer R0→R2再生成(丸め情報あり、既存R0入力を固定して比較、約JPY13)+Adv/Std英語化(約JPY1)+Fact Checker/Ledger Deviation Checkerの実行(約JPY1〜3)=**約JPY20〜30**。T-3 Guardrail=**JPY100**。承認区分C。日次はS0で実測。TTS/ASR/Research/新規テーマは禁止。
- 最新モデル原則(25節): 丸め判断・Writer=Productionと同一(gpt-6.1-sol)[比較目的]。評価LLMを使う場合は最新上位系で明記。
- Opus(11-3): 本委任では呼ばない(Fableが仕様変更案に対し条件A/Cレビューを別途実施)。
- STOP条件: §2事前Gateで「今回の方式に関係する否定的検証結果」(丸めによるFact NG・意味変化・誤検知・意図しない文章変更、REJECTED案、矛盾する正式仕様)が見つかった場合はTrialを**開始せず**、内容・原因・今回への影響・対応案を報告(Trial設計書に記録してcommit、有料呼出0)。Guardrail超過見込み、Trial中に新仕様判断が必要になった場合もSTOP。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準(SSOT全文読込禁止)。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_委任_01.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_01」を含む最新index)。check結果1行。T-2: TTSなし。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
# Claude Code指示：Family X 中核数値の丸め判断 Trial

**管理ID：FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01**

## 1. 目的

Family XのB3に、**機械的に選定された中核数値について、厳密値を維持するか、概数化するかを判断する機能だけを追加**する。

Trialのゴールは、この機能を実現するための**B3の必要最小限の仕様変更案を確立すること**。

B3の既存のFact選定・構成判断・その他の機能は変更しない。

## 2. 最優先：過去Trial調査（事前Gate）

**新規Trial開始前に、必ず過去の類似Trial・承認仕様を確認すること。**

対象：
- 数値丸め・概数化・Numeric Precision関連Trial（特にTrial-18〜20）
- B3 Fact選定・中核数値マーキング関連Trial
- Fact Checker／Ledger Deviation Checkerによる数値変更の検証
- 過去の失敗事例、REJECTED案、未解決Open Item

確認事項：

1. 過去に同様の方式を検証していないか。
2. 丸めによるFact NG・意味の変化・誤検知・意図しない文章変更が発生していないか。
3. 過去の否定的結果が今回の設計にも当てはまるか。
4. 既存の正式仕様と矛盾しないか。

**STOP条件：今回の方式に関係する否定的な検証結果が見つかった場合、Trialを開始せず、内容・原因・今回への影響・対応案をユーザーに報告する。**

否定的結果がなければ、追加承認を待たず次工程へ進む。

## 3. Trialの変更許可範囲

| 工程 | 変更可否 |
|---|---|
| Research／Verified Fact Ledger | 変更禁止 |
| B3のFact選定・優先順位・構成判断 | 変更禁止 |
| 機械による中核数値選定・件数上限・優先順位 | 変更禁止 |
| **選定済み中核数値の丸め要否判断** | **今回の唯一の新機能** |
| B3 → Writerの情報伝達 | 丸め判断を伝える最小限の変更のみ許可 |
| Writerの既存執筆仕様 | 変更禁止（新情報の受け取りに必要な最小限の接続のみ可） |
| Fact Checker／Validator | 変更禁止 |
| Production経路 | 変更禁止 |

特に、B3のFact選定結果を新しい丸め判断に影響させたり、丸め判断を理由に中核数値の選定結果を変更したりしないこと。

現行では中核数値のマーキングがB3のFact選定後に行われるため、**選定結果を固定した後に丸め判断を実行する**構成を基本とする。

既存の決定論producerの動作は維持し、必要最小限の追加処理で実現すること。実装手段はQCDを踏まえて判断してよい。

## 4. 丸め判断の基本原則

- 数字の精度自体が重要でない場合、聞き取りやすい概数を優先する。
- 正確な数値が意味・比較・判断に必要な場合は厳密値を維持する。
- 異なるFact・指標・集団・時点・調査項目の統合は禁止。
- Verified Fact Ledgerの正確な数値は変更しない。
- 数字の意味、比較方向、閾値、結論、確信度を変えない。
- 判断が不確かな場合は無理に丸めず、厳密値を維持する。

既存の承認済みSpoken-first Number Treatment／Listener-Friendly Numeric Precisionと整合させ、新しい品質基準を独自に追加しないこと。

## 5. Trial対象

### A. 丸めるべきケース

今回の記事A「給料が上がると、性格も変わる？」を使用する。

対象例：

- 原文：`134,515 people`
- 期待する判断：`APPROXIMATE_OK`
- 期待する表現例：`about 135,000 people`

ただし、元Factの「最大標本数」「解析ごとに人数が異なる」という意味を維持すること。

概数化後も、事実性・表現の自然さ・聞き取りやすさを評価する。

### B. 丸めてはいけないケース

過去Trial・既存Ledgerから、厳密値保持が必要な事例を選ぶ。

例：
- 法律・制度・安全基準などの閾値
- 比較結果が変わる僅差
- 精度そのものに意味がある研究結果
- 丸めによって異なる数値を同一視してしまうケース
- 日付・回数など、正確さが記事の意味に直結するケース

過去の実例を優先し、必要な場合のみ最小限の検証用fixtureを追加する。

**丸めるケース・丸めないケースの双方を検証すること。**

## 6. 評価項目

### ① 丸め判断の妥当性

- 丸めるべき数字が適切に概数化される。
- 丸めてはいけない数字は厳密値を維持する。
- 元Factの意味が変わらない。

### ② B3 → Writerの伝達

- B3の判断内容がWriterへ正しく渡る。
- Writerが指定に従い、意図した数値表現を使用する。
- 丸め指示が欠落・重複・誤適用されない。

### ③ 変更範囲の限定

同一のB3 Fact選定結果・中核数値選定結果・Writer入力を使用し、丸め判断追加前後を比較する。

- 採用FactのID・件数・順序が一致する。
- 中核数値の対象・件数・順序が一致する。
- B3のその他の情報が変化しない。
- Writerへ渡す情報の差分が丸め判断に限定される。
- Writerの出力に数値表現以外の意図しない変化がない。

B3出力・Writer入力の構造的な差分検査を必須とし、Writerの自然言語出力については意味上の差分を確認する。

### ④ Fact Safety

既存のFact Checker／Ledger Deviation Checkerで、丸めによる事実逸脱がないことを検証する。

単なる文字列差分と、意味が変わるFact差分を区別すること。

## 7. 実行方法とQCD

- 既存の記事AのResearch Ledger・B3・Writer成果物を最大限再利用。
- 過去のTrialで使用した厳密値保持ケースを再利用。
- APIを使う前に、既存の成果物だけで検証可能な部分を実施。
- 独立した検証は並列化。
- 新規Research、記事テーマ追加、音声生成、ASR実行は不要。
- Trial用経路に限定し、ProductionのPrompt・コード・routingは変更しない。
- 既存の承認済み開発予算内で進め、API費用と実行回数を記録する。
- 必要十分な品質に達した時点でTrialを終了し、追加の磨き込みをしない。

## 8. Trial終了Gate・報告

Trial結果は次のいずれかに分類する。

- `VALIDATED`：丸め判断とWriter伝達が期待どおり機能し、その他の仕様に影響しないことを確認。
- `REJECTED`：期待品質を満たせず、採用に適さない。
- `USER_DECISION_REQUIRED`：仕様上の判断・追加承認が必要。

報告は次の順序とする。

1. 過去Trial調査結果（否定的事例の有無）
2. Trial結果と最終Status
3. 丸めたケース・丸めなかったケースのBefore／After
4. B3の数値判断とWriterへの伝達結果
5. Fact選定・中核数値選定・その他のB3情報が不変である証拠
6. Fact Safetyの検査結果
7. 仕様変更案（追加・変更した箇所を明示）
8. QCD（品質、実行時間、Trial費用、量産単価への見込み影響）
9. 残存課題とProduction採用に必要なユーザー判断

CURRENT_SPEC・DECISION_LOG・OPEN_ITEMSとの整合も確認し、Trial記録をGitに保存する。

**VALIDATEDでもProduction採用・配線は行わない。正式採用はユーザー判断待ちとする。**

## 9. 最重要の受入条件

**今回の変更で達成することは「機械が選んだ中核数値を、B3が必要に応じて丸める判断を行い、Writerへ正確に伝えること」だけ。**

B3のその他の役割・判断・出力内容、既存の中核数値選定ロジック、Fact Safetyの基準は変更しない。

この範囲で、必要最小限の仕様変更案を完成させること。
--- 原文ここまで ---

## 手がかり(鵜呑みにせず原文で確認)
- 中核数値の仕組み: `docs/research/FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01/CORE_NUMBER_QUERY_01.md`(委任_07回答: 決定論producer `er053_b3_deterministic_producer_01.py:420-549`[適格・cap・優先順]、注記md/sidecar、W-1 R0規則:86-93「【中核数値】の数字だけ使える」、R1/R2に数字規則なし、周辺数値Gate化は不採用=DECISION_LOG:20547、producer v2承認=CURRENT_SPEC:1177、B3 Fact選定=`er019_family_x_storyline_b3_fact_selection_01.py`)。
- 記事A成果物: `er019_output/paycheck_personality/run_pp_01/`(`research_ledger/verified_fact_ledger.txt` F04、`storyline_b3/`[selected_brief.md、selected_brief_annotated.md、sidecar/annotation.json、annotation_manifest.json、fact_selection_evidence.json]、`ja_writer/`[factlock/r0.md、r1/r2、Prompt dump]、`b1b/article.md`・`a2/article.md`、Fact Checker/LDC結果[`audit/fact_check.json`等])。
- 過去Trial(事前Gate対象): CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/`docs/research/`/`ER-*_REPORT.md`をGrep: `丸め|概数|Numeric Precision|Spoken-first|Listener-Friendly|Trial-18|Trial-19|Trial-20|rounding|approximate|about 1`、`Fact Checker.*数値|Ledger Deviation|数値.*NG|数値逸脱`、B3関連(`er052_output/b3_rootfix_trial_02/`、`FACTLOCK`、`中核数値`、`b_numbers`)。承認済みの「Spoken-first Number Treatment」「Listener-Friendly Numeric Precision」の正式仕様箇所(file:行)と、そこでの丸めの許容条件(例: 聞き取りやすさのための概数化が許される条件・禁止条件)を特定し、今回の方式と矛盾しないか判定。REJECTED案・否定的結果(丸めでFact NG、意味変化、誤検知、意図しない文章変更)の有無を列挙(各出典行)。
- Fact Checker/Ledger Deviation Checkerの数値扱い(`er003_*fact_check*`、`ledger_deviation`、許容=概数表現を同一Factと認めるか、"about 135,000"が"134,515"のLedgerに対しOKかNGかの現行規則)。これはTrial設計の前提(丸めた本文がFact SafetyでNGになるなら、是正は許可範囲外=USER_DECISION_REQUIRED材料)。

## 手順
S0. daily cost、`git status`件数、T-0・原文保存。
S1. **事前Gate**(API 0): 上記Grepで過去Trial・承認仕様・Fact Checker規則を調査→`docs/research/FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01/PRIOR_TRIAL_GATE_01.md`(ユーザー§2の確認事項1〜4、21節A/B/C分類、否定的結果の有無と今回への当てはまり)。**否定的結果あり→STOP**(commitして報告、有料呼出0)。なし→S2へ。
S2. 設計(`TRIAL_DESIGN_01.md`、有料前にcommit): (a)挿入位置=決定論producerの注記完了後、Writer R0入力生成前(Trial専用wrapper、producer/B3選定/Writer本体は無改変)。(b)丸め判断=中核数値ごとに`EXACT_REQUIRED`/`APPROXIMATE_OK`(+概数表現候補、理由、根拠Fact ID)を出すLLM判定(gpt-6.1-sol、承認済みSpoken-first/Listener-Friendlyの原文条件をPromptに逐語引用、独自基準を足さない。不確実なら`EXACT_REQUIRED`)。概数表現はLedger数値から機械的に検証可能な範囲(例: 有効数字・上下限・「about/up to/as many as」等の修飾維持、「最大」「解析ごとに異なる」の意味語を落とさない)。(c)Writerへの伝達=注記md/sidecarへの**追加フィールドのみ**(例: `【中核数値】134,515人【概数可: about 135,000】`または sidecar `rounding: {...}`)。Writer R0 Promptの変更はこの注記を読む1文の追加に限定(Trial wrapperでPrompt末尾に差し込み、Production定数は不変)。(d)比較設計: 同一のB3選定結果・注記(Before)を固定し、丸め判断を付けたR0入力(After)でWriter R0→R1→R2→Adv/Stdを再生成。構造的diff(selected_fact_ids順序、中核数値対象・件数・順序、sidecarの他フィールド、Writer入力テキストのdiff=丸めフィールドのみ)をtestで固定。Writer出力の意味差分はLLM判定(最新上位系、ラベル伏せ)+Sonnet通読。(e)Fact Safety: 既存Fact Checker/LDCをAfter本文に実行(Trial専用out_dir)。(f)丸めないケース: 過去Trial/既存Ledgerから実例(閾値・僅差比較・精度が意味を持つ研究値・同一視リスク・日付/回数)を3〜5件選び(記事Aの他の中核数値「11件」「3回以上」「0.0630」も含める)、丸め判断のみ実行(Writer再生成はしない)。
S3. 実行: 判断LLM(記事A+丸めないケース)、Writer再生成(After 1回)、Adv/Std、Fact Checker/LDC、意味差分判定。費用・時間を記録。
S4. 評価(ユーザー§6①〜④)と仕様変更案(§8-7: 追加・変更箇所をfile:行/フィールド名/Prompt文で明示、Production適用時の最小diff見積、量産単価影響=判断LLM 1呼出/記事≒JPY0.3〜1推定を実測で)。
S5. 記録: `TRIAL_RESULT_01.md`(§8の1〜9順)、OPEN_ITEMS新規行(Status `TRIAL_DONE_PENDING_FABLE`)、REPORT_LEDGER、ACTIVE_TASK(ローカル)。secret scan→明示add(docs/research/..., `er090_b3_core_number_rounding_trial_01_*.py`, `er090_output/...`, delegation_log)→commit→`git push origin HEAD:main`。CURRENT_SPEC/DECISION_LOGは変更しない(採用判断後)。

## 報告(docs/pm/RESULT_PACKET_B3RD1.md 上書き。ユーザー§8の1〜9の順。Sonnetは「判断候補」表記、Statusラベルは付けない)
STOP時(事前Gate該当)は1のみ詳細+対応案。