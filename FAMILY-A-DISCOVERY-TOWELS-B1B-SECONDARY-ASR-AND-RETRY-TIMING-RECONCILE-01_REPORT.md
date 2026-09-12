# FAMILY-A-DISCOVERY-TOWELS-B1B-SECONDARY-ASR-AND-RETRY-TIMING-RECONCILE-01

## 要点(5行)
1. Part A: 既存Secondary ASR Cascade・Connected Speech Equivalence Layerは、いずれも「対象外」判定で発火しなかった(バグ・配線漏れではない。has→hadは実在の単語差でありentity_like/homophone_candidate/音韻カテゴリのどれにも該当しない)。
2. Part A追加: take5音声へAzure Secondary ASR関数を単独適用(実費用¥1.8程度、事前見積内)した結果、SecondaryもPrimaryと同じく"had dried"と書き起こし、canonicalの"has"へは一致しなかった。Cascadeが発火してもこのattemptは救済されなかったと判断できる。
3. Part B: 既存2script再実行(冪等・API呼び出し0円)により、タオルTrial-11 B1B resume分を含む最新データ(retry-after-NGペア74件、種別B70件)を集計した。即時<150秒 PASS率52.8%(N=53) vs 非即時PASS率41.2%(N=17)、Fisher p=0.578(有意差なし)。
4. 事前定義の「傾向十分」基準(各bin N≥20・差≥20pt・介入なし長間隔≥5件)は未達(最小bin N=3、差11.6pt)。**Part Bの結論は「仕様採用しない、継続観測」**。
5. 今回のfull_story_part1「2022 survey文欠落」解消(take1-3→take4-6)は、時間経過そのものではなく人的介入(Human Review Lock解除後の`approve_regenerate`明示的regen)に分類される。時間効果と介入効果はこのデータだけでは分離できない(全resumeペアがmanual_regenerate_beyond_loop_capに分類され、時間だけを空けた自然発生の同一条件対照が無い)。

---

## Part A: Secondary ASR Cascade事実確認

### 対象事実(監査ログ根拠)
- ファイル: `er011_output/discovery_generalization_towels_trial_11/b1b/audit/human_review_resume_04_results.json`
- take5(resume round attempt2、ファイル名`full_story_part1_attempt5_englishstyleprefixwidemargin.wav`)のASR結果:
  - canonical: `...or after the laundry **has** dried, and these stages can overlap.`
  - ASR: `...or after the laundry **had** dried. And these stages can overlap.`
  - `audio_classification: "TRUE_CONTENT_MISMATCH"`
- `review_lock_state.json`: `full_story_part1`は現在も`state: "HUMAN_REVIEW_REQUIRED"`のまま(未解決)。

### (1) 発火有無・コード根拠
呼び出し元は`er011_discovery_generalization_towels_trial_11_audio_04_b1b_fullstory_resume_human_review.py`から`er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin(..., enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True)`。内部で`er006_secondary_asr_01.py::evaluate_attempt_with_cascade(cascade_enabled=True[FEATURE_FLAG_SECONDARY_ASR_ENABLED既定ON], enable_connected_speech_equivalence_layer=True)`を呼ぶ(この呼び出し元は`enable_non_latin_cascade`を渡していない=既定False、Key Phrase専用機構のため対象外は仕様通り)。

`evaluate_attempt_with_cascade_detail()`内の実際の分岐(オフライン・API呼び出しなしで実コードを直接実行し確認、`er006_preprod_hardening_01_validation.classify_asr_match()`/`er006_secondary_asr_01.is_entity_like_mismatch()`/`is_homophone_candidate_mismatch()`/`er011_connected_speech_equivalence_layer_production_01.classify_connected_speech_equivalence()`を実データで直接呼び出し):

- `classify_asr_match(canonical, asr_text)` → `content_word_diffs = [{"canonical": "has", "asr": "had", "entity_like": False, "homophone_candidate": False}]`(唯一の内容語差)。
- `is_entity_like_mismatch = False`、`is_homophone_candidate_mismatch = False` → `cascade_eligible = False`。既存コード(`er006_secondary_asr_01.py` line ~612)は`if verified or not cascade_enabled or not cascade_eligible: return result`で**即座にreturn**し、Secondary ASR・Primary#2・Human Reviewログ追記のいずれも実行しない。
- Connected Speech Equivalence Layer(OPEN-122、同じ呼び出しで`enable_connected_speech_equivalence_layer=True`)は上記gateより手前で評価される別条件(`cls.classification=="TRUE_CONTENT_MISMATCH" and cls.protected.passed`)を満たすため、無料の事前チェック(`_connected_speech_equivalence_layer_attempt`内の`cheap_check`)だけは実行される。結果は`layer_judgment: "NOT_A_PHONEME_PREFIX_DROP"`(`NEVER_ELIGIBLE_JUDGMENTS`に該当)で、追加ASR呼び出し(Secondary Azure・local faster-whisper)は一切発生せずNoneを返す。

