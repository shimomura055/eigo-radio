# OPUS_REVIEW_REQUEST_01 — 独立技術レビュー依頼(条件A: 新しい処理フロー設計)

依頼元: Fable(sandwich-pm)経由。管理ID: FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_01(Phase 0)成果物に対する、実装前(Phase 1着手前)の独立レビュー。
根拠: PM_GOVERNANCE 11-3 条件A(Z正式経路のretry/fallback構造に新しい処理フロー[ctx→ctx→cooldown→従来方式]を加える)。条件C(Production採用提案)は、ユーザーが既に`APPROVED_FOR_PRODUCTION`と決定済みのため対象外。配線完了判定時は本レビューを再利用する。
レビュー者の立場: 読取専用・API 0。Production採用の可否は判断しない(ユーザー決定済み)。判断対象は『その決定を、承認済み仕様・既存安全装置を壊さずに実装できる設計か』。

## 0. 前提(ユーザー決定。変更不可)

原文=`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md`。要点: Family Z dialogue(Std/Adv)で、1回目=文脈・感情付きTTS→NGなら即時2回目=同→NGなら10分クールダウン→3回目=従来方式(文脈・感情情報を完全除外)。総試行3回(Fallbackは4回目でない)→NGは既存Local Rewrite→Human Review/STOP。Trial方式の正確な移植(Prompt・感情分類方式・品質基準の変更/追加/緩和なし)。retry/fallback/regeneration/resume/Local Rewrite/HR Lockの全経路で同一仕様。X/Y不変。

## 1. 読むべき資料(優先順)

1. `DESIGN_01.md`(全体設計。特に§C状態機械、§B合成、§D不変保証、§E Trial問題)、`EXISTING_SPEC_CHECK_01.md`(現行経路のファイル:行と差分表)。
2. `SPEC_LEDGER_01.md`、`TEST_PLAN_01.md`、`BUDGET_PLAN_01.md`、`OPEN_TRACKING_01.md`。
3. コード(読取のみ): `er012_b_family_voices_production_01.py:483〜615`(共有ループ)、`er063_family_z_audio_01.py:790〜829,917〜929,1383〜1480`、`er003_v1_n3_01_tts_generate.py:298〜479`(外側ループ)、`er011_human_review_lock_01.py:299〜475,673〜702`、`er020_tts_retry_local_rewrite_01.py:57〜92`、`er118_fz_dialogue_context_tts_trial_01.py`(移植元、`:182〜406`)、`er118_fz_full_episode_trial_01.py`(`gen_case`など)。
4. 過去Opus指摘: `docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/OPUS_REVIEW_01.md`(M-1〜M-8/R-1〜R-9。本設計での引継ぎ=DESIGN_01 §I)。

## 2. 重要論点(これらに重点を置く。各論点について M[必須修正]/R[推奨]/OK[問題なし]で回答)

