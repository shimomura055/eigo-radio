# DESIGN_01 — Family Z 文脈・感情付きTTS 正式Production Wiring 設計(Phase 0)

管理ID: FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_01(2026-10-26)。到達上限=DESIGN_READY_FOR_OPUS(条件Aレビュー待ち)。
ユーザー決定: APPROVED_FOR_PRODUCTION(2026-10-26、原文=`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md`)。**PRODUCTION_WIREDではない**(Phase 0=設計のみ。Production code変更0・API 0)。
照合の根拠=`EXISTING_SPEC_CHECK_01.md`(ファイル:行)。要求項目=`SPEC_LEDGER_01.md`(R番号)。

## 0. 結論と設計の骨子

1. ユーザー仕様(ctx → ctx → 10分cooldown → 従来方式、総3回)は**そのまま実装できる**。ただし『3回目NG後のLocal Rewrite』は、**現行のZ dialogueにLRが配線されていない**(EXISTING_SPEC_CHECK §2・§3 行3)ため、既定は『LRを新設せず、現行どおりSTOPPED→HR Lock→STOP』とする。LRをdialogueへ新規配線するかはユーザー確認事項J-1(非ブロッキング)。
2. 骨子=**単一の clip単位 attempt policy object + 永続state**。全経路(初回/retry/fallback/regeneration/resume/中断再開/HR Lock)がこの1つのobjectを通る。決定者が1つなので経路間で方式がずれない。
3. 既存の ASR/Gate/retry ループ(`generate_voice_body_wide_margin`)は**単一コピーのまま**使い、ループの『attempt番号→Style』『attempt前後の記録/待機』だけを既定None(=現行とバイト同一)のhookで差し込む。
4. 感情・文脈情報は Trial と同一のPrompt/model/検査規則(sha固定)で run単位に1度だけ生成し、runの`audit/`に不変保存(resume・再runで再call 0)。Fable目視レビューは決定論の自動受理に置換(根拠: 決定済み77件でvalidatorとFableの判断が100%一致、覆し0件)。**新しい品質基準は作らない**。
5. Trialで観測された6問題は、既存の承認済みValidator・組立・品質条件に反するものが0件。新gateは作らない(J-4=非ブロッキングの開示)。

## A. 感情・文脈情報生成の正式経路

### A-1. 配置
- 新module `er122_fz_dialogue_ctx_tts_production_01.py`(番号はPhase 1着手時に空き確認。並行agentはer121を使用)。**`er118_*`を一切importしない**(R3-3、test TEST-11)。Trialの関数は逐語コピー+shaで固定。
- 呼出点: `er063_family_z_audio_01._run_tts_stage_impl`(`:1383`)の clip ループの前で `dialogue_ctx.prepare(run_dir, level, plan, story_key, llm_fn=None)` を1回呼ぶ(runner `stage_tts`経由でも、他の`run_tts_stage`呼出でも同じ経路を通すため)。dry_runでは呼ばない(API 0・書込0を維持)。
- `prepare` の戻り=dialogue各ClipSpecの `spec.extra["dialogue_ctx"]`(style文字列・context sha・note状態を持つ不変record)と、policy識別子。policy=`legacy`なら何も付けず現行動作。

### A-2. 入力(Trialと同一の決定論抽出)
- 入力=story clip列(ClipSpecのうち `full_story_part{n}_c{k}`/narrator・dialogue、順序そのまま。`speaker`・`text`・`kind`)。Trialの `segment_plan_{level}.json` の `clips` と同一情報(runner `load_level_inputs` の `story_clips = plan["clips"]`、`er026:2265〜2320`)。
- `extract_context`・`allowed_source_text`・`PREV_DIALOGUE_MAX=2`・`NEXT_DIALOGUE_MAX=1`・`NEIGHBOR_MAX_CLIP_DISTANCE=4`・`TIMESKIP_NARRATION_WORDS=40`・`NARRATION_SENTENCES=2`・`STAGE_LEXICON`(Trial `er118_fz_dialogue_context_tts_trial_01.py:99〜106,182〜236`)を逐語移植。testで Trial 4単位の53 clip全てについて `extract_context` の出力dictが Trial module の出力と**完全一致**(TEST-01)。
- 話者表示名(`speaker_display`)・許可語(`allowed_names`)・EMOTION_DEVELOPERの作品名は**story別data**として新moduleに持つ:
  - `the_monkeys_paw`/`melos`: Trial全編のWORK_CFG(`er118_fz_full_episode_trial_01.py:49〜61`)を逐語(猿の手の許可語に `whites` を含む。Trialで初回に12件が誤DISCARDされ許可名追加で解消した事実を反映)。
  - `the_open_window`/`the_gift_of_the_magi`: Round 2/Round 1のdata(`er118_fz_dialogue_context_tts_trial_01.py:1364〜1383` WORKS)。
  - `after_twenty_years`/`the_tell_tale_heart`/将来の新作: Trial未検証。**決定論fallback**=speaker key(`er062 STORY_VOICE_ROSTER`の `speaker`)のTitle化を表示名、表示名のtokenを許可語。該当clipのevidenceに `speaker_display_source: "fallback"` を記録。許可語不足の失敗モードは『誤DISCARD=中立化』(安全側。品質を上げる/下げる判断を含まない)。→ Opus確認事項。

