# E2E_PLAN_01(FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01 委任_01、2026-10-18)

**転用元**: `docs/research/FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01/E2E_PLAN_01.md` §1〜§11(THEME/slug/out-dir/run-labelのみ置換)。Python=`.venv/Scripts/python.exe`。
**ユーザー原文**: `docs/pm/delegation_log/2026-10-18_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01_USER.md`(5312文字、sha256=`81b8b986843fb80ca914645aed1dd0c30c5ba2cd1141856fff8477a94325a652`)。
**到達上限Status(委任_01)**: `TEXT_STAGES_COMPLETE_AUDIO_PLAN_READY_PENDING_FABLE_CP`(音声有料工程S7〜S11は委任_02)。

## 1. 開始条件チェックリスト(2026-10-18 S0、1つでも未達なら有料生成しない)

| # | 条件 | 確認結果(2026-10-18) |
|---|---|---|
| 1 | S3がStd日本語Preview/Commentの正式Style(新規run既定) | **PASS**: `er019_family_x_style_profile_01.py:187` `DEFAULT_NEW_RUN_PROFILE = PROFILE_FX_20261017`、`SUPPORT_JA_STYLE_S3_SHA256`=`060c08fd…923f33`(`:159`)。python importで`DEFAULT_NEW_RUN_PROFILE`=`fx_20261017`を実測。 |
| 2 | retry/fallback/regeneration整合 | **PASS**: `er019_family_x_s3_wiring_01_test_01`+`style_profile_01_test_01`+`entertainment_production_runner_01_test_01` 計97件OK(実行、本日)。 |
| 3 | Production runtime evidence | **PASS**: BAPE run_bape_01(`audit/style_profile.json`等)・Coffee s3prod。 |
| 4 | 必要テストPASS | **PASS**: 上記97件。 |
| 5 | CURRENT_SPEC `PRODUCTION_WIRED`記録 | **PASS**: `CURRENT_SPEC.md:1656`節 Family別配線Status表のX列: PD06/S3/E1/K2/P8-KP/P7/6%減速/AUW/SRC=`PRODUCTION_WIRED`(2026-10-17 Fable)、M2P0+A・Risk Flagger=`PRODUCTION_WIRED`(`:1254-1266`/`:1157`節)。 |
| 6 | Git反映 | **PASS**: `git status --porcelain` が style_profile/entertainment runner/audio runnerに対し空(非dirty)。HEAD=`6d0973185`。 |
| 7 | Fable独立受入 | **PASS**: BAPE E2E受入(OPEN-408 USER_ACCEPTED、2026-10-17)・委任_01でFableが本計画の実行を指示。 |
| 8 | STOP | **PASS**: `tools/stop_scope_check_01.py --managed-id FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01`=rc0 stop:false(`docs/pm/delegation_log/2026-10-18_MEY1_stop_check.json`)。 |
| 9 | 出力dir非存在 | **PASS**: `er019_output/middle_east_yemen_saudi`は実走前に存在せず(S0で`audit/`のみ作成)。 |

## 2. テーマ・slug・out-dir

- `--theme`: ユーザー仮題をそのまま渡す(Fable決定): `中東情勢が悪化、イエメン・サウジ周辺で攻撃続く`。BAPEは英語1段落指示文を渡したが、今回はFable指示に従い日本語仮題のまま(英語補助文は付けない。Researchの事実受入は§12のチェック表で行う)。
- slug=`middle_east_yemen_saudi`、run=`run_mey_01`、run-label=`MEY-E2E-01`、out-dir=`er019_output/middle_east_yemen_saudi/run_mey_01`。audio側(AR既定derive)=`er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_01`。

## 3. テーマ選定
ユーザー選定(2026-10-18指示§1)。PM_GOVERNANCE 13節の候補提示は不要(区分A)。仮題の最終見出しはResearch事実で決定可。`er019_output/**/entry_point.json`に同テーマの既存runなし(旧記事・他Trial成果物の流用なし)。

