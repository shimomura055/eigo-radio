| 世代 | 従来(本文ごと再生成) | 旧attempt1 MAJOR(要約) | 許容型を含む | 新・腕R: 要約のみ再生成 | 解消(COMPLIANT+前回指摘解消) | 前回指摘の解消 | 腕R後の新規MAJOR(位置/origin/型) | 腕F(初回JA+台帳入力)のMAJOR(要約/本文) | M1+M2 最終check |
|---|---|---|---|---|---|---|---|---|---|
| G01 | 解消 | changed_scope | - | 1回: Meta rolled back Muse’s human-concierge test after admitting it began without properly disclosing that contractors handled some calls. | ○ | ○ | - | なし | COMPLIANT |
| G02 | STOP | changed_scope; changed_causality | users(+prompting因果) | 1回: Meta tested human contractors handling some Muse calls without proper disclosure, then paused its human concierge feature. | ○ | ○ | - | なし | MAJOR ?/translation/changed_actor |
| G03 | STOP | changed_causality | - | 1回: Meta rolled back Muse’s human concierge feature after admitting it was a mistake to let contractors make calls without proper disclosure. | × | ○ | body/ja_source/changed_scope | なし | MAJOR body/ja_source/changed_scope |
| G04 | 解消 | changed_fact+changed_scope | - | 1回: Meta temporarily rolled back Muse’s human-concierge feature after contractors made some calls without proper disclosure. | ○ | ○ | - | body/ja_source/changed_scope | MAJOR body/ja_source/changed_scope |
| G05 | 解消 | changed_fact+unsupported_new_claim | - | 1回: The United States has, for the first time, officially acknowledged deploying weapons in orbit, though their exact nature remains unknown. | ○ | ○ | - | なし | COMPLIANT |
| G06 | STOP | changed_scope | oil prices | 1回: Brent futures soon recovered even after Trump replaced his proposed 20% payment on all cargo passing through Hormuz with Gulf investment deals. | ○ | ○ | - | なし | COMPLIANT |
| G07 | STOP | changed_fact+unsupported_new_claim | users | 1回: Meta tested some Muse calls with human contractors without proper disclosure, then rolled back the human concierge feature. | ○ | ○ | - | なし | COMPLIANT |
| G08 | STOP | changed_certainty+unsupported_new_claim | - | 1回: Meta rolled back its human concierge feature after a vice president called testing without proper disclosure a mistake. | × | ○ | body/translation/changed_fact+unsupported_new_claim | なし | COMPLIANT |
| G09 | STOP | changed_scope+unsupported_new_claim | users | 1回: Meta rolled back a Muse feature that let contractors handle some calls after admitting it was tested without proper disclosure. | ○ | ○ | - | なし | COMPLIANT |
| G10 | 解消 | changed_scope | - | 1回: Trump withdrew a proposed 20% reimbursement tied to all cargo passing through Hormuz, but oil prices soon rebounded. | ○ | ○ | - | なし | COMPLIANT |
| G11 | 解消 | changed_scope | - | 1回: Meta rolled back Muse’s feature that let contract workers make calls after admitting users weren’t properly informed. | ○ | ○ | - | ?/ja_source/changed_scope | MAJOR ?/ja_source/changed_certainty |
| G12 | STOP | changed_fact+changed_scope+changed_certainty+unsupported_new_claim | users | 1回: Meta temporarily rolled back Muse’s human-concierge feature after admitting it tested some contractor-handled calls without proper disclosure. | ○ | ○ | - | なし | COMPLIANT |
| G13 | 解消 | changed_fact+changed_scope | - | 1回: The U.S. acknowledged deploying weapons in orbit to protect the joint force, but their specific systems, attack capabilities, and targets remain unknown. | ○ | ○ | - | なし | COMPLIANT |
| G14 | STOP | changed_scope | - | 1回: Meta temporarily rolled back Muse’s human-handoff test after admitting it had not explained when contractors might handle calls. | ○ | ○ | - | summary/translation/changed_scope | COMPLIANT |
| EV28 | - | (指摘なし=EV-28見逃し) | - | (対象外) | - | - | - | body/translation/changed_fact+changed_certainty | - |

要約MAJOR 14世代: 厳密解消(COMPLIANT かつ 前回指摘が全て解消) = 12/14、前回指摘(要約のMAJOR)の解消 = 14/14 (従来方式は 6/14)
STOP相当(未解消MAJOR)だった8世代のうち、なお未解消: 2件 ['G03', 'G08'] (従来は 8件)
従来で解消していた6世代のうち、新方式でも解消: 6/6
V1 実費 ¥13.261 (要約生成+check の実測トークン x 登録単価)
要約生成1call平均 ¥0.1179 (n=29) (JA+台帳入力あり)