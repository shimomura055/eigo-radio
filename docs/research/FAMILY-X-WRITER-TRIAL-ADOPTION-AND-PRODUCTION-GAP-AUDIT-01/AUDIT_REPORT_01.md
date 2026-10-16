# AUDIT_REPORT_01: Family X Writer採用漏れ／Production反映漏れ 統合監査報告書

管理ID: `FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01` 委任_02(Part A/B/C統合)
作成: 2026-10-16 / 調査基準commit `69817ebde`(work/post-merge-01) / read-only・JPY0 / 到達Status=`AUDIT_COMPLETE`(未確認事項は§13に分離)
**Opus独立レビュー前**(Fableが本日2回目の任意レビューを予定。レビュー後に内容が変わりうる)。本書提出でSTOP。Trial・実装・Coffee再制作・SSOT是正には進まない。
略記: CS=`CURRENT_SPEC.md` / DL=`DECISION_LOG.md` / OI=`OPEN_ITEMS.md` / REG=`docs/pm/USER_DECISION_REGISTER_01.md` / FX記録=`docs/pm/delegation_log/2026-10-16_FAMILY-X-20261016-0900-USER-DECISION-RECORD-01_USER.md`(ユーザー原文、09:00記録) / PA・PB・PC=同フォルダのPART_A/B/C。
行番号は全て基準commit時点で再照合済み(訂正は§11)。DLの行番号はPB・PA記載値に+2が現行値(8箇所で実測、§11)。

---

## §1 結論: Family XのWriter仕様は本当に最新か

**回答: 「一部」。** 日本語Writer本体は最新で配線済みだが、09:00にユーザーが承認した音声系4仕様とIn One Lineは承認済み・未配線で、完成品にはまだ反映されない。

非エンジニア向けの要約: 日本語の記事を書く部分(B3→R0→R1→R2)は、承認どおり全て `gpt-6.1-sol` で動き、Fact Lockの構造もTrialと同一のまま実装されている。一方、「良いTrial成果が実際の記事・音声に反映されているか」という問いには、次の3群で「いいえ」が残る。(1) 09:00に承認された PD06・K2・P8・P7・In One Line(基本2文)は、Family Xの正式経路にまだ入っていない(PD06/P8/P7のPrompt文字列のshaがProduction側の .py に0件、K2はFamily Zにだけ存在)。In One Lineは今も「Exactly one sentence」のままで、実際に作られた記事も1文。(2) 仕様書(CURRENT_SPEC等)に「置換済みなのに注記がない」古い記述が複数あり、次の担当者が旧方式を現行と誤読する。(3) VALIDATED等の良いTrial成果のうち、採否をユーザーに問い直していないものが複数ある(§3)。

| 観点 | 判定 | 根拠(file:line) |
|---|---|---|
| 日本語B3/R0/R1/R2=gpt-6.1-sol(初回・retry・regeneration) | **Yes(問題なし)** | `er006_model_routing_contract_01.py:134,137,138`(リテラル固定、env上書き0件)、`er019_family_x_entertainment_production_runner_01.py:153`、`er053_family_x_factlock_ja_writer_01.py:40,42`、実run `er019_output/meta/run_sol61_01`で4工程とも`gpt-6.1-sol`・mismatch=false(PA§5) |
| Fact Lock構造・R2入力=R1 raw・Prompt sha不変 | **Yes(問題なし)** | `w1:66,95`ほか(w1=`er053_family_x_factlock_ja_writer_01.py`)、`verbatim_shas()` 14キーが実run 2本の記録と全一致(PC§2 W3/W4)。adb15c30はモデル配線のみでPrompt本文不変(PA§6) |
| 09:00承認6仕様(PD06/K2/P8/P7/In One Line/A方式[変更不要]) | **No(未配線)** | §2。PD06/P8/P7のshaは Production .py に0件(Grep実測)、K2は Family X に無く Family Z(`er063_family_z_audio_01.py:154`)のみ |
| 実際の記事への反映(Coffee) | **No** | 現行Coffee記事は正式W-1 chainではなく`MAQ_TRIAL_W-1`(Trial出力の再利用、PA§5)。IOLは1文(PC§2 W9、`run_l3_01/b1b/article.md:22`) |
| SSOT記述の鮮度 | **一部(陳腐化あり)** | CS:829-831, 1169, 2462/2501/2519, OI:750(OPEN-248旧見出しStatus)ほか(§4・§7 P2) |
| AN3(Concreteness Control)第1文 | **変質(意図的な可能性、追認記録なし)** | `w1:131-139`が第1文を送らず第2文のみ保持(§4・§8e) |
| 英語化(Advanced/Standard)のWriterモデル | **Luna据置(判断記録なし)** | `er006…:48-50,105,110`(§4・§8d) |
| 死コード・Dangling | **軽微** | R0規則7(`w1:66,95`)、`open243_m1_enabled`(`er003_v1_n3_01_advanced_adaptation_generate.py:583,601`)、`jaw.run_ja_writer_o_r1_r2`(`er019_family_x_ja_writer_o_r1_r2_01.py:183`) |

---

## §2 承認済みなのにProduction未反映の一覧

承認原文: FX記録§2(ユーザー原文表)= CS:1203-1246(同小節の表)。「配線対象」は初回/retry/fallback/regenerationのうち反映が必要な範囲。全行`APPROVED_FOR_PRODUCTION`・Family X正式経路は未配線(Grep実測。`PRODUCTION_WIRED`ではない)。adv=`er003_v1_n3_01_advanced_adaptation_generate.py`、style_profile=`er019_family_x_style_profile_01.py`。

