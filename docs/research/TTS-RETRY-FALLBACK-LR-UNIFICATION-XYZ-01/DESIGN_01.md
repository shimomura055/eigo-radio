# DESIGN_01 — Family X/Y/Z TTS Retry・Fallback・Local Rewrite統一の実装設計(委任_01・read-only・API 0)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01 / 2026-10-26 / 到達上限Status=DESIGN_READY(Opus独立技術レビュー[条件A]待ち)。
ユーザー原文: `docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_USER.md`(§2基本フロー・§3部位別表・§4 LR安全条件・§6必須検証)。
入力(棚卸し): `docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/`(REPORT_01・COMMON_CORE_01・consolidated_01.json)。
関連: `SPEC_LEDGER_01.md`(要件ID)、`ROW_MAPPING_01.md/.json`(49行)、`REMOVAL_01.md`、`TEST_PLAN_01.md`、`EVIDENCE_PLAN_01.md`、`BUDGET_PLAN_01.md`、`OPUS_REVIEW_REQUEST_01.md`。

表記: 事実は`ファイル:行`、設計判断は「設計」、Fable/Opus確認事項は「確認」。本書はコード・Prompt・SSOT・run dirを一切変更していない。

---

## 0. 結論(先に読む)

1. **新仕様は「3回構成ブロック」1種類に帰着する。** 部位差は(a)③のFallback Style、(b)LRの有無、(c)KP英語のみ③④(ENGLISH_LOCK 2回)の3点だけで表現でき、`BLOCK_PROFILES`表(星取表のコード化)1枚で全49行を決定できる(ROW_MAPPING_01で機械照合済み: 9 policy)。
2. **実装は「単一policy表+共通3部品」で行い、leaf関数のTTS/ASR本体は書き換えない。** 新module `er127_tts_block_policy_01.py`(仮称。er126番は並行Agent確保の可能性があるため127)に、(i)`BLOCK_PROFILES`表と`block_policy_for(...)`(X/Y/Z run scope内のみ有効)、(ii)`cooldown_core`(180秒、1箇所定義・STOP確認つき分割sleep・時計注入・resume時の残り時間計算)、(iii)`lr_recover`(LRの共通ラッパ。深さカウンタで再入を構造的に禁止し、LR後に元と同じ3回構成を1回だけ実行する)を置く。
3. **旧条件の撤去は「scopeで分岐」する。** leaf関数は`er109_xz_scope_01.current_scope() in {X,Y,Z}`のときだけ新flowを使い、scope外(Family A/B/C=Legacy凍結[PM_GOVERNANCE 27-3/27-7])は現行とbyte同一に残す。これによりA/B/Cの出力を変えずにX/Y/Zの正式経路から旧10分待機・LR後1回・Adv技術エラー時のみStyle切替を消せる(REMOVAL_01)。
4. **Family別の共通核分岐は減る**: cooldown実装5→1、LR回復helper 3→1、KP二段実装3→1(`kp_two_stage`)、cooldown定数の正式定義は1箇所(600は`LEGACY_COOLDOWN_SECONDS`としてscope外専用)。Family別runnerのcall siteは原則変更不要(leafがscope+segment_idからpolicyを自己解決するため)。
5. **U-03(非ASR起因NG)**: ③NG後にLR適用可否を0 APIで判定し、不可(NO_NG_SPAN等)なら待機・③は省略せず(①②→180秒→③は実行済み)、③NG直後に即HR(LR LLM・LR block・無益な再TTSなし)。**これはユーザー原文§4の後半が直接答えている**ため、OPEN-536(旧=ユーザー判断要)は「原文§4=既判断」へ移せる(27-3のA)。
6. **Opus条件A該当の論点は8件**(OPUS_REVIEW_REQUEST_01)。最大の構造論点はStd本文(6%減速)の扱い(D6)と、Z dialogue ctxのstate machine統合の範囲(D10)。

---

## 1. 新仕様の確定解釈(曖昧点の扱い。ユーザー原文を逐語で変更しない)

