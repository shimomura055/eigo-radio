# EXISTING_SPEC_CHECK_01 — 既存仕様・過去Trial・現行Z経路の照合(PM_GOVERNANCE 21節)

管理ID: FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_01(Phase 0、API 0、Production code変更0)。照合日: 2026-10-26。
照合は読取のみ(Grep/Read)。`.venv`起動・有料API・Production file編集なし。行番号は2026-10-26時点のworktree。

## 0. 21節分類と11-8線引き

| 項目 | 分類 | 根拠 |
|---|---|---|
| 文脈・感情付きTTSをZ dialogueの標準方式にする | **C(新規)だがユーザー承認済み**(APPROVED_FOR_PRODUCTION、2026-10-26、原文=`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md`) | 新仕様だが採用判断はユーザーが完了。本件は『配線』であり、新仕様提案・再質問ではない |
| Trialの方式・Prompt・検査規則 | **B(過去Trialあり)→採用済み** | OPEN-516(Round 1/2)・OPEN-528(全編)。Trial結果を再利用し、同じTrialは再実施しない(Phase 2はTrialではなくProduction runtime evidence) |
| TTS総試行3回、HR Lock、ASR cascade、10分cooldownの定数 | **A(既存仕様あり)** | `er011_human_review_lock_01.py:80`(3回)、`er020_tts_retry_local_rewrite_01.py:57`(`COOLDOWN_SECONDS=600.0`、docstring『固定10分・短縮禁止』) |
| Z dialogueへのcooldown付与 | A(定数・関数は既存)+**dialogueへの適用は新規(ユーザー承認済み §2)** | 下表§3 行4 |
| Z dialogueのLocal Rewrite | **既存仕様の対象外(未配線)**=判断候補J-1 | §3 行3 |

11-8線引き: 範囲内=ユーザー決定§2・§3をZ既存経路へ実装すること。範囲外=ユーザー決定に無い受理面・閾値・方式・試行回数・クールダウン時間の新設/拡大、X/Y/B/C/narrator/KPへの拡大。

## 1. 確認対象7種(21節)と結果

| 対象 | 確認内容 | 結果(ファイル:行) |
|---|---|---|
| `CURRENT_SPEC.md` | Z dialogue/ER-011/Local Rewrite/HR Lock/a2減速/OPEN-517 | Local Rewrite=『英語のみ・5 role』(Grep `Local Rewrite(英語のみ・5 role)`、L2871付近)。『Section固有の既存例外』(5)A2減速=通算TTS3回を共有する外側ループ(Dialogue Std/Voices A2も)(L2870付近)。(6)Dialogue=複数Voice・話者帰属・Segment構造を維持。Assembly最終段ヘッドルーム安全弁=L2123(閾値0.98)。**Z dialogueに文脈・感情方式の記述は無い**(未採用のため) |
| `DECISION_LOG.md` | 先頭書式 | 先頭に『- YYYY-MM-DD \| 管理ID 委任_NN (OPEN-xxx…) \| 本文』形式(本委任で同形式を追記) |
| `OPEN_ITEMS.md` | OPEN-528/516/511 | OPEN-511=調査(反映していない=設計上不可)、OPEN-516=Round 1/2 Trial、OPEN-528=全編通しTrial(PHASE1B_DONE_USER_LISTENING_PENDING)。本件はOPEN-528を追跡行として使う(新規OPEN行は作らない) |
| 過去Trial | Round 1/2・全編 | `docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/{DESIGN_02,OPUS_REVIEW_01,TRIAL_RESULT_01,EVAL_01,BUDGET_LOG_01}.md` を全文照合。Fable目視レビューは全編53件でaccept 53・discard 0(`er118_output/fz_full_episode_trial_01/*/*/llm/emotion_review.json`の集計、下記§4) |
| Production code | Z dialogue生成・retry・組立 | §2・§3 |
| regression・validator test | `er063_family_z_audio_01_test_01.py`ほか | 既存testファイルの存在のみ確認(編集せず)。Phase 1で新testを追加し既存を回す |
| 関連管理ID・commit | FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01(速度v2)、AUW(統一judge)、FX-FZ-CHUNK-TTS(narratorのみ) | dialogueの速度仕様v2(Adv atempo 1.06・Std無処理)は不変で維持 |

## 2. 現行Z dialogue経路の動作(ファイル:行)

入口: `er026_family_z_fiction_production_runner_01.py:2344 stage_tts` → `er063_family_z_audio_01.py:1367 run_tts_stage`(Z scope `er109`+Secondary run scope)→ `:1383 _run_tts_stage_impl` が ClipSpec 列を clip 単位で回す(`:1425〜1470`)。

