# results summary (委任_02)

obs=126 gen_tts_jpy=3.8986 total_jpy=17.2743

## (i) 動詞 x 名前 (全level/target pooled)
| 名前 | 動詞 | 群 | n | OR PASS | OpenAI PASS | Azure PASS | spell OA | spell Az | spell WH |
|---|---|---|---|---|---|---|---|---|---|
| Melos | said | s | 12 | 4/12 | 0/12 | 4/12 | 0/12 | 3/12 | 0/12 |
| Melos | says | s | 12 | 4/12 | 0/12 | 4/12 | 0/12 | 3/12 | 0/12 |
| Melos | sighed | s | 12 | 2/12 | 1/12 | 1/12 | 1/12 | 4/12 | 1/12 |
| Melos | replied | ns | 12 | 12/12 | 2/12 | 12/12 | 2/12 | 12/12 | 10/12 |
| Melos | answered | ns | 12 | 12/12 | 3/12 | 12/12 | 3/12 | 12/12 | 11/12 |
| Melos | asked | ns | 12 | 11/12 | 2/12 | 11/12 | 2/12 | 11/12 | 6/12 |
| Brontes | said | s | 9 | 9/9 | 7/9 | 9/9 | 0/9 | 9/9 | 3/9 |
| Brontes | says | s | 9 | 9/9 | 8/9 | 9/9 | 0/9 | 9/9 | 0/9 |
| Brontes | sighed | s | 9 | 9/9 | 9/9 | 6/9 | 0/9 | 8/9 | 9/9 |
| Brontes | replied | ns | 9 | 9/9 | 9/9 | 9/9 | 9/9 | 9/9 | 6/9 |
| Brontes | answered | ns | 9 | 9/9 | 8/9 | 9/9 | 6/9 | 9/9 | 8/9 |
| Brontes | asked | ns | 9 | 8/9 | 4/9 | 8/9 | 5/9 | 8/9 | 5/9 |

## (ii) 要因分離 (s群{said,says,sighed} vs 非s群{replied,answered,asked}; Fisher two-sided、観測単位=過小評価)
- Melos or_pass: 非s群 35/36 vs s群 10/36 p=0.0000
- Melos openai_verified: 非s群 7/36 vs s群 1/36 p=0.0553
- Melos spell_openai: 非s群 7/36 vs s群 1/36 p=0.0553
- Melos spell_azure: 非s群 35/36 vs s群 10/36 p=0.0000
- Brontes or_pass: 非s群 26/27 vs s群 27/27 p=1.0000
- Brontes openai_verified: 非s群 21/27 vs s群 24/27 p=0.4672
- Brontes spell_openai: 非s群 20/27 vs s群 0/27 p=0.0000
- Brontes spell_azure: 非s群 26/27 vs s群 26/27 p=1.0000
- pooled or_pass: 非s群 61/63 vs s群 37/63 p=0.0000
- pooled openai_verified: 非s群 28/63 vs s群 25/63 p=0.7183
- pooled spell_openai: 非s群 27/63 vs s群 1/63 p=0.0000
- pooled spell_azure: 非s群 61/63 vs s群 36/63 p=0.0000

動詞別 vs 非s群(Melos):
- Melos or_pass: 非s群 35/36 vs said 4/12 p=0.0000
- Melos or_pass: 非s群 35/36 vs says 4/12 p=0.0000
- Melos or_pass: 非s群 35/36 vs sighed 2/12 p=0.0000
- Melos or_pass: said以外のs始まり(says+sighed) 6/24 vs said 4/12 p=0.7004
- Melos openai_verified: 非s群 7/36 vs said 0/12 p=0.1686
- Melos openai_verified: 非s群 7/36 vs says 0/12 p=0.1686
- Melos openai_verified: 非s群 7/36 vs sighed 1/12 p=0.6593
- Melos openai_verified: said以外のs始まり(says+sighed) 1/24 vs said 0/12 p=1.0000
- Melos spell_openai: 非s群 7/36 vs said 0/12 p=0.1686
- Melos spell_openai: 非s群 7/36 vs says 0/12 p=0.1686
- Melos spell_openai: 非s群 7/36 vs sighed 1/12 p=0.6593
- Melos spell_openai: said以外のs始まり(says+sighed) 1/24 vs said 0/12 p=1.0000

## (iii) 委任_01(L2)との再現一致 (Melos/Brontes, said=ss, replied=nss; OR PASS / OpenAI PASS / spell OA)
- Melos said: 委任_01 OR 2/9 / OA 0/9 / spell 0/9  |  委任_02 OR 4/12 / OA 0/12 / spell 0/12
- Melos replied: 委任_01 OR 7/9 / OA 2/9 / spell 2/9  |  委任_02 OR 12/12 / OA 2/12 / spell 2/12
- Brontes said: 委任_01 OR 9/9 / OA 9/9 / spell 2/9  |  委任_02 OR 9/9 / OA 7/9 / spell 0/9
- Brontes replied: 委任_01 OR 9/9 / OA 9/9 / spell 6/9  |  委任_02 OR 9/9 / OA 9/9 / spell 9/9

