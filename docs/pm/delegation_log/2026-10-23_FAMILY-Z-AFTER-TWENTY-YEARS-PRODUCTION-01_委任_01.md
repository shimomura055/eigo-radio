FABLE-DELEGATION-MARKER: FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01-委任_01-FULL-PRODUCTION-RUN-20261023

# FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_01: Family Z新規作品 O. Henry『二十年後(After Twenty Years)』をStd/Advとも**既存の承認済みProduction経路(『開いた窓』完成経路と同一)**で制作し、試聴ページ公開・再生確認まで完成させる。新仕様探索なし、作品個別実装なし。費用上限100円(目標70円/セット。見込み超過時は停止前にFableへ)。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(固定ヘッダ、line 2 Git注意、FAMILY-Z-SOURCE-FIDELITY行・ASR行)、`.claude/agents/sonnet-worker.md`(有料run・停止・再起動節、Z完成段は1起動指定の注記)、ユーザー原文(§9、T-0で保存)、『開いた窓』の完成経路: `docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/{PHASE4_RESULT_01,PHASE4_RESULT_04,CLOSEOUT_01}.md`、`docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_USER_03.md`、`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/{PN/RUNTIME_EVIDENCE_01,UKUS/RUNTIME_EVIDENCE_01,B_STAGE_RESULT_01}.md`、`docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/BERTIE_LEDGER_CANDIDATE_01.md`。SSOT: `CURRENT_SPEC.md` を「Family Z」「修正版B」「Seed」「key_roles」「フルネーム」「Voice」「配役」「dialogue speed」「speed v2」「PNAP」「RET」「UKUS」「Key Phrase」「KP」でGrep(全文読込禁止)。`OPEN_ITEMS.md` のOPEN-46x/47x(Grep)。`DECISION_LOG.md` の直近Family Z決定(Grep)。runner `er026_family_z_fiction_production_runner_01.py`(CLI stages、`--help`)、Seed/plan構造は『開いた窓』run `er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/`(audit/plan/seed)を参照。

## 1. Fable判断・前提
- 制作対象の選定はユーザー承認済み(USER原文)。新仕様採用ではない。未承認のKey Phrase改善案(G2/G3/possessor_role/検査call等)・Family Y専用仕様・DEV flagをZへ導入しない。承認済みの既定(修正版B、dialogue speed v2、RET/PNAP/UKUS既定ON、OPEN-479修正済み)で実行する。
- 原作: パブリックドメイン(1906年、O. Henry "The Four Million")。テキスト出典(Project Gutenberg等)をURL・取得日付きで記録し、権利関係を1行明記。
- 『開いた窓』で解決した問題の再発防止: 固有名詞(人名)は音声生成前に発音調査(正式経路のPerplexity調査=クレジット復旧済み)→Ledger/RETで救済される設計。Seedの `key_roles` に登場人物(例: Bob["Silky" Bob]、Jimmy Wells、巡回中の警官[実はJimmy]、西部から来た男、私服刑事)を宣言(RETのdeclared経路)。ただし**作品個別のLedger手動登録・個別例外は禁止**。
- 固有名詞の扱い: CURRENT_SPECの「フルネームに関する承認済みルール」と「登場人物の名前の扱い」をGrepで確認し、それに従う(結末の意外性を損なわないよう、警官の正体=Jimmy Wellsは原作どおりの開示タイミングを守る)。
- Voice: 既存Family Z Voice候補・配役ルール(固定割当があれば遵守)に従い、ナレーター+人物(Bob、警官/Jimmy、私服刑事)を選定。不必要にVoiceを増やさない。新Voice体系禁止。
- HR Lock: 発火したら当該clipで停止しFableへ(approve_regenerateはFable承認後のみ)。再起動は各段1回まで、完成段(`provision_shell,gate,assemble,pages,page_verify`)は**1起動**。RESTART_STORM回避。STOPセンチネル削除禁止。
- TTS直列化: ACTIVE_TASK他行の「有料run(TTS)進行中」があれば待機(最大45分)。自行にflag記載/終了更新。

