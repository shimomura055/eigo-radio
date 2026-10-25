# PART1_T1_CHECK_01(Part 1 T1 翻訳工程の正確性確認)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_16 / 日付: 2026-10-25 / 使用model: gpt-6-luna(`routing.SUPPORT_MODEL`=最新世代推奨系、旧/下位モデルの使用なし)
目的: ユーザー承認条件「翻訳の正確性と本文との意味整合を確認する」。Trial-03/04の3作品9文(`INPUT_04.json`の引用英文=既存の03d由来確定訳付き)に、Production module `er003_kp_source_sentence_ja_01.py`(入力=引用英文のみ)を実行し、既存訳と並べた。
実行: `run_t1_check_01.py`(作品ごと1 call×3、実費0.0923円、retry 0)。生データ=`part1_t1_check_01_raw.json`。Prompt template sha=`98b1871c…7999`。
注: 既存訳は本文・gloss等を見た別工程の訳。T1は引用英文のみから訳すため、文脈なしの訳との差を見るのが目的。**Fable目視用**(私は差異の性質だけ分類した)。

| # | 作品 | 引用英文 | 既存訳(03d由来) | T1訳 | 差異の性質 |
|---|---|---|---|---|---|
| 1 | gift | One was Jim's gold watch, handed down from his grandfather to his father, and then to him. | その一つはジムの金時計で、祖父から父へ、そして彼へと受け継がれてきたものでした。 | その一つは、祖父から父へ、そして父からジムへと受け継がれてきた金時計だった。 | 表現差(「彼」→「ジム」と明示。意味同一) |
| 2 | gift | Then she caught sight of herself in the mirror. | それから彼女は、鏡に映った自分の姿をふと目にしました。 | そのとき、彼女は鏡に映った自分の姿に気づいた。 | 表現差(「ふと目にした」→「気づいた」。軽微) |
| 3 | gift | Outside a hair-goods shop, she paused just long enough to catch her breath. | 髪用品店の外で、彼女は息を整えるのに十分なだけ立ち止まりました。 | 髪飾り店の外で、彼女は息を整えるためにほんの少し立ち止まった。 | **意味差(軽微)**: hair-goods→「髪飾り店」は範囲が狭い(既存の「髪用品店」が正確)。just long enoughの含みが弱い。※追加3回の再実行でも「髪飾り店」が3/3で出た(安定した傾向) |
| 4 | ig_nobel | The Ig Nobel Prize went to research on nutrient-rich crystals that had been published earlier. | イグ・ノーベル賞は、以前に発表された栄養豊富な結晶に関する研究に贈られました。 | 栄養豊富な結晶に関する、以前に発表されていた研究がイグ・ノーベル賞を受賞しました。 | 表現差(能動/受動の向き。意味同一) |
| 5 | ig_nobel | Fats were bound to the protein, and sugars were attached too. | 脂肪はタンパク質に結びついていて、糖も付着していました。 | 脂肪はタンパク質に結合し、糖も付着していました。 | 表現差(「結びついて」→「結合」。科学文脈で適切) |
| 6 | ig_nobel | At this point, the marketing team might be ready to leap into action, but hold on. | この時点で、マーケティングチームはすぐに動き出そうとしているかもしれませんが、ちょっと待ってください。 | この時点で、マーケティングチームはすぐに行動を起こす準備ができているかもしれませんが、ちょっと待ってください。 | 表現差(be ready toを直訳寄りに保持。意味同一) |
| 7 | open_window | They tried to cross a bog, but the ground gave way beneath them. | 彼らは沼地を渡ろうとしたが、足元の地面が崩れた。 | 沼地を渡ろうとしたが、足元の地面が崩れた。 | 表現差(主語「彼らは」省略。日本語として自然) |
| 8 | open_window | Inventing convincing stories at a moment's notice was Vera's speciality. | その場ですぐに、もっともらしい話を作ることがヴェラの得意技だった。 | すぐに人を信じさせる話を作ることは、ヴェラの得意技だった。 | **意味差(中、1回目のみ)**: at a moment's noticeの係り先を取り違え(「すぐに人を信じさせる」)。追加3回の再実行では3/3「その場ですぐに…話を作る」と正しく訳せた=ばらつき |
| 9 | open_window | I hope Vera has kept you company! | ヴェラがお相手をしてくれていたならいいのですが！ | ヴェラがあなたの話し相手になってくれているといいのですが！ | 表現差(「お相手」→「話し相手」。軽微) |

## 追加3回再実行(gift・open_windowの各3文、安定性確認、実費0.171円、`stdout`は本文に転記)
- open_window #8: 「その場ですぐにもっともらしい話を作るのが…」「…説得力のある話を作り出すことは…」「…人を信じ込ませる話を作るのが…」(3/3で「その場ですぐ」を正しく保持)。#7は「沼地/湿地」の揺れ。#9は常に「話し相手」。
- gift #1: 「祖父から父へ、そしてジムへ/父からジムへ」(意味同一)。#3: 3/3「髪飾り店」(「前で/外で」の揺れ)。
- 文体: 作品の文体に応じて「です・ます」(news)と「だ・である」(fiction)が自動で選ばれた(既存の03d訳も同様に混在)。

## 判定の材料(Fable向け)
- 9文中: 意味同一の表現差=7、軽微な意味差=1(#3 hair-goods→髪飾り)、中程度の意味差=1(#8 係り先の取り違え、再現せず)。重大(意味反転・欠落)=0。
- 原因の見立て: 本文を見せない(入力=引用英文のみ)設計のため、hair-goodsのような語の限定は文脈なしでは決まらない。係り先の揺れはLLMの確率的ばらつき。
- 追加の防止策(Production採用済み範囲内で可能): 構造検査(件数・ID・空・英語残り・かな有無・禁止パターン)は実装済み。意味の正否は機械検査できない(新Validatorを作らない方針)。次の改善案(未実施・判断候補): ①Promptへ「副詞句がどの語にかかるか英文の構造から判断する」旨の追記(Prompt変更=再検証要) ②T1訳を試聴ページの「日本語訳」欄に出す前にHR対象にしない(現状はLLM訳を直接表示)。**①②とも未採用。現状はユーザー承認どおり「引用英文のみ入力・自然な訳」。**
