# TRIAL_RESULT_ADV_01: Family Z Advanced 会話clip 6%高速化(B)Trial結果(FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01 委任_02、2026-10-23)

Status: TRIAL_COMPLETE_USER_DECISION_REQUIRED(素材制作まで。試聴ページ統合・SSOT反映は後続委任)。Production未配線・生成(TTS)費用0円・追加API 0円。

## 1. 条件表
| 項目 | A:現行 | B:Trial |
|---|---|---|
| Advanced Narrator/Preview/Comment/KP/効果音 | 無変更 | 無変更(clip sha一致) |
| Advanced 会話(dialogue kind) | 速度変更なし | `atempo=1.06`(再生時間×1/1.06、ピッチ保持) |
| Voice・Prompt・本文・順序・無音間隔 | 現行 | 同一 |

## 2. 元run特定
- 『走れメロス』: 公開`user_test/family_z_melos_02/audio_advanced/Melos_b1b_full.mp3`=294.7795秒 = `er026_output/family_z_production_e2e_01/melos/run_e2e_06/b1b/assembly/Family_Z_melos_b1b.wav` 294.7795秒(一致)。委任_01(Standard)と同じ元run run_e2e_06。
- 『開いた窓』: 公開`user_test/family_z_open_window_01/audio_advanced/OpenWindow_b1b_full.mp3`=298.8243秒 = `the_open_window/run_e2e_01/b1b/assembly/...b1b.wav` 298.8243秒(一致)。
- A版再組立(`run_assembly(level=b1b, kp_third=explanation)`)のwav shaがProduction wavとsha一致(両作品true)。

## 3. 処理方式・再利用箇所
- 既存実装 `er008_a2_postprocess_slowdown_01.py:32 apply_a2_slowdown(src,dst,slowdown_pct)`(FFmpeg `atempo`、pitch-preserving WSOLA系、`-ar 24000 -ac 1 -s16`)を**無変更で再利用**。内部で`tempo=1/(1+pct/100)`なので`slowdown_pct=(1/1.06-1)*100=-5.660377`を渡し tempo=1.06 とした(Standard 6%減速と同一ライブラリ・同一方式、係数のみ逆向き)。新アルゴリズムなし。
- 組立は既存`er063_family_z_audio_01.py:1509 run_assembly`を無変更利用(無音間隔・順序はAと同一、sequence_order一致)。
- スクリプト: `er026_output/family_z_std_dialogue_speed_ab_01/adv/build_adv_01.py`(build)、`analyze_adv_01.py`(QA/WPM/mp3/manifest)。

## 4. QA結果
### 走れメロス
- 会話clip 11本: 長さ比B/A min 0.9442 max 0.9515(目標0.943±0.01=0.933〜0.953、全clip範囲内)。
- 非対象(Narrator/Preview/Comment/KP等)clip sha一致 38/38。順序一致=True、台詞テキストplan一致=True、Voice同一(会話clipは同一Voiceのまま処理のみ)。
- 通し: A 294.779秒 -> B 292.923秒。B通しwav peak 0.9799・clip 0・NaN False・RMS 0.0913(A rms 0.0913)。
- B会話clip単体: clip(>=0.999)最大 0サンプル、最大peak 0.6996、無音欠落なし(全clip RMS>0.06)。
- ASR(ローカルfaster-whisper small.en、API 0): 正規化完全一致 11/11、類似度<0.9: []。
### 開いた窓
- 会話clip 18本: 長さ比B/A min 0.9435 max 0.9519(目標0.943±0.01=0.933〜0.953、全clip範囲内)。
- 非対象(Narrator/Preview/Comment/KP等)clip sha一致 34/34。順序一致=True、台詞テキストplan一致=True、Voice同一(会話clipは同一Voiceのまま処理のみ)。
- 通し: A 298.824秒 -> B 293.701秒。B通しwav peak 0.8636・clip 0・NaN False・RMS 0.0822(A rms 0.0823)。
- B会話clip単体: clip(>=0.999)最大 0サンプル、最大peak 0.6997、無音欠落なし(全clip RMS>0.06)。
- ASR(ローカルfaster-whisper small.en、API 0): 正規化完全一致 15/18、類似度<0.9: ['full_story_part3_c4', 'full_story_part3_c9']。
- ASR不一致3件(open_window part2_c2 'sang'->'saying'、part3_c4 'was'->'is'、part3_c9 'spaniel'->'spanial')は、**同一ローカルASRでA版(現行)clipを判定しても同一の転写**(A=B)で、B(6%高速化)による劣化ではない(ローカルASRの癖/既存Production警告と同種)。Production既定のAzure ASRは未実行(見積: Azure約0.0463円/秒×B会話clip合計約122秒≒5.7円。5円超のため規定により未実行、必要ならFable判断)。

