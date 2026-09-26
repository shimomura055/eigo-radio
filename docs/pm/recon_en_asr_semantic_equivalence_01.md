# Recon: EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01

- 管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01
- 種別: Recon(¥0、read-only、実装・Trial・Production変更なし)
- 目的: Fableの「English ASR Semantic Equivalence Layer」包括対策案を批判的レビューするための、Repo上の現行仕様・実装・証跡の棚卸し
- API呼び出し: 0件

---

## 1. 現行English ASR照合の実装

### 1.1 `classify_asr_match`本体

- 所在: `er006_preprod_hardening_01_validation.py`
  - 分類本体(無変更コア): `_classify_asr_match_core()`(L794-949)
  - 公開ラッパー: `classify_asr_match()`(L952-1004)。OPEN-123(標準contraction展開)採用後、コアを「外側から包む」薄いラッパーになった。

**分類フロー(`_classify_asr_match_core`、全分岐、L794-949)**:
1. `asr_text is None` → `TTS_FAILURE`(should_retry=True)
2. 完全一致(strip後) → `EXACT_MATCH`
3. `tokenize()`後の一致(発音区別符号・ハイフン・序数・数値表記・英米綴り等を`normalize_text()`で吸収済み) → `NORMALIZED_MATCH`
4. 複合語の分かち書き差(despace後一致) → `NORMALIZED_MATCH`
5. 冠詞のみを除いた内容語のdespace一致 → `NORMALIZED_MATCH`
6. `protected_check()`(数字・否定・内容語の欠落/追加/置換を検出)がFAIL
   - 数字ゲート例外(`_try_homophone_number_rescue`、CMU辞書ARPAbet完全同音のみ、alignment_safe必須)に該当すれば `HOMOPHONE_MATCH_NUMBER_EXCEPTION`
   - 非該当なら即 `TRUE_CONTENT_MISMATCH`(should_retry=True)
7. ratio < 0.4 → `TTS_FAILURE`
8. 内容語差が「固有名詞以外」を含む(non_entity_diffs)
   - 3パターン限定Connected Speech Validator(`er011_b1_connected_speech_validator_01.classify_connected_speech`)がACCEPT/RESEGMENTATIONと判定すれば `CONNECTED_SPEECH_ACCEPT`/`CONNECTED_SPEECH_PASS_WITH_WARNING`
   - 非該当なら `TRUE_CONTENT_MISMATCH`
9. 固有名詞のみの差(entity_only_diffs) → `ASR_VALIDATION_UNCERTAIN`(should_retry=False、retryでは解決しない扱い)
10. 完全同音語のみの差(homophone_only_diffs) → `ASR_VALIDATION_UNCERTAIN`
11. ratio >= 0.98 → `HIGH_SIMILARITY_SAFE`
12. (fallback)Connected Speechパターン再確認 → 該当すればACCEPT/PASS_WITH_WARNING
13. それ以外 → `ASR_VALIDATION_UNCERTAIN`(「内容語差は無いが一致率が届かない」)

**戻り値の分類一覧(`VALID_CLASSIFICATIONS`、L751-775)**: `EXACT_MATCH, NORMALIZED_MATCH, HIGH_SIMILARITY_SAFE, ASR_VALIDATION_UNCERTAIN, TRUE_CONTENT_MISMATCH, TTS_FAILURE, CONNECTED_SPEECH_ACCEPT, CONNECTED_SPEECH_PASS_WITH_WARNING, HOMOPHONE_MATCH_NUMBER_EXCEPTION, CONNECTED_SPEECH_EQUIVALENCE_ACCEPT(注:cascade層のみ返す), CONNECTED_SPEECH_EQUIVALENCE_PASS_WITH_WARNING(同), TRANSCRIPT_STYLE_NORMALIZED_MATCH`。

**"benign扱い"の現行ルール(規則的複数形ペア、`_is_benign_plural_pair`, L525-531)**: `result/results`のような規則複数形のみ吸収。ただし「吸収」の意味は限定的で、**content_word_diffsに計上しない**だけであり、自動PASSにはならない(下記4.gで実証)。1トークン差の場合、ratio<0.98であれば最終的に`ASR_VALIDATION_UNCERTAIN`へ落ちる(retry無効・Human Review方向)。

