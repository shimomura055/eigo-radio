# CURRENT_STATE_01 — ZセリフLR正式採用: 現状調査(委任_01、read-only・API 0・コード変更0)

管理ID: FZ-DIALOGUE-LR-ADOPTION-01 / 作成: 2026-10-29 / 原文: `docs/pm/delegation_log/2026-10-29_FZ-DIALOGUE-LR-ADOPTION-01_USER.md`
行番号は2026-10-29時点のworking tree(HEAD=047eb72f9)。

## 0. 結論(要点)
1. 共通LR機構(`er127.lr_recover` + `er020.run_local_rewrite_recovery`)は再利用可能。ただしZセリフ(`generate_dialogue_ctx`)は**統一ブロック(`er127.BlockRun`)の外**にあり(`er012_b:484-485` の `skip_when=attempt_hook is not None`)、試行状態は `er122`(`dialogue_ctx_attempt_state.json`)が単独で持つ。LR配線は「er122状態機械を6回+LR段に拡張」+「`lr_recover`が要求するblk契約をer122側のadapterで満たす」形になる。
2. Zセリフの上限3は**3箇所の独立定数**: `er127:114`(Profile)、`er122:32`(MAX_TOTAL_ATTEMPTS=3)、`er003_n3:516`(外側ループ total_budget=`PRODUCTION_MAX_TTS_ATTEMPTS`=3)。1箇所だけ変えると不整合になる。
3. `lr_recover` は `out_path in review_lock._ACTIVE_GUARDED_OUT_PATHS`(外側guard実行中)を要求する(`er127:770`)が、Zセリフは**leaf単位**でguardされ(`er012_b:483`)、`generate_dialogue_ctx` 自体はguard外。6回+LRを通す外側guardが必要。
4. **藪の中c6の実データ(最重要)**: (a) #3のNGは「反復検査(repetition_qa)flagged」でASR転写は原稿と一致 → 最終転写だけでは `identify_ng_span` が `found:false`(LR適用不可)。ASR差分を持つのは#1(`an`→`and`)と#2減速後(`sank for ever`→`sink forever`)。(b) #2減速後のNG span `sank for ever` は**確定済みVocab(Adv confirmed_selection items[3])**そのもの、`on soft feet` は確定KP(items[1])で、どちらもc6本文内 → LRが触ると `LR_OVERLAPS_CONFIRMED_CONTENT`(T1/T2)で組立前Gateに止まる。LR入力の選び方と確定内容保護の事前検査が設計の核心。
5. 既存の表示・採用台帳・Gate(er129/er130/er132/er133)は**Z形LR(`audio_text_deviation`)を既に扱える**。c6相当の引用符付き本文でも `compute_ops`/`locate_op` が一意位置特定できることをoffline probeで確認(§7)。追加が必要なのは `final_adoption`(depth=1)の記録と、er130 `dialogue_legacy_fallback_direct` の ordinal 比較のみ。

