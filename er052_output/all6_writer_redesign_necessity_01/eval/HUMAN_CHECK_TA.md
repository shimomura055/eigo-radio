# HUMAN_CHECK_TA(重大候補、ユーザー確認用。LLM単独判定、人間確認前)

重大判定は全2件。以下は最大10件を、armが偏らないよう交互に列挙(MAP開封後のためarm表示あり。確認時の先入観に注意)。

## 1. [baseline] meta/control/b3__baseline__r1(評価者=gpt-6-luna)
- NG文: “callers were not clearly told who was speaking.”
- fact_id: MUSE-HC-012 / 型: object / 存在: R0=False R2=False EN=True
- 判定理由: 開示が適切でなかった相手は電話を受ける側と読める文脈だが、ENの要約では「callers」が知らされなかったとしており、情報を受け取る側を取り違えている。
- 原文: `er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b3__baseline__r1/ja_writer/revision2.md`(JA R2) / `er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b3__baseline__r1/b1b/article.md`(EN)
- 台帳: `er052_output/open233_polysemy_trial_02/ledgers/meta/control/research_ledger/verified_fact_ledger.txt`

## 2. [all6] meta/control/b3__all6__r2(評価者=gpt-5.6-luna)
- NG文: 電話機能は改善を続け、準備が整い、適切な開示ができる場合にだけ公開する方針です。
- fact_id: MUSE-HC-005 / 型: scope / 存在: R0=False R2=True EN=True
- 判定理由: ロールバック対象の人間コンシェルジュ実験ではなく、一般の電話機能全体がまだ公開前であるかのように読める。台帳では電話機能はユーザー向けに段階展開されており、一般機能とロールバックされた人間コンシェルジュ実験を区別する必要がある。対象範囲・状態を取り違えるため重大とした。
- 原文: `er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b3__all6__r2/ja_writer/revision2.md`(JA R2) / `er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b3__all6__r2/b1b/article.md`(EN)
- 台帳: `er052_output/open233_polysemy_trial_02/ledgers/meta/control/research_ledger/verified_fact_ledger.txt`