1. **状態機械の網羅性と再開時の整合**。(a)`n_started`を『TTS呼出前に書く』ことで3回超過が構造的に起きないか。(b)resume時の`carried_log()`により、`record_outcome`の累積(`cumulative_tts_attempts`)と`generate_with_a2_slowdown_outer_loop`の生成数会計(`count_tts_generations_in_result`=attempts_log行数)が実消費と食い違わないか。同一プロセス内の前passと前プロセス分を二重計上しない設計は正しいか。(c)Advで『ASR OK→減速後NG』のattemptを`mark_prev_postprocess_ng()`でNG化する方式は、cooldown判定・n継続・HR Lock最終遷移(`finalize_a2_slowdown_final_ng`)と矛盾しないか。(d)明示再生成(`approve_regenerate`/`--only-clips`/本文変更)とresumeの判別(stateのstatusと一致条件)に穴は無いか。(e)ASR OK確定直後〜`save_checkpoint`前のクラッシュ窓(総3回は超えないが、そのclipはn+1から再生成される)の許容可否。(f)cooldown残り時間を『実時間経過』で数えることが『固定10分・短縮禁止』と整合するか。
2. **共有関数へのhook追加(案A)の妥当性**。`generate_voice_body_wide_margin`はFamily B/C Voicesも呼ぶ(27-7 Legacy凍結)。`attempt_hook=None`既定でB/C呼出がバイト同一になるか(DESIGN_01 §C-2、§D-2、TEST-12)。案B(Z専用に複製)・案C(max_attempts=1を3回呼ぶ)との優劣。hookの差込点(ループ先頭/技術失敗`continue`/log追記後/関数冒頭のcarried_log/末尾STOPPED)に漏れは無いか。`attempt_ctx`のslot(call内番号)を変えない設計(現行意味の維持)でよいか。
3. **fallback時の完全除外保証**。attempt 3のstyle=`None`→`p9a.ENGLISH_STYLE_PREFIX`で現行Z dialogueとバイト同一になる、というtest設計(TEST-05: HEAD旧関数との送信prompt一致)は十分か。attempt内`minimal_fallback`(技術失敗時、MINIMAL_INSTRUCTION)が ctx attempt で発火した場合の扱い(開示のみで採否は既存ASR判定)は『3回目のみ従来方式』と矛盾しないか(ユーザー仕様上『ctx attemptの生成がctxを含まない』状態を許すか)。
4. **X/Y/B/C/narrator/KPへの無影響**。policy pin(`audit/style_record.json`の`dialogue_tts_policy`、キー無し=legacy)とreuse_key追加(dialogueのみ、legacyではキー不変)の設計に、既存runの混在・再利用の取りこぼし・RESTARTでの方式切替がないか。`REUSE_DENY`(auditディレクトリ拒否)で新state/notesが新runへ漏れないか。
5. **感情情報の自動受理の歯止め**。Fable目視レビューを外す根拠(決定済み77件でvalidatorとFableの判断が100%一致、覆し0件、全編53件はaccept 53)で十分か。残余(validatorをすり抜けるLLM創作、0/76)をnotes保存のみで許容してよいか。新基準を作らずに閉じる別案があるか(ただし『ACCEPTEDの一部だけ採用』は新基準追加になる)。story別data(表示名・許可語)のfallback(Trial未検証story)の妥当性。LLM失敗時の『全clip中立note続行』対『技術STOP』のどちらが適切か。
6. **強制NG注入がGate迂回にならない設計**。driverが`apply_repetition_qa_gate`の戻りをNG方向にのみ上書き(実TTS・実ASR・統一judge・disfluencyの後)する方式は、Productionの安全装置を迂回・無効化せずに『遷移』だけを検証できるか。注入口をProduction codeに置かない設計(env/flagなし)で十分か。強制NG runが公開page・共有storeを汚さない隔離は十分か(forced run dir・pages出力なし・attempt_history/HR queue/Lockへの書込の扱い)。
7. **Trial観測問題の扱い**。6項目(話速0.56×、長ポーズ、境界音量差、F0、メロスStd比較音量不一致、ASR/QA不合格1件)を『既存の承認済みValidator・組立・品質条件に反するものは0件。新gateは作らない』と整理した判断(DESIGN_01 §E)に誤りは無いか。見落とした既存条件はあるか(例: ヘッドルーム安全弁と`check_clip_audio_quality`のpeak_max=0.999の関係)。
8. **費用・時間**。EVAL_01の『+約0.08円/call』と本設計の再導出『+約0.098円/call』の差(BUDGET_PLAN §1 区分2)。fallback待機を既定でclip内ブロックにする判断(deferralを後回しにする判断)の妥当性。Phase 2見積(期待約48円)とGuardrail。
9. **Local Rewriteの扱い**。Z dialogueにLRが未配線である事実(EXISTING_SPEC_CHECK §2・§3 行3)に基づき『LRを新設せず3回NG→STOPPED→HR』を既定とする判断は、ユーザー文言『既存のLocal Rewrite処理へ』『LRも既存の回数上限・安全条件を維持』に反しないか。将来LRを配線する場合に本設計が障害にならないか。

## 3. 出力形式(Opus台帳`OF-FZCW-*`へ転記する前提)

- 必須修正(M-n)、推奨(R-n)、問題なし(OK-n)、残リスクを論点番号つきで。各指摘に根拠のファイル:行を付す。
- 『実装前にFableが判断すべき事項』と『実装中に確認すれば足りる事項』を分ける。
- Production採用可否の判断は不要。既存仕様・承認済み仕様との矛盾を見つけた場合は『不具合』として明記(新仕様候補とは区別)。
- 新しい品質基準・仕様の提案は、設計既定にせず『ユーザー判断候補』として分離。

## 4. 制約・非目標

- Production code・Prompt・閾値・辞書の編集提案は『ユーザー決定の範囲内の配線』に限る。品質基準の追加/緩和、試行回数・クールダウン時間の変更、X/Yへの拡大は範囲外。
- 本レビューは実装前。レビュー後、Fableが照合のうえ11-3のSTOP条件に該当しなければPhase 1へ進む(Opusレビュー自体はユーザー承認Gateではない)。
