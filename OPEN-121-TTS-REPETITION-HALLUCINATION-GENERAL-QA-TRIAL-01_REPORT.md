# OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-01 レポート

管理ID: OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-01
Lane: A(隔離Trial、ユーザー承認2026-09-07)。最大到達Status: **`VALIDATED`**
(方式ごとの有効性はデータで実証、Production採用は不可・全てユーザー判断待ち)。
Production Validator/QA/retry/Cost Guard/TTS Prompt/適用範囲は**一切変更していない**。
既存Production関数(`er003_b1_p9a_audio.generate_narration_snippet`[Standard同期経路]・
`er006_asr_provider_routing_01.transcribe`・`er008_disfluency_qa_18`の各関数)を
無変更のまま呼び出すだけの独立Trialモジュール。Git操作なし(統合はFableが実施)。

書き込み: `er011_open121_tts_repetition_general_qa_trial_01.py`(root)、
`er011_output/open121_tts_repetition_general_qa_trial_01/`。

## 0. Closeout分類(方式別)

| 方式 | 到達Status | 理由 |
|---|---|---|
| A(n-gram句・文単位反復検知、canonical crosscheck付き、min_words=3) | `VALIDATED` | 実在陽性2/2検知、false reject 0/26。目的スコープ(句・文単位)内では完全動作を実データで確認 |
| A(min_words=1変種) | `VALIDATED`(ただしNOT_RECOMMENDED) | catch率は上がるが false reject 5/26(19%)、実データで再現性の低い誤検知が確認された |
| A-ext(単語duration異常、同一単語参照) | `VALIDATED`(ただしNOT_RECOMMENDED as auto-reject) | 唯一partial-word false start型を検知できたが false reject 10/26(38%)、参照corpusが小さすぎる |
| B(適用範囲拡大の評価) | `EVALUATED`(実装なし) | 本文segment[full_story/point body]でも方式A/Dが機能することを実データで確認。適用範囲の正式拡大はUSER_DECISION_REQUIRED |
| C(窓分割ASR、naive concat設計) | `REJECTED`(この設計のままでは) | overlapping window連結によるfalse reject 13/26(50%)、設計欠陥を実データで発見 |
| C-v2(窓内独立判定に再設計) | `VALIDATED`(ただし対象範囲が狭い) | false reject 0/26、だが「即座の言い直し」型(gap<0.5秒)のみ検知、合成陽性(gap>10秒)・false start型は未検知 |
| D(spectral self-similarity) | `VALIDATED` | 閾値run長0.12秒で false reject 0/39、TP 11/12(false start型のみ構造的に対象外) |
| 予防策候補 | `SURVEYED`(実装なし) | 既存資料から調査、Trial候補として提示のみ(§5) |

## 1. テストセット(全51件、audit=読み取りコピー元・生成元を明記)

| 区分 | 件数 | 出典 |
|---|---|---|
| 陽性・実在確認済み | 3 | (a)(b) A2 Point Two/In One Line原本(`…/audit/duplication_diagnosis_review_fix_02/`のBUGGY_UNFIXED/BEFORE_FIX_buggyコピー、OPEN-112-THEME2-AUDIO-REVIEW-FIX-02_REPORT.md確認済み)。(c) B1 Full Story Part 1 partial-word false start型(`…/b1_fsp1_recheck/falsestart_opening_0-3s.wav`、OPEN_ITEMS.md OPEN-121行、2026-09-07ユーザー試聴で確認・`falsestart_characterization_evidence.json`で特性確認済み) |
| 陽性・合成 | 9 | clean音声3本(A2 point_one/full_story_part1/full_story_part2)を、faster-whisper word timestampで特定した先頭付近のspanを音声中盤へ複製挿入(word/phrase[3-5語]/sentence[7-12語]の3種×3本) |
| 陰性・既存Production PASS再利用 | 27 | rerun-02のA2/B1B narration(EN13件・JA13件、comment/meaning/kp/preview/full_story等) |
| 陰性・新規Standard TTS(意図的反復) | 6 | "Not now. Not later. Not ever."等、台本自体に反復・言い換えを含む文をStandard同期TTSで新規生成(Aoede、A2/B1と同一voice/prompt) |
| 陰性(自然hallucination試行、6件とも陰性と確認) | 6 | 記事本文に似た長さの段落6本をStandard同期TTSで新規生成。hallucination自然発生は0件(Method D run長最大0.06秒、全て負例水準) |