### A-3. Prompt・model(sha固定)
- `EMOTION_DEVELOPER`(rule 1〜10)・`EMOTION_SCHEMA`・`INTENSITY_STEMS`・`emotion_user_message` を逐語。作品名置換のみ(`The Gift of the Magi`→story別title、Trial `configure_case` と同一)。`emotion_prompt_sha()`(Trial `:280`)と同値になることをtest(TEST-01)。
- model=`gpt-6-luna`、`reasoning effort=low`、structured output(Trial `run_llm_case` `er118_fz_full_episode_trial_01.py:338〜377` と同一call形)。本番ラインのモデル選定は別判断(25節)のため据置。原価最適化(より安価なモデル)は別Trial(R5-3の範囲外)。
- 1 level = 1 call(全dialogue clip一括)。

### A-4. 出力の保存先・再利用(原価最適化。R5-3)
- 保存先: `<run>/<level>/audit/dialogue_ctx_notes_<level>.json`。内容=`schema, policy, model_requested/returned, emotion_prompt_sha, user_message_sha, per_clip{clip_id: {context_sha256, validated(status/state/scene/reaction/evidence/discard_reasons), ctx_style_sha256}}, cost_jpy, created_at`。
- **run内immutable**: 存在しsha(prompt/user_message/model)が一致すれば再call 0(resume・`--only-clips`・再run)。clipのcontext sha(前後の台本)が変わったclipだけは、LLMを再callせず**決定論のみの中立note**(A-5のDISCARDED相当)を使う(追加費用0、前後の台本が変わった事実をevidenceに記録)。
- 他run・他levelへは流用しない(Std/Advは本文が異なる)。`classify_reuse_path`は`audit/`配下を既に拒否(`er063:734〜`、`REUSE_DENY_DIR_SEGMENTS`)なので新runへ持ち込まれない。
- LLM call失敗(transport/schema): 1回だけ再試行。なお失敗なら**全clip中立note**で続行し、`ctx_notes_status: "LLM_UNAVAILABLE"` をrun summary・各clip evidenceに記録(非blocking、ctx方式自体は維持)。代替案=技術STOPして再開。→ Opus確認事項。

### A-5. 決定論チェックによる自動受理(Fable目視レビューの代替。新基準を作らない)
- 検査=Trialの `validate_emotion_items`(`:284〜340`)を**逐語**移植(逐語引用一致・語数上限・新規固有名詞・強度語deny・rule 10)。結果の3値をそのまま消費する:
  - `ACCEPTED` → CONTEXTへ state/scene/reaction 行を出す。
  - `NO_EXPLICIT_CUE` → state行を出さず scene/reaction のみ。
  - `DISCARDED` → LLM由来の行を全て出さず、speaker・前後セリフ・前後の地の文・manner wordsだけのCONTEXT(=Trialの『discard=中立』と同一)。
- 根拠(`er118_output/**/emotion_review.json` の決定済み77件、API 0集計): ACCEPTED→accept 49 / NO_EXPLICIT_CUE→accept 27 / DISCARDED→discard 1。**Fableがvalidatorの判断を覆した件=0**。全編53件はaccept 53・discard 0。よってFable目視を外してもTrialで実際に使われた入力と一致する。
- 閉じられない残余: validatorをすり抜けるLLM創作(引用は原文に逐語一致するが解釈が不適切)の可能性。0/76(rule of three 95%上限≈3.9%)。緩和策=notesファイルを監査可能な形で保存するのみ(新しい警告種別・blocking条件は追加しない)。**この残余を許容するかはOpus/Fableが11-3で判断**(許容できない場合の代替=『ACCEPTEDのうちrule 10の根拠が地の文/他者発話由来のものだけ採用し、他はDISCARD扱い』だが、これは新基準の追加なのでユーザー判断になる→J候補としては記録のみ)。
- leakage検査(`leakage_check`/`leakage_all_attempts`、Trial `:513〜555`)は**観測のみ**で移植し、再生成/NGの理由にしない(Trial全編53件でflagged 0。ASRの表記違いだけで再生成しない=R3-11を満たすため。内容の過剰読み上げは既存のASR内容一致・長さ判定(`max_len=len(text)+15`、`er012_b:515,565`)が従来どおり検出する)。

## B. TTS指示合成