**結論**: 両cascadeとも「発火しなかった」。原因は条件不一致でも配線漏れでもなく、**設計通りの対象外**(has→hadは固有名詞らしき語でもhomophoneでも既知の音韻連結パターンでもない、正真正銘の単語置換のため)。

### (2) 追加Trial(既存cascade関数の単独適用)
- 見積: 過去実績(`ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01_report.md`、Azure Secondary ASR 8コール258.8秒→¥11.50、単価約¥0.0444/秒)から、take5音声(40.731秒)の単独Azure Secondary ASR呼び出しは概算¥1.8程度と見積り、¥30以内のため実施。
- 実施: `er006_secondary_asr_01.get_full_text_via_azure_stt_with_phrase_list()`(既存Production関数、無変更)をtake5音声へ直接1回適用(Human Review承認代行やstate変更は一切行わず、読み取り専用の診断呼び出しのみ)。
- 実測コスト: Azure STT 1コール、40.731秒送信(ログ: `er011_output/discovery_generalization_towels_trial_11/b1b/audit/secondary_asr_manual_diagnostic_take5_cost_log.jsonl`)。
- 結果: Secondary ASR書き起こし = `...or after the laundry **had** dried, and these stages can overlap...`(Primary ASRと同じく"had"、canonicalの"has"とは不一致)。

### Part A 結論(指定書式)
| 項目 | 内容 |
|---|---|
| Family/現象 | Discovery B1B(タオルTrial-11)`full_story_part1`、take5でcanonical "has dried"がASRで"had dried"(TRUE_CONTENT_MISMATCH) |
| 既存対策 | Secondary ASR Cascade(entity_like/homophone_candidate限定)、Connected Speech Equivalence Layer(音韻カテゴリA〜G限定、OPEN-122) |
| 今回なぜ効かなかったか | 両方とも「対象外」(diffが固有名詞様でもhomophoneでも既知音韻連結パターンでもない、実在の単語置換のため)。バグ・配線漏れではなく設計通り |
| 追加Trial有無 | あり(既存Azure Secondary ASR関数のtake5単独適用、実費用¥1.8程度、¥30以内で実施) |
| 結果 | Secondary ASRもPrimaryと同じ"had"を書き起こし、canonical"has"とは不一致のまま。Cascadeが発火していても救済されなかった可能性が高い |
| Production判断が必要か | 今回は不要(現状仕様通りの正しい動作、segmentはHuman Review Required維持が適切)。「has/had等の実在単語置換もSecondary ASR corroborationの対象に広げるか」は新規仕様候補のため、実装はせず報告のみに留める(USER_DECISION_REQUIREDとして提起可能、今回未提起・未実装) |

---

## Part B: TTS retry timing再集計

### 実行
- `er011_tts_retry_timing_monitor_01.py`を再実行(冪等・API呼び出し0件): attempt files scanned=483、observations=483 → `er011_output/tts_retry_timing_monitor_01/observations.jsonl`
- `er011_tts_retry_cooldown_monitor_01.py`を再実行(冪等・API呼び出し0件、script本体は無改変): pairs=74 → `er011_output/tts_retry_cooldown_analysis_01/`(summary.json/summary.md/cooldown_pairs.jsonlを上書き)
- タオルTrial-11 B1B `full_story_part1`のresume分(take4対take1-3の間隔2716秒[中bin]、take5/take6の即時retry)が新規に`cooldown_pairs.jsonl`へ反映されていることを確認済み(全件NG、後述)。

### 分けて集計した結果(既存script出力そのまま、詳細summary.md参照)
1. **即時retry(<150秒)PASS率**: N=53, PASS 28件, 52.83%
2. **非即時retry(bin別)PASS率**: 短時間(150秒〜30分) N=10, 40.0% / 中(30分〜6時間) N=4, 25.0% / 長(6時間以上) N=3, 66.67%
3. **連続NG回数別・次attempt PASS率**: 1回後(即時) N=38, 68.42% / 2回後(即時) N=11, 18.18% / 3回以上後(即時) N=4, 0% / 3回以上後(長間隔) N=3, 66.67%(詳細は表2参照、binが細分化されるためN小)
4. **人的介入あり/なし**: 非即時17件中、介入なし(automatic_retry_within_loop_cap)は5件のみ(短bin、PASS率40%[2/5])、残り12件は`manual_regenerate_beyond_loop_cap`または`deliberate_override`(介入あり)。介入ありグループの内訳はPart Bで求める「時間効果」と交絡しており分離不可。

