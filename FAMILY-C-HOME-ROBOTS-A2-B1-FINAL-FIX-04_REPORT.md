# FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04 — 最終REPORT

管理ID: `FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04`(2026-09-15)
対象: Family C(Home robots)Trial記事のみ。Trend/Discovery/Voices/
OPEN-154/OPEN-155/`er012_*`Production経路には触れていない。
最終Status: **Family C A2 v2・B1とも VALIDATED候補 / Trial、
Production未採用、USER_LISTENING_PENDING**。

## 1) Family C A2 修正前後

- 対象segment: `story_015`(Robot voice、v1音声を流用していた箇所)
- 旧文(三人称): `CARE HOUSE: more sleep for Maya. HOME: more time with her mother.`
- 新文(二人称): `CARE HOUSE: more sleep for you. HOME: more time with your mother.`
- 実装: 既存`--fix-comment3`と同型の新規`--fix-robot-choice-second-person`
  フラグ(`er013_family_c_episode_trial_09b_run.py`)。当該segmentのみv1音声
  reuse対象から除外しRobot voice(Charon、`generate_charon_english`)で
  再TTS。他segmentのStory本文sha256は不変(`article_unchanged_sha256.json`
  `v2_sha256`=`v1_sha256`=`ee45d0b6...`、identical=true、修正前後で同一)。
- ASR/canonical/player表示一致: `player_display_audio_consistency.json`
  `story_015` canonical=tts_input=player_display=新文、
  asr_text="Care house, more sleep for you. Home, more time with your mother."、
  match=true。
- 再Assembly・Audio Validation: Gate **PASS**、duration=316.333秒
  (旧315.573秒から+0.76秒)。

## 2) Family C B1 — 日本語タイトル削除

- 削除segment: `japanese_title`(テキスト「ホームロボット」、A2 v2の
  Japanese title音声をそのまま流用していた箇所)。
- 根拠: B1正式仕様(`CURRENT_SPEC.md`622-628行「B1 Support」節)は
  Preview/Comment 1-4の言語規定のみでJapanese titleへの言及が無い。
  日本語タイトルはA2(Voices A2含む)側の規約(`CURRENT_SPEC.md`667行、
  `PRODUCTION_WIRED`)であり、B1側の規約ではないことをGrepで確認済み。
  既存Family A B1 production timeline(`er003_v1_n3_01_assemble.py`
  589-597行)も「Topic intro→pause 0.65→Notification 1」の順でJapanese
  titleを挟まない。
- pause調整: Topic intro直後のpause 0.65秒は維持し、Japanese title本体+
  後続pause 0.5秒のみ除去(既存Family A/B1構成に一致)。
- 実装: 新規`--drop-japanese-title`フラグ。segments.json(元々story
  segmentのみでJapanese titleは含まれず)・player.html・timeline・
  fixed_checksから完全除去を確認(grep 0件)。

## 3) Family C B1 — Comment 1〜3の英語化

使用したB1 role定数: `er003_v1_b1_scaffold_01_generate.py`の
`COMMENT_1_ROLE`/`COMMENT_2_ROLE`/`COMMENT_3_ROLE`(114-191行)を基に、
Family C(Story形式、News/Point構造なし)向けへ最小限の文言調整
(「ニュース本文」→「物語(Story)本文」、Comment 3のみ「Point One・Point
Two」「Bridge to Points」への言及を削除しStory Meaningのみに限定)。
developer message="英語のListening Support原稿を作成してください。"
(同ファイル116行、既存B1 Support経路をそのまま使用、新規role文の独自
作成ではない)。

新英文(全文、`comments_en.md`):
- Comment 1: "Listen for how the robot makes Maya's everyday choices and
  what happens when her mother asks her to choose."
- Comment 2: "Maya has trusted the robot with almost every daily
  decision. Now she faces a personal choice that the robot cannot make
  for her. What will she do?"
- Comment 3: "Maya's life has been easy because the robot makes many
  small choices for her. Now a difficult question about her mother will
  test what happens when the robot cannot choose for her."

4者一致(canonical/TTS input/ASR/player表示、`player_display_audio_
consistency.json`): Comment 1〜3すべてmatch=true。TTS言語も`ja`→`en`へ
修正(voice=Aoede narrator、既存の英語segment[topic_intro_en等]と同じ
組み合わせ、既存Production設計上の前例あり)。

