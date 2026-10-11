# FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 Phase 1-A 調査(read-only、課金0)

日付: 2026-10-11 / worktree: C:\Users\tensh\eigo-radio-tone (feature/coffee-new-tone-01, origin/main b2986887 起点)

## 1. E案マスター
- 正式保存: `docs/quality/ja_quality_masters/coffee_prices/E_master_r2.md`(+`E_master_meta.json`、status=HUMAN_APPROVED_QUALITY_MASTER)。
- SHA-256(LFバイト) = `742e7b6a7fe43f1bd8e6106fc5892720124e0a174c6bb1e0b63e70a5b3eb248a`(meta記載値=git blob値=`ja_writer/runtime_evidence.json.ja_text_sha256`)。
  **注意**: このrepoは`core.autocrlf=true`のため、Windows checkout後のworking tree実体はCRLF変換されsha=`00f19a3d...`になる(blobはLF)。
  マスターmdと`revision2.md`はblob同士・LF同士で一致(`export/r2.md`==`E_master_r2.md`、byte-identical)。
- 元artifact: `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/coffee_prices/E/`
  - ja_writer: original.md / revision1.md / revision2.md(=マスター)/ factlock/{r0,r1,r2…} / runtime_evidence.json
  - runtime_evidence.json: `chain_method="MAQ_TRIAL_W-1"`(**ProductionのW-1ではない**)、models=r0/r1/r2全て`gpt-6.1-sol`、`annotated_md_sha256=249b0c08...3425`、`annotation_manifest_producer=deterministic_v2`、override_reason="...DEV/Trial...Production不変"
  - storyline_b3(B3 Sol、`annotation.json`/`annotation_manifest.json`/`selected_brief_annotated.md`ほか)、producer=deterministic_v2(LLM 0)
  - Ledger: `research_ledger/verified_fact_ledger.txt` sha `e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b`(18 facts、A案run_l3_01と**同一ledger**)
  - 選択Fact: COFFEE-001/010/014/015/018、本文872字(空白除く894字相当)、Trial費用¥26.94
  - タイトル: 「コーヒー豆は値下がり。値札は、まだ旅の途中？」

## 2. 既存Productionコーヒー記事(`er019_output/coffee_prices/run_l3_01`、A案 Luna/Astra)との差
| 項目 | A案(既存Production) | E案(承認マスター) |
|---|---|---|
| Writer | chain_method="W-1"(factlock_r0_luna__astra_r1_r2) | "MAQ_TRIAL_W-1"(全段gpt-6.1-sol) |
| 選択Fact | 003/010/009/014/015 | 010/001/015/014/018 |
| 本文(空白除く) | 934字 | 894字 |
| タイトル | 相場は下落、値札は居残り。コーヒー価格の「時差ぼけ」 | コーヒー豆は値下がり。値札は、まだ旅の途中？ |
| ledger sha | e94a50c1... | e94a50c1...(同一) |
原稿・選択Factが異なるため、既存のEN(Advanced/Standard)・KP・各音声(A案由来)は**再利用不可**。研究/ledger(¥46.8相当)とJA記事は再生成不要(E案artifact流用)。

## 3. Sol 6.1 Production Wiring
`feature/sol61-ja-allocation-01`(tip cacc665a)はorigin/mainに含まれる(adb15c30 merge済み、B3/R0/R1/R2がgpt-6.1-solへ配線)。本E2Eは日本語を再生成しないためSol配線に依存しない。整合: E案Trialの全段モデル配置=Production配線と同一。

## 4. 正式経路(entertainment runner reused JA経路 / U-1)での再利用可否(乾式、API 0)
検証方法: `load_reused_ja_text(out_dir)`(er019_family_x_entertainment_production_runner_01.py:233)をE案run dirのscratch複製へ直接呼び出し。
- **結果1(無変更コピー): FAIL = `LegacyWriterProvenanceStop`**: `chain_method='MAQ_TRIAL_W-1'` は 'W-1' ではない(U-1検査はW-1完全一致のみ許可)。
- 診断(scratch限定、repo非反映): chain_methodのみ"W-1"に書換えた複製では **PASS**(contract.validate_annotated_b3 V1-V10、annotated_md_sha256=249b0c08...一致、revision2.md読込916文字)。= 唯一のブロッカーはchain_method文字列。
- 補足(別の落とし穴): gitに入れたartifactは`core.autocrlf=true`でcheckout時にLF->CRLF変換され、`selected_brief.md`/annotated md/sidecar/writer_constraintsのshaがmanifest記録値と不一致になる(契約V3違反)。一方ledgerは原本がCRLFでありcheckout後に一致する(混在)。= **run dirをgit経由で複製してはならない**。バイト完全コピー(主ツリーの原本から`cp`/shutil.copyfile)かつsha検証が必須。
- 判定: 無変更コピーでは通らない -> **STOP**(迂回しない)。最小対応案は報告本文参照。run_e_tone_01の実体作成はこの判断が出るまで行っていない。

