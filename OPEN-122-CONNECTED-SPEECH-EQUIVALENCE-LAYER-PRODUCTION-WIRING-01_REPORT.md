# OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01

管理ID: OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01。
Lane: Lane A。種別: Production配線(ユーザー2026-09-07`APPROVED_FOR_
PRODUCTION`: 範囲=**A2/B1英語本文segmentのProduction正式ASR/Validator
経路のみ**。Key Phrase・日本語segment・Trial専用path・他用途は対象外)。
到達Status: **コード実装・Runtime evidence・回帰いずれも完了。Git操作は
未実施**(Lane B Trial-09がcommit権保持中のため、本タスクではcommitして
いない。Fableの統合commit後に`PRODUCTION_WIRED`を正式宣言する)。

採用元: `CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-01/02_
REPORT.md`(いずれも`VALIDATED`)。判定ロジック(既存3パターンValidatorの
UNCLASSIFIED後段、ARPAbet音韻環境カテゴリA〜G+独立ASR corroboration必須、
単一証拠のみでは絶対にacceptしない)はTrialから無変更で移植した。

---

## 1. 配線箇所

新規[er011_connected_speech_equivalence_layer_production_01.py](er011_connected_speech_equivalence_layer_production_01.py)
(Trial-01/02のPart1〜3を無変更で移植、テスト/コスト計測ハーネス等の
Trial固有コードは含めない)。

配線先: `er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail()`
(既存Cascade層、既存3パターンValidator`er011_b1_connected_speech_
validator_01.py`のUNCLASSIFIED fallthrough後段)。新規opt-inフラグ
`enable_connected_speech_equivalence_layer`(既定`False`、既存OPEN-119の
`enable_non_latin_cascade`と同一の設計パターン)を追加した。

判定フロー: `classify_asr_match()`がTRUE_CONTENT_MISMATCHかつ
`protected.passed`(数字/否定の真の不一致ではない)の場合のみ、まず
Secondary/local ASR無しの安価な事前判定(音韻環境カテゴリ該当有無のみ、
`NEVER_ELIGIBLE_JUDGMENTS`)を行い、候補である場合のみSecondary Azure
(既存`get_full_text_via_azure_stt_with_phrase_list`を再利用)+local
faster-whisper(既存`er008_disfluency_qa_18.transcribe_verbatim`を再利用、
無料)を1回ずつ追加実行してcorroboration判定する。corroboration>=1件かつ
カテゴリA/B/Cは新規classification`CONNECTED_SPEECH_EQUIVALENCE_ACCEPT`、
D/E/F/Gは`CONNECTED_SPEECH_EQUIVALENCE_PASS_WITH_WARNING`(いずれも
`should_pass=True`、`er006_preprod_hardening_01_validation.
VALID_CLASSIFICATIONS`へ追加)。corroboration 0件・独立ASR同士が食い違う
場合は非accept(既存`TRUE_CONTENT_MISMATCH`を維持、診断情報のみ
`connected_speech_info`へ付与)。

適用範囲の限定(opt-inフラグを明示的に`True`で渡す箇所のみ):
- `er003_v1_n3_01_tts_generate.py::generate_b1_segments()`
  (`full_story_part1`/`full_story_part2`/`point_one`/`point_two`ループ)
  → `er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin()`
- `er003_v1_n3_01_tts_generate.py::generate_a2_segments()`(同4segment)
  → `generate_a2_segment_with_slowdown()`
  → `er003_v1_crosslevel_audio_02_common.py::generate_english_segment_with_fallback()`
  (標準path・fallback[minimal instruction]pathの両方)
  → `er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict()`

いずれも最終的に`er006_secondary_asr_01.py::evaluate_attempt_with_cascade()`
へ到達する。既定`False`のため、引数を渡さない全既存呼び出し元
(Key Phrase・日本語・comment/preview/title/in_one_line等)は無変更。

