# 委任文 — USER-TEST-NEWS-CONVENIENCE-AI-01

## 管理ID
USER-TEST-NEWS-CONVENIENCE-AI-01。報告は`docs/pm/RESULT_PACKET_NEWS_CONVENIENCE_AI_01.md`(新規、★★★★報告ここから/ここまでブロック、累積Full Report)へ。テーマはユーザー指定済み(テーマ候補提示は不要)。

## 並行Agent注意(重要)
別のsonnet-workerが`USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02`(Tiny Bags、`er014_output/user_test_news_light_01/**`、PM_GOVERNANCE 9-9新設、DECISION_LOG追記、小規模TTS/ASR)を並行実行中。衝突回避:
- 音声共有ストア(`er006_output/master_audio_store_01/manifest.json`、`pronunciation_ledger_01/ledger.json`、`audio_retry_cascade_prod_01/human_review_queue.jsonl`、`er011_output/attempt_history.jsonl`)を書く段階(TTS/ASR/Ledger登録)に入る前に、`docs/pm/locks/audio_stage.lock`(内容: 管理ID+ISO時刻)を作成する。既に他タスクのlockが存在すれば60秒ごとにpoll(最大40分)。さらに、Tiny Bags側は本lock方式を知らないため、TTS段階開始前に`git fetch origin`して`origin/main`のlogに`USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02`のcommitが現れているか、または`docs/pm/RESULT_PACKET_NEWS_LIGHT_02.md`が「★★★★報告ここまで★★★★」を含むかを確認し、いずれも未達なら同じpollで待つ(最大40分、超過時はテキスト段階までの成果をcommitしてSTOP報告)。音声段階終了後にlockを削除する。lockファイルはcommitしない。
- SSOT(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`ARTIFACT_REGISTRY.md`/`CURRENT_SPEC.md`)編集は最後にまとめて行い、編集直前に`git fetch origin`→`git merge origin/main --no-edit`(rebase/force禁止)→編集→即commit→push。pushが拒否されたらfetch+merge再試行。conflictが発生したら自力解決せずSTOP報告。
- `docs/pm/ACTIVE_TASK.md`は使わず、`docs/pm/ACTIVE_TASK_NEWS_CONVENIENCE_AI_01.md`を使う。

## 目的
ユーザーテスト用News「日本のコンビニ商品開発にAIが使われ始めている」をA2/B1で完成(player URLまで)。最重要条件: 前提知識がなくても音声だけで理解できる、身近でシンプルなNews(AI Controlが難しすぎた反省、OPEN-164意識)。

## テーマ
仮EN: "AI Is Helping Japan's Convenience Stores Invent New Food" / 仮JA: 「日本のコンビニ、AIで新しい味を開発」/ 別案EN: "AI Made This Snack Idea — But Would You Eat It?"。最終タイトルはResearch結果・記事内容に合わせて調整可(日本語タイトルはconfig供給、Tiny Bagsと同型)。

## 記事の中心軸・伝えたいこと
主役は「AIの技術説明」ではなくAIが商品アイデアを出し、人間が試し、味を整えて商品にすること。入口はローソンの「レモンタルト+ピクルス」のような意外な組み合わせ。使えるならFamilyMart等「販売データから売れそうな商品を考えるAI」との違いに触れる(無理に企業比較で情報量を増やさない)。分かれば十分な5点: (1)日本のコンビニがAIを商品開発に使い始めている (2)AIは「変わったアイデア」を出す使い方もある (3)AIが全部作るのではなく人間が試作・調整する (4)別の会社では過去の販売データから商品案を考える使い方もある (5)AIは人間の代わりではなくアイデア補助。

構成イメージ: Hook=「レモンタルトにピクルス?」型の驚き / Main Story=AIでアイデア→意外な組み合わせ→人間が試作・調整 / Point One=AIは人間が思いつきにくい案を出すのに使える / Point Two=販売データから売れそうな商品を考える支援もある / In One Line="AI is helping with ideas, but people still decide what actually reaches the shelf." 程度のシンプルなまとめ。

## 禁止(難しくしない)
AI Control型の抽象議論、生成AIの仕組み説明、machine learning/model/algorithm等の技術解説、AI倫理・失業・制御問題への横展開、小売業DX論、市場分析の詰め込み、企業戦略の深掘り、数字の多用、難しい一般語の多用、Factを集めたから全部使うこと。目標=普通の人が家事や移動中に音声だけで聞いて理解できる。scriptを見ないと追えない記事にしない。