- CONTEXT block: `CONTEXT_HEAD`/`CONTEXT_TAIL`/`build_context_block`/`_unq`/`is_dialogue_tag`/`_narration_without_tags` を逐語移植(Trial `:342〜396`)。
- ctx Style = `ENGLISH_STYLE_PREFIX.rstrip() + "\n\n" + build_context_block(ctx, note)`(Trial `style_for_arm("ctx")` `:399〜406`)。base styleは`p9a.ENGLISH_STYLE_PREFIX`(sha `add26d27…`、Trial `EXPECTED_BASE_STYLE_SHA`)を実行時に参照し、shaを起動時に検査(不一致=STOP)。
- 合成順序: STYLE区画=base+空行+CONTEXT、TEXT区画=当該セリフのみ(`er003_b1_p4c_audio.build_tts_prompt`、Trialと同一)。
- **従来方式への完全復帰の保証(R3-7/R3-9)**:
  1. attempt 3 のstyle引数は `None`。`generate_voice_body_wide_margin` は `style_prefix_override or p9a.ENGLISH_STYLE_PREFIX`(`:520`)なので、**現行Z dialogueと同一のprompt**になる。ctx関連の文字列・設定はこの経路に一切渡らない(styleを返す関数はattempt番号≥3で `None` を返し、ctx styleを保持しない)。
  2. test: (a) `policy.before_attempt(3).style_prefix_override is None`、(b) hook有でattempt 3に送られたprompt全体が、HEAD時点の`generate_voice_body_wide_margin`(`git show HEAD:er012_b_family_voices_production_01.py` をtemp moduleとして読込)でstyle無指定の呼出が送るpromptと**バイト一致**、(c) Voice・model・max_len・ASR呼出順が同一。
  3. attempt内の `minimal_fallback`(技術失敗時、`:537〜546`)は既存の安全機構として維持。ctx attemptで発火した場合その生成はMINIMAL_INSTRUCTIONでありctxを含まないため、evidenceに `effective_mode: "minimal_fallback"` を記録して開示(採否は既存ASR判定どおり)。

## C. retry/fallback状態機械(中核)

### C-1. 状態遷移(clip単位、n=TTS試行番号、最大3)
```
START → n=1 [ctx style] ─PASS→ DONE_OK(採用: mode=ctx)
                          └NG→ n=2 [ctx style, 待機なし] ─PASS→ DONE_OK(mode=ctx)
                                                           └NG→ COOLDOWN(600秒固定)→ n=3 [style=None(従来)] ─PASS→ DONE_OK(mode=legacy_fallback)
                                                                                                          └NG→ TERMINAL_NG
TERMINAL_NG → (現行どおり) STOPPED → record_outcome → HUMAN_REVIEW_REQUIRED(Lock+HR queue) → Gate BLOCK / STOP
              [J-1: Local Rewriteは本案件で新設しない]
```
- 『NG』の定義=現行の採否chain全体の不採用(Std: Primary/Secondary統一judge→disfluency→repetition QA。Adv: これに加え減速後の統一judge再検証)。ctx固有のNG条件は追加しない。
- 総TTS試行(ループ反復)の上限は3で、fallbackは3回目そのもの(4回目ではない)。HR Lockの累積guard(15回、`er011:68`)は不変。

### C-2. 実装方式の候補と推奨(Opus論点)
| 案 | 内容 | 長所 | 短所 |
|---|---|---|---|
| **A(推奨)** | `generate_voice_body_wide_margin` に既定`None`の引数 `attempt_hook` を追加。ループ先頭で `hook.before_attempt(attempt, max_attempts, out_path)` が `{stop, style_prefix_override}` を返す。attempt後(OK/NG/技術失敗`continue`の各出口)に `hook.after_attempt(...)`。関数冒頭で `hook.carried_log()` を `attempts_log` に先頭追加 | ASR/QA/lock/ループは**単一コピー**(AUW等の今後の進化が自動で反映)。`classification_history`・`attempt_ctx`・attempt音声保存がそのまま保たれる。B/Cの既定呼出はバイト同一 | 共有関数(Family B/C Voicesも呼ぶ)に約10行を追加=『B/C凍結(27-7)』との関係。`style_prefix_override`(2026-09、既定None追加)と同種の前例 |
| B | Z専用に同ループを複製した新関数 | 共有関数に触れない | ASR判定/AUWの今後の変更が複製に反映されない(承認済み判定規則との乖離リスク)。複製の同値test維持コスト |
| C | 共有関数を`max_attempts=1`で3回呼ぶ(外側でpolicy) | 共有関数は不変(slot引数のみ追加) | `classification_history`が毎回リセット、`attempt_ctx`のslot/is_last_slotを引数で補正する必要(KP前例の`slot_offset`/`total_slots`が要る)、per-attempt guardだと1回目NGでLockが立つ(reentrancyは外側guarded内なら回避可能だが複雑) |
- 推奨=A。Opusに『案Aの共有関数への追加がB/C既定呼出に影響しないこと』『案Bとの優劣』の独立判断を求める(OPUS_REVIEW_REQUEST_01 論点2)。