## 4. 工程表(BAPE §4転用)
共通: 各stage前に`tools/stop_scope_check_01.py --managed-id FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01 --run-dir er019_output/middle_east_yemen_saudi/run_mey_01 --out <json>`(rc=3なら中止)。`TTS_EXECUTION_MODE=STANDARD`(音声runner)。

| # | 工程 | コマンド | STOP/Gate |
|---|---|---|---|
| S0 | 実走前JPY0 | §1全PASS・当日累計集計 | 未達=開始しない |
| S1 | Research+Verified Fact Ledger | runner `--stage research`(`--budget-jpy 110`) | budget超過STOP、`reused:false` |
| S2 | B3(Sol) | `--stage storyline_b3` | model_id不一致STOP |
| S3 | W-1 R0→R1→R2 | `--stage writer` | 記号Validator STOP |
| S4 | Advanced英語化+IOL+RF b1b | `--stage advanced` | IOL spec_ok=false=STOP |
| S5 | Standard調整+RF a2 | `--stage standard` | text runner終端 |
| S6 | 音声plan(JPY0) | audio runner `--level both --stage plan` | `audit/style_profile.json` 6 role sha確認(CLI指定なし) |
| S7〜S11 | KP scaffold/TTS/AUW+Assembly/試聴ページ | **委任_02(Fable CP後)** `--budget-jpy 70` | 本委任では起動しない |

## 5. 仕様照合表(BAPE §5の11行転用。値は実走で`audit/`から再確認)

| 対象 | 正式仕様 | 確認方法 |
|---|---|---|
| B3/Writer R0〜R2 | Sol、W-1 | `storyline_b3/runtime_evidence.json` `model_id_actual`、`writer_run_summary.json` |
| Std日本語Preview/Comment1〜4 | S3 | `audit/style_profile.json` SUPPORT_JA sha `060c08fd…` |
| Full Story | PD06 | FULL_STORY sha `3a680861…` |
| KP英語 | K2 | KP_EN `9d905cfe…` |
| Std KP日本語意味 | P8-KP | KP_JA_MEANING `b12c8721…` |
| Adv KP英語解説 | P7 | KP_EXPLANATION_EN `05180006…` |
| Adv Preview | E1 | PREVIEW `8862317f…` |
| KP候補・選定 | M2P0+A | 委任_02で `kp_supply=m2` 確認 |
| IOL | 原則2文、必要時3文 | `writer_run_summary.json` `in_one_line` |
| Std Full Story | 6%減速 | 委任_02で `slowdown_info` 確認 |
| 音声QA | AUW | 委任_02 |

契約所在: Risk Flagger / Fact Lock = `CURRENT_SPEC.md:1157`節(Family X Production経路 W-1 Fact Lock Writer + Risk Flagger + Review Queue)、AN3/Fact Lock数字規則=`:905-907`。

## 6. 流用禁止の担保
新out-dir(実走前非存在)、Family Xに`reuse_from`機構なし、Research/Ledger/B3/Writerは引継なし、RLCT(er082)方式(検索上限・Select-then-Verify)不使用。実走後に`runtime_evidence.json` `reused:false`と`verified_fact_ledger.txt` sha不一致(他run既存ledger)を確認。

## 7. 費用見積
BAPE実績: text 66.677 / audio 23.223 / 合計89.900(`audit/cost_by_stage_e2e_04.json`)。本件上限JPY180(ユーザー承認、text `--budget-jpy 110`+audio `--budget-jpy 70`)。情勢調査のためResearch/Ledgerの検索回数が増えうる(BAPE: 検索9+14回、36.8円)。超過見込みでSTOP。

## 8. 当日(2026-10-18 JST)費用
`docs/pm/tools/daily_dev_cost_01.py --date 2026-10-18` S0時点 adopted=JPY86.13(並行RLCT Stage 1b分、log基準)。本件上限180を加えても1,000円以内(RLCT上限493+180=673)。

## 9. STOP条件
ユーザー指示§6(重要事実を検証できない/Fact Lock・HR等のGate発火/既存経路で解決不能な品質問題/費用上限超過見込み/未承認仕様が必要/Production・音声検証の重大問題)。同種失敗2回・外部停止・原因不明rc≠0が2回=再起動せずSTOP(26節)。