**canonical/transcriptの正規化処理**(`normalize_text`/`normalize_numeric`, L319-436):
- 小文字化・句読点除去(`[^a-z0-9]+`をスペース化)あり。
- 数字処理: cardinal語→算用数字(2語以上、または`hundred/thousand/million`単独)、序数語→算用数字+接尾辞、複合序数(twenty eighth→28th)、桁区切りカンマ除去、$記号→`xdollarx`マーカー、小数点→`xdecimalpointx`マーカー、%→`xpercentx`マーカー、日付文脈の序数接尾辞除去、数式指数表記(Unicode上付き・ASCIIキャレット・話し言葉"to the minus N")のマーカー化。
- 英米綴り(`BR_AM_SPELLING_PAIRS`, 12ペア)、住所略語(street→st等、`_STREET_SUFFIX_EXPANSIONS`)を閉じた既知集合として吸収。

### 1.2 `er003_audio_tts_asr_safety.py`

- 役割: (A)TTS入力正規化(Markdown除去・日本語分数読み等、canonicalは変更しない使い捨てコピー用)と、(D)Production Telemetry統一スキーマの提供。
- `validate_asr_match()`(L324-375)は**旧世代の簡易版**(先頭n語の単語完全一致サブシーケンス判定+英米綴りのみ吸収、`EXACT_MATCH/NORMALIZED_MATCH/FAIL`の3値)。ASR未取得・API/認証エラーは常にFAIL(PASS禁止)というポリシーは`er006`版にも継承されているが、数字/否定/内容語の"保護"チェックは持たない(`er006_preprod_hardening_01_validation.py`のほうが厳格かつ新しい)。呼び出し元は現在も一部の古い個別記事script(`er003_v1_*`、44ファイルで参照)や`er007_ja_asr_validator_01.py`(日本語側、構造的ヘルパーとして再利用)。**現行Production英語本文/Key Phrase経路の主判定は`er006`の`classify_asr_match`であり、`er003.validate_asr_match`はそれより粗いレガシー層**という位置づけ(両者が並存)。

### 1.3 Primary/Secondary ASR、Cascade

- 英語Cascade: `er006_secondary_asr_01.py`。`evaluate_attempt_with_cascade_detail()`(L442)が統一エントリ。Primary ASRが`classify_asr_match`でNGだった場合のみ、条件付きでSecondary(Azure STT/local faster-whisper)を追加実行する設計。
  - Key Phrase英語専用のNon-Latin Cascade(`is_non_latin_dominant_mismatch`, L65): OPEN-119由来。Primary ASR(`gpt-4o-mini-transcribe`)が英語を非ラテン文字(CJK等)へ意味変換してfalse rejectする事象への対策(`generate_key_phrase_component_verified`限定、`CURRENT_SPEC.md` L1331)。
  - Connected Speech Equivalence Layer(OPEN-122、後述2節)もこのCascade層内(`_connected_speech_equivalence_layer_attempt`, L302)に実装。
- 日本語用は別モジュール`er007_ja_asr_validator_01.py`(`classify_ja_asr_match`)+`er007_ja_secondary_asr_01.py`(Secondary Cascade)。英語側とは完全に別実装(辞書ベースの確定読みチェック等、日本語固有ロジック)。
- Key Phrase Secondary ASR: `KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-TRIAL-01`(OPEN-119由来、`CURRENT_SPEC.md` L1331)。英語Key Phrase Component経路(`generate_key_phrase_component_verified`)限定でPrimary(Minimal)/Fallback(English Lock)にのみ`asr_prompt`+`enable_non_latin_cascade=True`を渡す。本文segment・Point見出し・Previewには展開していない。
- Human Review Lock(`er011_human_review_lock_01.py`)への到達条件: `record_outcome()`(L255)がstatus!="OK"(STOPPED等)なら`new_state="HUMAN_REVIEW_REQUIRED"`(L292)、status=="OK"なら`"RESOLVED"`(L289)。`VALID_STATES`(L106-107)。2026-09-26のTTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01により、この判定の直前にcool-down+Local Rewrite回復経路が挟まった(下記3節)。

---

## 2. Connected Speech Equivalence Layer(OPEN-121/122)

**用語の食い違いに注意**: タスク指示は「OPEN-121/122」としているが、Repo上の実際の番号付けでは、Connected Speech Equivalence Layerに対応するOPEN項目は**OPEN-122**のみ(`OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01_REPORT.md`)。**OPEN-121は別件**(`OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-*`、TTSの反復幻覚QAで無関係)。関連する近傍項目は OPEN-103(TTS側の誤発音)・OPEN-110(単数複数取り違え、Pattern A/C原型)・OPEN-119(Key Phrase非ラテン文字)・OPEN-123(Transcript Style Normalization、3節参照)。