言語内訳: EN 38件・JA 13件(方式A/C/D/A-extはEN前提のためJAはスキップ、方式設計はEN/JA共通概念)。

## 2. 方式A/B/C/Dの設計と実装(Trial専用、既存コードは無変更)

- **方式A**: `er008_disfluency_qa_18.transcribe_verbatim`(無変更)でword-level timestamp
  取得 → 新規`find_repeated_spans()`(非隣接も含む完全一致spanを最長優先で検出)→
  `_canonical_repeat_count()`でcanonical textに同じspanが2回以上出現するかを照合し、
  該当すれば「意図的反復」として除外。min_words=3(既定・推奨)とmin_words=1(比較用)の
  2変種を比較。
- **方式A-ext**: 上記のtoken一致に依らない補完策。`build_word_duration_reference()`で
  陰性26音声から単語(正規化後)ごとの典型durationを集計し、`detect_word_duration_
  anomaly_same_word_ref()`で同一単語の過去durationと比べ異常に長いwordを検知
  (falsestart型は"September"が1.28秒 vs 参照0.46秒、比率2.8倍)。
- **方式B**: 個別実装ではなく、方式A/DをFull Story/Point本文長のsegment(point_one/
  full_story_part1/part2相当)へ適用して実データで機能を確認する評価(§3参照)。
- **方式C**: `er006_asr_provider_routing_01.transcribe`(無変更)を(a)全文一括
  (baseline、陽性系はnon-determinism確認のため2回)、(b)window=8秒/hop=4秒・
  window=12秒/hop=6秒の2設定で窓分割呼び出し。v1は窓transcriptを連結して方式Aの
  text版(`_text_ngram_repetition`)を適用、v2は各窓のtranscriptを独立に判定
  (連結しない)。
- **方式D**: OPEN-112診断(`b1_fsp1_recheck/recheck_script.py`)のspectral_self_
  similarity()と同一設計(frame25ms/hop10ms/min_lag1.0秒)を独立コピーとして再実装
  (Production/他タスクファイル無変更)。run長(閾値0.85)の最大値を検知指標とする。

## 3. 結果表(方式×テスト、TP=陽性12件中の検知数、FP=陰性26件中の誤検知数)

| 方式 | TP | FP | 平均latency/件 | 追加cost/件 |
|---|---|---|---|---|
| 既存disfluency QA(baseline、隣接1語のみ) | 0/12 | 1/26 | ~3.5秒(ローカル) | ¥0(既存Production配線分は既発生) |
| **方式A(min_words=3、提案)** | 8/12(*設計対象8/8=100%*) | **0/26** | ~3.5秒(ローカル、faster-whisper small) | ¥0(ローカルCPUのみ) |
| 方式A(min_words=1) | 11/12 | 5/26(19%) | ~3.5秒 | ¥0 |
| 方式C full(既存Production ASR、非windowed) | 6/12 | 0/26 | ~1.3秒/call | 既存ASR課金と同額 |
| 方式C windowed v1(naive連結、**設計欠陥**) | 11/12 | **13/26(50%)** | ~6.2秒(窓8件分/2設定合計) | ASR呼び出し約8倍 |
| **方式C-v2 windowed(窓内独立判定)** | 2/12(*即時言い直し型は2/2=100%*) | **0/26** | 同上 | 同上 |
| **方式D(spectral、閾値0.12秒)** | 11/12 | **0/39** | ~3.1秒(最大14.8秒、O(n²)) | ¥0(ローカルCPUのみ) |
| 方式A-ext(単語duration、同一単語参照) | **12/12(唯一false start型を検知)** | 10/26(38%) | ~3.5秒(A本体と共有) | ¥0 |

**個別失敗モード別の検知状況**:
- Point Two/In One Line型(句・文まるごと反復、gap<0.5秒): 方式A(min3)・D・C-v2
  いずれも2/2検知。方式C full(既存Production ASR)はPoint Two 0/2・In One Line
  1/2(非決定的)で、OPEN-112診断の実測(8回中0回・4回中3回)と整合する結果を
  本Trialでも再現した。
