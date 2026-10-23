# STD_AUDIT_01: Standard日本語意味のNG原因別内訳(FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_10、API 0・新規生成0・コード変更0)

生成=`AUDIT_01/audit_01_build_std.py`。Trial_03のFable盲検最終判定は `TRIAL_03/FABLE_BLIND_RESULT_03.md:7-17`(blind表の行#・列A〜F)を、`fable_blind_std_03_key.json`でarm/repに復元して適用(復元後のgloss文字列がresults.jsonlと360/360一致することを確認)。行番号はT3=`er112_output/kp_gm_trial_03/results.jsonl`、T2=`er112_output/kp_gm_trial_02/results.jsonl`の1始まり行。

## 0. 結論(先頭)

1. **Trial_03(60 KP×各方式2回=各120出力)のFable最終判定: 確定FAIL G0=3・G2=1・G3=2(各120中。2.5% / 0.8% / 1.7%)。** G0のみ『境界(FAIL寄り)』が別に1件(`settle at` rep2)あり、含めるとG0=4。
2. **原因別(確定FAILの合計=分類合計): G0=字義訳3、G2=字義訳1、G3=文法・意味関係2。** 語義誤認・その他・原因不明は確定FAILでは0(境界のG0 `settle at`が語義誤認)。ただし `reach for someone's wallet` の分類は字義訳/所有者誤りの両読みが可能で、感度を§1に別掲。
3. **薄い(△)は別集計: G0=0、G2=3、G3=4**(計7出力)。NGではない。
4. `draw a line`の厳密形「線を引く」の発生は **Trial_02+03の各5出力中: G0=2、G2=0、G3=0**。変種「はっきりと線を引く」(同じく字義でNG)がG2=1(Trial_03 rep2)。合計の字義NGは G0 2/5・G2 1/5・G3 0/5(Fable集計と一致)。Trial_03単体ではG0は2/2が『一線を引く』(慣用義・許容)で、G0の字義2件はいずれもTrial_02。
5. Fable最終判定とSonnet参考判定の不一致は360出力中 83 セル(§2)。うち78セルはSonnetが薄△・FableがPASSの組で、薄△の基準差が主因。Sonnet FAIL 9(G0 4・G2 3・G3 2)に対しFable確定FAIL 6(+境界1)。
6. Trial_02 Std(難例20+通常6、rep1、n=26/arm)は個別のOpus判定ログが無い。Opus集計: G0 24/26(NG2)・G2 26/26・G3 25〜26/26。G0のNG2件は draw a line「線を引く」(確実)と reach「人の財布に手を伸ばす」(推定)で、いずれも字義訳型(§5)。

## 1. Trial_03 Std: NG原因別内訳(Fable最終判定を正とする、重複なし)

| NG分類 | G0 | G2 | G3 |
|---|---|---|---|
| 字義訳NG | 3 | 1 | 0 |
| 語義誤認NG | 0 | 0 | 0 |
| 文法・意味関係NG | 0 | 0 | 2 |
| その他NG | 0 | 0 | 0 |
| 原因不明 | 0 | 0 | 0 |
| **確定FAIL合計(=分類合計)** | **3** | **1** | **2** |
| 境界(FAIL寄り、上記合計の外・語義誤認) | 1 | 0 | 0 |
| 境界を含む合計 | 4 | 1 | 2 |
| 確定FAIL率(÷120) | 2.5% | 0.8% | 1.7% |
| KP単位のFAIL含有KP数(確定のみ / 境界含む) | 2 / 3 | 1 / 1 | 2 / 2 |

注: FABLE_BLIND_RESULT_03.md:18 の『KP単位でFAILを含むKP: G0=3 KP(reach、unseen clock、settle at)』は**境界の`settle at`を含む**数。出力単位の『G0=3(+境界1)』と数え方が異なる(出力単位の確定3は2KP、境界を含めると4出力・3KP。CONSISTENCY_01.md参照)。

**感度(分類のゆれ)**: `reach for someone's wallet`を所有者誤り(文法・意味関係)として分類した場合 G0=字義訳2+文法・意味関係1、G2=字義訳1、G3=文法・意味関係2。G3の `reach`「誰かの財布」を字義訳とした場合 G3=字義訳1+文法・意味関係1。いずれも確定FAIL合計は不変(3/1/2)。

### 1-1. 確定FAIL・境界の全出力(分類つき)

| arm/rep | KP(型/X-Z) | 日本語出力 | T3行 | 分類 | 分類の根拠 |
|---|---|---|---|---|---|
| G0/rep1 | an unseen clock(T/X) | 目に見えない時計 | 60 | 字義訳NG | Fable記述「目に見えない時計」(字義)(:10) |
| G0/rep2 | an unseen clock(T/X) | 目に見えない時計 | 177 | 字義訳NG | Fable記述「目に見えない時計」(字義)(:10) |
| G0/rep1 | reach for someone's wallet(-/X) | 人の財布に手を伸ばす | 2 | 字義訳NG | Fable記述(FABLE_BLIND_RESULT_03.md:20結論(2))が「人の財布」を比喩表現の字義訳型に分類。盗む読み(:9) |
| G0/rep2 | settle at(P/X) | ～で落ち着く | 191 | 語義誤認NG(境界・FAIL寄り) | Fable記述「市場用語『取引を終える』が落ちる」(:11)。複数語義(落ち着く/取引を終える)から本文に合わない語義を選択 |
| G2/rep2 | draw a line(-/X) | はっきりと線を引く | 212 | 字義訳NG | Fable記述「はっきりと線を引く」(字義)(:8) |
| G3/rep1 | apply one's findings(-/X) | 人の研究結果を当てはめる | 61 | 文法・意味関係NG | Fable記述「itsは自分の。所有者誤り」(:7) |
| G3/rep1 | reach for someone's wallet(-/X) | 誰かの財布に手を伸ばす | 29 | 文法・意味関係NG | 実行層分類(推定): Fableは「盗む読み」(:9)とのみ記述。:20結論(2)は『G2/G3は…所有者誤り…』と述べる。someone'sを他人と解した所有者の取り違え。※G0の同型「人の財布」(字義訳)との分類不一致あり(感度参照) |

### 1-2. 薄い(△)の別集計(NGではない。Fable判定)

| 方式 | 薄(△)出力数 | 一覧(KP/rep/日本語出力) |
|---|---|---|
| G0 | 0 | - |
| G2 | 3 | price tag rep1「値札に表示された価格」; reach for someone's wallet rep2「人が支払いを覚悟する」; standard deviation rep2「データのばらつき具合を表す値」 |
| G3 | 4 | brace yourself for rep2「～に備える」; on the throne rep2「トップの座にいて」; standard deviation rep1「データのばらつきを表す値」; standard deviation rep2「データが平均からどれくらい散らばっているかを表す値」 |

| 方式 | PASS | 薄(△) | 確定FAIL | 境界 | 計 |
|---|---|---|---|---|---|
| G0 | 116 | 0 | 3 | 1 | 120 |
| G2 | 116 | 3 | 1 | 0 | 120 |
| G3 | 114 | 4 | 2 | 0 | 120 |

## 2. Fable最終判定 vs Sonnet参考判定の差(Trial_03、360出力)

| Fable＼Sonnet | PASS | THIN(薄△) | FAIL |
|---|---|---|---|
| PASS | 266 | 78 | 2 |
| THIN | 1 | 5 | 1 |
| FAIL | 0 | 1 | 6 |

方式別(境界はFable側FAILに含む):

| 方式 | Sonnet PASS/薄/FAIL | Fable PASS/薄/FAIL |
|---|---|---|
| G0 | 91/25/4 | 116/0/4 |
| G2 | 88/29/3 | 116/3/1 |
| G3 | 88/30/2 | 114/4/2 |

不一致 83 セル(Fable PASSでSonnetがTHIN/FAIL: 80、FableがTHIN/FAILでSonnetがPASS: 1、その他: 2)。FableがFAILでSonnetがFAIL以外は draw a line G2 rep2(Sonnet薄)の1件。SonnetがFAILでFableがFAIL以外は center stage G2 rep1「注目の的になる」(Fable PASS)・run on G2 rep2「～に沿って動く」(Fable PASS)・reach G2 rep2「人が支払いを覚悟する」(Fable薄△)の3件。

### 2-1. 判定が食い違った全セル(一致しているセルは付表)

| KP | arm/rep | 日本語出力 | Fable | Sonnet | T3行 |
|---|---|---|---|---|---|
| draw a line | G2/rep2 | はっきりと線を引く | FAIL | THIN | 212 |
| reach for someone's wallet | G2/rep2 | 人が支払いを覚悟する | THIN | FAIL | 276 |
| standard deviation | G2/rep2 | データのばらつき具合を表す値 | THIN | PASS | 351 |
| Carry the Load | G0/rep1 | 荷物を運ぶ | PASS | THIN | 19 |
| Carry the Load | G0/rep2 | 荷物を運ぶ | PASS | THIN | 138 |
| Carry the Load | G2/rep1 | 荷物を運ぶ | PASS | THIN | 48 |
| Carry the Load | G2/rep2 | 荷物を運ぶ | PASS | THIN | 278 |
| Carry the Load | G3/rep1 | 荷物を運ぶ | PASS | THIN | 97 |
| Carry the Load | G3/rep2 | 荷物を運ぶ | PASS | THIN | 261 |
| an unseen clock | G2/rep1 | 表には見えない時間の仕組み | PASS | THIN | 174 |
| an unseen clock | G2/rep2 | 表からは見えない時間の流れ | PASS | THIN | 324 |
| an unseen clock | G3/rep2 | 表からは見えない時間の仕組み | PASS | THIN | 313 |
| behind the curtain | G0/rep1 | 舞台裏に | PASS | THIN | 95 |
| behind the curtain | G0/rep2 | 舞台裏に | PASS | THIN | 207 |
| behind the curtain | G2/rep1 | 表に出ずに裏で関わっている | PASS | THIN | 167 |
| behind the curtain | G2/rep2 | 舞台裏にいる | PASS | THIN | 329 |
| behind the curtain | G3/rep1 | 舞台裏で | PASS | THIN | 170 |
| behind the curtain | G3/rep2 | 舞台裏にいる | PASS | THIN | 306 |
| brace yourself for | G2/rep1 | ～に心の準備をする | PASS | THIN | 40 |
| brace yourself for | G2/rep2 | ～に心の準備をする | PASS | THIN | 256 |
| bring in | G2/rep2 | ～を取り入れる | PASS | THIN | 284 |
| bring in | G3/rep2 | ～を取り入れる | PASS | THIN | 274 |
| center stage | G2/rep1 | 注目の的になる | PASS | FAIL | 136 |
| come down | G0/rep1 | 下がる | PASS | THIN | 59 |
| come down | G0/rep2 | 下がる | PASS | THIN | 176 |
| come down | G2/rep1 | 下がる | PASS | THIN | 173 |
| come down | G3/rep2 | 下がる | PASS | THIN | 312 |
| control over time | G3/rep2 | 時間を自分で管理できること | PASS | THIN | 300 |
| gap between | G0/rep2 | ～の間にある隔たり | PASS | THIN | 178 |
| gap between | G2/rep1 | ～の間にある隔たり | PASS | THIN | 143 |
| gap between | G2/rep2 | ～の間にある隔たり | PASS | THIN | 314 |
| gap between | G3/rep1 | ～の間にある隔たり | PASS | THIN | 117 |
| give one's word | G0/rep1 | 約束する | PASS | THIN | 103 |
| give one's word | G2/rep2 | 約束する | PASS | THIN | 354 |
| give one's word | G3/rep1 | 約束する | PASS | THIN | 222 |
| give one's word | G3/rep2 | 約束する | PASS | THIN | 344 |
| grow lighter | G0/rep1 | 軽くなる | PASS | THIN | 92 |
| grow lighter | G0/rep2 | 軽くなる | PASS | THIN | 220 |
| grow lighter | G2/rep1 | 気持ちが軽くなる | PASS | THIN | 247 |
| grow lighter | G2/rep2 | 気持ちが軽くなる | PASS | THIN | 359 |
| grow lighter | G3/rep1 | 軽くなる | PASS | THIN | 210 |
| grow lighter | G3/rep2 | 軽くなる | PASS | THIN | 342 |
| on paper | G0/rep1 | 書面上では | PASS | THIN | 85 |
| on paper | G0/rep2 | 書面上では | PASS | THIN | 226 |
| on paper | G2/rep2 | 書面上では | PASS | THIN | 348 |
| on paper | G3/rep1 | 書面上では | PASS | THIN | 185 |
| pull back | G0/rep1 | 取り下げる | PASS | THIN | 74 |
| pull back | G0/rep2 | ～を取り下げる | PASS | THIN | 195 |
| pull back | G2/rep1 | いったん引き下げる | PASS | THIN | 147 |
| pull back | G2/rep2 | ～を取り下げる | PASS | THIN | 334 |
| pull back | G3/rep1 | ～を取り下げる | PASS | THIN | 157 |
| pull back | G3/rep2 | 取り下げる | PASS | THIN | 294 |
| put on hold | G2/rep2 | ～を一時中断する | PASS | THIN | 328 |
| reach for someone's wallet | G0/rep2 | 誰かが自分の財布に手を伸ばす | PASS | THIN | 123 |
| reach for someone's wallet | G2/rep1 | 人が自分の財布に手を伸ばす | PASS | THIN | 78 |
| reach for someone's wallet | G3/rep2 | 財布に手を伸ばす | PASS | THIN | 265 |
| run on | G0/rep1 | ～に合わせて動く | PASS | THIN | 82 |
| run on | G0/rep2 | ～に合わせて進む | PASS | THIN | 216 |
| run on | G2/rep1 | ～の時間軸で進む | PASS | THIN | 229 |
| run on | G2/rep2 | ～に沿って動く | PASS | FAIL | 338 |
| run on | G3/rep1 | ～の時間軸で進む | PASS | THIN | 154 |
| run on | G3/rep2 | ～に合わせて進む | PASS | THIN | 308 |
| settle down | G0/rep1 | 落ち着く | PASS | THIN | 84 |
| settle down | G0/rep2 | 落ち着く | PASS | THIN | 218 |
| settle down | G2/rep1 | 落ち着く | PASS | THIN | 231 |
| settle down | G3/rep1 | 落ち着く | PASS | THIN | 156 |
| settle down | G3/rep2 | 落ち着く | PASS | THIN | 310 |
| shine a light on | G2/rep2 | ～を明らかにする | PASS | THIN | 255 |
| shine a light on | G3/rep2 | ～を明らかにする | PASS | THIN | 253 |
| speak against someone | G0/rep1 | 人を批判する | PASS | THIN | 105 |
| speak against someone | G0/rep2 | 人を批判する | PASS | THIN | 234 |
| speak against someone | G2/rep1 | 人を批判する | PASS | THIN | 242 |
| speak against someone | G2/rep2 | 人を批判する | PASS | THIN | 356 |
| speak against someone | G3/rep1 | 人を批判する | PASS | THIN | 224 |
| step out | G0/rep1 | 外へ出る | PASS | THIN | 76 |
| step out | G0/rep2 | 外へ出る | PASS | THIN | 197 |
| take off an AI costume | G0/rep1 | AIの衣装を脱ぐ | PASS | THIN | 77 |
| take off an AI costume | G3/rep1 | AIの衣装を脱ぐ | PASS | THIN | 160 |
| take off an AI costume | G3/rep2 | AIの衣装を脱ぐ | PASS | THIN | 297 |
| take the wheel | G2/rep2 | 運転する | PASS | THIN | 283 |
| walk out | G0/rep1 | 歩いて外へ出る | PASS | THIN | 93 |
| walk out | G2/rep1 | 歩いて外へ出る | PASS | THIN | 248 |
| walk out | G3/rep2 | 歩いて外に出る | PASS | THIN | 343 |

## 3. 各NGの実例(ユーザー§3)

### 3-reach: `reach for someone's wallet`(-/X)

- 本文: "That's enough to make you reach for your wallet before the volume button"
- 本文の用法: 音量ボタンより先に、自分(you)の財布を出して支払う/買う気になる、の意。figurative-literal境界
- 正しい意味: gold(GOLD_LABELS_FINAL_01.md reach行): 『(人が)お金を払おうとして財布に手を伸ばす/財布を出す』。不可=『盗む』解釈
- 全6出力(Fable判定/Sonnet参考):

| arm/rep | 日本語出力 | Fable | Sonnet | T3行 |
|---|---|---|---|---|
| G0/rep1 | 人の財布に手を伸ばす | FAIL | FAIL | 2 |
| G0/rep2 | 誰かが自分の財布に手を伸ばす | PASS | THIN | 123 |
| G2/rep1 | 人が自分の財布に手を伸ばす | PASS | THIN | 78 |
| G2/rep2 | 人が支払いを覚悟する | THIN | FAIL | 276 |
| G3/rep1 | 誰かの財布に手を伸ばす | FAIL | FAIL | 29 |
| G3/rep2 | 財布に手を伸ばす | PASS | THIN | 265 |

- NG理由: someone'sを『他人の財布』と取り、盗む/他人の財布に手を伸ばす読みになる(本文は自分の財布を出す意味)。G0 rep1「人の財布に手を伸ばす」・G3 rep1「誰かの財布に手を伸ばす」が該当。G0 rep2「誰かが自分の財布に手を伸ばす」・G2 rep1「人が自分の財布に手を伸ばす」・G3 rep2「財布に手を伸ばす」はPASS。G2 rep2「人が支払いを覚悟する」は動作が消え意訳=薄△。
- 発生状況(確定FAIL): G0=1, G2=0, G3=1

### 3-unseen: `an unseen clock`(T/X)

- 本文: "A coffee price tag may have an unseen clock of its own, separate from the latest news about the market"
- 本文の用法: コーヒーの値札にも、(他とは別に)表からは見えない独自の時間の流れ・仕組みがある、の意(比喩)。normal KPなのでgold無し
- 正しい意味: Fable PASS例(同KPの他出力): 「表には見えない時間の仕組み」「見えないところで時を刻む仕組み」
- 全6出力(Fable判定/Sonnet参考):

| arm/rep | 日本語出力 | Fable | Sonnet | T3行 |
|---|---|---|---|---|
| G0/rep1 | 目に見えない時計 | FAIL | FAIL | 60 |
| G0/rep2 | 目に見えない時計 | FAIL | FAIL | 177 |
| G2/rep1 | 表には見えない時間の仕組み | PASS | THIN | 174 |
| G2/rep2 | 表からは見えない時間の流れ | PASS | THIN | 324 |
| G3/rep1 | 見えないところで時を刻む仕組み | PASS | PASS | 194 |
| G3/rep2 | 表からは見えない時間の仕組み | PASS | THIN | 313 |

- NG理由: 比喩(見えない時間の仕組み)を字義の『時計』で訳し、意味が伝わらない。G0のみ2/2で発生(rep1・rep2とも同一文字列)。G2・G3は『仕組み』『流れ』へ言い換えPASS。
- 発生状況(確定FAIL): G0=2, G2=0, G3=0

### 3-draw: `draw a line`(-/X)

- 本文: "The words draw that line simply"
- 本文の用法: 言葉が『その線(許容/不許容の区別)』をはっきり示す、の意(慣用・figurative)
- 正しい意味: gold確定(GOLD_LABELS_FINAL_01.md末尾『Fable確定』): 許容=一線を引く/区別をはっきりさせる/線引きをする/境界をはっきりさせる。不可=線を引く/境界線を引く(描く動作)
- 全6出力(Fable判定/Sonnet参考):

| arm/rep | 日本語出力 | Fable | Sonnet | T3行 |
|---|---|---|---|---|
| G0/rep1 | 一線を引く | PASS | PASS | 1 |
| G0/rep2 | 一線を引く | PASS | PASS | 110 |
| G2/rep1 | 一線を引く | PASS | PASS | 5 |
| G2/rep2 | はっきりと線を引く | FAIL | THIN | 212 |
| G3/rep1 | 一線を引く | PASS | PASS | 22 |
| G3/rep2 | 区別をはっきりさせる | PASS | PASS | 481 |

- NG理由: G2 rep2「はっきりと線を引く」は『描く動作』の字義訳(『はっきり』を足しても描く動作)。他の5出力は慣用義でPASS。
- 発生状況(確定FAIL): G0=0, G2=1, G3=0

### 3-apply: `apply one's findings`(-/X)

- 本文: "We can't apply its findings directly to everyday meanness or boredom that lasts a long time"
- 本文の用法: 『その研究(its)の知見を日常の悪意や退屈へ直接応用することはできない』。one'sは不定の人称(本文はits)
- 正しい意味: gold: 『(自分の/研究の)結果・知見を(実際の場面に)当てはめる/応用する』
- 全6出力(Fable判定/Sonnet参考):

| arm/rep | 日本語出力 | Fable | Sonnet | T3行 |
|---|---|---|---|---|
| G0/rep1 | 自分の研究結果を応用する | PASS | PASS | 16 |
| G0/rep2 | 自分の研究結果を応用する | PASS | PASS | 142 |
| G2/rep1 | 自分の研究結果を当てはめる | PASS | PASS | 57 |
| G2/rep2 | 自分の研究結果を当てはめる | PASS | PASS | 264 |
| G3/rep1 | 人の研究結果を当てはめる | FAIL | FAIL | 61 |
| G3/rep2 | 自分の研究結果を応用する | PASS | PASS | 263 |

- NG理由: G3 rep1「人の研究結果を当てはめる」はone's/its(自分の・その研究の)を『人の』と他人に取る所有者誤り。他の5出力は『自分の研究結果』でPASS。
- 発生状況(確定FAIL): G0=0, G2=0, G3=1

### 3-settle: `settle at`(P/X)

- 本文: "On July 13, Brent rose 9.59% and settled at $83.30."
- 本文の用法: 市場用語。『Brent rose 9.59% and settled at $83.30』=終値が83.30ドルで取引を終えた
- 正しい意味: Fable PASS例: 「～で取引を終える」(G0 rep1、G2・G3の全出力)。誤り=一般義「落ち着く」
- 全6出力(Fable判定/Sonnet参考):

| arm/rep | 日本語出力 | Fable | Sonnet | T3行 |
|---|---|---|---|---|
| G0/rep1 | ～で取引を終える | PASS | PASS | 65 |
| G0/rep2 | ～で落ち着く | FAIL(境界) | FAIL | 191 |
| G2/rep1 | ～で取引を終える | PASS | PASS | 137 |
| G2/rep2 | ～の水準で取引を終える | PASS | PASS | 321 |
| G3/rep1 | ～で取引を終える | PASS | PASS | 127 |
| G3/rep2 | ～で取引を終える | PASS | PASS | 293 |

- NG理由(境界・FAIL寄り): G0 rep2「～で落ち着く」は市場用語『取引を終える』が落ち、一般義『落ち着く』を選択=語義誤認。G0 rep1・G2・G3の全出力は『取引を終える』でPASS。
- 発生状況(確定FAIL): G0=0, G2=0, G3=0 ／ 境界: G0=1

## 4. `draw a line`(ユーザー指定項目): Trial_02(3rep)+Trial_03(2rep)

| 試行 | arm | rep | 日本語出力 | 『線を引く』系 | 判定 | 行 |
|---|---|---|---|---|---|---|
| T2 | G0 | 1 | 線を引く | 厳密形「線を引く」(字義NG) | NG(gold不可) | 7 |
| T2 | G0 | 2 | 一線を引く | - | OK(gold内。実行層照合) | 81 |
| T2 | G0 | 3 | 線を引く | 厳密形「線を引く」(字義NG) | NG(gold不可) | 80 |
| T3 | G0 | 1 | 一線を引く | - | PASS | 1 |
| T3 | G0 | 2 | 一線を引く | - | PASS | 110 |
| T2 | G0sol | 1 | 線引きをする | - | OK(gold内。実行層照合) | 1 |
| T2 | G0sol | 2 | 境界をはっきりさせる | - | OK(gold内。実行層照合) | 89 |
| T2 | G0sol | 3 | 線引きをする | - | OK(gold内。実行層照合) | 90 |
| T2 | G2 | 1 | 境界をはっきりさせる | - | OK(gold内。実行層照合) | 12 |
| T2 | G2 | 2 | 境界をはっきりさせる | - | OK(gold内。実行層照合) | 84 |
| T2 | G2 | 3 | はっきり区別する | - | OK(gold内。実行層照合) | 85 |
| T3 | G2 | 1 | 一線を引く | - | PASS | 5 |
| T3 | G2 | 2 | はっきりと線を引く | 変種(字義NG) | FAIL | 212 |
| T2 | G2sol | 1 | 許される範囲をはっきりさせる | - | OK(gold内。実行層照合) | 98 |
| T2 | G2sol | 2 | 区別をはっきりさせる | - | OK(gold内。実行層照合) | 95 |
| T2 | G2sol | 3 | 区別をはっきりさせる | - | OK(gold内。実行層照合) | 101 |
| T2 | G3 | 1 | 区別をはっきりさせる | - | OK(gold内。実行層照合) | 11 |
| T2 | G3 | 2 | 境界をはっきりさせる | - | OK(gold内。実行層照合) | 83 |
| T2 | G3 | 3 | 一線を引く | - | OK(gold内。実行層照合) | 82 |
| T3 | G3 | 1 | 一線を引く | - | PASS | 22 |
| T3 | G3 | 2 | 区別をはっきりさせる | - | PASS | 481 |

| arm | 出力数(T2 3+T3 2) | 厳密形「線を引く」 | 変種(はっきりと線を引く等) | 字義NG計 | 内訳 |
|---|---|---|---|---|---|
| G0 | 5 | 2 | 0 | 2 | T2=2, T3=0 |
| G2 | 5 | 0 | 1 | 1 | T2=0, T3=1 |
| G3 | 5 | 0 | 0 | 0 | T2=0, T3=0 |

参考(T2のみのSolモデル2arm、各3rep): 字義NG G0sol=0(線引きをする×2・境界をはっきりさせる=gold許容)、G2sol=0。『境界線を引く』の発生は0回(全出力に無し)。
注: G3 T3 rep2(T3 行481)は欠損補修の再実行出力(CONSISTENCY_01.md)。補修前の元出力は不明。

## 5. Trial_02 Std(難例20+通常6、rep1、n=26/arm): Opus盲検を正として

**制約: Opus盲検の個別判定ログはrepoに無い。** 保存されているのは集計(OPUS_REVIEW_04.md:5-6,8: G0 24/26・G2 26/26・G3 25〜26/26、薄化指摘5件)と、Fable記述(委任_08 §1:11「G2・G3とも難例の誤り(draw a line字義、reach for someone's wallet『人の財布』=盗む読み)を解消」、OPUS_REVIEW_04.md:5「難例の誤り2種を解消」)のみ。個別NGの同定は下記の通り推定を含む。

| 方式 | n | Opus PASS | Opus NG | NG分類(Opus基準) | Sonnet暫定 PASS | Sonnet暫定NG |
|---|---|---|---|---|---|---|
| G0 | 26 | 24 | 2 | 字義訳NG 2(draw a line「線を引く」=確実／reach「人の財布に手を伸ばす」=推定) | 22 | 4 |
| G2 | 26 | 26 | 0 | - | 22 | 4 |
| G3 | 26 | 25〜26(未確定) | 0〜1 | 0件なら-、1件なら**原因不明**(個別未特定。Sonnet暫定はapply「自分の研究結果を応用する」のみ指摘) | 25 | 1 |

分類合計との一致: G0 字義訳2=NG2、G2 0=0、G3 0〜1(原因不明1が入る場合のみ1)。

### 5-1. Sonnet暫定(gold確定前・draft gold)で不合格とされた全出力(Opusとの差)

| 方式 | KP | 日本語出力 | Sonnet暫定の指摘 | Opus(個別未保存、集計・Fable記述からの推定) | T2行 |
|---|---|---|---|---|---|
| G0 | apply one's findings | 人の研究結果を応用する | deictic(人の研究結果が逐語) | PASS(推定: Opus G0 NG2件=draw a line+reachのため) | 34 |
| G0 | draw a line | 線を引く | sense_ok=0(字義の線を引くで不可) | NG(確実) | 7 |
| G0 | keep someone company | 誰かの話し相手をする | deictic(「誰かの」が指示語的訳出) | PASS(推定: Opus G0 NG2件=draw a line+reachのため) | 43 |
| G0 | reach for someone's wallet | 人の財布に手を伸ばす | deictic(「人の」が逐語訳) | NG(推定) | 10 |
| G2 | apply one's findings | 自分の研究結果を当てはめる | deictic(「自分の」が逐語訳) | PASS(Opus集計G2 26/26) | 50 |
| G2 | keep someone company | 人の話し相手になる | deictic(人の逐語訳) | PASS(Opus集計G2 26/26) | 77 |
| G2 | pump one's fist | 喜んで拳を突き上げる | deictic(喜んでが本文外) | PASS(Opus集計G2 26/26) | 75 |
| G2 | reach for someone's wallet | 人が支払いに備えて自分の財布に手を伸ばす | deictic(人が・自分のを逐語訳) | PASS(Opus集計G2 26/26) | 38 |
| G3 | apply one's findings | 自分の研究結果を応用する | deictic(自分の逐語訳) | 候補(Opus G3「25〜26/26」の未特定1件がこれの可能性。不明) | 41 |

Sonnet暫定のG0 22/26(85%)とOpus 24/26(92%)の差は、Sonnetの『deictic(「人の」「誰かの」の逐語訳)』指摘のうちapply・keep someone companyの2件。G2 22/26(85%)とOpus 26/26(100%)の差4件(reach・apply・pump one's fist『喜んで』・keep someone company)もSonnetのdeictic指摘が主因。

### 5-2. 薄い表現(別集計。Opus盲検の記録 OPUS_REVIEW_04.md:5)

- Opusが挙げた薄化5件(通常KP中心、G3): `brace yourself for`「～に備える」(難例)、`a sense of occasion`「特別感」、`keep someone company`「人の相手をする」、`behind the scenes`「見えないところで」、`on the throne`「トップの座にいる」(難例)。いずれも『NGではなく薄い』扱い。
- G0・G2の薄い判定は**個別未保存(未判定)**。注: G2の `on the throne`(「トップの座にいる」、T2 行57)はG3と同一文字列だが、Opusの薄化列挙はG3に限定されている(理由は不明)。
- 薄化5件は『薄い(△)』であり、§1の確定FAIL表(Trial_03)にも§5の上表のNGにも含めない。

### 5-3. Trial_02 `draw a line` Std 3rep(個別): G0=線を引く/一線を引く/線を引く(T2 行7,81,80)、G2=境界をはっきりさせる/境界をはっきりさせる/はっきり区別する、G3=区別をはっきりさせる/境界をはっきりさせる/一線を引く。字義NGはG0の2(rep1・rep3)のみ(§4)。

## 付表: Trial_03 全360出力(60 KP×G0/G2/G3×rep1,2)

各セル=日本語出力 `[Fable/Sonnet]`。Fable: P=PASS・△=薄・F=FAIL(境界は F*)。Sonnet: P/△/F。T3行は G0r1,G0r2,G2r1,G2r2,G3r1,G3r2 の順。

| blind# | 型/X-Z | KP | G0 rep1 | G0 rep2 | G2 rep1 | G2 rep2 | G3 rep1 | G3 rep2 | T3行 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | hard/X | apply one's findings | 自分の研究結果を応用する [P/P] | 自分の研究結果を応用する [P/P] | 自分の研究結果を当てはめる [P/P] | 自分の研究結果を当てはめる [P/P] | 人の研究結果を当てはめる [F/F] | 自分の研究結果を応用する [P/P] | 16,142,57,264,61,263 |
| 2 | hard/X | brace yourself for | ～に備えて心構えをする [P/P] | ～に備えて心構えをする [P/P] | ～に心の準備をする [P/△] | ～に心の準備をする [P/△] | ～を覚悟する [P/P] | ～に備える [△/△] | 7,122,40,256,36,254 |
| 3 | hard/X | bring in | 持ち込む [P/P] | 持ち込む [P/P] | 取り入れる [P/P] | ～を取り入れる [P/△] | 取り入れる [P/P] | ～を取り入れる [P/△] | 34,151,79,284,71,274 |
| 4 | hard/X | Carry the Load | 荷物を運ぶ [P/△] | 荷物を運ぶ [P/△] | 荷物を運ぶ [P/△] | 荷物を運ぶ [P/△] | 荷物を運ぶ [P/△] | 荷物を運ぶ [P/△] | 19,138,48,278,97,261 |
| 5 | hard/X | draw a line | 一線を引く [P/P] | 一線を引く [P/P] | 一線を引く [P/P] | はっきりと線を引く [F/△] | 一線を引く [P/P] | 区別をはっきりさせる [P/P] | 1,110,5,212,22,481 |
| 6 | hard/Z | execution bell | 処刑を知らせる鐘 [P/P] | 処刑を知らせる鐘 [P/P] | 処刑を知らせる鐘 [P/P] | 処刑を知らせる鐘 [P/P] | 処刑を知らせる鐘 [P/P] | 処刑を告げる鐘 [P/P] | 4,112,15,258,18,245 |
| 7 | hard/X | fire the starting gun | スタートの号砲を鳴らす [P/P] | スタートの合図を出す [P/P] | 始まりの合図を出す [P/P] | スタートの合図を出す [P/P] | 始まりの合図を出す [P/P] | 始まりの合図をする [P/P] | 8,140,27,268,37,259 |
| 8 | hard/X | hold on | ちょっと待って [P/P] | ちょっと待って [P/P] | ちょっと待って [P/P] | ちょっと待つ [P/P] | ちょっと待って [P/P] | ちょっと待つ [P/P] | 25,153,80,277,66,273 |
| 9 | hard/X | jump to conclusions | 早まった結論を出す [P/P] | 早まって結論を出す [P/P] | 早まって結論を出す [P/P] | 早まった結論を出す [P/P] | 早合点する [P/P] | 早合点する [P/P] | 46,162,102,289,100,281 |
| 10 | hard/X | leap into action | すぐに行動を起こす [P/P] | すぐに行動を起こす [P/P] | すぐに行動を起こす [P/P] | すぐに行動を起こす [P/P] | すぐに行動を起こす [P/P] | すぐに行動を起こす [P/P] | 21,134,69,270,47,271 |
| 11 | hard/Z | letter of introduction | 紹介状 [P/P] | 紹介状 [P/P] | 紹介状 [P/P] | 紹介状 [P/P] | 紹介状 [P/P] | 紹介状 [P/P] | 26,152,81,275,70,272 |
| 12 | hard/X | off the hook | 責任を問われずに済む [P/P] | 責任を問われずに済む [P/P] | 責任を問われずに済む [P/P] | 責任を問われずに済む [P/P] | 責任を問われずに済む [P/P] | 責任を問われずに済む [P/P] | 45,161,101,288,99,280 |
| 13 | hard/X | on the throne | 王座に就いている [P/P] | 王座に就いて [P/P] | 頂点に立つ [P/P] | 王座に君臨している [P/P] | 王座に就いている [P/P] | トップの座にいて [△/△] | 20,139,49,279,98,262 |
| 14 | hard/Z | pull someone under | 人を水中に引きずり込む [P/P] | 人を水中に引きずり込む [P/P] | 人を水の中に引きずり込む [P/P] | 人を水中に引きずり込む [P/P] | 人を水中に引きずり込む [P/P] | 人を水中に引きずり込む [P/P] | 10,113,41,249,30,236 |
| 15 | hard/X | reach for someone's wallet | 人の財布に手を伸ばす [F/F] | 誰かが自分の財布に手を伸ばす [P/△] | 人が自分の財布に手を伸ばす [P/△] | 人が支払いを覚悟する [△/F] | 誰かの財布に手を伸ばす [F/F] | 財布に手を伸ばす [P/△] | 2,123,78,276,29,265 |
| 16 | hard/X | refueling support | 給油支援 [P/P] | 給油支援 [P/P] | 給油の支援 [P/P] | 給油による支援 [P/P] | 給油支援 [P/P] | 給油支援 [P/P] | 23,131,72,282,67,266 |
| 17 | hard/Z | sentence someone to death | 人に死刑を言い渡す [P/P] | 人に死刑を言い渡す [P/P] | 人に死刑を言い渡す [P/P] | 人に死刑を宣告する [P/P] | 人に死刑を言い渡す [P/P] | 人に死刑を言い渡す [P/P] | 3,111,14,257,17,244 |
| 18 | hard/X | shine a light on | ～に光を当てる [P/P] | ～に光を当てる [P/P] | ～に光を当てる [P/P] | ～を明らかにする [P/△] | ～に光を当てる [P/P] | ～を明らかにする [P/△] | 6,121,39,255,35,253 |
| 19 | hard/X | take the wheel | ハンドルを握る [P/P] | ハンドルを握る [P/P] | ハンドルを握る [P/P] | 運転する [P/△] | ハンドルを握る [P/P] | ハンドルを握る [P/P] | 24,132,73,283,68,267 |
| 20 | hard/X | turn on its head | ～をひっくり返す [P/P] | それをひっくり返す [P/P] | ～をひっくり返す [P/P] | ～をひっくり返す [P/P] | ～をひっくり返す [P/P] | ～を覆す [P/P] | 9,141,28,269,38,260 |
| 21 | T/X | a place of one's own | 自分だけの場所 [P/P] | 自分だけの場所 [P/P] | 自分だけの場所 [P/P] | 自分だけの場所 [P/P] | 自分だけの場所 [P/P] | 自分だけの場所 [P/P] | 86,227,214,349,186,326 |
| 22 | P/X | add up | つじつまが合う [P/P] | つじつまが合う [P/P] | つじつまが合う [P/P] | つじつまが合う [P/P] | つじつまが合う [P/P] | つじつまが合う [P/P] | 83,217,230,339,155,309 |
| 23 | T/X | an unseen clock | 目に見えない時計 [F/F] | 目に見えない時計 [F/F] | 表には見えない時間の仕組み [P/△] | 表からは見えない時間の流れ [P/△] | 見えないところで時を刻む仕組み [P/P] | 表からは見えない時間の仕組み [P/△] | 60,177,174,324,194,313 |
| 24 | I/X | behind the curtain | 舞台裏に [P/△] | 舞台裏に [P/△] | 表に出ずに裏で関わっている [P/△] | 舞台裏にいる [P/△] | 舞台裏で [P/△] | 舞台裏にいる [P/△] | 95,207,167,329,170,306 |
| 25 | I/Z | catch one's breath | 息を整える [P/P] | 息を整える [P/P] | 息を整える [P/P] | 息を整える [P/P] | 息を整える [P/P] | 息を整える [P/P] | 91,219,246,358,209,341 |
| 26 | I/X | center stage | 注目の中心 [P/P] | 注目の中心 [P/P] | 注目の的になる [P/F] | 注目の中心 [P/P] | 注目の中心 [P/P] | 注目の中心 [P/P] | 64,190,136,320,126,292 |
| 27 | C/X | change one's surroundings | 自分の周りの環境を変える [P/P] | 身の回りの環境を変える [P/P] | 身の回りの環境を変える [P/P] | 自分の周りの環境を変える [P/P] | 身の回りの環境を変える [P/P] | 周りの環境を変える [P/P] | 87,228,215,350,187,327 |
| 28 | P/X | come down | 下がる [P/△] | 下がる [P/△] | 下がる [P/△] | 値段が下がる [P/P] | 値下がりする [P/P] | 下がる [P/△] | 59,176,173,323,193,312 |
| 29 | C/X | control over time | 時間を自分で決められること [P/P] | 時間の使い方を自分で決めること [P/P] | 時間の使い方を自分で決められること [P/P] | 時間の使い方を自分で決められること [P/P] | 時間を自分で調整できること [P/P] | 時間を自分で管理できること [P/△] | 55,180,145,316,119,300 |
| 30 | I/Z | fall to one's knees | ひざまずく [P/P] | ひざまずく [P/P] | ひざをつく [P/P] | ひざまずく [P/P] | ひざまずく [P/P] | ひざまずく [P/P] | 104,233,241,355,223,345 |
| 31 | T/Z | far bank | 向こう岸 [P/P] | 向こう岸 [P/P] | 向こう岸 [P/P] | 対岸 [P/P] | 向こう岸 [P/P] | 向こう岸 [P/P] | 13,116,44,252,33,239 |
| 32 | P/X | fill in | ～を補う [P/P] | 補う [P/P] | 足りないところを補う [P/P] | 足りない部分を補う [P/P] | 足りない部分を補う [P/P] | 補う [P/P] | 96,208,168,330,171,307 |
| 33 | T/X | gap between | ～の間の隔たり [P/P] | ～の間にある隔たり [P/△] | ～の間にある隔たり [P/△] | ～の間にある隔たり [P/△] | ～の間にある隔たり [P/△] | ～の間の隔たり [P/P] | 53,178,143,314,117,298 |
| 34 | C/X | give back gains | 上昇分を失う [P/P] | 上昇分の一部を失う [P/P] | 上昇分の一部を失う [P/P] | 上げ幅を縮める [P/P] | 上昇分を失う [P/P] | 上げ幅を失う [P/P] | 62,188,133,318,124,290 |
| 35 | I/Z | give one's word | 約束する [P/△] | 約束をする [P/P] | 固く約束する [P/P] | 約束する [P/△] | 約束する [P/△] | 約束する [P/△] | 103,232,240,354,222,344 |
| 36 | C/Z | grow lighter | 軽くなる [P/△] | 軽くなる [P/△] | 気持ちが軽くなる [P/△] | 気持ちが軽くなる [P/△] | 軽くなる [P/△] | 軽くなる [P/△] | 92,220,247,359,210,342 |
| 37 | C/Z | hold out a hand | 手を差し出す [P/P] | 手を差し出す [P/P] | 手を差し出す [P/P] | 手を差し出す [P/P] | 手を差し出す [P/P] | 手を差し出す [P/P] | 12,115,43,251,32,238 |
| 38 | T/X | impulse buying | 衝動買い [P/P] | 衝動買い [P/P] | 衝動買い [P/P] | 衝動買い [P/P] | 衝動買い [P/P] | 衝動買い [P/P] | 89,204,183,352,200,332 |
| 39 | I/Z | in one's place | 人の代わりに [P/P] | 人の代わりに [P/P] | 人の代わりに [P/P] | 人の代わりに [P/P] | 人の代わりに [P/P] | 誰かの代わりに [P/P] | 106,235,243,357,225,347 |
| 40 | C/Z | lose trust in someone | 人への信頼を失う [P/P] | 人への信頼を失う [P/P] | 人への信頼を失う [P/P] | 人への信頼を失う [P/P] | 人への信頼を失う [P/P] | 人への信頼を失う [P/P] | 11,114,42,250,31,237 |
| 41 | C/X | move in the other direction | 反対の方向に動く [P/P] | 反対の方向に動く [P/P] | 反対の方向に動く [P/P] | 逆の方向に動く [P/P] | 逆の方向に動く [P/P] | 逆の方向に動く [P/P] | 90,205,184,353,201,333 |
| 42 | I/X | not the same picture | 同じ状況ではない [P/P] | 同じ状況ではない [P/P] | 同じ状況ではない [P/P] | 同じ状況ではない [P/P] | 同じ状況ではない [P/P] | 同じ状況ではない [P/P] | 51,164,129,303,108,286 |
| 43 | I/X | on paper | 書面上では [P/△] | 書面上では [P/△] | 理論上は [P/P] | 書面上では [P/△] | 書面上では [P/△] | 理論上は [P/P] | 85,226,213,348,185,325 |
| 44 | T/X | price tag | 値札 [P/P] | 値札 [P/P] | 値札に表示された価格 [△/△] | 値札 [P/P] | 値札 [P/P] | 値札 [P/P] | 58,175,172,322,192,311 |
| 45 | P/X | pull back | 取り下げる [P/△] | ～を取り下げる [P/△] | いったん引き下げる [P/△] | ～を取り下げる [P/△] | ～を取り下げる [P/△] | 取り下げる [P/△] | 74,195,147,334,157,294 |
| 46 | I/X | put on hold | ～を保留にする [P/P] | 保留にする [P/P] | ～をいったん保留にする [P/P] | ～を一時中断する [P/△] | ～をいったん保留にする [P/P] | ～を保留にする [P/P] | 94,206,166,328,169,305 |
| 47 | C/X | room for one's own pace | 自分のペースで行動できる余地 [P/P] | 自分のペースで過ごせる余地 [P/P] | 自分のペースで過ごせる余地 [P/P] | 自分のペースを保てる余地 [P/P] | 自分のペースで過ごせる余裕 [P/P] | 自分のペースで進められる余裕 [P/P] | 54,179,144,315,118,299 |
| 48 | C/X | room to choose | 選ぶ余地 [P/P] | 選ぶ余地 [P/P] | 選ぶ余地 [P/P] | 選ぶ余地がある [P/P] | 選ぶ余地 [P/P] | 選ぶ余地がある [P/P] | 52,165,130,304,109,287 |
| 49 | P/X | run on | ～に合わせて動く [P/△] | ～に合わせて進む [P/△] | ～の時間軸で進む [P/△] | ～に沿って動く [P/F] | ～の時間軸で進む [P/△] | ～に合わせて進む [P/△] | 82,216,229,338,154,308 |
| 50 | P/X | settle at | ～で取引を終える [P/P] | ～で落ち着く [F*/F] | ～で取引を終える [P/P] | ～の水準で取引を終える [P/P] | ～で取引を終える [P/P] | ～で取引を終える [P/P] | 65,191,137,321,127,293 |
| 51 | P/X | settle down | 落ち着く [P/△] | 落ち着く [P/△] | 落ち着く [P/△] | 安定する [P/P] | 落ち着く [P/△] | 落ち着く [P/△] | 84,218,231,340,156,310 |
| 52 | C/Z | speak against someone | 人を批判する [P/△] | 人を批判する [P/△] | 人を批判する [P/△] | 人を批判する [P/△] | 人を批判する [P/△] | 誰かに反対する発言をする [P/P] | 105,234,242,356,224,346 |
| 53 | P/X | speak for | ～に代わって話す [P/P] | 私たちに代わって話す [P/P] | ～の代わりに話す [P/P] | ～の代わりに話す [P/P] | ～の代わりに話す [P/P] | ～の代わりに話す [P/P] | 75,196,148,335,158,295 |
| 54 | T/X | standard deviation | 標準偏差 [P/P] | 標準偏差 [P/P] | 標準偏差 [P/P] | データのばらつき具合を表す値 [△/P] | データのばらつきを表す値 [△/△] | データが平均からどれくらい散らばっているかを表す値 [△/△] | 88,202,182,351,199,331 |
| 55 | P/X | step out | 外へ出る [P/△] | 外へ出る [P/△] | 姿を現す [P/P] | 姿を現す [P/P] | 外へ出てくる [P/P] | 姿を現す [P/P] | 76,197,149,336,159,296 |
| 56 | I/X | take a sharp turn | 急展開する [P/P] | 急展開する [P/P] | 急展開する [P/P] | 急展開する [P/P] | 急展開する [P/P] | 急展開する [P/P] | 63,189,135,319,125,291 |
| 57 | C/X | take off an AI costume | AIの衣装を脱ぐ [P/△] | AIの着ぐるみを脱ぐ [P/P] | AIの仮面を脱ぐ [P/P] | AIの仮面を脱ぐ [P/P] | AIの衣装を脱ぐ [P/△] | AIの衣装を脱ぐ [P/△] | 77,198,150,337,160,297 |
| 58 | I/X | the new normal | 新しい当たり前 [P/P] | 新たな当たり前 [P/P] | 新しい当たり前 [P/P] | 新たな当たり前 [P/P] | 新しい当たり前 [P/P] | 新しい当たり前 [P/P] | 50,163,128,302,107,285 |
| 59 | T/X | too broad a label | 広すぎるくくり [P/P] | 範囲が広すぎる呼び名 [P/P] | 大まかすぎるくくり [P/P] | 範囲が広すぎる呼び方 [P/P] | 広すぎる呼び方 [P/P] | 広すぎる呼び方 [P/P] | 56,181,146,317,120,301 |
| 60 | P/Z | walk out | 歩いて外へ出る [P/△] | 歩いて出ていく [P/P] | 歩いて外へ出る [P/△] | 歩いて出ていく [P/P] | 歩いて出ていく [P/P] | 歩いて外に出る [P/△] | 93,221,248,360,211,343 |
## Fable確定(2026-10-23、元の推定表記は上に残す。詳細=FABLE_VERIFICATION_01.md)

| 分類 | G0 | G2 | G3 |
|---|---|---|---|
| 字義訳NG | 2(`an unseen clock`×2) | 1(`draw a line`「はっきりと線を引く」) | 0 |
| 文法・意味関係NG(所有者誤り) | 1(`reach for someone's wallet`「人の財布」) | 0 | 2(`apply one's findings`「人の研究結果」、reach「誰かの財布」) |
| 語義誤認・その他・原因不明 | 0 | 0 | 0 |
| 確定FAIL合計 | 3 | 1 | 2 |
| △(用語性欠落、NGではない) | 1(`settle at`「～で落ち着く」。上の「境界」を△に確定) | 3 | 4 |

- reachの「人の財布」(G0)・「誰かの財布」(G3)は所有者誤り(someone'sは本文では自分の)に統一。字義訳ではない。
- FABLE_BLIND_RESULT_03の「G0=3 KP」は境界を含む表記。確定FAIL3出力は2 KP(reach 1、unseen clock 2)。