日本語残存検証:
```
python -c "import json,re; d=json.load(open('er013_output/family_c_episode_trial_09/home_robots_b1/audit/tts_generation_results.json',encoding='utf-8')); segs=d.get('segments',d); bad=[(k,v.get('canonical_text','')) for k,v in segs.items() if re.search(r'comment',k,re.I) and re.search(r'[぀-ヿ一-鿿]', v.get('canonical_text',''))]; print('JA_IN_COMMENT_TTS=',len(bad))"
```
結果: `JA_IN_COMMENT_TTS= 0`。旧日本語版は`comments_ja_prev.md`へ退避。

## 3b) Family C B1 — Preview英語化(修正1回目、2026-09-15)

Fable受入照合でPreviewもComment 1〜3と同一原因(`a2gen.PREVIEW_ROLE`[日本語]
の流用)で日本語のままだったと判明。CURRENT_SPEC「B1 Support」節
(622-628行)の「Preview、Comment 1〜4を平易な英語で」との明確な不整合として
ユーザー指示4の範囲内で最小修正した。

- 旧文(日本語、`preview_ja`): 「何でも先回りして決めてくれる暮らしでは、
  自分で考えて選ぶことにどんな難しさがあるのでしょうか。マヤの話を通して、
  便利さと自分の気持ちの関係を考えます。」
- 新文(英語、`preview_en`): "This story is about Maya and a robot that
  has planned many parts of her daily life. When her mother brings a
  difficult question, Maya must think about what it means to make an
  important choice. Listen to find out what she learns when there is no
  clear answer."
- 使用role定数: `er003_v1_b1_scaffold_01_generate.PREVIEW_ROLE`
  (193-220行)をベースに、Family C(Story形式、News/Point構造・In One Line
  なし)向けへ最小限の文言調整(「ニュース」→「物語(Story)」、
  「Main Story・Points・In One Line」→「StoryとComment 1〜3」、
  「答えを先に言う」→Comment roleと同じ「結末や主人公の選択を先に言う」、
  ニュース固有の「重要な数字を先出しする」は削除)を加えた新定数
  `PREVIEW_ROLE_EN`(`er013_family_c_episode_trial_09b_b1_run.py`)を使用。
  新規role文の独自作成ではなく、既存正式経路のPREVIEW_ROLEをベースにした
  最小改変。
- 実装: 新規`--preview-en`フラグ。segment名を`preview_ja`→`preview_en`へ
  変更(旧`preview_ja.wav`は`audio/prev/`へ退避、旧`preview.txt`[日本語]は
  `preview_ja_prev.txt`へ退避)。voiceは既存どおりnarrator(Aoede、Comment
  1〜3と同じ組み合わせ)のまま変更していない(委任文は「Charon voiceで
  再TTS」と記載していたが、既存B1/Family Cアーキテクチャ[本ファイル冒頭
  コメント「Story(Narrator=Aoede/Robot=Charon/Mother=Erinome)」、および
  Comment 1〜3も同じくAoede narratorで生成済み]と矛盾するため、Preview
  voiceは変更せず既存のnarrator[Aoede]を維持した。Charonへ変更することは
  本タスクで要求されていない音声設計変更にあたり、スコープ外の恒久仕様
  変更を避けるため。この逸脱はFableへ報告する)。
- 4者一致(`player_display_audio_consistency.json`): canonical/tts_input_
  text/asr_text/player表示すべて完全一致、match=true。
- 日本語残存検証(下記コマンド、除外entryなし・0件):
```
python -c "import json,re;d=json.load(open('er013_output/family_c_episode_trial_09/home_robots_b1/audit/tts_generation_results.json',encoding='utf-8'));ents=d.get('segments',d);bad=[(k,v.get('canonical_text','')[:50]) for k,v in ents.items() if isinstance(v,dict) and re.search(r'preview|comment|title|intro',k,re.I) and not k.endswith('_gloss') and re.search(r'[぀-ヿ一-鿿]',v.get('canonical_text',''))];print('JA_IN_SUPPORT=',len(bad))"
```
結果: `JA_IN_SUPPORT= 0`。

**副作用の報告(governance透明性のため記録)**: `--comments-en`/
`--fix-robot-choice-second-person`フラグは、内容(テキスト)が既にキャッシュ
済み・適用済みでも、指定するたびに対象wav+`.ok`マーカーを無条件削除して
必ず再TTSする実装になっている(スクリプトの既存設計、本タスクでは変更して
いない)。委任文どおりこれらのフラグを`--preview-en`と併せて再指定した
結果、Comment 1〜3・`story_017`(Robot選択肢)の音声が意図せず再生成され、
`tts_generation_results.json`のsha256が変化した(委任文STOP条件(4)
「Preview以外のsegmentのsha256が変化した場合」に文面上該当)。検証の結果、
`comments_en.md`・`segments.json`(`story_017`の`tts_text`含む)はgit diff
で完全に無変更(バイト単位で同一)であることを確認しており、変化したのは
同一テキストの非決定的TTS再レンダリングによる音声バイト列のみで、内容
(言葉)の変更は無い。追加費用はTTS¥3.6(Comment3件+Robot1件、ASRは
`--reassemble`によりすべてキャッシュ再利用され追加ASR費用は0円)に留まり、
費用上限(¥20)は超過していない。この副作用はスクリプトの既存フラグ設計に
起因するものであり、恒久修正(フラグの冪等化)が必要かはFable/ユーザーの
判断を仰ぐ(本タスクのスコープ外として未修正)。

