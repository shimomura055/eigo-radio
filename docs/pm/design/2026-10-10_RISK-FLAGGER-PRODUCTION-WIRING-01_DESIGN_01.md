# RISK-FLAGGER-PRODUCTION-WIRING-01 設計書 DESIGN_01(Phase 1: 棚卸・設計のみ)

- 管理ID: RISK-FLAGGER-PRODUCTION-WIRING-01 委任_01(2026-10-10)
- Status: **DESIGN_READY / USER_DECISION_REQUIRED(STOP候補あり、13節)**。`APPROVED_FOR_PRODUCTION`の仕様をPRODUCTION_WIREDにする前段の設計。**Productionコード・CURRENT_SPEC・Promptは変更していない。課金API 0件。pip install なし。**
- 調査基準: git HEAD `f4d27045`(2026-10-10)のワーキングツリー。行番号は同時点。
- Opus独立レビュー: Phase 2(実装)前に条件A(新しい処理フロー設計)・条件C(重要変更のProduction採用提案前)が該当(PM_GOVERNANCE 11-3)。本書がレビュー対象。未実施。
- 使用モデル(PM_GOVERNANCE 25節): 本Phase 1はLLM API呼び出し0件のため評価モデルなし。Phase 2で使うLuna=`gpt-6-luna`(現行世代)、Gemini=`gemini-3.5-flash-lite`(ユーザー指定名。旧世代`gemini-3.1-flash-lite`/`gemini-2.5-flash-lite`はより安価に実在するが置換しない、A4-DUALMODEL-OR-TRIAL-01 RESULT_01 §2)。

---

## 0. 非エンジニア向けサマリ(結論5点)

1. **今のProduction正式経路でFact Checkerが動いているのはFamily X(ニュース)だけ**。Family X = `er019_family_x_entertainment_production_runner_01.py` → `er012_e_family_entertainment_two_level_runner_01.py` → `er019_family_x_ja_writer_o_r1_r2_01.py`。Family A/B/Cは「legacy(最新追従しない)」、Family Zは台帳を使わないのでFact Checkerなし(CURRENT_SPEC L1472以降)。
2. **「新Writer(Fact Lock)」と「OPEN-233 Checker(Self-Recovery/Floor)」はどちらもProduction正式runnerへ配線されていない**(`git grep "er052_open233"`をer003/er009/er010/er012/er019で実行し0件)。今のProductionは「旧Writer(Luna R0→R1→R2)+旧Fact Checker」。CHECKER-FLOOR E2Eの配線先は`er052_open233_self_recovery_flow_runner_01.py`(Trial/検証runner)。→ **STOP候補S-1**(新Writer未配線のまま旧Checkerだけ撤去すると「旧Writer+Checkerなし」になる)。
3. **撤去対象(旧Fact Checker)はコード上かなり明確**(Family Xで22行、生きたAPI呼び出し9箇所)。技術QA(記号Validator・段落3分割gate・TTS/ASR/Audio Validation Gate等)は別関数・別ファイルにある。**ただし境界が曖昧な2箇所**(例外クラス`JAFactCheckStopError`が記号QAと共用/`must_fix`機構が段落retryと共用)がある → STOP候補S-4(解決案つき)。
4. **文分割(splitter)の欠陥はTrialで実在**: 「ensuring U.S.」の文途中切れは**X09 s8**(hormuz)で確認。略語で終わる文は11本中6本・計21文。`vs_sentence_segments_l6()`は`er052_open233_self_recovery_flow_runner_01.py`(Trial runner)内にあり、Productionからimportできない(Trial依存禁止)。**新設の共通モジュール(追加のみ、既存splitter無変更)**を推奨。他Production経路への影響0。
5. **Review Queueは`review_queue/post_en/`新設を推奨**(.gitignoreに該当ルールなし、追跡可能と実測)。既存`human_review_queue.jsonl`はTTS/ASR技術QA用のLock付きキューで意味が違うため流用しない。**入力はTrialと意味的にほぼ同一だが、(a)Standard(a2)はTrial未検証 (b)Production費用ロガーがGemini思考tokenを計上しない・Gemini単価未登録 の2点は要判断**(S-3/S-8)。

---

## 1. Production正式経路の特定(stage順序表)

根拠: CURRENT_SPEC.md「Family体系」L1472〜(Active=X/Y/Z、Legacy=A/B/C)、各runner本体(HEAD)。

### 1-1. runner別stage順序

| Runner | Family/Status | stage順序(コード上の実順序) | Fact Check/Checkerの位置 | 新Writer(Fact Lock)? | OPEN-233 Checker? |
|---|---|---|---|---|---|
| **er019_family_x_entertainment_production_runner_01.py**(L295 main) | **X(Active)** | research_ledger(L91、`efam.run_researcher_for_topic/run_verification_for_topic`)→ storyline_b3(L141)→ writer=JA(L185 `run_ja_writer`→`jaw.run_ja_writer_o_r1_r2`)→ advanced(L378 `efam.run_writer_stage(only="advanced")`)→ standard(L389 同`only="standard"`)→ **Mandatory STOP**(TTS/assemble/playerのstageはこのrunnerに存在しない) | JA Original後・JA R2後(jaw)、EN Advanced後・Standard後(efam)。計4か所 | なし(JA Writerは旧`R0_PROMPT`のLuna R0→R1→R2) | なし |
| er012_e_family_entertainment_two_level_runner_01.py(L1127 main) | X(上記の下位。単体CLIでも起動可、`--ja-article`) | ledger → writer(L737 `run_writer_stage`、L467 `_run_writer_stage_once`)→ scaffold/tts/assembleは**封鎖**(L854 OPEN-228、audio runnerへ誘導)→ player | EN Advanced/Standard deviation check(L509,L634) | なし | なし |
| **er019_family_x_audio_production_runner_01.py**(L1842 main) | X(音声側の正式経路) | plan(L201)→ scaffold(L304: Comment1-4/Preview/Key Phrase)→ tts(L554/L820)→ assemble(L1262/L1468、`asm.verify_episode_audio_validation_gate`)→ player(L1725) | **なし**(`deviation`/`fact_check`のgrep 0件。技術QAのみ) | - | - |
| er026_family_z_fiction_production_runner_01.py(L787 main) | Z(Active) | text stage(L577)→ keyphrase(L736) | なし(台帳なし。fact関連語のgrep 0件。`vfl01`はclient取得にのみimport) | - | - |
| er012_b_family_production_runner_01.py(main_b1_3v L1119/main_b1_2v L1254/main_a2 L1626/main_a2_2v L1947) | B(Legacy) | scaffold→tts→assembly。Fact Check=`run_fact_check_b1/a2`(L238/L243)、Support Ledger Deviation(L295/L806/L1112、monitoring専用) | あり(legacy) | なし | なし |
| er003_discovery_focus_staged_production_01.py | A Discovery(Legacy) | Stage1 Writer→Stage1 QA(Fact Checker A→Ledger Deviation+Local Rewrite)→…→記事全体Fact Checker→Deviation+Local Rewrite | あり(legacy、L195-L287) | なし | なし |
| er013_family_c_production_runner_01.py | C(Legacy) | plan→comments→full generation | なし(grep 0件) | - | - |
| er003_v1_n3_01_articles_generate.py::run_one_pattern(L888) | A News/Daily(Legacy) | Writer→Fact Checker→Ledger Deviation→Local Rewrite(MAX_REWRITE_CYCLES)→NG_REVIEW_REQUIRED | あり(legacy、L1100,L1142,L1161) | なし | なし |

### 1-2. 事実で特定した3点

- **新Writer(Fact Lock R0 / Astra R1 / R2)を呼ぶProduction runnerは0件**。実装は`er052_factlock_writer_trial_01_run.py`・`er052_factlock_astra_e2e_runner_01.py`(docstringに「Trial/DEV、Production経路ではない」)のみ。同E2E runnerの新仕様腕は、新Writer出力を`ja_writer/revision2.md`に置いて**er019 Production経路(旧Checker込み、`OPEN243_M1=1`・`OPEN233_RECLASSIFY_PROTECT_FLAGS=changed_actor`)の再利用分岐へ乗せる**構造(同ファイル冒頭docstring)。つまり「新Writer経路でFact Checkerを呼んでいる」のはTrialの新仕様腕だけで、呼んでいるのはer019/er012_eの**旧Checker**。
- **OPEN-233 Checker Floor Production E2E(`docs/pm/delegation_log/2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_01〜07`)の配線先は`er052_open233_self_recovery_flow_runner_01.py`(11,188行)**。委任_04=「Production候補経路(er052 runner)への配線実装」、`FLOOR_MODE=number_only`・`PRECHECK_MODE=number_only`・`OPEN233_APPROVED_FLOW_SWITCHES`をrunnerへ。E2E出力は`er052_output/open233_prod_e2e_02/`。CURRENT_SPEC L2338節「適用先(Trial/検証用モジュール、Production正式path[`er003*`・`er009*`・`er010*`・`er012*`・`er019*`]は無変更、`git grep`で`er052_open233`のimportが0件)」・Production Flow仕様12「Production moduleは`er050`/`er051`/`er052_*`をimportしない(新規`er0XX_self_recovery_flow_01.py`)」。その新規Production moduleは**存在しない**。9/20 run E2E完了・PRODUCTION_WIRED未・残11 runはユーザー総合レビュー待ち(同L2338追記)。
- **Fact Check(`ja_original_check`)の位置**: `er019_family_x_ja_writer_o_r1_r2_01.py` L277(`cl.logging_context(THEME_TAG,"ja_original_check")`)=Original直後。R2直後は`ja_r2_check`(L390)。ENはefam L509/L634。

### 1-3. RFの挿入位置(設計案)

`er019 entertainment runner`はStandard生成で**必ずMandatory STOP**し、その後に`er019 audio runner`を別CLIで起動する運用。ユーザー決定「英訳完了後・TTS開始前」に最も整合する位置は、**audio runnerの`all`の先頭に新stage `risk_flag`(`plan`の後・`scaffold`の前)を追加**(単独`--stage risk_flag`でも実行可)。RFはBlockingでないので、scaffold/ttsの前提条件にはしない(RF_UNAVAILABLEでも進む)。代替案: entertainment runner末尾(Standard完了直後)に追加。→ 13節 D-1。

---

## 2. 旧Fact Checker撤去対象の棚卸表(Family X Production、行番号はHEAD)

ユーザー列挙8項目の原文は委任文に逐語では含まれていない(「Fact Ledger比較によるBLOCK/Rewrite/retry/regeneration」と、「動作」「トリガー語」の列挙のみ)。下表は委任文の動作・トリガー語の全項目(BLOCK/Hard STOP/must-fix retry/local rewrite/full rewrite/recheck/ja差し戻し、Stage1/Stage2/reclassify/MAJOR/JA_RECHECK_REQUIRED/must-fix/Deviation Check/origin=ja_source)を網羅するよう作成した。**ユーザーの8項目原文との照合は要(13節 D-9)。**

到達経路: 初=初回path / R=retry / F=fallback / G=regeneration(再生成・JA差し戻し含む) / U=resume(既存成果物再利用)

