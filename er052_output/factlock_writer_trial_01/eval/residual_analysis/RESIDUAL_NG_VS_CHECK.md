# RESIDUAL_NG_VS_CHECK(factlockセルの残存NGと照合(i)(ii)(iii)の突合。既存artifactのみ・¥0・Status=ANALYZED)

盲検採点(eval/judgments, MAP解決)のfactlockセル24本の全NG項目を、各runの factlock_check_r0/r2.json(照合)と JA Fact Check(ja_writer/audit/deviation_checks)に突合。突合(a)は手動の文照合。検出の定義: 狭義=(i)不整合 or (ii)new_specific_claim or (iii)数値不一致、広義=狭義+(i)判定不能。(ii)のuntagged_brief_fact/neutral/hedged、(i)整合は未検出扱い。

## 1. 全NG項目一覧(factlockセル、計14項目: 重大1・軽微8・保留5)

| # | run | 重大度 | 型 | 所在(R0/R2/EN) | NG文(引用) | 起点 |
|---|---|---|---|---|---|---|
| 0 | factlock/meta/b3/r1 | 軽微 | scope | EN | Meta executives admitted it was a mistake to begin testing calls by co | EN_ONLY |
| 1 | factlock/meta/b3/r1 | 軽微 | added_fact | EN | after admitting it had not clearly told call recipients that human sta | EN_ONLY |
| 2 | factlock/meta/b3/r1 | 保留 | - | (保留:所在は突合表(a)参照) | AI Phone-Answering Service | EN_ONLY |
| 3 | factlock/space_weapons/b4/r2 | 軽微 | scope | R0/R2 | 宇宙条約は、地球周回軌道への核兵器など大量破壊兵器の配備や、天体上への兵器設置などを禁じている。 | JA |
| 4 | factlock/space_weapons/b4/r2 | 保留 | - | (保留:所在は突合表(a)参照) | ただし、具体的な装置名や攻撃能力、標的は明らかにされていない。 | JA |
| 5 | factlock/hormuz/b3/r2 | 重大 | causal | R0 | 相場が発表前に近い水準へ戻ったのは、供給への懸念が残ったためだ。 | JA_R0_ONLY |
| 6 | factlock/hormuz/b3/r2 | 軽微 | scope | R2/EN | 供給への懸念はそのまま残ったようだ。 | JA+EN |
| 7 | factlock/meta/b3/r2 | 軽微 | subject | EN | Meta executives also admitted that it was a “mistake” to start tests i | EN_ONLY |
| 8 | factlock/space_weapons/b2/r2 | 保留 | - | (保留:所在は突合表(a)参照) | It can include attacks on orbits, communication links, and parts on th | JA+EN |
| 9 | factlock/hormuz/b3/r1 | 軽微 | subject | R0/R2/EN | 米国とイランの攻撃 | JA+EN |
| 10 | factlock/meta/b4/r2 | 保留 | - | (保留:所在は突合表(a)参照) | 「電話の相手はAIか、人間か」／“who is on the other end of the call: an AI or a perso | JA+EN |
| 11 | factlock/hormuz/b1/r2 | 軽微 | scope | R0/R2 | 湾岸諸国の対米投資 | JA |
| 12 | factlock/hormuz/b1/r2 | 保留 | - | (保留:所在は突合表(a)参照) | いったん縮んだ値上がり幅が、また高い水準へ戻った流れも読みやすくなります。 | JA |
| 13 | factlock/space_weapons/b1/r2 | 軽微 | scope | R0/R2/EN | 天体上の軍事基地や要塞、兵器試験、軍事演習も禁じる。 | JA+EN |

