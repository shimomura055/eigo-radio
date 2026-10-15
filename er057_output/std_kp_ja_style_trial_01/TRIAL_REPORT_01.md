# STANDARD-KP-JA-TTS-STYLE-TRIAL-01 委任_01 TRIAL_REPORT_01 (2026-10-15)

## 0. 超サマリ
- 6 Style x 5 Phrase=30音声の比較素材と試聴ページを作成。新規TTSは25 call(P1〜P5 x 5)、失敗0・retry 0。実費見積は約JPY1.1(TTS約0.97+ASR約0.11、usage実測tokens換算、請求画面は未確認)。上限JPY50に対し大幅に内側。
- 試聴ページ: https://shimomura055.github.io/eigo-radio/user_test/coffee_std_kp_ja_style_trial_01/index.html (push後のHTTP確認結果はRESULT_PACKET_SKJT1.md参照)
- Sonnetは聴感評価をしていない(機械指標とASRのみ)。「すぐに」の感情表現が改善したかは、ユーザー試聴で判断してください。
- 機械指標だけで見ると、どのStyleも「すぐに」の抑揚幅はJ3(F0 std 3.22st)から大きくは変わらない(P5 2.48stとP3 2.67stがやや小さい、P4は3.63stでむしろ大きい)。指標は感情の有無を直接測れないため、結論は出せない。
- ASR上の注意: P2とP4の「生豆」が聞き違い(生麺/生め)、P1の「大喜びする」が「おお、喜びする?」と聞こえる。明瞭さの懸念として試聴時に確認推奨。P5は5件すべて一致。