| 経路 | 現行動作 | 根拠 |
|---|---|---|
| 初回生成 | `generate_or_reuse_z`(`:824`)がreuse_key一致+status OK+sha一致で再利用、それ以外は `real_generators()["dialogue"]`(`:917`)。Std=`bvoices.generate_voice_body_wide_margin(text, out_path, voice)`(`:929`、`style_prefix_override`なし)。Adv=`n3_tts.generate_with_a2_slowdown_outer_loop(..., lambda max_attempts: bvoices.generate_voice_body_wide_margin(text, out_path, spec.voice, max_attempts=max_attempts), slowdown_pct=Z_ADV_DIALOGUE_SLOWDOWN_PCT)`(`:920〜927`) | er063 |
| retry | `generate_voice_body_wide_margin`(`er012_b_family_voices_production_01.py:483`)の内部ループ `for attempt in range(1, max_attempts+1)`(`:518`)。`max_attempts`既定=`PRODUCTION_MAX_TTS_ATTEMPTS`=3(`er011_human_review_lock_01.py:80`)。**全attemptが同一Style**(`style_prefix_override or p9a.ENGLISH_STYLE_PREFIX`、`:520`)、待機なし(即時retry) | er012_b |
| 『fallback』 | 段階的Style切替は**無い**。attempt内でTTS技術失敗/発話区間検出失敗のときだけ `generate_voice_body_minimal_fallback`(MINIMAL_INSTRUCTION、`:537〜546`、同じattempt番号の追加生成として `attempts_log` に2行) | er012_b |
| 採否判定 | 各attemptで ASR Primary→`evaluate_attempt_with_cascade`(統一judge、Secondary含む、`:560`)→disfluency gate→repetition QA(`:567〜574`)。verifiedならOK返却。`stop_retrying`時は `ASR_VALIDATION_UNCERTAIN` で打切り(`:605`)。3回未達なら次attemptへ、尽きれば `STOPPED`(`:614`) | er012_b |
| Adv外側ループ | `n3_tts.generate_with_a2_slowdown_outer_loop`(`er003_v1_n3_01_tts_generate.py:434〜479`): `gen_fn(remaining)`→atempo 1.06→減速後を統一judgeで再検証→NGなら**通算3回の残予算**で取り直し。生成数は `count_tts_generations_in_result`(`:298〜306`、=attempts_logの行数、最低1)を累積。通算3回目の減速後NGは `finalize_a2_slowdown_final_ng`(`:309`)でHR Lock+HR queue 1行 | n3_tts |
| 回数の数え方 | 初回を含めて3回(上記ループ)。外側ループは減速後NGも1回に数える(『通算TTS3回を共有』、CURRENT_SPEC『Section固有の既存例外』(5)) | 同上 |
| クールダウン | **dialogue経路には無い**。既存のcooldownは (a) narrator `er003_v1_sing01_news_tail_fix.py:143〜152`(`retry_primitive.maybe_cooldown_before_attempt`、最終attemptの直前に10分)、(b) `er003_v1_repro01_main_generate.py:337〜342`(通算3回目直前、`COOLDOWN_BEFORE_OVERALL_ATTEMPT`イベント)、(c) crosslevel/A2(`prior_generations`・`cooldown_total_budget`、`er003_v1_n3_01_tts_generate.py:404`)。実体=`er020_tts_retry_local_rewrite_01.py:64〜92`(`time.sleep(600)`の単一sleep、**STOP sentinel確認なし**)。実測: 全Z run の dialogue 667 entry 中 `cooldown_occurred`=0(下記§2注) | grep |
| Local Rewrite | **dialogue経路には配線が無い**。LR呼出は `er003_v1_sing01_news_tail_fix.py:301/327`(narrator)、`er003_v1_n3_01_tts_generate.py` のA2系、`...voice01_generate.py`のみ。`er012_b_family_voices_production_01.py` にLR呼出ゼロ(Grep済み)。`finalize_a2_slowdown_final_ng` のdocstringも『A2外側ループ内にはLR配線が無く(06d dlg_cap2でもLLM呼出0)』と明記(`:319`)。実測: dialogue 667 entry 中 `audio_text_deviation`=0 | grep+実測 |
| HR Lock | `@review_lock.guarded_generate("en")`(`er012_b:482`)。呼出前 `check_before_generation`(`er011:299`)がHUMAN_REVIEW_REQUIRED/HUMAN_APPROVEDで0 API、呼出後 `record_outcome`(`er011:357`)でRESOLVED/HUMAN_REVIEW_REQUIRED、`cumulative_tts_attempts`(上限15、`:68`)を累積。同一out_pathのネスト呼出はcheck/recordをskip(reentrancy、`:670〜702`) | er011 |
| regeneration | (a) `approve_regenerate`(`er011:474`)でREGENERATE_APPROVED→次の呼出で消費、(b) runner `--only-clips`(clip限定再実行、`stage_tts`→`run_tts_stage(only_clips=…)`)、(c) 外側ループ内の取り直し | er011/er026 |
| resume/中断再開 | clip完了ごとに `save_checkpoint`(`er063:1216`)。再起動時は `load_checkpoint` で完了clipのみ再利用(`generate_or_reuse_z`)。**clip途中のattempt履歴・残回数は保存されない**(未完了clipは attempt 1 から再実行し、`record_outcome` の累積15回guardだけがrun間の安全弁) | er063 |
| STOP | clip開始前に `_check_stop_sentinel(run_dir, "tts:<clip>")`(`:1196`、`:1430`付近)と runner の `wrap_generators_with_budget`(`er026:2321`)が各clipで確認。**clip内の待機中(sleep)は確認しない** | er063/er026 |

