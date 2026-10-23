# SOURCE_CHECK_01 (原作確認、2026-10-24)

## 出典・権利
- Project Gutenberg eBook #2776 "The Four Million" (O. Henry, 1906) の全文。取得 2026-10-24、HTTP 200。pg2776.txt sha256 = 6bb719852f2f0eb33db25613124d2d3c522dd3b879c187667ab31072bb2fb48d(『二十年後』取得時と同一)。
- 作品発表: 1905-12-10 New York Sunday World、1906-04-10 短編集 The Four Million に収録(en.wikipedia.org/wiki/The_Gift_of_the_Magi、HTTP 200)。原作者 William Sydney Porter (O. Henry) 没 1910-06-05(en.wikipedia.org/wiki/O._Henry、HTTP 200)。日本: 死後50年(1960-12-31)+戦時加算3,794日=1971-05-22満了。2018年の70年化は遡及しない。日本でパブリックドメイン(最終的な法的判断ではない)。米国も1931年前の出版でPD。
- 利用テキスト: `er026_seeds/the_gift_of_the_magi/story.md`(pg2776.txt l.385-611の見出し除く本文、空白正規化のみ。Gutenberg版は文中('already / introduced to you as Della')に空行が混入しているため前後を1段落へ連結。単語変更なし。2,061語/42段落)。sha256はSOURCE_PROVENANCE.json。第三者の翻訳・翻案・あらすじは不使用。

## あらすじ・人物関係・結末の確認表(原文照合)
| 要素 | 原文での内容 |
|---|---|
| 設定 | クリスマス・イブ。週8ドルの家具付きフラット。Jimの給料は週30ドルから20ドルに減っている |
| 夫婦 | Della(妻)とJim(James Dillingham Young、22歳)。互いを深く愛している。貧しい |
| 二つの宝物 | Jimの金時計(父・祖父から受け継ぐ)とDellaの長い茶色の髪(膝下まで) |
| 所持金 | 1ドル87セント(60セントは1セント硬貨)。数か月貯めた結果 |
| Dellaの行動 | 髪を切って Madame Sofronie の店で20ドルで売る。2時間店を探し回り、プラチナの時計鎖(21ドル)をJimへ買う。時計は古い革紐で吊るしている |
| 髪を切った後 | カールをかけて「脱走した学童」のような頭。「Jimが私を殺さないで、もう一度見てくれるなら」と独白。7時に夕食の支度、「Please God, make him think I am still pretty」と祈る |
| Jimの帰宅 | 痩せて真剣な顔。古い外套・手袋なし。入口で固まり、Dellaを凝視(怒りでも驚きでもない読めない表情)。Dellaが「髪を売った、また伸びる」と説明 |
| 贈り物 | JimがDellaへ渡したのは、Broadwayの店の窓で憧れていた鼈甲の櫛(縁に宝石)のセット。Dellaは歓喜の叫び→涙。「My hair grows so fast, Jim!」。鎖を差し出す |
| 結末 | Jim「I sold the watch to get the money to buy your combs. And now suppose you put the chops on.」(時計を売ってお金を作り、櫛を買った。互いの贈り物が使えなくなった) |
| 語り手の結語 | Magi(東方の三博士)は「Babe in the manger」に贈り物をした賢者で、クリスマスの贈り物を発明した。愚かな2人は最も賢い贈り手であり「They are the magi.」 |

結末の開示タイミング(Jimが時計を売ったこと・櫛の中身)は Jimの告白まで先回りしない(Seedの withhold_until_end、Preview/Comment lintのspoiler語に反映)。原題『The Gift of the Magi』の意味は結語段落で語り手が説明する(Seedの ending_reveal.source_quote と conversion_plan で結語維持を明示)。
