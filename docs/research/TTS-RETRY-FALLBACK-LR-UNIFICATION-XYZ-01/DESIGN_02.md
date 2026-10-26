# DESIGN_02 — DESIGN_01 へのOpus条件Aレビュー反映差分と実装確定事項(委任_02)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02 / 2026-10-26。到達上限Status=IMPLEMENTED(test PASS、runtime evidenceは委任_03。PRODUCTION_WIRED判定はFable)。
入力: `DESIGN_01.md`(骨格は不変)、`OPUS_REVIEW_01.md`(逐語。Opus判定=GO with changes、M-1〜M-11は実装前必須、R-1〜R-7は推奨)。
本書は**差分**だけを書く。DESIGN_01のD1〜D14のうち下記以外は変更なし。実装は`er127_tts_block_policy_01.py`(共通核)+各leafのscope内分岐。

## 0. 実装方式の確定事項(DESIGN_01からの具体化)

| # | 確定内容 | 理由 |
|---|---|---|
| I-1 | 統一flowは`er127.unified_flow_active()`(=`er109_xz_scope_01.current_scope() in {X,Y,Z}`)のときだけ有効。scope外(A/B/C・単体呼出)はleafが**従来コードをそのまま**通る(golden固定)。各leafは入口で`er127.open_block(leaf, out_path, text, ctx, ...)`を1回呼び、`None`ならlegacy | M-1/DESIGN_01 D1 |
| I-2 | 1ブロックの進行は`BlockRun.step(ordinal)`→TTS→`done(ordinal, verified)`の3呼出に統一。loop型(L1,L2,L8 legacy)もstage型(L3,L5,L6,L7)も同じ。strictの内側loopは`tts_block=`/`block_ordinal_offset=`で同じ`step`を呼ぶ | I-1, 待機・STOP・resumeを1実装にする |
| I-3 | `D11 topic_intro_en`の役割追加は**scope内限定**(`resolve_narrative_role`)。Family Cが同名ID`topic_intro_en`を使うため無条件追加はA/B/C出力を変える(委任_02で発見、Opusの「他Familyに波及しないこと」確認に対する回答) | A/B/C byte同一 |
| I-4 | `er020.COOLDOWN_SECONDS`は`LEGACY_COOLDOWN_SECONDS`(600)の別名として残置(A/B/C・旧test互換)。`maybe_cooldown_before_attempt`はscope内に迷い込んでも`er127.cooldown_core`(180秒+STOP確認)へ委譲する安全網 | R-01/K-01 |
| I-5 | `kp_two_stage`の完全統合は**縮小採用**(Opus M-7が許容した縮小案): KP 3複製の本体(primary→circuit判定→ENGLISH_LOCK→fallback_attempts_log合算)は残し、**待機・STOP・resume・slotだけを`BlockRun.step`に共通化**(strictの`tts_block`引数)。3 call siteの出力dictは待機以外同一(goldenで確認)。完全統合は`attach_kp_vote_check`/`primary_instruction_type`ラベル差の吸収で3複製の出力差を壊すリスクが待機欠落リスクを上回るため見送る | M-7 |
| I-6 | `BlockProgress`は**segment単位ファイル**(`<level_dir>/audit/tts_block_progress/<segment_id>.json`、tmp+os.replace)。並列process間のread-modify-write競合を避ける。標準layoutでない(単体test)ときはin-memory | Opus O-2 |
| I-7 | 古い`IN_PROGRESS`(更新から6時間超)は新規サイクル扱い(落ちたまま放置された旧attemptを消費済みと誤認して③1回だけで終わらないため)。verified済みattemptを含むstateも新規サイクル | 安全側の自己判断(新仕様ではなく実装上の保護) |
| I-8 | LLM段(`run_local_rewrite_recovery`)の例外は`HUMAN_REVIEW_LOCKED_LR_EXCEPTION`として終端HRQ化するが、**STOP例外・LR block内の例外・設定不備(`init_logger`/`[STOP]`)は握らず伝播**(M-11) | M-4/M-11 |

## 1. Opus必須修正 M-1〜M-11 の反映

