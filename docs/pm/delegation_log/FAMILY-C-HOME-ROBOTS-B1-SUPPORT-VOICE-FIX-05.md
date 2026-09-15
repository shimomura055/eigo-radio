## 管理ID

`FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05`
並行タスクなし(本委任が唯一の実行中タスク)。`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`は本タスクで上書きしてよい。前タスク`FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04`(commit `584f6d67`まで)の続き。

## 性質/到達上限Status/禁止事項

- 性質: Family C B1 Trial記事のSupport voice修正(ユーザー正式判断: Preview/Comment 1〜3をAoede→Charonへ。B1正式仕様CURRENT_SPEC 642行「Navigator/Support(Charon): Preview、Comment 1〜4…」への整合)。
- 到達上限Status: Family C B1は`VALIDATED候補 / Trial / USER_LISTENING_PENDING`のまま。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ昇格しない。A2 v2はユーザーOK済みとして**一切触らない**。
- 対象外: A2 v2(`home_robots_v2/`配下・`er013_family_c_episode_trial_09b_run.py`)、Trend/Discovery/Voices/OPEN-154/155、`er012_*`/`er003_*`/`er011_*`Production経路、`CURRENT_SPEC.md`。
- 禁止: 4 segment(`preview_en`・`comment_1_ja`・`comment_2_ja`・`comment_3_ja`[実体は英語Comment 1〜3])以外の再TTS(特に`story_017`[Robot選択肢]・Story本文・Key Phrase・Intro/Outro/Notification/日本語gloss)、canonical text変更、Comment 4復活、日本語タイトル復活、pause値変更、Trialスクリプトの癖4件(非冪等再生成/ASR名前キャッシュ/引用符なしRobot話者判定/A2退避上書き)の恒久修正(ユーザー指示8で別タスク扱い。本タスクでは「今回の4 segmentに限定した最小限のbypass」のみ可)、`git add -A`/`stash`/`amend`、wavのcommit。
- 費用上限: ¥10(TTS 4件≒¥3.60+ASR 4件≒¥1.20+余裕)。全segment再ASR・全episode再TTSは禁止。超過見込みならSTOP。
- STOP条件: (1)費用上限超過見込み、(2)4 segment以外のwav sha256が変化した(意図せぬ再TTS)、(3)ASR不一致(disfluency/欠落/追加語)、(4)Audio Validation Gate FAIL 2回連続、(5)Voice evidence上にAoedeが残る原因が既存スクリプト構造にありbypassで解決できない、(6)Trialスクリプトの癖4件が本作業の正当性に影響した場合(ユーザー指示8)。STOP時はcommitせず状態をRESULT_PACKETへ記録して停止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

以下ユーザー原文(2026-09-15)を要約せず引用:

---
目的: Family C / Home robots のB1について、ユーザー試聴で判明した Preview / Comment 1〜3 のVoice不整合を修正する。今回はFamily C B1のみ対象。A2はユーザー試聴でOK済みなので触らない。Trend / Discovery / Voices / OPEN-154 / OPEN-155には触れない。

1. ユーザー判断: B1の、Preview/Comment 1/Comment 2/Comment 3は、既存B1正式仕様どおり Charon voice にする。現在のAoede使用は不採用。Family CではRobotもCharonだが、今回はそれを理由にB1 Support voiceを別Voiceへ変えない。つまり今回のB1では、Preview = Charon/Comment 1 = Charon/Comment 2 = Charon/Comment 3 = Charon/Robot = Charon でよい。これはユーザー正式判断。

2. 修正対象: 以下4segmentのみ再TTSすること。Preview/Comment 1/Comment 2/Comment 3。canonical textは変更しない。現在の英語文言をそのまま使う。他segmentは原則再生成しない。

3. 必須確認: 各segmentについて、canonical text/TTS input/actual voice = Charon/ASR transcript/player表示 を照合。すべて一致確認すること。特にVoice metadata / evidence上で Aoedeが残っていないことを確認。