## 10. 報告様式
BAPE §10と同じ(工程別円表、実測/推定/未取得区分)。

## 11. SSOT追記
OPEN_ITEMS(新規OPEN)、DECISION_LOG、USER_DECISION_REGISTER(費用180承認)、REPORT_LEDGER。

## 12. Research受入チェック表(ユーザー§3の7項目。Production Prompt変更ではなく成果の受入チェック。S1後、2026-10-18)

出典=`research_ledger/fact_ledger_draft.json`の`source_url`(1 Factにつき1 URL)と`fact_ledger_verification.json`の検証メモ。Reuters/AP等の独立報道はLedger上に**0件**(全Factが当事者・公的機関・当事者系通信社の発表)。

| Fact | 日時/場所 | 主体 | 標的・被害 | 発表元の区分 | 報道時点の明示 | 出典(Ledger記載) |
|---|---|---|---|---|---|---|
| F01 | 2026-10-09 イエメン複数前線・サウジ民間/エネルギー施設 | 国連特使(評価) | 戦闘激化 | 国連DPPA発表(評価) | 特使の10/9説明 | dppa.un.org 1本 |
| F02 | 10/6-7 アブハ・リヤド空港 | 攻撃主体=未特定 | アブハ死2負28、リヤド死1負8 | サウジGACA発表 | 発表時点の人数 | spa.gov.sa 1本 |
| F03 | 10/8 リヤド空港2件 | 未特定 | 死3、負傷者数未公表 | GACA発表 | 10/9発表 | spa.gov.sa 1本 |
| F04 | 10/10 リヤド空港 | 未特定 | 死12負309(10/11続報時点、後続13人は別時点と明記) | GACA発表 | 時点区別あり | oananews(SPA転載)1本。F11(国連特使、12人/300人超)で別系統の裏付け |
| F05 | 10/11午後 リヤド空港 | 未特定 | 負傷者あり・詳細未確定 | GACA発表 | 発表時点 | spa.gov.sa 1本 |
| F06 | 10/11 リヤド空港付近 | 連合軍報道官発表 | 巡航ミサイル迎撃 | 連合軍(当事者)発表 | 発表 | spa.gov.sa 1本 |
| F07 | 10/11夜 ダンマーム空港 | 未特定 | 損害評価中 | GACA発表 | 発表時点 | spa.gov.sa 1本 |
| F08 | 10/13夜 ダーランのアラムコ管理棟 | 未特定 | 小規模火災・死傷者なし(省関係者) | エネルギー省関係者(報道) | 報道10/14 | okaz.com.sa 1本 |
| F09 | 10/15 マリブ市内住宅地域 | フーシ派(マリブ県メディア局の報告) | 弾道9・飛翔体7 | イエメン政府系SABA(当事者側報告) | 帰属明示(独立検証なし) | sabanew.net 1本 |
| F10 | 10/16 アデン国際空港 | フーシ派(アデン治安局の発表) | ミサイル2発、初期情報で死者未確認 | アデン治安局(当事者側) | 初期情報と明示 | media.aden-gov.net 1本 |
| F11 | 10/11 国連特使声明(10/10リヤド) | 国連特使 | 死12・負傷300人超(サウジ当局引用)、和平への影響=特使の評価 | 国連OSESGY | 時点明示 | osesgy.unmissions.org 1本 |

