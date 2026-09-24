## 管理ID

`NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`(Phase 0: Evidence保存+SSOT反映+Production経路recon)。並行タスクなし。一時ファイルは標準名`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`を上書きしてよい(前タスクNEWS-HOOK-MODEL-COMPARISON-01はcommit fd0d82a1済み)。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式判断(`APPROVED_FOR_PRODUCTION`)の記録・Trial Evidenceの正式保存・Open Item 2件起票・Production配線先の**read-only recon**。本Phase 0では**Production codeの実装・変更を行わない**(配線はFableがrecon結果を見てユーザー判断/次Phaseへ回す)。API呼出なし(費用¥0)。
- 到達Status: 本管理IDは`APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`(ユーザーが正式採用を宣言済み。`PRODUCTION_WIRED`はGate 3全項目充足まで宣言しない。Sonnetは`PRODUCTION_WIRED`と書かない)。
- 禁止事項: Production code(`er003_*`/`er006_*`/`er012_*`/`generate_test.py`等)・Prompt・Search/Topic Selection ruleの変更禁止。`er015_*`Trial scriptの変更禁止(読み取りのみ)。Open Item Aから「商品記事除外」等のProduction Selection Ruleを作らない。Open Item BでPromptを変更しない。`git add -A`/`stash`/`amend`禁止。R2/R3等Trial内呼称をCURRENT_SPEC本文で単独使用しない(Production上の意味を併記)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

