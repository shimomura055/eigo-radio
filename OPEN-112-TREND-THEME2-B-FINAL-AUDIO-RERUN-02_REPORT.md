# OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-02

管理ID: OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-02

種別: Theme 2(若者の旅行、B条件)A2/B1完成音声の「追加1回のみ」再実行
(ユーザー承認: 2026-09-06「A/BのProduction wiring完了後、Theme 2の
A2/B1完成音声を1回だけ再実行してよい」+`KEYPHRASE-JA-GLOSS-NO-
PARENTHETICAL-PROD-WIRING-01`完了後の追加1回)。

到達Status: **`USER_FINAL_AUDIO_REVIEW_REQUIRED`**。A2・B1とも完成音声
生成に成功した(RERUN-01は選定段でSTOPし完成音声0件だったが、本タスクは
両レベルとも最後まで到達した)。

## 0. 結論(先出し)

RERUN-01が"median"型の括弧併記gloss(「（中央値）」)で構造Validatorに
拒否されてKey Phrase選定段でSTOPした問題は、直前タスク
(`KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01`、選定Promptへ
「括弧内の別訳・専門用語・補足を併記しない」1句を追加配線)により解消
した。本タスクはRERUN-01と完全に同一のロジック(本文/Preview/Comment
はTrial-13から再利用、Key Phraseのみ最新Production経路[`sc.run_key_
phrases`]で選定→canonicalization→英語Component→日本語gloss→ASR
検証→Assembly)を再実行し、A2・B1とも最後まで到達、完成音声を得た。

## 1. 実装

`er011_open112_trend_theme2_b_final_audio_rerun_02.py`(root新規)を
RERUN-01(`er011_open112_trend_theme2_b_final_audio_rerun_01.py`)から
複製した。コード差分は識別子のみ(`THEME_ID`/`OUT_DIR`/`article_id`/
ログprefix)で、本文reuseロジック(`prepare_level_inputs`/`reuse_non_
kp_segments`/`_expected_canonical_text`)・Key Phrase選定(`sc.run_key_
phrases`、Production関数を無変更で直接呼ぶ)・Key Phrase音声生成
(`generate_kp_audio_b1`/`generate_kp_audio_a2`、Production関数
`shared_narration.ensure_key_phrase_english_component`/`tts_gen.
generate_charon_japanese_with_reading_safety`/`generate_a2_japanese_
with_reading_safety`を直接呼ぶ)・Assembly(`asm.stage_assemble_b1`/
`stage_assemble_a2`、Production関数)は完全に同一ロジック。
TTS_EXECUTION_MODE=STANDARD(Standard同期)。

## 2. 実行結果(両レベルとも`status=DONE`)

```
b1b: kp_selection_status=KEY_WORDS_STRUCTURE_PASS
     kp_canonicalization_status=CANONICALIZATION_PASS
     kp_redundancy_status=REDUNDANCY_PASS
     assemble_result.status=OK

a2:  kp_selection_status=KEY_WORDS_STRUCTURE_PASS
     kp_canonicalization_status=CANONICALIZATION_REVIEW_REQUIRED
     kp_redundancy_status=REDUNDANCY_PASS
     assemble_result.status=OK
```

`CANONICALIZATION_REVIEW_REQUIRED`(A2)は`run_key_phrases()`の既存設計
上の継続許容ステータス(STOPではない)であり、実際にAssembly到達・完成
音声生成まで問題なく進んだ。両レベルともKey Phrase選定候補5件のglossに
括弧は一切含まれなかった(下記4節)。Gate/Human Review Lockでの停止は
発生しなかった(0件)。

## 3. 総尺・clipping・安全弁

| Level | duration | peak(適用後) | clipping | headroom safety valve |
|---|---|---|---|---|
| B1 | 341.975秒(5:42) | 0.80806 | なし | 未適用(peak適用前から0.98閾値未満) |
| A2 | 375.226秒(6:15) | 0.98000 | なし | **適用**(適用前peak=1.0350189[Point One起因]→scalar 0.94684262で0.98へ抑制) |

A2は`ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-PRODUCTION-WIRING-01`
(`PRODUCTION_WIRED`)のheadroom safety valveが実際に発火し、Trial-13で
発生していたAssembly最終段クリッピング(`OPEN-112-TREND-THEME2-B-A2-
PEAK-MEASUREMENT-16_REPORT.md`参照)を今回は未然に防止したことを実測で
確認した(サンプルフォーマット: 48000Hz・2ch、Python `wave`モジュールで
実ファイルのnframes/framerateから独立に尺を再計算し、`assemble_result`
記録値と一致することを確認済み)。両レベルともclipping検知は`false`。

## 4. Key Phrase表(英語/表示用/TTS用/ASR/分類/attempt/新ラベル発火)

**B1**:

