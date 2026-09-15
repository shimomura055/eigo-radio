# USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02 統合REPORT

管理ID: `USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02`(Sonnet分割委任4件:
FAMILYC/TREND/DISCOVERY/VOICES[+CONT1]) + `PM-CLOSEOUT-CONSOLIDATION-134`
(Git記録・Web到達確認・SSOT反映担当、本タスク、API呼び出し¥0)。

詳細ログ(実データ)の保存先: `docs/pm/RESULT_PACKET_FIX02_FAMILYC.md`、
`RESULT_PACKET_FIX02_TREND.md`、`RESULT_PACKET_FIX02_DISCOVERY.md`、
`RESULT_PACKET_FIX02_VOICES.md`/`_2.md`、
`docs/pm/web_playback_check_FIX02.json`。本REPORTはそれらの統合要約。

新Validatorは追加していない(全対象共通、ユーザー指示どおり)。

---

## 0. 今ユーザーが試聴すべきURL(5件)

- Family C v2(Home robots): https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_v2/player.html
- Trend A2: https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/trend/audio/a2/player.html
- Trend B1B: https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/trend/audio/b1b/player.html
- Discovery A2: https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/a2/player.html
- Voices v2(2V、一人称版): https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/voices/audio/b1_2v_v2/player.html

Discovery B1Bは音声未完成のため試聴URLなし(6節参照)。

---

## 1. Family C / Home robots v2

### 1.1 修正内容・修正前後

v1(`home_robots/`)は無変更のまま保持。v2(`home_robots_v2/`)を新規作成。

- **Key Phrase/Preview音声の不整合**: v1の原因は`_resumable_reuse()`が
  「ファイル+`.ok`マーカーの存在」のみで再利用可否を判定し、canonical
  textとの一致を検証しないバグ。Key Phrase選定は最大6回再試行され、
  途中の失敗attemptでも同じrank番号のwav/.okが書かれていたため、最終
  選定結果が変わっても古いattemptの音声が使われ続けていた(実測:
  kp2英語="belong to"[someone欠落、ユーザー報告と一致]、kp3英語は実際
  "Awake"、kp5英語は実際"Advantage"、日本語gloss5件も現行canonicalと不一致)。
  v2はKey Phrase選定結果(JSON)のみv1を再利用し、**音声は新規ディレクトリで
  全件新規生成**することで構造的に回避。修正後: `key_phrase_consistency.json`
  で5件全てmatch_en=true・match_ja=true。
- **Family A流用**: Intro/Outro/Notification(3箇所)は既存SFXジングルを
  そのまま使用。Welcome/Preview intro/Key phrases intro/Full story introは
  記事非依存の既存B1共有資産をコピー流用(追加TTSなし)。Topic introは
  A2既定の`Today's topic is {title}.`パターンへ変更(v1はタイトル単体の
  みでタイトル読み上げ不足)。Comment前後pause(1.0s en→ja/0.8s ja→en)と
  Outro直前pause(0.5s)はA2既存値(`build_a2_timeline`)へ統一(v1は
  0.6/0.8sでFamily A値と不一致だった)。
- **Mother Voice分離**: 母親発話をErinome(既存2V Voice B)へ分離。Mayaは
  分離しない(報告された不具合が母親発話のみのため)。

### 1.2 runtime evidence・Audio Validation

Audio Validation Gate: PASS(`home_robots_v2/audio_validation.json`、
level=`FAMILY_C_TRIAL_09B`)。全38 segment(narrator/robot/mother混在)+
15 Key Phraseサブsegment、`tts_generation_results.json` status=OK。
retry/fallback上限到達(STOPPED)は0件。テスト38件PASS
(`er013_family_c_episode_trial_09*_test_*.py`、本タスクで実測再確認)。

### 1.3 Comment位置・前後volume

C1(導入、Full story intro直後)duration=6.10s、C2(段落9/10境界)6.88s、
C3(段落22/23境界)9.22s、C4(Story終了後)6.64s。前後pause値は1.1節参照。

### 1.4 SFX

Intro/Outro/Notification(3箇所)はA-Family既存ジングルをそのまま使用。
新規SFX・新規演出は追加していない。

### 1.5 Mother Voice