| ID | ファイル:関数:行 | 到達経路 | 動作 | トリガー語 |
|---|---|---|---|---|
| R-01 | er019_family_x_ja_writer_o_r1_r2_01.py:`run_ja_writer_o_r1_r2`:L275-L325(check1 L277-278、must-fix再生成L291-296、check2 L298、raise L305) | 初・G(案Bの内側) | JA Original直後のFact Check→**must-fix full rewrite(1回)→recheck→Hard STOP** | `LEDGER_DEVIATION`/MAJOR/must-fix/`JA_FACT_CHECK_STOP`/`prior_issues` |
| R-02 | 同:L387-L450(check L390-391、R2 must-fix L405-424、check2 L426、raise L433) | 初・G | JA R2直後のFact Check→R2 must-fix再生成(R1から)→recheck→Hard STOP | 同上(`ja_r2_check`) |
| R-03 | 同:`build_must_fix_block` L125-L146、`build_original_prompt`のmust_fix/full_ledger_text引数L148-L166、`original_must_fix`引数L237・L264 | R・G | must-fixブロックをPromptへ付加(Full Ledger全文再掲) | must-fix |
| R-04 | 同:`_major_deviations`/`_must_fix_from_deviations` L184-L197 | R | MAJOR抽出→must-fix変換 | MAJOR |
| R-05 | 同:`full_ledger_text`引数ゲート(L275 `if full_ledger_text is not None`、L388) | 初 | full_ledger_textが渡るとFact Check有効(Noneで無効=既存互換スイッチ) | - |
| R-06 | er019_family_x_entertainment_production_runner_01.py:`run_ja_writer`:L185-L232(L193 `full_ledger_text=`、L194-L203 `JAFactCheckStopError`ハンドラ=`deviation_checks`/`rejected_ja_*`保存、L215-L230 `fact_checks_summary`) | 初・U | Fact Check STOPの監査保存・evidence | `JA_FACT_CHECK_STOP` |
| R-07 | 同:main L354-L362(`full_ledger_text=ledger_text`)、L375-L396(`storyline_line`/`selected_fact_brief_text`をefam.run_writer_stageへ渡す=案B有効化) | 初・G・U | 案B有効化の引数 | ja_source/JA差し戻し |
| R-08 | er012_e:`JARecheckRequiredError` L285-L293 | G | 例外クラス(JA再確認要) | `JA_RECHECK_REQUIRED` |
| R-09 | er012_e:`_major_deviations`/`_must_fix_from_deviations` L296-L309 | R | 同上 | MAJOR/must-fix |
| R-10 | er012_e:OPEN-243 M1/G3(`open243_majors_only_in_summary` L377-L394、`open243_m1_summary_only_retry` L397-L436、`open243_g3_record_translation_minor` L438-L456) | R | 要約のみ再生成(最大2回)→recheck→STOP。G3=translation起源MINORのtelemetry(観測のみ、API 0) | M1/`origin=translation`/`ja_source` |
| R-11 | er012_e:Advanced deviation check L509-L517(`audit/deviation_checks/advanced_attempt1.json`保存) | 初 | EN Advanced Hard STOP判定の起点 | Deviation Check |
| R-12 | 同:L518-L531 | 初 | `origin==ja_source`のMAJOR→`JARecheckRequiredError`(ja差し戻し) | origin=ja_source |
| R-13 | 同:L532-L557(M1要約再生成+STOP L553) | R | M1経路(env`OPEN243_M1=1`時のみ) | M1 |
| R-14 | 同:L556-L590(must-fix full regeneration L558-L564、段落3分割再検査L565-L570、recheck L571-L574、Hard STOP L576-L588) | R・G | **Hard STOP**(再生成後もMAJOR/前回指摘未解消) | MAJOR/must-fix |
| R-15 | 同:Standard deviation check L634-L642 | 初 | EN Standard Hard STOP判定の起点 | Deviation Check |
| R-16 | 同:L643-L652 | 初 | ja_source→`JARecheckRequiredError` | origin=ja_source |
| R-17 | 同:L653-L680(must-fix regeneration L654-L657、段落再検査L658-L664、recheck L665、Hard STOP L676) | R・G | Standard側のHard STOP | MAJOR/must-fix |
| R-18 | er012_e:`run_writer_stage`(wrapper) L737-L835(案B: JA Oへmust-fix差し戻し→JA Original→R1→R2→Fact Check全体を1回再生成→Advanced/Standard再実行、`ja_recheck_attempt1*.json`) | G(JA差し戻し) | ja差し戻し+full rewrite | `JA_RECHECK_REQUIRED`/案B |
| R-19 | er012_e:main L1170-L1195(`storyline_b3/fact_selection_evidence.json`読込L1181-L1183、存在時のみ案B有効化)、L1189・L1195の`storyline_line=`引数 | G・U | 案B有効化 | ja_source |
| R-20 | er012_e:evidence/監査出力(`must_fix_used`/`retried_for_deviation`/`deviation_overall_status`、`audit/deviation_check.json`書込、`writer_run_summary.json`のキー)L510-L512,L572-L575,L591,L592-L605,L681-L720付近 | 初 | 記録のみ(下流依存は9節で整理) | - |
| R-21 | er003_v1_en_direct_vfl_01_generate.py:`run_deviation_check`+`DEVIATION_PROMPT`/`ORIGIN_ENUM`(`ja_source`/`translation`/`not_applicable` L649-L723)/`OPEN243_M2`(L685-L723) | - | **共有関数。Family Xは呼ばなくする。Legacy A/B/Cが使い続けるため関数自体は残置**(撤去対象は呼出元) | - |
| R-22 | er019_writer_run_summary_reconstruction_01.py(`deviation_check.json`前提の再構築ツール)+ test | U | 旧Checker出力に依存する事後ツール | - |

**件数: 撤去対象22行(R-01〜R-22)**。うち`run_deviation_check`の生きた呼出は**9箇所**(jaw L278/L298/L391/L426、efam L405[M1クロージャ]/L509/L571/L634/L665)。到達経路別: 初回=R-01/02/05/06/11/12/15/16/20、retry=R-03/04/09/10/13/14/17、regeneration=R-01/02/07/08/14/17/18/19、resume=R-06/07/19/22(resume時のJA再利用分岐L354-L357自体は技術的に残す)、fallback=該当なし(Checker起点の独立fallbackはなく、retry→STOPのみ)。

**撤去対象に含めないと整理したもの**: OPEN-233 Self-Recovery一式(Trial runner、Production未接続)、`er052_*`/`er050`/`er051`/`er011_*`のTrial、legacy A/B/C Production(15箇所の`run_deviation_check`: er003_v1_n3_01_articles_generate 3、er003_discovery_focus_staged 3、er012_b_family_production_runner 3、er012_b_family_voices_a2_production 2、er012_b_family_voices_writer_generic 4)。legacyを撤去範囲に含めるかは D-10。

---

## 3. 技術QA維持対象の棚卸表と、2節との境界判定

維持するもの(ユーザー決定の列挙): TTS失敗検知/TTS technical retry/ASR・発音QA/disfluency QA/segment構造検証/required structure validation/Key Phrase構造・source整合/音声欠落検知/manifest・artifact整合。以下はFamily X Production経路での所在。

| ID | ファイル:関数:行 | 到達経路 | 動作 | 対応するユーザー列挙項目 |
|---|---|---|---|---|
| T-01 | er019_family_x_ja_writer_o_r1_r2_01.py:L325-L352(JA Original音声化禁止記号Validator+must-fix再生成1回→STOP `JA_SYMBOL_CHECK_STOP` L343) | 初 | Layer 2記号Validator | TTS失敗の予防(音声化禁止記号) |
| T-02 | 同:L454-L495(JA R2版、`JA_SYMBOL_CHECK_STOP` L488) | 初 | 同上 | 同上 |
| T-03 | 同:`call_fresh` L209/`call_with_previous_response_id` L223、R1/R2連鎖の`previous_response_id`失敗→`fallback_full_text`切替(L360-L388) | F | 技術的fallback(Checker無関係) | 技術retry |
| T-04 | er012_e:`_family_x_ensure_split_or_paragraph_retry` L312-L366、`_FAMILY_X_PARAGRAPH_RETRY_MUST_FIX` L346、呼出 L488-L507(Advanced)/L617-L632(Standard) | 初・R | `split_family_x_article_text_v2`のstatus≠OKで1回だけ段落保持retry→なおNGならSTOP | segment構造検証/required structure validation |
| T-05 | er003_v1_n3_01_advanced_adaptation_generate.py:`generate_family_x_faithful_translation`(L664-L750、`structure_status`/`attempts`/`fallback_detected`/`model_id_actual`)、er003_v1_n3_01_standard_a2_generate.py:`generate_family_x_standard_a2_no_heading`(L541-、`checks`、`structure_status`) | 初・R・F | 構造validation・モデルfallback検知(`model_actual != requested`) | required structure validation/model fail-closed |
| T-06 | er012_e:`_load_pricing`(L106-L121、`PricingNotFoundError` fail-closed)、`assert_budget_ok`(L162)、各stage後の`assert_budget_ok` | 初 | 予算ガード・単価未登録fail-closed | (運用安全装置。技術QAではないが維持) |
| T-07 | er019 audio runner:`run_theme_scaffold` L304-L360(paragraph_count<3で本文を直さずSTOP L325) | 初 | scaffold前構造Gate | segment構造検証 |
| T-08 | 同:`_generate_or_reuse`/`_generate_or_reuse_kp` L400-L470(再利用時も既存Gate再判定を回避しない)、`_load_cached_tts_results` L390 | U | TTS再利用の整合 | manifest・artifact整合 |
| T-09 | 同:`generate_key_phrase_explanation_en_verified` L472-L505、KP text-gate fail-closed L771-L815(`text_gate_status!="OK"`→STOPPED) | 初 | Key Phrase解説のASR/text検証 | Key Phrase構造・ASR・発音QA |
| T-10 | 同:`_assert_shared_narration_ok` L520-L550(共有narration STOPPED→STOP、review_lock/human_review_queue記録は既存機構) | 初 | 共有narration Gate | 音声欠落検知/Human Review Lock |
| T-11 | 同:`stage_assemble_family_x_b1/a2` L1262/L1468、`asm.verify_episode_audio_validation_gate`(er003_v1_n3_01_assemble.py:L469、`required_structure`引数あり)、Key Phrase source整合Gate(L1088-L1097 `article_text=`渡し) | 初 | Assembly前Audio Validation Gate(異常時は例外で完全停止、自動retryなし) | required structure/KP source整合/音声欠落/manifest整合 |
| T-12 | 同:`assert_production_tts_backend` L1823(承認済みbackend以外は課金前STOP) | 初 | backend fail-fast | TTS技術安全 |
| T-13 | er020_tts_retry_local_rewrite_01.py(`PRODUCTION_MAX_TTS_ATTEMPTS=3`=er011_human_review_lock_01.py L80、標準+minimal fallback)、er011_human_review_lock_01.py(Review Lock)、er006_secondary_asr_01.py/er007_ja_secondary_asr_01.py(ASR Cascade→`human_review_queue.jsonl`) | 初・R・F | TTS technical retry・Local Rewrite(**TTS用**)・ASR Cascade・Human Review Lock | TTS失敗検知/TTS technical retry/ASR・発音QA |
| T-14 | er003_audio_tts_asr_safety.py(記号正規化Layer 1/3/4、外来語/foreign token gate L800)、OPEN-121 TTS Repetition/False Start QA、Disfluency QA(CURRENT_SPEC L1909-L1910) | 初・R | 音声QA | disfluency QA/ASR・発音QA |
| T-15 | er012_e L854-L880(OPEN-228封鎖stub: scaffold/tts/assembleをfail-fast) | 初 | 誤経路封鎖 | segment構造検証 |
| T-16 | er019_family_x_audio_plan_01.py/`derive_japanese_title`(L133)・`entry_point.json`等のmanifest/artifact出力 | 初 | manifest整合 | manifest・artifact整合 |

**件数: 技術QA 16行(T-01〜T-16)**。

### 3-1. 境界判定: 「コード上おおむね明確。ただし曖昧2箇所(STOP候補S-4)」

明確な点(根拠): (i)Fact Check呼出は`vfl01.run_deviation_check`の9箇所に集約され、関数名で一意に特定できる。(ii)技術QAは別モジュール(`er003_audio_tts_asr_safety`/`er020`/`er011_human_review_lock`/`er003_v1_n3_01_assemble`)にあり、Fact Checkのコードと同一関数内に混在するのはT-01/02/04のみ。(iii)Audio runner・assemble・playerは`deviation`/`fact_check`/`ja_recheck`/`must_fix_used`のgrepで**0件**(`git grep`で`er019_family_x_audio*.py`・`er003_v1_n3_01_assemble.py`・`er003_v1_n3_01_scaffold_generate.py`・`er003_key_phrase_source_gate_01.py`・`audio_review_player.py`を検索し、依存は`er019_writer_run_summary_reconstruction_01.py`のみ)。つまり下流(TTS以降)にFact Check出力へ依存する箇所はない。

