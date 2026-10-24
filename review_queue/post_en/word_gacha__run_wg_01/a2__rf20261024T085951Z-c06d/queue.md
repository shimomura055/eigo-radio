# Post-EN Risk Flagger Review Queue: word_gacha__run_wg_01 / a2

- run_id: `rf20261024T085951Z-c06d`  status: **OK**
- article_sha256: `b3e0660918a8b2d99f5bc19658cf2e4aa9bdcbbee4b5e24cb90116150b2b520b`  ledger_sha256: `26c3eb894d155700bc2ce8cde612146f08d4e56b37fb987425674b3d87ac0135`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `run_wg_01`
- sentences: 58  facts: 13  candidate issues: 9

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=6 cost_jpy=0.212976 model=gpt-6-luna
- luna A4: OK flags=9 cost_jpy=0.310896 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.227824 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.233984 model=gemini-3.5-flash-lite

## Issues

### s1  (confidence max 0.22)
- issue_id: `word_gacha__run_wg_01__a2__b3e06609__rf20261024T085951Z-c06d__s1`
- sentence: # I Checked How Rare the Words Were Before Learning Them: “Rare-Word Hunting” Starts with an English Word Gacha
- after: If you want to learn English words, start with the ones people use often. / That is clearly right, and no one can argue with it.
- detected_by: luna-A4(0.22)
- reason [その他]: 「I Checked」とある実体験は台帳に記載されていないため、確認が必要ではありませんか。

### s2  (confidence max 0.35)
- issue_id: `word_gacha__run_wg_01__a2__b3e06609__rf20261024T085951Z-c06d__s2`
- sentence: If you want to learn English words, start with the ones people use often.
- before: # I Checked How Rare the Words Were Before Learning Them: “Rare-Word Hunting” Starts with an English Word Gacha
- after: That is clearly right, and no one can argue with it. / Still, when a gacha appears, the good student in you steps away.
- detected_by: luna-A3(0.35), luna-A4(0.35)
- reason [その他]: 「start with the ones people use often」は、使用頻度が高い単語ほど学習優先度も高いと示す表現ではありませんか。
- reason [その他]: 「people use often」と「learn first」を結び付ける学習上の優先順位は、台帳では確認できないのではありませんか。
- fact F12: GIGAZINEの説明ではレア度の基準は単語の使用頻度であり、学習上の重要性を判定する基準とは示されていない。
  scope: ゲームのレア度説明と、記事内で示された情報
  conditions: 頻度を基準とする仕様から、学習上の重要度も同じ指標だとは結論できない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: レアな単語を「重要」「役に立つ」と同一視しない。頻度と学習上の重要度は別の軸として扱う。

### s13  (confidence max 0.35)
- issue_id: `word_gacha__run_wg_01__a2__b3e06609__rf20261024T085951Z-c06d__s13`
- sentence: Surprisingly, useful words and star power do not go together.
- before: Words used less often have higher levels. / The words you should learn first seem boring in the game.
- after: Usually, you might ask, “Can I use this in a conversation?” / But now you may lean forward and ask, “What?
- detected_by: luna-A3(0.32), luna-A4(0.35)
- reason [その他]: 「useful words and star power do not go together」は、使用頻度に基づくレア度と学習上の有用性が必ず反比例するという意味ではありませんか。
- reason [その他]: 「useful words」と「star power」が結び付かないという断定は、使用頻度によるレア度と学習上の重要性を別の軸とする台帳の説明を超えていませんか。
- fact F03: カードのレア度は低い順にC、UC、R、SR、SSR、UR、LRの7段階。GIGAZINEは、使用頻度が高い単語ほどレア度が低く、頻度が低い単語ほどレア度が高い仕組みと説明している。
  scope: ゲーム内の英単語カード
  conditions: GIGAZINEの説明するゲーム内ルール。
  numeric_value: 7段階 (numeric_scope: CからLRまでのレア度区分数)
  date_or_period: 2026-10-23のプレイレビュー時
  notes_for_writer: 「レア度」は記事上、単語の使用頻度に対応するゲーム上の区分。学習上の重要度や難易度と同義とはしない。
