# E2E_PLAN_01(FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01 委任_01、2026-10-17、計画のみ・JPY0・有料実行なし・git書込みなし)

**状態**: `E2E_PLAN_READY_PENDING_S3_WIRED_AND_COST_APPROVAL`。S3 `PRODUCTION_WIRED`未達かつ費用承認未取得のため、有料runは開始しない。
**雛形**: `docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/COFFEE_E2E_PLAN_01.md`(§1担保表、§2工程表、§5費用、§実走記録)。Python=`.venv/Scripts/python.exe`(`python`shimは壊れている)。
**ユーザー原文**: `docs/pm/delegation_log/2026-10-17_FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01_USER.md`(7905文字、sha256=0c3f79e60ec22eba1985bbf77397a6204eb6babc107200940b7362d5dc4921b2)。

## 1. 開始条件チェックリスト(ユーザー§2。1つでも未達なら有料生成しない)

| # | 条件 | 確認方法 | 現時点(2026-10-17) | 2026-10-17 実走前再確認(委任_03) |
|---|---|---|---| --- |
| 1 | S3がStd日本語Preview/Comment1〜4の正式Styleとして配線済み | `er019_family_x_style_profile_01.py` Grep `DEFAULT_NEW_RUN_PROFILE`がS3 sha`060c08fd…`を持つprofileを指し、新規run`--stage plan`の`audit/style_profile.json`のSUPPORT_JA shaが`060c08fde003cf7c2d15c654da96d3f857b8e7a9bd79eac31814ceaf7c923f33`(`:159`) | 作業ツリーに未commitの`fx_20261017`(`:186-187`,`:277-283`)があるが、S3W委任_03が編集中。commit/Fable受入前=**未達** | **PASS**: `er019_family_x_style_profile_01.py:186-187` `PROFILE_FX_20261017`=`DEFAULT_NEW_RUN_PROFILE`。実走S6 planの`audit/style_profile.json` SUPPORT_JA sha=`060c08fd…`(CLI指定なし)。 |
| 2 | 初回・retry・fallback・regeneration整合 | S3W委任_03のRESULT_PACKETと該当test ID | OPEN-405のPhase B論点(a)(b)(c)が未解決=**未達** | **PASS**: S3W 委任_03/_04 `FallbackGuaranteeTests` 7件含む`er019_family_x_s3_wiring_01_test_01.py` 28件PASS(CURRENT_SPEC.md:1265付近のFable判定)。 |
| 3 | Production runtime evidence | `.../coffee_prices__run_fxpw_01_s3prod/`(`audit/style_profile.json`等) | 当該dir**不存在**(進行中)=**未達** | **PASS**: `coffee_prices__run_fxpw_01_s3prod`存在(audio配下)。 |
| 4 | 必要テストPASS | S3W委任_03報告のtest結果 | **未確認** | **PASS**: 同上28件(Fable判定記録)。 |
| 5 | CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSに`PRODUCTION_WIRED`記録 | Grep `S3-ADOPTION` | OPEN-405=`PHASE_A_USER_LISTENING_PENDING`、UDR #105(S3採用可否)待ち=**未達** | **PASS**: `CURRENT_SPEC.md:1259/1265` S3W=`PRODUCTION_WIRED`(2026-10-17 Fable)。 |
| 6 | Git反映 | `git log`に配線commit、`git status --porcelain`でstyle profile等が非dirty | `er019_family_x_style_profile_01.py`が`M`(未commit)=**未達** | **PASS**: commit `61e5ad3e1`、`git status --porcelain er019_family_x_style_profile_01.py`=空。 |
| 7 | Fable独立受入 | Fableの判定記録(CURRENT_SPEC同日Fable判定行) | **未達** | **PASS**: Fable判定(S3W 委任_05、2026-10-17)。 |

結論(当初2026-10-17計画時): S3W Phase B進行中=開始条件未達。**実走前再確認(委任_03、最右列)で7項目全PASS、有料run開始可**(費用上限JPY180はユーザー承認済み)。

## 2. テーマ・slug・out-dir