ユーザー§3の7項目に対する判定:
1. 日時・場所・主体・標的・被害: 日時・場所・標的・被害はLedgerに明記。**攻撃主体はF02〜F08で「未特定」**(Ledgerが推測せず保持=項目6に適合。一方で記事で「誰が」を語れない制約になる)。
2. 当事者の立場の混同: フーシ派・イエメン政府・サウジ・連合軍・イランのうち、イランはLedgerに登場しない。混同なし。
3. 当事者発表 vs 独立確認: 全Factが当事者・公的機関発表で、**独立確認(Reuters/AP等)はLedger内0件**。各Factのnotes_for_writer/conditionsで帰属は保持。
4. 数字の報道時点: F04に「12/309は10/11続報、13人は別時点」と明記、他も発表時点を保持。
5. 過去 vs 新しい攻撃: 全Factが2026-10-06〜10-16の範囲。過去事件の混在なし。
6. 推測を事実化していないか: 攻撃主体・動機・報復関係をLedgerは記載せず(帰属不明のまま保持)。F11の因果は`CAUSAL_STATED_BY_SOURCE`で特使の評価と明示。
7. 中心Factの複数出典: Ledger記載は**全Fact 1 URL**。ただし中心Fact(死傷12/309=F04)はF11(国連特使がサウジ当局報告として引用)で別系統の裏付けあり。F01・F09・F10・F02/F03等は1出典(いずれも当事者発表として帰属明示)。

受入判定(Sonnet所見): 事実の取り違え・過去混在は認められない。**ただし「独立確認0件」「1 Fact 1 URL」「攻撃主体未特定」はユーザー§3項目3・7の理想に対する不足候補**。Fable判定対象(Prompt改変・手動Fact追加はしていない)。

## 13. 実走記録(委任_01、2026-10-18、text工程S1〜S5+S6 plan。各stage前stop_scope rc0・stage 1回ずつ・rc=0・再起動0)

- runner=`er019_family_x_entertainment_production_runner_01.py`、`TTS_EXECUTION_MODE=STANDARD`、`PYTHONIOENCODING=utf-8`(consoleのbash tee文字化け回避のみ)、`--budget-jpy 110`、`--run-label MEY-E2E-01`。コマンドはPowerShell Tee-Objectをbash teeに置換(他は委任文と同一)。
- S1: Research gpt-6-luna facts=11・web_search 15回、Ledger VERIFIED11/AMBIGUOUS0/REJECTED0(web_search 5回)、`reused:false`。
- S2 B3: gpt-6.1-sol、attempts1、**選定Factは F11 の1件のみ**(F01〜F10はfact_tests=excluded。`storyline_b3/fact_selection_evidence.json`)。
- S3 W-1: R0/R1/R2 Sol(factlock_r0__r1_r2_independent_sol61)、再生成なし。
- S4 Advanced: STRUCTURE_PASS attempts1、IOL 2文・spec_ok:true、RF b1b OK候補2件。S5 Standard: STRUCTURE_PASS attempts1、checks_failed空、numbers_missing/added空、IOL 2文・spec_ok:true、RF a2 OK候補3件。
- 記事: タイトル「Why Does “Peace” Appear in Airport News?」(日本語: 空港のニュースに、なぜ「和平」が出てくる?)。In One Line(Adv)=「A UN envoy said the Riyadh airport attack could make peace efforts in Yemen harder. Saudi authorities supplied the casualty figures, while the effect on peace was the envoy’s assessment.」(Std)=「The UN official for Yemen said the Riyadh airport attack could make peace efforts harder. Saudi officials gave the death and injury numbers, while the official described the effect on peace.」
- **品質所見(Fable CP要判定)**: (a) 記事は国連特使発言(F11)1件だけに基づく「ニュースの読み方」型エッセイで、ユーザー狙い「なぜイエメン周辺の紛争がサウジと地域全体に影響するか」の背景(F01の全面戦闘、F02〜F10の連続攻撃・被害)をほぼ使わない。(b) 冒頭の「空港の出発案内板に『Peace in Yemen』と表示された」場面はLedgerに無い創作的導入で、RF(luna A4)がb1b/a2ともs3を「台帳で確認できない事実」と候補化。(c) RF a2 s31/s46は「the attack」「could make」の範囲・法助動詞の候補(F11は『攻撃』全般について『困難にする』と評価)。(d) In One Lineは特使の評価を明示しており因果の誇張は無いが、「could」はF11の断定的評価より弱い。いずれもRF候補一覧であり合否判定ではない。Human Review/Fableの判断対象。本委任ではProduction変更・再生成・Prompt改変をしていない。
- RF候補: b1b 2件(s3 departure board、他1)/a2 3件(s3、s31、s46)。Fact Lock/Human Review/Review Lock発火: Writer段のFact Lock数字規則違反による停止なし、HR待ちstatusなし(RF候補はReview Queueに保存)。
- S6: `er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_01/audit/style_profile.json` profile_id=fx_20261017、`entry_point.json` profile_source=default_new_run_fx_20261017(CLI指定なし)、6 role sha全一致(SUPPORT_JA 060c08fd…/FULL_STORY 3a680861…/PREVIEW 8862317f…/KP_EXPLANATION_EN 05180006…/KP_EN 9d905cfe…/KP_JA_MEANING b12c8721…)、a2/b1b plan status=OK、JPY0。有料TTS未起動。
- 費用(実測=usage x pricing_snapshot計算値、`audit/cost_by_stage_text_01.json`、`er019_mey_cost_01.py`): runner cost.json total=JPY56.621(Gemini RFをcached割引なし保守計算)、集計スクリプト計算値=56.533。Research 26.995(LLM 2.995+web_search 15回24.0)/Ledger 9.11(LLM 1.11+web_search 5回8.0)/B3 5.993/Writer R0 6.234・R1 3.08・R2 2.375/Advanced 0.332/RF b1b 0.792/Standard 0.527/RF a2 1.095。web_search計20回(32.0)。retry/fallback: RF gemini A4 a2が内部attempt2で1回(0.0)。text残(上限110)=約53.4、E2E残(上限180)=約123.4。当日累計(daily_dev_cost_01、log基準)=217.4/1,000(RLCT等並行分を含む)。
- 成果物: `er019_output/middle_east_yemen_saudi/run_mey_01/`(research_ledger/storyline_b3/ja_writer/b1b/a2/writer_run_summary.json/cost.json/raw_usage_log.jsonl/audit/cost_by_stage_text_01.json/console_s1〜s6)、review_queue、audio plan dir。

