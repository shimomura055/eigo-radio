# FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01 Phase 1-X: Family X 仕様一覧(read-only)

- 管理ID: FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01 委任_01(Sonnet実行層、2026-10-11)
- 調査時点: origin/main HEAD 0db97bae(origin/main、調査時点)。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)・設計書・コードをGrep+部分Readで照合。全文読込なし
- 性格: read-only調査。コード・Prompt・Routing・SSOT・Trial実行・API課金なし(費用¥0)。**本書は正式SSOTではなく**、Family Zへの横展開検討用の整理資料
- 機械可読版: 同名 `.json`(`items[]`に全項目、`counts`/`approved_for_production_not_yet_wired`/`shared_components`/`unconfirmed`)
- 並行調査(委任_02 Family Z)の領域には触れていない

## 0. Status語彙(厳密)

| 本書のStatus | 意味 |
|---|---|
| `PRODUCTION_WIRED` | 正式経路へ配線済み(SSOT記載に基づく) |
| `APPROVED_UNWIRED` | APPROVED_FOR_PRODUCTION済みだが実装・配線に未着手 |
| `IN_PROGRESS` | APPROVED_FOR_PRODUCTION済み、配線進行中(PRODUCTION_WIREDではない) |
| `VALIDATED_TRIAL_ONLY` | Trial成功のみ(Production採用ではない) |
| `OPEN_UNAPPROVED` | OPEN候補・未承認・Production仕様ではない |
| `SUPERSEDED_REMOVED` | 旧仕様・撤去済(現行仕様と混同しない) |
| `OPERATIONAL_RULE` | PM運用ルール(コード機構ではない) |
| `RECORD_ONLY` | 記録・参照資産(仕様ではない) |
| `NOT_WIRED_FOUNDATION` | 基盤として保持するが配線見送り |
| `UNCONFIRMED` | 本調査で確認できず |

`VALIDATED`(Trial成功)・`APPROVED_FOR_PRODUCTION`(ユーザー採用)・`PRODUCTION_WIRED`(正式配線)は別物として扱う。Trial結果をProduction仕様と読まない。`APPROVED_FOR_PRODUCTION`は人間ユーザーのみが決定でき、本書は決定を新設していない(既存SSOT/依頼文の記載を転記・区別しただけ)。

## 1. 重要な確認結果(先に読む)

1. **日本語記事モデル配置(E案、B3/R0/R1/R2=gpt-6.1-sol)**: 依頼文は『進行中、PRODUCTION_WIRED化はCloseout結果に従う』。調査時点のSSOT(CURRENT_SPEC L1157、DECISION_LOG 2026-10-11 Closeout行、commit 2823d0ea)には『Fable判定=PRODUCTION_WIRED、Gate 3=META run_sol61_01、merge adb15c30』が明記済みのため、その記載に従い `PRODUCTION_WIRED` とした(3-02)。CURRENT_SPEC L1153〜L1170本文の『R0=gpt-6-luna/R1・R2=gpt-6-astra』は旧配置の履歴記述(3-03=SUPERSEDED)。
2. **SCG・J2/E2・F1.5はSSOT未記録**: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSに『SCG』『J2/E2採用』『F1.5採用』の決定記録がない(Trial記録は存在)。`IN_PROGRESS`としたのは依頼文の記載+(SCGのみ)feature branchのcommit/コード実在による。いずれも`PRODUCTION_WIRED`ではない。
3. **名称衝突に注意**: Role Style現行の `J3`/`E2`(TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02、2026-09-28、PRODUCTION_WIRED)と、Tone Trial(2026-10-11)の `J2_BRIGHT`/`E2_UPBEAT` は**別の候補名**。『E2』が二重に存在する。Z展開検討・配線では必ず管理ID付きで区別すること。
4. **仕様の置換**: 旧Fact Checker/Ledger Deviation/案B/M1(b)/G3/JA Writer O→R1→R2/HEADING_READOUT は撤去済み(SUPERSEDED)。CURRENT_SPECにはこれらの旧記述が『履歴』として残るため、そのまま現行仕様として読まない。

## 2. 集計

- 総項目数: **101**(12領域)

### 2-1. Status別

| Status | 件数 |
|---|---|
| `PRODUCTION_WIRED` | 64 |
| `APPROVED_UNWIRED` | 0 |
| `IN_PROGRESS` | 3 |
| `VALIDATED_TRIAL_ONLY` | 1 |
| `OPEN_UNAPPROVED` | 12 |
| `SUPERSEDED_REMOVED` | 5 |
| `NOT_WIRED_FOUNDATION` | 1 |
| `OPERATIONAL_RULE` | 9 |
| `RECORD_ONLY` | 5 |
| `UNCONFIRMED` | 1 |
| 合計 | 101 |

### 2-2. 領域別

| # | 領域 | 項目数 | PW | IP | VAL | OPEN | SUP | OPR | REC | NW | UNC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Research・Fact抽出・Fact Ledger | 6 | 4 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 |
| 2 | Fact選択・Storyline・B3 | 5 | 4 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 3 | 日本語記事生成 R0/R1/R2(W-1) | 12 | 6 | 0 | 0 | 3 | 2 | 0 | 1 | 0 | 0 |
| 4 | 英語化・難易度調整 | 6 | 4 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| 5 | 記事構造・Comment・Preview・In One Line | 9 | 7 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| 6 | Key Phrases・解説・レベル別仕様 | 9 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 | 音声Voice・Style・TTS・速度 | 9 | 5 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| 8 | ASR・読み誤り・再生成・SCG | 12 | 8 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| 9 | Validator・品質Gate・Review Queue | 9 | 6 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 |
| 10 | retry・fallback・regeneration・resume | 8 | 5 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 0 |
| 11 | 音声Assembly・Master Store・試聴ページ | 5 | 2 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 |
| 12 | コスト・runtime管理・運用ルール | 11 | 4 | 0 | 0 | 1 | 0 | 5 | 1 | 0 | 0 |

(PW=PRODUCTION_WIRED、IP=IN_PROGRESS、VAL=VALIDATED_TRIAL_ONLY、OPEN=OPEN_UNAPPROVED、SUP=SUPERSEDED_REMOVED、OPR=OPERATIONAL_RULE、REC=RECORD_ONLY、NW=NOT_WIRED_FOUNDATION、UNC=UNCONFIRMED。`APPROVED_UNWIRED`(承認済みだが着手なし)は0件)

### 2-3. Family固有 / 共通の別

| scope | 件数 |
|---|---|
| FAMILY_X | 60 |
| SHARED | 31 |
| GOVERNANCE | 10 |

## 3. APPROVED_FOR_PRODUCTIONだが未配線(配線進行中を含む)

| 仕様 | 本書Status | 根拠・現況 |
|---|---|---|
| SCG(日本語Secondary Confirm Gate) | `IN_PROGRESS` | APPROVED_FOR_PRODUCTION 2026-10-11(依頼文+branchコード/commit文言)。feature/scg-ja-secondary-01 HEAD be936a96(main先行6 commit、Opus是正・runtime evidence a-e取得済)。main未merge、SSOT未記録(OPEN-258行は旧Status) |
| J2/E2 Tone(Preview・Comment) | `IN_PROGRESS` | APPROVED_FOR_PRODUCTION 2026-10-11(依頼文)。SSOT未記録。配線管理ID FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01はリポジトリ内0件、worktree feature/coffee-new-tone-01はmain先行commit 0 |
| F1.5 Full Story Tone | `IN_PROGRESS` | 同上(Full Story) |

`APPROVED_UNWIRED`(承認済みで実装未着手)に該当するものは、調査範囲では確認できなかった。なお『TTS Pronunciation Hint』は承認ではなく基盤保持・配線見送り(`NOT_WIRED_FOUNDATION`、8-06)。

## 4. 他Familyと共有する共通コンポーネント

| コンポーネント | 共有状況・備考 |
|---|---|
| er006_model_routing_contract_01.py(PROCESS_MODEL_MAP/require_model) | 全Family共通のfail-closed Routing。Family X固有キー(FAMILY_X_*)を同ファイルに持つ |
| er005_output/cost_baseline_01/pricing_snapshot.json + er009 PRICING_USD_PER_M | 単価台帳・費用機構(fail-closed) |
| er007_ja_asr_validator_01 / er007_ja_secondary_asr_01(+SCG実装予定先) | 日本語ASR Validator/Cascade。SCGは同moduleへ実装(feature branch) |
| er006_secondary_asr_01 / er006_preprod_hardening_01_validation(English ASR Tier1/Tier3) | 英語ASR Cascade・Semantic Equivalence |
| er011_a2_reading_resolver_01 | A2(日本語)Reading Resolver |
| er006_pronunciation_ledger_01(ASR側) | Pronunciation Ledger(Phrase List供給) |
| er020_tts_retry_local_rewrite_01(Connected Speech 5role・Local Rewrite・全文性検証) | role判定resolve_narrative_roleは他Familyも参照(Family ZはRead-only参照とimportコメントあり) |
| er011_human_review_lock_01 / human_review_queue.jsonl | TTS最大3 attempt・Human Review Lock |
| er006_master_audio_store_01(Master Audio Store) | 固定phrase/KP phrase reuse基盤 |
| er003_v1_n3_01_scaffold_generate(Key Phrase共有層)・er003_key_words_production・er003_v1_repro01_main_generate | KP選定/英語Component/QA。CURRENT_SPEC上『Family A/B/C/News/Z全ての共有Production入口』 |
| er029/er030 KP DB Hybrid + Source Reference Contract | Contractは『Family X/Family Z共通Core』(CURRENT_SPEC明記)。DB Hybrid方式自体の配線はFamily X限定(Z用ruleは er031_*_family_z_trial 系=Trial) |
| er033_tts_flash_lite_backend_wiring_01(backend) | backend実装は共通moduleだが配線ゲートはFamily Xのtts_backend明示。Family ZでのProduction利用は未確認(Z調査側) |
| er003_v1_n3_01_standard_a2_generate / A2 6%減速(apply_a2_slowdown_postprocess) | Standard(A2)方式はFamily A由来の共通仕様 |
| audio assembly(er003_v1_n3_01_assemble: gain/headroom/Audio Validation Gate)・audio_review_player.py | 共通Assembly/player |
| Review Queue/RF(er053_risk_flagger_production_01・er053_review_queue_01・er053_en_sentence_splitter_01) | 名称は汎用だがProduction配線はFamily X(英語記事)のみ。他Familyでの利用は未確認 |
| docs/pm/PM_GOVERNANCE.md の運用ルール(Gate 1〜7・14-6・25・10-X等) | Family非依存のPM運用 |

