# design_tts_fixed_shell_master_champion_trial_02

管理ID: TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02(Trial、Production実装なし)

## 1. Existing Spec / Prior Trial確認

- 対象10 phrase(EN 9+JA 1)は`TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01`で既に
  棚卸し済み(`er006_audio_cost_pilot_02_shared_narration.FIXED_ENGLISH_TEXTS`
  9件+`FIXED_JAPANESE_TEXTS_A2_ONLY`1件、詳細`TTS-FIXED-SHELL-MASTER-CHAMPION-
  TRIAL-01_REPORT.md`§1)。
- 現行Production Master実測(read-only、`er006_output/master_audio_store_01/
  manifest.json`):
  - EN 9件全て`style_instruction_id="charon_english_fixed_shell"`,
    `style_instruction_version="v2_flash_lite_short_style"`,
    `tts_model_id="gemini-3.8-flash-lite-tts"`, voice=Charon,
    `asr_verified=True`(9/9)。styleは`er006_audio_cost_pilot_02_shared_
    narration._resolve_shell_english_style_prefix_override`経由で
    `er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`
    =**"natural, clear, conversational"**(9件全てに同一文言を適用、welcomeから
    num_fiveまで区別なし)。
  - JA(point_explanation)は`style_instruction_id="charon_japanese_fixed_shell"`,
    `style_instruction_version="v1"`, override無し(既定`voice01.p9a.
    JAPANESE_STYLE_PREFIX`=記事本文向けの長い既定style、短い4文字phrase
    「ポイント解説」に対してもそのまま適用されている=ユーザー指摘「平板」の
    直接原因と考えられる)。
- 過去Trial(TRIAL-01)実測: Candidate A(現行Production Master再利用)は
  One〜Five 5/5全件OK・drift無し(揃い: duration幅0.33秒、RMS幅4.68dB)。
  Candidate B(Role style「brief, clear, neutral」)はnum_one/two/three
  3attempt全滅(OPEN-222)。Candidate C(2.5 Pro系既定style)もnum_three
  3attempt全滅・num_two 3attempt中2回CJKドリフト。**「brief, clear,
  neutral」という文言そのもの、および2.5 Pro系既定styleのいずれでも
  極短数字語の不安定性が再現しており、Flash-Lite固有の問題ではない
  ことが既に確認済み**(OPEN-222)。本Trialではこの既知失敗文言を
  そのまま使わず、新しいstyle文言を設計する。

## 2. Candidate設計

対象は同じ10 phrase。A=Production既存Master再利用(新規TTS/ASR無し、¥0)。
B/C=新規生成2候補(Flash-Lite backend、モデルは揃えてstyle文言のみ変える。
理由は§4)。

### 2-1. num_four の扱いについて(委任文内表記の解消)

delegation Fable補足の(i)は「指摘なしphrase」の例としてnum_fourを挙げるが、
(ii)は「num_one〜num_five=5個セットとして同一styleで一括生成」と明記しており、
num_fourの扱いについて両者は矛盾している。ユーザー原文(「One.〜Five. 現行は、
One / Two が大人しめ、Three が勢い強すぎ、Five が疑問形っぽい。→ 5個セットと
して、テンション/抑揚/語尾/音量/テンポを安定させる」)を最上位の根拠とし、
5-word setの一体性(numだけ旧styleを残すと「揃い」を安定させるという目的自体が
達成できない)を優先して、**num_fourも5個set styleの対象に含める**ことを実装
判断とした。よってグループ分けは以下の通り:

- グループ1(指摘なし、baseline再現x2): welcome / preview_intro / key_phrases_intro
- グループ2(指摘あり、pace調整): full_story_intro
- グループ3(指摘あり、5個set安定化): num_one / num_two / num_three / num_four / num_five
- グループ4(指摘あり、JA抑揚): point_explanation

### 2-2. Candidate A(Baseline)

Production既存Master(EN=`v2_flash_lite_short_style`、JA=`v1`)をread-onlyで
コピー再利用。新規TTS/ASR呼び出し無し。`er040_tts_fixed_shell_master_champion_
trial_01.ensure_candidate_a_from_production`をそのまま呼ぶ(import/流用、
Trial側は独自実装を追加しない)。10/10対象。

### 2-3. Candidate B/C 共通仕様

- model: `gemini-3.8-flash-lite-tts`(`TTS_MODEL_FLASH_LITE`)
- backend: `tts_backend="speech_metadata_flash_lite"`
- voice: Charon(既存と同じ)
- 生成関数: `voice01.generate_charon_english`(EN、`style_prefix_override`
  引数でstyle差し替え)/ `voice01.generate_charon_japanese`(JA、
  `er040_tts_fixed_shell_master_champion_trial_01.trial_japanese_style_
  override`コンテキストマネージャで`voice01.p9a.JAPANESE_STYLE_PREFIX`を
  一時差し替え、既存precedent[`er011_final26_runtime_evidence_01.py`]と同一手法)。