4. Assembly: B1 episodeを再Assembly。既存の以下は変更しない。英語タイトルのみ/日本語タイトルなし/Comment 4なし/Robot二人称文/Mother voice/Story本文/Key Phrase/Intro / Outro / SFX / pause/Preview / Comment本文内容。Voice変更のみ。

5. Audio Validation: 再Assembly後、Audio Validation/segment consistency/player script/audio consistency/web player到達確認 を実施。既存ASR cacheをそのまま信用せず、今回再生成した4segmentについては実音声に対して再ASRすること。過去にsegment名だけでcache hitして検証漏れが起きているため、今回の4segmentは必ず現物音声を検証する。

6. 費用最小化: 今回の対象は4segmentのみ。不要な全segment再ASR / 全episode再TTSをしない。追加費用を最小化すること。実費を、TTS/ASR/その他 に分けて報告。

7. Status: Family C B1は修正後も、VALIDATED候補 / Trial / USER_LISTENING_PENDING。Production採用ではない。ユーザー試聴OK後にTrial成果物としてVALIDATED確定可否を判断する。A2は今回触らず、既にユーザーOK済みとして維持。

8. 未解決技術課題: 今回の作業では以下を修正しない。Trial scriptの非冪等再生成/ASR cacheがsegment名だけを見る問題/引用符なしRobot発話の汎用話者判定/A2退避ファイル無条件上書き。ただし今回の検証で影響が出た場合はSTOPして報告。これらは別タスクで扱う。

