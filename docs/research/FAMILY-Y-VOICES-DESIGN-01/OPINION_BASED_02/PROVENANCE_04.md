# PROVENANCE_04 (委任_25: テーマ『宅配の再配達は有料にすべきか?』R0 run_01 の出典対応表。内部記録・リスナーには見せない)

対象: `er110_output/family_y_opinion_based_03/redelivery_fee/run_01/article_ja.md`(確定稿)。書式は`../OPINION_BASED_01/PROVENANCE_TEMPLATE_01.md`+「R2+のみが根拠の文」欄+agent目視判定。生成: `scripts/build_provenance_04.py`(runの`state.json`のluna付番+機械照合の結果と、agentが全21文を読んで付けた列を結合。API 0)。
手順は`PROVENANCE_03.md`と同じ(luna付番 → 機械照合 → UNMAPPEDのVoiceだけ各1回再生成 → agent目視)。**手作業での本文修正は0**。

## 1. 件数
- 初回生成の機械照合UNMAPPED: One Voice 2文 / Another Voice 1文 / A Third Voice 0文。UNMAPPED再生成: One Voice 1回, Another Voice 1回(各Voice1回まで)。
- **再生成後の最終稿の機械照合UNMAPPED(final_map)**: One Voice 0文 / Another Voice 0文 / A Third Voice 1文(規則どおり再生成は各Voice1回までのため、最終稿のUNMAPPEDは記録のみ)。
- agent目視: 機械判定の**偽陽性**と判断した文 **1件**(A Third Voice 第6文=Sheetの矛盾欄THREE_eにそのまま対応)。**要注意**(意味・文脈のずれ、出典にない補い)は **2件**(下表の備考)。**出来事・人物・会話の捏造は0件**。最終稿に残る機械UNMAPPED 1文は上記の偽陽性。
- 世界設定の定義由来の出典外意見: 0件(V1・V2・V3に『物流業界全体の待遇』『環境』の語なし。EVAL_SET_04の逸脱文検査も0)。
- **Gate(Leakage判定)**: runnerは累計22円超で`SKIPPED_BUDGET`にしたため、同一委任内で後追い実行 -> **PASS**(判定1回、flagged False、書換0、本文不変。`gate_status_original`=SKIPPED_BUDGET を`state.json`・`run_status.json`に残した)。
- 判定の限界: lunaの付番はIDの付け間違い・取りこぼしがある(例: Another Voice 第1文にTWO_eが付いたが本文に該当内容なし)。IDの正しさはagent目視で補ったが、**1名(1agent)の目視であり、独立した第二者の確認ではない**。

