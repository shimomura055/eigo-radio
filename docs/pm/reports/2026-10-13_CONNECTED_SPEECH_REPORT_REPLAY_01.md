# 連結発音(子音のつながりによる融合・弱化・脱落)問題 報告再掲 01

作成: 2026-10-13 / 作成者: sonnet-worker(Fable委任、読み取り・要約のみ、API 0、ファイル変更は本ファイル新規1件のみ、commitなし)
対象管理ID: FAMILY-Z-MELOS-CONNECTED-SPEECH-ROOT-CAUSE-AUDIT-01 / FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01
方針: ディスク上の正本から再構成。採用判断は書かない。原本に無い事項は「原本に記載なし」と明記。

注意(原本内の新旧差): `phase2/A_AUDIT_02.md` 結論4の「配線しない理由(今回の事象ではUNCERTAINでEqLayerは入口条件で発火せず)」は、委任_04で**訂正済み**(本文3-5参照)。訂正後の記述を正とする。

---

## 1. 問題の定義(何が起きたか)

### 1-1. 事象
- 案件: Family Z Melos run_e2e_02。問題のsegmentは `full_story_part1_c5`(原文は2語「Melos said.」、narrator=Aoede)。
- 語レベルの現象: `Melos`(語末 /s/)と `said`(語頭 /s/)が連続し、語末sと語頭sが1つの長い /s/ に融合する(歯擦音の連続=Connected Speechの典型環境)。このため音声を聞いたASRが `Melos` と書かず、同じ音を別綴りで返す。
- ASRの綴りの揺れ(同一wavでも揺れる。Primary=OpenAI gpt-4o-mini-transcribe、Secondary=Azure Speech STT+Phrase List `["Melos"]`):
  - `Mello said.`(OpenAI Primary、Std/Adv両方)、`Mellow said.`(Azure、Adv計3回・Std take2計3回・減速後8/8)、`Melo said.`(Azure secondary_1、Std fallback take3)、`Melos said.`(Azure Tier3、Std take1のみ)、`Mellos`(a2 part1_c1等)、`Mellis said`(att4)、`melloset`/`Mellowset`(att5/att6、TTS_FAILURE扱い)。
  - local faster-whisper(small/medium、無料): a2 att1 Mello/Mellow、att2 Mello/Mellow、att3 Melo/Mellow、減速後final Mello/Mellow、b1b Mellow/Mello。**どの転写にも語末s(Melos)は無い**。
  - CMU音素は `Melo`/`Mello`/`Mellow` とも `M EH L OW` で完全に同一(`melos` 自体はCMU未収録)。

### 1-2. Adv(b1b) `full_story_part1_c5`
- Production入口: runner → `er063_family_z_audio_01.py::real_generators().narrator`(L552-557) → `news_tail_fix.generate_news_narration_wide_margin`(`enable_connected_speech_equivalence_layer=cs(spec)`、`enable_pronunciation_resolver=True`) → `secondary_asr.evaluate_attempt_with_cascade`。
- Primary=OpenAI `Mello said.` → `ASR_VALIDATION_UNCERTAIN`(entity_like_source=`["capitalized"]`、sub_reason=`entity_only`)。
- Validator(Pattern A〜C)はPrimary段階で**呼ばれない**: `classify_asr_match`(`er006_preprod_hardening_01_validation.py`)が `entity_only_diffs`(L1064)をL1096-1099でUNCERTAINにreturnするため。仮に呼んでも `classify_connected_speech("Melos said.","Mello said.")=UNCLASSIFIED`(`mello`+`s`≠`melos`)。
- Equivalence Layer: 呼出なし(`er006_secondary_asr_01.py` L547-548が `TRUE_CONTENT_MISMATCH` 限定、本件はUNCERTAIN)。強制呼出しても `NOT_A_PHONEME_PREFIX_DROP`(`word_phones("melos")=None`)。
- Azure計3回: Tier3 `Mellow said.`、secondary_1 `Mellow said.`、secondary_2 `Mellow said.`。OpenAI Primary#2 `Mello said.`。
- Ledger: `melos` = `cascade_unresolved_entity`/confidence=low/IPA `/ˈmiː.lɑːs/`(TTS注入対象外)。
- 最終: cascade全step不一致 → `stop_retrying` → Local Rewrite実行(17:49:42、Luna候補5件、7 Gate全通過0件、`HUMAN_REVIEW_LOCKED_NO_CANDIDATE_PASSED_QA`) → HR(`HUMAN_REVIEW_REQUIRED`)。TTS生成は1回のみ(上限3の残り2回は未使用: b1b経路はUNCERTAINで即打切り)。

### 1-3. Std(a2) `full_story_part1_c5`(`generate_a2_segment_with_slowdown`経由、TTS通算3回上限)
- take1(standard): Primary `Mello said.` UNCERTAIN。Tier3 Azure=`Melos said.` → `SECONDARY_ASR_CORROBORATED_MATCH` で**PASS**。
- take2(standard): UNCERTAIN → cooldown 600秒(18:35:29→18:45:29)、Azure=`Mellow said.`×3。
- take3(fallback minimal instruction、`gemini-2.5-pro-preview-tts`): secondary_1 Azure=`Melo said.` → `CONNECTED_SPEECH_ACCEPT`(Pattern A)で**PASS**。
- 6%減速後の再検証(`A2_SLOWDOWN_REVERIFY`): attempt1 Primary=`Mello said`(ピリオドなし) UNCERTAIN → 救済なし → STOPPED(L12672)。attempt2 Primary=`Mello said.` UNCERTAIN → 救済なし → STOPPED(L12674)。TTS通算3回=上限で終了。最終 `status=STOPPED`(`slowdown_applied=true`)。
- STOPPEDの直接原因は「減速後再検証に救済(Tier3/cascade/Pattern A)が無かった」こと(分類A)。eb4c6479の `_post_slowdown_cascade_rescue` で是正済み。ただしpart1_c5は `--only-clips` 対象外のため再実行しておらず、現在のwavの再評価(`reeval_post_slowdown_01.json` P2)は 0/3 PASS、Azure=`Mellow said.`。

