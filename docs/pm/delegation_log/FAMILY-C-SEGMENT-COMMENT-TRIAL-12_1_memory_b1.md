## 管理ID

`FAMILY-C-SEGMENT-COMMENT-TRIAL-12`(委任1: Memory B1+Memory A2 Trial-11 VALIDATED記録)
並行タスクなし(直近commit `89bbffcb`)。報告は`docs/pm/RESULT_PACKET_T12_MEMORY_B1.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は本タスクで上書き可。

## 性質/到達上限Status/禁止事項

- 性質: Memory A2 Trial-11でユーザー評価「問題なし」だったStory segmentation方式を、Memory B1へ展開する仕様Trial。B1英語Comment/Preview/Key Phraseは変更せず既存音声をreuse。兄Voice=Algieba(A2/B1統一)。
- 到達上限Status: Memory B1=`VALIDATED候補 / USER_LISTENING_PENDING`。Memory A2 Trial-11=`VALIDATED`(Trial成果物、ユーザー試聴OK済み)としてSSOT記録。**新仕様(segmentation/Comment)はProduction未採用のまま**。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ変更しない、Production wiringを先回りしない。
- **旧成果物保存**: Trial-10 `er013_output/family_c_episode_trial_10/memory_b1/`と`er013_family_c_episode_trial_10_memory_b1_run.py`は無編集(git statusで空を確認)。新出力先`er013_output/family_c_episode_trial_12/memory_b1/`、新スクリプト`er013_family_c_episode_trial_12_memory_b1_run.py`(trial_10 memory B1版の複製)。Memory A2 Trial-11(`family_c_episode_trial_11/memory_a2/`、`er013_family_c_episode_trial_11_memory_run.py`)も無変更(import参照のみ可)。
- **本文固定**: B1本文はTrial-10で独立生成済みの`er013_output/family_c_episode_trial_10/memory_b1/reader_facing_article_b1.txt`を正本候補として固定(sha256を記録)。Writer再実行禁止、Story本文変更禁止、音声化都合の本文再生成禁止。A2正本`family_c_future_trial_08/memory/reader_facing_article.txt`も不変。
- 禁止: Opus、Writer再実行、Story/Key Phrase/Preview再生成、B1 Comment内容・Prompt変更、新Voice探索・Voice比較Trial、A/B大量生成、Production-wide refactor、新Validator、hard cap Validator化、無関係なRepo監査、同一segmentの理由なき再生成(既存cascade 標準2+fallback1内のみ)、`er003_*`/`er012_*`/`er005_*`/`er006_*`編集、`CURRENT_SPEC.md`編集、`git add -A`/`stash`/`amend`、wavのcommit。
- 費用上限: ¥40(Story segment再TTS+現物ASRのみ。Support/KP/共通assetは再TTSしない)。超過見込みならSTOP。
- STOP条件(ユーザー指定): Story本文変更が必要/100語前後でも重大TTS欠落が繰り返す/大幅な追加コスト/新しいVoiceが必要/今回承認されていない新仕様が必要/Production Gate変更が必要。それ以外の軽微な問題(ASR表記揺れ・話者判定例外・player表示不一致等)は本episode内で最小個別修正して完成音声まで進める。軽微な表記差で無駄なretryを増やさない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(保存名: `docs/pm/delegation_log/FAMILY-C-SEGMENT-COMMENT-TRIAL-12_1_memory_b1.md`)

## ユーザー指示(原文)

ユーザー原文(2026-09-16)の本委任該当部分を引用:

---
目的: Memory A2 Trial-11について、ユーザーが試聴し、「問題なし」と評価した。Trial-11で改善した以下2点を、残りのFamily C対象へ展開して試聴可能な完成音声まで作る。TTS Story segmentation改善/A2 Comment生成Promptの理解ガイド型への改善。今回対象: Memory B1/Digital Twins A2/Digital Twins B1。Memory A2 Trial-11は変更しない。

1. Status / Gate: Memory A2 Trial-11: VALIDATEDと記録してよい。ただし、今回検証している新仕様全体については、まだProduction採用を確定しない。今回到達してよい上限: USER_LISTENING_PENDING / VALIDATED候補。重要: ユーザーは、これらでも問題なければ、今回の仕様(Segmentの区切り、Comment仕様)を正式仕様として織り込むと意思表示している。ただし、残り3episodeのユーザー試聴OKが条件。ユーザー試聴前にAPPROVED_FOR_PRODUCTIONやPRODUCTION_WIREDへ変更しない。

2. 既存成果物を保存: Trial-10のMemory B1/Twins A2/Twins B1は比較用としてそのまま保存。上書き禁止。新しいTrial出力先を使用する。既存Trial-08由来のStory本文は正本候補として固定し、Writer再実行禁止/Story本文変更禁止/音声化都合による本文再生成禁止を維持する。

3. Story segmentation仕様: 基本原則: できるだけ自然な連続発話としてまとめ、必要な理由がある場所だけTTSを分割する。分割理由: Voiceが変わる/A2 Comment挿入位置/scene / semantic boundary/TTS安定性上、長くなりすぎる場合。避けること: 段落ごとの機械的分割/数語だけのnarrator segment/1文だけの不要な独立TTS/同一Voiceが続いているのに細かく分割/引用符だけを理由に同一Voiceの台詞を独立TTS化/"No,"のような短い同一Voice台詞を単独生成すること。同一Voiceで前後が自然につながる場合は、前後と一緒に生成する。

4. Segment長のTrial安全ガイド: 概ね100語以内を基本目安とする。120語を大きく超えない/150〜200語級にはしない/hard cap Validatorにはしない。word countだけで機械的に切らず、Voice連続性/自然な意味単位/scene/dialogue/Comment位置/TTS安定性を合わせて判断する。

5. Memory B1: Memory B1では、Trial-10の細かいdialogue分割をそのまま流用しない。特に同一narrator/Aoede内で、台詞/she said/前後の地の文が短く分断されている箇所を重点的に再構成する。ただし異なるVoice間は分離する。Brother Voice: Memory A2 Trial-11で採用した、Brother = AlgiebaをMemory B1にも使用する。対象: Do not make my last day your whole life, 兄のVoiceはA2/B1で統一。新たなVoice比較Trialは不要。B1 Comment: B1英語Commentについてはユーザーから品質問題の指摘がないため、内容・Promptとも変更しない。必要なら既存音声assetをreuseする。

9. 音声化: 試聴可能な状態まで完成させる。必要工程: 新segmentation/必要Story segmentのTTS/Memory B1 Brother Voice変更/Assembly/Audio Validation/player生成。既存正常assetは最大限reuse。

10. Token / Cost Guard: 最小作業。禁止: Opus/Writer再実行/Story再生成/Key Phrase再生成/不要なPreview再生成/新Voice探索/A/B大量生成/Production-wide refactor/新Validator開発/無関係なRepo監査。同じsegmentを理由なく何度も再生成しない。重大なTTS mismatch以外の軽微な表記差で無駄なretryを増やさない。

11. 完了報告: episodeごとに: Segmentation(旧segment数→新segment数/旧最短・最長word count/新最短・最長word count/短segment統合の代表例/残した短segmentとその理由/最長segmentが安全ガイド内か)、Comment(Memory B1はComment変更なしと明記)、Voice(Memory B1: Brother = Algieba)、Audio(duration/Audio Validation/player URL/direct audio URL/追加費用)。

12. 3episode完成時点ではSTOPして、USER_LISTENING_PENDINGとして報告する。今回のTrial生成タスク内では先回りしてProduction wiringしない。

STOP条件: Story本文変更が必要/100語前後でも重大TTS欠落が繰り返す/大幅な追加コストが必要/新しいVoiceが必要/今回承認されていない新仕様が必要/Production Gate変更が必要。それ以外の軽微な問題は、対象episode内で最小個別修正して試聴可能音声まで完成させる。
---

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET.md`(Trial-11): 8-27行(Trial-11 segmentation設計表・統合方針・安全ガイド適用の実例)、38-40行(Algieba選定・`tts_brother`実装)
- `er013_family_c_episode_trial_11_memory_run.py`: Grepで`segmentation_plan|def build_story_segments|def plan_segments|merge|lead_in|trailing|MAX_WORDS|TARGET_WORDS|--plan-only`→Trial-11の新segmentationロジック範囲Read(B1へ移植する対象)、Grepで`BROTHER_VOICE_NAME|def tts_brother|Algieba`→兄Voice実装範囲
- `er013_family_c_episode_trial_10_memory_b1_run.py`: 1-120行(定数・import)、Grepで`def build_all_story_segments_b1|def classify_quote_voice|def split_paragraph|story_%03d|kind`→旧B1 segment構築ロジック範囲、Grepで`reader_facing_article_b1|REUSED existing`→本文reuse機構、Grepで`comment_placement|snap|merge境界|C2|C3`→B1 Comment位置ロジック(累積語数37.1%/65.1%→直近境界スナップ)、Grepで`\.ok|reuse|copy|topic_intro_en`→resumable/reuse機構、Grepで`tts_support_charon|tts_device|tts_brother|a2m\.`→TTS関数と依存import
- `er013_family_c_episode_trial_10_twins_b1_run.py`: Grepで`def classify_quote_voice`→関数全体Read(OPEN-156の引用符境界修正版。同種バグがmemory B1にも内在するため、本Trial-12 B1スクリプトへ同じ修正を移植する[個別修正、汎用化しない])
- `er013_output/family_c_episode_trial_10/memory_b1/segments.json`: 全文(旧36 story segmentのid/voice/raw_text。旧最短/最長word count算出、統合対象の特定)
- `er013_output/family_c_episode_trial_10/memory_b1/reader_facing_article_b1.txt`: 全文(B1正本候補)
- `docs/pm/PM_GOVERNANCE.md`: Grepで`15-8`→該当節
- `docs/pm/PM_BRIEF.md`: 135-159行