**2段構え(既存3パターン + Equivalence Layer)**:
1. **既存3パターン**(`er011_b1_connected_speech_validator_01.py`、OPEN-107/110、無変更・拡張禁止のユーザー決定済み):
   - Pattern A(歯擦音連続、studies+suggest→study suggests): `CONNECTED_SPEECH_ACCEPT`
   - Pattern B(破裂音連続、opened+to→open to): `CONNECTED_SPEECH_ACCEPT`
   - Pattern C(再分節、survey+suggest→surveys suggest): `CONNECTED_SPEECH_PASS_WITH_WARNING`
   - `classify_asr_match`のnon_entity_diffs分岐(L890)とfallback分岐(L933)から直接呼ばれる。
2. **Equivalence Layer**(`er011_connected_speech_equivalence_layer_production_01.py`、OPEN-122、312行): ARPAbet音韻環境カテゴリA〜G(assimilation/coalescence/flapping/resyllabification等)+多証拠corroboration。既存3パターンがUNCLASSIFIEDだった場合の**後段**として`er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail()`内でのみ発火(`classify_asr_match`自体はこのラベルを直接返さない)。
   - 安全ゲート: (1)音韻環境がカテゴリA〜G該当 **かつ** (2)独立ASR(Secondary Azure/local faster-whisper)の少なくとも1つがcanonical側を支持(corroboration)。0件→`INSUFFICIENT_EVIDENCE`、食い違い→`MIXED_EVIDENCE_INSUFFICIENT`。corroboration≥1かつA/B/C→ACCEPT、D/E/F/G→PASS_WITH_WARNING。
   - 適用範囲(ユーザー正式承認2026-09-07、`APPROVED_FOR_PRODUCTION`): **A2/B1英語本文segment(full_story_part1/2・point_one・point_two)のみ**。Key Phrase・日本語・他segmentは対象外(新規opt-inフラグ`enable_connected_speech_equivalence_layer`、既定False)。

**今回のSemantic Equivalence案との重複・競合範囲**:
- 重複: どちらも「ASR文字列差分を即NGにしない」層である点、および「独立evidence(Secondary ASR)がある場合のみ救済」という設計思想(Tier3の保護対象概念と同型)。
- 非重複: Connected Speech Equivalence Layerは**音韻(発音)レベルの差**(語末子音の弱化・融合)を対象とし、Fable案のTier1(数値・通貨・%等の**表記**レベルの等価)・Tier2(transcript style)とは対象レイヤーが異なる。ただし両者とも「canonicalとASRの文字列が食い違うが意味は変わらない」という同じ問題領域に属し、実装場所(`classify_asr_match`周辺 vs Cascade層)の設計判断が今後競合しうる(Tier1をコア`normalize_text()`に置くか、Tier2/Equivalence Layerと同じくCascade後段のopt-in層にするかは要決定)。

---

## 3. retry/Local Rewrite(er020)との位置関係

- ASR判定(`classify_asr_match`/`evaluate_attempt`)は既存retryループ内で毎attempt呼ばれる(標準経路2回+fallback1回、合計`PRODUCTION_MAX_TTS_ATTEMPTS=3`)。
- **Local Rewrite(`er020_tts_retry_local_rewrite_01.py`, 637行)はNG種別を区別しない**: `run_local_rewrite_recovery()`(L541)は、呼び出し元(`generate_charon_english`等)が「3回とも(またはstop_retryingで)ASR検証に合格しなかった場合のみ」呼ぶ(`er003_v1_sing01_voice01_generate.py` L219-241のコメント)。`identify_ng_span()`(L171)はcanonical/ASRの`SequenceMatcher`差分のうち**最初のdiff opcode**を機械的に取るだけで、その差が`TRUE_CONTENT_MISMATCH`(真の内容誤り)なのか`ASR_VALIDATION_UNCERTAIN`(表記/固有名詞/同音語のみの差)なのかを一切見ない。
  - trigger条件: cool-down(10分固定)→attempt3もNG→Local Rewrite(問題spanのみをLuna 1 callで言い換え候補生成→7 Gate QA→再TTS→再ASR)。
  - 適用範囲(role): `CONNECTED_SPEECH_SEGMENT_IDS`(L95-111、5 role: Full Story/Comment/Preview/Topic intro/In One Line)のみ。Heading readout・Key Phraseは非適用(`NON_APPLICABLE_SEGMENT_IDS`, L114-116)。