曖昧な点(撤去時に設計判断が必要):
- **B-1: `JAFactCheckStopError`が記号QA(T-01/02、stage=`original_symbol`/`r2_symbol`)と共用**(jaw L169-L182、raiseはL305/L341/L433/L486)。runner側ハンドラ(er019 entertainment runner L194-L203)は`exc.checks`を`deviation_checks/ja_*_attempt*.json`へ保存するが、記号QAでは`checks=[]`。→ 解決案: 記号QA専用の例外`JASymbolCheckStopError`へ分離(クラス名のみ、挙動不変)し、Fact Check用は削除。runner側ハンドラは記号QAの保存(`rejected_ja_{stage}.md`+findings)だけ残す。
- **B-2: `must_fix`機構が段落retry(T-04、技術)と共用**。`adv_gen/std_gen.generate_*(must_fix=…)`・`build_must_fix_block`(adv L325)は`_FAMILY_X_PARAGRAPH_RETRY_MUST_FIX`(段落保持用)でも使われる。→ 解決案: `must_fix`引数・`build_must_fix_block`は**維持**(段落retry専用として)。ただし`_must_fix_from_deviations`(Checker由来のmust-fix生成)だけ削除。docstringのFact Check言及を更新。
- **B-3(軽微): `_open243_iol`(L459-L464)は`OPEN243_M1=1`時に要約生成入力へJA本文+Ledgerを足す**(Writer側のPrompt入力切替でCheckerではない)。Trial限定の環境変数スイッチ(既定OFF)。→ 撤去対象(R-10/13)と同時に`OPEN243_M1`依存分岐を削除するか残すかを決める必要(D-4)。

**判定: 「撤去対象は関数単位で切り出せる(境界明確)が、上記B-1/B-2は撤去時に分離作業が必要」。STOP(新仕様判断)ではなく、Opus条件Aレビューで確認すべき構造変更点。**

---

## 4. 既存sentence splitterの実装差と共通化案

### 4-1. 3実装の差

| 実装 | 所在 | 分割規則 | 略語保護 | 出力 |
|---|---|---|---|---|
| (A) Risk Flagger Trial用`_split_sentences` | `er052_output/writer_dev_risk_flagger_01/detectors/run_flagger_01.py` L60-L63(post_en_trial_01/a4_dualmodel_or_trial_01/FIX02もこれを`R._split_sentences`で使用) | `re.split(r"(?<=[.!?])\s+|(?<=[。！？])(?![」』）)\s])\s*|\n+")`。見出し行(`#`)も1文として残す | **なし**(`.`+空白で必ず切る) | 文字列list |
| (B) `vs_sentence_segments_l6` | `er052_open233_self_recovery_flow_runner_01.py` L5503(補助 `_vs_l6_abbrev_period` L5486、略語リスト`_VS_L6_ABBREV` L5477-L5480、`_VS_SENT_END_RE` L4944) | 文末記号+空白/行末、日本語句点、改行。略語直後の`.`は切らない(`no`は直後が数字のとき、`st`は直後が大文字のときだけ略語扱い) | あり(下記33語) | (start,end)オフセットlist(位置座標用) |
| (C) `er003_ja_to_en_translation.split_sentences` | `er003_ja_to_en_translation.py` L567(`split_paragraph_into_sentences`、`_ABBREVIATIONS` L482) | 段落保持。`.`直後が大文字・数字・開き引用符のとき分割。小数点保護 | あり(10語: `u.s.`/`u.k.`/`mr.`/`mrs.`/`ms.`/`dr.`/`prof.`/`st.`/`jr.`/`sr.`)。月名・`Co.`/`Inc.`は無し | 文字列list(プレーンテキスト前提、見出し除去しない) |

(B)の略語リスト(33語、小文字・末尾`.`なし): `u.s` `u.k` `u.n` `mr` `mrs` `ms` `dr` `prof` `sr` `jr` `jan` `feb` `mar` `apr` `jun` `jul` `aug` `sep` `sept` `oct` `nov` `dec` `st` `no` `vs` `e.g` `i.e` `inc` `co` `ltd` `corp` `a.m` `p.m`。他にer010の`split_sentences`(L60、見出し除外・別規則)、er052の`split_sentences_generic`(L4591)等の用途別実装が存在(RF用途ではない)。

### 4-2. Trialで文途中切れが起きた事実(artifact確認済み)

`er052_output/writer_dev_risk_flagger_01/a4_dualmodel_or_trial_01/runs/{luna,gemini35fl}/<記事>/A3.json`の`sentences`と`flags`を機械走査(read-only)。

- **「ensuring U.S.」の途中切れ: 記事ID=X09(hormuz)、文ID=s8**。文末が`…as reimbursement for the cost of ensuring U.S.`で終わり、続く文s9=`security.`に分離されている(s7も`It all began with Mr.`で途中切れ)。**LunaのA3がこのs8をFlag**(reason: 「"20% payment on all cargo"は貨物価値に20％を適用する意味にも読めますが…」、HF-002,HF-003、conf 0.34)。
- 略語で終わる文の数(11本のうち): U03=6文(s5 `…while the U.S.`、s7、s9、s10、s21、s25)、U06=3文(s4 `…in the U.S.`、s24、s33)、U07=1文(s6 `…USA TODAY Co.`)、X09=3文(s7 `It all began with Mr.`、s8、s17)、X10=7文(s3 `“The U.S.`、s6、s8、s9、s17、s21、s32)、X11=1文(s5 `…USA TODAY Co.`)。**6記事・計21文**(U01/U02/U04/U05/U08は0文)。
- **誤切断された文にFlagが付いた例**: Luna A3/A4が U03 s5(`…while the U.S.`)・X09 s8 にFlag(3 Flag)。つまり**Flag文面が文途中で切れている**ため、Human Reviewでのsentence提示が不完全になる実害が出ている。
- 影響の限定: 台帳照合は文IDと`fact_ids`で行われLLM入力は記事全文のため、検出能力そのものへの影響は限定的だが、Queueに保存する「該当英文」が途中で終わる点がUXと重複統合キー(文ID)の安定性を損なう。

### 4-3. 共通化案