| rank | 英語Key Phrase | 表示用gloss | TTS用テキスト | 英語ASR | 日本語ASR | attempt(en/ja) | 英語Component再利用 |
|---|---|---|---|---|---|---|---|
| 1 | self-directed travel | 自分で進め方を決める旅行 | 自分で進め方を決める旅行 | Self-directed travel | 自分で進め方を決める旅行 | 0(再利用)/1 | Master Audio Store cache hit |
| 2 | two different speeds | 二つの異なるペースで進んでいること | (同左) | two different speeds | 二つの異なるペースで進んでいること。 | 0(再利用)/1 | cache hit |
| 3 | too broad a label | ひとまとめにしすぎた呼び方 | (同左) | Too broad a label. | ひとまとめにしすぎた呼び方。 | 1(新規)/1 | 新規生成 |
| 4 | interest-led plans | 興味を中心にした旅行プラン | (同左) | Interest-led plans. | 興味を中心にした旅行プラン | 0(再利用)/1 | cache hit |
| 5 | leading travel arrangement | 最も多い旅行の形 | (同左) | Leading travel arrangement. | 最も多い旅行の形。 | 1(新規)/1 | 新規生成 |

**A2**:

| rank | 英語Key Phrase | 表示用gloss | TTS用テキスト | 英語ASR | 日本語ASR | attempt(en/ja) | 英語Component再利用 |
|---|---|---|---|---|---|---|---|
| 1 | at one's own pace | 自分のペースで | (同左) | At one's own pace. | 自分のペースで | 0(再利用)/1 | cache hit |
| 2 | a full month off | まる一か月の休み | (同左) | A full month off. | 丸1か月の休み。 | 1(新規)/2(attempt1 TRUE_CONTENT_MISMATCH「丸一ヶ月」→attempt2 PHONETIC_MATCH「丸1か月」で確定) | 新規生成 |
| 3 | hobby-focused travel | 趣味を中心にした旅行 | (同左) | Hobby-Focused Travel | 趣味を中心にした旅行。 | 1(新規)/1 | 新規生成 |
| 4 | median | 真ん中の値 | (同左) | Median | 真ん中の値。 | 0(再利用)/1 | cache hit |
| 5 | the new normal | 新しい当たり前 | (同左) | The new normal. | 新しい当たり前 | 1(新規)/1 | 新規生成 |

分類(`audio_classification`)は全件`PHONETIC_MATCH`(A2 rank2 attempt1
のみ`TRUE_CONTENT_MISMATCH`で1回retry)。全10件(A2/B1×5)とも
`asr_verified=true`で最終的にPASS。表示用gloss=TTS用テキストは全件
一致(`tts_text_fallback_derived=false`、フォールバック未使用)。

**新ラベル発火**: なし。英語Key PhraseのASR prompt/非ラテン文字Cascade
(`asr_prompt_applied`/`non_latin_cascade_enabled`/`non_latin_cascade_
invoked`)はいずれも該当箇所で`false`/`null`のまま(この機構は英語
ASRのfalse rejection対策であり、今回いずれの英語Key Phraseも初回で
正しくASR一致したため発火条件[非ラテン文字優勢の不一致]に該当しな
かった)。"median"のような括弧併記も今回は0件(4件のTTS用テキストが
確認できた10件すべてに全角/半角括弧なし)。

## 5. 再利用/新規segment数

- 本文/Preview/Comment: B1 13 segment・A2 14 segment、いずれもTrial-13
  から100%再利用(review_lock RESOLVED+canonical text sha256一致検証
  済み、再TTSなし)。
- Key Phrase英語Component: B1 3/5(rank1,2,4)・A2 2/5(rank1,4)が
  Master Audio Store cache hitで再利用(過去の同一canonical_text/voice/
  tts_model_id/style_instruction_versionのProduction資産をそのまま
  再利用、新規TTS/ASR呼び出しなし)。残り(B1 rank3,5・A2 rank2,3,5)は
  新規生成(各1attempt、初回でPASS)。
- Key Phrase日本語gloss: 全10件(A2/B1×5)が新規生成(gloss自体は選定の
  たびに変わりうるため再利用対象外)。B1は全件1attemptで確定、A2は
  rank2のみ2attempt(数字表記の読みゆれによる既存TRUE_CONTENT_MISMATCH
  retry、本タスクの変更とは無関係の既存挙動)。

## 6. Cross-level仕様準拠

Assembly自体はProduction関数`asm.stage_assemble_b1`/`stage_assemble_
a2`(無変更)をそのまま呼び出しており、ポーズ・trim margin・headroom
safety valve等の既存Cross-level仕様(`CURRENT_SPEC.md`「Cross-level
仕様」節)はいずれもこの関数内部で適用済み(本タスクでの個別調整・
override・バイパスは一切行っていない)。A2側のheadroom safety valve
発火(3節)もこの既存仕様どおりの自動挙動。

