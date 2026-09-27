2管理IDを直列で扱う委任(同じer019 runnerを触るため1 Agentで実施)。一時ファイル `docs/pm/ACTIVE_TASK_FXA7.md` / `docs/pm/RESULT_PACKET_FXA7.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_07.md` に保存しcommitに含める。Guardrail **¥20**(Part Bのみ課金、Part Aは¥0想定。Assemblyで課金が発生する処理があれば事前に見積を記録)。`TTS_EXECUTION_MODE=STANDARD` を設定(TTSは実行しない想定だが念のため)。APIキーは環境変数のみ。

## Part A: NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01 Stage 3f — OPEN-193/204(同根)の修正とAssembly
1. 既存資産照合: OPEN-193(2026-09-27起票、`article.md` コピー/`article_text` fallback未自動化)とOPEN-204(Stage 3e、`er003_v1_n3_01_assemble.py` `verify_episode_audio_validation_gate()` の `article_text` 必須化[commit 8f197a74/1d69aa97、KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01]にFamily X runner側が未追従)は同一の実装穴。分類A。
2. 修正(最小差分、Family A/B/C legacy呼び出し不変): `er019_family_x_audio_production_runner_01.py` の assemble stage で、記事本文(text runnerの `article.md`/article_text の正規ソース)を `verify_episode_audio_validation_gate()` へ渡す(または out_dir へ `article.md` を配置する既存fallback機構を自動化)。どちらが既存仕様に沿うかはOPEN-193の記述とGate実装から判断しREPORTに根拠を書く。unit test追加(article_text欠落時はfail-closedのまま、正常時はGate通過)。
3. Assembly実行: Hormuz A2 / Hormuz B1B / Meta A2(全segment OK)を `--stage assemble`。Meta B1B(既完成)は再実行不要だが最終artifactの存在確認。small_bag A2/B1BはSTOP中のため実行せず。各levelの結合音声・player・validation gate結果をREPORTに記録。
4. OPEN-193/204 → CLOSED(SSOT)、Family X REPORT Stage 3f節、DECISION_LOG、REPORT_LEDGER。

## Part B: KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01 — 修正1回目(commit bfd7090e)後のruntime evidence(Gate 3最終項目)
1. Hormuz A2 1記事を、Production共有入口 `run_key_phrases(kp_backend="db_hybrid")`(Family X runner経由が望ましい: `run_theme_scaffold` のKP部分のみ、既存Production artifactは上書きしないevidenceモード `er030_output/family_x_kp_db_hybrid_evidence_02/`)で1回実行(約¥1〜2)。確認: B1 telemetry(strategy_l/db_hybrid両経路の全項目、`synthetic=false`)、B2 per-article metadata(`keywords_runtime_metadata.json`/`kp_backend.json`、`entry_point.json` の `kp_backend_used`)、S3 raw article照合、S4 cost意味論(per-call runaway記録・記事累積)、S5 shortlist条件、model_id(routing contract経由)。
2. B3(routing違反→STOP)は課金せずmock注入testで再確認済みであることをREPORTに参照記載。
3. REPORT §9「post-fix runtime evidence」+ Gate 3チェックリスト全項目のevidence表を最終化(PRODUCTION_WIRED判定はFable。「Fable判定待ち」のまま記載)。SSOT: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER に post-fix evidence の事実を追記(Statusは APPROVED_FOR_PRODUCTION のまま)。

## 共通
- 他Agent(small_bag診断: read-only)との衝突なし。er032/er029/er030 Coreは変更しない。
- SSOT編集直前に `git status` で未commit差分を確認。
- Git: Part A と Part B は**別commit**(トレーラーはそれぞれ `Management-ID: NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01` / `Management-ID: KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01`)、path指定add(`git add -A`禁止、index.lockリトライ)、push origin main。reset/amend/rebase/force push禁止。
- RESULT_PACKETに費用・commit hash群・Assembly完成一覧(artifactパス)・Gate 3表要約・残STOPを記載。
