# model_agreement / rerank eval results

**DRY-RUN(ダミーpredicted_score/user_scoreによる動作確認専用。Trial評価として扱わない)**

| Arm | n_paired | Pearson | Spearman | Top20>=5率 | Top10>=5率 | user>=7件数 | Recall(>=7 in Top20) | Top20内<=3件数 |
|---|---|---|---|---|---|---|---|---|
| L | 60 | 0.137 | 0.143 | 0.65 | 0.50 | 21 | 0.38 | 3 |
| T | 60 | 0.000 | -0.000 | 0.55 | 0.50 | 21 | 0.38 | 7 |
| S | 60 | 0.280 | 0.271 | 0.65 | 0.70 | 21 | 0.52 | 5 |
| J | 60 | 0.018 | -0.002 | 0.50 | 0.50 | 21 | 0.33 | 7 |
