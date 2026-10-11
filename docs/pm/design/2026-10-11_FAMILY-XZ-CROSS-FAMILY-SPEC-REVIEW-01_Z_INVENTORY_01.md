# Family Z(Fiction)現行仕様一覧(横展開検討用)

管理ID: FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01 委任_02 / Phase 1-Z / 2026-10-11
性質: read-only調査。コード・Prompt・SSOT変更なし、API費用 ¥0。判断はしない(事実整理のみ)。
情報源: CURRENT_SPEC.md(Family Z節 L1373-1521、Family体系節 L1523-、共通Core節)、DECISION_LOG.md、OPEN_ITEMS.md(OPEN-185/202/211/241)、docs/pm/REPORT_LEDGER.md、
docs/pm/recon_family_z_production_e2e_01.md、docs/pm/design_family_z_melos_production_e2e_and_latest_spec_wiring_01.md(Phase A設計、commit 55cb58ed)、
er026_family_z_fiction_production_runner_01.py(824行)、er026_output/、FICTION-*_REPORT.md、KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01_REPORT.md。

注意: CURRENT_SPECのFamily Z節は2026-09-26/27時点で止まっており、2026-09-28以降に共通仕様(Flash-Lite TTS、J3/E2 Role Style、4+1 Key Phrase、gpt-6-luna routing等)が更新されている。Z側へのこれらの適用は、Phase A設計書上の判定のみ存在し、実装は無い。

## 0. 位置づけ(非エンジニア向け1段落)

Family Zは「Fiction(物語)」専用の番組Familyで、青空文庫などのパブリックドメイン文学、実話(Real Story)、歴史的犯罪実話(Historical True Crime)を、元作品をなるべく変えずに短く(約280-420語)して英語で聞く体験を提供する。ニュース系のFamily Xが「最新ニュースを調べて記事を書く」のに対し、Zは「権利確認済みの原作を一次資料として確認し、尺に収めるための圧縮だけ行う」外部Seed方式で、AI完全自由創作は標準方式にしない。Active Production FamilyはX/Y/Z(開発中心はXとZ、Yは未着手)、Legacy/BackupはA/B/C(最新仕様へ追従しない)。現状Zは「走れメロス」1本についてtext工程(本文確定・Preview・Comment1・In One Line・Key Phrase)までのProduction runnerが実装されたところで止まっており、TTS・Assembly・試聴ページは未実装。PRODUCTION_WIREDではない。

## 1. Status

- Family Z仕様(定義/Story方針/Seed必須条件/人名ルール/story_type/TTS適用/PRODUCTION_WIRED条件、Z-1権利Gate、Z-2 runner方針、Z-3 In One Line、Z-4 Dialogue Voice): `APPROVED_FOR_PRODUCTION`(2026-09-26ユーザー決定、OPEN-185)。
- Family Z Production wiring: text工程のみ実装(commit 42b43772、Phase 1、約¥26.28)。TTS/Assemblyは`NotImplementedError`スタブ。`PRODUCTION_WIRED`ではない。
- Phase A設計(最新X仕様のZ横展開設計): commit 55cb58ed。設計のみ。Phase B/C(実装)のcommitはgit logに存在しない。DECISION_LOG/OPEN_ITEMSにこの管理IDのエントリは無い(grep確認)。
- er018 Fiction Trial群はすべてTrial/VALIDATED止まり(仕様ではない)。

## 2. 現行Production仕様の全体フロー(テキスト図)

```
[Seed選定(Trial、手動)] 外部Seed。一次資料確認+日本国内PD(必須)。rights_block、check_rights_gate()でfail-closed
 -> er018 Trial生成物(seed.json/story.md)を読込  ※Production Writerは存在しない。Melosは er018_output/.../03_japanese_lit_2 のTrial story.mdが入力
 -> resolve_canonical_text(): タイトル除去・語数受入(280-420)・外国人名ルール確認/復元(canonical text、sha256記録)
 -> build_segment_plan(): Family C build_flat_voice_chunks()/classify_quote_voice_window()でnarrator/dialogue境界分割(Melos=8 voice-clip story_001..008)
 -> build_story_type_metadata(): literature=UI/音声冒頭なし、real_story/true_crime=固定intro+UIラベル
 -> Preview(JA、Z所有prompt) -> Comment1(Family C generate_family_c_a2_comment(1)呼出) -> In One Line(EN、Z所有prompt)
 -> Key Phrase: scaffold.run_key_phrases(...,"A2")(Strategy L経路、DB Hybridではない)
 ==== ここまで実装済み(er026_output/family_z_production_e2e_01/melos/run_01、LLM実測 約¥0.46) ====
 -> [未実装] stage_tts(): 既承認TTS(attempt1->即時2->10分cool-down->3->Local Rewrite+Natural English QA、Connected Speech 5 role)、TTS記号正規化、読み解決
 -> [未実装] stage_assemble(): 共有er003_v1_n3_01_assemble.py想定
 -> [未実装] Audio Validation / Master Store reuse / 試聴ページ
```