9. 最終報告: 最低限以下を報告。Preview / Comment 1〜3 の修正前Voice / 修正後Voice/canonical text不変確認/Charonであるruntime evidence/ASR結果/Audio Validation/duration/追加費用/player URL/direct audio URL/unresolved issue/final status。最後にユーザーが再試聴すべきURLは、Family C B1の1本だけ再掲すること。
---

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET.md`: 72-137行(修正1回目: `--preview-en`実装・非冪等性の説明)、151-211行(修正2回目: ASRキャッシュの実装事実616-641行/1189-1247行、4 wav sha256)
- `er013_family_c_episode_trial_09b_b1_run.py`: Grepで`generate_charon_english|generate_a2_japanese|narrator|Aoede|"voice"|voice=`を位置特定→Preview/Comment 1〜3のTTS呼び出し箇所(voice決定ロジック)とRobot(`story_017`)のTTS呼び出し箇所を範囲Read。Grepで`--comments-en|--preview-en|--fix-robot-choice-second-person|--reassemble|\.ok`を位置特定→各フラグの再TTS判定(wav+`.ok`削除)ロジック範囲Read。Grepで`_load_prior_seg_asr_cache|_load_prior_comment_asr_cache`→616-641行Read(既読の場合は再読不要)。Grepで`speaker_map|"voice":|voice_name|tts_voice`→audit/evidence(`tts_generation_results.json`・`speaker_map.json`・`player_display_audio_consistency.json`・`segments.json`)へvoice名を書き出す箇所を範囲Read。
- `er013_output/family_c_episode_trial_09/home_robots_b1/audit/tts_generation_results.json`: Grepで`preview_en|comment_1_ja|comment_2_ja|comment_3_ja|story_017`→各entry範囲Read(現在のvoice記録・sha256・pathを取得。修正前evidenceとして保存)
- `er013_output/family_c_episode_trial_09/home_robots_b1/player.html`: Grepで`Aoede|Charon|voice`(大小無視)→表示箇所Read
- `docs/pm/PM_GOVERNANCE.md`: Grepで`2-3`+`supersession`→該当節Read(旧artifact退避ルール)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. 修正前evidence採取: `Grep pattern="Aoede" path=er013_output/family_c_episode_trial_09/home_robots_b1/ glob=*.{json,html,md} output_mode=content`→ヒット全件をRESULT_PACKETに記録(修正前Voice=Aoedeの証跡。Story narrator segmentのAoedeは正しいので、4 segmentに関するヒットのみ「修正対象」と分類)。
2. 修正後確認: 同Grepを再実行→4 segment(`preview_en`・`comment_1_ja`・`comment_2_ja`・`comment_3_ja`)に関するAoedeヒットが0件、Charonが記録されていることを確認。Story narrator(Aoede)・Mother(Erinome)のヒットは正常として件数を報告。
3. 4 segment以外のsha256不変: 実行前に`audit/tts_generation_results.json`の全entryのsha256を`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\7464676f-2545-4919-a668-1fdd436c9816\scratchpad\fix05_pre_sha.json`へ保存し、実行後に比較(差分=4 segmentのみであること。`story_017`はsha256フィールドが無い実装のため、`audio/story_017.wav`のファイルsha256とmtimeを実行前後で直接比較)。
4. ASR現物検証: 実行前に`player_display_audio_consistency.json`・`comment_consistency.json`から当該4 segmentのasr_textキャッシュentryを除去(pythonで当該keyのみ`asr_text`をnullに、または該当rowを削除)し、スクリプトが必ず新規ASRを走らせる状態にする(名前キャッシュ設計そのものは変更しない=ユーザー指示8遵守)。実行後、`raw_usage_log.jsonl`に本実行時刻の`asr_diag`エントリが4 segment分(ちょうど4件、他segment分は0件)存在することを確認・報告。
5. `story_017`再TTS回避: `--fix-robot-choice-second-person`が無条件再TTSする場合、本実行ではそのフラグを付けずにvoice=robot・二人称tts_textが維持されるかを実行前にコード上で確認する。維持されない(フラグ無しだとnarrator/三人称へ戻る)場合は、当該フラグに「wavと`.ok`が存在しtts_textが固定文と一致するなら再TTSをスキップ」する本タスク限定の最小bypass(引数`--keep-robot-audio`)を追加してよい(恒久的な冪等化ではなく、本タスクのSTOP条件(2)を守るための限定措置。RESULT_PACKETに明記)。それでも回避不能ならSTOP条件(6)として報告。
6. SSOT追記位置: `Grep pattern="^## FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04" path=DECISION_LOG.md`→そのエントリ末尾直後(`## 参照元`の直前)に新エントリ追加、同エントリの索引行直後に索引1行追加。`OPEN_ITEMS.md`OPEN-147はpythonで行末追記(Readツール不可)。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05.md --json-out docs\pm\delegation_log\FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05_check.json
```

実装: `er013_family_c_episode_trial_09b_b1_run.py`へ`--support-voice-charon`フラグを追加。効果: Preview(`preview_en`)・Comment 1〜3のTTSをRobot選択肢と同じ`generate_charon_english`(既存関数、Robot `story_017`で使用中)経由に切り替え、当該4 wav+`.ok`のみ削除して再TTS→現物ASR→単一segment差し替えで再Assembly→Audio Validation→player再生成。voice evidence(`tts_generation_results.json`・`speaker_map.json`・`player_display_audio_consistency.json`・`segments.json`・player.html表示)のvoice記録をCharonへ更新。canonical text(`comments_en.md`・`preview.txt`)はバイト単位で不変。旧episode mp3/playerは`home_robots_b1/web/prev/family_c_home_robots_trial_09b_b1_support_aoede.mp3`・`home_robots_b1/player_prev_support_aoede.html`へ退避(既存の`_ja_support`・`_preview_ja`退避は上書きしない)。旧4 wavは`audio/prev/`へ`*_aoede.wav`として退避。
```
.venv\Scripts\python.exe er013_family_c_episode_trial_09b_b1_run.py --drop-japanese-title --support-voice-charon --reassemble
```
(`--comments-en`/`--preview-en`/`--fix-robot-choice-second-person`はテキスト再生成・再TTSを引き起こすため**付けない**方針。ただし付けないとComment英文/Preview英文/Robot二人称・robot voiceの状態が失われる実装なら、Grep 5と同様に「既存テキストを保持し再生成をスキップする」本タスク限定bypassを追加し、実際に使った引数全文と理由を報告。)

修正後検証(Aoede残存・voice記録):
```
.venv\Scripts\python.exe -c "import json;d=json.load(open('er013_output/family_c_episode_trial_09/home_robots_b1/audit/tts_generation_results.json',encoding='utf-8'));e=d.get('segments',d);[print(k,'voice=',v.get('voice',v.get('voice_name')),'sha=',str(v.get('sha256'))[:12]) for k,v in e.items() if k in ('preview_en','comment_1_ja','comment_2_ja','comment_3_ja','story_017')]"
```
(実構造に合わせキー名を修正可。修正後コマンド全文を報告。)

回帰(テスト1件追加: `test_support_segments_use_charon_voice`[4 segmentのvoice evidence=Charon]):
```
.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_09*_test_*.py"
```
全件PASS(前回69件+1=70件見込み)。A2 v2側のテストも回帰に含まれるが、A2 artifactは無変更であること(`git status --porcelain er013_output/family_c_episode_trial_09/home_robots_v2/`が空)を確認・報告。

Web到達確認(push後、raw.githackはUser-Agent付きGET):
```
.venv\Scripts\python.exe -c "import urllib.request as u;[print(u.urlopen(u.Request(x,headers={'User-Agent':'Mozilla/5.0'})).status,x) for x in ['https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/player.html','https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/web/family_c_home_robots_trial_09b_b1.mp3']]"
```
CDN遅延時は60秒待って最大3回再試行。

## SSOT追記文

`DECISION_LOG.md`(新エントリ、`## FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04`エントリ末尾直後):
```
## FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05

- 日付: 2026-09-15
- 種別: Trial記事修正(ユーザー正式判断の反映)、Status不変(Family C B1=VALIDATED候補/Trial/USER_LISTENING_PENDING、Production未採用。A2 v2はユーザー試聴OK済み・無変更)
- ユーザー正式判断: Family C B1のPreview/Comment 1〜3は既存B1正式仕様(CURRENT_SPEC「B1 Voice」節: Navigator/Support=Charon)どおりCharon voiceとする。Aoede使用は不採用。Family CでRobotもCharonであることを理由にSupport voiceを別voiceへ変えない(Preview/Comment 1〜3/Robot=すべてCharon)。
- 実施: 4 segment(preview_en/comment_1_ja/comment_2_ja/comment_3_ja[英語Comment 1〜3])のみCharonで再TTS。canonical text不変(comments_en.md/preview.txt バイト一致)。他segment wav sha256不変(<比較件数>件、差分0)。4 segmentは現物音声でASR実測(4/4 match=true)。Voice evidence上の4 segment Aoede残存0件。
- Audio Validation: B1 <PASS/FAIL>、duration <秒>(前回393.375秒)
- 費用: TTS¥<x>/ASR¥<y>/その他¥<z>=合計¥<実測>。Family C累計¥285.00+¥<実測>=¥<合計>。
- 回帰: `run_project_regression.py --pattern "er013_family_c_episode_trial_09*_test_*.py"` collected=<n> passed=<n> failed=0
- 未修正(別タスク、ユーザー指示8): Trial scriptの非冪等再生成/ASR cache名前キー/引用符なしRobot話者判定/A2退避上書き。本タスクでの影響: <なし/あり詳細>。
- 参照: `docs/pm/RESULT_PACKET.md`、`FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05_REPORT.md`、commit <hash>
```
索引1行(FIX-04索引行の直後、既存形式)。

