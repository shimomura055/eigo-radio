# OPEN-121-REPETITION-QA-SYMMETRIC-NORMALIZATION-PRODUCTION-WIRING-01

**管理ID**: OPEN-121-REPETITION-QA-SYMMETRIC-NORMALIZATION-PRODUCTION-WIRING-01
**種別**: Production配線実装(`APPROVED_FOR_PRODUCTION`後のGate 3進行)
**実行者**: sonnet-worker(Fable委任、初回、Git操作禁止)
**日付**: 2026-09-12
**Status**: `APPROVED_FOR_PRODUCTION` + 配線実装済み(**`PRODUCTION_WIRED`ではない**。SSOT[`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`]反映・Git commit/pushは統合タスクで実施予定。Trial-12 A2既存takeのLock状態遷移は未実施、下記5節でSTOPし報告)

---

## 0. 要約

1. ユーザー承認2026-09-12(対称正規化: (i)ハイフン境界の対称正規化 (ii)数詞↔数字0〜999拡張)を`er011_open121_repetition_qa_production_01.py`のProduction正式初回経路(`_normalize_tokens`/`_normalize_token_numeric_equiv`)へ実装した。
2. 全retry/fallback/regeneration呼び出し経路(A-Family標準+fallback、B1 News tail、B-Family 3V)はいずれも同一の`apply_repetition_qa_gate()`→`evaluate_repetition_qa()`→`detect_ngram_repetition()`を通るため、単一module修正で全経路へ反映される(経路差異なし、確認済み)。
3. pin test 2件の期待値を新スコープへ更新、既存35テスト全PASS、RECONCILE-03の8正例+23負例+Trial-12実バグ再現1件(計32件)を回帰テストとして追加、テストファイル計67件全PASS。
4. 遡及Regression(¥0、機械再判定): 実Production incident 4件を特定し、真陽性1件は維持・既存2件の解消は無変化・対象の1件(Trial-12)が新規に解消。新規flagの発生は確認されなかった(23負例含む)。
5. Trial-12 A2 `full_story_part1`の3attempt(標準2回+fallback1回)は、新実装で method_a_ngram の`canonical_repeat_count`が0→2に解消し、method_d/method_d_prime は元々flagged=falseであったため、3件とも`evaluate_repetition_qa().flagged`はTrue→Falseに変わる(runtime evidence、下記7節)。
6. **Lock状態遷移(採用)は未実施**。既存`er011_human_review_lock_01.py`に「音声を再生成せず、QA再判定のみでHUMAN_REVIEW_REQUIRED→RESOLVEDへ遷移させる」正式APIが定義されていないため、委任指示(「Lock状態の遷移方法が既存機構で定義されていなければ、遷移せず報告してSTOP」)に従いSTOPした。過去の類似事例2件(RECONCILE-02の`after two months`、OPEN-127の`do not need`)はいずれも人間側の明示的承認(直接JSON編集の事前ユーザー承認、または`record_human_approval()`)を伴っており、本タスクの委任内にはその同等の明示承認が含まれていない。7節に詳細と、Fable/ユーザーがすぐ実行できる具体的な次アクション案を記載した。
7. 上記6により、A2 Assembly・標準player更新(6節の作業)は未実施(PASS確定=Lock採用後に行う設計のため)。
8. 費用: **¥0**(新規TTS/ASR/API呼び出し一切なし。既存記録の読取・ローカルoffline python実行・既存unittestの実行のみ)。

---

## 1. 実装(Production正式初回path)

対象: `er011_open121_repetition_qa_production_01.py`

