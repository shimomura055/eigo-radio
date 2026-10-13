# PATH_MAP_01 (経路 x 配線点マトリクス、2026-10-13、設計のみ・code無変更)

凡例: 変更=Y(差替/追加)・N(無変更)・G(guard/test追加のみ)。行番号は2026-10-13時点の実測(委任_02で再Grepする)。

## 1. M2P0(Key Phrase候補供給)

| Family | 経路 | ファイル:行 | 現状値 | 変更後値 | 変更 |
|---|---|---|---|---|---|
| X | 初回(scaffold) | `er019_family_x_audio_production_runner_01.py:368` `sc.run_key_phrases(..., kp_backend=kp_backend)`、`:323`既定`"db_hybrid"` | db_hybrid | 同(引数無変更) | N |
| X | 初回 候補供給 | `er030_key_phrase_db_hybrid_selector_01.py:450-461` `core.run_stage1_and_shortlist(article_text, dbs, title)` | M0(予算60、cap15) | `m2_supply.build_m2_stage1_and_shortlist(...)`(予算n2+100+guard+U2+U3+(a)(b2)(c)、cap15の外側に予約枠3) | **Y** |
| X | 初回 候補行 | 同`:508` `src_ref_contract.build_lightweight_user_message(...)`(`evidence_fn`引数は`er030_..._contract_01.py:215`に既存) | evidence_fn未指定(注釈なし) | 注釈付きevidence_fn(`contains:`/`contained_in:`/`fragment_risk`。`match:`なし) | **Y**(selector側のみ、契約関数は無変更) |
| X | 初回 選定Prompt(P0) | `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`+contract `_FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE` | sha `69d0e6ff…`/`b8af4d50…`/`026aa730…` | 同(無変更) | N(sha test追加=G) |
| X | 初回 選定gate | `selector:524付近` `prod.run_production_selection_gate`、`er003_key_words_production.py:164 MAX_PRODUCTION_RETRY_ATTEMPTS=2` | 初回+1回 | 無変更 | N |
| X | retry: 選定gate(技術的失敗/hard要件不適合) | 同上 | 上限2 | 無変更。retry時も同一M2候補(`shortlist_cache`) | N |
| X | retry: canonicalization INVALID/Redundancy・Symbol NG | `scaffold_generate.py:677-` `run_key_phrases`ループ、`KEY_PHRASE_REDUNDANCY_RETRY_MAX=2`(`:656`)、上限超過`NG_REVIEW_REQUIRED` | 同 | 無変更。`shortlist_cache`で**Wiktionary照会・M2構築を再実行しない**(cacheの値にm2メタを追加) | G(cache形式拡張+test) |
| X | fallback: DbHybridFailure | `scaffold_generate.py:494-` `_run_key_phrase_selection_db_hybrid_with_fallback`→Strategy L(`:350`) | fallback_allowed時にStrategy L全文方式 | 無変更。M2構築例外(Wiktionary 429枯渇等)は既存`SELECTOR_EXCEPTION`(`selector:455-460`)へ。**M0への自動fallbackは作らない** | N |
| X | fallback不可(STOP) | `MODEL_CONTRACT_VIOLATION`/`KP_ARTICLE_COST_CAP_EXCEEDED`(`KP_ARTICLE_COST_CAP_JPY=15`、`selector:79`) | fail-closed | 無変更 | N |
| X | regeneration(KPのみ再生成) | runnerに現状KP単独stageなし(`run_theme_scaffold`はPreview/Comment生成も含む) | なし | `--scaffold-only kp`相当の最小引数追加(Opus論点④) | **Y**(要レビュー) |
| X | telemetry | `_log_kp_backend_telemetry`(`scaffold_generate.py`)、`er030_output/kp_backend_telemetry_01/telemetry.jsonl` | 既存key | `kp_supply`/`reserved`/`overflow`/`m2_lookup_seconds`/`wiktionary_api_calls`追記 | Y(追記のみ) |
| X | モデルrouting | `process="A2_SUPPORT"/"B1_SUPPORT"`→`routing.require_model`、`SUPPORT_MODEL="gpt-6-luna"`(`er006_model_routing_contract_01.py:50`) | gpt-6-luna | 無変更 | N |
| Z | 初回 | `er062_family_z_writer_01.py:931 run_kp_stage`→`scaffold.run_key_phrases(...)`(`kp_backend`未指定) | **strategy_l(全文方式、shortlistなし)** | **構造上M2が載らない(Z-1)**。変更なし | N(UDR) |
| Z | `family_profile="family_z"`でdb_hybrid | `er030_..._contract_01.py:60-72` `SUPPORTED_FAMILY_PROFILES=("family_x",)` | NotImplementedError | 変更なし(Z-1判断まで) | N(UDR) |
| Z | retry(Z限定暫定) | `er062:943-` `run_kp_with_outer_retry`(`Z_KP_OUTER_RETRY_MAX=3`、共有module無改変) | 外側retry(OPEN-310暫定) | 無変更 | N |
| Z | fallback/regeneration | Strategy Lの`prod.run_production_selection_gate`(上限2) | 同 | 無変更。KP再生成はZ記事再生成STOPに抵触するため実施しない | N |

