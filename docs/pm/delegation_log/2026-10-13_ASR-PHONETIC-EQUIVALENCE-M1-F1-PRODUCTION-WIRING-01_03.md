# ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_03(要点保存。見出し保持、全文は省略)

## 管理ID
ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_03(Fableからの修正・継続指示1回目。委任_02の設計にOpus独立レビュー[条件A/C、OF-159〜168]を反映し、F1のみ実装する。M1はOOV扱いがUSER_DECISION_REQUIREDのため配線しない。M1(i)の実益集計のみAPI 0)。並行タスク: FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01 委任_01。

## 性質/到達上限Status/禁止事項
- 性質: Production実装(F1)+影響集計再実行+replay evidence+SSOT。到達上限Status: F1=WIRED_PENDING_RUNTIME_EVIDENCE / M1=WIRING_DESIGN_DRAFT維持(未配線) / OOV=USER_DECISION_REQUIRED維持。費用¥0(有料API禁止)。
- 禁止: M1配線、OOV関連コード、Pattern A/B/C拡張・緩和、頭字語の新正規化、allow-list、Gate緩和、R1/V2'、Melos固有処理、Family Z記事再生成・音声化、git add -A/-f、amend/rebase/force push、stash/clean/reset --hard、.env、wav/telemetry/log add、ACTIVE_TASK/RESULT_PACKET commit、共有ファイルへ追記するtest実行、外部プロセス再起動、監督ループ。
- STOP条件: 既存承認仕様の拡大が必要/受入条件に新ルールが必要/関連外の新規回帰失敗/census再実行で「全差分が承認済みPattern・既存正規化で説明できるのにF1が非PASS」(=真の誤NG)が出た場合は報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
T-0: 本ファイルへ保存しcheck_delegation_prompt実行。T-2: TTSなし。T-3: ¥0。

## ユーザー指示(原文)
委任_02保存分(2026-10-13_..._02.md)の「ユーザー指示(原文)」節を参照。

## Opusレビュー反映事項(要点)
1. OF-159 Eq Layerガード(F1のdiffは最初の残差、Eq Layerは残差ちょうど1件のみ評価)
2. OF-160 benignは冠詞のみ/_is_benign_plural_pair 1:1のみ
3. OF-161 f1_residual_kind(none/entity_or_homophone_only/content)、entity_or_homophone_onlyはUNCERTAIN
4. F1本体: 全差分列挙→各差分にPattern A/B/C個別適用→説明不能は残差、残差0のみACCEPT
5. OF-167 観測項目 f1_all_diffs/f1_explained/f1_residual/f1_residual_kind/f1_version
6. census再実行(674ペア+segment_id=None+KP実データ)、誤NG定義固定
7. cascade層replayテスト(ユーザー例/正常6/反例11/Eq Layerガード/dialogue相当)
8. M1(i)実益集計(OF-168、配線なし)
9. US sea 4件の記録(音声は聴取しない、頭字語は新規OPEN案)
10. 設計書訂正(OF-163/164/165): forced-secondary/減速後再検証/m1_enabledフラグ/cascade_enabled=False時
Regression/SSOT/Git/報告項目は委任文どおり(commit 2回、Managed-ID trailer付き)。