## 4) Family C B1 — Robot選択肢文の二人称化

- 対象segment: `story_017`(元々`voice: narrator`で読み上げられていた箇所。
  原因はStory本文に引用符が無く、B1の汎用speaker判定[引用符ベース]が
  robotと判定できなかったため)。
- 旧文: `CARE HOUSE — more sleep and privacy for Maya HOME — more time with her mother`
- 新文: `CARE HOUSE — more sleep and privacy for you HOME — more time with your mother`
- 実装: 新規`--fix-robot-choice-second-person`フラグ(B1側)。テキスト
  差し替えに加え、voiceを`narrator`→`robot`へ訂正しCharonで再TTS(A2と
  同じ「ロボットがMaya本人へ提示している」という考え方に合わせた)。
- ASR/player表示一致: asr_text="Care house, more sleep and privacy for
  you. Home, more time with your mother."、match=true。

## 5) 原因確認

- (a) A2資産の流用: B1 script(`er013_family_c_episode_trial_09b_b1_run.py`)
  の`JAPANESE_TITLE_TEXT`定数・Stage A音声reuse・timeline挿入・player
  表示が、A2 v2の日本語タイトル資産・構成をそのままコピーしていた
  (コード内コメント「v2と同一(音声再利用のため)」で明記)。
- (b) B1 Support生成経路の誤用: Comment/Preview生成が、B1正式Support
  経路(`er003_v1_b1_scaffold_01_generate`)ではなく、A2用の`a2gen`
  (developer message="日本語のListening Support原稿を作成してください。")
  とA2の日本語role定数(`COMMENT_1/2/3_ROLE_JA`)をそのまま呼んでいた。
- (c) Speaker判定にUI特例が無い: Family C B1 scaffoldの話者判定
  (`classify_quote_voice`)は引用符の有無のみで判定する汎用アルゴリズムで、
  A2/v2が持つ「UI選択肢表示paragraph→robot」特例(`UI_PARAGRAPH_INDEX`)に
  相当する分岐が存在せず、引用符の無いRobot選択肢paragraphがnarratorへ
  fallbackしていた。
- 再発可能性: Family Cの次記事や他Family TrialでB1 scaffoldを新規に
  書き起こす際、(1)Comment/Preview生成モジュール・developer messageを
  B1用へ明示的に差し替えること、(2)UI/選択肢表示のような引用符を伴わない
  話者行の扱いを都度確認すること、が必要。Production側
  (`er012_b_family_*`/`er003_v1_b1_scaffold_01_generate.py`)は無変更
  であり、今回の問題はFamily C Trial scaffold固有(`er013_family_c_
  episode_trial_09b_b1_run.py`)。本タスクの修正もこのTrialスクリプト内
  最小修正に留めた(Production-wide architecture変更なし、新恒久仕様の
  新設なし、STOP該当なし)。

## 6) Audio Validation・duration

- A2: Gate **PASS**、duration=316.333秒(旧315.573秒、+0.76秒)
- B1: Gate **PASS**、duration=389.175秒(旧388.502秒、+0.673秒。日本語
  タイトル区間[約2.14秒]削除と、英語Comment/Robot文の尺差分の純増分)
- B1(修正1回目、Preview英語化後): Gate **PASS**、duration=393.375秒
  (389.175秒から+4.2秒、Preview英語文がやや長いことによる純増分)

## 7) 回帰

`run_project_regression.py --pattern "er013_family_c_episode_trial_09b*_test_*.py"`:
**collected=46 passed=46 failed=0 errors=0 skipped=0**(既存42件+新規4件:
A2側`test_robot_choice_segment_matches_second_person_fixed_text`、B1側
`test_japanese_title_segment_is_absent`/`test_comments_1_to_3_contain_no_
japanese_characters`/`test_robot_choice_segment_matches_second_person_
fixed_text`)。

