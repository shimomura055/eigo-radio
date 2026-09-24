## 管理ID

`NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`(初回委任)。並行タスクなし。一時ファイルは標準名`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`を上書きしてよい(ヘッダの「APPROVED未配線」に`NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`、「UDR-deferred」に`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`(full_story_part2処置・配線先判断待ち)を保持)。

## 性質/到達上限Status/禁止事項

- 性質: 原因切り分けTrial(日本語のみ)。「Entertainment性低下の原因が参照情報の量か、Ledger形式か」を4条件×3段(Original→R1→R2)で比較。到達上限Status=`VALIDATED`。良い結果でもProduction採用へ進めない。
- 禁止事項: Production Writer Prompt/Production wiring/英語版再Trial/Hook採用/Audio生成/Search方式改善/Ledger Gate改修/Fact Check仕様変更/retry・fallback設計変更を行わない。Production code・SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)を変更しない。既存`er015_*`/`er016_*`/`er017_*`scriptを変更しない(import/複製のみ)。
- **Writer Promptは4条件で完全同一**(前回VALIDATEDのP7逐語)。「Factを減らせ」「Ledgerを無視せよ」「面白いFactだけ選べ」「情報が多い場合の特別ルール」等、結果を誘導する追加指示は禁止。R3を生成しない。
- 品質の主観評価・順位付けはSonnetが行わない(観察事実・機械集計のみ。評価はFable)。
- 費用上限¥40(Writer 12 call+Ledger変換1 call。Web検索は10記事に満たない場合の補充のみ、Luna web_search最大2 call)。
- `git add -A`/`stash`/`amend`禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

(2026-09-24、管理ID `NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`。要点抜粋。全文は本委任文末尾【ユーザー指示全文】としてdelegation_logへ保存)
- 「MetaのAI電話記事を対象に、Entertainment性が落ちた原因が参照情報の量なのか、Ledger形式そのものなのかを切り分ける。今回のTrialは日本語記事のみで行う。」
- 「最重要: 条件(2)は前回再現。過去の日本語Meta Muse Trialを確認し、Writerへ実際に何件分の元情報・要点を渡していたかを事実確認する。前回が2件なら2件、3件なら3件。推測で3件に固定しないこと。可能な限り前回と同じ情報量・粒度・入力形式を再現するBaselineとする。」
- 「条件1: 1記事分の少量の元情報・要点だけ。条件2: 前回Baseline。条件3: 10記事分の少量の元情報・要点(各記事全文ではなく条件1・2と同程度の少量の要点として揃える)。条件4: 条件3で使用した同一10記事だけを材料にLedgerを作る。別Sourceを追加しない。条件3と4はSource集合は同じで、違うのは形式だけになるようにする。」
- 「Source選定: 既存Trialで使用済みのSource・検索結果・Research artifactを優先的に再利用。不足時のみ検索してよい。新しい面白い切り口探し/Source数を無駄に増やす/関係の薄い関連記事を混ぜることはしない。10記事条件では同一事象について事実補完できる記事を使う。」
- 「Ledger条件: 可能であれば既存Verified Fact Ledger生成primitiveを使う。ただし目的はLedger形式に変換したことでEntertainment性が変わるかを見ることなので、条件3と4で情報集合が大きく変わらないことを優先する。Ledger作成のために別Sourceを追加する必要がある場合はSTOPして報告。」
- 「Writer Prompt: 前回VALIDATEDした日本語Entertainment Promptをそのまま使用。4条件で完全同一。生成方法: Stage 0 Original→Stage 1 R1→Stage 2 R2。前回と同じRevision方式。R3は生成しない。model/effort/revision instructionも前回日本語Trialと揃える。」
- 「評価方法: 生成前に正解を決めつけない。4条件のR2を横並びで比較。可能なら記事全文を伏せた識別子A/B/C/Dでも一度比較する。」
- 「Fact Safety: 架空のFact追加禁止。Source外の固有名詞・数字・出来事・因果関係・発言の追加がないか確認。」
- STOP条件: 「条件2の前回入力数・入力形式を確認できない/条件3と条件4で同一10記事を維持できない/Ledger生成に別Source追加が必要/前回Entertainment Promptを特定できない/前回Revision条件を再現できない/Source自体に重大な矛盾がある/Trial途中で新仕様判断が必要になる。複数の代替Trialを勝手に始めない。」
- 「QCD: 可能な限り既存artifact/Source/Promptを再利用し、不要なWeb Search・Audio・Validatorを実行しない。完了後はSTOPし、ユーザー判断を待つこと。」

