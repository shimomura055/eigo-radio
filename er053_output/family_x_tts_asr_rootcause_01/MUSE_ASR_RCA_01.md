# MUSE_ASR_RCA_01: META Advanced(B1B)固有名詞 "Muse" ASR不一致の根本原因分析

管理ID: FAMILY-X-TTS-ASR-ROOTCAUSE-01 委任_21 / 日付: 2026-10-11 / 性質: read-only調査(課金API 0回、コード・音声・記事・SSOT変更なし)
モデル: 本調査はLLM/TTS/有料ASRを新規に呼んでいない(使用モデル名: 該当なし)。ローカルfaster-whisper(small、無料)で既存wavを再転写しただけ。
対象: `er019_output/family_x_audio_production_wiring_01/meta__run_regen_01/b1b/`

## 0. 結論(先に)
1. **これは「固有名詞辞書の未登録」でも「Production配線漏れ」でもない。** "Muse" は文中で必ず "Some Muse calls"(直前語が "Some"=語末/m/)の形になっており、**/m/+/m/の連続(同一音素の連結)で "Muse" の語頭/m/が音として潰れ "some use calls" に聞こえる**可能性が高い。Primary(OpenAI)・Secondary(Azure、Phrase List付き)・ローカルfaster-whisper の**独立3系統すべてが同じ "use" と聞いた**(下記§2)。ASR側の辞書不足ではなく、**音声自体の聴こえ方の問題**である可能性が高い(人間の聴取は未確認)。
2. 過去対策(Ledger発音ヒント注入・Tier3 corroboration・Connected Speech Layer)は**この音韻衝突型を対象にしていない**(適用範囲外)。さらにLedgerのMuseエントリは**設計上TTS注入から除外**されていた。
3. comment_2 が止まり in_one_line が回復した差は、**Local Rewrite の安全網 `validate_candidate_is_full_segment()` が「文頭15文字の一致」を要求する実装**のため、問題語が文頭付近(index 1)の comment_2 では全5候補が形式不合格(`is_full_segment_format_valid=false`)になったこと。他の6 Gateは候補1・2・4で全PASSしていた。これは**承認済み仕様の実装上の欠陥(過剰拒否)**。
4. 同種再発(「語末音素=固有名詞の語頭音素」)は、個別辞書登録では防げない。包括対策は §4。

## 1. 過去対策の棚卸し表
Status欄は `CURRENT_SPEC.md` 記載どおり(複製ではなく要約)。行番号は2026-10-11時点。