Erinome(既存2V Voice B、`APPROVED_FOR_PRODUCTION`実績あり)。**重要な
留保**: SSOT(`er012_output/editorial_b_voices_phase1_5_3v_4v_integrated_
trial_03/design.md`)を確認した結果、Algieba/Erinome/Schedar/Sulafatの
「男性的/女性的」という印象は正式には記録されていない。Erinomeは実績・
安定性を理由とした暫定選定であり、ユーザー試聴の結果、意図と異なる
印象であれば差し替えが必要(6節参照)。

### 1.6 Key Phrase text-audio consistency

5件全てmatch_en=true・match_ja=true(`key_phrase_consistency.json`)。

### 1.7 Intro-Outro-title-pause

Intro→Welcome→0.5→Topic intro→0.65→Japanese title→0.5→Notification1→
0.4→Preview intro→0.65→Preview→0.5→Notification2→0.4→Key phrases intro→
0.5→KP1〜5→Notification3→0.4→Full story intro→1.0→Comment1→0.8→
Story(段落0〜9)→1.0→Comment2→0.8→Story(段落10〜22)→1.0→Comment3→0.8→
Story(段落23〜33)→1.0→Comment4→0.5→Outro。全pause値はFamily A(A2)既存値。

### 1.8 Story本文不変確認

`home_robots_v2/audit/article_unchanged_sha256.json`: v1=v2=
`ee45d0b608c565cbf6a11e7178a2eb6e955bdbaeddc392d8c2e3477e6300ded1`
(identical=true)。

### 1.9 player URL・direct audio URL・duration

- player: https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_v2/player.html
- direct audio: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_v2/web/family_c_home_robots_trial_09b.mp3
- duration: 319.593秒(5:19.6)、peak=0.9544(clipping無し)

### 1.10 追加費用・Production 1生成セット総原価

本タスク(v2作成)実測¥52.20。Family C累計(v1¥96.30+v2¥52.20)=**¥148.50**。
Family C予算枠(¥133.99)を**約¥14.51超過**(理由: Key Phrase/Preview
音声の全面新規生成+4者照合用ASR診断72件、いずれも委任文の要求に
対応するための追加コスト)。

### 1.11 unresolved issue

(1) Mother voice(Erinome)の性別的印象はSSOT未確認、ユーザー試聴後の
確定が必要。(2) `_resumable_reuse()`型resumabilityパターン(ファイル+
`.ok`存在のみで判定しテキスト内容ハッシュを見ない)は、Family C以外の
Trial scriptにも同種の潜在リスクがある可能性(横展開調査は未実施)。
(3) Audio Validation Gateがcanonical_textとASR実測の再照合を行わない
設計上のgap(1.12節)。

### 1.12 final status

**VALIDATED候補(Trial、ユーザー試聴待ち)**。Production採用・B1/B2生成は
行っていない。v1は「試聴NGを受けVALIDATED扱いを取り消し、v2を作成」と
記録する(v1自体は無変更のまま保持、比較用)。

### 1.13 なぜv1が「完成」と報告できたか

(a) **表示/音声不一致を検出する仕組みが存在しなかった**: Audio
Validation Gate(`er003_v1_n3_01_assemble.py::verify_episode_audio_
validation_gate()`)は`tts_generation_results.json`の`status=="OK"`と
sha256存在のみを検証し、audio実体をASR再照合しない(呼び出し側が渡す
`canonical_text`を無条件で信用する設計)。(b) **`_resumable_reuse()`の
resumability bug**(1.1節)により、Key Phrase・Preview音声が実際には
古いcanonical textの内容のままだったにもかかわらず、audit entryには
「現在のcanonical_text」が記録され、Gate PASSした。(c) Family C用の
`required_structure`が未登録(level=`FAMILY_C_TRIAL_09`)のため、
Intro/Outro/Comment数等の「構造上あるべき要素」の充足チェックが一切
働かなかった。(d) player/display/audio の3者一致を検証するQAが元々
存在しない(標準player format[PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-
STANDARD-FORMAT-11]はUI表示のみを規定し、内容一致検証は範囲外)。

---

## 2. Trend

### 2.1 修正内容・修正前後