## 2. N01(メイン音声style、Full Story narrationのみ)

| Family | 経路 | ファイル:行 | 現状値 | 変更後値 | 変更 |
|---|---|---|---|---|---|
| X | 定数(新) | `er019_family_x_style_profile_01.py`(P8_TEXT:49-54付近に並置) | なし | `N01_TEXT`(逐語)/`N01_SHA256="d1956c91c925d197e27cf1204d7ed17248a96bef096b082fb1bd0846106a0477"`/`N01_LENGTH=202`、`_verify_constants()`ループへ追加 | **Y** |
| X | profile(新) | 同`:111-128 _FULL_STORY_OVERRIDE/STYLE_PROFILES` | `coffee_p8`/`coffee_final_v5`(P8) | 新profile `n01`(FULL_STORYのみ、`std_append_slower_instruction=False`)と、R2/P3を維持する`coffee_final_v5`+N01の結合profile(命名は実装時) | **Y**(UDR N-1: defaultへの切替は別判断) |
| X | CLI | `er019_family_x_audio_production_runner_01.py:1986-1995` `--style-profile`(`choices=STYLE_PROFILES`) | 既存choices | 自動的に新profileを含む | N(自動追従) |
| X | Adv 初回 | runner`:742` `style_prefix_override=_role_style("FULL_STORY")`→`news_tail_fix.generate_news_narration_wide_margin`(`:128 standard_style_prefix = override or p9a.ENGLISH_STYLE_PREFIX`) | default=`FAMILY_X_ROLE_STYLE_EN["FULL_STORY"]`、coffee profile=P8 | profile `n01`選択時=N01 | N(解決関数経由) |
| X | Std 初回 | runner`:1098` `_role_style_slower("FULL_STORY") or A2_ENGLISH_STYLE_PREFIX_SLOWER`→`n3_tts.generate_a2_segment_with_slowdown` | default=FULL_STORY+減速instruction連結、coffee profile=P8逐語 | profile `n01`=N01逐語(連結なし、Std逐語例外を踏襲) | N(解決関数経由) |
| X | Std 6%減速 | `er003_v1_n3_01_tts_generate.py:169-` `apply_a2_slowdown_postprocess`、`er008_a2_postprocess_slowdown_01.py:32` | 6% | 無変更 | N |
| X | Std 減速後再検証 | 同`:190-`: `routing.transcribe`→`en_validator.classify_asr_match(segment_id=name)`、NG→STOPPED、`_post_slowdown_cascade_rescue`(`:117`) | 現行 | 無変更 | N |
| X | retry(標準経路2回) | `er003_v1_crosslevel_audio_02_common.py:79-` `standard_attempts=PRODUCTION_STANDARD_TTS_ATTEMPTS=2`、総計`PRODUCTION_MAX_TTS_ATTEMPTS=3`(`er011_human_review_lock_01.py:80,102`) | 2+fallback1 | 無変更 | N |
| X | retry(減速後NGの取り直し) | `generate_a2_segment_with_slowdown`外側ループ(`max_slowdown_attempts=3`、通算TTS上限3共有、OPEN-270) | 現行 | 無変更 | N |
| X | fallback take(Std) | `_run_a2_minimal_fallback_attempt`(`crosslevel_audio_02_common.py:301-`): `style_prefix_override`を渡さない仕様(`:110-114`) | minimal instruction(N01ではない) | **無変更(fallback takeはN01を使わない=既存仕様)** | N |
| X | fallback take(Adv) | `repro01.generate_english_component_minimal_instruction(..., tts_backend)`(`news_tail_fix.py:175`)。speech_metadata_flash_liteでは`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]="natural, clear, conversational"` | 同 | 無変更 | N |
| X | regeneration(Local Rewrite等) | `_local_rewrite_recovery_for_english_segment_with_fallback`(`crosslevel_audio_02_common.py:369-`) | 現行 | 無変更 | N |
| X | profile固定記録/resume | `style_profile.py:resolve_run_profile`(M2: 既存run記録のあるout_dirで新profileを記録不可)、`assert_profile_backend`(M5: speech_metadata_flash_lite必須)、`m3_assembly_gate` | 現行 | 無変更。新profileは**新out_dir**必須 | N |
| X | tts_backend/model | `--tts-backend speech_metadata_flash_lite`→`gemini-3.8-flash-lite-tts`(`er006:119`)、voice Aoede | 同 | 無変更(委任_02は`--tts-backend speech_metadata_flash_lite`と`TTS_EXECUTION_MODE=STANDARD`を明示) | N |
| Z | 定数 | `er063_family_z_audio_01.py:103 _PD8`、`:133-147 _STYLE_SHA256/_STYLE_TEXT` | PD8(sha `329ff46a…`)/`PD8_A2SLOW`(`74b456ca…`) | `"N01"`を追加(sha `d1956c91…`)。PD8系は参照元grep後に判断(Dangling防止) | Y(実装は委任_02、Z側はN-2判断後) |
| Z | Adv narrator | `er063:153 NARRATOR_FULL_STORY_ADV`、生成`:551-558`(`news_tail_fix.generate_news_narration_wide_margin(... style_prefix_override=style)`) | text=`_PD8` | text=N01(label"N01") | Y(UDR N-2) |
| Z | Std narrator | `er063:156 NARRATOR_FULL_STORY_STD`、生成`:559-`(`n3_tts.generate_a2_segment_with_slowdown`) | PD8+`"\n"`+A2減速instruction | N01逐語(連結なし) | Y(UDR N-2) |
| Z | Std減速/減速後再検証/retry/fallback/regeneration | Xと同じ共有module(`n3_tts`/`crosslevel`) | 現行 | 無変更 | N |
| Z | dialogue(Adv/Std) | `er063:160-166 DIALOGUE_ADV/STD`(`text=None`) | 既存style | **対象外(無変更)** | N |
| Z | Preview/Comment/KP/TOPIC_INTRO/JA title/SHELL | `er063:167-190` | 各承認済みstyle | **対象外(無変更)** | N |
| Z | style整合assert | `er063:208 assert_style_table_integrity` | sha一致assert | N01のsha追加で追従 | Y(同上) |
| Z | 実行 | Z記事再生成・音声化 | STOP | **STOP厳守**。mock/dry-runのみ(Checklist 5/6は未確認) | N |

## 3. 読み取り上の注意(事実)

1. Family Xの「現行P8」はCoffee限定profile(`--style-profile`明示)にのみ存在し、defaultのFull Story styleはP8ではない。Family Zの現行は短い版PD8で、P8とは別文言(それぞれ別sha)。
2. Std減速後再検証のASRは`routing.transcribe`+`classify_asr_match`(EN ASR Semantic Equivalence Validator)であり、本配線では**緩和・変更しない**。連結発音層(`enable_connected_speech_equivalence_layer`)は`full_story_part1/2`等にのみ現行どおり適用され、未承認のer065/er068系を混ぜない。
3. fallback takeは(Std/Adv共に)N01ではなく既存のminimal instruction系style。したがって「fallbackで合格した音声」はN01ではない旨をruntime evidenceに記録する(`style_prefix`/`instruction_type`、`fallback_used`)。
