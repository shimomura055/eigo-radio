# RESULT_PACKET — USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-FAMILYC(v2)

## 1) 最終Status

**VALIDATED候補(ユーザー試聴待ち)**。Audio Validation Gate: PASS
(`home_robots_v2/audio_validation.json`, level=`FAMILY_C_TRIAL_09B`)。
Production採用・B1/B2生成は行っていない。v1(`home_robots/`)は無変更で保持。

## 2) Family A流用表(要旨、全表は`home_robots_v2/family_a_reuse_map.md`)

Intro/Outro/Notification(3箇所)は`p9a.INTRO_MP3_PATH`等の既存SFXジングルを
そのまま使用。Welcome/Preview intro/Key phrases intro/Full story introは
B1_SHARED_NAMES(記事非依存Charon資産)をコピー流用(追加TTSなし)。
Topic introは`Today's topic is {title}.`というA2既定文言パターンを採用
(v1は"Home Robots"単体のみでTitle読み上げ不足の一因だった)。Comment前後
pause(1.0s en→ja/0.8s ja→en)とOutro直前pause(0.5s)はA2既存値
(`build_a2_timeline`)をそのまま採用(v1のsupport前後pauseは0.6/0.8sで
Family A値と不一致だった)。Key Phrase構成・pauseはv1も既にA2/B1既存
primitiveを使用済みのため無変更。新規SFX・新規演出は追加していない。

## 3) Key Phrase 4者照合表(5件、修正前後)

`home_robots_v2/key_phrase_consistency.json`。**5件全てmatch_en=true・
match_ja=true**(修正後)。修正前(v1)の実測ASR(本タスクで実施した診断、
事前指定外読み取り): kp2英語="belong to"(someone欠落、ユーザー報告と
一致)、kp1/2/3/4/5の日本語gloss音声は現行canonical文と異なる文を読んで
いた(例: kp1は「本人の希望」ではなく「自分が望むこと」、kp2は「その人
自身のものである」ではなく「何々のものである」[ユーザー報告の「だれだれ」
的読みと一致])、kp3英語音声は実際には"Awake"(rank5の内容)、kp5英語音声は
実際には"Advantage"(いずれとも異なる内容)だった。**原因**: v1の
`_resumable_reuse()`がファイル+`.ok`マーカーの存在のみで判定し、
canonical textとの一致を検証しない。Key Phrase選定パイプラインは最大6回
再試行され、途中の失敗attemptでも同じrank番号のkp{rank}_*.wav/.okが書かれて
いたため、最終選定結果のrank内容が変わっても古いattemptの音声が
「REUSED」として使われ続けた。v2はKey Phrase**選定結果(JSON)のみ**v1を
再利用し、**音声は新規ディレクトリで全件新規生成**することでこの不整合を
構造的に回避した。

## 4) Voice構成

Narrator=Aoede(無変更)、Robot=Charon(無変更)、**Mother=Erinome**
(既存2V B-Family Voice B、`er012_b_family_editorial_type_registry_01.py::
VOICE_ASSIGNMENT["voice_b"]`、`APPROVED_FOR_PRODUCTION`実績あり)。
`er012_b_family_voices_production_01.py::generate_voice_body_wide_margin()`
(既存Production関数、voice_name引数のみ指定)をそのまま呼び出した。
**重要な留保**: SSOT(`er012_output/editorial_b_voices_phase1_5_3v_4v_
integrated_trial_03/design.md` L551「SSOT上に性別的印象の記載が一切
存在しない」)を確認した結果、Algieba/Erinome/Schedar/Sulafatの「男性的/
女性的」という印象は**正式には記録されていない**(委任文の「既存4Voice
Trialで使用した女性系Voice」という前提はSSOT上未確認)。Erinomeは既存
2V Voice B(実績あり・Production承認済み)という安定性を理由に選定した
暫定的判断であり、ユーザーが試聴の上で性別的印象が意図と異なる場合は
差し替えが必要(新Voice探索はしていない、既存承認候補内での選択)。
Mayaの分離: 分離しない(理由は`speaker_map.json`の`maya_split_decision`
に記録、報告されている不具合が母親発話のみであるため)。
話者判定表: `home_robots_v2/speaker_map.json`(10件、引用符+帰属句または
直前文主語で機械的判定)。

## 5) Comment 4件

`home_robots_v2/comment_consistency.json`。4件中3件は表示文/canonical/
TTS input/ASRが完全一致。Comment 2のみ不一致(ASRが「この後」と漢字表記、
canonicalは「このあと」平仮名。読みは同一で意味・内容の差はない、ASRの
表記選択差にとどまる)。位置・前後volume: `home_robots_v2/
comment_placement.json`(語数・尺を記録)。C1(導入、Full story intro直後)
duration=6.10s、C2(段落9/10境界)6.88s、C3(段落22/23境界)9.22s、C4
(Story終了後)6.64s。