### Family X固有(共通ではない)

- W-1 Writer(er053_family_x_factlock_ja_writer_01)+記号QA案A+U-1/U-2
- storyline_b3(er019_family_x_storyline_b3_fact_selection_01)+決定論producer(er053_b3_deterministic_producer_01)+契約V1〜V10
- M1(a) In one line(Advanced限定)・Family X新記事構造(v2 3分割/Comment3/4 role)
- Role Style(FAMILY_X_ROLE_STYLE_JA/EN)・固定フレーズChampion・Advanced KP英語解説(Variant B)・KP音声構造
- audio runner(er019_family_x_audio_production_runner_01)・TTS前3者照合guard

## 5. 確認できなかった項目(推測せず『未確認』)

- 『FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01』の実在・進捗(リポジトリ/SSOT/委任ログに記録なし。branch feature/coffee-new-tone-01はmain先行commit 0)
- J2/E2/F1.5のAPPROVED_FOR_PRODUCTION決定文(ユーザー逐語)のSSOT記録(DECISION_LOGにはTrial記録のみ、Production採用未承認/試聴待ちの記述で止まる)
- SCGのAPPROVED_FOR_PRODUCTION決定文のSSOT記録(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSに『SCG』0件)
- TTS Pronunciation Hint(augment_style_prefix_with_pronunciation)が現在もProduction未配線か(CURRENT_SPEC L1995記述時点以降の変更)
- Family X audio runnerのTTS実行方式(Standard同期かBatchか)
- Standard(A2)側の全segmentのvoice名明細(Advancedは plan labelから確認済)
- 『fallback voice』(voice切替fallback)の仕様・実装(minimal instruction fallbackは確認済)
- SFX行(Intro/Notification 1〜3)の現行構造上の役割(SE-1『Point One/Two用Notification音は不使用』との関係)
- Section Segmentation Contract(5-07)の途中Heading廃止後の現行有効性
- Production parse_ledgerとTrial側『台帳パーサ欠落』(FIX01)の実装同一性
- OPEN-243/235/236/238/239/246/250の最新Close状況(行頭Statusのみでは判定不能)
- E案1記事セット費用(約63.5円など)のSSOT記載有無(出典はCOST_PER_ARTICLE_SET_E_VS_A_01.mdの見積。推定含む)
- CURRENT_SPEC L1971の『gpt-5.6-luna』表記と現行コード参照(WRITER_MODEL=gpt-6-luna)の整合更新有無
- Family Zにおける上記共通componentの利用状況(委任_02=Z_INVENTORYが担当)
- KP 4+1構成(6-03)のGate3判定の行内明示(設計書表記のみ確認)

## 6. 項目一覧(12領域)

凡例: scope=FAMILY_X(Family X固有)/SHARED(他Familyと共有する共通層)/GOVERNANCE(PM運用)。根拠は『ファイル・関数・DECISION_LOG/OPEN番号・管理ID』。

### 領域1. Research・Fact抽出・Fact Ledger

#### 1-01 Research(web_search)+独立Verification
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: Topic文字列→Researcher(web_search tool)→Verification(別call、web_search付)。model=RESEARCH_MODEL(gpt-6-luna、routing EVIDENCE_PACK/VFL/VERIFICATION)。runner入口=er019_family_x_entertainment_production_runner_01.run_research_and_ledger
- 根拠: er012_e_family_entertainment_two_level_runner_01.run_researcher_for_topic/run_verification_for_topic; er006_model_routing_contract_01.PROCESS_MODEL_MAP; OPEN-241(PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 Fable判定2026-10-08); 実走=er019_output/coffee_prices/run_l3_01・meta/run_sol61_01
- 備考: Routing/単価は共通基盤。Research/Ledger呼出し関数はFamily X(efam)側。web_search課金は予算ガード計上済(OPEN-242、PRODUCTION_WIRED 2026-10-08)

#### 1-02 Verified Fact Ledger(verified_fact_ledger.txt)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: Research+Verification結果から build_verified_ledger_text で台帳確定(verdict_counts: VERIFIED/AMBIGUOUS等、kept_facts)。既存Ledgerがあれば再利用(reused=true、Research再実行なし)
- 根拠: run_research_and_ledger(runner L97-); vfl01.build_verified_ledger_text; runtime_evidence.json(research_ledger/)
- 備考: 台帳ID(例MUSE-HC-011)はRF・注記・Queueで参照される

#### 1-03 AMBIGUOUS Fact扱い
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: 台帳ヘッダ[AMBIGUOUS...]はD-det v2が決定論で処理(固定限定文『この点は確定していない。』、台帳タグ原文保持=AMB_TAG_ORIGINAL)。Writerへ断定させない
- 根拠: er053_b3_deterministic_producer_01.py(AMB_QUALIFIER/AMB_TAG_ORIGINAL/HEAD正規表現); CURRENT_SPEC『Family X Production経路』; ユーザー完了承認2026-10-11
- 備考: B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01(OPEN-248)案D由来

#### 1-04 Ledger parser(決定論)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: producer内 parse_ledger(HEAD/FLD正規表現)で台帳→Fact単位へ分解。Fact本文の原本はB3 Facts文でなく『台帳+選択IDからの決定論再導出(D-full)』
- 根拠: er053_b3_deterministic_producer_01.parse_ledger/assemble_D; 契約V10(er053_b3_annotation_contract_01)
- 備考: WRITER-R0-MODEL-IMPACT-TRIAL-01-FIX01で判明した『台帳パーサ欠落』はTrial側パーサの話であり、Production parse_ledgerと同一実装かは未確認

#### 1-05 Fact台帳の明確化(上流対策)設計 OPEN-237
- **Status**: `OPEN_UNAPPROVED` / scope: FAMILY_X
- 要旨: Writerが誤解しやすい台帳表現(HC-012『ロールバック』等)を台帳側で明確化・分割する案。未承認の新仕様
- 根拠: OPEN_ITEMS OPEN-237(USER_DECISION_REQUIRED、設計完了・Opus条件A済)
- 備考: Production採用扱いではない

#### 1-06 Trial driver側 --theme パス文字列混入の影響 OPEN-240
- **Status**: `OPEN_UNAPPROVED` / scope: FAMILY_X
- 要旨: 過去Trial(TRIAL-04 Control/E2E_02)で--themeにtopic.txt内容でなくパス文字列が渡っていた影響が未測定
- 根拠: OPEN_ITEMS OPEN-240
- 備考: Trial側の問題。Production runnerは--themeを文字列のまま使う(コード確認)

### 領域2. Fact選択・Storyline・B3

#### 2-01 storyline_b3(Storyline1行+Fact選定、4テスト)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: Full LedgerからStoryline1行決定→全fact_idに4テスト→selected/excluded→Selected Fact Brief。LLM 1 call。採用Fact数の目安3〜5件(Hard ruleではない、6件以上はrecheck_note必須記入)。model=gpt-6.1-sol(FAMILY_X_STORYLINE_B3)、effort high
- 根拠: er019_family_x_storyline_b3_fact_selection_01.py; runner.run_storyline_b3; DECISION_LOG 2026-10-11 SOL61 Closeout(PRODUCTION_WIRED、merge adb15c30、Gate3=META run_sol61_01); CURRENT_SPEC L1157
- 備考: 旧配置(Luna暗黙参照vfl01.MODEL)はSUPERSEDED。API前require_model+返却model不一致STOP

#### 2-02 決定論B3 producer(D-det v2+D-full assembler)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: storyline_b3確定直後に必ず1回(run_annotation_producer)。LLM call 0・¥0/記事。RULE_VERSION=deterministic_v2.0、rules_sha256=525f2309…(CURRENT_SPEC記載)。注記なしB3へのfallback/switch/CLI/環境変数は存在しない。初回/regeneration/resume/再利用の全分岐を通る
- 根拠: er053_b3_deterministic_producer_01.py(PRODUCER=deterministic_v2); CURRENT_SPEC『経路全体図』【PRODUCTION_WIRED(2026-10-11ユーザー正式完了承認)】; OPEN-247 CLOSED
- 備考: Fact/Writer指示/制約の分離=案D(OPEN-248、Trial VALIDATED→Production採用済)。制約ブロック見出し『Writerへの注意(事実ではありません)』

#### 2-03 注記済みB3入力契約 V1〜V10(fail-closed)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: validate_annotated_b3: V1存在/UTF-8/JSON、V2 manifest、V3 sha整合、V4 parse成功、V5 Facts全行形式、V6 数値印(【中核数値】/【周辺数値】)、V7 sidecar整合、V8 checks、V9 spec/brief sha、V10 Storyline完全一致+事実本文連結一致。違反は課金前STOP
- 根拠: er053_b3_annotation_contract_01.py; er053_output/risk_flagger_production_wiring_01/completion_matrix_01.md
- 備考: V5/V6/V10はTrial成果物に合わせた解釈追加を含む(Fable承認、OPEN-247)

