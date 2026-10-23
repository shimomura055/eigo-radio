# Post-EN Risk Flagger Review Queue: family_y_trial__r2 / b1b

- run_id: `rf20261023T023826Z-c83e`  status: **OK**
- article_sha256: `3da626ef5db0ece2b0c01e938e1ec8bff90bf56cbaee5658b144b61cecdf998d`  ledger_sha256: `115a6528d97f9dab19f9b5022e2ce13ca83b4f50316f248dfaa9d3e45a67da89`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `None`  run_label: `FAMILY-Y-TRIAL-r2`
- sentences: 41  facts: 15  candidate issues: 7

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.121632 model=gpt-6-luna
- luna A4: OK flags=7 cost_jpy=0.210112 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.186659 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.192776 model=gemini-3.5-flash-lite

## Issues

### s5  (confidence max 0.28)
- issue_id: `family_y_trial__r2__b1b__3da626ef__rf20261023T023826Z-c83e__s5`
- sentence: A Japanese teacher, someone who reviews school budgets, and a student who goes to school while working: even when they face the same bag, different alarms go off in each person’s mind.
- before: If only we could lock away the problems in the classroom, too. / When the screen goes dark, does the learning switch turn on by itself?
- after: Before class, I mark the passages I want to discuss with my middle school Japanese class. / Looking at the lesson plan spread across the teacher’s desk, I think about where to add a check that everyone has put their phone away.
- detected_by: luna-A4(0.28)
- reason [その他]: 「日本の教師」「自治体の予算審査担当者」「働きながら通学する生徒」という人物設定は、台帳に対応するFactが見当たらず、確認が必要ではありませんか。

### s6  (confidence max 0.3)
- issue_id: `family_y_trial__r2__b1b__3da626ef__rf20261023T023826Z-c83e__s6`
- sentence: Before class, I mark the passages I want to discuss with my middle school Japanese class.
- before: When the screen goes dark, does the learning switch turn on by itself? / A Japanese teacher, someone who reviews school budgets, and a student who goes to school while working: even when they face the same bag, different alarms go off in each person’s mind.
- after: Looking at the lesson plan spread across the teacher’s desk, I think about where to add a check that everyone has put their phone away. / I want them to focus on the text without worrying about their screens.
- detected_by: luna-A4(0.3)
- reason [その他]: 「中学校の国語の授業を担当する」という記述は、台帳に対応するFactが見当たらず、確認が必要ではありませんか。

### s15  (confidence max 0.3)
- issue_id: `family_y_trial__r2__b1b__3da626ef__rf20261023T023826Z-c83e__s15`
- sentence: I review school budgets for the local government.
- before: It’s my responsibility to keep the lesson moving. / I can’t think that a quiet classroom is enough.
- after: I lay out the costs of managing devices and the papers on learning support on my desk, and mark them with sticky notes. / Is it right to count the cost of putting phones away as spending to help students do better in school?
- detected_by: luna-A4(0.3)
- reason [その他]: 「自治体の予算を審査する」という職務の記述は、台帳に対応するFactが見当たらず、確認が必要ではありませんか。

### s23  (confidence max 0.32)
- issue_id: `family_y_trial__r2__b1b__3da626ef__rf20261023T023826Z-c83e__s23`
- sentence: Since I decide how the money is divided, I can’t avoid explaining why.
- before: I worry that spending money on the bags could mean cutting support for students who need help with learning. / At the same time, I still can’t tell whether this cost is necessary.
- after: After work, at the evening high school I attend, I take out my notebook and check whether I still have any work messages on my phone. / I want to avoid using it during class.
- detected_by: luna-A4(0.32)
- reason [その他]: 「予算の配分を決める」という権限の記述は、台帳に対応するFactが見当たらず、確認が必要ではありませんか。

### s24  (confidence max 0.28)
- issue_id: `family_y_trial__r2__b1b__3da626ef__rf20261023T023826Z-c83e__s24`
- sentence: After work, at the evening high school I attend, I take out my notebook and check whether I still have any work messages on my phone.
- before: At the same time, I still can’t tell whether this cost is necessary. / Since I decide how the money is divided, I can’t avoid explaining why.
- after: I want to avoid using it during class. / But can I really say with confidence, “No matter what happens, I can stay away from work messages”?
- detected_by: luna-A4(0.28)
- reason [その他]: 「夜間高校に通い、仕事のメッセージを携帯電話で確認する」という人物設定は、台帳に対応するFactが見当たらず、確認が必要ではありませんか。

### s40  (confidence max 0.22)
- issue_id: `family_y_trial__r2__b1b__3da626ef__rf20261023T023826Z-c83e__s40`
- sentence: A teacher, a school budget reviewer, and a working student each see different risks in locking phones away at school.
- before: Before we close the bag, are we shutting out even the acceptance someone has not yet found the words to express? / ## In one line
- after: They all value learning, but their stakes and responsibilities differ, and those with much to protect may have little say.
- detected_by: luna-A4(0.22)
- reason [その他]: 「教師・予算審査担当者・働く生徒が、それぞれ異なるリスクを見る」という要約は、台帳に対応するFactが見当たらず、確認が必要ではありませんか。

### s41  (confidence max 0.2)
- issue_id: `family_y_trial__r2__b1b__3da626ef__rf20261023T023826Z-c83e__s41`
- sentence: They all value learning, but their stakes and responsibilities differ, and those with much to protect may have little say.
- before: ## In one line / A teacher, a school budget reviewer, and a working student each see different risks in locking phones away at school.
- detected_by: luna-A4(0.2)
- reason [その他]: 「守るものが多い人ほど発言権が少ない」という一般化は、台帳に対応するFactが見当たらず、確認が必要ではありませんか。
