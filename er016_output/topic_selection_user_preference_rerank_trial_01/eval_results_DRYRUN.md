# model_agreement / rerank eval results

**DRY-RUN(ダミーpredicted_score/user_scoreによる動作確認専用。Trial評価として扱わない)**

| Arm | n_paired | Pearson | Spearman | Top20>=5率 | Top10>=5率 | user>=7件数 | Recall(>=7 in Top20) | Top20内<=3件数 |
|---|---|---|---|---|---|---|---|---|
| L | 60 | 0.035 | 0.041 | 0.60 | 0.60 | 25 | 0.24 | 6 |
| T | 60 | -0.022 | -0.009 | 0.60 | 0.80 | 25 | 0.28 | 6 |
| S | 60 | -0.008 | 0.002 | 0.60 | 0.70 | 25 | 0.24 | 5 |
| J | 60 | -0.135 | -0.132 | 0.65 | 0.50 | 25 | 0.24 | 6 |