- **設計上の含意**: 現状、「表記は違うが意味は同じ」false rejectと「本当に内容が違う」true mismatchのどちらも、同じ土俵(cool-down→Local Rewrite→Human Review Lock)に乗る。Semantic Equivalence Layerが`classify_asr_match`より前段(またはLocal Rewrite呼び出し判定の前段)で数値・通貨等の等価を検出できれば、**Local Rewrite自体が不要になるケースがある**ことを、下記4節(a)の実証データが直接示している(数字表記差はLocal Rewriteで解決できない性質のため、cool-down 600秒+Luna 2 call を消費した末に`HUMAN_REVIEW_LOCKED_RETTS_FAILED`へ到達している)。

---

## 4. 過去のfalse rejection証跡(Repo evidenceのみ)

### (a) $2.3 million系 — `er020_output/tts_local_rewrite_production_wiring_01/a2/`

- 証跡: `comment_test2_probe.json`、`evidence_theme_01/a2/audit/review_lock_state.json`(segment `comment_test2`)、`TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01_REPORT.md` §12.3(L267-306)。**2026-09-26(本日)実施**の架空theme検証run(Production wiring実証用、実記事ではない)。
- canonical(逐語、report L269-271): `"The price rose to two point three million dollars, a fifteen percent increase from last year."`
- ASR(逐語、`comment_test2_probe.json` attempt1/2/fallback、全て同一): `"The price rose to $2.3 million, a 15% increase from last year."`
- 当時の判定: 3回とも`audio_classification: "TRUE_CONTENT_MISMATCH"`。
- 当時の対処: cool-down(実測600.004秒)→Local Rewrite候補生成(Luna`gpt-5.6-luna`、5候補)→7 Gate QAで`candidate_2`("two million three hundred thousand dollars")採用→再TTS→**再ASRも不一致(依然digit/spelled-out表記差)**→最終`status: "HUMAN_REVIEW_LOCKED_RETTS_FAILED"`(report L282-285)。
- 現在の状態: Human Review Lockで停止したまま(このrun自体は評価用の架空データであり実記事ではないため、実際のHuman Reviewキューには影響しない)。
- **根本原因の直接特定(本Reconで`normalize_numeric()`のロジックをトレースして確認)**: `_SCALES = {"hundred":100,"thousand":1000,"million":1000000}`(L97)には**billionが存在しない**。加えて`_convert_cardinal_words()`(L279-310)は空白区切りの連続する数値語トークン列のみをまとめて変換するため、`"two point three million"`のように**"point"が数値語列を分断する**表記では、"two"のみが独立して`"2"`に、"three million"が独立して`"3000000"`に変換され(pointの後にある"three"と"million"が連結され3×1,000,000として計算される一方、"point"の前の"two"との関係は失われる)、結果として`"2 point 3000000 dollars"`という**元の意味(2.3百万)とは異なる中間表現**になる。一方ASR側`"$2.3 million"`は`$`規則(L345)で`"2.3 dollars million"`となり、"million"が単独スケール語として`"1000000"`に変換され`"2.3 dollars 1000000"`となる。両者は最終的に`xdecimalpointx`/`xdollarx`マーカー配置が構造的に異なるトークン列になり、`tokenize()`後も一致せず、`protected_check()`の数字保護ゲート(`asr_numbers=["1000000"]` vs `canon_numbers=[]`相当の不一致)に必ず抵触して`TRUE_CONTENT_MISMATCH`になる。**つまり現行実装は「decimal+scale word(2.3 million等)」の値そのものを一度も計算しておらず、digit形式とspelled-out形式のどちらであっても、両者を同じ数値へ正規化する経路が存在しない**(Fable案のTier1数値等価が埋めるべき、実証済みのギャップ)。

### (b) want to/wanna — `OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01_REPORT.md`