## 事前指定Grep一覧+追記位置・更新位置の手順

1. 旧segment統計: `segments.json`から旧story segment数(前回報告36件)・最短/最長word count・同一Voice(narrator)連続で細切れになっている箇所(台詞/"she said"/前後地の文の分断)を列挙。
2. 新segmentation設計: Trial-11ロジックを移植し、Voice変化点(装置2・兄1、`segments.json`の`voice`で確認)・B1 Comment挿入位置(Trial-10と同じ累積語数37.1%/65.1%近傍の意味的境界を維持。新segment境界にスナップし直し、位置がずれる場合は理由付きで報告)・scene boundaryのみで区切り、narrator連続部分は概ね100語以内・120語を大きく超えない範囲で統合。"No,"型の短い同一Voice台詞・"she said"・lead-in/trailingは前後と結合。設計表を`er013_output/family_c_episode_trial_12/memory_b1/segmentation_plan.json`へ保存し、`--plan-only`ドライランで語数分布(最短/最長/各segment、150語以上0件、120語超原則0件、装置・兄以外の10語未満独立segment 0件)を確認してから本実行。
3. 兄Voice: `BROTHER_VOICE_NAME="Algieba"`、Trial-11の`tts_brother`と同一関数経路(`bvoices.generate_voice_body_wide_margin`)。`speaker_map.json`・`tts_generation_results.json`にAlgiebaが記録されることを確認。
4. 既存asset reuse: Trial-10 `memory_b1/`から`audio/`配下の非Story wav(topic_intro_en/preview_en/comment_1〜3[Charon]/kp英語5件・日本語5件/Notification等)・`key_phrases/`・`preview*.txt`・`comments_en.md`・`reader_facing_article_b1.txt`を新OUT_DIRへコピー(`.ok`含め再TTSされない状態)。再TTS対象=新Story segment全件のみ。
5. 話者判定: Trial-12 B1スクリプトの`classify_quote_voice`にtwins B1(OPEN-156)と同じ「before windowを直近の閉じ引用符より後ろに限定」修正を移植。ドライランで旧Trial-10と同じVoice割当(装置2/兄1、他narrator)になることを確認(差が出た場合は該当箇所と判断理由を報告)。
6. SSOT追記位置: `Grep pattern="^## FAMILY-C-MEMORY-A2-SEGMENT-COMMENT-TRIAL-11" path=DECISION_LOG.md`→そのエントリ末尾に「2026-09-16 ユーザー試聴OK→VALIDATED(Trial成果物、新仕様はProduction未採用)」を1行追記。その直後に新エントリ`## FAMILY-C-SEGMENT-COMMENT-TRIAL-12(委任1: Memory B1)`を追加(索引1行も)。`OPEN_ITEMS.md`はpythonでOPEN-147行末追記。
7. `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: LLM未使用なら追記不要(TTSのみ)。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FAMILY-C-SEGMENT-COMMENT-TRIAL-12_1_memory_b1.md --json-out docs\pm\delegation_log\FAMILY-C-SEGMENT-COMMENT-TRIAL-12_1_memory_b1_check.json
```

