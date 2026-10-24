# Post-EN Risk Flagger Review Queue: word_gacha__run_wg_01 / b1b

- run_id: `rf20261024T085833Z-30da`  status: **OK**
- article_sha256: `a92a8d5d9dbd0f898ca0ffa7c1e3211b69752ecfcaca1fc9b05929309dee31a7`  ledger_sha256: `26c3eb894d155700bc2ce8cde612146f08d4e56b37fb987425674b3d87ac0135`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `run_wg_01`
- sentences: 47  facts: 13  candidate issues: 9

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=5 cost_jpy=0.23224 model=gpt-6-luna
- luna A4: OK flags=9 cost_jpy=0.26104 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.219472 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.225232 model=gemini-3.5-flash-lite

## Issues

### s2  (confidence max 0.35)
- issue_id: `word_gacha__run_wg_01__b1b__a92a8d5d__rf20261024T085833Z-30da__s2`
- sentence: If you’re going to learn English words, start with the ones people use a lot.
- before: # I Checked the Rarity Before Learning the Words: “Rare-Word Hunting” Starts with an English-Word Gacha
- after: That’s obviously right. / There’s no arguing with it.
- detected_by: luna-A3(0.34), luna-A4(0.35)
- reason [その他]: 『使用頻度が高い単語から学ぶべき』という優先順位は、台帳の『レア度は使用頻度を基準とし、学習上の重要性とは別』という説明からは確認できないのではありませんか。
- reason [その他]: 「people use a lot」と「start with」が結びつき、使用頻度の高い語を先に学ぶべきだと述べていますが、台帳は使用頻度を学習上の重要性と同一視していないのではありませんか。
- fact F12: GIGAZINEの説明ではレア度の基準は単語の使用頻度であり、学習上の重要性を判定する基準とは示されていない。
  scope: ゲームのレア度説明と、記事内で示された情報
  conditions: 頻度を基準とする仕様から、学習上の重要度も同じ指標だとは結論できない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: レアな単語を「重要」「役に立つ」と同一視しない。頻度と学習上の重要度は別の軸として扱う。

### s9  (confidence max 0.43)
- issue_id: `word_gacha__run_wg_01__b1b__a92a8d5d__rf20261024T085833Z-30da__s9`
- sentence: The “Dopa English Word Gacha” is just the thing to send your mind off track.
- before: Wait. / You came here to study today, didn’t you?
- after: English word cards have seven rarity levels. / The more often a word is used, the lower its level; the less often it is used, the higher.
- detected_by: luna-A3(0.43), luna-A4(0.3)
- reason [その他]: 『Dopa English Word Gacha』は、台帳にある公式名『Dopa Word Gacha』とは異なるサービス名を示しているのではありませんか。
- reason [その他]: 「send your mind off track」は、この仕組みが利用者の関心を学習からそらすと述べていますが、台帳には利用者の動機や行動を示すデータがないのではありませんか。
- fact F01: 公式ページのサービス名は「ドパ英単語ガチャ | Dopa Word Gacha」。英単語カードをガチャで集めるゲームとして、GIGAZINEが紹介している。
  scope: Webサービス
  conditions: 公式ページ本文は調査時にWeb取得ツールで読み取れず、ゲーム内容の確認は主にGIGAZINEのプレイレビューによる。
  date_or_period: 2026-10-23のGIGAZINE紹介記事掲載時
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: サービス名・存在の確認に限る。個別機能の裏付けとして公式ページを直接確認できたとは扱わない。
- fact F10: ゲームの仕組み上、レア度の高い単語カードの獲得がジャックポット・連チャンの開始条件として機能する。一方、プレイヤーが単語学習よりレアカード収集に夢中になるかどうかを示す利用者調査や行動データは、確認した紹介記事には掲載されていない。
  scope: ゲームの仕組みと、確認した紹介記事の内容
  conditions: 報酬条件は記事に記されたルール。プレイヤーの動機・行動についての一般化は含まない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: 逆転した面白さはゲームの報酬設計から生じる見方として扱う。利用者全般が学習より収集に熱中すると断定しない。