- 合成陽性(phrase/sentence、gap>10秒): 方式A(min3)・D は8/8・8/8全検知。
  方式C-v2はgapが窓長(8/12秒)を超えるため0/8(窓内独立判定の設計上の限界、
  意図した挙動)。
- 合成陽性(word、1語のみ): 方式A(min3)は設計上対象外(0/3)。方式A(min1)は
  flagged=Trueにはなるが、詳細確認したところ実際に挿入した語ではなく無関係な
  数字表記トークン("%"の偶然一致)を検知していた例があり、**1語spliceは
  ASR/token一致ベースの検知そのものが原理的に不安定**(挿入部が短すぎて
  ASRが正しく書き起こせない)であることが分かった。方式Dはこの型も3/3検知
  (波形として複製が残るため)。
- Point Two/In One Line/合成陽性いずれとも異なる**partial-word false start型**
  (B1 FSP1、語の途中で切れて再開、"September"のword-level timestampが1.28秒
  [通常0.46〜0.6秒の約2〜2.8倍]): 方式A・C・Dいずれも0/1(トークン完全一致・
  波形完全一致のいずれの前提にも合致しない失敗モードのため構造的に検知不能)。
  **方式A-ext(単語duration異常)のみ検知**(唯一の成功例)。

**新規Standard TTS 6件(自然hallucination発生を狙った試行)**: いずれも
hallucination発生なし(方式D run長0.02〜0.06秒、全て陰性水準)。まれな現象の
ため6回の試行では自然発生を捕捉できなかった(統計的に想定内、詳細は§9)。

生データ: `er011_output/open121_tts_repetition_general_qa_trial_01/results/`
(`method_a_local_verbatim.json`・`method_a_ext_word_duration_same_word_ref.json`・
`method_c_windowed_asr.json`・`method_c_v2_within_window_only.json`・
`method_d_spectral_self_similarity.json`・`summary_table.json`)。

## 4. 検知後flowの既存機構との接続案(設計のみ、未実装)

- 方式A(min_words=3)・方式Dは、`er003_v1_repro01_main_generate.py::generate_
  narration_snippet_verified_strict()`内の既存`dq18.apply_disfluency_gate()`
  呼び出し(`verified = gate["verified"]`)と全く同じパターンで、`verified =
  verified and not ngram_check["flagged"]`のように追加のANDゲートとして
  接続できる。これにより新しいretry回数・新しいCost Guardを一切追加せず、
  既存の`PRODUCTION_MAX_TTS_ATTEMPTS`(3回)予算内でretryが自動的に発生し、
  上限到達後は既存の`STOPPED`→`er011_human_review_lock_01`の`HUMAN_REVIEW_
  REQUIRED`自動遷移にそのまま合流する(disfluency QAで実証済みの経路を
  再利用するだけで済む)。
- 方式C(v2)は同じ呼び出し内で追加のASR呼び出し(窓分割分)を行うため、
  `record_outcome()`の`asr_calls_this_call`カウント(`attempts_log`内
  `asr_text is not None`の件数)が実際のASR呼び出し数を過小評価する
  (窓分割分が計上されない)。方式Cを採用する場合は、この会計ロジックの
  拡張が必要(未実装、Cost Guard budget[`MAX_CUMULATIVE_ASR_CALLS`=60]の
  実効性に関わるため要修正)。
- 方式A-ext(単語duration)は、現状のfalse reject率(38%)のままではauto-reject
  ゲートとして接続すべきではない(safety≠success原則に反する)。接続するなら
  「flagged=True→即STOPPEDではなく、Human Review Queueへ直接ソフトフラグ
  として記録するだけ(既存`is_duplicate_queue_entry()`を流用)」という弱い
  接続が現実的(未実装)。
- 方式B(適用範囲拡大): Point Two/B1 FSP1はいずれも`disfluency_qa`引数が
  既定False(本文segmentは承認スコープ外)の呼び出しだった。方式A/Dを本文
  segmentへ適用するには、`stage_c_generate_new_narrations()`等の呼び出し元
  で`disfluency_qa=True`相当のフラグをbody segment向けにも渡す変更が必要
  (対象segment数×TTS試行回数分のASR/計算コストが増える、未実装)。

