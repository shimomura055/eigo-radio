## 管理ID

`USER-FEEDBACK-CLOSEOUT-AND-VOICES-SPEC-REVIEW-01`(本委任はそのうち**Closeout部分**: 項目2〜6。Voices仕様レビュー[項目1・7]は別委任`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-REVIEW-01`が並行実施)。現在main=`fa9e3f15`以降。報告は`docs/pm/RESULT_PACKET_FEEDBACK_CLOSEOUT_01.md`(新規)へ。

**並行タスクあり**: (a)`USER-TEST-NEWS-LIGHT-TOPIC-01`(er014_output/user_test_news_light_01配下、音声→player→DECISION_LOG編集→commit)、(b)`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-REVIEW-01`(read-only、`docs/pm/RESULT_PACKET_VOICES_SPEC_REVIEW_01.md`のみ書く)。ルール: SSOT編集・git操作は`git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/PM_GOVERNANCE.md`で自分以外の未commit変更が無いことを確認してから(あれば5分間隔で最大30分待つ)。commit前に`git fetch origin`→`git merge origin/main --no-edit`(rebase/force push禁止、競合時STOP)。全文Write禁止。`docs/pm/ACTIVE_TASK.md`は最後に1回固定ヘッダで上書き(他タスク状態保持)。**API/TTS実行0、Productionコード変更0、記事再生成0。**

## ユーザー判断(2026-09-17、原文要旨)

### 2. AI Control A2/B1: ユーザー試聴OK → 両方とも**ユーザー品質確認PASS / USER_TEST_READY**として記録。
ただし重大Open Item: 内容が難しすぎる/前提知識依存/情報詰め込み/聞き手が追いつけない/専門用語だけでなく難しい一般語も多い/AI知識のあるユーザー自身がscriptを追いながらでも理解困難/一般ユーザーがNewsとして理解するのは厳しい。Space Weaponsも難しかったがAI Controlは度を越えていた。
→ **News系共通の新規Open Item**(OPEN-164想定): 「CEFR言語難易度調整とは別に、Listening Newsとしての情報密度・前提知識依存・概念密度・難語密度を制御する必要がある」。最低限含める観点: information density/prerequisite knowledge/conceptual load/number density/difficult but non-technical vocabulary/abstract concept density/one episode内で扱う論点数/audio-only理解可能性/scriptを見なくても追えるか/Factを集めたからといって全部入れない/Storytelling Firstと理解可能性のバランス。優先度=中〜高。期限=量産開始前に改善方針を決める。今回の記事はユーザーOKのため再生成しない。
Word-level確認結果も記録: A2=平易な一般語優先・平均文長11語以下・最長18語以下・1文1メッセージ・単純構文・spoken-first(ただしCEFR外語彙の機械的禁止方式ではない。過去にA2超語彙数上限Trialは却下済み)。B1=B1-B Difficulty Control instructionあり・A2とは別生成・CEFR外語彙禁止やhard capなし。**結論: AI Controlが難しかったのは「レベル調整未実施」ではなく情報設計・概念負荷の問題**として整理(該当CURRENT_SPEC行・過去Trial却下記録をGrepで裏付け、行番号を記載)。

### 3. Space Weapons A2: タイトルTTSの発音・区切り修正だけが問題だった。**それ以外を変更していないことが確認できれば全体OK**。確認事項: 変更対象がタイトルTTS segmentのみか/article本文変更なし/scaffold変更なし/Key Phrase変更なし/Comment変更なし/Full Story変更なし/他segment音声変更なし。確認できれば**ユーザー試聴PASS / USER_TEST_READY**。タイトル以外も変更されていれば差分を報告してSTOP。
→ 確認方法: `git diff --stat c2af33f2..6d088d2e -- er014_output/user_test_news_2ep_01/space_weapons/a2/`と`git diff c2af33f2..6d088d2e -- .../a2/parts.json .../a2/article.md .../a2/a2_support_texts.json .../a2/key_phrases/`、`tts_generation_results.json`の各segment sha256(topic_intro以外が不変)、assembly成果物(episode.mp3/web)は再assembleによる更新のみで他segmentの音源が同一であることを示す。

### 4. Space Weapons B1: 内容変更なし・視聴ページレイアウト修正のみ・修正後レイアウトOK → **ユーザー試聴PASS / USER_TEST_READY**。再試聴不要。

### 1. Personalized News A2: **現行版はユーザーNG**(REJECTED_AS_CURRENT_OUTPUT相当。既存Status語彙に合わせる)。理由=個別文言ではなくVoices構造の根本問題(VoiceがSurvey/統計/外部Evidenceを引用/各Voiceの立場がぼやけている)。個別修正禁止・仕様見直し要求(別委任で実施中)。**重要: 記事品質NGでもB-Family A2 E2E Production wiring(`PRODUCTION_WIRED`)は未配線に戻さない**。実装基盤=PRODUCTION_WIRED、今回の生成記事=品質NG、の2層で管理。

