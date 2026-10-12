# FAMILY-Z-MELOS-CONNECTED-SPEECH-ROOT-CAUSE-AUDIT-01 委任_01 CS_AUDIT_01

(2026-10-12。read-only調査+オフライン再現。有料API 0、TTS生成 0、runner起動 0、HR Lock/run_e2e_02 state書換 0。
local faster-whisper(無料CPU)とPython純関数のみ使用。Production code変更 0。親: FAMILY-Z-MELOS-PROPER-NOUN-ASR-ROOT-CAUSE-01)

## 0. 結論

先行調査の「2語clipで機械判定不能(分類D)」は **そのままでは維持できない**。実測は次のとおり。

1. **承認済みConnected Speech機構は配線されており、今回のログでも実際に発火した**(コード上の存在ではなく実発火)。
   Pattern A(B1 Connected Speech Validator)は、本Melos案件のログで **計5回** `CONNECTED_SPEECH_ACCEPT`を出し、うち **4回がMelos clip**
   (`er011_output/attempt_history.jsonl`: run_e2e_01 b1b part1_c1 / part1_c20 ×2、**run_e2e_02 Std a2 part1_c5 fallback attempt**。残り1回は run_e2e_02 b1b part1_c3 `guards→guard seized`)。Std a2 part1_c5 は減速前に **2回PASS**(take1=Tier3「Azure=Melos said.」、
   take3=Pattern A「Azure=Melo said.」)しており、STOPPEDの直接原因は **減速後の再検証に救済が無かったこと**(分類A、委任_01で是正済み)。
2. 一方、Adv b1b part1_c5 の HR 到達と、Std の減速後最終wavが今も救済されないのは、**分類C(設計上の不足)** が主因:
   - Pattern A は **綴り水準**(ASR語 == canonical語から`-s/-es`を除いた綴り、完全一致)の規則。ASRが同じ音を `Melo` と綴れば受理されるが、
     `Mello`/`Mellow`(CMU音素は `Melo` と完全同一 `M EH L OW`)と綴ると対象外になる。
   - 音素水準の拡張である Equivalence Layer(OPEN-122)は **(i) `TRUE_CONTENT_MISMATCH`でのみ呼ばれる**(`er006_secondary_asr_01.py` L547-548)ため、
     固有名詞差由来の`ASR_VALIDATION_UNCERTAIN`には到達せず、**(ii) 仮に到達しても CMU辞書に`melos`が無く**
     (`word_phones("melos")=None`)`NOT_A_PHONEME_PREFIX_DROP`で終わる。つまり固有名詞(OOV語)に対しては構造的に発火できない。
3. 固有名詞のentity gate(`entity_only_diffs`→UNCERTAIN)が先に走って Validator に到達しない、という懸念(重点項目6)は
   **実測では「到達しない」ケースが0**だった: 接尾辞-sだけを落とした綴り(`Melo`)は`_is_benign_plural_pair`(`er006_preprod_hardening_01_validation.py` L637)が
   差分を吸収するため、entity扱いにならず最終fallback(L1119)でValidatorが走る。合成スイープ(18固有名詞×6語, 108件)で exact stem drop は108/108 PASS、
   entity gateに遮られた件数は0。ただし「stemと同音だが綴りが違う」(`Mello`/`Mellow`)は`entity_like`差になり、Validatorは呼ばれず(呼ばれても未分類)UNCERTAINで止まる。
4. **英語音声として自然な現象か**: 可能性は高い(語末`-os`の/s/と次語頭`said`の/s/の歯擦音連続=Pattern Aの音韻環境そのもの。
   同一wavをOpenAI/Azure/local whisperに通すと `Melo`/`Mello`/`Mellow`/`Mellos`/`Melos`と揺れ、`Melos`と書かれたのはtake1のAzureのみ)。
   **機械判定で安全に自動PASSできるか**: 現状の独立証拠(ASR文字列)だけでは不可。語末sを実際に落とした発音崩れと、歯擦音融合で聞こえにくいだけの正常音を、
   綴りからは区別できないため(安全≠成功原則)。音響的な独立証拠(摩擦区間長)は探索的に有望だが、n不足で未校正(§6)。