## 2. 対応表(1行=1文)
| Voice | 位置 | 文 | 経験欄ID(根拠の声ID) | 根拠URL | 補った表現(luna種別) | 機械判定 | agent判定 | 備考(要注意・偽陽性) |
|---|---|---|---|---|---|---|---|---|
| One Voice | 第1文 | 不在票を入れて帰るときは、私もやはり少し気持ちが沈む。 | ONE_c(RV-55) | https://note.com/z1kata3ne/n/n4f3f3ee2107d | なし | OK | OK | ONE_c(不在票を入れて帰るときの気持ち。RV-55の趣旨を自分の言葉で) |
| One Voice | 第2文 | でも、そのまま次の家へ向かう。 | ONE_c(RV-55) | https://note.com/z1kata3ne/n/n4f3f3ee2107d | なし | OK | OK | ONE_c末尾(そのまま次の家へ向かう) |
| One Voice | 第3文 | 再配達はできれば減ってほしいし、きついのも本当だ。 | ONE_b(RV-55); ONE_c(RV-55) | https://note.com/z1kata3ne/n/n4f3f3ee2107d | 口調・言い回し | OK | OK | ONE_c(減ってほしい)+芯『きついのは本当』 |
| One Voice | 第4文 | それでも、その費用をお客さんに払ってもらえばいい、とは割り切れないんだ。 | ONE_a(RV-55,RV-56); ONE_d(RV-59) | https://ameblo.jp/yukitanoyonkoma/entry-12788458083.html; https://goroneko.net/entry/2024/03/21/070000; https://note.com/z1kata3ne/n/n4f3f3ee2107d | 仮定・意見の言い換え | OK | OK | 芯・矛盾欄(割り切れない)。ONE_aの反対側の言い換え |
| One Voice | 第5文 | 私は、受け取れなかったお客さんごとに、その再配達にかかった分を請求するより、荷物を運ぶための料金全体で受け止めるほうが、筋が通るんじゃないかと思う。 | ONE_a(RV-55,RV-56) | https://ameblo.jp/yukitanoyonkoma/entry-12788458083.html; https://note.com/z1kata3ne/n/n4f3f3ee2107d | 仮定・意見の言い換え | OK | OK | ONE_a(請求より料金全体で受け止める)。逐語でなく言い換え |
| One Voice | 第6文 | そのためには、通販の送料無料も、そのままでいいのか、会社の側で考えてもらいたい。 | ONE_a(RV-55,RV-56) | https://ameblo.jp/yukitanoyonkoma/entry-12788458083.html; https://note.com/z1kata3ne/n/n4f3f3ee2107d | 仮定・意見の言い換え | OK | OK | ONE_a(送料無料の見直し=RV-56)+ONE_b(会社の側が見直されなくなる)。lunaはONE_aのみ |
| One Voice | 第7文 | 送料を見直すなら、その分がちゃんと運ぶ人に回るように、料金の組み方まで見直してほしい。 | ONE_a(RV-55,RV-56) | https://ameblo.jp/yukitanoyonkoma/entry-12788458083.html; https://note.com/z1kata3ne/n/n4f3f3ee2107d | 口調・言い回し,仮定・意見の言い換え | OK | OK(要注意) | ONE_a(運ぶ人に回る=RV-56)。『運ぶ人』が三人称で、ドライバー本人の語りとして役割の手がかりがやや弱い(捏造ではない)。『料金の組み方まで』は注文の補い |
| Another Voice | 第1文 | 再配達でお金を払うとなると、どうも引っかかるんだよね。 | TWO_e(RV-07,RV-65); TWO_g(RV-63) | https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q14303526044; https://woman.excite.co.jp/article/lifestyle/rid_E1493024559197/ | 感情の言い方,口調・言い回し | OK | OK | TWO_g/芯(払うとなると引っかかる)。lunaがTWO_eも付けたが、本文に『家にいたのに不在票』の自分の出来事は**ない**(TWO_eは仮定の意見欄で未使用) |
| Another Voice | 第2文 | わたしも夫も仕事で家を空けるから、指定できる荷物は確実に家にいる日と時間にしてる。 | TWO_a(RV-08); TWO_d(RV-08) | https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11292012431 | なし | OK | OK | TWO_a・TWO_d |
| Another Voice | 第3文 | でも、午前の時間帯を指定したのに来なくて、用事を済ませに出て、戻ったら不在票が入っていたことがある。 | TWO_b(RV-08) | https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11292012431 | なし | OK | OK | TWO_b(午前指定、外出、戻ったら不在連絡票)。Eの出来事一つ |
| Another Voice | 第4文 | 時間指定できない荷物も多くて、いつ届くか事前に分からない。 | TWO_a(RV-08) | https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11292012431 | なし | OK | OK | TWO_a |
| Another Voice | 第5文 | お金を取る前に、指定した時間に来ることと、届く日時を知らせることを、まず何とかしてほしい。 | TWO_a(RV-08); TWO_d(RV-08) | https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11292012431 | 仮定・意見の言い換え | OK | OK | TWO_d(有料化の前に時間指定の遵守・届く日時の事前通知) |
| Another Voice | 第6文 | 配達員さんも人手が足りなくて大変なんだろうし、仕方ないのかなとも思う。 | TWO_f(RV-07) | https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q14303526044 | 感情の言い方 | OK | OK | TWO_f(配達員の事情は分かる) |
| Another Voice | 第7文 | でも、そこでわたしが払うのは納得できない。 | TWO_g(RV-63) | https://woman.excite.co.jp/article/lifestyle/rid_E1493024559197/ | 聞き手への呼びかけ・つなぎ | OK | OK | TWO_g/矛盾欄(分かるが納得できない) |
| Another Voice | 第8文 | そう思うわたしが悪いの？ | TWO_g(RV-63) | https://woman.excite.co.jp/article/lifestyle/rid_E1493024559197/ | 聞き手への呼びかけ・つなぎ,感情の言い方 | OK | OK(要注意) | 感情の癖欄の『わたしが悪いの、と問い返す』を結びにした文。自分への問い返しの補い(出来事の追加ではない) |
| A Third Voice | 第1文 | 僕は再配達で迷惑をかけないよう、営業所やロッカーで受け取るようにしている。 | THREE_a(RV-26,RV-54) | https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11316828261; https://komachi.yomiuri.co.jp/topics/id/1227312/ | なし | OK | OK | THREE_a |
| A Third Voice | 第2文 | 自分の都合で取りに行けるのは便利なんだけど、商品によってはロッカーを選べないし、営業所に頼んでも届くのが遅れて、結局は対面で受け取ることもある。 | THREE_a(RV-26,RV-54); THREE_b(RV-26) | https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11316828261; https://komachi.yomiuri.co.jp/topics/id/1227312/ | 聞き手への呼びかけ・つなぎ | OK | OK | THREE_a(都合のいい時間に取りに行ける)+THREE_b(ロッカーにできない・営業所は遅れる・対面で受け取る)。Eの出来事は欄にあるもの |
| A Third Voice | 第3文 | それでも、こっちは受け取り方を考えて手間をかけているのに、いつも不在で再配達を頼む人と同じ料金なのは、正直おかしいと思う。 | THREE_a(RV-26,RV-54); THREE_c(RV-11) | https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11316828261; https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q13328335058; https://komachi.yomiuri.co.jp/topics/id/1227312/ | 口調・言い回し | OK | OK | THREE_c(同じ料金はおかしい)+THREE_a |
| A Third Voice | 第4文 | 配達する人の時間を使うんだから、再配達は有料でいい。 | THREE_d(RV-40,RV-41) | https://komachi.yomiuri.co.jp/topics/id/800042/ | 聞き手への呼びかけ・つなぎ | OK | OK | THREE_d(配達する人の時間を奪う、有料でいい) |
| A Third Voice | 第5文 | 最初の再配達は無料にして、くり返し不在になる人から払ってもらう形なら納得できる。 | THREE_h(RV-09,RV-15,RV-19) | https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q10276041280; https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q10323315035; https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11292012431 | なし | OK | OK | THREE_h(最初は無料で、くり返す人から)。V2には同種の項目なし(OF-Y8-04) |
| A Third Voice | 第6文 | ただ、これは営業所が近くて、受け取り方を選べる僕の言い分かもしれないけど。 | (IDなし) | — | 聞き手への呼びかけ・つなぎ | UNMAPPED | OK(機械判定は偽陽性) | THREE_e/矛盾欄(営業所が近い人の言い分かもしれない=引け目1つ)。lunaがIDを付けられずUNMAPPEDとしたが、Sheetの矛盾欄そのもの |

