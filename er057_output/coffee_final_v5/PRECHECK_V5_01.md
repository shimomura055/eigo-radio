# PRECHECK_V5_01 (FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01 委任_01、2026-10-12、実装・生成前の記録)

## 0. 停止確認
`docs/pm/delegation_log/*STOP_NOTICE*` は Melos 案件用(別案件)のみ。`er026_output/family_z_production_e2e_01/STOP_ALL`・`<run>/STOP` なし。Coffee案件に停止指示なし。

## 1. v4 試聴本文と Production source_dir の相違(U1/U2)
- v4 原稿 = Tone Trial 由来(`feature/coffee-new-tone-01`、`coffee_prices/run_e_tone_01`)。Std article sha256 `a3cc7bb9...`、Adv `d9b77190...`。見出し「Coffee Bean Prices Fall. Are Price Tags Still on a Journey?」系("Beans cost less now!")。
- Production source_dir(`er019_output/coffee_prices/run_l3_01`)は別原稿。Std `6f5e8e53...`、Adv `5e8979dc...`。見出し「Coffee Prices Fall, but Store Prices Stay: Coffee's "Jet Lag"」系("Coffee prices are falling!")。両者は**別原稿**(WIRING_EVIDENCE_01 §0 で既知、`run_p8_wiring_01` は L3 原稿)。
- 対応: **v4原稿を維持した完成版を制作**。Production正本(`run_l3_01`)は変更しない。v4原稿は Production runner 用に別 source_dir `er019_output/coffee_prices/run_v5_ms_01`(Tone source の明示コピー、改変なし、sha一致を確認)と out_dir `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_v5_ms_01`(scaffold明示コピー)へ配置。Production側の原稿正本をどちらにするか(U1/U2)は**ユーザー判断事項として分離記録**(完成版の内容には影響しない)。

## 2. Adv P3 の定義
- P3 = 現行P0(`KEY_PHRASE_EXPLANATION_EN` = "clear, precise, at a measured pace, without dragging")+半角空白+"Let the sentence flow from its first word to its last, without stopping partway through."。141文字、sha256 `a8aaec591ef6d9acb42532cc0c84b6edfb2f75991e713d413c565b7e27677acc`。出典 `er057_output/kp_en_explanation_style_trial_01/prompts/prompts_kp_en_explanation_style_01.md` "## P3"。コードの定数と逐語一致(testで固定)。
- 正式選択の記録: DECISION_LOG `PM-COFFEE-REASSEMBLY-CONDITIONS-AND-USER-DECISION-REGISTER-01 委任_01`(2026-10-12)とOPEN-317(判断済み(P3))に記録済み。本指示でも再確認(再比較・P5/P8再提示なし)。

## 3. Std R2 の定義
- R2 = Standard日本語Aoede Style Trial-02(`FAMILY-X-COFFEE-STANDARD-JA-AOEDE-STYLE-TRIAL-02`、R1〜R8のうちR2「親しみ」)。168文字、sha256 `625826c1187b6381fe36ff444f1f568fc1f68d639d6a6a8931e728463692252f`。出典 `er057_output/ja_aoede_style_trial_02/prompts/prompts_R.md` "## R2"。
- v4でStd Preview/Comment1〜4はP2(Final v2採用、166文字、sha `4ade8738...`)のまま(v3継承、R2未反映)。Production現行(J3)ともv4(P2)とも異なる。

## 4. Comment4 Prompt
- `prompt_diff_03.md`/`prompts/prompt_trial_03.md` と Production定数 `FAMILY_X_A2_COMMENT_4_ROLE`(2文追加後)は**逐語一致**(sha256 `22feebde438ad5ec70d6a3ce19e067bc0c5fa3890de3fc600b5c6477278a3663`、testで固定)。他Role/Family定数は不変。

## 5. In One Line の正式仕様 と v4 の IOL
- CURRENT_SPEC(DECIDED、ER-003-A2-STRUCT-05): In One Line = 中心1文(要約)+英語の短い補足2文程度。
- v4(v3継承)のIOLは2文(Std: "Coffee bean prices fell, but shop prices may take at least about nine months to change. Other costs also matter, so lower bean prices do not promise a cheaper cafe cup." / Adv も2文)。これは**新2文方針(中心1文+補足1文)をTrialで適用した原稿**で、仕様化は OPEN-299(未仕様化・未承認)。つまり「正式仕様の文数(1+約2)」と「v4のIOL(2文)」には**記録上の不一致**がある。
- 本委任の決定A/B/Cは**IOLの変更を求めておらず**、IOLは「既存正式仕様に整合した音声・文章」=v4のものを**そのまま再利用**する(再生成・原稿変更なし)。したがって実装・生成にIOL仕様の未確定は影響しない(STOP条件の「仕様未確定で実装が止まる」には非該当)と判断し続行。ただし**OPEN-299は未解決のまま残り、USER_DECISION_REQUIRED(IOL文数方針の仕様化)として最終報告に記載**する。

