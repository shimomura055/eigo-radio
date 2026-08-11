# ER-003-A2-AUDIO-AB-01 詳細レポート(A02完成候補 A/B比較)

**管理ID: ER-003-A2-AUDIO-AB-01**
**実施日: 2026-08-12**
**ステータス: `A/B READY FOR LISTENING`(A02のみ対象。A01/ADD03・B1/B2は未対応)**

比較試聴: [Artifactプレーヤー](https://claude.ai/code/artifact/f105ed9c-98cd-4058-b58b-716ec9fa1600)

## 1. 対象と方針

A02の完成候補について、以下2版を生成した。

- **A版**: 速度指定なし(既存承認済みの自然なTTS読み上げ方式)
- **B版**: 英語ニュースナレーション部分(Full Story Part1/2・Point One/Two・
  In One Line)のみ約135 WPM目安

両版とも以下を共通で反映済み:
- Key Phrase統合発音方式(意味+語末音素+phrase一体感、ER-003-CROSSLEVEL-AUDIO-04で試作)
- In One Line見出しの発話安定化(見出しテキストを実際に本文へ含める方式、同AUDIO-04で検証済み)
- Point One→Point Twoポーズ 0.8秒(旧0.5秒)
- In One Line→Outroポーズ 0.8秒(旧0.5秒)
- 「ポイント解説」後ポーズ 0.7秒(既存)
- Outroさらなる追加減衰(v2からさらに同一係数を1段、ER-003-CROSSLEVEL-AUDIO-03/04で試作)

## 2. 生成方式の内訳(A版とB版で何が同じで何が違うか)

| パーツ | A版 | B版 |
|---|---|---|
| Intro/Welcome/タイトル/Notification/Preview intro/Point explanation/Key phrases intro/Full story intro | 共通(既存資産) | 共通(既存資産) |
| Preview | 共通(ER-003-CROSSLEVEL-AUDIO-01承認版) | 共通 |
| Comment 1〜4 | 共通(Comment4はv2確定文言) | 共通 |
| Key Phrase 1(opt out)・2(covered apps)・3(urge to watch)・5(digital switch-off period) | 共通・新規生成(統合発音方式) | 共通 |
| Key Phrase 4(personalized feed) | 共通・**既存承認版を維持(後退させない)** | 共通 |
| Full Story Part 1 | 既存(a2_audio_01)、無変更 | 既存、**無変更**(元々134.91 WPMで目標付近のため) |
| Full Story Part 2 | 既存(a2_audio_01)、無変更 | 新規(約135 WPM目安) |
| Point One | 既存(a2_audio_01)、無変更 | 新規(約135 WPM目安) |
| Point Two | 既存(a2_audio_01)、無変更 | 新規(約135 WPM目安) |
| In One Line | **新規**(見出しテキスト追加、速度は自然) | **新規**(見出しテキスト追加、約135 WPM目安) |
| Outro | 共通(v2からさらに1段減衰) | 共通 |

## 3. Key Phrase統合発音方式の適用

A01/ADD03で試作した「意味grounding+語末音素保持+phrase一体感」の統合
instructionを、A02の5件へ適用した。

| Key Phrase | 対応 | 備考 |
|---|---|---|
| opt out | 新規生成(統合方式) | ASR: "Opt out."正確 |
| covered apps | 新規生成(統合方式) | ASR: "Covered apps."正確 |
| urge to watch | 新規生成(統合方式、要修正1回) | 初回ASRが"Urged to watch"と誤検出したため、tense保持instructionを追加し再生成。2回目で"Urge to watch."を確認 |
| personalized feed | **既存承認版を維持** | ER-003-CROSSLEVEL-AUDIO-01/02でユーザー試聴済みのtrial版をそのまま再利用(後退防止) |
| digital switch-off period | 新規生成(統合方式) | ASR: "Digital switch off period."正確 |

## 4. In One Line修正の適用結果

A版・B版とも、完成音声のASR全文で "In one line, the UK hopes..." と、
見出しから正しく発話されていることを確認した(過去のADD03で発生した
幻覚的な日本語風発話は再現していない)。

## 5. 速度制御の実施内容

**方法**: TTS自身の明示的な速度パラメータは存在しないため(既存監査で
確認済み)、prompt/style instructionによる速度誘導を採用した(post-
processing time-stretchは今回未使用)。

**校正過程(正直な記録)**:

| 試行 | 対象 | instruction強度 | 結果 |
|---|---|---|---|
| 予備調査 | Full Story Part1相当 | "noticeably slower, genuinely slower" | 1.612倍(狙いを大幅に超過、不採用) |
| 1回目 | Full Story Part2 | "just a little slower"(mild) | 0.986倍(ほぼ無効) |
| 1回目 | Full Story Part2 | "somewhat more slowly"(moderate) | 1.108倍 → **採用** |
| 2回目 | Full Story Part2 | さらに強い表現 | 1.034倍(**moderateより弱い結果、非単調**、不採用) |
| 1回目 | Point One | moderate | 1.212倍(狙い1.088倍に対し超過) |
| 2回目 | Point One | milder | 0.897倍(**baselineより速くなった、逆方向**、不採用) |
| 1回目 | Point Two | moderate | 1.199倍 → **採用**(狙い1.156倍に近い) |
| 1回目 | In One Line | moderate | 134.66 WPM → **採用**(目標にほぼ一致) |

最終的に、Full Story Part2・Point One・Point TwoはいずれもMODERATE
instructionの1回目の結果を採用した(2回目の調整はいずれも狙いから
遠ざかったため不採用)。**同一の指示文でもsegmentごとに反応が大きく
異なり、instructionを強めると必ずしも遅くなるとは限らない(非単調)
ことが分かった。** これは今後A2速度を正式仕様化する際の重要な制約
条件として記録する(prompt指示のみでの精密な速度制御には限界がある)。

## 6. WPM測定結果

| Segment | A(速度指定なし) | B(約135目安) |
|---|---:|---:|
| Full Story Part 1 | 134.91 | 134.91(無変更) |
| Full Story Part 2 | 167.62 | 151.25 |
| Point One | 146.82 | 121.09 |
| Point Two | 156.03 | 130.14 |
| In One Line | 167.51 | 134.66 |
| **単純平均** | **154.58** | **134.41** |

B版の5segment単純平均は134.41 WPMとほぼ目標(135)に一致しているが、
segmentごとのばらつきは121〜151と大きい。

## 7. 機械QA

- **ASR全文確認**: A版・B版とも en-US/ja-JP で完全なトランスクリプトを
  取得(タイムアウトによる部分結果なし)。内容の欠落・hallucinationは
  検出されなかった
- **content QA**: Key Phrase・Full Story・Points・In One Lineすべて
  ASRで内容一致を確認
- **clipping**: A版・B版とも検出されなかった(peak 0.86494、同一)
- **総尺**: A版 310.454秒、B版 329.314秒(+18.86秒。速度低下分+
  ポーズ変更分+0.6秒の合計)

## 8. Naturalness QA(軽量確認)

大規模自動化は実施せず、A02最終scriptを既存の6観点
(Grammar/Idiomaticity/News narration/Meaning preservation/A2
suitability/Spoken-first)で再確認した。ER-003-CROSSLEVEL-AUDIO-03で
指摘した1件("apps under the plan would not open at first"の意味曖昧性)
は未修正のまま(指示により今回本文は書き換えていない)。新たな問題は
確認されなかった。

## 9. 未反映・非対象(今回のスコープ外)

- A01・ADD03の完成音声再assemble
- B1/B2音声の変更
- A2速度の正式Decision化(A/B試聴後にユーザー判断)
- 大規模Naturalness QA自動化
- push

## 10. 作成・変更ファイル

- 新規: [er003_v1_a2_audio_ab_01_generate.py](er003_v1_a2_audio_ab_01_generate.py)
- 新規: `er003_output/a2_audio_ab_01/A02/`以下(key_phrase_components/, narration/, audit/、音声はgitignore対象外)
- 新規: 本レポート
- 更新: [OPEN_ITEMS.md](OPEN_ITEMS.md)
- 既存資産(a2_audio_01/a2_audio_02等)・共有凍結モジュールは無変更

## 11. Git / push

音声ファイルは`.gitignore`により追跡対象外。コード・監査JSON・レポート
のみをcommit済み。**pushは実行していません。**