Trend A2の`point_two`(Amazon Alexa+関連の表記)は前回run
(2026-09-14)でASRが"Alexa+"のまま書き起こしHuman Review Cost Guardで
ロックされていた。ユーザー承認(2026-09-15)に基づき`approve_regenerate()`
を1回のみ呼び出し(対象=同ファイル、canonical text sha256は前回lock
エントリと完全一致=テキスト変更なしを機械確認済み)、同一canonical
text・同一経路で1回限りの承認付き再生成を実施。

### 2.2 runtime evidence(時間差run)

前回(2026-09-14T20:25:16 UTC): final_status=`ASR_VALIDATION_UNCERTAIN`、
ASRが"Alexa+"のまま書き起こし、verified=false。今回(2026-09-15T08:56:47
UTC): final_status=`OK`、ASRが"Alexa Plus"と書き起こしcanonicalと一致、
classification=`NORMALIZED_MATCH`、verified=true。経過時間=45091秒
(約12時間31分)。canonical_text_sha256は両run完全一致。TTS attempt数=1、
ASR呼び出し2回(標準ペース+6% time-stretch再検証、既定挙動どおり)。
詳細: `trend/audio/a2/point_two_time_variance_run.json`。

### 2.3 Audio Validation

gate_off=PASS(Assembly成功)。gate_on(`verify_episode_audio_validation_
gate`、緩和なし)=PASS(`trend/audio/a2/audio_validation.json`)。

### 2.4 player URL・direct audio URL・duration

**A2(新規完成)**
- player: https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/trend/audio/a2/player.html
- direct audio: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/trend/audio/a2/web/episode.mp3
- duration: 415.42秒(約6分55秒)

**B1B(既存、2026-09-14完成分)**
- player: https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/trend/audio/b1b/player.html
- direct audio: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/trend/audio/b1b/web/episode.mp3
- duration: 364.734秒

### 2.5 追加費用・Production 1生成セット総原価

本タスク実費=¥3.36(point_two 1回の再生成)。本タスクで**cost
aggregation bug**を発見・補正した: 従来の`cost_summary_audio.json`
levels.b1b=¥160.16は実際にはa2初回パス分まで混入した誤値だった。補正後:
a2=¥93.98、b1b=¥69.54、combined=¥163.52。**Trend総原価(補正後)=
¥174.03(本文)+¥163.52(A2+B1B音声化)=¥337.55**(旧報告¥334.18/
¥334.19はバグ発見前の値。差額の大部分はバグ補正による再配分であり
実際の追加支出ではない、本タスクの追加支出は+¥3.36のみ)。

### 2.6 unresolved issue

なし(A2・B1BともAudio Validation Gate PASSで完成)。OPEN-153(e)に
記載のASR表記揺れ自体は「双方向」であることが判明済み(2.8節)。恒久
対応(tts_safe_en系への辞書拡張等)は依然ユーザー承認要。

### 2.7 final status

A2・B1BともAudio Validation Gate PASS、試聴可能。

### 2.8 なぜ既存normalizerで表記揺れを吸収できなかったか

既存の記号・複合語対応(`_KP_COMPOUND_OVERRIDES`辞書、healthspan→
health span等)は**単一方向の固定テキスト置換**(TTS入力テキスト側を
書き換えるだけ)であり、ASR側の書き起こし表記そのものの揺れを予測・
吸収する仕組みではない。「Alexa+」は前回runではASRが記号のまま
"Alexa+"と書き起こし、今回runでは同一canonical text("Alexa Plus")に
対しASRが"Alexa Plus"と書き起こした。つまりASR側の表記ゆれは
**双方向**(run次第で記号/展開形のどちらにも振れる)であり、一方向
置換だけでは原理的に安定して吸収できない(今回はたまたまASRが
canonicalと一致する側に振れてPASSしたに過ぎない)。既存QAが「完成と
誤報告」しなかったのは正しい動作(Human Review Cost Guardが1 attemptで
即座にロックし、0 API callで安全に停止した)。

---

## 3. Discovery

### 3.1 修正内容・修正前後(B1B)

