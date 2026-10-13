# A. 既存「連結発音」対策の徹底監査 (委任_03、費用JPY0、Production無変更)

出典(重複調査せず再利用): `melos/cs_audit_01/CS_AUDIT_01.md`、`melos/asr_root_cause_01/ROOT_CAUSE_01.md`、委任_01 `TRIAL_REPORT_01.md` A-1表。
行番号は2026-10-13時点の現行ファイルをGrepで再照合した。**未回答だった点(7番の音韻水準の説明可否、5番の落ちた判定条件の具体行、固有名詞以外の一般語での実データ)だけを新規に埋めた**。
承認済み基本原則: 「自然な英語で、子音が連続することにより一方の音が融合・弱化・脱落し得る場合、その音韻構造を診断し、正常な連結発音で説明できるなら許容する。ただし文脈によるASRの推測だけを根拠に自動PASSしない。」

## A-1. 5機構 x 8点の回答表

凡例: コード位置は `file:line`。「Melos run_e2e_02」はFamily Z Melos案件(Std a2 / Adv b1b の `full_story_part1_c5` = `Melos said.`)。

| 点 | M1 Connected Speech Validator (Pattern A/B/C, OPEN-107/110) | M2 Connected Speech Equivalence Layer (OPEN-122) | M3 固有名詞・音韻照合 (Pronunciation Resolver/Ledger, CMU Case A) | M4 Secondary ASR Cascade (Tier3 Azure corroboration) | M5 English ASR Semantic Equivalence Layer (er021, OPEN-186/123) |
|---|---|---|---|---|---|
| 1 正式Productionに存在するか | あり。`er011_b1_connected_speech_validator_01.py` `classify_connected_speech` (Pattern A L151 / B L166 / C L181)。CURRENT_SPEC L2025(3パターン限定「一般化しない」) | あり。`er011_connected_speech_equivalence_layer_production_01.py` (`phoneme_prefix_drop` L142 / 本体 L215)。CURRENT_SPEC L2026、OPEN-122 `PRODUCTION_WIRED`(commit 3297d1b、2026-09-07、5 role) | あり。`er006_pronunciation_ledger_01.py` / ledger.json、`er006_secondary_asr_01.py` `_step_alternate_pass` L423(CMU Case A) | あり。`er006_secondary_asr_01.py` `evaluate_attempt_with_cascade` L347 / `_detail` L464、Tier3 L601-660 | あり。`er021_en_asr_semantic_equivalence_production_01.py`、`classify_asr_match` 内蔵。CURRENT_SPEC L2019 |
| 2 初回/retry/fallback/減速後再検証/Local Rewrite への配線 | `classify_asr_match`(`er006_preprod_hardening_01_validation.py` L1076 `non_entity_diffs` 時、L1119 最終fallback)から呼ばれるため **ASRを分類する全経路で有効**(初回・retry・fallback・cascade各step・減速後 `_post_slowdown_cascade_rescue`・LR後QA)。role非依存 | 初回/retry/fallback/cascadeは配線(`enable_connected_speech_equivalence_layer`)。**減速後 `_post_slowdown_cascade_rescue` には未配線(OPEN-122(4)既知Gap、OPEN-328)**。Dialogue本文は `segment_id` 非伝播でTier3/role gatingが効かない(OPEN-322) | 初回/retry/fallback/cascade(Phrase List供給)/減速後(`get_hint_for_text`)に配線。TTS注入は信頼度`high`のみ(Melosは`low`=注入対象外) | 初回UNCERTAIN→cascade(Adv: UNCERTAINで即cascade→LR→HR / Std: fallback+cooldown+減速)。減速後は `_post_slowdown_cascade_rescue`(是正済み eb4c6479)。LR自体にはcascade無し(LR後QAは別) | `classify_asr_match` 内で全経路共通(OPEN-123/186、英語ASR照合経路全体) |
| 3 Melos run_e2e_02 runtimeで発火したか(evidence行) | **発火あり**: Std a2 part1_c5 take3 secondary Azure=`Melo said.` -> `CONNECTED_SPEECH_ACCEPT`(`er011_output/attempt_history.jsonl` L12673)。attempt_history 528 attempt中CS系7件(ACCEPT 5[Melos 4])。b1b `Mello`/`Mellow` では不発 | **Melosで0回**(attempt_history `cascade_steps` 112 attemptに `connected_speech_equivalence_*` step 0件)。他案件(OPEN-122 Gate3, four_type_observation_01)では発火実績あり | **発火あり**: Ledger melos=`cascade_unresolved_entity`/low、Azure Phrase List=`["Melos"]`使用。CMU Case Aは `melos` 未収録で常に未解決 | **発火あり**: 長clipで多数PASS。Std a2 take1 Tier3 Azure=`Melos said.` -> `SECONDARY_ASR_CORROBORATED_MATCH`(L12671)。take2/b1b は Azure=`Mellow` x3 で `tier3_attempted_no_corroboration` | **発火あり**: telemetry全clipで記録(`entity_only` 等)。`Melo`↔`Melos` は `_is_benign_plural_pair`(validation.py L637)が吸収 |
| 4 発火しなかった場合の原因(配線/適用範囲/判定順序/固有名詞分類) | b1b `Mello`/`Mellow`: **適用範囲**(綴り水準。`Mello`≠`Melos`-s)。判定順序は問題なし(entity gateが先でValidatorに届かないケースは実データ・合成108件とも0) | **判定順序(入口条件)+固有名詞分類**: 入口は `TRUE_CONTENT_MISMATCH` のみ(L547-548)だが `Mello said.` は `entity_only` の `ASR_VALIDATION_UNCERTAIN`。さらに**適用範囲**: `word_phones("melos")=None`(CMU未収録)で `NOT_A_PHONEME_PREFIX_DROP` | **適用範囲**: CMU Case Aは辞書語限定。Ledgerの期待読み(`/ˈmiː.lɑːs/`=MEE-lahs)と実TTS読み(MEL-os系)が不一致(OPEN-308)で信頼度low | **適用範囲**: Tier3は Azure が canonical 語を**綴りまで**一致して初めて成立。Azureが `Mellow` と綴れば不成立(2語clip) | (発火した) |
| 5 発火したがNGの場合、落ちた判定条件(コード行) | b1b: `classify_asr_match` L1096-1099 `entity_only_diffs`->UNCERTAIN return。Validatorは呼ばれず、呼んでも `UNCLASSIFIED`(Pattern A: `s_suffix_label_if_match("Melos","Mello")` が `None`=`mello`+`s`≠`melos`、validator.py L90-99) | (呼出されず) 強制呼出しても `phoneme_prefix_drop` L142-146で `c_phones is None` -> `None` | `_step_alternate_pass` L423 が `melos` 辞書なしで `None` | Tier3 L601-660: Azure転写語が canonical と綴り不一致 -> `tier3_attempted_no_corroboration`。cascade後段 Primary#2/Azure#1/#2 も全て `Mello`/`Mellow` で `_step_alternate_pass` が全て不成立 -> `stop_retrying` -> LR(7 Gate全不通過)->HR | Primary `Mello said.` は `entity_only` -> `ASR_VALIDATION_UNCERTAIN`(telemetry L7062-7063)。Semantic Equivalenceは数値/複数形/略語/契約形のみで、固有名詞の同音別綴りは対象外 |
| 6 接尾辞のs(複数形・三単現)と語幹末のs(Melos)の扱い | **区別しない**。`s_suffix_label_if_match` は文字列として `canonical == asr+"s"/"es"` を見るだけ(`bus stops`<-`bu stops` も受理、合成test)。語幹末s(Melos, bus, gas)でも綴りが一致すれば受理(**OPEN-330**) | 音素水準で語末1〜2子音の脱落を見る。形態素は区別しない(Melosの語幹末sも対象になり得るが、OOVで届かない) | Ledgerは語単位。形態素なし | 形態素なし(語の綴り一致のみ) | 規則的な複数/単数のみ吸収(`_singularize_simple` L630-635)。`melos`->`melo` も吸収される(語幹末sと接尾辞sを区別しない) |
| 7 綴り一致だけに依存し正常な連結を取りこぼしていないか(`Melos said`->`Mello/Mellow/Mellis said`,`meloset`) | **取りこぼす**。Pattern Aは `Melo` のみ受理し `Mello`/`Mellow`(CMU音素は `M EH L OW` で `Melo` と完全同一)は範囲外。音韻列 /m ɛ l ɒ s/ + /s ɛ d/ の s+s融合として説明できる転写を、**綴りが違うだけで** UNCLASSIFIED にする | **取りこぼす**(入口条件+OOV)。CMU辞書語なら音素prefixで説明できる(`studies suggest`->`study suggest`等)が、固有名詞(OOV)では不能 | **取りこぼす**: OOV固有名詞に G2P が無い(`g2p_en` 未導入。`melos` の音素列を作れない) | **取りこぼす**: 綴り一致のみ(Azureが`Melos`と書くかどうか) | **取りこぼす**: 固有名詞の綴り揺れは対象外 |
| 8 真の語尾欠落・別語誤発音を誤PASSしない条件 | 保たれている: ASR語==canonical-`s/es`の**完全一致**+次語頭が歯擦音/同系破裂音。`Melon`/`Marcus`/`Melody`/`Melos aid`/`Melos.` は合成25反例で誤PASS 0。ただしPattern A自体が「語末sを実際に落とした音声」も同じ綴りで通す(**ASR文字列では融合と脱落を区別できない**) | 保たれている: `TRUE_CONTENT_MISMATCH`+protected_check通過+音韻環境A〜G+**独立ASR corroboration必須**(corroboration 0なら `INSUFFICIENT_EVIDENCE`) | 誤PASSなし(Ledgerは注入にhigh信頼のみ) | 保たれている: 独立engine(Azure)がdiff位置でcanonical語を支持する場合のみ。ただし Phrase List が綴りを誘導する(Azure=Melosは強い証拠ではない) | 保たれている(数値/否定のprotected_checkが先) |