### C-3. hookのインタフェース(案A)
```
class DialogueAttemptPolicy:            # clip単位。dialogue()内で1個作り、Adv外側ループの各passで共有
    def __init__(self, run_dir, level_dir, spec, ctx_style, ctx_record, policy_id, sleep_fn=sliced_sleep, clock=time.time)
    def carried_log(self) -> list       # 前プロセスで完了済みのattempt log行(プロセス内の前passは含めない=二重計上防止)
    def before_attempt(self, attempt, max_attempts, out_path) -> dict
        # n = state.n_started + 1
        # n > 3 または state.status != IN_PROGRESS → {"stop": True, "reason": "ATTEMPT_BUDGET_EXHAUSTED"}
        # STOP sentinel確認(毎attempt)
        # n == 3 → cooldown(必要時)後に style=None
        # n in (1,2) → style = ctx_style
        # state に n_started=n, attempts[n]={mode, started_at} を原子的に書く(TTS呼出より前)
    def after_attempt(self, attempt, log_entry, verified, instruction_type) -> None
        # log_entryへ additive: tts_mode(ctx|legacy_fallback), overall_attempt_n, style_prefix(review_lock.style_prefix_record)
        # state に finished/verified を書く。n==2 かつ NG なら cooldown.required_before_n=3 を書く
    def finish(self, result) -> None    # DONE_OK / TERMINAL_NG を state に確定(Adv外側ループ終了後にdialogue()から呼ぶ)
```
- 注意: ループ内の `attempt` はcall内の番号、`n` はclip通算(外側ループの各passと再開をまたぐ)。slot(`attempt_ctx`)はcall内番号のまま=現行の意味を変えない(案Aは`build_attempt_ctx(attempt, max_attempts, …)`を触らない)。
- Adv外側ループ: `generate_with_a2_slowdown_outer_loop(…, lambda max_attempts: generate_voice_body_wide_margin(…, max_attempts=max_attempts, attempt_hook=policy))`。減速後NGで外側ループが再度gen_fnを呼ぶと、policyは`n`を継続(前passの生成を1回消費済みとして数える)。前passが『ASR OKだが減速後NG』の場合、`dialogue()`のlambda冒頭で2回目以降の呼出を検知して `policy.mark_prev_postprocess_ng()` を呼び、そのattemptのverdictをNGに更新する(これにより cooldown 判定が正しく働く)。

### C-4. state永続化とresume(R3-5/R3-6)
- 保存先: `<run>/<level>/audit/dialogue_ctx_attempt_state.json`(clip_id→state、原子書込 tmp+`os.replace`。`save_checkpoint`と同形式)。
- state: `{schema, clip_id, segment_id, canonical_text_sha256, policy, ctx_style_sha256, status(IN_PROGRESS|DONE_OK|TERMINAL_NG), n_started, attempts[{n, mode, started_at, finished_at, verified, status, instruction_type}], cooldown{required_before_n, started_epoch, started_at, seconds, ended_epoch}, updated_at}`。
- 書込タイミング: (1)attempt開始**前**(TTS呼出より前に`n_started`を増やす。TTS中に中断しても『消費済み』扱い=3回超過は構造的に起きない)、(2)attempt終了後、(3)cooldown開始前(`started_epoch`)とsleep終了後、(4)finish。
- resume規則(`dialogue()`内でpolicy生成時):
  - state無し → 新規開始(n=1)。
  - state有・同一(canonical sha, policy, ctx_style_sha)・IN_PROGRESS → **続行**: `n=n_started+1`から。1〜2回目のctx生成は再実行しない。`carried_log()`は前プロセスで完了したattempt行を返し、`record_outcome`/外側ループの生成数会計が実際の消費と一致する。
  - state有・DONE_OK/TERMINAL_NG、または不一致 → この時点でgenerate_fnが呼ばれているということは明示再生成(`--only-clips`/`approve_regenerate`/本文変更)なので**新規開始**(旧stateは`audit/`に`.prev`として残す)。TERMINAL_NGのままLockが立っていれば`check_before_generation`が先に0 APIでblockする(既存)。
  - cooldown中断: `cooldown.started_epoch`が有り`ended_epoch`無し → 残り`600−(now−started)`だけ待つ(≤0なら待たない)。**待機時間は実時間の経過で数える**(10分未満には短縮しない。『NG後10分以上空ける』を満たす)。
- 残余リスク(開示): attempt N が『ASR OK・採用確定』した直後〜`save_checkpoint`前にプロセスが落ちた場合、そのclipはn=N+1から再生成される(最大でも総3回は超えない)。窓は1 clip内の数秒。

