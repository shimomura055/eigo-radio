# COMMON_CORE_01 — X/Y/Z共用のTTS生成・Retry・Fallback・Local Rewrite・HR関数(正本)

管理ID: TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01X / 2026-10-26 / read-only(API 0・JPY0・コード/SSOT変更0)
対象HEAD: `764901e3a`(作業ツリー読取、未コミット差分は本調査の対象外)。
ユーザー原文: `docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_USER.md`
構造化版: `common_core_01.json`。Family X固有の部位表は `FAMILY_X_01.md`。
表記: セルは事実(ファイル:行)のみ。技術的見解・解釈は末尾「所見(事実ではない)」へ分離。用語は委任文の固定用語(通常TTS上限/Retry/Fallback[F-Style・F-Model・F-Voice・F-Prompt・F-Tech]/LR/HR/STOP/cooldown)に従う。

## 0. 先に読む要約(事実)

1. TTS生成の「leaf関数」は**3系統+KP専用+JA**に分かれ、**LR(Local Rewrite)が働くか否かは「leaf関数の種類」と「呼出側が `enable_connected_speech_equivalence_layer`(以下 `cs`)にTrueを渡すか」の2点だけで決まる**。flag・環境変数・設定dictによる切替は無い。
2. `cs` の値は呼出側が `er020_tts_retry_local_rewrite_01.connected_speech_enabled_for(segment_id)`(L188)から得る。同関数は `resolve_narrative_role()`(L135)が FULL_STORY/COMMENT/PREVIEW/TOPIC_INTRO/IN_ONE_LINE を返したときだけTrue。**`cs`=True がcooldown(600秒)とLRの両方を同時に有効化**する(別々に切れない: voice01.py:156/:304/:323、news_tail_fix.py:149/:300/:325、crosslevel:200/:288/:318)。
3. LRが「無い」ケースは、実コード上 **(a)leaf関数がLR呼出を持たない(JA関数・`generate_voice_body_wide_margin`・`generate_key_phrase_component_verified`)** か **(b)`cs`未指定=既定False(KP解説・shell固定英語)** のいずれか。(a)はFamily側の「引数未指定」では解決しない(別関数)。(b)は呼出側が渡せば有効化できる位置にある。
4. 3回上限は `review_lock.PRODUCTION_MAX_TTS_ATTEMPTS=3`(er011:80)。ただし**Standard系の英語・日本語3関数は「標準2+minimal fallback 1」(er011:102-103)**、Adv系2関数(`generate_charon_english`・`generate_news_narration_wide_margin`)は**同一Styleで3回**(fallbackは技術失敗時のattempt内救済のみ)。
5. LR後再TTSは `max_attempts=1`・`script_version="v1"` の1回。**voice01/news_tail_fix のLR再TTSは `__wrapped__` を `cs`=True のまま呼ぶため、再TTSがNGなら同関数内でLRが再入し得る(再入カウンタ無し)。実LR記録に深さ2の例が3件ある(§6-F1)。この事象は既存 OPEN_ITEMS.md:885 OPEN-376(D-B4: 入れ子4回の実測、D-B5: LR成功でもHR queueに4行残る、D-B6: 監査recordが実音声とずれる)として既知(2026-10-16起票)。**

## 1. Leaf関数一覧(生成・ASR判定・Retry/Fallback/LR/HRの入口)

