# Post-EN Risk Flagger Review Queue: family_y_trial__r1 / a2

- run_id: `rf20261023T023843Z-bfb7`  status: **OK**
- article_sha256: `70a9528167b06a3cbad7e8d8d5c4e2e3fb7c04414dda8e2c6d8984b5baeb874a`  ledger_sha256: `115a6528d97f9dab19f9b5022e2ce13ca83b4f50316f248dfaa9d3e45a67da89`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `None`  run_label: `FAMILY-Y-TRIAL-r1`
- sentences: 46  facts: 15  candidate issues: 4

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.121904 model=gpt-6-luna
- luna A4: OK flags=4 cost_jpy=0.229024 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.186755 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.192472 model=gemini-3.5-flash-lite

## Issues

### s8  (confidence max 0.25)
- issue_id: `family_y_trial__r1__a2__70a95281__rf20261023T023843Z-bfb7__s8`
- sentence: I teach Japanese at a junior high school.
- before: But different alarms ring in their minds. / Before class, I mark the parts of a text that I want to discuss with my students.
- after: If phones are in bags, can students focus on the text in front of them? / That makes me hopeful.
- detected_by: luna-A4(0.25)
- reason [その他]: 「I teach Japanese at a junior high school」という職業・勤務先の記述は台帳で確認できませんが、事実関係を確認する必要があるのではありませんか。

### s17  (confidence max 0.25)
- issue_id: `family_y_trial__r1__a2__70a95281__rf20261023T023843Z-bfb7__s17`
- sentence: I review school budgets for the local government.
- before: What if checking that phones are away takes time from working with the text? / That would be a problem.
- after: I spread papers about managing devices and supporting learning across my desk. / Then I add sticky notes.
- detected_by: luna-A4(0.25)
- reason [その他]: 「I review school budgets for the local government」という職務の記述は台帳で確認できませんが、事実関係を確認する必要があるのではありませんか。

### s24  (confidence max 0.25)
- issue_id: `family_y_trial__r1__a2__70a95281__rf20261023T023843Z-bfb7__s24`
- sentence: I worry that spending money on bags could mean cutting support students need.
- before: Can I really explain the link: put phones away, and grades go up? / Budgets are limited.
- after: I cannot treat schools overseas and schools in this area as the same. / Even so, I have to show why I think the money should be spent that way.
- detected_by: luna-A4(0.25)
- reason [その他]: 「spending money on bags could mean cutting support students need」という支出と支援削減の関係は台帳で確認できませんが、事実関係を確認する必要があるのではありませんか。

### s27  (confidence max 0.25)
- issue_id: `family_y_trial__r1__a2__70a95281__rf20261023T023843Z-bfb7__s27`
- sentence: At the evening high school I go to after work, I take out my notebook.
- before: I cannot treat schools overseas and schools in this area as the same. / Even so, I have to show why I think the money should be spent that way.
- after: I check whether I still have work messages on my phone. / I want to avoid using it in class.
- detected_by: luna-A4(0.25)
- reason [その他]: 「At the evening high school I go to after work」という在学状況の記述は台帳で確認できませんが、事実関係を確認する必要があるのではありませんか。