## 5. 後工程の再利用(固定Master等)
- 固定Master(shell: welcome/preview_intro/key_phrases_intro/full_story_intro/num_one..five、Standardのpoint_explanation): Master Audio Store key=(language,voice,tts_model,canonical_text,style_instruction_id,version)。`FAMILY_X_ROLE_STYLE_*`/`FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`を参照しない(`er006_audio_cost_pilot_02_shared_narration.py`)。今回の変更では無影響 -> 再利用維持(再生成しない)。
- KP英語(Aoede、used_form単位のMaster key、style_instruction_version=KEY_PHRASE_TRIM_POLICY_VERSION): 無影響。ただしE案のKP選定(db_hybrid)結果が既存phraseと一致した分のみreuse、未保存phraseは新規生成。
- KP英語解説(Advanced、`KEY_PHRASE_EXPLANATION_EN`style不変): run単位cache(新run dirは空)かつ記事依存のLLM生成のため、どのみち新規生成。version bumpの影響なし(新run dir)。
- In One Line: style不変(IN_ONE_LINE)。ただし文面が新記事のため新規生成。
### 新規生成対象一覧
- Standard: japanese_title(J2)、japanese preview、comment_1-4(J2)、KP日本語意味(J2)、topic_intro(不変style、新title)、Full Story part1-3(F1.5+既存6%減速)、in_one_line(不変style)、KP英語(未保存分のみ)
- Advanced: topic_intro(不変style)、英語 preview、comment_1-4(E2_UPBEAT、Charon)、Full Story part1-3(F1.5、Aoede)、in_one_line(不変style)、KP英語(未保存分)+KP英語解説(現行style)
- 再生成しない: 固定shell Master(champion)、point_explanation。

## 6. 進行中作業との競合
- Sol61: mainへmerge済み。worktree(eigo-radio-sol61)に未commit差分なし。
- SCG(feature/scg-ja-secondary-01): 変更ファイル = er003_v1_n3_01_tts_generate.py / er003_v1_repro01_main_generate.py / er003_v1_sing01_voice01_generate.py / er007_*。**本件の変更ファイル(er033 styles / er019 audio runner定数 / 関連test)と重複なし**。意味的にもTTS経路の別領域(SCG=ASR secondary)。将来mergeは自動解決見込み。
- 主ツリー(別agentがSSOT編集中): 本件はSSOTを編集しないため衝突なし。

## 7. Phase 1-B 実装結果(課金0)
- 変更: `er033_tts_flash_lite_family_x_styles_01.py` に内部識別子 `JA_J2_BRIGHT` / `EN_COMMENT_E2_UPBEAT` / `EN_FULLSTORY_F1_5` を新設(従来Full Story用Style名「E2」とは別物)。
  `FAMILY_X_ROLE_STYLE_JA = JA_J2_BRIGHT`、`FAMILY_X_ROLE_STYLE_EN["PREVIEW"/"COMMENT"] = EN_COMMENT_E2_UPBEAT`、`["FULL_STORY"] = EN_FULLSTORY_F1_5`。
- Role対応: J2=Standardのjapanese_title/preview/comment_1-4/KP日本語意味(既存`_role_style_ja()`経由、変更なし)。E2_UPBEAT=Advancedの英語preview/comment(Charon)。F1.5=両LevelのFull Story part1-3(Standardは`_role_style_slower`で既存6%減速を連結、Advancedは速度不変)。
  不変: TOPIC_INTRO / HEADING_READOUT / IN_ONE_LINE / FALLBACK style / KP英語・英語解説(KEY_PHRASE_EXPLANATION_EN) / 固定shell Master / 他Family(Family X限定定数、`speech_metadata_flash_lite` backend明示時のみ参照、既定backendはNone)。
- version guard: `FAMILY_X_VARIABLE_ROLE_STYLE_VERSION` v3_j3_kp_meaning_and_explanation_guard -> `v4_j2_e2upbeat_f15_tone_refresh`(旧tone cacheの可変segment/KP日本語意味/KP英語解説を黙ってreuseしない)。Master Store(固定phrase/KP英語)は別versioning=無影響。
- 注意(既存仕様・変更せず): fallback(minimal instruction)経路は従来どおりstyle_prefix_overrideを無視し`FAMILY_X_ROLE_STYLE_EN_FALLBACK`を使う=retry/fallback時のみ新toneが乗らない(既存設計。変更には別判断が必要)。初回・retry標準経路・regeneration・resumeは同一定数参照。
- test: 新規`er033_family_x_coffee_new_tone_wiring_01_test_01.py`(9件: 逐語固定・Role対応適用/非適用・Trial値一致・version guard・Dangling)。旧値固定の既存test 5件を新値へ更新(er019_variable_role_style_wiring / er033 styles / er038 / er044、意図的な期待値更新のみ)。
- 全suite(run_project_regression.py、venv=.venv Python3.14.6): base collected=5316 passed=5178 failed=17 errors=75 skipped=38 -> 変更後 collected=5325 passed=5187 failed=17 errors=75 skipped=38。FAIL/ERROR集合(93行)はbaselineと完全一致(既存のenv起因failure、本件無関係)。
- Dangling: 旧style3文字列は Production code(er033 styles / er019 audio runner)にリテラルとして残存0(testで固定)。残存は旧Trial script(er022/er038/er044、履歴)とSSOT文書(履歴)のみ。

## 8. 費用見積(課金0のPhase 1で算出、実行は未承認)
基準: run_l3_01 cost.json実測+Fable指定単価。研究(¥21.96)・ledger(¥24.88)・JA writer・B3は**E案artifact流用のため0**(ledger sha同一)。
| 項目 | 点見積(JPY) |
|---|---|
| EN Advanced+Standard生成 | 0.73(実測0.349+0.381) |
| RF 8 call | 2.42(実測8条件合計) |
| Review Queue | 0 |
| 支援文生成 | 3.5 |
| KP選定(db_hybrid) | 0 |
| TTS新規(固定Master除く) | 8 |
| ASR | 4 |
| retry期待値 | 3.6 |
| 技術QA | 0 |
| **合計(点)** | **約22.3**(retry除き約18.7) |
| **保守(x1.5)** | **約33.4** |
(承認済み予算は本管理IDに未設定。Fableがユーザーへ提示する。)
