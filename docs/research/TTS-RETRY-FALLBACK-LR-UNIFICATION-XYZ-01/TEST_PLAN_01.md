# TEST_PLAN_01 — Retry/Fallback/LR統一のoffline test計画(API 0・実sleepなし)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01(設計)。実装=委任_02、runtime evidence=委任_03(EVIDENCE_PLAN_01)。
原則: (1)待機は`cooldown_core`の`clock`/`sleep`注入で検証(実sleep 0、`er122_fz_ctx_policy.RUNTIME`と同方式)。(2)TTS/ASR/judgeは既存の`er122_fz_ctx_fakes_01.py`(scripted fake。`SCENARIOS` S1〜S8、golden凍結)を拡張して共用。(3)scope外(A/B/C)は**変更前コードで生成したgolden**とのbyte同一を固定(`er122_fz_ctx_fakes_01.build_golden`と同じ手順)。(4)不整合な出力を期待値としてassertするtestは書かない(例: 旧600秒・LR後1回をscope内で期待値にしない)。

## 1. 構成と件数(新規/更新)

| 区分 | 内容 | 新規件数(目安) | 備考 |
|---|---|---|---|
| T-MAP | 49行 ROW_MAPPING_01.json の全行について`block_policy_for`の戻り(profile名・最大TTS・待機回数・LR有無・③Style種別)が一致 | 49(parametrize)+3(集計: LR行24・行数16/19/14・全ID網羅) | 星取表とコードの乖離防止の要 |
| T-SCOPE | scope外(A/B/C)のgolden: voice01/news_tail_fix/crosslevel/n3_tts/repro01/er012_b(hook=None)の結果dict・sleep列・TTS prompt列がbyte同一。scope内外の切替が`current_scope()`のみに依存し、env/引数/設定dictで変わらない | 10 | `unified_flow_active()`単一読取関数 |
| T-CD | `cooldown_core`: 180秒定数1箇所・①②では払わない・③直前のみ・①PASS/②PASS無待機・STOP分割確認(5秒刻み、STOP時中断)・resume時の残り時間(再開で再度180秒払わない)・clock注入・戻り値キー(`cooldown_actual_seconds`等)・③がTTSされない場合(Lock/Store hit/circuit open)は払わない | 14 | V-01/V-02/V-03/V-12 |
| T-BLK | `BlockPolicy.before_attempt`/`between_stages`: 全9 policyの順序(①PASS→終了/②PASS→終了/①②NG→待機→③)。最大TTS 6/3/4・待機回数(LRあり2/LRなし1)・④は存在しない | 18 | V-01〜V-03/V-06 |
| T-STY | ①②が呼出側Style・③がFallback Style(英語minimal[flash-lite `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`/既定backend `MINIMAL_INSTRUCTION_PREFIX`]、JA minimal、ENGLISH_LOCK、KP解説minimal、Z dialogue=None)。送信prompt/`speech_metadata.style`で検証。Voice名・速度(Std 6%減速Style・Adv PD06)・model_idが全attemptで同一(ordinal3でも)。Voice既定Style不変 | 16 | V-08 |
| T-ADV3 | Adv ③が`_run_a2_minimal_fallback_attempt`を呼ぶ(`force_secondary=True`)。L1(voice01)/L2(news_tail_fix)/chunk/in_one_line。trim margin確認(L2標準 vs minimal)。①②のF-Tech(技術エラー)は別枠で残りattempt番号を進めない | 10 | S-02/F-03 |
| T-LR | LR共通ラッパ: LRあり部位のみ発動(JA/KP/KP解説/Zセリフ/shellは呼ばれない)。③NG→`lr_applicable`→LR→LR block(①'②'→180秒→③')。LR PASS(①'PASS/②'PASS/③'PASS各)・LR block最終NG→HR。`script_version=v1`・`m1_anchor_text`=元原稿・書換え後文が全attemptの正解・Lock keyは元原稿 | 16 | V-05/V-09 |
| T-LRN | U-03: ASR一致+disfluency/repetition単独NGの③NG→`NO_NG_SPAN`→LR LLM 0回・LR block 0回・即HR・待機/③は実行済み。技術STOP(Secondary不能)ではLRしない | 6 | L-08 |
| T-RE | LR再入禁止: LR block内で`depth>=1`ではLR分岐に入らない(`LocalRewriteReentryError`/`lr_allowed()==False`)。`run_local_rewrite_recovery`のdepthガード。LR回数≤1・TTS総数≤6・待機≤2を全シナリオ(全NG)で不変条件として検証。深さ2の旧実例(hormuz comment_4等)の再現入力で再入しない | 8 | V-06/F-07 |
| T-HRL | HR Lock/HRQ/終端: 終端NGでLock=HUMAN_REVIEW_REQUIRED・HRQ**1行**(LR成功時0行・LR不可③NGで1行・disfluency単独NGでも1行[U-04])・同一canonical再実行は0 API・`approve_regenerate`で次の1回だけ・Assemble前Gate BLOCK(X)/`YE2EStop`(Y)/`FamilyZTtsClipFailedStop` rc=2(Z)・STOP中は新規TTS 0 | 14 | V-11 |
| T-KP | KP英語: 前段2(X/Z=K2、Y=MINIMAL)→ENGLISH_LOCK段直前に180秒→ENGLISH_LOCK 2→HR(slot4のみHRQ)。3複製(repro01/k2_store/er063)が`kp_two_stage`経由で同一挙動。Store key B hit・circuit open時は待機0・TTS0。3-ASR多数決・非ラテン再判定不変 | 12 | V-07 |
| T-KPX | KP解説: ①②解説Style→180秒→③短文Style→HR。LRなし。X/Y/Z 3 call site。適合性縮退(`style_seq`をPRIMARY×3に変えると「同一2回→180→同一③」になる) | 8 | S-06 |
| T-JA | JA: ①②→180秒→③JA minimal→HR(日本語HRQ slot3)。LR呼出0。2関数(n3_tts/voice01) | 6 | S-04 |
| T-Z | Zセリフ: ctx①②→180秒(5秒刻み)→従来③→TERMINAL_NG→rc=2。legacy方式も180秒。Adv高速化(減速後NGを通算に数える)不変。U-07据置の回帰 | 8(既存E-1〜E-6系26 testを180秒へ更新して維持) | S-03 |
| T-ROLE | `resolve_narrative_role("topic_intro_en")=="TOPIC_INTRO"`、cs/LR/cooldown有効。A/B/CのID解決不変。X `topic_intro`不変 | 6 | S-07/U-06 |
| T-D6 | (案A採用時)Std本文: 減速+再検証がattempt内。①減速後NG→attempt NG(②へ)・②③も同様・最終NG→LR(減速後転写でNG span)・LR block内も減速。`*_original.wav`退避・attempt audio保存・sha・chunk別`std_chunk_slowdown_violations`・親集約が不変。Std chunkのLR(chunk内局所、plan/境界/合成不変) | 14 | D6 |
| T-RES | resume/regeneration: 待機中kill→再開で①②再実行0・残り時間のみ待機(Z ctxは既存、非Zは`BlockProgress`)。LR block内kill→再開で`lr_used`によりLR LLM再実行0・書換えtextで続行。DONE_OK再利用(API 0)。Lock中0 API。`approve_regenerate`で新サイクル。二重計上なし(attempts_log連結) | 12 | V-12 |
| T-Y | Y: Y Gateの規則は不変(`STD_FALLBACK_USED_OR_UNKNOWN`/`LOCAL_REWRITE_RECOVERY`/`ADV_MINIMAL_FALLBACK`は③/LR採用時に従来どおりBLOCK)。`block_evidence`が付与されること。Voice既定Style・`STYLE_PROFILE="default"`不変。Y Std/Advで`y_voice_*`が同一policy | 8 | D13 |
| T-REG | 既存regressionの維持(§2) | (既存) | — |
| 合計(新規) | | **約240件**(うちT-MAP 52件がparametrize) | |