### 1-4. 委任_02での再生成(CS監査)
- 再生成1回のみ実行(rc=2、STOPPED)。take: 標準 Mellis said / Mallow said.(UNCERTAIN)、fallback melloset、Mellowset(TTS_FAILURE)。Pattern A・減速後救済は到達せず。review_lock=HUMAN_REVIEW_REQUIRED。費用+JPY0.60。
- 後に(2026-10-13、FINAL-ASSEMBLY側の別管理ID)ユーザーがHR3件(Std part1_c5 attempt4 / Adv part1_c5 / Std comment_1)を個別承認。ただし採用attempt4は6%減速前の音声のため `verify_std_english_slowdown` でSlowdown Gate STOP(ratio=1.2683、OPEN-331)。現在 Melos最終試聴は依存事項待ち・判断保留(UDR #23)。

---

## 2. 既存機構の監査結果(`CS_AUDIT_01.md`、`TRIAL_REPORT_01.md` A、`A_AUDIT_02.md`)

### 2-1. 結論(配線バグの有無)
- **配線漏れ・実装バグ・判定順序のバグは新規発見なし**(委任_01〜、phase2でも同結論)。承認済みConnected Speech機構は配線されており実発火した。
- 分類: **A(是正済み: 減速後救済欠落)+ C(設計上の不足: OOV固有名詞に対し音素水準のCS判定が構造的に不能)+ D残余(音声実体の真偽)**。先行調査の「分類D(機械判定不能)」は、C主体へ訂正。ただしC案(拡張)は「語末sを本当に落とした音声」を区別する独立証拠が揃うまで安全でない=Dの核は残る。

### 2-2. 機構別
**M1 Connected Speech Validator Pattern A/B/C(OPEN-107/110、`er011_b1_connected_speech_validator_01.py`)**
- `classify_connected_speech` L125。Pattern A L151(語末 -s/-es 脱落: ASR語 == canonical語から -s/-es を除いた綴りの**完全一致**+次語頭が歯擦音)/B L166(同系破裂音連続)/C L181(再分節・追加子音)。**いずれも綴り水準のみ**。CURRENT_SPEC L2025で3パターン限定「それ以外へ一般化しない」。
- 配線: `classify_asr_match` から `non_entity_diffs` あり時(L1068/L1076付近)と、diff空の最終fallback(L1119)で呼ばれる。role非依存。cascade各step・減速後 `_post_slowdown_cascade_rescue`・LR後QAでも `classify_asr_match` を通る。
- **今回の発火**: attempt_history 528 attempt中CS系7件(ACCEPT 5[うちMelos clip 4: run_e2e_01 b1b part1_c1 / part1_c20×2、run_e2e_02 Std a2 part1_c5 fallback]、残1はb1b part1_c3 `guards→guard seized`、PASS_WITH_WARNING 2[`kp3_explanation_en`/`studied them`])。
- 取りこぼし: `Mello`/`Mellow`(CMU音素は `Melo` と同一なのに綴りが違う)は範囲外。

**M2 Connected Speech Equivalence Layer(OPEN-122、`er011_connected_speech_equivalence_layer_production_01.py`)**
- `phoneme_prefix_drop` L142 / 本体 L215。配線 `er006_secondary_asr_01.py` L547-596。flag既定False、呼出元がrole別にTrue(PRODUCTION_WIRED commit 3297d1b、2026-09-26に5 role拡張)。承認条件: 既存3パターンのUNCLASSIFIED fallthrough後段・`TRUE_CONTENT_MISMATCH`+`protected_check`通過+音韻環境カテゴリA〜G+独立ASR corroboration必須。
- **入口条件**: `TRUE_CONTENT_MISMATCH` 限定(L547-548)。固有名詞差由来の `ASR_VALIDATION_UNCERTAIN`(entity_only)には届かない。
- **OOV G2P不在**: `melos` がCMU未収録(`word_phones("melos")=None`)。`g2p_en` 等は未導入。仮に到達しても `NOT_A_PHONEME_PREFIX_DROP`。固有名詞(OOV)には構造的に発火できない。
- **Melos案件での発火は0回**(attempt_historyのcascade_stepsを持つ112 attempt中 `connected_speech_equivalence_*` step 0件。ただしb1b経路はcascade_stepsがnullで記録されない)。他案件(OPEN-122 Gate3、`er014_output/four_type_observation_01/trend/audio/b1b` の `CONNECTED_SPEECH_EQUIVALENCE_ACCEPT`)では発火実績あり。

**M3 固有名詞 Pronunciation Resolver/Ledger**: `_step_alternate_pass` L423(CMU Case A)は `melos` 辞書なしで常に未解決。Ledger期待読み(MEE-lahs)と実TTS読み(MEL-os系)が不一致(OPEN-308)でconfidence=low=TTS注入対象外。Azure Phrase Listのみ使用。

**M4 Secondary ASR Cascade(Tier3 Azure corroboration)**: Tier3 L601-660。Azureが diff位置でcanonical語を**綴りまで**支持して初めて成立。長clipでは多数PASS(10試行中8回 Azure=`Melos`)、2語clipではAzureが `Mellow` と綴ると `tier3_attempted_no_corroboration`。Phrase Listが綴りを誘導するためAzure=Melosは強い証拠ではない。

**M5 English ASR Semantic Equivalence Layer(er021)**: 数値/複数形/略語/契約形のみ。固有名詞の同音別綴りは対象外。`Melo`↔`Melos` は `_is_benign_plural_pair`(validation.py L637)が吸収。

### 2-3. dead wiring(`_post_slowdown_cascade_rescue`)
- `er003_v1_n3_01_tts_generate.py` `_post_slowdown_cascade_rescue` L117(同L127付近で判定)、`apply_a2_slowdown_postprocess` L169。是正前は Primary 1回のみで救済なし。是正後(eb4c6479)は Tier3/cascade/Pattern A を共有するが、`enable_connected_speech_equivalence_layer` flag は**渡さない**(OPEN-122(4)既知Gap、OPEN-328)。
- **[委任_04訂正]** このflag未配線の見送り理由は「UNCERTAINで入口外」ではない。正しくは: (i) `_post_slowdown_cascade_rescue` は `ASR_VALIDATION_UNCERTAIN` 以外を即returnし、Eq Layer入口は `TRUE_CONTENT_MISMATCH` 限定のため、flagを渡すだけではdead wiring(入口が噛み合わない)。(ii) 実際のギャップ=「減速後に、辞書語の `TRUE_CONTENT_MISMATCH`(`studies suggest`、`pay showed coffee` 型)へEq Layerが一切効かない」。これはMelos固有ではなく一般語の問題で、OPEN-270の外側ループと合わさり量産時のretry浪費・HR反復に直結し得る。承認済み仕様の配線漏れではなく、OPEN-122本体(L297)でスコープ外・ユーザー承認なしに実装しない既知ギャップ。
- 回帰test `test_post_slowdown_wiring` が現状を固定(TRUE_CONTENT_MISMATCH→cascade非呼出、UNCERTAIN→cascade呼出だがEq Layer flag非渡し)。

### 2-4. 8項目の検証(`CS_AUDIT_01.md` §3)
1. Family Z clip_idがFULL_STORY認識: OK(`er020_tts_retry_local_rewrite_01.py` L124-149)。
2. CS flagがCascadeまで伝播: コード上OK。ただし呼出層ごとの実値・`layer_invoked` がattempt_historyに無い=観測性不足(OPEN-328)。
3. Dialogue vs Narrator: 本件2clipはnarrator=問題なし。Dialogueは `bvoices.generate_voice_body_wide_margin`(L549)が `segment_id` を渡さずTier3/role gating無効(OPEN-322、本件無関係)。
4. Adv/Std差: Adv=UNCERTAINで即打切り→LR→HR、Std=fallback+cooldown+6%減速後再検証。仕様上の差。
5. 減速前後の対策: 減速前はTier3・Pattern A共に発火(PASS×2)。減速後(是正前)は救済なしSTOPPED×2。是正後は同じ4 stepを適用。
6. 固有名詞diffがCS判定より先にentity_only/UNCERTAINへ: **到達不能になった受理可能ケースは0件**(実データ26 CS環境pair、合成108件)。`_is_benign_plural_pair` がstem綴り一致(`Melo`)を吸収し、最終fallback(L1119)でValidatorが走る。到達しないのは「stem同音の別綴り」(`Mello`等)のみで、その場合Validator自体も未分類。**gate順序は原因ではない**。
7. 3パターン対象外→拡張Layer到達: UNCERTAIN(entity_only)は到達しない。TRUE_CONTENT_MISMATCHで到達してもOOVは `NOT_A_PHONEME_PREFIX_DROP`。構造上到達不能(固有名詞)=C。
8. retry/fallback/LR/resume: 欠落なし(resumeは本2clipで未発動のため未確認)。

### 2-5. 「接尾辞s」と「語幹末s」の扱い(OPEN-330)
- Pattern Aの `s_suffix_label_if_match`(`er011_b1_connected_speech_validator_01.py` L87-99)は文字列として `canonical == asr + "s"/"es"` を見るだけで、形態素上の接尾辞に限定しない。`Melos→Melo`、`Chris→Chri`、`Marcus→Marcu`、`bus stops←bu stops` も機械的にACCEPT(合成test: 14名×6動詞で全PASS)。当初の承認根拠(-s/-es接尾辞の脱落。例 studies→study)より実装の受理範囲が広い。承認範囲の拡大ではなく事実の記録(CURRENT_SPEC L2025に記録済み)。扱いはユーザー判断(OPEN-330)。

### 2-6. 音声現象として自然か(`CS_AUDIT_01.md` §4)
- `Melos said` = /ˈmɛloʊs/ + /sɛd/。語末/s/と次語頭/s/は同一調音(歯茎摩擦音)で、英語では1つの長めの/s/に融合するのが通常=Pattern Aの音韻環境そのもの。
- 5分類: 音声自体の発音誤り=不明(同一wav群でASRが Melos/Melo/Mello/Mellow/Mellos/Mello's に揺れ、収束しない。Azure take1は `Melos` を返したので少なくとも1 takeに語末sが聞き取れる音あり) / 音声正常だがASRが別綴り=部分的に確証 / 連結発音は正常だが既存Validatorの認識範囲外=**YES(主因)** / 必要機構が未配線・未発火=部分的(Aのみ、是正済み) / 独立した音声証拠の不足=**YES**。

### 2-7. 汎化検証(オフライン、API 0)
- 実データ(HRキュー全step転写+er021 telemetry先頭7155行、612ユニークpair): CS環境26 pairは全て現行Validatorでは未分類(UNCERTAIN 18[うち17がMelos、1はthis/the取り違え]、TRUE_CONTENT_MISMATCH 7、NUMERIC 1)。entity gateが先に走ってValidatorに到達できなかった(Validatorなら受理できた)pair=0。仮説規則A'(stem同音)の候補10 pairは全てMelos。**実データ上、Melos以外の事例は存在しない**。
- 合成スイープ(18固有名詞[-s/-es終わり]×次語6[said, spoke, smiled, sat, saw, stood]): ASR=stem綴り完全一致108件=108/108 `CONNECTED_SPEECH_ACCEPT`(entity gateに遮られた件数0)。stem同音の別綴り114件=6 PASS(`Carlos→Carlo`)/108 NOT_PASS。A'が追加で拾うのは12件=`Melos→Mello/Mellow` のみ(他の固有名詞はstemがCMU未収録)。**A'の効果はMelos固有の偶然(`melo`がCMU収録)で汎用性は低い**。
- 反例25件(`Melos said.`←`Melon`/`Marcus`/`Melody`、`Marcus smiled.`←`Marker`、`The studies suggest`←`The studio suggests`、`The bosses said`←`The bonus said` 等): 全て現行でNOT_PASS(誤PASS 0)。一般名詞の自然現象(`bosses said`→`boss said`、`classes started`→`class started`、`cities seem`→`city seem`)はPattern Aで受理。語尾が接尾辞でない最終子音(`school starts`←`schoo starts`、`nice sign`←`nigh sign`)は未分類のまま=過受理なし。

### 2-8. 探索的音響観測(Production判定には使わない、`CS_AUDIT_01.md` §6)
`said` 語頭付近の最長摩擦区間(4kHz以上の高域比>0.5、5ms刻み): a2 take1 190ms(Azure `Melos`) / take2 170ms(`Mellow`×3) / take3 120ms(`Melo`) / final(減速後)120ms(`Mellow`) / b1b 165ms(`Mellow`×3) / 対照 `he said softly.` 140ms / `he said at last.` 90ms。run_e2e_02既存wavのキャリブレーション: s終わり+s始まり境界 n=4(160-250ms、平均204ms)、非s終わり+s始まり n=48(65-255ms、中央値125ms)。測定値は両分布の中間でA群n不足のため判定根拠に使えない。

### 2-9. Local Rewrite候補5件のGate別不通過(`CS_AUDIT_01.md` §13-1、原文2語「Melos said.」)
| 候補 | 不通過Gate |
|---|---|
| 1 `Melos stated.` | Gate7のみ(unchanged_ratio=0.5、LOW_ORIGINAL_COVERAGE) |
| 2 `Melos spoke.` | Gate1(意味保持)・Gate5(自然さ)・Gate7 |
| 3 `Melos remarked.` | Gate7のみ(LLM QA Gate1-5通過) |
| 4 `Melos had this to say.` | Gate5・Gate7(TOO_LONG_OVER_EXPANDED) |
| 5 `That was Melos speaking.` | Gate1・Gate7(TOO_LONG_OVER_EXPANDED) |
- 全5候補がGate7(全面書換でない)で落ちる。原文が2語しかないため1語入れ替えでunchanged_ratio=0.5、原文語被覆率0.5となり「全面書換」と機械判定される構造。全候補が `Melos` を保持するため、仮に通過してもASRが同じMello/Mellowを返す懸念が残る(TTS再生成していないため未検証)。Gate7閾値の変更は新Production仕様のため提案のみ(OPEN-318の「固有名詞のみの短clipを避ける原稿/分割ルール」と一体検討)。

### 2-10. 副作用(telemetry重複行)
- CS監査の初回オフライン再評価スクリプトが、共有 `er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl` へ再評価分の重複行を追記してしまった。委任_03のmanifest(`cs_audit_01/telemetry_probe_rows_manifest_01.json`)で特定: **audit行 1,998行 = 7156〜9153行(連続)**(入力pair一致1,820、合成行列177、単体test追記1)。9154〜9165行は委任_02のProduction正規再生成の正当な追記。他agent行と判定できる行は0件。本体は未変更・未stage。巻き戻しはFable/ユーザー判断(OPEN-328)。集計時は7156〜9153行を除外。以後のscript/testは `append_telemetry_log` をno-op化済み。

---

## 3. 承認原則の扱い

### 3-1. 承認原則(原文に近い形)
「自然な英語で、子音が連続することにより一方の音が融合・弱化・脱落し得る場合、その音韻構造を診断し、正常な連結発音で説明できるなら許容する。ただし文脈によるASRの推測だけを根拠に自動PASSしない。」(`A_AUDIT_02.md` 冒頭)

### 3-2. 現行実装との関係(phase2 結論)
- 原則は**「綴り水準の限定3パターン」としてのみ実装**されている。Pattern A/B/Cは「説明できる転写のうち、ASRがたまたま特定の綴り(canonical-`s`)で書いたもの」だけ許容する。`Mello`/`Mellow` は音韻列が `Melo` と同一なのに綴りが違うため説明されない。
- 欠けている層(配線漏れ・判定順序のバグではなく設計上の不足): (a)綴り水準 vs 音韻水準、(b)Equivalence Layer入口条件(`TRUE_CONTENT_MISMATCH` 限定)、(c)OOV固有名詞のG2P欠如(Trial音韻判定では `melos` を stem `melo`(CMU収録)+S/Z で派生して `M EH L OW Z` を作れたが、stemがCMU未収録の名前では不能。`g2p_en` 等の新規依存が必要で未導入)。
- 「ASR推測のみで自動PASSしない」原則は現行機構で守られている(誤PASS 0)が、その代償として(i)融合で説明できる正常音声も(ii)語末sを実際に落とした音声も、ASRテキストからは区別できない。

### 3-3. Trial専用の音韻判定(Production未配線)の結果(`A_AUDIT_02.md` A-2)
| ASR転写 | 現行Production | Trial音韻判定 | Trial 3分類(独立証拠なし) |
|---|---|---|---|
| `Mello said.` / `Mellow said.` | UNCERTAIN | PHON_EXPLAINED_FUSION(RIGHT_FINAL_DROP: melos[Z]+said[S]) | HR |
| `Melo said.` | CONNECTED_SPEECH_ACCEPT(PASS) | PHON_EXPLAINED_FUSION | HR(Trialでは独立証拠なしのため) |
| `Mellis said.` | UNCERTAIN | NOT_EXPLAINED(母音 OW<->IH 相違) | 説明不能(既存判定に委譲) |
| `meloset` / `Mellowset.` | TTS_FAILURE | PHON_EXPLAINED_VOICING(融合+`said`の/d/無声化) | HR |
| `Mellos said.` | UNCERTAIN | PHON_HOMOPHONE_ONLY | HR |
| `Melos said.`(Azure att1) | EXACT_MATCH(PASS) | EXACT | 許容 |
| `Melon`/`Marcus`/`Mel`/`Melos aid`/`Melos.` | UNCERTAIN/TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | 説明不能 |

### 3-4. 自動PASS(auto-accept)をREJECTEDとした理由
- 2つの別のREJECTED:
  1. **ASR時のみ文脈結合(C-c)のauto-accept化: REJECTED(Trial実測、委任_01)**。文脈を足すと(a)att6以外では文脈にMelosが含まれる条件でのみ上がる(プライミング)、(b)判定根拠が結合音声になりASRが他clipの綴りに引きずられる(安全≠成功原則に抵触)、(c)proxy反例で単独NG→文脈付きPASSに反転が13/41観測。診断用途のみ可。
  2. **音韻説明可の転写の自動許容側: REJECTED(単独gateとして、独立証拠未校正、phase2)**。理由: ASR文字列は融合と語末s脱落を区別できず、区別に使える独立証拠として摩擦区間長を既存wav 215本(s+s 250境界 vs 単独s 2,007境界)で較正したが **AUC=0.74(bootstrap 95% 0.69-0.77)で単独gateに使えない**。同一clip内の差は平均+51ms・78%で融合側が長い(現象は実在)が、絶対閾値は話者・速度・語で揺れる。Melos 7 takeの測定: att1 195ms、att2 0、att3 120、att4 180(**人間HR承認済み**)、att5 100、att6 145、b1b_att1 0(**人間HR承認済み**)。承認済み2本が180msと0msに分かれ、正常音声が閾値を満たさない。
  - **[委任_04訂正]** b1b_att1の0msは、有声Z+Sでは高域比が低く0msになりやすい**測定失敗の可能性**=「測定不能」扱い。「偽陰性の実例」とは呼ばない。AUC=0.74はラベル(融合長/単独s)が文字列由来で真値でないため参考値。clip内相対値正規化等を試すまでは「現指標では不可」。
  - 結論: 音韻説明可の転写は「許容」ではなく「HR候補(説明付き)」に止めるのが現状唯一の安全な運用。ただし**[委任_04訂正]** 説明付きHR候補化は確認時間の短縮のみで**HR件数は減らさない**(一般語のHR候補化は6/288=2%)。
- Trial音韻判定の安全前提(委任_04で明記・test固定): 本判定はProductionの `protected_check`(否定・時制・数・固有名詞等)通過後にのみ適用する設計前提。単体では `can't talk`→`can talk`(T+T融合、否定反転)、`he walked to`→`he walk to`(時制)、`great time`→`gray time`(別語化)が「説明可」になる穴があり(`three trees`→`tree trees` は NOT_EXPLAINED)、最小の安全装置 `risk_flags()`/`three_way_with_flags()` を追加(フラグがあれば独立証拠があっても許容にせずHR)。音響証拠は落ちた音素がS/Zかつ摩擦音境界(GEMINATE_SAME/SIBILANT_SEQ)でのみ有効で、破裂音境界(`last time`、`pay showed coffee`)は「測定不能」。`second_engine_exact`(Azure+Phrase List)はPhrase List誘導のため独立証拠から除外。
- 増分誤許容の残余リスク(D-4): `said` 語末を70〜220ms切詰めたMelos said音声19件(すべて `syn_B1_trunc*`)が、独立証拠最大の仮定下で許容側に倒れる(ASR転写がintactと同一の `mello said`/`mellow said` のため)。Trial規則を導入する場合は**clip末尾の完全性の独立確認(末尾エネルギー/継続長等)の併用が必要**。

### 3-5. 推奨(採否はユーザー、すべて未実装・未検証)
- **第一候補=上流対策**(PHASE2 E-2、TRIAL_REPORT 推奨1): (i)固有名詞の語末が歯擦音(s/z/sh等)のとき、直後に歯擦音始まりの語(said/says/saw/softly等)を連続させない(`said Melos` の語順等)、(ii)引用間narrator chunk(attribution clip)に最小語数を置く。裏付け=B-1実測(Melos+非s始まり: Azure 2語cut 2/8 vs 元clip全体2.7〜4.6秒 4/4、OpenAI 0/16 vs 2/8)=clip長が増えると認識が改善。ただし**長さと「s+s融合の有無」が交絡しており、clipを長くする効果自体は未検証**。
  - 影響範囲(読取確認のみ): `er062_family_z_structure_01.py` `build_flat_chunks`(L535付近)・`plan_clips`(L552付近)が `fam_c.plan_story_segments`(`er013_family_c_production_01.py` L306付近、`_build_base_segments` L202付近)を使い、voice変化は `voice_boundary` で必ず別clipになる=**narrator chunkの最小語数制約は構造上存在しない**。変更候補は(a)Z writer記事生成promptへのattributionルール追加(`er062_family_z_writer_01.py`、記事生成promptの位置は本委任では未特定)、(b)structure段の決定論的lint。TTS/ASR/retry/LR/Master Store/HR Lockは変更不要、既存記事の遡及不要(新規記事のみ)。規模は小〜中。
- 代替案(併記): 「名前×ASR綴り変種」の人間承認台帳(承認済み変種+音韻説明可+clip末尾完全性確認の3条件を満たす場合に限り再登場時のみ自動受理、初出は1回HR)。D-4の末尾切詰に対する独立確認が前提。
- 作品単位allow-list(人間が聴いて承認した綴り群のみ`PASS_WITH_WARNING`)は、**「その作品内でこの名前の語末s脱落リスクを許容する方針決定」と等価**で、1 takeの人間承認(綴りに紐付き音声に紐付かない)は別takeのs脱落を防がない。3択: (i)方針として許容 (ii)承認をaudio sha256に紐付け (iii)音響的独立証拠の併用を採用条件にする。OPEN-331(HR承認take→6%減速後再検証Gate)と一体検討。
- 誤PASS対策(共通): Azure(決定的)+Phrase Listを一次指標に維持(決定的=忠実ではない)、結合ASRや単独OpenAIのPASSはSecondary corroboration必須、HR fallback維持(Gate無効化なし)、語末子音欠落には音響的な独立証拠が要る(未検証)。
- Production採用提案前にOpus独立技術レビュー(条件A/C)と人間の`APPROVED_FOR_PRODUCTION`が必要。

---

## 4. 短尺clip ASR文脈一般化Trial(A〜E)の設計・結果・数値

### 4-0. 概要
- 管理ID: FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01(委任_01〜_04、委任_04で上限到達)。出力: `er065_output/short_clip_asr_context_trial_01/`。評価モデル: Production同一(OpenAI `gpt-4o-mini-transcribe`、Azure Speech STT+Phrase List)。最新モデル原則の例外理由=比較可能性。local faster-whisper small/medium は無料の第三者参照(Production対象外)。TTS再生成0。
- 実験構成(音声は全て既存): Melos run_e2e_02 の `full_story_part1_c5`(Std a2=6take[att1〜att6]、Adv b1b=1take)と同run内の前後clip(同一ナレーターAoede、台詞voice Algieba/Charon/Erinome)を、clip間300ms無音で結合。7take×24条件(単独/同一voice前後[3〜27秒]/異voice前後[3〜25秒]/実ストーリー順隣接[c3 c4 T c6 c7、c1〜c7])=168結合音声。OpenAIは各2回、AzureはR00全take×2回+選抜条件、local whisperは全条件。target領域抽出は(1)期待テキストとのdifflib整列、(2)Azure/whisperはword timestampsのtarget区間。一致率: Azure 49/49、whisper-small 92%、medium 100%。
- 反例セット: (a)synthetic(既存音声のオフライン編集、欠陥の真値既知: 語末子音切詰[70/140/220/300/380/460ms]、語欠落[Melos/said削除]、誤語[Melosをrulerに差し替え]、無改変対照)、(b)natural_ng(過去の本番NG take 11件)。
- 注意: 一般化の範囲は **1フレーズ(`Melos said.`)・1ナレーター(Aoede)・7 take** のみ。Family Z全体・複数ナレーターへの一般化は未検証。

### 4-A. 既存仕様・実装の確認(¥0、新規重複機構を作らないためのGate)
7機構(Pattern A/B/C、Equivalence Layer、ASR Semantic Equivalence、Resolver/Ledger、Cascade Tier3、6%減速後再検証、retry/fallback/Local Rewrite 7 Gates)の機能・配線・適用範囲・Melos発火を1表化(TRIAL_REPORT A-1)。結論: 解決できる=長clip(6語以上)の固有名詞綴り揺れ(Tier3: 10試行中8回Azure=`Melos`)、綴り一致の語末s脱落(Pattern A)、減速後の救済(是正済み)。解決できない=OOVかつ同音別綴りを返す2語clip、Pattern Aの語幹末s受理(OPEN-330)、ASR文字列だけでの語末子音脱落の区別。**配線漏れ・判定順序の欠落は新規発見なし**。

### 4-B. ASR評価単位の比較(Melos、数値)
| 観点 | OpenAI | Azure+PL | whisper-small |
|---|---|---|---|
| 単独2語clipで `melos said` 一致 | 0/13 (0%) | 2/14 (14%)[att1のみ2/2] | 0/7 |
| Production判定PASS(Pattern A受理含む) | 0/13 | 6/14 (43%) | 4/7 |
| 文脈付きで `melos said` 一致 | 34/298 (11%) | 10/49 (20%) | 26/161 (16%) |
| 同一音声2回でtarget領域転写が一致 | 148/205 (72%) | 15/15 (100%) | 決定的 |
- OpenAI(正認識=`melos said`)を文脈量別に: Npre3/Npre8/Npre14/Npost3/Npost14/Dpre3/Dpost*=0%、Dpre25=31%、Npre27=15%、Rwin7(c1〜c7、28.6秒)=67%。**単調な「何秒以上なら安定」という閾値は、試した範囲では見つからなかった**。各recipeはn=13程度(7take×2回、take相関あり)で、0/13でも真の率の上限は約25%。
- OpenAI文脈付き出力の内訳(base 298観測): `mello said` 148、`melo said`(Pattern A受理)42、`melos said` 33、空(整列不能)13、その他(Mellow/Mellos/malice/mally等)。

### 4-C. 結果の核(委任_02訂正後の結論)
1. **単独2語clipで `Melos said.` が不安定な原因は、本Trialでは1つに確定できない**。併記すべき3点:
   - (a) att6以外ではプライミングが優勢: att6を除いて再集計すると、文脈にMelos語を含まない 3/198 (2%) vs 含む 13/55 (24%)(付録C-2b。att6を含む旧集計は 18/234 (8%) vs 16/64 (25%))。whisper-smallは含む 74% (26/35) vs 含まない 0% (0/126)。改善して見えるのは「文脈にMelosが書かれている」ためで、当該clipの発音確認ではない。
   - (b) a2_att6は音響に基づく効果の可能性があり真値は試聴待ち: att6の文脈付き `melos said` 17/45のうち15件は文脈にMelosを含まない条件。文脈付きで `melos said` 化したdistinct recipe 11件のうち9件は `ctx_has_focus_word=false`(付録C-2c)。Dpre25(異voice前置25秒・Melos語なし)でatt3/att5/att6が `melos said`(att6は2/2、att3/att5は1/2。付録C-2d)。プライミングでは説明できず、文脈で綴りが安定する音響上の効果、または実際の発音差を拾った可能性。真値(耳で確認)が無く「maskingの証拠」とも「正しく拾った証拠」とも確定不可。→ 「masking主証拠」から**真値未確定の候補**に弱めた。
   - (c) 「clipの長さ」と「s+s融合の有無」が交絡して未分離: 長clipでAzure/OpenAIが `Melos` と書けた例は、Melosの後ろがs始まりの語ではない(Opus指摘)。
2. **文脈結合は正認識率を明確には上げず、誤PASS(masking)の候補を増やす可能性がある**(真値未確定): 本番NG take由来のproxy反例で、単独NG→文脈付きPASSに反転した観測 **13/41**(単独NGの10 targetの全rep観測)。内訳は nat_feet 4・nat_design 4・nat_bements 3(同音語・文脈で語が推測できるタイプ、**実効標本は3 target**)と nat_paused 2(語末子音付加のASR揺れ)。固有名詞誤発音3件(Milo/Milos'/Melus')は反転0。proxyの限界(正解は検証済みtake等)があり確定false acceptではない。
3. **既知欠陥の反例(オフライン編集、真値既知)**: 語の欠落/誤語(Melos→ruler、Melos削除、said削除)は文脈付きでも **0/12** でPASSにならない(文脈にMelosが有っても幻覚補完せず)。clip末の予測しやすい語(`said`/`death`、基音声3本)の末尾70〜460msを切詰めた音声は、単独でも文脈付きでもOpenAI/whisperとも最終語を**綴りとしては**正しく書き、検出されなかった(**42/42**。ただし12音声×recipeの**非独立観測**。syn_B1_trunc*は `mello said` 等でProduction判定ならほぼNG[18観測中PASSは3]になるため、42/42は「最終語の綴り一致」基準の数字)。→ 結論は「clip末の予測しやすい語(said/death、基音声3本)の切詰めは、単独・文脈付きともASRの綴りでは検出されなかった」に限定。**語中の語末子音(`Melos` の語末s、OPEN-330対象)は未検証**。70ms切詰が知覚上の欠陥かは真値未確認、300〜460msは母音まで削っている。
4. **Azure STT+Phrase Listは決定的**(同一音声2回で15/15一致)で、文脈の有無でtakeごとの結果がほぼ不変(att1=Melos、att3=Melo、他=Mellow/Mallow)。ただし**決定的=忠実ではない**(Phrase Listも綴りを誘導する)。OpenAIは同一音声でも領域転写が2回で一致するのは72%。
5. 防止条件の評価(OpenAI文脈付き一次): 単独整合(G1)はnatural proxyの反転を13/36→3/36に抑える(D-5の36はtarget×recipeのrep1単位で単独PASSのtargetも含む。D-4の13/41とは母集団が異なる)が、**Melosのように単独が常にNGの問題は救えなくなる**(目的矛盾)。2回呼出一致(G2)・logprob閾値(G3)・独立engine(G4)は反転抑止が弱い/部分的(語末切詰には全て無効)。OpenAI領域tokenのmin logprobはgood_control(5%点-2.48)と欠陥(-1.0)で分離せず、確信度は防止条件にならない。Secondary corroboration必須+HR fallback維持が最低限の安全弁。D-5表頭G0は「Prod判定PASS」ではなく実際の受理基準(切詰/対照syntheticは最終語の綴り一致、それ以外はProduction `classify_asr_match` PASS)に修正(数値不変)。
6. 複数ナレーター: 同一ナレーター文脈 vs 異ナレーター文脈(同秒数、前置)でProd PASS 3秒 15%/0%、7-8秒 23%/8%、13秒 46%/38%、23-26秒 38%/69%(同一/異)。差は一貫せずナレーター差は検出できない(同一内容・別voiceのTTSが要るが本Trialでは禁止のため未分離)。Std(6take)とAdv(1take)の結論は同じ(Advも単独OpenAI 0/1、Azure `mellow` 3/3固定)、Advはn=1。
7. OpenAI promptで作品名を与えると単独36%・3秒文脈付き75%が `melos said`(base 0%)。ただしMellis take(att4)も `melos said` 化(2/2)、att6も3秒文脈+promptで2/2(att4は誤認の疑い)。前文テキストpromptは効果弱い(21%)。AzureのPhraseListは効果あり(nophrase 0/7→2/14)だが再現性はtake依存。

### 4-D. phase2(委任_03)の追加実測(連結発音対策の徹底監査+評価単位+NG時Fallback+再発防止)
- **B 評価単位(長さ vs s+s融合の分離)**: OpenAIは s+s融合の無い「Melos+非s始まり2語cut」(called/turned/had/listened/fell)でも exact **0/16**・Melos語一致 1/16(6%)で、`Melos said`(0/13)と有意差なし=**短さ+OOV固有名詞が主因**(s+s融合の寄与は検出不能: floor effect)。Azure+PLは s+s の寄与が示唆される: `Melos said` take単位 **1/7** vs 非s 2語cut **6/8**、Fisher両側 **p=0.0406**(旧p=0.008は、Azureが決定的でrep1/rep2が同一出力のため2/14とrep重複計上した過大値。委任_04で訂正)。さらに交絡あり(`Melos said`はTTS単独生成clip、非s 2語cutは長clipからの切出し)のため「融合寄与は有意」ではなく**「融合寄与を示唆(交絡あり、確定不可)」**。p=0.041もn=7/8で脆い(att2を含めて2/7にするとp=0.13)。
  - 1文単位(直前台詞+attribution)gap300で OpenAI 2/13 (15%)、gap80 で **0/14**(Azure 0/7)=gapを詰めても改善せず。28秒窓(前後2-3clip)で 10/25 (40%)(文脈にMelos語を含む条件に偏る)。Melos+非s 元clip全体(2.7-4.6秒): OpenAI 2/8 (25%)、Azure 4/4。
  - 編集音声実験: 融合長の摩擦区間を単独s相当(80ms)まで短縮したMelos said(5 take)でもOpenAIの出力は多くのtakeで元と変わらず(att1/3/4: `mello said`)=ASR文字列は融合と単独sを区別しない。Azure+PLはatt1のみ `Melos said`→`Mello said` に変化。
  - 一般語(Production採用済み正常音声の実境界、0.5-1.6秒の2語窓): 融合型6種(SS/TT/DD/NN/YOD/SHS)OpenAI exact 57/144 (40%)、対照(融合しない境界)12/24 (50%)、Fisher p=0.37。2語窓は一般語でも不安定(`by this small`、`top users state`、`meant to be`、`sunlight touch` 等=連結発音で説明できないASR側の別語化)。融合型固有のペナルティは検出できず。注意: 41% vs 52%(全engine混合)とB-1の40% vs 50%(OpenAIのみ)は別母数。
  - 長範囲ASR(1文/段落単位)の設計案: **推奨しない**(gap80で0/14、masking、HR Lock/Master Store整合の問題。窓NGでも責任clip特定が必要、窓合否が隣接clip次第でMaster Store再利用キーが崩れる、HR承認がsha256紐付けのため窓変化で無効化され得る=OPEN-331と同型)。費用の「約14倍」は28秒重複窓の上限値で、重ならない1文単位なら≈1倍(**[委任_04訂正]**)。
- **C NG時Fallback(NG take 5本)**: F1 同条件繰返し=**0/5 take**(OpenAI観測 0/9、Azureは決定的で同一)。F2 前後音声追加(OpenAI): exact率 att2 1/46、att4 5/46、att5 3/46、att6 17/45、b1b 0/23。F3 別engine: Azure exact 0/5 take(att1のみexactだがProduction OK take)、whisper-smallが `melo said` を返しPattern Aで受理3/5観測。F4 文脈付き音韻判定(Trial): 音韻説明可(FUSION)がOpenAI単独3/9、Azure 8/10、whisper-small 5/5、whisper-medium 4/5、VOICING弱説明OpenAI 4/9、説明不能OpenAI 2/9。F1で救済できなかったNG take観測のうち、F4がHR候補にできたのはOpenAI 7/9(FUSION+VOICING)、Azure 8/10。F5 F4+音響独立証拠: 単独gateとして不可(AUC 0.74)。
  - 人間確認の実例: a2_att4はOpenAI `Mellis`/Azure `mallow` でTrial音韻判定も説明不能(既存判定に委譲)だが、ユーザーHR試聴では**承認**された。取りこぼしの原因は母音一致の厳格さで、改善案=unstressed母音(AH/IH)許容を(b)G2P導入案と並記。3分類の「NG」ラベルは「説明不能(既存判定に委譲)」の意味(人間NGの意味ではない)。
- **D 再発防止(Melos以外の一般例+反例)**: Production実データ英語2,030対で語境界の子音連続は7,412境界。境界付近に綴り差が出た割合(上限値)は、同一子音の重なり1,841境界で8.9%、歯擦音連続476で7.4%、歯擦音+口蓋歯擦音509で4.3%、同位置破裂音877で2.7%、yod 366で1.1%、その他破裂音連続3,343で1.6%。融合しやすい境界でもProductionの実運用ではほぼ綴り一致で通っている。実データの差分124 instance: Trial音韻判定 FUSION 15 + VOICING 2、HOMOPHONE_ONLY 26、NO_PHONOLOGICAL_EVIDENCE 11、NOT_EXPLAINED 70(実際の別語化・数値・語脱落)。FUSION/VOICING 17件の内訳: Productionが既に受理(Pattern A)6件、現行未受理11件(Melos関連7、一般語4 instance=`the products stores stock→the products' store stock`[s+s]、`some Muse calls→some use calls`[m+m、2出所]、`pay showed coffee→pay show coffee`[d+k])。**Melos以外の固有名詞の実データは0件**(OOV固有名詞への一般化は合成評価のみ)。
  - 一般語2語窓の3分類(正常音声=真値「正常な連結発音」): 融合型n=288: 現行Production PASS 45% / Trial許容(綴り一致のみ)41% / HR 2%(6/288) / 説明不能57%。対照n=48: 69% / 52% / 6% / 42%。Trialは一般語の正常音声でほぼ新たな許容を生まない。45%→41%の低下は `Melo said` 型(Pattern AがASR綴りだけで自動PASS)をTrialは独立証拠なしのためHRに止める差(Melo/Mello非対称、OPEN-330)。
  - 反例(真値既知): 欠落語 0/26許容、誤名(`ruler`)0/15、固有名詞誤読proxy 0/39。**増分誤許容19件(すべて `syn_B1_trunc*`)**(上記3-4)。
  - 人間verdict: HR queue(75件)は `final_status` のみで人手verdictを保持しないため、「過去に人間がNGとした実音声」は取り出せなかった。→ 新規OPEN-335。
  - 残余リスク型: (R1)融合と脱落のASR文字列上の不可分(音響証拠未校正)、(R2)OOV名のG2P欠如、(R3)unstressed母音差(`Mellis`型)の取りこぼし、(R4)clip末切詰の併発、(R5)一般語でも2語窓のASR別語化(連結発音以外の失敗)は説明不能のまま。

### 4-E. 改善方式の比較(机上+実測。採用判断なし)
| 方式 | 要点 | A/B/C分類 |
|---|---|---|
| (1) clip分割維持+ASR時のみ前後文脈結合 | att6以外は名前が文脈にある時のみ上がる(プライミング)。反転13/41。auto-acceptには非推奨(REJECTED)、診断用途のみ可。OpenAI 8秒文脈で約JPY0.03/回、Azure約JPY0.36/回 | B(OPEN-318 C-c) |
| (2) TTS clip自体を長くする(原稿/分割ルール) | 既存証跡ではAzure長clip8/10(2語clipは0/8)、OpenAI 10語超10/22(3語以下0/6)だが長さとs+s融合が交絡で効果自体は未検証。TTS再生成不要(新規記事の原稿/分割で回避) | B(OPEN-318代替案③) |
| (3) ASRへ文脈情報を与える(prompt/Phrase List/前文) | OpenAI promptは単独36%/3秒文脈75%だがmasking懸念。AzureのPhraseListは既存仕様。単独ではmasking懸念、独立証拠(Azure/音響)と必ず併用が条件 | Azure PhraseList=A、OpenAI promptのbody拡張=C |
| (4) 既存CS/Resolver/Secondary ASRの再判定改善 | A'(stem同音)は効果限定的。作品単位allow-listは方針決定と等価(3択)。OPEN-330範囲確定が前提 | A'拡張=B(OPEN-327)、allow-list=B、OPEN-330範囲確定=A |

### 4-F. Opus独立レビューで修正した点(主要)
**TRIAL_REPORT_01(委任_02): Opus必須修正4点+推奨**
1. **Status過大表示の修正**: 旧「VALIDATED」表記を廃止。Statusは「C-c(ASR時のみ文脈結合)のauto-accept化: REJECTED(Trial実測) / 推奨(2)(4)+音響証拠: 未実装・未検証、USER_DECISION_REQUIRED / 計測: Trial完了」。
2. **原因説明の訂正**: 「主因はclipの短さではない」等の断定を撤回し、3点併記(プライミング優勢、att6は音響の可能性で真値未確定、長さとs+s融合の交絡)。att6の17/45は「masking主証拠」から「真値未確定の候補」に弱め。
3. **42/42ラベルの訂正**: 「語末子音脱落の一般化可能な実証」から「clip末の予測しやすい語の切詰めは単独・文脈付きともASRの綴りでは検出されなかった(12音声×recipeの非独立観測、Production判定ならPASS 3/18)」に限定。語中の語末s(Melos)は未検証。
4. 推奨(2)(4)の訂正: 例文`Melos said softly to the ruler.`の旧提示は不適切だった(`Melos said ...`はs+s融合が残る)。ルールを作品非依存の音声的条件として書き直し。allow-listは「方針決定と等価」と明記し3択提示。
5. 推奨修正: 数値統一(OpenAI 25% vs 8% / att6除外 24% (13/55) vs 2% (3/198)、whisper 74% vs 0%、旧「78%」は誤記)、費用累計(「+39.5」を39.61に統一)、OpenAI音声入力token単価は未確認(`pricing_snapshot.json`にtext単価$1.25/Mのみ、過小評価の可能性、usage画面照合要、推定値なし)、本文33件と表34件の定義差(exact_tokens vs focus_exact)。

**PHASE2_REPORT_02(委任_04): Opus独立レビュー(phase2)必須修正5点+推奨**
1. OPEN-122(4)見送り理由の訂正(2-3参照)。
2. 推奨を上流対策へ戻す(説明付きHR候補化はHR件数を減らさない)。
3. Trial音韻判定の安全前提の明記とtest固定(`protected_check`通過後のみ、`risk_flags`、音響証拠の境界型照合、`second_engine_exact`除外)。
4. **p値の計数修正**: Fisher p=0.008 → take単位 1/7 vs 6/8 で **p=0.0406**、交絡明記。
5. Melo/Mello非対称をユーザー判断事項へ。
- 推奨修正: 長範囲ASR費用「約14倍」=28秒重複窓の上限(重ならない1文単位は≈1倍)、OpenAI単価不整合(¥0.004 vs 実計上約¥0.0052/秒)は未確認のまま推定値なし、`derived_stem_s`(`melos`=M EH L OW Z)は綴り推定でLedger期待読みと不一致(OPEN-308)、音響AUCのラベル・測定失敗の限界、3分類「NG」を「説明不能(既存判定に委譲)」へ改名(コード上のクラス名は後方互換で`NG`のまま)。新規OPEN-335。

---

## 5. Melos以外の一般例を固定した回帰test(32件)の内容要約
ファイル: `er065_short_clip_asr_context_trial_01_regression_test_01.py`。ASR呼出なし、既存転写入力、telemetry追記無効化。全32件PASS(委任_03で19件+委任_04で13件)。実行: `.venv\Scripts\python.exe er065_short_clip_asr_context_trial_01_regression_test_01.py`。
- **ProductionCharacterization(7件、Production現行挙動の固定)**: Pattern Aの綴り水準受理(`Melos said.`←`Melo said.`、`The studies suggest that`←`The study suggests that`、`the guards seized`←`the guard seized`、`stores stock`←`store stock`)/同音別綴り(`Mello`/`Mellow`/`Mellis`/`Mellos`)は現行未受理=UNCERTAIN(OPEN-327の記録。この固定が崩れたら是正が入った合図)/既知欠陥(`Melon`/`Marcus`/`Mel`/`Melody`、`Melos aid.`/`Melos.`)は誤PASS 0/接尾辞でない語末子音欠落(`school starts`←`schoo starts`、`nice sign`←`nigh sign`)は過受理なし/Pattern Aは形態素非依存(`bus stops`←`bu stops` ACCEPT、OPEN-330)/Eq LayerはOOV `melos` に到達不能(`word_phones("melos")` が None、判定 `NOT_A_PHONEME_PREFIX_DROP`)/辞書語(`pay showed coffee`)でも独立corroboration無しでは非受理。
- **TrialPhonologyJudge(7件)**: Melos said系(`Mello`/`Mellow`/`Melo`)=FUSION、`meloset`/`Mellowset`=VOICING、`Mellis`/`Melon`/`Marcus`/`Melody`/`Mel`/`Melos aid`/`Melos.`/`Melo sat`=NOT_EXPLAINED、`Mellos`=HOMOPHONE_ONLY。一般語の実データ: `the guards stopped`/`the guard stopped`・`stores stock`/`store stock`・`The studies suggest`/`The study suggest`・`last time`/`lass time`(t+t)・`pay showed coffee`/`pay show coffee`(d+k)=FUSION、`some muse calls`/`some use calls`(m+m)=VOICING。非融合の別語化(`when Melos spoke`/`when Milo spoke`、`followed two groups`/`followed three groups`、`is safe`/`is unsafe`、`experts spoke with`/`experts speak with`)=NOT_EXPLAINED。stemの無いOOV(`Zxqvt said.`/`Zxqv said.`)=NO_PHONOLOGICAL_EVIDENCE。
- **ThreeWayPolicy(5件)**: ASR推測のみでは許容にならない/独立証拠があっても許容になるのは「説明可」のみ/反例は証拠最大でも許容にならない/VOICINGとHOMOPHONEは証拠があってもHR止まり/EXACTは許容。
- **TrialSafetyPremise_Delegation04(8件)**: 単体で否定(`can't talk`→`can talk`)・時制(`walked`→`walk`)・別語(`great time`→`gray time`)を「説明可」と出す穴の記録、`risk_flags` の各検出、`three_way_with_flags` が反例を許容にしない、`three/tree` 非許容、Melosの許容経路が壊れない回帰、破裂音境界で音響証拠が測定不能、摩擦音境界で適用、Phrase List第二engineは独立証拠でない。
- **ProductionPatternsAndEqLayer_Delegation04(5件)**: Pattern B一般例(`it opened to`←`it open to` ACCEPT、`opened up`は非発火)、Pattern C一般例(`The survey suggest`/`The surveys suggest` → Pattern_C_resegmentation_added_consonant)、Eq Layer受理経路(`pay showed coffee`で独立ASRがcanonical綴りを返した場合のみACCEPT、同じ誤転写なら非受理)、減速後経路の配線現状(TRUE_CONTENT_MISMATCH→cascade非呼出、UNCERTAIN→cascade呼出だがEq Layer flag非渡し)、Eq Layer入口が `TRUE_CONTENT_MISMATCH` 限定であることのソース固定。
- 注記: 既存対策の機能確認は**単体関数レベル**(Pattern/Eq Layer関数への入力転写固定)であり、retry loop全体のE2E再現ではない。
- 別test(CS監査 委任_01〜03): `er026_cs_audit_regression_01_test_01.py` 12件PASS(3 testをcharacterization化: `test_characterization_proper_noun_stem_final_s_drop_accepted_by_pattern_a_open330` 等。OPEN-320/328/330是正時に期待値を反転・更新)。`er026_post_slowdown_cascade_rescue_01_test_01.py` 16件、`er011_no18_connected_speech_reading_resolver_wiring_08_test.py` 15件、`er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py` ALL PASS、`er006_secondary_asr_01_test.py` ALL PASS(CS_AUDIT §10)。

---

## 6. 残課題・未決とユーザー判断(いずれも未承認・未実装・Production無変更)

### 6-1. 未決・残課題
- **OPEN-122(4) 一般語ギャップ**: 減速後に辞書語の `TRUE_CONTENT_MISMATCH`(`studies suggest`、`pay showed coffee` 型)へEq Layerが効かない。承認済み仕様の配線漏れではなく既知のスコープ外。量産時のretry浪費・HR反復に直結し得る。
- **Melo/Mello非対称(OPEN-330追記)**: 同じ音素列(M EH L OW)でも、`Melo said` はPattern A(`protected_check` の複数形吸収→L1119 fallback)でASR綴りだけを根拠に自動PASS(Std a2 part1_c5 take3の実例)、`Mello said` はTrialでは独立証拠なしでHR止まり(Productionでも未受理=OPEN-327)。「ASR推測だけで自動PASSしない」原則を既存Pattern Aにも遡及適用するか、新規綴り変種のみか、が未決。
- **OPEN-330(Pattern Aの語幹末s受理範囲)**: 選択肢 (a)現状承認(広い受理範囲を正式仕様として確認、仕様文書化のみ)/(b)接尾辞に限定(形態素的に -s/-es 接尾辞と判定できる場合のみ。固有名詞は対象外=Melos→Meloは受理されなくなりHR化が増える。最も保守的)/(c)固有名詞は作品単位の人間承認(許容語幹リストを人間が一度承認した場合のみ受理。OPEN-327の作品単位許容リスト案と一体。(c)は(i)方針許容 (ii)audio sha256紐付け (iii)音響的独立証拠併用 から選ぶ)。
- **OPEN-327**: C-1(stem同音A'、PASS_WITH_WARNING+独立ASR corroboration)は最低優先(効果が小さく語末s脱落の誤PASSリスクが残る)。C-2(音響独立証拠)、作品単位allow-list案、次Trial候補=参照テキスト付き音素評価(Azure Pronunciation Assessment、またはlocal forced alignment/wav2vec2音素CTC[プロジェクト未使用]。ユーザー試聴ラベルを真値に校正、語中の語末s[s+s接続含む]の切詰め反例を追加、実施前に費用見積+Opus条件A)。不確実性: Adv b1b part1_c5の実測は1 take(TTS 1回)のみ、Std側もtake差で転写が揺れる(Mello→Mellis→Mallow)ため「Mello/Mellowを返す」は一般則と言えない。
- **OPEN-328**: 観測性(attempt_history/tts_generation_resultsに呼出層ごとの `connected_speech_enabled` 実値と `layer_invoked` が残らない。記録のみの追加案)、減速後cascadeのEq flag未配線、telemetry重複行1,998行(7156〜9153行)の巻き戻し判断。
- **OPEN-318**: C-a(試聴で1回確定→`seed_work_canon_reading`)、C-c(ASR時のみ文脈結合)=本Trialで実測、代替案③(said Melosの語順、前後clipと結合)、固有名詞のみ短clipを避ける原稿/分割ルール、Gate7閾値(2語clipでLRが全面書換と判定)。
- **OPEN-320**: 減速後cascade枯渇時にHRへ到達せず最終STOPPED(`review_lock_state.json` が `RESOLVED/OK` のまま `tts_generation_results.json` は `STOPPED`)。part1_c5は再実行未実施、ユーザーHR3件個別承認後もgate stageでSTOP。
- **OPEN-331**: HR承認take(attempt4、6%減速前)→減速後再検証Gate STOP(ratio=1.2683)。選択肢案 (a)attempt4に`apply_a2_slowdown_postprocess`適用[ローカルDSP+ASR再検証 約JPY0.2、承認音声から6%変化]/(b)減速のみ適用しASR再検証を省く運用承認/(c)Std part1_c5のみ減速免除をユーザーが承認(Gate例外=新仕様)/(d)再度HR試聴(減速版)。FINAL-ASSEMBLY 委任_02/03で(a)の経路(JPY0.24)が実行されgate/assemble/pages/page_verify/Playwright実再生まで完成した旨が追記済み。残: HR採択take配置の汎用機構、RESTART_STORM検知の誤検知注意。
- **OPEN-335(新規)**: HR queueに人間verdictが残らず再発防止を実データで評価できない。提案(未実装): HR承認/却下を `record_human_approval` 系にclip sha256・canonical・ASR転写・verdict・日時で記録。
- 任意(無料): a2_att6/att1/att3の人手試聴で、attempt6の文脈付き `melos said` が真に `said` か `set` かを確定(真値)。

### 6-2. ユーザー判断として提示済みの選択肢
**短尺clip ASR判断1〜4(PHASE2 E-6、DECISION_LOG 委任_04、UDR #25=UDR状態、#23の依存事項)**
1. **上流対策**(attribution clip最小語数、歯擦音で終わる名前+s始まり語の回避)をZ writer/structure仕様のTrialへ進めるか。推奨=進める(HR反復を減らす第一候補)。
2. **OPEN-122(4)の一般語ギャップ**(減速後の辞書語`TRUE_CONTENT_MISMATCH`にEq Layerが効かない)の扱い。選択肢=現状維持/入口条件の拡張を別仕様として設計(Opus独立レビュー要)。推奨=量産でのretry浪費・HR反復の実測頻度を把握(telemetry観測性OPEN-328と同時)した上で判断。
3. **Melo/Mello非対称**: 原則「ASR推測だけで自動PASSしない」を既存Pattern Aにも適用するか、新規綴り変種のみか。推奨=判断保留(Pattern Aは承認済み仕様で変更は影響大。OPEN-330の選択肢と併せてユーザー判断)。
4. **Trial優先順位**: 推奨=上流対策 > (d)forced alignment/Pronunciation Assessment(音響証拠の再較正) > (b)G2P導入(unstressed母音許容案と並記)。

**TRIAL_REPORT_01(委任_02)の残るユーザー判断事項案U1〜U4(参考。委任_04のE-6が最新)**
- U1: ASR文脈結合(C-c)をauto-accept条件にしない(REJECTED)の確認。推奨=確認(診断用途のみ可)。
- U2: allow-list(4)の方針3択 (i)方針許容 (ii)audio sha256紐付け (iii)音響的独立証拠併用。推奨=(ii)を基本に、(iii)の校正結果が出れば併用。OPEN-331と一体で判断。
- U3: 原稿/構造ルール(2)(作品非依存の音声的条件)を新仕様候補としてTrial化するか。推奨=Trial化(長さとs+s融合を分離する実験設計とセット)。
- U4: 音響的独立証拠(音素評価)の次Trialを許可するか。推奨=許可(実施前に費用見積+Opus条件A)。

**ユーザー決定済みの関連状態(USER_DECISION_REGISTER_01)**: #10 Melos HR 5clip: 判断済み(2026-10-13、HR 3件を個別承認、#23参照)。#23 Melos最終試聴・受入判断: 判断保留(依存事項待ち、2026-10-13ユーザー指示。依存=(a)Voice Prompt改善の正式採用仕様とMelos適用範囲 (b)ASR連結発音・短尺判定の改善[OPEN-318/327/330/331/122(4)/335、短尺ASR判断1〜4]。現行試聴ページは暫定、再試聴依頼禁止)。#25 短尺ASR判断1〜4: UDR(#23の依存事項)。

**CS監査側の改善案(未導入、Production投入禁止、USER_DECISION_REQUIRED)**: C-1 音素水準A'(隔離Trial+Opus条件A必須、最低優先)/C-2 音響独立証拠(無料オフライン校正から)/C-3 作品単位EN読み確定(OPEN-318 C-a、OPEN-308)/C-4 観測性(OPEN-328)。有料検証案(既存6wavへAzure×3/OpenAI×1、上限JPY10)は未実行。

---

## 7. Status・費用・使用モデル

### 7-1. Status
- **FAMILY-Z-MELOS-CONNECTED-SPEECH-ROOT-CAUSE-AUDIT-01**: 委任_01〜03完了(Sonnet委任3回)。分類=A(是正済み)+C(設計上の不足)+D残余。配線バグ新規なし。Production code変更0。新規OPEN-327(USER_DECISION_REQUIRED/未承認・Trial要)・OPEN-328(OPEN候補・未承認)・OPEN-330(USER_DECISION_REQUIRED/未承認)起票、OPEN-318/320/322追記。C案(拡張)はTrial+Opus独立レビュー(条件A)必須でProduction投入禁止。Opus独立レビュー(委任_03)必須修正4点は反映済み。Sonnet委任上限に対する到達の記載は原本に記載なし(委任ログは3回)。
- **FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01**: 委任_01〜04(合計4回=**Sonnet委任の上限(初回+修正3回、合計最大4回)に到達**。委任_04の委任ログに「本管理IDのSonnet委任の上限(4回目)」と記載)。Status: **C-c(ASR時のみ文脈結合)のauto-accept化=REJECTED(Trial実測)/ 音韻説明可の自動許容側=REJECTED(単独gateとして、独立証拠未校正)/ 推奨(2)(4)+音響証拠=未実装・未検証、USER_DECISION_REQUIRED / 計測=Trial完了**。「VALIDATED」「APPROVED」は使わない。Production無変更、TTS生成0、Production state書込0(`state_guard_02.json`、`telemetry_guard_01.json`でsha256一致)。上限到達のためこれ以上のSonnet委任は不可(以降はUSER_DECISION_REQUIREDとして扱う)。
- Production採用(`APPROVED_FOR_PRODUCTION`)は人間ユーザーのみ。本件のいずれの案もまだ承認されていない。

### 7-2. 費用
- CS監査: 有料API 0、JPY0(委任_02の再生成のみ+JPY0.60)。Melos案件累計 約JPY185.4/300(委任_02時点、COST_LEDGER最終値)。
- 短尺clip Trial 委任_01: **JPY39.61 / 40**(OpenAI 19.87[4,816音声秒]、Azure 19.74[443音声秒]、local whisper 0)。呼出984件。Melos累計 185.4+39.61 = 約225.0/300。OpenAI音声入力token単価は未確認(text単価$1.25/Mで計算、過小評価の可能性、usage画面照合要)。
- 委任_02: JPY0。委任_03(phase2): **JPY 8.21 / 20**(OpenAI 2.60 / Azure 5.61 / local whisper 0)。Melos累計 約233.2 / 300。委任_04: JPY0。
- 合計(Trial): 39.61 + 8.21 = 約JPY47.8。

### 7-3. 使用モデル(最新モデル原則 PM_GOVERNANCE 25節)
- 評価ASR: OpenAI `gpt-4o-mini-transcribe`、Azure Speech STT(en-US)+Phrase List。Production同一モデル(最新モデル原則の例外理由=比較可能性: Productionの実判定条件で評価するため)。local faster-whisper small/medium は無料の第三者参照(Production対象外)。
- CS監査のLR候補生成・QAは `gpt-6-luna`(Productionの既存Local Rewrite実行ログ)。
- 実行層: sandwich-pm配下 sonnet-worker(Sonnet 5.5)。Opus独立レビューが委任_03(CS監査)・委任_02/_04(Trial)で実施された旨は委任ログ・報告書に記載(使用モデルの具体名は原本に記載なし)。

---

## 8. 参照URL(raw.githubusercontent.com、main)
正本・報告:
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er026_output/family_z_production_e2e_01/melos/cs_audit_01/CS_AUDIT_01.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er065_output/short_clip_asr_context_trial_01/TRIAL_REPORT_01.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er065_output/short_clip_asr_context_trial_01/phase2/PHASE2_REPORT_02.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er065_output/short_clip_asr_context_trial_01/phase2/A_AUDIT_02.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er065_output/short_clip_asr_context_trial_01/analysis_tables_01.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er065_output/short_clip_asr_context_trial_01/phase2/analysis_b_02.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er065_output/short_clip_asr_context_trial_01/phase2/analysis_c_02.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er065_output/short_clip_asr_context_trial_01/phase2/analysis_d_02.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er065_short_clip_asr_context_trial_01_regression_test_01.py
委任ログ:
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-CONNECTED-SPEECH-ROOT-CAUSE-AUDIT-01_01.md (_02, _03 も同ディレクトリ)
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-13_FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01_04.md (_01〜_03 も同ディレクトリ)
SSOT:
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN_ITEMS.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/USER_DECISION_REGISTER_01.md

## 付記(読取り範囲と未確認)
- `analysis_b_02.md`/`analysis_c_02.md`/`analysis_d_02.md`、`analysis_tables_01.md`、TRIAL_REPORT_01.md 付録(C-2b/C-2c/C-2d/D-4b/D-5の生表)の詳細表は、本再掲では報告書本文・PHASE2_REPORT_02の数値引用に留め、生表の逐一再計算・全行転記はしていない(出典: 各ファイル)。
- 本ファイルは未commit(委任指示)。
