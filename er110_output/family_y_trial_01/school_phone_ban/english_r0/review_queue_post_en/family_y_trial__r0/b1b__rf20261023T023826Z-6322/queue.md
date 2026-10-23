# Post-EN Risk Flagger Review Queue: family_y_trial__r0 / b1b

- run_id: `rf20261023T023826Z-6322`  status: **OK**
- article_sha256: `3c36b4d3fc80efa385f98496df64989122e077ba82e4bee935fa10bc0f4a4ee6`  ledger_sha256: `115a6528d97f9dab19f9b5022e2ce13ca83b4f50316f248dfaa9d3e45a67da89`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `None`  run_label: `FAMILY-Y-TRIAL-r0`
- sentences: 37  facts: 15  candidate issues: 2

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.129792 model=gpt-6-luna
- luna A4: OK flags=2 cost_jpy=0.206752 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.177539 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.183299 model=gemini-3.5-flash-lite

## Issues

### s27  (confidence max 0.28)
- issue_id: `family_y_trial__r0__b1b__3c36b4d3__rf20261023T023826Z-6322__s27`
- sentence: Everyone wants to value the time they spend learning.
- before: Before it is decided that devices will be locked away, I want room to think about it too. / I don’t want to put in the bag my responsibility to manage how I use the device myself.
- after: I think we agree on that. / But when a decision is wrong, what people lose and how much they have to take on themselves are different.
- detected_by: luna-A4(0.28)
- reason [その他]: 「Everyone wants to value the time they spend learning」という全員への一般化は、台帳で確認できない主張ではありませんか。

### s36  (confidence max 0.28)
- issue_id: `family_y_trial__r0__b1b__3c36b4d3__rf20261023T023826Z-6322__s36`
- sentence: Teachers, budget reviewers, and working students all value learning time, but they have different concerns about smartphone rules.
- before: Whose understanding is still waiting to be put into words? / ## In one line
- after: People who bear a decision’s weight may have little say in it, so their concerns still need to be heard.
- detected_by: luna-A4(0.28)
- reason [その他]: 「all value learning time」という全員への一般化は、台帳で確認できない主張ではありませんか。