## A-2. 「Melos said -> ASR別綴り」を音韻水準で説明できるか(未回答点の新規実測、オフライン、ASR呼出なし)

Trial専用の音韻判定(`er065_short_clip_asr_context_trial_01_p2_phon.py`、Production無変更)で、現行機構とTrial音韻判定を同じ転写に当てた結果(`a7_table_02.json`):

| ASR転写(出所) | 現行Production判定 | CS Validator | Equivalence Layer(入口,cheap) | Trial音韻判定 | Trial 3分類(独立証拠なし) |
|---|---|---|---|---|---|
| `Mello said.` (OpenAI att1/2/3/4, b1b) | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | **PHON_EXPLAINED_FUSION**(RIGHT_FINAL_DROP: melos[Z]+said[S]) | HR |
| `Mellow said.` (Azure att2, b1b, 減速後8/8) | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | **PHON_EXPLAINED_FUSION** | HR |
| `Melo said.` (Azure att3,4,6 / whisper) | CONNECTED_SPEECH_ACCEPT(PASS) | ACCEPT | ACCEPT | PHON_EXPLAINED_FUSION | HR |
| `Mellis said.` (OpenAI att4) | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | NOT_EXPLAINED(母音 OW<->IH 相違) | NG(説明不能) |
| `meloset` / `Mellowset.` (OpenAI att5/att6) | TTS_FAILURE | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | PHON_EXPLAINED_VOICING(INTERNAL_FINAL_DROP。`melo`+`set` = M EH L OW S EH T、融合した`said`の/d/が無声化した読み) | HR |
| `Mellos said.` (OpenAI a2 part1_c1等) | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | PHON_HOMOPHONE_ONLY(融合不要の同音綴り違い) | HR |
| `Melos said.` (Azure att1) | EXACT_MATCH(PASS) | NO_DIFF | - | EXACT | 許容 |
| `Melon said.` `Marcus said.` `Mel said.` `Melos aid.` `Melos.` (反例) | UNCERTAIN / TRUE_CONTENT_MISMATCH | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP等 | **NOT_EXPLAINED** | NG |

