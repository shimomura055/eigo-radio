# 委任_16 結果: FACTLOCK-ASTRA-E2E-TRIAL-01 評価文書 v2(2026-10-09、API支出¥0、Production変更なし)

## 1. 成果物・commit hash・raw URL
- commit: c5db43c6a99be1eb3fdc13e1358832a2187fb567(pushed to origin/main)。Status=MEASURED、USER_DECISION_REQUIRED(方向判断待ち)。VALIDATED/APPROVED_FOR_PRODUCTION未宣言。
- 主成果物(`er052_output/factlock_astra_e2e_trial_01/eval/`): `EVAL_E2E_01.md`(v2)、`HUMAN_CHECK_E2E_01.md`(v2、6節=面白さpairwise)、`judge_table_01.py/json`(再計算)、`merge_labels_01.py`/`labels_merged.jsonl`(8行にqa_noteのみ追記、原本labels_w*不変)、`build_human_check_01.py`、`_private/PAIRWISE_MAP_01.json`(対応表、回答前に開かない)。
- SSOT/記録: `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§111)、`DECISION_LOG.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`(OF-111〜119)、`docs/pm/opus_a_review_factlock_astra_e2e_01.md`(評価レビュー節)。`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET.md`は.gitignore対象の一時ファイル(更新済み、commitされない)。
- raw URL(主要):
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/eval/EVAL_E2E_01.md
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/eval/HUMAN_CHECK_E2E_01.md
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/eval/judge_table_01.json
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG.md

## 2. 最終判定表(そのまま転記可)
| 判定線 | Fable最終判定 | 根拠(要約) |
|---|---|---|
| 2-1 重大(出荷最終本文の残存) | 判定不能 | 床効果0対0。要確認フラグはB-05回答待ち |
| 2-2 軽微 JA列 | 同等(検出力不足) | 新4対旧9(平均0.67対1.50、新が少ない3対・旧が少ない0対・同点3、p=0.125)。判定線は構造上到達困難、新優位方向の記述的傾向のみ |
| 2-2 軽微 EN Adv列 | 同等 | 3対3 |
| 2-2 軽微 EN Std列 | 判定不能 | 床効果 |
| 2-4 EN Adv STOP率 | 同等 | 2/9対0/9、差2記事は線未満、全件軽微・問題なし起因、§5-11適用で新1 |
| 2-4 EN Std STOP率 | 同等 | 2対2 |
| 2-5 Rewrite率 | 同等 | 0.111対0.167。旧の不要RewriteはChecker欠陥由来 |
| 2-5 Human Review率 | 判定不能 | 0対0 |
| 2-5 人手介入必要率 | 同等・混在 | 0.333対0.333、感度(失ったChecker run)0.444対0.333、層別逆向き(旧4: 0.125対0.625、新5: 0.50対0.10) |
| **総合** | **同等・混在** | 事実安全の良化は示されなかった(測定力不足を含む)。費用約6倍(新約¥43.9対旧約¥7.1/記事)。面白さは未測定 |

## 3. 訂正点一覧(Opus 1〜5)
1. semiconductor新EN STOPの帰属: 「B3注記のqualifier文由来」は誤り。Opus指摘のファイル・行を全て実ファイルで確認(brief_original.md L7=旧腕briefにも同文、r0_with_tags.md L11、r2.raw.md L13、advanced_attempt1.json L20、annotation.jsonのunmapped_claimsにqualifierとして記録)。EVAL 3-4の5/5-0/5-3/4-1、OC-5訂正、OC-11新設。§5-11別集計: Adv STOP 新1/9、人手介入 新5/18=0.278対旧6/18=0.333、判定不変。
2. 2-2 JA列からopenai新 w3-40(未出荷)を除外: 新5→4件。平均 0.67対1.50、新が少ない対3・旧が少ない対0・同点3、符号検定 p=0.31→0.125。判定「同等」不変。層別 新5=3対5。
3. 感度値(新8/旧6=0.444対0.333)を2-Cの主表に独立行として格上げ。
4. ラベル基準統一: semi(w3-90/92 問題なし)とspace(w1-49/76/61/62/73/75 軽微)にOC-8同型のqa_noteを追記(8行、ラベル値・原本は不変)。
5. 言い過ぎの訂正: 注記起因の過剰ブロックは確認0件(central周辺扱いが未検証の候補1件)、「Checker欠陥に強い」は母数不足の見かけ、M3は便益・コストとも観測不能。「少なくとも1〜2件は注記起因」は撤回。

## 4. 人間確認パックの構成(HUMAN_CHECK_E2E_01.md v2)
- 事実確認3記事(変更なし): 2節 byd_recall(B-1〜B-6)、3節 openai_copyright(O-1〜O-3)、4節 central_bank_mortgage(C-1〜C-4)、5節 共通基準質問 space_weapons(S-1/S-2)。
- 追加(6節 面白さpairwise、約10分): P-1 space_weapons、P-2 streaming_price、P-3 small_bag。各対は新旧のJA最終本文(ja_writer/revision2.md)をA/B表記、順序は乱数(seed 20261009)。問い=①面白さ(A/B/差なし)②事実の不安(なし/引用)③一言理由。MAPは`eval/_private/PAIRWISE_MAP_01.json`(P-1: A=旧/B=新、P-2: A=新/B=旧、P-3: A=旧/B=新。Fable/回答後の照合用)。
- 注意: P-1は5節の文面から腕を推測できる可能性(パックに明記)。文体・字数の差で腕が推測できる点は既知の盲検の限界。

## 5. Production Checker文分割器の配線確認(Grep+実測)
- 存在する: Production経路の `er052_open233_self_recovery_flow_runner_01.py`(E2E acceptance等がimportして使うrunner)の `split_sentences_generic`(L4591)は `re.split(r"(?<=[。！？.!?])\s*", ...)` で、実測 `"The annual price will rise by $25.99 per year. Next sentence."` → `['The annual price will rise by $25.', '99 per year.', 'Next sentence.', '']`。`locate_best_sentence`(L4434)も同型。呼出し: 位置比(L4687)、precheck対象文特定(L8399)、ja_fail_open_guard非JA分岐(L8015)、同一fact位置展開(L1759)。`open238_precheck_fix_trial_01/tools/precheck_baseline.py`も同ロジック(コメントで明記)。
- 未特定(断定しない): 旧腕Std Checkerの断片claim(「…by $25.」等)の発生源が上記の分割器か、Stage 1 LLMのclaim列挙か。claim_in_articleはStage 1出力だが、断片化の起点は未切り分け。`er052_output/open233_prod_e2e_02` は出力置き場でコード上の分割器ではない(runnerをimportする側の実行結果)。OC-1起票時の最初の調査(¥0)は切り分け。

## 6. 未確認・Fable判断要
- ユーザー方向判断(選択肢 a〜e、REPORT §111/EVAL 8節。費用は全て推定)。OPEN起票(OC-1最上位、OC-3/OC-8次点、OC-11新設)はFable判断(OPEN_ITEMS.md未編集)。
- 人間回答待ち: B-05(2-1要確認フラグ)、STOP妥当性(O-1・C-1〜C-3)、基準(S-1/S-2)、pairwise。
- 未検証: central周辺扱いの因果、断片claimの発生源、pairwiseは1名・3対のため統計的比較ではない、請求照合。
- 判断要: `eval/_private/PAIRWISE_MAP_01.json` を公開リポジトリにcommitしてよいか(ユーザー専用リポジトリ想定でcommit済み。盲検の運用上、回答前に開かない前提)。
- 「Fable最終判定」は委任文の指示どおり転記。ラベルはSonnet暫定、n=9、各腕n=1生成。