## 5. 予防策候補(read-only調査、実装なし)

既存資料からの調査結果(全てTTS生成側の設定変更候補、Production未採用):

1. **Structured Separation**(既存`PRODUCTION_WIRED`、ER-005-AUDIO-INSTRUCTION-
   SEPARATION-01): style instructionとspoken textを`=== STYLE INSTRUCTIONS
   ===`/`=== TEXT TO SPEAK ===`で明示区切り。instruction leakage型
   hallucinationへの対策として既に導入済みだが、Point Two/In One Line型
   (句・文の言い直し)への直接効果は未検証(別のfailure mode)。
2. **文レベルprosodyとの相関**(OPEN-107診断、`er011_open107_opened_tts_
   diagnostic_trial_01.py`): 誤発音は短い断片では12/12正解、完全な一文では
   6件中2件失敗という実データがあり、「完全な一文としての読み上げ」が
   TTSの不安定性を誘発しやすい可能性を示唆。今回のPoint Two/In One Lineの
   反復も、複数文からなる本文segment(そのものが「完全な一文の連なり」)で
   発生しており、示唆と方向性が一致する(相関の域を出ないが、Trial候補
   として提示価値あり)。
3. **temperature等の生成パラメータ**: `er002_gemini_client.py::build_speech_
   config()`はvoice指定のみで、`GenerateContentConfig`にtemperature等の
   明示指定は無い(API既定値のまま)。temperatureを下げることでhallucination
   頻度が下がるかは今回未検証(Trial候補)。
4. **hallucination根本原因**: CURRENT_SPEC.md「hallucination対応」行に
   「根本原因は未解明のまま」と明記されている。既存対策(strict検証+minimal
   instruction fallback)は自動検出・自動吸収止まりで予防策ではない。
5. **segment長・句読点**: 本Trialで観測した限り、Point Two/In One Line
   (それぞれ6文・1文)、B1 FSP1(1文目冒頭)いずれも短くはない/長くもない
   中庸な長さで発生しており、単純な「長いほど危険」という相関は今回の
   3サンプルからは確認できなかった(サンプル数不足、追加調査が必要)。

いずれも**Production TTS Promptの正式変更は行っていない**(調査のみ)。

## 6. 推奨方式と理由(QCD)

**推奨: 方式A(min_words=3) + 方式D の並列採用**(いずれもローカル計算・
追加API課金ゼロ・実データでfalse reject 0)。実在確認済み failure mode
(Point Two/In One Line型、句・文まるごと反復)に対し、2つの独立した検知
原理(token一致 vs 波形一致)で二重に防御でき、既存disfluency QAの接続
パターンをそのまま流用できるため実装コストも低い。方式C(v2、窓内独立
判定)は同じ失敗パターンに対する3つ目の確認手段として補助的に追加可能
(ただしASR追加コストとCost Guard会計修正が必要)。方式A-ext(単語duration)
は唯一partial-word false start型を検知できる有望な方向性だが、現状の
false reject率(38%)のままではauto-reject接続に不適格 — Human Review
への**ソフトフラグ**としてのみ将来検討する価値がある(要・大規模参照
corpus)。方式C windowed v1(naive連結)は**明確に非推奨**(false reject
50%という設計欠陥を実データで確認)。

## 7. 受入条件10項目セルフチェック

1. Point Two型を検知 → **PASS**(方式A/D/C-v2いずれも2/2中1/1、実音声で確認)
2. In One Line型を検知 → **PASS**(同上)
3. 正常音声を過剰にrejectしない → **PASS**(方式A min3・D・C-v2は26/26中0件誤検知)。
   min1変種・A-ext・C windowed v1は誤検知ありと明記(§3)
4. full ASR平滑化の見逃しを補完 → **PASS**(方式C full(既存)はPoint Two
   0/2・In One Line 1/2の非決定的見逃しを実測、方式A(ローカル)・C-v2
   windowedはいずれも2/2で完全に補完)