| # | 仕様 | 承認原文(file:line) | 正本Prompt/sha | 配線対象 | 現状(実測) | Blocking(Coffee再制作前に必要か) |
|---|---|---|---|---|---|---|
| 1 | Full Story TTS(Std/Adv)=**PD06** | FX記録§2、CS:1203表 | `er057_output/pace_trial_02/prompts/prompts_pace_02.md:74-82`のPD6(名称対応)、sha `3a680861…`・177文字(CS:1203小節の再計算) | Full Story TTS Style選択(profile)。初回/retry/regen/resumeはProfile record(`audit/style_profile.json`、style_profile:180)経由で同一Styleになる設計。fallbackの扱い要設計 | Production .py にshaヒット0。現行はN01(style_profile:104)、既定profile=`DEFAULT_NEW_RUN_PROFILE=n01`(:110) | **Yes**。ただし「正本Trial-02はAdv対象で、Std適用・6%減速併用は正本に明記なし」(CS:1203小節)=§8b |
| 2 | KP英語音声(Std/Adv)=**K2** | 同上 | `er057_tone_trial_kp_ja_gen_01.py:38-39`(B_SPECS["K2"])+`:33`B_GUARD連結、332文字、sha `9d905cfe…` | KP英語音声。retry/fallback同一Style | **Family Xに無い**。profileのroleはFULL_STORY/SUPPORT_JA(R2)/KP_EXPLANATION_EN(P3)/PREVIEW(E1)のみで、K2/M2は「後続Phase」と自記(style_profile:16-17)。**Family Z側には存在**(`er063_family_z_audio_01.py:154`) | **Yes** |
| 3 | KP日本語意味(Std)=**P8**(旧M2置換) | 同上 | `er057_std_kp_ja_style_trial_02.py:25`、sha `b12c8721…`(Trial-02のverbatim_match=true) | Std KP日本語意味 | shaヒット0。M2相当もFamily X profileに無し | **Yes**。注: 「P8」はFull Story style(2026-10-12のPD8→P8、CS:2671)とは別物(§11-1) |
| 4 | KP英語解説(Adv)=**P7**(旧P3置換) | 同上 | `er080_coffee_kp_pacing_trial_01.py:35`のp7「速度・リズムのバランス型」136文字、sha `0518000694…`(ユーザー指示原文`2026-10-16_FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01_USER.md:85-88`と一致) | Adv KP英語解説(`er019_family_x_kp_explanation_01.py`) | shaヒット0。現行はP3(Coffee限定profile`coffee_n01_r2_p3[_e1]`、CLI明示指定時のみ) | **Yes**。「同名別P7あり」(FX記録§3注)=§8a。OPEN-393(OI:902)は試聴待ちのまま |
| 5 | In One Line(Std/Adv)=**基本2文・必要時のみ3文** | FX記録§2、CS:1203表 | **正本未特定**(改修Promptは未作成)。Trial原稿のみ`er057_output/coffee_final_audio_assembly_01/IN_ONE_LINE_REWRITE_01.md` | Adv英語生成(`_advanced_in_one_line` `er012_e_family_entertainment_two_level_runner_01.py:327`)→Std継承→Comment4。retry(段落3分割retry、IOL再生成)も同Prompt(PC§2経路表) | 旧Prompt `"- Exactly one sentence."`が現存(adv:558)。実run=1文(PC§2 W9)。Comment4は「1文とは限りません」と指示(`er019_family_x_audio_plan_01.py:206-208`)でIOL生成と矛盾(PC§4 D2)。CS:583「中心1文+補足2文程度」とも未整合 | **Yes(最重要)**。Prompt作成が先(§8c) |
| 6 | KP選定優先順位=**A方式(現行)** | FX記録§2 | 正本=DL「FAMILY-X-KP-IDIOM-PRIORITY-ABC-TRIAL-01 委任_01」、`er064_output/kp_idiom_priority_abc_01/ABC_REPORT_01.md` | 変更不要(現行Prompt維持) | 配線差分なし見込み。**実Prompt逐語の再確認は本監査では未実施**(CS記載の「逐語一致をtest固定」を信頼) | No(確認のみ) |
| 7 | KP候補供給=**M2P0** | FX記録§2、DL 2026-10-13決定 | Prompt文字列なし(方式) | Coffee runtimeあり。Std側`CANONICALIZATION_INVALID`の未完了(OI:852、OPEN-343) | 配線済み・未完了(`PRODUCTION_WIRED`不付与) | **要確認**(OPEN-343、本監査では精読せず) |
| 8 | Hook Side output(R2完成後にLunaでHook1本) | DL NEWS-HOOK-POLICY-DECISION-01節(DL:9417、PB記載9415+2)、OI:357(OPEN-176) | Prompt未再確認 | R2後のSide output | Production .py(`er019*`/`er053*`/`er012_e*`)にHook stageのGrep 0件。OI自記も「未配線」 | No(比較観測用Side output)。引継ぎ可否はユーザー判断(§8g) |
| 9 | Adv Preview=E1(Coffee限定profile) | OPEN-350(OI:859) | 『calm, composed news anchor; steady and unhurried, clear and natural.』 | Adv Preview | OI:859は「未配線」と記載、style_profile:108に`coffee_n01_r2_p3_e1`が存在(OI記載は古い可能性、本監査では未精査)。既定profileは含まない | Yes(既定化と同時、§8i) |
| 10 | Comment4「最後に」2文のB1(Adv)展開 | OPEN-316(c)(OI:819)、V5決定A | A2側`audio_plan:221-238`には有り、B1側`:193-208`には無し | Adv Comment4 | 未展開(意図的に未決) | No(同時に片付けると良い) |

参考(承認済みで既に配線済み・問題なし): Sol統一(§5)、Fact Lock W-1、決定論B3 producer、Risk Flagger、旧Fact Checker撤去、AN3、Comment4(Std)、KP解説(P3)。

---

## §3 VALIDATEDなのに採否判断が未提示の一覧(「OIに載っている=保留」とは扱わない)

「ユーザー判断の証拠」はDLの逐語記述のみを採用(PB方法注)。DL行はPB+2。