| # | 関数(ファイル:行) | 使うFamily/部位 | 通常TTS上限 | cooldown(600秒) | Fallback | LR | HR Lock/queue |
|---|---|---|---|---|---|---|---|
| L1 | `voice01.generate_charon_english`(er003_v1_sing01_voice01_generate.py:49、`@guarded_generate("en")`:48) | X Adv topic_intro/preview/comment、shell固定英語、Z/Y Charon英語 | `max_attempts=3`(:50)。同一Style・同一Prompt。attempt内の技術救済は別枠 | `cs`=Trueのとき3回目直前のみ(:156→er020:64) | **F-Tech**: attempt内でTTS例外(技術retry1回後)・発話区間検出失敗時のみ minimal短文Style(`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`、flash-lite時:194)で即再TTS(:179-216)。異常長はfallbackなしで次attempt(:232→`continue`) | `cs`=Trueのときのみ(:304/:323→`_local_rewrite_recovery_for_charon_english`:337)。再TTSは `style_prefix_override` 維持(:363-369) | `@guarded_generate`→`record_outcome`(er011:357)でSTOPPED→HUMAN_REVIEW_REQUIRED。HR queue行はslot3 NG時に統一judgeが書く(§4) |
| L2 | `news_tail_fix.generate_news_narration_wide_margin`(er003_v1_sing01_news_tail_fix.py:63、:62) | X Adv 本文/chunk/in_one_line、Z narrator Adv、Y本文 | `max_attempts=3`(:64)。同一Style | `cs`=Trueで3回目直前(:149) | **F-Tech**: TTS例外/発話区間検出失敗/**異常長**のとき `repro01.generate_english_component_minimal_instruction`(:181)で即再TTS(voice01と異なり異常長もfallback対象:171-178) | `cs`=Trueのとき(:300/:325→:346)。**再TTSは `style_prefix_override` を渡さない**(:370-377)=role Styleが落ちる | 同上 |
| L3 | `crosslevel.generate_english_segment_with_fallback`(er003_v1_crosslevel_audio_02_common.py:95、`@guarded_generate("en")`:94) | X Std topic_intro、(Z Std topic_intro・body経由) | 標準**2**(`standard_attempts`、:162)+minimal fallback**1**(`fallback_budget=max_attempts-標準消費`:188)=総3。`max_attempts=min(…,3)` | 通算3回目直前(`overall_attempt==cooldown_total_budget or max_attempts`:200) | **F-Style**: 3回目=`_run_a2_minimal_fallback_attempt`(:327)=minimal短文Style、`force_secondary=True`(:381)=Primary PASSでもSecondary必須 | `cs`=Trueのとき標準+fallback全滅後(:288/:318→:402)。再TTSは `_run_a2_minimal_fallback_attempt` 直呼び(:425-427、再入なし)=**minimal Styleで1回** | 同上 |
| L4 | `n3_tts.generate_a2_segment_with_slowdown`(er003_v1_n3_01_tts_generate.py:331) | X Std 本文/chunk/in_one_line、Z Std narrator | 通算`PRODUCTION_MAX_TTS_ATTEMPTS=3`を外側ループで共有(:387-399)。内側=L3へ `max_attempts=remaining`・`prior_generations`・`cooldown_total_budget=3` | 通算3回目直前(L3/`strict`が実施) | 内側L3のF-Style。外側ループは**減速後(6%)再検証NG時のみ**残予算内で取り直し(`max_slowdown_attempts=3`) | 内側L3のLRのみ。**減速後再検証NGの最終はLRなし**で `finalize_a2_slowdown_final_ng`(:309)→HR(docstring(iii):317-319) | 内側guarded+`finalize`が `record_outcome`(STOPPED)。HR queueは `_post_slowdown_unified_judge(log_human_review=True)` |
| L5 | `repro01.generate_narration_snippet_verified_strict`(er003_v1_repro01_main_generate.py:198、`@guarded_generate_with_language_arg`:197) | L3/JA Std/KP解説の下位、X KP解説(`generate_key_phrase_explanation_en_verified` er019:1205) | 引数 `max_attempts`(既定3)。同一Style | `cooldown_total_budget`を渡された場合のみ(:336-343)。**単独呼出(KP解説)は渡さず無効** | なし(F-Techなし。TTS非OK=attemptを消費して `continue`:348) | **関数内にLR呼出なし**(上位L3が担う) | `@guarded`で STOPPED→Lock |
| L6 | `repro01.generate_key_phrase_component_verified`(:797、`@guarded_generate("en")`:796) | X/Z KP英語phrase(Master Store経由) | **4回**=Minimal(またはK2 styled)2+ENGLISH_LOCK2(:685-687)。**全体「3回」の唯一の例外**(CURRENT_SPEC.md:2885(1)) | なし(`cooldown_total_budget`未指定) | **F-Style**: 前半2回NG→ENGLISH_LOCK prefixで後半2回(:858)。KP3Vでは Azure/Whisper circuit open時に後半スキップ(:845)。K2経路は `er019_family_x_kp_en_k2_store_01._styled_two_stage`(:55) | **なし**(関数に呼出なし。`cs`引数自体を持たない) | slot4(最終)NGのみHR queue(`slot_offset/total_slots`:861)。`@guarded`→Lock |
| L7 | `voice01.generate_charon_japanese`(voice01.py:446)/`n3_tts.generate_a2_japanese_with_fallback`(n3:693、`@guarded_generate("ja")`:692) | X Std JA(japanese_title/preview/comment/KP日本語意味/point_explanation) | `min(max_attempts,3)`(:487/:732)。標準**2**+minimal fallback**1** | **なし** | **F-Style**: 3回目=JA minimal instruction(`_generate_a2_japanese_minimal_instruction`:621) | **なし**(関数に呼出なし。`cs`引数自体を持たない) | slot3 NGでJA HR queue(`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`、er007_ja_secondary_asr_01.py:39/:733-734/:778)+Lock |
| L8 | `er012_b.generate_voice_body_wide_margin`(er012_b_family_voices_production_01.py:483、`@guarded_generate("en")`:482) | **X未使用**(Z dialogue・Voices等) | `max_attempts`引数(attempt_hook時は通算) | **なし**(`attempt_hook` 指定時のみhook内で実施:528) | F-Tech(`generate_voice_body_minimal_fallback`:451、技術失敗時) | **関数にLR呼出なし**(`cs`既定Trueでも使途はASR判定への転送のみ:579) | `@guarded`→Lock |

### 1-1. 「引数でLRが入る」関数と「関数にLRが無い」関数の判別(Y/Z突合用)
- **引数 `cs` でLR・cooldownが入る**: L1・L2・L3(→L4経由含む)。呼出側が `connected_speech_enabled_for(seg_id)` を渡せば入り、渡さなければ(既定False)入らない。
- **引数以前に関数がLRを持たない**: L5(strict単体)・L6(KP phrase)・L7(JA)・L8(`generate_voice_body_wide_margin`)。Y/ZでLRが「無い」部位がこの関数を呼んでいるなら「別関数」であり引数追加では有効化されない。
- `er020.resolve_narrative_role` は X ID(full_story_part*/comment_*/preview/topic_intro/in_one_line)に加え、Z `full_story_part{n}_c{k}`(L122)、chunk `…_k{j}`(L126)、Y `y_(lead|closing|intro_[1-3]|voice_[1-3])(_k{j})?`(L132)をFULL_STORYへ解決する(L135-176)。KP/shellは `kp\d+_(en|ja)`→KEY_PHRASE(L121)、shell名(welcome等)と `kp1_explanation_en` は**None**(未分類)になりFalse。

