# ANOMALY_RECHECK_03(委任_03 §4、無料ローカル解析のみ・API不使用)

検知器: `er057_audio_anomaly_detect_trial_01.py`(委任_01C、閾値・アルゴリズム不変)。実行: `er057_tone_trial_final_recheck_03.py`(生データ `anomaly_recheck_03.json`、local faster-whisper small の語タイムスタンプ `whisper_words_03.json`)。追加の検知アルゴリズム開発・Validator変更なし。
**重要な前提**: 01Cの検知器はFOCUS1(Std part3 coffee)を元から検出できていない。したがって「新音声で検知器が出さない」ことは解消の証拠にならない。新音声は**別のTTS生成(別take)**であり、旧takeの異音(take固有のTTS不具合)が持ち越されない点だけが根拠。最終判断はユーザー試聴。

## 1. ユーザー確認結果(2026-10-12)の対応付けと処置
| ID | 位置(旧) | ユーザー判定 | 属するsegment | 区分 | 処置 |
|---|---|---|---|---|---|
| FOCUS1 | Std Full Story Part3 `coffee`(旧 seg 43.30〜43.56s / episode 265.45〜265.71s) | 異音あり | Std part3 | (a) 再生成segment | F5で再生成(別take)。新完成版では `coffee` = seg 37.58〜37.80s / episode **262.84〜263.06s**(Part3開始225.26s+37.58) |
| FOCUS2 | Adv Part3 `coffee`(対照) | なし | Adv part3 | (a) 再生成 | F5で再生成(参考確認のみ)。新 `coffee` = seg 37.98〜38.24s / episode 258.20〜258.46s |
| STD-02 | Std part2 40.94s(`raw beans`→robbings付近、click medium) | 異音あり | Std part2 | (a) 再生成 | F5で再生成。新 `raw`/`beans` = seg 40.78〜41.30s / episode 197.96〜198.48s |
| STD-20 | Std part2 41.07s(whisper `raw beans`→`robbings`) | 異音あり | Std part2 | (a) 再生成 | 同上 |
| STD-06 | Std part2 8.35s(`earlier.`直後の音量階段) | 軽微(許容) | Std part2 | (a) 再生成 | 許容。新 `earlier.` = seg 7.82〜8.32s |
| STD-24 | Std Topic intro 1.44s(`Coffee`、whisper確率0.458)、検出より少し前にも異音の可能性 | 異音あり | Std topic_intro(**再利用segment**) | (b) 切り分け→TTS由来 | 下記2 |
| 他Std候補 | - | なし | - | - | 処置なし |

## 2. STD-24(再利用segment)の切り分け
- **assembled側由来か?(否)**: Standard assembled(既存完成版)の Topic intro 区間(13.126〜18.526s)を、元segment wav(24kHz)に 既存gain(1.0091)を掛け、runnerと同じ `p9a.mono_24k_to_stereo_target`(24k→48kリサンプル)で変換した波形と比較すると、16サンプルの整列ずれのみで**最大差 3.05e-05(PCM16量子化誤差)**。完成版の当該区間は元segmentの線形変換にすぎず、加工・連結で生じた異音ではない(確定)。
- **元segment wavに存在するか(是)**: 元segment単体の `Coffee` 直前(1.31〜1.43秒)に**約120msの深い無音(−62〜−74dB、デジタルゼロ約165サンプル/20ms)**があり、1.44秒で−24dBへ**急に再開**する(これが検知器のSTD-24候補位置)。ユーザーの「検出位置より少し前にも異音」は、この深い無音+急な再開の手前(Coffee語頭〜1.3秒付近)と整合する(推定)。検知器は元segmentに候補を出さない(ratio等は閾値未満)。
- 判定: **TTS由来**。処置: 規定どおり **その役割の既存承認Style(変更なし)で1回だけ再生成**(Aoede、`brief, clear, engaging news topic introduction with natural emphasis on the topic; not dramatic.`、原稿 `Today's topic is Coffee Bean Prices Fall. Are Price Tags Still on a Journey?.` 変更なし、Primary ASR NORMALIZED_MATCH、費用約JPY0.13)。再生成数 1 segment(上限3以内)。
- **再生成後の所見(解消とは断定できない)**: 新takeにも `Coffee` 直前に**約80msの深い無音(1.38〜1.45s、−57〜−71dB)**があり、直後に再開する同型の特徴が残る(語頭 /k/ の閉鎖に相当する可能性。ただし−60dB未満まで落ちる点は旧takeと同様に深い)。検知器は新takeにも候補を出さない。whisper確率は旧0.458→新0.575(やや改善)。**聴感での確認が必要**。再生成は上限どおり1回のみのため、これ以上は行っていない。旧takeは試聴ページに「参考: 旧take」として併載。
- 再利用のまま残した他のsegment(topic_intro以外)は、ユーザー判定で異音指摘なし。

