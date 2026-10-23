# POSS_RESCORE_01: WC-06 「誤り9→0」内訳の再採点(API 0、2026-10-23、委任_18)

入力: `er112_output/kp_gm_trial_04/poss_score_detail.json`(rep==1の42件のみ。rep2は委任_17が作成中のため触れない)。採点者=Fable基準を適用した実行層(目視、新規API 0)。
基準(委任文§2-2): 辞書慣例。所有者=動作主自身[物・擬人化含む]→one's許容 / 他者の人→someone's / 動作主でない物・組織→現状維持。
実務上の線引き: 物・組織が動作主自身の場合でも、**辞書に見出し形one'sが載る定型句**(keep one's promise / find one's way / pump one's fist的擬人化)のみ「許容」、定型句でない自由結合(compete through ... presence / question ... methods)で非人にone'sを付けるのは意味関係の誤りとした(Opus WC-06の内訳「7+2」と一致する線引き)。

## 1. 結論(rep1、42件)
| 区分 | C0A(現行+A-1) → C1A(本案) |
|---|---|
| 意味関係の誤り(WRONG) | 7 → 0 (3件は正しいone's/someone'sへ、4件は無変更[its/their]へ) |
| 辞書的に許容できる一般化の後退(`keeps its promise`, `finding its way back`) | C0Aはone's=許容 → C1Aはits(無変更)。意味は壊れない |
| 擬人化の後退(`wallet pumps its fist` x2 unit) | C0Aはone's=許容 → C1Aはits(無変更)。意味は壊れない |
| 不変 | 31件(C0AとC1Aで同一。`turned on its head`は屈折形のみの差) |

従来の表現「誤り9→0」は、**意味関係の誤り7→0、加えて辞書的に許容できる一般化2件+擬人化2件が無変更(its)へ後退**と書くのが正確(Opus WC-06と一致)。C1Aの後退4件はいずれも無変更形であり、WRONG化はない(WC-10条件5を満たす)。
境界注記: `compete through its presence`(phone自身のpresence)と`questioned its methods`(its=paper)は文面が自己参照読みも可能。その読みを許容に回すと、WRONG=5→0・許容後退=4→6件になる(結論の方向は変わらず、後退が増えるのみ)。