| # | 原文の記述 | 本設計の解釈 | 根拠 |
|---|---|---|---|
| I-1 | §2-5「①〜④と同じ3回構成で再生成」 | 「①〜③」の誤記と解釈する。LR後ブロックも**3回**(①'②'③')。④は存在しない(最大TTS=6が表の根拠) | 原文§2「LRあり：最大6回」「最大TTS 6回」。4回はKP英語のみの例外と明記 |
| I-2 | §2「待機最大2回=360秒(LRあり)」 | 待機は**各ブロックの②NG後・③直前だけ**。LR書換え直後(LR block ①'直前)には待機を入れない | 原文「180秒待機は各3回構成において2回目NG後、3回目を実行する直前にのみ発生する」 |
| I-3 | §2「技術的エラーに対する既存の即時再試行は別枠」 | attempt内のF-Tech(TTS例外・発話区間検出失敗の即時1回再試行/minimal短文Styleへの即再TTS)は現行のまま残し、attempt番号を進めない・品質NG回数に数えない | 原文§2「別枠で維持」。COMMON_CORE_01 §2 |
| I-4 | §3「XYZ Standard／Advanced Key Phrase英語: ENGLISH_LOCK、4回維持、前段2→180秒→ENGLISH_LOCK 2回」 | 待機は**ENGLISH_LOCK段の実TTS直前**に1回。③④の間には入れない。Master Audio Storeのkey B hit/Azure・Whisper circuit open/STOP等で後段TTSが走らない場合は待機しない(無益な待機を作らない) | 原文§3「Fallback移行前、すなわち通常2回NG後に180秒待機…後段のENGLISH_LOCKは既存どおり最大2回」 |
| I-5 | §3「Z セリフ(文脈・感情方式): 承認済みの従来Dialogue Style」 | ctx ①②→180秒→従来Dialogue Style③(`style_prefix_override=None`)。legacy方式(ロールバック/既存run)は①②③同一従来Style+③前に180秒(共通基本フローの適用) | 原文§3。legacyは表に明記なし→A-2として確認事項 |
| I-6 | §3「Advanced KP英語解説(音声が存在する経路): 既存短文Styleの適合性を確認。不可なら同一Style」 | 音声は実在(§8)。適合と判断(§8)→①②解説Style→180秒→③短文Style、LRなし | §8 |
| I-7 | §4「LRの有無は現行を基本。Z冒頭英語の部位判定不備は是正」 | LRあり行=現行22+Z `topic_intro_en`(Std/Adv)の2=24行。他(JA・KP英語・KP解説・Zセリフ・shell固定英語)にLRを追加しない | 原文§4「独断でLRを追加しない」 |
| I-8 | §4「LR後もNGならHR」「LR後の原稿にも元のGate・ASR・音声QAを適用」 | LR block内の全attemptは元と同じleaf・同じ引数(Style/Voice/速度/QA/`m1_anchor_text`/`script_version=v1`)で走る。最終attemptのNGで初めてHRQを書く | §4/D4/D5 |
| I-9 | §4「ASR一致でも繰り返し・言い淀みQAでNGとなるケースを適切に扱い…品質NGの再試行フローや180秒待機を勝手に省略しない」 | ①②→180秒→③は省略しない。③NG後のLR適用可否判定(最終attempt転写とcanonicalの語差分)で不可なら即HR。LR block不実行 | D5 |
| I-10 | §3表外: shell固定英語(Welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five) | 表に名指しなし(X-A09/Y-S-01/Y-B-01)。Master Audio Store再利用で生成0が通常・399 entry失敗0。**現行維持**(scope内でもpolicy=None)。確認事項A-1(§7) | ROW_MAPPING_01 SHELL_EN |

---

## 2. 現行共通核の構造(事実。設計の前提)

出典: COMMON_CORE_01 §1、および本委任で再確認した行。

| leaf | 場所 | 現行の3回の作り | cooldown | LR | LR再TTS |
|---|---|---|---|---|---|
| L1 `generate_charon_english` | voice01:49(`@guarded_generate`:48) | 同一Style×3、F-Tech(attempt内minimal) | :156 `maybe_cooldown_before_attempt`(attempt==max) | :304/:323→`_local_rewrite_recovery_for_charon_english`:337 | `__wrapped__(max_attempts=1, cs=True)`:365 → **再入可** |
| L2 `generate_news_narration_wide_margin` | news_tail_fix:63(:62) | 同一Style×3、F-Tech(異常長もminimal) | :149 | :300/:325→`_local_rewrite_recovery_for_news_narration`:346 | `__wrapped__(max_attempts=1)`:372、**style_prefix_override脱落**、再入可 |
| L3 `generate_english_segment_with_fallback` | crosslevel:95 | 標準2(strict)+minimal1(`_run_a2_minimal_fallback_attempt`:327) | :200(`overall_attempt==budget`) | :288/:318→`_local_rewrite_recovery_for_english_segment_with_fallback`:402 | `_run_a2_minimal_fallback_attempt`直呼び(minimal Style、再入なし) |
| L4 `generate_a2_segment_with_slowdown` | n3_tts:331 | L3を外側ループ(総予算3)で包み、各成功後に6%減速→再検証 | L3/strictが実施 | L3内のみ。**減速後最終NGはLRなし**→`finalize_a2_slowdown_final_ng`:309 | — |
| L5 `generate_narration_snippet_verified_strict` | repro01:198 | `max_attempts`回・同一Style | :336-343(`cooldown_total_budget`指定時のみ) | なし | — |
| L6 `generate_key_phrase_component_verified`ほか | repro01:797 / er019_kp_en_k2_store:55 / er063:1069 | 前段2+ENGLISH_LOCK 2 | なし | なし | — |
| L7 JA | n3_tts:693(`generate_a2_japanese_with_fallback`)、voice01:446(`generate_charon_japanese`) | 標準2+JA minimal1 | なし | なし | — |
| L8 `generate_voice_body_wide_margin` | er012_b:483 | `attempt_hook`(Z dialogue ctx)で①②ctx→cooldown→③従来 | hook内(er122:298-338) | なし | — |

定数: `COOLDOWN_SECONDS=600.0`(er020:57)、`PRODUCTION_MAX_TTS_ATTEMPTS=3`(er011:80)、`PRODUCTION_STANDARD_TTS_ATTEMPTS=2`(er011:102、`assert 2+1==3`:104)、`MAX_CUMULATIVE_TTS_ATTEMPTS=15`(er011:68)。
scope: X/Y/Z TTS段は`er109_xz_scope_01.family_scope`で囲まれる(X=er019:1428/1795、Y=er121_audio:428/515、Z=er063:1490)。`is_active_for_run()`は別feature(ASR表記同値層)のflagに従属するため**本件の判定には使わない**(D1)。

---

## 3. 設計(D1〜D14)

### D1 `BLOCK_PROFILES`表と`block_policy_for` — 星取表のコード化・scope gate

```
er127.BLOCK_PROFILES = {
  "EN_LR_STD":  Profile(style_seq=("PRIMARY","PRIMARY","FALLBACK_MINIMAL_EN"), cooldown_before=3, lr=True,  slots=6, ...),
  "EN_LR_ADV":  Profile(style_seq=("PRIMARY","PRIMARY","FALLBACK_MINIMAL_EN"), cooldown_before=3, lr=True,  slots=6, ...),
  "JA_STD":     Profile(("PRIMARY","PRIMARY","FALLBACK_MINIMAL_JA"), 3, lr=False, slots=3),
  "KP_EN":      Profile(("PRIMARY","PRIMARY","ENGLISH_LOCK","ENGLISH_LOCK"), 3, lr=False, slots=4),
  "KP_EXPL":    Profile(("PRIMARY","PRIMARY","FALLBACK_MINIMAL_EN"), 3, lr=False, slots=3),
  "Z_DLG_CTX":  Profile(("CTX","CTX","LEGACY_DIALOGUE"), 3, lr=False, slots=3),
  "Z_DLG_LEGACY": Profile(("PRIMARY","PRIMARY","PRIMARY"), 3, lr=False, slots=3),
}
def block_policy_for(leaf, segment_id, level, *, out_path=None) -> BlockPolicy | None
def unified_flow_active() -> bool   # er109_xz_scope_01.current_scope() in {"X","Y","Z"}  (単一読取関数)
```

- `unified_flow_active()`は唯一の読取関数。env/引数/設定dict/起動scriptで迂回不可(CLAUDE.md安全境界と同形)。**flagではない**: 本件は`APPROVED_FOR_PRODUCTION`(2026-10-26)であり、X/Y/Z run scope内では既定で有効。scope外(Family A/B/C=Legacy凍結)は`None`を返し、leafは現行コードをそのまま通る。
- `segment_id`→profile解決は`er020.resolve_narrative_role`(narrative role)+leaf種別+level(Std/Adv)で行う。`FALLBACK_MINIMAL_EN`の実体は**既存のものを再利用**する(新Style・新Promptなし): flash-lite backend=`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`("natural, clear, conversational")、既定backend=`repro01.MINIMAL_INSTRUCTION_PREFIX`。JAは`n3_tts._A2_JA_MINIMAL_INSTRUCTION_PREFIX`、KP英語は`KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION`、Z dialogue ③は`style_prefix_override=None`。
- `BlockPolicy`が提供する関数: `before_attempt(ordinal) -> {stop, style_mode, wait_done}`(loop型leaf用)/`between_stages(...)`(stage型leaf用)/`slots()`(`slot_offset`,`total_slots`)/`lr_allowed(depth)`。**Voice・速度・role Style(①②)は呼出側が渡した値のまま**であり、policyは③のStyleだけを決める(Voice既定Style不変)。
- **機械照合**: `ROW_MAPPING_01.json`の49行すべてについて、`block_policy_for`の戻り(profile名・最大TTS・待機回数・LR有無)が一致することを`TEST_PLAN_01`のT-MAP(49 parametrize)で固定する。表を直すと49行testが落ちる=星取表とコードの乖離を機械的に防ぐ。

### D2 `cooldown_core` — 180秒の1箇所定義・STOP確認・resume

```
COOLDOWN_SECONDS = 180.0                     # 正式定義(1箇所)。er020.COOLDOWN_SECONDSはこれを再exportするのではなく、scope外(A/B/C)専用に LEGACY_COOLDOWN_SECONDS=600.0 を残す(REMOVAL_01 R-01)
def cooldown_seconds(*, legacy: bool) -> float
def cooldown_core(*, ref_epoch, seconds, stop_check, clock=time.time, sleep=time.sleep, slice_seconds=5.0, store=None) -> dict
```
- 起点=**直前attemptのNG確定時刻**(無ければ完了時刻→開始時刻。Z ctxと同じ定義 er122:298-316)。残り=`ref+seconds-clock()`。**実時間**で数えるため、resume時は消費済みの待機を再度払わない(重複待機防止)。
- `stop_check`: runnerが`register_stop_check(fn)`で登録(Z=`er063._check_stop_sentinel`→`er062.check_stop_sentinel`、Y=既存`guard`、X=`<run>/STOP`等の新規薄いwrapper)。**5秒刻み**で確認し、STOP時は例外で即中断(stateは起点保持=後でresume可)。これが**U-12の是正**(単一sleepでSTOP sentinelを見ない現状を解消)。登録が無い場合(scope外)は従来動作。
- 戻り値は現行`maybe_cooldown_before_attempt`と同じ形(`cooldown_requested_seconds`/`cooldown_actual_seconds`/`attempt_before_cooldown`/`attempt_after_cooldown`)+`resumed`/`total_elapsed_since_ref_seconds`(Z ctxの追加項目)。evidenceで**実待機秒**を検証可能にする。
- 時計注入点(`clock`/`sleep`)はtest用(実sleepしない)。`er122_fz_ctx_policy.RUNTIME`と同形で、Z ctxも`cooldown_core`に委譲(D10)。
- **発動条件(全leaf共通)**: 「③を実際にTTSする直前、かつ①②が通常NGで終わっているときだけ」。③がLock/Store hit/circuit open/STOP/予算guard等でTTSされない場合は払わない(無益な待機を作らない)。
- 呼出位置の正規化(旧4+1箇所→1実装): voice01:156→`policy.before_attempt`、news_tail_fix:149→同、crosslevel:200→`policy.between_stages`、repro01:339→KP/strictの`between_stages`、er122:298→`cooldown_core`。

### D3 Adv英語(L1/L2)の③=短文Style — 既存`_run_a2_minimal_fallback_attempt`の再利用

- 現行L1/L2はattempt内F-Tech(技術失敗時のみminimal)しか持たない。新仕様の③(ordinal==3、品質NGの後)は、**Std(L3)の③と同一の実装`crosslevel._run_a2_minimal_fallback_attempt`を呼ぶ**(`force_secondary=True`を含む。同じ③をStd/Advで二重実装しない)。L1/L2のループは`attempt==3 and policy.style_mode=="FALLBACK"`で標準TTS本体を飛ばしてこの関数へ分岐する。
- ①②のF-Tech(技術エラー時のattempt内minimal)は**別枠として残す**(I-3)。
- 確認事項(実装時): ③のtrim margin。L2標準=`LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS`、minimal=`NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS`(repro01の既定)で値が異なる可能性。現行F-Tech(news_tail_fix:171-178)が既にminimalを使うため差は既存。同値か実測で確認しtestで固定(TEST_PLAN T-ADV3)。
- Adv各QA(L1 disfluency、L2 repetition/disfluency、in_one_line文数不変)は③にも引数で転送される(`_run_a2_minimal_fallback_attempt`が`disfluency_qa`/`enable_repetition_qa`を受ける: crosslevel:331付近)。これでOPEN-389(news_tail minimal fallbackにforce_secondaryなし)の論点も③では解消(Advのminimal ③はSecondary必須)。

### D4 LR共通ラッパ`lr_recover` — 再入禁止・LR後3回構成・Style保持

現行3 helper(`_local_rewrite_recovery_for_charon_english`:voice01:337 / `_for_news_narration`:news_tail_fix:346 / `_for_english_segment_with_fallback`:crosslevel:402)は構造がほぼ同一(artifact保存・resolved合成・attempts_log連結)で、差は`retts_fn`だけ。これを1つに統合する:

```
def lr_recover(*, leaf_call, text, out_path, last_asr_text, policy, depth, leaf_kwargs) -> dict | None
    assert depth == 0                 # LR block内からは呼べない(構造的ガード。違反は LocalRewriteReentryError)
    recovery = er020.run_local_rewrite_recovery(retts_fn=_retts_block, ...)   # 既存関数は不変(候補生成・7 Gate・全文性・unchanged_ratio選定)
    def _retts_block(rewritten):      # 旧: max_attempts=1。新: 元と同じ3回構成を1回
        return leaf_call.__wrapped__(rewritten, out_path, **leaf_kwargs_same_style_voice_speed_qa,
                                     tts_block=BlockCtx(depth=1, slot_offset=3, total_slots=6,
                                                        script_version="v1", m1_anchor_text=text))
```
- **再入禁止(OPEN-376 / D-B4)**: `BlockCtx.depth>=1`では`policy.lr_allowed()`がFalse → leaf末尾のLR分岐に入らない(`cs`とは独立)。`run_local_rewrite_recovery`にも`depth`ガードを追加(二重防御。depth≥1で呼ぶと例外)。LR block内で失敗すれば`HUMAN_REVIEW_LOCKED_RETTS_FAILED`でHR。
- **Style/Voice/速度保持(OPEN-312 / U-02)**: `leaf_kwargs`は元の呼出と同一の`style_prefix_override`・`tts_backend`・`disfluency_qa`・`enable_repetition_qa`・`enable_pronunciation_resolver`・`max_extra_chars`等。**現行L2が落としている`style_prefix_override`を渡す**。LR block内の①②は元の①②と同じStyle、③は同じFallback Style(元のStyle=role Style/minimalの混在をやめる)。Voiceはleaf固有(L1=Charon、L2/L3=`p9a.VOICE_NAME`、L8=voice_name)で関数が決めるため不変。
- **LR後も同じGate**: LR block内attemptは`script_version="v1"`(LR_REWRITTENをPASS_WITH_WARNINGとして付与)+`m1_anchor_text=元原稿`+統一judge(書換え後文を正解とする`resolve_expected_text_after_local_rewrite`)+元と同じdisfluency/repetition QA+(Std)force_secondary。HR Lock keyと人間承認keyは元原稿のまま(現行仕様維持)。
- **累積budget**: 1 segmentのblock数は2(元+LR)。`record_outcome`への`attempts_log`は元+LR blockを連結(現行`resolved["attempts_log"]`連結と同形)。最大6 attempt(+F-Tech別枠)は`MAX_CUMULATIVE_TTS_ATTEMPTS=15`の範囲内。ただし`approve_regenerate`で再生成を重ねると6+6+…で3周目に15へ達する(安全上限として維持。変更しない)。
- **成功時の記録**: `local_rewrite_recovery`/`canonical_text_before_local_rewrite`/`audit/ledger_deviation`(書換えが表示本文と音声の関係に与える差)は現行形式を維持(OPEN-376 D-B6: 最初の書換えのみ記録→再入が無くなるので「最初=唯一」となり不一致が解消)。

### D5 LR適用可否判定・HRQ一本化(U-03 / U-04)

- 順序: ①②NG→180秒→③NG→**`lr_applicable(...)`(0 API)**→適用可ならLR(LLM)→LR block→最終判定。不可ならLR block不実行で**即HR**。
- `lr_applicable`: ①`policy.profile.lr==True` ②depth==0 ③NGが技術STOP(Secondary/Whisper不能=`_tech_only`)でない ④`identify_ng_span`(最終attemptのPrimary転写とcanonicalの語差分)が`found` ⑤`review_lock._has_valid_narration_layout`。④が偽(=ASR一致だがdisfluency/repetition/長さQAでNG: U-03)なら`HUMAN_REVIEW_LOCKED_NO_NG_SPAN`で即HR。**LR LLM 0回**(現行もNO_NG_SPANは候補生成前に返る[er020:773-777]ため費用は同じだが、LR呼出に至る前に判定してHR登録の契機を一本化する)。
- HRQ(`audio_retry_cascade_prod_01/human_review_queue.jsonl`)登録を**終端NGの1回に統一**: 現行は最終slot NGの統一judgeがLRの前に書く(er006:1294-1296)ため、LR成功でも行が残る(OPEN-376 D-B5)/disfluency単独NGでは行が出ない(U-04b)。新: LRあり部位は`total_slots=6`にして③(slot3)・①'②'(slot4-5)では書かせず、**終端(LR不可の③、またはLR blockの③'=slot6)**でだけ書く。LR不可の場合は`register_terminal_hr(detail)`が`_log_human_review`を呼ぶ(重複は`is_duplicate_queue_entry`で抑止済み)。LRなし部位は`total_slots=3`(KPは4)で現行どおり。
- LR成功(RESOLVED)時は行を書かない=D-B5解消。

### D6 Std本文(6%減速)の扱い — 最大の構造論点(Opus論点1)

現行: L4が外側ループ(総予算3)でL3を包み、各成功後に6%減速→減速後ASR再検証。再検証NGは「残予算で取り直し」、通算3回目のNGは`finalize_a2_slowdown_final_ng`でLRなしHR(U-09、ユーザー逐語承認なし=C)。LRはL3内(減速前の最終NG時)だけ。
新仕様の「③NG後にLR」「LR後も同じ検査」を満たすには、**減速後再検証NGも「そのattemptのNG」として数え、最終NGからLRへ入る**必要がある。案:

| 案 | 内容 | 長所 | 短所/リスク |
|---|---|---|---|
| **A(推奨)** | 減速+再検証を**各attemptの検証の一部**にする(`attempt_post_hook`をstrict/`_run_a2_minimal_fallback_attempt`に追加。既定None=他callerは不変)。attemptは「TTS→ASR PASS→減速→減速後ASR PASS」で初めてverified。外側ループ・`prior_generations`・`cooldown_total_budget`・`generations_used`(OPEN-270 M3配管)を撤去 | LR/cooldown/HRQ/slotsがすべて1つの3回構成に収まる。U-09解消。guarded_generateの外側recordと整合(L3のguard内で完結)。LR NG spanは減速後転写を使える | strict/minimalのループ内に副作用(wav上書き・`*_original.wav`退避)を入れるため、save_tts_attempt_audio順序・chunk検査(`std_chunk_slowdown_violations`)・既存fzaq8/fzaq2 testの再表現が必要。Std本文のみ影響 |
| B | L4をouter `@guarded_generate`で包み、内側L3のLRを抑止、LRはL4が最終NG(減速前exhaust/減速後最終NG)で実行 | 構造変更が小さい | 内側L3のguardがSTOPPEDをLockへ記録してからL4でLR…の順序問題(reentrancy guard[OPEN-105]で内側recordを抑止する設計の追加)。outer recordのattempts_log集計が複数の内側呼出をまたぐ |
| C(最小) | 現行維持。減速後最終NGはLRなしHRを**文書化された単一の例外**として残す | 変更最小 | 「LRあり部位でLRが走らない」例外が残る(C分類のまま)。ユーザー§4の「例外の少ない共通仕様」から後退 |

設計: **Aを推奨**、Opusが過大リスクと判断した場合はCへ縮退(B'として単一例外を明記、DESIGN/CURRENT_SPECにU-09を例外として記録)。いずれの案でも**Std chunk(X-S05/Y-S-07/Z chunk)はchunk単位で独立の3回構成+LR**(chunk境界・Plan・合成は不変。LR書換えはchunk内の局所のみ)。減速後再検証のASR/閾値は変更しない。

### D7 日本語(L7 2関数)

- `n3_tts.generate_a2_japanese_with_fallback`:693(標準2+JA minimal 1)と`voice01.generate_charon_japanese`:446は構造が既に「①②→③JA minimal」。cooldownが無いので**fallbackループ直前に`policy.between_stages`を1箇所追加**するだけ。LRなし(`lr=False`)。HRQは`er007`の日本語queue(slot3)で現行どおり。
- 日本語にLRを追加しない(I-7)。

### D8 Key Phrase英語 — 3つの二段実装の統合(`kp_two_stage`)

`repro01.generate_key_phrase_component_verified`:797、`er019_family_x_kp_en_k2_store._styled_two_stage`:55、`er063._kp_en_two_stage`:1069(+`er104`は repro01 経由)は、いずれも「前段strict(2回)→circuit open判定→ENGLISH_LOCK strict(2回)→`fallback_attempts_log`合算」の複製。`er127.kp_two_stage(primary_fn, lock_fn, circuit_open_fn, policy, ...)`へ統合し、**cooldownは`lock_fn`の先頭**(=ENGLISH_LOCK段の実TTS直前)に`cooldown_core`を1回だけ置く(I-4)。Master Store経路(key A miss→key B)ではkey B hit時に`lock_fn`が呼ばれないため自動的に待機しない。4回構成(2+2)・`slot_offset`/`total_slots`(HRQはslot4のみ)・3-ASR多数決・circuit open時のskipは**不変**。統合は挙動を変えずに複製を1つにするだけ(複製のうち1つだけ待機を入れ忘れる事故の防止が目的)。

### D9 Adv KP英語解説(L5)

`er019.generate_key_phrase_explanation_en_verified`:1205を二段(`strict(max_attempts=2, 解説Style)`→`cooldown_core`→`strict(max_attempts=1, 短文Style)`)に変更し、KPと同じ外側guardで包む(`slot_offset`/`total_slots=3`)。Y/Zは同関数をx_runner経由で呼ぶ(er063:1105)ため追加変更なし。LR・新Style・新Promptなし。適合性は§8。

### D10 Zセリフ(L8)と`er122` — 統合の範囲

- **統合する(委任_02)**: cooldown定数・時刻起点・STOP確認付き分割sleepを`cooldown_core`へ。`er122.cooldown_seconds()`(:41-44)・`_cooldown_before_fallback`(:298-338)は`cooldown_core`の薄い呼出に置換し、5秒刻みSTOP確認・resume残り時間計算は共通実装へ移す(Z ctxの設計が正本として採用される=Opus M-1/M-4レビュー済みの挙動を保存)。イベント名`CTX_COOLDOWN_BEFORE_FALLBACK`は維持(監査互換)。
- **統合しない(理由)**: `DialogueAttemptPolicy`のstate machine(`n_started`をTTS前に書く/`counted`・`carried_log`による二重計上防止[M-1]/`explicit_regenerate`・Lock`consuming_regenerate_approval`による再生成とresumeの判別[M-4]/Adv外側ループとの行会計[U-07]/DONE_OKのsha採用)はZ dialogue固有の外側ループ・Lock結合を含み、Opusレビュー済み(E-1〜E-6 runtime evidence・26 test)。これを一般化すると再レビューと証跡取り直しが必要になり、本件の必須要件(ctx②→180秒→従来③)に不要。**非Z部位向けの`BlockProgress`(D12)は同一スキーマのsubset**として実装し、将来の基底クラス統合(Z ctx = style_seq (CTX,CTX,LEGACY) のBlockProgress)を可能な形にする。
- legacy方式(`attempt_hook`なし、`er012_b`ループ)は、ループ先頭に`policy.before_attempt`を1箇所入れて③前の180秒だけ追加(Style変更なし)。
- Zセリフ ③NG後のLR: **追加しない**(I-7)。終端=Lock→TERMINAL_NG→rc=2(現行)。
- U-07(Adv ctxの行会計でlegacy ③未到達)は**据置**(OPEN-528 Deferred(2)。Adv減速後NGを外側ループで通算に数える現行を変えない。D6の案Aを採用してもdialogueの外側ループは触らない)。

### D11 Z `topic_intro_en`の役割解決(U-06 / OPEN-538)

`er020.resolve_narrative_role`に`topic_intro_en`(Z clip_id)→`TOPIC_INTRO`を追加する(1行。Zのclip_idを`topic_intro`へ変えるより安全: 保存済みrun state・audit・公開物のID互換を壊さない)。影響: (1)`connected_speech_enabled_for("topic_intro_en")`がTrueになり、**LR+cooldown+CS Equivalence層(判定)がZ topic intro(Std/Adv)で初めて有効**になる(判定層の有効化は`er006._resolve_semantic_equivalence_role`が同関数を参照するため連動。Xの`topic_intro`と同条件になる=設計意図どおり)。(2)旧run(再試行0・notOK 0の34 entry)の再利用に影響しない(generation不要)。(3)`NARRATIVE_ENGLISH_ROLE_LABELS`は既存。Opus確認: 共有関数の追加が他Family(A/B/C)の`topic_intro_en`相当IDに波及しないこと(testで固定: 非Z IDの解決は不変)。

### D12 `BlockProgress` — retry/regeneration/resumeの重複生成・重複待機防止

- 非Z部位向けに`<level_dir>/audit/tts_block_progress.json`(tmp+`os.replace`原子書込。Z ctxの`StateStore`と同形)。キー=`(segment/clip id, canonical_text sha)`。内容: `phase`(MAIN|LR)、`n_started`(TTS呼出**前**に書く)、各attemptの`finished_epoch`/`verified`、`cooldown{ref_epoch, ended_epoch, resumed}`、`lr_used`(bool)・`lr_text_sha`。
- 再開: 同一shaでIN_PROGRESSなら`n_started+1`から続ける(消費済みattemptを再実行しない)。`cooldown`は`cooldown_core`が実時間で残りを払う(再開で180秒を再度払わない)。`lr_used==True`なら**LRを再度実行しない**(LR block内で落ちた再開でも、書換え済みtextで続行しLR LLMを再実行しない)。DONE(OK)は既存`_generate_or_reuse`の再利用(canonical・style_version一致)に委ね、本storeは触れない。Lockが残っていれば既存どおり0 API(`guarded_generate`)。本文shaが変われば新規サイクル。
- `approve_regenerate`/`--only-*`の明示再生成は新規サイクル(store初期化)。ER-011の累積15は不変の上位guard。
- 性能: 書込は1 attemptあたり2回(開始前・終了後)の小さいJSON。Z ctxと同等。

### D13 Y固有 — Y Gateとの整合分析(要求4)

`er121_family_y_audio_01.y_style_gate`(:672-715)は、(a)`STD_FALLBACK_USED_OR_UNKNOWN`(Std本文で`fallback_used≠False`)、(b)`LOCAL_REWRITE_RECOVERY`(:706-709)、(c)(profile指定時)`ADV_MINIMAL_FALLBACK`/`ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED`を、人間承認(`record_human_approval`)が無ければBLOCKにする。X側の`m3_assembly_gate`(er019_style_profile:685-743)も同形(profile≠defaultのとき)。

**整合分析**: 新仕様の「HR」は**生成flowの終端**(③/LR block最終NGでLock+HRQ)であり、「採用Gate」(Assemble前に、承認済みprofile/Style以外で作られた音声を人手確認する安全装置)とは**別軸**。ユーザー2026-10-21「Fallback音声は今回の個別承認であり、今後すべて無条件自動採用ではない」(FALLBACK-APPROVAL-FINAL-ASSEMBLY_USER.md:23)は新仕様(2026-10-26)でも取り消されていない。よって:
1. **本件ではY Gate/X M3の規則を変更しない**(Gate緩和は品質Gate変更=ユーザー判断。11-8の「矛盾の是正」ではなく「Gate方針の変更」に当たる)。③PASS・LR PASSの採用は、現行のStd/X同様に人間承認を経てAssemble可、が維持される。Advは③短文Styleが新規に入るため、**Adv ③採用が新たにGate対象になる**(現行Std ③と同じ扱いに揃う)。これは新仕様の帰結であり、品質側(安全側)の挙動。
2. 矛盾していたのはGate自体ではなく、**Gateが検知する「Style違反」の中身**: 現行はLR再TTSがrole Styleを落とす(OPEN-312)ためLR採用が常に追加の違反を伴った。D4でLR block内のStyleが①②=元Style/③=Fallback Styleに揃うので、違反は「LR使用」「③ Fallback採用」の2点に純化される。
3. **最小変更の提案(任意・Gate方針は変えない)**: attempt結果に`block_evidence`(`ordinal`・`style_mode`・`wait_seconds_actual`・`lr_used`・`lr_block_ordinal`)を記録し、Gateのviolationに添えて表示する(人間承認時の判断材料。BLOCK/PASSは不変)。
4. **判断候補(Delivery改善。Fable判断)**: 「承認済みFallback(正規③、正しいFallback Styleが`block_evidence`で証明される)とLR採用を、追加の人間承認なしにAssembleへ進める」Gate緩和。効果=Y Voice 1(旗率72%)等でのHR待ち削減。**Gate/QA blocking条件の変更なので正式ユーザー承認の対象**(CLAUDE.md「承認済み…Gate・QA blocking条件の変更」)。本件の必須要件ではないため、**今回は実装せず**、実走データ(③採用率)を測ってから別途提案する。
- Voice既定Style(Y runnerの`STYLE_PROFILE="default"`)は**触らない**(OPEN-537=別件)。①②は既存の呼出引数どおり。
- Yのcs引数: `connected_speech_enabled_for(cid)`(er121_audio:386/415/454/467/487/562/602)は変更なし。policyは`y_`ID→FULL_STORY(er020:132)を既に解決する。

### D14 STOP・予算・安全上限の維持

- 維持: ER-011 Review Lock(同一canonical_textの0 API block、`approve_regenerate`/`record_human_approval`)・累積15/ASR60(`MAX_CUMULATIVE_*`)・RESTART_STORM/RUN_LOCK(Y/Z/er062系)・`budget guard`・各clip前のSTOP/予算guard(Y `guard`/Z `_check_stop_sentinel`)・`SharedNarrationBlockedError`。
- 追加: cooldown中のSTOP確認(D2)。待機中にSTOPが出れば例外で即中断し、`BlockProgress`が起点を保持。
- 待機中の有料run外部停止(26節): 本設計はsleep中の外部kill後に**自動再起動しない**(runner側の既存規則)。再開は人間/Fable指示のresume(D12で重複なし)。

---

## 4. 関数別の「残す/統合/撤去」表

| 対象 | 処置 | 内容 |
|---|---|---|
| `er020.COOLDOWN_SECONDS=600`:57 | **改名して残置**(scope外専用) | `LEGACY_COOLDOWN_SECONDS=600.0`。X/Y/Z scopeでは到達不能(testで固定) |
| `er020.maybe_cooldown_before_attempt`:64 | 残置(scope外)+X/Y/Z側呼出を`cooldown_core`へ | 旧シグネチャ維持(A/B/C goldenとtest互換) |
| `voice01._local_rewrite_recovery_for_charon_english`:337 / `news_tail_fix._…_for_news_narration`:346 / `crosslevel._…_for_english_segment_with_fallback`:402 | **統合→`lr_recover`** | 3→1。scope外は旧helperを温存(byte同一) |
| leafのLR再入(`cs`でのLR分岐) | **撤去(scope内)** | depth guardに置換。`cs`はjudge層の切替に純化 |
| `__wrapped__(max_attempts=1)` LR再TTS(voice01:365, news_tail_fix:372) | **撤去(scope内)** | 3回構成のLR block(`BlockCtx(depth=1)`) |
| L2 LR再TTSの`style_prefix_override`脱落(news_tail_fix:370-377) | **是正** | 元と同じ引数転送 |
| L1/L2 F-Techのみの「Adv=Style不変」 | **scope内で撤去** | ③短文Style(D3)。F-Techは別枠で残す |
| `n3_tts.generate_a2_segment_with_slowdown`の外側ループ/`prior_generations`/`cooldown_total_budget`/`generations_used`(OPEN-270) | **D6案Aで撤去**(案C縮退時は残置) | `finalize_a2_slowdown_final_ng`:309もA採用時は撤去 |
| `repro01`のKP二段(797)/`er019_kp_en_k2_store._styled_two_stage`:55/`er063._kp_en_two_stage`:1069 | **統合→`kp_two_stage`** | 3→1 |
| `er019.generate_key_phrase_explanation_en_verified`:1205 `KP_EXPLANATION_MAX_ATTEMPTS=3`単一段 | **二段化**(D9) | 定数は`BLOCK_PROFILES["KP_EXPL"]`へ移す |
| `er122._cooldown_before_fallback`:298-338 / `cooldown_seconds`:41 | **`cooldown_core`委譲** | 外形・イベント名維持 |
| `stop_retrying`分岐(cascade OFF専用残置コード) | **残置**(撤去しない) | rollback互換。撤去対象を増やさない(U-14=Fable判断どおり) |
| `min(max_attempts, 3)`クランプ(voice01:487/n3:732/crosslevel:149) | **残置**(意味を「1ブロックの上限」に再定義) | `max_attempts=6`を渡す旧caller[A/B/C・shell JA]のため |
| `er011.PRODUCTION_MAX_TTS_ATTEMPTS=3` / `STANDARD=2` / `assert 2+1==3`(:104) | **残置**(意味=1ブロック) | LR有りのsegment総計は6(`BLOCK_MAX_TOTAL`は表側で保持) |
| `kp_two_stage`外のKP 4回定数(`KEY_PHRASE_*_MAX_ATTEMPTS`) | 残置 | 不変 |

### Family別分岐の削減数(定量)

| 項目 | 現行 | 新設計 | 削減 |
|---|---|---|---|
| cooldown実装 | 5(voice01/news_tail_fix/crosslevel/repro01/er122) | 1(`cooldown_core`) | −4 |
| 正式経路のcooldown定数 | 1(+Z ctxが参照) | 1(`COOLDOWN_SECONDS=180`)。600はscope外`LEGACY_`のみ | 0(正式経路から600は消える) |
| LR回復helper | 3 | 1(`lr_recover`)+3薄い`leaf_call` | −2 |
| KP二段実装 | 3 | 1(`kp_two_stage`) | −2 |
| ③ Fallback実装(英語) | L3 `_run_a2_minimal_fallback_attempt`+L1/L2のF-Tech専用 | ③は`_run_a2_minimal_fallback_attempt`1つ(Adv/Std共通) | Adv ③の新規実装0 |
| LR有無の決定 | `cs`1本(関数ごとに暗黙) | `BLOCK_PROFILES`表1枚+test(49行) | 暗黙分岐→明示表 |
| Family別runner call site変更 | — | 0(topic_intro_en役割解決1行+stop_check登録3箇所のみ) | — |

---

## 5. 呼出別フロー(新仕様。各leafが実行する順序)

```
[loop型 L1/L2/L8(legacy)]            [stage型 L3/L5/L6/L7]
for n in 1..3:                       stage A: strict(max_attempts=2, PRIMARY style)  (OKなら即return)
  policy.before_attempt(n)           policy.between_stages()   <- cooldown_core (180s, 実TTS直前のみ)
     n==3: cooldown_core(180s)       stage B: FALLBACK 1回(KP: ENGLISH_LOCK 2回)
     n==3: style_mode=FALLBACK       ↓ 全NG
  attempt(n)  (同一leaf本体+QA)      lr_applicable? (0 API)
  OK→return                            可: lr_recover → leaf_call(rewritten, BlockCtx(depth=1, slot_offset=3, total_slots=6))
↓ 全NG                                       = 同じleafの同じ3回構成(①'②'→180s→③')。再入なし
lr_applicable? ... 同上                不可/LR block最終NG: register_terminal_hr → Lock(HUMAN_REVIEW_REQUIRED)
```
- ①PASS/②PASSでは`before_attempt`/`between_stages`は待機・③を発生させない(V-01/V-02)。

## 6. Z固有の整合(要求5)

1. dialogue ctx: ctx①②→180秒→従来③→HR/STOP(LRなし)。変更点は`cooldown_seconds()`の参照先(600→180)とcooldown本体の共通化のみ(D10)。
2. Z narrator Std chunk(`er063`/`er117`): chunk id(`full_story_part{n}_c{k}_k{j}`)は`resolve_narrative_role`が既にFULL_STORYへ解決(er020:148)。chunkごとに独立の`generate_a2_segment_with_slowdown`呼出(er117:14) → D6(案A)の3回構成+LR+減速後再検証。LR書換えはchunk内局所のみで、chunk plan・境界・合成(`write_raw_parent`/`verify_parent_integrity`)は不変。LR採用chunkは`local_rewrite_recovery`を持つ(`evidence_record`:543)ので親statusは現行どおり。
3. Z `topic_intro_en`(D11)。
4. Z Adv narrator(L2)・Preview/Comment(L1)は他Familyと同一policy(EN_LR_ADV)。

## 7. 例外・未確定の整理(確認事項)

| # | 内容 | 設計の暫定 | 確認先 |
|---|---|---|---|
| A-1 | shell固定英語(X-A09/Y-S-01/Y-B-01)は§3表に名指しなし | 現行維持(policy=None)。Store hit生成0・失敗0。旧「Adv Style不変」はscope内でもこの3行だけ残る | Fable(表外=現状維持でよいか。拡張する場合は③のStore汚染[③音声を通常keyへ保存しない]設計が追加で要る) |
| A-2 | Zセリフlegacy方式(ロールバック/既存run)は表に明記なし | 共通基本フロー(③前180秒、Style変更なし) | Fable |
| A-3 | D13 Gate緩和 | 本件では実装しない。測定後に別提案 | Fable→ユーザー(Gate変更) |
| A-4 | D6案(A/B/C) | A推奨 | Opus |
| A-5 | 並行Agentが`er125_*`/`er105`/`er119`/`er003_v1_n3_01_scaffold_generate.py`を編集中。本設計の実装(委任_02)は`er003_v1_n3_01_tts_generate.py`・`er020`・`er019`・`er063`・`er122`等を触る | 衝突は委任_02開始時に`git status`で確認(現時点でKP-GATE案件の編集対象と重複しない) | Fable |
| A-6 | `FamilyAUnchangedTest`(er019_family_x_pointless_01_test_01:75-97)は`er003_v1_n3_01_tts_generate.py`・`voice01`・`news_tail_fix`等のworking tree diff=0を要求 | commit後に実行すれば通る(`git status --porcelain`判定)。実装中のtest実行はcommit後に行う | 実装担当 |

## 8. Adv KP英語解説の音声実在確認と短文Style適合性(要求2)

**音声は実在する**(正式経路):
- X: `er019:2218` `common.read_wav_float(f"{narration_dir}/kp{rank}_explanation_en.wav")`で**Adv(b1b)タイムラインに組込**(`er019:2210-2217`のコメント「Advanced中間segmentを日本語意味からEnglish解説へ変更…ユーザー正式決定」、`:2885`の`audio=(kp_en.wav, kp{rank}_explanation_en.wav, …)`)。生成=`er019:1205 generate_key_phrase_explanation_en_verified`(:1748/:1760で`kp{rank}_explanation_en.wav`)。実wav: `er019_output/**/b1b/narration/kp1_explanation_en.wav`(96件を`find`で確認)。
- Y: `er121_family_y_audio_01.py:783` `_read(nd, f"kp{rank}_explanation_en")`(timeline)。生成はX共通関数(er121_audio:444 `seed_kp_explanations_cache`→X `_resolve_kp_explanations_text`)。
- Z: `er063:584` `ClipSpec(f"kp{r}_explanation_en", …, role_key="KP_EXPL_EN")`、生成`er063:1105 → x_runner.generate_key_phrase_explanation_en_verified`。b1b `kp_explanation` 130 entry(棚卸しFAMILY_Z)。
→ **適用対象はX-A08/Y-B-08/Z-B1B-KPEXPLの3行**(Stdには解説音声なし=対象外)。存在しない学習テキストを新規に音声化する変更はない。

**短文Style(minimal)の適合性** — 判断: **適合**(根拠3点):
1. 内容の性質: KP解説は複数文の説明調の通常英語(`tts_safe_en`で正規化する自然文: er019:1196-1197、`max_extra_chars=max(20,len//2)`)。Std本文・Comment・Previewも複数文の通常英語で、③には既に同じminimal Styleが使われている(L3)。minimalの内容は`natural, clear, conversational`(flash-lite: er033_styles:61)/`Speak the following text aloud naturally and clearly, in a warm podcast announcer voice. Do not add, omit, or change any words.`(既定backend: repro01:538)で、**文の長さ・語彙・言語固有の制約を持たない**(ENGLISH_LOCKのようなKP phrase専用の短語向け指示ではない)。
2. 現行Styleとの関係: ①②のP3系Styleはroleの抑揚付け(`ROLE_KP_EXPLANATION_EN`, er019_style_profile:192/239)で、③で抑揚が弱まるのは他のStd/Adv ③と同じ許容範囲(Fallbackの目的=発話の安定化)。③音声はGate(M3/`KP_EXPLANATION_STATUS_NOT_OK`等)で現行どおり検査される。
3. 検査: 同じASR(統一judge)+disfluency QA+非ラテン救済が③にも掛かる(`generate_narration_snippet_verified_strict`引数不変)。
**適合性の実測確認(委任_03のevidence内)**: 既存の解説text 3本に対しminimal ③を各1 take生成し、ASR PASS・disfluency NGなしを確認(EVIDENCE_PLAN_01 E-X5)。**PASS基準を満たさない場合のみ**「同一Style2回→180秒→同一Style③→HR」へ縮退(`BLOCK_PROFILES["KP_EXPL"].style_seq=("PRIMARY","PRIMARY","PRIMARY")`の1行変更。新Style・新Promptは作らない)。

## 9. リスクと緩和

| リスク | 影響 | 緩和 |
|---|---|---|
| D6案Aで減速処理をattempt内へ移す | Std本文の既存test(fzaq8/fzaq2/stdchunk)の再表現が必要。wav上書き順序の誤りで`*_original.wav`/attempt保存が壊れる | TEST_PLAN T-D6(減速前後wav・sha・original退避・chunk検査の固定)。Opus条件A。縮退案C |
| scope gateの取りこぼし | A/B/C出力の変化 | golden(A/B/C leaf出力のbyte同一)をscope外で実行(TEST_PLAN T-SCOPE) |
| 3回構成+LRで最大TTS 6/待機360秒 → chunk多数失敗時の所要時間 | 制作時間増(1 chunkあたり最大360秒) | 現行は最大600秒/ブロック。新=180秒/ブロックで**ブロックあたり−420秒**。LRありで最大2ブロックでも360秒<600秒+LR後1回(旧)の実質。評価はBUDGET_PLAN「制作時間」 |
| `topic_intro_en`の役割解決でCS Equivalence層がZ topic introで有効化 | 判定の甘さ方向の変化 | Xの`topic_intro`と同条件であり設計意図どおり。Opus確認項目 |
| KP二段統合の取りこぼし(3複製のうち1つで待機を忘れる) | KPの待機欠落 | `kp_two_stage`1実装+3 call siteそれぞれのunit test(T-KP) |
| 外部kill(待機中)後の再起動 | 重複生成・重複待機 | D12 `BlockProgress`+evidence E-X6(kill/resume) |

## 10. 一覧外Read(本設計で参照した一覧外ファイル)

`er011_human_review_lock_01.py`(定数68/80/102/104・guarded_generate 673-725)、`er078_asr_unified_attempt_ctx_01.py`(build_attempt_ctx)、`er006_secondary_asr_01.py:478-500,1285-1300`(HRQ書込)、`er109_xz_scope_01.py:41-100`(scope)、`er019_family_x_style_profile_01.py:685-743`(m3_assembly_gate)、`er019_family_x_kp_en_k2_store_01.py:40-110`、`er033_tts_flash_lite_family_x_styles_01.py:40-70`、`er117_chunk_tts_production_01.py`(関数一覧)、`er122_fz_ctx_policy_01.py:1-130`、`er019_family_x_pointless_01_test_01.py:75-97`、`er121_family_y_audio_01.py:650-715`、OPEN_ITEMS.md(OPEN-536/537/538/540の先頭行)、CURRENT_SPEC.md(1531/1647/1857/2185/2873/2954/2963の該当行)、FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/COST_01.md・BUDGET_PLAN_02.md(実費単価)。