(2026-09-24、管理ID `NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`。要点抜粋、全文はdelegation_logに本委任文末尾【ユーザー指示全文】として保存すること)
- 「News記事のEntertainment改善方式として、Original → Revision 1 → Revision 2 の逐次Revision方式を採用し、Production標準をR2とする。Statusを`APPROVED_FOR_PRODUCTION`へ変更する。これはTrial評価ではなく、Production正式採用判断。ただし、Gate 3をすべて満たすまでは`PRODUCTION_WIRED`としないこと。」
- 採用根拠: 「3テーマ(下水道/AI電話代行・Meta Muse/旅行荷物・圧縮ポーチ)で同一方式をTrial済み。3/3でR2が最良域、R3がR2を上回ったテーマは0、R3は共通して冒頭は改善するが本文では比喩・演出が増加、強いテーマでも地味な生活テーマでもR2が安定、R2までの費用・latencyは量産上許容可能。」
- 「最重要: Trial Evidenceを完全保存。なぜR2を選んだのかを後から完全に追跡できる状態にする。A. 使用Prompt(Original生成Prompt全文/developer message/R1・R2・R3修正Prompt全文/model・reasoning設定/previous_response_idによる連鎖方式)。Promptを要約だけで残さない。実際に使用した逐語Promptを保存する。B. 全生成記事(3テーマ×Original/R1/R2/R3=12記事全文)。C. 比較・判断Evidence(各Revisionの変化/R2・R3比較/3テーマ横断比較/latency/cost/actual model_id/Fact維持確認/ユーザー判断/Fable評価)。Trial Reportに既に存在する場合も、将来消えたり参照不能にならない正式なEvidence pathとして整理する。」
- CURRENT_SPEC: 「Production News WriterのEntertainment生成方式として Original → R1 → R2 を正式仕様として記載。R3はProduction標準に含めない。仕様文中で『R2』というTrial内だけの呼び名を単独で使うのではなく、Production上何を意味するか明確に記載(例: 1. Original generation 2. Entertainment revision 3. Further entertainment revision 4. 2回目revisionの結果を最終記事として使用)。」
- DECISION_LOG: 「採用日/採用対象/3テーマTrial結果/R2採用理由/R3不採用理由/User正式承認/Evidence pathを必ず記録。」
- 新Open Item A(広告・商品紹介Fact混入): 「旅行荷物Trialで『楽天ランキング上位の売れ筋4点セットは、700円〜1,190円前後』という記述が入った。ユーザー判断: 圧縮ポーチを使えば荷物を小さくできる、までは許容。特定販売サイトのランキング、商品セット、価格紹介まで入るのは明らかに過剰。これはWriter Promptの問題として直さないこと。根本原因は広告・アフィリエイト・商品紹介色の強いSourceをNews素材として取得していること。Topic Search / Source Selection側のOpen Itemとして登録。検討方向: Source品質Gate(商品ランキング/おすすめ○選/値段比較/楽天・Amazon等売れ筋紹介/購買誘導中心/セール告知/PR記事/商品宣伝主目的/Affiliate的記事を検知・減点・除外できるか)。ただし『商品を扱う記事を全部除外』はしない(小さいバッグがなぜ流行るか/エコバッグになぜ高級感を求めるか/圧縮ポーチでなぜ荷物が減るか、のように商品を入口に一般化できる面白い問いは対象になり得る)。問題は『商品』ではなく『Sourceの主目的が宣伝・購買誘導になっていること』。仕様未承認、今回はOpen Item登録まで。Status: USER_DECISION_REQUIRED / Open Item。次回Search Trial設計時に他のSearch問題(Reference級素材への到達不足/対象が狭すぎる記事/PR・商品紹介/SNS一次情報/世界の変化型不足)と統合して扱う。広告除外だけを個別対応してSearch Trialを終えない。」
- 新Open Item B(「これ、ちょっと面白くない？」Prompt復唱): 「Original Promptの『友人に「これ、ちょっと面白くない？」と話すような読み物』という表現を、Lunaが本文冒頭へそのまま出す例が複数確認されている。現在のEvidenceでは Originalで出る/R1でも残る場合がある/R2までに消える 傾向。ユーザー判断: 気になるが、現時点ではPromptを変更しない。もう少し記事を作って様子を見る。Prompt変更禁止。Open Itemとして観測継続。最低限、今後のNews生成で Originalで出たか/R1で出たか/R2で残ったか を記録できるようにする。特に問題なのはProduction finalであるR2に残る場合。R2で一定頻度以上残ることが確認された時点でPrompt修正Trialをユーザーへ提案する。Status: OPEN / MONITORING。」
- Dangling Reference Check: 「Production Prompt/codeへ新しい正式名称を追加する場合、CURRENT_SPECに存在/user approved/initial path実装/retry・fallback整合を確認。Trial用語『R2』をProduction内部で暗黙参照しない。」
- 完了条件(PRODUCTION_WIRED): Production正式初回pathへR2方式実装/retry・fallback・regeneration整合/R3がProductionでは呼ばれない/Production runtime evidence/regression・integration PASS/actual model_id確認/CURRENT_SPEC更新/DECISION_LOG更新/OPEN_ITEMS更新/12記事+全Prompt Evidence保存/Git反映/ユーザー承認内容と実挙動一致。1項目でも未確認なら`APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`としてSTOP。

## 事前指定Read一覧