## 2. ASR判定とRetry契機(統一judge)

- 判定入口: 英語=`er006_secondary_asr_01.evaluate_attempt_with_cascade`(:586)→`…_detail`(:874)。日本語=`er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade`。両者とも `cascade_enabled=True` が既定(er006:297、JA:28)。
- Primary=OpenAI `gpt-4o-mini-transcribe`(en/ja共通、er006_asr_provider_routing_01.py:31)。Secondary=Azure Speech STT(PhraseList重み2.0 `AZURE_PHRASE_LIST_WEIGHT` er006:75)。Primary PASS→Secondary不要(最終ANDゲートのみ)。Primary NG→原則Secondary **1回**(同一wav+engine+lang+phrase_hashは `SecondaryCache` で再呼出なし)。Primary NG・Secondary PASS=`PASS_WITH_WARNING`(自動採用+事後試聴リスト)。NG_PROTECTED/NG_EXCLUDED(Secondary不呼出)・NG_BOTH・NG_SECONDARY_UNAVAILABLE(PASS不可)は次slotへ(CURRENT_SPEC.md:2873-2875)。
- **`stop_retrying` は cascade有効時は常にFalse**(er006:961/:1238)。よって voice01.py:302/news_tail_fix.py:294/crosslevel `stop_retrying`分岐(`ASR_VALIDATION_UNCERTAIN`返却)は**cascade OFF(rollback)時のみ到達**する残置コード。
- Retryを発動する契機(同一設定での次attempt): (i)統一judgeのNG全種(上記)、(ii)`length_ok`/`final_length_ok`(`unified_judge_mod.final_length_ok`)NG、(iii)`disfluency_qa` NG(`dq18.apply_disfluency_gate`、対象は呼出側が決める: Adv preview/comment/in_one_line、KP phrase/解説)、(iv)`enable_repetition_qa` NG(`repetition_qa.apply_repetition_qa_gate`、本文/chunkのみ。L1にはこの引数が無い)、(v)TTS非OK/発話区間検出失敗/異常長(L1は異常長で次attempt、L2は異常長もF-Tech)。
- **技術エラー再試行(別枠)**: `common._call_tts_with_retry(max_retry=p9a.MAX_TTS_TECHNICAL_RETRY=1, sleep_fn=None)`(er002_common.py:703、p9a:138→p4:61)。1 attemptあたりTTS API最大2回、待機なし(`TTS_API_RETRY_SLEEP_SECONDS=2` は `sleep_fn=None` のため未使用)。attempt番号は進まない。SDK内部のretryは未確認。
- 「品質NG n回+技術エラー別枠m回」表記: 例 L2=「品質NG3回+技術別枠(各attempt最大+1、F-Techでさらに最大+2)」。