- `import er006_preprod_hardening_01_validation as en_validator`を追加(逆方向import不可の懸念は無関係。実地確認: `er006_preprod_hardening_01_validation.py`が直接importするのは`er008_asr_variant_hardening_15_homophone_en`・`er011_b1_connected_speech_validator_01`のみで、いずれも`er011_open121_repetition_qa_production_01`を参照しない。`python -c "import er011_open121_repetition_qa_production_01"`および`er003_v1_n3_01_tts_generate`/`er003_v1_repro01_main_generate`/`er003_v1_crosslevel_audio_02_common`/`er003_v1_sing01_news_tail_fix`の全importが実際にエラーなく成功することを確認済み)。
- 旧`_NUM_WORD_TO_DIGIT_EN`(2〜12専用辞書)を廃止。
- `_dash_unify()`(新規): em/en dash(—/–)は常に空白へ(既存OPEN-127のem dash処理をen dashへ拡張)。ハイフン(-)は英字/数字が隣接する境界のみ空白へ(`(?<=[A-Za-z])-(?=[A-Za-z]|[0-9])`・`(?<=[0-9])-(?=[A-Za-z])`、digit-digit境界["10-15"等の範囲表記]は除外)。
- `_fold_cardinal_words()`(新規、canonical側専用): `en_validator._ONES`/`_TENS`/`_NUM_WORD_VOCAB`/`_words_to_number`を再利用し、連続する数詞語の最大munchを1つの算用数字tokenへ畳み込む(0〜999、"one"は代名詞曖昧性のため対象外)。
- `_normalize_token_numeric_equiv()`(ASR側単一token、拡張): (a)先頭ハイフン/en-dash/em-dashのartifact除去(faster-whisperの複合語分割artifact対策) (b)既存`dq18._normalize_token()` (c)単一token数詞→算用数字(0〜99、"one"除く。100以上はhundred等の複数token構成のためASR側単一token変換の対象外のまま)。
- `_normalize_tokens()`(canonical側、更新): `_dash_unify()`→`text.split()`→`_fold_cardinal_words()`→各tokenへ`dq18._normalize_token()`。
- `_canonical_repeat_count()`・`find_repeated_spans()`・`detect_ngram_repetition()`本体・閾値(`canon_count>=2`)は無変更。
- %/percent同値化・序数(first〜ninety-ninth)は対象外のまま(実装なし、コメントで明記)。

**min_words/span検出への影響**: ASR側`words`のトークン数(word-level ASRの要素数)自体は不変(1トークン→1トークンの文字列変換のみ)。ただしトークンの**内容**が変わるため(例: 先頭ハイフン除去、数詞→算用数字)、`find_repeated_spans()`が「等しい」と判定するトークン対が変化しうる(意図した挙動: 例えば"-hour"と"hour"が新たに等価になる)。canonical側`_normalize_tokens()`の出力トークン数は変化する(ハイフン分割で増加/数詞畳み込みで減少)が、これは`_canonical_repeat_count()`内でのみ使われ、`find_repeated_spans()`(ASR側のみに作用)には影響しない。`METHOD_A_MIN_WORDS=3`自体は無変更。

---

## 2. retry/fallback/regeneration整合(経路確認)

Grepで`er011_open121_repetition_qa_production_01`を参照する全呼び出し元を確認した結果、以下は全て`apply_repetition_qa_gate()`→`evaluate_repetition_qa()`→`detect_ngram_repetition()`という単一経路を共有しており、いずれも今回の修正対象2関数(`_normalize_tokens`/`_normalize_token_numeric_equiv`)を直接使う:

| 呼び出し元 | 用途 |
|---|---|
| `er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict()` | A-Family標準生成(A2/B1本文4segment) |
| `er003_v1_crosslevel_audio_02_common.py::generate_english_segment_with_fallback()` | A-Family fallback(minimal instruction)経路 |
| `er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin()` | B1 News tail wide-margin経路 |
| `er012_b_family_voices_production_01.py`(他Agent成果物、**本タスクでは未編集・未接触**) | B-Family 3V Voices Production |

Human Review Lock(`er011_human_review_lock_01.py::guarded_generate*`)は上記関数を装飾(デコレータ)するだけで、`REGENERATE_APPROVED`による再生成も同じ内部関数を再度呼ぶため、同一経路に自動的に合流する。Secondary ASR Cascade(`er006_secondary_asr_01.py`)はASR一致検証という別レイヤーであり、`verified`の値をrepetition QA gateに渡すだけで、repetition_qa側のtoken正規化とは独立(相互不干渉、既存AND-gate設計のまま)。

**ER-010-NO9の`(?<!-)`との層の違い**: `er003_v1_n3_01_tts_generate.py::tts_safe_number_words_en()`の`(?<!-)`は、TTSへ送る**台本テキスト自体**(canonical_text)を書き換える前処理レイヤーであり、ハイフン複合数("twenty-four"等)は意図的に**変換せず**綴りのまま残す設計(複合数の同値判定はProduction ASR Validator側に委ねる方針、コメント参照)。今回の修正はRepetition QA**内部の比較専用**トークン化であり、canonical_textの実体(TTSへ送られる文字列・音声内容)には一切影響しない。両者は独立した別レイヤーであり、干渉しないことを確認した(`tts_safe_number_words_en()`適用後の実際のcanonical_text["twenty-four-hour"のまま]がRepetition QA側の`_normalize_tokens()`へそのまま渡ることを、Trial-12実データで直接確認済み)。

---

## 3. テスト結果