#### 2-04 B3再選定時のU-1 STOPと下流再生成 OPEN-249
- **Status**: `OPEN_UNAPPROVED` / scope: FAMILY_X
- 要旨: --regenerate-stage storyline_b3で注記shaが変わるとU-1がPROVENANCE_MISMATCHでSTOP。下流自動再生成は未実装(利用者が--regenerate-stage writerを明示)
- 根拠: OPEN_ITEMS OPEN-249(現状は安全側、Closeout時点で維持)
- 備考: 自動再生成は新仕様のため未実装・ユーザー判断

#### 2-05 Fact数・Fact選定の品質ゲート
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: Fact数はSoft目安(3〜5件)のみでValidator/Gate化なし。B3後のValidatorは契約V1〜V10(構造整合)のみ。内容品質の判定はRF+Human Review側
- 根拠: storyline_b3 prompt【採用Fact数についての注意】; 契約V1-V10
- 備考: 『6件以上』時のrecheck_noteはsoft_warningsへ記録

### 領域3. 日本語記事生成 R0/R1/R2(W-1)

#### 3-01 W-1 Writer(R0 Fact Lock→R1→R2)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: run_w1_writer。R0=Fact Lock(developer message、単発、previous_response_idなし)→R1(Revise、独立、developer none)→R2(Revise、入力=R1のraw出力 factlock/r1.raw.md)。effort high。R0の[ニュース]欄=注記済みFacts+制約ブロック(annotated.news_field_text)
- 根拠: er053_family_x_factlock_ja_writer_01.py(CHAIN_METHOD='W-1'); CURRENT_SPEC『W-1 Writer』【PRODUCTION_WIRED(2026-10-11ユーザー正式完了承認)】
- 備考: Prompt本体・Fact Lock構造・Revision方式はTrialからbyte-identical移植(verbatim_shasをruntime_evidenceへ記録、変更はUSER_DECISION_REQUIRED)

#### 3-02 日本語記事モデル配置E案(B3/R0/R1/R2=gpt-6.1-sol)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: ユーザー正式決定2026-10-11(Blind評価、N=1×3テーマ)でAPPROVED_FOR_PRODUCTION。SSOT Closeout(commit 2823d0ea)でPRODUCTION_WIRED。routing key FAMILY_X_STORYLINE_B3/FAMILY_X_FACTLOCK_R0/FAMILY_X_FACTLOCK_REVISE=gpt-6.1-sol。Gate3=META run_sol61_01: 全4 stageのactual model_id=gpt-6.1-sol・model_mismatch=false・費用18.499円・173秒。rollback tag rollback/pre-sol61-ja-allocation-01-20261011(merge adb15c30)
- 根拠: DECISION_LOG 2026-10-11 SOL61 Closeout(PW)/委任_01決定; CURRENT_SPEC L1155/L1157; er053_output/sol61_production_wiring_01/runtime_evidence_01.md; OPEN-255 CLOSED
- 備考: 依頼文は『進行中・推測で確定しない』だったが、本調査時点(origin/main HEAD 0db97bae)のSSOT(CURRENT_SPEC L1157、DECISION_LOG Closeout行)に『Fable判定=PRODUCTION_WIRED』が明記されているため、その記述に従う。単価gpt-6.1-sol=input 2.00/cached 0.10/output 10.00 USD per 1M(pricing_snapshot登録値)。CURRENT_SPEC L1153〜L1170本文中の『R0=gpt-6-luna/R1・R2=gpt-6-astra』は旧配置の履歴記述

#### 3-03 旧配置 R0=gpt-6-luna / R1・R2=gpt-6-astra
- **Status**: `SUPERSEDED_REMOVED` / scope: FAMILY_X
- 要旨: E案移行前のW-1配置(2026-10-10〜10-11 PRODUCTION_WIRED時点)
- 根拠: CURRENT_SPEC L1155(旧配置の記述である旨)
- 備考: gpt-6-astraはW-1専用の別集計経路だった(OPEN-246 ASTRA-BILLING-RECONCILIATION-01は請求照合未実施のまま。E案でR1/R2はSolへ移行したため現行経路での重要度は低下、Close状況は未確認)

#### 3-04 U-1(W-1来歴のないJA再利用禁止)/U-2(単体CLI封鎖)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: U-1: load_reused_ja_textが ja_writer/runtime_evidence.json の chain_method=='W-1' かつannotated_md_sha256一致時のみ再利用、違えばLegacyWriterProvenanceStop。U-2: er012_e単体CLIのwriter経路(--ja-article/--stage writer|all/--regenerate-stage)を封鎖(--stage ledgerのみ残す)
- 根拠: runner.load_reused_ja_text; er012_e_..._01.guard_standalone_cli; CURRENT_SPEC『U-1/U-2』【PRODUCTION_WIRED(2026-10-11)】
- 備考: U-1はmodel非依存(既存Luna/Astra生成JAの再利用を許容、SOL61 Closeout記載)

#### 3-05 音声化禁止記号QA(案A)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: R0は禁止記号検出で1回だけ再生成、R2は検出時にR2のみ同一R1 rawで1回再実行、残ればJASymbolCheckStopError(STOP)
- 根拠: er053_family_x_factlock_ja_writer_01.py(JASymbolCheckStopError、w1_r0_symbol_regen); CURRENT_SPEC『W-1 Writer』
- 備考: SOL61 META runtime: 記号QA findings 0、R0再生成なし・R2再実行なし

#### 3-06 Concreteness Control(AN3-T0)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: R0 PromptへCONCRETENESS_CONTROL_AN3_BLOCK(sha 067030ff53ecb76a…)を含める(W-1移植後もR0 Promptに含まれたまま)
- 根拠: CURRENT_SPEC『Family X Writer — Concreteness Control(AN3-T0)』(Gate3=Meta run_03、2026-09-29); runtime_evidence記録

#### 3-07 Prompt sha・verbatim固定
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: verbatim_shas()をruntime_evidenceへ記録。R1/R2のUSER_TMPL・MUSTFIX_PRIORITY等は逐語固定。Prompt変更はUSER_DECISION_REQUIRED
- 根拠: er053_family_x_factlock_ja_writer_01.verbatim_shas; SOL61でPrompt shaは不変(CURRENT_SPEC L1155)
- 備考: 個別sha値はruntime_evidenceで確認(本書では未転記)

#### 3-08 生成段階の禁止記号予防 OPEN-261
- **Status**: `OPEN_UNAPPROVED` / scope: FAMILY_X
- 要旨: coffee D(R1=Luna)が全角括弧『（）』『〜』を出力、R2再実行後も残存しSTOP。W-1のR1/R2 promptには禁止記号指示がない(R0のみSYMBOL_PREVENTION_BLOCK)。予防策P1〜P5候補
- 根拠: OPEN_ITEMS OPEN-261(OPEN候補・未承認、2026-10-11)
- 備考: E案(R1=Sol)では未観測。Production変更はユーザー承認まで禁止

#### 3-09 記号QAが句読点重複『、。』を検出しない OPEN-262
- **Status**: `OPEN_UNAPPROVED` / scope: FAMILY_X
- 要旨: SOL61 runtime META revision2.mdで1件。仕様候補のため未実装
- 根拠: OPEN_ITEMS OPEN-262(2026-10-11)

#### 3-10 JA R2がENでの修正・削除に追随しない OPEN-239
- **Status**: `OPEN_UNAPPROVED` / scope: FAMILY_X
- 要旨: 旧Checker前提の指摘(JA/EN不一致)。旧Fact Checker撤去後の現行有効性は未確認
- 根拠: OPEN_ITEMS OPEN-239(2026-10-07)
- 備考: 旧Checker系はSUPERSEDED(OPEN-244)

#### 3-11 旧JA Writer O→R1→R2(+JA Fact Check/差し戻し)
- **Status**: `SUPERSEDED_REMOVED` / scope: FAMILY_X
- 要旨: er019_family_x_ja_writer_o_r1_r2_01(Original→R1→R2→Fact Check)。Production正式経路から置換・撤去。W-1来歴なしJAはU-1で通常経路再利用不可
- 根拠: CURRENT_SPEC『旧Fact Checker撤去(2026-10-10)』; RISK-FLAGGER-PRODUCTION-WIRING-01_08.md R-01〜R-28
- 備考: moduleファイルは残置

#### 3-12 日本語記事OKマスター(HUMAN_APPROVED_QUALITY_MASTER)
- **Status**: `RECORD_ONLY` / scope: FAMILY_X
- 要旨: E案R2×3(META/hormuz/coffee_prices)=OKマスター、C案×3=次点参照。記事品質の承認のみ。META完成音声の公開判断は保留
- 根拠: docs/quality/ja_article_blind_eval_2026_10_11/README.md; docs/quality/ja_quality_masters/; DECISION_LOG 2026-10-11 委任_01
- 備考: 仕様ではなく品質基準資産。音声・翻訳・RF等の承認ではない

### 領域4. 英語化・難易度調整

#### 4-01 Advanced(B1B)忠実英訳(見出し生成なし)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: 日本語R2から generate_family_x_faithful_translation。途中Heading生成指示なし。model=NATURAL_ENGLISH_ADAPTATION=WRITER_MODEL(gpt-6-luna)
- 根拠: er003_v1_n3_01_advanced_adaptation_generate.generate_family_x_faithful_translation; FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 W1(Gate3 Meta run_03 2026-09-29)

#### 4-02 M1(a) In one line(Advanced限定・無条件ON)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: 日本語R2本文+Ledgerを『In one line』生成へ常に追加(環境変数条件なし)。Standardは呼ばない(意図的Level非対称、Advanced英文からのLevel調整で差が伝播)。初回/段落retry再生成の両方で同じ関数
- 根拠: er012_e_..._01._advanced_in_one_line; CURRENT_SPEC『M1(a)』(ユーザー採用2026-10-10、PRODUCTION_WIRED 2026-10-11)