§2注(実測、API 0): `er026_output/family_z_production_e2e_01/*/*/*/audit/tts_generation_results.json` ほか run直下 level dir の `clip_kind=="dialogue"` 667 entry(複数runの合算。重複あり): attempts 数=1回645/2回16/3回6(2回以上=3.3%)、`audit_text_deviation`あり=0、`cooldown_occurred`あり=0。

## 3. ユーザー仕様 vs 現行cascade 差分表

区分: **[実装可]**=ユーザー仕様どおり実装できる / **[順序変更]**=既存cascadeの順序変更が必要(判断候補) / **[維持]**=既存仕様の維持で足りる。

| # | 論点 | ユーザー仕様 | 現行 | 区分 | 設計上の扱い |
|---|---|---|---|---|---|
| 1 | 試行回数の数え方(a) | 初回を含め最大3回、Fallbackは4回目でない | 初回含め3回(`er011:80`、`er012_b:518`)。外側ループは減速後NGも1回に数える | **[維持]** | 3回を『clip単位の永続attempt番号n=1..3』として一元管理。Advの減速後NGもn消費 |
| 2 | 1〜2回目=文脈・感情付き、3回目=従来方式 | 回ごとにStyleを切替 | 全attempt同一Style。段階切替は存在しない | **[実装可]** | attempt番号→styleを返すhookをgeneric loopへ追加(DESIGN_01 §C) |
| 3 | Local Rewriteの位置(b) | 3回目NG後に『既存のLocal Rewrite処理へ』 | **Z dialogueにLR未配線**(§2)。現行は3回NG→STOPPED→HR Lock→Gate BLOCK | **[順序変更]に近い=判断候補J-1** | 既定=LRを新設せず、3回NG後は現行どおり `STOPPED`→`record_outcome`→HR Lock→STOP(ユーザー仕様の『Local Rewriteで解決できなければ、既存のHuman Review／STOP規則』の後段は完全に満たす)。LRをdialogueへ新規配線するか否かはユーザー判断(OPEN_TRACKING_01 J-1) |
| 4 | クールダウン(c) | 2回目NG後に10分、3回目の直前 | dialogueに無い。narrator等で10分固定の既存primitiveあり | **[実装可]**(ユーザー承認済みの新規適用) | `er020.maybe_cooldown_before_attempt`/`COOLDOWN_SECONDS`を再利用。sleepはSTOP sentinel確認つきの分割sleepにして時間は短縮しない |
| 5 | resumeの状態復元(d) | 1〜2回目を再実行せず、3回上限を超えない | clip途中の履歴は保存されない(`generate_or_reuse_z`+checkpointはclip単位) | **[実装可]** | `<level>/audit/dialogue_ctx_attempt_state.json`(原子書込)にattempt開始前/後を永続化。started-but-unfinishedは消費済み扱い(安全側) |
| 6 | a2減速外側ループ(e) | (明示なし) | 減速後NGも通算3回に含む | **[維持]** | hookのnは外側ループの各passをまたいで継続(同一clipのpolicy objectが共有) |
| 7 | 10分cooldown中のSTOP/中断 | (明示なし) | narrator cooldownはsleep 600単一でSTOP不確認 | **[実装可]** | 5秒刻みのsentinel確認。cooldown開始時刻をstateに保存し、再開時は残り時間だけ待つ(10分未満へ短縮しない=経過時間は実時間) |
| 8 | HR Lock | 既存規則に従う | guarded単一呼出で一貫 | **[維持]** | policyは1回のguarded呼出の内側(ループ内)で動く。per-attempt guard呼出にはしない(per-attempt guardだと1回目NGでLockが立ち2回目が0 APIになる) |
| 9 | regeneration | 同一仕様 | REGENERATE_APPROVED/--only-clips/外側ループ | **[実装可]** | stateのstatus(IN_PROGRESS/DONE/TERMINAL_NG)で『再開』と『明示再生成(新規開始)』を区別(DESIGN_01 §C-6) |
| 10 | attempt内のminimal_fallback | (明示なし) | 技術失敗時にMINIMAL_INSTRUCTIONへ切替(同attempt番号の追加生成) | **[維持]** | 既存の安全機構として維持。ctx attemptで発火した場合その生成は文脈情報を含まない→evidenceに `effective_mode=minimal_fallback` を記録(判断候補ではなく開示) |
| 11 | reuse_key | 方式の保証 | dialogueのreuse_keyに方式識別なし(`style_prefix_sha256`=None、`er063:798〜815`) | **[実装可]** | run単位のpolicy識別子を `ClipSpec.extra` 経由でdialogue reuse_keyへ追加(policy=legacyのrunは不変) |
| 12 | 既存runの混在 | 方式の一貫性 | `assert_run_style_record`(`er063:701`)はroleのstyleのみ比較 | **[実装可]** | `audit/style_record.json` に追加キー `dialogue_tts_policy` を新規runで記録。キー無し=legacy policyとして継続(既存runは方式が混在しない) |
| 13 | Std/Adv差 | 両方 | Adv=外側ループ+atempo、Std=外側ループなし | **[維持]** | 差は外側ループの有無のみ。policyは共通 |