| ID | 指摘 | 反映(設計) | 実装箇所 |
|---|---|---|---|
| M-1 | scope内でpolicy解決不能はfail-closed。`current_scope()`の契約を「判定に使う唯一の読取関数」へ | `block_policy_for`が`BlockPolicyError`を送出(英語leafでsegment_id=None/未知role)。shellは表上の明示行`SHELL_EN`(`SHELL_EN_ID_RE`、suffix付き可)。`er109.current_scope()`のdocstringを更新。8 leaf×X/Y/Z production moduleのcall siteがscope内であることを静的test(`test_static_callsites_in_scope`) | `er127`:`block_policy_for`,`SHELL_EN_ID_RE`、`er109_xz_scope_01.py`(docstring) |
| M-2 | BlockProgressのkeyに(segment_id, 元原稿sha, Style/Voice/backend/profile/policy指紋)。書換え本文そのものを保存。再生成/resume判別はZ ctx信号流用 | `BlockProgress.key`=sha(seg,text_sha,fingerprint_sha)。`lr.text`に書換え本文を保存しresume時にLR LLMを再実行しない。新規サイクル条件=key不一致/DONE/Lockの`REGENERATE_APPROVED`(`consuming_regenerate_approval`と同じ根拠)/古いIN_PROGRESS/verified済み。`--only-*`だけでは新規サイクルにしない | `er127.BlockProgress`,`lr_recover`(resume分岐) |
| M-3 | (a)`lr_recover`入口で`out_path in _ACTIVE_GUARDED_OUT_PATHS`をassert (b)record_outcomeが数えるTTS数=実TTS呼出数 (c)LR blockの元Style+元resolver flag統一(hint二重付与回避) | (a)`LocalRewriteContractError`。(b)resume時の消費済みattemptは`stub_row`でattempts_logに保持。LR block入口で`attempts_log`をmain+LR連結(`merge_logs`)し、testで`len(attempts_log)==fake TTS呼出数`を全シナリオで固定。(c)LR blockへは**呼出元の元`style_prefix_override`+元`enable_pronunciation_resolver`**を渡す(hint付与済み`style_prefix_override`+resolver=Trueの組合せを作らない) | `er127.lr_recover`、各leafの`block_call` |
| M-4 | 終端NG1件=HRQ1行。LR全非RESOLVED結果と減速後終端NGを網羅。③が技術STOPならLR/HRに入れない | `register_terminal_hr`(重複は既存`is_duplicate_queue_entry`で抑止)。LR不可/LR block最終NG/LR例外/減速後終端NGで呼ぶ。技術STOP(`TECHNICAL_STOP_STATES`)は登録しない=既存の再開可能STOP維持 | `er127.register_terminal_hr`,`lr_recover`、L3/L4 |
| M-5 | 採用attemptの`style_prefix`(実送信文字列)/`instruction_type`/`fallback_used`/`local_rewrite_recovery`をtop-levelに正規化。leaf matrixの結果をGateへ通して期待違反を固定 | L1/L2の③OK結果は`style_prefix`=実際に送ったminimal文字列、`instruction_type="minimal_fallback"`。L3は`fallback_used=True`。LR採用は`local_rewrite_recovery`。`test_gate_contract`が`m3_assembly_gate`/`y_style_gate`に通し`ADV_MINIMAL_FALLBACK`/`ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED`/`STD_FALLBACK_USED_OR_UNKNOWN`/`LOCAL_REWRITE_RECOVERY`を固定。**Gate規則は変更しない**(J-1は別提案) | 各leaf、`er127_tts_block_policy_01_test_01.py` |
| M-6 | 案A採用条件(a)〜(g) | (a)`post_hook`は引数(既定None)。scope外L4・Z Adv `generate_with_a2_slowdown_outer_loop`(K-07)は温存 (b)attempt内順序 TTS→ASR→PASSなら`*_original.wav`退避→減速→減速後ASR。attempt音声は減速前後を別route名で保存 (c)期待text=attemptの送信文、Lock/HRQ`lock_canonical_text`=BlockCtxの元原稿 (d)`_post_slowdown_unified_judge`のslotをブロック通算slot (e)LRへ渡す転写はNG原因転写(減速後NGなら減速後転写)、`ng_source`記録 (f)採用結果top-levelに`slowdown_applied`/`original_path`/`slowdown_info`/`post_slowdown_*`/再計算sha256/比例補正trim_info (g)chunkはchunkごと独立1ブロック | n3_tts、crosslevel、repro01(strict) |
| M-7 | Master Audio Store manifestの更新消失(180秒待機+並列で顕在化) | `get_or_generate`の保存直前にmanifestを**再読込してmerge**+`_save_manifest`をtmp+os.replace。待機はstrict内`step(3)`=ENGLISH_LOCK段のTTS直前のみ(circuit-open判定後・Store key B hit時はそもそも到達しない) | `er006_master_audio_store_01.py` |
| M-8 | evidence注入はdriver側monkeypatchのみ。Production moduleへhook/env追加禁止 | 本委任はProductionにhook/envを**追加していない**(`RUNTIME`のclock/sleepはtestがmonkeypatchする属性のみで、env参照なし)。`injected_override_count`のordinal別記録は委任_03のdriver側 | — |
| M-9 | T-Yの「STYLE_PROFILE=default不変」assertを「呼出元が解決したprofileを透過」testへ置換。BlockProgress指紋にprofile | `fingerprint`に`style_prefix_override`のsha(=解決済みprofileのStyle)を含める。test: default/fx_20261017の両Styleで①②が呼出元Styleのまま、③はFallback、kp系はprimary_fnを呼出元から受領 | 各leaf、test |
| M-10 | L1の③がAoedeになる設計欠陥(重大) | L1(`generate_charon_english`)の③は`_run_a2_minimal_fallback_attempt`を**呼ばず**、自関数内minimal分岐(既存F-Tech分岐と同じCharon/`SAFETY_MARGIN`/`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`or`MINIMAL_INSTRUCTION_PREFIX`+発音hint)をordinal 3で使い、judgeに`force_secondary=True`。L2は`p9a.VOICE_NAME`で一致するため自関数内の既存minimal分岐(`generate_english_component_minimal_instruction`)を③で使う。T-STYのVoice一致testはL1を含む | voice01、news_tail_fix |
| M-11 | cooldown中STOPは専用例外型・runner最上位まで伝播。STOPPED結果保存なし。I-3明確化 | `TtsBlockStopError(BaseException)`(`except Exception`で握られない)。registered stop_checkが投げる例外(Z=`FamilyZStopSentinel`等)もそのまま伝播(Z ctxの既存挙動維持)。runner単位のtest(`_generate_or_reuse`+`guard_generate`経由でrecord_outcome未発火・Lock未更新)。I-3: 技術的再試行を使い切ったattemptもordinalを1つ消費し「②NG」として③前の待機対象 | `er127`,test |