5. 分類: **A(是正済み: 減速後救済欠落)+C(設計上の不足: OOV固有名詞に対し音素水準のCS判定が構造的に不能)+D残余(音声実体の真偽)**。
   新規のバグ(B)は未発見。**Productionコード変更なし**。再発防止testを追加(12件PASS)。

## 1. runtime trace(既存ログのみ。証拠が無い項目は「未確認」と明記)

### 1-1. Adv(b1b)`full_story_part1_c5`「Melos said.」

| 列 | 内容(出典) |
|---|---|
| Production入口 | runner → `er063_family_z_audio_01.py::real_generators().narrator`(L552-557、`spec.level=="b1b"`) → `news_tail_fix.generate_news_narration_wide_margin`(`enable_connected_speech_equivalence_layer=cs(spec)`、`enable_pronunciation_resolver=True`) → `secondary_asr.evaluate_attempt_with_cascade`(`er003_v1_sing01_news_tail_fix.py` L199-206でsegment_id導出) |
| Segment識別 | clip_id=segment_id=`full_story_part1_c5`、voice=narrator、`role=FULL_STORY`(`b1b/audit/tts_generation_results.json`)。`er020_tts_retry_local_rewrite_01.py` L135 `_FAMILY_Z_STORY_CLIP_PATTERN.fullmatch`→FULL_STORY。cascade内にTier3 stepが存在(`segment_id is not None`が前提、`er006_secondary_asr_01.py` L598)→segment_idは実際に伝播 |
| CS有効化 | 呼出時 `connected_speech_enabled_for("full_story_part1_c5")=True`(`tts_generation_results.json`: `connected_speech_enabled: true`)。伝播: er063 `cs(spec)`(L549)→`generate_news_narration_wide_margin`引数→`evaluate_attempt_with_cascade(enable_connected_speech_equivalence_layer=...)`。**呼出層ごとの実値は記録されていない**(attempt_historyにflag値の列なし。results.jsonのspec単位値のみ)→各層の実値は「コード上の引数渡しは確認、実行時の層別値は未確認」 |
| Primary ASR | OpenAI `Mello said.` → `ASR_VALIDATION_UNCERTAIN`、entity_like_source=`["capitalized"]`、sub_reason=`entity_only`(`er021_output/.../telemetry.jsonl` L7062-7063、attempt_history L12619) |
| Validator Pattern A〜C | **Primary段階では呼出なし**: `classify_asr_match`(`er006_preprod_hardening_01_validation.py`)は`entity_only_diffs`(L1064)をL1096-1099でUNCERTAINにreturn、CS Validatorの呼出箇所はL1068(`non_entity_diffs`)とL1119(diffが空の最終fallback)のみ。`Mello`は`Melos`のbenign plural対でないためL1064に残る。**仮に呼んでも**`classify_connected_speech("Melos said.","Mello said.")=UNCLASSIFIED`(`mello`+`s`≠`melos`、本監査オフライン再現)。Secondary stepの`Mellow said.`も同様に未分類 |
| Equivalence Layer | **呼出なし**。`er006_secondary_asr_01.py` L547-548 は`cls.classification=="TRUE_CONTENT_MISMATCH"`が条件で、本件はUNCERTAIN。HRキュー(L73)・attempt_historyに`connected_speech_equivalence_*` stepは無い。強制呼出しても`NOT_A_PHONEME_PREFIX_DROP`(`word_phones("melos")=None`、CMU未収録) |
| Secondary ASR | Azure計3回(Phrase List `["Melos"]`使用): Tier3 `Mellow said.`、secondary_1 `Mellow said.`、secondary_2 `Mellow said.`。OpenAI Primary#2 `Mello said.`(HRキュー`human_review_queue.jsonl` L73、全step転写) |
| 固有名詞処理 | Ledger: `melos` = `cascade_unresolved_entity`/confidence=low/IPA `/ˈmiː.lɑːs/`(TTS注入対象外)。Phrase List使用(Azure)。CMU Case A: `melos`未収録で解決不能(`_step_alternate_pass` L423)。Tier3: Azureが`Melos`と綴らず`tier3_attempted_no_corroboration` |
| 最終Gate | cascade全step不一致 → `stop_retrying` → **Local Rewrite回復を実行**(17:49:42、Luna候補5件`Melos stated.`等、7 Gate全通過0件、`HUMAN_REVIEW_LOCKED_NO_CANDIDATE_PASSED_QA`、`er011_output/local_rewrite_recovery/run_e2e_02/b1b/local_rewrite_recovery_full_story_part1_c5.json`) → HR(`HUMAN_REVIEW_REQUIRED`)。TTS生成は1回のみ(上限3の残り2回は未使用: b1b経路はUNCERTAINで即打切り、A2のような minimal fallback 経路を持たない) |

