# labels_w2 notes(委任_06-W2、label_source=sonnet_w2_2026-10-06、confirmed_by=空欄=推測・未確認)

担当: neg7_meta_prodrunner_b1b / meta_run03_advanced / hormuz_run03_advanced の計24 claim(全件ラベル済)。

## 注意(正直な開示)
- 作業用シート生成前にrun jsonの先頭を確認した際、neg7 claim#19(「In this convenient future, the AI on your screen handles everything for you.」)に付いたStage2のseverity=MAJOR・理由文が目に入った(§3違反の可能性)。他claimの判定列は見ていない。#19はこの影響を避けるためUNDECIDABLEとし、Fable確認へ回す。
- Ledgerはrun jsonではなく`er052_open233_e2e_acceptance_01.prepare_instances()`のfixture(ledger_text/article_text)を使用。
- rewrite_needed列: Rewrite対象かどうかは判定列(floor/final_materiality)を見ないと分からないため、基準書§1-2の定義(Rewrite前の文が重大/軽微ならY、問題なしならN)をclaim単位で適用した仮置き。実際にRewriteされたかは集計scriptが突合する。

## run別集計
| run | claim数 | 重大 | 軽微 | 問題なし | UNDECIDABLE | true_problem Y/N | true_critical Y |
|---|---|---|---|---|---|---|---|
| neg7_meta_prodrunner_b1b | 5 | 0 | 0 | 4 | 1 | 0/4 | 0 |
| meta_run03_advanced | 8 | 0 | 2 | 5 | 1 | 2/5 | 0 |
| hormuz_run03_advanced | 11 | 0 | 0 | 11 | 0 | 0/11 | 0 |
| 計 | 24 | 0 | 2 | 20 | 2 | 2/20 | 0 |

## 重大Y: 0件

## UNDECIDABLE(全件逐語)
1. neg7 / cycle1 / MUSE-HC-002: 「In this convenient future, the AI on your screen handles everything for you.」
   Ledger: 「Museは...ブラウザーを開く、フォームに入力する、ユーザーに代わって交渉するなどの作業を実行できる」(scope: 公式製品設計・機能説明) notes: 「機能の存在を示す事実。実際の性能や成功率を示す事実ではない。」
   理由: 「everything」は誇張だが、冒頭「Imagine...」の仮想Hook内。Hook許容線か軽微かが曖昧。
2. meta_run03_advanced / cycle1 / MUSE-HC-012: 「The company also restored the human concierge feature to the way it had been before, at least for now.」
   Ledger: 「機能を当面ロールバックしたと社内投稿で説明した」 notes: 「『サービス全体を停止した』とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。」
   理由: 巻き戻し(正)とも、機能の再開・復活(方向反転、gold A5-0系)とも読める。【推測】英語として「restored ... feature」は復活と読まれやすく重大寄りの可能性。

## 軽微(Y/N)
- meta_run03_advanced#11 MUSE-HC-006「Behind a service ..., humans were actually making the calls.」: notesは「一部の電話・テスト」限定を要求、当該文は限定なし。直後の文で「test」と補足。
- meta_run03_advanced#14 MUSE-HC-006「They were enjoying the convenience of AI, only to find a human on the other end of the call without realizing it.」: 利用者体験の断定(演出)。かつ「find」と「without realizing」が矛盾気味。

## 境界例の所感(【推測】)
- hormuz#9はfact_idがHF-009だが内容はHF-002(7/13の20%案)。fact_id割当の揺れ。
- hormuz#2「fee collection had not actually begun」はLedger未記載だがHF-003 notesと整合のため問題なしとした。
