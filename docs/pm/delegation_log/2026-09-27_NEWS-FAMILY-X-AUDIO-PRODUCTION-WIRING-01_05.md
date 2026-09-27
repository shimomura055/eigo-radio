# 2026-09-27 NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01 委任文(Stage 3d、05)

管理ID: NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01(Stage 3d: 残STOP解消とAssembly完成)。Guardrail **¥300**(超過見込みなら実行前STOP報告)。一時ファイル `docs/pm/ACTIVE_TASK_FXA5.md` / `docs/pm/RESULT_PACKET_FXA5.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_05.md` に保存しcommitに含める。**全TTS実行で `TTS_EXECUTION_MODE=STANDARD` を必ず設定し、実行コマンドを逐語でRESULT_PACKETに記録**(Batch実行は禁止)。APIキーは環境変数のみ、key本文を表示・log・commit・報告に書かない。

## 先出しRead
- `NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md` Stage 3a〜3c(commit f7d4eac4)の残STOP一覧
- `TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01_REPORT.md` §12〜§13(時刻コロン修正、commit 9bc458d0/d89e9068)
- `PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01_REPORT.md` §14〜§22(EN resolver配線範囲、OPEN-197/198/199)
- `er019_family_x_audio_production_runner_01.py`(`--slug/--run/--level/--stage tts|assemble`、`_generate_or_reuse(expected_text)` 再利用ガード)、`er011_human_review_lock_01`(Lock状態の読み方)
- 対象run: Meta `family_x_audio_production_wiring_01/family_x_b3_production_wiring_01__run_01`、Hormuz `family_x_b3_diversity_trial_01/hormuz__run_02`、small_bag `family_x_b3_diversity_trial_01/small_bag__run_02`

## 作業(すべて既存Production経路・既存Gate・既存retry予算の範囲内。新仕様・Gate緩和・Prompt変更は禁止)
0. **Lock棚卸し(最初に、¥0)**: 3記事×A2/B1Bの全segmentについて、Human Review Lock状態(`review_lock_state.json`等)・STOP理由・attempt消費数を表にする。**Lock中のsegmentは `approve_regenerate()` 等でLock解除しない**(ユーザー明示操作のみ)。Lock解除が必要なsegment一覧を「ユーザー承認待ち」としてRESULT_PACKETに明記し、それ以外を本委任で進める。
1. **Hormuz B1B `full_story_part2`**: 時刻コロン修正後の既存runner `--stage tts` で再TTS(既存音声OKのsegmentは `_generate_or_reuse` で再生成されないことを確認)。"11:04 a.m." のASR照合結果(Tier 1数値等価の発火有無、retry回数)を記録。
2. **small_bag B1B Key Phrase構造Gate("have")**: 既存の再選定経路(runnerの既存retry/再選定手順)で解消を試みる。既存仕様で自動再選定が無い(max_attempts=1で人手)場合は、勝手に変えずその旨と既存仕様の該当箇所を報告してSTOP(このsegmentのみ)。
3. **small_bag A2 `comment_2`/`full_story_part2`/`full_story_part3`(ブランド名ASR失敗)**: Phase 2で配線済みのEN resolver(A2英語経路)を通る既存runnerで再TTS。resolver lookup(Perplexity)の発火・confidence・hint注入・ASR結果を記録。既存retry予算内で不合格ならHuman Reviewへ落ちるのは正常動作として記録(Lock解除はしない)。
4. **Meta A2 `japanese_title`(Muse)**: OPEN-199(JA Validator句読点ギャップ)未修正のため**再TTSしない**(現状維持、理由記録)。
5. **Assembly**: 全segment OKになった記事/レベルは `--stage assemble` で結合音声・player作成。未完のものは「未完・理由」を表に。
6. **CURRENT_SPEC「Family X音声構造」DESIGN NOTE**(Stage 3c積み残し): 見出しsub-segment(`full_story_part2_heading`/`full_story_part3_heading`、Family A `point_one_heading`機構流用、unit 25→32)を既存記述へ最小追記。**SSOT編集直前に `git status` でCURRENT_SPEC/DECISION_LOG/OPEN_ITEMSに他Agent(Flash-Lite比較パケット)の未commit差分があれば最大10分待ち、解消しなければ記載案をRESULT_PACKET/REPORTに置いてSSOTは編集しない**。
7. REPORT Stage 3d節: Lock棚卸し表、各segmentの結果(attempt/ASR/費用)、Assembly状況、費用合計、残STOPと分類(ユーザー承認待ちLock解除 / OPEN-199待ち / Human Review正常落ち)。

Git: 変更・生成ファイル(音声artifact含む、25MB超除外)・REPORT・delegation_log・(可能なら)CURRENT_SPECのみpath指定add(`git add -A`禁止、他Agent[er028_*, er022_*, docs/pm/flash_lite_*]のstageを外さない、index.lockリトライ)。トレーラー `Management-ID: NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETに費用合計・commit hash・変更ファイル・Lock解除待ち一覧・Assembly完成一覧を必ず記載。