## 1. Baseline設定とJ3本文一致確認
- 出典: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/a2/audit/tts_generation_results.json` の `key_phrases.{1-5}.japanese_meaning`。
- **ユーザー提示J3本文の sha256 = 実使用 style_prefix の sha256 = `ae68e3e6ac8e8dc29069666742ec04d64c823d4c7bdb6c0902797a2cc09fb69b`(65字、5件すべて同一、逐語一致)。J3 = 実使用。差分なし、J3新規生成は不要。**
- Baseline設定: model `gemini-3.8-flash-lite-tts` / voice `Aoede` / backend `speech_metadata_flash_lite` / language ja-JP / Standard同期。P1〜P5も同一(scriptがtts_generation_resultsから読み取り固定)。
- canonical text(5件、ユーザー表と一致): 大喜びする / 生豆 / すぐに / インタビューをもとにした / 時間がかかる(tts入力もreading_safety変更なしで同一)。
- 設定差: (a)Baselineは本番pipeline経由(trim後の前後margin約0.28秒保持。P1〜P5はTrial scriptのtrim margin 0.35秒=Production定数 NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS を使用)。最終長の差は先頭/末尾の無音数十msの範囲(機械指標の長さ比較にその程度の誤差を含む)。(b)Baselineは本番で後段のgain/assemble処理を受けるが、比較には`narration/meaning_N.wav`(trim後・TTS直後)を使用し、P1〜P5も同じ段階のwavなので音量処理の差は無い。(c)TTSの確率的ゆらぎ(同一入力でも毎回出力が違う)があり、各Style 1サンプルのみ=Style差とゆらぎの切り分けは未実施。

## 2. 生成結果
- 新規TTS 25 call(P1〜P5 x 5)、全てOK、retry 0。Master Store再利用/差分再生成の余地: 対象はStyleが異なるため全件新規が必須(再利用キャッシュ対象外。想定どおり25件)。
- 実費: prompt 85 tok / 出力 1,008 tok → 約JPY0.97(Standard単価 出力$6/M・入力$0.5/M、USD_JPY=160)。ASR(gpt-4o-mini-transcribe相当の既存`er006_asr_provider_routing_01`)25件の推定約JPY0.11。合計約JPY1.08。ローカル見積(dry-run)は約JPY1.43+ASR0.16で、委任文の旧推定(約JPY23、F5再生成の単価)より実測側が大幅に小さい(F5の約0.93円/callは長文segmentの単価で、2秒未満の短語では当てはまらない)。
- 並列: P1〜P3を同時3 process、P4〜P5を同時2 process。ASRと客観指標は並列。Batch不使用、`TTS_EXECUTION_MODE=STANDARD`。
- 証跡: `P1..P5/results.jsonl`(call単位)、`cost_actual.json`、`asr_results.jsonl`、`objective_metrics.json`、`evidence/`(gen_*.log、dry_run.json、shared_state_sha_*.json)。

## 3. 6x5比較表(参考値。長さ秒 / F0 std半音 / RMS dyn dB / ASR)
| Phrase | J3(Base) | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|---|
| 1 大喜びする | 1.72 / 4.16 / 17.9 / EXACT | 1.81 / 1.24 / 19.3 / PHONETIC(おお、喜びする?) | 1.79 / 4.31 / 18.1 / NORM | 1.76 / 2.05 / 19.5 / NORM | 1.68 / 2.11 / 15.8 / NORM | 1.71 / 2.13 / 19.7 / EXACT |
| 2 生豆 | 1.40 / 2.14 / 9.9 / EXACT | 1.33 / 1.94 / 12.0 / EXACT | 1.13 / 1.63 / 11.8 / **MISMATCH(生麺)** | 1.20 / 2.06 / 4.7 / EXACT | 1.05 / 1.37 / 9.9 / **MISMATCH(生め)** | 1.27 / 0.82 / 5.6 / EXACT |
| 3 すぐに | 1.21 / 3.22 / 20.6 / EXACT | 1.17 / 3.23 / 17.0 / EXACT | 1.38 / 2.92 / 22.2 / EXACT | 1.11 / 2.67 / 22.9 / EXACT | 1.16 / 3.63 / 18.8 / EXACT | 1.00 / 2.48 / 20.2 / EXACT |
| 4 インタビューをもとにした | 1.95 / 2.07 / 27.1 / EXACT | 2.24 / 4.04 / 15.5 / PHONETIC(基に) | 2.15 / 2.47 / 15.0 / EXACT | 2.13 / 2.72 / 19.1 / EXACT | 2.09 / 1.40 / 20.0 / EXACT | 2.07 / 3.64 / 13.1 / EXACT |
| 5 時間がかかる | 1.71 / 3.53 / 18.5 / EXACT | 1.79 / 1.49 / 21.3 / NORM | 1.79 / 2.17 / 13.8 / NORM | 1.48 / 1.30 / 12.1 / EXACT | 1.52 / 1.68 / 15.3 / NORM | 1.64 / 2.90 / 17.0 / NORM |

(J3のASRは本番時の既存ASR結果[全件EXACT_MATCH]。NORM=句点差のみの一致。F0は自己相関法の簡易推定でpyworld/librosa未導入のため粗い。)

Style別平均(分散)(5 Phrase、参考値の安定性指標):
| 指標 | J3 | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|---|
| 長さ(秒) | 1.60 (0.07) | 1.67 (0.14) | 1.65 (0.13) | 1.54 (0.14) | 1.50 (0.14) | 1.54 (0.14) |
| F0 std(st) | 3.02 (0.66) | 2.39 (1.15) | 2.70 (0.82) | 2.16 (0.27) | 2.04 (0.70) | 2.39 (0.87) |
| F0 range p10-p90(st) | 6.88 (5.74) | 6.03 (8.04) | 7.13 (6.67) | 5.45 (1.93) | 5.22 (4.81) | 5.37 (7.70) |
| RMS dyn(dB) | 18.8 (30.4) | 17.0 (10.4) | 16.2 (13.4) | 15.7 (42.4) | 16.0 (12.3) | 15.1 (29.1) |
| 無音比率 | 0.34 | 0.33 | 0.39 | 0.37 | 0.36 | 0.41 |
ASR EXACT/NORMALIZED一致: P1 3+1/5(PHONETIC 2、うち「大喜び」を「おお、喜び」と認識)、P2 4/5(MISMATCH 1)、P3 5/5、P4 4/5(MISMATCH 1)、P5 5/5。

## 4. 「すぐに」(right away)の客観指標の変化(参考値)
J3: 1.21秒 / F0 std 3.22st / RMS dyn 20.6dB。P1 1.17 / 3.23 / 17.0、P2 1.38 / 2.92 / 22.2、P3 1.11 / 2.67 / 22.9、P4 1.16 / 3.63 / 18.8、P5 1.00 / 2.48 / 20.2。
→ 抑揚幅(F0 std)がJ3より明確に小さいのはP5(-0.74st)とP3(-0.55st)。P1はほぼ同じ、P4は逆に大きい。ただし1サンプルかつ簡易F0推定のため、差が「感情表現の差」なのか「ゆらぎ」なのかは判別できない。

## 5. Sonnetの所見(聴感は未実施)
- 言えること: 全30音声が揃い、ASRで極端な欠落/繰り返しは無い(P2/P4「生豆」の誤認、P1「大喜びする」の音韻的ずれあり)。P3・P5は5件ともASR一致、P5はF0 stdが「すぐに」で最小。P3はF0 std/rangeのPhrase間ばらつきが最小(安定性の参考)。
- 言えないこと: 感情・演技の過不足、棒読み感、親しみやすさ、自然さは機械指標では判断できない。P5はRMS dyn低め・無音比率最高(0.41)で、淡々さが強く平板に聞こえる可能性があるが未確認。聴感評価の代替はできない。
- 1サンプル/Styleのため、TTSゆらぎで結果が変わる可能性がある(再生成での再現性確認は今回のスコープ外)。

## 6. 推奨候補案(Fable判断材料。自動評価でユーザー聴感を代替しない)
| Style | 感情抑制 | 自然さ | 明瞭さ | 安定性 | メモ |
|---|---|---|---|---|---|
| P1 最小修正 | 指標上は不明(「すぐに」はJ3と同程度) | 要試聴 | 「大喜びする」「基に」の揺れ | 分散大 | 現行への変更最小 |
| P2 意味伝達 | 「すぐに」F0 std小さめ(-0.3) | 要試聴 | 「生豆→生麺」誤認 | 中 | 明瞭さ懸念 |
| P3 ニュートラル | 「すぐに」-0.55 | 平板化の可能性 | ASR 5/5 | F0ばらつき最小 | 有力候補 |
| P4 会話調 | 「すぐに」は逆に+0.4 | 親しみやすさ狙い | 「生豆→生め」誤認 | 中 | 目的(感情抑制)と逆の可能性 |
| P5 簡潔・淡々 | 「すぐに」-0.74で最小 | 棒読み懸念(要試聴) | ASR 5/5 | 中 | 有力候補 |
- 機械指標とASRのみに基づく暫定の注目候補は **P3とP5**(次点P1: 現行に最も近い最小修正)。最終はユーザー試聴で「すぐに」の過剰感情が消え、かつ平板すぎないかを確認する必要がある。Production採用はしない。

## 7. Status分類案
`USER_DECISION_REQUIRED`(Fable最終判断)。根拠: 音声は生成できたが、目的(感情表現の適切さ・自然さ)の評価はユーザー聴感が必須で、機械指標だけでVALIDATED/REJECTEDにできない。VALIDATEDとはしない。APPROVED_FOR_PRODUCTIONには変更していない。

## 8. SSOT文案(本委任では編集しない)
- DECISION_LOG(Trial記録): 「2026-10-15 STANDARD-KP-JA-TTS-STYLE-TRIAL-01 委任_01: Std KP日本語意味5件のJ3(実使用=ユーザー提示本文、sha ae68e3e6)に対しP1〜P5を新規25 callで比較Trial(Aoede/gemini-3.8-flash-lite-tts/speech_metadata_flash_lite同一、実費約JPY1.1)。試聴ページ user_test/coffee_std_kp_ja_style_trial_01。機械指標・ASR上はP3/P5が注目候補(P2/P4は「生豆」ASR誤認)。聴感評価はユーザー試聴待ち。Status USER_DECISION_REQUIRED。Production/正式J3/他segment無変更。」
- OPEN_ITEMS(新規): 「Std KP日本語意味Style候補(P1〜P5)ユーザー試聴待ち。採否・追加Trial(1サンプルゆらぎ確認、Style組合せ)はユーザー判断。USER_DECISION_REQUIRED」
- REPORT_LEDGER行: 「SKJT-1 委任_01 Std KP日本語意味 6 Style x 5 Phrase Trial、25 call、実費約JPY1.1、Status USER_DECISION_REQUIRED、TRIAL_REPORT_01.md」

## 9. 共有state不変の証明
- `evidence/shared_state_sha_before.json` / `_after.json`(35ファイル)を比較。**34ファイル不変、`er011_output/attempt_history.jsonl`のみ変化**。末尾追記は`results_path=er019_output/.../kgcpw_evidence_01/E5_cli_x_a2/...`、タイムスタンプ16:13:20(並行中のKGCPW 委任_03のE5 runによる書込)で、本Trialのscriptは当該ファイルを参照・書込しない(grep済み: 本scriptは出力先をer057_output/std_kp_ja_style_trial_01と user_test/coffee_std_kp_ja_style_trial_01のみに限定、Production関数は`flw.make_speech_metadata_call_fn`相当のTTS呼出を直接実行)。厳密には「本Trialが書いていない」ことを書込主体の記録(results_path)から推定したもの。
- Coffee完成版wav/run dirは読み取りのみ(J3は読み込んでmp3化、原本は変更なし)。

## 10. 確認できなかった事項
聴感評価(全項目)/ TTSゆらぎ(同一Styleの複数サンプル)/ F0の精密測定(pyworld/librosa未導入)/ 請求画面上の実費 / `attempt_history.jsonl`変化がKGCPW由来であることの第三者検証(results_pathと時刻からの推定)。