### s12  (confidence max 0.4)
- issue_id: `word_gacha__run_wg_01__b1b__a92a8d5d__rf20261024T085833Z-30da__s12`
- sentence: The words you’d want to learn first for study end up on the dull side in the gacha.
- before: English word cards have seven rarity levels. / The more often a word is used, the lower its level; the less often it is used, the higher.
- after: Practical value and star power, surprisingly, live apart. / Normally, you might think, “Could I use this in conversation?”
- detected_by: luna-A3(0.36), luna-A4(0.4)
- reason [その他]: 『学習で最初に覚えたい単語』が『ガチャで低レア側になる』という関係は、台帳の使用頻度に基づくレア度の説明だけでは確認できないのではありませんか。
- reason [その他]: 「want to learn first」と「dull side in the gacha」を結びつけていますが、台帳は使用頻度と学習上の重要性を同一視できないとしているのではありませんか。
- fact F12: GIGAZINEの説明ではレア度の基準は単語の使用頻度であり、学習上の重要性を判定する基準とは示されていない。
  scope: ゲームのレア度説明と、記事内で示された情報
  conditions: 頻度を基準とする仕様から、学習上の重要度も同じ指標だとは結論できない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: レアな単語を「重要」「役に立つ」と同一視しない。頻度と学習上の重要度は別の軸として扱う。

### s17  (confidence max 0.3)
- issue_id: `word_gacha__run_wg_01__b1b__a92a8d5d__rf20261024T085833Z-30da__s17`
- sentence: You check the rarity before reading the meaning.
- before: But now you might lean forward and think, “What? / This word is hardly ever used!”
- after: You thought you were opening a vocabulary book, but in your mind, a send-off for the rare-word hunters is already underway. / What’s more, when you draw a card rated “UR” or higher, the bonus “Jackpot” begins, and you can keep opening packs.
- detected_by: luna-A3(0.29), luna-A4(0.3)
- reason [その他]: 『意味を読む前にレア度を確認する』というプレイヤーの行動は、台帳にある紹介記事の記載から確認できないのではありませんか。
- reason [その他]: 「check the rarity before reading the meaning」はプレイヤーの行動を述べていますが、台帳にはその行動を裏付ける調査やデータがないのではありませんか。
- fact F10: ゲームの仕組み上、レア度の高い単語カードの獲得がジャックポット・連チャンの開始条件として機能する。一方、プレイヤーが単語学習よりレアカード収集に夢中になるかどうかを示す利用者調査や行動データは、確認した紹介記事には掲載されていない。
  scope: ゲームの仕組みと、確認した紹介記事の内容
  conditions: 報酬条件は記事に記されたルール。プレイヤーの動機・行動についての一般化は含まない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: 逆転した面白さはゲームの報酬設計から生じる見方として扱う。利用者全般が学習より収集に熱中すると断定しない。

### s23  (confidence max 0.3)
- issue_id: `word_gacha__run_wg_01__b1b__a92a8d5d__rf20261024T085833Z-30da__s23`
- sentence: It’s that the reason for your interest changes.
- before: Your willpower is just about to stand up and say, “All right, time to review,” when “Just one more” tugs at its sleeve. / What might happen here is not that you lose interest in English words.
- after: You go from “I draw a card because I want to learn” to “I look at words because I want to draw a card.” / Even if you’re looking at the same cards, the person in charge inside your mind has changed from the study worker to the treasure hunter.
- detected_by: luna-A4(0.3)
- reason [その他]: 「the reason for your interest changes」と利用者の関心の変化を述べていますが、台帳には利用者の動機を示す調査や行動データがないのではありませんか。
- fact F10: ゲームの仕組み上、レア度の高い単語カードの獲得がジャックポット・連チャンの開始条件として機能する。一方、プレイヤーが単語学習よりレアカード収集に夢中になるかどうかを示す利用者調査や行動データは、確認した紹介記事には掲載されていない。
  scope: ゲームの仕組みと、確認した紹介記事の内容
  conditions: 報酬条件は記事に記されたルール。プレイヤーの動機・行動についての一般化は含まない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: 逆転した面白さはゲームの報酬設計から生じる見方として扱う。利用者全般が学習より収集に熱中すると断定しない。

### s24  (confidence max 0.4)
- issue_id: `word_gacha__run_wg_01__b1b__a92a8d5d__rf20261024T085833Z-30da__s24`
- sentence: You go from “I draw a card because I want to learn” to “I look at words because I want to draw a card.”
- before: What might happen here is not that you lose interest in English words. / It’s that the reason for your interest changes.
- after: Even if you’re looking at the same cards, the person in charge inside your mind has changed from the study worker to the treasure hunter. / But here’s something worth underlining in red.
- detected_by: luna-A4(0.4)
- reason [その他]: 「I draw a card because I want to learn」から「I look at words because I want to draw a card」へ動機が変わると述べていますが、台帳は利用者全般の動機の変化を確認していないのではありませんか。
- fact F10: ゲームの仕組み上、レア度の高い単語カードの獲得がジャックポット・連チャンの開始条件として機能する。一方、プレイヤーが単語学習よりレアカード収集に夢中になるかどうかを示す利用者調査や行動データは、確認した紹介記事には掲載されていない。
  scope: ゲームの仕組みと、確認した紹介記事の内容
  conditions: 報酬条件は記事に記されたルール。プレイヤーの動機・行動についての一般化は含まない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: 逆転した面白さはゲームの報酬設計から生じる見方として扱う。利用者全般が学習より収集に熱中すると断定しない。

