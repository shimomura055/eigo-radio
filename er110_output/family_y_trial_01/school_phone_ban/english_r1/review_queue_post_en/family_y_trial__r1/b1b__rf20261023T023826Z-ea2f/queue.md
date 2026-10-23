# Post-EN Risk Flagger Review Queue: family_y_trial__r1 / b1b

- run_id: `rf20261023T023826Z-ea2f`  status: **OK**
- article_sha256: `eeeb63c8ce8bcb9459b6ce8abe35f4d923d9819810ce2d4ff45452800a4846e2`  ledger_sha256: `115a6528d97f9dab19f9b5022e2ce13ca83b4f50316f248dfaa9d3e45a67da89`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `None`  run_label: `FAMILY-Y-TRIAL-r1`
- sentences: 41  facts: 15  candidate issues: 3

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.114464 model=gpt-6-luna
- luna A4: OK flags=3 cost_jpy=0.199984 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.27112 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.27688 model=gemini-3.5-flash-lite

## Issues

### s7  (confidence max 0.28)
- issue_id: `family_y_trial__r1__b1b__eeeb63c8__rf20261023T023826Z-ea2f__s7`
- sentence: I teach Japanese at a junior high school.
- before: A teacher, someone who manages a school budget, and someone who studies while working may all look at the same phone, but different alarms are ringing in their minds. / Before class, I mark the parts of a text I want to discuss with my students.
- after: If the phones are in bags, will students be able to give their attention to the text in front of them? / That makes me hopeful.
- detected_by: luna-A4(0.28)
- reason [その他]: 「I teach Japanese at a junior high school.」という経歴は、台帳Factで確認できない事実主張ではありませんか。

### s15  (confidence max 0.28)
- issue_id: `family_y_trial__r1__b1b__eeeb63c8__rf20261023T023826Z-ea2f__s15`
- sentence: I review school budgets for the local government.
- before: What if checking that the phones are away cuts into the time for working with the text? / That would be a problem.
- after: I spread papers on device management and learning support across my desk and add sticky notes. / Should spending to reduce phone use also be a priority as a way to help students do better in school?
- detected_by: luna-A4(0.28)
- reason [その他]: 「I review school budgets for the local government.」という職務は、台帳Factで確認できない事実主張ではありませんか。

### s24  (confidence max 0.28)
- issue_id: `family_y_trial__r1__b1b__eeeb63c8__rf20261023T023826Z-ea2f__s24`
- sentence: At the evening high school I go to after work, I take out my notebook and check whether I still have work messages on my phone.
- before: I cannot treat schools overseas and schools in this area as if they were the same. / Even so, I have to show why I think the money should go where it does.
- after: I want to avoid using it in class. / But I cannot promise, “No matter what happens, I will stay away from work messages.”
- detected_by: luna-A4(0.28)
- reason [その他]: 「At the evening high school I go to after work」という通学状況は、台帳Factで確認できない事実主張ではありませんか。
