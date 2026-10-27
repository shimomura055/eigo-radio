# DIAG_SLOWDOWN_ASR_01(AI-ISLAND-FORM-PRODUCTION-01 委任_04、read-only、API 0・JPY0、2026-10-27)

対象: run `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01`(a2=Standard、b1b=Advanced)の`full_story_part1_k2`(本文「The AIs sent to the island …」)。Productionコード・run dirは未編集。

## 1. 結論(要約)

**判定: 仕様どおり。不具合(減速後再検証で二次ASR救済が未適用)ではない。** 委任_03の疑い(「減速後再検証経路で二次ASR確認が適用されていない」)は反証された。

- 減速後再検証でも、二次ASR(Azure)は**毎回呼ばれ**、Tier3 corroboration(`SECONDARY_ASR_CORROBORATED_MATCH`救済)も**実行された**。Azureの転写が減速後音声では3回とも単数形"AI"で、canonical語`ais`を支持しなかったため、救済が成立しなかった(`corroborated_by: []`)。
- 同じ"AIs"問題は**減速のないAdvanced(b1b)でも**3試行すべてで発生し、Azure Tier3でも救済できずLocal Rewrite(LR)に至った。原因は「減速後経路の実装差」ではなく、**複数形の"s"(acronym+s)がTTS音声からASRに安定して拾われない**こと。減速は主因ではない。

## 2. 証拠

### 2-1 Std(a2) `full_story_part1_k2`の経過(`a2/audit/tts_generation_results.json` segments.full_story_part1_k2 / `a2/narration/attempts/`)

| slot | 生成直後(OpenAI primary / 二次) | 減速後(6%) OpenAI primary | 減速後 二次(Azure) |
|---|---|---|---|
| 1 | "The AI sent…" UNCERTAIN → Tier3でAzure"The **AIS** sent…"→`SECONDARY_ASR_CORROBORATED_MATCH`(`standard_attempts_log[0]`.cascade_steps `tier3_corroboration_secondary`、`azure_real_calls=1`) | "The AI sent…" `ASR_VALIDATION_UNCERTAIN`(`attempts/…attempt2_postslowdown.json`) | Azure呼出あり(raw_usage_log 03:04:50 UTC, 12.989s)、telemetry L7493 `corroborated_by: []`、Azure転写=L7494 "The AI sent … LED…" |
| 2 | "The AIs sent…" `NORMALIZED_MATCH`(二次不要) | "The AI sent…" UNCERTAIN(`attempt4_postslowdown.json`) | Azure呼出あり(03:05:05, 14.282s)、telemetry L7496 `corroborated_by: []`、L7497 "The AI sent…" |
| 3(minimal fallback) | "The AI sent…" UNCERTAIN → Tier3でAzure支持→`SECONDARY_ASR_CORROBORATED_MATCH`(`fallback_attempts_log[0]`、03:08:13) | "The AI sent…" UNCERTAIN(`attempt6_postslowdown.json`) | Azure呼出あり(03:08:23, 12.541s)、L7501 `corroborated_by: []`、L7502 "The AI … they're starting settings LED…" |
| LR(slot4) | "The AI agents…" `NORMALIZED_MATCH` | primary `TRUE_CONTENT_MISMATCH`("rewards"→"awards")、**Azure"rewards"で救済**→`NORMALIZED_MATCH`(`post_slowdown_cascade`、secondary_confirmed) | Azure呼出あり(03:09:24, 14.276s) |

- `slowdown_attempts_log`の3行はいずれも`classification=ASR_VALIDATION_UNCERTAIN`(`post_slowdown_ng=true`)。
- LR採用attemptでは減速後にprimary NG→Azure救済が実際に機能している(`post_slowdown_cascade.steps[1]`)。つまり減速後経路にSecondary救済は配線され機能している。
- Azure呼出数: raw_usage_log上、a2 `full_story_part1_k2`で6件(生成時tier3 2件=03:04:40/03:08:13、減速後3件、LR減速後1件)。減速後wav(別sha)ごとに1回ずつ=`SecondaryCache`の仕様(同一wav重複なし、別wavは別呼出)どおり。phrase_list_size=0は生成時・減速後とも同一。
- 一時的なAzureの"AIS"(slot1生成時のみ。全大文字で出力されトークン化で`ais`に一致)に依存した救済であり、再現性は低い。Azureは減速後wavでは3/3回とも単数"AI"。