旧文「In a study of 2,557 college students at 12 sites in 11
countries, an everyday activity was enjoyed more than thinking for
pleasure in every country tested.」
→ Attempt1(1文短縮)「In a study of about 2,500 college students in
11 countries, ...」
→ Attempt2(2文分割、意味不変、**現在のcanonical**)「In a study of
about 2,500 college students in 11 countries, an everyday activity
was enjoyed more than thinking for pleasure. This was true in every
country tested.」
Ledger F007実測(N=2,557; 12 sites; 11 countries)に対し、about 2,500は
丸め、12 sitesの省略は情報削減であり矛盾ではないと確認
(`b1b/audit/fix02_ledger_consistency_check.json`)。

### 3.2 QA結果

両Attemptとも diff QA(Fact Checker A'+Ledger Deviation Checker)=
resolved=True/human_review_required=False/blocks_acceptance=False/
fact_check_verdict=PASS。Directional Fact Precheck(non-blocking)=
DIRECTION_REVIEW_REQUIRED(既存仕様上blockingではない)。

### 3.3 TTS/ASR結果(B1B、STOP)

Attempt1は3attempt中3回ともTRUE_CONTENT_MISMATCH(文の脱落の疑いを
含む)。Attempt2(2文分割)は3attempt中3回ともTRUE_CONTENT_MISMATCHだが、
ASR書き起こしを確認したところ内容(数値・国名・意味)自体は全て含まれ
ており**文の脱落は解消していた**。不合格の実体は「In a study」→
「In one study」、「Japan–United States」→「Japan/U.S.」等の**細部の
言い回し差**によるものだった。委任文の禁止事項(それ以上の構造変更、
segment分割等)によりこれ以上は追加対応せずSTOP。

### 3.4 A2長さ調査(短縮候補は生成せず)

公式ロジック(見出し除外、本文のみ)=**604語**(目安280-420の約1.44倍)。
`CURRENT_SPEC.md`541行目でA2全体語数「上限なし・意図的に削らない」が
`DECIDED`。コード内`TOTAL_SOFT_LOWER/UPPER`定数は今回の生成経路
(staged経路)に配線されておらず、配線先の非staged経路でも記録のみで
gate/警告なし。Fact Checker/Ledger Deviation/Point Overlap QAはいずれも
長さを判定しない。「大幅超過時にユーザーへ明示」運用は**未規定**
(既存仕様と矛盾はしないが規定もされていない)。短縮候補は**生成せず
STOP**(staged経路のWriter promptには既定length targetがなく、同一
Ledgerでの無変更再生成が目安内へ収まる根拠がないため)。

### 3.5 Audio Validation

A2: 既存(2026-09-14完成分、Gate PASS、480.082秒)、本タスクでは無変更。
B1B: 未実行(Assembly到達前にSTOP)。

### 3.6 player URL・direct audio URL・duration

**A2(既存)**
- player: https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/a2/player.html
- direct audio: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/a2/web/episode.mp3
- duration: 480.082秒

**B1B**: 未生成(Assembly到達前にSTOP、player/mp3なし)。

### 3.7 追加費用・Production 1生成セット総原価

Part 1(B1B短文化)実費=¥40.98(TTS¥38.85+diff QA¥2.14)。Part 2(A2長さ
調査)実費=¥0(API不使用、短縮候補は生成せず)。**Discovery総原価=
¥565.10(前回まで)+¥40.98(本タスク)=¥606.08**。

### 3.8 unresolved issue

**(a) B1B音声**: 2文分割で文の脱落は解消したが、TTS/ASRの細部言い回し
差(a/one、United States/U.S.等)で3回とも不合格のままHUMAN_REVIEW_
LOCKED。何を試したか=1文短縮/2文分割の2パターン×各3回TTS試行。何が
残ったか=言い回し差そのものは解消不能(委任文の禁止事項によりこれ以上
のsegment分割・構造変更は未実施)。ユーザーに必要な判断=
`approve_regenerate()`実行可否、またはテキスト側の追加対応方針。
**(b) A2長さ運用**: 604語(目安の1.44倍)を(a)現行仕様のまま受け入れる
/(b)staged経路へsoft target配線をProduction変更として正式検討(要承認)
/(c)完成報告運用ルールのみ追加(Prompt/Validator変更なし)、のいずれかを
ユーザーが判断する(OPEN-135末尾に候補記載、5節参照)。

### 3.9 final status

A2=試聴可能(既存、READY)。B1B=音声未完成(USER_DECISION_REQUIRED)。

### 3.10 なぜ完成と報告できたか(A2長さ)

A2全体語数には既存仕様上そもそも上限が存在しない(意図的`DECIDED`)。
コード内`TOTAL_SOFT_LOWER/UPPER`はstaged経路(今回の生成経路)に配線
されておらず、配線されている非staged経路でも記録のみでgate/警告なし。
Fact Checker/Ledger Deviation/Point Overlap QAが全てPASSした時点で
status=OKが返る設計であり、どのQAも長さを判定しない。

---

## 4. Voices(2V、一人称版)

### 4.1 修正内容・修正前後

一人称"I"はB-Family Voices 2V(Voice A/B)の**既存APPROVED_FOR_
PRODUCTION仕様**(2026-09-08決定)。不整合の所在:
`er012_b_family_voices_writer_generic_01.py`の
`COMMON_INTRO_AND_STRUCTURE_BLOCK_TEMPLATE_2V`に、3V用テンプレートには
存在する【人称】指示block・禁止事項1行が**丸ごと欠落**していた(3V側は
無変更のまま温存)。修正: 同ブロックへ【人称(重要、2026-09-08ユーザー
正式決定、APPROVED_FOR_PRODUCTION)】block+禁止事項1行を追加
(diff +13行、3V関数・3Vテンプレートは1文字も変更なし)。旧テスト
`test_does_not_mention_three_person_wording`は逆に一人称"I"指示の
**非存在**をassertしていた設計不備があり修正、新規
`test_first_person_instruction_present`を追加。

### 4.2 再生成runtime evidence

同一Ledger・Prompt無変更、既存2V正式経路(`run_voices_2v_b1_v2.py
--reuse-ledger`)で3回試行:
- r1: attempt1 Leakage FAIL(voice_b)→attempt2 Leakage FAIL(tension)
  →attempt3 Leakage PASS・**Fact Checker FAIL**(Tension文の政治的
  態度変化claimが2026-02のNature論文と矛盾)。NG_REVIEW_REQUIRED。
- r2: attempt1 Leakage FAIL→attempt2 Leakage PASS・Fact Checker PASS・
  Ledger Deviation該当1件がLocal Rewrite自動修正で位置特定失敗、
  `human_review_required=True`。NG_REVIEW_REQUIRED。
- r3: attempt3でfinal_status=OK、Fact Checker A' verdict=PASS、Ledger
  Deviation overall_status=LEDGER_COMPLIANT、Comment Contract
  (preview/comment_1-4)も全件OK・LEDGER_COMPLIANT。
- pov_check(機械カウント): 修正前baseline(`run2_clean/attempt3`)は
  Voice1/2とも一人称0件・三人称8件/4件。r3確定記事はVoice1=一人称10/
  三人称0、Voice2=一人称9/三人称0。**一人称化は成功**。Hook/Tension/
  Closingは三人称のまま(仕様どおり不変)。

r1/r2でFact Checker A'・Ledger Deviation Local Rewriteが実際に発火し
NG_REVIEW_REQUIREDで停止したのは、POVとは無関係な**Tension文の事実
精度**の問題であり、Gate/Local Rewriteが正しく機能した実例
(OPEN-120のevidence)。

### 4.3 音声化・Audio Validation

r3確定記事(`run3_first_person_r3/b1_2v_new_theme_attempt3/article.md`、
382語、27文)で音声化を実施。1回目実行でKey Phrase音声生成ステップの
欠落によりAssemblyがFileNotFoundErrorで停止(run1に存在した既知の
欠落と同一原因)。`step_key_phrase_audio()`を追加し既存segment/Key
Phrase結果を再利用する冪等性チェックも追加して再実行、成功。TTS:
14 segment全OK、Key Phrase 5件×en/ja全OK。Assembly: status=OK
duration=321.105s peak=0.88535 clipping=False。Audio Validation
Gate=PASS(14/14 VALIDATED)。

### 4.4 Comment/Fact Safety反映証拠・残存Leakage

`voices/audio/b1_2v_v2/comment_fact_safety_evidence.json`に記録:
r1(Fact Checker FAIL)・r2(Ledger Deviation human_review_required=True)
でGateが実際に発火・停止したevidence(OPEN-120)、r3ではfired=false
(記事は既にPASS状態で確定)。Analytical Leakage Check(voice_b 5項目・
tension 2項目)は3attempt上限到達後もflagged残存(既存仕様どおり、
Gate緩和なし・隠さず記録、OPEN-151残存事象)。

### 4.5 player URL・direct audio URL・duration

- player: https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/voices/audio/b1_2v_v2/player.html
- direct audio: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/voices/audio/b1_2v_v2/web/episode.mp3
- duration: 321.105秒

### 4.6 追加費用・Production 1生成セット総原価

r1/r2実費=¥76.62、r3+音声化実費=¥92.36(r3 Writer/Comment/QA/Gate=
¥55.82+音声化¥36.54)。**Voices総原価=¥185.74(既存)+¥76.62+¥92.36=
¥354.72**。

### 4.7 unresolved issue

Analytical Leakage Check(voice_b 5項目/tension 2項目)が3attempt上限
到達後も残存。何を試したか=r1〜r3の3回の独立再生成(retry上限・Gate
基準は変更していない)。何が残ったか=記事は確定・音声化完了したが
Leakage flagは解消していない。ユーザーに必要な判断=(a)残存Leakageを
許容したままPRODUCTION_WIRED化するか、(b)追加Prompt改善を別途検討
するか。

### 4.8 final status

**PARTIAL / USER TEST READY(一人称版)**。OPEN-151は`PARTIAL`のまま、
`PRODUCTION_WIRED`は宣言しない。

### 4.9 なぜ既存QAで三人称化を検出できなかったか(+今回Gateが正しく
機能した対比)