## 事前指定Read一覧

- `er015_output/news_iterative_entertainment_trial_02/sources.md`: 全文(**前回Article Aの入力=何Source・何文・どの粒度・どの形式**を事実確認する根拠。URL・取得方法・`[ニュース]`欄に実際に入れた文を特定)。
- `er015_news_iterative_entertainment_trial_02.py`: Grep `MATERIAL|sources|\[ニュース\]|テーマ|def build_prompt|THEME|effort|previous_response_id|REVISION`→該当範囲(Promptへの素材挿入の正確な形式[テンプレート]、model/effort、R1/R2逐語、連鎖実装)。
- `er015_output/news_iterative_entertainment_trial_02/api_meta_A_original.json`(またはA相当のapi_meta): Grep `"input"|"user"|prompt`→実際に送ったuser message全文(素材部分の逐語確認。長ければ該当範囲のみ)。
- `docs/evidence/news_iterative_r2_adoption_2026-09-24/prompts.md`: AI電話版Original Prompt逐語・developer・R1/R2指示(前回条件の正本)。
- `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/ai_phone_revision2.md`: 全文(前回R2、比較表用。Promptへは入れない)。
- `er017_output/news_entertainment_production_line_trial_01/ledger/verified_fact_ledger.txt`: 全文(Ledger形式の正本[fact_id/scope/numeric_value/causal_strength等の行形式]と、Source URL一覧[10記事候補の第一候補])。
- `er017_output/news_entertainment_production_line_trial_01/ledger/`配下のresearch raw(Grep `url|source`→URL一覧のみ)。
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `RESEARCHER_PROMPT|LEDGER_FORMAT|def format_ledger|fact_id|canonical|def render_ledger`→Ledger本文の行形式・フィールド定義のみ(呼び出しはしない。形式を条件4のLedger変換で忠実に再現するため)。
- `er015_news_iterative_entertainment_trial_01.py`: Grep `def call_with_previous_response_id`→連鎖関数(流用)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna/web_search単価行。
- `docs/pm/PM_BRIEF.md`: 行151-175。

## 事前指定Grep一覧+追記位置・更新位置の手順

### Step 0 前回Baseline確認(STOP判定)
- sources.md/api_meta/scriptから、前回Article Aの`[ニュース]`欄に入れた**Source数・文数・文字数・要約粒度(原文引用か要約か)・形式(箇条書きか段落か)**を確定し`baseline_evidence.md`に根拠(ファイル:行、逐語)付きで記録。確認できなければSTOP。
- 前回Prompt(P7逐語)・developer・R1/R2指示・model(gpt-5.6-luna)・effort(high)・連鎖方式が特定できることを確認。できなければSTOP。

### Step 1 Source収集(既存artifact優先)
- 候補URL: TRIAL-02 sources.md(Reuters/marketscreener)+Phase B LedgerのSource URL+research raw内URL。同一事象(Meta Muse電話代行の人間コンシェルジュ試験、2026-09-22 Reuters報道)を扱う記事を優先。関係の薄い記事(Muse発表一般記事等)は「事実補完できる」場合のみ。
- 各URLをHTTP取得(Python requests、403時はTRIAL-02と同じreader proxy `r.jina.ai`フォールバック可、使用したら記録)。取得できた本文から**各記事2〜3文の要点**(条件2と同じ粒度・同じ形式)を作る(Sonnetが機械的に要約するのではなく、Luna 1 call・effort medium・「各記事の内容を、与えられた本文にある事実だけで2〜3文に要約」で生成してもよい。使った方法を記録)。
- 10記事に満たない場合のみLuna web_search最大2 callで補充(検索クエリ・結果URLを記録)。10記事に到達できなければSTOP(到達数と理由を報告)。
- `sources_10.md`: #、URL、媒体、取得方法、取得日時、要点2〜3文、条件1/2/3での使用有無。