### 2-2 Adv(b1b)は減速なしでも同じ失敗(`b1b/audit/tts_generation_results.json`)
- attempts 1〜3 すべて OpenAI "The AI sent…" `ASR_VALIDATION_UNCERTAIN`、`asr_judgement.state=NG_BOTH`(Azure Tier3でも救済できず)。attempt3は`…attempt3_minimalfallback`。LR(slot4)で"AI systems"に書換えて採用(`b1b/…hr_packet_data_01.json` selected_candidate=2)。
- Advは減速後処理を持たない(`slowdown_applied`なし)ため、**減速が原因なら起きない事象**が起きている=減速非依存の根拠。

### 2-3 コード経路(Grep/Read)
- (b) 減速後再検証: `er003_v1_n3_01_tts_generate.py:122-192 _post_slowdown_unified_judge` → `secondary_asr.evaluate_attempt_with_cascade_detail`(`:145-153`)。呼出元 `apply_a2_slowdown_postprocess`(`:195-315`、`segment_id=name`=chunk idをそのまま渡す)。chunk系は`make_slowdown_post_hook`(`:340-361`)から同関数を呼ぶ。
- (a) 生成直後: `er003_v1_crosslevel_audio_02_common.py`(`evaluate_attempt_with_cascade`、`:550`)→内部は同じ判定本体。
- (c) 差: どちらもTier3は`er006_secondary_asr_01.py:1020-1085`の同一ブロック(条件=`not verified and segment_id is not None and cls.classification=="ASR_VALIDATION_UNCERTAIN"`、role∈5role、sub_reasonがplural_only/entity_only、`semantic_equivalence.corroboration_supports(canon_tokens, idx, azure_tokens)`で`other_tokens[idx]==canon_tokens[idx]`)。減速後は`enable_connected_speech_equivalence_layer`を渡さない(`:122-134`docstring記載、Primary層は不変)だが、これはTRUE_CONTENT_MISMATCH用でUNCERTAIN→Tier3には無関係。**Tier3の呼出有無・判定条件に生成直後/減速後の差はない**。
- (d) Y/Z: Zは`er063_family_z_audio_01.py:958,1035,1428`で同じ`generate_with_a2_slowdown_outer_loop`/`apply_a2_slowdown_postprocess`を使う。Yは`er121`が同じ`er003`共通関数(chunk hook)を使う。**同じ経路・同じ判定**で、独自の差はない。
- telemetry(`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl` L7490-7502): `ais`→`ai`のentity_only Tier3記録が、生成時corroborated=2件(L7491, L7499)、減速後`corroborated_by: []`=3件(L7493, L7496, L7501)で、Azure呼出5件(生成時2+減速後3)と一致。

## 3. CURRENT_SPECとの照合
- `CURRENT_SPEC.md:2239`: Tier3(規則的複数形・固有名詞のみの1トークン差、Secondary ASR corroboration**必須**)の適用箇所に「post-slowdown再検証」を明記。`:2915`: 旧`_post_slowdown_cascade_rescue`撤去・減速後判定も同一の統一judge。→ 実装は仕様どおり。
- Tier3の受理条件は「独立ASRが差分位置でcanonical語を支持」(`corroboration_supports`)。Azureが"AI"と転写した以上、仕様上「AIs→AI」は救済不可。これはGateの意図(音声に複数形の"s"が無い可能性を残す、別語に聞こえるなら人が確認)であり、緩和は**Gate緩和=ユーザー承認事項**(`CURRENT_SPEC.md:3162`: 『Gate・QA blocking条件は無変更。HR増はGate緩和を提案する場合のみユーザー承認事項』)。