## 5. WPM表(語/分)
| 作品 | Narrator中央値(全/8語以上) | Narrator全clip加重 | Dialogue A中央値(全/8語以上) | Dialogue B中央値(全/8語以上) | Dialogue加重 A->B |
|---|---|---|---|---|---|
| 走れメロス | 137.4 / 149.3 | 151.4 | 109.0 / 146.3 | 114.6 / 154.8 | 125.8 -> 132.8 |
| 開いた窓 | 138.5 / 155.4 | 148.1 | 136.6 / 151.9 | 144.1 / 160.0 | 141.3 -> 149.4 |

(8語以上の会話clip数: メロス3、開いた窓7。メロスAdvは会話に短い台詞が多く全clip中央値は低め。語数は台詞テキストの空白区切り。)

### clip別(会話)
| 作品 | # | id | 話者 | Voice | 語数 | A秒 | B秒 | 比 | WPM A | WPM B |
|---|---|---|---|---|---|---|---|---|---|---|
| 走れメロス | 1 | full_story_part1_c2 | melos | Algieba | 13 | 5.331 | 5.038 | 0.9451 | 146.3 | 154.8 |
| 走れメロス | 2 | full_story_part1_c4 | melos | Algieba | 4 | 2.491 | 2.356 | 0.9459 | 96.3 | 101.9 |
| 走れメロス | 3 | full_story_part1_c6 | melos | Algieba | 13 | 4.761 | 4.499 | 0.945 | 163.8 | 173.4 |
| 走れメロス | 4 | full_story_part1_c8 | king | Charon | 12 | 5.741 | 5.432 | 0.9463 | 125.4 | 132.5 |
| 走れメロス | 5 | full_story_part1_c10 | friend | Erinome | 6 | 2.651 | 2.517 | 0.9494 | 135.8 | 143.0 |
| 走れメロス | 6 | full_story_part3_c2 | melos | Algieba | 4 | 2.491 | 2.355 | 0.9455 | 96.3 | 101.9 |
| 走れメロス | 7 | full_story_part3_c4 | melos | Algieba | 4 | 2.361 | 2.242 | 0.9498 | 101.7 | 107.0 |
| 走れメロス | 8 | full_story_part3_c6 | friend | Erinome | 4 | 2.651 | 2.514 | 0.9482 | 90.5 | 95.5 |
| 走れメロス | 9 | full_story_part3_c8 | king | Charon | 3 | 1.781 | 1.691 | 0.9496 | 101.1 | 106.4 |
| 走れメロス | 10 | full_story_part3_c10 | king | Charon | 3 | 1.651 | 1.571 | 0.9515 | 109.0 | 114.6 |
| 走れメロス | 11 | full_story_part3_c12 | king | Charon | 7 | 2.921 | 2.758 | 0.9442 | 143.8 | 152.3 |
| 開いた窓 | 1 | full_story_part1_c2 | vera | Zephyr | 6 | 2.371 | 2.242 | 0.9456 | 151.8 | 160.6 |
| 開いた窓 | 2 | full_story_part1_c4 | vera | Zephyr | 6 | 2.021 | 1.924 | 0.9518 | 178.1 | 187.2 |
| 開いた窓 | 3 | full_story_part1_c5 | framton | Algieba | 2 | 1.731 | 1.648 | 0.9519 | 69.3 | 72.8 |
| 開いた窓 | 4 | full_story_part1_c7 | vera | Zephyr | 8 | 3.161 | 3.0 | 0.9492 | 151.9 | 160.0 |
| 開いた窓 | 5 | full_story_part1_c8 | framton | Algieba | 3 | 1.931 | 1.837 | 0.9514 | 93.2 | 98.0 |
| 開いた窓 | 6 | full_story_part1_c10 | vera | Zephyr | 18 | 7.821 | 7.39 | 0.9449 | 138.1 | 146.1 |
| 開いた窓 | 7 | full_story_part1_c12 | vera | Zephyr | 31 | 14.041 | 13.261 | 0.9445 | 132.5 | 140.3 |
| 開いた窓 | 8 | full_story_part2_c2 | vera | Zephyr | 39 | 14.821 | 13.988 | 0.9438 | 157.9 | 167.3 |
| 開いた窓 | 9 | full_story_part2_c4 | vera | Zephyr | 12 | 5.411 | 5.115 | 0.9452 | 133.1 | 140.8 |
| 開いた窓 | 10 | full_story_part2_c6 | mrs_sappleton | Kore | 32 | 12.091 | 11.418 | 0.9443 | 158.8 | 168.2 |
| 開いた窓 | 11 | full_story_part2_c8 | mrs_sappleton | Kore | 5 | 2.811 | 2.652 | 0.9435 | 106.7 | 113.1 |
| 開いた窓 | 12 | full_story_part3_c2 | men | Schedar | 6 | 3.371 | 3.194 | 0.9476 | 106.8 | 112.7 |
| 開いた窓 | 13 | full_story_part3_c4 | men | Schedar | 5 | 2.221 | 2.109 | 0.9497 | 135.1 | 142.2 |
| 開いた窓 | 14 | full_story_part3_c6 | mrs_sappleton | Kore | 4 | 2.611 | 2.474 | 0.9475 | 91.9 | 97.0 |
| 開いた窓 | 15 | full_story_part3_c8 | mrs_sappleton | Kore | 6 | 2.531 | 2.4 | 0.9481 | 142.2 | 150.0 |
| 開いた窓 | 16 | full_story_part3_c9 | vera | Zephyr | 4 | 1.691 | 1.605 | 0.9489 | 141.9 | 149.6 |
| 開いた窓 | 17 | full_story_part3_c11 | vera | Zephyr | 30 | 11.171 | 10.553 | 0.9447 | 161.1 | 170.6 |
| 開いた窓 | 18 | full_story_part3_c13 | vera | Zephyr | 5 | 2.481 | 2.356 | 0.9495 | 120.9 | 127.4 |