- `er015_news_iterative_entertainment_trial_01.py`: Grep `REVISION|INSTRUCTION|developer|P7|BASELINE_PROMPT|THEME_TAG|effort|previous_response_id`で位置特定→該当範囲Read(Original Prompt・developer message・R1/R2/R3修正指示の逐語、model/effort、連鎖方式の実装箇所)。
- `er015_news_iterative_entertainment_trial_02.py`: 同上Grep→該当範囲Read(Trial-01との差分=`[ニュース]`欄への素材2〜3文の付与方法、Article A/Bの素材文)。
- `er015_output/news_iterative_entertainment_trial_01/`: `prompt_original.txt`全文、`original.md`/`revision1.md`/`revision2.md`/`revision3.md`全文、`chain.json`、`cost.json`、`api_meta_original.json`/`api_meta_r1.json`/`api_meta_r2.json`/`api_meta_r3.json`(model実値・usage・latency項目のみGrep→Read)、`fact_diff.md`、`observation_table.md`。
- `er015_output/news_iterative_entertainment_trial_02/`: `sources.md`全文、`A_original.md`/`A_revision1.md`/`A_revision2.md`/`A_revision3.md`/`B_original.md`/`B_revision1.md`/`B_revision2.md`/`B_revision3.md`全文、`latency_table.md`、`fact_diff.md`、`api_meta_*.json`(model実値・usage・latencyのみ)、`cost.json`があれば費用。
- `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01_REPORT.md`: Grep `Fable|評価|結論|R2|R3`→Fable評価・結論の記載範囲Read。
- `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02_REPORT.md`: 同上(§D/§G/§H)。
- `DECISION_LOG.md`: 行440-452(索引末尾の書式)、行9314-9340(`PM-USER-VALIDATION-DIRECTION-RECORD-01`エントリの書式=直近エントリ、これに倣う)、末尾(`tail -c 3000`相当、最終エントリ位置確認)。
- `OPEN_ITEMS.md`: 行318-321(OPEN-170〜172の行書式=列構成。最新番号はOPEN-172、新規はOPEN-173/174)。
- `CURRENT_SPEC.md`: Grep `PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01`(行675付近、表の列構成確認のため行673-676のみRead。**長い行があるので全文Readしない**)。Grep `^## |^### `で節見出し一覧を取得し、News/Family A/Writer関連の節と表の末尾を特定(新規行の追記位置)。
- `docs/pm/PM_BRIEF.md`: 行151-175(ACTIVE_TASK固定ヘッダ書式)。
- `docs/pm/PM_GOVERNANCE.md`: Grep `2-1|Reconciliation`→該当節のみRead(reconに使う確認観点)。

## 事前指定Grep一覧+追記位置・更新位置の手順

### Recon(read-only、Step 3用)
1. `Grep pattern="日本語|読み物|ja_free|er002" path=CURRENT_SPEC.md -o` で、日本語記事(Trial P7方式のような「日本語のニュース読み物」)を生成するProduction経路の記載有無を確認。
2. `Grep pattern="er002_script_adapter|ja_free_markdown|WRITER_MODEL" glob="er002_*.py" -l`、および`Grep pattern="er002" path=CURRENT_SPEC.md -c`で、ER-002系Japanese生成経路が現在Production(`PRODUCTION_WIRED`)か旧経路/retiredかをCURRENT_SPEC記述で確認。
3. `Grep pattern="def main|argparse|--stage" path=er012_b_family_production_runner_01.py -n`、`Grep pattern="def run_writer_stage_generic" path=er012_b_family_voices_writer_generic_01.py -n -A 30`、`Grep pattern="A2_WRITER|B1_WRITER|WRITER_MODEL|def " path=er006_model_routing_contract_01.py -n`で、既存Production Writer経路(Family A/B、英語B1/A2、Ledger→Writer→Fact Checker→TTS)のstage構成・retry(attempts)・fallback・validator・出力構造を**事実として**列挙(設計判断はしない)。
4. `Grep pattern="previous_response_id" glob="*.py" -l`で、Production code内にResponses API会話連鎖を使う既存箇所があるか確認(Trial scriptのみなら「Production内に前例なし」と記録)。
5. `Grep pattern="これ、ちょっと面白くない" glob="er015_output/**/*.md" -n`で12記事中の復唱出現(どのテーマ・どの段階)を機械集計(Open Item B初期観測値)。
6. `Grep pattern="楽天|円" glob="er015_output/news_iterative_entertainment_trial_02/B_*.md" -n`でOpen Item Aの該当記述が4段階のどこに出るか機械集計。

