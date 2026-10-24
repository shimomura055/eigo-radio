# AGREE_06_FINAL: Trial_06 Fable+Opus二重判定集計(厳しい側採用、継承ラベル含む。委任_33、API 0)

## 0. 公式script出力(`py er112_kp_gm_trial_06_blind2.py agree --labels1 TRIAL_06/fable_labels_06.json --labels2 TRIAL_06/opus_labels_06.json` 逐語。注: 同scriptのdistは盲検表に載らない同一文字列行[38行]を除くため、下の補足表[全行を継承ラベルで補完]と数が異なる)
```
一次(Fable/継承)対第二評価者: 比較可能100 厳密一致83(83%) PASS/非PASS一致83(83%)
ラベル欠落の出力行: 38(盲検表から除外した同一文字列行を含む。同一文字列は継承で埋まる)
('HC', 'B0p') {'PASS': 13, 'FAIL_LIT': 1, 'THIN': 4}
('HC', 'X2pp') {'PASS': 14, 'THIN': 4}
('R', 'X2pp') {'PASS': 4, 'THIN': 2, 'FAIL_LIT': 1}
('S2', 'B0p') {'PASS': 29, 'FAIL_LIT': 2, 'THIN': 3, 'FAIL': 1}
('S2', 'X2pp') {'PASS': 28, 'THIN': 7}
('HC', 'B0p=PASS -> X2pp<=THIN') 2
     ('legs fail someone', 2, 'THIN', '誰かの脚が体を支えられなくなる')
     ("keep one's eyes on them", 2, 'THIN', '人々から目を離さない')
('HC', 'PASS->THIN') 2
     ('legs fail someone', 2, 'THIN', '誰かの脚が体を支えられなくなる')
     ("keep one's eyes on them", 2, 'THIN', '人々から目を離さない')
('HC', 'THIN->PASS(改善)') 2
     ('feel like friction', 1, 'PASS', '邪魔なもののように感じる')
     ('feel like friction', 2, 'PASS', '邪魔に感じる')
('S2', 'PASS->THIN') 7
     ('keep someone company', 1, 'THIN', '人の話し相手になる')
     ('grow lighter', 1, 'THIN', '気持ちが軽くなる')
     ("shock someone's wallet", 1, 'THIN', '人の財布をびっくりさせる')
     ('not the same picture', 1, 'THIN', '同じ傾向ではない')
     ('take off an ai costume', 1, 'THIN', 'AIのふりをやめて人間だと明かす')
     ("reach for someone's wallet", 1, 'THIN', '支払いに備えて誰かの財布に手を伸ばす')
     ('too broad a label', 1, 'THIN', '大ざっぱすぎる呼び方')
```

## 補足集計(全出力行を継承ラベルで補完。script: 作業用、ラベル欠落行=0)
## (a) Fable-Opus一致率(100セル)
- ラベル完全一致 83/100 (83%) / PASS・非PASS二値一致 83/100 (83%)
- 不一致セル(Fable→Opus): 4:B PASS→THIN, 5:A PASS→THIN, 10:B PASS→THIN, 15:A PASS→THIN, 17:A THIN→PASS, 19:A PASS→THIN, 20:B PASS→THIN, 22:C PASS→THIN, 26:B PASS→THIN, 28:B PASS→THIN, 29:A PASS→THIN, 31:A PASS→THIN, 33:A PASS→THIN, 33:B THIN→PASS, 37:B PASS→THIN, 45:C PASS→THIN, 49:B PASS→THIN

## (b) arm別分布(出力行単位。継承で埋まる同一文字列行も含む。ラベル欠落行=0)
| 集合 | arm | 行数 | Fable単独 | Opus単独 | 厳しい側(継承込み) |
|---|---|---|---|---|---|
| HC | B0p | 18 | PASS=15 THIN=2 FAIL_LIT=1 | PASS=15 THIN=2 FAIL_LIT=1 | PASS=13 THIN=4 FAIL_LIT=1 |
| HC | X2pp | 18 | PASS=18 | PASS=14 THIN=4 | PASS=14 THIN=4 |
| R | X2pp | 7 | PASS=6 THIN=1 | PASS=5 THIN=2 | PASS=4 THIN=2 FAIL_LIT=1 |
| S2 | B0p | 54 | PASS=52 FAIL_LIT=2 | PASS=49 THIN=3 FAIL_LIT=2 | PASS=48 THIN=3 FAIL_LIT=2 FAIL=1 |
| S2 | X2pp | 54 | PASS=52 THIN=2 | PASS=47 THIN=7 | PASS=47 THIN=7 |