Analytical Leakage Check(2V/3V共通)は`leak_evidence_subject`等6項目
のみで、いずれも「調査データが前面に出ていないか」「語り手が外側から
分析していないか」を見るものであり、**文法上の人称(I vs she/he)自体
は判定項目に含まれていない**。Fact Checker/Ledger Deviation Checkも
事実の正確性のみを見る。Comment Contract QAもコメント文の内容を見る
のみ。このため、2V用Promptに一人称指示が欠落したまま「三人称だが
構造的には正しい」記事がLeakage PASSしてしまい、既存QA全体では検出
できなかった。対比: 今回のr1/r2でFact Checker A'・Ledger Deviation
Local Rewriteが実際に発火しNG_REVIEW_REQUIREDで停止したのは、POVとは
無関係なTension文の事実精度の問題であり、各Gateが「見るべきものを
見て正しく機能した」例(OPEN-120のevidence)。

---

## 5. 未解決事項の一覧(何を試したか/何が残ったか/ユーザーに必要な判断)

| 対象 | 何を試したか | 何が残ったか | ユーザーに必要な判断 |
|---|---|---|---|
| Discovery B1B音声 | 1文短縮/2文分割×各3回TTS | 言い回し差(a/one、Japan-U.S.)で3回とも不合格、脱落自体は解消 | `approve_regenerate()`実行可否/テキスト側追加対応方針 |
| Discovery A2長さ運用 | 仕様・配線箇所を調査(¥0) | 604語(目安の1.44倍)、警告なし | (a)現行仕様のまま受入/(b)soft target配線を正式検討/(c)完成報告運用ルールのみ追加、のいずれか |
| Family C Mother voice印象 | Erinome選定(実績・安定性理由) | 性別的印象がSSOT未記録のまま | ユーザー試聴後、意図と異なれば差し替え要否を判断 |
| Voices Leakage残存 | r1〜r3の3回再生成 | voice_b 5項目・tension 2項目のflagged残存 | 許容したままPRODUCTION_WIRED化するか、追加Prompt改善を検討するか |