## 2. 既存testの再利用(変更なし=golden/regression)

対象モジュールの既存test(`*_test*.py`)を、scope外golden・scope内regressionとしてそのまま実行する:
`generate_charon_english`言及22ファイル、`generate_news_narration_wide_margin`20、`generate_english_segment_with_fallback`22、`generate_a2_segment_with_slowdown`21、`generate_a2_japanese_with_fallback`8、`generate_key_phrase_component_verified`12、`generate_voice_body_wide_margin`15、`run_local_rewrite_recovery`8、`maybe_cooldown_before_attempt`8、`DialogueAttemptPolicy|dialogue_ctx`3、`_local_rewrite_recovery_for_`7ファイル(grep実測)。
特に再利用: `er020_tts_retry_local_rewrite_01_test_01.py`(LR本体・cooldown旧シグネチャ=legacy golden)、`er003_lr_post_rewrite_outer_loop_fzaq8_test_01.py`/`er020_lr_post_rewrite_expected_text_fzaq2_test_01.py`(LR後expected text規則)、`er007_ja_tts_retry_path_fix_test_01.py`、`er058_asr_tts_prodfix_01_test_01.py`、`er122_fz_ctx_policy_test_01.py`・`er122_fzcw_runtime_evidence_test_01.py`・`er063_fz_ctx_wiring_test_01.py`(Z ctx)、`er019_*`/`er121_*`/`er026_*`/`er063_*`/`er117_*`のstd chunk・KP・Y Gate系。