## 2. Opus推奨 R-1〜R-7 の採否

| ID | 採否 | 理由/実施 |
|---|---|---|
| R-1 | 採用 | legacy方式(`attempt_hook=None`)のZ Adv外側ループ: `generate_voice_body_wide_margin`のscope内分岐は`step(通算ordinal)`で判定(局所attempt番号ではなく`max_attempts`=残予算でも③前に180秒) |
| R-2 | 採用 | `FamilyAUnchangedTest`はcommit後は常にPASSで保護にならないため、golden(`er127_golden_01.json`、変更前コードで生成)を証拠とする。変更した全leafのscope外呼出(新kwarg無し)+A runner `generate_a2_segments`の1経路を含める |
| R-3 | 採用 | 最終報告の星取表に「表外・現行維持(SHELL_EN 3行)」を明示 |
| R-4 | 採用 | `IMPLEMENTATION_01.md`にTrial/tool(er113/er114/er118/er019_clobber_restore/validation_inheritance/er121_e1)がscope内で新flowになることを記録。scopeを使う既存testがleafを実sleepで通らないよう確認(`er127.RUNTIME`のclock/sleepをtestで置換できる。Productionにenv迂回口なし) |
| R-5 | 委任_03で任意 | kill→resume実走(LR block内)は費用約数円。委任_03の判断 |
| R-6 | 採用 | clip単価guard見積り更新(最大6TTS+LR LLM)。Z`E2E_TTS_CLIP_EST_JPY`/Y guard見積りをPhase 2で確認・更新(未更新なら`IMPLEMENTATION_01.md`に差分を明記) |
| R-7 | 委任_03報告 | Adv ③採用がGate対象になることによるHR待ち増の数値化はevidence後 |

## 3. ROW_MAPPING修正
- Y-S-06「y_voice_1 Algieba」→「y_voice_1 Puck」(Opus e。`er121_family_y_audio_01.py:13`の2026-10-26 Voice表)。`ROW_MAPPING_01.md/.json`のcosmetic修正はFable判断で次版に反映(本委任では`ROW_MAPPING_01.md`のY-S-06行のみ直接修正)。

## 4. 変更後の呼出フロー(確定)
```
leaf入口: blk = er127.open_block(leaf, out_path, text, ctx=tts_block, fingerprint=...)   # None=legacy
loop型:   for n in 1..3: s = blk.step(n); if s.skip: stub; continue
              TTS(style = Fallback if s.style_mode=="FALLBACK" else role Style) -> ASR(force_secondary=③のみ) -> blk.done(n, verified)
stage型:  strict(2, tts_block=blk, offset=0) -> [③: blk.step(3)が待機] strict/minimal(1, tts_block=blk, offset=2) -> done
終端:     LRあり部位: er127.lr_recover(blk, block_call=(rewritten, BlockCtx(depth=1,...))->同じleafを再帰呼出, merge=leaf固有)
          非RESOLVED: register_terminal_hr(終端1行) -> 従来のSTOPPED/ASR_VALIDATION_UNCERTAIN -> guardがLock化
```
