# SOURCE_CHECK_01 (原作確認、2026-10-23)

## 出典・権利
- Project Gutenberg eBook #2776 "The Four Million" (O. Henry, 1906) の全文。取得 2026-10-23 22:00 JST、HTTP 200。pg2776.txt sha256 = 6bb71985...fb48d。
- 原作者 William Sydney Porter (O. Henry) 没 1910-06-05(en.wikipedia.org/wiki/O._Henry、HTTP 200)。日本: 死後50年(1960-12-31)+戦時加算3,794日=1971-05-22満了。2018年の70年化は遡及しない。日本でパブリックドメイン(最終的な法的判断ではない)。米国も1931年前の出版でPD。
- 利用テキスト: `er026_seeds/after_twenty_years/story.md`(pg2776.txt l.4915-5068の見出し除く本文、空白正規化・イタリック記号'_'除去・署名'JIMMY.'を手紙段落へ連結のみ、単語変更なし。1,261語/33段落)。sha256はSOURCE_PROVENANCE.json。第三者の翻訳・翻案・あらすじは不使用。

## あらすじ・人物関係・結末の確認表(原文照合)
| 要素 | 原文での内容 |
|---|---|
| 設定 | 夜10時前、ニューヨークの人通りの少ない大通り。雨まじりの風。閉店した金物屋の戸口 |
| 20年前の約束 | 20年前の今夜、同じ場所の"Big Joe" Brady's restaurantで最後の食事。翌朝、Bob(18歳)は西部へ、Jimmy Wells(20歳)はニューヨークに残る。20年後の同日同時刻(10時)に必ず会うと約束 |
| Bob | 西部で成功(大きなダイヤのスカーフピン・懐中時計)。1,000マイルを来た。30分は待つ |
| 警官 | 戸口の男に声をかけられ話を聞く。レストランは5年前に取り壊されたと言う。"Hope your friend comes around all right"と言い巡回に戻る |
| 約20分後 | 背の高い長いオーバーコートの男が来て"Is that you, Bob?"。BobはJimmy Wellsと思い込み腕を組んで歩く |
| 露見 | 薬局の明るい光で顔が見え、Bobが「Jimmyではない(鼻がローマ鼻と獅子鼻)」と気づく。男は10分前から"Silky" Bobとして逮捕されている、シカゴが手配と告げる |
| 手紙 | Patrolman Wellsからのメモ。約束の場所に時間通り来た、マッチの光でシカゴの手配犯の顔と分かった、自分では出来ず私服刑事に頼んだ。署名JIMMY |
| 結末 | 序盤の警官こそJimmy Wellsだった。約束を守りつつ職務を果たした。手紙で明かされる |

結末の開示タイミング(警官=Jimmy、Bob=指名手配犯)は最終の手紙まで先回りしない(Seedの withhold_until_end、Preview/Comment lintのspoiler語に反映)。