- pin test 2件(`test_c_hyphen_en_dash_percent_numeric_cases_unchanged`・`test_e_range_boundary_one_twelve_thirteen`)の期待値を新スコープへ更新(更新理由をテスト内コメントに記載)。
- 既存35テスト実行結果: 修正前(実装直後・pin未更新時点)33 PASS / 2 FAIL(想定通りpin 2件のみ)→ pin更新後 **35/35 PASS**。
- 新規回帰テスト追加(`er011_open121_repetition_qa_production_wiring_01_test_01.py`、scratchpadには残さずtestファイルへ直接追加):
  - `SymmetricNormalizationResolvedPositivesTests`(8件、RECONCILE-03 §2「(a)」8パターン)
  - `SymmetricNormalizationNegativesRemainFlaggedTests`(23件、RECONCILE-03 §2「(d)」23負例)
  - `Trial12FullStoryPart1RealBugReplayTests`(1件、Trial-12実データのword-level分割artifactを再現し3attempt型が解消することを直接検証)
- **最終実行結果: 67/67 PASS**(実行時間約100秒、`.venv/Scripts/python.exe -m unittest er011_open121_repetition_qa_production_wiring_01_test_01`)。

---

## 4. 遡及Regression(¥0、機械再判定のみ)

`er011_output/**`・`er012_output/**`配下の全`review_lock_state.json`(46件)を走査し、`last_attempts_log`内で方式A(method_a_ngram)が`flagged=true`だった**実際のProduction incident**(テスト用fixtureではなく実segment)を機械抽出した。実際にRepetition QAがflagしAPI消費に影響した記録は以下4パターンに集約される(重複除去済み):

| span_text(抜粋) | segment | 旧canon_count | 新canon_count(今回実装、実関数で再計算) | 分類 |
|---|---|---|---|---|
| "A wash is not just clean or dirty." | towels_trial_11/a2 point_two | 1 | **1(不変)** | **flag維持(真陽性)** — 実際のTTS重複バグ(false-start型)、影響なし |
| "after two months." | towels_trial_11/b1b full_story_part2 | 0(当時) | **2(不変)** | 既存OPEN-121 RECONCILE-02修正(2026-09-12早期)により既に解消済み。今回の修正でも変化なし(現状維持を確認、退行なし) |
| "24 -hour day." | wake_before_alarm_trial_12/a2 full_story_part1 | 0 | **2** | **flag消失(false positive解消、今回の対象バグ)** |
| "do not need" | editorial_b_family_production_phase1_02/b1b point_two | 1(当時) | **2(不変)** | 既存OPEN-127修正(em dash、2026-09-08)により既に解消済み。今回の修正でも変化なし(退行なし)。**注記**: このsegmentは最終的に`record_human_approval()`(人間試聴承認)経由でPRODUCTION_WIREDされており、`review_lock_state.json`自体はHUMAN_REVIEW_REQUIRED表示のまま(human_approved_segments.jsonが優先される既存仕様どおりで、これはバグではない)。 |

**3区分まとめ**:
- **flag消失(false positive解消)**: 1件(Trial-12 `full_story_part1`)。
- **flag維持(真陽性)**: 1件("A wash is not just clean or dirty."、towels A2 point_two)。**真陽性は消えていない**(退行なし)。
- **新規flag**: 0件(上記4件のいずれも新規にflagされるようにはなっていない。また3節の23負例回帰テストで、ハイフン複合語・digit-digit範囲・序数・%/percent無関係文脈のいずれも誤PASSしない[=不必要な新規flag解消も発生しない]ことを確認済み)。

**スコープの正直な限界**: `review_lock_state.json`(実際にHuman Review Lockへ到達した実incidentのみ記録)を走査対象としたため、Lockへ到達しなかった(即PASSした)過去のflag候補や、方式D/D'由来のflag(方式Aとは無関係)は本表の対象外。より広い`tts_generation_results.json`全文走査(構造が記事ごとに異なるため`canonical_text`との機械的な対応付けが不安定)は、RECONCILE-03が既に同等の分析を実施済み(6パターン、同じ結論)であり、本タスクでは実Production incidentに絞った再検証とした。

---

## 5. Trial-12 A2再判定(¥0、既存記録のみ使用、再ASR不要)

`er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/audit/tts_generation_results.json`の`full_story_part1`(標準attempt1・attempt2・fallback attempt1、計3件、いずれもASRテキスト完全一致)を、実際の記録(canonical_text・span_text・method_d/method_d_prime評価結果)を用いて新実装で再判定した。

