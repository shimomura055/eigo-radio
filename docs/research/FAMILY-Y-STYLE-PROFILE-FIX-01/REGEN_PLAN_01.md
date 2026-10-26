# REGEN_PLAN_01 — 再配達記事の再生成計画と見積(委任_02用。本委任はAPI 0)

管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_01 / read-only。入力=`er121_output/family_y_production_01/redelivery_fee/run_voice_puck_ev_01/{a2,b1b}/audit/tts_generation_results.json`(現行`_02`版)、`run_01/cost_log.jsonl`・`cost_by_stage.json`、`docs/research/FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/EVIDENCE_01.md,EVIDENCE_02.md`(Puck実績)。
前提(ユーザー§1C・原文): Voice 1=Puck/Voice 2・3の承認済みVoice(Zephyr/Schedar)/3 Personaを維持、Advanced Comment 2削除を維持、品質PASS済みの無関係な音声は再利用、Standard/Advanced両方を再組立・公開、旧版は旧Style版として保持。

## 1. 影響範囲(segment単位。Style prefixが変わるもの=再生成、変わらないもの=Style上は再利用可)
根拠=STYLE_MATRIX_01.md。現行`_02`版のsegment数=Adv 12本文系+KP、Std 14+KP(上記results実測: b1b 12 segments[comment_2なし]・a2 14 segments)。
| level | 再生成が必要(Style変更) | 件数 | Style上は再利用可 | 件数 |
|---|---|---|---|---|
| Adv(b1b) | y_lead、y_intro_1〜3、y_voice_1〜3、y_closing(PD06) / preview(E1) / kp1〜3_english(K2) / kp1〜3_explanation(P7) | 8+1+3+3=**15** | topic_intro、comment_1、comment_3(基底のまま) | 3 |
| Std(a2) | y_lead、y_intro_1〜3、y_voice_1〜3、y_closing(PD06+6%減速) / preview、comment_1〜3(S3) / kp1〜3_english(K2) / kp1〜3_japanese_meaning(P8-KP) | 8+4+3+3=**18** | topic_intro、japanese_title(J3基底) | 2 |
| 計 | | **33 TTS take** | | 5 clip |
- shell固定音声(welcome/番号/KP intro/full_story_intro/outro 等)はStyle非対象でMaster Audio Store由来(`narration/*_charon.wav`)。新runでも共有ストア再利用(再生成ゼロ)。
- テキスト系(日本語原稿・英訳・support・KP・文法Part 2・study_text)は不変で再利用(LLM再生成0)。
- 不変条件の確認項目: Adv Comment 2が音声・本文・ページに残らない(現行`b1b/audit/tts_generation_results.json`にcomment_2なし。`narration/comment_2.wav`は旧ファイルが残るため新runでは複製しない)/Voice 1=Puck(`voice_assignment.json`)/Persona(本文不変、sha一致)。

