# Post-EN Risk Flagger Review Queue: family_y_persona_trial__it2 / b1b

- run_id: `rf20261023T073237Z-7b86`  status: **OK**
- article_sha256: `7b498a0cc3a951b46eeb66cf1372ddabb7f9e88f08b473638d9c276884949d54`  ledger_sha256: `115a6528d97f9dab19f9b5022e2ce13ca83b4f50316f248dfaa9d3e45a67da89`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `None`  run_label: `FAMILY-Y-PERSONA-TRIAL-it2`
- sentences: 55  facts: 15  candidate issues: 10

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.130768 model=gpt-6-luna
- luna A4: OK flags=10 cost_jpy=0.317568 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.2932 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.29936 model=gemini-3.5-flash-lite

## Issues

### s7  (confidence max 0.24)
- issue_id: `family_y_persona_trial__it2__b1b__7b498a0c__rf20261023T073237Z-7b86__s7`
- sentence: We agreed that at night, she'd put her phone in a basket in the living room.
- before: Until then, they stay handed in. / Then I wouldn't be the only bad guy.
- after: My daughter didn't keep that promise. / I took her phone away.
- detected_by: luna-A4(0.24)
- reason [その他]: 「夜に娘が居間のかごに携帯電話を入れると約束した」という出来事は、台帳Factでは確認できない事実主張ではありませんか。

### s8  (confidence max 0.24)
- issue_id: `family_y_persona_trial__it2__b1b__7b498a0c__rf20261023T073237Z-7b86__s8`
- sentence: My daughter didn't keep that promise.
- before: Then I wouldn't be the only bad guy. / We agreed that at night, she'd put her phone in a basket in the living room.
- after: I took her phone away. / The next morning, breakfast was quiet.
- detected_by: luna-A4(0.24)
- reason [その他]: 「娘がその約束を守らなかった」という出来事は、台帳Factでは確認できない事実主張ではありませんか。

### s9  (confidence max 0.24)
- issue_id: `family_y_persona_trial__it2__b1b__7b498a0c__rf20261023T073237Z-7b86__s9`
- sentence: I took her phone away.
- before: We agreed that at night, she'd put her phone in a basket in the living room. / My daughter didn't keep that promise.
- after: The next morning, breakfast was quiet. / All I could hear was the sound of dishes.
- detected_by: luna-A4(0.24)
- reason [その他]: 「父親が娘の携帯電話を取り上げた」という出来事は、台帳Factでは確認できない事実主張ではありませんか。

### s21  (confidence max 0.28)
- issue_id: `family_y_persona_trial__it2__b1b__7b498a0c__rf20261023T073237Z-7b86__s21`
- sentence: Every morning, I see the faces of kids who come to the nurse's office first thing, and I wonder what else is behind that word.
- before: I'm a dad asking the school to come to my rescue. / “I'm sleepy,” they say.
- after: The other day, a phone screen was glowing beside the pillow of a child resting on a bed. / I couldn't look away from that glow.
- detected_by: luna-A4(0.28)
- reason [その他]: 「毎朝、保健室に来る子どもたちを見ている」という継続的な経験は、台帳Factでは確認できない事実主張ではありませんか。

### s22  (confidence max 0.28)
- issue_id: `family_y_persona_trial__it2__b1b__7b498a0c__rf20261023T073237Z-7b86__s22`
- sentence: The other day, a phone screen was glowing beside the pillow of a child resting on a bed.
- before: “I'm sleepy,” they say. / Every morning, I see the faces of kids who come to the nurse's office first thing, and I wonder what else is behind that word.
- after: I couldn't look away from that glow. / I wanted to ask about last night, but what would happen if they thought I was a teacher who takes phones away?
- detected_by: luna-A4(0.28)
- reason [その他]: 「休んでいる子どもの枕元で携帯電話の画面が光っていた」という出来事は、台帳Factでは確認できない事実主張ではありませんか。

### s31  (confidence max 0.28)
- issue_id: `family_y_persona_trial__it2__b1b__7b498a0c__rf20261023T073237Z-7b86__s31`
- sentence: I sort packages in a warehouse during the day, and go to evening high school at night.
- before: I don't want the nurse's office to be a place where phones are taken away. / After we take a phone in, who will listen to that child?
- after: But I can't hand in my phone until school lets out. / I can keep my promise not to touch it during class.
- detected_by: luna-A4(0.28)
- reason [その他]: 「日中は倉庫で働き、夜は高校に通っている」という人物の経歴は、台帳Factでは確認できない事実主張ではありませんか。

### s35  (confidence max 0.24)
- issue_id: `family_y_persona_trial__it2__b1b__7b498a0c__rf20261023T073237Z-7b86__s35`
- sentence: Before, calls from work kept coming during class.
- before: I can keep my promise not to touch it during class. / During breaks, I want to answer work messages.
- after: I couldn't answer, and the missed calls just kept piling up on my screen. / Later, they told me it was a problem that they couldn't reach me.
- detected_by: luna-A4(0.24)
- reason [その他]: 「以前、授業中に職場からの電話が続いていた」という経験は、台帳Factでは確認できない事実主張ではありませんか。