Fisher正確検定(即時 vs 非即時統合): p=0.5781(有意差なし、参考値)。

### 事前定義基準への到達可否
| 基準 | 必要値 | 現状 | 到達 |
|---|---|---|---|
| 各binでN≥20 | ≥20 | 4bin中最小N=3(長bin) | 未達 |
| 即時/非即時PASS率差 | ≥20pt | 11.6pt | 未達 |
| 介入なし長間隔サンプル | ≥5件 | 5件(いずれも短bin、中・長binは0件) | 形式上到達だがbin限定 |

**総合判定: `criteria_met = False`(未達)**。

### 今回のfull_story_part1欠落→解消の分類
- take1-3(original round、`.../b1b/audit/tts_generation_results.json`): いずれも2022年survey文が丸ごと欠落したTRUE_CONTENT_MISMATCH。
- take4-6(resume round、`.../audit/human_review_resume_04_results.json`): survey文の欠落は解消したが、take5/6は別の残存差分(has/had、Part A参照)によりTRUE_CONTENT_MISMATCHのまま。segment全体は現在も`HUMAN_REVIEW_REQUIRED`。
- `cooldown_pairs.jsonl`実データ: take3→take4間の間隔2716秒(中bin)は`generation_path_field_raw: "manual_regenerate_beyond_loop_cap"`(attempt_number(4) > max_attempts(3)により機械判定)、結果は`next_try_result_verified: false`。take4→5(125秒)・take5→6(128秒)はいずれも即時retryかつ同じくmanual分類、結果ともNG。
- **分類**: ユーザー指示通り「人的介入あり(Human Review Lock解除後の`approve_regenerate`明示的regen)」に該当する(`er011_discovery_generalization_towels_trial_11_audio_04_b1b_fullstory_resume_human_review.py`が`review_lock.approve_regenerate()`を明示呼び出し)。
- **時間効果と介入効果の分離可否**: 分離不可。この1segmentのresume観測は「時間を空けた」と「人的承認を経た」が完全に同時に発生しており、時間経過のみを変数化した対照(介入なしで同じだけ時間を空けた自然発生retry)が存在しない。Part Bのcooldown集計全体でも、非即時binのうち中・長bin(30分以上)は介入なしサンプルが0件(表: 介入なし長間隔サンプル一覧は短bin[150秒〜30分]の5件のみ)であり、「時間を空ければ改善するか」という論点は現時点のデータでは介入効果と構造的に交絡したままである。

### Part B 結論(指定書式)
| 項目 | 内容 |
|---|---|
| Family/現象 | Discovery B1B(タオルTrial-11)`full_story_part1`、original round(欠落)→resume round(欠落解消、別差分は残存)。TTS retry間隔とPASS率の関係全体を横断集計 |
| 既存対策 | Human Review Lock(`er011_human_review_lock_01.py`)の`approve_regenerate()`による明示的regen許可機構(既存Production仕様、無変更) |
| 今回なぜ効かなかったか(=なぜ仕様化しないか) | 「時間を空けたretryが即時retryより有意に良い」という傾向は、現時点のデータ(N=74、非即時17件)ではFisher p=0.578で有意差なし、事前定義の十分性基準(N≥20/bin、差≥20pt、介入なし長間隔≥5件)も未達。加えて中・長binは介入なしサンプルが0件のため時間効果単独を検証できない |
| 追加Trial有無 | なし(人工的なTTS追加生成は行わず、既存ログの再集計のみ。API呼び出し0円) |
| 結果 | **仕様採用しない、継続観測**(criteria_met=False)。正式retry方針の素案は提示しない |
| Production判断が必要か | 不要(今回は現状維持の確認のみ。基準到達時のみ改めてUSER_DECISION_REQUIRED素案を提示する運用は既存のまま据え置き) |

---

## 出力・証跡パス
- Part A: `er011_output/discovery_generalization_towels_trial_11/b1b/audit/human_review_resume_04_results.json`、`.../review_lock_state.json`、`.../secondary_asr_manual_diagnostic_take5_cost_log.jsonl`(新規、本タスクで追加した診断コストログのみ)
- Part B: `er011_output/tts_retry_timing_monitor_01/`(observations.jsonl/summary.json/summary.md、再実行により最新化)、`er011_output/tts_retry_cooldown_analysis_01/`(cooldown_pairs.jsonl/summary.json/summary.md、再実行により上書き)
- 本タスクでの変更: 上記出力ファイルの再生成(script本体は無改変)、および診断用コストログ1件の追加のみ。SSOT(`CURRENT_SPEC.md`等)・`docs/pm/`・Production retry/QAコードは無変更。
