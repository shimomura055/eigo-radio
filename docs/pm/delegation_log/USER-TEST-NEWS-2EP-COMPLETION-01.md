## 管理ID

`USER-TEST-NEWS-2EP-COMPLETION-01`
並行タスクなし(直近commit `4a73d9c0`、local main = origin/main)。報告は`docs/pm/RESULT_PACKET_NEWS_2EP.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は固定ヘッダ形式で上書き可(UDR-deferred/APPROVED未配線欄は前回内容[Family C 2仕様=APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE、Discovery B1/A2個別対応、OPEN-154/155、Voices Priority 2着手待ち、AI hiring A2試聴待ち]を引継ぎ)。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー実検証用News記事2テーマ×A2/B1=4完成episodeを、**既存の最新News仕様・既存Production経路・既存承認済みmoduleをそのまま再利用**して完成させる。新仕様検証・改善Trialではない。
- 到達上限Status: `USER_TEST_READY`(4本すべて受入条件を満たしたときのみ)。それ以外は`USER_LISTENING_PENDING`等の実状態か`USER_DECISION_REQUIRED`。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`への変更禁止(Production採用判断ではない)。
- 禁止: A/B比較、複数案生成、exploratory Trial、Prompt改善Trial、新validator開発、新しい記事構造の検討、Opusレビュー、**同じResearchのA2/B1別実行、取得済み情報の再Research**、問題発生後に別方式・別モデル・Prompt変更を次々試すこと、旧Legacy Newsフォーマット(本文中心でComment・解説がない旧形式、B1-A方式、P-series専用スクリプト`er003_v1_iran01_*.py`等)の使用、SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)変更、Productionモジュール(`er003_*.py`/`er011_*.py`/`er005_*.py`等root直下の正式module)の変更、`user_test/unified.html`の大改修、新規user-test UIの作成、Google Sheet編集、既存QA PASS基準の人間判断による緩和、`git add -A`/`stash`/`amend`/`rebase`/`force push`、wavのcommit。
- **通常経路が成功したら、それ以上の最適化・改善を行わず終了する。**
- コスト目安: 4 episode+Research 2セットで概ね¥300〜600想定。累計実測が**¥1,200**を超える見込みになった時点で続行せずSTOP(USER_DECISION_REQUIRED)。

## STOP条件(1つでも該当したら即STOP、`USER_DECISION_REQUIRED`で報告。「別案を試す」「別モデルで試す」「Promptを変える」を勝手に行わない。問題内容・影響・必要なユーザー判断だけを短く報告)

- **Step 0で`user_test/unified.html`がorigin/main上にも存在しない、またはsrc形式が既存出力(player/timeline)と互換不明**(この場合はResearch前=API支出0でSTOP)
- Human Review Lock発火
- Audio Validationで通常retry上限到達
- Fact Checkerの重大な未解決問題
- Ledgerと記事の重大矛盾
- 現行News仕様/正式生成pathが複数ありどれを使うかユーザー判断が必要
- 新しいPrompt/Validator/Production仕様変更が必要
- Researchでテーマの前提そのものが誤っていると判明
- 完成に追加Trialが必要/既存正式経路では生成できない
- unified.html互換性問題(UI側を改修せずSTOP)
- コスト累計¥1,200超見込み
- Step 0の時点でテーマ1つだけ成立しない場合は、成立しないテーマのみSTOP扱いで他テーマは続行してよい(Research着手後に判明した場合も同様、ただし追加Researchはしない)

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、恒久運用): 受領した委任文を`docs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01.md`へ保存し、`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-NEWS-2EP-COMPLETION-01.md --json-out docs\pm\delegation_log\USER-TEST-NEWS-2EP-COMPLETION-01_check.json`を実行し、結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業継続、非ブロッキング)。

## ユーザー指示(原文・要旨の忠実転記)

### 目的
2テーマ×A2/B1で、最新ニュース調査→Verified Fact Ledger→A2/B1記事→Preview/Key Phrases/Comment等の完成script→TTS→episode assembly→Audio QA→user-test player→rawcdn.githack URLまで進める。最終成果物=4完成episode。

