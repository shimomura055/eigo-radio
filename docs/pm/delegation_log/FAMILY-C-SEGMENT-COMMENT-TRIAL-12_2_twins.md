## 管理ID

`FAMILY-C-SEGMENT-COMMENT-TRIAL-12`(委任2: Digital Twins A2+B1+全Family展開候補のOpen Item登録)
並行タスクなし(委任1完了、直近commit `e01c3df8`)。報告は`docs/pm/RESULT_PACKET_T12_TWINS.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は本タスクで上書き可。

## 性質/到達上限Status/禁止事項

- 性質: Trial-11(Memory A2、ユーザー評価OK)のStory segmentation方式とA2 Comment理解ガイド型Promptを、Digital Twins A2/B1へ展開する仕様Trial。**1記事完結順序: Twins A2完成→commit→Twins B1完成→commit**。加えてSSOT作業(¥0): 全Family展開候補A/BのOpen Item登録。
- 到達上限Status: Twins A2/B1=`VALIDATED候補 / USER_LISTENING_PENDING`。新仕様はProduction未採用。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ変更しない、Production wiringを先回りしない。
- **旧成果物保存**: Trial-10 `er013_output/family_c_episode_trial_10/twins_a2/`・`twins_b1/`と`er013_family_c_episode_trial_10_twins_run.py`/`_twins_b1_run.py`は無編集(git statusで空確認)。新出力先`er013_output/family_c_episode_trial_12/twins_a2/`・`twins_b1/`、新スクリプト`er013_family_c_episode_trial_12_twins_run.py`(複製元: `er013_family_c_episode_trial_11_memory_run.py`のsegmentation/Comment Promptロジック+`er013_family_c_episode_trial_10_twins_run.py`の記事設定[Voice割当・Echo表記指示・Comment位置])と`er013_family_c_episode_trial_12_twins_b1_run.py`(複製元: `er013_family_c_episode_trial_12_memory_b1_run.py`のsegmentationロジック[段落境界空白修正・OPEN-156修正含む]+`er013_family_c_episode_trial_10_twins_b1_run.py`の記事設定)。Trial-11/12 memory・Trial-10 twinsの各スクリプトは編集しない(複製・import参照のみ)。
- **本文固定**: A2本文=`er013_output/family_c_future_trial_08/digital_twins/reader_facing_article.txt`(sha256 `b22e5f8e5f6951df302a31f7e83d1a6c9bef0d871dcfee65be480298d38a00b3`一致確認)。B1本文=Trial-10で独立生成済み`er013_output/family_c_episode_trial_10/twins_b1/reader_facing_article_b1.txt`(sha256記録)。Writer再実行禁止、Story本文変更禁止。
- 禁止: Opus、Writer再実行、Story/Key Phrase/Preview再生成、B1 Comment内容・Prompt変更、新Voice探索・Voice比較Trial、A/B大量生成、複数候補Commentの大量生成(Twins A2 Comment 1〜3は各1回生成、品質不足時のみ同一Promptで最大1回再生成)、Production-wide refactor、新Validator、hard cap Validator化、無関係なRepo監査、同一segmentの理由なき再生成、`er003_*`/`er012_*`/`er005_*`/`er006_*`編集、`CURRENT_SPEC.md`編集、`git add -A`/`stash`/`amend`、wavのcommit。
- 費用上限: A2 ¥45(Story再TTS+Comment 3件LLM/TTS+ASR)、B1 ¥35(Story再TTS+ASR)、合計¥80。超過見込みならそのlevelのみSTOP(完了分はcommit)。
- STOP条件(ユーザー指定): Story本文変更が必要/100語前後でも重大TTS欠落が繰り返す/大幅な追加コスト/新しいVoiceが必要/今回承認されていない新仕様が必要/Production Gate変更が必要。それ以外の軽微な問題は本episode内で最小個別修正して完成音声まで進める。軽微な表記差で無駄なretryを増やさない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(保存名: `docs/pm/delegation_log/FAMILY-C-SEGMENT-COMMENT-TRIAL-12_2_twins.md`)

## ユーザー指示(原文)

ユーザー原文(2026-09-16、FAMILY-C-SEGMENT-COMMENT-TRIAL-12)の本委任該当部分:

---
3. Story segmentation仕様: 基本原則: できるだけ自然な連続発話としてまとめ、必要な理由がある場所だけTTSを分割する。分割理由: Voiceが変わる/A2 Comment挿入位置/scene / semantic boundary/TTS安定性上、長くなりすぎる場合。避けること: 段落ごとの機械的分割/数語だけのnarrator segment/1文だけの不要な独立TTS/同一Voiceが続いているのに細かく分割/引用符だけを理由に同一Voiceの台詞を独立TTS化/"No,"のような短い同一Voice台詞を単独生成すること。同一Voiceで前後が自然につながる場合は、前後と一緒に生成する。

4. Segment長のTrial安全ガイド: 概ね100語以内を基本目安。120語を大きく超えない/150〜200語級にはしない/hard cap Validatorにはしない。word countだけで機械的に切らず、Voice連続性/自然な意味単位/scene/dialogue/Comment位置/TTS安定性を合わせて判断する。

6. Digital Twins A2: Story segmentationをMemory A2方式で見直す。特に短い、Maraの台詞/Echoの台詞/Echo said./The door opened. 等について、Voice境界は維持しつつ、同一Voice内で不必要に細かくなっているsegmentを整理する。EchoとMaraのVoiceが変わる境界を無理に統合しない。

7. Digital Twins A2 Comment生成Prompt: Memory A2 Trial-11でユーザー評価が良かった「理解ガイド型Comment」へ変更する。役割: 次に聞く英文を理解しやすくするため、状況・人物関係・場面転換・重要な選択肢など、理解に必要な情報だけを短く日本語で整理する。禁止: 聞いてみましょう/耳を傾けて/耳を澄ませて/注目してみましょう/これからどうなるでしょう/内容のない雰囲気誘導/結末の先取り/新Fact追加。生成後にもこれらを品質チェックする。特に旧Twins A2のComment 3「扉が開き、マラはピアノの前へ進みます。エコーに任せるかどうか、緊張の高まる場面です。」のように、次の英語理解に直接役立つ具体的なガイドを基準にする。Comment 1〜3を新Promptで生成する。

8. Digital Twins B1: Segmentation改善のみ適用。B1英語Commentは変更しない。既存のPreview/Key Phrase/Comment/共通音声assetで変更不要なものはreuseする。Story本文は変更しない。

9. 音声化: 試聴可能な状態まで完成させる。必要工程: 新segmentation/必要Story segmentのTTS/Twins A2 Comment 1〜3再生成・TTS/Assembly/Audio Validation/player生成。既存正常assetは最大限reuse。

10. Token / Cost Guard: 最小作業。禁止: Opus/Writer再実行/Story再生成/Key Phrase再生成/不要なPreview再生成/新Voice探索/A/B大量生成/Production-wide refactor/新Validator開発/無関係なRepo監査。同じsegmentを理由なく何度も再生成しない。重大なTTS mismatch以外の軽微な表記差で無駄なretryを増やさない。

11. 完了報告: episodeごとに: Segmentation(旧segment数→新segment数/旧最短・最長word count/新最短・最長word count/短segment統合の代表例/残した短segmentとその理由/最長segmentが安全ガイド内か)、Comment(Twins A2: 旧Comment 1〜3→新Comment 1〜3を提示。Twins B1はComment変更なしと明記)、Audio(duration/Audio Validation/player URL/direct audio URL/追加費用)。

12. 3episode完成時点ではSTOPして、USER_LISTENING_PENDINGとして報告する。今回のTrial生成タスク内では先回りしてProduction wiringしない。

STOP条件: Story本文変更が必要/100語前後でも重大TTS欠落が繰り返す/大幅な追加コストが必要/新しいVoiceが必要/今回承認されていない新仕様が必要/Production Gate変更が必要。それ以外の軽微な問題は、対象episode内で最小個別修正して試聴可能音声まで完成させる。
---

追加指示(2026-09-16、全Family展開候補のOpen Item化、原文):
---
今回のTrialで検証している以下2仕様について、Family C限定の仕様として閉じず、将来の全Family共通仕様候補としてOPEN_ITEMSへ登録してください。対象A: Story segmentation(同一Voiceの自然な連続性を優先/不要な短segmentを避ける/Voice変更点は分割/scene / semantic boundaryを考慮/概ね100語以内を運用目安/120語を大きく超えない/150〜200語級を避ける/word countだけで機械的に分割しない)。対象B: A2 Comment(「聞くことを促すメタナレーション」ではなく、「次の英語理解に必要な具体的contextを短く提供する理解ガイド」にする)。Open Itemの位置づけ: 今回はFamily CでのみTrial中/全Familyへの正式採用ではない/次回、Trend / Voices / Discovery等ほかFamilyで新規記事・音声を作る機会に、これらを織り込んだTrialを行う/他FamilyでのTrial結果を確認するまで全Family共通Production仕様にはしない/Familyごとの構造差があるため、無条件横展開せず適用可能性を確認する/次回ほかFamily作成時に見落とさないよう、OPEN_ITEMSの次Actionに明記する。既存Open Itemに適切な項目がある場合はそこへ統合し、なければ新規Open Itemとして起票してください。今回のFamily C TrialのProduction採用判断とは別管理にしてください。
---

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET.md`(Trial-11): 8-36行(A2 segmentation設計表・Comment Trial-11 Prompt要点・新旧Comment)
- `docs/pm/RESULT_PACKET_T12_MEMORY_B1.md`: 8-29行(B1 segmentation設計・統合例・Comment位置スナップ)、41行(段落境界空白バグの修正内容)
- `docs/pm/RESULT_PACKET_UT06_C.md`: 12-21行(Trial-10 Twins A2: Voice割当[narrator=Aoede/Echo=Erinome]、Comment位置C2=段落13/14・C3=段落22/23、Echo表記指示、旧Comment全文は`twins_a2/comments_ja.md`)、23-39行(Trial-10 Twins B1: 話者判定キーワード、OPEN-156修正、Comment位置)
- `er013_output/family_c_episode_trial_10/twins_a2/comments_ja.md`: 全文(旧Comment 1〜3、報告で並記)
- `er013_output/family_c_episode_trial_10/twins_a2/segments.json`・`twins_b1/segments.json`: 全文(旧segmentのid/voice/raw_text。旧最短/最長word count算出、統合対象特定)
- `er013_output/family_c_future_trial_08/digital_twins/reader_facing_article.txt`・`er013_output/family_c_episode_trial_10/twins_b1/reader_facing_article_b1.txt`: 全文(segmentation設計対象)
- `er013_family_c_episode_trial_11_memory_run.py`: Grepで`segmentation_plan|def plan_segments|def build_story_segments|merge|lead_in|trailing|--plan-only|COMMENT_1_ROLE_JA_TRIAL11|COMMENT_2_ROLE_JA_TRIAL11|COMMENT_3_ROLE_JA_TRIAL11`→A2 segmentationロジックとTrial-11 Comment Prompt定数の範囲Read
- `er013_family_c_episode_trial_12_memory_b1_run.py`: Grepで`def plan_segments|def build_story_segments|段落境界|" ".join|classify_quote_voice|--plan-only`→B1 segmentationロジック(空白修正・OPEN-156修正含む)範囲Read
- `er013_family_c_episode_trial_10_twins_run.py`: 1-120行(記事設定: ARTICLE_PATH/OUT_DIR/ARTICLE_ID/Voice/日本語タイトル)、Grepで`Echo|エコー|classify_quote_voice|TWIN_VOICE|tts_twin|PREVIEW_ROLE_JA|COMMENT_.*_ROLE_JA|comment_placement`→Echo表記指示・話者判定キーワード・Comment位置の記事固有箇所範囲Read
- `er013_family_c_episode_trial_10_twins_b1_run.py`: 1-120行、Grepで`echo|twin|classify_quote_voice|tts_support_charon|import er013_family_c_episode_trial_10_twins_run`→記事固有箇所・import先
- `OPEN_ITEMS.md`: Bash(python)で`OPEN-147|OPEN-156|segment|Comment役割|Comment Contract|メタナレーション`を含む行の先頭200字を抽出(既存Open Itemへの統合可否判断。Readツールは単一行長超過でエラーになるため使わない)。既存最大番号をGrep`^\| OPEN-1[0-9][0-9]`で確認。
- `docs/pm/PM_GOVERNANCE.md`: Grepで`15-8`→該当節。`docs/pm/PM_BRIEF.md`: 135-159行。