*`PYTHONIOENCODING=utf-8`以外のRunner引数・環境差異なし。*

## §14 Fable CP-C判定と再生成記録(委任_02、2026-10-18)
- Fable CP-C=NG(根拠: 冒頭の「空港案内板に“Peace in Yemen”」はLedger外の創作/B3がF11のみ選定し狙い未達)。対応=既存機構でB3再選定1回+下流再生成(Prompt・Gate・Style・Ledger不変、Research再実行なし)。
- E-1 既存仕様確認: runner usage `er019_family_x_entertainment_production_runner_01.py:33`(`--regenerate-stage storyline_b3|writer|advanced|standard`)。実装は:410-413(B3再生成)、:429-432(Writer)、:449/:461(Adv/Std)。**下流の自動再生成は行わない(安全側)**=:253「(下流の自動再生成は行いません=安全側)」、B3再生成後にWriterをreuseしようとするとU-1 PROVENANCE_MISMATCHでSTOP(:246-254)。したがって委任文の「stage再生成が下流をstale化し再生成する」のうち、再生成は自動ではなく段階別に明示実行が正式手順(`--stage X --regenerate-stage X`をstoryline_b3→writer→advanced→standardの順に各1回)。各stageは1回ずつ(retry/2回目の再生成なし)。
- 実行(実在形): `--theme ... --slug middle_east_yemen_saudi --out-dir ...run_mey_01 --run-label MEY-E2E-01 --budget-jpy 110 --stage <S> --regenerate-stage <S>`、S=storyline_b3/writer/advanced/standard。console=`console_regen_b3_02.txt`・`console_regen_s3_02.txt`〜`_s5_02.txt`。初回成果保全=`run_mey_01/_before_regen_01/`。