## 3. 12領域の整理(Zの現行仕様/Status/実装/Xとの共通性/意図的差異/OPEN)

### 1 Research・Fact Ledger
- Z: Research/Fact Ledgerは無い。Seed方式(権利確認済み原文)。Fact Checkは「article.mdが承認済みのためDeviation Check不要」(Phase A §5)。「検索要約だけをSeedにしない」「他の要約からFactを継ぎ足さない」(F-4 4条件)。
- Status: 仕様APPROVED / 実装=rights gateのみ(`check_rights_gate`, `MELOS_RIGHTS_BLOCK`、er026)。
- 共通: なし(Risk FlaggerのZ適用有無は未確認)。差異: 意図的(外部Seed方式、CURRENT_SPEC Family Z 1/3)。
- OPEN: Seed選定プロセスのProduction化(誰が/どう選ぶか)は仕様記述なし=未整備。

### 2 Fact選択・Storyline
- Z: 無し。許容編集=脇筋削除・人物整理・背景/心理描写圧縮・重複場面削除のみ(Story内容方針2)。Story品質基準4項目中3以上。
- Status: 方針APPROVED / 実装なし(Melosは既存Trial story.mdを受入判定+人名復元するだけ)。
- 共通: なし。差異: 意図的(原作忠実)。OPEN: 圧縮Writer未実装(領域3)。

### 3 日本語記事生成(Writer・モデル・Prompt)
- Z: 日本語Writerは無い(本文は英語Story、日本語はPreview/Comment/タイトルのみ)。Story本文のProduction Writerは未実装(Seedからの圧縮生成はTrial er018_*で実施、Production化されていない)。Preview/In One Line prompt=er026内Z所有定数(`_FAMILY_Z_PREVIEW_ROLE_JA`, `_FAMILY_Z_IN_ONE_LINE_ROLE_EN`)。Comment1=er013(Family C)の`generate_family_c_a2_comment`呼出。
- モデル: `routing.require_model_or_override("A2_WRITER", routing.WRITER_MODEL)`でrouting参照(commit 756ed882でgpt-6-luna化、OPEN-241 PRODUCTION_WIRED)。
- Status: Preview/Comment1/In One Line=実装済み(Phase 1、run_01実測あり)。Writer=未実装。
- 共通: routing(er006)。差異: Comment1がFamily C(legacy)read-only再利用=意図的(Z-2 APPROVED)。
- OPEN: CURRENT_SPEC L2126「Family Z Writer実装時はTTS記号正規化(Prompt予防+Normalizer+Gate)必須」(Writer未着手のため未達)。

### 4 英語化・難易度
- Z: 英語化工程なし(Seed要件: 現代の第三者英訳は別著作物で流用不可、自前生成)。レベルはA2(Standard)のみ、B1B(Advanced)は存在しない。
- Status: A2のみ。Advanced Key Phrase英語解説(2026-09-28承認)はB1B限定のためZ対象外(Phase A §3g)。
- 共通: なし。差異: 意図的か否か=決定記録は未確認。OPEN: 難易度(A2/B1B)方針の明示決定は未確認。