## 事前指定Grep一覧+追記位置・更新位置の手順

1. Twins A2 segmentation: 旧`segments.json`(22 segment: narrator12/twin10)から短segment("Echo said."/"The door opened."/Maraの短い台詞等の同一Voice細切れ)を特定。Voice変化点(Mara[narrator=Aoede]⇄Echo[Erinome]、引用符なし表示メッセージ1件含む)は**必ず分割**し無理に統合しない。同一Voice連続部分(narrator側のlead-in/trailing/"Echo said."等)は前後と結合。Comment挿入位置(C2=段落13/14境界、C3=段落22/23境界、Trial-10の意味的判断を維持)・scene boundaryで区切り、概ね100語以内・120語超回避。設計表を`twins_a2/segmentation_plan.json`へ保存、`--plan-only`ドライランで語数分布確認(150語以上0件、120語超原則0件、Echo台詞以外の10語未満独立segment 0件)後に本実行。Echo台詞が短く連続する箇所はVoice境界のため短segmentが残る(理由付きで報告)。
2. Twins A2 Comment: Trial-11の`COMMENT_*_ROLE_JA_TRIAL11`をTwins用に移植(記事固有の表記指示[「エコー」片仮名・算用数字]はTrial-10 twinsから維持)。旧Prompt(`_TRIAL10_PREV`)は残置。生成後、禁止語句Grep(`聞いてみましょう|耳を傾け|耳を澄ま|注目して|どうなるでしょう`)0件、結末先出しなし・新Factなしを目視確認。旧Comment 3「扉が開き、マラはピアノの前へ進みます。エコーに任せるかどうか、緊張の高まる場面です。」を具体性の基準にする。
3. Twins B1 segmentation: 旧`segments.json`(53 segment: narrator42/twin11)を、委任1 Memory B1と同じロジック(段落境界空白修正・OPEN-156修正含む)で再構成。Voice変化点(Echo=Erinome)は分割、narrator細切れは統合。B1 Comment位置(累積語数40.7%/73.2%近傍の意味的境界を維持し新境界へスナップ、差を報告)。設計表・ドライラン同上。
4. 既存asset reuse: Twins A2=Trial-10 `twins_a2/`からIntro/Outro/SFX/Welcome/topic_intro_en/japanese_title/preview_ja/kp英語5件・日本語5件等の非Story・非Comment wav/mp3と`key_phrases/`・`preview.txt`をコピー(`.ok`含む)。再TTS=新Story segment+Comment 3件。Twins B1=Trial-10 `twins_b1/`からpreview_en/comment_1〜3(Charon)/kp/topic_intro_en/共通assetをbyte-identicalコピー、`comments_en.md`・`reader_facing_article_b1.txt`もコピー。再TTS=新Story segmentのみ。
5. Voice: Twins A2/B1ともnarrator・Mara=Aoede、Echo=Erinome(Trial-10と同一、変更なし)。B1 Support=Charon既存音声reuse。
6. **Open Item登録(¥0)**: Grep結果に基づき、対象A/Bを(i)既存Open Itemへ統合するか(ii)新規起票するかを判断。判断基準: OPEN-147はFamily C全体サマリのため「全Family共通候補」の管理場所としては不適(Family C Trial採用判断と別管理にするというユーザー指示に反する)→原則**新規2件**(対象A=`OPEN-157`候補「全Family共通候補: Story TTS segmentation原則」、対象B=`OPEN-158`候補「全Family共通候補: A2 Comment理解ガイド型」、番号は既存最大番号+1/+2で確定)。既存にsegment長やComment役割の全Family横断項目があればそこへ統合し理由を報告。各行の必須内容: 位置づけ(Family CでのみTrial中/全Family正式採用ではない/他FamilyでのTrial結果確認まで全Family共通Production仕様にしない/Familyごとの構造差があるため無条件横展開せず適用可能性を確認)、**次Action**「次回Trend/Voices/Discovery等ほかFamilyで新規記事・音声を作る機会に、本原則を織り込んだTrialを行う(見落とし防止)」、Family C Trial-12のProduction採用判断(OPEN-147管理)とは別管理である旨、参照(Trial-11/12 RESULT_PACKET・DECISION_LOG)。Status=`OPEN / DEFERRED_UNTIL_NEXT_FAMILY_TRIAL`(既存語彙に合わせて調整可)。
7. SSOT追記位置: `Grep pattern="^## FAMILY-C-SEGMENT-COMMENT-TRIAL-12(委任1" path=DECISION_LOG.md`→そのエントリ末尾直後に`## FAMILY-C-SEGMENT-COMMENT-TRIAL-12(委任2: Digital Twins A2+B1+全Family展開候補Open Item)`を追加(索引1行も)。`OPEN_ITEMS.md`はpythonでOPEN-147行末追記+新規行を末尾に追加。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`末尾にTwins A2 Comment再生成の行を追加。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FAMILY-C-SEGMENT-COMMENT-TRIAL-12_2_twins.md --json-out docs\pm\delegation_log\FAMILY-C-SEGMENT-COMMENT-TRIAL-12_2_twins_check.json
```

