# SPEC_COMPARISON_TABLE_DRAFT_01 (ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_01、骨子、2026-10-11)

日英ASR/TTS仕様の比較表の**骨子**。日本語列=今回の詳細調査(`JA_SPEC_SURVEY_01.md`)。**英語列は発火条件・回数・Tier名・根拠行のみの最小確認**で、詳細は別agent(FAMILY-X-EN-ASR-CONFIRM-RETRY-REDESIGN-01 委任_01)と後続委任で統合する(英語側の調査は本委任で重複していない)。
英語列の「未確認」は、今回の最小確認では裏が取れていない項目。API未使用。

| 論点 | 日本語(現行Production) | 英語(現行Production、最小) | 目標共通フロー | 差・統合論点 |
|---|---|---|---|---|
| Primary ASR | OpenAI `gpt-4o-mini-transcribe` ja-JP。`classify_ja_asr_match`の6分類(EXACT/NORMALIZED/PHONETIC/UNCERTAIN/TCM/READING_RESOLVED)(VAL L35-40、L333-504) | OpenAI `gpt-4o-mini-transcribe` en-US。`val.evaluate_attempt`(`er006_preprod_hardening_01_validation.py`)。Tier 1(role gating)、Tier 3(複数形・固有名詞ASR表記差のcorroboration)(`er006_secondary_asr_01.py` L158-165、L596-667、SPEC L1945/L2359) | 初回: Primary 1回 | モデル同一。判定器は別実装 |
| Primary NGの分類 | TCM(数字/否定/非cascade diff)とUNCERTAIN(entity_like・濁点差のみ)に二分(VAL L491-498) | TCMとUNCERTAIN(entity_like/homophone_candidate)(`er006_secondary_asr_01.py` L182-205) | 「Primary NG」で一本化 | 日本語にhomophone_candidate相当なし(同音はPHONETIC_MATCHでPASS)。英語の`ARPAbet`系はCMU辞書ベース |
| Secondary ASRの起動条件 | (1)TCM -> SCG(Azure 1回、除外9条件)(SEC L399-425)。(2)UNCERTAIN -> 旧Cascade(Primary#2->Azure#1->#2)(SEC L427-500) | (1)UNCERTAINでentity_likeまたはhomophone_candidate -> Cascade(Primary#2->Secondary#1->#2、`CASCADE_CONFIG` L169-172)。(2)TCM + protected通過 + `enable_connected_speech_equivalence_layer`(5 role)-> Equivalence Layer(Azure+local ASR corroboration)。(3)Key Phrase英語: 非ラテン文字主体のNG -> Secondary 1回(`enable_non_latin_cascade`)。Cost Guard $0.05/seg(L179) | Primary NG -> Secondary 1回(全NG) | 日本語のSCGは英語より広く(TCM全般)、英語は限定されたカテゴリ。英語のPhrase List(`get_full_text_via_azure_stt_with_phrase_list` L69)は日本語SCGでは使わない(安全条件) |
| Secondary PASS条件 | EXACT/NORMALIZEDのみ(SEC L78)。旧CascadeはPHONETIC_MATCHもPASS(L473)、2エンジンORTHOGRAPHIC_VARIANT_CONFIRMED(L477) | 未確認(Cascade内`should_pass`、`HOMOPHONE_EQUIVALENT`/`PROPER_NOUN_ENTITY_ARPABET_CONFIRMED`定数あり L205-206付近) | 両エンジンでNGなら再生成へ | 日本語内でも不統一(SCG vs 旧Cascade)。英語との基準対応は後続 |
| 数字・否定・固有名詞の扱い | 数字/否定=保護(SCG不実行)。固有名詞(カナ)=C1でSCG不実行、単独はUNCERTAIN。辞書語=読み照合 | 数字/否定=protected_check。固有名詞=entity_like -> Cascade、CMU辞書でARPAbet一致のみ自動PASS(SPEC L1693) | 例外分類は`JA_EXCEPTION_CLASSIFICATION_DRAFT_01.md` | 「固有名詞はASR収束だけではPASSしない」(SPEC L1693)は英語側の承認原則。日本語C1との関係はg8調査参照 |
| TTS再生成の上限 | 総3回(標準2+minimal fallback 1)(LOCK L80/L102-104、SPEC L1692) | 総3回(標準2+minimal 1)。Key Phraseは4回(minimal 2+English lock 2)(`er003_v1_repro01_main_generate.py` L633-635) | 初回+再生成(1)+(2)=3回、同一Prompt固定 | 3回で一致。内訳(minimal)が異なる/Key Phraseは4回 |
| fallback | JA minimal instruction(3回目、J3 style喪失)(N3 L473-、V01 L434-) | 英語minimal instruction(3回目)、KPはEnglish lock(`er003_v1_crosslevel_audio_02_common.py` L79-)。Role style(E2等)を持つ | minimal除外 | 目標フローでは日英とも除外。J3/E2の保持 |
| Local Rewrite | **なし**(OPEN-260未承認) | あり: attempt3直前に固定600秒cool-down、3回NG後に問題spanのみLuna(`gpt-5.6-luna`)で局所書換7 Gate、再TTS 1回。5 role限定(`er020_tts_retry_local_rewrite_01.py` L56、SPEC L1971) | 除外 | 英語のLocal Rewriteは目標フローから外れる。承認済み仕様の取扱いは別途判断 |
| cool-down | なし | attempt3直前のみ600秒。`enable_connected_speech_equivalence_layer=True`(5 role)の呼出のみ有効(`er003_v1_crosslevel_audio_02_common.py` L164-180、`er020` L56) | 未規定 | 日英差。目標フローでの扱いは後続 |
| Human Review移行 | 3回後STOPPEDまたはUNCERTAIN尽き。lock+キュー`er007_output/ja_asr_cascade_01/`(SEC L39) | 同じlock(LOCK L255-310)。キュー`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(SPEC L2001)。Local Rewrite回復後にHR | 再生成(2)後 | キューが日英で別パス |
| Role・Family別適用 | 全JA segmentが同一Validator+SCG。Family X: title/preview/comment/meaningがJ3 | Connected Speech Equivalence Layer・Local Rewrite・Repetition QAは特定role限定(Full Story/Comment/Preview/Topic intro/In One Line、A2/B1本文) | 全role共通か役割別か未決 | 日本語はrole差なし、英語はrole差あり |
| Voice/Style一貫性 | 標準=J3(Family X)、fallbackでminimalに変化 | 標準=role style(E2等)、fallback=minimal(別style) | 同一Prompt固定 | 日英とも3回目で変化。J2_BRIGHT/E2_UPBEAT(approved-but-unwired)導入後はさらに目立つ |
| 承認状態の注意 | SCG=PRODUCTION_WIRED(2026-10-11)。**C1はユーザー個別承認なし**(g8 13/14受入確認待ち)。PHONETIC非許容=ユーザー決定済み安全条件 | Tier 1/3(2026-09-27 APPROVED)、Local Rewrite(2026-09-26 APPROVED)。EN Coffee part2等の個別事象は別agent | - | 英語側の根拠行は後続委任で補完 |
| 費用・時間(参考) | SCG 1回約0.16円・1.4秒。再生成1回約0.1円・120〜170秒(RESULT_01) | 未確認(cool-down 600秒、Luna局所書換あり) | - | - |

## 英語列の確認方法(最小)
`er006_secondary_asr_01.py`(L69/L158-205/L459-)、`er003_v1_crosslevel_audio_02_common.py`(L79-、L143、L162-180、L229-269)、`er003_v1_repro01_main_generate.py`(L633-635、strict loop L198-)、`er020_tts_retry_local_rewrite_01.py`(L1-60)、`CURRENT_SPEC.md` L1692/L1693/L1971/L2001の記述を読んだだけ。英語telemetry再計算・Coffee part2 NG原因・英語retry/fallback詳細は別agentの担当のため触れていない。