---

## 6. Web到達確認結果

`docs/pm/web_playback_check_FIX02.json`に実測全件記録。要旨:
direct mp3 5件全てHTTP 200(Content-Type: audio/mpeg)、player.html
(raw.githack)5件全てHTTP 200(text/html; charset=utf-8)、各player内
相対参照(episode+先頭3 segment、計20件)を`raw.githubusercontent.com`
基準でHEAD相当確認、全てHTTP 200。CDN遅延による待機・再試行は発生
しなかった(初回確認で全件到達)。commit `ccf43e8c09fe6773251174a8dd
6038dc764c12ab`のpush直後に確認。

| 対象 | direct mp3 | player.html |
|---|---|---|
| Family C v2 | 200(3,472,272 bytes) | 200(18,130 bytes) |
| Trend A2 | 200(4,664,280 bytes) | 200(20,049 bytes) |
| Trend B1B | 200(4,312,968 bytes) | 200(18,720 bytes) |
| Discovery A2 | 200(5,398,416 bytes) | 200(21,125 bytes) |
| Voices v2 | 200(3,762,912 bytes) | 200(16,811 bytes) |

---

## 7. Production 1生成セット総原価(PM_GOVERNANCE 15-8形式)

| Family | 総原価 | 備考 |
|---|---|---|
| News | ¥98.32 | 無変更(A2+B1) |
| Trend | **¥337.55** | 本文¥174.03+音声化¥163.52(補正後、本タスクで level別二重計上バグを発見・補正。従来報告¥334.18/¥334.19は誤り、差額の大部分はバグ補正による再配分で実支出ではない、本タスクの追加実支出は+¥3.36のみ) |
| Discovery | **¥606.08** | 本文¥463.27+音声化¥85.51+¥16.32(既存)+¥40.98(本タスクPart1) |
| Voices(2V) | **¥354.72** | 本文¥140.39+音声化¥32.34+¥13.01(既存)+¥76.62(r1/r2)+¥92.36(r3+音声化) |
| Family C Trial-09(参考、別予算枠) | **¥148.50** | v1¥96.30+v2¥52.20、Family C予算枠¥133.99を¥14.51超過 |