本文sha256:
```
.venv\Scripts\python.exe -c "import hashlib;[print(p,hashlib.sha256(open(p,'rb').read()).hexdigest()) for p in ['er013_output/family_c_future_trial_08/digital_twins/reader_facing_article.txt','er013_output/family_c_episode_trial_10/twins_b1/reader_facing_article_b1.txt']]"
```

Twins A2(上限¥45):
```
.venv\Scripts\python.exe er013_family_c_episode_trial_12_twins_run.py --plan-only
.venv\Scripts\python.exe er013_family_c_episode_trial_12_twins_run.py --budget-jpy 45
```
Twins B1(上限¥35、A2 commit後):
```
.venv\Scripts\python.exe er013_family_c_episode_trial_12_twins_b1_run.py --plan-only
.venv\Scripts\python.exe er013_family_c_episode_trial_12_twins_b1_run.py --budget-jpy 35
```
(複製元argparseに合わせ実引数を確定し全文報告。)

禁止語句検証(A2):
```
.venv\Scripts\python.exe -c "import re;t=open('er013_output/family_c_episode_trial_12/twins_a2/comments_ja.md',encoding='utf-8').read();m=re.findall(r'聞いてみましょう|耳を傾け|耳を澄ま|注目して|どうなるでしょう',t);print('BANNED_HITS=',len(m),m)"
```

