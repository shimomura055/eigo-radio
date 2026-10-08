# HUMAN_CHECK_SWEEP: 重大候補(LLM抽出、人間確認待ち)

性質: 軽量rubric call(gpt-6-luna、JA R2+EN、1記事1 call)が`major`と判定した全件。**LLM抽出であり確定ではない**。人間確認で true/false を付ける(下の列を埋める)。盲検コード→変種は`eval/_private/MAP_SWEEP.json`。

件数: 1件

## H01. X029 (S1 meta/b2) 所在=JA R2/EN
- 該当文: 「電話の相手はAIのはず。」 / “the person on the other end of the phone is supposed to be AI.”
- 種別: object / fact_id: MUSE-HC-006
- 判定理由: 台帳ではMuse経由の一部の電話を人間の契約スタッフがかけ、相手とのやり取りを担当した。ここではAIを電話の相手側に置いており、誰が電話をかけるのかという役割が逆に読める。
- 記事: `er052_output/factlock_writer_trial_01/sweep_01/runs/meta/control/b2__S1__r1/ja_writer/revision2.md`
- 人間確認: (未)  true重大 / false(誤検出) / 境界

