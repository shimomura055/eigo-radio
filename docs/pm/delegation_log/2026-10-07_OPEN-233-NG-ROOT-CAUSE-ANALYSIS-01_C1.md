# 2026-10-07 OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01 委任_C1(再採点の集計+原因系統合ドラフト、¥0)

## 管理ID
OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01(委任_C1)

## 性質
再採点の集計と原因系統合ドラフト作成(¥0)。API禁止。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT)は編集しない。Production変更なし。推測と事実を明確に分ける。並行タスクなし(評価者3本・B1・B2は完了)。git操作は本委任の最後に実施。ACTIVE_TASK/RESULT_PACKETは最後に更新。

## 目的
「前回(E2E_02等)でNGが多発し、今回(B3 Trial)で重大0だった理由」を、(A)盲検再採点、(B1)条件差分表、(B2)工程別分解の3つの証拠で統合し、Fableが最終判断する原因系ドラフトを作る。

## 事前指定Read一覧
- `er052_output/open233_ng_root_cause_01/_private/MAP_rca.json`(開封。開封時刻を記録)、`eval/articles/*.json`(27件)、`PREP_NOTE.md`
- `er052_output/open233_b3_trial_01/eval/articles/*.json` のうち MAP_rca の src が B3 V0 を指す12記事の元の採点(評価者間一致の計算用)、`eval/SUMMARY_STAGE2.md`
- `er052_output/open233_allfact_note_e2e_02/eval/SUMMARY.md` と独立評価のNG一覧(従来5/P2 10記事の元の採点。重大/軽微件数を記事単位で取り出す)
- `docs/pm/ng_root_cause_01/conditions_diff.md`、`docs/pm/ng_root_cause_01/ng_origin_by_stage.md`
- `docs/pm/b3_trial_01/aggregate_b3.py`(集計関数の再利用可)

## 事前指定Grep一覧+追記位置・更新位置の手順
なし(追記・更新位置: ACTIVE_TASK.md固定ヘッダに管理ID行を追加+本文末尾に1行、RESULT_PACKET.mdは上書き)

## 実行コマンド全文(作業)
1. 集計(`er052_output/open233_ng_root_cause_01/eval/aggregate_rca.json` と `eval/SUMMARY_RCA.md`): 出所別(E2E_02従来5/E2E_02 P2 10/B3 V0 12)の重大/軽微/退行/保留 件数と1記事平均、工程別(s0/s1/s2)内訳、機序別内訳、評価者別件数。同一記事の新旧採点の対応表(E2E_02 15記事=元評価 vs 再採点、B3 V0 12記事=今回B3評価者 vs 再採点評価者、一致率)。重大1件(space_weapons 89wf)の出所と元評価での扱い。
2. 統合ドラフト(`docs/pm/ng_root_cause_01/root_cause_draft.md`): 仮説H-A(測定差)・H-B(Note介入による実差)・H-C(Checker→Rewriteループ由来)・H-D(Writer JA R2段階での発生)・H-E(評価範囲・工程の差)・H-F(Gate STOP除外による選択)・H-G(テーマ差、hormuz)ごとに「支持する証拠/反証/判定(支持・部分支持・不支持・判定不能)」。各仮説の寄与を数値で示し、原因系の順位付け(証拠の強さ順)と次アクションへの含意(推奨は『候補』と明記)、限界(N、単独LLM評価、EN版の交絡、機序ラベルは事後付与)。
3. `docs/pm/ACTIVE_TASK.md` 固定ヘッダ(管理ID追加: DRAFT_READY、Opusレビュー待ち)+本文末尾に1行。`docs/pm/RESULT_PACKET.md` 上書き(12行以内)。
4. T-0: 本委任文を `docs/pm/delegation_log/2026-10-07_OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01_C1.md` へ保存+`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`。A1/B1/B2の委任文も同形式で保存(要旨再構成、`_A1.md`/`_B1.md`/`_B2.md`)。

## SSOT追記文
なし(SSOT編集禁止)。

## Git
個別add(`er052_output/open233_ng_root_cause_01/`(`_private/` は除外、`__pycache__`除外)、`docs/pm/ng_root_cause_01/`、delegation_log本件分)。commit「OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01: 前回NG多発の原因系分析(盲検再採点27記事+条件差分表+工程別分解、仮説H-A〜H-G判定ドラフト)、¥0、Production変更なし」+ trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`。push origin main。

## 報告
最終メッセージ(25行以内): 出所別の再採点結果表(重大/軽微/記事平均)、元/再の件数比(従来・P2それぞれ)、B3 V0の評価者間一致、重大1件の出所、H-A〜H-Gの判定と根拠1行ずつ、原因系の順位付け、限界、commit hash・push結果、check結果、raw URL(root_cause_draft.md、SUMMARY_RCA.md、conditions_diff.md、ng_origin_by_stage.md)。
(E-1/D-1/G-1/F-1: 固定ブロックは本件では適用なし(評価集計・ドラフト作成のみ、Gate・Production変更なし))
