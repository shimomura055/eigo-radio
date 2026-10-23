# Post-EN Risk Flagger Review Queue: family_y_trial__r2 / a2

- run_id: `rf20261023T023844Z-ba22`  status: **OK**
- article_sha256: `fa3afe920dba91dfacc4bd450bf541c90cf83abe47654743d891fbdb388fcff9`  ledger_sha256: `115a6528d97f9dab19f9b5022e2ce13ca83b4f50316f248dfaa9d3e45a67da89`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `None`  run_label: `FAMILY-Y-TRIAL-r2`
- sentences: 51  facts: 15  candidate issues: 7

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.125248 model=gpt-6-luna
- luna A4: OK flags=7 cost_jpy=0.220128 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.193624 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.199384 model=gemini-3.5-flash-lite

## Issues

### s5  (confidence max 0.3)
- issue_id: `family_y_trial__r2__a2__fa3afe92__rf20261023T023844Z-ba22__s5`
- sentence: A Japanese teacher, a school budget worker, and a student who works and goes to school all face the same bag.
- before: If only we could lock away classroom problems, too. / When the screen goes dark, does learning start by itself?
- after: But different alarms go off in each person’s mind. / Before class, I mark parts to discuss with my middle school Japanese class.
- detected_by: luna-A4(0.3)
- reason [その他]: 「日本人教師」「学校予算の担当者」「働きながら通学する生徒」が同じバッグに直面するという記述は、台帳Factで確認できない事実主張ではありませんか。

### s7  (confidence max 0.3)
- issue_id: `family_y_trial__r2__a2__fa3afe92__rf20261023T023844Z-ba22__s7`
- sentence: Before class, I mark parts to discuss with my middle school Japanese class.
- before: A Japanese teacher, a school budget worker, and a student who works and goes to school all face the same bag. / But different alarms go off in each person’s mind.
- after: I look at the lesson plan spread across the teacher’s desk. / I think about where to add a check.
- detected_by: luna-A4(0.3)
- reason [その他]: 「中学校の日本語クラス」で授業前に話し合う箇所に印を付けるという記述は、台帳Factで確認できない事実主張ではありませんか。

### s18  (confidence max 0.3)
- issue_id: `family_y_trial__r2__a2__fa3afe92__rf20261023T023844Z-ba22__s18`
- sentence: I check school budgets for the local government.
- before: It is my job to keep the lesson moving. / I cannot think a quiet classroom is enough.
- after: I lay out device costs and papers about learning help on my desk. / I mark them with sticky notes.
- detected_by: luna-A4(0.3)
- reason [その他]: 「地方自治体の予算を確認する」という職務の記述は、台帳Factで確認できない事実主張ではありませんか。

### s19  (confidence max 0.2)
- issue_id: `family_y_trial__r2__a2__fa3afe92__rf20261023T023844Z-ba22__s19`
- sentence: I lay out device costs and papers about learning help on my desk.
- before: I cannot think a quiet classroom is enough. / I check school budgets for the local government.
- after: I mark them with sticky notes. / Should money for putting phones away count as spending to help students do better at school?
- detected_by: luna-A4(0.2)
- reason [その他]: 机に「端末の費用」と「学習支援に関する資料」を広げているという記述は、台帳Factで確認できない事実主張ではありませんか。

### s27  (confidence max 0.3)
- issue_id: `family_y_trial__r2__a2__fa3afe92__rf20261023T023844Z-ba22__s27`
- sentence: I decide how the money is shared.
- before: I worry that money for the bags could mean less help for students who need help with learning. / At the same time, I still do not know if this cost is needed.
- after: So I cannot avoid explaining why. / After work, I take out my notebook at the evening high school I attend.
- detected_by: luna-A4(0.3)
- reason [その他]: 語り手が「お金の配分を決める」という権限を持つとの記述は、台帳Factで確認できない事実主張ではありませんか。

### s29  (confidence max 0.3)
- issue_id: `family_y_trial__r2__a2__fa3afe92__rf20261023T023844Z-ba22__s29`
- sentence: After work, I take out my notebook at the evening high school I attend.
- before: I decide how the money is shared. / So I cannot avoid explaining why.
- after: I check if my phone still has any work messages. / I want to avoid using it during class.
- detected_by: luna-A4(0.3)
- reason [その他]: 語り手が「仕事の後に通う夜間高校」でノートを取り出すという記述は、台帳Factで確認できない事実主張ではありませんか。

### s30  (confidence max 0.2)
- issue_id: `family_y_trial__r2__a2__fa3afe92__rf20261023T023844Z-ba22__s30`
- sentence: I check if my phone still has any work messages.
- before: So I cannot avoid explaining why. / After work, I take out my notebook at the evening high school I attend.
- after: I want to avoid using it during class. / But can I say with confidence, “No matter what happens, I can stay away from work messages”?
- detected_by: luna-A4(0.2)
- reason [その他]: 語り手の携帯電話に「仕事のメッセージ」が残っているか確認するという記述は、台帳Factで確認できない事実主張ではありませんか。