### C-5. クールダウン(R2-2)
- 条件: `n==3`の直前でのみ(2回目NG後)。待機=`er020_tts_retry_local_rewrite_01.maybe_cooldown_before_attempt(attempt=3, max_attempts=3, True, sleep_fn=…, cooldown_seconds=COOLDOWN_SECONDS)`を再利用(時間定数は既存の600.0、短縮不可)。
- `sleep_fn`は5秒刻みで `_check_stop_sentinel(run_dir, "tts_cooldown:<clip>")` を確認する分割sleep。STOP検知時は例外で即中断(stateは`started_epoch`保存済みのため後でresume可能)。**既存narrator cooldown(`time.sleep(600)`単一)は変更しない**。
- イベント: `append_attempt_history_event(out_path, "CTX_COOLDOWN_BEFORE_FALLBACK", {...})`(前例=`COOLDOWN_BEFORE_OVERALL_ATTEMPT`、`er003_v1_repro01_main_generate.py:342`)。
- 待ち時間の最適化案(Delivery。原則2): 既定は**clip内ブロック待機**(単純・narrator前例と同じ)。fallbackが必要なclipは期待0.4〜0.6件/set(約4〜6分。Trialでctx 2回以上NG=1/53 clip、猿の手32・メロス21 dialogue clip/set換算。BUDGET_PLAN §2)だが、Wilson 95%上限(9.9%/clip)では2.1〜3.2件/set(約21〜32分)になり得る。代替=『deferral』(NGのclipを保留しrun内の他clipを先に進め、600秒後に戻る)。clip順序が入替わるが各clipのattempt列は不変。複雑度が上がるためPhase 1では実装せず、Phase 2で実fallback率を測ってからFable判断(BUDGET_PLAN §4)。

### C-6. HR Lock・STOP・Local Rewrite・regenerationとの整合
- HR Lock: policyは`generate_voice_body_wide_margin`の**1回のguarded呼出の内側**で動く(hookはループ内)。per-attempt guard呼出にしないので、1回目NGでLockが立ち2回目が0 APIになる事故は起きない。最終NGは従来どおり`STOPPED`→`record_outcome`→HUMAN_REVIEW_REQUIRED(Adv減速後NGは`finalize_a2_slowdown_final_ng`)。
- STOP sentinel: 各attempt前(`before_attempt`)と、cooldownの5秒刻みで確認。`run_tts_stage`/runnerの各clip前確認は不変。
- Local Rewrite: Z dialogueには未配線(EXISTING_SPEC_CHECK §2)。**新設しない**(J-1)。将来配線される場合は、LR再TTSが従来style(`style_prefix_override=None`、`max_attempts=1`)で走ること、既存`lr_used==0`・累積15回guardを維持することが要件(本設計はその拡張を妨げない: policyのn上限3の外側にLRの1回が付く現行LR構造と同じ)。
- regeneration: 『明示再生成=新規開始』(上記C-4)。外側ループの取り直し=同一policy内のn継続。

### C-7. a2減速外側ループとの関係(e)
- 外側ループは `gen_fn(remaining)` を最大3pass呼び、`remaining = 3 − 通算生成数`。policyのnは外側ループの会計とは独立に**clip通算で単調増加**し、上限3を強制する(外側ループの会計がずれても3を超えない)。resume直後は`carried_log()`で外側ループの生成数会計を実消費に合わせる(ただし同一プロセス内の前passは含めない)。
- Advでn=1のctxが『ASR OK→減速後NG』なら、nは1消費(NG扱い)。n=2も同様。n=3(従来style)は減速前OK→減速後NGでも最終NG(現行の通算3回目の減速後NGと同一: Lock+HR queue 1行)。

### C-8. 経路別保証表(R3-4)
| 経路 | どう保証するか | test/evidence |
|---|---|---|
| 初回Production生成 | `_run_tts_stage_impl`→`prepare`→`dialogue()`が新policyを生成。runnerの`stage_tts`も同経路 | TEST-01, E-1 |
| retry(1→2回目) | policy n=2。待機なし・ctx | TEST-02 |
| fallback(3回目) | n=3でcooldown→style None | TEST-03, TEST-05, E-2 |
| regeneration | state status(DONE/TERMINAL/不一致)→新規開始。`approve_regenerate`/`--only-clips`/本文変更 | TEST-07b |
| resume | state続行(n=n_started+1)、cooldown残り時間のみ待機 | TEST-07, E-3 |
| 中断後の再開(kill) | 同上+started-but-unfinished=消費済み | TEST-07, TEST-09, E-3 |
| Local Rewrite | 既定=未配線(J-1)。3回NG→STOPPED→HR | TEST-04, E-4 |
| Human Review Lock | 1回のguarded呼出内、per-attempt guardなし。Lock済みは0 API | TEST-04, TEST-10 |
| STOP | 各attempt前+cooldown 5秒刻み | TEST-08 |
| X/Y/B/C/narrator/KP | hook=None→バイト同一 | TEST-12 |

## D. X/Y不変の保証(R1-4/R6-6)