#### 4-03 Standard(A2)Level調整
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: 入力=Advanced英文(RF結果は無関係、記事不変)。v5 6,000語ライン+自然さ優先Prompt。generate_family_x_standard_a2_no_heading。model=STANDARD_A2_ADAPTATION(gpt-6-luna)
- 根拠: er003_v1_n3_01_standard_a2_generate; routing STANDARD_A2_ADAPTATION; runner Standard stage
- 備考: Standard(A2)方式自体はFamily A由来の共通仕様をFamily Xが利用

#### 4-04 Standardの英語6%減速
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: A2英語ナレーション: A2_ENGLISH_STYLE_PREFIX_SLOWER+post-process time-stretch(atempo、実測比1.0595)。Family X a2 segment生成は generate_a2_segment_with_slowdown 経由(コード確認)
- 根拠: CURRENT_SPEC A2英語ナレーション速度行; er019_family_x_audio_production_runner_01 L979; 『Role Style』regressionでslower指示との重畳を実測
- 備考: Full Story Tone Trial(F0〜F2)は『通常速度(6%減速なし)』で実施=Trial条件であり、Productionの6%減速仕様は不変

#### 4-05 翻訳段のLedger Deviation Check/M1(b)/G3
- **Status**: `SUPERSEDED_REMOVED` / scope: FAMILY_X
- 要旨: 英訳後のDeviation Check、MAJOR must-fix全文再生成、案B(JA差し戻し)、M1(b)/G3は撤去済。共有関数run_deviation_check+DEVIATION_PROMPTは旧Family A/B/C用に残置(Family X経路参照0、AST+spy testで固定)
- 根拠: CURRENT_SPEC『旧Fact Checker撤去』; 実施表RISK-FLAGGER-PRODUCTION-WIRING-01_08.md R-01〜R-28

#### 4-06 翻訳段の事実NG(主体取違え・複数形化等) OPEN-243
- **Status**: `OPEN_UNAPPROVED` / scope: FAMILY_X
- 要旨: 翻訳段で生じる事実NGとCheckerの見逃し。現行は旧Checkerを撤去しRF 4条件+Human Reviewで後検知する運用(OPEN-244)
- 根拠: OPEN_ITEMS OPEN-243(POST_USER_VALIDATION、起票2026-10-08)
- 備考: Close有無は本調査で未確認(行頭Statusに明示なし)

### 領域5. 記事構造・Comment・Preview・In One Line

#### 5-01 新記事構造(途中Heading廃止・段落境界3分割)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: 見出し生成指示なし・split_family_x_article_text_v2で決定論3分割。Comment1→本文1→Comment2→本文2→Comment3→本文3→Comment4→In One Line。Heading Readout撤去
- 根拠: CURRENT_SPEC『Family X音声構造』項目6(W1、Gate3=Meta run_03、2026-09-29); er019_family_x_audio_plan_01(V2 segment order)
- 備考: 旧split_article_text()はFamily A現役で無変更(AST testでFamily X経路から到達不能を固定、OPEN-228解消)

#### 5-02 Comment 4本
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: Advanced=英語Comment(Charon)、Standard=日本語Comment。Comment1/2/PreviewはFamily A既存role流用、Comment3/4はFamily X専用role文言(FAMILY_X_B1/A2_COMMENT_3/4_ROLE)。内部構造ラベル(Part 1等)を出力に含めない制約
- 根拠: er019_family_x_audio_plan_01.py L181-; CURRENT_SPEC項目1/6
- 備考: SE-1: Point One/Two用Notification音はFamily Xで不使用、本文前後に新効果音なし(CLOSED)。ただしplanにはSFX行(Intro/Notification 1〜3)が存在し、その役割の詳細は未確認

#### 5-03 Preview(Standard=日本語/Advanced=英語)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: Standard Previewは日本語(A2 Preview role、2文程度・80〜110字目安)、Advanced Previewは平易な英語(Charon)。『Preview intro』は固定フレーズChampion
- 根拠: CURRENT_SPEC『Preview』節/B1 Support節; plan A2/B1 segment order
- 備考: Preview節はA2/旧P-seriesの記述が主で、Family X Advancedの現行Previewは『B1 Support-based Natural English』節に依拠。細部は未再照合

#### 5-04 In One Line(短文)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: AdvancedはM1(a)入り(4-02)、Standardはレベル調整経由。In One Line=別枠(本文3の後)。Comment4はIn One Lineの文数を断定しない
- 根拠: CURRENT_SPEC項目2/6; plan FAMILY_X_*_COMMENT_4_ROLE

#### 5-05 本文1/2/3比率(50/25/25)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: 理想目安のみ。Validator/Gate化しない(明らかなアンバランスが多発した場合のみ再検討)
- 根拠: CURRENT_SPEC項目2(DECIDED)

#### 5-06 段落数不足の1回must-fix再生成
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: Advanced/Standardとも3段落未満なら共通ヘルパー _family_x_ensure_split_or_paragraph_retry で1回だけ再生成、なお不能ならSTOP(fail-closed、他retry軸と独立)
- 根拠: er012_e_..._01._family_x_ensure_split_or_paragraph_retry; CURRENT_SPEC項目6

#### 5-07 Section Segmentation(見出し境界)Contract
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: Advanced/Standard Promptへ見出し境界Contract(ADVANCED_SECTION_BOUNDARY_CONTRACT/STANDARD_A2_SECTION_PRESERVE_SENTENCE)を適用(2026-09-27)
- 根拠: CURRENT_SPEC項目3(commit 9cec45f1/e7311d37)
- 備考: 途中Heading廃止(W1 2026-09-29)後の現行有効性・Prompt残存は未確認

#### 5-08 見出し独立sub-segment(HEADING_READOUT)
- **Status**: `SUPERSEDED_REMOVED` / scope: FAMILY_X
- 要旨: Stage 3cで導入→W1で撤去済
- 根拠: CURRENT_SPEC項目1/6(撤去)

#### 5-09 音声runnerのsource_dir導出 OPEN-234
- **Status**: `OPEN_UNAPPROVED` / scope: FAMILY_X
- 要旨: --slug/--runのみからer019_output/{slug}/{run}を導出。writer段--out-dirと不一致なら手動コピーが必要
- 根拠: OPEN_ITEMS OPEN-234
- 備考: 恒久対応(CLI引数追加等)の要否はユーザー判断

### 領域6. Key Phrases・解説・レベル別仕様

#### 6-01 Key Phrase選定: DB Hybrid(Primary)/Strategy L(Fallback)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: 決定論DB候補生成(CEFR-J/NGSL/Wiktionary/wordfreq)+compact LLM選定。Family X通常記事のPrimary。DbHybridFailure時はStrategy L全文方式へFallback。Strategy L経路max_attempts=MAX_PRODUCTION_RETRY_ATTEMPTS(=2)
- 根拠: CURRENT_SPEC Key Phrase節『Family X選定方式(DB Hybrid)』(2026-09-27 APPROVED→Fable Gate3 PRODUCTION_WIRED、Opus L2 BLOCKER 3件は修正1回目で解消); er029/er030; er003_key_words_production.MAX_PRODUCTION_RETRY_ATTEMPTS=2
- 備考: Family X限定配線。LLM段のモデルはSUPPORT系(gpt-6-luna、OPEN-251記載)

#### 6-02 KP選定LLM出力契約(Source Reference Contract、候補ID方式)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: selector LLM出力からsource_sentence/source_spanの自由記述を除去し source_candidate_id を必須化。Family X/Family Z共通Core contract
- 根拠: CURRENT_SPEC Key Phrase節(2026-09-28、Fable Gate3、PRODUCTION_WIRED); design_kp_source_reference_contract_01.md
- 備考: Family X配線+Family Z共通仕様。Family Z runnerは配線時点で未配線・対象外と記載(現在状況はZ調査=委任_02側)

#### 6-03 4+1構成(重要語4+Topic Phrase/Word 1)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: Key Phrase 5枠を『important 4+topic 1』へ。Topic=記事特有で事前に意味・用法・音の理解が望ましい語句
- 根拠: CURRENT_SPEC Key Phrase節(2026-09-28 APPROVED); design_family_x_refresh_e2e_production_wiring_01.md §(KP 4+1構成: DECIDED/PRODUCTION_WIRED(既存、変更対象外))
- 備考: CURRENT_SPEC該当行にはGate3判定の個別明記が見当たらず、PRODUCTION_WIREDの根拠は上記設計書の表記による(行内の明示文言は未確認)

#### 6-04 KP音声構造(共通骨格: 英語Phrase→中間→英語Phrase)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: Standard=英語→日本語意味(J3)→英語、Advanced=英語→英語解説(Variant B)→英語。最後のPhraseは最初と同一canonical(phrase_repeatは英語と同一sha256=Master reuse)
- 根拠: CURRENT_SPEC『Key Phrase 音声構造』【PRODUCTION_WIRED(2026-09-29、Gate3=Meta run_03)】; er019_family_x_audio_production_runner_01 L735-805
- 備考: 再生reuseによりAdvancedの追加API費用なし(実測=runtime evidence記載)

#### 6-05 Advanced Key Phrase英語解説(text仕様+Aoede/Variant B style)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: KEY_PHRASE_EXPLANATION_EN style=『clear, precise, at a measured pace, without dragging』(Variant B)、voice=Aoede。text生成=SUPPORT系モデル(routingキーはW4追加)。KP解説fail-closed、cache text/style_version guard
- 根拠: er033_tts_flash_lite_family_x_styles_01.KEY_PHRASE_EXPLANATION_EN; er019_family_x_kp_explanation_01.py; CURRENT_SPEC『Advanced Key Phrase 英語解説』(W4/W5)