本文sha256記録:
```
.venv\Scripts\python.exe -c "import hashlib;print(hashlib.sha256(open('er013_output/family_c_episode_trial_10/memory_b1/reader_facing_article_b1.txt','rb').read()).hexdigest())"
```

ドライラン:
```
.venv\Scripts\python.exe er013_family_c_episode_trial_12_memory_b1_run.py --plan-only
```

本実行(上限¥40):
```
.venv\Scripts\python.exe er013_family_c_episode_trial_12_memory_b1_run.py --budget-jpy 40
```
(複製元argparseに合わせ実引数を確定し全文報告。工程: asset copy→新Story segment TTS[narrator=Aoede/装置=Charon/兄=Algieba]→現物ASR→Comment位置スナップ→Assembly[英語タイトルのみ、日本語タイトルなし、Comment 4なし、Support=既存Charon音声reuse]→Audio Validation→player→web_delivery.json。)

回帰: `er013_family_c_episode_trial_10_memory_test_01.py`のB1側テストを複製して`er013_family_c_episode_trial_12_memory_b1_test_01.py`(本文sha一致・日本語タイトル不在・Comment英語・Support voice=Charon・兄voice=Algieba・150語以上segmentなし、6件程度)を作成し:
```
.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_12*_test_*.py"
```
Trial-10/11成果物無変更確認: `git status --porcelain er013_output/family_c_episode_trial_10/ er013_output/family_c_episode_trial_11/`が空。