1. 入口がZ dialogue closure(`er063.real_generators().dialogue`)のみ。Xは`er019`系、Yは`er121`系で`er063.real_generators`を使わない。
2. 共有関数 `generate_voice_body_wide_margin`(Family B/Cも呼ぶ)は `attempt_hook=None` 既定。**hook=Noneの経路は現行とコード上も出力上もバイト同一**であることを、`git show HEAD:er012_b_family_voices_production_01.py` を読んだ旧関数と新関数を、同一のfake TTS/ASR backendで呼び、送信prompt列・attempts_log・戻り値dictが完全一致するtestで固定(TEST-12)。
3. `dialogue()` 以外の generator(narrator/topic_intro/preview/comment/japanese_title/kp_*)は無編集。`style_text_for`・`build_reuse_key`(dialogue以外)・FAMILY_Z_ROLE_STYLEは不変。
4. policy=`legacy`(既存run・ロールバック)ではdialogue()も現行と同一。ロールバック手段=module定数 `Z_DIALOGUE_CTX_POLICY_DEFAULT = "fz_ctx_v1"` を `"legacy"` に戻す1行(前例: `A3_SECONDARY_LENGTH_REEVAL`。env/flagではない)。起動script・`.env`でのON/OFFはしない。
5. run単位のpolicy固定: 新規runの`audit/style_record.json`へ追加キー `dialogue_tts_policy`を記録。**キー無しの既存record=legacy扱い**で継続する(公開済みrunを再開/`--only-clips`しても方式が混在しない)。`inspect_run_style_record`のroles比較は不変(追加キーは比較対象外)。

## E. Trial観測問題6項目 × Production上の扱い(R4)

照合先=既存の承認済みValidator・組立・品質条件(`er063:1640 verify_z_speed_profile`、`:1703 check_clip_audio_quality`、`er003_audio_tts_asr_safety.detect_duration_anomaly`、`er012_b:515,565`のmax_len/length_ok、`er003_v1_n3_01_assemble.py:982〜1012`ヘッドルーム安全弁[閾値0.98]・clip別gain、CURRENT_SPEC Assembly安全弁行`L2123`)。

| # | Trial観測(出典: EVAL_01 §3,§5、TRIAL_RESULT_01) | Productionの既存Validator/条件との関係 | 反する? | 扱い |
|---|---|---|---|---|
| 1 | 不自然な話速(猿Adv part2_c11 話速0.56×・70wpm) | 既存の長さ系=`detect_duration_anomaly`は**上限のみ**(hallucination検知)、`max_len`も上限。`verify_z_speed_profile`はAdvのatempo後/原音の長さ比(0.93〜0.96)を見る=生成速度は見ない。Trial自身のC6 Gateも全PASS | **反しない**(遅すぎる音声を弾く承認済み条件が存在しない) | 新gateは作らない。J-4(開示、ユーザーが欲する場合のみ新基準=別判断) |
| 2 | 新規長ポーズ(猿Std part2_c8 0.83s、メロスStd part3_c4 0.73s) | 発話区間trim(`p3u.trim_english_keyword_silence`)は先頭/末尾のみ。clip内部の無音は未検査。組立は固定無音(dialogue後0.2s/narrator後0.5s) | 反しない | 同上(J-4) |
| 3 | 地の文とセリフの音量差(境界RMS>3 dB 20/98、最大+9.64 dB) | 組立はclip別gainで目標RMSへ揃える(`apply_*_gain`)。境界段差(窓RMS)を見る承認済みgateは無い。TrialはProductionと同一組立でtarget_rms・gain一致を確認済み(M-5) | 反しない | 同上(J-4)。Phase 2で境界段差を観測値として報告(判定には使わない) |
| 4 | 一部の声の高さの不安定(F0 SD上昇) | F0を見る承認済み条件なし | 反しない | 同上(J-4) |
| 5 | 『走れメロス』Standardの比較音量条件不一致 | 原因=ctx takeのpeakが高くヘッドルーム安全弁(閾値0.98、全編一律scalar)がTrialでのみ作動。**Productionでは承認済みの通常動作**(scalar≦1.0、観測最大−0.158 dB)。比較用のTrial構成(Production原clipとの一致)に固有の問題 | 反しない(Trial比較条件の問題。Production欠陥ではない) | Productionでは何もしない。Phase 2でheadroom.scalar/gain_reportを記録。`check_clip_audio_quality`(peak_max=0.999、`clipping_detected`)は既存条件のまま=ctx clipがそれを超えれば既存条件でGate停止(新基準ではない)。Trial最大peak 0.998は閾値内 |
| 6 | 53件中1件のASR/QA不合格(メロスStd part3_c10、ctx 3 call全NG) | 新仕様ではこの形が『ctx→ctx→cooldown→従来方式』に遷移し、従来方式の3回目で救済される想定(同clipはProduction従来方式で合格済み)。3回目もNGなら既存のSTOPPED→HR Lock | 反しない(仕様どおりの再現ケース) | 自然発生は約2%/clip(1/53)。E-2/E-4で強制NGにより遷移を検証 |