#### 6-06 Standard Key Phrase日本語意味へのJ3適用
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: japanese_meaning/japanese_gloss(_tts)にJ3(_role_style_ja)を適用。backendゲート=speech_metadata_flash_lite明示時のみ
- 根拠: CURRENT_SPEC『可変segment Role Style』W5追記; Gate3=Meta run_03(style_prefix=J3文言)

#### 6-07 KP日本語gloss規約(表示用/TTS用分離・数値placeholder回避・括弧併記禁止・自然さ基準)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: 選定Prompt(A2/B1共有 b1_p2_keywords_l_prompt_template.txt)の規約A/B、表示用japanese_gloss/TTS用japanese_gloss_tts分離、構造Validator(validate_min_unit_selection)
- 根拠: CURRENT_SPEC Key Phrase節(2026-09-06以降の複数行、PRODUCTION_WIRED)
- 備考: Family A/B/C/X共有の選定Prompt層

#### 6-08 KP英語Component生成(Minimal instruction+English Lock retry、function-word reduction、source gate、disfluency QA、set redundancy QA)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: KEY_PHRASE_MINIMAL_MAX_ATTEMPTS=2/KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS=2、冠詞reduction指示、canonicalization(source_span→display_phrase→key_phrase→used_form)、人称代名詞一般化、5件相互重複QA
- 根拠: CURRENT_SPEC Key Phrase節; er003_v1_repro01_main_generate.py L628-629
- 備考: 共通Production層。個別No.9例外(default)等の履歴あり

#### 6-09 Strategy L(Listening Blocker Ranking)/5件/1〜5語
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: 選定方式Strategy L、件数5/記事、語数1〜5語。Family XではFallback位置づけ(6-01)
- 根拠: CURRENT_SPEC Key Phrase節 DECIDED行(ER-003-P2I/KP-02-R1)

### 領域7. 音声Voice・Style・TTS・速度

#### 7-01 TTS backend: speech_metadata_flash_lite / gemini-3.8-flash-lite-tts
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: routing key FAMILY_X_FLASH_LITE_TTS=gemini-3.8-flash-lite-tts。Family X audio runnerはtts stage開始前にbackend fail-fast(--tts-backend speech_metadata_flash_lite必須、legacyは--allow-legacy-backend明示時のみ)。CLI既定値自体はstructured_separation
- 根拠: er033_tts_flash_lite_backend_wiring_01.py; er006_model_routing_contract_01.py L119; er019_family_x_audio_production_runner_01.py L1785-1830(fail-fast); design_flash_lite_family_x_wiring_01.md
- 備考: Family A/B/Cは当該keyを参照しない(legacy)。Family Zでの利用は未確認(Z調査側)

#### 7-02 Voice割当(Charon/Aoede)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: Advanced: Welcome/Topic intro/Preview/Comment=Charon(英語)、Full Story=Aoede(plan segment labelで確認)、KP解説=Aoede。Standard: 日本語segment(Comment等)は日本語、英語Full Story/KP英語はEnglish voice(個別voice名のStandard側明細は未確認)
- 根拠: er019_family_x_audio_plan_01.py L246-300; CURRENT_SPEC『可変segment Role Style』/KP節
- 備考: Standard側segmentごとのvoice名はplan定数から全件は未確認

#### 7-03 Role Style 現行: JA=J3 / EN=E2
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: JA(J3)=『落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。演技がかった話し方は避けてください。』をStandard(A2)のpreview/comment_1〜4・japanese_title・KP日本語意味へ適用(長文JAPANESE_STYLE_PREFIXを置換)。EN(E2)=TOPIC_INTRO/FULL_STORY/IN_ONE_LINEの3roleのみ(PREVIEW/COMMENT='calm, conversational'、HEADING_READOUT='brief and clear'は不変)。backendゲート=speech_metadata_flash_lite明示時のみ
- 根拠: er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_JA/_EN(コード照合済); CURRENT_SPEC『可変segment Role Style(J3/E2)』【PRODUCTION_WIRED(2026-09-29、Gate3=Meta run_03)】
- 備考: 命名注意: 本項のE2/J3はTTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02(2026-09-28)の候補名。7-04のJ2/E2(Tone Trial 2026-10-11)とは別物で名称が衝突する

#### 7-04 新Tone: J2(JA明るく親しみやすい)/E2(EN upbeat、Preview・Comment)
- **Status**: `IN_PROGRESS` / scope: FAMILY_X
- 要旨: FAMILY-X-TTS-VOICE-TONE-BRIGHTNESS-TRIAL-01(2026-10-11)の候補。J2_BRIGHT=『明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽やかなリズムをつけてください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。』/E2_UPBEAT=『warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation.』(Trial結果RESULT_01.md)。依頼文: Preview・Commentへ適用するAPPROVED_FOR_PRODUCTION(2026-10-11、ユーザー決定)、配線は FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 で進行中・未完
- 根拠: (根拠1)Trial: er053_output/tts_voice_tone_brightness_trial_01/RESULT_01.md、DECISION_LOG L20545付近の2026-10-11 Trial記録(Production採用未承認・試聴待ちの記載まで)。(根拠2)APPROVED_FOR_PRODUCTION・配線進行中は依頼文(Fable)の記載
- 備考: SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)にはJ2/E2採用決定の記録が未反映(grep 0件、HEAD 0db97bae時点)。『FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01』の語もSSOT/委任ログに0件。git worktree上に feature/coffee-new-tone-01(eigo-radio-tone)が存在するが main に対し先行commit 0(WIPのstash参照のみ)=実装commitは未確認。したがってProduction正式仕様としては未配線・SSOT未記録として扱う

#### 7-05 新Tone: Full Story F1.5
- **Status**: `IN_PROGRESS` / scope: FAMILY_X
- 要旨: FAMILY-X-TTS-FULL-STORY-TONE-TRIAL-01(2026-10-11)のF1.5 style=『warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration.』(Aoede、gemini-3.8-flash-lite-tts、通常速度、1回生成、ASR NORMALIZED_MATCH 87/87語、約JPY3)。依頼文: Full Story適用でAPPROVED_FOR_PRODUCTION(2026-10-11、ユーザー決定)、配線進行中
- 根拠: (根拠1)Trial: er053_output/tts_full_story_tone_trial_01/RESULT_01.md、DECISION_LOG L20546(Production採用未承認・ユーザー試聴待ち)。(根拠2)採用・配線進行中は依頼文
- 備考: 7-04と同様にSSOT未反映。現行FULL_STORY=E2『calm, steady news narration…』(F0)。6%減速(4-04)との併用可否・Trial条件(通常速度)との差は配線側で要確認(未確認)

#### 7-06 固定フレーズChampion(10 phrase)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five/point_explanationのChampion(Candidate A/B/C、Charon、gemini-3.8-flash-lite-tts)。welcomeのみ現行Master継続。welcome除く9 phraseはMaster Storeへv3_champion_2026_09_29で登録、Meta run_03でshared_narration 10件全て reused=true・TTS call 0
- 根拠: CURRENT_SPEC『固定フレーズ Champion』【PRODUCTION_WIRED(2026-09-29、Gate3=Meta run_03)】; er043/er047_output; FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 W2
- 備考: 固定phraseはlevel横断のMaster Store対象(11-03)。point_explanation(JA)のstyle=『自然な抑揚をつけて、はっきりと落ち着いた調子で話す』

#### 7-07 音量・ヘッドルーム(RMS正規化+最終段安全弁)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: scalar RMS基準のgain、apply_*_gainでpeak<=0.95、最終段ヘッドルーム安全弁(resample後オーバーシュート対策)
- 根拠: CURRENT_SPEC Audio Assembly節(2026-09-06、ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-PRODUCTION-WIRING-01)

#### 7-08 TTS Batch/Standard同期の実行方式
- **Status**: `UNCONFIRMED` / scope: GOVERNANCE
- 要旨: PM_GOVERNANCE 7-4: Trial/開発=Standard同期、量産Production=Batch前提(別軸管理)。Family X audio runnerの実際の実行方式は本調査で未確認
- 根拠: docs/pm/PM_GOVERNANCE.md 7-4(規則のみ確認)
- 備考: Family X runnerがBatch/同期のどちらを使うかの確認は未実施

#### 7-09 Tone Trial: 旧日本語好評価音源の特定
- **Status**: `RECORD_ONLY` / scope: FAMILY_X
- 要旨: Voice Tone Brightness Trial時点で『旧日本語好評価音源は未特定』と記録(J0=現行との比較は可能、旧音源との比較は不可)
- 根拠: docs/pm/ACTIVE_TASK.md前タスク群(FAMILY-X-TTS-VOICE-TONE-BRIGHTNESS-TRIAL-01)

### 領域8. ASR・読み誤り・再生成・SCG

#### 8-01 日本語ASR Validator+Secondary ASR Cascade
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: Primary=OpenAI gpt-4o-mini-transcribe、AzureはSecondary Cascade(entity-like mismatch時のみ、日本語はPhrase Listなし)。classify_ja_asr_match+evaluate_attempt_ja_with_cascade、CASCADE_CONFIG_JA(max_primary 2/max_secondary 2)。FEATURE_FLAG_JA_PRIMARY_OPENAI=True
- 根拠: er007_ja_asr_validator_01.py/er007_ja_secondary_asr_01.py; CURRENT_SPEC L1945/L1997(ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01、2026-08-25)
- 備考: Family X(Standard日本語segment)が利用する共通Production層

#### 8-02 英語ASR: Secondary ASR Cascade(Azure+Phrase List)・ASR-first Retry
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: 固有名詞ASR不一致は即TTS再生成せず Primary#1→#2→Azure+Phrase List#1→#2→Human Review。CASCADE_CONFIG max_primary 2/max_secondary 2、FEATURE_FLAG_SECONDARY_ASR_ENABLED=True(2026-08-24)
- 根拠: er006_secondary_asr_01.py; CURRENT_SPEC L1996