## 6. P8/P3/R2 の初回/retry/fallback/LR経路
- 初回: runner の `resolve_role_style`(単一解決関数)経由。V5では Std preview/comment_1〜4=R2(`_role_style_ja_support`)、Adv KP解説=P3(`_kp_explanation_style`)、Full Story=P8。
- retry: 標準経路内retryは同一 style_prefix_override を再送(Std JA 2回、Adv KP解説 max_attempts=2)。
- fallback: Std JA は標準2回失敗後 `_generate_a2_japanese_minimal_instruction` へ移行しroleのStyleが落ちる(`fallback_used=True`)→ M3 GateでBLOCK(人間承認なしにAssembly不可)。Adv KP解説は minimal fallback 経路なし(失敗=STOPPED=M3 BLOCK)。
- Local Rewrite(OPEN-312): 英語Full Story系の再TTSでrole styleが落ちる既存の穴。本委任の再生成対象(Std JA、Adv KP解説)にLocal Rewrite経路は無い。Full Storyはv4音声を再利用するため影響なし。OPEN-312は未解決のまま(Full Story側、Family X全体の仕様変更でUSER_DECISION_REQUIRED)。
- Master Store(OPEN-313 b): Std JA Preview/CommentとAdv KP解説はMaster Store対象外。reuse判定(OPEN-313 a)は固定記録(`audit/style_profile.json`)+新out_dirで同一profileに閉じる。

## 7. 既存承認予算と本委任の費用見積
- Coffee累計(COST_LEDGER_COFFEE_01.md): 約JPY133.9 + 委任_03 wiring evidence JPY13.19 = 約JPY147.1(未集計項目除く)。SSOTにCoffee案件全体の上限記載なし。**本委任は上限JPY100として扱う**(委任文)。
- 本委任の生成前見積: Std Comment4文章 LLM 1 call ≈ JPY0.1(実績JPY0.05)/ Std Preview+Comment1〜4 R2 TTS 5 clip + ASR ≈ JPY1.5〜3(retry込み最大約5)/ Adv KP解説P3 TTS 5 clip + ASR ≈ JPY1〜2(retry込み最大約3)/ Risk Flagger guard(sha一致しないため実行される可能性、非Blocking)≈ JPY0〜3 / Assembly・WPM・Playwright = JPY0。**合計 約JPY3〜11、上限見込み約JPY15 << JPY100**。Runner `--budget-jpy 30` を指定。
- 使用モデル(最新原則): TTS=gemini-3.8-flash-lite-tts(Production正式backend、最新世代)、Comment4文章=gpt-6-luna(Trial-03同一経路)、ASR=gpt-4o-mini-transcribe(Production既存、変更なし)。

## 8. 並行agent作成の計画書
- `docs/pm/design/2026-10-12_COFFEE-FINAL-REASSEMBLY-PLAN-01.md` と整合: 必須反映5点(IOL確定仕様反映[本委任ではv4のIOL維持]/P3/R2/変更対象音声の更新/最終Assembly後runtime evidence+試聴ページ確認)。工程: 前提確認→生成(独立なStd JA/Adv KPは別level実行)→Assembly(流用分sha照合)→QA/速度→runtime evidence→試聴ページ→Gate確認。計画書の「Adv KP 4件」は誤記で、実際のCoffee KPは5件。

## 9. 生成方針(実行層の設計判断、要約)
- 生成は Production runner(`--style-profile coffee_final_v5 --tts-backend speech_metadata_flash_lite --only-segments ...`)で行う。`--only-segments`は本委任で追加した最小CLI(既定None=従来同一)。
- 注意(M2との関係): Adv KP解説textをv4のまま保つため、out_dir作成(style_profile.json記録)の**後**に `b1b/audit/tts_generation_results.json` へ「key_phrase_explanations_text bundleのみ」を事前配置した(音声segment結果は含まない、Tone runのtext bundle逐語、provenance付き)。M2(既存run記録とStyleの混在防止)の目的である「Review Lock/承認をまたいだStyle混在」は起きない(承認・segment結果は無し)が、手順上のM2回避であるため最終報告で明示する。