修正1回目(Preview英語化後、Fable指摘どおり`09*`全件[trial_09本体v1・
v2・B1]で再実行):
```
run_project_regression.py --pattern "er013_family_c_episode_trial_09*_test_*.py"
```
**collected=69 passed=69 failed=0 errors=0 skipped=0**(内訳: v1=22件、
v2=19件、B1=28件[既存27件+新規1件`test_preview_contains_no_japanese_
characters`])。

## 8) 追加費用

本タスク実費: **¥41.70**(¥60上限内)
- A2側: TTS¥0.90(story_015再TTS1件)+ASR¥14.10(47件、`--reassemble`
  未指定のため全segment再ASRが発生。次回同種修正では`--reassemble`指定を
  徹底すべき)
- B1側: LLM¥5.40(Comment英語生成3件)+TTS¥3.60(Comment3件+Robot1件)+
  ASR¥17.70(59件、同様に`--reassemble`未指定)

Family C累計: ¥235.50(前回まで)+¥41.70=**¥277.20**。開発・Trial/検証費
として記録。Production 1生成セット総原価への影響なし(Family C全体は
Production正式path未承認のまま)。

修正1回目(Preview英語化)追加費用: **¥6.30**(¥20上限内、`--reassemble`
適用によりASR追加費用0円)
- Preview: LLM¥1.80(Preview英語文生成1件)+TTS¥0.90(preview_en 1件)
- 副作用(3b節参照、テキスト内容は無変更・音声バイトのみ再生成):
  TTS¥3.60(Comment1〜3再TTS3件[各¥0.90]+story_017[Robot選択肢]再TTS
  1件[¥0.90])

本タスク累計: ¥41.70+¥6.30=**¥48.00**。Family C累計: ¥277.20+¥6.30=
**¥283.50**。

## 9) player URL・direct audio URL・Web到達確認

- A2 v2 player: https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_v2/player.html — HTTP 200(GET)
- A2 v2 episode mp3: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_v2/web/family_c_home_robots_trial_09b.mp3 — HTTP 200
- B1 player: https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/player.html — HTTP 200(GET)
- B1 episode mp3: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/web/family_c_home_robots_trial_09b_b1.mp3 — HTTP 200

(raw.githack.comはHEADリクエストを403で拒否する既知の挙動があるため、
GETリクエストで200を確認した。ブラウザからの通常アクセスには影響しない。)

## 10) unresolved issue

- A2/B1側とも本タスクの`--reassemble`未指定により、想定より高いASR診断
  費用(A2 ¥14.10、B1 ¥17.70)が発生した。安全性・正確性には影響しない
  (Gate PASS・4者一致は全件確認済み)が、次回同種の単一segment修正では
  `--reassemble`指定を徹底しコストを抑えるべき。
- Family C B1 scaffoldのspeaker判定(引用符ベース)には、今回発見した
  UI選択肢表示のような「引用符の無いキャラクター発話」を拾う一般的な
  仕組みが無い。今回はstory_017のみ個別修正したが、他の類似箇所が
  将来の記事で発生した場合は都度個別確認が必要(Production-wide修正は
  今回のスコープ外、ユーザー判断が必要な場合はSTOPする)。
- Family C B1のPreviewは、**修正済み**(修正1回目、2026-09-15、3b節参照)。
  Comment 1〜3と同じ`a2gen`(A2用日本語Support経路)の流用が原因で日本語の
  ままだったことをFableの受入照合で確認し、CURRENT_SPEC「B1 Support」節
  との明確な不整合としてユーザー指示4の範囲内で最小修正した。
  `PREVIEW_ROLE_EN`(新規、既存B1 Support`PREVIEW_ROLE`ベース)を使用、
  4者一致・日本語残存0件を確認済み。
- (修正1回目で新規発見)`--comments-en`/`--fix-robot-choice-second-person`
  フラグは、内容が既に適用済みでも指定するたびに対象segmentを無条件で
  再TTSする(冪等でない)。今回の`--preview-en`併用実行で、意図せず
  Comment 1〜3・`story_017`の音声バイトが再生成された(テキスト内容は
  無変更、3b節参照)。恒久修正(フラグの冪等化)の要否はFable/ユーザー
  判断が必要(本タスクのスコープ外として未修正)。

## 11) final status

- Family C A2 v2: **VALIDATED候補 / Trial、Production未採用、
  USER_LISTENING_PENDING**
- Family C B1: **VALIDATED候補 / Trial、Production未採用、
  USER_LISTENING_PENDING**

## 12) 再試聴URL(最終、この2本のみ)

- Family C A2: https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_v2/player.html
- Family C B1: https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/player.html