- **推奨: 新設の共通モジュール `er0XX_en_sentence_splitter_01.py`(追加のみ)**。(B)の略語セマンティクス(`_VS_L6_ABBREV`+`no`/`st`の文脈規則+`...`/閉じ引用符の扱い)を移植し、(A)の出力契約(見出し行も1文として残す、`\n`でも分割、文字列list、IDは出現順`s1…`)を維持。`splitter_version`定数をQueueに記録。理由: (B)はTrial runner内(11,188行)にありProductionから`er052_*`をimportできない(Opus#15、Production Flow仕様12)。(C)をそのまま使うと略語が10語のみ(`Co.`/`Inc.`/月名が欠け、U07/X11の`USA TODAY Co.`が割れる)。(A)単独は略語ゼロ。
- **他Production経路への影響範囲: 0**。既存(A)(B)(C)は一切変更しない(`vs_sentence_segments_l6`を移動・変更しない)。新モジュールはRF専用の追加。`er003_ja_to_en_translation.split_sentences`(C)をProductionで使っている箇所は無変更。
- **代替案(非推奨)**: (B)を共通モジュールへ移設しTrial runnerもそこをimportする → Trial runnerの改変+Opus#9で固定したL6の挙動に影響しうるため、splitter共通化が他経路へ大きく影響する(STOP条件)。採らない。
- トレードオフ: 略語を厳格に保護すると「略語で終わる実際の文末」(例`…in the U.S. Officials said…`)で文を結合しすぎる(under-split)。RFでは「途中切断」より「結合」の方が害が小さい(文全体が見える)ため、結合側へ倒す(Luna/Gemini入力は全文なので検出に影響なし)。
- **Sentence IDズレの扱い**: 新splitterではU03/U06/U07/X09/X10/X11の文ID付番がTrial(Human照合済み、ChatGPT側保持)と変わる。ID比較ではなく**文面(正規化一致)でTrialと照合**できるよう、Queueに`sentence_text`と`splitter_version`を必ず保持する(MATCHING_RULE_01 §2の「空白・句読点を除いて一致」と整合)。→ D-6。

---

## 5. Review Queue保存先

### 5-1. 既存調査

- `human_review_queue.jsonl`系は**TTS/ASR技術QA専用**: `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(英語ASR Cascade、`HUMAN_REVIEW_LOG_PATH`)、`er007_output/ja_asr_cascade_01/...`、`er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`(L800)。`er011_human_review_lock_01.py`のReview Lockが「Human Review到達後はTTS/ASR再生成を機械的にブロック」する(AUTO_PROCESSING/HUMAN_REVIEW_REQUIRED/HUMAN_APPROVED/REGENERATE_APPROVED/RESOLVED)。**RFは非Blocking・Lockなしなので意味が衝突する → 流用しない**。
- `HUMAN_REVIEW_*.md`は試験ごとのユーザー確認用一覧(例`er052_output/writer_dev_risk_flagger_01/post_en_trial_01/HUMAN_REVIEW_POST_EN_01.md`: 記事→Union Flag→該当英文/対応Fact原文/理由/Known or New)。Markdown様式の先例。
- **.gitignore(実測)**: `er0XX_output/`配下は`*.wav`・`raw_source_fulltext*`・`_tmp/`・`*.tmp`・`*_ab_mapping.json`・`episode_*.json`・`.env`以外は追跡対象。`git check-ignore -v`で`er052_output/review_queue/post_en/x.json`、`er019_output/x/run_01/review_queue/x.json`、`docs/pm/review_queue/x.json`、`review_queue/post_en/x.json`はいずれも**ignoreなし(rc=1)**。`git ls-files`で`er019_output`は1,034件、`er052_output`は17,302件が追跡中。`docs/pm/ACTIVE_TASK*.md`/`RESULT_PACKET*.md`のみ明示ignore。

### 5-2. 保存先候補

| 案 | パス | 長所 | 短所 |
|---|---|---|---|
| **A(推奨)** 新設 | `review_queue/post_en/<article_id>__<run_id>/{queue.json,queue.md,raw/,inputs/}` + 追記専用`review_queue/post_en/index.jsonl`(1記事1行) | ChatGPTは`index.jsonl`1本から全記事を辿れる。.gitignore非該当。raw/inputsも同居し自己完結 | 新設トップレベルdirの追加(SSOT/READMEの1行追記が必要) |
| B per-run | `er019_output/<slug>/<run>/risk_flag/{queue.json,queue.md,raw/}` | 既存の記事成果物と同居。変更最小 | 記事ごとに散在しindexが無い。ChatGPTが記事一覧を持つ必要 |
| C 既存流用 | `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`へ追記 | 既存の置き場 | **Review Lockと意味衝突、TTS/ASR用schemaと不整合 → 不採用** |

**推奨=A**。raw flag source(各条件のAPI生応答)はA内`raw/`に保存し、`queue.json`の`raw_flag_source`から相対パスで参照。GitHub参照URL例: `https://raw.githubusercontent.com/shimomura055/eigo-radio/main/review_queue/post_en/index.jsonl`。

**運用上の注意(STOP候補S-9)**: runnerはgit操作をしない(Productionにgit pushを持たせない)。「Repo上のQueue」を成立させるには、**RF実行後にClaude側が当該`review_queue/post_en/<id>/`と`index.jsonl`だけを明示`git add`→commit→push**する運用手順が必要(CLAUDE.md Git運用ルールは自律commit/push)。この手順をruntime evidenceの必須項目にする(Gate 3 R5)。

### 5-3. JSON schema案(`queue.json`)

```json
{
  "schema_version": "rf_queue_v1",
  "article_id": "meta__run_03",          // slug__run
  "run_id": "rf_20261010T153000_ab12cd",  // RF実行ID(再実行ごとに別)
  "level": "b1b",                         // "b1b"(Advanced) | "a2"(Standard)
  "generated_at": "2026-10-10T15:30:00+09:00",
  "status": "OK",                         // OK | PARTIAL | RF_UNAVAILABLE
  "inputs": { "article_path": "...", "article_sha256": "...", "ledger_path": "...", "ledger_sha256": "...",
              "ledger_fact_count": 15, "splitter_version": "en_split_v1", "n_sentences": 32,
              "prompt_sha256": { "A3": "9d9950428419...", "A4": "c87b95e5bcf1..." } },
  "conditions": [                         // 4条件の実行結果(モデル別集計の元)
    { "model_key": "luna",       "model_id_requested": "gpt-6-luna",           "model_id_returned": "gpt-6-luna",
      "condition": "A3", "status": "OK", "attempts": 1, "n_flags": 3, "cost_jpy": 0.17, "finish": "stop",
      "raw_path": "raw/luna_A3.json", "error": null },
    { "model_key": "gemini35fl", "model_id_requested": "gemini-3.5-flash-lite", "model_id_returned": "gemini-3.5-flash-lite",
      "condition": "A4", "status": "OK", "attempts": 1, "n_flags": 0, "cost_jpy": 0.22, "finish": "STOP",
      "raw_path": "raw/gemini35fl_A4.json", "error": null }
  ],
  "issues": [
    { "issue_id": "meta__run_03__b1b__s8",
      "sentence_id": "s8", "sentence_index": 8,
      "sentence_text": "...",
      "context": { "before": ["s6 text", "s7 text"], "after": ["s9 text"] },
      "related_fact_ids": ["HF-002", "HF-003"],
      "facts": [ { "fact_id": "HF-002", "text": "<台帳ブロック全文>" } ],
      "flag_reasons": [ { "model_key": "luna", "condition": "A3", "type": "その他", "severity": "重大",
                          "confidence": 0.34, "question": "..." } ],
      "detected_by": [ { "model_key": "luna", "condition": "A3", "confidence": 0.34 } ],
      "n_detectors": 1, "confidence_max": 0.34,
      "raw_flag_source": ["raw/luna_A3.json"],
      "review_state": "UNREVIEWED" }
  ],
  "unlocated_flags": [ ]                  // 文ID未特定・無効Flag(MATCHING_RULE_01 §2: 別掲、issuesには含めない)
}
```

- **重複統合キー**: `(article_id, level, sentence_id)`(MATCHING_RULE_01 §1/§3準拠。同一文に複数Flag→**文単位で1 issue**に集約し`flag_reasons`/`detected_by`に全元情報を保持。Flag単位件数と文単位ユニーク件数を両方集計)。`sentence`文字列が文IDの文と(空白・句読点除去で)不一致→`unlocated_flags`へ(件数0でも0と明記)。
- OR統合=4条件のどれか1つでもFlagすればissueに入る。confidenceは相対比較用(MATCHING_RULE_01 §8、絶対評価に使わない・閾値でフィルタしない)。
- `context`(before/after 各最大2文)は**Queue生成時にだけ**付与し、LLM入力には含めない(Trial入力と同一性を保つため、Trialのunitは`before=""/after=""`)。
- Markdown(`queue.md`)は`HUMAN_REVIEW_POST_EN_01.md`様式: 記事→issue→該当英文/対応Fact(日本語台帳原文)/理由(A3/A4×モデル)/検出元/review_state。
- `index.jsonl`1行: `{article_id, run_id, level, generated_at, status, n_issues, n_unlocated, queue_path, article_sha256}`。

---

## 6. 外部API障害時ルール

### 6-1. 既存Productionのルール(引用・実測)

- **Writer技術的retry**: `er003_v1_en_direct_vfl_01_generate.py::run_writer_with_technical_retry`(L407-L433)= `max_attempts=2`、例外時`time.sleep(2)`後に再試行、2回失敗で`TECHNICAL_GENERATION_FAILED`を返す(例外で落とさず状態で返す)。
- **TTS technical retry**: `PRODUCTION_MAX_TTS_ATTEMPTS=3`(`er011_human_review_lock_01.py` L80、標準+minimal fallbackの内訳assert L104)。ASR Cascade未解決は`human_review_queue.jsonl`へ(CURRENT_SPEC L1949)。
- **横断監査(CURRENT_SPEC L1952)**: 「Production全体のretry/regenerate/polling上限…**上限が全く無い経路は0件**」。Assembly Audio Validation Gateは異常時に例外で完全停止(自動retryなし)。Human Review Lockは明示承認なしに再処理しない。
- **Model Routing Fail-Closed契約(CURRENT_SPEC L2291〜)**: 規定外Model/Provider・Model未指定・SDK defaultフォールバックは**API call前に**`ModelContractViolation`。「fallbackとして高価なmodelへ自動昇格しない」。
- **OPEN-233 Production Flow仕様9(未配線)**: `api_failure`は許可リスト4種のHuman Review出口の1つ。
- **RF Trialのドライバ(`run_flagger_01.py` L51-L52,L297-L316)**: `TRANSIENT_RETRIES=2`(待機2×n秒)、`FORMAT_RETRIES=1`(JSON/schema違反時に1回だけ再質問)。A4-DUALMODEL-OR-TRIAL-01の実測では44 cell全てattempts=1・transient例外0。
- **未確認**: 「OpenAI/Gemini全体の障害(長時間outage)時にProduction全体をどうするか」を明文化した規定はCURRENT_SPEC/PM_GOVERNANCEをgrepしても見つからない(上記の個別規定のみ)。

### 6-2. RF技術障害の最小設計案(新仕様ではなく既存規定の組合せ)

1. **条件ごとに独立実行**(Luna A3/Luna A4/Gemini A3/Gemini A4)。1条件の失敗が他条件・記事・TTSへ波及しない。
2. 各条件の技術retryは**Trialと同一値**(transient 2回[2×n秒待機]・format 1回)。有界(1条件最大4 attempt、1記事最大16 call)。「自動retryなし」の解釈(記事側retry/再生成なし=維持、API技術retryは既存規定どおり)は **D-5で要確認**。
3. retry後も失敗した条件は`conditions[].status="FAILED"`(`error`型・メッセージ先頭300字・attempts)としてQueueに記録。`validate_flags`違反(format retry後も)は`INVALID`として同様に記録(破棄ではなく`raw/`に保存)。
4. 記事レベル`status`: 4/4成功=`OK`、1〜3成功=`PARTIAL`、0成功または入力不整合(台帳不完全・prompt sha不一致・記事なし)=`RF_UNAVAILABLE`。いずれも**例外を呼び出し元へ伝播せず、TTS/scaffold stageへ進む(STOPしない・記事再生成しない・削除しない・Rewriteしない)**。`index.jsonl`に`status`を必ず1行残す(Human Reviewが「この記事はRF未実施」と分かる)。
5. `ModelContractViolation`(routing契約違反)・価格未登録(`PricingNotFoundError`)も当該条件を`FAILED`(reason=`model_contract`/`pricing_missing`)として記録し、モデル自動切替(Luna↔他、Gemini→他モデル)はしない(Fail-Closed契約の維持、独自fallback禁止)。「契約違反は設定ミスのため大きく警告」はD-5で併せて確認。
6. 予算ガード: RFのcostは`raw_usage_log.jsonl`へ記録し、既存`assert_budget_ok`(後続stage)が累計に含める。RF stage自体は`assert_budget_ok`を呼ばない(非Blocking維持)。1記事worstは約16 call(通常は4 call・¥0.75)。

---

## 7. Risk Flagger Production入力の同一性

### 7-1. 対応表(Trial → Production)

| 要素 | Trial(POST-EN-TRIAL-01/A4-DUALMODEL-OR-TRIAL-01) | Production(Phase 2で構築) | 同一性 |
|---|---|---|---|
| 英語稿 | `inputs/<unit>.md`(固定コピー)。出所: `…/b1b/article.md`(7本)または`audit/deviation_checks/advanced_attempt1.json`のpromptから復元した稿(4本: U07,U08,X09,X11、`source_kind=recovered_from_dev_check_prompt`、「完成記事ではないSTOP稿」)。**全て Advanced(b1b)のみ** | `<out_dir>/b1b/article.md`(Advanced)と`<out_dir>/a2/article.md`(Standard)。構造は同じ(`# Title`/本文/`## In one line`)。同じ`er012_e::_run_writer_stage_once`が出力するため形式一致 | 形式=同一。**Standardは未検証(S-3)** |
| 台帳 | 各runの`research_ledger/verified_fact_ledger.txt`(**完全台帳**、B3 Selected Briefではない)。sha256をmanifestで固定、API前にassert | `<out_dir>/research_ledger/verified_fact_ledger.txt`(er019 entertainment runner L91-L135がTrialと同じ`vfl01.build_verified_ledger_text`で生成、REJECTED除外済み)。B3 Selected Fact Brief(`storyline_b3/selected_brief.md`)は**使わない** | 同一(同じ生成関数・同じファイル種別) |
| `[AMBIGUOUS - …]`見出し | `vfl01`が`[AMBIGUOUS - 断定禁止、曖昧さを保持すること] <ID>: <claim>`を生成(L292)。旧`ledger_restore_01._HDR`は`[A-Z_]+`のみで**AMBIGUOUS Factを無音で脱落**(FIX01)。post_en_common.HDRで補正(`^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$`)し、expected(行頭`[`行数)==regex見出し数==parsed==manifest(重複IDなし)をAPI前assert(LEDGER_COMPLETENESS_01.md: 8テーマPASS、streaming_priceにAMBIGUOUS 2・semiconductorに1) | **Production台帳にも該当する**(同じ生成関数、`vfl01` L292-L293)。Production moduleは補正済みregexを自前で持ち、同じ完全性assertを**実行時**に行う。不一致=`RF_UNAVAILABLE(reason=ledger_incomplete)`(旧parserでの無音脱落を許さない) | 保証方法あり(実行時assert)。Production側に旧parserは入れない |
| A3/A4 prompt | `antenna_prompts.antenna_system(3/4)`。sha256 `9d9950428419c3af824cc5b8676a4b564f96aeb87657c547d418cc86ef3538e9`(A3)/`c87b95e5bcf1b5c266b8978c5688849eb339a6087efbcaf56bb7399ed128ef01`(A4)。driverで`EXPECT_SHA`をassert、既存Sol rawとsystem/user完全一致をdry-runでassert(22/22) | Production moduleがprompt本文を**byte-identicalな定数として保持**(Trial dirからimportしない=Trial依存禁止)。起動時にshaをassert、不一致=`RF_UNAVAILABLE(reason=prompt_sha_mismatch)`。**Prompt変更なしで配線可能**(Trialは`P.d2_system`等をmonkeypatchして注入しているだけで、promptテキスト自体は固定文字列) | 同一(test: system sha一致+同一sentence/factを注入した`build_user`出力がTrial保存requestと一致) |
| user prompt/schema | `P.build_user(unit)`、`validate_flags`(sentence_id∈sids、type∈`P.TYPES`+因果+`その他`、severity、confidence∈[0,1]、question必須、fact_ids⊂台帳ID) | 同じ検証規則を移植 | 同一 |
| 呼出パラメータ | Luna: OpenAI Responses `reasoning.effort=medium`・`max_output_tokens=8000`・`instructions=system`・`input=user`。Gemini: REST `generateContent`、`systemInstruction`+`contents`+`generationConfig.maxOutputTokens=8000`、thinkingConfig/temperature/responseMimeType**送らない**(Provider既定) | 同一request body(Gemini REST方式を維持するか、SDKへ移すかは13節 D-7。SDKに移す場合は同一body確認テスト必須) | 同一(要test) |
| 文分割・文ID | `R._split_sentences`(略語保護なし)。unitの`before/after`は空 | 新splitter(4-3)。**文ID付番が変わる**(U03/U06/U07/X09/X10/X11の21文付近)。LLM入力のsentences listが変わる | **意味的に異なる点(許容案)**: 途中切断の修正であり検出対象の文章内容は同一。S-6/D-6で承認要 |
| 文脈(before/after) | 空文字 | Queue生成時のみ付与、LLM入力には入れない | 同一(LLM入力に影響なし) |

### 7-2. 結論

**入力は「Advanced英語稿全文+完全台帳+同一A3/A4 Prompt+同一schema」としてProductionで同じ意味に構築できる**(Prompt変更なしで配線可能)。完全台帳の保証は実行時assert(expected==regex==parsed==ID一意)で行い、不一致はRF_UNAVAILABLEとして記録する。

意味的に異なる点(STOP候補として列挙、勝手に新仕様を作らない):
- **差1(S-3): Standard(a2)稿はTrial未検証**。Trial 11本は全てAdvanced(b1b)。RFをStandardにも適用するか(費用2倍・検証母集団外)はユーザー判断。
- **差2(S-1): Writer母集団**。Trial稿の7本はFact Lock新Writer腕(`factlock_astra_e2e_trial_01/runs/<theme>/new/…`)、X09〜X11はB1回復前の`b1b_prev_b1`(同runs配下)。**旧Writer(Luna R0→R1→R2)のProduction記事でのRF検出性能は未検証**(Meta rollback等のTrialはer019 meta run_03の旧稿を使用=旧Writer例はあるが、A4-DUALMODELの11本評価セットには含まれない)。
- **差3**: 4/11本は「Advanced STOP稿の復元」(完成記事ではない)。ProductionではChecker撤去後、この種の稿がそのまま流れるため、RFが唯一の網になる(Trial上のFlag数は参考値として扱う)。
- **差4(D-6)**: 文分割変更に伴う文ID変化(上記)。

---

## 8. Model routing・runtime evidence・費用

### 8-1. モデル固定とactual model_idの記録

- **固定方法**: `er006_model_routing_contract_01.py`の`PROCESS_MODEL_MAP`に2キー追加(先例: `"FAMILY_X_FLASH_LITE_TTS": "gemini-3.8-flash-lite-tts"`、L119)。案: `"FAMILY_X_RISK_FLAGGER_LUNA": "gpt-6-luna"`、`"FAMILY_X_RISK_FLAGGER_GEMINI": "gemini-3.5-flash-lite"`。**環境変数での上書きは設けない**(`require_model`がAPI call前にfail-closed)。Production初期値は有効(ユーザー決定で配線対象)。
- **Luna actual model_id**: OpenAI Responses応答の`resp.model`を`model_id_returned`として条件ごとにQueue/evidenceへ記録(Trialの実測: `model_ids_returned=["gpt-6-luna"]`)。`requested != returned`なら`model_mismatch=true`を記録(既存`adv_result.fallback_detected`と同じ思想、`er003_v1_n3_01_advanced_adaptation_generate.py` L469)。自動切替・自動破棄はしない。
- **Gemini**: REST応答の`modelVersion`を同様に記録(Trial実測: `gemini-3.5-flash-lite`)。

### 8-2. Production側の費用計測ギャップ(Phase 2で必ず対処、事実)

1. `er005_output/cost_baseline_01/pricing_snapshot.json`に`gpt-6-luna`は登録済み(L255-L291)だが**`gemini-3.5-flash-lite`は未登録**。`_load_pricing().price()`は未登録を`PricingNotFoundError`でfail-closed(er012_e L106-L121)。→ 単価登録が必要(Production変更)。出典付きの確認済み値は`meta_rollback_crossmodel_01/xm_prices_01.json`(2026-10-10取得、公式`https://ai.google.dev/gemini-api/docs/pricing`、$0.30 in/$0.03 cached/$2.50 out per 1M、出力単価はthinking tokensを含む)。**実装時に再確認して登録**(PM運用メモ: 価格は出典付き確認済み値のみ)。
2. `er005_cost_logger.py::_gemini_usage_to_dict`は`candidates_token_count`のみ記録し**思考token(`thoughts_token_count`)を含めない**(Trialは`output=candidates+thoughts`で計上)。かつRF TrialのGemini呼出はREST(`requests`)でありSDK patchを経由しない。→ RF moduleが自前で`raw_usage_log.jsonl`互換レコード(`provider="gemini"`,`model_id`,`input_tokens`,`output_tokens=candidates+thoughts`,`reasoning_tokens`,stage tag=`risk_flag`)を書く。
3. er019 entertainment runnerの`compute_stage_cost_breakdown`(L240)は`provider=="openai"`のみ集計(Gemini無視)。audio runnerの`compute_cost_jpy_so_far`(L1528)は`openai/gemini/openai_asr/gemini_batch`を`by_provider`で集計(実測: meta__run_03 ¥23.98=openai 5.09+gemini 15.58+asr 3.31)。→ RF stageはaudio runner側(`risk_flag`)に置く案ならRF費用が`by_provider`に出る。

### 8-3. runtime evidence設計(`runtime_evidence.json`+Queue `conditions[]`)

記事×レベルごとに: `run_id`/git HEAD/RF module sha256/splitter_version/prompt sha(A3・A4)/入力sha(記事・台帳)/`conditions[]`(上記5-3: model_key・model_id_requested/returned・condition・status・attempts・transient_retries・format_retries・n_flags・input/output/reasoning tokens・cost_jpy・elapsed_s・finish_reason・error・raw_path)/OR統合結果(n_issues・n_unlocated)。

**モデル別集計(`review_queue/post_en/MODEL_STATS.json/.md`、集計script`er0XX_risk_flagger_aggregate_01.py`が全`queue.json`から再計算)**: articles processed / A3 flag count / A4 flag count(モデル別) / unique issue count(モデル別・OR後) / overlap count(≥2条件が同一文を検出、うちLuna∩Gemini) / zero-flag article count(モデル別・OR後)。**Gemini A4が0件でも停止・削除・モデル変更しない**(経過観察のみ。Trial実測: Gemini A4は11本全て`flags:[]`、finish_reason=STOP、空応答/打切り/解析失敗0=A4-DUALMODEL RESULT_01)。zero-flag続きでも自動対応は組まず、集計表に出すだけ。

### 8-4. 記事単価の参考値(実測の根拠行)

出典: `er052_output/writer_dev_risk_flagger_01/a4_dualmodel_or_trial_01/runs/{luna,gemini35fl}/<unit>/A{3,4}.json`の`cost_jpy`を合算(read-only、11本×2レベル×各モデル)。

| | A3 | A4 | 合計(11本) | 1記事平均 |
|---|---|---|---|---|
| Luna(`gpt-6-luna`) | ¥1.629 | ¥1.820 | ¥3.449 | **¥0.314** |
| Gemini(`gemini-3.5-flash-lite`) | ¥2.393 | ¥2.371 | ¥4.764 | **¥0.433** |
| 合計 | | | ¥8.213 | **¥0.747** |

ユーザー提示の参考値(Luna ¥0.31 / Gemini ¥0.43 / 合計¥0.75)と一致。レイテンシ実測: Luna 1 callあたり平均11.5秒、Gemini 1 callあたり平均0.84秒(同上`elapsed_s`)。4条件は独立のため並列実行可(記事あたり約12秒に短縮見込み、ただし並列化の実測は未)。**Advanced+Standard両方に適用する場合は約¥1.49/記事(Standardは未測定の外挿=推測のため「未確認」扱い)**。

---

## 9. Dangling reference候補(撤去後に孤立しうる参照)

区分: **[P]=Production到達不能にする/書き換える** **[T]=Trial/DEV artifactとして残す(Production不到達を静的testで保証)** **[L]=legacy A/B/C共有のため残置**

| 種別 | 候補 | 区分 | 備考 |
|---|---|---|---|
| retry/regeneration | 案B(JA差し戻し1回)・M1要約再生成・must-fix再生成・`--regenerate-stage`後のrecheck | P | R-07/R-10/R-13/R-14/R-17/R-18/R-19。`--regenerate-stage advanced/standard`は技術的な再生成として残るが旧Checker再検査はなくなる |
| fallback | Checker起点のfallbackは無し | - | 確認済み(2節) |
| error handling | `JAFactCheckStopError`(Fact用 raise L305/L433)、`JARecheckRequiredError`、er019 runnerのFact用ハンドラ、`ja_recheck_attempt1*.json`出力 | P | 記号QAのSTOP(L341/L486)は`JASymbolCheckStopError`へ分離して維持(B-1) |
| runtime switch | `OPEN243_M1`(adv L583-L602)・`OPEN243_M2`(vfl01 L685-L723)・`OPEN243_G3_TELEMETRY_PATH`(er012_e L441)・`OPEN233_RECLASSIFY_PROTECT_FLAGS`(Trial E2E runnerが子processへ渡す環境変数)・`full_ledger_text is not None`ゲート・`storyline_line`有無による案B有効化 | P(Family X経路)/T | M1(要約入力切替`_open243_iol`)の扱いはB-3/D-4 |
| validator/schema | `writer_run_summary.json`のキー`deviation_overall_status`/`must_fix_used`/`retried_for_deviation`/`ja_recheck_*`、`audit/deviation_check*.json`、`audit/deviation_checks/*.json`、`audit/rejected_*` | P | 下流の依存は`er019_writer_run_summary_reconstruction_01.py`のみ(grep済み)。出力スキーマ変更をdocに明記 |
| Prompt | jaw `build_must_fix_block`(Full Ledger再掲、JA)・`build_original_prompt`のmust_fix分岐 | P(削除) | |
| Prompt | adv/std `build_must_fix_block`("Fact Safety issues… Verified Fact Ledger"文言、advanced_adaptation L325)+`_FAMILY_X_PARAGRAPH_RETRY_MUST_FIX` | **残置(B-2)** | 段落retryが同関数を使う。**Prompt文言変更は禁止のため変えない**。文言がFact Safety前提のまま段落retryに使われている点だけ記録 |
| Prompt | `vfl01.DEVIATION_PROMPT_TEMPLATE`/`ORIGIN_ENUM` | L | legacy A/B/Cが使用 |
| tests | `er019_family_x_ja_recheck_retry_01_test_01.py`(24参照)=案B専用→廃止/書換。`er019_family_x_ja_writer_o_r1_r2_01_test_01.py`(11)、`er012_e_family_entertainment_two_level_runner_test_01.py`(10)、`er019_family_x_new_structure_wiring_01_test_01.py`(13)、`er019_family_x_entertainment_production_runner_01_test_01.py`(5)、`er019_family_x_b3_production_wiring_01_test_01.py`(2)、`er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py`(1)、`er019_family_x_pointless_01_test_01.py`(1)、`er019_writer_run_summary_reconstruction_01_test_01.py`(1) | P | 件数は`git grep -c "run_ja_writer_o_r1_r2\|JAFactCheckStopError\|JARecheckRequiredError\|run_writer_stage\|…"`のヒット数。記号QA・段落retry・予算ガード等の技術QAテストは維持 |
| docs/SSOT | CURRENT_SPEC.md Family X節の項目4・5(L1230-L1262「Fact Check方針(実装・配線済み)」「ja_source MAJOR時の暫定retry拡張(案B)」)、OPEN-233節末尾の「古い日本語から英語を再生成するProduction経路…再生成後のChecker(`run_deviation_check`)で必ず再検査される接続仕様」(L2338節)、Production Flow仕様10「Family X固有」、OPEN_ITEMS OPEN-187/189/233/243/244、`docs/pm/b3_trial_01/design_01.md` L65等 | P(SSOT) | CURRENT_SPECは「既存節は削除・書換せずlegacy/superseded注記」の運用(L1472〜)。Phase 2でGate 3後に更新(今回は更新しない) |
| Trial依存 | `er052_factlock_astra_e2e_runner_01.py`/`_stub_01.py`(`run_writer_stage`・`JARecheckRequiredError`等に各8参照、旧腕=er019経路をsubprocessで利用)、`er052_factlock_sweep_01_test_01.py`(2)、`er052_factlock_writer_trial_01_test_01.py`(1)、`er052_output/open243_translation_ng_analysis_01/_assemble_analysis.py`(2)、`er052_output/factlock_writer_trial_01/astra_revise_matrix_02/tools/gen_r0_small_bag.py`(3) | T | Production撤去後は「旧腕を再現できない」Trial。再現性が必要なら撤去を**既定OFFスイッチ+Trial限定opt-in**にする案(S-6/D-3) |
| telemetry | raw_usage_log.jsonlのstage tag `ja_original_check/_retry`,`ja_r2_check/_retry`,`ja_original_must_fix`,`ja_r2_must_fix`(by_stage集計・過去runとの比較) | P(新runで0件になる) | 過去run比較のためtag名自体はdocに残す |
| 関数(共有) | `vfl01.run_deviation_check`・`deviation_audit_record`・`DEVIATION_FLAG_KEYS`、`er010_ledger_local_rewrite_09`(legacy Local Rewrite) | L | legacy A/B/Cが呼ぶため削除しない(Family Xから呼ばれなくなるだけ) |

**Production到達不能の静的保証(Phase 2 test)**: `er019_family_x_entertainment_production_runner_01.py`/`er012_e_…`/`er019_family_x_ja_writer_o_r1_r2_01.py`/`er019_family_x_audio_production_runner_01.py`からのimport・呼出グラフに`run_deviation_check`/`JARecheckRequiredError`/Fact用`JAFactCheckStopError`/`_must_fix_from_deviations`/`open243_m1_summary_only_retry`が到達しないことをAST+`git grep`で検査。

---

## 10. 既存APPROVED項目との整合(変更はしない・整理案のみ)

| 項目(SSOT) | 現Status | 本設計との関係 | 矛盾 |
|---|---|---|---|
| R0後Hard STOP Fact Check除去(DECISION_LOG L20490、OPEN-244) | `APPROVED_FOR_PRODUCTION`・未`PRODUCTION_WIRED` | Productionの対応物は「JA Original後(`R0_PROMPT`)のFact Check+must-fix+STOP」=R-01(L275-L325)。撤去対象に含む | なし。ただし「R0」は新Writer(Fact Lock)の用語で、旧Writerの対応物の読替えが必要。**R2後チェック(R-02)は決定文に明記なし → D-2** |
| 翻訳後Hard STOP Fact Check除去(同) | 同上 | EN Advanced/Standardのdeviation check+STOP=R-11〜R-17 | なし |
| 新Writer+Production Checkerなし+A3/A4+Human Review(OPEN-244) | `APPROVED_FOR_PRODUCTION`・未`PRODUCTION_WIRED` | **新Writer(Fact Lock)がProduction未配線のため、本IDだけでは概念の一部(「Checkerなし」「A3/A4」「Human Review」)のみ実現**。Writerは旧Luna R0→R1→R2のまま | 範囲の食い違い(S-1) |
| A3+A4の英訳後・音声化前配置 | `VALIDATED`(2026-10-10) | 1-3の配置と一致。VALIDATEDの根拠はAdvanced 11本のTrial(Standard未検証、Writer母集団差) | なし(適用範囲は S-3) |
| AI Pre-sorter | 新規Trial・Production採用未決 | 本設計に含めない(runnerへAPI組込みなし)、ユーザー決定どおり | なし |
| OPEN-241 gpt-6-luna全工程routing | `PRODUCTION_WIRED`(2026-10-08) | RFのLunaは同モデル。routing contractへ**追加のみ**(既存キー無変更) | なし |
| OPEN-243 翻訳段NG・Checker見逃し | POST_USER_VALIDATION | 旧Checker撤去でENの機械的ガードは消え、RFが観測網になる。POST-EN-TRIAL-01で「Hormuz oil prices・BYD In One Line文は未Flag」の検出限界が既知 | 要認識(リスク) |
| Family X Fact Check方針(CURRENT_SPEC L1230-L1262項目4、`PRODUCTION_WIRED`2026-09-27) / 案B(同項目5、`APPROVED_FOR_PRODUCTION`・Gate 3待ち) | 現行仕様 | **今回の撤去で置換される**。Phase 2でSSOTに`SUPERSEDED`注記(削除しない) | 更新漏れに注意 |
| OPEN-189(JA Fact Check固定費約¥2.20/記事・latency約110秒の改善) | OPEN | 撤去で解消見込み(記載値はCURRENT_SPEC L1234、旧モデル時の値で現在値は未再測) | なし |

**OPEN-233の整理案(今回は変更しない)**: 現状=Self-Recovery Flow `APPROVED_FOR_PRODUCTION`(2026-10-05)・Checker新仕様+Floor縮小 `APPROVED_FOR_PRODUCTION`(2026-10-06)・CHECKER-FLOOR E2E 9/20 run完了・`PRODUCTION_WIRED`未・残11 run停止(OPEN_ITEMS.md OPEN-233行、CURRENT_SPEC L2338)。いずれも**Production正式runnerへは未接続**(1-2、import 0件)。ユーザーが「Production Checkerなし」を正式決定したため、(a)OPEN-233のProduction配線(新規`er0XX_self_recovery_flow_01.py`作成・Family X経路への接続)は不要になる可能性が高い、(b)資産(Trial runner・Checker・Stage 2・rubric V7b・E2E 9 run証跡)はDEV/Trial/将来のHuman Review補助として保持、(c)**案**: OPEN-233 Statusを「Production配線は`OPEN-244`/本IDで置換(superseded)、Trial/DEV資産として保持・再開余地あり」とし、**残11 runの扱い(中止/保留)をユーザーに確認**。Fable/ユーザー判断で確定(D-8)。

---

## 11. Runtime evidence計画

### 11-1. 検証レベル(安い順、全て実Production正式path起点)

| Lv | 内容 | 通す経路 | 目的 |
|---|---|---|---|
| L1 | 既存Production記事に**RF moduleのみ**を実行(新API: Luna 2+Gemini 2 call) | 例: `er019_output/family_x_refresh_e2e_01/meta/run_03/{research_ledger,b1b,a2}` | 4条件・Queue・重複統合・GitHub参照・モデル別集計の実在確認。Production Writerの既存稿に対するRF結果を取得 |
| L2 | **既存記事のregen経路(推奨)**: 既存runから`research_ledger/`・`storyline_b3/`・`ja_writer/`を新out-dirへコピーし、`er019_family_x_entertainment_production_runner_01.py --stage all`(research_ledger・storyline_b3・JA R2は既存成果物の再利用分岐L330-L336,L354-L357、EN Advanced→Standardを再生成・旧Checkerなし)→`er019_family_x_audio_production_runner_01.py --stage all`(`risk_flag`→scaffold→tts→assemble→player)を実行 | Production正式path(retry/regeneration/resume分岐を実際に通る) | stage順序(RFが英訳後・TTS前)・Checker不到達・RF_UNAVAILABLE時にTTSへ進む(fault injectionは別途¥0)・技術QA維持の同時確認 |
| L3 | **新規記事1本の完全経路**(research→ledger→B3→JA→EN→RF→TTS→assemble) | Production正式path全体 | 初回pathの完全確認。**テーマはユーザー選定(PM_GOVERNANCE 13節)** |

PRODUCTION_WIRED判定にはL2以上が必要(「実Production正式pathで1記事以上」)。L2を第一推奨(既存記事で足り、新規テーマ選定が不要、費用最小)。L3を求めるかはユーザー/Fable判断(D-11)。

対象記事案(L1/L2): `er019_output/family_x_refresh_e2e_01/meta/run_03`(research_ledger・storyline_b3・ja_writer・b1b・a2が全てtrackedで揃う、既存音声は`er019_output/family_x_audio_production_wiring_01/meta__run_03`)。副案: 同`hormuz/run_03`(research_ledgerは`verified_fact_ledger.txt`のみ・a2は`audit`のみで不完全、使用は要確認)。Metaは過去Trial(Meta rollback等)の題材でもあり、RF結果を過去のFlagと照合しやすい可能性(未確認)。

### 11-2. 新規記事テーマ候補(ユーザー選定用。選ぶのはユーザー。Claude/Fableは選ばない)

出典: `er052_output/factlock_astra_e2e_trial_01/NEW_THEME_CANDIDATES_01.md`(2026-10-09、候補10件のうち**未選定の6件**から5件を再提示。ユーザー選定済みだった#1,#2,#7,#8とユーザー提案2件は除外)。**現在のニュース性・一次情報の取得可否・台帳が3件以上に育つかは全て未確認**(research実施まで不明、補欠入替あり)。

| # | English | 日本語 | 短い選定理由 |
|---|---|---|---|
| a | Japan's Minimum Wage Increase Takes Effect(元#4) | 最低賃金の引き上げが各地で始まる | 都道府県別の金額・上げ幅・対象範囲の混同が起きやすく、数字・範囲の限定でRFの効きを見られる(前回補欠だった) |
| b | Coffee Prices Surge: Why Your Cup Costs More(元#10) | コーヒー価格の高騰、なぜカップが高くなるのか | 原因が複数(天候・為替・需給)で、因果の断定と「要因の一つ」の書き分けが核心。生活者向け(前回補欠だった) |
| c | A Crewed Moon Mission Schedule Update(元#9) | 有人月探査ミッションの日程見直し | 「計画/目標/決定」の確からしさ段階の取り違え(提案か決定か)を試せる。宇宙兵器とは別題材 |
| d | A New Study Links Sleep Habits to Health Outcomes(元#6) | 睡眠習慣と健康の関連を示す新しい研究 | 相関と因果、対象者の範囲(年齢・人数)の書き分け。数字は中程度 |
| e | Record Heat and the Strain on a Power Grid(元#3) | 記録的な暑さと電力需給のひっ迫 | 需要記録・予備率の数字と、気象と電力の因果の書き分け。季節性のある生活ニュース |

(元#5ノーベル賞は固有名詞中心で今回の目的に弱いため候補から外したが、希望があれば追加可能。)

### 11-3. 1記事あたり費用の見積(**既存実測を根拠**、推測なし。「未確認」は未確認と明記)

| 工程 | 値 | 根拠(実測の出所) |
|---|---|---|
| research+ledger+B3(L3のみ) | **¥13.5〜¥57.4/テーマ**(中央値¥27.6、6テーマ) | `er052_output/factlock_astra_e2e_trial_01/stage_r/COST_STAGE_R.md`(`er019 compute_stage_cost_breakdown`による実測、gpt-6-luna+web_search) |
| JA Writer(旧Writer、Fact Check込み) | ¥3.49(meta run_03)・¥4.02(hormuz run_03)※JA stage tag合計 | `er019_output/family_x_refresh_e2e_01/{meta,hormuz}/run_03/cost.json`。**撤去後はFact Check分(`ja_original_check*`/`ja_r2_check*`/`must_fix`)が消える**(例: meta run_03のcheck系=0.532+0.909+0.303=¥1.744) |
| EN(Advanced+Standard、旧Checker込み) | ¥4.22(meta run_03のUNTAGGED) | `er019_output/family_x_refresh_e2e_01/meta/run_03/raw_usage_log.jsonl`を`compute_stage_cost_breakdown`で集計(read-only実行)。stage未tagのため内訳は不明、旧Checker分の割合は**未確認** |
| 新Writer(Fact Lock+Astra) | **本ID範囲外(未配線)。Trialの新仕様腕実績はraw ¥395.12/7テーマ(Astra段のみ¥336.71、B1回復再支出¥102.99[推定]含む)** | `er052_output/factlock_astra_e2e_trial_01/runs/final_aggregate/AGGREGATE.md` §7。Production単価は**未確認** |
| RF 4 call | ¥0.75/記事(Advanced 1本)。Advanced+Standard適用時は約¥1.49(Standardは実測なし=外挿) | 8-4(A4-DUALMODEL-OR-TRIAL-01、11本実測) |
| 音声(scaffold+TTS+ASR+assemble) | **¥23.98**(meta__run_03、openai 5.09+gemini 15.58+asr 3.31)。別runで¥89.03(b3_production_wiring_01 run_01、backend・retry条件の差は**未確認**)・¥7.02(run_02_parallel_b、一部stage) | `er019_family_x_audio_production_runner_01.py::compute_cost_jpy_so_far`で`er019_output/family_x_audio_production_wiring_01/*/raw_usage_log.jsonl`を集計(read-only) |

見積の使い方(単純和、上記実測の範囲): **L1 ≈ ¥0.75〜¥1.5**(RFのみ)。**L2 ≈ ¥4.2(EN再生成、旧Checker込みの上限参考)+¥0.75〜1.5(RF)+¥24〜89(音声)=約¥29〜¥95**。**L3 ≈ L2+JA Writer¥3.5〜4.0+research等¥13.5〜57.4=約¥46〜¥156**(新Writerは含まない)。TTS費用は条件差が大きく上限は不確実。各runnerの既定`--budget-jpy 150`で守られる。実行前にFable/ユーザーがCapと承認を判断(今回Phase 1は¥0)。

---

## 12. Phase 2 実装計画(別委任、Opus独立レビュー+Fable照合後)

### 12-1. 変更ファイル一覧(番号`er053_*`は仮、実装時に採番)

| # | ファイル | 種別 | 内容 | 規模(見込み) |
|---|---|---|---|---|
| 1 | `er053_family_x_risk_flagger_production_01.py` | 追加 | RF本体: A3/A4 prompt定数+sha assert、入力builder(完全台帳parser+完全性assert)、Luna/Gemini呼出(transient2/format1 retry)、`validate_flags`移植、OR統合・重複統合、Queue/evidence書込、RF_UNAVAILABLE/PARTIAL処理。**Trial dir・er050/er051/er052をimportしない** | +600〜800行 |
| 2 | `er053_en_sentence_splitter_01.py` | 追加 | 4-3の共通splitter(`splitter_version`定数) | +100〜150行 |
| 3 | `er053_risk_flagger_aggregate_01.py` | 追加 | 全`queue.json`からモデル別集計(`MODEL_STATS.json/.md`) | +120〜180行 |
| 4 | `review_queue/post_en/README.md`(+初回実行で`index.jsonl`) | 追加 | 保存先説明・schema_version・GitHub参照URL | 小 |
| 5 | `er006_model_routing_contract_01.py` | 変更(追加のみ) | `PROCESS_MODEL_MAP`へ`FAMILY_X_RISK_FLAGGER_LUNA`/`_GEMINI`の2キー。既存無変更 | +10行 |
| 6 | `er005_output/cost_baseline_01/pricing_snapshot.json` | 変更(追加のみ) | `gemini-3.5-flash-lite`のinput/cached/output(Standard)。出典URL・取得日・確認方法を記載 | +3エントリ |
| 7 | `er019_family_x_audio_production_runner_01.py` | 変更 | `--stage risk_flag`追加、`all`に`plan`の後・`scaffold`の前で組込み、`entry_point.json`へRF記録。**RFの例外は呼び出し元へ伝播させない** | +50〜80行 |
| 8 | `er019_family_x_ja_writer_o_r1_r2_01.py` | 変更(削除中心) | R-01〜R-05撤去。`JAFactCheckStopError`→`JASymbolCheckStopError`へ分離(B-1)。Original→R1→R2連鎖・記号QA・fallbackは維持 | −150〜200行 |
| 9 | `er012_e_family_entertainment_two_level_runner_01.py` | 変更(削除中心) | R-08〜R-20撤去(`_run_writer_stage_once`/`run_writer_stage`簡素化)。段落3分割retry・予算ガード・封鎖stubは維持。`must_fix`受け口はB-2のため維持 | −300〜350行 |
| 10 | `er019_family_x_entertainment_production_runner_01.py` | 変更(削除中心) | R-06/R-07、docstring更新 | −30〜50行 |
| 11 | tests(下記12-2) | 変更・追加・無効化 | 8本前後の既存testを撤去仕様へ更新、案B専用testは無効化(Trial参照用に残置) | ±600行 |
| 12 | `er019_writer_run_summary_reconstruction_01.py`(+test) | 無効化(docstringにlegacy注記) | 旧Checker出力前提のため新runでは不要 | 小 |
| 13 | CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md/PM_BRIEF等 | 変更(Gate 3完了後) | 項目4・5、OPEN-233節接続仕様、OPEN-187/189/233/243/244の更新、`SUPERSEDED`注記 | 小〜中 |

合計見込み: 新規コード約+1,000行、テスト約+800行、削除約−500行。**変更しない**: A3/A4 Prompt、`vfl01`の共有関数、legacy A/B/C runner、既存splitter(A)(B)(C)、Trial dir(`er052_output/…`、`er052_*`)。

撤去方式(S-6/D-3): **案P(物理削除)** = Family X経路から旧Checkerコードを削除(上記規模)。**案Q(既定OFFスイッチ)** = コードは残し`fact_check_mode`既定`off`、Trial runner(`er052_factlock_astra_e2e_runner_01.py`等)のみ明示`legacy`でopt-in。Qは旧腕のTrial再現性を保つが「Production到達可能なruntime switch」が残る。**推奨=案P+Trial用に旧版を`er052_output/…/legacy/`へ凍結コピー**(Production不到達を静的testで強く保証でき、Trial再現も可能)。ただし構造変更なので**Opus条件Aレビューで確定**。

### 12-2. テスト計画(全て¥0、mock/fixture/既存artifact)

1. **Splitter regression**: `U.S. officials said…`/`The U.K. government announced…`/`Mr. Trump spoke.`/`Dr. Smith agreed.`/`…on Jan. 5.`が**途中分割されない**+通常の文末分割(`It rose 5%. Prices fell.`→2文)、閉じ引用符(`…“20% plan.” It called…`)、`No. 5`/`St. Louis`/`a.m.`/`USA TODAY Co. said`/`Inc.`/`e.g.`、見出し行`# Title`が1文、`...`。**実データ**: Trial 11入力で略語終わり文が0件になる+それ以外は旧splitterと同一(差分は略語結合のみ)。
2. **旧Checker不到達のstatic test**: Family X Production module群(上記4ファイル)について、AST+`git grep`で`run_deviation_check`/`JARecheckRequiredError`/Fact用`JAFactCheckStopError`/`_must_fix_from_deviations`/`open243_m1_summary_only_retry`/`OPEN243_M1`/`ja_original_check`/`ja_r2_check`の参照0件。**retry/fallback/regeneration/resume各経路**(`--regenerate-stage`、JA再利用分岐、段落retry、`run_writer_stage`の`only=`)をモック実行し、`vfl01.run_deviation_check`が呼ばれないことをspyで確認。
3. **技術QA維持test**: 記号Validator(`original_symbol`/`r2_symbol`→`JASymbolCheckStopError`)、段落retry→STOP、予算ガード、`fallback_detected`、assemble Audio Validation Gate、Key Phrase source整合Gateが従来どおり動く既存testの再実行(回帰)。
4. **Review Queue test**: schema検証(手書きvalidator、`pip install`なし)、OR統合・重複統合(同一文をLuna A3とGemini A4が検出→1 issue・`detected_by`2件・`flag_reasons`2件)、文ID未特定Flagが`unlocated_flags`へ別掲、`context`はQueueのみでLLM入力に不含、`index.jsonl`追記専用・既存行不変、`git check-ignore`でqueue pathが非ignore(rc=1)、Markdown生成。
5. **入力同一性test**: A3/A4 system sha一致(`9d995042…`/`c87b95e5…`)、同一sentence/fact注入時の`build_user`・Luna body・Gemini bodyがTrial保存request(`dry_run/*/A{3,4}_request.json`)と一致、完全台帳assert(`streaming_price`/`semiconductor_earnings`の実台帳+AMBIGUOUS fixture)、旧`_HDR`なら脱落することの負例。
6. **障害系(fault injection)**: 4条件を全失敗/1条件失敗/format不正/`ModelContractViolation`/`PricingNotFoundError`にした場合に、`RF_UNAVAILABLE`/`PARTIAL`が`queue.json`と`index.jsonl`に記録され、例外が伝播せずscaffold/ttsへ進む(戻り値/終了コードで確認)。自動Rewrite・削除・STOP・article再生成のcallが0。
7. **routing/cost test**: `require_model`で誤model→`ModelContractViolation`、Gemini単価登録後の費用=`input×0.30+(candidates+thoughts)×2.50`(per 1M)の計算一致、RF cost recordが`raw_usage_log.jsonl`へ出る。
8. **モデル別集計test**: articles processed/A3/A4 flag count/unique issue/overlap/zero-flag articleの算出(Gemini A4 0件でも集計は出る・何も停止/削除/変更しない)。

### 12-3. Gate 3チェックリスト(PM_GOVERNANCE Gate 3/Gate 4に基づく)

**Static 8項目**
1. S1 Production module群が`er050`/`er051`/`er052_*`/`er052_output`をimportしない(`git grep`)
2. S2 Family X Production経路に旧Checker呼出0件(AST+grep、上記test2)
3. S3 retry/fallback/regeneration/resume各経路で旧Checker不到達(call-graph/spy test)
4. S4 A3/A4 prompt sha・schemaがTrialと一致
5. S5 model固定(routing 2キー・env上書きなし・fail-closed・pricing登録済み)
6. S6 RFが非Blocking(RF結果から分岐するSTOP/Rewrite/削除/regeneration/自動retryのcall 0、例外非伝播)
7. S7 splitter regression PASS、既存splitter(A)(B)(C)無変更(diff 0)
8. S8 Dangling Reference Check(9節の全項目がgrepで0件または`SUPERSEDED`注記済み、docs/tests整合)

**Runtime 11項目**(実Production正式path)
1. R1 formal runner(er019)でL2以上を実通し(Trial runner経由でない)
2. R2 RFが英訳(Advanced/Standard)完了後・TTS開始前に実行された(timestamp/log順序)
3. R3 4条件のcall完了、`model_id_returned`(Luna=`gpt-6-luna`、Gemini=`gemini-3.5-flash-lite`)記録、mismatch 0
4. R4 call count・cost(Gemini思考token込み)・retry・error・flag countを記録
5. R5 `review_queue/post_en/<id>/`+`index.jsonl`をcommit/pushし、`raw.githubusercontent.com`から読めることを確認
6. R6 重複統合・`detected_by`保持(複数条件が同一文を検出した実例、なければfixtureで補完を明記)
7. R7 略語文(`U.S.`等)を含む記事で途中分割0
8. R8 RF_UNAVAILABLE経路(fault injection、¥0)でTTS以降へ進む
9. R9 TTS以降の技術QA(Audio Validation Gate・Key Phrase source整合・Review Lock)が正常動作
10. R10 旧Checkerの呼出0(raw_usage_log.jsonlのstage tagに`ja_*_check`/`ja_*_must_fix`なし、`audit/deviation_check*.json`が生成されない)
11. R11 Gemini A4が0件でも停止/削除/モデル変更なし、モデル別集計(MODEL_STATS)出力

**Model evidence**: 実際のmodel_id(requested/returned)・routing key・単価出典(URL・取得日)・1記事費用を`runtime_evidence.json`+REPORTへ。Opus条件A/C所見の反映状況をGate 3に含める(PM_GOVERNANCE Gate 3)。`CURRENT_SPEC`/`DECISION_LOG`/`OPEN_ITEMS`更新・Git反映・approved specとProduction挙動の一致確認。

### 12-4. 並列化・順序(PROJECT-DELIVERY-SPEED、8-X)

- **並列可(独立ファイル・独立test)**: (1)RF module+Queue writer (2)splitter+regression test (3)pricing/routing追加+test (4)集計script (5)旧Checker撤去(jaw/er012_e/er019 runner/既存test更新は**ファイルごとに1担当、同一ファイルの並行編集は禁止**)。
- **直列(理由明示)**: Opusレビュー→Fable照合(前工程出力依存・PM Gate)→実装→static/unit test(コード依存)→L1/L2 runtime evidence(API支出・予算Guardrail・RFモジュール完成が前提)→SSOT更新・commit。runtime evidenceのL1とL2は条件同一性のため同一コード(同一HEAD)で実施。
- 時間見込み: 本Phase 1は調査中心。Phase 2の実工数は未見積(行数規模は12-1)。クリティカルパス=Opus/Fableレビュー→撤去方式確定(S-6)→RF module→L2実行。

---

## 13. STOP候補・要判断事項(設計書は完成させ、勝手に新仕様を作らず報告)

**STOP候補(Fableへ)**

| ID | 内容 | 該当STOP条件 | 推奨 |
|---|---|---|---|
| **S-1** | 新Writer(Fact Lock/Astra)はProduction未配線。旧Writerのまま旧Checkerを撤去すると「旧Writer+Checkerなし」(承認コンセプトOPEN-244は新Writer前提)。RFの検出性能も旧Writer記事では未検証(Trial評価11本は新Writer腕) | 新しい仕様判断が必要 | (a)本IDは旧Writer上でCheckerなし+RFへ進む(新Writer配線は別ID)をユーザーが承認、または(b)新Writer配線を先行/同時。**ユーザー判断** |
| **S-2** | R2後JA Fact Check(R-02)の撤去: ユーザー決定文は「R0後」「翻訳後」のみ明記。委任文の「旧Fact Checker(Ledger比較のBLOCK/Rewrite/retry/regeneration)撤去」は包括的 | 新しい仕様判断(解釈) | 包括解釈(R-01〜R-22全撤去)で進める旨の確認 |
| **S-3** | RF適用対象: Trialは**Advanced(b1b)のみ**。Standard(a2)は未検証。「英訳完了後」の英訳はAdvanced/Standardの両方 | Production入力がTrial入力と意味的に異なる | (a)Advancedのみ(¥0.75)(b)両方(約¥1.49、Standardは未検証の母集団)。**ユーザー判断** |
| **S-4** | 技術QAとの境界曖昧: B-1(`JAFactCheckStopError`共用)、B-2(`must_fix`機構・"Fact Safety"文言が段落retryと共用)、B-3(`_open243_iol`) | 境界がコード上不明 | 3節の解決案(例外分離・must_fix受け口維持・Prompt文言不変)。**Opus条件Aで確認** |
| **S-5** | 「自動retryなし」の解釈: RFのAPI技術retry(transient 2/format 1、Trial同一)を維持してよいか | retry・fallbackの設計判断 | 記事側retry/再生成なし=維持、API技術retryは既存Production規定(Writer technical retry等)と同様に許容。確認 |
| **S-6** | 撤去方式(案P物理削除/案Qスイッチ)と、Trial旧腕(`er052_factlock_astra_e2e_runner_01.py`等)の再現性 | retry・fallbackに設計判断が必要な旧Checker依存 | 案P+旧版凍結コピー。**Opus条件A** |
| **S-7** | splitter共通化は新規モジュール追加で他Production経路への影響0だが、Trial Human照合済み文IDとズレる(U03/U06/U07/X09/X10/X11) | splitter共通化の影響 | 新規追加案。照合は文面ベース+`splitter_version`保持。承認 |
| **S-8** | 費用計測ギャップ(Gemini単価未登録・thinking token未計上・`compute_stage_cost_breakdown`はopenaiのみ) | A3/A4 Prompt変更なしに配線できるが、Production費用機構の変更が必要 | 8-2の対処(単価登録は出典付き再確認)。Production変更を含むためGate/Opus条件C |
| **S-9** | Review QueueをGitHubへ載せる運用主体: runnerはgitを触らない。誰がcommit/pushするか | Review QueueをGitHub追跡対象にできない(運用側) | Claudeが実行後に`review_queue/post_en/<id>/`+`index.jsonl`のみ明示add→commit→push(CLAUDE.md Git運用ルールの範囲)。runtime evidence R5で必須化 |
| **S-10** | legacy A/B/Cの扱い: `vfl01.run_deviation_check`のlegacy Production呼出(15箇所/5モジュール)は「Production正式経路」に含めるか | 新しい仕様判断 | Family体系(Active=X/Y/Z)に従いFamily Xのみ撤去、legacyは不変(共有関数は残置)。確認 |

**確認事項(軽微)**: D-1 RFの挿入位置(audio runnerの`risk_flag` stage推奨 vs entertainment runner末尾) / D-4 `OPEN243_M1`/`_open243_iol`(Trial限定スイッチ)の残置可否 / D-5 契約違反・単価未登録を「FAILED記録のみ」でよいか(設定ミスの警告強度) / D-6 文ID変化の承認(S-7) / D-7 Gemini呼出をREST維持(Trial同一body)かSDK移行(cost logger統合、同一body確認test必須)か / D-8 OPEN-233のStatus整理(10節)と残11 runの扱い / D-9 ユーザー列挙8項目原文との照合 / D-11 runtime evidenceはL2(既存記事regen)で足りるか、L3(新規テーマ)まで要るか / Family Z(fiction、台帳なし)はRF対象外としてよいか。

**STOP条件の該当判定(委任文)**: 旧Checkerと技術QAの境界=一部曖昧(S-4)/Production入力とTrial入力の意味的差=あり(S-3、母集団S-1)/A3・A4 Prompt変更なしの配線=**可能(STOPなし)**/Review QueueのGitHub追跡=**可能(STOPなし、運用S-9)**/retry・fallbackの旧Checker依存=Checker起点のfallbackなし・案B/must-fix retryは撤去対象、設計判断はS-5/S-6/S-1/splitter共通化の他経路影響=**0(追加のみ、STOPなし、S-7はID変化の承認)**/新しい仕様判断=S-1/S-2/S-3/S-10。

---

## 14. 付録: 調査の根拠(再現コマンド、全てread-only・API 0)

- Production経路: `git grep -l "er052_open233" -- 'er003*.py' 'er009*.py' 'er010*.py' 'er012*.py' 'er019*.py'`(出力なし=0件)、`sed`/`grep -n`で各runner、`CURRENT_SPEC.md` L1472-L1510/L2338-L2433。
- 撤去対象行: `git grep -n "run_deviation_check(\|JAFactCheckStopError\|JARecheckRequiredError\|origin.*ja_source\|must_fix" -- er019_family_x_ja_writer_o_r1_r2_01.py er012_e_family_entertainment_two_level_runner_01.py er019_family_x_entertainment_production_runner_01.py`。下流依存: `git grep -n "deviation_check\|deviation_overall_status\|retried_for_deviation\|must_fix_used\|ja_recheck\|fact_checks_summary" -- 'er019_family_x_audio*.py' …`(`er019_writer_run_summary_reconstruction_01.py`のみ)。
- splitter事実: `.venv/Scripts/python.exe -X utf8`で`a4_dualmodel_or_trial_01/runs/{luna,gemini35fl}/<U01..X11>/A{3,4}.json`の`sentences`を走査(略語終わり文: U03×6/U06×3/U07×1/X09×3/X10×7/X11×1=21文)。X09 s7=`It all began with Mr.`、s8=`Trump’s “20% plan.” It called for … ensuring U.S.`、s9=`security.`。
- 費用実測: `compute_stage_cost_breakdown`/`compute_cost_jpy_so_far`を既存`raw_usage_log.jsonl`へread-only実行、`a4_dualmodel_or_trial_01/runs/*/A*.json`の`cost_jpy`合算、`COST_STAGE_R.md`・`AGGREGATE.md`§7。
- .gitignore: `git check-ignore -v`(4候補path、rc=1=非ignore)、`git ls-files`件数(`er019_output`1,034、`er052_output`17,302)。
- 委任文保存・検証(T-0): `docs/pm/delegation_log/2026-10-10_RISK-FLAGGER-PRODUCTION-WIRING-01_01.md`+`_check.json`(**FAIL**: 本委任文がテンプレート見出し構成[性質/事前指定Read/実行コマンド全文/SSOT追記文、固定ブロックE-1/D-1/G-1/F-1]を持たないため。作業は継続、非ブロッキング運用)。

---

## 14. Opus独立レビュー結果(2026-10-10)

(条件A新構造設計+条件C重要変更のProduction採用提案前。本節は追記のみで、1〜13節および旧14節(付録)は変更しない。旧付録と節番号が重複するが、指示どおりこの見出しで追記する。)

**総合: 条件付き同意。** 撤去棚卸(R-01〜R-22)はコードで確認済みで、技術QAを壊す削除はない。

### 論点1(撤去範囲): 同意+補足
- T-17/T-18(`er019_family_x_storyline_b3_fact_selection_01.py` のFact ID整合STOP L20-23/L242、research_ledger の `run_verification_for_topic`)を「維持」と明記すべき。
- `_open243_iol`(efam L459-464): 環境変数`OPEN243_M1`依存をProduction経路から外し、常にM1なしで呼ぶ。adv_gen側M1 promptはTrial用として残置。

### 論点2(撤去方式): 案P同意、ただし凍結コピーは不可
- 凍結コピーはimport先が現行ツリーのため凍結にならず、同名モジュール取り違えリスクがある。
- 代替: 撤去直前commitにgit tag、旧腕再現はgit worktree。
- Trial影響: `er052_open233_self_recovery_flow_runner_01.py` は影響なし。`er052_factlock_astra_e2e_runner_01.py` はL896-914 monkeypatch/L372 `_SCRIPTS` shaにより再開時STOP(tag固定で足りる)。

### 論点3(段階導入): 段階案を推奨
1. RF+Queue配線、Checker維持、runtime evidence取得
2. 旧Writer既存記事(`audit/deviation_checks/*.json`あり)にRFをL1で数本実行し、旧Checker MAJORとRF Flagの一致度を測る(1本約JPY0.75)
3. Checker撤去
4. 新Writer配線は別ID

RF追加とChecker撤去は触るファイルが重ならず、分割の手戻りなし。

### 論点4(挿入位置・UNAVAILABLE等): 修正必須あり
- audio runnerの`all`はplanを含まない(L1876, L1892-1932)ため、個別stage実行でrisk_flagが抜ける。tts直前に「article.md sha256に一致するQueueレコードがあるか、なければその場でRF実行(非Blocking)」の保険が必須。
- 挿入位置: entertainment runner末尾(Standard完了直後・Mandatory STOP L396の前)を主、audio側tts前を保険。
- RF_UNAVAILABLE: WARN表示+`entry_point.json`記録+MODEL_STATSのUNAVAILABLE件数+報告時列挙を必須。
- 台帳完全性assert不一致→RF_UNAVAILABLE(ledger_incomplete)は妥当。実装前に既存`er019_output`配下の`verified_fact_ledger.txt`全件をJPY0走査するテストを追加。
- S-5(有界API技術retry)に同意。

### 論点5(Review Queue schema): 条件付き
- levelは記事レベル(b1b/a2)で、A3/A4はdetected_by側。同一文のA3/A4は1 issueに統合される(正)。フィールドは`article_level`へ改名推奨。
- 修正: (a) pathにlevelが無い→1path=1levelか同居かを確定 (b) issue_idに`article_sha256`先頭8桁またはrf run_idを含める (c) `review_state=UNREVIEWED`固定は誤解を招く→削除、または書き戻し先を別ファイル定義 (d) 全文ID対応表`inputs/sentences.json`と台帳全文をQueueに同梱。
- S-9: push漏れ検知(git status/ls-files)をCloseout必須化。`index.jsonl`追記はlock/単一process。保存pathは`__file__`基準。

### 論点6(splitter共通化): 同意
新モジュール追加、既存(A)(B)(C)は無変更。golden test(略語33語)+`splitter_version`記録。S-7は実害小だが、LLMへ渡すsentence listが変わる点を報告に明記する。

### 論点7(費用計測): 事実誤認の修正必須
- audio runnerの`compute_cost_jpy_so_far`は単価未登録を0円扱い=fail-open(L1557-1564、`cost_usd`があれば採用 L1554)。efam側はfail-closed(L148-151)で`cost_usd`無視。RFレコードがentertainment out_dirにあると`--regenerate-stage`→`assert_budget_ok`で`PricingNotFoundError` STOPとなり、設計6-2と矛盾する。
- 最小修正: Gemini単価登録をPhase 2前提条件とする。単価キーはpinしたmodel_id(返却model_idは別フィールド)。output_tokens=candidates+thoughts、`cost_usd`併記。LunaはSDK patchが自動記録(cost_logger L110-146)のため二重記録しない。`er005_cost_logger`の`_CONTEXT`がglobal(L42/L79)のため、4条件は逐次実行(約25秒/記事)か、競合解消後に並列。

### 論点8(runtime evidence・その他)
- L2は`ja_writer/`をコピーするとJA再利用分岐(er019 entertainment runner L354-357)でjaw(R-01〜R-05)を通らない。research_ledgerとstoryline_b3のみ再利用しJA再生成(+約JPY3.5)。古い`audit/deviation_checks`をコピーしない(R10誤判定防止)。
- RF前後で`article.md` sha256不変をassert+テスト。
- Queue保存失敗時はTTS継続+out_dir fallback+WARN+`entry_point.json`記録、except範囲を明記。古いQueue検知はtts前sha照合。
- a2はAdvancedから別LLMで書き直し(efam L617)のため、Checker撤去+RFがAdvancedのみだとa2を見る網がゼロ(S-3判断材料)。
- 残留リスク(記録のみ): 旧Checkerの「EN対JA翻訳一致」観点(`source_article_text=ja_text`)はRFでは代替されない。

### 実装前必須修正8点
1. T-17/T-18の「維持」明記と`_open243_iol`のM1非依存化(論点1)
2. 凍結コピー案を撤回し、git tag+git worktreeへ変更(論点2)
3. audio側tts前のQueue sha照合+必要時RF実行の保険(論点4)
4. RF_UNAVAILABLEの可視化4点(WARN/entry_point.json/MODEL_STATS/報告列挙)と、台帳全件JPY0走査テスト(論点4)
5. Queue schema修正(a)〜(d)(論点5)
6. S-9運用: push漏れ検知、index.jsonl排他、`__file__`基準path(論点5)
7. 費用計測の修正(Gemini単価登録の前提化、fail-open/closed不整合解消、二重記録回避、逐次実行)(論点7)
8. L2手順(ja_writer非コピー、古いdeviation_checks非コピー、article.md sha不変assert、Queue保存失敗時の扱い)(論点8)

### ユーザー判断
- **S-1 / S-3 / D-1**: ユーザー判断が必要。
- S-2 / S-10: 設計書推奨の確認で足りる。