| attempt | 旧method_a canon_count | 新method_a canon_count | method_d flagged(旧=新、無変更) | method_d_prime flagged(旧=新、無変更) | 統合flagged(evaluate_repetition_qa相当) |
|---|---|---|---|---|---|
| standard attempt1 | 0 | **2** | False | False | 旧True → **新False** |
| standard attempt2 | 0 | **2** | False | False | 旧True → **新False** |
| fallback attempt1 | 0 | **2** | False | False | 旧True → **新False** |

3件とも`verified`を決めるASR一致検証(`audio_classification: NORMALIZED_MATCH`)は元々True相当であり、`verified=False`だった唯一の原因はrepetition_qa gate(method_a)であったことをコード追跡で確認済み(`er003_v1_repro01_main_generate.py`のAND-gate順序: cascade一致→disfluency gate[この経路では無効]→repetition_qa gate)。したがって新実装では**3attemptとも`verified=True`となり、Lockが到達しなければstandard attempt1の時点で即座に`status=OK`確定していたはずの状況**である。

**Lock状態遷移: 未実施(STOP)**

`er011_human_review_lock_01.py`には、「音声を再生成せず、既存の録音済みaudioに対する事後のQA再判定のみでHUMAN_REVIEW_REQUIRED→RESOLVEDへ遷移させる」ための正式APIが存在しない(`record_outcome()`は実際の生成呼び出し[`result`引数]と対で使う設計、`approve_regenerate()`は「次の1回の呼び出しに限り再生成を許可する」設計であり、いずれも「オフラインでの再判定のみでの遷移」を想定していない)。

過去の類似ケース2件を確認したところ、いずれも人間側の明示的な関与を伴っていた:
- `OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01`(`after two months.`): ユーザーの**事前承認**(「内容一致しているtakeが新QAでPASSするなら、ユーザー試聴は不要」)に基づき、Sonnetが`review_lock_state.json`を直接RESOLVEDへ編集し、最初にPASSした取りを採用した。
- OPEN-127(`do not need`): ユーザーが実際に音声を確認したうえで、既存`record_human_approval()`(人間承認記録API)経由で承認された。

本タスクの委任指示には、上記いずれかに相当する明示的な承認(Trial-12 A2に対する「試聴不要」の事前承認、または人間による試聴結果)が含まれていない。委任指示自体が「Lock状態の遷移方法が既存機構で定義されていなければ、遷移せず報告してSTOP」と明記しているため、これに従い**Lock状態遷移(採用)を実施していない**。

**Fable/ユーザーへの次アクション案(すぐ実行可能、¥0)**: 上記表の再判定結果(3attemptともflagged解消)を踏まえ、以下のいずれかをご判断いただければ、次のタスクで即座に完了できる。
- (a) 過去のRECONCILE-02と同様の「内容一致takeは試聴不要」を今回にも適用してよいと明示的にご承認いただく → `review_lock_state.json`の`full_story_part1`エントリを`RESOLVED`へ更新し、`attempts/full_story_part1_attempt1_custom35d6860b.wav`(標準attempt1、最初にPASSした取り)を`narration/full_story_part1.wav`へ複製(TTS/ASR再実行なし、¥0)。
- (b) 実際にattempt1の音声を試聴確認のうえ、既存`record_human_approval()`経由で承認する。

---

## 6. A2 Assembly・標準player更新

上記5節でLock状態遷移(採用)が未確定のため、**未実施**。5節の(a)または(b)が確定次第、`er003_v1_n3_01_assemble.py`のstage_assemble/Audio Validation Gate、および`er011_wake_before_alarm_trial12_std_player_01.py`(標準player再生成)を実行する準備は整っている(追加TTS/ASRは不要な見込み)。

---

## 7. Gate 3 Production Wiring Checklistとの対応

| # | 項目 | 状態 |
|---|---|---|
| 1 | Production正式初回経路への実装 | 完了(1節) |
| 2 | retry・fallback・regenerationとの整合 | 完了(2節、全経路が単一関数を共有することを確認) |
| 3 | DEV・Trial-onlyではないこと | 該当(Production正式module本体への直接実装、Trialコードではない) |
| 4 | Production runtimeでの実発火 | **部分的**(Trial-12 A2の既存3attemptに対するoffline再判定[¥0]では実証。実際のTTS/ASR runtime新規発火は今回未実施[不要と判断、既存記録のみで十分な実証と考えるが、Fable判断を仰ぐ]) |
| 5 | 必要testのPASS | 完了(67/67、3節) |
| 6 | runtime evidence | 完了(7節[本節]・5節の表) |
| 7 | 実際のmodel_id・routing確認 | 該当なし(TTS/ASRのroutingは無変更、ローカル正規化ロジックのみの変更のため) |
| 8 | コスト影響評価 | 完了(¥0、下記) |
| 9 | `CURRENT_SPEC.md` | **未反映**(統合タスクで実施予定、末尾に追記文案) |
| 10 | `DECISION_LOG.md` | **未反映**(統合タスクで実施予定) |
| 11 | `OPEN_ITEMS.md` | **未反映**(統合タスクで実施予定、末尾に追記文案) |
| 12 | 必要なGit反映 | **未実施**(本タスクはGit操作禁止。統合タスクで実施予定) |
| 13 | approved specとProduction挙動の一致 | 完了(実装がユーザー承認範囲[(i)ハイフン境界対称化 (ii)0〜999拡張、%/percent・序数は対象外]と一致することをテストで確認) |
| 14 | Dangling Reference Check | 完了(新規importは既存Production稼働中module`er006_preprod_hardening_01_validation`のみ。未承認・Trial-only仕様への参照なし) |