- 実例(§6、L100-116): canonical `"Don't you want to come with us?"`、Primary ASR `"Don't you wanna come with us?"`。
- 当時の判定: baseline(wanna正規化なし)= `TRUE_CONTENT_MISMATCH`(false reject)。
- 検証結果: mode_a(wanna無条件正規化)は救済するがfalse accept理論リスクあり(Production非推奨)。mode_c(Secondary/local ASR corroboration必須)は実例1件で正しく救済(ただしテストカバレッジ小)。
- **ユーザー正式決定(2026-09-07)**: 標準contraction(否定保持のみ、`don't`⇔`do not`等)はProduction採用(`classify_asr_match`ラッパー、L699-1004)。**"want to"⇔"wanna"等の口語的縮約(2語→1語)はProduction不採用のまま**(正規化しない、現状維持、L690・L734のコード注記)。
- 現在の状態: 未解決のまま(Tier2のtranscript style equivalenceが提案する範囲そのものだが、既に一度検証され「corroboration必須なら安全に運用できる可能性はあるが、Production採用は見送り」という決定履歴がある)。

### (c) drug store/drugstore — `CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-02_REPORT.md`

- T2A3("drug store"→"drugstore"、L70,182,256): **既存Validatorの`despaced()`複合語分かち書き吸収(`_classify_asr_match_core` L822-825)により既にNORMALIZED_MATCHとして無害化済み**と確認されている。追加対応不要(Fable案のSAFE_ORTHOGRAPHIC_EQUIVALENCEの一部は既に実装済みという事実)。

### (d) 数字↔spelled-out(一般)

- `normalize_numeric()`(1.1節)がcardinal/ordinal/桁区切り/%/decimal/$の**単純なケース**は吸収する(例: "28"⇔"twenty-eight"はER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01で一般化済み、L69-98コメント参照)。
- 一方、(a)で実証した通り**decimal+scale word(million/billion)の組み合わせ**は現行実装の既知の穴。billion自体も`_SCALES`未対応。

### (e) 過去のKey Phrase ASR表記問題

- OPEN-119(`KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01`)→`KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-TRIAL-01`(`CURRENT_SPEC.md` L1331): TTSは正しく英語発話しているのに、Primary ASR(`gpt-4o-mini-transcribe`)が非英語文字列(例:「新常態」)へ意味変換しfalse rejectする事象(false rejection率57.1%→対策後0%)。これは**表記の揺れではなく、ASR自体が言語検出を誤って全く別の文字体系へ書き起こす**という、Fable案の分類(EXACT/SAFE_ORTHOGRAPHIC/NUMERIC/TRANSCRIPT_STYLE/CONNECTED_SPEECH/PROTECTED/UNKNOWN)のどれにも直接該当しない、性質の異なるfalse reject(ASR provider自体の言語誤検出)。
- kp4_en「point to」/ASR「Point two」(OPEN-116(b)、`er006_preprod_hardening_01_validation.py` L598-609コメント): cardinal変換がASR側"two"のみを数字化しcanonical側"to"が数字扱いされない非対称性により、数字保護ゲートが誤爆した実例。対策としてTrack B数字ゲート例外(`_try_homophone_number_rescue`, L631-678、CMU辞書完全同音限定)がProduction採用済み。

### (f) Connected Speech関連

- OPEN-110(studies/suggest型、単数複数取り違え、Pattern A/C原型として解決済み)。
- Connected Speech Equivalence Layer Trial-01/02の実音声実証(2節参照)、負の対照(N1・T2N4)はいずれも非accept(`TRUE_CONTENT_MISMATCH`のまま)を確認済み(false accept 0)。

### (g) point/points(comment_4) — `TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01_REPORT.md` §12.2(L85-123)

- 2026-09-26実本番run、Family X comment_4「bring the main point together」。attempt1〜3すべてASRが"point"を"points"と聞き取り、**3回とも`ASR_VALIDATION_UNCERTAIN`**(単数複数の規則的揺れであり`_is_benign_plural_pair()`によりcontent_word_diffs自体には計上されないが、その結果ratio<0.98の最終fallback[L947]へ落ち、自動PASSにはならない)。
- 対処: cool-down(実測600.009秒)→Local Rewrite候補生成(Luna)→7 Gate QAで`candidate_3`("bring the main point together"→"boil it down to the main idea")採用→再TTS→ASR完全一致→`status="OK"`確定(`RESOLVED`)。
- **本Reconでの技術的指摘**: これは意味的に完全に無害な単数複数の揺れ(Fable案のNUMERIC_EQUIVALENCE寄りだが厳密には形態論的等価)であり、Local Rewriteで言い換える必然性はない(実際、最終的に採用された言い換えは"point"自体を回避する全く別表現になっている)。Semantic Equivalence Layerが「規則的複数形のみの差はPASS」と明示的に判定できれば、cool-down 600秒+Luna 2 callのコストと、canonical文言の実質的な書き換え(意味は保持されるが元の文言ではなくなる)を回避できた可能性が高い、という**実データに基づく具体的な改善余地**。