### 最初に行うこと(コードを書く前にread-only確認)
1. `CURRENT_SPEC.md` 2. 最新のFamily A/News仕様 3. 現在のNews正式生成path 4. Preview/Key Phrase/Comment/Point/In One Line等の現行構成 5. 現行TTS/Assembly/Audio Validation経路 6. 現在ユーザーテストで使用しているplayer形式。古いLegacy Newsフォーマットは使わない。確認後、そのまま最短の既存経路で生成する。

### Theme 1: 宇宙に"兵器"が配備される時代へ
直近のニュースを起点にする。Researchでは少なくとも以下を区別: 実際に発表・確認された事実/space-based weapon・counterspace weapon・defensive system等の用語差/何が「宇宙への兵器配備」と言えるのか/既存の宇宙安全保障との違い/条約・国際ルール上確認できる事実/将来予測や専門家の解釈。センセーショナルにしない。「宇宙戦争が始まった」等ソースが直接支持しない表現は禁止。政治・安全保障上の評価を記事側で決めず、確認済みの出来事と従来との違いを中心にNewsとして構成する。

### Theme 2: AIは本当に人間の制御を超える可能性があるのか
直近のAI safety/capability関連ニュースを入口にする。Researchで分離: 現時点で実証されているAI能力/self-improvement・autonomous behavior等について確認されている事実/AI企業・研究者が述べている将来リスク/Singularity・recursive self-improvement等の仮説/現時点では確認されていない推測。「AIが人間の制御を超える」と事実認定しない。問いは"Could AI eventually become difficult for humans to control — and what evidence do we actually have today?"に近い構造でよいが、Research結果に合わせて自然なタイトルへ調整可。恐怖を煽らず、現在できていること/できていないこと/なぜ専門家が議論しているのかを理解できるNewsにする。

### Research/Fact方針
各テーマResearchは1セット。一次情報・Reuters/AP等・公的機関・原論文・公式発表を優先。A2/B1で別Researchを行わずVerified Fact Ledgerを共有。Fact Checker/Ledger Deviation等は既存正式経路をそのまま使う。既存QAがPASSしたものを人間判断で緩和しない。

### A2/B1
同一Ledgerに基づき事実関係を一致させる。難易度差は語彙・文構造・情報密度・説明量で出す。A2だから重要な事実を別内容へ変えない。Cross-levelで日付・数値・方向性・因果が矛盾しないことを確認する。

### 完成episode(現行News仕様に従い最低限以下をすべて)
Welcome/Topic intro、日本語タイトル、Preview、Key Phrases 5件、Full Story、現行仕様上必要なComment/解説、Point One/Point Two等の掘り下げ、In One Line/Closing、Outro。CURRENT_SPECの最新News仕様を優先。古いNews成果物を根拠に構成要素を削らない。

### Key Phrase
各level 5件。表示用日本語とTTS用テキストが異なる場合は現行仕様に従う。ユーザー向けplayerには英語+日本語意味だけを表示。以下の内部情報をuser-test画面へ出さない: `TTS用`/`表示用`/`gloss`/voice名/validator結果/Trial情報/Production情報/internal note/QA flag/runtime metadata。

### Audio
既存正式TTS経路。新しい音声方式Trial禁止。各levelで全必要segment生成/ASR・Audio Validation/Assembly/完成episode mp3/timeline/playerまで。既存retry規約内の通常retry自動発火は可。通常retry上限超過・Human Review Lock発火時は追加対応を勝手に行わない。

### user-test player
既存`user_test/unified.html`で正常表示できるplayerを作る。Sheet掲載の既存記事と同形式で、全体再生/Preview/Key Phrases/Full Story・Script/Comment/「▶ ここから再生」が使えること。SFX/jingle/internal metadataは表示しない。新UIを作らず既存を再利用。互換性問題はUI側を大改修せずSTOP。

### Git/rawcdn URL
完成成果物を必要なGit反映まで行う。最終main SHA確定後、クリック可能なrawcdn.githack URLを4本出力:
`https://rawcdn.githack.com/shimomura055/eigo-radio/<FINAL_MAIN_SHA>/user_test/unified.html?src=<PLAYER_PATH>&level=<LEVEL>&en=<URL_ENCODED_ENGLISH_TITLE>&ja=<URL_ENCODED_JAPANESE_TITLE>`
必須: 1. Space Weapons — Normal(A2) 2. Space Weapons — Advanced(B1) 3. AI Control — Normal(A2) 4. AI Control — Advanced(B1)。file://・localhost・GitHub raw URLだけで終了しない。