---

## 8. OPEN-153追記内容(ユーザー指示、原文要旨反映)

観測仮説として、今回複数のTTS問題が集中したが恒常的なProduction
defectと断定しない。併記する可能性: TTS run-to-run variance/時間依存の
一時的不安定性/特定text shapeとの相互作用/記号・数字・長文等の入力
前処理不足/ASR側表記揺れ/Gemini version。当面: 標準=Gemini 2.5 Flash
TTS。将来retry候補: Gemini 3.1 Flash TTS(仮イメージ: 2.5で通常生成、
NG時のみ3.1をretry候補として検証。正式routingではない、詳細は今後
Trialで決める)。比較観点: 品質/ASR一致率/読み飛ばし率/retry率/
latency/Production 1生成セット総原価。3.1は2.5よりTTS単価が高いため
品質だけで評価せずretry削減込みの総原価で比較する。

再発例: Trend A2 point_two時間差runは通過(揺れは双方向、2.8節)、
Discovery B1B言い回し差(a/one、U.S.、3.3節)、Family C v1のKey Phrase
音声stale問題(TTSではなく`_resumable_reuse()`の再利用ロジック起因と
区別して記録、1.13節)。

OPEN_ITEMS.mdへの反映位置: OPEN-153(本文末尾追記)。

---

## 9. SSOT反映位置

- `OPEN_ITEMS.md`: OPEN-135(A2 length運用ルール候補を末尾に記載)/
  OPEN-147(参照のみ、変更なし)/OPEN-151(Voices r1/r2/r3結果を追記)/
  OPEN-152(保持、変更なし)/OPEN-153(観測仮説+再発例を追記)/
  OPEN-120(Voices r1/r2のFact Safety Gate実発火evidenceを追記)。
- `DECISION_LOG.md`: `## PM-CLOSEOUT-CONSOLIDATION-134`エントリ+索引1行。
- `CURRENT_SPEC.md`: B-Family Voices 2V節末尾(667行目直前)に
  Production不整合修正の記録を1段落追加。
- `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: Family C v2/Trend A2/Voices v2
  (r3+音声化)のrun行を追記。
- `er014_output/four_type_observation_01/index.html`: v2 player・Trend
  A2・Voices v2リンク、Trend総原価訂正。

---

## 10. Git

- commit 1回目: `ccf43e8c09fe6773251174a8dd6038dc764c12ab`
  (成果物本体、513 files changed)
- commit 2回目: SSOT反映・最終REPORT・Web到達確認・OPEN-153追記
  (本コミット、詳細は`docs/pm/RESULT_PACKET.md`参照)
