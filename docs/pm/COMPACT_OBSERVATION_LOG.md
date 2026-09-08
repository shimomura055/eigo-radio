# COMPACT_OBSERVATION_LOG — auto-compact観測ログ(軽量)

管理ID: PM-CONTEXT-MANAGEMENT-PLAN-B-IMPLEMENTATION-02

目的: 案B(`docs/pm/ACTIVE_TASK.md`固定ヘッダ+`CLAUDE.md`復帰手順)と
auto-compact閾値約65%(`.claude/settings.local.json`の`autoCompactWindow`)
導入後、最初の数回のauto-compactを軽量に観測する。大規模なTelemetry基盤は
作らない。記入はFableが次にSonnetへ委任するタイミングで依頼する運用とする。
このファイル自体はSSOTではなく観測記録であり、正式仕様はCURRENT_SPEC.md等
既存SSOTを変更しない。

| 日時 | 設定閾値 | 前回compactからの経過 | 復帰所要時間 | 復帰時に読んだファイル・範囲 | 推定追加Token | UDR・Status・STOP条件の欠落有無 | 作業継続への支障 |
|---|---|---|---|---|---|---|---|
| (未観測、導入直後) | 650,000 tokens(Sonnet 5ネイティブ1,000,000 token windowの約65%) | - | - | - | - | - | - |