## (c) X2ppの非PASS全セル(出力行単位、同一文字列は重複せず1セルとして列挙)
| セル | KP | 集合 | 文字列 | 継承 | Fable | Opus | 厳しい側 | rep/set |
|---|---|---|---|---|---|---|---|---|
| 33:A | story with two different speeds | HC | 二つの動きが異なるペースで進む状況 | None | PASS | THIN | THIN | 1 |
| 20:B | keep one's eyes on them | HC | 人々から目を離さない | None | PASS | THIN | THIN | 2 |
| 19:A | keep someone company | S2 | 人の話し相手になる | PASS | PASS | THIN | THIN | 1 |
| 24:B | grow lighter | S2 | 気持ちが軽くなる | PASS | THIN | THIN | THIN | 1 |
| 50:B | shock someone's wallet | S2 | 人の財布をびっくりさせる | None | THIN | THIN | THIN | 1 |
| 22:C | legs fail someone | HC | 誰かの脚が体を支えられなくなる | None | PASS | THIN | THIN | 2 |
| 15:A | come down | R | 値下がりする | PASS | PASS | THIN | THIN | 1 |
| 49:B | not the same picture | S2 | 同じ傾向ではない | PASS | PASS | THIN | THIN | 1 |
| 17:A | question shaped like a trophy | R | 賞の形をした問いかけ | FAIL_LIT | THIN | PASS | FAIL_LIT | 1 |
| 5:A | greener grass | R | 他人の暮らしのほうがよく見えること | PASS | PASS | THIN | THIN | 1 |
| 31:A | take off an ai costume | S2 | AIのふりをやめて人間だと明かす | None | PASS | THIN | THIN | 1 |
| 28:B | reach for someone's wallet | S2 | 支払いに備えて誰かの財布に手を伸ばす | None | PASS | THIN | THIN | 1 |
| 4:B | too broad a label | S2 | 大ざっぱすぎる呼び方 | None | PASS | THIN | THIN | 1 |

## (d) 退行・改善件数(Stage 2はB0最良=B0p+B0_t4継承を基準)
| 区分 | Fable単独 | Opus単独 | 厳しい側 |
|---|---|---|---|
| ('HC', 'PASS->THIN') | 0 | 4 | 2 |
| ('HC', 'THIN->PASS') | 2 | 2 | 2 |
| ('S2', 'PASS->THIN') | 2 | 7 | 7 |
| HC B0p=PASS->X2pp<=THIN | 0 | 4 | 2 |

厳しい側 HC B0p=PASS->X2pp<=THIN (2):
- ('legs fail someone', 2, 'THIN', '誰かの脚が体を支えられなくなる')
- ("keep one's eyes on them", 2, 'THIN', '人々から目を離さない')

厳しい側 ('HC', 'PASS->THIN') (2):
- ('legs fail someone', 2, 'THIN', '誰かの脚が体を支えられなくなる')
- ("keep one's eyes on them", 2, 'THIN', '人々から目を離さない')

厳しい側 ('HC', 'THIN->PASS') (2):
- ('feel like friction', 1, 'PASS', '邪魔なもののように感じる')
- ('feel like friction', 2, 'PASS', '邪魔に感じる')

厳しい側 ('S2', 'PASS->THIN') (7):
- ('keep someone company', 1, 'THIN', '人の話し相手になる')
- ('grow lighter', 1, 'THIN', '気持ちが軽くなる')
- ("shock someone's wallet", 1, 'THIN', '人の財布をびっくりさせる')
- ('not the same picture', 1, 'THIN', '同じ傾向ではない')
- ('take off an ai costume', 1, 'THIN', 'AIのふりをやめて人間だと明かす')
- ("reach for someone's wallet", 1, 'THIN', '支払いに備えて誰かの財布に手を伸ばす')
- ('too broad a label', 1, 'THIN', '大ざっぱすぎる呼び方')

## R集合(元難例、X2pp)
- fable: {'PASS': 6, 'THIN': 1}
- opus: {'PASS': 5, 'THIN': 2}
- strict: {'PASS': 4, 'THIN': 2, 'FAIL_LIT': 1}

## (e-機械) 持ち込み検出(record-only)hit
- B0p rep1 KP=keep one's eyes on them 文字列=相手から目を離さない flags=['neg_in_gloss_not_in_kp'] 厳しい側=PASS
- B0p rep2 KP=keep one's eyes on them 文字列=彼らから目を離さない flags=['neg_in_gloss_not_in_kp'] 厳しい側=PASS
- X2pp rep1 KP=keep one's eyes on them 文字列=自分の目を彼らから離さない flags=['neg_in_gloss_not_in_kp'] 厳しい側=PASS
- X2pp rep2 KP=feel borrowed 文字列=自分のものではないように感じる flags=['neg_in_gloss_not_in_kp'] 厳しい側=PASS
- X2pp rep2 KP=keep one's eyes on them 文字列=人々から目を離さない flags=['neg_in_gloss_not_in_kp'] 厳しい側=THIN
- X2pp rep1 KP=fill in 文字列=足りないところを補う flags=['neg_in_gloss_not_in_kp'] 厳しい側=PASS
- X2pp rep1 KP=behind the scenes 文字列=表に出ずに flags=['neg_in_gloss_not_in_kp'] 厳しい側=PASS