| 項目 | 初回(_before_regen_01) | 再生成後 |
|---|---|---|
| b1bタイトル | Why Does “Peace” Appear in Airport News? | Airport Attacks: Another Crisis the Damage Figures Alone Cannot Show |
| 選定Fact | F11のみ(F01〜F10 excluded) | F11のみ(F01〜F10 excluded) |
| 選定storyline | 空港攻撃の民間被害+特使の和平困難評価 | 同(10月11日の特使の非難・警告) |
| In one line(b1b) | A UN envoy said the Riyadh airport attack could make peace efforts in Yemen harder. Saudi authorities supplied the casualty figures, while the effect on peace was the envoy’s assessment. | The UN envoy for Yemen warned that attacks on Saudi airports would make efforts to end Yemen’s conflict harder. Readers should look beyond casualty figures and keep both lives at stake now and future peace in view. |
| Risk Flagger候補 | b1b 2件/a2 3件(luna A4=冒頭の案内板場面s3ほか) | b1b 0件/a2 0件(status=OK) |
| HR/Lock | 発火なし | 発火なし(symbol_qa findings=[]、r2 rerun=False) |
| 費用(JPY) | 56.621 | 再生成分23.260(B3 6.673/W-1 R0-R2 14.264/Adv 0.343+RF 0.92/Std 0.270+RF 1.03)、text累計79.881/110 |

- Ledger外具体描写の突合(再生成後b1b/a2): 固有名詞・場面・数字14項目を突合。UN envoy for Yemen=F11/Saudi authorities・Riyadh airport・12人死亡・300人超負傷=F11(帰属付き)/Riyadh・Abha空港の同週攻撃=F11/地域安全保障の脅威・和平努力困難=F11(特使の評価と帰属明示)=一致。Ledger外の具体事実・創作場面=0件(「空港が攻撃された」引用は報道一報の言い換え、「Imagine if it were an airport you used」は読者への仮定と明示された非事実、「two clocks」は比喩)。初回の“Peace in Yemen”案内板のような事実風創作場面は消失。
- 数字の時点明示・帰属: 帰属は良好(死傷者数=Saudi authoritiesの発表を特使が引用/和平困難化=特使の評価と分離)。**本文に日付(10月10日・11日)が無い**(初回も本文中のOctober出現0=同じ)。「that same week」のみ。
- 評価材料(Fable CP2用): 創作場面は解消・RF0。一方B3は再びF11のみ選定(選定理由はF02-F10が「F11で説明可能/背景のみ」)で、ユーザーの狙い(なぜ周辺の紛争が地域全体に影響するか)を複数Factで語る構造にはならず「ニュースの読み方」型エッセイのまま。再生成2回目は行わない(STOP方針)。

## §15 Fable CP2判定(USER_DECISION_REQUIRED)(委任_03、2026-10-18)
- 事実性・中立性=PASS: Ledger外の創作描写0件、Risk Flagger候補0件、帰属・数字の時点分離は良好、因果誇張なし(再生成後タイトル "Airport Attacks: Another Crisis the Damage Figures Alone Cannot Show")。
- 狙い適合=NG: B3が2回連続でF11(国連特使発言)のみ選定(F01〜F10 excluded)。記事は「ニュースの読み方」型のメタ・エッセイで、ユーザーの狙い「なぜイエメン周辺の紛争がサウジ・地域全体に影響するのか」を一連の事実(10/6〜16の空港・アラムコ・マリブ・アデン)で語れていない。
- 判定根拠: 同じ問題が2回再現(原則5)。改善にはB3選定基準(Prompt)変更=Production挙動変更が必要でFable権限外。Ledgerも攻撃主体が公的発表で未特定・独立報道0件・1Fact1URLの限界があり、Research再実行でも達成保証なし。ユーザー§6「既存Production経路では解決できない品質問題」に該当。
- 結論: 音声工程へ進めずSTOP、USER_DECISION_REQUIRED #112。
- 選択肢: (a)この記事のまま音声工程へ(見込み約JPY25〜30、E2E累計約105〜110/180) (b)本記事を見送り(text実費JPY79.9で終了、成果物は保全) (c)Research再実行1回(見込み約JPY36+下流約25=約61、E2E累計約141、音声で180に接近、保証なし) (d)B3選定基準の改善を別Trialとして起票(Prompt変更=Production Gate対象、本記事とは切り離す)。Fable推奨=(b)+(d)。(a)はユーザーが本文を読んで許容できる場合のみ。
- 本委任_03はSSOT記録のみ(JPY0、コード/Prompt/成果物変更0、音声工程未起動)。