## 1. 共通LR機構(X/Y/Z英語本文)
| 項目 | 実装 | 場所 |
|---|---|---|
| Profile表(9 policy) | `PROFILES`。EN_LR_STD/ADV=`Profile(name,3,(3,),"FALLBACK_MINIMAL_EN",True,6,6,2)` | `er127_tts_block_policy_01.py:108-117` |
| 単一読取関数 | `unified_flow_active()`=`er109.current_scope() in {X,Y,Z}`。env/引数で変えられない | `er127:129-134` |
| policy解決 | `block_policy_for(leaf,segment_id,z_dialogue_policy=)`。L8は `fz_ctx_v1`→Z_DLG_CTX / `legacy`→Z_DLG_LEGACY | `er127:144-170` |
| 180秒の唯一定義 | `COOLDOWN_SECONDS=180.0`、`cooldown_core`(実時間・5秒刻みSTOP確認) | `er127:31,183` |
| 1ブロック進行 | `BlockRun.step/done/finish`(STOP確認→③前180秒→n_started永続化) | `er127:484-` |
| LR共通ラッパ | `lr_recover(blk,text,out_path,last_asr_text,block_call,merge,last_attempt)`。再入禁止(depth>=1で`LocalRewriteReentryError`)、外側guard assert、resume時は保存LR本文でLR LLM再実行なし、非RESOLVEDは`register_terminal_hr` | `er127:757-842` |
| LRコア | `run_local_rewrite_recovery(segment_id,canonical_text,last_asr_text,retts_fn,context_before/after,client)`: NG span特定→Luna候補5件→局所QA→7 Gate+文数→最良1件→`retts_fn`→採否 | `er020:757-838` |
| NG span | `identify_ng_span(canonical,asr)`。差分無しは `HUMAN_REVIEW_LOCKED_NO_NG_SPAN`(LR不可) | `er020:224-`、`:775-782` |
| 7 Gate | 1意味/2役割/3事実無矛盾/4文脈接続/5自然英語(LLM QA)+6局所性+7非全面書換え(機械)。全文性`diagnose_candidate_full_segment`、span整合、数字保持 | `er020:352-402,547-573,695-733` |
| roleラベル | c-clipは`FULL_STORY`に解決 | `er020:145-160`(`_FAMILY_Z_STORY_CLIP_PATTERN`:132) |
| LR後の期待text | `resolve_expected_text_after_local_rewrite`(Z形`audio_text_deviation`も2次出典) | `er020:904-936` |
| 確定KP重なり(記録のみ) | `_note_confirmed_kp_overlap`→`er128.note_lr_fired`(採否は変えない) | `er020:886-899`、`er128:1280` |
| 参照実装(Std英語) | `_generate_english_segment_unified`: ①②strict→`blk.step(3)`で180秒→③minimal→`lr_recover`(`_block_call`=同leafの`__wrapped__`をLR ctxで呼ぶ)。LR可否は`blk.lr_allowed`、技術STOPはLR/HRへ入れない | `er003_v1_crosslevel_audio_02_common.py:337-518` |
| 表示(UD-1)/採用台帳 | `er129._lr_info`(X/Y=`local_rewrite_recovery`、Z=`audio_text_deviation`)、`build_lr_ledger`、`check_confirmed_overlap`(T1語句/T2文/T3数字・固有名詞) | `er129:659-`、`:935`、`:327-390` |
| 表示overlay/三者一致Gate | `er132.assert_text_parity`、`z_assemble_gate` | `er132:288,369` |
| 採用Take分類・Style照合 | `er130._allowed_fallback_slots`(lrありなら{3,6})、`LR_ON_NON_LR_ROLE`、`LR_TAKE_INCONSISTENT`、`dialogue_legacy_fallback_direct` | `er130:182-186,350-351,365,265-278,428` |
| 最終Human報告(赤/濃青) | `er131_final_human_report_01`、`er133_report_marks_01`。Zページは`er063:2498-2650,2781` から呼ぶ | |
| 通算試行の上限 | `MAX_CUMULATIVE_TTS_ATTEMPTS=15`(segment累積のbudget guard) | `er011:68` |

