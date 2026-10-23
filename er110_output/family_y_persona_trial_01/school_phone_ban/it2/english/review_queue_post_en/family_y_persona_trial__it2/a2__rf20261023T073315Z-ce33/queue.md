# Post-EN Risk Flagger Review Queue: family_y_persona_trial__it2 / a2

- run_id: `rf20261023T073315Z-ce33`  status: **OK**
- article_sha256: `bd92b00e8cd03524ae0f9f98d348e70e712d08901829b549f79643f5927a3588`  ledger_sha256: `115a6528d97f9dab19f9b5022e2ce13ca83b4f50316f248dfaa9d3e45a67da89`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `None`  run_label: `FAMILY-Y-PERSONA-TRIAL-it2`
- sentences: 66  facts: 15  candidate issues: 16

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.140656 model=gpt-6-luna
- luna A4: OK flags=16 cost_jpy=0.264656 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.125973 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.13169 model=gemini-3.5-flash-lite

## Issues

### s2  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s2`
- sentence: I want my daughter's high school to keep the phones.
- before: # Phones Handed In in the Morning: Different Voices
- after: Collect them all in the morning. / Give them back when school lets out.
- detected_by: luna-A4(0.2)
- reason [その他]: 「my daughter's high school」という家族関係と学校に関する情報は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s7  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s7`
- sentence: We agreed she'd put her phone in a basket in the living room at night.
- before: Until then, they stay with the school. / Then I wouldn't be the only bad guy.
- after: My daughter didn't keep that promise. / So I took her phone away.
- detected_by: luna-A4(0.2)
- reason [その他]: 「合意して娘が夜に携帯電話を居間のかごに入れることにした」という出来事は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s8  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s8`
- sentence: My daughter didn't keep that promise.
- before: Then I wouldn't be the only bad guy. / We agreed she'd put her phone in a basket in the living room at night.
- after: So I took her phone away. / The next morning, breakfast was quiet.
- detected_by: luna-A4(0.2)
- reason [その他]: 「娘が約束を守らなかった」という出来事は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s9  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s9`
- sentence: So I took her phone away.
- before: We agreed she'd put her phone in a basket in the living room at night. / My daughter didn't keep that promise.
- after: The next morning, breakfast was quiet. / I could hear only dishes.
- detected_by: luna-A4(0.2)
- reason [その他]: 「父親が娘の携帯電話を取り上げた」という出来事は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s10  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s10`
- sentence: The next morning, breakfast was quiet.
- before: My daughter didn't keep that promise. / So I took her phone away.
- after: I could hear only dishes. / I wanted her to keep our agreement.
- detected_by: luna-A4(0.2)
- reason [その他]: 「翌朝の朝食時に静かだった」という出来事は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s22  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s22`
- sentence: Every morning, I see kids come to the nurse's office first thing.
- before: I'm a dad asking the school to come to my rescue. / “I'm sleepy,” they say.
- after: I wonder what else is behind that word. / The other day, a child's phone screen glowed beside their pillow.
- detected_by: luna-A4(0.2)
- reason [その他]: 「毎朝、子どもたちがまず保健室に来る」という頻度と行動は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s24  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s24`
- sentence: The other day, a child's phone screen glowed beside their pillow.
- before: Every morning, I see kids come to the nurse's office first thing. / I wonder what else is behind that word.
- after: The child was resting on a bed. / I couldn't look away from that glow.
- detected_by: luna-A4(0.2)
- reason [その他]: 「先日、子どもの枕元で携帯電話の画面が光っていた」という出来事は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s25  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s25`
- sentence: The child was resting on a bed.
- before: I wonder what else is behind that word. / The other day, a child's phone screen glowed beside their pillow.
- after: I couldn't look away from that glow. / I wanted to ask what happened last night.
- detected_by: luna-A4(0.2)
- reason [その他]: 「その子がベッドで休んでいた」という状況は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s36  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s36`
- sentence: I sort packages in a warehouse during the day.
- before: I don't want phones to be taken away in the nurse's office. / After we take a phone away, who will listen to that child?
- after: At night, I go to evening high school. / But I can't hand in my phone until school lets out.
- detected_by: luna-A4(0.2)
- reason [その他]: 「話者が日中に倉庫で荷物を仕分けしている」という職業上の情報は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s37  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s37`
- sentence: At night, I go to evening high school.
- before: After we take a phone away, who will listen to that child? / I sort packages in a warehouse during the day.
- after: But I can't hand in my phone until school lets out. / I can promise not to touch it during class.
- detected_by: luna-A4(0.2)
- reason [その他]: 「話者が夜間高校に通っている」という情報は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s41  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s41`
- sentence: Before, calls from work kept coming during class.
- before: I can promise not to touch it during class. / During breaks, I want to answer messages from work.
- after: I couldn't answer them. / The missed calls kept piling up on my screen.
- detected_by: luna-A4(0.2)
- reason [その他]: 「以前、授業中に仕事先から電話が続けてかかってきた」という出来事は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s42  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s42`
- sentence: I couldn't answer them.
- before: During breaks, I want to answer messages from work. / Before, calls from work kept coming during class.
- after: The missed calls kept piling up on my screen. / Later, they told me it was a problem that they couldn't reach me.
- detected_by: luna-A4(0.2)
- reason [その他]: 「話者がその電話に出られなかった」という出来事は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s43  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s43`
- sentence: The missed calls kept piling up on my screen.
- before: Before, calls from work kept coming during class. / I couldn't answer them.
- after: Later, they told me it was a problem that they couldn't reach me. / I almost had my shifts cut.
- detected_by: luna-A4(0.2)
- reason [その他]: 「不在着信が画面に増え続けた」という出来事は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s44  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s44`
- sentence: Later, they told me it was a problem that they couldn't reach me.
- before: I couldn't answer them. / The missed calls kept piling up on my screen.
- after: I almost had my shifts cut. / I give the money I earn to my family.
- detected_by: luna-A4(0.2)
- reason [その他]: 「仕事先から連絡が取れないことを問題だと言われた」という出来事は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s45  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s45`
- sentence: I almost had my shifts cut.
- before: The missed calls kept piling up on my screen. / Later, they told me it was a problem that they couldn't reach me.
- after: I give the money I earn to my family. / I want to earn trust at work myself.
- detected_by: luna-A4(0.2)
- reason [その他]: 「話者が勤務シフトを減らされかけた」という出来事は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。

### s46  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it2__a2__bd92b00e__rf20261023T073315Z-ce33__s46`
- sentence: I give the money I earn to my family.
- before: Later, they told me it was a problem that they couldn't reach me. / I almost had my shifts cut.
- after: I want to earn trust at work myself. / But I don't want to quit school.
- detected_by: luna-A4(0.2)
- reason [その他]: 「話者が稼いだお金を家族に渡している」という情報は台帳に記載がなく、裏付けを確認する必要があるのではありませんか。