### 2-1. 更新が必要な既存test(REMOVAL_01 §3の表を正とする)
600秒を固定するもの(er122_fz_ctx_policy_test_01:117-131/208-219、er122_fzcw_runtime_evidence_test_01:207-213、er063_fz_ctx_wiring_test_01:248/396、er007_ja_tts_retry_path_fix_test_01:465-469、er063_family_z_audio_01_test_01:64)、LR後1回を固定するもの(fzaq8/fzaq2/er078_wiring_05/er025_phase3)、通算3回目直前を固定するもの(er058 M3)。

### 2-2. 既知の失敗とその扱い(OPEN-543)
HEAD既存失敗4件(er119 2件・er108 Importers[er123/er124]・er019 R4 hunk classifier)は本件の前から存在。実装前後で**差分が増えないこと**(同じ4件のまま)を確認し、新規失敗を混ぜない。`FamilyAUnchangedTest`はcommit後に実行。

## 3. 時計・fake・harness設計

- `cooldown_core(clock=, sleep=)`: fake clockが`sleep(s)`で`t+=s`、5秒刻み確認が`stop_check`を呼ぶ回数も記録(`sum(sleeps)==180`、`max(sleeps)<=5`)。
- leaf fake: `er122_fz_ctx_fakes_01.World`を拡張し、TTS呼出ごとの成否・ASR判定列(`SCENARIOS`)に加えて「呼出ordinal→強制NG」を指定可能にする(evidence driverと同じ意味論=NG方向のみ)。
- 各leafについて同一シナリオ表を流す**leaf matrix**: シナリオ ∈ {① PASS, ②PASS, ①②NG③PASS, ①②③NG(LRなし→HR), ①②③NG→LR→①'PASS, ①②③NG→LR→①'②'NG→③'PASS, 全6NG→HR, LR不可③NG→HR, 技術失敗(F-Tech)混在, STOP中}。
  - LRありleaf(L1,L2,L3,L4[案A]): 全シナリオ。
  - LRなしleaf(L7×2,L5,L6×3,L8 ctx/legacy): LR関連を除く5シナリオ。
- 各シナリオで不変条件を共通assert: `tts_calls<=max_tts`、`lr_calls<=1`、`cooldown_events<=waits`、`sum(actual_wait)==180*n`、④(5番目以降)なし(KP除く)、`record_outcome`は1回、Lock状態、HRQ行数。

## 4. leaf別matrix