## 2. Zセリフ現行実装
- Profile: `Z_DLG_CTX=Profile("Z_DLG_CTX",3,(3,),"LEGACY_DIALOGUE",False,3,3,1)`(`er127:114`)。`Z_DLG_LEGACY`(`:115`、third_style=SAME・lr=False)。`_self_check`の関係式 `max_tts==total_slots` / `max_waits==len(cooldown_before)*(2 if lr else 1)`(`:872-878`)は、lr=True・6・6・2 でも成立(1×2=2)。
- 試行状態機械(`er122_fz_ctx_policy_01.py`): `MAX_TOTAL_ATTEMPTS=3`(:32)、`CTX_ATTEMPTS=2`(:33)。`DialogueAttemptPolicy`: `_open`(:189、new/resume/adopt_saved_done_ok/terminal_ng/`_restart`)、`remaining()`(:240)、`before_attempt`(:283、n=1,2=ctx、n=3=legacy_fallbackで`_cooldown_before_fallback`:299)、`after_attempt`(:348、rowsに`tts_mode`/`overall_attempt_n`/`style_prefix`)、`_attach_final_adoption`(:390、depth=0固定・ordinal=n)、`finish`(:409、非OK→`TERMINAL_NG`)。永続=`<level>/audit/dialogue_ctx_attempt_state.json`(tmp+os.replace、TTS呼出**前**に`n_started`、`counted`二重計上防止)。docstring `er122:21-22`「Local Rewrite: Z dialogueには未配線」。
- 生成(`er063_family_z_audio_01.py`): `prepare_dialogue_ctx`(:898)→`generate_dialogue_ctx`(:918): ①`check_before_generation`(Lock済ならleafのblock結果を返す、:930-934)→②`provider.style_for`(ctx Style、level単位1 call)→③`DialogueAttemptPolicy`→④Std=`bvoices.generate_voice_body_wide_margin(max_attempts=policy.remaining(), attempt_hook=policy)`(:944-946)、Adv=外側ループ`n3_tts.generate_with_a2_slowdown_outer_loop(..., slowdown_pct=Z_ADV_DIALOGUE_SLOWDOWN_PCT, prior_generations=)`(:955-964、速度=atempo1.06 fast6)→⑤`policy.finish`。`terminal_before_fallback`(:968)。legacy方式は`dialogue()`(:1037-)でL8(`_blk`)経由。
- leaf: `generate_voice_body_wide_margin`(`er012_b:483-`)=`@guarded_generate("en")`+`@with_block("L8",...,z_policy=lambda a:"legacy", skip_when=attempt_hook is not None)`。hook有=blk無し(`:497-522`)、`for attempt in range(1,max_attempts+1)`で`before_attempt`→TTS→ASR(統一judge)→disfluency→repetition QA→`after_attempt`。
- 外側ループ: `er003_n3:503-552`。`total_budget=review_lock.PRODUCTION_MAX_TTS_ATTEMPTS`(:516)、`max_slowdown_attempts=3`、`is_last_slot=(generations_used>=total_budget or attempt>=max_slowdown_attempts)`(:532)、最終周回の減速後NGで`finalize_a2_slowdown_final_ng`(:551、`record_outcome`でLock=HR、:324-343)。`log_human_review=True`の最終slotでHRQ1行。
- Lock: `check_before_generation`(`er011:300`、HUMAN_REVIEW_REQUIRED→blocked/REGENERATE_APPROVED→`consuming_regenerate_approval`)、`record_outcome`(:358、OK→RESOLVED/他→HUMAN_REVIEW_REQUIRED、累積TTS=`cumulative_tts_attempts`)、`approve_regenerate`(:475、「ユーザーの明示的な指示でのみ」)、`guarded_generate`(:674、reentrancy=`_ACTIVE_GUARDED_OUT_PATHS`、内側は記録せずfn直行)。
- stage: `stage_tts`(`er026_family_z_fiction_production_runner_01.py:2597-`)=非OKで`FamilyZTtsClipFailedStop`(:2610、rc=2)。`--only-clips`→`explicit_regenerate`(`er063:906-`)。
- build_entry(`er063:1223`): `local_rewrite_recovery`→`audio_text_deviation`(before/after/diff)、`dialogue_tts`、`final_adoption`を透過コピー。`_handle_local_rewrite`(:1698)は監査記録のみ(2026-10-12決定でer061再検証撤去)。

## 3. 一覧・文書の所在(「Zセリフ従来方式」独立行)
- `CURRENT_SPEC.md:3171` Z_DLG_CTX行(LR「なし(今回追加しない)」・3/1回・「③NG→Lock→TERMINAL_NG→HR/STOP」)、**`:3172` Z_DLG_LEGACY行=独立行(削除対象)**、`:3161`「9 policy」見出し、`:3179`「Zセリフ…(LRなし・計3回。OPEN-528 Deferred(1)=LR新設せず確定)」、`:1652`(Z文脈・感情節「Z dialogueにLocal Rewriteは未配線」)。
- `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/ROW_MAPPING_01.json`(49行・9 policy。`Z-A2-DIALOGUE-LEGACY`/`Z-B1B-DIALOGUE-LEGACY`がZ_DLG_LEGACY、`Z-*-DIALOGUE-CTX`のlr/max_tts/hr_terminalが旧値)/`ROW_MAPPING_01.md:16-17,33-34,77-78,84-85`。`er127_tts_block_policy_01_test_01.py:23,140-166`(MapTests)が読む。
- 過去判断: UDR-TRA-1「Zセリフ用LR新設要否」=2026-10-26「今回LRは追加しない」(`DECISION_LOG.md:22622`、`USER_DECISION_REGISTER_01.md:464`)。**今回2026-10-29のユーザー正式採用がこれを上書き**(OPEN-602、supersede記録が必要)。当時の懸念J-1「LR新設は古典セリフの書換で音声と表示本文が乖離する」(`RESULT_PACKET_FZCW2.md:11`)は、その後のUD-1(LR後英文を最終表示本文へ反映、三者一致Gate、2026-10-28 PRODUCTION_WIRED)で解消済みの前提。
- 8区分との対応: PROFILES 9件から `Z_DLG_LEGACY` を除いた8件=EN_LR_STD / EN_LR_ADV / Z_DLG_CTX / JA_STD / KP_EN / KP_EXPL / SHELL_EN(英語固定案内音声・3回・通常Style) / NO_TTS(固定MP3)。原文§4の8行と1対1。

