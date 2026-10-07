# 2026-10-08 OPEN-233-REVERSAL-DETECT-HUMAN-ROUTE-TRIAL-01 委任_01 (T-0: 受領した委任文の保存。要約版。Opus診断レビューの逐語は別ファイル)

Management-ID: OPEN-233-REVERSAL-DETECT-HUMAN-ROUTE-TRIAL-01(委任_01)
性質: T1(反転型の決定論検出器と人間直送の負荷・再現率測定、¥0〜5、Trial/DEV)

## 並行タスク(衝突回避)
委任(STAGE2-01_03: ①v3、runner/checkerコードの構造要素Rewrite部分、`er052_output/open233_stage2_01/v3/`)が並行。本委任の書込先: `er052_output/open233_reversal_detect_01/`、`docs/pm/reversal_detect_01/`、`docs/pm/opus_l2_review_stage2_fail_diagnosis_01.md`、delegation_log。runner/checkerのコードは編集しない(検出器は独立モジュールとして `er052_output/open233_reversal_detect_01/tools/`)。SSOT/ACTIVE_TASK/RESULT_PACKET編集禁止、git禁止。起動前に `Get-Process python*` を確認し、他のpythonが走っていれば自分の処理は直列・1プロセス(M6)。API上限¥5(原則¥0、既存ログのみ)。held-outは手順4まで開かない。

## Opus診断レビュー
逐語保存先: `docs/pm/opus_l2_review_stage2_fail_diagnosis_01.md`(M1〜M6必須事項を含む)

## 事前指定Read
`er052_output/open233_stage2_01/eval/STAGE2_RESULT.md`、`er052_output/open233_stage0_01/reclass/known_relation_ng.jsonl`(dev)、`er052_output/open233_stage0_01/danger/danger_sentence_rules_v0.py`、replay対象33記事の本文・台帳(`er052_output/open233_stage2_01/precheck/replay_targets.json`)、台帳JSON構造

## 作業(M2: 先に事前登録)
1. `docs/pm/reversal_detect_01/preregistration_T1.md`(時刻付き): 検出器定義、主指標=否定・不在型と主体型の文レベル再現率≥60%(dev既知NG)、負荷=記事単位の「印が付く記事の割合」と「印が付く文/全文」を両方測る、合格ライン=印の付く記事≤33記事中2件(件数、M3)かつ再現率≥60%。held-out 1回のみ。費用上限¥5。
2. 検出器v0 `tools/reversal_detector_v0.py`(決定論): (i)否定・不在型=否定語(JA/EN)+台帳の肯定の出来事factの実体語/述語語との重なり (ii)主体型=文の主語の役割クラス(人/AI・システム/組織/利用者・公衆)が結び付くfactの主体クラスと異なる(曖昧なら候補化しない) (iii)否定文中の主体入替(475j-n1型)=(i)∧(ii)。語り枠(I/you/we・問いかけ)除外。クラス付与は辞書、LLM必要なら¥5内。
3. dev: 型別再現率、dev記事全文(JA R2・EN最終)の負荷(印の付く記事数・文数、位置別)、NGでない文への誤検出実例10件とその型。
4. held-out 1回(結果を見て調整しない)。
5. 人間直送の設計メモ `docs/pm/reversal_detect_01/routing_design_v0.md`(Rewriteせず人間レビューパックへ、Checker重さ判定は使わない、ladder枯渇時はM4どおり人間直送を設計判断として明示・BLOCKING未修正の出口は作らない、人間レビュー率の見積、10%枠との関係)。
6. `er052_output/open233_reversal_detect_01/T1_RESULT.md`(事前登録との照合、PASS/FAIL、限界)。
7. T-0: 本委任文を `docs/pm/delegation_log/2026-10-08_OPEN-233-REVERSAL-DETECT-HUMAN-ROUTE-TRIAL-01_01.md` へ保存+check.json。

## 報告
12行以内: 型別再現率、負荷(記事数/文数)、誤検出の型、held-out結果、PASS/FAIL、人間レビュー率見積、費用、ファイルパス。
RESULT_PACKET(短い要約)は本委任では編集禁止のため、最終報告を直接返す。