## 4. Trial固有の一時機構 — 持ち込まない/作り直す

| Trial機構 | 出所 | Production扱い |
|---|---|---|
| `redirect_production_sinks`(er113) | `er118_fz_full_episode_trial_01.py`/`gen_case` | **持ち込まない**(Productionは正規sinkへ書く) |
| `PHASE1_GO.json`/`_require_go`/`TRIAL_CAP_JPY` | Trial | **持ち込まない**(Productionは既存BudgetGuard/Guardrail) |
| `use_case`(Round 1/2 moduleのglobals切替) | Trial | **持ち込まない**(Opus M-6の趣旨どおり、Productionは引数明示の純関数) |
| Fable目視レビュー(`emotion_review.json` accept/discard) | Trial | **作り直す=決定論の自動受理**。根拠(`er118_output/**/emotion_review.json`の決定済み77件を集計、API 0): validator status×Fable決定=ACCEPTED→accept 49 / NO_EXPLICIT_CUE→accept 27 / DISCARDED→discard 1(Round 2猿の手part2_c6、機械DISCARDをFableが追認)。**Fableがvalidatorの判定を覆した件は0**(全編53件はaccept 53・discard 0)。DISCARDED/NO_EXPLICIT_CUEは`validate_emotion_items`が既に中立化済み |
| ALLOWED_NAMES手動追記(`whites`) | Trial | **作り直す**(DESIGN_01 §A-3: story registry由来のdataとして保持。検査規則は無変更) |
| Trial出力dir(`er118_output/...`)・Trial専用reuse key | Trial | **持ち込まない**。notes cache/stateはrun dirの`<level>/audit/` |
| 組立後M-5 3点assert(Trial vs Production比較用) | Trial | **持ち込まない**(比較用。Productionは通常assembly+headroom安全弁の記録) |
| NG clipをProduction原音に置換(M-8) | Trial | **持ち込まない**(Productionは3回NG→HR Lock→Gate BLOCK) |
| `capture_tts_requests`(送信prompt捕捉) | Trial/Round 2 | Production本体には入れない。Phase 2 evidence driverで再実装(Production外) |
| `leakage_*`(読み上げ混入検査) | Trial | **観測のみ**で持ち込む(再生成理由にしない。全編53件でflagged 0) |

## 5. Trial観測問題6項目 × 既存Validator

DESIGN_01 §E に同表を持つ。要点: 6項目のいずれも『既存の承認済みValidator・組立・品質条件に反する』と確認できたものは**0件**。反しない=新基準が必要=判断候補J-4。詳細はDESIGN_01 §E。

## 6. Dangling Reference候補(Phase 1後にGrepで確認)

- 維持する旧方式の参照点: `p9a.ENGLISH_STYLE_PREFIX`(`er003_b1_p9a_audio.py`、sha `add26d27…`)、`style_text_for`(`er063:790`、dialogue=None)、`build_reuse_key`(`:798`)、`_effective_style_sha`(`:1161`)、`extract_attempt_evidence`(`:1036`)、`verify_z_speed_profile`(`:1640`)、`generate_voice_body_minimal_fallback`。
- 新方式が参照されるべき後続: reuse_key(policy)、entry(`dialogue_tts`)、`audit/style_record.json`、evidence行(`_evidence_row`)、HR queue/attempt_history(`attempts_detail` の style_prefix_record)、Gate(`assert_tts_results_complete`は新キーを要求しない=旧readerが壊れない)、試聴ページ(変更なし)。表=DESIGN_01 §G。
