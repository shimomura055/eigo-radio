# KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-PROD-WIRING-01

**管理ID**: KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-PRODUCTION-WIRING-01
**Lane**: Lane A / Key Phrase。**Production配線**(ユーザー2026-09-06 `APPROVED_FOR_PRODUCTION`: 対策(c)=対策(b)逐語書き起こしprompt+対策(a)非ラテン文字時のSecondary再判定Cascade)。**適用範囲は英語Key Phrase経路に限定**、本文segment等の他の英語ASR経路へは展開していない。

---

## 1. 問題(何が問題だったか)

TTSは英語Key Phrase(例: "new normal")を正しく発話しているのに、Primary ASR(OpenAI `gpt-4o-mini-transcribe`、`language="en"`)が「新常態」のような非英語(日本語/中国語相当)の意味変換文字列を返し、Validatorが誤って不合格(false rejection)にする事象がOPEN-119として確定していた(`KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01_REPORT.md`)。既存のSecondary ASR Cascadeは`entity_like`/`homophone_candidate`限定のASR_VALIDATION_UNCERTAINにしか発動せず、この事象の一次分類`TTS_FAILURE`には一度も発動していなかった。対策Trial(`KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-TRIAL-01_REPORT.md`)で、(b) OpenAI ASRへの逐語書き起こしprompt付与、(a) 非ラテン文字主体時のSecondary Cascade拡張、(c) 両者併用がいずれもVALIDATEDとなり、false rejection率がbaseline 57.1%→(c)0.0%(陰性対照false accept 0件)を達成した。

## 2. 何を変更したか

対策(c)を、**英語Key Phrase Component経路(`generate_key_phrase_component_verified`)に限定して**Production配線した。

1. **prompt付与(対策b)**: `er006_asr_provider_routing_01.py::transcribe()`/`_transcribe_openai_mini()`へ`prompt`引数(既定`None`)を追加。`er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict()`へ`asr_prompt`(既定`None`)引数を追加し、`language=="en"`の場合のみ転送。`generate_key_phrase_component_verified()`のPrimary/Fallback両呼び出しのみが、Trialで検証済みの文言(`KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT`、canonical phraseは含めない)を明示的に渡す。
2. **非ラテン文字Cascade(対策a)**: `er006_secondary_asr_01.py`へ`non_latin_dominance_info()`(CJK比率>=0.5[`NON_LATIN_DOMINANT_THRESHOLD`]を非ラテン文字主体と判定)を新設。`evaluate_attempt_with_cascade_detail()`へ`enable_non_latin_cascade`引数(既定`False`)を追加し、真の場合のみ既存Secondary ASR(Azure)を1回追加で呼び再判定する。既存の`entity_like`/`homophone_candidate`限定Cascade条件・数字ゲート・否定ゲート・homophone判定・Connected Speech Validatorの順序は無変更。`generate_key_phrase_component_verified()`のみが`enable_non_latin_cascade=True`を渡す。
3. **記録**: `save_tts_attempt_audio()`のmetadataへ`asr_prompt_applied`/`non_latin_cascade_enabled`/`non_latin_cascade_invoked`/`cascade_invoked`/`cascade_steps`(Secondary raw出力含む)を追加。
4. Master Audio Store cache identity(`MasterAudioKey`)は無変更(ASR設定は音声内容へ影響しないため)。

## 3. 何が改善されるか

英語Key Phrase Componentの生成時、TTSは正しく発話しているのにASRの意味変換により誤ってHuman Review行き/blind TTS retryになっていた事象(false rejection)が、実質的に解消される見込み(Runtime evidenceで陽性2件[new normal/cashless]がいずれもPrimary ASR attempt1でPASS)。同時に、Secondary Cascadeが発動しても実際に不一致であれば依然rejectを維持するため、誤った音声を誤って採用してしまう(false accept)リスクは増えていないことを陰性対照・fixture化テストで確認済み。

## 4. リスクや注意点

- 適用範囲は英語Key Phrase Component経路のみに限定した(既定引数None/Falseで他の全経路は無変更)。本文segment・Point見出し・Preview等への展開は今回行っておらず、必要になった場合は別途ユーザー判断が必要(OPEN_ITEMS.md OPEN-119行に明記)。
- OpenAI ASRの`prompt`引数は公式には厳密な指示追従を保証する仕様ではなく、内部メカニズムは未解明(Trial時からの既知の限界を維持)。
- 非ラテン文字判定はラテン文字だが誤表記("Káslis"等)には対象外(Trialで確認済みの設計上の限界、バグではない)。
- 既知の無関係な既存failure(`er003_test_bad`・`er003_test_p2j_investigate`3件、`er006_asr_provider_routing_01_test.py::test_japanese_routes_to_azure`)は本タスクで発生したものではないことをgit stashでの前後比較・個別実行で確認済み。

---

## 5. 実装詳細

### 5.1 変更ファイル