## (g) Family別(HC 18行の内訳)
- Z小説5KP fable B0p: {'PASS': 10}
- Z小説5KP fable X2pp: {'PASS': 10}
- Z小説5KP opus B0p: {'PASS': 9, 'THIN': 1}
- Z小説5KP opus X2pp: {'PASS': 8, 'THIN': 2}
- Z小説5KP strict B0p: {'PASS': 9, 'THIN': 1}
- Z小説5KP strict X2pp: {'PASS': 8, 'THIN': 2}
- X(HC残り4KP) fable B0p: {'PASS': 5, 'FAIL_LIT': 1, 'THIN': 2}
- X(HC残り4KP) fable X2pp: {'PASS': 8}
- X(HC残り4KP) opus B0p: {'PASS': 6, 'FAIL_LIT': 1, 'THIN': 1}
- X(HC残り4KP) opus X2pp: {'PASS': 6, 'THIN': 2}
- X(HC残り4KP) strict B0p: {'PASS': 4, 'FAIL_LIT': 1, 'THIN': 3}
- X(HC残り4KP) strict X2pp: {'PASS': 6, 'THIN': 2}

## (c-理由種別) X2pp非PASS 13セルの理由種別(Opus理由=OPUS_EVAL_06.md、Fable=FABLE_LABELS_06_NOTES.md)
| セル | KP | 理由種別 |
|---|---|---|
| 4:B | too broad a label | ずれ(狭い。「大ざっぱ」は粗い・不正確寄り) |
| 5:A | greener grass | 説明的(名詞なのに「〜こと」) |
| 15:A | come down | 持ち込み(対象:価格。語義選択は正しい) |
| 17:A | question shaped like a trophy | 字義訳(継承ラベルFAIL_LIT。今回Fable=THIN[含意欠落]・Opus=PASS) |
| 19:A | keep someone company | ずれ(狭い。話し相手に限る) |
| 20:B | keep one's eyes on them | 持ち込み(対象:themを「人々」に特定。過剰解釈ではない) |
| 22:C | legs fail someone | 説明的(「誰かの」が不自然) |
| 24:B | grow lighter | 持ち込み(主語:胸の重み→気持ち) |
| 28:B | reach for someone's wallet | 説明的(支払いに備えて。他人の財布で払う読みも) |
| 31:A | take off an ai costume | 説明的/持ち込み(主語:人間だと明かす) |
| 33:A | story with two different speeds | 説明的(長い「〜状況」句) |
| 49:B | not the same picture | ずれ(狭い。傾向に狭めた/対象の持ち込み) |
| 50:B | shock someone's wallet | 字義的(擬人化の字義のまま、意味の伝達が弱い。Fable/Opus一致THIN) |
- 種別の集計: 説明的5(5:A/22:C/28:B/31:A/33:A) / 持ち込み3(15:A/20:B/24:B) / ずれ(狭い)3(4:B/19:A/49:B) / 字義系2(17:A継承/50:B)。**字義訳級(意味の誤り)の新規発生0**、含意欠落は継承17:Aのみ。