### Sheet投入用情報(Sheet自体は編集しない)
| 記事タイトル(English) | 記事タイトル(日本語) | 記事の概要(日本語) | ノーマル(A2) | Advanced(B1) | 備考 |
備考=`最新ニュース`。A2/B1欄にrawcdnリンク。

### 受入条件(各テーマ×level)
Article生成成功/Verified Fact Ledger整合/Fact QA規定内/Previewあり/Key Phrase 5件/Comment・解説あり/Full Story完成/A2/B1整合/全音声segment生成/Audio Validation PASS/完成episode Assembly PASS/playerでepisode参照可能/timeline・seek情報あり/unified.html互換/内部情報がuser画面に出ない/local path参照なし/rawcdn URL生成済み。4本すべて満たしたときのみ`USER_TEST_READY`。

## Fableからの補足(事前調査結果、read-only確認済み)

- **`user_test/unified.html`はローカルrepo(main=`4a73d9c0`)に存在しない**(Glob `**/unified.html`・`**/*unified*.html`とも0件、`user_test/`ディレクトリ自体なし。SSOT(DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC)にも記録なし)。ユーザーのSheetでは既に使用中とのことなので、**ChatGPT側等から本セッション外でGitHubへpushされた可能性**がある。Step 0でfetchして確認すること。
- News本文の直近production-set生成pathは`er014_output/four_type_observation_01/news/run_news_a2.py`・`run_news_b1b.py`(Researcher+Verification[`er003_v1_en_direct_vfl_01_generate`のbuild_researcher_prompt/build_verification_prompt、OpenAI responses+web_search、`research/`をA2/B1で共有・Resume機構あり]→`er003_v1_n3_01_articles_generate`のCOMMON_BLOCK_TEMPLATE経路)。本文のみで音声化未実施。
- Family A音声完成の直近正式path候補: `er011_family_a_completion_a2_trend_end_to_end_01_run.py`(`er003_v1_n3_01_scaffold_generate`/`tts_generate`/`assemble`+`er011_human_review_lock_01`+`er005_cost_logger`をimport)、および`er014_output/four_type_observation_01/trend/run_trend_audio_completion*.py`・`build_player_b1_label.py`・`er011_family_a_completion_a2_trend_end_to_end_01_{a2,b1b}_continuation_player_01.py`(player生成)。CURRENT_SPEC 796-860「通常News Reference仕様」ではHanshin(`ER-003-A2-B1-N3-01`、`er003_v1_n3_01_*.py`)が構造・Writer・Fact Safety・音声実装のreference。**どれが現行正式pathかを確認して1つに確定**し、確定できない(複数の現行候補が並立し判断が必要)場合はSTOP条件。
- 単語数報告義務: 各記事の本文語数を報告し、280語未満または500語超の場合はその旨を明記(PM_GOVERNANCE 9-11)。

## 手順

### Step 0(API支出0、必ず最初に)
1. T-0実行。
2. `git fetch origin --quiet` → `git status -sb | head -1` → `git ls-tree -r --name-only origin/main | findstr /i "user_test unified"`。origin/mainがlocalより進んでいれば`git merge origin/main --no-edit`(競合時はSTOP)。
3. `user_test/unified.html`が存在すれば、Grepで`src|level|en=|ja=|fetch\(|\.json|timeline|segments|keyPhrases|comment|episode`等を抽出し、**`src=`が何を指すか(player.html?JSON manifest?timeline.json?)と必要なデータ構造・必須フィールド**を確定してRESULT_PACKETに記録。既存Sheet掲載記事のうちrepo内に存在する参照例(直近commit `USER-TEST-PLAYER-WEB-DELIVERY-FIX-01`等で追加・変更されたファイルを`git show --stat <sha>`で特定)を1つ選び、その`src`対象ファイルの構造を確認する。
4. 存在しない、または互換に必要な構造が確定できない場合は**ここでSTOP**(Researchへ進まない)。RESULT_PACKETに「unified.html不在(origin/main SHA)/確認したpath/必要な判断」を記録して報告。