- Master Audio Key: `style_instruction_id`/`style_instruction_version`を
  Candidate/グループごとに一意にし、B/Cが誤って同一master_audio_idへcache
  hitしないようにする(グループ1・2はstyle文言自体がA/B/C間で同一のため、
  versionでB/Cを区別しないと2回目の生成が1回目のcache reuseになってしまう
  ため、versionへ`_sample_b`/`_sample_c`を付与)。
- ASR検証: 既存cascade(`secondary_asr.evaluate_attempt_with_cascade`、
  `review_lock.guarded_generate`のHuman Review Lock込み)をそのまま使う。
  独自retry追加なし。EN側`max_attempts`はProduction既定
  (`review_lock.PRODUCTION_MAX_TTS_ATTEMPTS`=3)のまま。JA側は
  `ensure_fixed_japanese_segment`と同じ`max_attempts=6`を渡すが、
  `generate_charon_japanese`内部で`PRODUCTION_MAX_TTS_ATTEMPTS`=3へ
  クランプされるため実質3回(standard 2+minimal fallback 1)。

### 2-4. グループ1(指摘なし: welcome/preview_intro/key_phrases_intro)

仕様(style文言・model・voice)をCandidate Aと同一のまま2回生成し、ばらつきを
比較する。

- style文言(B・C共通、逐語): `"natural, clear, conversational"`
  (現行Production `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`と完全一致、新規文言
  ではない)
- `style_instruction_id`: `"trial_ch2_repeat_baseline_style"`
- `style_instruction_version`: B=`"v1_sample_b"` / C=`"v1_sample_c"`

### 2-5. グループ2(full_story_intro、pace調整)

ユーザー指摘: 「現行は発音が速すぎる。少し余裕を持たせ、自然な導入にする」。
現行style="natural, clear, conversational"に、短いpace指示を追加する
(WPM等の数値指定は`common.assert_no_wpm_specification`によりブロックされる
ため使わない)。

- style文言(B・C共通、逐語): `"natural, clear, conversational, unhurried pace,
  with a brief pause before continuing"`
- `style_instruction_id`: `"trial_ch2_full_story_intro_pace"`
- `style_instruction_version`: B=`"v1_pace_b"` / C=`"v1_pace_c"`

同一文言をB/Cで2回生成し、ばらつきの中から選べるようにする(pace調整の
方向性は1つに絞り、文言のバリエーションは作らない。ユーザー指示が「少し
余裕を持たせる」という単一方向の修正であるため)。

### 2-6. グループ3(num_one〜num_five、5個set安定化)

ユーザー指摘: 「One / Two が大人しめ、Three が勢い強すぎ、Five が疑問形
っぽい。5個セットとして、テンション/抑揚/語尾/音量/テンポを安定させる。
特にFiveを疑問形にしない」。TRIAL-01の失敗文言(「brief, clear, neutral」)は
再利用しない(OPEN-222)。B/Cで異なる2種類のstyle文言を試す(ユーザー指示の
「B・Cで2種類試す」に対応)。いずれも5 word全てに同一styleを適用する
(setとしての統一性を狙う)。

- Candidate B style文言(逐語): `"calm, steady, declarative tone, even volume
  and pace across the set, ending each word with a clear falling pitch,
  stated plainly, never rising like a question"`
  - `style_instruction_id`: `"trial_ch2_num_set_style_b"`,
    `style_instruction_version`: `"v1"`
- Candidate C style文言(逐語): `"measured, matter-of-fact delivery, consistent
  energy and tempo for every word, plain falling pitch at the end, spoken
  as a flat statement, not a question"`
  - `style_instruction_id`: `"trial_ch2_num_set_style_c"`,
    `style_instruction_version`: `"v1"`

いずれも短い単語1語への適用のため、TRIAL-01同様にnum_one〜threeのいずれかで
ASR失敗(STOPPED)が再現する可能性がある。発生した場合は独自retryを追加せず
STOPPEDとして記録する(既存Human Review Lockに従う)。

### 2-7. グループ4(point_explanation、JA抑揚)

ユーザー指摘: 「現行は平板。もう少し自然な抑揚をつける」。既存precedent
(TRIAL-01の`ROLE_STYLE_JA_POINT_EXPLANATION`="簡潔に、はっきりと")とは
異なる、「抑揚」に焦点を当てた2種類の短いJA style文言を新規に作る
(B・Cで2種類試す)。