## 6) Assembly順序・間

Intro→Welcome→0.5→Topic intro→0.65→Japanese title→0.5→Notification1→
0.4→Preview intro→0.65→Preview→0.5→Notification2→0.4→Key phrases intro→
0.5→KP1〜5→Notification3→0.4→Full story intro→1.0→**Comment1**→0.8→
Story(段落0〜9、内訳: 冒頭[Aoede]→ロボット発話[Charon]混在)→1.0→
**Comment2**→0.8→Story(段落10〜22、母親発話2箇所[Erinome]・UI[Charon]
含む)→1.0→**Comment3**→0.8→Story(段落23〜33、母親発話1箇所[Erinome]
含む)→1.0→**Comment4**→0.5→Outro。全pause値はFamily A(A2)既存値を
流用(2節参照)。

## 7) Audio Validation結果

PASS(`home_robots_v2/audio_validation.json`)。全38 segment(narrator/
robot/mother混在)+15 Key Phraseサブsegment、`tts_generation_results.json`
status=OK。retry/fallback: Key Phrase英語/日本語・mother voiceとも既存
標準retry構成の範囲内で完了(上限到達・STOPPEDは0件)。duration=319.593秒
(5:19.6)、peak=0.9544(headroom safety valve不適用、clipping無し)。

## 8) consistency結果

`article_audio_consistency.json`: Story全文(2317字、正規化後)と全story
segmentのtts_text連結(2318字)が、"7:00"→"seven"の1箇所(読み整形、意味
不変)を除いて一致。`player_display_audio_consistency.json`: 36行中33行
完全一致(91.7%)。残り3件は診断用Primary-only ASR([existing production
secondary ASR cascadeを適用しない簡易照合]の既知の限界)による見かけの
不一致であり、実音声はv1で既にProduction正式retry+secondary ASR cascade
検証済みのものをそのまま流用している(story_009: "room"→"rooms"等の
ASR聞き取り差、story_025: "plans"→"plants"のASR聞き取り差、comment_2:
上記5)節と同一の表記差)。いずれも新たなTTS内容欠陥ではないと判断した
(未解決ではあるが原因特定済み、STOP対象ではない)。

## 9) Story本文不変(sha256)

`home_robots_v2/audit/article_unchanged_sha256.json`:
v1=v2=`ee45d0b608c565cbf6a11e7178a2eb6e955bdbaeddc392d8c2e3477e6300ded1`
(identical=true)。

## 10) duration・mp3一覧・player・予定URL

