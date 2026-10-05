# ループ2限定Trial 集計(委任_12、Step 1のみ。Step 2 G armは未実施=STOP)
provenance=fresh Stage 1限定の測定(r3は段階A保存出力の再利用、r5-Vのみfresh)。E2Eではない。Trial(DEV)、Production未変更。
(注: 指示の出力先`..._garm_01`はG arm未実施のため作成せず、Step 1出力dirに本書を置いた。)

## Step 1表(r5-V on 保存r3、42 run、否定案a、保存r3=high・旧否定検査で生成)
| 項目 | 基準(段階A high) | r5-V low | r5-V medium |
|---|---|---|---|
| r5 M検出(SC 18 instance-run) | 17/18 | 1/18(neg5のみ) | 0/18 |
| r3 M検出(保存再利用) | 16/18 | 16/18 | 16/18 |
| ∪M | 18/18 | 16/18 | 16/18 |
| A4-0 r5-V M | 3/3必須 | 0/3 | 0/3 |
| hold-out M検出 | 9/9 | 9/9(r3) | 9/9(r3) |
| neg5 r5-V M | - | 1/3 | 0/3 |
| NORMAL候補∪/記事(r3 23.5) | 24.0 | 23.83(r5-V 0.92) | 23.75(r5-V 0.58) |
| 費用/call・/run | ¥0.763・¥1.51 | ¥0.441・¥0.137 | ¥0.500・¥0.243 |
| 総費用(75 call) | ¥63.35 | ¥5.741 | ¥10.187 |
| worst run | ¥2.71 | ¥0.313 | ¥0.523 |
| runs_over_3jpy / API失敗 / 欠落ID | -/1/0 | 0/0/0% | 0/0/0% |
見積(script mid): low ¥16.63(委任_11目安¥14.5)、medium ¥23.86(同¥20.8)に対し実績は大幅に下回る(+30%超なし)。

## 判定: 事前基準(low>=17/18 かつ A4-0 3/3)もmediumも未達 → Step 2へ進まない
## 原因切り分け(確認済み・A4-0 s1/s2のrun jsonとコード)
- A4-0 gold=S2.1("completed the exchanges with users")。s1/s2では保存r3がS2.1を一度SUPPORTEDと判定→否定検査(D)で`SUPPORTED->CANDIDATE`に変更(M検出ではない)。
- `r5v_target_units`は「r3最終状態==SUPPORTED」の単位のみ検証対象とする。D変更後の状態は`SUPPORTED->CANDIDATE(...)`で対象外 → r5-VはS2.1を一度も検証していない(s1の対象は3単位S5.4/R:S4.1+S4.2/S6.2のみ)。
- 結論(確認): 失敗はeffort(low/medium)では説明できない構造要因(D変更単位がr5-V対象から落ちる)。medium・lowで同じ結果。
- 補足(確認): 段階Aのr5(full)はS2.1を3/3でMとして検出していた=r5はr3の誤SUPPORTEDを拾う経路として機能していた。r5-Vは「r3 SUPPORTED」が前提のため、r3モデル誤判定→D救済の単位を見落とす。
- 推測(未検証): D変更単位(`SUPPORTED->CANDIDATE`)もr5-V対象に含めれば解消する可能性。ただし設計変更で、本委任範囲外(未実装)。
- r5-Vが関係単位R:S4.1+S4.2をM検出している(s1/s3 medium)ことは確認。r5-Vの検証能力自体の否定ではない。

## Step 2(G arm)/(iii)見込み
未実施(STOP)。(iii)見込みは更新不能。委任_11時点の推測(別案1 NORMAL +2.5〜+3.3、+2未達見込み)を据え置き。ただしr5-V候補が少ない実測(0.6〜0.9件/記事)により、r5-Vが追加する候補数・Stage 2負荷は小さいことは確認(Stage 1費用は¥0.14〜0.24/run、r5-V分のみ)。r3のhigh維持分(¥約1.2/run)は未測定。Human Review 0はE2Eでしか判定不能。
## 費用
本委任 ¥15.93(low 5.741+medium 10.187)、本管理ID累計 ¥80.13 / 枠¥238(委任_12 Guardrail ¥60内)。
