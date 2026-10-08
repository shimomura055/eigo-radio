# HUMAN_CHECK_FL(重大候補、ユーザー確認用。LLM単独判定、人間確認前)

重大判定は全2件。最大10件をセルが偏らないよう巡回して列挙(MAP開封後のためセル表示あり。先入観に注意)。

## 1. [baseline] baseline/meta/b3/r1(評価者=gpt-5.6-luna)
- NG文: in one case in which Meta was asked to negotiate internet and cable bills
- fact_id: MUSE-HC-011 / 型: subject / 存在: R0=False R2=False EN=True
- 判定理由: 台帳では、Museにインターネット・ケーブル料金の交渉を依頼したのはMetaの従業員である。ENは「Meta was asked」とし、依頼を受けた主体をMeta社に置き換えている。
- 原文: `er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b3__baseline__r1/ja_writer/revision2.md` / `er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b3__baseline__r1/b1b/article.md`
- 台帳: `er052_output/open233_polysemy_trial_02/ledgers/meta/control/research_ledger/verified_fact_ledger.txt`

## 2. [all6] all6/space_weapons/b2/r1(評価者=gpt-5.6-luna)
- NG文: 「配備が確認されたことと、条約に違反するかどうかは別問題です」／“The fact that deployment has been confirmed and whether it breaks the treaty are separate questions.”
- fact_id: F-001 / 型: added_fact / 存在: R0=False R2=True EN=True
- 判定理由: 台帳が確認しているのは、米国が軌道上兵器の配備を公式に認めたという発言であり、配備そのものが確認済みだという事実ではない。R2とENは公式発表・認識を越えて、実際の配備が確認されたと断定している。
- 原文: `er052_output/all6_writer_redesign_necessity_01/runs/space_weapons/control/b2__all6__r1/ja_writer/revision2.md` / `er052_output/all6_writer_redesign_necessity_01/runs/space_weapons/control/b2__all6__r1/b1b/article.md`
- 台帳: `er052_output/open233_polysemy_trial_02/ledgers/space_weapons/control/research_ledger/verified_fact_ledger.txt`