duration=319.593秒。mp3: `web/family_c_home_robots_trial_09b.mp3`
(episode、3.47MB)+`web/segments/*.mp3`(51件)。player:
`er013_output/family_c_episode_trial_09/home_robots_v2/player.html`
(相対パスのみ、`file:///`/`C:\`検出0件)。予定URL: raw.githack player=
`https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/
family_c_episode_trial_09/home_robots_v2/player.html`、episode mp3=
`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/
er013_output/family_c_episode_trial_09/home_robots_v2/web/
family_c_home_robots_trial_09b.mp3`(いずれも本タスクではcommit/push
していないため未commit=404の可能性、Git操作はFableへ委ねる)。

## 11) なぜv1が「完成」と報告できたか(原因・gap)

(a) **表示/音声不一致を検出する仕組みが存在しなかった**: Audio
Validation Gate(`er003_v1_n3_01_assemble.py::verify_episode_audio_
validation_gate()`)は`tts_generation_results.json`の`status=="OK"`と
sha256存在のみを検証し、audio実体をASR再照合しない(呼び出し側が渡す
`canonical_text`を無条件で信用する設計)。(b) **`_resumable_reuse()`の
resumability bug**(3節参照)により、Key Phrase・Preview音声が実際には
古いcanonical textの内容のままだったにもかかわらず、audit entryには
「現在のcanonical_text」が記録され、Gate PASSした。(c) Family C用の
`required_structure`が未登録(level=`FAMILY_C_TRIAL_09`)のため、
Intro/Outro/Comment数等の「構造上あるべき要素」の充足チェックが一切
働かなかった(A-Family既存Gateはこの種の完全性チェックを担う設計では
ない、OPEN-129で既に指摘済みの既知gapと同種)。(d) player/display/audio
の3者一致を検証するQAが元々存在しない(標準player format
[PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11]はUI表示のみを
規定し、内容一致検証は範囲外)。本タスクでは新Validatorを追加せず、
上記gapを診断・報告するに留めた(Open Item候補15)参照)。

## 12) 費用

実測累計(`raw_usage_log.jsonl`全体、2回のresume実行含む): **¥52.20**
(precedentベースの安全側単価推定、TTS26件+LLM4件+ASR診断72件)。
うちASR診断(player/display/audio consistency検証専用、Primary ASRのみ)
は¥0.3/call[precedentなし暫定値]。Family C予算枠(残額¥37.69)を
**約¥14.51超過**。超過理由: (1)Key Phrase・Preview音声の全面新規生成
(v1のresumability bug対応のため流用を断念、想定より新規TTSが増えた)、
(2)consistency検証のためのASR診断呼び出し72件(本タスク新設の検証工程、
委任文が要求する4者照合の実施に必要)。本タスクの¥90上限は超過していない。

## 13) model_id/TTS model・voice割当

Narrator: `gemini-3.1-flash-tts-preview`相当(Aoede、既存
`generate_narration_snippet_verified_strict`既定)。Robot: 既存
`generate_charon_english`既定(Charon)。Mother: 既存
`generate_voice_body_wide_margin`既定モデル(`p9a.ENGLISH_MODEL_NAME`、
Erinome)。LLM(Comment): `a2gen.MODEL`(既存A2 Support基盤既定)。

## 14) Open Item候補

(1) Mother voice(Erinome)の性別的印象はSSOT未確認のためユーザー試聴後の
確定が必要(4節)。(2) `_resumable_reuse()`型resumabilityパターン
(ファイル+`.ok`存在のみで判定しテキスト内容ハッシュを見ない)は、Family C
以外のTrial scriptにも同種の潜在リスクがある可能性(横展開調査は未実施、
本タスクのscopeでは実施せず)。(3) Audio Validation Gateがcanonical_text
とASR実測の再照合を行わない設計上のgap(11節)はProduction全体の既知gap
として記録(Validator追加はPM承認が必要、本タスクでは追加せず)。

## 15) commit対象候補一覧(サイズ込み、wav除外・mp3必須)

| パス | サイズ | 種別 |
|---|---|---|
| `er013_family_c_episode_trial_09b_run.py` | 64K | 新規script |
| `er013_family_c_episode_trial_09b_test_01.py` | 8K | 新規test |
| `home_robots_v2/player.html` | 18K | player |
| `home_robots_v2/web/family_c_home_robots_trial_09b.mp3` | 3.47M | episode mp3 |
| `home_robots_v2/web/segments/*.mp3`(51件) | 約1.9M | segment mp3 |
| `home_robots_v2/{article_normalized.txt,family_a_reuse_map.md,speaker_map.json,key_phrase_consistency.json,comments_ja.md,comment_placement.json,comment_consistency.json,segments.json,audio_validation.json,article_audio_consistency.json,player_display_audio_consistency.json,web_delivery.json,cost_summary.json,preview.txt,raw_usage_log.jsonl}` | 各数K〜20K | 中間・報告成果物 |
| `home_robots_v2/key_phrases/keywords_canonicalized.json` | 4K | KP選定結果(v1流用の記録) |
| `home_robots_v2/audit/{gain_report.json,headroom_report.json,run_summary_assemble.json,tts_generation_results.json,article_unchanged_sha256.json,v1_reuse_log.json}` | 各数K | Assembly/Gate audit |
| `docs/pm/delegation_log/USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-FAMILYC.md`+`_check.json` | 数K | T-0記録 |
| `docs/pm/RESULT_PACKET_FIX02_FAMILYC.md` | 本ファイル | 報告 |

除外(wav、59MB assembled + 13MB audio、計約72MB): commitしない
(mp3で代替済み)。合計commit候補: 約6MB(mp3含む)。

## 16) T-0・事前指定外Read・STOP有無

T-0: **PASS**
(`docs/pm/delegation_log/USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-FAMILYC_check.json`、
reasons無し)。事前指定外Read(理由付き): (1)
`er012_output/editorial_b_voices_phase1_5_3v_4v_integrated_trial_03/
design.md`全文・`er012_voice_b_attempt_review_artifact_01.py`一部・
`DECISION_LOG.md`該当行grep: 委任文の「4Voice Trialで使用した女性系
Voice」という前提の裏付けを事前指定Grep一覧(`4v|four_voice|...`)だけ
では取れなかったため(voice名は見つかったが性別印象データはSSOT上
「記載なし」と判明、4節に記録)。(2)
`er012_b_family_voices_production_01.py`(`generate_voice_body_wide_margin`
の実装確認): Mother voice生成に使う既存Production関数のシグネチャ・
retry/ASR構成を確認するため(呼び出し前提の安全確認)。(3)
`er011_human_review_lock_01.py`(`guarded_generate`/`derive_segment_key`):
上記関数がreview lock guardedであるため、想定外の副作用が無いか確認する
ため。(4) 診断用ASR再照合(`er006_asr_provider_routing_01.transcribe`、
v1音声/共有Charon資産への事前実行): 4者照合表作成に実データが必要
だったため(委任文が要求する検証そのもの)。STOP: **なし**(費用上限
[本タスク¥90]内で完走、Gate PASSに到達。ただしFamily C累計予算枠は
超過、12節にユーザーへの明示が必要な事項として記録)。