### (h) メタ/メタン(日本語、参考、非対称リスクの実例)

- `DECISION_LOG.md` L9505-9515: 日本語側の逆方向の教訓。「Meta」(社名)をTTSが「メタン」(methane)と読み違え、当時のASR Cascade(最大4回の追加ASR)のいずれか1回が偶然「メタ」相当と一致すれば無条件PASSする構造だった(**false accept**、false rejectの逆)。原因は辞書確定読みがTTS入力にもASR照合にも使われていなかったこと。修正後、regression母集団18件中17件は分類不変、1件(Meta comment_3)は`ASR_VALIDATION_UNCERTAIN`→`TRUE_CONTENT_MISMATCH`(意図した厳格化)。
- **含意**: Semantic Equivalence Layerのような「一致を広げる」対策は、常に対称的な「false acceptを増やしていないか」の検証(Regression Corpus上のNEGATIVE側)とセットでなければならない、という既存の教訓が日本語側に既にある。

---

## 5. 既存の数値・略語処理(流用可能な既存関数)

- `normalize_numeric()`(`er006_preprod_hardening_01_validation.py` L319-378): cardinal/ordinal語⇔算用数字、複合序数、桁区切りカンマ、$、小数点、%、日付序数接尾辞、数式指数のマーカー化。**Tier1数値等価の土台として最も再利用しやすいが、上記4(a)の通りscale word(million/billion)を含む複合数値は未対応**。
- `_words_to_number()`(L251-276): word列→整数。thousand/millionの合成は対応、billionは非対応(`_SCALES`にキーが無い)。
- TTS入力側の前処理: `er003_audio_tts_asr_safety.py`にはMarkdown除去・日本語分数読みはあるが、英語の`$`/`%`をTTS発話用に展開する専用関数は見当たらなかった(TTSモデル自体が`$2.3 million`をそのまま読み上げている前提、Ledger/Fact tokens側の数値正規化とは別レイヤー)。
- Ledger側(`er006_output/pronunciation_ledger_01/ledger.json`等)の数値正規化は本Reconでは未調査(スコープ外、TTS/ASR照合には直接使われていない模様)。

---

## 6. 現行validatorの責務分離

- `classify_asr_match`自体はrole/segment_typeの引数を取らない(canonical_text/asr_textのみ)。**role別・Family別の分岐はvalidator関数の外側**(呼び出し元の配線)で行われている。
- Role分離のSSOT: `er020_tts_retry_local_rewrite_01.py::resolve_narrative_role()`(L120-140)。`FULL_STORY/COMMENT/PREVIEW/TOPIC_INTRO/IN_ONE_LINE`(Connected Speech Equivalence Layer + cool-down/Local Rewrite適用対象、5 role)と`HEADING_READOUT/KEY_PHRASE`(非適用)を判定する単一関数。
- Family別の差: **本Reconで発見した範囲では、classify_asr_match/protected_check自体にFamily(News/Fiction/Trend等)による分岐は無い**。適用差は「どのProduction関数から`enable_connected_speech_equivalence_layer=True`を渡すか」というsegment_id(role)ベースの配線のみで決まり、Family非依存(Family横断で同じroleなら同じ扱い)。

---

## 7. runtime cost/latencyの現状

- Azure STT実測単価: 約13.8円/回相当(`ER-005-AUDIO-VALIDATION-ROBUSTNESS-02_report.md` L164、音声長ベース推定、$1/時間換算)。同様に`ER-005-AUDIO-WASTE-REDUCTION-01_report.md` L15で「約137秒・128秒分のASR Cost、Azure STT $1/時間」→合計約11.77円。
- Secondary ASR(Cascade追加分)の限界費用: `ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01_report.md` L65「Cascadeによる追加ASRコストは1回あたり$0.00002程度で無視できる水準」。
- OPEN-122 Production wiring実測(2026-09-07): 標準同期・実API合計¥3.34(A2 Flagship+B1実本文1件+敵対的陰性対照2件、TTS/ASR/Luna込み)。
- TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01実測(2026-09-26): comment_4回復1件でTTS4回+ASR4回+Luna2回(候補生成+QA)、wall clock 702.4秒(cool-down600秒込み)。comment_test2(数字表記、未解決)でも同様に707.8秒。全体概算¥15〜20(run_01実測¥7.15を基準に按分)。
- Key Phrase Secondary ASR: 個別の単価データは本Reconでは未発見(Cascade全体の限界費用$0.00002/回が最も近い数値)。