## 3. cooldown・Local Rewrite(er020)

- `COOLDOWN_SECONDS=600.0`(er020:57)。`maybe_cooldown_before_attempt(attempt,max_attempts,gate)`(:64)は `gate=True かつ max_attempts>=3 かつ attempt==max_attempts` のときだけ実sleep。実測: 600.003秒(word_gacha b1b part3)・600.004秒(part2_hr_evidence_01__run_r2 b1b comment_4)。LR再TTS(`max_attempts=1`)では発動しない。ユーザー決定: 2026-09-26(DECISION_LOG.md:9711付近「(B)10分cool-down」)。X runnerのcooldownはSTOP sentinel確認なしの単一sleep(Z dialogue ctx経路のみ分割sleep: EXISTING_SPEC_CHECK_01.md:63)。
- `run_local_rewrite_recovery`(er020:739): ①`identify_ng_span`(:206)=canonical vs **最終attemptのPrimary転写**の最初の語差分(複合語分かち書き差は除外:216-222)。差分なし→`HUMAN_REVIEW_LOCKED_NO_NG_SPAN` ②Luna(`gpt-5.6-luna`)が局所書換え候補5件(`N_NEW_CANDIDATES_DEFAULT`:397)③7 Gate QA(意味保持/role/Fact非矛盾/前後文脈/Natural English/局所性/非全文)+全文性(`diagnose_candidate_full_segment`:334、長さ比0.7-1.5・原文被覆0.6以上・数値保持・span整合)+In One Line文数不変(`8_sentence_count_unchanged`:661、Family Xスコープのみ)④全PASS候補のうち `unchanged_ratio` 最大を採用(:717)⑤`retts_fn(書換え後文)` 1回。status=RESOLVED_BY_LOCAL_REWRITE/…_NO_NG_SPAN/…_NO_CANDIDATE_PASSED_QA/…_RETTS_FAILED。LR記録は `er011_output/local_rewrite_recovery/<theme>/<level>/local_rewrite_recovery_<seg>.json` と `er011_output/attempt_history.jsonl`(action=LOCAL_REWRITE_RECOVERY)。
- **発動条件(2026-10-19ユーザー決定)**: `TTS初回→Primary/Secondary承認済み検証→NGなら最大2回のTTS再生成→なおNGならRewrite`(原文 `docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md` §3:「両ASRが同じ箇所の誤読に合意すること」を**削除**、`APPROVED_FOR_PRODUCTION`)。er020:750-757 docstringがこれを明記し「旧条件はコードに実装されたことが無い」と記録。コード上の発動条件は「呼出元が通算TTS試行を使い切ってなお不合格」+ `cs`=True + 5 role。**`両エンジン合意` 名残のGrep: er020のdocstringのみ(実行コード0)。er078:838の同語は `force_secondary` の別意味**。
- LR後の正解原稿=書換え後文(`resolve_expected_text_after_local_rewrite` er020:815、OPEN-283修正、2026-10-19)。HR Lockのkeyとhuman承認は**元の原稿のまま**(assemble.py:101-104、er006:`lock_canonical_text`併記)。
- 再TTS後の検査: 統一judge(`script_version="v1"`→PASSでも `LR_REWRITTEN` 警告付与、er078:559)、`m1_anchor_text`=元原稿(OF-179)、disfluency/repetition QAは元呼出と同じ引数で再実施。L3系のみ `force_secondary=True`。