## 6. Production無変更の証拠
- 全成果物は`er026_output/family_z_std_dialogue_speed_ab_01/adv/`配下のみ。元run(`melos/run_e2e_06`、`the_open_window/run_e2e_01`)・公開ページ(`user_test/family_z_melos_02`、`family_z_open_window_01`)・Master Audio Store・er063/er003/er008はコード/ファイルとも無変更(`git status`で当委任起因の差分0。元run配下に本委任開始後の更新ファイル0、`find -newer`)。
- 元b1b wav sha: メロス 14a5a58c...db79、開いた窓 f9a1dadb...1a64d(A再組立と一致)。Standard側成果物・ページ・SSOT・ACTIVE_TASKは未編集。user_test配下へ未出力。

## 7. 費用
TTS再生成0 clip(Advancedは既存clipをatempo処理のみ)、追加API呼出0、処理費用ローカル0円。

## 8. 成果物
- `er026_output/family_z_std_dialogue_speed_ab_01/adv/manifest_adv.json`(story/level/clip id/話者/Voice/テキスト/A・B mp3 path/秒/WPM/係数1.06/sha)、`analysis_adv.json`、`build_report.json`(各story dir)。
- mp3(lameenc 128kbps): `adv/<story>/mp3/full_A.mp3`・`full_B.mp3`、`dNN_A.mp3`・`dNN_B.mp3`(NNは会話通番)。wavはgitignore。
- 未解決: Production既定Azure ASRによるB clip判定は未実施(上記)。ページ統合時はStandard側と同ページで、mp3を`user_test/family_z_std_dialogue_speed_ab_01/`配下へコピーしsha/duration表示を使うこと。
