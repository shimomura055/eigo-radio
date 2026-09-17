## 管理ID

`PM-CLOSEOUT-CONSOLIDATION-137-STATUS-CONSISTENCY-FIX`(Fable受入照合で発見したSSOT間の不整合の訂正。API 0、Productionコード変更0)。現在main=`16132f9c`。報告は`docs/pm/RESULT_PACKET_CLOSEOUT_137.md`(新規、簡潔)へ。

並行タスク: なし(念のためSSOT編集前に`git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md ARTIFACT_REGISTRY.md`で自分以外の未commit変更が無いことを確認。commit前に`git fetch origin`→進んでいれば`git merge origin/main --no-edit`)。全文Write禁止(Editで局所修正)。

## 発見した不整合(Fable確認済み)

B-Family新規topic A2 E2E Production経路(`main_a2_2v()`)の基盤Statusは、`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01`(2026-09-17、`docs/pm/RESULT_PACKET_PN_A2_PHASE_B_FIX1.md` 1節・12節、Gate 3 11項目全○、regression 2893/2896、Fable受入済み)で**`PRODUCTION_WIRED`**へ到達し、`CURRENT_SPEC.md` L669(新規topic A2 Production経路行)は`PRODUCTION_WIRED`と記載されている。しかし以下は旧Status`WIRING_INCOMPLETE`のまま:
1. `OPEN_ITEMS.md` L295(OPEN-151行): Phase B時点の「Status: `WIRING_INCOMPLETE`(配線自体は完了…Human Review…)」の記述がFIX-01後も更新されておらず、さらに`USER-FEEDBACK-CLOSEOUT-AND-VOICES-SPEC-REVIEW-01`追記で「実装基盤(`main_a2_2v()`配線)のStatus`WIRING_INCOMPLETE`は…変更しない」と再記載。
2. `DECISION_LOG.md` L8043(`## USER-FEEDBACK-CLOSEOUT-AND-VOICES-SPEC-REVIEW-01`エントリ内): 「(`main_a2_2v()`、OPEN-151行、Status=`WIRING_INCOMPLETE`)」。
3. `ARTIFACT_REGISTRY.md` L137(Personalized News A2行): 「実装基盤`main_a2_2v()`配線自体は`WIRING_INCOMPLETE`のまま」。

## 訂正内容

- OPEN_ITEMS.md OPEN-151行: 「2026-09-17 FIX-01追記: 見出しTTS retry policyを承認済み経路と整合させ、Personalized News A2 episode完成・Gate PASS・E2E再生確認により基盤Statusは`PRODUCTION_WIRED`へ到達(`docs/pm/RESULT_PACKET_PN_A2_PHASE_B_FIX1.md`、CURRENT_SPEC L669)。」を追記し、同行末尾のCloseout追記文の「`WIRING_INCOMPLETE`」を「`PRODUCTION_WIRED`(FIX-01到達、記事1本の品質NGとは別軸)」へ訂正。Phase B時点の旧記述は履歴として残してよい(「Phase B時点」と明示)。
- DECISION_LOG.md: 該当エントリ末尾に「**訂正(PM-CLOSEOUT-CONSOLIDATION-137、Fable受入照合)**: 上記の`main_a2_2v()`基盤Status`WIRING_INCOMPLETE`は誤記。FIX-01で`PRODUCTION_WIRED`到達済み(CURRENT_SPEC L669)。基盤=`PRODUCTION_WIRED`、Personalized News A2現行記事=`REJECTED_AS_CURRENT_OUTPUT`の2層管理。」を追記(既存文の削除はしない)。
- ARTIFACT_REGISTRY.md L137: 「`WIRING_INCOMPLETE`のまま」→「`PRODUCTION_WIRED`(FIX-01到達)」へ訂正。
- `docs/pm/RESULT_PACKET_FEEDBACK_CLOSEOUT_01.md` 2節・4節: 同様に訂正注記を追記(元文は残す)。
- OPEN_ITEMS.md先頭の「最終更新」要約行があれば、OPEN-163/164追加とOPEN-151訂正を反映(慣行に従う)。
- CURRENT_SPEC.md: L669-670が`PRODUCTION_WIRED`+品質NG注記になっていることを確認のみ(変更不要なら無変更)。

## Git
明示add(上記4ファイル+RESULT_PACKET+delegation_log)。メッセージ`PM-CLOSEOUT-CONSOLIDATION-137: main_a2_2v基盤Status表記をPRODUCTION_WIREDへ統一(OPEN-151/DECISION_LOG/ARTIFACT_REGISTRY訂正)`、trailer `Task-ID: PM-CLOSEOUT-CONSOLIDATION-137-STATUS-CONSISTENCY-FIX`。push。

T-0: 委任文を`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-137-STATUS-CONSISTENCY-FIX.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。E-1/D-1/G-1/F-1/T-1従来どおり。

## 報告(`docs/pm/RESULT_PACKET_CLOSEOUT_137.md`)
0. T-0 1. 訂正箇所一覧(ファイル:行、before→after要旨) 2. CURRENT_SPEC確認結果 3. Git SHA 4. 無変更証跡(`git status --porcelain er0*.py`空)/事前指定外Read。
