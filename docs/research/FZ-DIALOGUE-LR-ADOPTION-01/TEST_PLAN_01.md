# TEST_PLAN_01 — ZセリフLR正式導入のtest・runtime evidence計画(委任_01、コード/実行なし・API 0)

管理ID: FZ-DIALOGUE-LR-ADOPTION-01 / 2026-10-29 / 設計=`WIRING_DESIGN_01.md` / 基準線=`CURRENT_STATE_01.md` §8
方針: 不整合な出力を期待値にしない。test(API 0、fake/clock注入)で構造と全分岐を固定し、runtime evidence(正式経路・実API)は最小回数で原文§7の項目を埋める。DEV/Trial専用経路の動作だけでPRODUCTION_WIREDとしない。

## 1. test(API 0)— 新規 `er122_fz_ctx_policy_lr_test_01.py` ほか
| ID | 目的 | 主な検査 |
|---|---|---|
| **T-P(Profile/定数)** | | |
| P1 | Profile変更 | `PROFILES["Z_DLG_CTX"]==(lr True, total_slots 6, max_tts 6, max_waits 2, third LEGACY_DIALOGUE)`、`_self_check`通過、9 policy名集合不変、他8 Profileのフィールド不変 |
| P2 | 互換 | `Z_DLG_LEGACY`が`PROFILES`に残り lr=False/3/3/1、`policy=legacy` runは従来動作(LRなし) |
| P3 | 定数の一貫性 | er127/er122/er003外側ループ/leafの上限(6・ブロック3)がAST/値で一致。1箇所だけ3のまま残る回帰を検出 |
| **T-S(状態機械 er122 v2)** | | |
| S1 | 全NG経路 | fake TTS/ASR+clock注入: 1ctx,2ctx,[wait180],3legacy,LR,4ctx,5ctx,[wait180],6legacy→終端。mode/ordinal/slot/待機回数=2/実TTS=6/LR=1 |
| S2 | 途中PASS | n=1,2,3,4,5,6 それぞれでPASS→以降のTTS・待機・LR呼出0(n≤3 PASSはLR呼出0) |
| S3 | LR1回・再入禁止 | LR後の2回目LR要求→拒否(persisted `lr.state`)。`lr_recover`のdepth>=1→`LocalRewriteReentryError`。`run_local_rewrite_recovery(depth=1)`→RuntimeError。LR block内NG後にLRへ戻らない |
| S4 | 6回上限・kill/resume行列 | n_started=0..6の各時点・各phase境界(B1/LR(LLM前後・本文保存後)/B2)でkill→再開。実TTS総数≤6、消費済みattempt不再実行、待機は実時間経過で残りのみ(再開しても180秒未満にならない) |
| S5 | 待機 | 待機はn=3,6の直前のみ(n=4,5,2の前は0)。起点=直前attemptの最終NG確定時刻(Adv減速後NGは`note_final_ng`)。待機中STOP sentinel→`TtsBlockStopError`でstate据置(IN_PROGRESS)。`STOP_ALL`も同様 |
| S6 | ブロックゲート | B1終端でLR未実施のn=4要求→stop(fail-closed)。B1でremaining>0なのにLRへ入らない。LR本文未保存でB2開始不可 |
| S7 | v1互換 | v1 IN_PROGRESS(n=1,2)→v2でそのまま継続し6回構成へ。**v1 TERMINAL_NG(n=3)は自動ではLRへ進まない**(remaining=0・API 0・Lockが先にblock) |
| S8 | 再生成/新規サイクル | v2 DONE_OK/TERMINAL_NG +`explicit_regenerate`/`consuming_regenerate_approval`→新規サイクル(n=0・6スロット)。LR phaseのIN_PROGRESSは明示信号でもリセットされない(resume) |
| S9 | 会計 | `counted`/`carried_log`がLR境界で二重計上しない。resume時の`record_outcome`累積=旧3+新規のみ。`MAX_CUMULATIVE_TTS_ATTEMPTS`(15)との関係(2サイクル+α)、budget guard境界 |
| **T-L(LR flow)** | | |
| L1 | LR入力選択(c6実データ) | `ng_transcripts`=c6の#1/#2減速後/#3(実文字列)+確定項目(`sank for ever`,`on soft feet`等)→#2は文が確定Vocabと重なるため除外、#1採用。保護なし条件では#2採用。全転写でspan無し/全て保護文→`NOT_APPLICABLE`(TTS 0、`register_terminal_hr`1行、Lock=HR) |
| L2 | 候補事前保護 | `candidate_filter`: 確定語句/出典文/数字・固有名詞に触れる候補→`adoptable=False`(理由付き)、触れない候補は不変、全滅→`NO_CANDIDATE_PASSED_QA`(再TTS 0)。filter=None(X/Y/Z narrator)は出力byte同一。`precheck_candidate_overlap`と台帳`check_confirmed_overlap`が同一入力で同一判定(property test) |
| L3 | LR block内の不変条件 | LR block TTSのctx Style sha=B1のctx sha、Voice同一(Puck/Std Voice)、Adv fast6速度・減速後再検証あり、`script_version="v1"`、`m1_anchor_text`/Lock key/HRQ canonical=元原稿、送信本文=書換え後 |
| L4 | HRQ・Lock | HRQはn=6の判定器(最終slot)かLR不可の終端でのみ1行(n=3終端・LR前に書かれない)。LR成功時HRQ0行。Lock=RESOLVED/HR、`cumulative_tts_attempts` |
| L5 | 技術STOP | B1/B2での技術STOP(`TECHNICAL_STOP_STATES`)→LR・HRに入れない、stateはIN_PROGRESSで再開可 |
| L6 | stop_retrying | B1の同一ASR署名連続打切り→LR段へ。B2→終端(X/Y統一flowと同挙動) |
| L7 | Adv外側ループ | B1の減速後NG最終周回→`finalize_a2_slowdown_final_ng`・最終slot HRQなし→LR→B2最終NGで1回だけfinalize/HRQ。generations会計=ブロック相対。**既定kwの既存呼出(Voices A2・Z legacy・旧Z ctx経路相当)の出力byte同一(golden)** |
| L8 | Std | 外側ループ無し(単一leaf呼出)で同じ6回/LR/待機規則 |
| L9 | leaf attempt_ctx | `attempt_hook.attempt_ctx_kwargs`あり→`slot=n`,`total_slots=6`,`is_last_slot`はn=6のみ。hook=None(B/C)は`build_attempt_ctx`引数が従来と同一(golden) |
| **T-R(記録・Gate・表示)** | | |
| R1 | `final_adoption` | ①②③採用=depth0/ordinal=n/従来の記録同形。④⑤採用=depth1,ordinal1/2,slot ①'/②',PRIMARY,sent_style_sha=ctx。⑥採用=depth1,ordinal3,③',FALLBACK |
| R2 | er130分類核 | LR採用Z(PRIMARY④/⑤)→PASS_WITH_WARNING(LR_APPLIED)。⑥採用→FALLBACK_APPLIED+LR_APPLIED。slot{3,6}許可。`LR_ON_NON_LR_ROLE`: Z_DLG_CTXで出ない/Z_DLG_LEGACY・JA・SHELL等で出続ける。`dialogue_legacy_fallback_direct`: depth1,ordinal3,n=6で真/不整合recordで偽。`LR_TAKE_INCONSISTENT`回避の確認。既存`er130`53件は期待値の更新箇所(`:56,132,222,312,321`)以外不変 |
| R3 | er129台帳 | Z形LR(`audio_text_deviation`)のdialogue clip(引用符・入れ子単引用符つき実c6本文): before/after/changed_spans/anchor、`locate_op`一意、text_parity PASS、resume形(`resumed_without_llm`/`lr_selection_audit_restored`)でも理由が復元。T1/T2/T3: 確定語句/出典文に触れる合成LR→STOP verdict、触れない→PASS |
| R4 | 4者一致 | `er132.assert_text_parity`+`z_assemble_gate`: 表示overlay=TTS入力(`audio_text_after`)=ASR正解(`resolve_expected_text_after_local_rewrite`)=採用wavのASR転写(mock)。不一致/位置不能→技術STOP(HRに入れない)。LR注記が(a)TTS Prompt (b)ASR正解 (c)学習者向け本文に出ない(`assert_no_public_leak`・公開ページscan) |
| R5 | 最終報告(§6) | `er131`/`er133`: Before/After、変更箇所=赤、理由、対象clip+話者/Voice、最終採用がLR後か(`depth>=1`)、LR+Fallback両方該当で双方、Fallbackのみ=濃青、LRなしclipに赤なし。Zページ(Std/Adv・user page/開発者ページ)で描画 |
| R6 | build_entry/Style gate | LR採用dialogue entryの`audio_text_deviation`、`dialogue_tts`(n_started 4〜6)、`style_actual`が④⑤=ctx sha一致・⑥=従来Dialogue allowlist。`Z_STYLE_ACTUAL_MISMATCH`の偽BLOCKなし。承認Style不一致の実違反は引き続きBLOCK |
| **T-M(状態移行ツール `tools/fz_dialogue_lr_resume_01.py`)** | | |
| M1 | dry-run | 書込0・計画出力・前提検査の全項目表示 |
| M2 | 前提違反は中止(書込0) | text sha不一致/n_started≠3/`lr`使用済み/Lock≠HR/STOP sentinel(stop_scope rc=3)/ctx style sha不一致/`--clip`未指定/3 attemptのうち`counted`欠落 |
| M3 | apply(c6 stateのcopy) | state→IN_PROGRESS/phase=LR/n_started=3維持/attempts不変/`ng_transcripts`を出典付きで補完(#2減速後は`attempt_history.jsonl:20128`のイベントから)/Lock=REGENERATE_APPROVED(`approved_by`に原文§3参照)/attempt_historyに移行イベント/`*.pre_fzlr_migration`バックアップ。冪等(2回目拒否) |
| M4 | 再開 | 移行後のmock実行: B1の#1〜#3は再実行0(API counter=0)、LR→④…、Lock承認は1回だけ消費、終了時`record_outcome`累積=3+新規 |
| M5 | 他clip非干渉 | 移行対象外clipのstate・Lockが1バイトも変わらない |
| **T-D(既定・回帰)** | | |
| D1 | X/Y/Z既存共通経路 | er127 105件+subtests・`er127_test_golden_01`(80ケースbyte同一)・`er127_final_adoption_b1`18・Z narrator/KP/JA/topic_intro系・Y/X leaf test: **旧失敗集合と同一**(CURRENT_STATE §8の3件のみ) |
| D2 | Z dialogue通常パス不変 | 初回PASS(n=1)・n=2 PASS・n=3 Fallback PASSの結果dict/entry/lock store/attempt_history/state(新キー以外)が実装前goldenと同値 |
| D3 | scope外 | A/B/C・単体呼出は従来コードのまま(`unified_flow_active()`=False)。policy=legacy不変 |
| D4 | 切替口の不在 | AST/Grep test: 新flag・env・設定dict・起動scriptでLRをON/OFFできない(`er127.unified_flow_active`が唯一) |
| D5 | 一覧整合 | `ROW_MAPPING_02.json`の正式47行が`block_policy_for`の戻りと全一致、`Z_DLG_LEGACY`が正式行に出ない、compat行・`PROFILES["Z_DLG_LEGACY"]`は存在。CURRENT_SPEC表に『Zセリフ従来方式』独立行が無い(Grep) |
| D6 | Dangling Grep | `CURRENT_STATE_01.md` §6のD1〜D10各語(`MAX_TOTAL_ATTEMPTS`値・『LR未配線』『LRなし』Z dialogue・旧期待値)の残存を確認し、残るのは履歴注記のみ |

## 2. runtime evidence(実API・正式経路)— 原文§7全項目との対応
| ID | 内容 | 費用見込み | 取得物 |
|---|---|---|---|
| **E1(主)** | 藪の中Adv c6を移行ツール→正式runnerで実再開(`--stage tts_b1b --only-clips full_story_part3_c6 --mode real`)。LR(gpt-6-luna)→④(ctx)→PASSで停止(NGなら⑤→180秒→⑥→終端) | ¥0.7〜2.5 | LR Before/After(赤)・選定根拠・各attempt ASR/反復検査/減速後再検証・採否・Voice=Puck/ctx sha/速度・費用(cost_log)・Lock/state/HRQ・採用wavの**独立ASR再実行**・4者一致・日本語訳不変の目視 |
| E2 | 同stageで他13 Adv dialogue clipが再利用(API 0・wav sha不変) | 0 | sha表 |
| **E3(Std)** | 正式runnerのcopy-run(`er026_output/.../run_fzlr_ev_a2_01`等、`tru_ev_cases_01.py`式の**強制NG注入**=Gate判定のみ。『注入であること』を全記録に明記)でStd dialogue 1 clip: ①②NG→180秒→③NG→LR→④(PASS or ⑥) | ¥2.4〜3.5(TTS≤¥15枠内) | 6スロット表・実180秒×2(実測値)・実LR・Style/Voice維持・Std(減速なし)・Lock/HRQ |
| E4 | resume/再生成/再入禁止/policy=legacy/Lock: kill→resume(各phase境界)をcopy-run(TTS≤3)+test、E1実走の中断再開は偶発のみ | ≈¥1 | ログ |
| E5 | 回帰: §1 T-D実行ログ | 0 | pytest出力 |
| E6 | 完成候補: c6 OK後 `--stages provision_shell,gate,assemble,pages,page_verify`を**1起動**。Std/Adv候補ページ+(配線済みなら)End User向け。Voice配役・Std bandit・constable追加解説の維持照合 | ≈0 | page_verify結果・URL・公開ページ検証 |
注記: 起動は300秒内≤2、間隔≥150秒(RESTART_STORM)。有料run前に`stop_scope_check`。外部停止/rc≠0が2回続けば再起動せず報告。Cap: 現¥135(累計¥122.02)。見込み合計≈¥5〜8、推奨Cap¥145(7-7の300円以下自律)。

## 3. 原文§7(検証項目)→ test/evidenceの対応表
| 原文§7 | 検証 |
|---|---|
| 通常2回→180秒→Fallback→LR→通常2回→180秒→Fallback | S1, E3(Std実走), E1(Adv:④以降) |
| 最大6回の安全上限 | S1, S4, P3 |
| LR最大1回・再入禁止 | S3, E4 |
| 途中PASSで即終了 | S2, E1(④PASS時) |
| LR適用不可時の既存安全処理 | L1(NOT_APPLICABLE), L2(全滅), L5, R2 |
| LR後の元Style・Voice維持 | L3, E1/E3(送信Style記録) |
| ASR・反復検査・減速後再検証 | L3, L7, E1(Adv実走で減速後ASR) |
| Human Review Lock・終端NG | L4, M3/M4, S9 |
| retry/fallback/regeneration/resume | S4, S5, S8, M4, E4 |
| 既存runからの正規の再開 | M1〜M5, E1 |
| 最終本文・音声・学習項目の整合 | R3, R4, E1(独立ASR+日本語訳/KP/Word/文法不変) |
| X/Y/Z既存共通経路にRegressionがない | D1〜D4, E5 |
| 正式runtime evidence | E1, E3(copy-runは正式runner経由、注入明記) |
| Fableによる独立受入評価 | 実装後、Fable(`FABLE_ACCEPTANCE_01.md`) |

## 4. 完了判定(PRODUCTION_WIRED条件)
原文§7の全項目充足(上表)+ Opus条件A反映済み + SSOT(CURRENT_SPEC 8区分・ROW_MAPPING_02・DECISION_LOG・OPEN-602・UDR-TRA-1 supersede)+ Git + Fable独立受入。E1が④〜⑥で未PASSの場合でも『配線のPRODUCTION_WIRED』は正式経路のruntime発火(LR実行・状態移行・再開・HR終端)が確認できれば判定可能だが、**藪の中c6の完成は別**(未PASSなら新形式HR提示で報告、Status据置)。受入基準は`sandwich-pm.md`手順4-2に従い、ユーザー原文(c6を最短で完成候補へ戻す)との適合を別途記載する。