### 1-2. Std(a2)`full_story_part1_c5`「Melos said.」(narrator、`generate_a2_segment_with_slowdown`経由)

| 列 | take1(18:35:19-24、standard) | take2(standard、18:35:29) | take3(fallback minimal instruction、`gemini-2.5-pro-preview-tts`、18:45:3x) |
|---|---|---|---|
| Production入口 | er063 narrator L559-561 → `n3_tts.generate_a2_segment_with_slowdown`(外側ループ通算TTS 3回上限) → `crosslevel.generate_english_segment_with_fallback`(L340-352 segment_id導出、fallbackは`force_secondary=True`) | 同左 | 同左(`_run_a2_minimal_fallback_attempt`) |
| Segment識別 / CS flag | `full_story_part1_c5`/FULL_STORY/`connected_speech_enabled=true`(`a2/audit/tts_generation_results.json`)。Tier3 step有→segment_id伝播済み | 同左 | 同左 |
| Primary ASR | `Mello said.` UNCERTAIN(entity_only) | `Mello said.` UNCERTAIN | `Mello said.` UNCERTAIN |
| Validator | Primary段階は呼出なし(上記と同じ理由) | 同左 | Primaryは同左。**secondary_1 Azure=`Melo said.` → `classify_asr_match`が`CONNECTED_SPEECH_ACCEPT`(Pattern A)で verified=True**(attempt_history L12673 fallback attempt cascade_steps、`audio_classification: CONNECTED_SPEECH_ACCEPT`) |
| Equivalence Layer | 呼出なし(UNCERTAIN、/PASS済) | 呼出なし(UNCERTAIN) | 呼出なし(Pattern Aで受理済み) |
| Secondary ASR | Tier3 Azure=`Melos said.`(1回) → `SECONDARY_ASR_CORROBORATED_MATCH`(L12671) | Tier3/secondary_1/secondary_2すべてAzure=`Mellow said.`(計3回、HRキュー L75) | Tier3 Azure=`Melo said.`(`melo`≠`melos`で非corroboration)、secondary_1 Azure=`Melo said.`→Pattern A |
| 固有名詞処理 | Ledger/Phrase List/Tier3発火。CMU Case A不能 | 同左 | 同左 |
| 減速前判定 | **PASS**(Tier3) | UNCERTAIN→cooldown 600秒(18:35:29→18:45:29) | **PASS**(Pattern A) |
| 6%減速後再検証 | `A2_SLOWDOWN_REVERIFY` attempt1: Primary=`Mello said`(ピリオドなし) UNCERTAIN → **救済なし → STOPPED**(L12672) | - | `A2_SLOWDOWN_REVERIFY` attempt2: Primary=`Mello said.` UNCERTAIN → **救済なし → STOPPED**(L12674)。TTS通算3回=上限で終了 |

最終: `status=STOPPED`(`slowdown_applied=true`)。**HRキューにはtake2のcascade枯渇分(L75)が記録されているが、最終STOPPEDの直接原因は減速後再検証の救済欠落**(OPEN-320の状態不整合とも関連)。
(注: eb4c6479以降の`_post_slowdown_cascade_rescue`で修正済み。ただしpart1_c5は`--only-clips`対象外のため再実行しておらず、現在のwavでの再評価は`reeval_post_slowdown_01.json` P2: 0/3 PASS、Azure=`Mellow said.`。)

### 1-3. 本監査での追加観測(local faster-whisper、API課金0、`local_asr_probe_01.json`)

