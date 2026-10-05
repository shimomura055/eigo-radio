# OPEN-233 Self-Recovery Production wiring report(骨子、委任_09、2026-10-05)

## 1. 目的・Status

目的: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`の配線作業の記録場所。Status: 対象仕様=`APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`ではない(完了条件1〜12達成後のみ)。仕様正本: `CURRENT_SPEC.md`「OPEN-233 Self-Recovery Production Flow仕様」。

## 2. rep30有効構成とProduction対応

`docs/pm/production_wiring_gap_open233_01.md` §1(S01〜S23/N01〜N10)を参照。本節は実装時に対応状況を追記。

## 3. Stage 1 A構成fresh確認

委任_08(2026-10-05、実費¥11.42、gpt-6-luna、n=2、A4はn=4、prompt sha 26/26一致=復元は正確)の結果: **事前固定受入条件(1)(2)(3)でFAIL**。
- (1)SC: B3 2/2、B4-a 2/2、A2A3-0 2/2、A5-0 2/2、A4-0 2/4(3/4未満でFAIL)。neg5 B3-same 0/2(frozenは検出)。
- (2)B群既知重大の見逃し: neg5 B3-same(0/2)、B2_hormuz HF-011(0/2)、B4の一部claim(0/2)。
- (3)負例/NORMAL群MAJOR run率: fresh 58.3%(7/12) vs frozen 54.5%(6/11)=超過。
- 復元差なし(prompt sha・model一致)=Stage 1 Checkerのrun間変動。frozenは単発サンプル。claim単位一致率平均0.658。
- 影響分析(¥0): `er052_output/open233_kpi_recovery_02_offline_01/agg_stage1_variance_impact_01.md`。判断材料のみ、採用提案ではない。

## 4. 配線設計

Opus#15(`docs/pm/opus_l2_review_open233_production_wiring_15.md`)とGap文書§7 Fable評価を参照。

## 5. 実装記録

(module・アダプタ・テスト。後で記載)

## 6. runtime evidence

(後で記載。Phase 2計画はCURRENT_SPEC項目15)

## 7. Regression・integration

(後で記載)

## 8. Dangling Reference Check表

| 仕様名 | CURRENT_SPEC | 実装 | テスト | runtime evidence | 運用文書 |
|---|---|---|---|---|---|
| Self-Recovery Production Flow | 充足予定(委任_09、commit後に確認) | 未 | 未 | 未 | 未 |

## 9. 完了条件1〜12チェック表

| # | 条件 | 状況 |
|---|---|---|
| 1 | Production正式初回path配線 | 未 |
| 2 | retry/fallback/regeneration整合 | 未 |
| 3 | Trial専用依存なし | 未 |
| 4 | Production runtime evidence | 未 |
| 5 | Regression/integration PASS | 未 |
| 6 | actual routing/model確認 | 未 |
| 7 | CURRENT_SPEC更新 | 未(委任_09で仕様節を追加、完了確認は最終時) |
| 8 | DECISION_LOG更新 | 未 |
| 9 | OPEN_ITEMS更新/close | 未 |
| 10 | Git commit/push | 未 |
| 11 | ユーザー承認内容とProduction挙動一致 | 未 |
| 12 | Dangling Referenceなし | 未 |

## 10. 費用記録

| run | 費用 | ¥3超 | 備考 |
|---|---|---|---|
| (実装後に記録。¥3超のrunは必ず報告・記録、自動STOP/FAILにはしない) | | | |

## 11. 未解決・開示事項

- K1: Tを含め本文変更が計4回になりうる。
- K4: 日本語側の誤りは残存する(english_only、全文再生成廃止)。
- A2A3 HF-009: rep30では非検出。
- 委任_05の費用¥20.10を記録(K14 Phase 1補完)。
- 未解決(CORRECTION-02、2026-10-05): A構成fresh確認FAIL(SC 4/5・neg5 B3-same 0/2・A4-0 2/4、復元差なし=Stage 1非決定性)。rep30のVALIDATEDはStage 1出力を所与とした後段検証に限られ、Production初回pathのStage 1はrep30の忠実再現としては成立しない。USER_DECISION_REQUIRED候補: Production初回pathのStage 1をどう成立させるか。委任_08費用¥11.42(Guardrail超過、暴走ではない)。