結論: 6項目のうち『既存の承認済み条件に反する』は0件。したがって『承認範囲内の是正』対象は無く、1〜4は観測値の開示、5は承認済み安全弁の通常動作、6は仕様遷移で扱う。新基準が必要かはユーザー判断(J-4、非ブロッキング)。

## F. 品質基準の扱い(R3-2/R4-3)—新基準を作らない宣言

追加しないもの: leakageのblocking化、話速/ポーズ/音量差/F0のgate、感情情報のreview gate/警告種別、ctx固有のASR閾値、試行回数・cooldown時間の変更。変更しないもの: Prompt文言、rule 1〜10、検査規則、model、ASR Primary/Secondary判定、repetition/disfluency QA、組立・音量・速度。

## G. Dangling Reference防止(R7-3)

| 維持する旧方式の参照点 | 場所 | 新方式からの参照 |
|---|---|---|
| `p9a.ENGLISH_STYLE_PREFIX` | `er003_b1_p9a_audio.py` | ctx styleのbase、fallbackのstyle |
| `style_text_for(spec)`(dialogue=None) | `er063:790` | reuse_key・style_recordのdialogue項は不変。方式識別は`extra["dialogue_ctx"]`/policy |
| `build_reuse_key` | `er063:798` | dialogueにだけpolicyキー追加(policy=legacyでは追加しない=旧key不変) |
| `_effective_style_sha` | `er063:1161` | 変更なし(legacy attemptの実効styleshaを記録)。ctx attemptは attempts_log の `style_prefix` に記録 |
| `extract_attempt_evidence`/`_evidence_row` | `er063:1036,1502` | 新キー(`dialogue_tts`)をadditiveで追加。旧readerは新キーなしで動く(TEST-15) |
| `generate_voice_body_minimal_fallback` | `er012_b:450` | 維持 |
| `verify_z_speed_profile`/`check_clip_audio_quality`/Gate | `er063:1640,1703,1727` | 変更なし。ctx entryも同じ検査を通る |
| Trial module `er118_*` | 別 | **Productionからの参照0**(TEST-11)。Trial module自体は無編集のまま保存 |
旧記述の撤去要否: 撤去する規則・検査・testは**0**(『撤去・残置した規則』の残存Grep=Phase 1で実施: `grep -n "style_prefix_override" er063_family_z_audio_01.py` 等)。

## H. 段階計画

### Phase 1(実装+offline test、API 0。Opus条件Aレビュー後)
並列可能: (a)新module逐語移植+golden test (b)案Aのhook追加+B/C parity test (c)policy/state/cooldown (d)er063配線(dialogue()・prepare・reuse_key・style_record policy・entry追加キー) (e)runner/evidence summary (f)Phase 2 evidence driver(強制NG注入・kill/resume harness・送信prompt捕捉)。依存: (d)は(a)(b)(c)後。見込み: 実装+test 2〜3時間(並列で短縮)。
遮断harness下の`py`でtest。`.venv`/有料APIは起動しない。

### Phase 2(runtime evidence、実費あり。見積=BUDGET_PLAN_01)
| ID | 経路 | 方法 | 注入 |
|---|---|---|---|
| E-1 | 正常経路(Std+Adv同時、猿の手) | 新run dirへテキスト資産を`copy_reusable_run_assets`で取込み、`--stages tts_b1b,tts_a2,provision_shell,gate,assemble`を**1起動**。Z scope・Secondary scope・正式runner経由 | なし(自然発火)。公開page出力先を上書きしないことをPhase 1で確認(上書きの恐れがあれば`pages`を含めない) |
| E-2 | fallback経路(Std 1 clip、Adv 1 clip) | 別の小規模evidence run dir(1 dialogue clipのみ、`--only-clips`)で、同一clipのattempt 1・2を強制NG。実cooldown 600秒を待つ | 後述の強制NG |
| E-3 | resume | E-2と同形で、cooldown中に**自起動PID**のみterminate→同一args再起動。attempt 1・2が再実行されない(TTS call総数=3)ことを`raw_usage_log.jsonl`とstateで確認 | 同上 |
| E-4 | 3回NG | 1 clip(Std、可能ならAdv)でattempt 1〜3を強制NG→STOPPED→HR Lock→Gate BLOCK | 同上(3回目も) |
E-2〜E-4はStd/Advそれぞれ。並列(別run dir・別process)にできるので全体の壁時間は最長のcooldown+αで約12〜15分。RESTART_STORM(5分に3起動)を避けるためE-3の起動は1 run dirあたり2回に抑える。各起動前に`stop_scope_check_01.py --managed-id`(rc=3なら中止)。