| ファイル | 変更内容 |
|---|---|
| `er006_asr_provider_routing_01.py` | `transcribe()`/`_transcribe_openai_mini()`へ`prompt`引数(既定`None`)追加 |
| `er006_secondary_asr_01.py` | `non_latin_dominance_info()`/`is_non_latin_dominant_mismatch()`新設、`evaluate_attempt_with_cascade_detail()`/`evaluate_attempt_with_cascade()`へ`enable_non_latin_cascade`(既定`False`)・`detail_out`(既定`None`)引数追加 |
| `er003_v1_repro01_main_generate.py` | `KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT`定数新設、`generate_narration_snippet_verified_strict()`へ`asr_prompt`/`enable_non_latin_cascade`引数追加・`save_tts_attempt_audio()`記録拡張、`generate_key_phrase_component_verified()`のPrimary/Fallback両呼び出しへ新引数を明示的に渡す |
| `er006_secondary_asr_01_test.py` | 9件追加(既存20件は無変更のままPASS) |
| `er006_asr_provider_routing_01_test.py` | 2件追加(既存は無変更) |
| `er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py`(新規) | 5件(適用範囲限定・KP経路配線確認) |
| `er011_tts_attempt_audio_retention_wiring_01_test.py` | 既存3箇所の`fake_evaluate`mockへ`enable_non_latin_cascade`/`detail_out`引数を追加(新規kwargsによる既存テストの回帰を修正) |
| `er011_kp_en_asr_false_rejection_prod_wiring_01_runtime_evidence.py`(新規) | Runtime evidence取得script |

### 5.2 テスト結果

- 新規16件: 全PASS(`er006_secondary_asr_01_test.py`9件、`er006_asr_provider_routing_01_test.py`2件、`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py`5件)。
- 既存回帰: `er006_preprod_hardening_01_validation_test.py`57件PASS、`er008_asr_variant_hardening_15_homophone_en_test.py`6件PASS、`er006_secondary_asr_01_test.py`既存20件PASS、`er011_human_review_lock_01_test_01.py`18件PASS、`er011_tts_attempt_audio_retention_wiring_01_test.py`9件PASS(修正後)、`er011_no18_connected_speech_reading_resolver_wiring_08_test.py`15件PASS(1件は実LLM呼び出しの非決定性により1回目FAIL→2回目PASS、本タスクの変更対象外モジュールのため無関係)、`er007_ja_tts_retry_path_fix_test_01.py`22件PASS。
- `run_project_regression.py`: 変更前(git stash baseline)collected=2104/passed=2101/failed=3、変更後collected=2109(新規5件)/passed=2106/failed=3。失敗3件(`er003_test_bad.FixtureTests.test_case_0`・`er003_test_p2j_investigate`3件中の集計)はbaseline/candidateで完全に同一であり、本タスクによる新規failureはゼロ。

### 5.3 Runtime evidence(Standard同期、実API)

`er011_kp_en_asr_false_rejection_prod_wiring_01_runtime_evidence.py`実行結果:

| ケース | 内容 | 結果 |
|---|---|---|
| 陽性1 | 実Production経路で"new normal"を実TTS生成 | Primary ASR(prompt付き)attempt1で"New Normal"、`status=OK`(Cascade不要) |
| 陽性2 | 実Production経路で"cashless"を実TTS生成 | Primary ASR(prompt付き)attempt1で"Cashless"、`status=OK`(Cascade不要) |
| 陰性 | 既存音声(日本語TTSで「新常態」)を実Cascade関数へ直接投入 | Primary(prompt付き)は`心状態`のまま非ラテン文字優勢→Secondary Cascade実発動→Secondary(Azure)`Xinjio Tai.`も不一致→`verified=False`、reject維持 |

出力先: `er011_output/kp_en_asr_false_rejection_prod_wiring_01/`(`evidence_result.json`、`raw_usage_log.jsonl`、`player.html`)。実測cost: Gemini TTS2回・OpenAI ASR3回・Azure Secondary1回、いずれも短い音声のため合計数円程度。

---

## 6. SSOT更新

- `CURRENT_SPEC.md`: 「英語Key Phrase Component検証: Primary ASR逐語書き起こしprompt+非ラテン文字時のSecondary再判定Cascade(false rejection対策)」行を新規追加(`DECIDED`/`PRODUCTION_WIRED`、適用範囲限定を明記)。
- `DECISION_LOG.md`: `KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-PROD-WIRING-01`エントリを新規追加。
- `OPEN_ITEMS.md`: OPEN-119を`RESOLVED / PRODUCTION_WIRED`へ更新(本文等の他経路への展開は未決事項として引き続き記録)。OPEN-103行へ本対策との関係(OPEN-103の核心はTTS側非決定的誤発音のため対象外、status変更なし)を追記。

## 7. PRODUCTION_WIRED可否の自己判定と懸念

**自己判定**: `PRODUCTION_WIRED`(Gate 3チェックリスト全項目完了)。適用範囲(英語Key Phrase経路限定)・回帰(新規失敗ゼロ)・Runtime evidence(陽性PASS・陰性reject維持)・SSOT更新をいずれも実施・確認済み。

**懸念**: (1) OpenAI ASRの`prompt`引数の効果はサンプル数が限られており(Trial: 陽性7件、本Runtime evidence: 陽性2件)、将来のモデル更新で効果が変動する可能性は排除できない。(2) 本文segment等の他の英語ASR経路にも同種のfalse rejectionが発生しうるが、今回は展開しておらず、発生頻度・費用対効果を見た上で改めてユーザー判断が必要(OPEN_ITEMS.md OPEN-119行に明記)。(3) 非ラテン文字判定の対象外である「ラテン文字だが誤表記」型の失敗モード(cashless「Káslis」等)は、対策(b)のprompt付与のみに依存しており、将来promptが効かないケースが出た場合の追加安全網は今回未実装。