### s25  (confidence max 0.3)
- issue_id: `word_gacha__run_wg_01__b1b__a92a8d5d__rf20261024T085833Z-30da__s25`
- sentence: Even if you’re looking at the same cards, the person in charge inside your mind has changed from the study worker to the treasure hunter.
- before: It’s that the reason for your interest changes. / You go from “I draw a card because I want to learn” to “I look at words because I want to draw a card.”
- after: But here’s something worth underlining in red. / Just because a word is rare doesn’t mean it should be high on your study list.
- detected_by: luna-A4(0.3)
- reason [その他]: 「the study worker」から「the treasure hunter」へ内面の主導権が移ると述べていますが、台帳にはこのような利用者の行動や動機を裏付けるデータがないのではありませんか。
- fact F10: ゲームの仕組み上、レア度の高い単語カードの獲得がジャックポット・連チャンの開始条件として機能する。一方、プレイヤーが単語学習よりレアカード収集に夢中になるかどうかを示す利用者調査や行動データは、確認した紹介記事には掲載されていない。
  scope: ゲームの仕組みと、確認した紹介記事の内容
  conditions: 報酬条件は記事に記されたルール。プレイヤーの動機・行動についての一般化は含まない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: 逆転した面白さはゲームの報酬設計から生じる見方として扱う。利用者全般が学習より収集に熱中すると断定しない。

### s38  (confidence max 0.25)
- issue_id: `word_gacha__run_wg_01__b1b__a92a8d5d__rf20261024T085833Z-30da__s38`
- sentence: makes you stop and look at a word you would have passed by because it seemed useful, that’s an interesting way to spark curiosity.
- before: Of course, this system alone can’t tell us whether people really get more interested in opening packs than in memorizing words. / Still, if “It’s rare!”
- after: It’s unexpected to find a gacha at the entrance, though. / “What did you learn today?”
- detected_by: luna-A4(0.25)
- reason [その他]: 「spark curiosity」と好奇心を引き起こす可能性を述べていますが、台帳にはその効果を示す利用者調査や行動データがないのではありませんか。
- fact F10: ゲームの仕組み上、レア度の高い単語カードの獲得がジャックポット・連チャンの開始条件として機能する。一方、プレイヤーが単語学習よりレアカード収集に夢中になるかどうかを示す利用者調査や行動データは、確認した紹介記事には掲載されていない。
  scope: ゲームの仕組みと、確認した紹介記事の内容
  conditions: 報酬条件は記事に記されたルール。プレイヤーの動機・行動についての一般化は含まない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: 逆転した面白さはゲームの報酬設計から生じる見方として扱う。利用者全般が学習より収集に熱中すると断定しない。

### s45  (confidence max 0.4)
- issue_id: `word_gacha__run_wg_01__b1b__a92a8d5d__rf20261024T085833Z-30da__s45`
- sentence: An English-word gacha makes rare, less-used words the prize, even though common words are usually better to learn first.
- before: Now, before we move on to the next card, shall we look at the word’s meaning too? / ## In one line
- after: Rarity reflects word frequency, not what learners should study first. / The game alone cannot show whether players will focus more on opening packs than memorizing words.
- detected_by: luna-A3(0.35), luna-A4(0.4)
- reason [その他]: 『よく使われる単語は通常、先に学ぶ方がよい』という学習上の優先順位は、台帳の『使用頻度と学習上の重要性は別』という説明からは確認できないのではありませんか。
- reason [その他]: 「common words are usually better to learn first」と述べていますが、台帳は単語の使用頻度から学習上の優先順位を結論できないとしているのではありませんか。
- fact F12: GIGAZINEの説明ではレア度の基準は単語の使用頻度であり、学習上の重要性を判定する基準とは示されていない。
  scope: ゲームのレア度説明と、記事内で示された情報
  conditions: 頻度を基準とする仕様から、学習上の重要度も同じ指標だとは結論できない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: レアな単語を「重要」「役に立つ」と同一視しない。頻度と学習上の重要度は別の軸として扱う。