#### 8-03 English ASR Semantic Equivalence Layer(Tier1数値等価/Tier3規則複数形・固有名詞)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: role gating(5role: Full Story/Comment/Preview/Topic intro/In One Line、Key Phrase/Heading非適用)付きTier1 early-exit(NUMERIC_EQUIVALENCE_MATCH)。Tier3(規則的複数形・固有名詞のみの1トークン差)はSecondary ASR corroboration必須(SECONDARY_ASR_CORROBORATED_MATCH、warning付き)
- 根拠: CURRENT_SPEC L1999(OPEN-186、2026-09-27 APPROVED、PRODUCTION_WIRED); er006_preprod_hardening_01_validation.classify_asr_match; er006_secondary_asr_01.evaluate_attempt_with_cascade_detail
- 備考: role判定はer020 resolve_narrative_roleを再利用

#### 8-04 A2 Reading Resolver(OPEN-111)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: pykakasi辞書候補+限定LLM選択による読み解決。日本語Validator classify_ja_asr_matchへ配線(全文読み一致救済が失敗した場合のみ呼ぶ)。A2(日本語)専用、B1非適用
- 根拠: CURRENT_SPEC L2008; er011_a2_reading_resolver_01.py
- 備考: SCGでは『Resolver不呼出』設計(8-07)

#### 8-05 Pronunciation Ledger(ASR側配線のみ)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: 固有名詞の発音情報(Perplexity)をsurface+entity_typeでcache、Secondary ASR Phrase List(ledger_phrases)へ渡す経路のみProductionへ配線。cache hit時はPerplexity再クエリなし
- 根拠: CURRENT_SPEC L1994; er006_pronunciation_ledger_01.py

#### 8-06 TTS Pronunciation Hint(style/metaへの発音ヒント注入)
- **Status**: `NOT_WIRED_FOUNDATION` / scope: SHARED
- 要旨: augment_style_prefix_with_pronunciation を基盤として保持するがProduction TTS生成呼び出しには未配線(最難関ケースOttoniで確実な改善を実証できず見送り)
- 根拠: CURRENT_SPEC L1995(記述時点の状況)
- 備考: 『配線判断は追加検証』と記載。現在も未配線かは本調査で未再確認(記述日以降の変更は未確認)

#### 8-07 SCG(Secondary Confirm Gate、日本語)
- **Status**: `IN_PROGRESS` / scope: SHARED
- 要旨: Primary(OpenAI)がTRUE_CONTENT_MISMATCH判定の音声に対し、除外条件に該当しない場合のみAzure Secondary ASRを1回(Phrase Listなし、timeout 90s)実行。SecondaryがEXACT_MATCH/NORMALIZED_MATCHならPASS(final_status=SECONDARY_CONFIRMED_PRIMARY_FALSE_NG)、PHONETIC_MATCH含む他は従来どおり再生成へ。除外=数字/否定不一致、全体類似度<0.4、C1固有名詞、C2同形異音語ガード、推奨4否定マーカー、length_ok/Resolver不呼出。TTS attempt上限・fallback・Human Review Lockは無変更(attempt非消費)。FEATURE_FLAG_JA_SCG_ENABLED=True(branch実装値)+環境変数JA_SCG_ENABLED=0で即OFF
- 根拠: git branch feature/scg-ja-secondary-01(worktree eigo-radio-scg、HEAD be936a96、main先行6 commits: c9ca93ee実装→6b054b52 Opus是正→5ed0dc7e runtime evidence a-e 見積2.64円→93c99da8 C2/推奨4『(APPROVED_FOR_PRODUCTION)』)。設計=er053_output/family_x_tts_asr_rootcause_01/OPEN258_DESIGN_01.md、Phase0=er053_output/open258_phase0_trial_01/RESULT_01.md
- 備考: APPROVED_FOR_PRODUCTION(2026-10-11)は依頼文とbranchのコード/commit文言による。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)には未記録(grep 0件)で、OPEN-258行はなお『DESIGN_READY_FOR_REVIEW/Phase 0 VALIDATED_PHASE0』。main未merge。PRODUCTION_WIREDではない。日本語ASR経路専用(英語経路は不変)

#### 8-08 OPEN-258 Phase 0 Trial(V1方式)
- **Status**: `VALIDATED_TRIAL_ONLY` / scope: SHARED
- 要旨: META出演/出現3/3救済、14群=成功7/失敗6/既存除外1、誤PASS 0/5(C群)、Azure 25回約4.0円(上限5円内)。Status案=VALIDATED_PHASE0(条件付き)。Phase 1=SCG(8-07)へ進行
- 根拠: er053_output/open258_phase0_trial_01/RESULT_01.md; DECISION_LOG/OPEN_ITEMS OPEN-258
- 備考: Trial成功のみ。要試聴5音声等の未決はOPEN-258行参照

#### 8-09 TTS retry: 10分cool-down+Local Rewrite+Natural English QA
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: 既存TTS最大3回(attempt1即時→attempt2即時→attempt3直前に固定600秒cool-down)で全NG→Human Review Lock前に、問題span周辺のみをLocal Rewrite(7 Gate: 意味保持/role保持/Fact非矛盾/前後文脈/Natural English/局所性/非全文)→全PASS候補のみ再TTS 1回→ASR PASSなら RESOLVED_BY_LOCAL_REWRITE。Connected Speechは5 role(Full Story/Comment/Preview/Topic intro/In One Line)のみ。英語TTS role専用(日本語経路は未対応)。生成モデル=b1s.MODEL=vfl01.MODEL=routing.WRITER_MODEL(gpt-6-luna)
- 根拠: er020_tts_retry_local_rewrite_01.py; CURRENT_SPEC L1971(2026-09-26 APPROVED→PRODUCTION_WIRED); connected_speech_enabled_for(segment_id)
- 備考: CURRENT_SPEC L1971本文は『gpt-5.6-luna』と記載(旧)。現行コードの参照先はWRITER_MODEL=gpt-6-luna(routing)

#### 8-10 Local Rewrite 全文性検証(位置非依存、OPEN-256)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: 旧『先頭15文字一致』を位置非依存の全文性検証(文字数比0.7〜1.5・真部分文字列拒否・先頭引用符/ラベル拒否・終端一致・保持率>=0.6・数値保持・span整合)へ置換。実記録90件replayで救済13/14、META comment_2の3件が全7 Gate通過。runtime evidence取得済
- 根拠: er020_tts_retry_local_rewrite_01.py(FULL_SEGMENT_*定数/diagnose_candidate_full_segment); OPEN-256 CLOSED(PRODUCTION_WIRED 2026-10-11、Fable Gate判定+ユーザーCloseout受入); er053_output/family_x_tts_asr_rootcause_01/OPEN256_*
- 備考: 範囲=英語TTS role。OPEN-259(極短segmentの字数比0.7緩和)・OPEN-260(日本語経路未対応、Gate7 ASCII語計数)は未承認候補(8-12)

#### 8-11 Human Review Route(未解決ASR不確実性の送り先)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: Cascadeを尽くしても未解決の場合、API再試行を重ねずHuman Review queue(human_review_queue.jsonl)へ。canonical/audio/発音メタデータ/Primary・Secondary transcripts/判定理由を保持。Human Review Lock(PRODUCTION_MAX_TTS_ATTEMPTS=3)
- 根拠: CURRENT_SPEC L2000; er011_human_review_lock_01.py; er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl

#### 8-12 未承認候補: OPEN-257/259/260
- **Status**: `OPEN_UNAPPROVED` / scope: SHARED
- 要旨: OPEN-257=音韻衝突型固有名詞TTS/ASR失敗(包括対策未承認、Trial先行提案)/OPEN-259=極短segmentのLocal Rewrite字数比誤拒否(緩和方向、要ユーザー判断)/OPEN-260=Local Rewrite日本語経路未対応(Gate7が純日本語を常に不合格)
- 根拠: OPEN_ITEMS OPEN-257/259/260(2026-10-11)
- 備考: いずれも仕様未承認・未実装

### 領域9. Validator・品質Gate・Review Queue

#### 9-01 Risk Flagger 4条件(non-blocking)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: gpt-6-luna A3/A4+gemini-3.5-flash-lite A3/A4を逐次実行。Luna=Responses API effort medium、Gemini=REST generateContent(thinking込みoutput)。両Level(Advanced=b1b/Standard=a2)の完成英文×完全Ledgerへ。いずれか1条件のFlagで候補(OR統合)、同一文は1 issueに統合(detected_by[]保持)。splitter=er053_en_sentence_splitter_01(en_split_v1)
- 根拠: er053_risk_flagger_production_01.py; CURRENT_SPEC『Risk Flagger(RF)』【PRODUCTION_WIRED(2026-10-11ユーザー正式完了承認)】; routing FAMILY_X_RF_LUNA/FAMILY_X_RF_GEMINI; 設計=docs/pm/design/2026-10-10_RISK-FLAGGER-PRODUCTION-WIRING-01_DESIGN_01〜03.md
- 備考: A3_SYSTEM_SHA256=9d995042…/A4_SYSTEM_SHA256=c87b95e5…(import時assert、Trial antenna_promptsとbyte-identical)。ChatGPT Pre評価・Pre-sorterはrunner未組込

#### 9-02 RFの非Blocking契約・例外・状態
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: 記事を書き換えない(開始/終了shaで検証、不一致=ArticleModifiedError)、自動Rewrite/自動retry(RF結果起点)/自動削除なし。API技術retryのみ(transient 2回・format 1回)。伝播する例外は BudgetCheckStop と ArticleModifiedError の2種のみ。それ以外(ledger_incomplete・文0件・model contract違反・pricing_not_found・全条件API失敗)は status=RF_UNAVAILABLE で記録して次工程へ。一部失敗=PARTIAL、全成功=OK
- 根拠: er053_risk_flagger_production_01.py; runner.run_post_en_risk_flag L274-; CURRENT_SPEC『RF』
- 備考: RF_UNAVAILABLE/PARTIAL・記号QA再実行・U-1 STOPのProduction実発火は未観測(stub E2E/unit testのみ、CURRENT_SPEC記載)。Gemini A4が0件でも停止・削除しない(経過観察)