---

## 8. 費用(5区分)

1. **今回実測**: ¥0
2. **Trial特有の追加コスト**: ¥0(該当なし)
3. **異常retry・Human Review由来の上振れ**: ¥0
4. **Standard同期でのコスト**: ¥0(新規TTS/ASR呼び出しなし)
5. **Batch量産換算時のコスト**: ¥0(同上)

すべて既存記録の読取・ローカルoffline python実行(正規化関数の再計算、unittest実行)のみ。

---

## 9. 変更ファイル一覧

- `er011_open121_repetition_qa_production_01.py`(Production本体、+123/-24行相当、1節参照)
- `er011_open121_repetition_qa_production_wiring_01_test_01.py`(pin test 2件更新+回帰テスト32件追加、+320/-24行相当、3節参照)

他ファイルへの変更・stageは一切行っていない(`git status --short`で上記2ファイルのみが本タスクによる変更であることを確認済み。他agentによる並行変更[`CURRENT_SPEC.md`等]は本タスクと無関係)。

---

## 10. CURRENT_SPEC.md追記文案(統合タスクが転記、OPEN-121行の末尾へ追加)

> **追記(2026-09-12、OPEN-121対称正規化[ハイフン境界+0〜999拡張])**: `_normalize_tokens()`(canonical側)・`_normalize_token_numeric_equiv()`(ASR側)を、(i)ハイフン境界の対称正規化(em/en dashは常に空白、ハイフンは英字/数字が隣接する境界のみ空白、digit-digit境界["10-15"等の範囲表記]は除外)+(ii)数詞↔算用数字の同値化を2〜12専用辞書から0〜999へ拡張(Production既承認・稼働中のASR Validator実装[`er006_preprod_hardening_01_validation.py`の`_ONES`/`_TENS`/`_words_to_number`]を再利用、重複実装なし)、へ置き換えた。判定閾値(`canonical_repeat_count>=2`)・方式D/D'の閾値自体は無変更。%/percent同値化・序数(first〜ninety-ninth)は引き続き対象外(実例なし、範囲拡張は別途判断待ち)。ユーザー`APPROVED_FOR_PRODUCTION`(2026-09-12)、実装・回帰テスト67件PASS済み。Trial-12 A2既存take(3attempt)は再判定によりflagged解消を確認したがLock状態遷移は未実施(既存機構に該当APIなし、ユーザー/Fable確認待ち)のため`PRODUCTION_WIRED`は未宣言。詳細は`OPEN-121-REPETITION-QA-SYMMETRIC-NORMALIZATION-PRODUCTION-WIRING-01_REPORT.md`参照。

## 11. OPEN_ITEMS.md OPEN-121行追記文案(統合タスクが転記)

> **追記(2026-09-12、対称正規化Production配線実装)**: RECONCILE-03「修正1回目」で設計・検証した対称正規化(ハイフン境界+数詞0〜999拡張)をProduction本体へ実装し、67テスト全PASS・遡及Regression(真陽性1件維持・新規flag0件・対象1件[Trial-12 `24-hour day`]解消)・Trial-12 A2既存3attemptの¥0再判定(canon_count 0→2、flagged解消)まで完了した(`OPEN-121-REPETITION-QA-SYMMETRIC-NORMALIZATION-PRODUCTION-WIRING-01_REPORT.md`)。残課題: (1)Trial-12 A2既存takeのHuman Review Lock状態遷移(採用)方法が既存機構に定義されておらず`USER_DECISION_REQUIRED`(RECONCILE-02/OPEN-127の precedent同様、明示的なユーザー試聴不要承認または実試聴承認が必要)、(2)A2 Assembly・標準player更新は(1)確定後、(3)SSOT([CURRENT_SPEC.md]/[DECISION_LOG.md]本行)・Git反映は統合タスクで実施予定。
