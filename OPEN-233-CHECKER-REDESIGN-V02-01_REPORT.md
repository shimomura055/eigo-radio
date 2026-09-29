# OPEN-233-CHECKER-REDESIGN-V02-01 REPORT

**Status**: PROPOSED / REVIEW(v0.2、Production code・Checker Prompt・
severity・routing・Ledger schema変更なし。Production Trial未開始。
API呼び出しなし、¥0。設計のみのタスク)。

本REPORTは設計書`docs/pm/design_checker_redesign_v02_01.md`(章立て1〜14)
の要約であり、詳細根拠(ファイル:行・事例Evidence・机上シミュレーション
結果)は設計書本体を参照。設計書は`LEDGER-DEVIATION-CHECK-REDESIGN-
INVESTIGATION-01_REPORT.md`(調査)・`LEDGER-DEVIATION-CHECK-REDESIGN-
REVIEW-01_REPORT.md`+Part A/B(v0.1素案へのClaudeレビュー)・
`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`§Phase B(GPT-6/GPT-5.6実測
比較データ)を統合し、GPT-6 Trial fixture記録(67件のdeviationレコード)
への机上シミュレーション(scratchpad自作`simulate_rules_c233.py`、
API呼び出しなし)を追加した新規材料である。

## 1. 問題構造(§1)

過剰BLOCK(B-1原油→ガソリン価格ブリッジ文4回独立発生、B-2 Hormuz
causality、B-3接続詞"so"、B-4一般化)/重大見逃し(A-1時制ドリフト、
changed_actor系統的MISS[baseline 0/6]、gpt-6-lunaのcategory検出自体の
MISS事例)/非決定性(同一inputでCOMPLIANT↔MAJOR、Advanced/Standardで
勝敗逆転)/実装非対称(MAJOR→MINOR降格のみ、逆方向補正なし)/origin判定
揺れ/QCD(call数4/記事、Hormuz 3 run連続STOP)を、モデル/Prompt/
post-hoc/呼び出し側/Ledger起因に分類。**モデルを強くするだけでは過剰
BLOCKは解決しなかった**ことをGPT-6 Trial実測(B群不要BLOCK率75%=75%、
同値)で確認。

## 2〜4. 各原因の1段掘り

過剰BLOCK=notes_for_writerの事実上のhard化+claim単体判定+許容範囲規定の
境界未定義(GPT-6でも不変)。重大見逃し=post-hoc非対称設計+changed_actor
の構造的弱さ(GPT-6で部分改善[3/6]だが完全解決せず、B4はむしろ悪化)。
非決定性=LLM-as-judge固有+claim切り出し自体の揺れ(GPT-6でもja_original/
ja_r2は高い非決定性のまま=モデルに依らないCheckerの設計特性)。

## deterministic rule候補(§5昇格側/§6非STOP化側)

**昇格側**: changed_actor/changed_number/changed_negation/changed_comparison
の4カテゴリはflag=true→BLOCKING(severity非依存)を既存構造化フィールド
のみで実装可能(誤昇格0件観測、ただし負例fixture不足)。本シミュレーション
でchanged_actorのみ8件のrescue対象(MINORのまま放置)を確認。

**非STOP化側**: 「causality-only & origin!=ja_source→demote」をGPT-6
Trialデータへ機械適用した結果、**B3(origin=ja_source)は正しくBLOCKING
維持される一方、JA段(origin=None、source_article_text未指定のため
構造的にNoneになるだけ)のレコードが誤ってdemoteされる設計上の罠**を
実データで発見。causality単独の非STOP化ルールは、B群の実際の過剰BLOCK
候補(B2/B3/B4)を**1件も救済できない**(B3はja_source、B2は今回検出
自体消失)。真の生産性改善にはnotes_for_writer分離(§8)+新schema
(qualifier/ledger_field_basis検出)が前提になる可能性が高い。

## 再設計案v0.2(§7〜10)

既存`severity`維持+`severity_final`/`action`/`basis`/`rule_id`追加の
後方互換方式。BLOCKINGはfail-closed維持、QUALITYは通過+ログ(fail-closed
適用範囲をBLOCKINGへ限定する設計変更、★ユーザー判断)。notes_for_writer
はsoft化せず、factual_constraint/writer_guidance分離schema案(Trial候補、
Production変更なし)。単一`classify_severity()`関数への集約でdrift回避。
Family A/B/C/X/Z横断影響・Dangling Reference可能性あり(Prompt変更は
共有関数のため全Family同時波及)。

## Trial案(§11)

受入条件: 重大fixture BLOCKING維持率100%/不要BLOCK率≤25%(案、妥当性は
★ユーザー判断)/gold既知fixtureのgold一致率目標。比較構成3種(baseline/
Prompt変更/反復判定)×両モデル。費用概算¥450〜1,440程度(GPT-6単価未確認
のため仮値)。gold確定要USER_DECISION_REQUIRED fixture: er009_changed_actor、
Meta run_03 Standard、B-2、B-4。

## 既存仕様との競合(§12)

fail-closed設計・案B・JA Fact Check配線決定(2026-09-27
PRODUCTION_WIRED)・ER-009-N1 recalibration・OPEN-189・Human Review Lock・
OPEN-233再開順序(既存SSOT既定=Family X E2E完了→GPT-6 Trial/Routing判断
→Production導入→本再評価)との整合が必要。

## リスク/未解決(§13)

QUALITYログ運用未定義、Key Phrase/Comment/In One Lineへの伝播対策未定、
過去REPORT統計の遡及的再解釈リスク、GPT-6単価未確認によるTrial費用概算の
不確実性、本シミュレーションのサンプルサイズ制約(67件、Family X実運用
15件との重複は限定的)。

## ★ユーザー判断が必要な事項(§14、全10項目)

1. Hormuz B-2をBLOCKING/QUALITYどちらにするか
2. fail-closed適用範囲をBLOCKING限定にする設計変更の承認
3. Key Phrase/Comment/In One Lineへの伝播対策の要否
4. Human Review非常口の統合先(既存音声用Lockか新規queueか)
5. Responses API temperature/seed制御可否の確認要否
6. Family横断Prompt変更 vs Family X限定`prompt_variant`引数
7. 不要BLOCK率目標値(案≤25%)の妥当性
8. OPEN-233再開タイミング(既存順序維持か前倒しか)
9. notes_for_writer分離schemaのTrial先行検証の承認
10. GPT-6モデルをChecker用途の採用候補に含めるか

詳細は設計書§14を参照。

## Evidence

- 設計書: `docs/pm/design_checker_redesign_v02_01.md`
- 入力REPORT: `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`、
  `LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_REPORT.md`、
  `GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`
- 机上シミュレーション: scratchpad自作`simulate_rules_c233.py`
  (repo外、API呼び出しなし、¥0)、出典データ
  `er050_output/gpt6_checker_comparison_trial_01/`
- delegation記録: `docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-REDESIGN-V02-01_01.md`
  (T-0 check結果: `status: FAIL`、理由は「性質」見出し文言不一致+scratchpad
  スクリプトの絶対パス不在という機械的誤検知、ブロッキングではない記録用
  ツール。詳細は`docs/pm/ACTIVE_TASK_C233.md`参照)
