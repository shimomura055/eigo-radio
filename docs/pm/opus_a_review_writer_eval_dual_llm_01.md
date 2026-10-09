# Opus条件Aレビュー: WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01(評価方式Trialの設計)

保存元: 委任_01c の委任文に記載された「Opus所見要約」をそのまま転記したもの(出典=本委任文。Opusの原文全文ではなく、Fableが委任文へ要約した版)。保存日 2026-10-09。

## Opus所見要約
1. K10は因果追加型で「問題なし」枠に置けない(M2誤FAILの罠)。K07と同型矛盾。→境界へ。
2. M1「4判定すべてC」はBの扱い未定義。K02のFactには「did not exfiltrate…」が含まれBが擁護しやすい。両Bが人間確認に回らない。→段階判定とB×B扱いの固定。
3. HC-012のA対照が無く、Rollback文一律CでもM1通過。例示「撤回⇔再開」が軸を示唆。→F-19等のA対照追加、例示差替。
4. Bが受け皿になりM3が低く出る。→C不一致率・両B件数併記。
5. P1/P2はluna/astra系=次段階で比較Writerと同系統。本TrialはP1可。P3(Claude subagent)は隔離・再現性から非推奨。
6. eval_items_01.jsonに漏えいなし。notes_for_writer非提示を支持。
7. JSON検証にC+その他/なしの穴。
8. M4はtemperature=0が効くと情報なし。M3線は件数表記。
9. 欠落測定: (a)Fact対応付け、(b)記事1本あたりの確認量(任意ブロック案)。

## Fable判断(委任_01cでの採否)
所見1〜9を採用。反映先: ケース入替え(所見1,3)、PREREGISTRATION_01.md §6追記(所見2,4,8,9a)、EVAL_PROMPT_01.md/eval_prompt_01.txt・runner検証(所見3,7)、MODEL_OPTIONS_COST_01.md §7(所見5)、OPTIONAL_BLOCK_01.md(所見9b)。
