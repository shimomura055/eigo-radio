# fable_blind_06: 二重判定(第二評価者)用 盲検表(委任_30。OPUS_REVIEW_08 OF-KP2-03。**arm・既存ラベルは伏せてある**)

評価者: Opus または新しいcontextのFable。**判定してから** `fable_blind_06_key.json` を開く(開くのは集計時のみ)。

## 判定基準(明示。『範囲を超えた持ち込み=THIN』を含む)
行=Key Phrase(key_phrase と、それが使われた本文の文)。列=この表で見る日本語glossの**文字列**(同じ文字列は1列)。各セルに次のいずれかを付ける。
- **PASS**: 学習カードに『key_phrase = gloss』と書いたとき、**key_phrase全体の意味**を過不足なく表している。本文での語義(字義か比喩か)に合っている。
- **THIN**: 意味は概ね合うが、次のいずれかがある。
  1. **範囲を超えた持ち込み**: key_phraseに含まれていない、本文側の**否定・主語・時制・具体的な対象・場面**がglossに入っている(例の型: key_phrase『work out』= gloss『うまくいかなかった』[否定と過去を本文から持ち込み])。
  2. 意味が狭い/ずれている(key_phraseの一側面だけ、または別の語義方向へ移動)。
  3. 説明文的で長く、key_phraseと同じ品詞・長さの句になっていない。
- **FAIL**: key_phraseの意味と違う、または重要な語の意味が欠ける。
- **FAIL_LIT**: 字義(語の置換)の像のままで、本文での意味が日本語読者に伝わらない。
- 迷ったら**厳しい側**(THIN)に倒し、理由を1語(持ち込み:否定/主語/時制/対象/場面、狭い、説明的、字義)でメモする。
- **持ち込みテスト**: 『key_phrase = gloss』と学習カードに書いたとき、key_phrase単体では言えない内容(否定・過去・特定の人物/物/場面)が入っていないかを必ず確認する。
- 一次評価(Fable、委任_23〜29)と**同じ4ラベル**だが、本表では上記の『持ち込み』を明示的にTHINとして扱う点が異なる(一次評価の水準が緩い方向に揺れたことの確認が目的)。

## 再照合対象(Opus条件Cレビューの指摘。通常の判定に加え、理由を必ず書く)
- `add up`: 本文は 'that doesn't add up'。glossに否定が含まれる文字列について、key_phrase『add up』の範囲か否かを判断する。
- `reach for someone's wallet`: 過去のユーザー判断は『見出し語に忠実な訳(人の財布に手を伸ばす)でPASS』。本表の基準(本文での語義を選ぶが範囲はkey_phraseだけ)で、各文字列をどう評価するかと、過去判断と矛盾するかを書く。

## 盲検表