編集判断の実装手段(既存仕様の範囲内、新Gate・新Prompt仕様は作らない): (a)Researchスコープを上記5点+具体例(商品名・発売時期/地域・試験販売/継続利用の事実)に絞り、Ledgerを必要最小限(目安10〜15件)に保つ。(b)driverのtopic/brief/angle等、既存Writer入力チャネル(Tiny Bags/Space Weaponsのdriverで使った経路)で上記の中心軸・構成イメージ・「数字は最小限」「前提知識不要」を渡す。Production Writer Prompt本体・共通モジュールは変更しない。(c)生成後、read-onlyの情報密度チェック(語数、平均/最長文長[CURRENT_SPEC L539-542]、数字の出現数、想定外の難語[上記避けたい語]の有無、論点数)を報告に載せる。基準超過はGateではないが、明らかに密度過多・難語多用なら同じ正式経路で1回だけ再生成(brief調整)してよい。それでも解消しなければSTOP(新仕様が必要=USER_DECISION_REQUIRED)。

## A2 / B1
A2: 特に簡単に。優先語彙 food/taste/idea/try/make/sell/store/product/unusual/popular/data等。避ける: product development process/consumer behavior/predictive analytics/optimization/generative model/market segmentation等。A2正式仕様(spoken-first、平易な一般語、1文1メッセージ、平均文長/最長文長既存仕様、単純構文)遵守。不自然に情報を削りすぎない。
B1: A2より少しだけ深める。軸="Who comes up with the idea, and who decides if it actually tastes good?"(AI=idea assistant、Human=taste/judgment/final decision)。抽象論へ広げない。
A2/B1は同じLedgerから独立生成、B1→A2 adaptation禁止。Key Phraseは各レベル完成本文から独立選定(流用禁止)、本文理解に役立つ自然な表現優先。

## Research
Web Search(既存vfl01 researcher+verification経路)。優先source: Lawson公式、FamilyMart公式、Japan Times等信頼できる報道、必要に応じ一次/準一次情報。確認Fact例: ローソンがAIを商品アイデア作りに使った事実、「レモンタルト+ピクルス」等の具体例、AI案を人間が試作・調整したこと、発売時期・地域、FamilyMartのAI商品開発の使い方、実際に試験販売/継続利用した事実。裏付けられない話は入れない。Research 1回(A2/B1共有)。

## 正式Production経路(DEV/Trial pathで代替しない)
driverは`er014_output/user_test_news_light_01/tiny_bags/run_pipeline.py`(最新)を型に、`er014_output/user_test_news_convenience_ai_01/convenience_ai/run_pipeline.py`を新設。Research→Verified Fact Ledger→A2/B1 Writer(`er003_v1_n3_01_articles_generate.run_one_pattern`)→Fact Checker→Ledger Deviation(必要ならLocal Rewrite、`er010_ledger_local_rewrite_09`、MAX 3、OPEN-141 diff QA。OPEN-163のloop gapがあれば手動cycleで対応し報告)→Scaffold(Preview/Comment)→Key Phrase→TTS(`er003_v1_n3_01_tts_generate`)→ASR cascade(Secondary ASR+Phrase Listまで)→Human Review if needed→Assembly(`er003_v1_n3_01_assemble`、Audio Validation Gate、override禁止)→player(`build_web_player_common.py`、player.htmlは記事dir root、`web/episode.mp3`、B1はComment/本文の視覚分離済みテンプレ)→Browser E2E(Playwright headless Chromium、`docs/pm/closeout_136_e2e/`の型: currentTime進行/paused/readyState/error/seek、evidence JSON保存)。

Space Weapons A2で使った`title_tts`(parts.jsonの任意field、TTS入力のみ)は、タイトル読みの区切りが不自然な場合のみ使用可。

## 固有名詞・Human Review(恒久指示)
企業名(Lawson/FamilyMart等)・商品名でPrimary ASR不一致が出ても、正式ASR cascadeをSecondary ASR+Phrase Listまで使い切る。PrimaryだけでHuman Reviewに回さない。Pronunciation Ledger正式経路で発音を取得(cache hitなら再調査しない。OPEN-159の`get_hint_for_text`大文字小文字bugが発火する場合は`ledger_phrases`を明示的に渡し、`phrase_list_used`と渡したphraseを証跡化。bug修正はスコープ外)。TTS再生成条件はCURRENT_SPEC L1279に従う(固有名詞ASR表記ゆれのみでの再生成禁止)。

それでもHuman Reviewが必要な場合: raw mp3/wav直リンク禁止。`<level>/human_review/index.html`(+同dirにmp3、wav禁止)を作り、Play button(`<audio controls>`幅≥360px)/該当segment音声/canonical script/問題箇所`<mark>`/発音問題ならcanonical spelling・正しい読み・IPA・カタカナcue・source・Primary結果・Secondary結果・TTS実読/確認ポイントを同一ページに表示。Tiny Bags側が`user_test/human_review.html`(JSON駆動)を新設していればそれを再利用(`git fetch`で確認)。提示前にPlaywright E2E(page load/Play開始/currentTime≥2秒/audio errorなし/script表示)必須、evidence保存。承認代行(Human Approvalの記録)は一切しない。Human Review必要時はそのレベルをSTOP(他レベルは完了まで進める)。