- `--theme`の既存書式(`er019_output/coffee_prices/run_l3_01/entry_point.json` `args.theme`): **英語の1段落指示文**(「Current news/lifestyle topic: ... Using only facts confirmed by web search (...), cover ... Separate confirmed facts from forecasts ... Do not invent details and do not use the assistant's own prior knowledge.」)。日本語併記は無い。
- テーマ文字列案(ユーザー§3の主題をそのまま使い、研究結果・因果関係を含めない。既存書式の「事実と予測の分離」「作り話禁止」の定型句は踏襲):
  `Boredom and Aggression (退屈と攻撃性): the relationship between feeling bored and aggressive behavior. Using only facts confirmed by web search (peer-reviewed studies, university or research-institution releases, and Reuters/AP/Bloomberg-level reporting), identify what research has actually been reported on boredom and aggression, including who the participants were, the experimental conditions, and the stated limitations. Separate confirmed facts from interpretation and forecasts, and do not present a correlation as causation unless the source establishes it. Do not invent details and do not use the assistant's own prior knowledge.`
  (この文は「何を調べるか」の指示のみで、特定の研究結果・因果は含まない。最終文言はFableが確認。)
- slug案: `boredom_aggression`。out-dir案: `er019_output/boredom_aggression/run_bape_01`。run-label: `BAPE-E2E-01`。audio出力(AR既定derive予定): `er019_output/family_x_audio_production_wiring_01/boredom_aggression__run_bape_01`。
- 既存dir非存在確認: `ls er019_output | grep -i bored` → 0件、`er019_output/boredom_aggression`なし(2026-10-17確認)。
- stop_scope_check: `tools/stop_scope_check_01.py --managed-id FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01 --run-dir er019_output/boredom_aggression/run_bape_01 --out <json>` → dir未作成でも実行可、**rc=0(stop:false)**。

## 3. テーマ選定の扱いと過去記録(流用禁止対象)

- PM_GOVERNANCE 13-2は新規記事テーマをユーザー選択後に生成と定める。今回はユーザー原文§1・§3が「退屈と攻撃性」を指定済み(OPEN-301の繰越候補をユーザーが選択)=選定不要(区分A)。
- 過去記録(原文): `OPEN_ITEMS.md:804` OPEN-301「次回Family X候補提示時に含める繰越候補3件(TOPIC-SELECTION-FORM-AND-FAMILY-MIX-20261012-01、2026-10-12ユーザー決定)『退屈と攻撃性』『家の操作を変える壁の画面』『小さなEVの試乗評価』を、次回Family X候補提示…に繰越候補として含める。…Status=OPEN(次回候補提示待ち)」。`DECISION_LOG.md:20612`の同ID決定行にも同候補の言及。`docs/pm/USER_DECISION_REGISTER_01.md`は該当なし。
- 過去run/Trial成果: `er019_output/**/entry_point.json`のGrepで`退屈|boredom|aggression`は**0件**。`er019_output/boredom_aggression`も不存在。**流用して除外すべき既存の記事成果物は無い**。

## 4. 工程表(Coffee計画§2転用。THEME/slug/out-dir/run-labelのみ置換)

共通: 各stage前に `.venv/Scripts/python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01 --run-dir er019_output/boredom_aggression/run_bape_01 --out <json>` (rc=3なら中止)。全コマンドに`TTS_EXECUTION_MODE=STANDARD`(T-2、Batch例外理由なし)。`<THEME>`=§2の文字列。

| # | 工程(ユーザー§4) | コマンド | STOP/Gate |
|---|---|---|---|
| S0 | 実走前(JPY0) | 開始条件§1全PASS・費用承認・出力dir非存在・`--stage plan`でprofile確認 | 未達=開始しない |
| S1 | 1.Research+2.Verified Fact Ledger | `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_entertainment_production_runner_01.py --theme "<THEME>" --slug boredom_aggression --out-dir er019_output/boredom_aggression/run_bape_01 --run-label BAPE-E2E-01 --budget-jpy 110 --stage research` | budget超過STOP。`research_ledger/runtime_evidence.json` `reused:false`、web_search_call_count記録 |
| S2 | 3.B3(Sol) | 同 `--stage storyline_b3` | model_id不一致STOP |
| S3 | 4.W-1 R0→R1→R2 | 同 `--stage writer --budget-jpy 110` | 記号Validator STOP |
| S4 | 5.Advanced英語化+IOL+RF b1b | 同 `--stage advanced --budget-jpy 110` | IOL spec_ok=false=STOP |
| S5 | 5.Standard調整+RF a2 | 同 `--stage standard --budget-jpy 110` | **ここで構造的にMandatory STOP**(text runnerに音声stageなし)→ユーザー確認→音声runner。本指示は将来のGateを一括解除しない(ユーザー§8) |
| S6 | 音声plan(JPY0) | `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug boredom_aggression --run run_bape_01 --level both --stage plan` | `audit/style_profile.json`でSUPPORT_JA sha`060c08fd…`を含む6 role sha確認(CLI指定なし、`--tts-backend`省略=既定) |
| S7 | 6.KP(M2P0+A)・gloss・解説text・Preview/Comment text | `TTS_EXECUTION_MODE=STANDARD ... --stage scaffold --level both --budget-jpy 70` | gloss HR待ち=STOP。M2→Strategy L fallback=必須ユーザー報告 |
| S8 | 7.TTS Advanced | `TTS_EXECUTION_MODE=STANDARD ... --stage tts --level b1b --budget-jpy 70` | review_lock、`STOPPED` segment |
| S9 | 7.TTS Standard | `TTS_EXECUTION_MODE=STANDARD ... --stage tts --level a2 --budget-jpy 70` | Std fallback(`STD_FALLBACK_USED_OR_UNKNOWN`) |
| S10 | 8.AUW(正式配線済みgate)+9.Assembly | `TTS_EXECUTION_MODE=STANDARD ... --stage assemble --level both` | Audio Validation Gate、M3 Style Gate。BLOCKは迂回せず人間承認/segment再生成 |
| S11 | 10.試聴ページ | `TTS_EXECUTION_MODE=STANDARD ... --stage player`→`user_test/`配置→commit/push(GitHub Pages、`file:///`/raw URL不可)→HTTP200とPlaywright実再生 | Gate 7(a)〜(m) |

※音声runnerの引数はCoffee計画S6書式と同形(`--slug ... --run ...`)。runner実装はS3W委任_03で変更され得るため、実走直前に`--help`で再確認。
※commitを伴うS11(試聴ページcommit)は、並行タスクとcommitが重ならない時点で行う(ユーザー§10)。

## 5. 仕様照合表(ユーザー§5の11行)

| 対象 | 正式仕様 | 確認方法 |
|---|---|---|
| B3/Writer R0〜R2 | Sol、W-1 | `storyline_b3/runtime_evidence.json` `model_id_actual`、`writer_run_summary.json` |
| Std日本語Preview/Comment1〜4 | **S3** | S3W PRODUCTION_WIRED後、`audit/style_profile.json`のSUPPORT_JA sha=`060c08fd…`、`e2e_segment_style_table.json`のStd Preview/Comment行 |
| Full Story | PD06 | segment表FULL_STORY sha `3a680861e4d9…`(fx_20261016/17共通) |
| KP英語 | K2 | segment表KP_EN `9d905cfe6c04…`、Store key `+k2.<sha12>`、`fallback_used`一覧 |
| Std KP日本語意味 | P8 | KP_JA_MEANING `b12c8721eab8…` |
| Adv KP英語解説 | P7 | KP_EXPLANATION_EN `0518000694e3…` |
| Adv Preview | E1 | PREVIEW `8862317ff766…` |
| KP候補・選定 | M2P0+A | `kp_supply=m2`、`m2_fallback=null` |
| IOL | 原則2文、必要時3文 | `writer_run_summary.json` `in_one_line.sentence_count∈{2,3}`・`spec_ok:true` |
| Std Full Story | 6%減速 | `slowdown_info`ratio≒1.06+減速後ASR PASS |
| 音声QA | 正式配線済みAUW | `tts_generation_results.json`のASR/二次ASR判定、`style_profile_gate.json` |

**重要**: S3以外のshaは`fx_20261016`で確認済みの値(COFFEE_E2E_PLAN_01 §実行直前チェック(b)2、§実走記録)。現時点の`DEFAULT_NEW_RUN_PROFILE`は作業ツリー上`fx_20261017`(`er019_family_x_style_profile_01.py:187`)で、S3W委任_03が編集中のためcommit後に値が変わり得る。**実走直前に再確認**(DEFAULT_NEW_RUN_PROFILE、6 role sha、S3W完了後のtest結果)。仕様名の存在だけで適用済みと見なさず、profile・runtime evidenceから確認する。

## 6. 流用禁止の担保

Coffee計画§1を踏襲: (1)新out-dir(非存在確認済み、既存`verified_fact_ledger.txt`の黙示再利用を防ぐ) (2)Family Xに`reuse_from`機構なし、旧dirをseed/copyしない (3)Research/Ledger/B3/Writer/KP/音声は一切引継なし (4)Master Audio Storeは固定shell(welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five)と同sha音声のみ再利用=正当な通常機能。最終報告に流用/新規一覧を明記 (5)実走後検査: `runtime_evidence.json` `reused:false`、`ledger`/`writer`成果のshaが他run不一致、`tts_generation_results.json`の`reused_from_previous_run`(shell除く)なし。

## 7. 費用見積(工程別。出典=Coffee run_fxpw_01実測 `er019_output/coffee_prices/run_fxpw_01/cost.json`・`.../audit/cost_by_stage_e2e_06.json` とCoffee計画§5の係数。`manual_substitution`)

| 工程 | 期待JPY(Coffee実測) | 上限JPY(係数適用) | 根拠 |
|---|---|---|---|
| Research | 19.8(web検索11回) | 〜30 | 実測19.847。テーマにより検索回数が変わる |
| Verified Fact Ledger | 25.1 | 〜30 | 実測25.135(Research+Ledgerの最悪はCoffee計画で60) |
| B3 | 10.9 | 14 | 実測10.937(Coffee計画の見積7.0を上回った実績) |
| Writer R0/R1/R2 | 6.8/3.2/3.8=13.9 | 22 | R0記号再生成+R2再実行を見込む |
| Advanced英語化+RF b1b | 0.3+1.0=1.3 | 3 | |
| Standard調整+RF a2 | 0.5+1.1=1.6 | 3 | |
| **text小計** | **72.6** | **約102〜105** | |
| KP scaffold(LLM) | 2.4 | 12 | 実測2.358(16 call) |
| TTS Advanced(Gemini 7.0+ASR 1.5+Azure 2.3+LLM 0.03) | 10.8 | 28 | 実測Adv合計10.84 |
| TTS Standard(Gemini 6.1+ASR 2.1) | 8.2 | 27 | 実測Std合計8.19。S3によるSupport TTSの単価差は小(S3 Trial 5clip=約2.1) |
| **audio小計** | **21.4** | **約67** | |
| **合計** | **約94.0** | **約170〜172(Coffee計画の最悪162に、B3等の実績超過分を補正)** | |
| retry/fallback追加 | 上限に含む | — | |
| 偶発(合計に含めない) | — | +21〜43 | OPEN-395 JA Latin語web lookup(1回約21.5) |
| ASR | 実測値(上表に含む。usage logベース) | | 推定/実測は報告時に区別(ユーザー§6) |

7-7判定: **期待約94も上限約170も100円前後〜超で、ユーザー個別費用承認が必要**(PM_GOVERNANCE 7-7「JPY100超=従来どおりユーザー判断」)。ユーザー原文§7「新たな個別上限金額は承認されていない」「Coffeeの205円承認枠を流用しない」に従う。
- **承認案(Guardrail、期待約95)**: E2E合計上限 **JPY180**(= text `--budget-jpy 110` + audio `--budget-jpy 70`)。注: 委任文の「上限165、110+70=合計165以内」は算術が合わない(110+70=180)。合計165に抑えるならtext 100/audio 65とするが、textが最悪に近づいた場合に早期STOPし得る。**推奨は180**(stage cap合計と一致、必須品質Gateを費用で省略しない)。偶発OPEN-395(+21〜43)は別枠で、発生時はFableへ報告。
- Cap定型(後続委任文用、T-3): 「Guardrail/soft stop: text stage `--budget-jpy 110`、audio stage `--budget-jpy 70`、到達時はFableへ報告し自動継続しない。絶対上限ではなくGuardrail」。
- 量産原価目標70円(15-9)との差: 期待94.0 − 70 = **+24.0円**(Coffee実測94.025の転用値。今回の実測で更新)。本E2Eでは削減策を提案・実装しない(ユーザー§6)。

## 8. 本日(2026-10-17 JST)使用済み・残額

- 確定: SJS4(`er057_output/ja_support_calm_style_trial_04/cost_actual_01.json`)TTS推定31.33+ASR推定約10.3=約41.6(REPORT_LEDGER L346)+S3W Phase A(`.../coffee_prices__run_fxpw_01_s3_support_01/cost_actual_01.json` total_jpy_est=2.1)=**約43.7円**(`ACTIVE_TASK.md` QDC行と一致)。RLCT準備はJPY0。
- `docs/pm/tools/daily_dev_cost_01.py --date 2026-10-17`: log=0.0/ledger=0.0(スクリプト値は過小。手集計43.7を採用)。
- **未確定**: S3W委任_03(Production配線・実走)の費用。新run dir`.../coffee_prices__run_fxpw_01_s3prod/`は現時点**不存在=進行中・未確定**。
- 残額: 1,000−43.7=約956円(S3W委任_03分は未確定)。E2E加算(期待約94、上限約180、+偶発43)後でも累計は約180〜270円+S3W03で、**1,000円超過見込みなし**(7-9の事前承認対象外)。ただし7-7(100円超)は個別承認対象。

## 9. STOP条件・チェックポイント(Coffee計画のCP-A〜Fを転用)

STOP: ユーザー§11(S3未達/Mandatory HR/Production不具合/重大なFact・品質問題/仕様不一致/費用Gate超過見込み/新仕様・Trial必要)。CP-A=S0後(開始条件・承認)、CP-B=S1後(Research/Ledger: `reused:false`、検索回数、相関/因果の断定がLedgerに無いか、対象者・条件・限界の記載)、CP-C=S5後(Mandatory STOP、ユーザー確認)、CP-D=S7後(KP・M2・gloss)、CP-E=S10後(style_profile_gate・AUW)、CP-F=S11後(最終照合)。検索上限方式・Select-then-Verifyは適用しない(RLCTは別管理ID)。同種失敗再発・外部停止・原因不明rc≠0が2回=再起動せずSTOP(26節)。

## 10. 報告様式

- 冒頭3点(ユーザー§12): (1)Researchから音声完成までの正式E2E正常動作可否 (2)Std/Adv試聴ページURL (3)工程別費用Breakdownと総額。
- 円単位の工程別表(ユーザー§6): Research(実測円/Web検索回数/LLM費)、Ledger(同)、B3、Writer R0/R1/R2、Advanced、Standard、KP(生成・選定・解説)、TTS Std/Adv別、ASR(実測/推定の別)、retry/fallback、合計。70円目標との差額。実測/推定/未取得を区別。
- 工程ごとの記録(ユーザー§8): entrypoint、実model_id/routing、Prompt/Style SHA、入出力artifact、retry/fallback/regeneration、Validator/Gate結果、Mandatory STOP/HR有無、費用、後続引渡し。

## 11. SSOT追記文案(編集せず文案のみ)

- DECISION_LOG: 「2026-10-17 | FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01 委任_01 | ユーザー指示原文保存(7905文字)、計画・工程別費用見積作成(JPY0)。S3 PRODUCTION_WIRED待ち・費用承認待ち。有料run未実施」
- OPEN_ITEMS: 新規候補「BAPE Status=PENDING_S3_WIRED_AND_COST_APPROVAL。OPEN-301の繰越候補『退屈と攻撃性』をユーザーが選択。開始条件=S3W PRODUCTION_WIRED(OPEN-405)」
- REGISTER: 「#106 BAPE E2E費用承認(UDR-blocking): 期待約95/上限JPY180案(text110+audio70)。Coffee 205枠は流用不可」
- REPORT_LEDGER行: 「2026-10-17 | FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01 委任_01(原文保存+E2E計画+費用見積、JPY0、Status=E2E_PLAN_READY_PENDING_S3_WIRED_AND_COST_APPROVAL)」
- ACTIVE_TASK行: 「管理ID: FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01 / Status: E2E_PLAN_READY_PENDING_S3_WIRED_AND_COST_APPROVAL / UDR-blocking: #106 / 当日費用: 計画のみ+0円」

## 12. 実走記録(委任_03、2026-10-17、text工程S0〜S6。ユーザー承認: 費用上限JPY180、#106判断済み)

共通: out-dir=`er019_output/boredom_aggression/run_bape_01`、runner=`er019_family_x_entertainment_production_runner_01.py`(sha256 `6bcc8e4b…`、`writer_run_summary.json`)、`TTS_EXECUTION_MODE=STANDARD`、`--budget-jpy 110`、`--run-label BAPE-E2E-01`。各stage前のstop_scope_check=rc0・stop:false(`_stop_scope_check_03_s0`〜`s6.json`)。各stage 1回実行・rc=0・retry/fallback/Human Review/再起動なし。コマンドはE2E_PLAN_01 §4と同一(差異なし)。RLCT方式(検索上限・Select-then-Verify・er082)不使用。

| stage | model_id(actual) | 主要Gate/結果 | 費用JPY(実測=usage x pricing_snapshot計算値) |
|---|---|---|---|
| S1 Research | gpt-6-luna | facts=11、web_search 9回 | 16.354(LLM 1.954+検索14.4) |
| S1 Ledger(Verification) | gpt-6-luna | VERIFIED10/AMBIGUOUS1(F08)/REJECTED0、web_search 14回、`runtime_evidence.json` reused:false | 24.961(LLM 2.561+検索22.4) |
| S2 B3 | gpt-6.1-sol | attempts1、validation_errors空、選定F05・F06(Study7/8の二実験)。prompt sha dev=`b4391b03…`/user_tmpl=`d6fe9bc3…`/fact_test=`91513c89…` | 7.936 |
| S3 Writer W-1 R0/R1/R2 | gpt-6.1-sol | chain=W-1(factlock_r0__r1_r2_independent_sol61)、記号QA findings0・R0再生成なし・R2再実行なし。R0_PROMPT sha=`6108a7cd…`、DEVELOPER_MESSAGE=`d1fbb042…` | 8.440/2.997/3.105 |
| S4 Advanced | gpt-6-luna | STRUCTURE_PASS、attempts1、IOL sentence_count=3・spec_ok:true(prompt sha `be35201a…`)、RF b1b status=OK 候補2件 | 0.408(+RF 0.983) |
| S5 Standard A2 | gpt-6-luna | STRUCTURE_PASS、attempts1、checks_failed空、numbers_missing/added空、IOL 3文spec_ok:true(prompt sha `a894db1c…`)、RF a2 status=OK 候補4件 | 0.367(+RF 0.773) |
| S6 audio plan | — | `audio/…/boredom_aggression__run_bape_01/audit/style_profile.json`: profile_id=fx_20261017、`entry_point.json` profile_source=default_new_run_fx_20261017、6 role sha一致(SUPPORT_JA 060c08fd…/FULL_STORY 3a680861…/PREVIEW 8862317f…/KP_EXPLANATION_EN 05180006…/KP_EN 9d905cfe…/KP_JA_MEANING b12c8721…)、a2/b1b plan status=OK | 0 |

- **text小計**: runner `cost.json` total=JPY66.677(Gemini RF cached割引を適用しない保守側)、`audit/cost_by_stage_text_03.json`(`er019_bape_cost_03.py`)計算値=66.324。Research+Ledger: LLM 4.515+web_search 36.8(23回x約1.6)=41.315。E2E上限180に対する残(text小計後)=約113.3(cost.json基準)。当日(JST 2026-10-17)累計=304.1+66.677=約370.8。
- **Review Queue**(`review_queue/post_en/boredom_aggression__run_bape_01/{b1b,a2}__rf*/queue.json|md`、判定はHuman Review側): b1b候補2件(s20「The only choice was to reduce it」、s38 findings示唆の強さ)/a2候補4件(例s18「after watching」時点表現、s26「the other groups」比較範囲)。いずれも候補一覧で合否判定ではない。
- **CP-B所見**: Ledger内で相関を因果と断定したFactは無し(CORRELATIONAL 5件[F02/F03/F09/F10/F11]、無作為割付実験の因果記述`CAUSAL_STATED_BY_SOURCE` 4件[F04〜F07]で、いずれも「この短時間の動画操作と選択課題に限定」とnotes_for_writerで制約)。参加者・条件・限界は各Factのscope/conditions/notes_for_writerに記載、F08がAMBIGUOUSとして著者の限界を保持。
- **流用禁止検査**: `verified_fact_ledger.txt` sha256=`701612d8…b0ac`は`er0*`配下の既存596件の同名ファイルのいずれとも不一致(0件一致)。`reused:false`。ledger再利用ログ(「生成済みLedgerを再利用」)は同一run内の後続stageによる自run成果の参照。
- **成果物**: `run_bape_01/{research_ledger,storyline_b3,ja_writer,b1b,a2}/`、`writer_run_summary.json`、`cost.json`、`raw_usage_log.jsonl`、`audit/cost_by_stage_text_03.json`。音声側`er019_output/family_x_audio_production_wiring_01/boredom_aggression__run_bape_01/`(plan only)。
- **T-2追記(次委任S7〜へ)**: (1)差分再生成=`--only-segments`(tts専用)・`--scaffold-only kp`(KPのみ)がrunnerに実在、(2)Master Audio Store再利用=固定shell(welcome/preview_intro等)と同sha音声のみ(本記事の新規本文は再利用不可)、(3)`--budget-jpy 70`(scaffold/tts用、既定150)を明示、(4)想定外の全再生成が判明したらAPI前にSTOP。
- 気づき(Production仕様変更の提案ではなく記録): タイトル案「Bad-Guy Switch」等の表現が論文の対象(サディスティック攻撃性・特性サディズム)に対し口語的に強い可能性。Human Review/Fable判定対象。
