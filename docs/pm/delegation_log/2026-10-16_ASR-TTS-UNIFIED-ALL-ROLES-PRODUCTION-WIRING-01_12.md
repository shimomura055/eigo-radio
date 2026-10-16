# ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_12(受領した委任文の保存。T-0)
注: 委任文の主要部(管理ID・前委任受入・性質/到達上限・禁止事項・事前dry-run必須・上限・T-3定型文・時間/費用・固定ブロック・ユーザー指示参照・KPI provenance・Opus台帳・事前指定Read/Grep・実行コマンド・SSOT追記・Git・報告項目)を逐次保存した版。

## 管理ID
`ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_12(残evidence: B-A2-01 narrator[Hook/Tension/Closing含む全体]の実音声+fresh JA正例2 clip[Latin token無し原稿]+15条件表/マトリクス更新+commit/push。事前dry-run必須・費用上限厳守)。並行: Opus(A3設計D1レビュー、read-only)。

## 前委任(委任_11)の受入記録(Gate 7)
当初目的(A-5逐語): 「特にFamily B A2 narratorの見出し・Hook・Tension・Closingの必要な実音声確認を実施する。」「全SectionのProduction Wiring受入条件から未確認項目を黙って除外しない。」
最終成果物=commit 41adb2064。判定=PARTIALLY_ACCEPTED(narrator Hook/Tension/Closing未取得・fresh JA未取得・A3保留・費用JPY37.66でGuardrail16超過)。
Fable明示許可: narrator runは「harness不備修正済み新規run(事前dry-run合格後)」として1回に限り許可。dry-run不合格・STOP該当なら実行しない。

## 性質/到達上限/禁止
到達上限Status=`AUW_EVIDENCE_COMPLETE_PENDING_FABLE_15`。`PRODUCTION_WIRED`は書かない。
禁止: git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f、STOPセンチネル削除・回避、HR Lock変更、force_secondary拡大、Production flag/module monkeypatch、Latin文字を含むJA原稿の使用、有料runの再起動(各run初回1回のみ)、見積なしの有料実行。
事前dry-run必須(API 0): (d1)必須キー・Latin token・Store hit/miss (d2)呼出回数×委任_11実測単価で見積 (d3)上限超過なら実行せず報告 (d4)`evidence_12/<run>/dryrun.json`保存。
上限: narrator `bnarr_full` JPY30 / fresh JA `ja_fresh2` JPY4。合計Guardrail JPY34。T-3定型文適用(暴走疑い時のみSTOP)。1回JPY5超見込みのAPI(web lookup等)が発火しうる経路はdry-runで検出し、検出されたら実行しない。
Opus独立技術レビューGate(11-3): 非該当。時間見込み90〜120分。有料runは直列。当日既使用≒JPY57/1,000、本委任見積≤JPY34。承認区分C。

## 固定ブロック / ユーザー指示 / KPI
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3適用。ユーザー指示原文=`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`「# A.」A-5・A-7。KPI provenance: narrator/fresh JAとも`production_formal_path`(fresh)。

## 実行コマンド全文(要旨。--budget-jpy 30/4明示、差分再生成=新規topicのため対象外、Store再利用=共有narrationhit確認済み)
手順0 ff・STOP確認 → 手順1 dry-run(bnarr_full / ja_fresh2、`--dry-run`) → 手順2 narrator `--execute`(1回、`TTS_EXECUTION_MODE=STANDARD`、budget 30) → 手順3 fresh JA `--execute`(1回、budget 4) → 手順4 pytest(-p netguard) → 手順5 文書・SSOT・secret scan・明示add・commit・crbnでmainへff push。

## 事前指定Grep一覧+追記位置・更新位置の手順(SSOT追記先)
RUNTIME_EVIDENCE_06.md §18 / CLOSEOUT_PLAN_07.md §4-c / APPLICABILITY_MATRIX_01.csv B-A2-01(区分1、43行最終=実音声38/再利用4/N/A 1) / OPEN_ITEMS OPEN-396・395 / DECISION_LOG・REPORT_LEDGER・Opus台帳(OF-AUW-U1R-08→EVIDENCED)・CURRENT_SPEC統一ASR節。

## 報告
`docs/pm/RESULT_PACKET_AUW12.md`(項目1〜9)。`PRODUCTION_WIRED`は宣言しない。