## 7. player.html

`er011_output/open112_trend_theme2_b_final_audio_rerun_02/player.html`
(file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_
b_final_audio_rerun_02/player.html)。B1・A2の完成音声(`assembled/*.wav`、
相対パス参照)をそれぞれ`<audio controls>`で試聴できる。

## 8. Gate/Human Review Lock停止の有無

**発生なし**。両レベルとも選定・canonicalization・Redundancy QA・
Key Phrase音声(英語Component/日本語gloss)・Assemblyのすべてのステージ
を1回のパスで完走した。前タスク(RERUN-01)がSTOPした原因
(`KEY_WORDS_STRUCTURE_INVALID`、"median"の括弧併記)は、`KEYPHRASE-JA-
GLOSS-NO-PARENTHETICAL-PROD-WIRING-01`の選定Prompt配線により再発しな
かった(A2 rank4で再び"median"が選定されたが、今回のglossは「真ん中の
値」で括弧なし)。

## 9. cost

```
選定+canonicalization+Redundancy QA(gpt-5.6-luna、6 call、Standard):
  input 13,975 tok × $0.20/1M + output 19,258 tok × $1.20/1M ≈ $0.02590
Key Phrase日本語gloss TTS(gemini-3.1-flash-tts-preview、11 call、Standard):
  input 4,951 tok × $1.00/1M + output 911 tok × $20.00/1M ≈ $0.02317
Key Phrase英語Component TTS(gemini-2.5-pro-preview-tts、5 call、Standard):
  input 1,587 tok × $1.00/1M + output 259 tok × $20.00/1M ≈ $0.00677
ASR(gpt-4o-mini-transcribe、16 call):
  input 586 tok × $1.25/1M + output 149 tok × $5.00/1M ≈ $0.00148
合計 ≈ $0.0573(約¥9.2、$1=¥160換算)
```

`KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01`のRuntime evidence
実費($0.0329、約¥5.3)と合わせ、本タスク全体の実費は約$0.0902
(約¥14.4)。Theme 2累計(既存記録約¥137+本タスク約¥14.4)≈約¥151で、
上限¥1,000に対し引き続き余裕あり。計測は`er005_output/cost_baseline_
01/pricing_snapshot.json`公式単価×`raw_usage_log.jsonl`実測usage。

## 10. Production変更なしの確認

`er003_v1_n3_01_scaffold_generate.py`/`er003_key_words_production.py`/
`er003_key_words_min_unit.py`/`er003_key_words_canonicalization.py`/
`er003_v1_n3_01_tts_generate.py`/`er006_audio_cost_pilot_02_shared_
narration.py`/`er003_v1_n3_01_assemble.py`はいずれも無変更。本タスクで
新規作成したのは`er011_open112_trend_theme2_b_final_audio_rerun_02.py`
(RERUN-01の複製、識別子のみ変更)と出力artifactのみ。

## 11. 今回実施しなかったこと

override・fallback追加・上限緩和・手動unblock・再選定・場当たり修正
(D4、いずれも発生していないため不要だった)。承認された「追加1回」を
使い切ったため、本タスクの結果に関わらず、これ以上のTheme 2完成音声
再実行(3回目)は行わない。

## 12. 証跡

- `er011_open112_trend_theme2_b_final_audio_rerun_02.py`
- `er011_output/open112_trend_theme2_b_final_audio_rerun_02/rerun02_summary.json`
- `er011_output/open112_trend_theme2_b_final_audio_rerun_02/{b1b,a2}/audit/tts_generation_results.json`
- `er011_output/open112_trend_theme2_b_final_audio_rerun_02/{b1b,a2}/audit/run_key_phrases_result_summary.json`
- `er011_output/open112_trend_theme2_b_final_audio_rerun_02/{b1b,a2}/key_phrases/keywords_canonicalized.json`
- `er011_output/open112_trend_theme2_b_final_audio_rerun_02/{b1b,a2}/assembled/*.wav`
- `er011_output/open112_trend_theme2_b_final_audio_rerun_02/raw_usage_log.jsonl`
- `er011_output/open112_trend_theme2_b_final_audio_rerun_02/player.html`
- 前タスク(発見元・STOP経緯): `OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-01_REPORT.md`
- 対策配線元: `KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01_REPORT.md`

## 13. ユーザー最終試聴用

`file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_b_final_audio_rerun_02/player.html`
を開き、B1(5:42)・A2(6:15、headroom safety valve適用済み)を試聴して
ください。Status: `USER_FINAL_AUDIO_REVIEW_REQUIRED`(ユーザー最終試聴
待ち。`APPROVED_FOR_PRODUCTION`・Production採用可否の判定は本タスクの
範囲外)。