## 4. HR Lock・HR queue・STOP・resume(er011 / er006 / er007)

- **Lock**(`<level_out_dir>/audit/review_lock_state.json`、er011:155-157): `guarded_generate`(:673)が生成前に `check_before_generation`(:299)、生成後に `record_outcome`(:357)。`status=="OK"`かつ累積上限内→RESOLVED。それ以外(STOPPED/ASR_VALIDATION_UNCERTAIN/累積超過)→**HUMAN_REVIEW_REQUIRED**。HUMAN_REVIEW_REQUIRED・HUMAN_APPROVED中は**同一canonical_textのTTS/ASRを0 API callでブロック**(`_blocked_result`:504→status=`HUMAN_REVIEW_LOCKED`)。本文(canonical_text sha256)が変わればLockは無効(新版扱い)。RESOLVEDはブロックしない(A2再取り直しのため、`check_before_generation` 末尾コメント er011:299-356内)。
- **累積budget guard**: `MAX_CUMULATIVE_TTS_ATTEMPTS=15`/`MAX_CUMULATIVE_ASR_CALLS=60`(er011:68-69)を `record_outcome` が同一segment・同一文面の複数call間で集計(関数内の再帰LRは見ない)。
- **解除**: `approve_regenerate(out_path,text,approved_by)`(:474)=REGENERATE_APPROVED(次の1回だけ通常生成可)。人間承認=`asm.record_human_approval`(assemble.py:96、`<out_dir>/audit/human_approved_segments.json`、canonical sha一致のみ有効)。承認は共有Audio Validation Gate(`_segment_gate_status` assemble.py:116)の `ASR_VALIDATION_UNCERTAIN/HUMAN_REVIEW_LOCKED/STOPPED` にだけ効く。chunk親の `CHUNKS_NOT_ALL_VALIDATED` は承認で迂回不可(er117:53)。
- **HR queue**(表示用append-only): 英語=`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(er006:481、書込`_log_human_review`:484)、日本語=`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`(er007_ja:39)。書込条件=統一judgeが**そのattemptが最終slot(`is_last_slot`)かつNG**で `human_review_required=True` にしたとき(er006:1294-1296、`build_attempt_ctx` er078_asr_unified_attempt_ctx_01.py:25)。重複は `is_duplicate_queue_entry` で抑止(記録は attempt_history に残す)。**この書込はLR呼出より前**(slot3判定時点)。
- **STOP**: ①`STOP`/`STOP_ALL`/`*STOP_NOTICE*`/`RESTART_STORM_LOCK.json`/`RUN_LOCK.json` は `tools/stop_scope_check_01.py`(L35, L198-217)が判定する外部機構。**X runner(er019)には RUN_LOCK/RESTART_STORM の実装が無い**(Grep: 実装ファイルは er026(Z)・er062・er077・er119・er121(Y)のみ)。②X runnerのexit 3は上流(KP/Part1/Part2/budget/backend)失敗時で、**segmentのASR NG自体ではrunnerは停止しない**(NGはresults JSONに残り、Assemble前Gateが BLOCK)。③例外=shell固定英語が非OKの場合 `SharedNarrationBlockedError`(er019:1232/1255)をaudit保存後に送出。
- **resume/regeneration**: `_generate_or_reuse`(er019:1076)は前回OKかつcanonical_text一致・style_version一致・`_reuse_guard_blocks` 通過のときだけ再利用。それ以外は再生成だが、Lockが残っていれば `guarded_generate` が0 API callで返す(承認/`approve_regenerate`まで)。Std chunkは `drop_cached_std_chunks_without_slowdown`・Adv/Std共通で `drop_stale_chunk_entries`・`reconcile_saved_plan`(再計画禁止)。

## 5. 入口引数で挙動が変わる点(まとめ)

| 引数/条件 | 効果 | 既定 | 渡す側 |
|---|---|---|---|
| `enable_connected_speech_equivalence_layer` (`cs`) | cooldown+LR+CS Equivalence層(判定)を同時にON | False(L1/L2/L3/L4/L5) | X/Y/Z runnerが `connected_speech_enabled_for(id)` を渡す(KP解説・shell・JA・KP phraseは渡さない/関数が持たない) |
| `max_attempts` | 通常TTS上限(3関数は`min(…,3)`でクランプ) | 3 | 6/10を渡しても3に固定(er011/CURRENT_SPEC.md:1857 FINAL-26) |
| `standard_attempts` | L3の標準回数 | 2 | L4が`min(2,remaining)`を渡す |
| `prior_generations`/`cooldown_total_budget` | 外側ループとの通算(cooldown位置の通算化) | 0/None | L4・`generate_with_a2_slowdown_outer_loop`(n3:434) |
| `style_prefix_override` | 通常attemptのStyle。**LR再TTS・F-Styleでは維持されない経路がある**(L2 LR再TTS=脱落、L3 LR再TTS=minimal、L1 LR再TTS=維持) | None | role別 |
| `enable_repetition_qa`/`disfluency_qa` | 追加の独立QA(NGなら通常Retry) | False | 本文/preview等のみ |
| `vote_pass_required` | KP phrase 3-ASR多数決 | False | KP phrase |
| `attempt_hook`(L8のみ) | Z dialogue ctx方式(attempt番号→Style、cooldown、state永続化) | None | Z dialogueのみ |
| `TTS_EXECUTION_MODE` | STANDARD/BATCH(再試行回数は不変) | BATCH(未設定時) | 環境変数 |

## 6. 発見事項(共通核。分類はユーザー原文§7: A承認済み差異/B仕様との不一致/C根拠不明)

| ID | 内容(事実) | 分類 | 重要度 |
|---|---|---|---|
| CC-F1 | voice01/news_tail_fix のLR再TTSは `__wrapped__(…, cs=True, max_attempts=1)` を呼び(voice01:363-369、news_tail_fix:370-377)、再TTSが不合格なら同関数末尾の `if enable_connected_speech_equivalence_layer:`(voice01:323、news_tail_fix:325)で**LRが再入**する。再入を止めるカウンタ/引数は無い。実LR記録に `retts_result.local_rewrite_recovery` を持つ深さ2の例が3件: `er011_output/local_rewrite_recovery/hormuz__run_03_baseline/b1b/…comment_4.json`・`meta__run_regen_01/b1b/…in_one_line.json`・`run_e2e_01/b1b/…full_story_part1_c18.json`。一方、ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md:28 は「`lr_used==0`=明示カウンタ無し、LR再TTSがNGなら`None`→HR(2回目LRなし)」、CURRENT_SPEC.md:2886 は「LR後v1=標準Prompt・1 attempt」と記録 | **B・既知=OPEN-376(D-B4)**(2026-10-16起票。OPEN_ITEMS.md:885は『USER_DECISION_REQUIRED(仕様判断)』ラベルだが、PRINCIPLE_NONCOMPLIANCE_ANALYSIS_01.md:103 は『境界。是正が意味変更か否かをFableが判定してから』、REGISTER #122(L289)は不具合に当たる候補に列挙)。記述と実装の不一致。ユーザー2026-10-15 §6「Rewriteの発火・再TTS回数を正しく計数し、累積上限を守る」(`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`:164)とも関係) | 中(1 LRあたりLuna2呼出+TTS/ASR。深さは理論上非有界。実例3件=いずれも2026-09-28〜10-12でRESOLVED) |
| CC-F2 | news_tail_fix のLR再TTSは role Style(`style_prefix_override`)を渡さない(:370-377)。Std(L3)のLR再TTSはminimal Style。voice01のLR再TTSはStyle維持(:363-369)。既知: OPEN_ITEMS.md:815 OPEN-312(Deferred、M3 StyleGateがBLOCKで代替)、:777 OPEN-274 | **B**(既知OPEN。「全roleにStyleを適用」との不一致) | 中(品質: LR発火時のみ。Style Gate BLOCK→人間承認が要る=Delivery) |
| CC-F3 | LRのNG span特定は**最終attemptのPrimary転写とcanonicalの語差分**のみ(er020:206)。ASR自体はPASSでdisfluency/repetition/長さQAでNGになった場合、差分が無く `HUMAN_REVIEW_LOCKED_NO_NG_SPAN`→LR不発→STOPPED→HR。実例(2026-10-26、X Adv comment_4): 3attempt全て `EXACT_MATCH` かつ disfluency flagged(`now. Now,`)、cooldown600.004秒後LR不発、STOPPED(`er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r2/b1b/audit/tts_generation_results.json`)。非ASR起因NGでのLR要否は仕様記録なし。`NO_NG_SPAN` を扱うOPEN: 無し(Grep) | **C**(承認根拠も不採用根拠も記録なし) | 中(Quality: 追加HR / Delivery: 人手待ち / 単価: cooldown10分+TTS3回が無駄になる) |
| CC-F4 | HR queue行は最終slot(slot3)NG判定時に**LR前**に書かれる(er006:1294-1296)。LRが成功してもqueueに残る。実例: `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl` に word_gacha b1b full_story_part3(最終OK、LR RESOLVED)の行が2件(2026-10-24 18:26:06/18:27:21) | **既知=OPEN-376(D-B5)**(『LRで解決したsegmentでもHR queueに4行残る』。queue=表示用で、LR成功時の扱いの承認記録は無い=C相当) | 低-中(誤解を招く。Lockは正しくRESOLVED) |
| CC-F5 | `stop_retrying` 分岐(voice01:302、news_tail_fix:294、crosslevel、L7の:559/:611)は cascade有効時は到達不能(常にFalse: er006:961/1238)。cascade OFF(rollback)専用の残置コード | 残置(実害なし) | 低 |
| CC-F6 | 技術失敗時fallback: L1(voice01)は異常長を次attemptへ(:232)、L2(news_tail_fix)は異常長もminimal fallback(:171-178)。同じ「異常長」で処理が異なる。仕様記録: 未確認(Grepなし) | **C** | 低 |
| CC-F7 | 3関数(L3/L7/`generate_charon_japanese`)だけが「標準2+minimal1」、Adv 2関数(L1/L2)は「同一Style3回」。CURRENT_SPEC.md:1857 が3関数を名指しで列挙(2026-09-04ユーザー正式決定)。2026-10-15 §2「各TTS再生成では原稿・Prompt・モデル・Voice・速度を維持」(同ファイル:61)と文面は食い違うが、2026-10-21ユーザー決定「Fallback機構は現行仕様を維持(Minimal/ENGLISH_LOCK廃止せず、Prompt・Style・発動条件・再試行回数は変更しない、X/Z共通)」(`docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_FALLBACK-APPROVAL-FINAL-ASSEMBLY_USER.md`:9-15)が後日付で明示 | **A** | — |

## 7. 所見(事実ではない)

1. LRの有効化単位が「`cs` 1本」であるため、cooldownだけ/LRだけを部位ごとに切れない。Y/Zの設計判断(例: Z dialogueへcooldownのみ追加)は別関数 `attempt_hook` を新設して実現しており、共通核側の設計はこの結合を前提にしている。
2. CC-F1は、ユーザーが2026-10-19決定で定義した「Rewriteの回数」が仕様文では暗黙に「1回」と読めるのに、コードは非有界である点が本質。修正するなら再入禁止引数(例: LR再TTSでのみ `cs`のLR部分だけを切る)が最小だが、これは受理面の変更ではなく**既存仕様との整合是正**(PM_GOVERNANCE 11-8)に当たる可能性が高い。本調査では修正しない。
3. CC-F3は「LRは書換えで解消できるNGにだけ働く」設計意図とも読めるが、そうだとしても非ASR起因NGが「cooldown10分→LR不発→HR」に終わる点は単価・Deliveryに効く。承認記録が無い以上、設計意図かどうかは断定できない(判断候補はRESULT_PACKET参照)。
4. X/Y/Zでの「LR有無の違い」の大半は、**呼出関数の違い(L1-L3 vs L5-L8)**で説明でき、Family固有の承認よりも**実装経路の履歴**に依存している可能性がある(Zの `J-1` は「新設せず」とZ設計が明示した別ケース)。

## 8. 参照文書(根拠)
- `CURRENT_SPEC.md`: 1857(3回上限・2+1)、2176(2026-09-26 cooldown+LR+5role)、2873-2886(統一flow・Section例外・LR節)、2957(chunk: 上限不変)
- `DECISION_LOG.md`: 9711-9728(TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01)、21944(2026-10-19 ②③)
- `docs/pm/USER_DECISION_REGISTER_01.md`: #119(L286)、#5/#6/#8/#13(L22-31)
- `OPEN_ITEMS.md`: OPEN-274(L777)、OPEN-283(L786)、OPEN-290(L793)、OPEN-312(L815)、OPEN-371(L880)、OPEN-422(L934)、OPEN-432(L944)
- `docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`(ユーザー原文§2/§5/§6: L17-255内、L49・L147-148・L155-165)
- `docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md`(§3-§4)
- `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md`、`ITEMS23_WIRING_ASSURANCE_01.md`
- `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/EXISTING_SPEC_CHECK_01.md`(§2-§3: Z dialogue LR未配線の事実)、`DESIGN_02.md`(J-1:61)
- `docs/research/FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01/FALLBACK_INVESTIGATION_01.md`
- 変更履歴: `git log --oneline --since=2026-10-15 -- er020… er003_v1_n3_01_tts_generate.py er019…`(主要: 4413a532b[10-19 LR条件削除+OPEN-283]、5737b77f2[A3 length]、4019b5fe1/cc01cd8f3[統一judge]、7ca0df0ad/d00f41c8b/3fc684c37[Chunk Std]、7768af1d2[Z ctx])