### Step 2 4条件の入力を確定(`inputs/cond{1,2,3,4}.md`)
- 条件2: 前回`[ニュース]`欄の文を**逐語**再現(Step 0の根拠どおり)。
- 条件1: 条件2のSourceのうち中心記事(Reuters原記事)1件だけの要点。条件2が既に1記事由来なら、条件1=その記事の中心要点のみ(条件2より少ない文数、例1〜2文)とし、その差を明記。
- 条件3: 10記事×要点2〜3文(条件2と同じ形式で列挙。記事ごとに媒体名を付す)。
- 条件4: 条件3と同じ10記事の**取得本文**を入力に、Luna 1 call(effort medium、web_searchなし)で「与えられた本文にある事実だけを、以下のLedger形式(Phase B Ledgerと同一の行形式・フィールド)で列挙。本文にない事実・推測を加えない。検証(verification)は行わず`status: TRIAL_UNVERIFIED`と付す」→`ledger_cond4.txt`。別Source追加は禁止(必要ならSTOP)。fact数・Source URL集合が条件3と一致することを機械確認(URL集合の差=0)。条件3要点と条件4 Ledgerの情報集合の差(Ledgerにのみある事実/要点にのみある事実)を機械抽出し`info_set_diff.md`へ(観察事実)。

### Step 3 生成(4条件×3段=12 call、条件間は独立)
- developer/Original Prompt=P7逐語(prompts.md AI電話版)。`テーマ：`=前回と同一文、`[ニュース]`欄=各条件の入力(挿入形式は前回scriptのテンプレートと同一)。model=`gpt-5.6-luna`、effort=high、web_searchなし。
- R1/R2: `previous_response_id`連鎖、userは修正指示逐語のみ(前回と同一)。R3なし。
- 保存: `cond{n}_original.md`/`cond{n}_revision1.md`/`cond{n}_revision2.md`、`api_meta_cond{n}_stage{s}.json`(`response.model`・response_id・previous_response_id・usage[input/output/reasoning]・latency・cost)、`titles.json`(条件×段)。
- 機械集計: 文字数、比喩系統数はSonnetが判定しない。代わりに: 固有名詞・数字の出現数(条件×段)、Prompt復唱「これ、ちょっと面白くない？」の有無(条件×段、OPEN-175)、段落数。→`mechanical_stats.json`。
- Fact機械観測: 各記事の固有名詞・数字・引用符内発言を抽出し、その条件の入力(条件4はLedger)に存在しないものを列挙→`fact_diff_machine.json`(判定はFable)。

### Step 4 評価用資料
- `blind_r2.md`: 4条件のR2全文を**ランダムなA/B/C/D**で並べる(条件名・入力を書かない)。対応表は別ファイル`blind_key.json`(Fableはblind_r2.mdを先に読む)。
- `comparison_all.md`: 条件×段の全文+前回R2(参照)+タイトル一覧。
- REPORT `NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01_REPORT.md`: §1 前回Baseline確認(根拠)/§2 Source一覧・4条件入力全文/§3 条件4 Ledger全文+情報集合差/§4 Prompt・Revision指示全文・model/effort/連鎖/§5 各条件Original/R1/R2全文・タイトル/§6 機械集計・Fact機械観測/§7 api_meta・cost・latency/§8 Fable記入欄(4条件結果・比較A/B・原因仮説・次に検証が必要なこと・Status)`[Fable記入]`/§9 Production変更なし宣言。

## 実行コマンド全文

```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er015_news_meta_source_volume_format_trial_01.py --out-dir er015_output\news_meta_source_volume_format_trial_01 --step baseline
.venv\Scripts\python.exe er015_news_meta_source_volume_format_trial_01.py --out-dir er015_output\news_meta_source_volume_format_trial_01 --step sources --target 10
.venv\Scripts\python.exe er015_news_meta_source_volume_format_trial_01.py --out-dir er015_output\news_meta_source_volume_format_trial_01 --step inputs
.venv\Scripts\python.exe er015_news_meta_source_volume_format_trial_01.py --out-dir er015_output\news_meta_source_volume_format_trial_01 --step generate --conditions 1,2,3,4 --stages 0,1,2
.venv\Scripts\python.exe er015_news_meta_source_volume_format_trial_01.py --out-dir er015_output\news_meta_source_volume_format_trial_01 --step assemble
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01.md --json-out docs\pm\delegation_log\NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01.md_check.json
git status --short
```
(新規script `er015_news_meta_source_volume_format_trial_01.py`。各stepはSTOP条件該当時に非0終了し理由を`stop_reason.json`へ。)

## SSOT追記文

