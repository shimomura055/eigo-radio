# WIRING_DESIGN_01 — ZセリフLR正式導入(最大TTS6回+LR1回)の配線設計(委任_01、コード実装なし・API 0)

管理ID: FZ-DIALOGUE-LR-ADOPTION-01 / 2026-10-29 / 原文=`docs/pm/delegation_log/2026-10-29_FZ-DIALOGUE-LR-ADOPTION-01_USER.md` / 現状=`CURRENT_STATE_01.md` / test=`TEST_PLAN_01.md`
状態: **設計案(Opus条件Aレビュー待ち)**。本書の内容はレビュー後に確定する。Production変更なし。

## 0. 設計の骨格(Fableの枠に沿う)
共通LR機構(`er127.lr_recover`→`er020.run_local_rewrite_recovery`)を再利用し、Z専用の重複実装を最小にする。Zセリフ固有の部分は「試行状態機械(er122)を6回+LR段に拡張」と「`lr_recover`の呼出契約を満たすadapter」「c6で露見した2点(LR入力転写の選び方・確定内容保護)」だけ。
- `Z_DLG_CTX` Profile を `lr=True / total_slots=6 / max_tts=6 / max_waits=2` に(D1)。`_self_check`(`er127:872-878`)の関係式は無改変で成立。
- 新しい処理flowはフラグでなく**承認済み仕様の既定動作**(原文§7「Trial限定ではなく正式Production」)。ただしZセリフ(scope内 X/Y/Z・policy=fz_ctx_v1)にのみ効き、`policy=legacy`・narrator・KP・JA・X/Y・A/B/Cは通らない。

### 0-1. 正式フロー(slotと状態)
| n(通算) | ブロック | 表記 | Style | 直前の待機 | NG時 |
|---|---|---|---|---|---|
| 1 | 元ブロック | ① | 文脈・感情付き(ctx) | — | ② |
| 2 | 〃 | ② | 同ctx | — | 180秒待機→③ |
| 3 | 〃 | ③ | 従来Dialogue(`style_prefix_override=None`) | 180秒(②NG確定時刻起点・実時間) | LR |
| — | LR(最大1回) | LR | — | なし | 書換え後原稿でn=4へ。LR不可=HR |
| 4 | LR block | ①' | 同ctx(Style・Voice・速度・QA不変) | — | ⑤ |
| 5 | 〃 | ②' | 同ctx | — | 180秒→⑥ |
| 6 | 〃 | ③' | 従来Dialogue | 180秒(⑤NG確定時刻起点) | Human Review(終端) |
途中PASSで即終了(以降のTTS・待機・LRなし)。TTS最大6・LR最大1・待機最大2は構造的上限(D2の永続state+`LocalRewriteReentryError`)。

## 1. 原文条項→設計項目の対応
| 原文 | 設計項目 |
|---|---|
| §2 新フロー/最大6回・LR1回・待機2回 | D1,D2,D3 |
| §3 #1〜#3を再実行せずLR段階から再開/試行履歴・費用・音声・Gate結果を保持/Lock・上限・resumeを迂回しない/3試行を消費済みに | D8(状態移行ツール)、D2(counted/cumulative) |
| §3 LR品質条件(意味・証言・人物像・感情・矛盾を解消しない・最小書換え・確定KP等の保護・4者一致) | §5(既存Gate/Promptで担保される項目とZ追加分) |
| §4 8区分の一覧/独立行削除/従来Styleは維持 | D10 |
| §5-1〜10 | 各D(§1下表に対応) |
| §6 最終報告(Before/After/赤/理由/区間/LR後音声か/Fallback濃青) | D11(既存er129/er131/er133の適用先確認) |
| §7 検証項目 | TEST_PLAN_01 |
| §8 費用/単価 | §8 |
| §9 完成候補再提出 | 実装後stage手順(§8) |

§5の10項目: 1=D1 / 2=D2 / 3=D8 / 4=D3,D2(mode規則) / 5=D2(mode規則)・D7 / 6=D2,D3,D8 / 7=D9 / 8=D7(er130/er129) / 9=D11 / 10=D10。

## 2. 設計項目

### D1. Profile変更(`er127_tts_block_policy_01.py:114`)
`"Z_DLG_CTX": Profile("Z_DLG_CTX", 3, (3,), "LEGACY_DIALOGUE", True, 6, 6, 2)`。他のProfile・`LR_ROLES`・`block_policy_for`は不変(`Z_DLG_LEGACY`は残置=policy=legacy・ロールバック用、lr=False)。`er130._allowed_fallback_slots`(`:182-186`)はlr=Trueで自動的に{3,6}。`er127`のdocstring(「LRなし部位 Z会話」)を更新。

