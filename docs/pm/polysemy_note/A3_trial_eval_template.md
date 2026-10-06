# A3: Trial評価表テンプレート(合格基準はFableが記入)
Before参照: 前回P'-TRIAL-01(commit 4ef943f5要約)・E2E_02 meta 5 run。数値は要約からの転記で、REPORT §88未照合。
| 指標 | 測定方法 | 合格基準 | Before参照値 |
|---|---|---|---|
| ①a 多義語検出率(Meta rollback型, n回repeat) | HC-012に注意(多義)が出た回数/n(人手ラベル) | | Before: 台帳明確化なしで復元型誤読3/5(Writer側) |
| ①b 実用notes生成率 | 注意が3要素(曖昧表現・解釈候補・取違え時変質)を含み、原資料に無い意味を確定していない率 | | 前回P'は「原語=rolled back/当面」型で不十分 |
| ①c 復元誤読率 | 最終記事のHC-012文が復元型の件数/n(人手+決定論検査) | | 前回P' After: 0 / Before 3/5 |
| ② 一般化 | 別の多義表現(HF-009/HF-007/HF-012/F002等)で①a,①bを測定、held-out固定 | | 未測定 |
| ③ FP(不要注意率) | 対象NOのFact(上記除外例)に注意が付いた件数/対象NO件数(複数run) | 要記入(発火見込み13/44) | 前回P' 未測定 |
| ④ Fact安全性 | fact_safety_p01.py流用: 本文・scope・conditions・数値・因果・他notesがベース台帳と不変か | 変更0 | 前回P': ④断定強化1件+保留2件 |
| ⑤a Writer自然さ/説明過多 | 前回E3指標流用(人手/AI評価、注意由来の不要な説明の混入) | | |
| ⑤b 逐語追従 | JA R0/R2逐語率(notes文言のWriter出力への転写率) | | 前回P' JA R2逐語率 +16.4pt NG |
| ⑤c EN Entertainment | EN pairwise(ベース対比) | | 前回P' pairwise 2/2維持 |
| ⑥a Checker候補数 | Checker最終候補数 | | 前回P' 8 vs 5(最終状態不変) |
| ⑥b 後段AI判定/Rewrite/再判定 | 件数 | | |
| ⑥c Human Review | 件数 | | |
| ⑥d 最終重大NG/不要重大判定 | 件数(誤爆含む) | 最終重大NG 0 | 前回P' 真の重大NG 0 |
| 費用 | 実費(円) | 上限は別途 | 前回P' ¥34.85/上限¥100 |
注: 評価はTrial専用。Production採用は人間ユーザーのみ(APPROVED_FOR_PRODUCTION)。