## (iv) level/target別 (Melos | Brontes; OR PASS / OpenAI PASS) 群別
| level/target | 群 | Melos n | Melos OR | Melos OA | Brontes n | Brontes OR | Brontes OA |
|---|---|---|---|---|---|---|---|
| std/raw | s | 12 | 4/12 | 0/12 | 9 | 9/9 | 9/9 |
| std/raw | ns | 12 | 12/12 | 5/12 | 9 | 9/9 | 7/9 |
| std/slow6 | s | 12 | 3/12 | 1/12 | 9 | 9/9 | 8/9 |
| std/slow6 | ns | 12 | 12/12 | 1/12 | 9 | 9/9 | 8/9 |
| adv/raw | s | 12 | 3/12 | 0/12 | 9 | 9/9 | 7/9 |
| adv/raw | ns | 12 | 11/12 | 1/12 | 9 | 8/9 | 6/9 |

## (v) Azure Phrase Listなし (Melos x said/replied、全take x 3obs)
- Melos said: n=12 Azure(PhraseListなし) PASS 1/12, 綴り一致 0/12; Azure(PhraseListあり) PASS 4/12; OpenAI PASS 0/12; OR(OpenAI or AzureなしPL) 1/12; OR(Phrase Listあり) 4/12
- Melos replied: n=12 Azure(PhraseListなし) PASS 8/12, 綴り一致 8/12; Azure(PhraseListあり) PASS 12/12; OpenAI PASS 2/12; OR(OpenAI or AzureなしPL) 8/12; OR(Phrase Listあり) 12/12

## transcript samples (Melos, raw/adv, 動詞別 OpenAI | Azure)
- Melos_said_L2_adv_t1: OA='Mello said.' AZ='Mellow said.' WH='Mello said.'
- Melos_said_L2_adv_t2: OA='Mello said.' AZ='Mello said.' WH='Mellow said.'
- Melos_said_L2_adv_t3: OA='Mella said.' AZ='Mello said.' WH='Melo said.'
- Melos_said_L2_adv_t4: OA='Mello said.' AZ='Melos said.' WH='Mello said.'
- Melos_says_L2_adv_t1: OA='Mello says' AZ='Mellow says.' WH='Melo says'
- Melos_says_L2_adv_t2: OA='Mello says' AZ='Melos says.' WH='Melo says.'
- Melos_says_L2_adv_t3: OA='Mello says' AZ='Mellow says.' WH='Mellow says'
- Melos_says_L2_adv_t4: OA='Mellow says,' AZ='Melo says.' WH='Melo says.'
- Melos_sighed_L2_adv_t1: OA='Mello sighed.' AZ='Mellow.' WH='mellow side'
- Melos_sighed_L2_adv_t2: OA='Mellow side' AZ='Mellow sighed.' WH='mellow side'
- Melos_sighed_L2_adv_t3: OA='Mello's sighed.' AZ='Mellow's side.' WH='mellows side'
- Melos_sighed_L2_adv_t4: OA='Mello sighed.' AZ='Mellow sighed.' WH='mellows side'
- Melos_replied_L2_adv_t1: OA='Melos replied,' AZ='Melos replied.' WH='Melos replied,'
- Melos_replied_L2_adv_t2: OA='Mellos replied.' AZ='Melos replied.' WH='Melos replied.'
- Melos_replied_L2_adv_t3: OA='Mellos replied.' AZ='Melos replied.' WH='Melos replied.'
- Melos_replied_L2_adv_t4: OA='Mellos replied.' AZ='Melos replied.' WH='Melos replied.'
- Melos_answered_L2_adv_t1: OA='Mellos answered.' AZ='Melos answered.' WH='Melos answered.'
- Melos_answered_L2_adv_t2: OA='Mellus answered.' AZ='Melos answered.' WH='Melos answered.'
- Melos_answered_L2_adv_t3: OA='Mellos answered.' AZ='Melos answered.' WH='Melos answered.'
- Melos_answered_L2_adv_t4: OA='Mellos answered.' AZ='Melos answered.' WH='Melos answered.'
- Melos_asked_L2_adv_t1: OA='Mellos asked?' AZ='Melos asked.' WH='mellows asked'
- Melos_asked_L2_adv_t2: OA='Mellis asked.' AZ='Mellis asked.' WH='Mellis asked.'
- Melos_asked_L2_adv_t3: OA='Mellos asked.' AZ='Melos asked.' WH='Melos asked.'
- Melos_asked_L2_adv_t4: OA='Mello's act?' AZ='Melos asked.' WH='Melos asked'