### D2. 試行状態機械の拡張(`er122_fz_ctx_policy_01.py`、v2 schema、v1後方互換)
**単一の決定者**はer122のまま(経路間でずれない)。変更点:
- 定数: `BLOCK_ATTEMPTS=3`、`MAX_TOTAL_ATTEMPTS=6`、`CTX_ATTEMPTS=2`(ブロック内)。mode規則=ブロック内ordinal `o=((n-1)%3)+1`: o∈{1,2}=`ctx`、o=3=`legacy_fallback`。待機は o==3 の直前(n=3,6)のみ(既存`_cooldown_before_fallback`を`n%3==0`へ一般化、起点=直前attemptの`final_ng_epoch`/`finished_epoch`)。
- state追加キー(v2): `phase`∈{B1,LR,B2}、`lr`:{`state`∈{NOT_STARTED,PENDING,TEXT_SAVED,RESOLVED,UNRESOLVED,NOT_APPLICABLE}, `text`, `text_sha`, `audit`(選定根拠), `input`{n,source,asr_text}, `migration`{…}}、`ng_transcripts`[{n,source∈{pre_slowdown,post_slowdown},asr_text}]。v1(キー無し)=`phase` 導出: n_started<3→B1。**v1のTERMINAL_NG(n=3)は自動ではLRへ進めない**(移行ツールD8のみが遷移させる=誤発火防止)。
- `remaining()`(`:240`)はブロック限定(B1: 3−n、LR: 0、B2: 6−n)→ leafの`max_attempts`にそのまま渡せる(Std単一呼出・Advループ双方が自然にブロック境界で止まる)。`before_attempt`(`:283`)は n>ブロック終端で `stop`(B1終端でLR未実施のn=4要求=fail-closed)。
- `finish()`(`:409`): 非OK時の`TERMINAL_NG`化は「LR段が使えない/終わった」ときだけ。B1終端NG+LR可=`phase=LR`・status据置(IN_PROGRESS)。B2終端NG・LR不可(NOT_APPLICABLE)・B1内で終了不能(技術STOPは別: status据置=再開可)。`TERMINAL_NG`は従来どおりn_started消費済みとして再実行しない。
- `_attach_final_adoption`(`:390`): n≥4で `depth=1, ordinal=n-3, slot=er127._slot_label(n-3,1)`(①'②'③')。`style_mode`/`sent_style_sha`の規則は不変(ctx採用=PRIMARY+ctx sha、従来=FALLBACK)。
- `final_reason`文言・docstring(`:21-22`)更新。記録は追記のみで既存キーの意味を変えない(`dialogue_tts.attempts[]`に`block`/`depth`を追加)。
- 二重計上防止(`counted`/`carried_log`)はLR境界をまたいでも維持(B1の3行はcounted済み→resume時のB2呼出では新規行のみ→`record_outcome`累積=3+新規)。

### D3. 生成driver(`er063_family_z_audio_01.py` 4-D節、`generate_dialogue_ctx`:918-)
- 外側guardの新設: 本体を `@review_lock.guarded_generate("en")` 付きの内部関数(`_dialogue_ctx_flow`)へ。理由=`lr_recover`が `out_path in _ACTIVE_GUARDED_OUT_PATHS`(`er127:770`)を要求し、かつ「1論理生成=1 record_outcome」(`er011:674`のreentrancy)を保つため。leaf(`er012_b:483`)は外側guard中は記録せずfn直行になる(既存機構)。**注意(Opus論点O3)**: 現行はleaf呼出ごとにrecord_outcomeされる(Advは減速後NG取り直しで複数回)。外側guardにすると通常パスのLock記録が「呼出ごと」→「clipごと1回」に変わる(累積TTS数は同値、状態遷移は最終結果のみ)。通常パスのgolden(lock store・attempt_history・entry)で同値を固定する。
- 流れ(疑似):
```
flow(text,...):
  Lockチェック(既存)→ style_for → policy=DialogueAttemptPolicy(...) → saved_result()採用(API 0)
  if policy.phase == B1:  r = run_block(text, depth=0, final_block=False)      # Std=単一leaf呼出 / Adv=外側ループ
        OK→finish / 技術STOP→据置で返す(LR・HRへ入れない) / 非OK→policy.enter_lr_phase(r)  # ng_transcripts保存
  if policy.phase in (LR,B2):
        stop_check("lr")→ lr_recover(adapter, text=原文, last_asr_text=policy.select_lr_input(...),
                                      block_call=lambda rewritten,ctx: run_block(rewritten, depth=1, final_block=True),
                                      merge=..., last_attempt=...)
        成功=OK結果(local_rewrite_recovery付き)/ 失敗=None→終端(register_terminal_hr済み)→STOPPED結果
  policy.finish(result)
```
- `run_block`: Std=`bvoices.generate_voice_body_wide_margin(text, ..., max_attempts=policy.remaining(), attempt_hook=policy)`、Adv=`generate_with_a2_slowdown_outer_loop`(D4)。LR block(depth1)は**書換え後の本文**を渡し、Style(ctx style_for(clip_id))・Voice・速度(Adv fast6)・QA(ASR/repetition/disfluency)・減速後再検証をそのまま使う(原文§2「同じTTSモデル・Voice・速度・文脈感情Style」)。Lock key/HRQ `lock_canonical_text`/`m1_anchor_text`は元原稿。
- 技術STOP判定は`er127._is_tech_stop`(Secondary/Whisper不能)を再利用。`stop_retrying`(同一ASR署名連続)はB1ではLR段へ(X/Y統一flowと同じ)、B2では終端。
- `terminal_before_fallback`(`:968`、`< MAX_TOTAL_ATTEMPTS`)はLR段経由の終端を例外化しない形に更新。

### D4. Adv外側ループ・leafの最小拡張(共有コード、既定=現行とバイト同一)
- `er003_v1_n3_01_tts_generate.generate_with_a2_slowdown_outer_loop`(:503): keyword-only 追加 `total_budget=None(=PRODUCTION_MAX_TTS_ATTEMPTS)`, `slot_offset=0`, `total_slots=None`, `final_block=True`。`is_last_slot=(slot_offset+generations_used>=total_slots …)`、`final_block=False`(B1)では`finalize_a2_slowdown_final_ng`も最終slotのHRQ書込(`log_human_review`)も行わない(LRが続くため。終端NG=1件=HRQ1行の維持)。既存呼出(Voices A2・Z legacy・Z ctx旧3回)は引数なし=現行と同一。
- `er012_b.generate_voice_body_wide_margin`(:483-): `attempt_hook`が任意メソッド `attempt_ctx_kwargs(attempt)` を持つとき `build_attempt_ctx(..., **hook.kwargs)` へ渡す(slot_offset/total_slots=6/script_version/m1_anchor_text)。**これが無いと B1の3回目が`is_last_slot=True`になり、LR前に判定器がHRQ行を書く**(`er078_asr_unified_attempt_ctx_01.py:19-33`: is_last_slot=slot>=total)。hook=None(B/C等)は無変更。LR block内は`script_version="v1"`(LR_REWRITTEN→PASS_WITH_WARNING扱い)。

### D5. `lr_recover`の呼出契約を満たすadapter(Z専用の薄い層、er122に同居)
`lr_recover`が使うblk属性は限定的: `depth`、`policy.profile.lr`、`_open_ordinal`/`done()`、`total_slots`、`progress.{resumed, lr_state(), save_lr_text(), save_lr_audit()}`、`lr_outcome`、`policy.profile`。これらを**er122 stateを唯一の永続先**として提供する`ZLrBlockAdapter`を作る(BlockProgress別ファイルを併用しない=状態の二重化・6時間失効(`er127:36`)による『LR LLM再実行』を避ける。resumedは`lr.text`の存否)。`lr_recover`本体・再入禁止・resume時LLM非再実行・非RESOLVED時の`register_terminal_hr`(終端NG=HRQ1行)は無改変で再利用。
代替案(O6): 実`er127.open_block("L8",…,z_dialogue_policy="fz_ctx_v1")`+BlockProgress。長所=無改造で統一、短所=attempt進行が二重管理(er122とBlockProgress)でc6の既存3試行をBlockProgressへも複製する必要。推奨=adapter。

### D6. LR入力の選び方と確定内容保護(c6で露見。Z向け追加、共通コアは加算のみ)
**問題**: (i) c6の#3は反復検査NGでASR転写が原稿と一致→最終転写では `NO_NG_SPAN`(CURRENT_STATE §4)。(ii) #2減速後の唯一のASR差分 `sank for ever`→`sink forever` は確定Vocab(`confirmed_selection.items[3]`)で、書換えると `LR_OVERLAPS_CONFIRMED_CONTENT`(`er129.check_confirmed_overlap`のT1/T2→`er130`の`LR_OVERLAPS_CONFIRMED_CONTENT`)で組立前Gateに止まる=LR後に3 TTSを使っても採用不能。
**案(推奨)**:
1. `policy.select_lr_input(canonical, protected)`: `ng_transcripts`(B1の全attempt転写+Advの減速後転写)を新しい順に走査し、`identify_ng_span(canonical, asr).found` かつ **NG spanを含む1文が確定項目(KP/Word/Vocab)の語句・出典文と重ならない**最初の転写を `last_asr_text` とする。全て不成立=`NOT_APPLICABLE`(既存の『LR不可は即HR』と同じ安全処理。TTS 0)。c6では#2(確定Vocabの文)が除外され#1が選ばれる見込み(offline実測)。※ X/Yの『最終attemptの転写のみ』規則は変えない(共通LRは不変)。Zセリフだけの入力選択規則。
2. 候補段の事前保護: `er020.run_local_rewrite_recovery`に加算専用のkeyword `candidate_filter=None`(None=現行バイト同一)を追加し、`build_full_candidate_records`直後に呼ぶ。Zは`er129`のT1/T2/T3純関数(`check_confirmed_overlap`を候補の(before,after)に適用する薄いwrapper `precheck_candidate_overlap`、台帳側と同一関数を使い不一致を作らない)で重なる候補を`adoptable=False`(理由コード付き、7 Gateのキーは不変)にする。選定は既存`select_final_candidate`が`adoptable`だけを見るので変更なし。全滅=`NO_CANDIDATE_PASSED_QA`→HR(再TTS前=TTS 0)。`lr_recover`にも透過kw `candidate_filter`(既定None)。
3. 文脈: `context_before/after_text`(`er020:757`の既存引数)に隣接clipの本文を渡す案(Gate 3/4の判断材料、他証言との矛盾防止)。**既存のProduction LRは文脈を渡していない**ため、これはPrompt入力の追加であり適用の是非をO2で確認(推奨: 渡さない=現行同等。clip局所の最小書換え+事後T1/T2で足りる)。
**位置づけ**: 3.と2.は『確定済みKP/Word/文法/日本語訳を保護する』(原文§3)の実装。基準の緩和ではなく、既存の事後STOP(T1-T3)を事前に移すだけ(同じ純関数)。承認済みLR Promptの文言・7 Gate・閾値は不変。
**英語以外の保護**: LRは英語本文のみ変える。日本語訳・日本語解説は不変(UD-1の既存扱い)。c6のLR前後で当該Part訳文が不変であること、英語Beforeと訳の対応が崩れないことを証拠(§8 E1)で目視確認項目に入れる。

### D7. 記録・Style照合・台帳(加算)
- `final_adoption`: D2。LR block採用=depth1(`er130:428`の`LR_TAKE_INCONSISTENT`を回避)。
- `er130.dialogue_legacy_fallback_direct`(`:265-278`): `take.ordinal == dt.final_attempt_n` を `take.ordinal + 3*take.depth == dt.final_attempt_n`(depthキー無し=0)へ。n=6採用(ordinal3,depth1)で直接記録として成立。
- `er129._derive_from_logs`(`:510-520`)のdialogue_tts分岐: `final_adoption`が無い旧記録はdepth0のまま(旧entryと同形)。LR block採用の新記録は`final_adoption`が優先されるので導出分岐は触らない。
- `build_entry`(`er063:1223`): 既存のdeviation生成(`local_rewrite_recovery`→`audio_text_deviation`)がそのまま働く。`style_actual`(`build_style_actual_record`)は採用attempt=ctx sha(PRIMARY)または従来Dialogue(FALLBACK)を`er129.resolve_adopted_take`経由で同定(`_adopted_take_for_style_actual`:2010)=追加不要。
- Gate: `Z_REPLACED`(`er130`)のStyle違反置換は、LR採用clipもイベントclipとして分類核が判定(新規ルール追加なし)。Gate/QA blocking条件は無変更。

### D8. 既存run(c6)の正規再開 — 状態移行ツール
新規 `tools/fz_dialogue_lr_resume_01.py`(runner/er026は編集しない=EndUser配線Workerと競合しない)。Production経路ではなく**運用ツール**(人間承認の消費をコードで記録する)。
- 既定=`--dry-run`(何も書かない): 前提条件を全て検査して計画を表示。`--apply --authorization-ref "<原文§3>"` で実行。
- 前提(全て真でなければ中止、書込0): ①`stop_scope_check`がrc=0 ②clip stateが v1/v2 の `status=TERMINAL_NG`・`n_started==3`・`lr`未使用・policy=fz_ctx_v1・`canonical_text_sha256`が現plan本文と一致・`ctx_style_sha256`が`style_for`と一致 ③Lock=`HUMAN_REVIEW_REQUIRED`で同text sha、`cumulative_tts_attempts`==3 ④3 attemptが全て`counted`・`finished` ⑤対象clipは `--clip` で明示(複数clip一括の暗黙適用はしない)。
- 実行(原子的・バックアップ`*.pre_fzlr_migration`): state → `status=IN_PROGRESS, phase=LR, lr={state:PENDING, migration:{from, at, authorization_ref, consumed:{n:3, rows:…}}}`、`ng_transcripts` を state の`log_rows`(#1,#3)と`er011_output/attempt_history.jsonl`の`A2_SLOWDOWN_REVERIFY`イベント(`post_slowdown_asr_text`、例 `:20128` run d420bbe8…)から**出典付きで**補完 → Lock は既存`review_lock.approve_regenerate(out_path, text, approved_by="user:FZ-DIALOGUE-LR-ADOPTION-01 原文§3")`(`er011:475`。「ユーザーの明示的な指示でのみ」=原文§3が該当)→ attempt_history に `FZ_DIALOGUE_LR_RESUME_MIGRATION` を追記。
- 再開は通常のrunner起動(`--stage tts_b1b --only-clips full_story_part3_c6 --mode real`、300秒内≤2起動規律)。`_open()`は IN_PROGRESS=resume扱い(`--only-clips`の明示信号でも新規サイクルにならない=`er122:200-204`の既存挙動)で、#1〜#3は再実行されない。LR→④…を実行し、PASSで停止。Lockは`REGENERATE_APPROVED`をここで消費し、終了時`record_outcome`が RESOLVED/HR を記録(累積TTS=3+新規)。
- 冪等: 2回目の`--apply`は拒否。LR後の再実行は通常resume(保存LR本文を使用、LR LLM再実行なし)。
- これは「HR Lockの迂回」ではなく、原文§3の明示指示を消費する既存の人間承認経路(`approve_regenerate`)+新規の状態遷移(試行履歴は破棄せず消費済みとして保持)。

### D9. 終端・HR・resume・再入禁止
- 終端HRは既存safety: LR不可/NO_CANDIDATE/RETTS_FAILED/LR例外/B2終端NG → `register_terminal_hr`(重複抑止付きHRQ1行)→ `record_outcome`でLock=HUMAN_REVIEW_REQUIRED → stage `FamilyZTtsClipFailedStop`(rc=2、`er026:2610`)。HR提示は`PM_GOVERNANCE.md` 30節の到達経路7項目形式(30節の「ZセリフLR対象外」はD10で更新)。
- 再入禁止の多重防御: ①persisted `lr.state` ②`LocalRewriteReentryError`(depth>=1) ③`run_local_rewrite_recovery(depth>=1)`のRuntimeError。LR block内のNGから再度LRへは行かない。
- resume: 各n・各phase境界でのkill→再開はstateのみで継続(TTS前にn_started永続、LR本文は再TTS前に永続)。STOP sentinelは待機中5秒刻み・各attempt前・**LR LLM前**に確認(LR LLM前の確認はD3で追加)。
- 技術STOP(Secondary/Whisper不能等)はLR・HRに入れず再開可(既存規則)。

### D10. 一覧・SSOT・撤去/残置
- 正式一覧=8区分(原文§4)。`ROW_MAPPING_02.json/.md`を新設(正式47行=旧49行から`Z-*-DIALOGUE-LEGACY`2行を外し、`Z-*-DIALOGUE-CTX`2行をlr=あり/6回/待機2回へ)。旧`ROW_MAPPING_01`は履歴として残し冒頭に『Z_DLG_LEGACY独立行は2026-10-29に正式一覧から削除。互換定義は`er127.PROFILES["Z_DLG_LEGACY"]`』の注記。`er127` MapTests(`:23,140-166`)は02を読む(正式47行がprofileと一致)+互換test(`Z_DLG_LEGACY`が`PROFILES`に残る・policy=legacy runが従来動作)を別caseに。
- `CURRENT_SPEC.md`: `:3161`見出しを8区分へ、`:3171`をZ_DLG_CTX(LRあり・6/2回・終端=B2最終NG→Lock→HR)に更新、**`:3172`の独立行を削除**(従来方式は『Z_DLG_CTXの③⑥のFallback』として本文で説明、互換・ロールバックの残置を明記)、`:3179`・`:1652`の「LRなし」記述を『2026-10-29以降はLRあり(履歴)』に。`DECISION_LOG`/`OPEN_ITEMS`(OPEN-528 Deferred(1)・UDR-TRA-1にsupersede注記)、`PM_GOVERNANCE.md` 30節のHR経路。
- 残置: `Z_DLG_LEGACY`、`policy=legacy`、従来Dialogue Style、`er063:1037-`のlegacy方式。撤去: なし(撤去対象の旧検査は『Zセリフ=LR非対象』を前提にした `er130 LR_ON_NON_LR_ROLE` の**Z_DLG_CTXに対する効力**のみ=Profile変更で自然に外れる。他policyには残る)。
- 実装後のGrep確認: `Z_DLG_LEGACY`が正式一覧(CURRENT_SPEC表・ROW_MAPPING_02)に出ないこと/コード・互換docには残ること、`MAX_TOTAL_ATTEMPTS`・`PRODUCTION_MAX_TTS_ATTEMPTS`参照の網羅、「LRなし」(Z dialogue)の残存。

### D11. ユーザー向け最終報告(原文§6)
既存スタックがZ形LRを扱う(CURRENT_STATE §1,§5): `er129`台帳(Before/After・変更箇所anchor・理由=`rationale`/復元audit・対象clip・採用がLR blockか=`final_adoption.depth`)→`er132`(Z表示本文overlay+三者一致)→`er131`(最終Human報告)・`er133`(⏸/LR赤/Fallback濃青)。LRとFallback両方=双方表示は既存仕様。TTS Prompt/ASR正解/学習者向け本文へ混入しないことは`er132.assert_no_public_leak`+三者一致で担保済み。**Zセリフ固有の追加実装は無し**の見込み。ただしdialogue clipの表示で(a)対象音声区間=clip id(`full_story_part3_c6`)+話者/Voice(Takehiro/Puck)の表記、(b)『最終採用音声がLR後か』=`final_adoption.depth>=1`が出ること、を実装時にtestで固定する(未確認なら追補)。
4者一致(表示=TTS入力=ASR正解=実音声): 3者は`er132.assert_text_parity`、実音声は採用attemptのASR転写(統一judge `PASS_WITH_WARNING(LR_REWRITTEN)`)とLR後`expected`の一致で担保。E1で採用wavを独立にASR再実行(既存`routing.transcribe`)し転写≒LR後英文を確認する。

## 3. 並行Workerとの競合回避
編集予定: `er122_fz_ctx_policy_01.py`、`er127_tts_block_policy_01.py:114`(1行)、`er063_family_z_audio_01.py`の4-D節(:893-975)と`dialogue()`(:1037-)付近のみ、`er003_v1_n3_01_tts_generate.py:503-552`、`er012_b…:483-`(attempt_ctx 1行)、`er020…:757-`(加算kw)、`er129`(加算関数)、`er130:265-278`、新規 `tools/fz_dialogue_lr_resume_01.py`、test。**触らない**: `er026_family_z_fiction_production_runner_01.py`(page_verify付近は別Worker)、`er121_*`、`er019_*`、`er135_*`。各ファイルはEdit直前にRe-Read+`git diff --stat`で未commit差分の有無を確認(他Workerの未commit差分が同一ファイルにある場合は待機/Fable報告)。

## 4. 5Gate・安全性チェック(CLAUDE.md安全境界)
- 新flag・env・起動script条件なし(承認済み仕様の既定動作。切替は`er127.unified_flow_active()`の既存単一読取関数とpolicy=fz_ctx_v1のみ)。DefaultOff型は不要だが、**A/B/C・policy=legacy・X/Y/narrator/KP/JAのbyte同一**をgolden/AST testで固定(TEST_PLAN T-D)。
- 新Gate・品質基準の変更なし。D6は既存T1-T3純関数の事前適用(同一基準)、Z限定の入力選択規則。
- retry/fallback/regeneration/resumeの既存安全装置(180秒・STOP sentinel・consumed不再実行・Lock・累積TTS 15)を迂回しない。

## 5. LR品質条件(原文§3)の担保マトリクス
| 条件 | 担保 | 追加要否 |
|---|---|---|
| 原作の意味・事実関係を変えない | LR Gate 1(意味保持)・3(事実無矛盾)=Luna QA、全文性/span整合/数値保持(`er020:352-402`) | 既存で担保 |
| 武弘の証言内容・人物像・感情表現 | Gate 2(role保持)・5(自然英語)、ctx Styleは元clipのnotes(文脈・感情)を維持(LR後もsame sha) | 既存+ctx Style維持 |
| 他の証言との矛盾・曖昧さを勝手に解消しない | Gate 3/4(clip局所)+最小変更(Gate 6局所性・7非全面書換え≥0.7) | 文脈未提供(O2)。clip局所+最小書換えで担保、c6の目視確認項目に入れる |
| 必要最小限の書換え | Gate 6/7 + 候補選定=unchanged_ratio最大 | 既存 |
| 確定KP/Word/文法/日本語訳の保護 | **D6**(事前保護+事後T1-T3)。日本語訳は不変・Before/After対応を目視 | **Z追加(D6)** |
| 最終表示本文=TTS入力=ASR正解の一致 | `er132.assert_text_parity`+`z_assemble_gate` | 既存(dialogue evidenceで確認) |
| 無理な書換え/基準緩和をしない | LR不可=HR(既存)。Gate緩和なし | — |

## 6. 引用符付き本文でのLR入出力の対応(OPEN-596対応後)
LRの単位=clip全文(`full_story_part3_c6`の`tts_safe_news_en`後本文、先頭の`"`と入れ子`'…'`を含む)。LRはclip本文全体を逐語再現して問題spanのみ置換した候補を返し、`diagnose_candidate_full_segment`が全文性・span整合・先頭引用符の追加禁止(`LEADING_QUOTE_OR_LABEL_ADDED`)を検査する(原文が先頭引用符を持つ場合は許容)。表示側は`entry.canonical_text`(引用符つき)へ`locate_op`で位置特定しoverlay(CURRENT_STATE §7: OK)。閉じ無し引用(OPEN-596のcluster)も同様にclip単位なので追加対応不要。

## 7. 未決・リスク(Fable/Opusへ)
- R1: c6のLR後に④〜⑥が再び反復検査等でNGになる可能性(#3のNG原因はTTS側の反復で、LRで本文を少し変えても改善する保証はない)。その場合は終端HR(新形式)。
- R2: D6の入力選択でc6が#1のspan(`an`→`and`)に誘導される=実際の問題(TTSの`sink`誤発音・反復)と無関係な箇所を書換える可能性。LR候補は#1のASR差分を回避する書換えを作るだけで、効果は不確実。成功率は事前に見積れない(offline推定不能)。
- R3: 外側guard化(D3)で通常パスのLock記録粒度が変わる。goldenで同値確認必須。
- R4: Adv外側ループ・leafの共有コードに加算kwを入れる(B Voices A2/Z legacyのbyte同一をgoldenで確認)。

## 8. 費用・時間・evidence計画
- 見込み(実測単価: 1 attempt=TTS+ASR≈¥0.35、LR≈¥0.28、`COST_01.md` §4):
  - E1 c6正式再開: LR ¥0.28 + TTS/ASR 最大3(④⑤⑥)×¥0.35〜0.5 + 減速後ASR ≈ **¥1.5〜2.5**(PASSなら¥0.7〜1.2)。待機は⑤NG時のみ180秒。
  - E3 Std copy-run(Gate強制NG注入、TTS≤¥15の枠内): 注入attempt①②③は実TTS(NG判定のみ注入)+LR LLM+④⑤⑥… 最大6 TTS×0.35+LR0.28 ≈ **¥2.4〜3.5**(180秒×2)。
  - E4 resume/kill(copy-run、TTS≤3): ≈¥1。
  - 合計 **約¥5〜8**(上限見積¥12)。Fableの見込み¥15〜20より小さい。累計 ¥122.02 → 約¥127〜135(現Cap¥135内に収まる見込み。余裕のため¥145を推奨、7-7の300円以下自律範囲)。
- 量産単価: LR発火は『clipが6回目まで届く』ときのみ。本記事は28 dialogue clip中c6の1件(Std側HR 2件は別経緯)。発火1件あたり最大 ¥0.28+3×0.35≈¥1.3。1記事セットあたり ¥0〜2.6(発火0〜2件)=**70円目標に対し0〜+3.7%**。LR発火が不要な記事は単価不変(待機・LR LLMは発火時のみ)。実発火率は運用で実測し報告。
- evidence(正式経路・DEV/Trial専用経路は証拠にしない):
  - **E1(主)**: c6を移行ツール→正式runner(`--stage tts_b1b --only-clips full_story_part3_c6 --mode real`)で実再開。LR Before/After(赤)・ログ・採否・費用・採用wavの独立ASR再実行・4者一致。
  - **E2**: 同stageでc6以外の13 Adv dialogue clipが再利用(API 0・sha不変)。
  - **E3(Std)**: 正式runnerのcopy-run(`run_fzlr_ev_a2_01`等、`tru_ev_cases_01.py`式の強制NG注入=『注入』と明記)でStd dialogue 1 clipを①②NG→180秒→③NG→LR→④…。注入点はGate判定のみ(TTS・ASR・LR LLM・ctx Styleは実)。
  - **E4**: kill→resume(各phase境界)・再入禁止・regeneration・policy=legacy不変・Lock/HRQ1行はtest+copy-run。
  - **E5**: 回帰(X/Y/Z既存test・golden 80・旧失敗集合同一)。
- 完成候補再提出(原文§9): c6 OK後に `gate,assemble,pages,page_verify`(`--stages provision_shell,gate,assemble,pages,page_verify`を**1起動**=OPEN-480)→Std/Adv完成候補ページ更新(Voice配役・Std `bandit`・`constable`追加解説の維持を既存`VOICE_TABLE_AFTER_14.md`と照合)。End User向けページはOPEN-597(別Worker)の配線状況に合わせて併記/未配線明示。
- 順序: ①実装+test(API 0、本Worker)→②Opus条件A→③E3(Std copy-run)とE1を**並行**可能(別run dir・別clip。ただし300秒内≤2起動規律のため起動間隔≥150秒)。

## 9. Opusレビュー依頼論点(条件A: 新しい処理フローの設計)
O1: D6-1 LR入力転写の選択規則(新しい順・確定文除外)と『最終attemptのみ』からの逸脱の妥当性。c6の#3(反復検査のみNG)で構造的にLR不可になる問題の他解(例: 反復検査NGは『LR適用不可』と割り切りHRへ)との比較。
O2: D6-3 文脈(隣接clip)を渡す/渡さない。D6-2 `candidate_filter`(共通コアへの加算hook)とZ限定wrapperのみ(retts直前の拒否)の比較。
O3: D3 外側guard化によるLock記録粒度の変化とgolden同値の十分性、`finalize_a2_slowdown_final_ng`/HRQ1行の位置。
O4: D2 state v2とD8移行(`TERMINAL_NG→IN_PROGRESS/LR`+`approve_regenerate`消費)の安全性・不変条件(LR1回・TTS≤6・待機2回・consumed不再実行)の十分性、v1 TERMINAL_NGを自動遷移させない判断。
O5: D4 共有コアへの加算kw(外側ループ・leaf attempt_ctx)の影響範囲。
O6: D5 adapter vs 実BlockRun+BlockProgress。
O7: D7 `final_adoption`/er130/er129の整合(depth1・ordinal規則)、`LR_ON_NON_LR_ROLE`の扱い。
O8: D10 ROW_MAPPING_02と互換test、独立行削除=従来Styleの撤去と混同していないか。
O9: evidence設計(E1実走+E3注入)でPRODUCTION_WIRED(原文§7全項目)を満たすか。

## 10. 判断候補(Fable宛・D/Cの別を付記)
- **JC-1 [B 承認範囲内自己解決、Opus確認推奨]** LR入力転写規則(D6-1): 原文§3『c6をLR段階から再開』が成立するために必要(最終転写では構造的にLR不可)。X/Y不変・Z限定。根拠: `CURRENT_STATE_01.md` §4(#3 found:false)。
- **JC-2 [B]** 確定内容の事前保護(D6-2、共通コアは加算kwのみ): 原文§3『確定済みKP等を保護』の実装。新Gateではなく既存T1-T3の前倒し。根拠: c6本文に確定`sank for ever`/`on soft feet`。
- **JC-3 [C 現タスクと独立の既知事項]** c6の実NG原因(TTSの`sink`誤発音/反復)はLRで直る保証がない(R1/R2)。失敗時は新形式HR提示→ユーザー採用判断(UDR新規、`hr_adopt_01.py`系)。現時点でユーザー判断は不要。
- **JC-4 [A 既判断]** UDR-TRA-1(2026-10-26「Zセリフ用LRは追加しない」)は今回の原文で上書き(supersede記録のみ)。
