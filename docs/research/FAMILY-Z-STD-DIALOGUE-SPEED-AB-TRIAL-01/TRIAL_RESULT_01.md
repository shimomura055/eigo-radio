# FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01 TRIAL_RESULT_01 (2026-10-23)

Status: TRIAL_COMPLETE_USER_DECISION_REQUIRED(Production未変更・Trial版のProduction反映は禁止。ユーザーの比較試聴待ち)

## 1. 条件表
| 項目 | A 現行版 | B Trial版 |
|---|---|---|
| Narrator(Story内) | 6%減速あり | 6%減速あり(Aとファイルsha256一致) |
| 登場人物の会話 | 6%減速あり | 6%減速なし(減速前の`<id>_original.wav`) |
| Voice / TTS Prompt / 本文 / 台詞 / 順序 / 効果音 / Comment / KP / shell | 現行 | 同一(同じファイル・同じ組立) |
| Advanced | 変更・再生成なし | 変更・再生成なし |

## 2. 元run特定(A版)
- 『走れメロス』: 公開ページ`user_test/family_z_melos_02/`の最終更新commit 1b9b39340(2026-10-20、run_e2e_06反映)。公開`Melos_a2_full.mp3`の長さ303.9225秒 = `melos/run_e2e_06/a2/assembly/Family_Z_melos_a2.wav`の303.9225秒(一致)。`run_jre_01`は別の証拠run(287.54秒、公開版ではない)。元run=`er026_output/family_z_production_e2e_01/melos/run_e2e_06`。
- 『開いた窓』: 公開`OpenWindow_a2_full.mp3` 325.3067秒 = `the_open_window/run_e2e_01/a2/assembly/...a2.wav` 325.307秒(一致)。元run=`er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01`。

## 3. 方式・原音の有無・再生成・費用
- 6%減速の実装: `er003_v1_n3_01_tts_generate.apply_a2_slowdown_postprocess`が`<id>.wav`を`<id>_original.wav`へcopyしてから`er008_a2_postprocess_slowdown_01.apply_a2_slowdown`(ffmpeg atempo=1/1.06、24kHz mono s16)で`<id>.wav`を上書きする。よって`_original.wav`が減速前の原音。
- 原音の有無: 全dialogue clip(『走れメロス』10、『開いた窓』18)に`_original.wav`あり。**TTS再生成0 clip・本文再生成0・追加TTS費用0円**。
- 原音の正当性: 各dialogue clipで`_original.wav`にProduction同一関数`apply_a2_slowdown`を再適用すると現行A版clipとsha256完全一致(メロス10/10、開いた窓18/18)。つまり原音=A版の生成元音声そのもの(Voice・Prompt・本文・take同一)。
- 組立: Production関数`er063.run_assembly`をTrial dirで実行。**A版を未変更narrationから再組立するとProduction公開用assembled wavとsha256完全一致**(メロス・開いた窓とも)。Bは会話clip差替えのみ(無音間隔・順序は同一)。
- 費用: 生成0円。音声QAのProduction ASR(`routing.transcribe`, en-US)を28 clipに実施(B会話clip合計132.8秒。上限見積=Azure単価0.0463円/秒(出典: OW full_story_part3_c9 asr_judgement est_jpy 0.1333/2.878秒)×132.8秒≒6.2円(実routing providerがOpenAI miniならさらに安価。正確額は未集計))。

## 4. 会話速度の実測(語/分、clip長はassembled前のclip wav長)
### 走れメロス
| 指標 | A 現行 | B Trial | 差 |
|---|---|---|---|
| 会話clip中央値(全10) | 136.1 | 143.6 | +7.5 |
| 会話clip平均 | 132.8 | 140.2 | +7.4 |
| 中央値(8語以上5) | 148.2 | 156.5 | +8.3 |
| 加重(総語数/総時間) | 131.6 | 139.0 | +7.4 |
| 参考: Narrator中央値(A=B) | 134.3 | 134.3 | +0.0 |

会話clip長比 A/B = 1.0531〜1.0579。会話合計 37.84秒→35.84秒。通し 303.923秒→301.925秒。