## 2. 作業
### T-0 記録・予算
- ユーザー原文逐語保存 `docs/pm/delegation_log/2026-10-23_FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01_USER.md`(§9)。委任文逐語保存 `..._委任_01.md`(`py docs/pm/tools/extract_delegation_from_jsonl_01.py ...`、MARKER一致)。
- ACTIVE_TASKへ新規行(自分の行): `並行タスク: FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_01 / Status=PRODUCTION_RUN_IN_PROGRESS / 上限100円 / 報告=docs/pm/RESULT_PACKET_FZ20Y1.md`。
- 予算: `daily_dev_cost_01`で当日累計確認(JST。10-23上限1,400円、10-24以降1,000円)。『開いた窓』実績(Writer 12.63+plan/support/kp 1.52+tts_b1b 23.05+tts_a2 24.75=約62円、再生成込み約78円)を基に見積を`docs/research/FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01/BUDGET_PLAN_01.md`へ。累計80円到達で見込み再計算、100円超過見込みなら停止前にFableへ。
### T-1 準備(API 0〜小)
- 原作テキスト取得(出典記録)、あらすじ・人物関係・結末の確認表(`SOURCE_CHECK_01.md`: 20年前の約束/Big Joe Bradyのレストラン/西部で成功したBob/警官との会話/私服刑事が現れる/手紙で警官がJimmy Wellsだったと判明=指名手配のBobを自分では逮捕できず代わりを頼んだ)。
- Seed作成(『開いた窓』run_sf_prod_01のSeed形式に準拠、key_roles宣言、承認済み構成)。run dir: `er026_output/family_z_production_e2e_01/after_twenty_years/run_sf_prod_01/`。
- 人名の読み確認(正式経路の発音調査段に委ねる。先回りの個別登録はしない)。
### T-2 正式Production run(CLI、承認済み段の順序どおり)
- Writer全段(Std/Adv本文)→原作忠実性・Fact・構成チェック(正式Gate)→plan/support/kp(Key Phrase: 選定・意味・英語説明は現行Production仕様)→tts_a2→tts_b1b(各段 rc確認、再起動1回まで)→`provision_shell,gate,assemble,pages,page_verify` 1起動。
- 途中でHR Lock(rc=2)なら停止→他の進められる作業→Fableへ報告。その他の失敗は既存仕様・予算内で原因究明→修正(Production code変更は不可。設定/Seed/再実行の範囲)→検証。見込みの低い同一再生成の反復禁止。
- runtime evidence: RET(`audit/entity_table.json`、NER call数、clip別受理basis[entity_table/Ledger/secondary]、会話経路での発火=OPEN-472追認)、UKUS発火有無、PNAP、speed v2、Repetition QA、`audio_text_deviations`、review_lock状態、PASS_WITH_WARNING一覧、retry/fallback/regeneration/resume件数。→`RUNTIME_EVIDENCE_01.md`。
### T-3 試聴ページ
- `user_test/family_z_after_twenty_years_01/`(『開いた窓』と同じテンプレート: Std/Adv切替、通し再生、パート別、全スクリプト、Key Phraseと意味・説明、開発者情報なし)。公開後にpage_verify(実再生・スクリプト整合・console error 0)→`PAGE_VERIFY_01.md`。
### T-4 SSOT・Git・報告
- OPEN新規(本作品: 完成版提出・ユーザー試聴待ち)、OPEN-472(会話経路RET追認の結果)、REPORT_LEDGER、DECISION_LOG(制作開始/完成の事実1行)、UDR新規(ユーザー最終試聴待ち)。CURRENT_SPEC変更なし。
- secret scan 0件→`git diff --cached --name-status`→`git commit --only -- <path…>`(wav/raw_usage_log/STOP関連は追跡しない)→`git push origin HEAD:main`。raw URL添付。
- 報告=`docs/pm/RESULT_PACKET_FZ20Y1.md`(ユーザー§8の8項目: (1)試聴URL (2)両levelの構成・再生時間・Voice配役 (3)原作忠実性・品質検査結果 (4)固有名詞・KP確認結果 (5)retry/再生成/HRの有無 (6)実費・制作時間・量産単価への示唆[出典cost_log] (7)Production経路・runtime evidence・SSOT/Git (8)未解決Open Item・ユーザー判断事項)。使用model名・最新か。手段と目的を区別。

## 3. 禁止・制約
Production code/Prompt/flag/閾値/golden変更0。未承認仕様・DEV flag・Family Y仕様の導入禁止。作品個別のLedger手動登録・個別例外・個別実装禁止。Gate/HR Lock/STOP迂回禁止。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。PIDは自分のもののみ(26-6)。`TTS_EXECUTION_MODE=STANDARD`。秘密情報出力禁止。上限100円無断超過禁止。
## 4. handback
完了/HR Lock/予算警告/blocker のいずれかで。途中経過は小刻みに返さない。

## 9. ユーザー原文(逐語)
# Claude Code／Fableへの指示｜Family Z『二十年後』正式制作

## 1. 目的・制作対象

Family Zの新規作品として、O・ヘンリーの短編小説 **『二十年後（After Twenty Years）』** を制作する。

- 対象：Family Z
- レベル：Standard／Advanced
- 原作：O. Henry, *After Twenty Years*
- 目標：両レベルの音声・Key Phrase・試聴ページまで完成させ、ユーザー最終試聴に提出する。
- Status：制作対象の選定はユーザー承認済み。新仕様の採用承認ではない。

今回の目的は、既存の承認済みProduction仕様を用いて、品質を守りながら効率的に新作品を完成させること。

## 2. 作品の基本方針

20年前に交わした再会の約束を軸に、友情、時間の経過、義務と感情の葛藤を描く。