| # | key_phrase | 本文の文 | A | B | C | D | E | F |
|---|---|---|---|---|---|---|---|---|
| 1 | walk out | I stepped back, then turned and walked out | 歩いて出ていく | 歩いて立ち去る | 歩いて外へ出る |  |  |  |
| 2 | fire the starting gun | A big name's words can fire the starting gun, or give people a reason to stop | スタートの号砲を鳴らす | 物事を動かし始める | スタートの合図を出す |  |  |  |
| 3 | work to do | Official policy still treats longer stays as work to do, not as a completed change. | まだやるべきこと | やるべきこと |  |  |  |  |
| 4 | come down | In your mind, the price of your usual cup has already come down, too | 値下がりする | 下がる |  |  |  |  |
| 5 | turn on its head | But in talks about bringing Tesla and SpaceX together, that hope may be turned on its head | それをひっくり返す | 期待をひっくり返す | ～をひっくり返す |  |  |  |
| 6 | Carry the Load | Bags Split the Job: Mini Bags Catch the Eye, Large Bags Carry the Load | 必要な荷物を運ぶ役目を担う | 荷物を運ぶ |  |  |  |  |
| 7 | rise above | At the wedding, his sister's laughter rose above the other voices | ひときわ大きく響く | ～より大きく聞こえる |  |  |  |  |
| 8 | off the hook | So, are tariffs off the hook | 責任を問われずに済む | 責任を免れている |  |  |  |  |
| 9 | grow lighter | My cough still hurt, and I was still short of money. But the weight in my chest had grown lighter. | 軽くなる | 気持ちが軽くなる |  |  |  |  |
| 10 | take off an AI costume | It was like someone took off an AI costume. | AIの裏に人がいると明かす | AIの着ぐるみを脱ぐ | AIの衣装を脱ぐ |  |  |  |
| 11 | become like porches | The researchers described this idea with a simple image: “benches become like porches.” | ベンチが人々の憩いや交流の場になる | 玄関先のような場所になる |  |  |  |  |
| 12 | a door inside the pain | Her earlier self had heard a door inside the pain. | 痛みの中にある扉 | 悲しみの中に見つけた、思い出と向き合い直す道 |  |  |  |  |
| 13 | one doorway among several | They show something quieter: the phone is becoming one doorway among several. | 複数あるアクセス手段の一つ | いくつかある入り口の一つ |  |  |  |  |
| 14 | draw a line | The words draw that line simply | はっきりと区別する | 違いをはっきり示す | 一線を引く | 線を引く | 区別をはっきりさせる |  |
| 15 | carry a decision's weight | People who carry a decision's weight may have little say | 決定の重さを背負う | 決定の重みを背負う |  |  |  |  |
| 16 | greener grass | It is like putting down binoculars you use to look at your neighbor's greener grass | 自分より恵まれて見える他人の暮らし | より青く見える芝生 | 人の暮らしのほうがよく見えること | 他人の暮らしが自分よりよく見えること | より青々とした芝生 |  |
| 17 | give back gains | After the withdrawal and replacement announcement, Brent crude futures briefly gave back some gains. | 上げ幅を一部縮める | 上昇分を失う | 上昇分の一部を失う |  |  |  |
| 18 | all it takes | Sometimes, all it takes is a short silence. | 必要なのは～だけ | それだけで十分 |  |  |  |  |
| 19 | two different speeds | As of September 2026, travel surveys in Japan tell a story with two different speeds. | 二つの異なるペース | 異なるペースで進む二つの動き |  |  |  |  |
| 20 | not the same picture | This is not the same picture as the male interest in solo and hobby-based trips. | 同じ状況ではない | 同じ傾向ではない |  |  |  |  |
| 21 | weak link | They found a weak link in both directions: personality with later income, and income with later personality | 弱い関連 | 弱いつながり |  |  |  |  |
| 22 | jump to conclusions | No, that would be jumping to conclusions too | 早合点する | 早まって結論を出す | 早まった結論を出す |  |  |  |
| 23 | put on hold | According to internal posts reviewed by Reuters, a Meta executive said the company had put the feature on hold. | 保留にする | ～を保留にする | いったん保留にする |  |  |  |
| 24 | take the wheel | Not taking the wheel is different from not supporting the journey | ハンドルを握る | 車を運転する |  |  |  |  |
| 25 | pump one's fist | When you hear that, your wallet pumps its fist | こぶしを突き上げて喜ぶ | 自分の拳を突き上げる | 喜んでガッツポーズをする |  |  |  |
| 26 | on the throne | Bags no longer play a game with only one size on the throne | トップの座を占める | 王座に就いて | 王座に就いている |  |  |  |
| 27 | too broad a label | “Young Japanese travelers” is too broad a label. | 範囲が広すぎる呼び名 | ひとくくりにするには広すぎる呼び方 | 広すぎるくくり |  |  |  |
| 28 | center stage | For the moment, only a large number stood at center stage | 注目の的になる | 注目の中心 |  |  |  |  |
| 29 | brace yourself for | It may be too early to brace yourself for "At last, it's time to compete over AI's writing skills | ～に備えて心構えをする | ～に備えて心の準備をする |  |  |  |  |
| 30 | supply chain | At the time of that report, the tariff-caused rise had not yet passed through the whole supply chain | 商品が作られて消費者に届くまでの流れ | 商品が作られて店に届くまでの流れ | 商品が作られて届くまでの供給の流れ |  |  |  |
| 31 | on paper | So a rule may look flexible on paper but feel difficult to one person. | 理屈の上では | 書面上では |  |  |  |  |
| 32 | pull back | For now, Meta has pulled back the human concierge feature. | 取り下げる | いったん提供を取りやめる | ～を取り下げる |  |  |  |
| 33 | spread through the whole market | We are not seeing mini bags spread through the whole market | 市場全体に広まる | 市場全体に広がる |  |  |  |  |
| 34 | shine a light on | A prize that is supposed to choose works also shines a light on the values of the people doing the choosing | ～に光を当てる | ～を浮き彫りにする |  |  |  |  |
| 35 | add up **[再照合対象]** | Wait a minute, that doesn't add up | つじつまが合う | つじつまが合わない |  |  |  |  |
| 36 | weakly linked to higher income | A rise in conscientiousness was also weakly linked to higher income later on | 収入が高いことと少し関係している | より高い収入と弱い関連がある |  |  |  |  |
| 37 | play a part | Something else may have played a part in both | 役割を果たす | 一因となる |  |  |  |  |
| 38 | tiny bomb | The lemon seemed to be a tiny bomb. | 小さな爆弾 | 小型爆弾 |  |  |  |  |
| 39 | step out | Then a person stepped out | 人が姿を現す | 外へ出る |  |  |  |  |
| 40 | behind the curtain | And who is behind the curtain? | 舞台裏に | 舞台裏で動いている |  |  |  |  |
| 41 | without asking for another promise | His friend had trusted him without asking for another promise | 改めて約束を求めずに | 新たな約束を求めずに |  |  |  |  |
| 42 | question shaped like a trophy | You could call it a question shaped like a trophy | トロフィーの形をした質問 | 賞という形で投げかける問い |  |  |  |  |
| 43 | move in the other direction | Sweets moved in the other direction. | 売れ行きは逆に下がった | 反対の方向に動く |  |  |  |  |
| 44 | an unseen clock | A coffee price tag may have an unseen clock of its own, separate from the latest news about the market | 目に見えない時計 | 値札に隠れた時間のずれ | 表には見えない独自のタイミング | 値札に隠れた独自のタイミング |  |  |
| 45 | stone video | Participants who were strongly inclined to enjoy seeing others suffer were more likely to reduce the other person's reward after watching the stone video than after watching the magician video | 石の動画 | 石を映した動画 |  |  |  |  |
| 46 | reach for someone's wallet **[再照合対象]** | That's enough to make you reach for your wallet before the volume button | 人の財布に手を伸ばす | 誰かが自分の財布に手を伸ばす | 財布を出してお金を払おうとする |  |  |  |
| 47 | run on | They are on different stages and run on different clocks | ～に合わせて動く | ～に合わせて進む | 別々の時間軸で動いている |  |  |  |
| 48 | rise above the other voices | At the wedding, his sister's laughter rose above the other voices | ほかの声よりひときわ大きく響く | ほかの声よりも際立つ | ほかの声よりひときわ大きく聞こえる |  |  |  |
| 49 | sound no one asked for | Here's news about this kind of "sound no one asked for | 誰も求めていない音 | 誰も聞きたくない音 | 誰も頼んでいない音 |  |  |  |
| 50 | behind the scenes | I thought AI was a helper working behind the scenes | 舞台裏で | 表に出ずに | 人目につかないところで |  |  |  |
| 51 | fill in | Human help is not automatically a bad thing: people can fill in the areas where AI is still weak. | ～を補う | 補う | 足りない部分を補う |  |  |  |