同一音声でもASR綴りは揺れる(whisper small / medium):
`a2 att1`: Mello / Mellow、`a2 att2`: Mello / Mellow、`a2 att3(=original)`: Melo / Mellow、`a2 final(減速後)`: Mello / Mellow、`b1b`: Mellow / Mello。
**どの転写にも語末`s`(`Melos`)は無い**。ただしOpenAI/Azure本番ログでは`Mellos`(a2 part1_c1等)、Azure `Melos`(a2 take1)も観測されている(`clip_transcripts_01.md`)。

## 2. 承認範囲 / 実装範囲 / 今回の発火状況(A・Bを独立に)

| | A. B1 Connected Speech Validator | B. Connected Speech Equivalence Layer |
|---|---|---|
| 承認SSOT | OPEN-107(`OPEN_ITEMS.md` L161、WITHDRAWN: Ending-Clarity fallback撤回→Validatorへ置換)/OPEN-110(L164、RESOLVED)/`CURRENT_SPEC.md` L2025。3パターン限定「それ以外へ一般化しない」 | OPEN-122(`OPEN_ITEMS.md` L297、PRODUCTION_WIRED commit `3297d1b`、2026-09-26に5 role拡張)/`CURRENT_SPEC.md` L2026。「既存3パターンのUNCLASSIFIED fallthrough後段」「`TRUE_CONTENT_MISMATCH`+`protected_check`通過+音韻環境カテゴリA〜G+独立ASR corroboration必須」 |
| 実装 | `er011_b1_connected_speech_validator_01.py` Pattern A L151 / B L166 / C L181。配線: `er006_preprod_hardening_01_validation.py` L1068-1094(non_entity_diffs)・L1119-1131(最終fallback)。Cascadeのsecondary stepも同じ`classify_asr_match`を呼ぶ | `er011_connected_speech_equivalence_layer_production_01.py` L142(phoneme_prefix_drop)・L215(本体)。配線: `er006_secondary_asr_01.py` L547-596(`enable_connected_speech_equivalence_layer`)。既定False、呼出元がrole別にTrue |
| 今回の発火(Melos said.) | **発火した**: Std a2 take3(secondary Azure=`Melo`)で`CONNECTED_SPEECH_ACCEPT`。他clipも含め attempt_history 528 attempt中7件がCS系(ACCEPT 5[うち4件Melos]/PASS_WITH_WARNING 2) | **発火0**(呼出条件`TRUE_CONTENT_MISMATCH`に不一致)。attempt_historyのcascade_stepsを持つ112 attempt中`connected_speech_equivalence_*` stepは0件(ただしb1b経路はcascade_stepsがnullで記録されない)。他の証跡では発火実績あり: OPEN-122 Gate3実測、`er014_output/four_type_observation_01/trend/audio/b1b`(point_two、`CONNECTED_SPEECH_EQUIVALENCE_ACCEPT`)。**Melos案件では0回** |
| 範囲内外の判定 | 範囲内: ASR=`Melo`(stem綴り一致)。範囲外: `Mello`/`Mellow`(綴りが違う同音) | 範囲外(構造): UNCERTAINは入口で除外。さらにOOV語はCMU音素が無く`NOT_A_PHONEME_PREFIX_DROP` |
| 抜け漏れ判定 | 配線漏れなし。「綴り水準」の定義に由来する認識範囲の限界(設計上の不足C) | 配線漏れなし(既知Gap: 減速後cascadeにflag未配線、OPEN-122(4))。入口条件+CMU依存で固有名詞に無効(設計上の不足C) |

## 3. 既存仕様の抜け漏れ検証(8項目)

