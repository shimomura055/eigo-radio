# 評価分担案(OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04、評価はPhase 1/2完了後、評価委任自体は有料callなし)
評価表: docs/pm/polysemy_trial_04/eval_template_5articles.md。ラベル基準: er052_output/open233_prod_e2e_01/labeling_guide_01.md(新基準追加禁止)。
## A 記事別5並列(各委任=1記事のcontrol/nbを段別ラベル+11項目)
slug=meta, hormuz, space_weapons, sewer, ai_control。
- 入力: er052_output/open233_polysemy_trial_04/runs/<slug>/{control,nb}/rep1/ 配下の ledger txt・Note(nb)・B3 brief・ja_writer/original/revision1/revision2・EN記事・nb_provenance_phase*.json、P0a_article_selection.md 6節の対象fact_id行。
- 出力: er052_output/open233_polysemy_trial_04/runs/<slug>/eval/E_<slug>.md(評価表1行x2条件+各段の根拠引用逐語)。Metaは追加で3節「rollback経路」表を必須記入。
- 禁止: Checker結果・Fable判断を見てからラベル付けしない、他slugの結果を見ない、Production file/SSOT変更、有料API、新基準の追加、Metaの成功判定をFableに代わって確定すること(判定欄は「提案」と明記)。
## B 横断(記事別評価と独立並列可)
- Entertainment決定論: `ja_copy_rate_p01.py --ja <revision2.md> --ledger <ledger.txt> --out <json>`、`ent_metrics_p01.py --article <EN article> --ledger <ledger.txt> --out <json>`(5記事x2条件)。出力 runs/<slug>/eval/ent_<cond>.json。
- pairwise: 5記事x順序入替2 call=10 call 約JPY10(N+B vs Control、台帳非提示)。pairwise_p01.pyは定数ハードコードのため引数化版が必要(P4a/Fable判断)。出力 runs/<slug>/eval/pairwise.json。
- Checker副作用集計(候補数・blocking・Rewrite回数・Rewrite hint 400字切り詰めで注意文が欠落したか): runs/<slug>/*/checker/ から集計、承認根拠に使わない。出力 runs/_agg/checker_side_effects.md。
## C Fable統合
A・B結果を照合し、Meta rollback経路が失敗なら他4記事が良好でも単純VALIDATEDにしない。判定(VALIDATED/REJECTED/USER_DECISION_REQUIRED)・REPORT追記・SSOT更新・commitはFable/PM。Production採用は人間ユーザーのみ。
## 順序・並列
A5本・Bは並列可(入力が独立)。Cは直列(全結果依存)。