### Evidence保存(Step 1)
- 新規ディレクトリ `docs/evidence/news_iterative_r2_adoption_2026-09-24/` を作成。配下:
  - `README.md`: 本Evidenceの目的(なぜR2を選んだかを追跡する正式Evidence)、管理ID、ユーザー正式判断日(2026-09-24)、構成一覧、元Trial artifactへのpath(`er015_output/...`、REPORT 2件、DECISION_LOGエントリ名)。
  - `prompts.md`: **逐語**で以下を保存(要約禁止): developer message、Original生成Prompt全文(`prompt_original.txt`をそのまま。テーマ欄・`[ニュース]`欄の実値は下水道版とA/B版の3通りを全て)、R1修正指示全文、R2修正指示全文、R3修正指示全文(R3はTrial実施の事実として保存。Production標準には含まれない旨を明記)、model(`gpt-5.6-luna`)・reasoning effort(high)・その他API引数、連鎖方式(各段階の`previous_response_id`に前段のresponse_idを渡す。Trial-02の`api_meta_*.json`から実際のresponse_id連鎖を転記)、fallback有無(Trial中未使用)。
  - `articles/`: 12記事をコピー(`sewer_original.md`/`sewer_revision1.md`/`sewer_revision2.md`/`sewer_revision3.md`、`ai_phone_original.md`〜`ai_phone_revision3.md`、`travel_bag_original.md`〜`travel_bag_revision3.md`)。各ファイル冒頭にコメント行なしで原文のみ(元ファイルとsha256一致をREADMEに記録)。
  - `comparison_and_decision.md`: (1)各テーマの段階別主要変化(Trial REPORTのFable評価から転記)、(2)R2 vs R3比較、(3)3テーマ横断表(下記Fable記載を転記)、(4)latency表(下水道O→R2 50.2秒/O→R3 70.7秒、A 45.3/56.8、B 32.2/44.5、各api_metaの実測値で裏付け)、(5)cost(Trial-01・Trial-02の`cost.json`実値、1 pass≒¥0.25、R2止め≒¥0.75/記事、R3≒¥1.0/記事)、(6)actual model_id(全12 callの`response.model`実値を表で)、(7)Fact維持確認(`fact_diff.md`の結果転記、3テーマとも素材外の固有名詞・数字・出来事の追加なし)、(8)条件差(下水道=素材なし、A/B=素材2〜3文あり)、(9)ユーザー判断(上記原文の採用根拠を引用)、(10)Fable評価(下記)。
  - `prompt_echo_and_ad_observation.md`: Open Item B(復唱)とA(広告記述)の12記事における機械集計結果(Grep手順5・6)。

Fable評価(転記用、要約せずそのまま):
```
3テーマ横断
| Theme | Original | R1 | R2 | R3 | Fable推奨 |
| 下水道(素材なし) | 弱(言い換え) | 改善(引っ越し) | 最良(合併の再解釈) | 冒頭◎/比喩4系統で過剰 | R2 |
| A AI電話(強いHook・素材あり) | 既に良(舞台) | 良(比喩2系統・進行役文) | 最良(タイトル・統一) | タイトル誇張・演出句増で過剰 | R2 |
| B 旅行荷物(地味・素材あり) | 良(見方あり・復唱) | 良(軽快) | 最良域(場面冒頭・統一) | 冒頭◎/見立て5系統で冗長 | R2 |
R2が勝ったテーマ3/3。R3が勝ったテーマ0(冒頭だけなら3/3でR3)。差が小さいテーマB(R1≈R2)。R3で過剰3/3(Aが最も顕著)。
Q1 R2は安定して良いか: はい。3テーマとも最良域で、進行役文・比喩の増殖が許容範囲に収まる最後の段階。
Q2 R3は安定してR2より良いか: いいえ。3テーマとも「冒頭は改善、本文は装飾増(比喩系統+1〜3、演出句、タイトル誇張)」で一貫。
Q3 強いテーマでR3は過剰になりやすいか: はい(A:「正体を追え！」「マジックのタネ」「幕を閉じます」)。
Q4 地味テーマでR3は有効か: 冒頭の生活描写は有効、本文は過剰。純増ではない。
Q5 一律固定か使い分けか: Evidenceは一律R2に最も合う(R3が勝つテーマが無いため使い分けの根拠が無い)。
A: R2≧R1>Original>R3。B: R2≧R1>R3≧Original。下水道: R2>R1>R3≧Original。
```

