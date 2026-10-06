# Trial対象セット 内訳(委任_01b、事前登録)

| 区分 | 項目数 | 合計call(項目数xrepeat) |
|---|---|---|
| 真の反転(gold) | 3 | 9 |
| 忠実(状態変化語あり) | 21 | 21 |
| 忠実(HC-012同fact・状態言及なし) | 17 | 17 |
| 人工反転 | 14 | 14 |
| 非該当(方向性なしfact) | 5 | 5 |
| 曖昧 | 3 | 9 |
| **合計** | 63 | 75 |

label別: {'忠実': 43, '真の反転': 3, '曖昧': 3, '人工反転': 14}

## 人工反転 一覧

| id | 元 | 置換 | 記事文 | 厳密/許容 |
|---|---|---|---|---|
| S-01 | F-01 | 『# The Fee Plan Leaves』→『# The Fee Plan Arrives』 | # The Fee Plan Arrives, But High Oil Prices Stay | REVERSED/UNCLEAR許容 |
| S-02 | F-02 | 『The fee plan vanished』→『The fee plan appeared』 | The fee plan appeared, but oil prices stayed high as tensions around the Strait of Hormuz continued. | REVERSED/UNCLEAR許容 |
| S-03 | F-03 | 『was withdrawn』→『was reinstated』 | What we can see here is that oil prices did not fall across the board immediately after the plan was reinstated. | REVERSED/UNCLEAR許容 |
| S-04 | F-06 | 『left the stage』→『took the stage』 | The fee plan took the stage, but the prices themselves quickly returned. | REVERSED/UNCLEAR許容 |
| S-05 | F-07 | 『left the stage』→『took the stage』 | This time, the fee plan took the stage, but the price did not leave with it. | REVERSED/UNCLEAR許容 |
| S-06 | F-09 | 『was withdrawn』→『was reinstated』 | After the fee plan was reinstated and replaced, Brent crude oil futures briefly lost some of their gains. | REVERSED/UNCLEAR許容 |
| S-07 | F-10 | 『briefly gave up』→『briefly added』 | After the withdrawal and replacement of the fee plan were announced, Brent crude oil futures briefly added some of their gains. | REVERSED/UNCLEAR許容 |
| S-08 | F-12 | 『would drop』→『would launch』 | Trump said he would launch the 20 percent fee plan. | 厳密 |
| S-09 | F-13 | 『left the stage』→『took the stage』 | The 20 percent plan took the stage about one day after it appeared. | 厳密 |
| S-10 | F-14 | 『suddenly appeared』→『suddenly disappeared』 | On July 13, a plan suddenly disappeared to charge a 20 percent fee on cargo passing through the Strait of Hormuz. | 厳密 |
| S-11 | F-16 | 『started』→『stopped』 | In other words, no one had actually stopped collecting the fee. | REVERSED/UNCLEAR許容 |
| S-12 | F-19 | 『pulled back』→『restored』 | For now, Meta has restored the human concierge feature. | 厳密 |
| S-13 | F-20 | 『put the human-call feature back on hold』→『put the human-call feature back in service』 | Meta then temporarily put the human-call feature back in service. | 厳密 |
| S-14 | F-21 | 『The rise』→『The drop』 | The drop was linked to concern about a US sea blockade of Iran, planned for the next day, and energy shipments through the Strait of Hormuz. | 厳密 |

## repeat=3

G-01, G-02, G-03, G-04, G-05, G-06

詳細(Ledger本文逐語・根拠・enum)は testset_01.json。