- Candidate B style文言(逐語): `"自然な抑揚をつけて、はっきりと落ち着いた
  調子で話す"`
  - `style_instruction_id`: `"trial_ch2_point_explanation_style_b"`,
    `style_instruction_version`: `"v1"`
- Candidate C style文言(逐語): `"やわらかい自然な抑揚で、簡潔かつ丁寧に伝える"`
  - `style_instruction_id`: `"trial_ch2_point_explanation_style_c"`,
    `style_instruction_version`: `"v1"`

## 3. num_two/num_threeの既知失敗との関係

TRIAL-01のCandidate B(Role style)はnum_two/num_threeを意図的に新規生成
せず、既知失敗(OPEN-222)をSKIPPED_KNOWN_FAILUREとして記録した。本Trialは
**新しいstyle文言を試すことが目的そのもの**であるため、num_two/num_threeも
含めグループ3の5 word全てを新規生成する(既知失敗の単純再現ではなく、
文言を変えた場合に改善するかどうかを確認する新規evidenceとして価値がある、
delegation「テンション/抑揚/語尾/音量/テンポを安定させる」という目的の
検証に必須)。STOPPEDになった場合はそのまま記録し、追加retryはしない。

## 4. モデル選択の実装判断

B/CともFlash-Lite backend(`speech_metadata_flash_lite`)を使う。2.5 Pro系
(`structured_separation`)は使わない。理由:
1. Candidate A(現行Production Baseline)も既にFlash-Liteであり、本Trialの
   目的は「style文言の違いによる品質差」を見ることであって、モデルの違いを
   混在させると比較が公平でなくなる。
2. OPEN-201実測でFlash-LiteはStructured Separation(2.5 Pro系)より大幅に
   安価(¥10.78 vs ¥44.85、同一記事1回完成比較)。¥40 Guardrail内に収める
   うえでも有利。
3. delegationが明記する通り「モデル比較が目的ではない」ため、B/C間で
   モデルを揃えることでstyle以外の変数を固定する。

## 5. Master Audio Key一覧(EQUALITY_FIELDS抜粋)

| Candidate/Group | style_instruction_id | style_instruction_version | tts_model_id | backend |
|---|---|---|---|---|
| A(全件) | (Production既存key、無変更) | (Production既存key、無変更) | gemini-3.8-flash-lite-tts(EN)/gemini-3.1-flash-tts-preview(JA) | (Production既存呼び出し規約) |
| B group1 | trial_ch2_repeat_baseline_style | v1_sample_b | gemini-3.8-flash-lite-tts | speech_metadata_flash_lite |
| C group1 | trial_ch2_repeat_baseline_style | v1_sample_c | 同上 | 同上 |
| B group2(full_story_intro) | trial_ch2_full_story_intro_pace | v1_pace_b | 同上 | 同上 |
| C group2 | trial_ch2_full_story_intro_pace | v1_pace_c | 同上 | 同上 |
| B group3(num_one〜five) | trial_ch2_num_set_style_b | v1 | 同上 | 同上 |
| C group3 | trial_ch2_num_set_style_c | v1 | 同上 | 同上 |
| B group4(point_explanation) | trial_ch2_point_explanation_style_b | v1 | gemini-3.1-flash-tts-preview | speech_metadata_flash_lite |
| C group4 | trial_ch2_point_explanation_style_c | v1 | 同上 | 同上 |

いずれもProduction既存key(`charon_english_fixed_shell`/`charon_japanese_
fixed_shell`)とは`style_instruction_id`が異なるため、誤ってProduction
Masterへcache hitすることは無い(Trial Store自体も隔離、二重の安全策)。

## 6. One〜Five揃い評価の方法

候補(A/B/C)ごとにnum_one〜five 5件のduration/RMSを`er002_common.
measure_metrics`で測定し、幅(max-min)を比較する。末尾ピッチ傾向は、
librosa等の外部ライブラリが本環境に無い場合は、既存`er002_common`内の
簡易手法(自己相関ベースのF0推定関数があれば流用、無ければ「末尾0.15秒の
RMS変化率」を疑問形らしさの代理指標として使い、その旨を明記する)で評価する。
One→Five連続再生mp3は`er040_..._page_01.concat_wavs`をimportして流用する。

## 7. Guardrail(実行前記録、ACTIVE_TASK_CH2.mdと同内容)

想定新規TTS call数20(B10+C10)、retry上限は既存cascade値のまま(EN=3回、
JA=3回)、想定費用¥40以内(TRIAL-01実績18generationで¥40以内完了)、
phrase group単位で分割実行し都度`fx_runner.assert_budget_ok`で確認する。