**強制NG注入の設計(Gate迂回でないことの説明)**
- 注入口をProduction codeに**作らない**(env/flag/設定dictなし)。evidence driver(`er122_fzcw_runtime_evidence_01.py`、Productionから参照されない独立script)が、同一プロセス内で `er011_open121_repetition_qa_production_01.apply_repetition_qa_gate` を包み、指定した(clip, 試行順序)のときだけ戻り値の `verified` を False にして `repetition_qa_evidence.forced_ng_by_driver=true` を付ける。
- 実TTS呼出・実ASR(Primary/Secondary統一judge)・disfluency gateは**全て実際に実行された後**に、同attemptの最後のchainでNG方向にのみ上書きする(NG→OK方向の上書きは実装しない)=Gateを迂回せず、Gateの出力をより厳しくする方向だけ。強制NGが無いattempt(3回目の従来方式)は完全な本物の判定でPASS/NGが決まる。
- forced run dirは公開page・公開dirへ出さない。証拠JSONに `path: normal|forced_ng_fallback|forced_ng_resume|forced_ng_exhaust` と `forced_ng_injection: true/false` を必須記録(R6-9)。E-1(正常経路)は注入0を明記。

### 実音声・QAの証拠(R7-4)
Std/Advそれぞれ: ctx発火(送信promptに`CONTEXT FOR THIS ONE LINE`有)・fallback(attempt 3の送信promptにCONTEXT無し、promptのshaが従来promptと一致)・state/attempts_log・ASR判定(asr_judgement)・assembly(headroom/gain_report)・最終mp3・費用(provider別)を表で報告。

## I. Opus既存指摘(OF-FZFE)の引継ぎ

| ID | Trial時の指摘 | Production設計での扱い |
|---|---|---|
| M-1 NG音声混入遮断 | NG/途中音声が組立入力へ残る | 現行Productionの仕組みを維持: 生成関数がout_pathへ書いてからASR判定し、最終STOPPED時は`status!=OK`のentryがGateでBLOCK(`assert_tts_results_complete`)。再利用は`status OK+sha一致`のみ。ctx→従来の切替でも最終採用wavのshaとentry.sha256が一致しないものは再利用されない(`generate_or_reuse_z`)。NG音声を採用する経路は存在しない |
| M-2 `_original.wav` | Std会話に残るProduction原音`_original`が検査/解析を汚す | Production新runでは旧`_original`が存在しない(新run dir・policy固定)。Stdは`_original`を作らず、Advは生成で作られた`_original`のみ(現行同一)。stateのclip再開時の前attempt wavは`attempts/`に保存済みで採用wavとは別(現行`save_tts_attempt_audio`) |
| M-4 書込ガード | realpath/hardlink/pages_dir誤上書き | Productionは正規sink。新規書込はrun dirの`<level>/audit/`のみ(notes/state)。forced evidence runはdriverが専用run dirとpages未出力で隔離 |
| M-5 組立3点assert/headroom | Trial vs Productionの比較条件 | Trial比較用の構成。Productionは通常assembly。Phase 2でtarget_rms・label別gain・headroom.scalarを記録(安全弁作動は承認済み通常動作として報告) |
| M-6 グローバル依存排除 | `use_case`のglobal差替えで未切替の関数がRound 1設定のまま動く | Productionは引数明示の純関数(`prepare`/`policy`)。global差替えなし(TEST-11でGrep) |
| M-8 NG clip方針 | NG clipの扱いを事前固定 | Productionは3回NG→STOPPED→HR Lock→Gate BLOCK。Production原音置換はTrial専用で持ち込まない |
M-3/M-7/R系はTrial比較設計固有のため引継ぎ対象外(M-7のC2=Production ASRカスケード最終判定PASS系=Productionでは通常の採否そのもの)。

## J. CURRENT_SPEC追記案(Phase 1/2完了時に別委任で反映。ここでは文案のみ)

『Family Z dialogue文脈・感情付きTTS(OPEN-528、APPROVED_FOR_PRODUCTION 2026-10-26、Z専用・Std/Adv)』: セリフclipは新規runで文脈・感情付きTTSを標準とし、TTS総試行は初回含め最大3回(1・2回目=文脈・感情付き、2回目NG後に600秒固定のクールダウン、3回目=従来style[文脈・感情情報を完全除外])。3回NGは現行どおりSTOPPED→HR Lock。感情情報はTrialと同一Prompt/rule/model(gpt-6-luna)でlevel単位1 call・run内不変保存し、決定論検査(逐語引用一致・語数・新規固有名詞・強度語)で自動受理(Fable目視なし)。leakageは観測のみ。attempt状態は`<level>/audit/dialogue_ctx_attempt_state.json`に永続化し、再開で消費済み試行を再実行しない。run単位のpolicyは`audit/style_record.json`の`dialogue_tts_policy`で固定(キー無し=legacy)。X/Y/B/C/narrator/KPは不変。Z dialogueにLocal Rewriteは未配線(別判断)。Status=PRODUCTION_WIRED(Phase 2完了+Fable独立照合後に限る)。
