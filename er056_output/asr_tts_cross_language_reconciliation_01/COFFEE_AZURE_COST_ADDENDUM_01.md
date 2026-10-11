# COFFEE_AZURE_COST_ADDENDUM_01 (ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_02、2026-10-11)

目的: 英語側所見F-7「Coffee Phase 2の累計費用 JPY 20.73 にAzure音声認識(STT)の費用が入っていない」の検証と補正値の算出。
方法: read-only。Coffee worktree(`eigo-radio-tone`)の`raw_usage_log.jsonl`と費用集計関数を**読んだ/実行した**だけで、Coffee側ファイルは一切編集していない。有料API 0円。
使用スクリプト: 一時スクリプト(scratchpad、リポジトリ外)。集計関数は worktree の `er019_family_x_audio_production_runner_01.compute_cost_jpy_so_far` をそのまま import して実行(読取のみ)。

## 1. 結論(確定)
- **所見は正しい**。Azure STTは累計 JPY 20.73 に**1円も入っていない**。Azure費用を補正すると Phase 2 累計は **約 JPY 31.03**(上限50円の約62%。登録単価=Azure $1/音声時間、USD/JPY=160)。
- 補正しても上限50円は超えていない。ただし**Budget Guard(予算上限の自動停止装置)もAzureを数えていなかった**ため、Azure呼出が多い run では実費が上限を超えても止まらない構造(下記4節)。

## 2. 根拠(確定)
| 項目 | 値 | 根拠 |
|---|---|---|
| Azure呼出回数 | **8回**(全て `get_full_text_via_azure_stt_with_phrase_list`、en-US、全て success) | `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01/raw_usage_log.jsonl`(worktree)164行中`provider=azure`が8行 |
| 内訳 | `full_story_part2` 4回(48.75+48.75+47.72+52.60=**197.82秒**)、`comment_2`(Advanced)4回(7.92+8.47+9.07+8.55=**34.01秒**) | 同上、`audio_duration_submitted_seconds`(LOCAL_WAV_HEADER_EXACT=送信WAVの実長) |
| 合計音声秒 | **231.83秒** | 同上 |
| 単価 | $1.00 / 音声1時間(Speech to Text real-time Standard、japanwest) | `er005_output/cost_baseline_01/pricing_snapshot.json` provider=azure、meter=audio_hour、price=1.0 |
| 為替 | USD/JPY=160 | worktree `er019_family_x_audio_production_runner_01.py` L1543 |
| Azure推定費用 | 231.83/3600 x $1 = **$0.0644 = JPY 10.30**(`full_story_part2` 8.79円、`comment_2` 1.51円)。呼出ごとに秒を切り上げる場合は 10.44円 | 計算(SCGの`est_cost_jpy`と同じ式=秒切上げ版が上限側) |
| 既存集計の挙動 | `compute_cost_jpy_so_far(raw_usage_log)` を実行 -> `{'openai': 3.1, 'gemini_batch': 8.64, 'openai_asr': 4.68, 'azure': 0.0}` 合計16.43円(Azure=0.0) | 同関数を実行して確認(今回)。コード上、`provider in ("gemini","openai","openai_asr")`のtoken単価計算か、レコードに`cost_usd`がある場合のみ加算。Azureレコードは`cost_usd`を持たず、条件に該当しないため**0円のまま** |

## 3. Phase 2 累計の補正
| 区分 | 公式報告(RUNTIME_EVIDENCE_01) | 補正後 |
|---|---|---|
| entertainment(Advanced/Standard/Risk Flagger) | 2.93 | 2.93 |
| audio(TTS 8.64 + OpenAI ASR 4.68 + Luna等 3.10) | 16.43 | 16.43 |
| **Azure STT(8回、231.83秒)** | **0(未計上)** | **+10.30**(上限側10.44) |
| 実fallback probe(Step 2。Azure呼出0回: 同probeの`raw_usage_log.jsonl`を確認) | 1.37 | 1.37 |
| **Phase 2 合計** | **20.73 / 50** | **約31.03 / 50(62.1%)**(上限側31.17) |

補足: RUNTIME_EVIDENCE_01の「ASR 69 call 4.68円(+azure-speech-stt補助8)」の4.68円は**OpenAIの69 callだけ**の金額(69 x約0.068円と一致)。括弧内のAzure 8は件数の注記のみで金額は入っていない。

## 4. 影響範囲と注意(一部は推測)
- **確定**: 同じ「Azureを数えない」集計パターン(`provider in ("gemini", "openai", "openai_asr")`)は main の11ファイルに複製されている(`er012_b_family_production_runner_01.py`、`er012_e_family_entertainment_two_level_runner_01.py`、`er019_family_x_audio_production_runner_01.py` ほか)。過去の費用報告(特に英語のcascade/forced Secondary、日本語SCGが走ったrun)にも同じ過少計上が**ある可能性が高い**(未集計。推測)。日本語SCGは自分で`est_cost_jpy`を`scg_info`へ記録しているが、run全体の費用集計には足されない。
- **推測**: Azureの実請求額は未確認。登録単価(S0/S1標準)での試算で、F0(無料枠5時間/月)の契約なら実費は0円になりうる(pricing_snapshotの注記)。契約tierは本調査では確認していない。
- **Azureが費用の主因になる**: 本segmentでは Azure 8.79円 > TTS 3.02 + OpenAI ASR 1.77 + LLM 0.37 の合計。英語の長い本文(約50秒)でAzureを呼ぶ設計は、日本語SCG(数秒の短文、約0.16円/回)より1回あたり約10倍高い。
- 是正は**提案のみ**(未実施): (a)集計関数にAzure(音声秒 x 単価)を加える、(b)今後の報告で「Azure別枠」と明記する。Production費用集計コードの変更に当たるため、Fable/ユーザー判断が必要。