| # | clip | 話者 | Voice | 語数 | A秒 | B秒 | A WPM | B WPM |
|---|---|---|---|---|---|---|---|---|
| 1 | full_story_part1_c2 | melos | Algieba | 13 | 5.042 | 4.771 | 154.7 | 163.5 |
| 2 | full_story_part1_c4 | melos | Algieba | 9 | 4.022 | 3.811 | 134.3 | 141.7 |
| 3 | full_story_part1_c6 | melos | Algieba | 6 | 2.844 | 2.701 | 126.6 | 133.3 |
| 4 | full_story_part1_c8 | king | Charon | 14 | 7.459 | 7.051 | 112.6 | 119.1 |
| 5 | full_story_part1_c10 | friend | Erinome | 9 | 3.644 | 3.451 | 148.2 | 156.5 |
| 6 | full_story_part3_c2 | melos | Algieba | 4 | 3.12 | 2.961 | 76.9 | 81.1 |
| 7 | full_story_part3_c4 | melos | Algieba | 6 | 2.474 | 2.341 | 145.5 | 153.8 |
| 8 | full_story_part3_c6 | friend | Erinome | 7 | 3.089 | 2.931 | 136.0 | 143.3 |
| 9 | full_story_part3_c8 | king | Charon | 8 | 3.06 | 2.901 | 156.9 | 165.5 |
| 10 | full_story_part3_c10 | king | Charon | 7 | 3.083 | 2.921 | 136.2 | 143.8 |

### 開いた窓
| 指標 | A 現行 | B Trial | 差 |
|---|---|---|---|
| 会話clip中央値(全18) | 130.4 | 137.9 | +7.5 |
| 会話clip平均 | 129.2 | 136.4 | +7.2 |
| 中央値(8語以上8) | 140.6 | 148.9 | +8.3 |
| 加重(総語数/総時間) | 137.0 | 144.8 | +7.8 |
| 参考: Narrator中央値(A=B) | 128.4 | 128.4 | +0.0 |

会話clip長比 A/B = 1.0532〜1.0593。会話合計 102.49秒→96.93秒。通し 325.307秒→319.749秒。

| # | clip | 話者 | Voice | 語数 | A秒 | B秒 | A WPM | B WPM |
|---|---|---|---|---|---|---|---|---|
| 1 | full_story_part1_c2 | vera | Zephyr | 8 | 2.669 | 2.531 | 179.9 | 189.7 |
| 2 | full_story_part1_c4 | vera | Zephyr | 6 | 2.67 | 2.531 | 134.8 | 142.2 |
| 3 | full_story_part1_c5 | framton | Algieba | 7 | 2.666 | 2.531 | 157.5 | 165.9 |
| 4 | full_story_part1_c7 | vera | Zephyr | 11 | 5.218 | 4.931 | 126.5 | 133.8 |
| 5 | full_story_part1_c8 | framton | Algieba | 6 | 3.187 | 3.021 | 113.0 | 119.2 |
| 6 | full_story_part1_c10 | vera | Zephyr | 19 | 8.767 | 8.281 | 130.0 | 137.7 |
| 7 | full_story_part1_c12 | vera | Zephyr | 28 | 12.715 | 12.011 | 132.1 | 139.9 |
| 8 | full_story_part2_c2 | vera | Zephyr | 37 | 14.164 | 13.371 | 156.7 | 166.0 |
| 9 | full_story_part2_c4 | vera | Zephyr | 12 | 5.505 | 5.211 | 130.8 | 138.2 |
| 10 | full_story_part2_c6 | mrs_sappleton | Kore | 31 | 11.614 | 10.971 | 160.2 | 169.5 |
| 11 | full_story_part2_c8 | mrs_sappleton | Kore | 3 | 2.427 | 2.301 | 74.2 | 78.2 |
| 12 | full_story_part3_c2 | men | Schedar | 6 | 2.889 | 2.741 | 124.6 | 131.3 |
| 13 | full_story_part3_c4 | men | Schedar | 7 | 2.792 | 2.651 | 150.4 | 158.4 |
| 14 | full_story_part3_c6 | mrs_sappleton | Kore | 4 | 2.881 | 2.731 | 83.3 | 87.9 |
| 15 | full_story_part3_c8 | mrs_sappleton | Kore | 7 | 3.643 | 3.451 | 115.3 | 121.7 |
| 16 | full_story_part3_c9 | vera | Zephyr | 4 | 2.878 | 2.731 | 83.4 | 87.9 |
| 17 | full_story_part3_c11 | vera | Zephyr | 32 | 12.884 | 12.171 | 149.0 | 157.8 |
| 18 | full_story_part3_c13 | vera | Zephyr | 6 | 2.917 | 2.761 | 123.4 | 130.4 |