特に以下を重視する。

- 序盤で再会の約束と登場人物の状況を明確にする。
- 登場人物の区別が音声だけでも自然につく。
- 最後の真相が分かりやすく、意外性を損なわない。
- 原作の重要な出来事・因果関係・結末を忠実に維持する。
- Standardでは理解しやすさ、Advancedでは自然な英語と文学的な魅力を両立する。
- 不要な脚色、説明過多、不自然な教訓の追加を避ける。

原作の権利関係と利用するテキストの出典を確認すること。

## 3. 既存仕様・過去成果の活用

制作前にCURRENT_SPEC、DECISION_LOG、OPEN_ITEMSおよび『開いた窓』の完成経路を確認する。

特に以下を引き継ぐこと。

1. Family Zの承認済み記事構成とStandard／Advancedの難易度仕様。
2. 登場人物・ナレーターのVoice選定仕様。
3. 登場人物の名前の扱いと、フルネームに関する承認済みルール。
4. 承認済み音声速度・TTS設定。
5. 固有名詞の発音調査・RET・PNAP救済。
6. 英米綴り差のASR救済。
7. Key Phrase選定・意味・英語説明・音声の既存Production仕様。
8. retry／fallback／regeneration／resumeおよび正式品質Gate。

未承認のKey Phrase改善案やFamily Y専用仕様を、Family Zへ無断導入しないこと。

**『開いた窓』で解決した問題を再発させない。既存の正式経路・機構を再利用し、作品ごとの個別実装を極力作らないこと。**

## 4. Voice選定

登場人物を整理したうえで、既存のFamily Z Voice候補・配役ルールに従って適切なVoiceを選定する。

- 固定済みVoiceの割当仕様があれば遵守。
- 不必要にVoiceを増やさない。
- 人物の年齢感、性格、場面、聞き取りやすさを考慮する。
- ナレーターと人物の区別を明確にする。
- 読みの難しい人名は音声生成前に確認する。

今回の作品だけのために、新しいVoice体系や品質基準を設けない。

## 5. 制作・品質検証

承認済みの正式Production経路で、テキスト制作から音声完成まで進める。

- 原作の内容・人物関係・結末を確認。
- Standard／Advancedの本文を生成。
- 必須のFact・原作忠実性・構成チェックを実施。
- Key Phraseを正式仕様どおり生成・検査。
- TTS・ASR・反復検査・速度・音声と原稿の一致を確認。
- 必要なretry／fallbackは既存仕様に従って自律実行。
- 音声品質Gateを迂回しない。
- Standard／Advancedとも通し音声を完成させる。

不具合が発生した場合は、既存仕様・予算・承認範囲内で原因究明、修正、検証まで自律的に進める。

見込みの低い同一Trialや再生成を繰り返さない。

## 6. QCD・予算管理

優先順位は **品質（Q）＞完成速度（D）＞量産単価（C）**。

- 必要十分な品質に到達したら、追加の磨き込みをせず完成させる。
- 独立して実施可能な工程は並列化する。
- 不要な検索・LLM呼び出し・TTS再生成を避ける。
- 70円／記事セットの量産単価目標を意識し、実費を計測する。
- 開発費の既存承認枠・日次上限を遵守する。
- 作業前と進行中に残予算・残工程の見積を確認する。
- **予算不足が見込まれる場合は、停止してからではなく、前広にユーザーへ報告する。**
- 日次予算内でも、未承認の新仕様・Trial範囲を無断採用しない。

## 7. 完成版の提出

『開いた窓』と同等のシンプルなユーザー試聴ページを作成・公開する。

必須項目：

- Standard／Advancedの切替
- 各レベルの通し再生
- パート別再生
- 全スクリプト
- Key Phraseと意味・説明
- 開発者向け情報を除いた見やすい画面

公開ページで実際の音声再生・スクリプト整合を確認する。

## 8. 完了報告・受入条件

以下を簡潔に報告すること。

1. 完成版試聴URL
2. 両レベルの構成・再生時間・Voice配役
3. 原作忠実性と品質検査結果
4. 固有名詞・Key Phraseの確認結果
5. retry／再生成／Human Reviewの有無
6. 実際の制作費用・制作時間・量産単価への示唆
7. Production経路・runtime evidence・SSOT／Git反映状況
8. 未解決Open Itemとユーザー判断事項

Fableは「完成」「Production実行済み」という自己申告をそのまま受け入れず、正式経路・音声・品質Gate・証跡を照合すること。

**完成しただけではユーザー試聴PASSとはしない。最終試聴と作品の承認はユーザーが行う。**

---

## 最重要事項

**『開いた窓』で確立した品質と制作方式を再利用し、Family Zの新規作品を追加開発の負担なく安定制作できるか確認する。**

新規仕様の探索ではなく、既存Productionの再現性を実証する制作とする。

品質を守りながら最速・低コストでStandard／Advancedの完成版を提出すること。