## 2. run構成(M2により新out_dir必須。`er019_family_x_style_profile_01.py:290-295,440-456`)
- 新run dir: `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01`(`run_voice_puck_ev_01`から入力複製)。複製に含める: `text/ translate/ support/ key_phrases/ study_text/ study_text_slots.json provenance.json voice_assignment.json final_manifest(参考)`等のテキスト系(`EVIDENCE_01.md:2`の前例と同じ「入力のみ複製、音声assembled・review_lock・human_approved・ログは除外」)。**複製しない**: `*/audit/tts_generation_results.json`、`*/audit/review_lock_state.json`、`*/audit/human_approved_segments.json`、`tts_a2_stage.json`/`tts_b1b_stage.json`、`*/narration/`の本文系wav、`assembled/`、`pages/`。複製後にこれらが紛れていないことを課金前に確認(紛れるとM2が固定記録作成をSTOP=fail-closed)。
- OPEN-535との整合: 旧Algieba/default時代のHR承認(`human_approved_segments.json`の`preview`・`y_voice_1`等)は新Style/新音声に流用できない。新runには複製せず、新音声は通常のValidationで判定し、HRが必要になった場合のみ新規にユーザー確認(Fable判断)。並行委任のguard実装とは独立にrunの作り方で担保。
- 検討事項(要確認): `kp_review_mode.json`の宣言は`scope.run`が`run_01`の絶対pathに束縛(`er119_kp_human_review_01.py:406,422`)。前例`run_voice_puck_ev_01`は同じ宣言(scope=run_01)のままtts〜assemble〜pagesまで通過した(`kp_review_mode.json` scope確認済み)。新runでも同様に通るか、委任_02の最初の`seed_check`/dry-runで確認し、通らなければ「Fable代行の不在宣言1回(declare_absent_cli)」を実施(API 0)。
- 実行(正式CLI。T-2: STANDARD明示): `.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_style_fix_01 --theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json --reuse-manifest docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json --approved-budget-jpy 60 --tts-execution-mode STANDARD --stages tts_b1b,tts_a2,gate,assemble,pages,page_verify`(**1起動**。RESTART_STORM回避。`provision_shell`はY runnerのSTAGESに無い[`er121_family_y_runner_01.py:34`]。Fable/委任文で確定)。`--style-profile`は指定しない=新out_dirで既定の承認profileが固定記録される(2-1-3)。開始前と有料run前に`tools/stop_scope_check_01.py --managed-id <ID> --run-dir <run> --out <json>`。
- `--regenerate-stage`: 新run dirにstage JSONが無いので不要。複製したstage JSON(あれば)を残すと`_tts_input_sha`(profile入り)が変わりstale→STOPとなるため、複製しない。
- 差分再生成の可否(T-2追記(1)): 新run dirにcacheが無いので全33 clipを生成する。Style不変の5 clipの扱いは下記§4。
- 公開: `user_test/family_y_production_redelivery_fee_03/`(`run_style_fix_01/pages/{index.html,audio/}`を複製、`listening/`は複製しない)。旧`_02`(default Style版)・`_01`(Algieba版)は保持。

## 3. 費用見積(JPY)
単価の根拠(実測):
- Puck Std y_voice_1(約42秒): 1.3459円(TTS 1+ASR 2、`EVIDENCE_01.md:9`)。Adv y_voice_1(約40秒): 約1.17円(総額2.511−1.346)。→ 本文は約0.03円/秒(TTS+ASR)。
- run_01実績: Gemini TTS 24 call=9.157円(0.38円/call、y_voice_1 7 takeを含む)、OpenAI ASR 31 call=2.785円(0.09円/call)、Azure 8 call=5.409円(0.68円/call。KP英語のvote 3+y_voice_1/preview再試行)。`cost_by_stage.json`。
- run_01の本文系は**全て1 attempt**(y_voice_1[Algieba]とa2 previewのみ多数回: `cost_log.jsonl`でy_voice_1 Gemini 7回、a2 preview 6回)。Zephyr/Schedar/Aoede(narrator)=1 attempt、Puck=1 attempt(EVIDENCE_01/02)。
| 区分 | 内訳 | 見積(円) |
|---|---|---|
| Adv 本文8 | 合計約215秒×0.03 | 約6.5 |
| Adv preview+KP(英語3+解説3) | preview約0.5、KP英語3×(TTS0.3+ASR0.09+Azure0.68)、解説3×0.4 | 約4.9 |
| Std 本文8 | 合計約229秒×0.032 | 約7.4 |
| Std preview+comment 3 | 4×約0.5(S3、日本語) | 約2.0 |
| Std KP(英語3+日本語意味3) | 3×1.07+3×0.4 | 約4.4 |
| **点推定(全attempt 1)** | | **約25** |
| retry見込み(本文でPuck 1.21 attempt平均相当を一部に加算) | +0.2×本文14円 | +約3 |
| **期待値** | | **約30** |
| 悪化ケース | a2 preview が run_01 同様6 take(TTS+Azure+ASR≈6×1.15=6.9円)+本文2 take追加 | **約45** |
| 上限(Cap案) | 個別Cap | **60** |
- 範囲: 点推定25〜悪化45円。**案件見積300円以下**(7-7)かつ承認済みScope(Y是正)内。日次: 当日既使用約563円+最大60円=約623円<1,000円(7-9)。Y累計予算上限は2026-10-24に撤廃済み(`DECISION_LOG.md:22308-22310`、per-run Cap=`er121_family_y_runner_01.py` の`APPROVED_BUDGET_MAX_JPY`=170円のみ残存)。
- ASR/Azure(KP vote)・LLM(LR発動時の書換え)を含む。LR発動の確率は低い(run_01で本文のLR発動はAlgieba y_voice_1のみ)が、発動時は+約1〜2円/回。
- 差戻し時(V2等でVoice本文のみ再生成): 本文6 segment×約1.2=約8円(STYLE_MATRIX_01 判断候補V)。

