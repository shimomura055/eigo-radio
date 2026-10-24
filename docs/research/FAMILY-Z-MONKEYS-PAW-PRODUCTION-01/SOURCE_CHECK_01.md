# SOURCE_CHECK_01 (原作確認、FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 委任_01、2026-10-24)

## 出典・権利
- Project Gutenberg eBook #12122 "The Monkey's Paw"(W. W. Jacobs、短編集 "The Lady of the Barge and Other Stories" 1902 より)。取得 2026-10-24、HTTP 200。pg12122.txt sha256 = 22f3431a7db6d9e210ffb446044739513475cb93992421d1b0d107f094d7408d(940行、本文 l.44-589)。
- 作品発表: 1902-09 Harper's Monthly Magazine、同1902年に短編集 The Lady of the Barge に収録(en.wikipedia.org/wiki/The_Monkey%27s_Paw、HTTP 200)。原作者 William Wymark Jacobs 没 1943-09-01(en.wikipedia.org/wiki/W._W._Jacobs、HTTP 200、"1 September 1943"を確認)。
- 日本: 死後50年(没年翌年起算、1993-12-31満了)+英国分の戦時加算3,794日 = 1993-12-31 + 3,794日 = **2004-05-21**(計算値、`datetime.date(1993,12,31)+timedelta(3794)`で確認)。2018年の70年化は満了済み作品に遡及しない。日本でパブリックドメイン(最終的な法的判断ではない)。米国も1931年前の出版(1902)でPD。コード側rights block = `MONKEYS_PAW_RIGHTS_BLOCK`(runner)、`check_rights_gate` PASS確認済み。
- 利用テキスト: `er026_seeds/the_monkeys_paw/story.md`(pg12122.txt l.44-589の本文、空白正規化・節番号 I./II./III. と `[Illustration]` 注記の除去・斜体記号 `_..._` の除去のみ。3,934語/144段落)。sha256は`er026_seeds/the_monkeys_paw/SOURCE_PROVENANCE.json`。登録testで raw extract と story.md が語・順序とも一致することを検査。第三者の翻訳・翻案・あらすじは不使用。

## 原文の要素確認表(原文照合)
| 要素 | 原文での内容 |
|---|---|
| 設定 | 寒く雨の夜、人里離れた Laburnam Villa の小さな居間。Mr. White と息子 Herbert がチェス、Mrs. White は編み物 |
| 家族 | Mr. White(父、主人公)、Mrs. White(母、白髪)、Herbert(息子、会社勤め) |
| 猿の手 | 退役軍曹 Sergeant-Major Morris(インド21年)が持参。ミイラ化した小さな猿の手。老いた行者(fakir)が「運命が人の人生を支配し、干渉する者は悲しみを味わう」ことを示すため、3人の男がそれぞれ3つの願いを持てるよう呪いをかけた |
| 警告 | Morris は自分の3つの願いを使ったが内容は言わない。最初の持ち主の最後の願いは死。猿の手を火に投げるがWhiteが拾う。「どうしても願うなら、分別のあるものを願え」「何が起こっても私を責めるな」 |
| 第一の願い | Herbert の冗談で「200ポンド」(家のローンを払える額)。Whiteが願うと猿の手が「蛇のように」手の中でねじれる。何も起きない |
| 翌日 | 夫妻は恐れを笑う。使者(絹の帽子の見知らぬ男、"Maw and Meggins" から)が門前で3度ためらってから来訪 |
| 悲劇 | Herbert は機械に巻き込まれて死亡。会社は責任を認めないが見舞金として200ポンドを提示(第一の願いと同額)。Whiteは気絶 |
| 第二の願い | 葬儀の約1週間後、夜中にMrs. Whiteが猿の手を思い出し、「息子を生き返らせて」と夫に願わせる。Whiteは「遺体は服でしか判別できなかった」と恐れる。願うが何も起こらず就寝 |
| 戻るもの | 静かでこっそりした叩き音、続いて大きなノック。Mrs. Whiteは「Herbert!」とドアへ。Whiteは「入れないで」と止めるが振り切られる。Whiteは床で猿の手を探す |
| 結末 | 最後のかんぬきが外れる瞬間に猿の手を見つけ、第三の最後の願いを息だけで唱える(内容は書かれない)。ノックは止み、ドアが開く。冷たい風と妻の嘆きの叫び。街灯が「静かで無人の道」を照らす |

結末の開示タイミング(Herbertの死・200ポンドの意味)は使者の来訪まで先回りしない(Seedの withhold_until_end、Preview/Comment lintのspoiler語に反映)。第三の願いの内容、ドアの外にいたものは原作どおり書かない(Seed ending_reveal.meaning/conversion_planで明示)。