## 4. 藪の中 Adv `full_story_part3_c6` の現状(`er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/`)
- 本文: `segment_plan_b1b.json` clips[id=full_story_part3_c6]、voice=Puck(takehiro)、91語、text_sha256=`fe82ad9a…f0181`、引用符つき(`"My wife said, 'Take me anywhere.' … 'Kill that man.' "He pushed…`)。TTS入力は`tts_safe_news_en`後も引用符を保持。
- `b1b/audit/dialogue_ctx_attempt_state.json`(clip): cycle=2、status=`TERMINAL_NG`、n_started=3、policy=fz_ctx_v1、ctx_style_sha=`3eb5d8ba…`、cooldown{required_before_n:3, 実測179.941秒}、attempts全3件`counted:true`。#1 ctx NG(14:55:44〜、ASR NG_BOTH `an unseen hand`→`and unseen hand`)、#2 ctx(一次PASS→**減速後再検証 TRUE_CONTENT_MISMATCH**、`I sank for ever`→`I sink forever`+`him, but she fled`、`er011_output/attempt_history.jsonl:20128` run d420bbe8…、14:58:06)、180秒、#3 従来(legacy_fallback、ASR PASS=NORMALIZED_MATCHだが**repetition_qa flagged:true**〔method_d long-lag〕で非verified、15:01:54)。history[0]=旧cycle(本文sha違い・DONE_OK、OPEN-596是正前)。
- `b1b/audit/review_lock_state.json[full_story_part3_c6]`: `HUMAN_REVIEW_REQUIRED`、cumulative_tts_attempts=3、cumulative_asr_calls=3、同text sha。`tts_generation_results.json[full_story_part3_c6]`: status STOPPED、tts_generations_used=3、`dialogue_tts.final_mode=legacy_fallback`。HRページ=`user_test/family_z_in_a_grove_hr_02/`(委任_15)。
- 費用: 本runの累計¥122.02/Cap135(委任_14)。1 attempt≈¥0.35(TTS+ASR、`TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/COST_01.md` §4)、LR1回≈¥0.28。
- **LR入力の可否(offline実測、API 0)**: `identify_ng_span(原稿, ASR転写)` — #1: found(`an`→`and`、窓`on soft feet an unseen hand quietly`) / #2減速後: found(`sank for ever`→`sink forever`) / **#3: found:false**。→「最終attemptの転写のみ」を渡す既存規則(`er003_crosslevel`の`last_ng`)ではc6は `NO_NG_SPAN`=LR不可でHRに戻る。c6をLRに載せるには「ブロック内で最後にASR差分を持つ転写」を使う規則が要る。
- **確定内容との重なり**: Adv `b1b/audit/confirmed_selection.json`(live, cf_942d4e494cc4eeec) items=[kp `cold contempt`, kp `on soft feet`, kp word `medium`, **vocab `sank for ever`**(key `sink for ever`), vocab `constable`]。c6本文に **`on soft feet`(KP)と`sank for ever`(Vocab)の両方が含まれる**。#2減速後のNG spanは確定Vocab自体 → LRで書換え不可(T1)、同じ文はT2(出典文重なり)でも対象。#1のNG span(`An unseen hand quietly drew the dagger from my chest.`の文)は確定項目の出典文ではない。
- 状態移行の論点: 現stateは`TERMINAL_NG`+Lock=`HUMAN_REVIEW_REQUIRED`。`_open()`(`er122:189-`)は TERMINAL_NG+明示信号なし=`terminal_ng:attempts_exhausted`(remaining=0)、明示信号(`--only-clips`/REGENERATE_APPROVED)あり=`_restart`で**cycle新規(n=0からやり直し)**=今回の要求(#1〜#3再実行しない)に反する。正規の再開用に「TERMINAL_NG(n=3,LR未実施)→IN_PROGRESS/LR待ち」へ移す専用の状態移行が必要(WIRING_DESIGN_01 D8)。

## 5. 4者一致(表示本文=TTS入力=ASR正解=実音声)の現状
- 表示=`er132`のoverlay(`level_ledger`→`display_text_of_clip`、`er063:2498-2650`)、TTS入力=Z形は`audio_text_deviation.audio_text_after`、ASR正解=`resolve_expected_text_after_local_rewrite`(`er020:904`)、三者一致Gate=`er132.assert_text_parity`(`:288`、不一致・位置不能・overlay未適用=技術STOP)。実音声はLR後attemptのASR判定(統一judge)で担保。Zは`z_assemble_gate`(`er132:369`)。dialogue clipでも表示unit=`entry.canonical_text`(引用符つき)、`compute_ops`+`locate_op`がOK/BEFOREを返す(§7)。
- 追加が必要な点: (a)`final_adoption`にdepth=1・ordinal=n−3・slot(①'②'③')を記録(`er122._attach_final_adoption:390`は現状depth=0固定=`er130:428`の`LR_TAKE_INCONSISTENT`でBLOCK) (b)`er130.dialogue_legacy_fallback_direct`(`:266-278`)は`take.ordinal == dt.final_attempt_n`を要求=LR block内の⑥(n=6, depth1 ordinal3)で偽になる。

## 6. Dangling Reference候補(旧仕様参照・実装時に解消)
| # | 場所 | 内容 | 対応 |
|---|---|---|---|
| D1 | `er127:114` | Z_DLG_CTX lr=False/3/3/1 | lr=True/6/6/2 |
| D2 | `er122:32,22,243,286,289,341,422` | MAX_TOTAL_ATTEMPTS=3、docstring「LR未配線」、`final_reason`文言「通算…上限3回」 | 6/BLOCK=3へ、文言更新 |
| D3 | `er003_n3:516,532,545` | 外側ループ総予算3固定 | kw追加(既定=現行)でblock予算・slot offset |
| D4 | `er063:893-897,968,950` | 4-Dヘッダ「総3回」、`terminal_before_fallback`の`< MAX_TOTAL_ATTEMPTS` | 6/LR対応 |
| D5 | `er130:182-186`+test `er130_adopted_take_classifier_01_test_01.py:56,132,222,312,321` | Z_DLG_CTXのslot許可・期待値 | lr=Trueで{3,6}(自動)。testの期待値更新 |
| D6 | `er129:510-520`(`_derive_from_logs` dialogue_tts)、`er122:390-407` | depth=0固定のfinal_adoption | depth/ordinal/slot対応 |
| D7 | `CURRENT_SPEC.md:3161,3171,3172,3179,1652` | 9policy表・Z_DLG_LEGACY独立行・「LRなし」記述 | 8区分へ、独立行削除、supersede注記 |
| D8 | `ROW_MAPPING_01.json/.md`、`er127_tts_block_policy_01_test_01.py:23,140-166` | 49行・LRなし・LEGACY行 | ROW_MAPPING_02(正式47行+compat参照)へ、MapTests更新 |
| D9 | `DECISION_LOG.md:22622`、`USER_DECISION_REGISTER_01.md:464`(UDR-TRA-1)、OPEN-528 Deferred(1) | 「LRは追加しない」 | supersede追記(今回のユーザー決定が優先) |
| D10 | `docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/W4_ROLE_COVERAGE_01.md:28`、`HR_ROUTE_PART3_C6_01.md:11`、`PM_GOVERNANCE.md` 30節のHR経路 | 「Z dialogue LR対象外」 | 履歴は消さず追記のみ。30節のHR経路テンプレに「ZセリフはLR対象」を反映 |

維持するもの(撤去しない): `Z_DLG_LEGACY`(`er127:115`)、`policy=legacy`(`er122.resolve_run_policy`)、従来Dialogue Style(`style_prefix_override=None`)=③⑥のFallbackとして現役、`er063:1037-`のlegacy方式。

## 7. offline probe(API 0、c6実本文)
- `compute_ops(before,after)`: 合成after(`An unseen hand`→`A hidden hand`)→`[{'kind':'replace','core_before_text':'An unseen','core_after_text':'A hidden'}]`。`_display_candidates('full_story_part3_c6',{canonical_text...},b1b)`→[`entry.canonical_text`(475字)]、`locate_op`→`OK/BEFORE`(一意)。引用符・入れ子単引用符は位置特定を妨げない。
- Zページの表示unitは`entry.canonical_text`(b1bに`parts.json`なし)。LRの`before`は`tts_safe_news_en`後のTTS入力で、両者の引用符形は一致。`diagnose_candidate_full_segment`(`er020:376`)は「原文に先頭引用符あり」なら候補の先頭引用符を許す。

## 8. 既存test基準線(HEAD=047eb72f9、API 0)
er122_fz_ctx_policy 32 pass / er063_fz_ctx_wiring 24 pass+1 fail / er127_final_adoption_b1 18 pass / er127_tts_block_policy 105 pass(150 subtests) / er130 53 pass / er129 39 pass+1 fail / er132 52 pass+1 fail / er122_fz_ctx_notes 17 pass。
既存失敗3件(本件起因ではない): `er063_fz_ctx_wiring_test_01::test_w11b_non_dialogue_generators_source_unchanged_vs_baseline_commit`、`er129_lr_display_reflection_01_test_01::test_u8_no_production_module_imports_er129`、`er132_lr_overlay_pages_01_test_01::test_public_page_scan_flags_exactly_the_known_publication_mismatches`。実装後は「旧失敗集合と同一」を回帰基準とする。