## 2. 42件の表
| # | 見出し語(元) | 目視gold | C1Aのrole | C0A(現行+A-1) | C1A(本案) | 区分 | 根拠 |
|---|---|---|---|---|---|---|---|
| 0 | pumps its fist | self | non_person | pump one's fist | pump its fist | 擬人化の後退 | wallet(擬人化)が動作主自身→pump one's fist許容。C1Aはitsへ後退 |
| 1 | in your place | other_person | other_person | in someone's place | in someone's place | 不変 | C0AとC1Aで同一 |
| 2 | held out his hands | self | self | hold out one's hands | hold out one's hands | 不変 | C0AとC1Aで同一 |
| 3 | catch their attention | other_person | other_person | catch someone's attention | catch someone's attention | 不変 | C0AとC1Aで同一 |
| 4 | a piece of your attention | other_person | other_person | a piece of someone's attention | a piece of someone's attention | 不変 | C0AとC1Aで同一 |
| 5 | compete through its presence | non_person | non_person | compete through one's presence | compete through its presence | WRONG解消 | 自由結合。phoneのitsは動作主自身だが定型句でない。非人にone'sを付けると意味関係が崩れる。境界[文面は自己参照可] |
| 6 | enforce their rules | non_person | non_person | enforce someone's rules | enforce their rules | WRONG解消 | C0Aのsomeone'sは「別の人」を示し誤り(組織・場所の規則)。C1Aはtheir維持(one'sも許容だが一般化機会は不問) |
| 7 | out of our hands | self | self | out of one's hands | out of one's hands | 不変 | C0AとC1Aで同一 |
| 8 | find its way back | non_person | non_person | find one's way back | find its way back | 許容一般化の後退 | find one's wayは辞書の見出し形。desk(物)が動作主自身→one's許容。C1Aはitsへ後退(意味は壊れない) |
| 9 | at their own pace | self | self | at one's own pace | at one's own pace | 不変 | C0AとC1Aで同一 |
| 10 | at their own pace | self | self | at one's own pace | at one's own pace | 不変 | C0AとC1Aで同一 |
| 11 | room for their own pace | self | self | room for one's own pace | room for one's own pace | 不変 | C0AとC1Aで同一 |
| 12 | a place of my own | self | self | a place of one's own | a place of one's own | 不変 | C0AとC1Aで同一 |
| 13 | change my surroundings | self | self | change one's surroundings | change one's surroundings | 不変 | C0AとC1Aで同一 |
| 14 | make something your whole life | self | self | make something someone's whole life | make something one's whole life | WRONG解消 | your=総称you(読み手自身)→one's。C0Aのsomeone'sは別人化 |
| 15 | occupy their thoughts | self | self | occupy someone's thoughts | occupy one's thoughts | WRONG解消 | their=動作主自身→one's。C0Aのsomeone'sは別人化 |
| 16 | apply its findings | non_person | non_person | apply one's findings | apply its findings | WRONG解消 | itsは動作主weでない研究。C0Aのone's(=we自身)は誤り |
| 17 | shock your wallet | other_person | other_person | shock someone's wallet | shock someone's wallet | 不変 | C0AとC1Aで同一 |
| 18 | shock your wallet | other_person | other_person | shock someone's wallet | shock someone's wallet | 不変 | C0AとC1Aで同一 |
| 19 | pumps its fist | self | self | pump one's fist | pump one's fist | 不変 | C0AとC1Aで同一 |
| 20 | pump its fist | self | non_person | pump one's fist | pump its fist | 擬人化の後退 | 同上(別unit) |
| 21 | go out of their way | self | self | go out of one's way | go out of one's way | 不変 | C0AとC1Aで同一 |
| 22 | turned on its head | non_person | non_person | turned on its head | turn on its head | 不変 | C0AとC1Aで同一(または屈折形のみの差) |
| 23 | reach for your wallet | self | self | reach for one's wallet | reach for one's wallet | 不変 | C0AとC1Aで同一 |
| 24 | give my word | self | self | give one's word | give one's word | 不変 | C0AとC1Aで同一 |
| 25 | in your place | other_person | other_person | in someone's place | in someone's place | 不変 | C0AとC1Aで同一 |
| 26 | my word | self | self | one's word | one's word | 不変 | C0AとC1Aで同一 |
| 27 | choose their words | self | self | choose one's words | choose one's words | 不変 | C0AとC1Aで同一 |
| 28 | look her in the face | none | none | look someone in the face | look someone in the face | 不変 | C0AとC1Aで同一 |
| 29 | told her the truth | none | none | tell someone the truth | tell someone the truth | 不変 | C0AとC1Aで同一 |
| 30 | lose her job | self | self | lose one's job | lose one's job | 不変 | C0AとC1Aで同一 |
| 31 | put herself in their shoes | other_person | other_person | put oneself in someone's shoes | put oneself in someone's shoes | 不変 | C0AとC1Aで同一 |
| 32 | pulled her own weight | self | self | pull one's own weight | pull one's own weight | 不変 | C0AとC1Aで同一 |
| 33 | runs its course | non_person | non_person | run its course | run its course | 不変 | C0AとC1Aで同一 |
| 34 | keeps its promise | non_person | non_person | keep one's promise | keep its promise | 許容一般化の後退 | keep one's promiseは辞書の見出し形。airline(組織)が動作主自身→one's許容。C1Aはitsへ後退 |
| 35 | take my place | other_person | other_person | take one's place | take someone's place | WRONG解消 | my=話者、動作主=他者(pilot)→someone's。C0Aのone'sは動作主自身と誤解釈 |
| 36 | catches your eye | other_person | other_person | catch someone's eye | catch someone's eye | 不変 | C0AとC1Aで同一 |
| 37 | mind your own business | self | self | mind your own business | mind your own business | 不変 | C0AとC1Aで同一 |
| 38 | raised her voice | self | self | raise one's voice | raise one's voice | 不変 | C0AとC1Aで同一 |
| 39 | admired their courage | other_person | other_person | admire someone's courage | admire someone's courage | 不変 | C0AとC1Aで同一 |
| 40 | questioned its methods | non_person | non_person | question one's methods | question its methods | WRONG解消 | 自由結合。its=paper。定型句でない。境界[文面は自己参照可、設計goldはnon_person] |
| 41 | changed their minds | self | self | change one's mind | change one's mind | 不変 | C0AとC1Aで同一 |

## 3. 注記
- 非所有格の対照item(102件): C0AとC1Aのkey同一99、差3(`poss_score_rep1.txt`)。差3件の中身は本再採点の対象外(rep2の集計で条件2を判定)。
- gold自体: `er112_kp_gm_trial_04_poss.py:25-56`は実行層単独の目視(Opus WC-06指摘)。本再採点も同一gold+Fable基準の適用であり、独立盲検ではない。盲検が必要ならユーザー採否前にFable盲検を別途。
- 本再採点はコード・Trial出力を変更しない(読取のみ)。
