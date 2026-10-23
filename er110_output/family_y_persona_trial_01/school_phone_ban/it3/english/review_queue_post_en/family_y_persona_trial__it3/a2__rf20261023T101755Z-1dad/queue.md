# Post-EN Risk Flagger Review Queue: family_y_persona_trial__it3 / a2

- run_id: `rf20261023T101755Z-1dad`  status: **OK**
- article_sha256: `f1a20d466227e6138b5693480218727bc96e0dc955c7a58651f39a9ee6e0504c`  ledger_sha256: `115a6528d97f9dab19f9b5022e2ce13ca83b4f50316f248dfaa9d3e45a67da89`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `None`  run_label: `FAMILY-Y-PERSONA-TRIAL-it3`
- sentences: 64  facts: 15  candidate issues: 10

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.135152 model=gpt-6-luna
- luna A4: OK flags=10 cost_jpy=0.275872 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.125493 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.13121 model=gemini-3.5-flash-lite

## Issues

### s16  (confidence max 0.25)
- issue_id: `family_y_persona_trial__it3__a2__f1a20d46__rf20261023T101755Z-1dad__s16`
- sentence: But if she can't use her phone at school, nothing changes at home at night.
- before: I want her to keep our promise. / I don't want to shout like my father, either.
- after: Maybe I just want the school to help so my life is easier. / I am a site supervisor who can't even manage things at home.
- detected_by: luna-A4(0.25)
- reason [その他]: 「学校で携帯電話を使えなくても夜の家庭での状況は変わらない」という因果関係は台帳Factで確認できず、事実関係の確認が必要ではありませんか。

### s26  (confidence max 0.3)
- issue_id: `family_y_persona_trial__it3__a2__f1a20d46__rf20261023T101755Z-1dad__s26`
- sentence: After their phone was taken away at school, they stopped coming to see me.
- before: When I hear they stayed up until morning, I don't know what to say. / I also think about one student.
- after: If they don't come, does that mean they are okay? / A teacher asked me, “If we ban phones, will fewer kids come to the nurse's office?”
- detected_by: luna-A4(0.3)
- reason [その他]: 「学校で携帯電話を取り上げられた後、その生徒が相談に来なくなった」という出来事は台帳Factで確認できず、事実関係の確認が必要ではありませんか。

### s38  (confidence max 0.25)
- issue_id: `family_y_persona_trial__it3__a2__f1a20d46__rf20261023T101755Z-1dad__s38`
- sentence: So I can't promise to stop all contact while I'm at school.
- before: I work at a warehouse during the day. / At night, I go to evening high school.
- after: Between classes, I get messages about my shifts. / If I reply late, the work goes to someone else.
- detected_by: luna-A4(0.25)
- reason [その他]: 「学校にいる間、すべての連絡を止める約束はできない」という事情は台帳Factで確認できず、事実関係の確認が必要ではありませんか。

### s40  (confidence max 0.25)
- issue_id: `family_y_persona_trial__it3__a2__f1a20d46__rf20261023T101755Z-1dad__s40`
- sentence: If I reply late, the work goes to someone else.
- before: So I can't promise to stop all contact while I'm at school. / Between classes, I get messages about my shifts.
- after: Once, my workplace kept calling during class. / I couldn't answer.
- detected_by: luna-A4(0.25)
- reason [その他]: 「返信が遅れると仕事が別の人に回る」という因果関係は台帳Factで確認できず、事実関係の確認が必要ではありませんか。

### s41  (confidence max 0.25)
- issue_id: `family_y_persona_trial__it3__a2__f1a20d46__rf20261023T101755Z-1dad__s41`
- sentence: Once, my workplace kept calling during class.
- before: Between classes, I get messages about my shifts. / If I reply late, the work goes to someone else.
- after: I couldn't answer. / Later, they told me it was a problem that they could not reach me.
- detected_by: luna-A4(0.25)
- reason [その他]: 「勤務先が授業中に何度も電話をかけた」という出来事は台帳Factで確認できず、事実関係の確認が必要ではありませんか。

### s43  (confidence max 0.25)
- issue_id: `family_y_persona_trial__it3__a2__f1a20d46__rf20261023T101755Z-1dad__s43`
- sentence: Later, they told me it was a problem that they could not reach me.
- before: Once, my workplace kept calling during class. / I couldn't answer.
- after: They almost cut my shifts, too. / I want to graduate from this school.
- detected_by: luna-A4(0.25)
- reason [その他]: 「連絡がつかなかったことを勤務先が問題視した」という出来事は台帳Factで確認できず、事実関係の確認が必要ではありませんか。

### s44  (confidence max 0.25)
- issue_id: `family_y_persona_trial__it3__a2__f1a20d46__rf20261023T101755Z-1dad__s44`
- sentence: They almost cut my shifts, too.
- before: I couldn't answer. / Later, they told me it was a problem that they could not reach me.
- after: I want to graduate from this school. / I also need money to give to my family.
- detected_by: luna-A4(0.25)
- reason [その他]: 「勤務先がシフトを減らしかけた」という出来事は台帳Factで確認できず、事実関係の確認が必要ではありませんか。

### s53  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it3__a2__f1a20d46__rf20261023T101755Z-1dad__s53`
- sentence: Longer phone-free time may mean fewer fights about the basket at night.
- before: But before you decide, please hear how I work, too. / At breakfast, beside the pillow in the nurse's office, and through work messages during breaks, people want to keep talking with someone.
- after: But a student whose phone is taken away may stop talking at the bedside. / He may follow the rule in class.
- detected_by: luna-A4(0.2)
- reason [その他]: 「携帯電話を使えない時間が長くなると夜の口論が減る可能性がある」という因果関係は台帳Factで確認できず、事実関係の確認が必要ではありませんか。

### s54  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it3__a2__f1a20d46__rf20261023T101755Z-1dad__s54`
- sentence: But a student whose phone is taken away may stop talking at the bedside.
- before: At breakfast, beside the pillow in the nurse's office, and through work messages during breaks, people want to keep talking with someone. / Longer phone-free time may mean fewer fights about the basket at night.
- after: He may follow the rule in class. / But if his shift messages stop during breaks, his workplace may lose trust in him.
- detected_by: luna-A4(0.2)
- reason [その他]: 「携帯電話を取り上げられた生徒が相談しなくなる可能性がある」という因果関係は台帳Factで確認できず、事実関係の確認が必要ではありませんか。

### s56  (confidence max 0.2)
- issue_id: `family_y_persona_trial__it3__a2__f1a20d46__rf20261023T101755Z-1dad__s56`
- sentence: But if his shift messages stop during breaks, his workplace may lose trust in him.
- before: But a student whose phone is taken away may stop talking at the bedside. / He may follow the rule in class.
- after: The father who asks the school for help also does not want another silent morning after taking the phone away. / They may disagree about how long phones can be used.
- detected_by: luna-A4(0.2)
- reason [その他]: 「休み時間の勤務連絡が止まると勤務先の信頼を失う可能性がある」という因果関係は台帳Factで確認できず、事実関係の確認が必要ではありませんか。