## ユーザーテストページ・URL・Sheet
`user_test/unified.html`(無変更)を使う。URL形式: `https://rawcdn.githack.com/shimomura055/eigo-radio/<SHA>/user_test/unified.html?src=<PLAYER_PATH>&level=<LEVEL>&en=<ENC_EN>&ja=<ENC_JA>`(A2/B1それぞれ、en=は各レベルの記事タイトル)。全体Play/全script(Preview/Comment含む、効果音除外)/Key Phrase EN・JA/Commentと本文の視覚分離。Sheet行: 記事タイトル(English)/記事タイトル(日本語)/記事の概要(日本語)/ノーマル(A2)/Advanced(B1)/備考=最新ニュース。

## コスト
上限¥600(News 2EPの1テーマ≈¥220、Tiny Bags¥173が目安)。無駄なTrial禁止、正式retry/fallback/Secondary ASRは省略しない。問題時は多案を試さず原因切り分け。`raw_usage_log.jsonl`実測+cost_stage未計測分(scaffold/keyphrase既知ギャップ)の推定を分けて報告。

## STOP条件
credibleなFact不足/テーマ前提が事実として弱い/AI商品開発の実態がResearchと大きく異なる/新Product仕様判断が必要/News難易度問題で既存仕様と衝突/proper nameが正式cascade後も未解決/TTS・ASRでHuman Review必要(該当レベルのみSTOP)/Production path gap/player・E2E問題/approved spec変更が必要/追加コスト大(¥600超見込み)/git conflict。新仕様候補が出たらREJECTED/VALIDATED/USER_DECISION_REQUIREDで分類し、Production採用しない。

## SSOT/Git
`DECISION_LOG.md`に`## USER-TEST-NEWS-CONVENIENCE-AI-01`エントリ(索引+本体、`## 参照元`直前)。`OPEN_ITEMS.md`は新規仕様問題がある場合のみ(OPEN-164への観測追記は可)。`ARTIFACT_REGISTRY.md` News-familyセクションへA2/B1行。明示add、`git add -A`禁止、wav禁止、mp3(web/episode.mp3・segments・human_review用)はcommit可。commit分割可。trailer `Task-ID: USER-TEST-NEWS-CONVENIENCE-AI-01`。

T-0: 委任文を`docs/pm/delegation_log/USER-TEST-NEWS-CONVENIENCE-AI-01.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。E-1/D-1/G-1/F-1/T-1従来どおり。

## 事前指定Read/Grep一覧
Tiny Bags driver・`docs/pm/RESULT_PACKET_NEWS_LIGHT_01.md`・Space Weapons driver/regen/title_tts例・`build_web_player_common.py`・`docs/pm/closeout_136_e2e/`・CURRENT_SPEC L538-542/L606(難易度)・L796-860(通常News Reference)・L1277-1280(ASR cascade/Human Review)・OPEN_ITEMS OPEN-159/163/164行。事前指定外Readは理由付き報告。

## 報告項目(★ブロック内)
0.T-0 1.採用タイトルEN/JA+決定理由 2.Research実態(Ledgerが裏付ける範囲、裏付けられず不採用にした話) 3.記事要旨+語数(A2/B1) 4.Ledger件数(VERIFIED/AMBIGUOUS/REJECTED)+費用 5.QA結果(Fact Checker/Ledger Deviation/Local Rewrite/Key Phrase/Directional precheck誤検知の有無) 6.情報密度チェック結果(A2/B1: 語数・平均/最長文長・数字出現数・難語・論点数、再生成有無) 7.Audio(segment数/OK/UNCERTAIN/STOPPED、cascade結果、Human Review有無、Gate結果、duration) 8.Browser E2E結果 9.A2 URL 10.B1 URL 11.Sheet行 12.cost実測(内訳+未計測推定) 13.model/routing 14.Git SHA 15.SSOT 16.ユーザー判断 A(仕様・Product・実装判断待ち、なければ「なし」)/B(ユーザー試聴・品質確認待ち、完成player URLが出た時点でactive、それ以前は「なし」。Human Review確認ページがあればその項目) 17.未決事項 18.無変更証跡(`git status --porcelain er0*.py user_test/unified.html`でProduction変更なし)/事前指定外Read/並行衝突回避の実施記録(lock作成・待機時間)。