- fact F12: GIGAZINEの説明ではレア度の基準は単語の使用頻度であり、学習上の重要性を判定する基準とは示されていない。
  scope: ゲームのレア度説明と、記事内で示された情報
  conditions: 頻度を基準とする仕様から、学習上の重要度も同じ指標だとは結論できない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: レアな単語を「重要」「役に立つ」と同一視しない。頻度と学習上の重要度は別の軸として扱う。

### s27  (confidence max 0.3)
- issue_id: `word_gacha__run_wg_01__a2__b3e06609__rf20261024T085951Z-c06d__s27`
- sentence: First, you draw a card because you want to learn.
- before: What may happen here is not that you stop liking English words. / Instead, the reason for your interest may change.
- after: Then, you look at words because you want to draw a card. / You may still be looking at the same cards.
- detected_by: luna-A4(0.3)
- reason [その他]: 「want to learn」ことがカードを引く動機だという記述は、確認した記事に利用者の動機を示すデータがないという台帳の注意を外れていませんか。
- fact F10: ゲームの仕組み上、レア度の高い単語カードの獲得がジャックポット・連チャンの開始条件として機能する。一方、プレイヤーが単語学習よりレアカード収集に夢中になるかどうかを示す利用者調査や行動データは、確認した紹介記事には掲載されていない。
  scope: ゲームの仕組みと、確認した紹介記事の内容
  conditions: 報酬条件は記事に記されたルール。プレイヤーの動機・行動についての一般化は含まない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: 逆転した面白さはゲームの報酬設計から生じる見方として扱う。利用者全般が学習より収集に熱中すると断定しない。

### s28  (confidence max 0.38)
- issue_id: `word_gacha__run_wg_01__a2__b3e06609__rf20261024T085951Z-c06d__s28`
- sentence: Then, you look at words because you want to draw a card.
- before: Instead, the reason for your interest may change. / First, you draw a card because you want to learn.
- after: You may still be looking at the same cards. / But the person in charge inside your mind has changed.
- detected_by: luna-A3(0.38), luna-A4(0.3)
- reason [その他]: 「you look at words because you want to draw a card」は、プレイヤーが学習よりカード獲得を動機に単語を見ると断定しているのではありませんか。
- reason [その他]: 「want to draw a card」ことが単語を見る動機に変わるという記述は、利用者の行動として確認された事実ではないのではありませんか。
- fact F10: ゲームの仕組み上、レア度の高い単語カードの獲得がジャックポット・連チャンの開始条件として機能する。一方、プレイヤーが単語学習よりレアカード収集に夢中になるかどうかを示す利用者調査や行動データは、確認した紹介記事には掲載されていない。
  scope: ゲームの仕組みと、確認した紹介記事の内容
  conditions: 報酬条件は記事に記されたルール。プレイヤーの動機・行動についての一般化は含まない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: 逆転した面白さはゲームの報酬設計から生じる見方として扱う。利用者全般が学習より収集に熱中すると断定しない。

### s31  (confidence max 0.3)
- issue_id: `word_gacha__run_wg_01__a2__b3e06609__rf20261024T085951Z-c06d__s31`
- sentence: The study worker is no longer in charge.
- before: You may still be looking at the same cards. / But the person in charge inside your mind has changed.
- after: The treasure hunter is. / But here is something to mark in red.
- detected_by: luna-A3(0.3), luna-A4(0.25)
- reason [その他]: 「The study worker is no longer in charge」は、プレイヤーの行動や動機が学習から収集へ変わると断定しているのではありませんか。
- reason [その他]: 「study worker is no longer in charge」という利用者の動機の変化は、台帳にある報酬設計の説明を超えた一般化ではありませんか。
- fact F10: ゲームの仕組み上、レア度の高い単語カードの獲得がジャックポット・連チャンの開始条件として機能する。一方、プレイヤーが単語学習よりレアカード収集に夢中になるかどうかを示す利用者調査や行動データは、確認した紹介記事には掲載されていない。
  scope: ゲームの仕組みと、確認した紹介記事の内容
  conditions: 報酬条件は記事に記されたルール。プレイヤーの動機・行動についての一般化は含まない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: 逆転した面白さはゲームの報酬設計から生じる見方として扱う。利用者全般が学習より収集に熱中すると断定しない。