#### 9-03 Review Queue(post_en)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: review_queue/post_en/<slug>__<run>/<level>__<rf_run_id>/{queue.json,queue.md,inputs/,raw/}+追記専用index.jsonl(schema_version=review_queue_post_en_v1)。review_stateは持たない(判定状態はHuman Review側)。Queue保存失敗時はout_dir配下risk_flagger_fallback/+WARN
- 根拠: er053_review_queue_01.py; review_queue/post_en/README.md; CURRENT_SPEC『Review Queue』【PRODUCTION_WIRED(2026-10-11)】
- 備考: commit/push運用責務は未解決=OPEN-245(runnerはgitを触らない)

#### 9-04 TTS前3者照合guard(ensure_rf_record)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: scaffold時sha256==TTS時source記事sha256==Queue記録sha256を照合。一致ならRF再実行なし(audit/rf_tts_guard.json)、不一致/Queueなしならその場でRF実行・Queue保存(非Blocking)
- 根拠: er019_family_x_audio_production_runner_01.py(ensure_rf_record); er053_c3_audio_guard_test_01.py; L3 run_l3_01でmatch/verified確認
- 備考: 観測専用警告a2_derived_from_advanced_sha_mismatch はCRLF正規化差による常時偽陽性(挙動影響なし)=OPEN-253

#### 9-05 旧Fact Checker/Ledger Deviation/must-fix/JA差し戻し(案B)の撤去
- **Status**: `SUPERSEDED_REMOVED` / scope: FAMILY_X
- 要旨: Family X Production正式経路(初回path+retry/fallback/regeneration/resume)から2026-10-10撤去済。OPEN-233 Self-Recovery系はProduction未配線のままSUPERSEDED(OPEN-244)。OPEN-235/236(Checker内部の潜在不具合)も当該Checker系
- 根拠: CURRENT_SPEC『旧Fact Checker撤去』; RISK-FLAGGER-PRODUCTION-WIRING-01_08.md R-01〜R-28; er053_dangling_reference_check_01(Dangling Check: Fact Checker専用シンボル0)
- 備考: OPEN-235/236/238の現在状況(Closeしたか)は行頭Statusだけでは未確認

#### 9-06 技術QA(旧Fact Checkerとは別、維持)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: ASR/発音QA、clipping/headroom、KP source gate、disfluency QA、repetition QA、segment構造検証、required structure validation、TTS technical retry、音声化禁止記号QA、段落3分割retry
- 根拠: CURRENT_SPEC『技術QAは維持』; er019_family_x_audio_production_runner_01(repetition QAはFull Story系body segmentで有効、enable_repetition_qa)
- 備考: 『安全≠成功』: 技術QA PASSは記事品質承認ではない(PM_GOVERNANCE)

#### 9-07 Audio Validation Gate(episode音声検証)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: assemble段で asm.verify_episode_audio_validation_gate を呼ぶ(KP解説=kp{rank}_explanation等を検証対象に含む)。完成episode構造・segment・音声整合を検証
- 根拠: er019_family_x_audio_production_runner_01.py L1060-1102; CURRENT_SPEC『Audio Validation Gate』言及
- 備考: 判定基準の詳細条件は本書では未転記

#### 9-08 PM運用Gate 1〜7・Closeout Mandatory Check(PM層ルール)
- **Status**: `OPERATIONAL_RULE` / scope: GOVERNANCE
- 要旨: Gate 1〜7、Closeout Mandatory Check、1記事ずつ完結原則、安全≠成功原則。Production仕様ではなくPM運用ルール
- 根拠: docs/pm/PM_GOVERNANCE.md(2-1/2-3/9-7/11/14/21/22節等)

#### 9-09 全回帰suite既存36 failed OPEN-252
- **Status**: `OPEN_UNAPPROVED` / scope: FAMILY_X
- 要旨: merge前から存在する36 failed(新規0)。対応要否はユーザー判断。SOL61後は『全suite 36 failed+収集error 1(既存37件の集合と同一・新規0)』と記載
- 根拠: OPEN_ITEMS OPEN-252; DECISION_LOG 2026-10-11 SOL61 Closeout
- 備考: 配線起因ではない

### 領域10. retry・fallback・regeneration・resume

#### 10-01 TTS attempt上限(Production=3)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: PRODUCTION_MAX_TTS_ATTEMPTS=3(標準経路2回+minimal instruction fallback 1回、assert固定)。Human Review Lock手前。SCG(8-07)はattemptを消費しない設計
- 根拠: er011_human_review_lock_01.py L80-104; CURRENT_SPEC L1971

#### 10-02 fallback(minimal instruction / EN fallback style)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: 標準経路不合格後に最小限instructionへ(Family X EN fallback style=『natural, clear, conversational』、FAMILY_X_ROLE_STYLE_EN_FALLBACK[0])。JA(J3)は長文JAPANESE_STYLE_PREFIXを置換するがfallback(minimal instruction)経路は不変
- 根拠: er033_tts_flash_lite_family_x_styles_01.py L56-61; CURRENT_SPEC『可変segment Role Style』
- 備考: 『fallback voice(voice切替fallback)』の仕様・実装は本調査で確認できず=未確認

#### 10-03 Local Rewrite(retry系の最終段)
- **Status**: `RECORD_ONLY` / scope: SHARED
- 要旨: 8-09/8-10参照。重複掲載を避け、本領域では参照のみ
- 根拠: 8-09, 8-10

#### 10-04 regenerate-stage(runner別)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: entertainment runner: --regenerate-stage storyline_b3|writer|advanced|standard、--stage research/ledger/…/all、--stop-after。audio runner: --stage plan/scaffold/tts/assemble/player、--level a2|b1b|both。regeneration/resume全分岐でproducer呼出+U-1検証
- 根拠: runner build_arg_parser(er019_family_x_entertainment_production_runner_01.py L350-); er019_family_x_audio_production_runner_01.py L1785-

#### 10-05 resume(既存成果物の再利用)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: 既存Ledger/Selected Fact Brief/revision2.md(U-1満たす場合)があれば再利用。Mandatory STOP: entertainment runnerはStandard+RFまでで停止し、ユーザー確認前にaudioへ進まない
- 根拠: runner main()(L371-470); CURRENT_SPEC『Mandatory STOP』
- 備考: audio側の旧記事TTS再生成にU-1相当確認なし=OPEN-250(現状安全側)

#### 10-06 PASS済み成果物の不要再実行・上書き禁止
- **Status**: `OPERATIONAL_RULE` / scope: GOVERNANCE
- 要旨: PM_GOVERNANCE 14-6(2026-10-11ユーザー決定③): PASS済み成果物を理由なく再実行・上書きしない/追加実行前に既存Statusと必要性確認/再実行時は対象・目的・影響を事前明示(可能なら別dir)/完成済み成果物の再利用を優先。新機構は実装しない運用ルール
- 根拠: docs/pm/PM_GOVERNANCE.md 14-6; FAMILY-X-TTS-ASR-ROOTCAUSE-01 委任_25(事例=META b1b comment_2のUNCERTAIN上書き)
- 備考: コード上の自動ガードは未実装(運用ルール)

#### 10-07 retry上限一覧(個別)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: KP: Strategy L max_attempts=2/KP Minimal 2/English Lock 2; 記号QA: R0 1回・R2 1回; 段落3分割must-fix 1回; RF API技術retry: transient 2・format 1; Local Rewrite再TTS 1回; ASR Cascade: primary 2/secondary 2
- 根拠: 各module(er003_key_words_production/er003_v1_repro01_main_generate/er053_family_x_factlock_ja_writer_01/er012_e/er053_risk_flagger_production_01/er020/er006_secondary_asr_01)

#### 10-08 segmentのretry_count累計表示不整合 OPEN-254
- **Status**: `OPEN_UNAPPROVED` / scope: FAMILY_X
- 要旨: retry_count/call_countが最終attempt分のみで、ASR起因再生成を含む累計と不整合(正は cumulative_tts_attempts)
- 根拠: OPEN_ITEMS OPEN-254(2026-10-11)
- 備考: 集計は cumulative_tts_attempts を正とする注記が暫定対応候補

### 領域11. 音声Assembly・Master Store・試聴ページ

#### 11-01 音声runner(plan→scaffold→tts→assemble→player)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: er019_family_x_audio_production_runner_01.py。既存Production低レベル関数を呼ぶのみ。a2(Standard)/b1b(Advanced)両Level。assembled wav+player.html生成。Mandatory STOP後に別実行
- 根拠: CURRENT_SPEC『Family X音声構造』(NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01、Gate3=Meta run_03); L3 run_l3_01(a2 21・b1b 25 segment全OK)

#### 11-02 Master Audio Store(固定phrase・KP phrase reuse)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: er006_master_audio_store_01.get_or_generate/register_precomputed。manifest.json+reuse_telemetry.jsonl。固定phraseはStore対象、可変segment(Comment/Preview/Full Story等)は対象外(設計書§2(d))。Advanced KP最終英語Phraseはreuse
- 根拠: er006_master_audio_store_01.py; CURRENT_SPEC Champion節; er006_output/master_audio_store_01/manifest.json
- 備考: level横断の共有基盤

