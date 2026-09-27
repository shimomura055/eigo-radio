# 委任文全文(修正2回目、2026-09-27)

管理ID: PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01(修正2回目=Opus L2所見反映、¥0)+ NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01 Stage 3e(ユーザー承認済みLock解除runtime、**Guardrail ¥150、超過見込みでSTOP**)。一時ファイル `docs/pm/ACTIVE_TASK_PRN7.md` / `docs/pm/RESULT_PACKET_PRN7.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01_03.md` に保存しcommitに含める。**全TTSで `TTS_EXECUTION_MODE=STANDARD` を設定し、実行コマンドを逐語記録**。APIキーは環境変数のみ。

## ユーザー既決(2026-09-27)
- Human Review Lock解除承認: 根本原因修正済みの6 segment(Hormuz A2/B1B `full_story_part2`、Hormuz B1B `kp2_ja_charon`、small_bag A2 `comment_2`/`full_story_part2`/`full_story_part3`)に `approve_regenerate()` 使用可。加えて small_bag B1B Key Phrase再選定1 call承認、再TTS→ASR→Assemblyまで一括実行可。
- Lock解除は根本原因修正済みのsegmentのみ。OPEN-197/199等の実装修正が必要だったsegment(small_bag B1B `full_story_part2/3`、Meta A2 `japanese_title`)はPhase 3修正(commit b3cb2308/8da4b190)で解消済みなので、**これらもLock解除対象に含める**(実装修正を経ているため条件を満たす)。
- Opus L2(BLOCKERなし、SHOULD_FIX S1〜S5)を反映してからruntime。

## Part 1: Opus所見反映(¥0、コード+test)
REPORT `PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01_REPORT.md` に §10「Opus L2所見(逐語)」を追記してから:
- **S1**: `er003_v1_sing01_news_tail_fix.py` `_local_rewrite_recovery_for_news_narration`(L281-286付近)へ `enable_pronunciation_resolver` を引数追加し `__wrapped__` へ転送、戻りdictに `en_pronunciation_resolver_info` を `setdefault` で注入。
- **S2**: `er003_v1_sing01_voice01_generate.py` `_local_rewrite_recovery_for_charon_english` の戻りdictに `en_pronunciation_resolver_info` を注入(hint自体は既に保持)。
- **S3**: 同ファイル `generate_charon_english` の技術的fallback(L159 `MINIMAL_INSTRUCTION_PREFIX`)を、算出済みhitsで同一hookによりaugment(非対称解消)。
- **S4(a)**: `er025_entity_pronunciation_resolver_core_01.py` EN低confidence web lookupに `MAX_EN_WEB_LOOKUP_CALLS_PER_RUN`(JA同型、既定5)+telemetryを追加。
- N6/N7: blocked時戻り値形状の変化と累積会計(2→最大3/call)をREPORTに記録(コード変更なし)。N4: fullwidth dead codeは現状維持。
- test: S1〜S4のunit test追加(cache-only)、既存test+`run_project_regression.py`(既知失敗以外なし)。
- ここで一度commit(トレーラー `Management-ID: PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01`)。

## Part 2: runtime(Opus N7/N8/N9/N12の事前措置を必ず実施)
0. **事前措置**: (a) N12: 作業ツリーに残る他run由来のtracked artifact差分(`er006_output/master_audio_store_01/*`、`er006_output/*/human_review_queue.jsonl`、`er007_output/*/human_review_queue.jsonl`、`er011_output/attempt_history.jsonl`、`er011_output/family_a_completion_a2_trend_end_to_end_01/**`、`er021_output/**/telemetry.jsonl`、`er006_output/pronunciation_ledger_01/ledger.json`)を**path指定で**「runtime前artifact同期」として先に別commit(untrackedのACTIVE_TASK/RESULT_PACKET/docs/pm/*_check.json等は含めない)。(b) N9: Meta/Hormuz/small_bag の a2/b1b `audit/review_lock_state.json` のstate一覧と N7 `cumulative_tts_attempts`/`cumulative_asr_calls` をダンプし、`_generate_or_reuse` が実際に発火する集合(status!=OK)を事前確定してRESULT_PACKETに表で記録。承認外のsegmentが実課金で走る場合は事前に列挙し、対象外は実行しない(runnerにsegment限定が無ければ、承認外segmentは一時的にLock状態を変えずスキップできる方法を選ぶ。無理なら見積に含めて報告)。(c) S4(b): 本runは `ALLOW_PRONUNCIATION_WEB_LOOKUP=0`(cache-only)で実行し明記。OPEN-196回避のためa2/b1bは**逐次1プロセス**。(d) N8: `approve_regenerate()` に渡すtextは正規化後(`tts_input`形、前例 `er011_discovery_generalization_towels_trial_11_audio_04_b1b_fullstory_resume_human_review.py` L61)に揃える。
1. Lock解除(承認済み対象のみ、各segmentの解除記録を残す)→ Hormuz A2/B1B → small_bag A2/B1B → Meta A2 の順に `--stage tts` を逐次実行。S5(A2 slowdown周回で最大9 TTS)を踏まえ、**segment完了ごとに累計費用を確認し ¥150到達見込みでSTOP**。
2. small_bag B1B Key Phrase再選定: 既存Strategy L(既定 `kp_backend`、DB Hybridは使わない)で1 call → 構造Gate → 通過時のみ以降のKP TTS。
3. 全segment OKのレベルは `--stage assemble`(Meta B1Bは既完成)。
4. REPORT(Family X REPORT Stage 3e節 + Phase 3 REPORT §11 runtime evidence): **解除対象ごとの結果 / retry回数 / resolver発火(hits_applied・cache hit・web lookup 0) / JA punctuation rescue(Meta japanese_title: 正規化前後の判定) / Key Phrase再選定結果 / Assembly結果 / runtime cost / 残STOP** を表で。
5. SSOT: CURRENT_SPEC(読み解決節へPhase 3追記: B1B EN配線・JA正規化・Lock記録fix・EN lookup上限)、DECISION_LOG(Phase 3エントリ+Lock解除ユーザー承認)、OPEN_ITEMS(OPEN-197/198/199 → CLOSED、Lock記録ギャップ CLOSED、Opus N10 service narration残穴をOPEN、Phase 3 Gate 3 evidence)、REPORT_LEDGER。**SSOT編集直前に `git status` で他Agent(KP Family X配線)の未commit差分を確認、あれば最大10分待ち、解消しなければ記載案をRESULT_PACKETへ。**

Git: path指定add(`git add -A`禁止、他Agent[er030_*, er031_*, er003_key_words_*]のstageを外さない、index.lockリトライ)。runtime commitのトレーラーは `Management-ID: NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01`(本文にPhase 3 IDも記載)。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETに費用合計・commit hash群・変更ファイル・Lock解除記録・Assembly完成一覧・残STOPを必ず記載。