## 4. 再利用の扱い(ユーザー§1C「無関係な音声は再利用」)
Style不変の5 clip(Adv topic_intro/comment_1/comment_3、Std topic_intro/japanese_title)はStyle上は再利用可だが、再利用の既存機構は**同一out_dirのcache限定**(`er019_family_x_audio_production_runner_01.py:921,1076-1118`)。新out_dirへは自動で引き継げない。
| 案 | 内容 | 節約 | リスク |
|---|---|---|---|
| **R(推奨)** | 5 clipも新runで再生成 | 0 | 追加費用約2.5円・時間+1分。Style混在リスク0。新規コード0 |
| P | 新run dirで固定記録作成後に、5 clipの`results`entryとwavだけを`validation_inheritance.try_inherit_from_cached`が受理する形でseed(style_version一致・asr_verified・sha/canonical_text一致が条件。`--only-segments`で他を生成) | 約2.5円 | seed用の新しいcross-run引継ぎスクリプトが必要(OPEN-535と同じ「旧記録の流用」領域)。Opus任意レビュー候補。実装+test約0.5h |
推奨=R(節約額約2.5円は、cross-run引継ぎ機構の新設とそのリスクに見合わない)。ただしユーザー原文は「無関係な音声は再利用」であり、Rはその文言の最大5 clipを再生成する。**この解釈はFable判断**(Pを選ぶ場合は委任_02にseed手順を追加し、条件Aの要否を判定)。実質の再利用: テキスト・KP・文法・shell固定音声は100%再利用。

## 5. 所要時間(クリティカルパス)
| 工程 | 見込み | 並列化 |
|---|---|---|
| 実装(runner/Gate/test、委任_02) | 約2h(並行委任のcommit待ちを除く) | OPEN-535/527委任の完了後に着手(同一ファイル競合のため直列) |
| (任意)Opus独立レビュー | 設計はFable判断で任意 | 実装と並行準備可 |
| 新run準備+dry-run(API 0) | 約15分 | — |
| 実行(tts_b1b/tts_a2/gate/assemble/pages/page_verify) | 約15〜20分(run_01: Gemini 24 call計92秒、ASRほか含めてTTS stage数分) | b1b/a2は1起動内で直列(RESTART_STORM回避のため1起動) |
| 公開+HTTP/ページ検証 | 約15分 | — |
| Fable受入 | 別 | — |
合計約3h(実装〜公開)。ユーザー再試聴待ちは別。HRが必要になった場合は待機が加わる。

## 6. 受入で確認する項目(委任_02のRESULT_PACKETへ)
1) 新run `audit/style_profile.json` profile_id=`fx_20261017`、`audit/style_actual_vs_approved.json`が全role網羅・不一致0 2) Adv/Std全33 clipのstyle prefix実測(PD06/S3/E1/K2/P8-KP/P7) 3) Voice 1=Puck・Voice 2=Zephyr・Voice 3=Schedar(actual voice) 4) モデル`gemini-3.8-flash-lite-tts`・STANDARD 5) attempt数・fallback・LR 0または承認 6) Comment 2(Adv)残存0 7) ASR/Repetition/長ポーズ/速度/音量の必須検査PASS 8) 旧`_02`との変更前後比較表(Style・対象音声・品質・費用)。