#### 11-03 試聴・配布経路(GitHub Pages user_test)
- **Status**: `OPERATIONAL_RULE` / scope: GOVERNANCE
- 要旨: 正式配布=GitHub Pages(https://shimomura055.github.io/eigo-radio/user_test/…、Landing=articles_2026_0918.html、個別=unified.html?src=…)。blob/raw.githubusercontent/githack/file:///はユーザー向け標準経路として使用禁止。再生ボタン+script同一行等の標準playerフォーマット(audio_review_player.py共通module)
- 根拠: docs/pm/PM_GOVERNANCE.md 9-5/配布経路(PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01、2026-09-18); CURRENT_SPEC L2489-2519(unified.html表示仕様)
- 備考: Family X Trialの試聴ページ例: user_test/tts_voice_tone_brightness_01/、tts_full_story_tone_01/

#### 11-04 Gate 7(音声artifact受入チェックリスト (a)〜(n))
- **Status**: `OPERATIONAL_RULE` / scope: GOVERNANCE
- 要旨: (a)完成episode音声〜(l)再生ボタン+script同一行、(m)file:///禁止・到達確認、(n)ユーザー試聴ページ表示フォーマット(2026-09-17)。判断依頼時は試聴・reviewリンクを同一報告内に提示
- 根拠: docs/pm/PM_GOVERNANCE.md Gate 7補足(L248-330)
- 備考: (b)〜(k)の個別項目は本書では未転記(正本参照)

#### 11-05 META完成音声の公開判断
- **Status**: `RECORD_ONLY` / scope: FAMILY_X
- 要旨: 『Wiring完了≠記事品質承認』。META音声の完成・公開判断は保留(OPEN-255 Close後も、OKマスター=記事品質の承認のみで音声は別)
- 根拠: CURRENT_SPEC L1157; OPEN_ITEMS OPEN-255

### 領域12. コスト・runtime管理・運用ルール

#### 12-01 pricing_snapshot.json(単価台帳、fail-closed)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: er005_output/cost_baseline_01/pricing_snapshot.json。gemini-3.5-flash-lite(in 0.30/cached 0.03/out 2.50、thinking込み)、gpt-6.1-sol(in 2.00/cached 0.10/out 10.00 USD per 1M)等を登録。RFは最初のAPI前に単価検証、未登録=RF_UNAVAILABLE(pricing_not_found)でAPI 0回
- 根拠: CURRENT_SPEC『単価登録・費用機構』; er053_risk_flagger_production_01

#### 12-02 er009 PRICING_USD_PER_M表
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: er009_n1_routing_governance_10_actual_model_cost.PRICING_USD_PER_M へ gpt-6-luna=(0.10,0.01,0.50)追加(OPEN-251、8ba79fdc)、gpt-6.1-solはpricing_snapshot値を転記。未知modelはfail-closed(UnknownModelPricingError)。gpt-6-astraはW-1専用の別集計経路(Production予算ガード係数1.0、OPEN-246)
- 根拠: CURRENT_SPEC『単価登録・費用機構』; OPEN-251 CLOSED

#### 12-03 予算ガード(assert_budget_ok/BudgetCheckStop)
- **Status**: `PRODUCTION_WIRED` / scope: SHARED
- 要旨: 各stage後に efam.assert_budget_ok(--budget-jpy 既定150)。RFの予算超過はBudgetCheckStopとして伝播(非Blocking RFでも握りつぶさない)。web_search課金も計上(OPEN-242)。audio runnerのcompute_cost_jpy_so_farはStopIterationを握りつぶさずPricingNotFoundErrorへ(fail-closed)
- 根拠: er012_e_..._01.assert_budget_ok/compute_cost_jpy_so_far; runner main(); OPEN-242 PRODUCTION_WIRED(2026-10-08)
- 備考: 予算Capは暴走防止Guardrailであり、Cap到達だけを理由とした自動STOPはしない(PM_GOVERNANCE 7-6)

#### 12-04 cost.json(stage別・provider別・RF Level別)
- **Status**: `PRODUCTION_WIRED` / scope: FAMILY_X
- 要旨: compute_stage_cost_breakdown_multi(er053_cost_aggregate_01.py)でRF Geminiを含む集計。by_provider_jpy、RF Level別内訳。entertainment runnerが_write_cost_jsonで出力
- 根拠: er053_cost_aggregate_01.py; runner _write_cost_json

#### 12-05 1記事セット費用(E案)見積
- **Status**: `RECORD_ONLY` / scope: FAMILY_X
- 要旨: 1記事セット=Standard(A2)+Advanced(B1B)。E案の見積(COST_PER_ARTICLE_SET_E_VS_A_01.md): (1)通常・retryなし: (a)Ledger再利用37.9円/(b)Research込み(coffee実測)84.8円/(c)Research込み(過去10 run中央値)63.5円。(2)現実的平均(retry期待値込み): (a)41.5円/(b)88.4円/(c)67.1円。依頼文の『≈63.5円』=(1)の(c)に一致。META runtime実測(B3〜R2のみ)=18.499円(別範囲)
- 根拠: er052_output/ja_article_quality_model_allocation_trial_01/COST_PER_ARTICLE_SET_E_VS_A_01.md/.json(commit ffbb7a7f); er053_output/sol61_production_wiring_01/runtime_evidence_01.md
- 備考: 推定を含む見積(音声のretryなし値12.77円は推定、Azure/Perplexity費用は未計測=0円計上、Research費はテーマ依存12.97〜56.82円)。PM_BRIEFの方針により、この表の値は『確認済みの実測』ではなく『出典付き見積』として扱う。SSOT(CURRENT_SPEC/DECISION_LOG)へのE案1セット費用の記載は未確認

#### 12-06 運用: ACTIVE_TASK/RESULT_PACKET/委任ログ・委任文標準
- **Status**: `OPERATIONAL_RULE` / scope: GOVERNANCE
- 要旨: ACTIVE_TASK.md/RESULT_PACKET.mdは一時ファイル(非SSOT)。委任ログ=docs/pm/delegation_log/。委任文標準D-2(check_delegation_prompt.py)は2026-09-13 PRODUCTION_WIRED。報告単位管理(12節)・6項目報告(9-13)・REPORT_LEDGER
- 根拠: CLAUDE.md; docs/pm/PM_BRIEF.md; docs/pm/PM_GOVERNANCE.md 9-13/11-D-2/12

#### 12-07 最新モデル原則(開発・評価用途)
- **Status**: `OPERATIONAL_RULE` / scope: GOVERNANCE
- 要旨: 検証・比較・方式評価では原則最新世代の最上位/推奨系モデル、旧/下位は例外理由を実行前に明記、報告に使用モデル名/最新か/理由。本番ライン選定は別判断
- 根拠: docs/pm/PM_GOVERNANCE.md 25(2026-10-09ユーザー正式採用、PM-DEV-EVAL-LATEST-MODEL-RULE-01)

#### 12-08 Git自律処理方針
- **Status**: `OPERATIONAL_RULE` / scope: GOVERNANCE
- 要旨: 同種Git作業(退避・復元・同期・非破壊的競合解消)は、内容保全でき仕様/Production挙動に影響しないと確認できる場合は自律処理。git add -A/-f/amend/rebase/force push/stash/clean/reset --hardは解禁しない
- 根拠: docs/pm/PM_GOVERNANCE.md 10-X(2026-10-11ユーザー決定、commit 5e5b32a3)

#### 12-09 開発時間最小化・並列実行原則/Opus独立レビューGate/Existing Spec Check Gate
- **Status**: `OPERATIONAL_RULE` / scope: GOVERNANCE
- 要旨: 独立作業は原則並列化(8-X)、Opus条件A〜D(11-3)、新仕様提案前のA/B/C分類(21)、ユーザー指示優先・Trial前後チェック(22)、重大誤解原則(23)
- 根拠: docs/pm/PM_GOVERNANCE.md 8/11-3/21/22/23; CLAUDE.md

#### 12-10 コスト報告ルール(15)・予算Cap・TTS実行方式別管理
- **Status**: `OPERATIONAL_RULE` / scope: GOVERNANCE
- 要旨: 1記事一式の総コスト報告(15-1〜15-8、Production 1生成セット総原価=15-8主指標)、予算Cap=Guardrail(7-6)、TTS Standard/Batch別軸(7-4)
- 根拠: docs/pm/PM_GOVERNANCE.md 7-4/7-6/15

#### 12-11 ASTRA請求照合 OPEN-246 / 費用機構周辺OPEN
- **Status**: `OPEN_UNAPPROVED` / scope: FAMILY_X
- 要旨: gpt-6-astra単価は登録済だが請求ダッシュボードとの照合未実施(Production予算ガードは係数1.0)
- 根拠: OPEN_ITEMS OPEN-246
- 備考: E案でR1/R2はSolへ移行済。Astra経路が現行Productionで使われているか(残存呼出し)は本調査で未確認

## 7. 調査方法・限界

- 照合順: PM_BRIEF → CURRENT_SPEC(Family X節群・Key Phrase・固定phrase・ASR/retry表)→ DECISION_LOG(末尾2026-10-07〜10-11)→ OPEN_ITEMS(OPEN-233〜262)→ 設計書(RISK-FLAGGER DESIGN_01〜03、design_family_x_refresh_e2e_production_wiring_01、design_kp_*)→ コード(er019_family_x_*、er053_*、er033_*、er020_*、er007_ja_*、er006_*、er011_human_review_lock_01)。
- git branch/worktree(feature/scg-ja-secondary-01、feature/coffee-new-tone-01)は`git log main..<branch>`等のread-onlyコマンドのみで確認し、checkout・merge・編集はしていない。
- DECISION_LOG/CURRENT_SPECの古い節には旧仕様(旧Fact Checker・Family A/B/C向け記述・旧モデル名)が履歴として残る。本書では現行/撤去済みを分けて記載したが、全節の網羅再照合までは行っていない(確認できなかった範囲は§5)。
- 数値(費用・sha・件数)はSSOT/コード/証跡の記載値を転記しており、本調査での再計算・再実行はない。費用見積はCOST_PER_ARTICLE_SET_E_VS_A_01.mdの推定を含む値(12-05)。