## 3. R2+のみが根拠の文(公開前の権利確認の対象。SOURCE_LOG_02 §5 (e)(f))と単一出典依存度
| Voice | 文数 | R2+/R3のみが根拠の文 | 声ID別の依存(その声を根拠に含む文数) |
|---|---|---|---|
| One Voice | 7 | 7 | RV-55:7, RV-56:4, RV-59:1 |
| Another Voice | 8 | 0 | RV-07:2, RV-08:4, RV-63:3, RV-65:1 |
| A Third Voice | 6 | 0 | RV-09:1, RV-11:1, RV-15:1, RV-19:1, RV-26:3, RV-40:1, RV-41:1, RV-54:3 |

- **One Voice(V1)は全7文がR2+/R3(個人ブログ・note)のみを根拠にし、全文がRV-55(note、現役ドライバー1人)を根拠に含む**。Opus指摘どおり、V1は別人2系統以上の声(RV-55/56/59 = R2+、RV-29 = R2)の集約で、根拠はR2+だけ。V1の経験欄のうちONE_e/f/g/h(RV-58・RV-59・RV-29・RV-57)は今回の語りでは未使用で、語りはONE_a〜ONE_dの意見・気持ちが中心(RV-58の怒りは出ていない)。公開・商用化の前に許諾か他の声への置換が必要(DEV/Trialの範囲では使用可)。
- Another Voice(V2)・A Third Voice(V3)はR2(Yahoo知恵袋・小町等)の声が根拠で、R2+のみの文は0。V2の経験欄(E)は全件RV-08(知恵袋の1人)の1出典に依存(公開前Gate(e)の既知の例外、`PROMPT_DIFF_06.md`)。

## 4. 長一致の機械照合(公開前Gate(f))と数量表現の検査
- R0本文と、R2+/R3の出典(S22, S23, S24a, S24b, S24c, S25)の本文の、**8文字以上(句読点・空白除去後)の共通部分列**: One Voice x S23: 「るんじゃないかと」。**agent判定: 偽陽性**(「〜るんじゃないかと」は一般的な推量の語尾で、出典の固有の言い回し・構成の写しではない。前後の語は一致していない)。
- R0本文の数字・数量表現(算用数字、漢数字+単位[年・歳・人・回・度・日・本・軒・目・つ等])の該当: なし(0件)。
- 回数の言い換え(Opus論点5): 『最初の再配達は無料にして、くり返し不在になる人から』(A Third Voice 第5文)。『二回目』『一度』等の数量表現は漏れていない。