Web到達確認(push後、raw.githackはUser-Agent付きGET、CDN遅延時60秒待ち最大3回):
```
.venv\Scripts\python.exe -c "import urllib.request as u;[print(u.urlopen(u.Request(x,headers={'User-Agent':'Mozilla/5.0'})).status,x) for x in ['https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_12/memory_b1/player.html']]"
```
episode mp3 direct URL(`web_delivery.json`の実ファイル名)も同様にGET確認、計2件のstatusを報告。

## SSOT追記文

`DECISION_LOG.md`(Trial-11エントリ末尾に1行追記後、新エントリ):
```
## FAMILY-C-SEGMENT-COMMENT-TRIAL-12(委任1: Memory B1)

- 日付: 2026-09-16
- 種別: Trial-11(Memory A2、ユーザー試聴OK→VALIDATED)のStory segmentation方式をMemory B1へ展開する仕様Trial。新仕様はProduction未採用(残り3episodeのユーザー試聴OK後に正式採用対象A[segmentation]/B[A2 Comment]をAPPROVED_FOR_PRODUCTION扱いとし、別途Production wiringを行う。本Trialでは先回りしない)。
- 本文: Trial-10 B1本文固定(sha256 <値>)、Writer再実行なし。旧Trial-10成果物は無変更で保存、新版は`family_c_episode_trial_12/memory_b1/`。
- Segmentation: 旧<n> segment(最短<n>語/最長<n>語)→新<n> segment(最短<n>語/最長<n>語)。統合代表例<要約>。残した短segment<装置2/兄1等と理由>。最長segment<n>語=安全ガイド内。話者判定はOPEN-156修正を移植(個別修正)。
- Voice: 兄=Algieba(A2 Trial-11と統一)。装置=Charon、narrator=Aoede。B1 Support(Preview/Comment 1〜3)=Trial-10既存Charon音声reuse、内容・Prompt変更なし。
- Audio: Audio Validation <PASS/FAIL>、duration <秒>(旧343.248秒)。再生成回数<n>。費用¥<実測>(TTS/ASR)。Family C累計¥601.20+¥<実測>=¥<合計>。
- Status: Memory B1=VALIDATED候補/USER_LISTENING_PENDING。
- 参照: `docs/pm/RESULT_PACKET_T12_MEMORY_B1.md`、commit <hash>
```
索引1行。`OPEN_ITEMS.md` OPEN-147行末: ` 2026-09-16追記(TRIAL-12 委任1): Memory A2 Trial-11=ユーザー試聴OK→VALIDATED。Memory B1へsegmentation展開(旧<n>→新<n>、最長<n>語、兄=Algieba)、Audio Validation <結果>、費用¥<実測>、Family C累計¥<合計>。Status=USER_LISTENING_PENDING。新仕様のProduction採用は残り3episode試聴後。`
`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ形式で上書き(報告単位Status: Trial-12 Memory B1=<状態>、Twins A2/B1=未着手[委任2]、Discovery=UDR継続)。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add対象(wav除外、mp3必須): `er013_family_c_episode_trial_12_memory_b1_run.py`、`er013_family_c_episode_trial_12_memory_b1_test_01.py`、`er013_output/family_c_episode_trial_12/memory_b1/`配下(player.html、web/**/*.mp3、segments.json、segmentation_plan.json、speaker_map.json、comment_placement.json、audit/*.json、各consistency/validation/cost json、web_delivery.json、コピーしたテキスト系)、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/delegation_log/FAMILY-C-SEGMENT-COMMENT-TRIAL-12_1_memory_b1.md`、同`_check.json`、`docs/pm/RESULT_PACKET_T12_MEMORY_B1.md`。
- `family_c_episode_trial_10/`・`trial_11/`配下、`er006_output/`・`er011_output/`の既存M、`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??は触らない。
- コミットメッセージ: `FAMILY-C-SEGMENT-COMMENT-TRIAL-12 (1): Memory B1へsegmentation展開+兄Voice Algieba(旧版保存)+Memory A2 Trial-11 VALIDATED記録`
- trailer: `Task-ID: FAMILY-C-SEGMENT-COMMENT-TRIAL-12`
- push: `git push origin main`。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_T12_MEMORY_B1.md`に:
1. T-0結果、B1本文sha256、Trial-10/11無変更確認
2. Segmentation: 旧segment数→新segment数、旧最短/最長word count、新最短/最長word count、設計表(id/voice/段落範囲/語数/分割理由)、短segment統合の代表例(旧id→新id)、残した短segmentと理由、最長segmentが安全ガイド内か、Comment位置の新境界スナップ結果(旧位置との差)
3. Comment: 「Memory B1はComment変更なし(Trial-10 Charon音声reuse)」と明記
4. Voice: 兄=Algieba(runtime evidence: speaker_map/tts_generation_results/TTS関数名)、話者判定OPEN-156修正移植の結果(割当差の有無)
5. Audio: TTS segment数と失敗/retry内訳、ASR 4者一致(表記揺れ列挙)、Audio Validation、duration(旧343.248秒との差)、player URL、direct audio URL、Web到達確認、追加費用(TTS/ASR/その他)
6. PM: Status=USER_LISTENING_PENDING、Production採用なし、STOP該当有無、恒久課題候補の追加有無
7. 回帰結果、commit hash・push結果・残差分要約
8. 事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(「B1B」不使用)。