### SSOT反映(Step 2)
- DECISION_LOG.md: 索引末尾(行448の次)へ1行追加、本体末尾へエントリ追加。エントリ名 `## NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01: News記事Entertainment生成方式(Original→Entertainment revision→Further entertainment revision、2回目revisionを最終記事とする)のユーザー正式採用(APPROVED_FOR_PRODUCTION、配線未完了)`。必須項目: 採用日2026-09-24/採用対象(方式の定義をProduction上の意味で: 1.Original generation 2.Entertainment revision[修正指示逐語] 3.Further entertainment revision[修正指示逐語] 4.2回目revisionの結果を最終記事として使用、3回目以降のrevisionは標準に含めない)/3テーマTrial結果(横断表)/R2採用理由/R3不採用理由/User正式承認(原文引用)/Evidence path(`docs/evidence/news_iterative_r2_adoption_2026-09-24/`と元artifact)/Status `APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`と未充足項目(配線先Production経路の確定・実装・runtime evidence・regression)/関連Trial管理ID(NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01/02、NEWS-R25-PRODUCTION-METHOD-TRIAL-01)/Open Item A=OPEN-173、B=OPEN-174。
- OPEN_ITEMS.md: 行321(OPEN-172)の直後へ2行追加(既存列構成に従う)。
  - OPEN-173: 「**広告・購買誘導が主目的のSourceがNews素材として取得され、商品ランキング・価格紹介が記事本文へ混入する**(2026-09-24起票、`NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`、Topic Search/Source Selection側)」。実例・ユーザー判断・根本原因の見立て・検討方向(Source品質Gate候補リスト)・「商品を扱う記事を全部除外はしない」原則・Writer Promptで直さない・次回Search Trial設計時に他Search問題と統合して扱う・単独対応でSearch Trialを終えない、を原文どおり記載。Status `USER_DECISION_REQUIRED / Open Item(仕様未承認、Production Search rule未実装)`。
  - OPEN-174: 「**Original Promptの『これ、ちょっと面白くない？』をWriterが本文冒頭へ復唱する(監視)**(2026-09-24起票、同管理ID)」。傾向(Originalで出る/R1で残る場合あり/R2までに消える)・12記事の機械集計値(Grep手順5)・ユーザー判断(Prompt変更しない、様子見)・記録要件(今後のNews生成でOriginal/R1/R2それぞれの出現を記録できるようにする。Production配線時に機械検出ログを必須項目とする)・提案trigger(Production final=2回目revisionに一定頻度以上残った時点でPrompt修正Trialをユーザーへ提案。勝手に書き換えない)。Status `OPEN / MONITORING`。
- CURRENT_SPEC.md: News/Writer関連の表の末尾へ1行追加(列構成は既存行に合わせる)。項目名「News記事(日本語Entertainment読み物)のEntertainment生成方式」。内容: 方式定義(上記4段の名称+Production上の意味、修正指示逐語、model=`gpt-5.6-luna`[`er006_model_routing_contract_01.WRITER_MODEL`]・effort high・Responses API `previous_response_id`連鎖)、3回目revisionは標準に含めない、Trial呼称R1/R2/R3との対応を注記(Trial内呼称であり仕様名ではない)、Evidence path、**配線先Production経路: 未確定(Phase 0 recon結果参照)**、Status `APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`(未充足: 配線先確定・実装・retry/fallback/regeneration整合・validator・音声化前Article出力・runtime evidence・regression)、管理ID、日付。

## 実行コマンド全文