---

## 8. 設計上の論点メモ(現行実装で何が起きるかの事実、判断はしない)

| 論点 | 現行実装で何が起きるか(事実) |
|---|---|
| locale(decimal/comma、通貨、日付順、単位) | 米国式のみ実装(`$`前置、decimal point、桁区切りカンマ)。日付は月名+序数(March 4th)前提のみ扱う専用パターンあり(`_DATE_ORDINAL_RE`)。他localeの通貨記号(£/€)・日付順(DD/MM)は`normalize_numeric()`に一切ハンドリングなし(未知の記号は一般記号除去でただ消えるだけ、桁情報は保持されない可能性)。 |
| million/billion scale | `million`のみ`_SCALES`に存在、`billion`は不在(語として`_NUM_WORD_VOCAB`に含まれず、cardinal変換の対象外のまま素通りする)。decimal+scale word複合(2.3 million等)は4(a)で実証した通り**現行実装は値を正しく計算しない**(構造的ギャップ)。 |
| approximate表現(about/nearly/more than/around) | `_STOPWORDS`/`_NEGATION_WORDS`のいずれにも含まれないため、通常の内容語として扱われる。canonical/ASR間でこれらの語自体に差があれば`content_word_diffs`(entity_like/homophone_candidateに該当しなければ`TRUE_CONTENT_MISMATCH`)として検出される(=これらの語の有無・置換は「保護」される、数値の質的差[概数か正確な値か]を意味変化として扱う設計になっている)。 |
| range(10–20/between) | 専用処理なし。ハイフンは`normalize_text()`の記号除去で吸収されるため「10-20」も「10 20」も同じトークン列になるが、"between 10 and 20"のような話し言葉との等価性チェックは無い。 |
| 負数 | `xexpnegx`マーカーは指数専用。通常の負の数値(-5等)の話し言葉("minus five"/"negative five")への対応は`normalize_numeric()`に見当たらない。 |
| 電話番号・住所・ID | 専用の「normalize禁止」フラグは無い。数字であれば`_is_number()`(isdigit)で保護対象になるため、桁単位で完全一致が要求される(結果的に意図せず保護されている)。住所の通り種別略語(street→st等)のみ明示的に吸収対象。 |
| acronym/initialism(U.S./US/NASA) | 専用処理なし。ピリオドは一般記号除去で消えるため"U.S."と"US"は`normalize_text()`後に同じトークン("us")になる(意図せず吸収されている)。大文字小文字は全て小文字化されるため、"NASA"と"nasa"の差は元々発生しない。 |
| 所有格・句読点 | アポストロフィは一般記号除去でスペース化される(例: "they're"→"they re"、"re"は`_STOPWORDS`に個別追加済みの既知パッチ、L506)。所有格('s)は同様にスペース化され、'sが独立トークン"s"として残るケースは`_STOPWORDS`に含まれず、内容語扱いされる可能性がある(未検証の残存リスク)。 |
| UNKNOWN時の扱い | Fable案のUNKNOWN分類に相当する現行の終端は`ASR_VALIDATION_UNCERTAIN`(should_pass=False, should_retry=False)。retryを打ち切り、Local Rewrite→Human Review Lockへ進む(3節)。 |
| 既存正常ケースを壊すリスク | OPEN-122 Production wiring時点で既存回帰`run_project_regression.py`は`collected=2112・failed=3(既知の無関係failure)・errors=0`。OPEN-123 Trial時点の正規化専用テストセットは「POSITIVE 29+AMBIGUOUS 2+NEGATIVE 28」の59通り(NEGATIVE 28/28で false accept 0を確認)。これらが現状の「現行PASSケースの分布」を代表する直接的な数字として利用可能(新規Tierを追加する際の回帰基盤として転用できる)。 |

---

## Regression Corpus候補表(証跡付き)

| ケース | canonical(逐語) | ASR(逐語) | 想定分類(Fable案) | 現行実装の挙動 | 証跡パス |
|---|---|---|---|---|---|
| 数値+scale word | "...rose to two point three million dollars, a fifteen percent increase..." | "...rose to $2.3 million, a 15% increase..." | NUMERIC_EQUIVALENCE(要新実装) | `TRUE_CONTENT_MISMATCH`→Local Rewrite失敗→`HUMAN_REVIEW_LOCKED_RETTS_FAILED` | `er020_output/tts_local_rewrite_production_wiring_01/a2/comment_test2_probe.json` |
| 規則的複数形 | "...bring the main point together." | "...bring the main points together." | SAFE_ORTHOGRAPHIC寄り(形態論的等価) | `ASR_VALIDATION_UNCERTAIN`(3回)→cool-down+Local Rewriteで言い換えて解決 | `TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01_REPORT.md` §12.2 |
| 口語的縮約(want to/wanna) | "Don't you want to come with us?" | "Don't you wanna come with us?" | TRANSCRIPT_STYLE_EQUIVALENCE | `TRUE_CONTENT_MISMATCH`(Production採用見送り、2026-09-07決定) | `OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01_REPORT.md` §6 |
| 複合語分かち書き | "drug store" | "drugstore" | SAFE_ORTHOGRAPHIC_EQUIVALENCE | 既に`NORMALIZED_MATCH`(対応不要) | `CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-02_REPORT.md` T2A3 |
| 標準contraction(否定含む) | "don't"等 | 展開形/短縮形 | TRANSCRIPT_STYLE_EQUIVALENCE | `TRANSCRIPT_STYLE_NORMALIZED_MATCH`(Production採用済み) | `er006_preprod_hardening_01_validation.py` L699-1004 |
| 音韻連結(3パターン) | studies/opened/survey等 | study suggests/open to/surveys suggest | CONNECTED_SPEECH | `CONNECTED_SPEECH_ACCEPT`/`_PASS_WITH_WARNING`(Production採用済み) | `er011_b1_connected_speech_validator_01.py` |
| 非ラテン文字誤変換 | 英語Key Phrase句 | CJK等への意味変換 | UNKNOWN寄り(ASR provider言語誤検出、既存分類外) | Cascade+prompt対策でfalse rejection 0%(Key Phrase英語限定) | `CURRENT_SPEC.md` L1331 |
| 対義語誤り(比較方向) | "more/fewer"等の方向 | (TTSがcanonical通りに正しく読み上げ) | PROTECTED_SEMANTIC_MISMATCH(ただし発生源がscript側) | 現行ASR照合層では原理的に検出不能(OPEN-72、script対Source Factの層の問題) | `OPEN_ITEMS.md` OPEN-72 |
| 日本語誤読(参考、逆方向) | "Meta"(辞書確定読み「メタ」) | "メタン" | PROTECTED_SEMANTIC_MISMATCH(false acceptしてはいけない例) | 修正前は偶然一致でfalse accept、修正後`TRUE_CONTENT_MISMATCH`に厳格化 | `DECISION_LOG.md` L9505-9515 |

---

## 参照ファイル一覧(主要)

- `er006_preprod_hardening_01_validation.py`(classify_asr_match本体、normalize_numeric等)
- `er003_audio_tts_asr_safety.py`(旧世代validate_asr_match、TTS入力正規化)
- `er011_b1_connected_speech_validator_01.py`(既存3パターン)
- `er011_connected_speech_equivalence_layer_production_01.py`(OPEN-122 Equivalence Layer)
- `er006_secondary_asr_01.py`(英語Cascade統一エントリ)
- `er020_tts_retry_local_rewrite_01.py`(cool-down/Local Rewrite、role taxonomy SSOT)
- `er011_human_review_lock_01.py`(Human Review Lock状態遷移)
- `TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01_REPORT.md`(2026-09-26実証、$2.3 million/point-points事例)
- `OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01_REPORT.md`
- `OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01_REPORT.md` / `-PRODUCTION-WIRING-01_REPORT.md`
- `CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-01/02_REPORT.md`
- `CURRENT_SPEC.md` L1331(Key Phrase Non-Latin Cascade)、`OPEN_ITEMS.md` OPEN-72/OPEN-122、`DECISION_LOG.md` L9505-9515(メタ/メタン)

---

Management-ID: EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01