### s37  (confidence max 0.24)
- issue_id: `family_y_persona_trial__it2__b1b__7b498a0c__rf20261023T073237Z-7b86__s37`
- sentence: Later, they told me it was a problem that they couldn't reach me.
- before: Before, calls from work kept coming during class. / I couldn't answer, and the missed calls just kept piling up on my screen.
- after: I almost had my shifts cut. / I give the money I earn to my family.
- detected_by: luna-A4(0.24)
- reason [その他]: 「職場から連絡がつかないことを問題だと言われた」という出来事は、台帳Factでは確認できない事実主張ではありませんか。

### s38  (confidence max 0.24)
- issue_id: `family_y_persona_trial__it2__b1b__7b498a0c__rf20261023T073237Z-7b86__s38`
- sentence: I almost had my shifts cut.
- before: I couldn't answer, and the missed calls just kept piling up on my screen. / Later, they told me it was a problem that they couldn't reach me.
- after: I give the money I earn to my family. / I want to earn my workplace's trust myself.
- detected_by: luna-A4(0.24)
- reason [その他]: 「勤務シフトを減らされかけた」という出来事は、台帳Factでは確認できない事実主張ではありませんか。

### s48  (confidence max 0.34)
- issue_id: `family_y_persona_trial__it2__b1b__7b498a0c__rf20261023T073237Z-7b86__s48`
- sentence: It might protect learning in class, but if it also stops messages about shifts during breaks, trust at work could be shaken.
- before: At the breakfast table, beside the pillow in the nurse's office, and when work messages come, people want to stay able to talk to the other person. / The school's phone collection might reduce arguments over the basket at night, but it could cut off a conversation by the pillow.
- after: The father asking the school for help also doesn't want to go through the silence after taking the phone away again. / They may disagree about how long phones should be handed in, but they share a wish to still have someone they can talk to.
- detected_by: luna-A4(0.34)
- reason [その他]: 「授業中の学びを守る可能性がある」という一般的な効果の示唆は、相関的な結果や限定的・混在した成績推定を示す「OECD-02」「STUDY-01」「STUDY-05」の範囲を超えていませんか。
- fact OECD-02: PISA 2022の分析では、校内で携帯電話を禁止している学校の生徒は数学授業でデジタル機器に気を散らされると報告する確率が低い一方、禁止校に通う生徒のうち29%は学校でスマートフォンを日に数回使うと回答し、さらに21%は毎日またはほぼ毎日使うと回答した。
  scope: PISA参加国・地域の生徒。使用頻度の割合はOECD平均の、校内携帯電話禁止校に通う生徒。
  conditions: 禁止と注意散漫の関係はPISAデータ上の関連であり、禁止の因果効果を単独で示すものではない。使用頻度は校内ルールの実施状況を示す自己申告。
  numeric_value: 29%、21% (numeric_scope: 校内携帯電話禁止校に通う生徒のうち、学校でスマートフォンを「日に数回」使用する割合が29%、「毎日またはほぼ毎日」使用する割合が21%。)
  date_or_period: PISA 2022
  causal_strength: CORRELATIONAL
  notes_for_writer: 禁止校での使用実態が残ること、また禁止と注意散漫の関係は相関的な分析であることを併記する。
- fact STUDY-01: 英国4都市の学校方針と行政データを用いた差の差分析では、携帯電話禁止後の重要試験の成績が平均約0.07標準偏差上昇し、上昇は成績下位の生徒を中心に見られたと研究者が報告した。
  scope: 英国の4都市の学校。分析は学校の携帯電話方針と生徒の行政上の成績データを結合したもの。
  conditions: 生徒特性と事前成績を調整した差の差分析。無作為化比較試験ではない。
  numeric_value: 約0.07標準偏差 (numeric_scope: 禁止後の高 stakes 試験における平均的な成績上昇の推定値。)
  date_or_period: 2016年公表。対象となる学校の禁止導入時期は研究データに基づく。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  ambiguity_note: 観察データを用いた準実験的推定であり、別の国・学校段階・禁止方式にも同じ効果があるとは限らない。
  notes_for_writer: 研究者が差の差法で推定した効果として記載し、禁止がどの環境でも成績を上げると一般化しないこと。
- fact STUDY-05: 同NBERワーキングペーパーは、ポーチ導入後のテスト得点への平均効果は一貫してほぼゼロに近く、高校では小幅なプラス（特に数学）、中学校では小幅なマイナスが見られたと報告した。
  scope: 米国のポーチ導入校における学校段階別・平均テスト得点の推定。
  conditions: 学校の導入時期の差を用いた推定。研究対象はロック式ポーチ導入で、学校段階により推定値の方向が異なる。
  date_or_period: 2026年4月刊行、2026年9月改訂のワーキングペーパー
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 全体平均と学校段階別の異質性を分けて記載すること。ワーキングペーパーである点も併記すること。
