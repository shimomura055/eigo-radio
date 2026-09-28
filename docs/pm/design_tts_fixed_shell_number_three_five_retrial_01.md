# design_tts_fixed_shell_number_three_five_retrial_01.md

管理ID: TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01(Trial)

## 1. 目的

TRIAL-02(`TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02`)でユーザーが既に決定した
Champion列位置(welcome=左/preview_intro=右/key_phrases_intro=右/
full_story_intro=右/num_one=右/num_two=中/num_four=右/point_explanation=中)
のうち、num_three/num_fiveは既存3 candidateいずれも決定的な採用候補が無い
(num_threeはB/C両方とも3attempt全滅、num_fiveはCandidate A[Baseline]の
pitch_trendが「rising(疑問形っぽさの疑い)」)。採用済みOne/Two/Fourと
モデル・voice・style思想(センス)を変えず、同条件でnum_three/num_fiveの
複数takeを生成し、ユーザーが良いtakeを選べるようにする。

## 2. 列順→A/B/C対応表の確定根拠

`user_test/fixed_shell_champion_trial_02/index.html`の比較表ヘッダー
(29行目)は
`<th>Phrase / Group</th><th>Baseline/Candidate A</th><th>Candidate B</th><th>Candidate C</th>`
の順であり、**表の列順どおり 左=A、中=B、右=C**。以下、delegationが
指定した各既決phraseの位置(左/中/右)を実データと突き合わせて確認した
(採用style文言・実測値は同HTML本文から転記、逐語)。

| phrase | 位置(delegation) | 対応candidate | 実際に確認したstyle/値 |
|---|---|---|---|
| welcome | 左 | A(Baseline) | style="既存Production v2_flash_lite_short_style(FALLBACK[0])" |
| preview_intro | 右 | C | style="natural, clear, conversational"(B/C同一文言、Cが採用) |
| key_phrases_intro | 右 | C | style="natural, clear, conversational"(B/C同一文言、Cが採用) |
| full_story_intro | 右 | C | style="natural, clear, conversational, unhurried pace, with a brief pause before continuing"(B/C同一文言、Cが採用) |
| num_one | 右 | C | Bは3attempt全滅(STOPPED)のため実質Cのみが選択肢。style="measured, matter-of-fact delivery, consistent energy and tempo for every word, plain falling pitch at the end, spoken as a flat statement, not a question" |
| num_two | 中 | B | style="calm, steady, declarative tone, even volume and pace across the set, ending each word with a clear falling pitch, stated plainly, never rising like a question"、pitch_trend=falling |
| num_four | 右 | C | Bは3attempt全滅(STOPPED)のため実質Cのみが選択肢。style同上num_one(C系統)、pitch_trend=rising(疑問形っぽさの疑い、既知課題) |
| point_explanation | 中 | B | style(JA)="自然な抑揚をつけて、はっきりと落ち着いた調子で話す" |

model/voice(全phrase共通、無変更): `model=gemini-3.8-flash-lite-tts`、
`voice=Charon`。

## 3. num_three/num_five再Trialの方針

採用済みOne(C系統)/Two(B系統)/Four(C系統)の中に、B系統・C系統の**両方**が
含まれているため、delegation本文「B系統・C系統の両方が採用されているなら
両方」に従い、num_three/num_fiveともに**B系統style・C系統styleの両方**で
生成する。style文言は`er043_tts_fixed_shell_master_champion_trial_02.py`の
既存定数`STYLE_TEXT_GROUP3_B`/`STYLE_TEXT_GROUP3_C`をそのままimportして
使う(新規文言を考案しない、モデル・voice・基本Style思想の変更禁止を厳守)。

- STYLE_TEXT_GROUP3_B(=num_two採用style、逐語):
  "calm, steady, declarative tone, even volume and pace across the set,
  ending each word with a clear falling pitch, stated plainly, never
  rising like a question"
- STYLE_TEXT_GROUP3_C(=num_one/num_four採用style、逐語):
  "measured, matter-of-fact delivery, consistent energy and tempo for
  every word, plain falling pitch at the end, spoken as a flat
  statement, not a question"

各語×各style系統×4 take = 2×2×4 = 16 take。各takeはProduction既存の
`voice01.generate_charon_english`(`review_lock.guarded_generate`
decorator、`PRODUCTION_MAX_TTS_ATTEMPTS=3`のASR検証cascade+Human Review
Lock)をそのまま1回呼ぶ(独自retry追加なし)。takeごとに内部で最大3
attemptが走る可能性があるため、理論上限は16×3=48 API call(+同数ASR)だが、
TRIAL-02実測(¥1.54/64 record、10 phrase・B/C両candidate・複数3attempt
失敗を含む)から単価は極めて小さく、¥20上限内に収まる見込み(§6実測欄に
実費用を記録)。

## 4. Master Audio Store key設計(take差異化)

`er006_master_audio_store_01.MasterAudioKey`は
`style_instruction_id`/`style_instruction_version`/`level`等が一致すると
既存生成物をreuseする(2回目以降は新規生成しない)。4 take独立生成のため、
style_instruction_id/versionは採用candidateと同一のまま(centeng文言の
出自を保つ)、`level`フィールドのみ`"retrial01_take{n}"`として take間で
異なるkeyにする(styleの実際の文言・model・voiceは一切変えない、cache
identity上の差異化のみ)。

out_pathは Human Review Lock の`_has_valid_narration_layout`
(".../<theme>/<level>/narration/<segment>.wav"、4階層以上必須)を満たす
よう `er047_output/.../{MANAGEMENT_ID}_{name}_style{candidate}/take{n}/
narration/{name}.wav` とする。これにより take ごとに Human Review Lock の
状態(`review_lock_state.json`)が独立し、あるtakeの3attempt失敗が他の
takeの新規生成をブロックしない(既存安全装置の仕様どおり、独自の回避や
無効化はしていない)。

## 5. 採用済みOne/Two/Fourの再利用

新規TTS/ASR呼び出しは行わず、`er043_output/tts_fixed_shell_master_champion_trial_02/`
配下の既存wav(candB/num_two、candC/num_one、candC/num_four)をそのまま
読み取り専用でコピーする(¥0)。試聴ページ冒頭に、採用candidate・style
全文・model/voiceとともに掲載する。

## 6. 実行・検証・費用実測

`docs/pm/RESULT_PACKET_TF1.md`および`TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01_REPORT.md`
に実測値(実行コマンド逐語・実費用・ASR合否内訳・regression結果・公開
確認7項目)を記録する。