### s32  (confidence max 0.3)
- issue_id: `word_gacha__run_wg_01__a2__b3e06609__rf20261024T085951Z-c06d__s32`
- sentence: The treasure hunter is.
- before: But the person in charge inside your mind has changed. / The study worker is no longer in charge.
- after: But here is something to mark in red. / A rare word does not have to be high on your study list.
- detected_by: luna-A3(0.3), luna-A4(0.25)
- reason [その他]: 「The treasure hunter is」は、プレイヤーの行動や動機が学習から収集へ変わると断定しているのではありませんか。
- reason [その他]: 「treasure hunter」が内面を支配するという利用者の状態は、台帳で確認された行動・動機ではないのではありませんか。
- fact F10: ゲームの仕組み上、レア度の高い単語カードの獲得がジャックポット・連チャンの開始条件として機能する。一方、プレイヤーが単語学習よりレアカード収集に夢中になるかどうかを示す利用者調査や行動データは、確認した紹介記事には掲載されていない。
  scope: ゲームの仕組みと、確認した紹介記事の内容
  conditions: 報酬条件は記事に記されたルール。プレイヤーの動機・行動についての一般化は含まない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: 逆転した面白さはゲームの報酬設計から生じる見方として扱う。利用者全般が学習より収集に熱中すると断定しない。

### s49  (confidence max 0.25)
- issue_id: `word_gacha__run_wg_01__a2__b3e06609__rf20261024T085951Z-c06d__s49`
- sentence: That is an interesting way to spark curiosity.
- before: may make you stop and look at a word. / You might have passed it by because it seemed useful.
- after: It is unexpected to find a gacha at the entrance, though. / “What did you learn today?”
- detected_by: luna-A4(0.25)
- reason [その他]: レア表示が好奇心を刺激するという因果的な効果は、台帳にある報酬設計の説明だけでは確認できないのではありませんか。
- fact F10: ゲームの仕組み上、レア度の高い単語カードの獲得がジャックポット・連チャンの開始条件として機能する。一方、プレイヤーが単語学習よりレアカード収集に夢中になるかどうかを示す利用者調査や行動データは、確認した紹介記事には掲載されていない。
  scope: ゲームの仕組みと、確認した紹介記事の内容
  conditions: 報酬条件は記事に記されたルール。プレイヤーの動機・行動についての一般化は含まない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: 逆転した面白さはゲームの報酬設計から生じる見方として扱う。利用者全般が学習より収集に熱中すると断定しない。

### s56  (confidence max 0.35)
- issue_id: `word_gacha__run_wg_01__a2__b3e06609__rf20261024T085951Z-c06d__s56`
- sentence: A word gacha makes rare words the prize, though common words are usually better to learn first.
- before: Before the next card, shall we also check the word’s meaning? / ## In one line
- after: Rarity shows how often a word is used, not what learners should study first. / The game alone cannot show if players will open more packs than learn words by heart.
- detected_by: luna-A3(0.34), luna-A4(0.35)
- reason [その他]: 「common words are usually better to learn first」は、使用頻度が高い単語を学習上も優先すべきだと示す表現ではありませんか。
- reason [その他]: 「common words are usually better to learn first」という学習上の優先順位は、台帳では確認できないのではありませんか。
- fact F03: カードのレア度は低い順にC、UC、R、SR、SSR、UR、LRの7段階。GIGAZINEは、使用頻度が高い単語ほどレア度が低く、頻度が低い単語ほどレア度が高い仕組みと説明している。
  scope: ゲーム内の英単語カード
  conditions: GIGAZINEの説明するゲーム内ルール。
  numeric_value: 7段階 (numeric_scope: CからLRまでのレア度区分数)
  date_or_period: 2026-10-23のプレイレビュー時
  notes_for_writer: 「レア度」は記事上、単語の使用頻度に対応するゲーム上の区分。学習上の重要度や難易度と同義とはしない。
- fact F12: GIGAZINEの説明ではレア度の基準は単語の使用頻度であり、学習上の重要性を判定する基準とは示されていない。
  scope: ゲームのレア度説明と、記事内で示された情報
  conditions: 頻度を基準とする仕様から、学習上の重要度も同じ指標だとは結論できない。
  date_or_period: 2026-10-23のプレイレビューの記載範囲
  notes_for_writer: レアな単語を「重要」「役に立つ」と同一視しない。頻度と学習上の重要度は別の軸として扱う。