### Step 1(read-only仕様確認)
CURRENT_SPEC.md: Grepで`^## CEFR-A2構造|^## B1(独立生成|^## 通常News|^## Key Phrase$|^## Preview$|^## Cross-level|^## Audio Assembly|Audio Validation|Human Review Lock`→該当節の必要行のみRead(796-860は必読)。PM_GOVERNANCE.md: Grepで`Gate 7`→標準player要件(a)〜(m)の行のみRead。上記候補スクリプトはGrep(`def main|add_argument|import er0|THEME|topic|out_dir|BASE_DIR`)で入口・設定箇所のみ確認し、正式path 1本を確定。

### Step 2(テーマごと、Research 1回)
出力先: `er014_output/user_test_news_2ep_01/space_weapons/`・`.../ai_control/`(配下`research/`共有、`a2/`、`b1b/`[内部id、ユーザー表記はB1]、`web/`)。既存`run_news_a2.py`/`run_news_b1b.py`と同じ構造の薄いdriver(scratchpadではなく上記出力dir直下に配置、既存moduleをimportして呼ぶだけ・Prompt本文の新規作成禁止)で、Researcher→Verification→Verified Fact Ledger(1回)→A2/B1本文(COMMON_BLOCK_TEMPLATE経路、B1はB1-B Direct)→Fact Checker→Ledger Deviation→Cross-level整合確認(既存`cross_level_consistency`相当の手順があればそれ)。Researchのtopic文には上記Theme別の区別要件(事実/用語差/将来予測の分離等)を**既存build_researcher_promptのtopic引数として渡す範囲**で反映し、Promptテンプレート自体は変更しない。

### Step 3(音声・player)
確定した正式pathでScaffold(日本語タイトル/Preview/Key Phrase 5件/Comment/Point heading等)→TTS全segment→ASR/Audio Validation→Assembly→episode mp3(`web/episode.mp3`または既存path命名規約に従う)→timeline→player(unified.htmlのsrc形式に合致するもの)。Human Review Lock/retry上限は既存規約に従い、発火時はSTOP。

### Step 4(Git・URL)
1. 成果物commit(明示add: 本文/ledger/json/timeline/player/mp3/driver .py[出力dir内のみ]/delegation_log。wav除外)。メッセージ: `USER-TEST-NEWS-2EP-COMPLETION-01: News 2テーマ(Space Weapons/AI Control)A2・B1完成episode+user-test player`、trailer `Task-ID: USER-TEST-NEWS-2EP-COMPLETION-01`。push。
2. そのcommit SHA(=FINAL_MAIN_SHA)で4本のrawcdn URLを組み立て、User-Agent付きGETで到達確認(unified.html本体とsrc対象、episode mp3にRange GET、200/206。CDN遅延時60秒待ち最大3回)。
3. RESULT_PACKET/ACTIVE_TASKを別commit(`USER-TEST-NEWS-2EP-COMPLETION-01: RESULT_PACKET`)でpush。URLに使うSHAは成果物commitのもので可(rawcdnはcommit固定のため有効)。

## 報告(`docs/pm/RESULT_PACKET_NEWS_2EP.md`、簡潔に)

0. T-0結果/Step 0結果(unified.htmlの有無・SHA・src形式)/確定した正式path(スクリプト名)
1. 2記事のEnglish/日本語タイトル
2. A2/B1各status(+本文語数、280未満/500超の明記)
3. Fact Checker/Ledger Deviation/Cross-level結果、Audio Validation結果(各level)
4. episode duration(各level)
5. actual model_id(Research/Writer/Fact Checker/Scaffold/TTS/ASR)
6. 実測cost/token(cost logger実測、未計上分があれば推定を併記)
7. final main SHA
8. rawcdn user-test URL 4本
9. Sheet投入用2行(上記表形式)
10. unresolved事項
11. USER_DECISION_REQUIREDの有無(あれば問題内容・影響・必要な判断のみ)
12. 無変更証跡(`git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md er003_v1_n3_01_*.py er011_family_a_*.py er005_cost_logger.py`が空)/事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(内部識別子`b1b`はpathにのみ可)。