なし。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `er015_news_meta_source_volume_format_trial_01.py`、`er015_output/news_meta_source_volume_format_trial_01/`(配下全て。取得した記事本文の全文は保存せず、要点・URL・sha256のみ保存[著作権配慮]。Ledger変換に使った本文は`fetched/`へローカル保存しcommit対象外=`.gitignore`追記はせず`git add`から除外)、`NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01.md`、同`_check.json`。
メッセージ: `NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01: Meta Muse日本語Entertainment記事で参照情報量(1/前回Baseline/10記事要点)とLedger形式(10記事Ledger)を4条件×Original→R1→R2で切り分け(Luna、Prompt同一、Production変更なし)`
trailer: `Management-ID: NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`
STOP時もそこまでの成果物をcommit(`STOP:`接頭)。

## 報告(RESULT_PACKET項目)

0. T-0結果。
1. 前回Baseline確認結果(Source数・文数・文字数・粒度・形式、根拠ファイル:行、逐語)。条件2での再現度(逐語一致か)。
2. Source 10記事一覧(URL・媒体・取得方法・要点)、補充検索の有無と内容、10記事に到達したか。
3. 4条件の入力全文(RESULT_PACKETにも転記)、条件4 Ledgerのfact数・URL集合一致・情報集合差の要約。
4. 12 callの`response.model`実値・連鎖確認・usage・latency・cost、合計(¥40以内か)。
5. `blind_r2.md`と`blind_key.json`の絶対パス(Fableはblindを先に読む)。`comparison_all.md`パス。
6. 機械集計(条件×段: 文字数・固有名詞数・数字数・復唱有無)、Fact機械観測の一覧。
7. Production/SSOT無変更の確認、`git status --short`、commit SHA、push結果。
8. 一覧外Read/Grepの理由、STOP該当の有無、懸念。

---
【ユーザー指示全文】(delegation_logへそのまま保存)

管理ID: `NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`

## 目的
MetaのAI電話記事を対象に、Entertainment性が落ちた原因が参照情報の量なのか、Ledger形式そのものなのかを切り分ける。今回のTrialは日本語記事のみで行う。Production実装・Production Prompt変更は行わない。

## 現在の問題
前回の日本語Entertainment Trialでは高いEntertainment性が確認できた。一方、直近の英語Production-line Trialでは、Verified Fact Ledger 18 facts全文をWriterへ渡した結果、Fact密度が高い/説明記事寄り/従来News記事との差が小さい/「一番面白い見方」に集中する力が弱い という問題が出た。ただし、情報量が多いことが原因なのか/Ledger形式が原因なのか/英語化やProduction構造が原因なのか はまだ切り分けできていない。今回はまず日本語へ戻し、情報量とLedger形式だけを比較する。

## テーマ
Meta Muse/AI電話。中心テーマ「AIに店への電話を頼んだら、裏では人間が話していた」。既存の日本語Entertainment Trialと同一テーマを使う。

## 最重要：条件(2)は前回再現
まず、過去の日本語Meta Muse Trialを確認し、Writerへ実際に何件分の元情報・要点を渡していたかを事実確認すること。前回が2件なら2件、3件なら3件。推測で3件に固定しないこと。条件(2)は、前回日本語Trialと可能な限り同じ情報量・粒度・入力形式を再現するBaselineとする。

## 比較する4条件
条件1: 1記事分の少量の元情報・要点だけをWriterへ渡す。条件2: 前回Baseline(前回日本語Entertainment Trialと同じ件数の元情報・要点。件数だけでなく、可能な限り前回と同程度の要約粒度・入力形式に合わせる)。条件3: 10記事分の少量の元情報・要点をWriterへ渡す(各記事全文をそのまま貼るのではなく、条件1・2と同程度の「少量の元情報・要点」として揃える)。条件4: 条件3で使用した同一10記事だけを材料にLedgerを作る。別Sourceを追加しない。条件3と条件4は、Source集合は同じ、違うのは「元情報・要点形式」か「Ledger形式」かだけになるようにする。

## Source選定
Meta Museの同一ニュース事象を扱うSourceを使う。既存Trialで使用済みのSource・検索結果・Research artifactを優先的に再利用する。不足時のみ検索してよい。ただし今回の目的はSource Discoveryではないため、新しい面白い切り口探し/Source数を無駄に増やす/関係の薄い関連記事を混ぜる ことはしない。10記事条件では、同一事象について事実補完できる記事を使う。