### 5 記事構造・Comment・Preview・In One Line
- Z: Preview(JA)・Comment1(JA)・In One Line(EN)実装済み。Topic introはID定義のみ(`FIXED_SEGMENT_IDS`)、生成未実装。Comment2-4未実装。
- Phase A設計(未承認・未実装): 3分割(body1=story_001-006/115語、body2=story_007/133語、body3=story_008/135語、境界(6,7))+Comment1-4(Comment4はZ所有新prompt)でXの構造に揃える案。Dialogue境界を跨がない。
- story_type: literature=UI表示/音声冒頭なし、real_story="This is a true story."、true_crime="This is a true crime story."(`build_story_type_metadata`、実装済み)。
- 共通: Xの3分割・Comment4本構成への整合は設計案のみ。差異: 1 body=複数voice-clip連結(Z-4 Dialogue Voice由来)。見出し読み上げ無し(案)の決定記録は未確認。
- OPEN: 3分割+Comment4構造の採用承認は未取得。

### 6 Key Phrases・解説
- Z: `scaffold.run_key_phrases(article, dir, id, "A2")`(Strategy L)。run_01は4+1導入前schemaで非互換。4+1構成の別artifact `er035_output/kp_4plus1_evidence_01/melos_a2/`はPASS済み(important4+topic1)。
- DB Hybrid(X Primary)はZ未適用: `family_profile="family_z"`は`NotImplementedError`(er030)。Z適用Trial(KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01)はMelos1記事で「不十分」、Core2ギャップはTrial-05(Core v2)で修正されたがZ採用は未決定。
- Status: Source Reference Contract(候補ID方式)は「X/Z共通Core contract」としてAPPROVED(2026-09-28)、Z runnerは未配線。4+1=APPROVED、Z runner統合は未実装。
- 共通: Strategy L(共有scaffold)、Source Reference Contract仕様。差異: DB Hybrid非採用は「未決定」で、意図的差異と決めた記録は未確認。
- OPEN: OPEN-202(会話タグfalse positive、Z拡大時に一般化修正の要否再判断)、OPEN-211(Strategy L経路はrunner_up候補無し)。

### 7 音声Voice・Style・TTS・速度
- Z: 既承認TTS仕様をそのまま使用(項目6)。Dialogue Voice(Z-4): narrator=Aoede、dialogue=Erinome/Charon等、`classify_quote_voice_window()`(er013 L66-95)再利用。Melos plan: narrator=Aoede/selinuntius=Erinome/dionysius=Charon。
- Status: 仕様APPROVED / 実装=plan only(TTS未実行、`stage_tts`スタブ)。
- 共通: er003/er020のTTS retry・Local Rewrite・Connected Speech(5 role)・TTS記号正規化(PRODUCTION_WIRED)。差異: Dialogue Voice=意図的(Z-4)。
- 未実装/未決: J3(JA Role Style)・E2(EN Role Style)・Flash-Lite `speech_metadata` backendのZ適用は設計案のみ(Preview/Comment=J3、Full Story/In One Line=E2、ただしresolver拡張が前提。backend既定未決)。
- OPEN: `resolve_narrative_role()`はfull_story_part1/2/3の完全一致のみで、Zの8 voice-clipはConnected Speech対象外(known_gap)。正規表現追加案は未承認・未実装。Melosの音声style/速度のZ固有決定は未確認。

### 8 ASR・読み誤り・再生成・Secondary
- Z: 既承認TTS仕様に内包。pronunciation resolver(`source_context="family_z_melos"`、work_canon seed=太宰原作表記、Web lookup無し)はer025に実装済み・実測記録あり。Gemini TTSへの反映は別Phase課題として記録。
- Status: resolver=APPROVED/共有。Z TTS stage未実装のため実配線は未。EN ASR意味等価性・Secondary ASRのZ適用は未確認。
- 共通: er025/er006/er021/er003。差異: 無し。OPEN: Melos人物名読みのTTS反映。

### 9 Validator・品質Gate・Review
- Z: story_type、外国人名ルール(`check_character_name_rule`)、語数受入(`check_word_count`)、rights gate(fail-closed)、segment再構成一致チェック、Key Phrase redundancy QA。Z専用pytest 19件(er026_family_z_fiction_production_runner_01_test.py)。
- Status: 実装済み(text工程)。Risk Flagger/B3 annotation(er053)のZ適用は未確認。
- 共通: Key Phrase Gate(er003_key_words_*)。差異: 外国人名ルールはFiction共通=Z独自(意図的、F-3)。
- OPEN: Opus L2は実装後1回の予定(Phase A§6)、未実施。