`OPEN_ITEMS.md` OPEN-147行末追記:
```
 2026-09-15追記(FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05): ユーザー正式判断によりB1 Preview/Comment 1〜3をCharon voiceへ変更(B1正式仕様整合、Robot=Charonと同一voiceで可)。canonical不変、4 segmentのみ再TTS+現物ASR 4/4一致。B1はVALIDATED候補/Trial/USER_LISTENING_PENDINGのまま、A2 v2はユーザーOK済み。実費¥<実測>、Family C累計¥<合計>。Trial script課題4件は別タスク。
```

`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ形式で上書き(`docs/pm/PM_BRIEF.md`135-159行。UDR-deferred: Discovery Part C/Discovery B1人間承認/OPEN-154/OPEN-155/Family C B1再試聴を引継ぎ。報告単位Status: Family C A2 v2=ユーザー試聴OK[Trial]、Family C B1=USER_LISTENING_PENDING)。

`docs/pm/RESULT_PACKET.md`: 本タスク内容で上書き。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add対象(wav除外、mp3必須): `er013_family_c_episode_trial_09b_b1_run.py`、`er013_family_c_episode_trial_09b_b1_test_01.py`、`er013_output/family_c_episode_trial_09/home_robots_b1/`配下の更新・新規(player.html、player_prev_support_aoede.html、web/family_c_home_robots_trial_09b_b1.mp3、web/prev/*_support_aoede.mp3、web/segments/対象4 mp3、segments.json、speaker_map.json、audit/*.json、comment_consistency.json、player_display_audio_consistency.json、audio_validation.json、cost_summary.json、raw_usage_log.jsonl[Git追跡済みなら])、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`(voice変更のみでLLM未使用なら追記不要)、`docs/pm/delegation_log/FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05.md`、同`_check.json`、`FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05_REPORT.md`(root直下、新規)。
- `home_robots_v2/`配下・`er006_output/`・`er011_output/`の既存M・`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??は触らない。
- コミットメッセージ: `FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05: B1 Preview/Comment 1〜3をCharon voiceへ(ユーザー正式判断・B1仕様整合、4segmentのみ再TTS+現物ASR)`
- trailer: `Task-ID: FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05`
- push: `git push origin main`。

## 報告(RESULT_PACKET項目)

1. T-0結果
2. 修正前Voice/修正後Voice(4 segment各: 修正前evidence[ファイル:行、voice名]→修正後evidence[同])、Grep 1/2の結果(4 segment関連のAoedeヒット: 修正前n件→修正後0件、正常なAoede/Erinomeヒット件数)
3. canonical text不変確認(`comments_en.md`・`preview.txt`のsha256前後、`segments.json`/`tts_generation_results.json`のcanonical_text前後一致)
4. Charonであるruntime evidence(`tts_generation_results.json`のvoice記録、TTS呼び出し関数名、`raw_usage_log.jsonl`のtts記録4件[時刻・segment・voice])
5. 4 segment以外のsha256不変(比較件数・差分0件、`story_017`wavのsha256/mtime前後一致)、`story_017`再TTS回避のために使ったbypassの有無と内容
6. ASR結果(4 segment各canonical/ASR全文/match、`raw_usage_log.jsonl`の`asr_diag`が本実行分ちょうど4件で他segment0件)
7. Audio Validation(PASS/FAIL、duration、前回393.375秒との差)、segment consistency、player script/audio consistency結果
8. 回帰結果(collected/passed/failed、新規テスト名)、A2 v2 artifact無変更確認(`git status --porcelain`空)
9. 費用(TTS/ASR/その他の3区分、合計、Family C累計)
10. player URL・direct audio URL・Web到達確認(HTTP status 2件)
11. unresolved issue(ユーザー指示8の4件が本作業に影響したか、その他)
12. final status(Family C B1=`VALIDATED候補 / Trial / USER_LISTENING_PENDING`、Production未採用。A2 v2=ユーザーOK済み・無変更)
13. commit hash・push結果・push後残差分要約
14. 事前指定外Read(理由付き1行ずつ)
15. 最終REPORT(`FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05_REPORT.md`)にユーザー指示9の全項目を含め、末尾にFamily C B1 player URL 1本のみ再掲。

ユーザー向け表記は「B1」に統一(「B1B」不使用)。