## Ledger条件
条件4のLedgerは、条件3で使った10記事からのみ作成する。可能であれば既存Verified Fact Ledger生成primitiveを使う。ただし今回の目的は、Ledger形式に変換したことでEntertainment性が変わるかを見ることなので、条件3と条件4で情報集合が大きく変わらないことを優先する。Ledger作成のために別Sourceを追加する必要がある場合はSTOPして報告。

## Writer Prompt
前回VALIDATEDした日本語Entertainment Promptをそのまま使用する。Prompt内容を改善・追加しない。特に、Factを減らせ/Ledgerを無視せよ/面白いFactだけ選べ/情報が多い場合の特別ルール など、今回の結果を誘導する追加指示は禁止。4条件でWriter Promptは完全同一。

## 生成方法
各条件について、Stage 0 Original/Stage 1 R1/Stage 2 R2 まで生成する。前回と同じRevision方式を使用する。R3は生成しない。model/effort/revision instructionも、可能な限り前回日本語Trialと揃える。

## 比較で見るもの
1. 最も面白い「見方」が一本に絞れているか 2. 説明記事化していないか 3. Factを並べる記事になっていないか 4. 冒頭で続きを聞きたくなるか 5. 比喩・見立てが自然か 6. RevisionでEntertainment性が上がるか 7. R2タイトルの強さ 8. 文章の軽快さ 9. 一度聞いて理解できるか 10. 不要なFactが本文に残っていないか

## 最重要比較
比較A: 条件1 vs 条件2 vs 条件3(元情報・要点形式のままでも、情報量が増えるとEntertainment性が落ちるか)。比較B: 条件3 vs 条件4(同じ10記事でも、Ledger形式に変換するとEntertainment性が落ちるか)。この比較が今回の核心。

## 評価方法
生成前に正解を決めつけない。「Ledgerは悪いはず」「情報量が少ない方が良いはず」という前提で評価しない。4条件のR2を横並びで比較し、どれが最も前回日本語Trialの品質に近いか/条件2が前回品質を再現したか/情報量増加の影響/Ledger化の影響 を分けて評価する。可能なら記事全文を伏せた識別子A/B/C/Dでも一度比較し、入力条件を知った評価との偏りを減らす。

## Fact Safety
今回も架空のFact追加は禁止。各記事について、Source外の固有名詞/数字/出来事/因果関係/発言 の追加がないか確認する。ただし今回の主目的はFact Check Gate評価ではなく、Entertainment性の切り分け。

## 保存物
条件1〜4の入力全文/使用Source一覧/条件2で再現した「前回入力件数」の根拠/条件3の10記事要点/条件4 Ledger全文/各条件のOriginal・R1・R2全文/各Stageのタイトル/Prompt全文/Revision指示全文/model_id/response_id・previous_response_id/token/latency/cost/Fact観測結果

## レポート
1. 前回Baseline確認(前回日本語Trialは何記事分の元情報だったか/条件2でどこまで再現できたか) 2. 4条件結果(Entertainment性/説明記事化の程度/見方の一本化/R2での改善度/タイトル品質) 3. 核心比較(1→Baseline→10記事で何が変わったか/10記事要点→10記事Ledgerで何が変わったか) 4. 原因仮説(Source数/情報量/Ledger形式/その他を分離して評価) 5. 次に検証が必要なこと(ただし追加Trialは勝手に実施しない)

## Status
開始時`TRIAL`。最大Status`VALIDATED`。Trial終了時に必ずREJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれかに分類する。良い結果でもProduction採用へ進めない。

## 非対象
Production Writer Prompt変更/Production wiring/英語版再Trial/Hook正式採用/Audio生成/Search方式改善/Ledger Gate改修/Fact Check仕様変更/retry・fallback設計変更

## STOP条件
条件2の前回入力数・入力形式を確認できない/条件3と条件4で同一10記事を維持できない/Ledger生成に別Source追加が必要/前回Entertainment Promptを特定できない/前回Revision条件を再現できない/Source自体に重大な矛盾がある/Trial途中で新仕様判断が必要になる。問題が出た場合、複数の代替Trialを勝手に始めない。

## QCD
今回の目的は原因切り分け。Production相当の重い後工程は不要。可能な限り既存artifact/Source/Promptを再利用し、不要なWeb Search・Audio・Validatorを実行しない。品質比較に必要な最小コストで実施すること。完了後はSTOPし、ユーザー判断を待つこと。