**配線しなかった箇所(スコープ外、正直に記録)**: A2の6% time-stretch後
独立再検証経路(`apply_a2_slowdown_postprocess`、`classify_asr_match()`を
直接呼ぶだけの別コードパスでCascadeを経由しない)には今回配線していない。
既存のslowdown retry機構(最大3回の取り直し)で吸収されるため安全上の
懸念は低いが、Layerの恩恵を受けない既知のギャップとして記録する。

---

## 2. A2 runtime evidence(Standard同期、実API)

OPEN-112 Theme2診断の保全音声("showed strong"、`point_two_attempt1_
custom35d6860b.wav`)+既知のPrimary ASR結果("show strong"の誤書き起こし)
を、修正後のProduction Cascade関数`evaluate_attempt_with_cascade()`へ
実際に投入した。

| 項目 | 結果 |
|---|---|
| classification | `CONNECTED_SPEECH_EQUIVALENCE_ACCEPT` |
| should_pass / verified | True / True |
| カテゴリ | A(final_stop_weakening_unreleased)/B(alveolar_stop_reduction)/C(homorganic_consonant_fusion) |
| Secondary ASR(Azure、実呼び出し) | "...still **showed** strong interest..."(canonical支持) |
| local ASR(faster-whisper、実呼び出し) | "...still **showed** strong interest..."(canonical支持) |
| corroboration_count / contradiction_count | 2 / 0 |

証跡: `er011_output/open122_connected_speech_equivalence_layer_production_
wiring_01/gate3_a2_flagship_result.json`、実行script
`gate3_a2_flagship_runtime_evidence.py`(同ディレクトリ)。

---

## 3. B1 runtime evidence(Standard同期、実API)

### Part A: B1実本文1件を実生成(通常時のLayer不介入確認)