### 10 retry・fallback・regeneration・resume
- Z: Preview/In One Lineはmax_attempts=2。TTS側retryは共有(er020)。runnerのresume機構は未確認。
- Status: LLM retry実装済み、TTS retry/regenは未配線。共通: er020 Local Rewrite・Gate。
- OPEN: Local Rewrite時のVoice assignment保持はruntime evidence未取得(Phase A「確認要」)。

### 11 Assembly・Master Store・試聴ページ
- Z: `stage_assemble`は`NotImplementedError`。設計案: 共有`er003_v1_n3_01_assemble.py`、順序 Comment1->body1(6 clip)->Comment2->body2->Comment3->body3->Comment4->In One Line。固定phrase(welcome/preview_intro/key_phrases_intro/full_story_intro/num_*)は汎用Master Storeでlookup(Family固有登録不要)。num_three/num_fiveはCURRENT_SPECで「未確定」(委任文はB take1)で食い違い、実装時に再照合要。
- Status: 未実装。試聴ページ生成経路は未確認。共通: Master Store・assembler・player。

### 12 コスト・runtime・運用
- Z: runner予算Cap ¥200/WARN ¥150(er026)。Phase 1実費約¥26.28(OPEN-185追記)。run_01 text LLM実測 ¥0.46(cost.json)。Phase A概算: 一回限りE2E約¥30-40(Guardrail案¥60)、恒常差分=Comment +1 call(約+¥3)、TTS clip数はDialogue量依存。
- Z記事1本あたりの量産コスト基準、量産cadence、運用フロー: 未確認。新規Seed/記事テーマはPM_GOVERNANCE 13節(候補提示->ユーザー選択)。

## 4. 実装済み/未実装一覧

実装済み(er026、text工程のみ): story_type metadata、rights block+gate、canonical text(語数・人名ルール)、segment plan(Dialogue境界)、Preview、Comment1、In One Line、Key Phrase(Strategy L)、budget guard、cost集計、unit test 19件、Melos run_01。
未実装: Production Writer/Story圧縮、Topic intro、Comment2-4、3分割、TTS stage、Dialogue Voice実TTS、J3/E2/Flash-Lite適用、Connected Speech(segment_id resolver拡張)、Assembly、Audio Validation、Master Store接続、試聴ページ、4+1 KPのrunner統合、DB Hybrid Z適用、runtime audio evidence、Opus L2、PRODUCTION_WIRED判定、Melos以外のStory(registryはmelosのみ)。

## 5. Xと共有するモジュール / Z専用

共有: er003_v1_n3_01_scaffold_generate(run_key_phrases)、er003_key_words_*、er003_v1_en_direct_vfl_01_generate、er003_v1_iran01_a2_generate(a2gen)、er006_model_routing_contract_01(routing)、er020_tts_retry_local_rewrite_01(read-only参照: resolve_narrative_role/connected_speech_enabled_for)、er025_entity_pronunciation_resolver_core_01(family_z_melos)、er003_audio_tts_asr_safety(記号正規化、Z Writer実装時必須)、er030 source reference contract(Zはfamily_profile未対応)。
Legacy Family C(Z-2/Z-4承認でread-only再利用): er013_family_c_production_01(plan_story_segments/build_flat_voice_chunks/split_into_paragraphs/classify_quote_voice_window/generate_family_c_a2_comment/build_family_c_a2_comment_prompt)。
Trial流用: er018_fiction_external_seed_selection_criteria_trial_02(Seed/story入力、logging)。
Z専用: er026_family_z_fiction_production_runner_01.py(+_test)。Z Key Phrase Trial: er031_key_phrase_db_hybrid_family_z_trial_01_*(Trial)。

## 6. 意図的差異(決定記録付き)と未整備の区別

意図的(根拠あり):
1. 外部Seed方式、AI完全自由創作を標準にしない(CURRENT_SPEC Family Z 1、2026-09-26)。
2. 日本国内PD必須・米国PD非必須(Z-1、PM-USER-DECISIONS-SSOT-CONSOLIDATION-03)。
3. 原作忠実、許容編集限定(Story内容方針2)。
4. 外国人名First/Last一方のみ(例外3条件)、True Crime含む全Story Type(F-3)。
5. story_type metadataによる音声intro・UI切替(項目5)。
6. 専用runner+Family C関数再利用(Z-2)、In One Line既存prompt最小変更(Z-3)、Dialogue Voiceは既存ルール再利用(Z-4)。
7. 本文は単一canonical text(Voice別複製なし)(Z-4)。
未整備(意図的差異の記録は未確認): 難易度A2限定、Key Phrase DB Hybrid非採用、J3/E2/Flash-Lite未適用、3分割/Comment4、Risk Flagger適用、Research系不在の運用。