### 5. SSOT反映
- DECISION_LOG: Personalized News A2現行版ユーザーNG(理由=Voices根本仕様、個別修正ではなく仕様見直し要求、レビュー中)/AI Control A2/B1ユーザー試聴PASS/AI Control難易度問題は別Open Item/Space Weapons A2 条件付きPASS(確認結果)/Space Weapons B1 PASS。1エントリ(本ID)。
- OPEN_ITEMS: 新規「News Listening Comprehension / Information Density問題」(量産前必須改善、上記観点、優先度中〜高)。Personalized NewsのVoices問題は**単なるdeferred Open Itemで逃がさず**、OPEN-151行(または該当行)へ「現行A2記事ユーザーNG、仕様見直しタスク`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-REVIEW-01`で継続中(USER_DECISION_REQUIRED予定)」を追記。
- CURRENT_SPEC: Personalized News/Voice役割の新仕様は書かない。B-Family A2新規topic経路行の`PRODUCTION_WIRED`は維持。必要なら同行に「初回生成記事(Personalized News A2)はユーザー品質NG(Voices仕様レビュー中)、基盤Statusとは別管理」を注記として追記のみ。通常News側でAI Control/Space WeaponsのUSER_TEST_READY(ユーザー試聴PASS)を記録する既存の場所(ARTIFACT_REGISTRY.md等)があればGrepで確認し、同書式で追記(User Quality=PASS、日付、根拠ID)。
- ARTIFACT_REGISTRY.md: Grep `User Quality|Full Audio`で書式確認→Space Weapons A2/B1・AI Control A2/B1の行を追加(User Quality=PASS 2026-09-17、URL・player path・Gate結果)。Personalized News A2はUser Quality=NG(Voices仕様レビュー中)で追加。

### 6. Status整理(報告に明記)
AI Control A2/B1=USER_TEST_READY(試聴PASS)。Space Weapons A2=タイトル以外無変更確認後USER_TEST_READY(試聴PASS)。Space Weapons B1=USER_TEST_READY(試聴PASS)。Personalized News A2=現行成果物ユーザー品質NG(基盤はPRODUCTION_WIRED維持)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)
従来どおり。T-0: 委任文を`docs/pm/delegation_log/USER-FEEDBACK-CLOSEOUT-AND-VOICES-SPEC-REVIEW-01_closeout.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。

## 事前指定Read/Grep一覧
- `git diff --stat c2af33f2..6d088d2e -- er014_output/user_test_news_2ep_01/space_weapons/`(A2/B1配下)、`.../space_weapons/a2/audit/tts_generation_results.json`: Grep `"sha256"|segment_id|topic_intro`(現行)と`git show c2af33f2:er014_output/user_test_news_2ep_01/space_weapons/a2/audit/tts_generation_results.json | findstr sha256`(修正前)の比較
- `CURRENT_SPEC.md`: Grep `平均文長|11語|18語|1文1メッセージ|spoken-first|B1-B Difficulty|語彙数上限|A2超語彙|REJECTED.*語彙`→行番号のみ
- `DECISION_LOG.md`: Grep `語彙数上限|A2超語彙|vocabulary cap|REJECTED`→却下記録の行番号、`^## PM-CLOSEOUT-CONSOLIDATION-136`(直近書式)
- `OPEN_ITEMS.md`: L295付近(OPEN-151)、L304-314(OPEN-159〜163書式)
- `ARTIFACT_REGISTRY.md`: Grep `User Quality|Full Audio|PASS`→書式
- `docs/pm/RESULT_PACKET_CLOSEOUT_136.md` 1節(URL)、`docs/pm/PM_BRIEF.md` L135-159

## Git
明示add(SSOT 4ファイル+ARTIFACT_REGISTRY+delegation_log+RESULT_PACKET)。メッセージ`USER-FEEDBACK-CLOSEOUT-01: AI Control A2/B1・Space Weapons A2/B1ユーザー試聴PASS反映+Personalized News A2品質NG記録+OPEN-164(News情報密度)登録`、trailer `Task-ID: USER-FEEDBACK-CLOSEOUT-AND-VOICES-SPEC-REVIEW-01`。push。

## 報告(`docs/pm/RESULT_PACKET_FEEDBACK_CLOSEOUT_01.md`、★★★★報告ここから/ここまで★★★★)
0. T-0 1. Space Weapons A2差分確認結果(変更ファイル一覧、segment sha256比較表、タイトル以外無変更の可否)→Status判定 2. Status整理表(5本) 3. OPEN-164登録内容(全文) 4. OPEN-151追記内容 5. DECISION_LOG行 6. CURRENT_SPEC注記(有無・行) 7. ARTIFACT_REGISTRY追記行 8. 難易度調整の既存仕様確認(行番号、却下記録) 9. Git SHA 10. API 0証跡 11. 未決事項/事前指定外Read。ユーザー向け表記は「B1」に統一。
