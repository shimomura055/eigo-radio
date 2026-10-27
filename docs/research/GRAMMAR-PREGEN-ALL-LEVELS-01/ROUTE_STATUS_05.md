# ROUTE_STATUS_05 6経路 Status(委任_05。PRODUCTION_WIRED判定はFable)
| 経路 | KCP(確定内容保護) | GPG(文法新仕様) | フォームv3経路 | 備考 |
|---|---|---|---|---|
| X Std(a2) | EVIDENCE取得(G1 PASS/frozen) | EVIDENCE取得(候補1->Top1採用・finalize LLM0・player節単位PASS・model変更耐性PASS) | 未実施(payloadは `gpg5_payload_01.py` 再現。フォームUI Playwrightは別委任のFORM系) | 候補1件。Top2採用は未観測 |
| X Adv(b1b) | EVIDENCE取得 | EVIDENCE取得(同上) | 未実施(同上) | 候補1件 |
| Y Std(a2) | 部分(confirm済み、finalize後G1/frozen 未) | **部分**: Top1/Top2提示(2件)・Top1採用確定・**2件拒否(CLI+from-form)**取得。finalize/ページ/model変更は**未実施(Y RESTART_STORM STOP保持)** | 未実施 | STOP解除後に再開 |
| Y Adv(b1b) | 部分 | **部分**: Top1/Top2提示(2件)・**Top2(非Top1)採用確定**取得。以降未実施 | 未実施 | 同上 |
| Z Std(a2) | 対象外(旧run互換KP) | EVIDENCE取得(候補0->ZERO->「構文なし」1ブロック、page_verify OK) | 未実施 | 0件経路の主証跡。Z Std非0はruntime未観測(Zは候補最大1) |
| Z Adv(b1b) | EVIDENCE取得(G1 PASS/frozen/kp_selection_verified) | EVIDENCE取得(候補1->採用・finalize LLM0・page_verify part2 OK・model変更耐性PASS) | 未実施 | |
| X 0件(Std/Adv) | AI島参照 | 参照: `ai_island_temple__run_form_prod_01`(d05729316)で Std/Adv ともREVIEWED 0件・ZERO確認。本委任ではAIF3のM3 Style Gate STOP(別件)は未関与 | AI島側 | 参照のみ |