| # | 対策(管理ID) | Status | 対象範囲 | Production配線先 | 発火条件 | Museへの効果 |
|---|---|---|---|---|---|---|
| 1 | Pronunciation Ledger(cache)+Perplexity research(ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01、OPEN-47) | 実装済み。Ottoni型は解決せず(OPEN-47 `TBD`) | EN/JA固有名詞 | `er006_pronunciation_ledger_01.py`(`get_hint_for_text`) | Ledger登録済みsurfaceのみ | Museは2件登録(Q1)、いずれもTTS注入されず |
| 2 | TTS発音ヒント注入 pre-TTS resolver(PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01 Phase2 / PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01 / PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01) | `PRODUCTION_WIRED`(CURRENT_SPEC L2138-2330) | EN(A2標準・fallback、B1/B1B全経路、`enable_pronunciation_resolver=True`はFamily Xのみ)、JA読み | `er025_entity_pronunciation_resolver_core_01.resolve_and_augment_en_style_prefix`(`er003_v1_sing01_news_tail_fix.py` L129-134、voice01、crosslevel fallback) | **Ledgerに登録済み**かつ`entity_type!=cascade_unresolved_entity`かつ`tts_injection_disabled=false`かつconfidence>=medium。EN未登録語の**新規自動lookupは無い**(再researchは「confidence=lowで既登録」のみ、run上限5回) | 不発(Q2) |
| 3 | `cascade_unresolved_entity`のTTS注入除外(Opus L2 BLOCKER-1是正、同Phase2) | `PRODUCTION_WIRED` | 同上 | `er006_pronunciation_tts_injection_01.augment_style_prefix_with_pronunciation` L66-69 | ASR cascade由来の誤entry("plus"/"us"/"main story"等)が無関係語へ誤注入されるのを防ぐ | Museの`MYOOZ`は除外され不使用 |
| 4 | Primary/Secondary ASR Cascade + Phrase List(ER-006-AUDIO-RETRY-CASCADE-PROD-01、OPEN-48) | 実装・配線済み(`FEATURE_FLAG_SECONDARY_ASR_ENABLED`) | EN/JA | `er006_secondary_asr_01.evaluate_attempt_with_cascade_detail` | Primary#1がASR_VALIDATION_UNCERTAIN等。Azure+Ledger phrase list(cascade entryも含む、`get_hint_for_text`素通し) | 発火したが3回ともAzureも"use" |
| 5 | 固有名詞Case A自動PASS `PROPER_NOUN_ENTITY_ARPABET_CONFIRMED`(ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15) | 実装済み | entity_like差分 | `er006_secondary_asr_01._case_a_entity_pass` L403-415 | CMU辞書ARPAbetが canonical/ASR で完全一致 | 不成立(MUSE=M Y UW Z vs USE=Y UW Z)。Case B(CMU外)は収束しても自動PASSしない設計(D-2') |
| 6 | entity phonetic corroboration `ASR_VALIDATION_UNCERTAIN_PHONETIC_ACCEPTED`(CURRENT_SPEC L1950) | 実装済み(`generate_news_narration_wide_margin`) | 複数takeの表記揺れ | news_tail_fix | Soundex+類似度、語数一致、繰り返し同一誤認識は不可 | 同一誤認識("use"反復)のため不成立 |
| 7 | **English ASR Semantic Equivalence Tier3**(EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01、OPEN-186) | `APPROVED_FOR_PRODUCTION / WIRING COMPLETE(runtime)`(2026-09-27。Phase B live発火は偶発のみのため最終`PRODUCTION_WIRED`判定はPhase B live telemetry取得後と記載) | 5 role(Full Story/Comment/Preview/Topic intro/In One Line)、1トークン差のplural/entity | `er006_secondary_asr_01.py` L575-650(`tier3_corroboration_secondary`) | sub_reason=entity_only かつ Azure(Phrase List付き)が diff位置で canonical語を支持 | **corroboration成立せず**(Azureも"use")。同日のcomment_3は別takeでAzureが"Muse"と聞き `SECONDARY_ASR_CORROBORATED_MATCH` で救済(telemetry L5012) |
| 8 | Connected Speech Equivalence Layer(OPEN-122) | `APPROVED_FOR_PRODUCTION`(2026-09-07)→5 role拡張 | A2/B1英語本文 | `er011_connected_speech_equivalence_layer_production_01.py` | **TRUE_CONTENT_MISMATCHかつprotected_check通過**のみ。Museは entity_only の ASR_VALIDATION_UNCERTAIN なので**入口に来ない** | 適用範囲外 |
| 9 | Local Rewrite Recovery + Natural English QA(TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01) | `PRODUCTION_WIRED`(2026-09-26、ユーザー確定) | 5 role(B1/B1B/A2 fallback配線済み) | `er020_tts_retry_local_rewrite_01.run_local_rewrite_recovery`(voice01/news_tail_fix/crosslevel) | Human Review Lock到達直前、7 Gate全PASSの候補のみ再TTS1回 | in_one_line=成功、comment_2=候補全滅(Q4) |
| 10 | retry/fallback/regeneration cascade + Human Review Route(ER-006-AUDIO-RETRY-CASCADE-PROD-01、CURRENT_SPEC L1996) | `DECIDED`/実装済み | 全segment | `human_review_queue.jsonl`、Review Lock | 同一ASR mismatch signature連続→`stop_retrying` | comment_2は1take目で打切り(Q4) |
| 11 | entity_like判定の一般化 A-1(b)loanword/S3 `entity_like_source`(PHASE-4-A2...-ASR-ENTITY-LIKE-01) | `PRODUCTION_WIRED`。A-1(a)Ledger surface条件は`DEFERRED/NOT_ADOPTED`(OPEN-208) | 分類のみ | `er006_preprod_hardening_01_validation.py` | 大文字始まり/外来語 | 今回は`capitalized`で正しくentity_only分類 |
| 12 | 英語homophone(`homophone_en`、OPEN-81)/JA reading(OPEN-145) | 実装済み | homophone_candidate | `er006_secondary_asr_01` | CMU発音一致 | Muse/useは別発音で非該当 |

JA辞書`DEFAULT_JA_READING_DICTIONARY`・ja_reading Ledgerはサブ対象(Museは`ja_reading_katakana`「ミューズ」が1件、JA用、EN発音ヒント空)。

## 2. 今回の実発火表

出典: `b1b/audit/tts_generation_results.json`、`b1b/narration/attempts/*.json`、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(L64=A2 in_one_line 01:27、L65-67=B1B)、`er021_output/.../telemetry.jsonl` L5005-5012、`er011_output/attempt_history.jsonl` L11809/L11817/L11828、`er011_output/local_rewrite_recovery/meta__run_regen_01/b1b/*.json`。

### comment_2(Charon、最終: `ASR_VALIDATION_UNCERTAIN`、Human Review待ち、queue L67、attempt_history L11828 `human_review_reached=true`)
canonical: `Some Muse calls were handed over to human workers, but not all of them. Were people told when a worker took over, and what did Meta change after the test?`

| 工程 | 認識結果(逐語) |
|---|---|
| Primary#1(OpenAI gpt-4o-mini-transcribe) | `Some use calls were handed over to human workers, but not all of them. Were people told when a worker took over? And what did Meta change after the test?` |
| Tier3 corroboration(Azure、Phrase List付き) | `Some use calls ... took over. And what did Meta change after the test?` -> `corroborated_by=[]` |
| Primary#2 | `Some use calls ...`(同一signature) |
| Secondary#1/#2(Azure、`phrase_list_used=true`) | `Some use calls ...`(同上、2回) |
| ローカルfaster-whisper small(今回再転写、無料、`comment_2.wav`) | `Some use calls were handed over ... And what did meta change after the test?`("use" 0.38-0.58秒、確率0.946) |
| Local Rewrite | 候補5件全て `is_full_segment_format_valid=false` -> `NO_CANDIDATE_PASSED_ALL_SEVEN_GATES` -> `HUMAN_REVIEW_LOCKED_NO_CANDIDATE_PASSED_QA`、再TTSなし |
| TTS take数 | 1(`cooldown_events=[]`、同一signatureで`stop_retrying`) |
| `en_pronunciation_resolver_info` | `hints_applied=false, cache_hits=[], low_confidence_retry_attempted=false, research_meta=null` |

### in_one_line(Aoede、最終: `OK`/`RESOLVED_BY_LOCAL_REWRITE`、attempt_history L11817 `human_review_reached=false`)
| 工程 | 認識結果 |
|---|---|
| take1 canonical `...contractors handle some Muse calls...` | Primary#1 `...handle some user calls`、Azure `Matta admitted ... handle some use calls`、Primary#2 `...used calls`、Azure#1/#2 `Matta ... use calls`(queue L65)。ローカルwhisper `Metta admitted ... handle some use calls` |
| Local Rewrite#1(候補1採用: `manage some Muse calls`)->take2 | Primary#1 `...manage some use calls`、Azure `use`、Primary#2 `user`、Azure#1/#2 `use`(queue L66)。ローカルwhisper `...manage some use calls` |
| Local Rewrite#2(入れ子: `manage some calls for Muse`)->take3 | Primary `...manage some calls for Muse without telling ...` = **EXACT_MATCH**(retts_result)。ローカルwhisper(attempt3 json)も `muse` と認識 |
| 回復後Tier | `semantic_equivalence_info=null`(Tier3不要) |

**同じ "some Muse calls" を含むA2 in_one_line(queue L64、01:27)も同一失敗**(Primary `used`/`use`、Azure `use`、`phrase_list_used=false`)。この時点で初めてLedgerに`muse|cascade_unresolved_entity|MYOOZ`が登録された(Q1/Q2)。

## 3. Q1〜Q6の回答

**Q1. Museは既存辞書・キャッシュに登録されていたか。** 登録されていた(2件)。`er006_output/pronunciation_ledger_01/ledger.json`: (a) `muse|ja_reading_katakana`(2026-09-27、ミューズ、EN `pronunciation_hint`空、confidence=high)、(b) `muse|cascade_unresolved_entity`(`updated_at=2026-10-11T01:27:18`、IPA `/mjuːz/`・hint `MYOOZ`・confidence=medium、A2 in_one_lineの失敗後cascade lookupで自動登録)。ただしEN pre-TTSで使える形ではない(Q2)。`ledger.json`にはこの種の`cascade_unresolved_entity`が20件あり、"plus"/"us"/"main story"のような一般語の誤entryも含む(OPEN-207)。

**Q2. なぜ`hints_applied=false`・`cache_hits=[]`か。** コード経路で確認済み(`get_hint_for_text`を同じ本文で実行して再現: TTS注入経路の戻り=[]、Phrase List経路の戻り=[muse/cascade_unresolved_entity/MYOOZ])。`news_tail_fix.generate_news_narration_wide_margin`/`voice01`->`resolve_and_augment_en_style_prefix`(core L461)->`augment_style_prefix_with_pronunciation`(`er006_pronunciation_tts_injection_01.py` L66-69)が `exclude_entity_types={cascade_unresolved_entity}`, `apply_tts_injection_filter=True` を付けるため、(b)は除外、(a)はhint空。結果`hits=[]`。低confidence再research(core L470-)も `cascade_unresolved_entity`除外+(a)はconfidence=highでlow対象外のため`low_confidence_retry_attempted=false`。つまり**設計どおりの不発**。除外理由はOpus L2 BLOCKER-1(誤entry誤爆防止)。Phrase List用途では(b)が使われ、B1Bでは`phrase_list_used=true`だった。

**Q3. Secondary ASRは呼ばれたか。** 呼ばれた。各segmentでAzure x3(tier3 corroboration、secondary_1、secondary_2)+OpenAI x2。全認識結果は§2。Azure(Phrase Listに`muse`/MYOOZ含む)は"use"のまま、in_one_lineでは"Meta"を"Matta"とも誤認。さらに今回の再転写でローカルwhisperも"use"(takeによって"Metta")。**独立3系統が一致して"use"** = ASRの偶然誤りよりも、音声が実際に "some-use" に近いことを示唆する(人間が聞いて"Muse"と取れるかは未確認、要ユーザー試聴)。

**Q4. comment_2とin_one_lineで回復結果が異なった理由。** 両者ともLocal Rewriteは発火した(`er011_output/local_rewrite_recovery/meta__run_regen_01/b1b/*.json`)。差は2点。(1)**候補全滅の直接原因**: `er020_tts_retry_local_rewrite_01.py` L213-216 `validate_candidate_is_full_segment()` は `rewritten_segment[:15]==canonical_text[:15]` を要求(`FULL_SEGMENT_PREFIX_CHECK_CHARS=15`、TTS-LOCAL-REWRITE-NATURAL-ENGLISH-QA-TRIAL-02で「LLMが置換句だけを返す」不具合の安全網として追加)。comment_2の問題語Museは文頭 index 1 (`some muse calls`) = 先頭15文字内にあるため、問題語を書き換える全候補("Certain Muse..."/"Some of the Muse..."/"A number of Muse..."等)が先頭15文字を変えてしまい形式不合格。**7 Gateの内訳は候補1・2・4が6 Gate全PASS(候補3・5は意味保存で不合格)** で、形式チェックさえ無ければ選定されていた。in_one_lineは問題語がindex 11で先頭15文字外のため通過。(2)in_one_lineは候補1(`manage some Muse calls`)の再TTSも失敗したが、入れ子のLocal Rewrite#2で`some calls for Muse`(Museを語順の後ろへ移し直前の/m/を除去)が成功。comment_2は1take目で`stop_retrying`(同一signature)+Local Rewrite形式不合格のため、この回復ループに入れなかった。

**Q5. 分類。** 主因=「**過去承認仕様の適用範囲外**(音韻衝突型=直前語末音素と固有名詞語頭音素が同一の場合を扱う対策が無い)」。副因=「**承認済みLocal Rewriteの実装上の設計限界(欠陥)**(15文字prefix安全網が文頭の問題語で過剰拒否)」。**Production配線漏れではない**(Tier3/Local Rewrite/Ledger注入はいずれも配線済みで、設計どおり、または既知の除外設計どおりに動作)。根拠: §1表#2/#3/#7/#8/#9、Q2/Q4。

**Q6. 同種固有名詞で再発しないために何が不足しているか。** (a)EN pre-TTSは**未登録固有名詞を事前に自動lookupしない**(失敗後cascadeで初めて登録、しかもTTS注入対象外)。(b)**音韻衝突(語末音素=固有名詞語頭音素)を検知・回避する手段が無い**(Museだけでなく、例: "Tom Matthews"/"some Moderna"/"Sam Mendes"型)。(c)Tier3救済は「独立ASRがcanonical語を支持」が必須で、3系統とも同じ誤聴だと救えず、救うべきでもない(誤PASSになる)。(d)Local Rewriteの文頭問題語での過剰拒否。(e)同日comment_3は別takeでAzureが"Muse"と聞き救済された(L5012)ことから、take間で発音ゆれがあり、1take目で打切る`stop_retrying`(同一signature)が取り直し余地を奪っている可能性(ただしin_one_lineのtake1/2は連続失敗しており再take効果は未実証)。

## 4. 再発防止案(実装はしていない)

費用の根拠(登録単価、`er005_output/cost_baseline_01/pricing_snapshot.json`): Gemini 3.8 Flash-Lite TTS Standard 出力$6.0/1M token(25 token/秒、10秒でおよそ$0.0015+入力)・Batch $3.0/1M、gpt-4o-mini-transcribe 入力$1.25/出力$5.0 per 1M、Azure STT $1.0/hour(コード内概算$0.00001/call)、gpt-6-luna $0.10/$0.01/$0.50 per 1M。Local Rewrite 1回の実額(Luna 2call+TTS1+ASR1)は過去Trial-02で約3円(旧gpt-5.6-luna価格時)。gpt-6-lunaでの実測は未確認。いずれも1segmentあたり数円以下の見込みだが、想定発火率・総額は未確認。

### 区分A: 既存仕様の修復(承認済み仕様の意図を変えない)
| 案 | 内容 | 対象範囲 | 期待効果 | リスク(誤PASS/安全性) | 費用影響 | 判断要否 |
|---|---|---|---|---|---|---|
| A1 | `validate_candidate_is_full_segment()`のprefix15文字一致を、問題spanが文頭にあっても過剰拒否しない判定へ修復(意図=「置換句だけを返す不具合」の検知は維持。`unchanged_ratio>=0.7`のcriterion7が断片返却の補強にもなる) | `er020_tts_retry_local_rewrite_01.py`(全Family・全5 role共通) | 今回のcomment_2は候補1/2/4が選定対象になり再TTSへ進める。文頭に固有名詞/問題語が来るsegment全般で救済率向上 | 低。他6 Gateは無変更。意味保存/Fact非矛盾/Natural English QAと再TTS後のASR PASSが引き続き必須のため誤PASSは増えない設計 | 追加はLocal Rewrite再TTS1回分(数円)、発火頻度は小 | Production module修正のためFable判断。新仕様ではなく欠陥修正と位置付け可。Opus必須ではない(PM_GOVERNANCE条件A-D非該当と思われるが確定はFable)。unit test+runtime evidence要 |
| A2 | Ledgerの`cascade_unresolved_entity`のうち、confidence>=medium・語長・一般語ガードを満たすものだけTTS注入対象に戻す(範囲拡張) | EN pre-TTS注入 | 効果は不確実: 今回の根本は発音綴りではなく/m/連結なので、`MYOOZ`ヒントで解消する保証は無い(OPEN-47 Ottoni型でヒント無効の前例) | 中。Opus L2 BLOCKER-1是正の対象箇所を再び緩める。誤entry(us/plus/main story等、OPEN-207)の誤注入に注意 | ヒント注入自体の追加費用はほぼ0 | Opus独立レビュー+Fable判断必須。**今回は優先度低(効果未実証)** |

### 区分B: 新仕様候補(本調査では実装・採用しない。人間ユーザー承認前提)
| 案 | 内容 | 対象範囲 | 期待効果 | リスク | 費用 | 判断要否 |
|---|---|---|---|---|---|---|
| B1 | **音韻衝突Lint(pre-TTS、決定的・無料)**: CMU辞書ARPAbet(既存`homophone_en`/connected speech tableを再利用)で「直前語の末尾音素=固有名詞(entity)の語頭音素」(m+m, s+s, t+t等)を検知し、TTS前に警告。検知時は(i)Writer段階のsoft rule、または(ii)TTS前にLocal Rewriteを先行発火(語順/前置詞挿入で衝突を回避)のいずれか | 英語canonical全般(entity_like対象) | 個別辞書登録不要で同種(Muse/Matthews/Moderna等)を包括的に削減。ASR失敗->複数take->Local Rewriteの無駄なTTS/ASR/待ち(10分cool-down)を避けられる | (ii)はcanonical変更を伴うため意味保存QAが必須。誤検知で不要な言い換えが増える可能性。Writer prompt変更は別途`APPROVED_FOR_PRODUCTION`が必要 | Lintは0円。(ii)は発火時のみLocal Rewrite(数円) | 新仕様。ユーザー承認+Opus条件A(新しい処理フロー設計)該当見込み。Trial先行 |
| B2 | 衝突語のTTS入力のみ微修正(短いpause/respell)、表示canonicalは維持 | 衝突検知時のみ | 言い換え不要で原文保持 | canonicalとTTS入力の乖離がASR照合と整合するか未検証。Gemini TTSが無視する可能性 | TTS再生成(数円) | 新仕様・Trial必須 |
| B3 | Tier3/Connected Speech拡張: 「独立ASR3系統が一致して誤聴」でもacceptする案 | - | - | **非推奨**: 今回は3系統が一致して"use"であり、acceptすると聴取者に"use"と聞こえる音声を誤PASSさせる(false accept)。安全≠成功原則に反する | - | 採用しない(記録のみ) |
| B4 | entity_only時の`stop_retrying`を、Local Rewrite前に追加take(既存上限内)へ緩和 | EN entity_only | take間のばらつき(comment_3は別takeでAzureが"Muse")を活かせる可能性 | 既存retry上限・cost guard・cool-down仕様との整合要。効果未実証 | 追加take 1-2回分 | 既存retry仕様変更のため要Fable+ユーザー判断 |

**推奨順(私見)**: 即A1(欠陥修正、小・低リスク)->B1(包括対策、まずlint+Trial観測のみ)->A2/B2/B4は必要性が証拠で示されてから。ユーザー確認事項: comment_2/in_one_line失敗takeの実音声を人間が聞いて "Muse" と聞こえるか(聞こえるならASR誤聴+Tier3方針の再議、聞こえないなら音声自体の欠陥でB1が本命)。

## 5. 既存OPENとの重複確認(登録はしない)
| 番号 | 内容 | 今回との関係 |
|---|---|---|
| OPEN-159 | 固有名詞発音パイプライン全体の設計ギャップ集約(Ledger IPAがSecondary ASR自動PASSに未使用、TTS hint引渡し経路未整備等)(defer) | 部分的に包含(Ledger注入・自動PASS未連携)。**音韻衝突型は含まれない** |
| OPEN-47 / OPEN-48 / OPEN-83 | Ledger+Secondary ASR(Ottoni型でヒント無効)、Cascade、CMU外固有名詞(Case B)自動照合未実装 | 背景。Case B非自動PASSの設計根拠 |
| OPEN-122 / OPEN-186 / OPEN-123 | Connected Speech Equivalence Layer / English ASR Semantic Equivalence(Tier3) / Transcript Normalization | 適用範囲の確認先。entity_only+3系統一致誤聴は範囲外 |
| OPEN-208 | Ledger surface条件のentity_like再有効化(DEFERRED) | 分類側の別件。今回のentity_only分類は`capitalized`で正常 |
| OPEN-207 / OPEN-196 | Ledger `us`誤entry(既知バグ)/Ledger同時書込み | A2案のリスク根拠。cascade entry20件に一般語誤entryが混在 |
| OPEN-197/198/203 | EN resolver配線(`CLOSED`/是正済み) | 配線は完了済み(配線漏れでない根拠) |
| OPEN-168 | A2 slowdown再検証がLedger Phrase List付きcascadeを通らない | 別経路(A2のみ)。今回の経路ではない |
| OPEN-184 | Local Rewrite後の再TTSで数値表記ゆれが不一致となる失敗モード | Local Rewrite失敗モードの前例。今回は別原因 |
| OPEN-183 | META「Muse human concierge」記事(B3配線)のユーザー確認 | 記事の背景。ASR問題は未含有 |
| OPEN-06 / OPEN-145 | ASR homophone(英)/JA reading | 同音語(出演/出現)は別agent担当。本件に直接は無関係 |

**新規登録提案(2件、本調査では登録しない)**
1. **[新規] Local Rewrite `validate_candidate_is_full_segment`の文頭問題語過剰拒否**: 既存OPENに無し。承認済みPRODUCTION_WIRED仕様の欠陥(実装バグ、修復案A1)。
2. **[新規] 音韻衝突(直前語末音素=固有名詞語頭音素)型ASR/TTS失敗の包括対策**: 既存OPEN-159の拡張サブ項目とするか独立登録かはFable判断。案B1-B4を引き継ぐ。

## 6. STOP/未確認
- 新規仕様判断が必要な点(列挙のみ): B1/B2/B4(Production prompt・retry仕様・TTS入力仕様に及ぶため人間ユーザー承認が前提)、A2(Opus L2決定の緩和)。
- 未確認: 実音声を人間が聞いた時に"Muse"と聞こえるか(`narration/comment_2.wav`=`attempts/comment_2_attempt2_...wav`は未試聴)。A1実装後のcomment_2再生成成否(実行禁止のため)。「/m/連結」仮説の直接証拠は、"through Muse"(attempt_history L11809 のcomment_2 first pass、OK)/"calls for Muse"(in_one_line take3)版がASRを通った事実と3系統一致誤聴のみ(音響分析・人間聴取は未実施)。