### 結論(「既存仕様は上記原則を実装しているか」)

1. **原則は「綴り水準の限定パターン」としてのみ実装されている**。承認済みの3パターン(A/B/C)は、原則の一部(歯擦音連続・同系破裂音連続での語末脱落/追加)を**綴りの完全一致**で実装している。これは「音韻構造を診断し、正常な連結発音で説明できれば許容」ではなく、「**説明できる転写のうち、ASRがたまたま特定の綴り(canonical-`s`)で書いたもの**だけ許容」である。`Mello`/`Mellow`は音韻列が`Melo`と完全に同一(`M EH L OW`)でありながら、綴りが違うために説明されない。
2. **欠けている層**(「配線漏れ」ではなく「設計上の不足」。判定順序の問題でもない):
   - (a) **綴り水準 vs 音韻水準**: M1は綴り水準。音韻水準のM2は存在するが、
   - (b) **Equivalence Layer入口条件**: `TRUE_CONTENT_MISMATCH` 限定(L547-548)のため、固有名詞差由来の `ASR_VALIDATION_UNCERTAIN`(entity_only)には届かない、
   - (c) **OOV固有名詞のG2P欠如**: `melos` がCMU未収録で音素列が作れない。Trial音韻判定では「OOVの`-s`語を stem(CMU収録)+S/Z で派生」で`melos`=`M EH L OW Z`を作れたが、stemがCMU未収録の名前では不能(`g2p_en`等の新規依存が必要、未導入)。
3. **ASR推測のみで自動PASSしない**原則は現行機構で守られている(誤PASS 0)が、その代償として、(i) 融合で説明できる正常音声も、(ii) 語末sを実際に落とした音声も、**ASRテキストからは区別できない**。区別には音響等の独立証拠が必要(本Trial C/D参照)。
4. 配線漏れ・バグ: **新規発見なし**(判定順序問題 0件、Validator/Layerの配線漏れ 0件)。既知のGap(OPEN-122(4) 減速後cascadeへのEq flag未配線、OPEN-322 Dialogueの`segment_id`非伝播、OPEN-328 観測性)は本件事象に無関係で、**是正候補のまま未実施**(Production変更0。理由: 今回の事象(UNCERTAIN)ではEqLayerは入口条件で発火せず、flag配線だけでは救済されない=効果が確認できない修正は行わない)。