既存承認済みhanshinテーマ`point_two_body`("Hanshin did not depend only
on its early lead...")を、修正後の`news_tail_fix.generate_news_narration_
wide_margin(..., enable_connected_speech_equivalence_layer=True)`で
Standard同期TTS実生成した。

| 項目 | 結果 |
|---|---|
| status | OK |
| audio_classification | `NORMALIZED_MATCH`("pinch hitter"/"pinch-hitter"のハイフン表記差のみ、既存正規化で吸収) |
| connected_speech_info | None(Layer不発火) |

Equivalence Layerは通常のexact/normalized matchでは一切介入しないことを
実生成で確認した(出力: `gate3_b1_real_generation_point_two_body.wav`、
既存Production narrationファイルは上書きしていない)。

### Part B: 合成fallthrough(Trial-01実音声再利用、ACCEPT確認)

Trial-01の実音声`P6_dont_you.wav`("Don't you want to come with us?"の
実発話、"want"の実際の発話音声を含む)を再利用し、canonical文字列は実音声
どおり、Primary ASR文字列のみ意図的に"want"→"wan"(語末/t/脱落)へ
差し替えた合成mismatchを構成した。Secondary/local ASRは実音声への実際の
ASR実行結果(fabricatedなのはPrimary ASR文字列のみ)。

| 項目 | 結果 |
|---|---|
| classification | `CONNECTED_SPEECH_EQUIVALENCE_ACCEPT` |
| カテゴリ | A/B/C/F |
| Secondary ASR(実呼び出し) | "Don't you **want** to come with us?"(canonical支持) |
| local ASR(実呼び出し) | "Don't you **want** to come with us?"(canonical支持) |
| corroboration_count | 2 |

証跡: `gate3_b1_part_a_real_generation_result.json`、
`gate3_b1_part_b_synthetic_fallthrough_result.json`、実行script
`gate3_b1_runtime_evidence.py`。

---

## 4. true mismatch非acceptの証拠(false accept 0/2)

Trial-01 N1(claimed canonical "showed"、実発話"show"、flagshipと同一
音韻環境の最も厳しい敵対的陰性対照)とTrial-02 T2N4(claimed canonical
"turned"、実発話"turn"、SecondaryがcanonicalをMIXEDに誤支持する陰性
対照)を、実音声+実際のProduction Cascade経路(Secondary/local ASRとも
実呼び出し)へ投入した。

| id | classification | should_pass | 備考 |
|---|---|---|---|
| N1_show_not_showed | `TRUE_CONTENT_MISMATCH` | False | Secondary/localとも実際に"show"を支持、corroboration 0件で`EQUIVALENCE_LAYER_INSUFFICIENT_EVIDENCE` |
| T2N4_turn_not_turned | `TRUE_CONTENT_MISMATCH` | False | Secondaryが誤ってcanonical側"turned"を支持したが、localが実発話"turn"を正しく支持し`EQUIVALENCE_LAYER_MIXED_EVIDENCE_INSUFFICIENT`で安全側停止 |

証跡: `gate3_negative_control_result.json`、実行script
`gate3_negative_control_runtime_evidence.py`。

---

## 5. retry/fallback/Human Review整合

- classify_asr_matchのTRUE_CONTENT_MISMATCH判定自体は変更していない
  (Equivalence Layerは既存の`ClassificationResult`をラップし直すのみ)。
  accept未達の場合、should_pass/should_retryは元のまま(既存TTS blind
  retryへ委ねる)。
- 既存Cascade eligibility判定(`is_entity_like_mismatch`/`is_homophone_
  candidate_mismatch`、classification=="ASR_VALIDATION_UNCERTAIN"限定)
  には一切影響しない(Equivalence Layerが介入するのはTRUE_CONTENT_
  MISMATCHのケースのみで、既存4-step cascadeとは独立した別分岐)。
- `review_lock.guarded_generate`・`REGENERATE_APPROVED`・Minimal
  instruction fallback・Cost Guardはいずれも既存のまま無変更。B1実生成
  (§3 Part A)・合成fallthrough検証(§3 Part B)とも、既存の
  `@review_lock.guarded_generate("en")`でguardされた実関数を直接呼んで
  おり、実際にこれらの機構を経由した。
- Human Review: accept未達(corroboration 0件・MIXED_EVIDENCE等)の場合、
  既存の`should_stop_retrying`/Cascade eligibility判定を経て、従来通り
  Human Reviewキューへ到達しうる経路は変更していない。

---

## 6. Regression

`run_project_regression.py`(canonical entry point): collected=2112、
passed=2109、failed=3、errors=0。failed 3件は本タスク以前から存在する
既知の無関係failure(`er003_test_bad`の意図的self-check・`er003_test_
p2j_investigate`のOPEN-77既知meta-test集計、いずれもConnected Speech/
ASR/音声Validatorとは無関係な別ドメインのfixtureであることをソース確認
済み)。**Lane A方針(Git操作禁止)によりgit stashでの前後比較は実施して
いない**(代わりにソースコード内容の確認[両ファイルとも音声/ASR系コードを
一切参照しない、テスト件数集計・意図的self-checkのみ]で無関係性を確認)。

直接実行で確認した関連テスト(регression glob patternに含まれない、
`_test.py`終端のファイル4件を含む):

| ファイル | 件数 | 結果 |
|---|---|---|
| `er006_preprod_hardening_01_validation_test.py` | 57 | 全PASS |
| `er006_secondary_asr_01_test.py` | 29 | 全PASS |
| `er011_no18_connected_speech_reading_resolver_wiring_08_test.py` | 15 | 全PASS |
| `er011_tts_attempt_audio_retention_wiring_01_test.py` | 9 | 全PASS(mock signature更新後) |
| `er011_human_review_lock_01_test_01.py` | 18 | 全PASS |
| `er007_ja_secondary_asr_01_test.py` | 9 | 全PASS |
| `er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py` | 5 | 全PASS(mock signature更新+新規assertion追加後) |
| 新規`er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py` | 16 | 全PASS |

**新規kwargs追加に伴う既存test修正**: `evaluate_attempt_with_cascade`/
`evaluate_attempt_with_cascade_detail`へ`enable_connected_speech_
equivalence_layer`引数を追加したことで、この関数を固定シグネチャの
`fake_cascade`/`fake_evaluate`でmonkeypatchしていた既存test 2ファイル
(`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_
01.py`・`er011_tts_attempt_audio_retention_wiring_01_test.py`)が
`TypeError`で一時的に破損した。両ファイルのmock signatureへ新規kwargを
追加し(既存の`enable_non_latin_cascade`追加時と同じ対応パターン)、
KP経路が新規フラグを一切渡さないことを確認するassertionも追加した。

**既知の回帰カバレッジ上の観察(既存・本タスクで発見、隠さず記録)**:
`run_project_regression.py`のglob pattern(`er0*_test_*.py`)は、
`_test.py`で終わる(`_test_XX.py`ではない)ファイル名を収集しない
構造的な既存gapがあり、上表の一部ファイルはこのpatternに含まれない
(今回は個別に直接実行して確認した)。本タスクのスコープ外のため
修正していない。

---

## 7. model_id・ASR routing evidence

- Primary ASR: `gpt-4o-mini-transcribe`(既存`er006_asr_provider_
  routing_01.py`、変更なし。A2 Flagship evidenceでは既知の実データを
  再利用、B1実生成では実際にこのmodel_idで呼び出したことをcost logで
  確認)。
- Secondary ASR: `azure-speech-stt`(既存`get_full_text_via_azure_stt_
  with_phrase_list`、変更なし。全evidence run共通で実際に呼び出し、
  `er011_output/open122_connected_speech_equivalence_layer_production_
  wiring_01/gate3_*_raw_usage_log.jsonl`に`provider=azure`で記録)。
- local ASR: faster-whisper `small`モデル、CPU実行(既存`er008_
  disfluency_qa_18.transcribe_verbatim`を再利用、新規外部依存なし、
  無料)。

Cost実測合計(全evidence run): **¥3.34**(gemini TTS 1件¥1.40・openai_asr
1件¥0.07・azure 4件¥1.87、local faster-whisperは無料)。TTS実行mode
は明示的に`TTS_EXECUTION_MODE=STANDARD`を指定(既定Batch modeでは
ポーリングに時間がかかるため、タスク仕様の「Standard同期」要件に従った)。

---

## 8. SSOT更新箇所

- `CURRENT_SPEC.md`: 最終更新ヘッダへ新規エントリ追加。「Audio
  Production Pipeline」節の「B1 Connected Speech Validator」行の直後へ
  新規行「Connected Speech Equivalence Layer(OPEN-122...)」追加
  (status: `APPROVED_FOR_PRODUCTION`(範囲限定)/`PRODUCTION_WIRED`候補
  [commit後に確定])。
- `DECISION_LOG.md`: 最終更新ヘッダへ新規エントリ追加。「参照元」節
  直前へ新規セクション`## OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-
  PRODUCTION-WIRING-01`追加。
- `OPEN_ITEMS.md`: OPEN-122行を更新(既存Trial-01/02の記録は保持しつつ、
  Production wiring追記。status`USER_DECISION_REQUIRED`→`CODE_COMPLETE_
  PENDING_COMMIT`。Key Phrase展開は引き続き`USER_DECISION_REQUIRED`の
  未決事項として残す)。

---

## 9. Key Phraseが範囲外である証拠

- `er003_v1_repro01_main_generate.py::generate_key_phrase_component_
  verified()`のPrimary/Fallback両呼び出しが、新規kwarg`enable_
  connected_speech_equivalence_layer`を一切渡していないことをソース
  コード直接確認(`inspect.getsource`によるテスト、`test_generate_
  key_phrase_component_verified_does_not_pass_flag`)。
- `er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_
  01.py`(既存KP wiringテスト)へ、KP実呼び出し相当のcall_logに
  `enable_connected_speech_equivalence_layer`キー自体が存在しないこと
  (`assertNotIn`)、および`enable_non_latin_cascade=True`のKP的な
  呼び出しでも同フラグが`False`のまま(`assertFalse`)を確認する
  assertionを追加。
- 新規テスト`test_key_phrase_style_call_without_flag_stays_unaffected`
  (KP経路の実呼び出しパターン[`enable_non_latin_cascade=True`]を模しつつ
  Equivalence Layerフラグを渡さない場合、Secondary/local ASRの追加
  呼び出しが一切発生しないことを直接確認)。
- 日本語経路(`er007_ja_secondary_asr_01.py`)が本Equivalence Layer
  モジュールを一切importしていないことをソースコード直接確認
  (`test_japanese_cascade_module_independent_of_equivalence_layer`)。

---

## 10. Git

**未実施**。タスク仕様によりLane B(`er012_*`)Trial-09がcommit権を
保持中のため、本タスクではコード変更・テスト追加・Runtime evidence
取得のみを行い、commit/pushは一切行っていない。Fableが統合commitを
行った後に`PRODUCTION_WIRED`を正式宣言する。

### 変更ファイル一覧(新規)

- `er011_connected_speech_equivalence_layer_production_01.py`(新規、
  Production判定ロジック本体)
- `er011_connected_speech_equivalence_layer_production_wiring_01_test_
  01.py`(新規、単体テスト16件)
- `OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01_
  REPORT.md`(本ファイル)
- `er011_output/open122_connected_speech_equivalence_layer_production_
  wiring_01/`配下(Runtime evidence一式: 実行script3件・結果json・
  usage log・実生成wav1件)

### 変更ファイル一覧(既存編集)

- `er006_secondary_asr_01.py`(Equivalence Layer配線本体、新規opt-in
  フラグ・local ASRヘルパー・eligibility事前チェック)
- `er006_preprod_hardening_01_validation.py`(`VALID_CLASSIFICATIONS`
  へ新規ラベル2件追加、コメントのみ)
- `er003_v1_repro01_main_generate.py`(`generate_narration_snippet_
  verified_strict`へ新規kwarg追加・転送)
- `er003_v1_crosslevel_audio_02_common.py`(`generate_english_segment_
  with_fallback`へ新規kwarg追加・標準/fallback両経路へ転送)
- `er003_v1_sing01_news_tail_fix.py`(`generate_news_narration_wide_
  margin`へ新規kwarg追加・転送)
- `er003_v1_n3_01_tts_generate.py`(`generate_a2_segment_with_slowdown`
  へ新規kwarg追加・転送、A2/B1本文4segmentループでのみ`True`を明示的に
  渡すよう変更)
- `er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_
  01.py`(mock signature更新、KP範囲外assertion追加)
- `er011_tts_attempt_audio_retention_wiring_01_test.py`(mock signature
  更新のみ)
- `CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`(SSOT更新)

---

## 11. 新規USER_DECISION_REQUIRED

新規のUSER_DECISION_REQUIREDは発生していない。既存のOPEN-122行に記録
済みの未決事項(Key Phrase経路への展開可否、カテゴリD/E/F/Gの実運用
頻度の継続観察、position-based corroboration比較の頑健性の追加検証、
A2 slowdown後再検証経路への展開要否)を、Production wiring後の状態へ
更新して維持した(いずれも未実装・ユーザー承認なしに実装しない)。

---

## 12. 懸念事項(正直に記録)

1. **A2 6% time-stretch後再検証経路は未配線**(§1で既述)。time-stretch
   自体がまれにASR誤認識を誘発することが既存コードコメントに記録されて
   おり、この経路でconnected-speech型のfallthroughが起きた場合は
   Equivalence Layerの恩恵を受けず、既存のslowdown retry(最大3回)へ
   委ねられる。安全側(過剰な再TTSで対処)ではあるが、コスト効率の観点
   では改善余地がある。
2. **自然発生の救済例は引き続きFlagship 1件のみ**(Trial-01/02からの
   既知の限界を継続)。今回のB1実生成(§3 Part A)でも新規の自然発生
   fallthroughは発生しなかった(NORMALIZED_MATCHで通常合格)。Production
   配線後の実運用頻度は、今後の実記事生成を通じて継続観測が必要。
3. **回帰カバレッジの構造的gap**(§6で既述、既存の`run_project_
   regression.py`のglob patternが一部`_test.py`終端ファイルを収集しない
   既知の問題)。本タスクのスコープ外のため未修正、報告のみ。
