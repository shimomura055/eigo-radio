# ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01(委任_01、2026-10-08)

(注: Fableからの委任文の要約保存。原文はセッション履歴。主要項目は全て保持。)

## 管理ID
ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01(委任_01)。並行タスクなし。RESULT_PACKET.md・ACTIVE_TASK.mdは上書き可。

## 性質/到達上限Status/禁止事項
- 性質: Trial(比較実験)。問い=現在gpt-5.6-lunaを使っている工程をgpt-6-lunaへ切替えると記事の事実NG率・重大見逃しがどれだけ良化/悪化するかを数値化。合否しきい値なし(ユーザー指示)。Writer根本設計の要否は数値を見てFable/ユーザーが判断。
- 到達上限Status: MEASURED。VALIDATED/APPROVED_FOR_PRODUCTIONは宣言しない。
- Production変更禁止(er006_model_routing_contract_01.py / er019_family_x_ja_writer_o_r1_r2_01.py / er003_v1_en_direct_vfl_01_generate.py等)。差替えはTrial harnessのmonkeypatch/require_model_or_override(override_reason)。夜間ループ新スイッチは既定OFFのまま両群同一。
- 費用上限¥500(Guardrail)。到達=自動STOPではない。暴走疑い時のみSTOP。cost.json実測で集計。
- STOP: Phase1 smokeでgpt-6-lunaがpreviousresponse_id連鎖または出力形式で非互換(2回連続)。1枠再実行1回まで、全体8回まで。
- Opus独立技術レビューGate: 非該当。
- git add -A禁止、destructive git禁止、open238_precheck_fix_trial_01/・open233_b3_trial_01/runs/への書込禁止。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(TTS伴わない)。T-3: Guardrail。

## ユーザー指示(原文)
「閾値は現時点設ける必要ありません。まずはTrialを流して良化(悪化)具体を数値化して報告してください。予算は500円まで認めます。Checkerは前回Trialと同じValitadedされた仕様ですね?」(2026-10-08)。前段: 「決めたいのは根本設計(Wrtier)をする必要があるか。6.0で改善するならやる必要がない。」「Checker含めて、現状5.6を使っているものは6.0にTrial的に変更して、今のNG率、重大の見逃しの改善代を見る。...今は時間優先」。

## KPI provenance欄
T-A: fresh(新規48本、Trial harness経由)。briefはreuse(B3 V0 b1-b4 12本)。T-B: frozen。E2E自己確認: No。

## Opus台帳更新
該当なし。

## 事前指定Read一覧 / Grep一覧
RESULT_PACKET(直前調査)、er019 writer、er003 vfl01、er052 dev runner、driver_stage2.py、eval_rubric.md、STAGE2_RUN_CHECK.md、er052_output/open233_stage0_01/配下の既知NG一覧。Grep: run_checker_after_p01|CHECKER_MODEL、OPEN_ITEMS CHECKER-FLOOR行Status引用、MODEL参照箇所列挙(PREREGISTRATION表)。SSOT追記位置: DECISION_LOG(## OPEN-233最新直後+ヘッダーチェーン)、OPEN_ITEMS(OPEN-233-SELF-RECOVERY-TRIAL-01行末)、REPORT(次§)、REPORT_LEDGER末尾1行。

## 実行コマンド全文(要旨)
Phase0: 保存+check、harness `er052_all6_writer_trial_01_run.py`(--arm baseline/all6)、単体テスト、PREREGISTRATION.md、T-B/items.json(重大8+軽微20)。
Phase1 smoke(≈¥10): meta b1で baseline1・all6 1(--budget-jpy 12)、model_id実測、R0->R1->R2連鎖確認。smokeはPhase3集計に含める。
Phase2 T-B(≈¥30, Phase3と並列): `er052_all6_writer_trial_01_tb_run.py`、既知NG記事をJA Fact Check同一prompt/schemaで5.6/6-luna各n=2。
Phase3 T-A(≈¥200): 12 brief x 2群 x 2反復=48本、4並列自動降格、Checker ON両群同一。MANIFEST.json。
Phase4 盲検評価(≈¥20): eval_rubric.mdで盲検採点、SUMMARY_TA.md、HUMAN_CHECK_TA.md(10件まで)。
Phase5: RESULT.md。

## SSOT追記文
DECISION_LOG新エントリ(見出し `## ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01: ユーザー判断(2026-10-08、委任_01)`)+ヘッダーチェーン索引行、OPEN_ITEMS行末追記、REPORT新§、REPORT_LEDGER 1行(MEASURED)、ACTIVE_TASK更新。CURRENT_SPEC/PM_GOVERNANCEは編集不可。

## Git
明示add対象のみ。中間commit最大3回。trailer `Trial-ID: ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01`。push origin main。git add -A禁止。

## 報告(RESULT_PACKET項目)
1結論(数値のみ) 2悪化項目 3差替え対象表+Checker構成+OPEN_ITEMS Status引用 4副指標 5R0->R2初出・NG型・評価者別 6重大候補確認リスト 7限界 8完了/問題/次候補 9artifactパス・commit・費用内訳・check結果1行。推奨は書かない。