## 5. 同一性の証拠(照合表)
- 走れメロス: Narrator Story clip sha256一致 13/13、dialogue clipがA/Bで別ファイル 10/10、原音へのatempo再適用=A版 10/10、再生順(sequence_order)同一=True、A再組立==Production wav sha=True。Voice・本文は同一results/segment_plan・同一TTS takeを共有(Bは同じtakeの減速前)。
- 開いた窓: Narrator Story clip sha256一致 16/16、dialogue clipがA/Bで別ファイル 18/18、原音へのatempo再適用=A版 18/18、再生順(sequence_order)同一=True、A再組立==Production wav sha=True。Voice・本文は同一results/segment_plan・同一TTS takeを共有(Bは同じtakeの減速前)。
- 詳細: `er026_output/family_z_std_dialogue_speed_ab_01/analysis.json`(全clip行・sha)、`<story>/build_report.json`。

## 6. 音声QA
- 走れメロス: B会話clipのProduction ASR 10件中 正規化完全一致 10件。通しB wav: sr=48000、peak=0.958、clip(>=0.999)=0、NaN=False、先頭無音0.947s/末尾無音0.731s(Aと同値)。headroom安全弁=未発動(A/B)。
- 開いた窓: B会話clipのProduction ASR 18件中 正規化完全一致 15件。通しB wav: sr=48000、peak=0.8997、clip(>=0.999)=0、NaN=False、先頭無音0.947s/末尾無音0.731s(Aと同値)。headroom安全弁=未発動(A/B)。
  - 差あり full_story_part2_c2 (類似度0.96): 期待=`"She expects them back and leaves it open until dark. Her husband wore a white waterproof coat over his shoulders. Her youngest brother sang, 'Oh, brother, why are you jumping?' He always sang that to annoy her."` / ASR(B)=`She expects them back and leaves it open until dark. Her husband wore a white waterproof coat over his shoulders. Her youngest brother sang, Oh, brother, why are you jumping? He always sang that to annoy her.`。A版事後ASR記録と同一テキスト(既存PASS_WITH_WARNINGまたは引用符/句読点のみ)で、B固有の新規欠陥ではない。
  - 差あり full_story_part2_c4 (類似度0.917): 期待=`"When it starts getting dark, I sometimes almost feel they really will—"` / ASR(B)=`When it starts getting dark, and sometimes almost feel they really will.`。A版事後ASR記録と同一テキスト(既存PASS_WITH_WARNINGまたは引用符/句読点のみ)で、B固有の新規欠陥ではない。
  - 差あり full_story_part3_c9 (類似度0.75): 期待=`"The spaniel frightened him,"` / ASR(B)=`The Spaniards frightened him.`。A版事後ASR記録と同一テキスト(既存PASS_WITH_WARNINGまたは引用符/句読点のみ)で、B固有の新規欠陥ではない。

## 7. 公開ページ検証
- URL: https://shimomura055.github.io/eigo-radio/user_test/family_z_std_dialogue_speed_ab_01/index.html / page HTTP 200 / audio 60本中 再生OK 60本(all_ok=True)。証跡=`public_play_verify_01.json`。

## 8. Production無変更の証拠
- `git diff --name-only 2f8b75126 HEAD`(Trial着手前HEAD→現HEAD)を保護対象(`user_test/family_z_melos_02`・`family_z_open_window_01`・`family_z_melos_jre_01`・`er026_output/family_z_production_e2e_01`・`er006_output/master_audio_store_01`・`er063_family_z_audio_01.py`・`er003_v1_n3_01_tts_generate.py`・`er008_a2_postprocess_slowdown_01.py`)に限定して実行: 0件。
- 元run a2配下・公開ページのファイルで、Trial着手(08:45 JST)以降に更新されたものは0件(find -newermt)。Master Audio Store manifestの未commit差分は08:17更新で、本Trial着手前の別作業によるもの(本Trialは書込まず)。
- Trial生成物は全て`er026_output/family_z_std_dialogue_speed_ab_01/`と新規`user_test/family_z_std_dialogue_speed_ab_01/`のみ。wavはpushせずmp3(lameenc 128kbps)のみ公開。
- 留意: 本作業のcommitは共有indexの競合で、別agent(ASR-HOMOPHONE 委任_04)のcommit 216ab62b0に本Trialのファイルが同梱された(内容は本Trialの新規ファイルのみ、他の既存ファイルは不変)。

## 9. 採用した場合の反映手順と費用見込み(参考、未実施)
- 手順案: `apply_a2_slowdown_postprocess`のdialogue clipだけ減速をskip(Std限定のProduction仕様変更=ユーザー承認後のflag/新コード経路)、既存2作品はB版assembled wav(+公開ページmp3)でproduction runのa2/assemblyと公開ページを差替え。再生成は不要(原音再利用)。
- 費用: 既存2作品の差替えはTTS 0円(ローカル組立+mp3化のみ)。今後の新規Z作品は生成工程でskipするだけで追加費用なし。新規作品のASR再検証は減速後ASR再検証が不要になる分むしろ微減。