## 7. 未解決OPEN / 未決事項

- OPEN-185: Z Production配線(TTS以降)実装待ち、PRODUCTION_WIRED未達。
- OPEN-202: 会話タグfalse positiveのZ拡大時再判断。OPEN-211: Strategy L経路のrunner_up契約・UI(Z/legacy該当)。
- Phase A設計の未承認論点: resolve_narrative_role()拡張(共有module)、Flash-Lite backend既定、num_three/five未確定、Comment4のZ所有prompt、Opus L2。
- CURRENT_SPEC L2126: Z Writer実装時のTTS記号正規化必須。N2: Z DB Hybrid配線は候補ID方式必須。

## 8. 過去Trial・改善提案(Status付き)

| 管理ID | 内容 | Status |
|---|---|---|
| FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01 | AI創作Fiction DNA、5本 | VALIDATED(Trial、標準方式にしない) |
| FICTION-CORE-PROVOCATION-PROMPT-BIAS-RETRIAL-01 | Prompt偏り再Trial | VALIDATED(Trial) |
| FICTION-STORY-DNA-E-AXIS-REDESIGN-01 | E軸再設計 | VALIDATED(Trial) |
| FICTION-EXTERNAL-STORY-SEED-TRIAL-01 | 外部Seed方式、4系統 | VALIDATED(Trial)、Z基本方式の根拠 |
| FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02 | Gate厳格化、5本(Melos由来) | VALIDATED(Trial) |
| FICTION-REAL-STORY-AND-TRUE-CRIME-TRIAL-01 | Real Story/True Crime各1 | VALIDATED、F-1/F-2、F-3不採用、F-4条件付き採用 |
| FICTION-FAMILY-Z-RIGHTS-RECHECK-01 | Melos権利再確認 | 決着(Z-1 APPROVED) |
| FICTION-FAMILY-Z-PRODUCTION-E2E-01 | Phase 0 recon+Phase 1 text工程 | 仕様APPROVED/text工程実装済み/PRODUCTION_WIRED未 |
| KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01 | X Hybrid CoreのZ適用 | Trial、Melos1本で不十分、Fable/ユーザー判断待ちで停止 |
| KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05 / SOURCE-REFERENCE-CONTRACT-TRIAL-06 | Zで発見したCore課題修正 | Trial-06 VALIDATED -> X/Z共通Core contractとしてAPPROVED、X側PRODUCTION_WIRED |
| KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01 | Melos A2 4+1 evidence(er035) | 4+1 APPROVED、Z runner統合は未 |
| FAMILY-Z-MELOS-PRODUCTION-E2E-AND-LATEST-SPEC-WIRING-01 | Phase A設計 | 設計のみ(55cb58ed)、実装・SSOT反映なし、ユーザー承認有無は未確認 |

## 9. 直近のZ関連承認事項・進行中作業

- 2026-09-26 Z-1〜Z-4 APPROVED。2026-09-27 Family体系決定(X/Y/Z Active)、Z text工程着手(commit 42b43772)。
- 2026-09-28 Source Reference Contract X/Z共通Core、4+1 Key Phrase。2026-09-29 Phase A設計。10/8 routing gpt-6-luna化がZ runnerへ反映。
- 進行中: ACTIVE_TASK等にZ記述は見つけていない(Zは停止中と推定されるが断定しない=未確認)。

## 10. 確認できなかった項目(推測せず)

- 難易度A2限定の意図的決定記録/B1B方針。
- Risk Flagger・B3 annotation・Research系のZ適用有無。
- Zの試聴ページ生成経路、量産cadence、Z記事あたりコスト基準。
- Phase A設計のユーザー承認有無とPhase B以降の計画。
- runnerのresume機構の有無(コード全読は未実施)。
- OPEN_ITEMS_HISTORY/DECISION_LOG_HISTORY/HISTORY_INDEXにはFamily Z記述0件(確認済み)。