| # | Trial/仕様 | 結果の要約 | 出典 | 判断証拠 | 推奨 |
|---|---|---|---|---|---|
| 1 | OPEN-237系: 台帳明確化(P')・多義語Note・Note転記(PB R06/R07/R08) | P'Trial(JPY34.85): HC-012型0、重大NG0、断定強化1件で保留。多義語Noteの自動生成は3ループで不成立。Rollback誤読0/22、曖昧→正の改善なし、N小で採否不能 | DL:20130-20245近傍(OPEN-233-LEDGER-CLARITY〜NOTE-TRANSFER-MATRIX)、OI:739 | **なし**(選択肢提示・Status判定のみ)。2026-10-08のFact Lock再設計後に整理した記録なし | **廃止方向の一括整理**(SUPERSEDED候補)。理由: notes_for_writerは決定論assemblerが制約ブロックへ転記済み(OI:750 OPEN-248、`er053_b3_deterministic_producer_01.py:141`)で、Trialの当初課題は別方式で吸収。ただしユーザー確認は必要 |
| 2 | RFの新仕様候補(a)台帳にない定量・事実の挿入検出、(b)確信度閾値による可変件数、(c)D2ベース+疑義時のみ専用呼出(D1コスト削減)(PB R41) | 候補のみ・未実装 | DL:20467-20514近傍 | **なし**。OI/REGに行もない | **継続(RF運用で実データが貯まってから再評価)**。(a)は事実混入の新型で価値の可能性あり=ユーザー判断で起票要否を決める |
| 3 | エンタメ性の代理指標v1(`docs/pm/stage0_01/narrative_elements_v1.md`)(R19) | 暫定・未承認 | DL:20247近傍 | なし | **廃止または正式化のどちらか**。現在は参照するコード/運用手順なし=推奨は「廃止」 |
| 4 | Pre-sorter Blind Trial(R40) | GPT系3モデルのみ、Anthropic3モデルは鍵なしで未実行。Production配線しない旨はユーザー明言(`docs/pm/delegation_log/2026-10-10_RISK-FLAGGER-PRODUCTION-WIRING-01_01.md:4`) | DL:20520近傍 | 再実行要否のみ未回答 | **不要(クローズ候補)** |
| 5 | R0モデル影響Trial(R30) | パーサ欠落を是正し12本RF | DL:20478-20493近傍 | UDRのまま。E案(DL:20573)で実質置換 | **不要(E案に吸収と明示記録)** |
| 6 | FACTLOCK-ASTRA-E2E-TRIAL-01 単体(R33) | G2完走、Fable最終判定=UDR(選択肢(a)〜(e)) | DL:20369-20436 | Trial単体の採否回答なし。W-1採用(DL:20532)で実質採用 | **不要(W-1に吸収と明示記録)** |
| 7 | OPEN-233-DIRECTIONAL-MISREAD-SAFETY系(R22)・STAGE0/T1/T3/T4/ACTION-POLICY系(R23) | R22 TRIAL-03=REJECTED、R23はFAIL(機械適用) | `er052_output/open233_*_01/*_RESULT.md` | R23の結果がDL/LED/OIに語として0件(PB§3-E-3) | **SSOTへ結果のみ記録**(開発側是正、重要度低) |
| 8 | ALL-6-LUNA(R29)の英語化モデル配置 | 48本生成、費用/本JPY9.46→4.29、事実NGは評価者で割れる | DL:20254-20298、OI:743 | 判断7=Luna方針(DL:20263)は「全体のProduction方針」。**英語化をLuna/Astra/Solのどれにするかの個別比較・判断は無い** | **ユーザー判断**(§8d) |
| 9 | R3: OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01(NOT_SUPPORTED)・R5 Lane B(REJECTED) | 不採用で確定済み | DL:20229、DL:20546 | あり(Lane B)/Fable判定のみ(R3) | 対応不要 |

Trial成果のうち「良いのに反映が無い」ことが確定しているのは §2 の#1-#5(09:00承認済み、配線のみ)と#8(Hook)。OPEN-237系・RF候補・代理指標は「良い成果」ではなく「不成立/候補のみ」であり、反映漏れというより整理漏れ。

---

## §4 採用済みだが部分配線・旧経路残存の一覧

| # | 項目 | 実態(file:line) | 影響 | 区分 |
|---|---|---|---|---|
| 1 | OPEN-238 Precheck(数値偽陽性修正) | コードは`er052_open233_self_recovery_precheck_01.py:179`、flow runner:8405(`er052_open233_self_recovery_flow_runner_01.py`)。Family X Production(`er019*`/`er053*`/`er012_e*`)からの参照0件。名目`PRODUCTION_WIRED`(DL:20225)だがOPEN-233 Self-Recovery自体が2026-10-10にSUPERSEDED(CS:2538) | Family Xの完成品に影響なし(到達経路なし)。OI:740の注記なし | 開発側是正(注記)+表記はFable判断 |
| 2 | AN3固有名詞方針がJAのみ(OPEN-220) | 英語側`ADVANCED_VOCAB_RULE_V2_BLOCK`(adv:144,350)は固有名詞KEEP。CS:886は「Advanced化Promptは変更しない」と明記 | 英語最終成果物に固有名詞が多く残りうる(影響は当初想定より小さい可能性、OI:403) | ユーザー判断・優先度低 |
| 3 | AN3第1文の置換 | `w1:131-139`の`build_r0_block`がAN3第1文(数字・時刻の抑制)を送らず、Fact Lock数字規則(5)で置換、第2文のみ逐語保持。runtime_evidenceのshaは定数のsha(実送信文のshaではない) | 「数字を極力使わない」というAN3の核がFact Lockの数字規則に置換されている。Fact Lockはユーザー承認済み構造で誤りではないが、CS:905/1169は「AN3はR0に含まれたまま」と記述 | SSOT精度(開発側)+追認(ユーザー、§8e) |
| 4 | 英語化(Advanced/Standard)=Luna | `er006…:48-50`(WRITER_MODEL=SUPPORT_MODEL=gpt-6-luna)、`:105`(STANDARD_A2_ADAPTATION)、`:110`(NATURAL_ENGLISH_ADAPTATION)。DL:20573は音声・翻訳・TTS・RF等を対象外と明記 | 日本語はSol、英語はLuna。判断記録なし | ユーザー判断(§8d) |
| 5 | Coffee限定profileはCLI明示指定専用 | `DEFAULT_NEW_RUN_PROFILE=PROFILE_N01`(style_profile:110)。`coffee_n01_r2_p3_e1`(:108)を付け忘れるとR2/P3/E1が黙って落ちる。FX記録§3は「Coffee限定ではなくFamily X全体」と明記しており、既定では共通化されていない | 再制作時の取り違えリスク | ユーザー判断(§8i)+開発側 |
| 6 | 旧`ja_writer_o_r1_r2`モジュールのLuna連鎖が残存 | `er019_family_x_ja_writer_o_r1_r2_01.py:45`(WRITER_MODEL=Luna)、`:183`(`run_ja_writer_o_r1_r2`、非test呼出0)、`:70`REVISION_INSTRUCTIONS。w1は定数のみ流用(`jaw.call_fresh`は呼ばない、PA§3) | 誤って呼ぶと旧仕様(Luna連鎖)で動く。隔離はtestのAST固定に依存 | 撤去要否はFable判断 |
| 7 | `open243_m1_enabled()`/`OPEN243_M1_ENV`が定義のみ | adv:583,601。呼出0(M1(a)は無条件ON) | 影響なし(死コード) | 開発側(撤去は別委任) |
| 8 | IOL Promptに「Trial-only guidance, not a strict rule... 12-18 words」文言がそのまま送信される | adv:561-563 | Trial由来の文言が本番Promptに混在 | §2 #5の改修時に併せて整理 |
| 9 | Std IOLの文数はAdv IOLに従属 | `er003_v1_n3_01_standard_a2_generate.py:522`は「保持せよ」のみ | Adv IOLを2文化してもStdで文数が保たれる保証のtestなし | 配線時にtest追加 |
| 10 | IOL文数のValidatorなし | `split_family_x_article_text_v2`は存在検査のみ(er012:296-304コメント) | 1文→2文へ仕様変更しても検出不能 | 新規仕様候補=実装せず提案のみ(§12-B) |
| 11 | Dangling検査の死角 | `er053_dangling_reference_check_01.py`のSCOPE_FILESにEN生成module(adv/std/scaffold)なし。PC実行9ファイルのhit=37、撤去対象の残存0(PC§4 D6) | EN生成moduleは走査外 | 開発側(範囲拡大は新規仕様候補) |

---

## §5 B3→R2 Sol統一の実装・runtime照合結果(PA要約)

結論: **問題なし(根拠付き)**。正式初回経路は main/HEAD でも `gpt-6.1-sol` 固定(PA§1-§7)。

| 項目 | 結果 | 証拠(file:line) |
|---|---|---|
| ユーザー承認原文(逐語) | E案(B3/R0/R1/R2=gpt-6.1-sol)、APPROVED_FOR_PRODUCTION | DL:20573(PA記載20571+2)。Closeout DL:20576(PRODUCTION_WIRED、merge adb15c30、rollback tag `rollback/pre-sol61-ja-allocation-01-20261011`)。FX記録§2で再確認 |
| routing単一出所 | 3キー=リテラル`gpt-6.1-sol`、`os.environ`0件、`require_model`(:170-190)がfail-closed | `er006_model_routing_contract_01.py:134,137,138` |
| B3初回/retry | 同一model引数(`for attempt in (1,2)`) | runner:153-157、`er019_family_x_storyline_b3_fact_selection_01.py:217` |
| R0/R1/R2初回 | `call_luna_r0`(名称は旧、中身はSol)/`call_astra`、返却model不一致でSTOP | w1:280,200,40,42 |
| R0記号再生成・R2記号再実行 | 同一関数・同一モデル、R2再実行は同一R1 raw | w1:355-364,421、PC§2経路表 |
| regeneration/resume | 初回と同関数。resumeはLLM呼出なし、旧Writer記事は`LegacyWriterProvenanceStop`で遮断 | runner:230-260 |
| R2入力=R1 raw | 実装済み | w1:402,407,421 |
| runtime evidence | META `run_sol61_01`: 4 stage全て`gpt-6.1-sol`、mismatch=false、18.499円、173秒。`verbatim_shas` 14キー全一致 | `er053_output/sol61_production_wiring_01/runtime_evidence_01.md`、`er019_output/meta/run_sol61_01/ja_writer/runtime_evidence.json` |

**留意(未確認、推測でPASSにしない)**: (1) 現行Coffee最新run `er019_output/coffee_prices/run_v5_ms_01`は`chain_method="MAQ_TRIAL_W-1"`(Trial armのE案マスター再利用、中身のmodelはSol)で、**正式runnerの`W-1`経路による実走ではない**。FX記録の「Researchから全面新規生成」で初めて、正式W-1のCoffee実走証跡が取れる。(2) **Sol配線後にretry系(B3 attempt2・R0記号再生成・R2再実行)が実際に発火した証跡はない**(META run_sol61_01は発火なし)。コード上は同一関数の再利用。(3) Sol配線後の正式runner実走はMETA N=1のみ。(4) unit testは本監査では再実行していない(DL:20576に関連171 passed記載)。

---

## §6 過去Trialから正式仕様への追跡マトリクス

詳細(11項目判定、ユーザー判断出典、問題・必要対応)はPB§2(R01-R45)が正本。本節は統合列(Production配線 × retry/fallback/regen × 現在Status)を示す。凡例: ○=正式経路に実装あり(初回+retry/regen同一)/△=一部/×=未配線/―=対象外。DL行はPB+2。

| 行 | 対象 | 判定 | 正式仕様 | Production | retry/regen | 現在Status | 区分 |
|---|---|---|---|---|---|---|---|
| R01 | B3 Fact Selection | 配線 | CS:829,1165 | ○ runner:147-157 | ○同一 | PRODUCTION_WIRED | 問題なし |
| R02 | B3 Diversity/Retry原因 | V/NC | CS:829 | R01に吸収 | ― | 吸収 | 問題なし |
| R03 | B3 Brief構造 | NS | なし | × | ― | NOT_SUPPORTED | 問題なし |
| R04 | B3 Fact/指示分離 ROOTFIX | V(案D) | CS:1165 | ○ `er053_b3_deterministic_producer_01.py:843` | ○全分岐 | PRODUCTION_WIRED | OI:750の見出しStatusが古い |
| R05 | Lane B注記自動化 | R | なし | × | ― | REJECTED | 問題なし |
| R06-R08 | OPEN-237系 | UDR | なし | × | ― | UDR | A(§3-1) |
| R09 | NG原因分析 | 分析 | なし | ― | ― | 完了 | 問題なし |
| R10 | 決定論B3 producer+契約 | 配線 | CS:1165,1186 | ○ | ○ | PRODUCTION_WIRED | 問題なし |
| R11-R12 | Fact Lock R0 / W-1 | 採用 | CS:1155,1169 | ○ w1:262-445 | ○(PC§2) | PRODUCTION_WIRED | D: CS:1169が旧配置のまま |
| R13 | R1/R2 Entertainment | 採用 | CS:829 | ○(W-1に置換) | ○ | PRODUCTION_WIRED(実装は別方式) | D: CS:829に置換注記なし |
| R14 | Astra R1/R2系列X | 採用 | CS:1169 | ○ | ○ | PRODUCTION_WIRED | 問題なし |
| R15 | Hook Side output | 決定済 | OI:357 | × | ― | OPEN | B(§2-8) |
| R16-R17 | Concreteness/AN3 | V | CS:886-957 | △(第1文置換) | ○ | PRODUCTION_WIRED | D(§4-3) |
| R18 | JA品質×モデル配置 | V | CS:1157,1159 | ○ | ○ | PRODUCTION_WIRED | F寄り: 品質マスター参照の運用手順なし(PB R18) |
| R19 | エンタメ代理指標 | 未承認 | なし | × | ― | 暫定 | A(§3-3) |
| R20 | AN3 T0配線 | 配線 | CS:886-957 | △ | ○ | PRODUCTION_WIRED | D |
| R21 | 固有名詞のEN伝播 | M | CS:886 | JAのみ | ― | DEFERRED | C(§4-2) |
| R22-R23 | 誤読Safety/Stage0〜 | R/FAIL | なし | × | ― | REJECTED/FAIL | E(SSOT記録欠落) |
| R24 | OPEN-243 翻訳段NG | M | なし | M1(a)のみ | △ | OPEN | E: 「守り」が撤去済み |
| R25-R27 | Checker/Self Recovery | V→SUPERSEDED | CS:2462-2538 | × | ― | SUPERSEDED | D: Status行に注記なし(2538のみ) |
| R28 | OPEN-238 Precheck | V | OI:740 | × 到達経路なし | ― | 名目PRODUCTION_WIRED | C(§4-1) |
| R29 | ALL-6-LUNA/英語化 | M/判断7 | `er006…:48-110` | ○(英語=Luna) | ○ | PRODUCTION_WIRED | C(§4-4) |
| R30 | R0モデル影響 | UDR | なし | ― | ― | E案に吸収 | A(§3-5) |
| R31 | Sol E案 | V | CS:1157,1159 | ○ | ○ | PRODUCTION_WIRED | D: CS:1169 |
| R32 | 二重LLM評価 | R | なし | ― | ― | REJECTED | 問題なし |
| R33 | FACTLOCK-ASTRA-E2E | UDR | CS:1169 | W-1に吸収 | ― | 吸収 | A(§3-6) |
| R34 | Standard A2 v5 | V | CS:831 | ○ `er003_v1_n3_01_standard_a2_generate.py` | ○同一 | PRODUCTION_WIRED | CS:831の旧記述要確認 |
| R35 | Advanced語彙v2 | V | CS:830 | ○ adv:144,350 | ○ | PRODUCTION_WIRED | 問題なし |
| R36 | 忠実英訳・段落3分割 | 採用 | CS:1371 | ○ | ○(must-fix retryは撤去) | PRODUCTION_WIRED | E(OPEN-230、OI:412) |
| R37 | In One Line | 承認 | CS:583 / FX記録 | × adv:558は旧1文 | ×(retryも旧Prompt) | APPROVED・未配線 | F(§2-5) |
| R38-R39 | Risk Flagger / 旧Checker撤去 | V/配線 | CS:1155-1200 | ○ | ○ | PRODUCTION_WIRED | 問題なし |
| R40 | Pre-sorter | UDR | なし | ― | ― | UDR | A |
| R41 | RF候補(a)(b)(c) | 候補 | なし | × | ― | 候補 | A/E |
| R42 | JA Fact Check配線 | 配線→撤去 | CS:829末尾 | ― 撤去済 | ― | 撤去済み | D |
| R43 | OPEN-183/174/175 | OPEN | ― | ― | ― | OPEN | E |
| R44 | 最新モデル原則 | 採用 | PM_GOVERNANCE 25 | 運用 | ― | ADOPTED | 問題なし |
| R45 | 09:00最終判断 | 承認 | CS:1203-1246 | §2参照 | §2参照 | APPROVED・未配線 | B |

**retry/fallback/regeneration/resume/Local Rewrite別の統合結果(PC§2)**: R0記号再生成・R1/R2技術retry・R2記号再実行・`--regenerate-stage`・Adv/Std構造parse retry・段落3分割retry・Std単独再生成・KP解説技術retryはすべて初回と同一Prompt/同一model(技術must-fixのみ追加)。resumeはPrompt未使用でLegacy記事を遮断。KP候補供給M2失敗時のStrategy L fallbackは承認済み・報告義務あり。Local Rewrite(TTS ASR NG回復)は別Prompt(`er020_tts_retry_local_rewrite_01.py:367,524`)で、IOL文数・Std/Adv構造保持の検査有無は**未精読**。Self Recovery/precheck retryはFamily X Production未配線(Grepヒット0)。Risk Flaggerは台帳照合のみでWriter原則への参照なし(Dangling無し)。

---

## §7 優先順位付き是正対象と影響範囲

| 優先 | 是正対象 | 影響範囲 | ユーザー判断 |
|---|---|---|---|
| **P1-1** | In One Line 基本2文のPrompt作成→Adv英語生成(adv:558,551-615)→Std継承→Comment4整合(audio_plan:206-208)→retry経路→test | Adv/Std全記事のIn One Line、Comment4 | 要(Prompt案の承認方式 §8c) |
| **P1-2** | PD06/K2/P8/P7をFamily X profileへ配線(style_profile:16-17,100-110,149-175)+既定profile化 | Full Story/KP英語音声/KP日本語意味/KP英語解説の全記事 | 要(§8a,8b,8i)。K2は`er063_family_z_audio_01.py:154`に先行存在=Family Zへの先行配線が逆転 |
| **P1-3** | R0規則7の宙ぶらりん(w1:66,95) | R0 Promptへ毎回送信される1文 | 要(Prompt変更はUDR扱い) |
| **P1-4** | 正式W-1実走(Coffee)でのrouting/model_id確認項目化 | Coffee再制作のGate | 不要(既決の運用) |
| **P2-1** | SSOT注記是正: CS:829・830・831・905・1169(AN3記述含む)・2462・2501・2519、OI:750(OPEN-248旧見出し)・412・745・740 | 仕様書の誤読防止のみ(実装は正しい) | **不要(開発側是正。ユーザー報告後の別委任)** |
| **P2-2** | 旧Luna連鎖モジュールの撤去要否・死コード(`open243_m1_enabled`) | 誤配線時の巻戻りリスク(低〜中) | 不要(Fable判断) |
| **P3-1** | OPEN-237系・RF候補・代理指標・Pre-sorterの一括整理 | OI整理 | 要(§8h) |
| **P3-2** | 英語化Writerモデル、OPEN-243の守り、AN3第1文追認、Hook | 品質の長期設計 | 要(§8d,8e,8f,8g) |
| **P3-3** | Dangling検査のSCOPE拡大、IOL Validator、Prompt送信全文の保存 | 検査の死角(新規仕様候補) | 要(別途提案) |

---

## §8 ユーザー判断が本当に必要な事項

各行に推奨・理由・影響・Blocking。判断前確認4点(過去判断済みでないか/技術的に解決を試みたか/なぜ今必要か/推奨案が基本要件を欠く成果物を残さないか)は§12で行ごとに示す。

| 記号 | 判断事項 | 推奨 | 理由 | 影響 | Blocking |
|---|---|---|---|---|---|
| (a) | **P7の正本確定**(`er080_coffee_kp_pacing_trial_01.py:35` p7[速度・リズムのバランス型]か、KP-EN-EXPLANATION系Trial-01の別P7か) | er080のp7(FX記録の再計算と、`..._PACING-TRIAL-01_USER.md:85-88`の指示原文が一致)を正本とする追認 | FX記録§3が「同名別P7あり、要確認」と自記。ユーザー指示原文と逐語一致しているのはer080側 | KP英語解説(Adv)の全記事。誤ると別のPromptが配線される | **Yes** |
| (b) | **PD06=Pace Trial-02のPD6の対応確認**と、Std適用・6%減速併用の方式 | 名称対応を追認。Std Full Story適用は「PD06をStdにも同一文で適用し、6%減速併用は[Adv相当に揃える/併用しない]のどちらか」をユーザーが選択 | 正本Trial-02はAdv対象。Std適用・併用はCS:1203小節自記で「正本に明記なし」 | Full Story TTS全記事のStd | **Yes** |
| (c) | **In One Line 2文Prompt案の承認方式** | 配線設計時に案(旧Prompt改修)を1つ提示し、ユーザーが承認してからwiring。案作成までは判断不要 | 改修Promptは未作成(正本未特定)。新Promptは新仕様の言葉であり、未承認のまま実装できない | 全記事のIOL・Comment4 | **Yes(設計後)** |
| (d) | **英語Advanced/Standard化のWriterモデル**(Luna維持かSol統一に含めるか) | まず現状維持(Luna)を既定とし、Sol化を望む場合のみ比較Trialを別途起票 | 判断記録なし(DL:20573は英語化を対象外と明記)。コストと品質のトレードオフはTrial未実施 | 英語最終成果物の品質・単価(目標70円/記事セット) | No |
| (e) | **AN3第1文置換の追認**(Fact Lock数字規則(5)が第1文の代わり) | 追認(Fact Lock構造はユーザー承認済み、置換はその一部) | DL:20299近傍の数値規則(c)の要旨で、置換の意図的採用は示唆されるが明示の追認記録がない | R0 Promptの数字方針の正本をSSOTに確定。実装変更なし | No |
| (f) | **OPEN-243(翻訳段NG)の守り範囲** | RFが拾う型(主体入替・複数形化・訳語ずれ・要約付け足し)を確認し、継続かcloseを選択 | 「現行の守り」(EN deviation check、O3観測)は撤去済み(CS:1182)で、残る守りはRFのみ | 英語化の事実NG検出 | No |
| (g) | **Hook Side outputの引継ぎ可否** | 引継がず廃止(R2 Title表示のみ維持)を推奨。ただし必要ならW-1後段に1stage新設 | 現Family X runnerに該当stageなし。比較観測用で品質に直結しない | 比較観測の継続可否 | No |
| (h) | **OPEN-237系・RF候補(a)(b)(c)・代理指標・Pre-sorterの一括整理**(継続/廃止) | §3の推奨のとおり一括提示 | 個別に問い直すより一括整理が現実的(PB§6-3) | OI整理のみ | No |
| (i) | **Coffee限定profileの既定化** | 09:00判断(Family X全体)に合わせ、PD06/K2/P8/P7/E1を含む新profileを既定にする | `DEFAULT_NEW_RUN_PROFILE=n01`(style_profile:110)では、CLI指定を忘れた新規runでR2/P3/E1が黙って落ちる | 全新規run。取り違えリスクの除去 | **Yes** |

**未承認の良好なTrial成果としてユーザー判断事項に挙げるもの**(FX記録§6「監査中に発見した未承認の良好なTrial成果は別途提示」): 該当は(h)の中の「RF新仕様候補(a)台帳にない定量・事実の挿入検出」のみ(良好かの評価は未確定)。それ以外の良好な未承認成果は発見されなかった。

---

## §9 CoffeeをResearchから再制作する前のBlocking事項

**Blocking(これらが無いと完成品が承認仕様を満たさない)**
1. IOL 2文化のPrompt作成→承認(§8c)→Adv英語生成・Std継承・Comment4整合・retry経路・test→evidence(§2 #5)。
2. PD06/K2/P8/P7の配線(設計→実装→test→evidence)。まず(a)(b)の判断。KPのM2→P8、P3→P7置換(§2 #1-#4)。
3. 既定profileの更新(§8i)と、Coffee限定profile/CLI依存の解消(§4-5)。
4. M2P0の未完了(OPEN-343、Std CANONICALIZATION_INVALID)の再確認(§2 #7、本監査では精読せず)。
5. 正式W-1での実走確認項目(model_id、`chain_method=W-1`、retry発火時の再確認)。MAQ_TRIAL_W-1の再利用は不可(FX記録§3「旧Coffee記事を完成品として流用しない」)。

**Blockingではないが同時に片付けるべき事項**
- R0規則7のDangling(§4・§8、Prompt変更なので判断後)。
- Comment4のB1側展開(OPEN-316(c))。
- SSOT注記是正(§7 P2-1。仕様書の誤読を避けるため再制作着手前が望ましい)。
- 旧`ja_writer_o_r1_r2`のLuna連鎖の撤去要否。
- Adv Preview=E1の既定化(§2 #9)。

---

## §10 残存Open Item・未報告Trial・未配線APPROVED事項

**残存Open Item(ID+1行、OI行番号は現行値)**
- OPEN-237(OI:739): 台帳明確化系、UDR、2026-10-07以降更新なし(§3-1)。
- OPEN-238(OI:740): Precheck、名目PRODUCTION_WIRED、到達経路なし(§4-1)。
- OPEN-243(OI:745): 翻訳段NG、「現行の守り」撤去(§8f)。
- OPEN-297(OI:800): Family Z MELOS比較(Family X外、09:00記録で行内追記あり)。
- OPEN-298(OI:801): 全記事共通Style展開、09:00で拡大(行内追記)。
- OPEN-299(OI:802): IOL 2文方針、状態タグは「未仕様化・未承認」のまま(09:00で承認済み、Prompt未作成)。
- OPEN-300(OI:803): Coffee限定配線方式、未設計。
- OPEN-313(OI:816): Phase2 K2/M2申し送り。
- OPEN-316(OI:819): Std Comment4/B1展開。
- OPEN-317(OI:820): KP英語解説P3、09:00でP7が置換。
- OPEN-325(OI:828): KP選定、A方式で判断済み(行内追記)。
- OPEN-343(OI:852): M2P0 Std完了、未完了。
- OPEN-350(OI:859): Adv Preview=E1、approved-but-unwired。
- OPEN-357(OI:866): 記録のみ・優先度低。
- OPEN-367(OI:876): Std KP日本語Trial-02、P8確定により更新対象。
- OPEN-393(OI:902): P7の試聴待ち。
- 関連: OPEN-174/175/183(OI:355,356,364)、OPEN-176(OI:357、Hook)、OPEN-220(OI:403)、OPEN-230(OI:412)、OPEN-241(OI:743)、OPEN-245/246/249/250(OI:747,748,751,752、非ブロッキング)、OPEN-248(OI:750、ROOTFIX旧見出しStatus)。

**未報告/整理漏れTrial**: R06-R08、R19、R30、R33、R40、R41(§3)。R23は結果がSSOTに未記録。

**未配線APPROVED**: PD06・K2・P8・P7・In One Line 2〜3文(いずれも2026-10-16 09:00)、Hook Side output(2026-09-24)、Adv Preview=E1(OPEN-350)。REG側はFXUD-1〜8(REG:180-187)で「判断済み」。

---

## §11 Part間の矛盾・訂正

**1. PCのラベル誤対応(FX記録の正本照合で解消)**
- PC§6はPD06をSSOT未定義、P8を「Full Story style」、P7を「Entertainment Original Prompt方式」と対応づけた。**訂正**: PD06=Pace Trial-02の「PD6」候補(名称対応、CS:1203小節)、K2=`er057_tone_trial_kp_ja_gen_01.py:38-39`、P8=Std KP日本語意味の`er057_std_kp_ja_style_trial_02.py:25`、P7=Adv KP英語解説の`er080_coffee_kp_pacing_trial_01.py:35`。
- ただし「P8」は2系統ある: (i)2026-10-12の「PD8→P8」はFull Story style(CS:2671の履歴)、(ii)2026-10-16 09:00のP8はStd KP日本語意味。09:00記録では(ii)が最新。P7も「同名別P7」がFX記録に自記済み(§8a)。
- PCの「K2/M2/IOLを含むCoffee承認StyleがFamily Zにあり本家(X)に無い逆転」は実測で確認(`er063_family_z_audio_01.py:154`にK2のshaが存在、Family X Productionには無し)。

**2. PBの行番号再照合結果**
- DL行番号: PB・PA記載値に+2が現行値。実測8箇所一致(20573=E案決定[PA 20571]、20576=Closeout[PA 20574]、20532=委任_04決定[PB 20530の(1)]、20546=ROOTFIX最終決定[PB 20544]、20552=正式完了承認[PB 20550]、20024=FLOOR-E2E決定[PB 20022]、18822[PB 18820]、9417=Hook決定[PB 9415])。DL:20530自体は存在するが内容はRF A4決定であり、PBが「W-1正式採用」と書いた箇所は20532。以降、DLの正確な所在は「管理ID見出し」で引くこと。
- CS: 09:00小節はCS:1203-1246(PB記載の1202〜1247は並行編集中のずれ)。CS:2669は見出し、2671に09:00追記のpointerが入った。他(583, 829-831, 886, 905, 1157, 1159, 1165, 1169, 1170, 1182, 1371, 1856, 2462, 2501, 2519, 2536, 2538)は**変更なし**で一致。
- OI: 739, 740, 745, 800-803, 816, 820, 828, 852, 859, 866, 876, 902は一致。PBの「OI:750」はOPEN-248(B3 ROOTFIX)の行番号(OPEN-ID番号ではない)。
- PBの「09:00記録の反映が未commit」との記述は、現在はcommit済み(`6ce564e58`)。
- コード側(主要5箇所): `adv:558`一致、`style_profile:16-17`一致、`w1:66,95`一致、`er006:134-138`一致、`audio_plan:206-208`一致(「1文とは限りません」の記述)。

**3. PCの`er053_family_x_factlock_ja_writer_01.py`(w1)行番号の訂正**
- `build_r0_block`: PC記載99-111 → 正は**131-139**(PB/PAの131-139が正)。
- `call_astra`: PC記載163-176 → 正は**200**(PAの200が正)。
- 記号予防ブロック付加: PC記載271 → 正は**270**(`prompt += jaw.SYMBOL_PREVENTION_BLOCK_JA`)。記号再生成note付加: PC記載279-281 → 正は**275-277**(`build_r0_symbol_regen_prompt`)。
- `build_r0_prompt`: 262(PC記載260-276は範囲として妥当)。`R0_MODEL`/`ASTRA_MODEL`は40/42(PA一致)。

**4. CS:905とCS:1169のAN3記述の正確な所在**
- CS:905: 「【撤去済み注記(2026-10-10)】本節のAN3-T0 Prompt block自体はW-1 Writer R0 Promptに含まれたまま有効(sha `067030ff…`)」(同行後半で旧Writer chainの撤去を述べる)。
- CS:1169: 「AN3-T0(Concreteness Control)はR0 Promptに含まれたまま(`CONCRETENESS_CONTROL_AN3_BLOCK` sha `067030ff…`、runtime_…)」。
- 実装: `er019_family_x_ja_writer_o_r1_r2_01.py:99-104`の定数は2文(数字・時刻の抑制/固有名詞)。`w1:131-139 build_r0_block`は第1文を送らず第2文のみ+Fact Lock規則6として連結。runtime_evidenceのshaは**定数のsha**であり実送信文のshaではない。**CS記述は「定数は含まれたまま」としては正しいが「実際にR0に入る文」とは異なる**=SSOT記述の精度の問題。

**5. PAとPCの証拠対象の違い(矛盾ではない)**
- PAは`coffee_prices/run_v5_ms_01`(MAQ_TRIAL_W-1、中身はSol)、PCは`coffee_prices/run_l3_01`(Luna/Astra期)を参照。IOLが1文である証拠は英語生成段(Luna)に由来するためSolの影響を受けない。「Sol期のCoffee Writerを正式runnerで通した記事」は存在しない(PC§7-3)。

---

## §12 ユーザー判断が本当に必要な事項/開発側是正(ユーザー判断不要)の区別表

判断前確認4点: ①過去判断済みか ②技術的に解決を試みたか ③なぜ今必要か ④推奨案が基本要件を欠く成果物を残さないか。

**A. ユーザー判断が必要**

| 項目 | ①過去判断 | ②技術試行 | ③なぜ今 | ④成果物 |
|---|---|---|---|---|
| (a) P7正本 | FX記録§2でP7採用は判断済み。「どのP7か」は自記で要確認 | 指示原文と`er080`を突合しsha一致を確認済み(CS:1203小節) | 配線前に正本が決まらないと配線不能 | 誤ると別Promptが本番に入る。推奨は基本要件を満たす |
| (b) PD06のStd適用/6%減速併用 | PD06採用は判断済み。Std適用細目は記録なし | 正本Trial-02を確認。Std明記なし | Full Story TTSの配線仕様に必須 | 推奨(追認+選択)で基本要件を満たす |
| (c) IOL 2文Prompt案の承認 | 方針(基本2文)は判断済み。Prompt文面は未作成 | 試案の作成は新規Prompt提案となり本委任では禁止 | 案提示後に承認が要る(配線設計時) | 承認なしで実装すると未承認仕様になる |
| (d) 英語化モデル | 判断記録なし | Trial未実施(本委任でも禁止) | 単価70円/品質に影響する設計判断 | 現状維持(Luna)で基本要件を欠かない |
| (e) AN3第1文置換 | 追認記録なし(DL:20299近傍の要旨は置換を示唆) | 実装と定数を突合済み | SSOT記述を確定させるため | 追認でも非追認でも実装変更は要らない |
| (f) OPEN-243守り範囲 | 継続/closeの回答なし | RFの検出型を確認(PB R24) | EN deviation check撤去で成立しない | 継続で基本要件を欠かない |
| (g) Hook Side output | 2026-09-24にユーザー決定済み。W-1置換後の扱いは記録なし | Grep 0件 | 引継ぐか廃止か | 廃止でも基本要件に影響しない |
| (h) OPEN-237系ほか一括整理 | 判断証拠なし | PBでDL/OIを精査 | 判断漏れの整理 | OI整理のみ |
| (i) 既定profile化 | 09:00で「Family X全体」は判断済み。既定化の方式は未記録 | style_profile:99-110を確認 | 取り違え防止 | 推奨で基本要件を満たす |

**B. 開発側是正(ユーザー判断不要)**

| 項目 | 内容 | 時期 |
|---|---|---|
| SSOT陳腐化注記 | CS:829/830/831/905/1169/2462/2501/2519、OI:750/412/745/740の置換注記 | ユーザー報告後の別委任 |
| 死コード・孤立モジュール撤去 | `open243_m1_enabled`、`jaw.run_ja_writer_o_r1_r2`の隔離強化 | Fable判断 |
| 検査の範囲拡大(新規仕様候補) | Dangling検査のSCOPE拡大、IOL Validator、Prompt送信全文保存 | 別途ユーザーへ提案(本委任では実装しない) |
| 配線実装(承認済みの6仕様) | 判断(a)(b)(c)(i)の後に設計→実装→test→evidence | Production Wiring委任 |
| 正式W-1のCoffee実走時のrouting確認 | 既決の運用手順 | 再制作時 |

---

## §13 Opusレビュー前である旨・未確認事項一覧

**本書はOpus独立レビュー前**。Fableの照合・Opusレビュー後に訂正の可能性がある。

**未確認事項(推測でPASSにしない)**
1. Sol配線後にretry系(B3 attempt2・R0記号再生成・R2再実行)が実発火した証跡(PA§5)。
2. 正式runner(W-1 chain)経由のCoffee記事のWriter実行(MAQ_TRIAL_W-1のみ)。
3. 送信されたPrompt全文は保存されておらず、R0/R1/R2以外(英訳・IOL・Std・Comment)のPrompt一致はコードからの推定(PC§7-2)。
4. Local RewriteがIOL文数・Std/Adv構造を保つ検査の有無(PC§7-5)。
5. CS:830-831のFamily X向け置換注記の有無(行全文未精読)。
6. A方式のPrompt逐語(CS記載のtest固定を信頼、本監査では再確認せず)。
7. OPEN-343/350/316の最新状態(OI行頭タグのみ確認)。
8. 「Coffee全面再制作」のDL記録: FX記録§3の原文とDL:21640節に記録あり(PC§6/§7-7の「Grepヒット0」は旧snapshot)。
9. Family A/B/C/Z/Yの共有関数(`vfl01.run_deviation_check`等)、Self-Recovery配下約66委任の細部、チャット原文そのもの(Repo外、DLの「逐語」記述の一致は未検証)。
10. unit testの再実行(本監査では実施せず)。

**Opusレビューに回すべき論点(候補)**: ①IOL 2文Prompt作成の方式(条件A: 新しい構造/処理フロー)と、Comment4・Std継承・retryの一貫性。②「全Style共通定数 vs profile既定化」の設計(OPEN-300/313、Family Xへの拡大)。③AN3第1文置換を「意図的」とするSSOT記述の是正方針(CS:905/1169)。④OPEN-237系・RF候補を一括SUPERSEDEDとする妥当性。⑤P1/P2の分類(SSOT注記是正をユーザー判断不要とした根拠)。