5. 本文segmentでも機能 → **PASS**(point_one/full_story_part1/part2相当の
   長さで方式A/Dとも機能確認、真陽性2件[Point Two/B1 FSP1]も本文segment)
6. retry/Cost Guardと整合 → **PASS**(§4で既存disfluency QAと同一パターンの
   接続案を提示、新規retry回数・新規Cost Guardの追加なし)
7. runtime costが現実的 → **PASS**(本Trial総cost¥29.09、364 API呼び出し、
   上限¥800の3.6%)
8. Production latency影響が許容可能 → **PASS(条件付き)**(方式A/D単体は
   3〜4秒/segment[オフライン事前QAとして許容範囲]。方式C windowedは
   窓8件×2設定で追加約6秒/segment、実採用時はProduction全体のTTS生成
   時間への影響を別途評価要)
9. Fact/content validationと競合しない → **PASS**(canonical crosscheckは
   既存内容Validatorと同じcanonical textを参照するのみで、判定ロジックは
   独立。意図的反復テキスト6件は方式A(min3)で正しく非flagged)
10. 既存disfluency QAとの役割分担が明確 → **PASS**(§3で失敗モード別の
    分担表を実データで整理。dq18=隣接1語のみ・狭いscope、方式A=非隣接
    句・文単位・canonical-aware、方式A-ext=token非依存のduration異常
    [false start専用]という3層構造が明確になった)

## 8. USER_DECISION_REQUIRED(Production採用に必要な判断)

1. 方式A(min_words=3)・方式Dを、既存disfluency QA接続パターンで実際に
   Production配線するか(新規Validator原則の`APPROVED_FOR_PRODUCTION`が必要)。
2. 適用範囲をfull_story/point本文segmentへ拡張するか(処理コスト増を
   許容するか、方式B該当)。
3. 方式C(windowed ASR、v2設計)を追加の確認レイヤーとして採用するか
   (ASR追加コスト・Cost Guard会計修正が必要)。
4. 方式A-ext(単語duration異常)を、false reject率を下げるための改善
   (大規模参照corpus構築等)を条件にHuman Reviewソフトフラグとして
   将来採用する方向性を維持するか、それとも見送るか。
5. B1 Full Story Part 1のpartial-word false start型自体の扱い
   (OPEN_ITEMS.md OPEN-121行で既にUSER_DECISION_REQUIRED登録済み、
   本Trialは追加の検知手段候補を示しただけで、既存の重複入り音声への
   対応方針自体は変更していない)。
6. §5の予防策候補(temperature調整等)を、別Trialとして追加検証するか。

## 9. Cost

総cost: **¥29.09**(内訳: Gemini TTS[Standard同期、12件新規生成]¥12.82・
OpenAI ASR[全文+窓分割、計約350呼び出し]¥16.27、1USD=160円換算、
`er005_output/cost_baseline_01/pricing_snapshot.json`の公式価格を使用)。
上限¥800に対し3.6%。生データ:
`er011_output/open121_tts_repetition_general_qa_trial_01/audit/raw_usage_log.jsonl`
(Production側の`raw_usage_log.jsonl`には一切書き込んでいない、専用ログ)。

## 10. SSOT登録案(Fable/ユーザーが実施、本Trialでは未実施)

- `OPEN_ITEMS.md` OPEN-121行へ、本Trialの結果概要(方式別TP/FP実測値、
  falsestart型の追加検知候補[方式A-ext]、Production採用は全てUSER_
  DECISION_REQUIRED)を追記。
- `DECISION_LOG.md`へ`OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-
  TRIAL-01`エントリを新規追加(Trial実施・Production未採用の記録)。
- `CURRENT_SPEC.md`は本Trialでは変更しない(Production採用決定後に
  該当行[Disfluency QA行等]を更新する想定)。

## 試聴用ページ(file:///)

`file:///C:/Users/tensh/eigo-radio/er011_output/open121_tts_repetition_general_qa_trial_01/player.html`
(陽性・実在確認済み3件[Point Two/In One Line/B1 FSP1 false start]、
合成陽性9件、陰性27+12件、それぞれ方式ごとの検知結果を表内に併記)。