## 3. 新音声での語位置の指標比較(旧→新、`word_window_metrics`、local whisper語タイムスタンプ)
| 位置 | 旧(peak / max_d2_ratio / hf4k / 窓内最小10ms RMS(dB相対) / ゼロサンプル) | 新 |
|---|---|---|
| Std part3 `coffee`(FOCUS1) | 0.542 / 8.5 / 0.002 / −55.0 / 168 | 0.821 / 5.6 / 0.0014 / −55.2 / 49 |
| Adv part3 `coffee`(FOCUS2) | 0.610 / 6.1 / 0.0009 / −60.3 / 149 | 0.662 / 5.6 / 0.0017 / −62.4 / 113 |
| Std part2 `raw bean(s)`(STD-02/20) 旧robbing(s)転写 | 旧 `robbing` ratio 12.2・`robbings` ratio 17.0(whisper確率 0.807/0.703、min10ms −61.8dB) | 新 `raw`/`bean(s)` whisper確率 0.964〜0.994、`raw bean` 転写が正しい(旧の `raw bean→robbing` 誤転写は新takeで解消)、max_d2_ratio 5.9〜13.1 |
| Std part2 `earlier.`(STD-06) | 0.483 / 7.7 / 0.0024 / −53.5 / 91 | 0.520 / 8.2 / 0.002 / −59.2 / 103(同程度) |
| Std topic_intro `Coffee`(STD-24) | 0.400 / 5.8 / 0.1406 / −64.1 / 623 | 0.732 / 7.1 / 0.0506 / −61.4 / 157 |
解釈: 検知器の窓指標はいずれも旧・新で通常範囲内の同程度(FOCUS1は旧も範囲内で、検知器では異音を区別できない)。確実に言える変化は「`raw bean(s)` のlocal whisper転写が旧 `robbing(s)` から新で正しい `raw`/`bean(s)` になった」点(読みの安定化)と、「新takeは別生成で旧take固有の音は持ち越されない」点。FOCUS1・STD-24の異音が実際に消えたかは試聴確認が必要。

## 4. 新完成版全体の検知結果(閾値は01C同一)
- segment候補(新F5 6本+topic再生成): Std part1 0件 / part2 4件(click low×2, level_step low×2) / part3 3件(click **medium** 1: seg 18.77s `three` 付近 ratio 63.3 abs_d2 0.063 isolation 0.96, level_step low×2) / Adv part1 1件(low) / part2 2件(low) / part3 3件(low) / topic再生成 0件。
- **新規medium以上の候補: 1件のみ = Std part3 seg 18.77s(episode 225.26+18.77=244.03s)の `three costs had pushed` 付近のclick(medium)**。自動検知のみを根拠に再生成しない規則に従い、**再生成していない**(ユーザー試聴で確認を要する新規候補として報告。OPEN-278の追加材料)。完成版assembledのmono検知では同位置は出ていない(48k/resample後)。
- assembled(固定音源除く): Standard 11件(全てlow: click 1・level_step 7・spec_jump 3。うちKey Phrase 5(K2/M2/既存shell)内が4件)、Advanced 8件(全てlow: click 2・level_step 4・spec_jump 2)。clip(音割れ)は**両Levelとも0件**、abrupt dropout 0件、edge 0件(segment)。
- 既知位置の残存: 旧候補ID位置(STD-02/20/06/FOCUS1)は別takeのため位置が対応しない。語位置ベースでは上表のとおり(旧と同程度の通常範囲/転写が改善)。残存の断定はできない。