## (d) TRIAL_DESIGN_07 §3 事前基準 vs 実測(3通り)
| 基準 | 値 | Fable単独 | Opus単独 | 厳しい側(継承込み) |
|---|---|---|---|---|
| (b)(1) HC FAIL系 X2pp<=B0p | B0p 1 / X2pp 0 | 達成 | 達成 | 達成 |
| (b)(2) B0p=PASS->X2pp<=THIN が0 | 実測 | 0 達成 | 4(story除く8KP: 2) 不適合 | 2(legs fail someone rep2, keep one's eyes on them rep2) 不適合 |
| (b)(3) HC THIN X2pp<=B0p+1 | B0p / X2pp | 2 / 0 達成 | 2 / 4 不適合(>3) | 4 / 4 達成 |
| (b)(4) HC 持ち込み検出が増えない | B0p 2 -> X2pp 3 | 不適合(機械検出、3通り共通) | 同左 | 同左 |
| (b') R FAIL系0 かつ THIN<=2 | R 7出力 | FAIL 0 / THIN 1 達成 | FAIL 0 / THIN 2 達成 | FAIL_LIT 1(17:A継承) 不適合 |
| (c)(1) S2 PASS->FAIL系 0 | 実測 | 0 達成 | 0 達成 | 0 達成 |
| (c)(2) S2 PASS->THIN<=2/54 | 実測 | 2 達成 | 7 不適合 | 7 不適合 |
| (c)(3) 全itemADOPT(HR=0) | ALIGN_PASS以外0 / retry 0 | 達成 | 達成 | 達成 |
| (c)(4) S2 持ち込み検出<=3 | S2 X2pp 1(fill in) | 達成 | 達成 | 達成 |
- 注: Fable単独のHC/R/S2ラベルには継承ラベル(Trial_04/05由来)を補完。「厳しい側」はFable・Opus・継承の3者のmin。S2 PASS->THIN 7件の内訳=keep someone company / grow lighter / shock someone's wallet / not the same picture / take off an ai costume / reach for someone's wallet / too broad a label。うちFable単独THINは grow lighter / shock someone's wallet の2件、他5件はOpus単独THIN。
- 全基準を満たすのはFable単独のみ(ただしFable単独でも(b)(4)が不適合)。**Opusとのラベル不一致17/100セルは全て「Fable PASS→Opus THIN」15件+「Fable THIN→Opus PASS」2件(17:A・33:B)**。厳密一致83%(>=70%のため『基準が曖昧』警告は不要)、Opusが厳しい側に偏る。

## (e) 持ち込み検出(record-only)hit 7件の目視(機械検出の説明のみ。合否ラベルには使わない)
| arm/集合 | KP | 文字列 | 真の持ち込み/偽陽性 |
|---|---|---|---|
| B0p HC rep1 | keep one's eyes on them | 相手から目を離さない | 偽陽性(「離さない」は定訳に内在する否定) |
| B0p HC rep2 | keep one's eyes on them | 彼らから目を離さない | 偽陽性(同上) |
| X2pp HC rep1 | keep one's eyes on them | 自分の目を彼らから離さない | 偽陽性(同上。ただし直訳調) |
| X2pp HC rep2 | keep one's eyes on them | 人々から目を離さない | 否定は偽陽性。ただし「人々」への特定はOpus THIN(20:B、対象の持ち込み) |
| X2pp HC rep2 | feel borrowed | 自分のものではないように感じる | 偽陽性寄り(borrowedの語義「自分のものでない」の言い換え) |
| X2pp S2 rep1 | fill in | 足りないところを補う | 偽陽性(「足りない」はfill inの語義[空白を埋める]に内在) |
| X2pp R rep1 | behind the scenes | 表に出ずに | 偽陽性寄り(「ずに」はbehind the scenesの語義[表に出ない]に内在) |
- 7件中、否定の持ち込みとして真と言えるものは0。**機械件数の増加(HC 2->3、全体2->5)は、否定語を語義の言い換えに使うX2pp文字列が増えたことによる偽陽性主体**。ただしX2ppは語義を言い換える傾向が強く、「説明的」「対象の持ち込み」のTHIN級は増えている(上表(c-理由種別))。

## (f) 費用・時間(METRICS_06.md)
- S2単価(本番構成): B0p 0.0266円/KP、X2pp 0.0704円/KP(2.6倍)。1記事セット(約10KP)換算増分 **0.438円(70円目標の0.63%)**。
- level(1 call)あたり時間増分 **25.8s**(X2pp 38.6s - B0p 12.8s)。記事セットあたりの推定時間増分=level数×25.8s(1 levelなら25.8s、2 levelなら51.6s)。Trial_06 S2全体(33 level・161KP)での合計増分=850.9s(1273.4-422.4)、KP当たり約5.3s(10KPなら約53s)。2 worker並列実行下の参考値。
- Trial_06総費用19.306円(102 call)。HC/R/S2全call ALIGN_PASS、retry 0。

## (g) Family別
- HC 18行の内訳(Fable単独 / Opus単独 / 厳しい側):
  - Z小説5KP(keep one's eyes on them / legs fail someone / one's face harden / sheltered from the rain / smile through one's tears、10出力/arm): B0p PASS10 / PASS9+THIN1 / PASS9+THIN1; X2pp PASS10 / PASS8+THIN2 / PASS8+THIN2(THINはkeep one's eyes on them rep2・legs fail someone rep2)。
  - X(HC残り4KP: feel borrowed / feel like friction / jump into action / story with two different speeds、8出力/arm): B0p PASS5+THIN2+FAIL_LIT1 / PASS6+THIN1+FAIL_LIT1 / PASS4+THIN3+FAIL_LIT1; X2pp PASS8 / PASS6+THIN2 / PASS6+THIN2。
  - 読み: **字義訳(FAIL_LIT)の解消はXのHC側で起きた**(B0p 1->X2pp 0、3通りとも)。Z小説5KPはB0pの時点でFAIL系0で、X2ppは改善せず弱いTHIN(Opus基準)が2件増えるのみ。Z小説では比喩KP発生率が低い(2.2%)ためX2p'の利益が小さい。