| # | 項目 | 期待動作(SSOT) | 実装(file:line) | 今回の実測 | 判定 |
|---|---|---|---|---|---|
| 1 | Family Z clip_idがFULL_STORY認識 | CURRENT_SPEC 5 role適用、`full_story_part{n}_c{k}`をFULL_STORY(委任_03 M6) | `er020_tts_retry_local_rewrite_01.py` L124-149、`_FAMILY_Z_STORY_CLIP_PATTERN` | results.json `role=FULL_STORY`、Tier3 step発火で裏付け。test(`FlagPropagationAndRoleTests`) | OK |
| 2 | CS flagがCascadeまで伝播 | 5 role=True(OPEN-122追記2026-09-26) | er063 L549/556/561、`news_tail_fix` L199-206、`crosslevel` L340-352、`n3_tts` L352 | spec単位`connected_speech_enabled=true`確認。**呼出層ごとの実値・`layer_invoked`はattempt_historyに無い**(観測性の不足)。コード引数渡しはOK | コードOK/**観測性不足**(OPEN-328) |
| 3 | Dialogue vs Narrator | Voice A/B本文は既定True(`er012_b_family_voices_production_01.py` L489) | Dialogue: `bvoices.generate_voice_body_wide_margin`(L549が`segment_id`を渡さない)。Narrator: `segment_id`導出あり | 本件2clipはどちらもnarrator(`segment_plan_*.json` voice=narrator)。Dialogueだとsegment_id欠落でTier3/Tier1 role gating無効(OPEN-322)、Pattern A/B/Cはrole非依存で有効 | Narratorは問題なし。Dialogueの非対称はOPEN-322のまま(本件に無関係) |
| 4 | Adv/Std差 | 同一承認仕様 | Adv: `news_tail_fix`(UNCERTAINで即打切り→Local Rewrite→HR)。Std: `crosslevel`(UNCERTAINでもfallback+cooldown+6%減速後再検証) | Adv=TTS 1回で HR。Std=TTS 3回、cooldown 10分、fallback経由でPattern A受理、減速後STOPPED | 仕様上の差(既存設計)。Stdの方が救済機会が多い |
| 5 | Std減速前後で同じ対策 | CURRENT_SPEC L2019「post-slowdown再検証を含む全経路」 | `n3_tts.apply_a2_slowdown_postprocess`(是正前: Primary1回のみ)。是正後 `_post_slowdown_cascade_rescue` L117-、`evaluate_attempt_with_cascade_detail(..., segment_id=name)`でflag(`enable_connected_speech_equivalence_layer`)は**渡さない** | 減速前: Tier3・Pattern A共に発火(PASS×2)。減速後(是正前): 救済なし→STOPPED×2。是正後のcascadeは同じ4 stepを適用、Pattern Aは`classify_asr_match`経由で有効。EqLayer flagは未配線(OPEN-122(4)既知Gap。ただし救済はUNCERTAIN限定で、EqLayerはTRUE_CONTENT_MISMATCH限定なので今回の事象には無関係) | **A(是正済み、委任_01)**+既知Gap(記録のみ) |
| 6 | 固有名詞diffがCS判定より先にentity_only/UNCERTAINへ | Validatorは`non_entity_diffs`と最終fallbackで呼ぶ(CURRENT_SPEC L2025) | `validation.py` L1062-1099 | **到達不能になっているケースは0件**(実データ26 CS環境pair・合成108 exact-stem-drop pair全てで、Validatorが受理できる形はentity gateに遮られていない)。`_is_benign_plural_pair`がstem綴り一致を吸収。**到達しないのは「stem同音の別綴り」(`Mello`等)のみ**で、その場合Validator自体も未分類(綴り水準の定義) | gate順序は原因ではない(順序問題なし)。限界は§4の定義 |
| 7 | 3パターン対象外→拡張Layer到達 | UNCLASSIFIED fallthrough後段(OPEN-122) | `secondary_asr.py` L547-548 | UNCERTAIN(entity_only)は到達しない。TRUE_CONTENT_MISMATCHで到達しても、CMU OOV語は`NOT_A_PHONEME_PREFIX_DROP` | **構造上到達不能(固有名詞)**=C |
| 8 | retry/fallback/Local Rewrite/resume適用欠落 | Local Rewrite・cooldown・fallbackも同じflagを使う(OPEN-122追記) | `news_tail_fix.py` L283-296 / `crosslevel` L255-300 / `voice01` L293-316 | Local Rewrite: b1bで実行(候補5件・全Gate不通過、`Melos`を含む候補は残るため改善せず)。fallback: Stdで実行しPattern A受理。resume: 本2clipでは **未発動のため未確認** | 欠落なし(resumeは未確認) |

## 4. 「特殊ケース」判断の再検証

### 4-1. 音声現象として自然か

`Melos said` = `/ˈmɛloʊs/ + /sɛd/`。語末/s/と次語頭/s/は同一調音(歯茎摩擦音)で、英語では1つの長めの/s/に融合するのが通常(Pattern Aの音韻環境と同一: 語末`-s`+歯擦音語頭)。
CS Validator定義(`er011_b1_connected_speech_validator_01.py` L87-99, L151-164): `s_suffix_label_if_match`は **文字列として** `canonical == asr + "s"/"es"`を見る。形態素上の複数/三単現接尾辞に限定してはおらず、`Melos`→`Melo`(+s)も、`bus`→`bu`も機械的に受理する(合成test: `bus stops`←`bu stops`はACCEPT)。語幹末子音(例えば`gas`の`s`が語幹末)も区別しない。
→ 「`Melos said`→`Melo said`」はPattern Aの範囲内。実際、本番でそのPASSが起きている。

### 4-2. 切り分け(5分類)

| 切り分け | 判定 | 根拠 |
|---|---|---|
| 音声自体の発音誤り | **不明(確証なし)** | 同一wav群でASRがMelos/Melo/Mello/Mellow/Mellos/Mello'sに揺れ、どの1つにも収束しない。Azure take1が`Melos`を返しており、少なくとも1 takeには語末sが聞き取れる音がある。TTS側の読みはMEL-os系でLedger期待値(MEE-lahs)と食い違う(OPEN-308) |
| 音声正常だがASRが別綴り | **部分的に確証** | `Mello`=`Mellow`=`Melo`はCMU音素が全て`M EH L OW`で同一。同じwavに対しOpenAI/Azure/whisperが別綴りを返す(`local_asr_probe_01.json`) |
| 連結発音は正常だが既存Validatorの認識範囲外 | **YES(主因)** | Pattern Aは綴り一致のみ(`Mello`/`Mellow`は範囲外)。Equivalence LayerはUNCERTAIN入口除外+OOV |
| 必要機構が未配線・未発火 | 部分的(A: 減速後救済欠落=是正済み)。Validator/Layer自体の配線漏れは **無い** | §3 |
| 独立した音声証拠の不足 | **YES** | 独立証拠はASR文字列だけ。音響(摩擦区間長)は探索的に有望だが未校正(§6) |

→ 分類を **D(機械判定不能)から C(設計上の不足)主体へ訂正**。ただしC案(拡張)の実装は「語末sが本当に脱落した音声」を区別する独立証拠が揃うまで安全でない=Dの核は残る(§7)。

## 5. 汎化検証(オフライン、API 0。`cs_offline_reeval_01.py/.json/_stdout.txt`)

### 5-1. 実データ(HRキュー全step転写+er021 telemetry先頭7155行、612ユニークpair)
- CS環境(最初の食い違い語が`-s`終わり×次語頭歯擦音、または`-ed`終わり×次語頭破裂音)26 pair: 全て現行Validatorでは未分類。内訳 UNCERTAIN 18(うち **17がMelos**、1はthis/the取り違え)、TRUE_CONTENT_MISMATCH 7、NUMERIC 1。
- **entity gateが先に走ってValidatorに到達できなかった(Validatorなら受理できた)pair = 0**。
- 仮説規則A'(stem同音)の候補10 pairは **全てMelos**。→ 実データ上、**Melos以外の事例は存在しない**。他の固有名詞への一般性は合成スイープで評価した(§5-2)。
- attempt_history(528 attempt)のCS系: `CONNECTED_SPEECH_ACCEPT` 5 / `PASS_WITH_WARNING` 2。うち4件がMelos clip(ACCEPT)、残りは`guards seized`(ACCEPT)・`kp3_explanation_en`/`studied them`(PASS_WITH_WARNING)。

### 5-2. 合成スイープ(18固有名詞(-s/-es終わり)×次語6(said, spoke, smiled, sat, saw, stood))
| 種別 | 件数 | 現行Production判定 |
|---|---|---|
| ASR=stem綴り完全一致(`Marcu smiled`等) | 108 | **108/108 `CONNECTED_SPEECH_ACCEPT`**(entity gateに遮られた件数0) |
| ASR=stem同音の別綴り(`Mello`, `Markus`, `Cree`...) | 114 | 6 PASS(`Carlos→Carlo`、stemと綴り一致)/108 NOT_PASS(UNCERTAIN) |
→ 仮説A'(音素がstemと一致すれば受理)が追加で拾うのは12件=`Melos→Mello/Mellow`のみ(他の固有名詞はstemがCMU未収録で音素比較不能)。**A'の効果はMelos固有の偶然(`melo`がCMU収録)であり汎用性は低い**。

### 5-3. 反例(25件の合成表、`cs_offline_reeval_01_stdout.txt`)
`Melos said.`←`Melon`/`Marcus`/`Melody said.`、`Marcus smiled.`←`Marker`、`The studies suggest`←`The studio suggests`、`The bosses said`←`The bonus said` 等: **全て現行でNOT_PASS**(誤PASS 0)。A'も上記反例には発火しない。
同系統の自然現象(general noun `bosses said`→`boss said`、`classes started`→`class started`、`cities seem`→`city seem`)は現行Pattern Aで受理。語尾が接尾辞でない最終子音(`school starts`←`schoo starts`、`nice sign`←`nigh sign`)は未分類のまま(TRUE_CONTENT_MISMATCH)=過受理なし。

### 5-4. 安全な自動判定の可否
- 現行(綴り一致)は安全(誤PASS 0)。stem同音の別綴りまで広げる案A'は、音素一致+歯擦音環境のみを根拠にするため、**語末sを実際に落とした音声でも通る**(Pattern A自体が持つ同じ不確実性)。Pattern Aは「ASRが`Melo`と書いた」という一致を、A'は「ASRが同音の別綴りを書いた」を根拠にする違いのみで、後者はASR選択バイアスが強い(Phrase List/モデル依存)。

## 6. 探索的音響観測(Production判定には使わない、`sibilant_duration_probe_01.*`、`sibilant_calibration_probe_01.*`)
`said`語頭付近の最長摩擦区間(4kHz以上の高域比>0.5のフレーム連続、5ms刻み、ms):

| wav | 区間 | ASR(Azureまたは本番ログ) |
|---|---|---|
| a2 take1 | 190 | Azure `Melos` |
| a2 take2 | 170 | Azure `Mellow`×3 |
| a2 take3(=original) | 120 | Azure `Melo` |
| a2 final(減速後) | 120 | Azure `Mellow`(再評価、2語wavで計8回全て) |
| b1b | 165 | Azure `Mellow`×3(本番)+再評価 |
| 対照 `he said softly.`(a2) | 140 | - |
| 対照 `he said at last.`(b1b) | 90 | - |

run_e2e_02の既存wav(語境界を含むclip)のキャリブレーション: `s`終わり+`s`始まり境界 n=4(160-250ms、平均204ms)、非s終わり+`s`始まり境界 n=48(65-255ms、中央値125ms)。
Melos said.の測定(120〜190ms)は両分布の中間に位置し、**take1(190ms)は融合長に近く実際にAzureが`Melos`と返した**一方、take2/b1b(165-170ms)はAzureが`Mellow`で、一貫しない。**nが不足(A群4件)で閾値を設定できないため、現時点では判定根拠に使えない**(Trial設計に回す、§8)。

## 7. 原因分類

| 事象 | 分類 | 直接原因 |
|---|---|---|
| Std a2 part1_c5 STOPPED | **A(是正済み)** | 減速後再検証に承認済み救済(Tier3/cascade/Pattern A経由)が未配線。減速前は2回PASS。eb4c6479で是正(新規runで有効。part1_c5は再実行未実施) |
| Adv b1b part1_c5 HR | **C** | OpenAI/Azure全転写が`Mello`/`Mellow`(stem同音の別綴り): Pattern A(綴り水準)対象外、Equivalence Layerは入口条件(TRUE_CONTENT_MISMATCH)+CMU OOVで構造的に不能、Tier3はAzureが`Melos`と綴ることが必要 |
| 減速後の最終Std wavが今も救済されない | **C+D** | 同上+減速後のAzureが`Mellow`(8/8)。音声に語末sがあるか不明 |
| Validator/Layerの配線漏れ・実装バグ | **無し** | §3(コード・実測とも) |
| 観測性 | (改善) | flag実値・`layer_invoked`がattempt_historyに残らない。減速後cascadeのEq flag未配線は既知Gap(OPEN-122(4)) |

## 8. 改善案(いずれも未導入。Production投入禁止、USER_DECISION_REQUIRED)

| 案 | 内容 | 期待効果 | リスク | 次工程 |
|---|---|---|---|---|
| C-1(音素水準A') | Pattern Aを「ASR語のCMU音素 == canonicalのstem候補のCMU音素」へ拡張(`PASS_WITH_WARNING`推奨、独立ASR corroboration併用) | `Melos→Mello/Mellow`を救済。ただし§5-2のとおり汎用的な追加救済はCMU収録stemに限られ小さい | 語末sを実際に落とした音声も通る(Pattern Aと同質だが根拠が弱い) | 隔離Trial+Opus独立レビュー必須(条件A: 新規判定構造) |
| C-2(音響独立証拠) | 歯擦音連続境界の摩擦区間長を、既存wav/ASR word timestampで測り、融合長なら語末s存在とみなす補助証拠 | ASR綴りに依存しない独立証拠 | 本監査の観測はA群n=4で未校正。語境界timestampの誤差、話者/速度依存 | まず無料のオフライン校正(既存wavを増やす: 全Family Z/他記事のs-s境界)。TTS再生成は不要な範囲で |
| C-3(作品単位EN読み確定) | OPEN-318 C-a(試聴で1回確定→`seed_work_canon_reading`)。固有名詞をOOVでなくする | 根本対策(全Melos clip) | TTS注入は別Phase(読み変化) | 既存OPEN-318/308のまま |
| C-4(観測性) | attempt_history/resultsに`connected_speech_enabled`実値と`layer_invoked`、減速後cascadeのEq flag有無を記録 | 次回以降の監査が推測不要に | 低(記録のみ) | 実装は小(OPEN-328) |

## 9. 有料検証の提案(実行していない)
- 目的: 既存6 wav(a2 take1/2/3・final・b1b・original)に対しAzure STTを各3回、OpenAI ASRを各1回実行し、「同一wavに対するASR綴りの再現性」(同じwavで毎回違う綴りか、wav差か)と§6の摩擦区間長との相関を取る。
- 期待効果: C-1/C-2のTrial設計に必要な、ASR綴り変動の分散(Azure/OpenAIの寄与)の実測。
- 費用見積: Azure 18回×平均1.3秒(音声秒×$1/時×160円の概算)≒約JPY1〜2、OpenAI約JPY0.5。上限案JPY10。

## 10. test結果

| suite | 結果 |
|---|---|
| 新規 `er026_cs_audit_regression_01_test_01.py` | 12件PASS |
| `er026_post_slowdown_cascade_rescue_01_test_01.py` | 16件PASS |
| `er011_no18_connected_speech_reading_resolver_wiring_08_test.py` | 15件PASS |
| `er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py` | ALL PASS |
| `er006_secondary_asr_01_test.py` | ALL PASS |
| er021 62 / er063 47 / er026統合42 / runner 21 | **未実行**(Productionコード変更0。これらは共有tracked state[telemetry等]へ書込むため、変更0の本監査では実行しない判断。前委任での結果は`ROOT_CAUSE_01.md` §5) |

## 11. 副作用・注意(要Fable判断)
- 本監査の初回オフライン再評価スクリプト(`cs_offline_reeval_01.py`)は、`classify_asr_match`(role適用)が不合格時に追記する共有telemetry(`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`)へ **再評価分の重複行を約1,675行追記してしまった**(行数 7155→9155、うち他agent(Coffee)の追記が約325行混在)。追記は既存実測の複製・合成対のため、統計集計に使う場合は **7155行目以降を除外** してほしい。
  既存tracked fileのため、整理(巻き戻し)は私の権限判断で行わず(試みたが自動承認で拒否)、Fable/ユーザー判断に残す。以後のscript/testは`append_telemetry_log`をno-op化済み(再追記なし)。
- 本ファイルはtelemetryをstageしない(他agentの未コミット差分と混在のため)。

## 12. 費用
有料API 0。local faster-whisper(small/medium)はCPU実行で課金なし。本委任の累計費用 JPY0(Melos案件累計は約JPY184.8/300のまま)。