(全項目1記事1評価者。重大の1件(#5)はR0のみに存在しR2/ENでは解消済み。)

## 2. 突合表(a)文の所在 (b)照合(i) (c)照合(ii) (d)照合(iii) (e)JA Fact Check (f)翻訳段由来か

| # | (a) 所在 | (b) (i) | (c) (ii) | (d) (iii) | (e) JA FC | (f) 由来 | 検出 |
|---|---|---|---|---|---|---|---|
| 0 | EN本文のみ(EN B1b)。JA R2対応文=s13『Meta幹部は…ミスと認め』(F3タグ付き) | 対応JA文は整合(ENは照合対象外) | - | 該当なし | JA FC R0/R2とも LEDGER_COMPLIANT(指摘なし) | ENのみ。JAは『幹部』(数不明)で複数形ではない=翻訳段で複数形化 | none |
| 1 | EN本文のみ(EN末尾『In one line』要約文)。JA R2に対応要約文なし(JA s12『誰が電話しているのか、きちんと伝えたのか』は無タグneutral) | 対応JA文なし | JA s12=neutral | 該当なし | 指摘なし(COMPLIANT) | ENのみ。EN段で追加された要約文に生じた | none |
| 2 | ENタイトル『AI Phone-Answering Service』。JAタイトル=『AI電話代行に、人間キャストが登場』 | タイトルは(i)対象外 | JAタイトル=untagged_brief_fact(新規主張扱いではない) | 該当なし | 指摘なし | ENのみ。『電話代行』→『phone-answering』の訳語選択(翻訳段) | none |
| 3 | R0 s17-18 / R2 s23-24 付近(引用文は言い換え。対応文=『また、天体上の軍事基地や要塞、兵器の試験、軍事演習も禁じています』と直前の条約文。R2 s24は無タグ) | R2 s23=untagged_brief_fact扱い, s24=無タグ((i)対象外)。タグ付きs25(F5)は整合 | R0 s18/R2 s24=new_specific_claim(理由:一覧にない条約上の禁止事項を列挙)=検出 | 該当なし | JA FC R0 attempt1が同F-016の天体兵器scopeをMAJOR指摘→attempt2/R2は COMPLIANT(指摘は解消扱い) | JA R0/R2とも存在(EN無し:STOP)=JA由来 | strict(ii new_specific_claim) |
| 4 | R2 s8『具体的なシステム名や攻撃能力、標的は確認されていません』(F1) | 整合 | - | 該当なし | 指摘なし | JA R2のみ(EN無し:STOP) | none |
| 5 | R0 s16『相場が発表前に近い水準へ戻ったのは、供給への懸念が残ったためだ』(F3)。R2には存在しない(R1/R2で解消) | R0 s16=判定不能 | - | 該当なし | JA FC R0 COMPLIANT(指摘なし) | R0のみ(R2/ENに無い) | weak(i 判定不能) |
| 6 | R2 s18『供給への懸念はそのまま残ったようだ』(F1,F2,F3)。R0に無し | 整合 | - | 該当なし | 指摘なし | JA R2に同内容あり(『そのまま残った』)。EN『remain unchanged』はその訳=JA由来 | none |
| 7 | EN本文のみ『Meta executives also admitted…mistake』。JA R2 s12『Metaの幹部は「ミス」だったと認めた』(F3) | 対応JA文は整合 | - | 該当なし | 指摘なし | ENのみ。JA『幹部』が複数形『executives』に(翻訳段) | none |
| 8 | EN本文『attacks on orbits』。JA R2 s18『軌道や通信のつながり、地上の部分への攻撃も含み』(F3) | 整合 | - | 該当なし | 指摘なし | JA R2に同内容あり=JA由来(英語表現の曖昧さ) | none |
| 9 | R0 s13 / R2 s15『米国とイランの攻撃、海上封鎖…』(F3)。EN『attacks by the United States and Iran』 | R0 s13・R2 s15とも整合 | - | 該当なし | 指摘なし(attempt1のMAJORは別箇所『費用の集め方』) | JA R0/R2に存在、ENで主体読みが強まった(JA由来+翻訳で増幅) | none |
| 10 | R2 s15『電話の相手はAIか、人間か』(無タグ)。EN『who is on the other end of the call: an AI or a person』 | タグなし文 | R2 s15=neutral | 該当なし | 指摘なし | JA R2に同内容あり=JA由来 | none |
| 11 | R0 s2 / R2 s3『湾岸諸国の対米投資案件へと主役が交代』(F1,F2) | R0 s2・R2 s3とも整合。(同runのR2 s5『貿易や投資の案件に置き換える』が不整合判定=より正確な文の方が不整合) | - | 該当なし | 指摘なし | JA R0/R2のみ(EN無し:STOP) | none |
| 12 | R2 s12『いったん縮んだ値上がり幅が、また高い水準へ戻った流れ』(F2,F3) | R2 s12=判定不能 | - | 該当なし | 指摘なし | JA R2のみ(EN無し:STOP) | weak(i 判定不能) |
| 13 | R2 s23『天体上の軍事基地や要塞、兵器試験、軍事演習も禁じる』(F5)。R0 s16は無タグ | R2 s23=整合 | R0 s16=untagged_brief_fact(R2は有タグ) | 該当なし | 指摘なし | JA R0/R2に存在。EN『bans military bases and forts on celestial bodies, weapons tests…』も同内容=JA由来 | none |

## 3. 集計
### 3-1. 照合が検出していたNG(修正ループの理論上の削減上限)
- NG9件(重大1+軽微8。保留5は別掲): 狭義検出=1件(#3: (ii)new_specific_claim)、広義検出(+(i)判定不能)=2件(#3、#5[R0のみの重大。R2では既に消えている])。割合: 狭義1/9=11%、広義2/9=22%。
- R2/EN段に残っているNG8件(R0のみの#5を除く)では、狭義1/8=12.5%、広義1/8=12.5%。
- (i)不整合が当たったNG: 0件。(iii)数値不一致が当たったNG: 0件(NG文に数値なし)。
- 保留5件: 広義検出1件(#12: (i)判定不能)。
### 3-2. どの照合も検出していないNG(prompt/照合では届かない残り)
- NG9件中7件(#0,#1,#6,#7,#9,#11,#13)。型: scope 4(#0,#6,#11,#13)、subject 2(#7,#9)、added_fact 1(#1)。
- 共通点: NG文はタグ付きで(i)整合(#6,#9,#11,#13)、または対応JA文が整合(#0,#7)。タグが指す事実と矛盾しない形で、範囲・主体の数・読み取りの広がりが加わった文は整合判定になる。
- 保留5件中4件(#2,#4,#8,#10)も未検出。
### 3-3. ENのみでJAにないNG(翻訳段由来)
- NG9件中3件(#0,#1,#7。全て軽微)。EN軽微6件中3件=50%。保留でも#2(ENタイトル訳語)が該当。JA側照合・JA修正では原理的に届かない。
- EN軽微の残り3件(#6,#9,#13)はJA R2に同内容があるJA由来。#9は翻訳でさらに主体読みが強まった。

## 4. 逆方向: 照合(i)が不整合判定した13文(R2)のうちNGにならなかった文
- 13文中、盲検採点のNG/保留項目と同一文だったもの=0件(13/13がNGにならず)。run単位では13文が8runにまたがり、うちR2にNGがあるrunは1(hormuz/b1/r2、ただしNG文は別文#11)。
- 不整合判定の多くは『タグが指す事実と、その文が支える主張とのずれ』(タグ付け側の問題)で、本文の事実誤りではない可能性が高い(偽陽性候補、または採点側の見落とし候補)。一覧: r2_inconsistent_sentences.json。
- 例3件:
  1. hormuz/b1/r2 s5『翌日には、その償還料を、湾岸諸国による米国との貿易や投資の案件に置き換えると投稿しました。』= 台帳(貿易・投資)に忠実な文が不整合判定(主張『先の投稿の翌日に置換を投稿した』がF2のみでは未支持扱い)。同runで盲検採点がNGにしたのは別文(s3『対米投資案件』、整合判定)。
  2. space_weapons/b3/r2 s23『また、天体上の軍事基地や要塞、兵器の試験、軍事演習も禁じています。』= 不整合判定だが盲検NGなし。同種の文(#13 sw/b1/r2 s23)は整合判定なのに盲検NG。同一事実文で照合と採点の判定が一致しない。
  3. meta/b3/r2 s5『MetaのMuseを通じた電話の一部では…』= 『MuseはMetaのもの』が未支持として不整合判定されたが、盲検採点はこの文をNGにしていない。

## 5. 所見(事実のみ。推奨なし)
- 現行(factlock): JA R2 軽微 5/24=0.21(重大0)、EN 軽微 6/19=0.32(重大0)、保留 5/24=0.21。
- 照合の検出分を全て修正できたと仮定した機械的上限(狭義検出のみ): JA R2 軽微 5→4(0.21→0.17)、EN 軽微 6→6(0.32→0.32。狭義検出の#3はEN本文なし[STOP]のため)。広義(+判定不能)でもR2/EN軽微は同じ。保留 5→4(0.21→0.17、#12)。
- 検出済み不整合を修正に回した場合の軽微/記事の低下余地は、本データでは最大でJA 0.04ポイント(1件)、ENは0。
- 照合の検出外のNGは、R2/EN段に残る8件中7件(88%)。EN軽微6件中3件(50%)は翻訳段由来でJA側照合の対象外。
- 照合(i)の不整合13文はNG/保留と1件も重ならない(0/13)。
- 制約: 盲検採点は1記事1評価者(LLM)で人間確認なし。NG総数が9と小さく、割合の不確実性は大きい。#3の対応文は引用が言い換えのため手動対応づけ。ここでの「検出」は文単位で当たったかの判定であり、修正の成否は見ていない。
