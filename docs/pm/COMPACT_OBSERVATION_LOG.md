# COMPACT_OBSERVATION_LOG — auto-compact観測ログ(軽量)

管理ID: PM-CONTEXT-MANAGEMENT-PLAN-B-IMPLEMENTATION-02
(2026-09-08、PM-GOVERNANCE-REVIEW-LINK-REQUIRED-AND-AUTOCOMPACT-50-12で
閾値変更・列調整)

初期閾値 500,000 tokens(50%)、2026-09-08変更(650,000/65%→500,000/50%、
実window 1,000,000 tokens、ユーザー決定PM-GOVERNANCE-REVIEW-LINK-REQUIRED-
AND-AUTOCOMPACT-50-12)。

目的: 案B(`docs/pm/ACTIVE_TASK.md`固定ヘッダ+`CLAUDE.md`復帰手順)と
auto-compact閾値(`.claude/settings.local.json`の`autoCompactWindow`)
導入後、最初の数回のauto-compactを軽量に観測する。大規模なTelemetry基盤は
作らない。記入はFableが次にSonnetへ委任するタイミングで依頼する運用とする。
このファイル自体はSSOTではなく観測記録であり、正式仕様はCURRENT_SPEC.md等
既存SSOTを変更しない。

| 日時 | 設定閾値 | 発火頻度(前回compactからの経過) | compact直前のcontext使用量 | 復帰所要時間 | 復帰時追加Token | UDR欠落 | approved-but-unwired欠落 | STOP条件欠落 | 作業継続への支障 |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-08時点 | 500,000 tokens(実window 1,000,000の50%) | compact未発生 | 使用約177.6k(18%)、compact未到達 | - | - | - | - | - | なし(compact未発生) |