## 4. 影響・費用(本runのAIs問題)
- Std k2: 通算TTS 4回(標準2+fallback1+LR1)、OpenAI ASR 約8回、Azure 6回、LR LLM 2回、固定cooldown 180秒(12:05:05-12:08:05)。Adv k2: TTS 4回(標準2+fallback1+LR1)、OpenAI ASR 約4回、Azure約4回、LR LLM 2回、cooldown 180秒。
- 費用(raw_usage_logの呼出数を実績単価[run合計の按分]で概算、±2円): Std k2 ≒ ¥6、Adv k2 ≒ ¥4 / run TTS合計¥32.72 のうち約30%。きれいに1回で通った場合(各 ≒ ¥0.5)との差(retry超過分)は約 ¥8〜9。時間は各 約5分(cooldown含む)。
- 減速の寄与: Stdで減速後再検証3回が不合格になったが、いずれも生成後のprimary NGとは独立にAzureが単数に聞いたため。減速を外してもAdv同様にNGになった可能性が高い(Adv実績)。

## 5. 修正案(実装せず・不具合ではないため必須修正なし)
不具合ではなく、Gate緩和でもない低リスク案のみ(いずれも実装は別委任・要承認の可能性あり)。
1. **Writer/Prompt側で複数形acronym("AIs")を避ける**(例:"AI agents"/"AI systems"と書く)。生成前に解消すればTTS retry・LR・HR packetが不要になる。仕様変更(Writer原則)=ユーザー判断(判断候補D)。
2. **発音供給(Ledger/TTS入力の綴り置換)で"AIs"を扱う**(既存の`en_pronunciation_resolver`/Ledgerの枠内)。既存仕様の運用範囲か新仕様かは別途確認要。TTS入力側のみで、判定Gateは不変。
3. 観測性の小改善(任意): 減速後NGのattempt(非最終slot)では`asr_judgement_post_slowdown_ng`が結果に残らず、Azure転写・判定が`attempts/…_postslowdown.json`に保存されない(OpenAI転写と分類のみ。`er003_v1_n3_01_tts_generate.py:340-361`)。今回はtelemetry.jsonlから復元できた。additiveで追加可能だが判定は変えない。
- test案(2を実施する場合のみ): 既存の`er0xx_*_test_01.py`型で、"AIs"を含む文のTTS入力が置換され、ASR比較の基準が置換後綴りになること/Gateが不変であることを固定。

## 6. M3 Gate `STD_FALLBACK_USED_OR_UNKNOWN`がStdのみに付いた理由
Std(a2)のLR成功時の合成entryは`er003_v1_crosslevel_audio_02_common.py:477 _merge`(`res["fallback_used"] = True`を**無条件**で立てる。旧経路`:627`も同様)で`fallback_used=true`になる。M3 Gate(`er019_family_x_style_profile_01.py:708-717`)はStd FULL_STORYで`entry.get("fallback_used") is not False`を違反とする。一方Adv(b1b)はLR成功entryが`repro01`の生成関数由来で`fallback_used=false`(今回の観測)、AdvのGateは`instruction_type=="minimal_fallback"`(`:709-714`付近)を見るため、LR後の最終音声がminimal fallbackでなければ違反にならない。Advでも実際にはattempt3でminimal fallbackを使っているが、最終entry側の記録は`english_style_prefix_wide_margin`・`fallback_used=false`。つまり**Std/Advの記録意味の非対称**(Stdは「segment履歴にfallbackあり」、Advは「最終音声の指示がfallback」)で、結果は両levelともBLOCK(Stdは`STD_FALLBACK_USED_OR_UNKNOWN`+`LOCAL_REWRITE_RECOVERY`、Advは`LOCAL_REWRITE_RECOVERY`のみ)。HR承認は`record_human_approval`のcanonical sha一致で区別なく解除でき、承認要否・最終結果は変わらないため実害なし。

## 7. 11-8分類
- 減速後再検証の二次ASR未適用: **不具合ではない(仕様どおり)**。OPEN新規登録なし。
- Std/Advのfallback_used記録非対称: **実害なし**(OPEN登録はFable判断、登録するなら実害なし)。
- 観測性(非最終slotの減速後Azure転写が保存されない): **実害なし(任意の改善候補)**。
- 複数形acronym"AIs"のTTS/ASR不安定: **ユーザー判断要(判断候補D=Writer/Prompt原則・発音供給方針の変更)**。進める場合は次委任で候補を整理。