| leaf | 呼出元(Family) | 新規test |
|---|---|---|
| L1 voice01 | X/Y/Z Adv topic_intro・preview・comment、Z Adv preview/comment | シナリオ全10 |
| L2 news_tail_fix | X/Y/Z Adv 本文・chunk・in_one_line | 全10(+Style保持) |
| L3 crosslevel | X/Y/Z Std topic_intro、Z Std topic_intro_en | 全10 |
| L4 n3_tts | X/Y/Z Std 本文・chunk・in_one_line | 全10+T-D6 |
| L5 repro01 strict(KP解説) | X/Y/Z Adv | 5 |
| L6 KP×3複製 | X/Z(K2)/Y(MINIMAL) | 5×3 |
| L7 JA×2 | X/Y/Z Std | 5×2 |
| L8 ctx/legacy | Z Std/Adv dialogue | 既存26+180秒更新、legacy 5 |

## 5. Family別統合test(runner接続)

- **X**(`er019`): TTS stage→segment結果JSONの`block_evidence`・Assemble前Gate BLOCK・exit code(segment NGでrunnerは停止せずGate BLOCK)。STOP sentinel登録(`register_stop_check`)・cooldown中STOP→中断→resume。
- **Y**(`er121`): `generate_y_b1/a2_segments`のguard(予算/STOP)・Y Gate(`y_style_gate`)・`YE2EStop` rc=2・chunk(Y)・`y_voice_*`policy。
- **Z**(`er063`/`er026`): 全clip処理後`FamilyZTtsClipFailedStop` rc=2・dialogue ctx・topic_intro_en・chunk narrator・`_check_stop_sentinel`登録。
- 共通: `BlockProgress`のresume、`approve_regenerate`、`--only-clips/--only-segments`再生成。

## 6. 静的検査(撤去の機械確認)

REMOVAL_01 §5のGrepをtest化: (1)X/Y/Z専用moduleに`er020.COOLDOWN_SECONDS`参照0、(2)`COOLDOWN_SECONDS==180.0`かつ`LEGACY_COOLDOWN_SECONDS==600.0`はscope外専用で`unified_flow_active()==True`のとき`cooldown_seconds()==180`、(3)scope内で旧LR helperが呼ばれない、(4)`BLOCK_PROFILES`のkeyが9 policyで未使用keyなし。

## 7. 要件→test→evidenceトレーサビリティ

| 要件 | test | evidence |
|---|---|---|
| V-01/V-02 | T-BLK, T-CD | E-N(正常) |
| V-03/V-10 | T-BLK, T-STY, T-CD | E-S1 |
| V-04 | T-BLK, T-HRL | E-S3 |
| V-05/V-09 | T-LR | E-S2a, E-S2b |
| V-06 | T-RE, T-BLK | E-S2b |
| V-07 | T-KP | E-S4 |
| V-08 | T-STY | E-S1, E-S2a |
| V-11 | T-HRL, T-Y, T-Z | E-S2b, E-S3 |
| V-12 | T-RES, T-CD | E-S6 |
| L-08(U-03) | T-LRN | E-S7 |
| S-06(KP解説適合) | T-KPX | E-X5 |
| S-07(U-06) | T-ROLE | E-S1(Z topic) |

## 8. 実行手順(委任_02)

1. 変更前コードでgolden(scope外・hook=None)を再生成してcommit(比較基準)。2. er127(policy/cooldown/lr/kp_two_stage/progress)をTDDで追加。3. leafを順次(L7→L5→L6→L1→L2→L3→L8→L4[D6])差し替え、各段でleaf matrixとgoldenを実行。4. Family別統合test。5. 全体regression(`py -m pytest`対象ファイル群)をcommit後に実行し、HEAD既存失敗4件から増えないことを確認。並列化: L1+L2 / L3+L4 / KP / JA+KP解説 / Z ctx / Y・X・Zのrunner統合 を別担当で並行(同一ファイル競合なし、`er127`共通コアが先行)。
