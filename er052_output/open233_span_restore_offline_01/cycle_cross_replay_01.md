# cycle横断replay結果(委任_66、¥0)

既存ログのcycle N-1の確定claimを、cycle N(N-1のRewrite後)の本文へ当てた(B3型の古い引用の再現)。

## 集計

```
{
 "files": 475,
 "runs_by_category": {
  "next_unresolved(L6も復元せず=従来どおりunresolvable)": 107,
  "L6_restored:restored_overlaps_rewritten_sentence(OK)": 69,
  "next_resolved_by_L0-P(L6非関与)": 4,
  "prev_unresolved(対象外)": 5,
  "L6_restored_and_issue_focus_absent_fires": 25
 },
 "L6_restored_unique": 46,
 "L6_restored_by_verdict_unique": {
  "restored_overlaps_rewritten_sentence(OK)": 46
 },
 "wrong_restore_unique": 0,
 "issue_focus_absent_fires_unique": 15,
 "issue_focus_present_unique(通常Rewrite)": 3,
 "issue_has_no_quoted_phrase_unique(通常Rewrite)": 28
}
```

## L6が復元した全件(unique)

### X01 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter4/instances/meta_run03_standard.json:meta_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `“Some calls needed user information to continue.”`
- issue: The Ledger describes a conditional concern: user information could be needed to carry out a call. The article turns that condition into an assertion that some calls actually needed it.
- 復元文(1文, ['anchor_with_substituted_words']): `Also, if a call needed user information to continue, that information might accidentally be shared with contract workers at a call center.`
- 正解(N-1のRewrite後の文): `A Meta executive acknowledged that starting a test in which contract staff made calls without proper disclosure was a “mistake.”

Also, if a call needed user information to continue, that information might accidentally be shared with contract workers at a call center.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X02 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現2回: er052_output/open233_self_recovery_flow_runner_01_iter4/instances/safety_A4.json:safety_A4:c1, er052_output/open233_self_recovery_flow_runner_01_rep23/instances_s1/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `“Through Muse, trained human contract workers made some calls and completed the exchanges with users.”`
- issue: この記事では、契約スタッフがやり取りを完了した相手をMuseのユーザーとしていますが、Ledgerが示すのは電話の相手先（企業・店舗など）です。
- 復元文(1文, ['anchor_with_substituted_words']): `Through Muse, trained human contract workers made some calls and completed the exchanges with the other party.`
- 正解(N-1のRewrite後の文): `Through Muse, trained human contract workers made some calls and completed the exchanges with the other party.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X03 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現3回: er052_output/open233_self_recovery_flow_runner_01_iter4/instances/safety_A5.json:safety_A5:c1, er052_output/open233_self_recovery_flow_runner_01_iter6/instances_s1/safety_A5.json:safety_A5:c1, er052_output/open233_self_recovery_flow_runner_01_rep9/instances_s1/safety_A5.json:safety_A5:c1)
- claim(N-1で確定したCheckerの引用): `They also temporarily put back the feature in which humans handled the calls. They did not stop Muse itself.`
- issue: The article says the human-call feature was put back, reversing the reported action: Meta temporarily rolled back that feature. The clarification that Muse itself was not stopped does not correct this reversal.
- 復元文(2文, ['anchor_with_substituted_words']): `They also temporarily rolled back the feature in which humans handled the calls. They did not stop Muse itself.`
- 正解(N-1のRewrite後の文): `They also temporarily rolled back the feature in which humans handled the calls.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X04 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現3回: er052_output/open233_self_recovery_flow_runner_01_iter4/instances/safety_er009_changed_time.json:safety_er009_changed_time:c1, er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s1/safety_er009_changed_time.json:safety_er009_changed_time:c1, er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s2/safety_er009_changed_time.json:safety_er009_changed_time:c1)
- claim(N-1で確定したCheckerの引用): `In 2019, researchers published a study in the American Economic Journal: Applied Economics showing that higher suggested tip rates led New York City taxi passengers to leave more money.`
- issue: 研究の発表年がLedgerの2014年と異なっています。
- 復元文(1文, ['anchor_with_substituted_words']): `In 2014, researchers published a study in the American Economic Journal: Applied Economics showing that higher suggested tip rates led New York City taxi passengers to leave more money.`
- 正解(N-1のRewrite後の文): `In 2014, researchers published a study in the American Economic Journal: Applied Economics showing that higher suggested tip rates led New York City taxi passengers to leave more money.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X05 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s1/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `“Through Muse, trained human contract workers made some calls and completed the exchanges with users.”`
- issue: この記事では、契約スタッフがやり取りを完了した相手をMuseのユーザーとしていますが、Ledgerが示すのは電話の相手先（企業・店舗など）です。
- 復元文(1文, ['anchor_with_substituted_words']): `Through Muse, trained human contract workers made some calls to businesses and completed the exchanges.`
- 正解(N-1のRewrite後の文): `Through Muse, trained human contract workers made some calls to businesses and completed the exchanges.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X06 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現2回: er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s2/safety_A4.json:safety_A4:c1, er052_output/open233_self_recovery_flow_runner_01_rep23/instances_s2/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `“Through Muse, trained human contract workers made some calls and completed the exchanges with users.”`
- issue: この記事では、契約スタッフがやり取りを完了した相手をMuseのユーザーとしていますが、Ledgerが示すのは電話の相手先（企業・店舗など）です。
- 復元文(1文, ['anchor_with_substituted_words']): `Through Muse, trained human contract workers made some calls and completed the exchanges.`
- 正解(N-1のRewrite後の文): `Through Muse, trained human contract workers made some calls and completed the exchanges.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X07 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現4回: er052_output/open233_self_recovery_flow_runner_01_iter6/instances_s1/meta_run03_standard.json:meta_run03_standard:c1, er052_output/open233_self_recovery_flow_runner_01_rep11/instances_s1/meta_run03_standard.json:meta_run03_standard:c1, er052_output/open233_self_recovery_flow_runner_01_rep11/instances_s2/meta_run03_standard.json:meta_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `“Some calls needed user information to continue.”`
- issue: The Ledger describes a conditional concern: user information could be needed to carry out a call. The article turns that condition into an assertion that some calls actually needed it.
- 復元文(1文, ['anchor_with_substituted_words']): `Also, some calls might need user information to continue.`
- 正解(N-1のRewrite後の文): `Also, some calls might need user information to continue.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X08 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter6/instances_s1/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `“Through Muse, trained human contract workers made some calls and completed the exchanges with users.”`
- issue: この記事では、契約スタッフがやり取りを完了した相手をMuseのユーザーとしていますが、Ledgerが示すのは電話の相手先（企業・店舗など）です。
- 復元文(1文, ['anchor_with_substituted_words']): `Through Muse, trained human contract workers made some calls and completed the exchanges with the people they called.`
- 正解(N-1のRewrite後の文): `Through Muse, trained human contract workers made some calls and completed the exchanges with the people they called.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X09 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter6/instances_s2/meta_run03_standard.json:meta_run03_standard:c2)
- claim(N-1で確定したCheckerの引用): `“It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.”`
- issue: The article’s plural “comments” and “calls” suggest multiple remarks or call instances. The Ledger records one reported case, so this wording extends the scope and implies a count not established by the Ledger.
- 復元文(2文, ['anchor_with_substituted_words']): `It said human staff made a comment about race during one call. These calls were about trying to lower internet or cable fees.`
- 正解(N-1のRewrite後の文): `It said human staff made a comment about race during one call.`
- issue引用語句: {"phrases": [{"phrase": "comments", "in_restored_range": false, "in_claim": true}, {"phrase": "calls", "in_restored_range": true, "in_claim": true}], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X10 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter6/instances_s2/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `“Through Muse, trained human contract workers made some calls and completed the exchanges with users.”`
- issue: この記事では、契約スタッフがやり取りを完了した相手をMuseのユーザーとしていますが、Ledgerが示すのは電話の相手先（企業・店舗など）です。
- 復元文(1文, ['anchor_with_substituted_words']): `Through Muse, trained human contract workers made some calls and completed the exchanges with recipients.`
- 正解(N-1のRewrite後の文): `Through Muse, trained human contract workers made some calls and completed the exchanges with recipients.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X11 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter6/instances_s2/safety_er009_changed_scope.json:safety_er009_changed_scope:c1)
- claim(N-1で確定したCheckerの引用): `The taxi study's results have now been directly confirmed in restaurants nationwide: higher suggested tip rates on restaurant screens cause customers to leave more money, just as they did in the New York City taxi data.`
- issue: タクシー研究の結果が全米のレストランでも直接確認され、レストラン画面の高い推奨率が客により多くチップを残させると因果的に断定している。Ledgerはレストランでのそのような因果確認を示していない。
- 復元文(1文, ['anchor_with_substituted_words']): `The taxi study's results have now been directly confirmed in restaurants nationwide: higher suggested tip rates on taxi screens cause customers to leave more money, just as they did in the New York City taxi data.`
- 正解(N-1のRewrite後の文): `The taxi study's results have now been directly confirmed in restaurants nationwide: higher suggested tip rates on taxi screens cause customers to leave more money, just as they did in the New York City taxi data.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X12 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter7/instances/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `“Through Muse, trained human contract workers made some calls and completed the exchanges with users.”`
- issue: この記事では、契約スタッフがやり取りを完了した相手をMuseのユーザーとしていますが、Ledgerが示すのは電話の相手先（企業・店舗など）です。
- 復元文(1文, ['anchor_with_substituted_words']): `Through Muse, trained human contract workers made some calls and completed the exchanges with called parties.`
- 正解(N-1のRewrite後の文): `Through Muse, trained human contract workers made some calls and completed the exchanges with called parties.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X13 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter7/instances_s1/neg1_meta_b3prod_a2.json:neg1_meta_b3prod_a2:c2)
- claim(N-1で確定したCheckerの引用): `The test began without clearly telling users that contract workers would make the calls.`
- issue: The article says users were not clearly told, whereas the Ledger describes an internal test involving Meta employees and does not establish that Muse users generally were the audience that lacked disclosure. The nearby suggestion that a user might think the exchange was with AI does not establish th
- 復元文(1文, ['anchor_with_substituted_words']): `The test began without clearly telling employees that contract workers would make the calls.`
- 正解(N-1のRewrite後の文): `The test began without clearly telling employees that contract workers would make the calls. A person was involved.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X14 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter7/instances_s1/neg1_meta_b3prod_a2.json:neg1_meta_b3prod_a2:c2)
- claim(N-1で確定したCheckerの引用): `A Meta executive admitted the mistake. The test had begun without clearly telling users.`
- issue: The article says users were not clearly told, whereas the Ledger describes an internal test involving Meta employees and does not establish that Muse users generally were the audience that lacked disclosure. The nearby suggestion that a user might think the exchange was with AI does not establish th
- 復元文(2文, ['anchor_with_substituted_words']): `A Meta executive admitted the mistake. The test had begun without clearly telling employees.`
- 正解(N-1のRewrite後の文): `The test had begun without clearly telling employees.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X15 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現3回: er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s1/meta_run03_standard.json:meta_run03_standard:c1, er052_output/open233_self_recovery_flow_runner_01_rep19/instances_s1/meta_run03_standard.json:meta_run03_standard:c1, er052_output/open233_self_recovery_flow_runner_01_rep21/instances_s1/meta_run03_standard.json:meta_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `“It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.”`
- issue: The plural “calls” presents the reported incident as involving multiple calls, while the Ledger describes one reported case.
- 復元文(2文, ['anchor_with_substituted_words']): `It said human staff made inappropriate comments about race during a call. These calls were about trying to lower internet or cable fees.`
- 正解(N-1のRewrite後の文): `News reports also cited one employee’s report of an inappropriate remark during a call. It said human staff made inappropriate comments about race during a call.`
- issue引用語句: {"phrases": [{"phrase": "calls", "in_restored_range": true, "in_claim": true}], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X16 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s1/meta_run03_standard.json:meta_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `However, this is only one report. It would be wrong to say all contract workers did this.`
- issue: The plural “calls” presents the reported incident as involving multiple calls, while the Ledger describes one reported case.
- 復元文(2文, ['anchor_with_substituted_words']): `However, this is only one report. It would be wrong to say many contract workers did this.`
- 正解(N-1のRewrite後の文): `It would be wrong to say many contract workers did this.`
- issue引用語句: {"phrases": [{"phrase": "calls", "in_restored_range": false, "in_claim": false}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X17 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s1/meta_run03_standard.json:meta_run03_standard:c2)
- claim(N-1で確定したCheckerの引用): `These calls were about trying to lower internet or cable fees.`
- issue: The plural “These calls” presents the reported fee-negotiation incident as involving multiple calls, while the Ledger records one reported case.
- 復元文(1文, ['anchor_with_substituted_words']): `This call was about trying to lower internet or cable fees.`
- 正解(N-1のRewrite後の文): `Also, Meta employees worried that, if a call needed user information, it might reach call center contract workers.

News reports also cited one employee’s report of an inappropriate remark during one call. It said human staff made inappropriate comments about race during one call. This call was abou`
- issue引用語句: {"phrases": [{"phrase": "These calls", "in_restored_range": false, "in_claim": true}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X18 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s1/meta_run03_standard.json:meta_run03_standard:c2)
- claim(N-1で確定したCheckerの引用): `News reports also cited one employee’s report of an inappropriate remark during a call.`
- issue: The plural “These calls” presents the reported fee-negotiation incident as involving multiple calls, while the Ledger records one reported case.
- 復元文(1文, ['anchor_with_substituted_words']): `News reports also cited one employee’s report of an inappropriate remark during one call.`
- 正解(N-1のRewrite後の文): `Also, Meta employees worried that, if a call needed user information, it might reach call center contract workers.

News reports also cited one employee’s report of an inappropriate remark during one call. It said human staff made inappropriate comments about race during one call. This call was abou`
- issue引用語句: {"phrases": [{"phrase": "These calls", "in_restored_range": false, "in_claim": false}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X19 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現2回: er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s1/meta_run03_standard.json:meta_run03_standard:c2, er052_output/open233_self_recovery_flow_runner_01_rep19/instances_s1/meta_run03_standard.json:meta_run03_standard:c2)
- claim(N-1で確定したCheckerの引用): `It said human staff made inappropriate comments about race during a call.`
- issue: The plural “These calls” presents the reported fee-negotiation incident as involving multiple calls, while the Ledger records one reported case.
- 復元文(1文, ['anchor_with_substituted_words']): `It said human staff made inappropriate comments about race during one call.`
- 正解(N-1のRewrite後の文): `Also, Meta employees worried that, if a call needed user information, it might reach call center contract workers.

News reports also cited one employee’s report of an inappropriate remark during one call. It said human staff made inappropriate comments about race during one call. This call was abou`
- issue引用語句: {"phrases": [{"phrase": "These calls", "in_restored_range": false, "in_claim": false}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X20 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s2/meta_run03_standard.json:meta_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `“It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.”`
- issue: The plural “calls” presents the reported incident as involving multiple calls, while the Ledger describes one reported case.
- 復元文(2文, ['anchor_with_substituted_words']): `It said human staff made inappropriate comments about race during one call. These calls were about trying to lower internet or cable fees.`
- 正解(N-1のRewrite後の文): `News report also cited one employee’s report. It said human staff made inappropriate comments about race during one call.`
- issue引用語句: {"phrases": [{"phrase": "calls", "in_restored_range": true, "in_claim": true}], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X21 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s2/meta_run03_standard.json:meta_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `News reports also cited one employee’s report.`
- issue: The plural “calls” presents the reported incident as involving multiple calls, while the Ledger describes one reported case.
- 復元文(1文, ['anchor_with_substituted_words']): `News report also cited one employee’s report.`
- 正解(N-1のRewrite後の文): `News report also cited one employee’s report. It said human staff made inappropriate comments about race during one call.`
- issue引用語句: {"phrases": [{"phrase": "calls", "in_restored_range": false, "in_claim": false}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X22 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現2回: er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s2/meta_run03_standard.json:meta_run03_standard:c1, er052_output/open233_self_recovery_flow_runner_01_rep19/instances_s1/meta_run03_standard.json:meta_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `However, this is only one report. It would be wrong to say all contract workers did this.`
- issue: The plural “calls” presents the reported incident as involving multiple calls, while the Ledger describes one reported case.
- 復元文(2文, ['anchor_with_substituted_words']): `However, this is only one case. It would be wrong to say all contract workers did this.`
- 正解(N-1のRewrite後の文): `However, this is only one case.`
- issue引用語句: {"phrases": [{"phrase": "calls", "in_restored_range": false, "in_claim": false}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X23 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現6回: er052_output/open233_self_recovery_flow_runner_01_rep11/instances_s1/bgroup_B3.json:bgroup_B3:c1, er052_output/open233_self_recovery_flow_runner_01_rep11/instances_s2/bgroup_B3.json:bgroup_B3:c1, er052_output/open233_self_recovery_flow_runner_01_rep12/instances_s1/bgroup_B3.json:bgroup_B3:c1)
- claim(N-1で確定したCheckerの引用): `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering.`
- issue: 継続していた攻撃・封鎖・タンカー安全への懸念が、20％案の撤回・置換や価格回復の原因だったかのように読める。Ledgerは、撤回・置換の理由としてトランプ氏が「非常に生産的な協議」を挙げたことと、供給懸念が継続していたことを確認しているが、両者の因果関係は確認していない。
- 復元文(1文, ['anchor_with_substituted_words']): `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.`
- 正解(N-1のRewrite後の文): `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.`
- issue引用語句: {"phrases": [{"phrase": "非常に生産的な協議", "in_restored_range": false, "in_claim": false}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X24 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep14/instances_s1/hormuz_run03_standard.json:hormuz_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `Oil prices did not fall across the whole market after the plan was withdrawn.`
- issue: Brent先物についての観測を、石油市場全体の値動きに広げている。
- 復元文(1文, ['anchor_with_substituted_words']): `Brent futures did not fall across the whole market after the plan was withdrawn.`
- 正解(N-1のRewrite後の文): `Brent futures did not fall across the whole market after the plan was withdrawn.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X25 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep14/instances_s2/hormuz_run03_standard.json:hormuz_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `Oil prices did not fall across the whole market after the plan was withdrawn.`
- issue: Brent先物についての観測を、石油市場全体の値動きに広げている。
- 復元文(1文, ['anchor_with_substituted_words']): `Brent futures prices did not fall across the whole market after the plan was withdrawn.`
- 正解(N-1のRewrite後の文): `Brent futures prices did not fall across the whole market after the plan was withdrawn.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X26 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep17/instances_s2/neg3_hormuz_prodrunner_b1b.json:neg3_hormuz_prodrunner_b1b:c1)
- claim(N-1で確定したCheckerの引用): `The fee plan left the stage, but the events driving oil prices—and the prices themselves—quickly returned.`
- issue: The article says the events affecting prices returned, whereas the Ledger says the relevant attacks, blockade, and tanker-safety concerns continued. This changes the events’ timeline.
- 復元文(1文, ['anchor_with_substituted_words']): `The fee plan left the stage, but the events driving oil prices continued.`
- 正解(N-1のRewrite後の文): `The fee plan left the stage, but the events driving oil prices continued. The prices themselves quickly returned.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X27 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep17/instances_s2/neg3_hormuz_prodrunner_b1b.json:neg3_hormuz_prodrunner_b1b:c1)
- claim(N-1で確定したCheckerの引用): `During that period, attacks between the United States and Iran, a sea blockade, and concerns about tanker safety continued.`
- issue: The article says the events affecting prices returned, whereas the Ledger says the relevant attacks, blockade, and tanker-safety concerns continued. This changes the events’ timeline.
- 復元文(1文, ['anchor_with_substituted_words']): `Meanwhile, attacks between the United States and Iran, a sea blockade, and concerns about tanker safety continued.`
- 正解(N-1のRewrite後の文): `Meanwhile, attacks between the United States and Iran, a sea blockade, and concerns about tanker safety continued.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X28 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep17/instances_s2/neg3_hormuz_prodrunner_b1b.json:neg3_hormuz_prodrunner_b1b:c1)
- claim(N-1で確定したCheckerの引用): `The fee plan may be replaced, but events continuing at the same time do not simply disappear backstage because of one announcement.`
- issue: The article says the events affecting prices returned, whereas the Ledger says the relevant attacks, blockade, and tanker-safety concerns continued. This changes the events’ timeline.
- 復元文(1文, ['anchor_with_substituted_words']): `The fee plan may be replaced, but events continuing at the same time do not simply stop backstage because of one announcement.`
- 正解(N-1のRewrite後の文): `The fee plan may be replaced, but events continuing at the same time do not simply stop backstage because of one announcement.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X29 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep19/instances_s1/meta_run03_standard.json:meta_run03_standard:c2)
- claim(N-1で確定したCheckerの引用): `“some calls needed user information to continue.”`
- issue: The Ledger describes a concern that information could be needed for a call and might be shared; it does not establish that some calls actually required user information. The English wording turns a conditional into an asserted occurrence.
- 復元文(1文, ['anchor_with_substituted_words']): `Also, a call might need user information to continue.`
- 正解(N-1のRewrite後の文): `Also, a call might need user information to continue.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X30 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep19/instances_s1/meta_run03_standard.json:meta_run03_standard:c2)
- claim(N-1で確定したCheckerの引用): `“These calls were about trying to lower internet or cable fees.”`
- issue: “These calls” presents the reported incident as involving multiple calls, whereas the Ledger records one reported case. The nearby wording limits the account to one report/case, but the plural claim remains.
- 復元文(1文, ['anchor_with_substituted_words']): `This call was about trying to lower internet or cable fees.`
- 正解(N-1のRewrite後の文): `News reports also cited one employee’s report about a single phone call. It said human staff made inappropriate comments about race during one call. This call was about trying to lower internet or cable fees.`
- issue引用語句: {"phrases": [{"phrase": "These calls", "in_restored_range": false, "in_claim": true}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X31 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep19/instances_s1/meta_run03_standard.json:meta_run03_standard:c2)
- claim(N-1で確定したCheckerの引用): `News reports also cited one employee’s report about a phone call.`
- issue: “These calls” presents the reported incident as involving multiple calls, whereas the Ledger records one reported case. The nearby wording limits the account to one report/case, but the plural claim remains.
- 復元文(1文, ['anchor_with_substituted_words']): `News reports also cited one employee’s report about a single phone call.`
- 正解(N-1のRewrite後の文): `News reports also cited one employee’s report about a single phone call. It said human staff made inappropriate comments about race during one call. This call was about trying to lower internet or cable fees.`
- issue引用語句: {"phrases": [{"phrase": "These calls", "in_restored_range": false, "in_claim": false}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X32 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep19/instances_s1/meta_run03_standard.json:meta_run03_standard:c2)
- claim(N-1で確定したCheckerの引用): `However, this is only one case. It would be wrong to say all contract workers did this.`
- issue: “These calls” presents the reported incident as involving multiple calls, whereas the Ledger records one reported case. The nearby wording limits the account to one report/case, but the plural claim remains.
- 復元文(2文, ['anchor_with_substituted_words']): `However, this is only one case. It would be wrong to say other contract workers did this.`
- 正解(N-1のRewrite後の文): `It would be wrong to say other contract workers did this.`
- issue引用語句: {"phrases": [{"phrase": "These calls", "in_restored_range": false, "in_claim": false}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X33 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現2回: er052_output/open233_self_recovery_flow_runner_01_rep20/instances_s1/meta_run03_standard.json:meta_run03_standard:c1, er052_output/open233_self_recovery_flow_runner_01_rep22/instances_s2/meta_run03_standard.json:meta_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `“It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.”`
- issue: The plural “calls” presents the reported incident as involving multiple calls, while the Ledger describes one reported case.
- 復元文(2文, ['anchor_with_substituted_words']): `It said human staff made inappropriate comments about race during one call. The call was about trying to lower internet or cable fees.`
- 正解(N-1のRewrite後の文): `It said human staff made inappropriate comments about race during one call. The call was about trying to lower internet or cable fees.`
- issue引用語句: {"phrases": [{"phrase": "calls", "in_restored_range": false, "in_claim": true}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X34 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現3回: er052_output/open233_self_recovery_flow_runner_01_rep20/instances_s2/meta_run03_standard.json:meta_run03_standard:c1, er052_output/open233_self_recovery_flow_runner_01_rep22/instances_s3/meta_run03_standard.json:meta_run03_standard:c1, er052_output/open233_self_recovery_flow_runner_01_rep22/instances_s4/meta_run03_standard.json:meta_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `“It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.”`
- issue: The plural “calls” presents the reported incident as involving multiple calls, while the Ledger describes one reported case.
- 復元文(2文, ['anchor_with_substituted_words']): `It said human staff made inappropriate comments about race during a call. This call was about trying to lower internet or cable fees.`
- 正解(N-1のRewrite後の文): `It said human staff made inappropriate comments about race during a call. This call was about trying to lower internet or cable fees.`
- issue引用語句: {"phrases": [{"phrase": "calls", "in_restored_range": false, "in_claim": true}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X35 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep21/instances_s1/meta_run03_standard.json:meta_run03_standard:c2)
- claim(N-1で確定したCheckerの引用): `“These calls were about trying to lower internet or cable fees.”`
- issue: The Ledger describes one reported case, but “These calls” presents the incident as involving multiple calls. The nearby statement that this was only one report does not resolve the plural wording.
- 復元文(1文, ['anchor_with_substituted_words']): `The reported call was about trying to lower internet or cable fees.`
- 正解(N-1のRewrite後の文): `The reported call was about trying to lower internet or cable fees.`
- issue引用語句: {"phrases": [{"phrase": "These calls", "in_restored_range": false, "in_claim": true}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X36 restored_overlaps_rewritten_sentence(OK) [oracle=rewrite_pair] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep22/instances_s1/meta_run03_standard.json:meta_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `“It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.”`
- issue: The plural “calls” presents the reported incident as involving multiple calls, while the Ledger describes one reported case.
- 復元文(2文, ['anchor_with_substituted_words']): `It said human staff made inappropriate comments about race during one call. This call was about trying to lower internet or cable fees.`
- 正解(N-1のRewrite後の文): `It said human staff made inappropriate comments about race during one call. This call was about trying to lower internet or cable fees.`
- issue引用語句: {"phrases": [{"phrase": "calls", "in_restored_range": false, "in_claim": true}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X37 restored_overlaps_rewritten_sentence(OK) [oracle=rewrite_pair] (出現2回: er052_output/open233_self_recovery_flow_runner_01_rep23/instances_s1/safety_A4.json:safety_A4:c1, er052_output/open233_self_recovery_flow_runner_01_rep23/instances_s2/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `“One helper meant one more person handling private data.”`
- issue: 情報が契約スタッフに共有される可能性についての懸念を、スタッフが実際に個人情報を扱うことが必ず起きるかのように述べています。
- 復元文(1文, ['anchor_with_substituted_words']): `One helper meant one more person potentially handling private data.`
- 正解(N-1のRewrite後の文): `One helper meant one more person potentially handling private data.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X38 restored_overlaps_rewritten_sentence(OK) [oracle=rewrite_pair] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep23/instances_s1/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `Through Muse, trained human contract workers made some calls and completed the exchanges with users.`
- issue: この記事では、契約スタッフがやり取りを完了した相手をMuseのユーザーとしていますが、Ledgerが示すのは電話の相手先（企業・店舗など）です。
- 復元文(1文, ['anchor_with_substituted_words']): `Through Muse, trained human contract workers made some calls and completed the exchanges with the other party.`
- 正解(N-1のRewrite後の文): `Through Muse, trained human contract workers made some calls and completed the exchanges with the other party.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X39 restored_overlaps_rewritten_sentence(OK) [oracle=rewrite_pair] (出現2回: er052_output/open233_self_recovery_flow_runner_01_rep23/instances_s1/safety_A4.json:safety_A4:c1, er052_output/open233_self_recovery_flow_runner_01_rep23/instances_s2/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `One helper meant one more person handling private data.`
- issue: 情報が契約スタッフに共有される可能性についての懸念を、スタッフが実際に個人情報を扱うことが必ず起きるかのように述べています。
- 復元文(1文, ['anchor_with_substituted_words']): `One helper meant one more person potentially handling private data.`
- 正解(N-1のRewrite後の文): `One helper meant one more person potentially handling private data.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X40 restored_overlaps_rewritten_sentence(OK) [oracle=rewrite_pair] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep23/instances_s2/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `Through Muse, trained human contract workers made some calls and completed the exchanges with users.`
- issue: この記事では、契約スタッフがやり取りを完了した相手をMuseのユーザーとしていますが、Ledgerが示すのは電話の相手先（企業・店舗など）です。
- 復元文(1文, ['anchor_with_substituted_words']): `Through Muse, trained human contract workers made some calls and completed the exchanges.`
- 正解(N-1のRewrite後の文): `Through Muse, trained human contract workers made some calls and completed the exchanges.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X41 restored_overlaps_rewritten_sentence(OK) [oracle=rewrite_pair] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep24/instances_s1/bgroup_B3.json:bgroup_B3:c1)
- claim(N-1で確定したCheckerの引用): `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering.`
- issue: 継続していた攻撃・封鎖・タンカー安全への懸念が、20％案の撤回・置換や価格回復の原因だったかのように読める。Ledgerは、撤回・置換の理由としてトランプ氏が「非常に生産的な協議」を挙げたことと、供給懸念が継続していたことを確認しているが、両者の因果関係は確認していない。
- 復元文(1文, ['anchor_with_substituted_words']): `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, and the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.`
- 正解(N-1のRewrite後の文): `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, and the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering`
- issue引用語句: {"phrases": [{"phrase": "非常に生産的な協議", "in_restored_range": false, "in_claim": false}], "absent": true} -> issue_focus_absent=発火(Rewrite見送り+Recheckのみ)

### X42 restored_overlaps_rewritten_sentence(OK) [oracle=rewrite_pair] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep24/instances_s1/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `“Through Muse, trained human contract workers made some calls and completed the exchanges with users.”`
- issue: この記事では、契約スタッフがやり取りを完了した相手をMuseのユーザーとしていますが、Ledgerが示すのは電話の相手先（企業・店舗など）です。
- 復元文(1文, ['anchor_with_substituted_words']): `Through Muse, trained human contract workers made some calls and completed the exchanges with businesses.`
- 正解(N-1のRewrite後の文): `Through Muse, trained human contract workers made some calls and completed the exchanges with businesses.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X43 restored_overlaps_rewritten_sentence(OK) [oracle=rewrite_pair] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep24/instances_s1/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `“One helper meant one more person handling private data.”`
- issue: 情報が契約スタッフに共有される可能性についての懸念を、スタッフが実際に個人情報を扱うことが必ず起きるかのように述べています。
- 復元文(1文, ['anchor_with_substituted_words']): `One helper might mean one more person handling private data.`
- 正解(N-1のRewrite後の文): `One helper might mean one more person handling private data.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X44 restored_overlaps_rewritten_sentence(OK) [oracle=rewrite_pair] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep24/instances_s1/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `Through Muse, trained human contract workers made some calls and completed the exchanges with users.`
- issue: この記事では、契約スタッフがやり取りを完了した相手をMuseのユーザーとしていますが、Ledgerが示すのは電話の相手先（企業・店舗など）です。
- 復元文(1文, ['anchor_with_substituted_words']): `Through Muse, trained human contract workers made some calls and completed the exchanges with businesses.`
- 正解(N-1のRewrite後の文): `Through Muse, trained human contract workers made some calls and completed the exchanges with businesses.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X45 restored_overlaps_rewritten_sentence(OK) [oracle=rewrite_pair] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep24/instances_s1/safety_A4.json:safety_A4:c1)
- claim(N-1で確定したCheckerの引用): `One helper meant one more person handling private data.`
- issue: 情報が契約スタッフに共有される可能性についての懸念を、スタッフが実際に個人情報を扱うことが必ず起きるかのように述べています。
- 復元文(1文, ['anchor_with_substituted_words']): `One helper might mean one more person handling private data.`
- 正解(N-1のRewrite後の文): `One helper might mean one more person handling private data.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

### X46 restored_overlaps_rewritten_sentence(OK) [oracle=sentence_diff] (出現1回: er052_output/open233_self_recovery_flow_runner_01_rep9/instances_s1/meta_run03_standard.json:meta_run03_standard:c1)
- claim(N-1で確定したCheckerの引用): `“Some calls needed user information to continue.”`
- issue: The Ledger describes a conditional concern: user information could be needed to carry out a call. The article turns that condition into an assertion that some calls actually needed it.
- 復元文(1文, ['anchor_with_substituted_words']): `Also, some calls could need user information to continue.`
- 正解(N-1のRewrite後の文): `Also, some calls could need user information to continue.`
- issue引用語句: {"phrases": [], "absent": false} -> issue_focus_absent=非発火(通常Rewrite)

