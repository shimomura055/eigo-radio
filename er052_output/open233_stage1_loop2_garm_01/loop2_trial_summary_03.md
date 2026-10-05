# ループ2 G arm 限定Trial 集計(委任_14、fresh Stage 1限定、E2Eではない)
Trial(DEV)、Production未変更。構成: r3 reasoning=medium + r5 5-lite full reasoning=medium + 否定案a、33 run(SC 6x3+hold-out 9+NORMAL 6)。出力: 本dir(runs/、stageA_aggregate.json、run_log_main.json)。

## 結果と基準(M=モデル判定のみ。Dは算入せず)
| 項目 | 基準 | 実測 | 判定 |
|---|---|---|---|
| r3 M(SC 18) | >=16/18 | 16/18(B3 2/3、A4-0 2/3、他3/3) | 合格 |
| r5 M(SC 18) | >=17/18 | 15/18(A4-0 0/3、B3 3/3、他3/3) | 未達 |
| ∪M | 18/18 | 17/18(A4-0 の1/3を r3・r5 とも見逃し) | 未達 |
| hold-out(er009 9) | 9/9 | 9/9 | 合格 |
| neg5 ∪M | 3/3 | 3/3 | 合格 |
| 欠落ID | <=5% | 0%(再実行0) | 合格 |
| API失敗 / 例外 | - | 0 / 0 | - |
| NORMAL候補∪/記事 | 対24.0(案a後20.0) | 21.83(r3 21.5、r5 6.5) | 参考 |
| HF-011監視(B2_hormuz) | - | 本plan対象外(未測定) | - |
- 経路相関(SC 18): r3○r5○ 15、r3○r5× 2、r3×r5○ 0、r3×r5× 1。
- 段階A high(同instance/sample一致33 run)との比較: r3 high M 18/18 → medium 16/18、r5 high 17/18(A4-0 3/3)→ medium 15/18(A4-0 0/3)。effort引下げで検出が落ちた(特にr5のA4-0)。
## 費用(同一33 run mixで比較、Stage 1のみ)
| | high(段階A同run) | medium(G arm) |
|---|---|---|
| r3 /run | ¥0.609 | ¥0.447 |
| r5 /run | ¥0.785 | ¥0.395 |
| 合計 /run | ¥1.394 | ¥0.843(実測 総¥27.80/33 run=¥0.8425) |
- reasoning tokens/call: r3 3,208→1,371、r5 6,900→2,348。worst ¥1.298(neg5 s2)、¥3超 0 run、1 run ¥6超 0。
- 見積 mid ¥33.83 に対し実績 ¥27.80(+30%超なし)。
## 判定規則の適用
r5のみ未達(r3 合格)→**採用構成=r3 medium + r5 high + 否定案a**。追加実行はせず、r5 highは段階A実測(A4-0 3/3、全体17/18)で代替=**混合構成のfresh測定は未実施**。Stage 1費用は合算の推測=r3 medium ¥0.447+r5 high ¥0.785=約¥1.23/run(high構成 ¥1.394に対し約-¥0.16/run、-12%)。∪ M 18/18 は混合構成では未確認(r5 high がA4-0を拾う前提=段階A 3/3)。
- 任意のr5 low SC 18追加は省略(medium で既に未達のため low は有意な情報を足さず、費用目安約¥5超)。
## 所見(推測を含む)
- Cost: (iii)基準でStage 1が約¥1.23 vs V4A実費仮置き¥0.12〜0.55の差が約+¥0.7〜1.1/run、Stage 2増分(NORMAL候補約22/記事)を加えると+¥2超の公算が高い(E2E実測で判定)。
- 構造的所見: r5 mediumのA4-0 0/3は、段階Aで3/3だったことから、reasoning量依存(推測)。
## 費用
本委任 ¥27.80(Guardrail ¥40内)、本管理ID累計 ¥139.71/枠¥238(残約¥98.29)。
