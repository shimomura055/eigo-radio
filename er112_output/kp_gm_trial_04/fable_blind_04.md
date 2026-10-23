# fable_blind_04: Std日本語gloss盲検表(委任_14 課題①。arm伏せ)

行=Key Phrase、列A〜=この表で初めて見る日本語glossの**文字列**(同じ文字列は1列。arm・repの帰属は`fable_blind_04_key.json`に分離)。**判定してからkeyを開くこと。**
判定: PASS / 薄(△=意味は誤りでないがフレーズ全体より弱い・含意欠落) / FAIL(用法取り違え・字義訳・別義・誤訳)。FAILのうち字義訳(比喩・慣用を字義の像で訳したもの)は `FAIL_LIT` と書く。
難例(draw a line, take the wheel 等)は`GOLD_LABELS_FINAL_01.md`のgold、通常は本文文の用法とフレーズ全体の意味への一致が基準。
Trial_02/03で既にFable確定済みの文字列(B0の旧出力)は表に含めない(ラベル継承)。

| # | 層/型 | key_phrase | 本文の文 | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | F/normal/X | add up | Wait a minute, that doesn't add up | つじつまが合わない |  |  |  |  |  |  |  |
| 2 | F/normal/X | an unseen clock | A coffee price tag may have an unseen clock of its own, separate from the latest news about the market | 見えない時計 | 目に見えない時間の流れ | 見えない時間の流れ | 目に見えないタイミングの仕組み |  |  |  |  |
| 3 | F/normal/X | behind the curtain | And who is behind the curtain? | 陰で動いている | 陰で関わっている |  |  |  |  |  |  |
| 4 | F/normal/X | behind the scenes | I thought AI was a helper working behind the scenes | 人目につかないところで | 表に出ずに裏で |  |  |  |  |  |  |
| 5 | F/hard/X | brace yourself for | It may be too early to brace yourself for "At last, it's time to compete over AI's writing skills | ～に備えて心の準備をする | ～に備えて身構える |  |  |  |  |  |  |
| 6 | F/hard/X | Carry the Load | Bags Split the Job: Mini Bags Catch the Eye, Large Bags Carry the Load | 荷物をしっかり運ぶ | 荷物をしっかり持ち運ぶ |  |  |  |  |  |  |
| 7 | F/normal/X | center stage | For the moment, only a large number stood at center stage | 注目の的 |  |  |  |  |  |  |  |
| 8 | F/hard/X | draw a line | The words draw that line simply | 違いをはっきり示す | 区別する |  |  |  |  |  |  |
| 9 | F/hard/X | fire the starting gun | A big name's words can fire the starting gun, or give people a reason to stop | 物事を動き出させる | ～の開始を告げる |  |  |  |  |  |  |
| 10 | F/normal/Z | give way | They tried to cross a bog, but the ground gave way beneath them | 崩れる | 崩れ落ちる |  |  |  |  |  |  |
| 11 | F/normal/Z | go cold | Framton went cold because she really did expect them back | ぞっとする |  |  |  |  |  |  |  |
| 12 | F/normal/X | go out of one's way | Why did they go out of their way to create this kind of entrance | わざわざ～する | わざわざ手間をかける |  |  |  |  |  |  |
| 13 | F/normal/X | greener grass | It is like putting down binoculars you use to look at your neighbor's greener grass | 人のもののほうがよく見えること | 他人のほうが恵まれているように見えること | 自分より良く見える他人の暮らし | 自分のものよりよく見える他人の暮らし | より青々とした芝生 | 自分より恵まれて見える人の暮らし |  |  |
| 14 | F/normal/Z | grow lighter | My cough still hurt, and I was still short of money. But the weight in my chest had grown lighter. | 気が楽になる | 胸の重苦しさが和らぐ |  |  |  |  |  |  |
| 15 | F/normal/X | in the spotlight | The person in the spotlight is none other than you | 注目を浴びている |  |  |  |  |  |  |  |
| 16 | F/hard/X | jump to conclusions | No, that would be jumping to conclusions too | 結論を急ぐ |  |  |  |  |  |  |  |
| 17 | F/normal/Z | keep someone company | I hope Vera has kept you company | 誰かの話し相手をする | 人の相手をする | 人の話し相手になる | 人と一緒にいて相手をする | 人の話し相手をする |  |  |  |
| 18 | F/hard/X | leap into action | At this point, the marketing team might be ready to leap into action, but hold on | すぐさま行動に移る |  |  |  |  |  |  |  |
| 19 | F/normal/X | move in the other direction | Sweets moved in the other direction. | 逆の傾向を示す | 逆の動きをする | 反対の方向へ動く |  |  |  |  |  |
| 20 | F/normal/X | not the same picture | This is not the same picture as the male interest in solo and hobby-based trips. | 同じ傾向ではない | 同じような傾向ではない |  |  |  |  |  |  |
| 21 | F/hard/X | off the hook | So, are tariffs off the hook | 責任を免れている |  |  |  |  |  |  |  |
| 22 | F/normal/X | on paper | So a rule may look flexible on paper but feel difficult to one person. | 理屈の上では |  |  |  |  |  |  |  |
| 23 | F/hard/X | on the throne | Bags no longer play a game with only one size on the throne | 一番の座を占めて | 一番の座にいる |  |  |  |  |  |  |
| 24 | F/normal/X | play a part | Something else may have played a part in both | 役割を果たす | 影響する | 一役買う | 一因となる |  |  |  |  |
| 25 | F/normal/X | pump one's fist | When you hear that, your wallet pumps its fist | うれしくてガッツポーズをする | ガッツポーズをする | こぶしを突き上げて喜ぶ | 自分の拳を突き上げる | 自分の拳を突き上げて喜ぶ |  |  |  |
| 26 | F/normal/X | put on hold | According to internal posts reviewed by Reuters, a Meta executive said the company had put the feature on hold. | いったん保留にする |  |  |  |  |  |  |  |
| 27 | F/normal/X | question shaped like a trophy | You could call it a question shaped like a trophy | 賞を通じて投げかける問い | 成果や地位を誇示するような問い | 賞という形で投げかける問い | トロフィーの形をした質問 | トロフィーの形をした問いかけ | トロフィーの形をした問い |  |  |
| 28 | F/hard/X | reach for someone's wallet | That's enough to make you reach for your wallet before the volume button | 誰かが自分の財布に手を伸ばして支払いの準備をする |  |  |  |  |  |  |  |
| 29 | F/normal/Z | rise above the other voices | At the wedding, his sister's laughter rose above the other voices | ほかの声よりも際立つ | ほかの人たちの声よりも大きく響く | ほかの声よりひときわ大きく聞こえる | ほかの声よりも大きく聞こえる |  |  |  |  |
| 30 | F/normal/X | run on | They are on different stages and run on different clocks | 異なる時間の流れで進む | 〜の時間に合わせて動く |  |  |  |  |  |  |
| 31 | F/normal/X | shock someone's wallet | Before you buy something to wake you up, the price shocks your wallet awake | 人の懐を痛める | 人の財布に大きな痛手を与える | 人の財布に大きな打撃を与える |  |  |  |  |  |
| 32 | F/normal/X | sound no one asked for | Here's news about this kind of "sound no one asked for | 誰も求めていない音 | 誰も頼んでいない音 |  |  |  |  |  |  |
| 33 | F/normal/X | spread through the whole market | We are not seeing mini bags spread through the whole market | 市場全体に広がる |  |  |  |  |  |  |  |
| 34 | F/normal/X | take off an AI costume | It was like someone took off an AI costume. | AIのふりをやめて、人間の姿を現す | AIのふりをやめる |  |  |  |  |  |  |
| 35 | F/hard/X | take the wheel | Not taking the wheel is different from not supporting the journey | 主導権を握る | 車を運転する |  |  |  |  |  |  |
| 36 | F/hard/X | turn on its head | But in talks about bringing Tesla and SpaceX together, that hope may be turned on its head | 〜をひっくり返す | ～を逆転させる |  |  |  |  |  |  |
| 37 | F/normal/X | weak link | They found a weak link in both directions: personality with later income, and income with later personality | 弱いつながり | 弱い関連 |  |  |  |  |  |  |
| 38 | N/normal/Z | at a moment's notice | Inventing convincing stories at a moment's notice was Vera's speciality | 必要になればすぐに | 急なときでもすぐに | とっさに | 急な場面でも即座に |  |  |  |  |
| 39 | N/normal/X | can't wait | Can't Wait for the Next Episode | 待ちきれない |  |  |  |  |  |  |  |
| 40 | N/normal/X | give back gains | After the withdrawal and replacement announcement, Brent crude futures briefly gave back some gains. | 値上がり分の一部を失う |  |  |  |  |  |  |  |
| 41 | N/normal/Z | hold out one's hands | Melos turned to his friend, but before he could speak, his friend held out his hands for the chains | 自分の手を差し出す | 自分の両手を差し出す |  |  |  |  |  |  |
| 42 | N/normal/X | on a regular basis | These companies often talk with stores about prices on a regular basis | 定期的に |  |  |  |  |  |  |  |
| 43 | N/normal/X | pull back | For now, Meta has pulled back the human concierge feature. | いったん取り下げる |  |  |  |  |  |  |  |
| 44 | N/normal/X | step out | Then a person stepped out | 外に出てくる | 出てくる |  |  |  |  |  |  |
| 45 | N/normal/X | stone video | Participants who were strongly inclined to enjoy seeing others suffer were more likely to reduce the other person's reward after watching the stone video than a | 石を映した動画 | 石の動画 |  |  |  |  |  |  |
| 46 | N/normal/X | supply chain | At the time of that report, the tariff-caused rise had not yet passed through the whole supply chain | 商品を作って届けるまでの流れ | 商品が作られて消費者に届くまでの流れ | 商品が作られて店に届くまでの流れ | 商品が作られて届くまでの供給の流れ |  |  |  |  |
| 47 | N/normal/X | tariff-driven | The key point is that, at the time of that report, the tariff-driven rise had not yet fully made its way through the supply chain to the prices consumers paid | 関税による |  |  |  |  |  |  |  |
| 48 | N/normal/X | too broad a label | “Young Japanese travelers” is too broad a label. | ひとくくりにするには広すぎる言い方 | 大ざっぱすぎるくくり | 範囲が広すぎる分類 |  |  |  |  |  |
| 49 | N/normal/X | turn out | The Main Character Turned Out to Be Your Former Self | ～だとわかる | 結局～だと分かる | ～だと分かる | 結局～だとわかる |  |  |  |  |
| 50 | N/normal/X | weakly linked to higher income | A rise in conscientiousness was also weakly linked to higher income later on | 収入が高くなることと少し関係している | より高い収入と弱い関連がある |  |  |  |  |  |  |
| 51 | N/normal/Z | without asking for another promise | His friend had trusted him without asking for another promise | さらに約束を求めずに | 新たな約束を求めずに | もう一度約束を求めずに |  |  |  |  |  |