```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe -c "import hashlib,glob;[print(hashlib.sha256(open(p,'rb').read()).hexdigest(),p) for p in sorted(glob.glob('er015_output/news_iterative_entertainment_trial_01/*.md')+glob.glob('er015_output/news_iterative_entertainment_trial_02/*.md'))]"
.venv\Scripts\python.exe -c "import hashlib,glob;[print(hashlib.sha256(open(p,'rb').read()).hexdigest(),p) for p in sorted(glob.glob('docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/*.md'))]"
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01.md --json-out docs\pm\delegation_log\NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01.md_check.json
git status --short
git diff --stat
```
(SSOT編集はEdit toolで行う。Production code・Trial scriptへの編集なし。API呼出なし。)

## SSOT追記文

上記「SSOT反映(Step 2)」の内容を、各SSOTの既存書式に合わせて記述する。DECISION_LOGエントリ末尾に`Status: APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE(PRODUCTION_WIREDはGate 3全項目充足後にユーザーへ報告して確定)`を明記。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `docs/evidence/news_iterative_r2_adoption_2026-09-24/`(配下全て)、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`CURRENT_SPEC.md`、`docs/pm/delegation_log/NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01.md`、同`_check.json`。(`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は.gitignore対象のため対象外、ローカル更新のみ。)
メッセージ: `NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01 Phase 0: 逐次Revision方式(2回目revisionを最終記事)のユーザー正式採用をDECISION_LOG/CURRENT_SPECへ記録(APPROVED_FOR_PRODUCTION、配線未完了)、12記事+逐語Prompt Evidence保存、OPEN-173(広告Source混入)/OPEN-174(Prompt復唱監視)起票、Production code変更なし`
trailer: `Management-ID: NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`
push後、`git rev-parse HEAD`と`git status --short`を記録。

## 報告(RESULT_PACKET項目)

0. T-0結果。
1. **Recon結果(最重要、事実のみ)**: (a)日本語Entertainment読み物記事を生成する既存Production経路がCURRENT_SPEC上に存在するか(存在する場合はその行番号・管理ID・Status、存在しない場合は「該当なし」)。(b)ER-002系Japanese生成経路の現Status(Production/旧経路/retired、根拠行)。(c)既存Production Writer経路(Family A/B)のstage構成・attempts数・fallback・validator(Fact Checker/Ledger Deviation等)・出力構造(ファイル名/JSON形)・音声化への受け渡し方法の一覧(関数名・ファイル名・行番号)。(d)Production code内の`previous_response_id`前例の有無。(e)Trial P7方式(日本語800〜1000字、素材2〜3文、Ledgerなし)と既存Production Writer(英語、Verified Fact Ledger必須)の入力・出力・validatorの差分表(設計判断はせず差分列挙のみ)。
2. Evidence保存先(絶対パス)、12記事のsha256一致確認結果、prompts.mdに逐語保存したPromptの文字数(3通りのOriginal Prompt+R1/R2/R3指示)。
3. Open Item B機械集計: 12記事×「これ、ちょっと面白くない？」出現(テーマ×段階の表)。Open Item A機械集計: 旅行荷物4段階の「楽天/円」出現。
4. DECISION_LOG追記位置(索引行番号・エントリ開始行番号)、OPEN-173/174の行番号、CURRENT_SPEC追記行番号と追記した行の全文。
5. Dangling Reference確認: 追記したSSOTが参照するpath/管理ID/関数名が全て実在すること(Glob/Grepで確認した結果)。Production codeに「R2」等Trial呼称の暗黙参照を追加していないこと(本Phaseはcode変更なしのため「該当なし」で可)。
6. `git status --short`(意図外混入なし)、commit SHA、push結果。
7. 一覧外Read/Grepの理由(あれば1行)。
8. 想定外事項・懸念(あれば)。特に「配線先経路が存在しない場合、新規Production module設計が必要」等、Fable/ユーザー判断が必要な事実を明示(提案・設計はしない)。

---
【ユーザー指示全文】(delegation_logへそのまま保存。以下はユーザー原文の全文)

管理ID: `NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`

## 1. ユーザー正式判断
ユーザーは以下を正式採用した。「News記事のEntertainment改善方式として、Original → Revision 1 → Revision 2 の逐次Revision方式を採用し、Production標準をR2とする。」Statusを`APPROVED_FOR_PRODUCTION`へ変更する。これはTrial評価ではなく、Production正式採用判断。ただし、Gate 3をすべて満たすまでは`PRODUCTION_WIRED`としないこと。

# 2. 採用根拠
以下3テーマで同一方式をTrial済み。1. 下水道 2. AI電話代行 / Meta Muse 3. 旅行荷物 / 圧縮ポーチ。結果: 3/3でR2が最良域/R3がR2を上回ったテーマは0/R3は共通して冒頭は改善するが、本文では比喩・演出が増加/強いテーマでも地味な生活テーマでもR2が安定/R2までの費用・latencyは量産上許容可能。従ってProduction標準はR2。

# 3. 最重要：Trial Evidenceを完全保存
今後、仕様を再検討するときに、「なぜR2を選んだのか」を後から完全に追跡できる状態にすること。最低限、以下をRepo上の正式Evidenceとして保存する。
A. 使用Prompt: Original生成Prompt全文/developer message/R1修正Prompt全文/R2修正Prompt全文/R3修正Prompt全文/model・reasoning設定/previous_response_idによる連鎖方式。Promptを要約だけで残さない。実際に使用した逐語Promptを保存する。
B. 全生成記事: 3テーマすべてについて(下水道/AI電話/旅行荷物 × Original/R1/R2/R3)計12記事を全文保存。
C. 比較・判断Evidence: 各Revisionの変化/R2・R3比較/3テーマ横断比較/latency/cost/actual model_id/Fact維持確認/ユーザー判断/Fable評価 も辿れる状態にする。Trial Reportに既に存在する場合も、将来消えたり参照不能にならない正式なEvidence pathとして整理する。

# 4. CURRENT_SPEC / DECISION_LOG
今回の正式採用を反映。CURRENT_SPEC: Production News WriterのEntertainment生成方式として「Original → R1 → R2」を正式仕様として記載。R3はProduction標準に含めない。ただし仕様文中で「R2」というTrial内だけの呼び名を単独で使うのではなく、Production上何を意味するか明確に記載すること(例: 1. Original generation 2. Entertainment revision 3. Further entertainment revision 4. 2回目revisionの結果を最終記事として使用 等)。DECISION_LOG: 必ず 採用日/採用対象/3テーマTrial結果/R2採用理由/R3不採用理由/User正式承認/Evidence path を記録。

# 5. Production wiring
正式Production News生成経路へ配線する。確認対象: initial Production generation/R1/R2/retry/fallback/regeneration/validator/audio化前の正式Article output。DEV / Trial scriptだけに存在する状態は禁止。

# 6. runtime evidence
Production正式pathで実際に Original→R1→R2→final article が発火することをruntimeで確認。最低限: actual model_id/各stepが連鎖したEvidence/R2がfinal outputとして採用されたEvidence/R3が呼ばれていないEvidence/retry・fallback時の挙動/cost・latency を残す。

# 7. Regression / integration
最低限以下を確認: Originalのみで終了しない/R1で終了しない/R3まで進まない/previous_response_id連鎖が維持される/Fact逸脱が増えていない/Output structureが既存後工程と互換/Audio pipelineへ正常に渡る/retry・fallbackでRevision回数が崩れない。

# 8. 新Open Item A：広告・商品紹介Fact混入
旅行荷物Trialで「楽天ランキング上位の売れ筋4点セットは、700円〜1,190円前後」という記述が入った。ユーザー判断: 圧縮ポーチを使えば荷物を小さくできる、までは許容。特定販売サイトのランキング、商品セット、価格紹介まで入るのは明らかに過剰。重要: これはWriter Promptの問題として直さないこと。ユーザーの見立ては、広告・アフィリエイト・商品紹介色の強いSourceをNews素材として取得していることが根本原因。従ってTopic Search / Source Selection側のOpen Itemとして登録。

# 9. 広告混入問題の検討方向
今後Search改善Trialで、Source品質Gate: 以下のような記事を検知・減点・除外できるか検討する。商品ランキング/「おすすめ○選」/値段比較/楽天・Amazon等の売れ筋紹介/購買誘導中心/セール告知/PR記事/商品そのものの宣伝が主目的/Affiliate的記事。ただし「商品を扱う記事を全部除外」はしない。例えば 小さいバッグがなぜ流行るか/エコバッグになぜ高級感を求めるか/圧縮ポーチでなぜ荷物が減るか のように、商品を入口に一般化できる面白い問いは対象になり得る。問題は「商品」ではなく、Sourceの主目的が宣伝・購買誘導になっていること と整理する。この仕様はまだ未承認なので、今回はOpen Item登録まで。Production Search ruleへ勝手に実装しない。Status: `USER_DECISION_REQUIRED` / Open Item

# 10. 新Open Item B：「これ、ちょっと面白くない？」Prompt復唱
現在のOriginal Promptに「友人に『これ、ちょっと面白くない？』と話すような読み物」という表現がある。Lunaがこれを本文冒頭へそのまま出す例が複数確認されている。ただし現在のEvidenceでは Originalで出る/R1でも残る場合がある/R2までに消える という傾向。ユーザー判断: 気になるが、現時点ではPromptを変更しない。もう少し記事を作って様子を見る。従って、Prompt変更禁止。Open Itemとして観測継続。最低限、今後のNews生成で Originalで出たか/R1で出たか/R2で残ったか を記録できるようにする。特に問題なのはProduction finalであるR2に残る場合。R2で一定頻度以上残ることが確認された時点で、Prompt修正Trialをユーザーへ提案する。勝手にPromptを書き換えない。Status: `OPEN / MONITORING`

# 11. Search改善との接続
現在進行しているTopic Search改善では、今回の広告混入問題を必ず考慮する。ただしSearch問題には他にも Reference級素材への到達不足/対象が狭すぎる記事/PR・商品紹介/SNS一次情報/世界の変化型不足 等があるため、広告除外だけを個別対応してSearch Trialを終えないこと。次回Search Trial設計時に統合して扱う。

# 12. Dangling Reference Check
Production Prompt / codeへ新しい正式名称を追加する場合、CURRENT_SPECに存在/user approved/initial path実装/retry・fallback整合 を確認。Trial用語「R2」をProduction内部で暗黙参照しない。

# 13. Git
必要な Production code/tests/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/Evidence docs をcommit / push。既存並行タスクとの競合があればSTOPして報告。

# 14. 完了条件
以下すべて満たして初めて`PRODUCTION_WIRED`と報告してよい。Production正式初回pathへR2方式実装/retry・fallback・regeneration整合/R3がProductionでは呼ばれない/Production runtime evidence/regression・integration PASS/actual model_id確認/CURRENT_SPEC更新/DECISION_LOG更新/OPEN_ITEMS更新/12記事＋全Prompt Evidence保存/Git反映/ユーザー承認内容と実挙動一致。1項目でも未確認なら`APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`としてSTOP。

# 15. Closeout
最終報告では必ず 1. Production wiring内容 2. runtime evidence 3. test結果 4. Evidence保存先 5. CURRENT_SPEC更新箇所 6. DECISION_LOG 7. Open Item A 広告Source問題 8. Open Item B Prompt復唱監視 9. Git commit 10. PRODUCTION_WIRED判定可否 を報告すること。