回帰: `er013_family_c_episode_trial_11_memory_test_01.py`・`er013_family_c_episode_trial_12_memory_b1_test_01.py`を複製してTwins用`er013_family_c_episode_trial_12_twins_test_01.py`(A2: 本文sha一致・Comment 4不在・禁止語句0件・150語以上なし・Echo voice=Erinome、B1: 本文sha一致・日本語タイトル不在・Comment英語不変・Support=Charon・150語以上なし、計10件程度)を作成し:
```
.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_12_twins*_test_*.py"
```
Trial-10/11/12memory無変更確認: `git status --porcelain er013_output/family_c_episode_trial_10/ er013_output/family_c_episode_trial_11/ er013_output/family_c_episode_trial_12/memory_b1/`が空。

Web到達確認(各push後、raw.githackはUser-Agent付きGET、CDN遅延時60秒待ち最大3回):
```
.venv\Scripts\python.exe -c "import urllib.request as u;[print(u.urlopen(u.Request(x,headers={'User-Agent':'Mozilla/5.0'})).status,x) for x in ['https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_12/twins_a2/player.html','https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_12/twins_b1/player.html']]"
```
episode mp3 direct URL(A2/B1各1件)も同様にGET確認、計4件のstatusを報告。

## SSOT追記文

`DECISION_LOG.md`(委任1エントリ末尾直後):
```
## FAMILY-C-SEGMENT-COMMENT-TRIAL-12(委任2: Digital Twins A2+B1+全Family展開候補Open Item)

- 日付: 2026-09-16
- 種別: Trial-11方式(segmentation/A2 Comment理解ガイド型)のDigital Twinsへの展開Trial。新仕様はProduction未採用(3 episodeユーザー試聴OK後に正式採用対象A/BをAPPROVED_FOR_PRODUCTION扱い、別途Production wiring。本Trialで先回りしない)。
- Twins A2: 本文固定(sha256一致)。旧<n> segment(最短<n>/最長<n>語)→新<n>(最短<n>/最長<n>語)。統合代表例<要約>。残した短segment<Echo台詞等と理由>。Comment 1〜3をTrial-11型Promptで再生成(禁止語句0件)。旧→新Comment全文はRESULT_PACKET参照。Voice=Aoede/Erinome不変。Audio Validation <PASS/FAIL>、duration <秒>(旧301.281秒)。費用¥<実測>。Status=VALIDATED候補/USER_LISTENING_PENDING。
- Twins B1: 本文固定(sha256 <値>)。旧<n>→新<n>(最短/最長)。Comment/Preview/KP=Trial-10既存Charon音声reuse・内容不変。Audio Validation <PASS/FAIL>、duration <秒>(旧364.554秒)。費用¥<実測>。Status=VALIDATED候補/USER_LISTENING_PENDING。
- 全Family展開候補Open Item: 対象A(Story segmentation原則)=<OPEN-xxx 新規/統合先>、対象B(A2 Comment理解ガイド型)=<OPEN-yyy 新規/統合先>。位置づけ=Family CのみTrial中・全Family正式採用ではない・他Family(Trend/Voices/Discovery等)の次回新規記事作成時にTrialを織り込む・構造差のため無条件横展開しない。Family C Trial採用判断(OPEN-147)とは別管理。
- 費用合計¥<実測>。Family C累計¥619.50+¥<実測>=¥<合計>。
- 参照: `docs/pm/RESULT_PACKET_T12_TWINS.md`、commit <A2 hash>/<B1 hash>
```
索引1行。`OPEN_ITEMS.md` OPEN-147行末: ` 2026-09-16追記(TRIAL-12 委任2): Digital Twins A2/B1へsegmentation展開+A2 Comment理解ガイド化(旧版保存)、Audio Validation <結果>、費用¥<実測>、Family C累計¥<合計>。Trial-12 3 episode(Memory B1/Twins A2/Twins B1)すべてUSER_LISTENING_PENDING。試聴OK後に正式採用対象A/BをAPPROVED_FOR_PRODUCTION扱いとし別途Production wiring(未実施)。全Family共通候補はOPEN-<xxx>/<yyy>で別管理。`
新規Open Item行(末尾、既存行の表形式に合わせる): 上記Grep 6の必須内容。
`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ形式で上書き(報告単位Status: Trial-12 Memory B1/Twins A2/Twins B1=USER_LISTENING_PENDING、Discovery B1/A2=USER_DECISION_REQUIRED継続、OPEN-154/155=DEFERRED)。

## Git(明示add対象・コミットメッセージ・trailer)

- A2完成時・B1完成時で分けてcommit(Open Item登録はB1 commitに同梱)。明示add対象(wav除外、mp3必須): 新規スクリプト2件+テスト1件、`er013_output/family_c_episode_trial_12/twins_a2/`・`twins_b1/`配下(委任1と同種)、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/FAMILY-C-SEGMENT-COMMENT-TRIAL-12_2_twins.md`、同`_check.json`、`docs/pm/RESULT_PACKET_T12_TWINS.md`。
- `family_c_episode_trial_10/`・`trial_11/`・`trial_12/memory_b1/`配下、`er006_output/`・`er011_output/`の既存M、`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??は触らない。
- コミットメッセージ: `FAMILY-C-SEGMENT-COMMENT-TRIAL-12 (2-A2): Digital Twins A2へsegmentation展開+Comment理解ガイド化(旧版保存)` / `FAMILY-C-SEGMENT-COMMENT-TRIAL-12 (2-B1): Digital Twins B1へsegmentation展開+全Family展開候補Open Item登録`
- trailer: `Task-ID: FAMILY-C-SEGMENT-COMMENT-TRIAL-12`
- push: 各commit後`git push origin main`。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_T12_TWINS.md`に:
1. T-0結果、A2/B1本文sha256、Trial-10/11/12memory無変更確認
2. Twins A2 Segmentation: 旧→新segment数、旧最短/最長、新最短/最長、設計表(id/voice/段落範囲/語数/分割理由)、短segment統合の代表例、残した短segmentと理由(Echo/Mara Voice境界)、最長が安全ガイド内か、Comment位置維持の確認
3. Twins A2 Comment: 旧1〜3→新1〜3並記、Prompt移植内容、禁止語句検証、model/routing、生成回数
4. Twins B1 Segmentation: 同2の項目+Comment位置スナップ差。「Twins B1はComment変更なし(Trial-10 Charon音声reuse)」と明記
5. Voice: A2/B1ともnarrator=Aoede/Echo=Erinome不変、runtime evidence
6. Audio(A2/B1各): TTS segment数と失敗/retry内訳、ASR 4者一致(表記揺れ列挙)、Audio Validation、duration(旧比)、player URL、direct audio URL、Web到達確認、追加費用(LLM/TTS/ASR/その他)
7. Open Item登録結果: 対象A/Bの番号(新規/統合)、判断理由、登録行の全文、次Action文言
8. PM: Status=USER_LISTENING_PENDING(3 episode)、Production採用なし、STOP該当有無、恒久課題候補の追加有無
9. 回帰結果、commit hash・push結果・残差分要約
10. 事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(「B1B」不使用)。
