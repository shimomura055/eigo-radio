# RESULT_01: POST-EN-HUMAN-PRE-SORTER-BLIND-TRIAL-01 一次報告(Trial/DEV、2026-10-10)

**User/ChatGPTのA/B/C/D判定は一切参照していない。User列・一致率はない(ChatGPT側で照合)。Production変更ゼロ。AI Pre-sorterのProduction wiringへは進まない。**

## 0. 実行できたモデル/できなかったモデル
- 実行できた(3): Luna `gpt-6-luna` / Sol `gpt-6.1-sol` / Astra `gpt-6-astra`(OpenAI Responses API直接、reasoning effort=medium、API応答のmodel欄と要求IDが一致)。
- **UNAVAILABLE(3)**: Fable `claude-fable-5-1` / Opus `claude-opus-5-5` / Sonnet `claude-sonnet-5-5`。理由: ANTHROPIC_API_KEYが環境(process/User/Machine/.env)に存在しない・`.venv`にanthropic SDKなし。api.anthropic.comへ3モデルを鍵なしで疎通し3件とも HTTP 401 authentication_error「x-api-key header is required」(model_check_01.json、request_id記録)。モデルの存在・権限は鍵がないため未検証。別モデルへの置換なし。GPT系3モデルのみ先行実施(ユーザー指示7のfallback)。

## 1. 一覧(Blind判定。User列なし。IDはPOST-EN-TRIAL-01の既存ID(稿番号-文番号)、ID順=BLIND_PACKET_01.mdの並び)

| # | ID | Fable | Opus | Sonnet | Luna | Sol | Astra |
|---|---|---|---|---|---|---|---|
| 1 | U01-s18 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | D | D | D |
| 2 | U02-s18 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | D | D | D |
| 3 | U03-s1 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | B | C | C |
| 4 | U03-s5 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | C | C |
| 5 | U03-s13 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | D | D |
| 6 | U03-s17 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | A | A | A |
| 7 | U03-s33 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | D | C |
| 8 | U04-s7 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | D | D |
| 9 | U04-s15 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | D | D |
| 10 | U05-s1 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | A | B | B |
| 11 | U05-s4 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | D | D | D |
| 12 | U05-s6 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | C | C |
| 13 | U06-s8 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | C | C |
| 14 | U06-s9 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | C | C |
| 15 | U06-s16 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | D | D | D |
| 16 | U06-s17 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | D | D | D |
| 17 | U06-s21 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | C | C |
| 18 | U07-s1 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | D | D |
| 19 | U07-s5 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | A | B | B |
| 20 | U07-s21 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | D | D | D |
| 21 | U07-s22 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | D | D | D |
| 22 | U08-s25 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | B | B |
| 23 | X09-s8 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | B | A | A |
| 24 | X09-s10 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | D | D | D |
| 25 | X10-s5 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | D | D | D |
| 26 | X11-s4 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | B | C |
| 27 | X11-s7 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | A | A | A |
| 28 | X11-s17 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | C | D | D |
| 29 | X11-s25 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | D | D | D |

## 2. モデル別集計(実測)

| モデル | actual model_id(API応答) | A | B | C | D | 修正推奨Yes | Human Review High | 費用(実測JPY) | 入力tok | 出力tok(うちreasoning) | calls | retry | API/JSON failure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Luna | gpt-6-luna | 4 | 2 | 13 | 10 | 14 | 4 | 0.97 | 27125 | 6655 (4565) | 3 | 0 | 0 |
| Sol | gpt-6.1-sol | 3 | 4 | 6 | 16 | 7 | 3 | 13.40 | 27125 | 2951 (574) | 3 | 0 | 0 |
| Astra | gpt-6-astra | 3 | 3 | 8 | 15 | 6 | 3 | 66.26 | 27125 | 2857 (328) | 3 | 0 | 0 |
| Fable/Opus/Sonnet | - | UNAVAILABLE | | | | | | 0 | | | 0 | | |

合計実費 **JPY 80.62**(見積 中央JPY249.5/高位JPY452.8に対し大幅に下回った。見積のreasoning仮定が過大だった。実測の1モデル当たり入力/出力は上表)。routing: 全て直接OpenAI API(api.openai.com、Responses API)、effort=medium、max_output_tokens=16,000。単価: 登録値(Luna 0.1/0.5、Sol 2/10、Astra 10/50 $/1M、USD/JPY=160、cached入力は登録cached単価)。
retry: 全9 callで再試行なし・JSON valid(attempts=1)。API failure: 0。使用モデル: 最新世代(Luna=最新の効率系、Sol 6.1=最新の推奨系、Astra=最新の旗艦、PM_GOVERNANCE 25節)。runtime evidence: `runs/<model_id>/batch_<n>.json`(system_prompt・user_message・packet/prompt sha・raw_text・response_id・usage・cost・timestamp・retried・parsed)、`cost_ledger_presorter_01.jsonl`。

## 3. モデル間の一致(3モデルのみ。User判定との照合は行わない)

- 3モデル全一致: 17/29件。
- 3モデルが全て異なる件: なし
- 最大差が2段階以上(例 A-C, B-D)の件: なし
- Luna vs Sol 完全一致: 17/29
- Luna vs Astra 完全一致: 19/29
- Sol vs Astra 完全一致: 27/29


## 4. 23番(ID順23件目 = X09-s8。U.S.のピリオドでsentence splitterが途中切断した例のうち、ユーザー指示の「23番」に相当すると推定した位置。対象モデルには一切教えていない)

Flag対象文: Trump’s “20% plan.” It called for a 20% payment on all cargo passing through the Strait of Hormuz, as reimbursement for the cost of ensuring U.S.

- Luna: grade=B / fix=Yes / HR=Medium / splitter・切断への言及(キーワード機械判定)=なし
  理由: The ledger says the proposed payment was reimbursement for U.S. costs of securing the Strait, while “ensuring U.S. security” can suggest the broader purpose of protecting the United States. The nearby reference to cargo passing through Hormuz narrows the interpretation, but the stated purpose could still mislead and should be clarified.
- Sol: grade=A / fix=Yes / HR=High / splitter・切断への言及(キーワード機械判定)=あり 「fragment」
  理由: Reading the adjoining fragment produces “the cost of ensuring U.S. security,” so this is not merely a sentence-segmentation issue. The ledger describes reimbursement for the United States providing security in the Strait of Hormuz, not for ensuring the security of the United States itself, materially changing the stated purpose.
- Astra: grade=A / fix=Yes / HR=High / splitter・切断への言及(キーワード機械判定)=あり 「fragment」
  理由: Read together with the following fragment, the sentence says the payment reimburses the cost of ensuring U.S. security. The ledger instead describes reimbursement for security provided by the United States in the Strait of Hormuz, so the wording changes the stated object of protection and rationale for the proposal.

参考: 全29件の理由文のうち分割/切断への言及(同キーワード機械判定)があった件:

- Luna: なし
- Sol: X09-s8
- Astra: X09-s8

(注: 23番=ID順23件目という対応は推定。ユーザーの番号体系と違う場合は ChatGPT側で補正。同じくU.S.で切れた文の候補が他にも29件内にある場合がある。)

## 5. 各判定理由の全文(モデル別。raw responseから転記、改変なし)

### Luna

- **1. U01-s18** [D] fix=No HR=Low — The sentence cautions against inferring that sharing occurred; it does not claim that no information was shared. The surrounding sentences make clear that the reported fact is a concern about possible inadvertent sharing, not proof of a leak.
- **2. U02-s18** [D] fix=No HR=Low — This is a reasonable summary of the reported brief pullback and subsequent recovery, and the following sentence clarifies that Brent gave up some gains rather than plunging. It does not say the replacement deal caused the price movement or prevented a larger fall.
- **3. U03-s1** [B] fix=Yes HR=Medium — The headline can imply that the deployed weapons have a specific secret attack capability, which the ledger does not establish. The following text pushes back against that interpretation, but the headline itself risks giving readers a misleading impression.
- **4. U03-s5** [C] fix=No HR=Low — The ledger supports that specific capabilities were not provided, but “remain secret” can imply they are deliberately classified rather than simply undisclosed in the cited account. The gap is limited because the sentence does not identify or invent any particular capability.
- **5. U03-s13** [C] fix=No HR=Low — The ledger cautions against supplying specific system names or capabilities, but does not itself establish that none have been given publicly. In context, this is a plausible summary of what was disclosed, with little risk of materially misleading readers.
- **6. U03-s17** [A] fix=Yes HR=High — The ledger records Russia destroying one satellite, COSMOS 1408, while “satellites” ordinarily suggests multiple satellites were destroyed. That expands a single documented event into a broader record and should be corrected.
- **7. U03-s33** [C] fix=No HR=Low — The sentence broadly says capabilities were not disclosed, although the ledger does report a defensive purpose and does not establish that every aspect of capability is undisclosed. In context, it likely means specific operational capabilities, so the imprecision is modest.
- **8. U04-s7** [C] fix=No HR=Low — The ledger describes particular runway clutches as more artistic than practical, while the sentence generalizes that framing to a mini bag. The surrounding discussion narrows the topic to decorative runway trends, so the likely effect on readers’ understanding is small.
- **9. U04-s15** [C] fix=No HR=Low — The sentence suggests a neat division between small bags for decoration and large bags for carrying, whereas the ledger supports coexistence of small and roomy styles without assigning every bag that role. The surrounding text presents this as a trend interpretation rather than a strict rule.
- **10. U05-s1** [A] fix=Yes HR=High — The headline states the brake-light behavior as an unqualified occurrence, while the ledger describes it only as a possibility in an extreme case involving the stopper pad falling off. This turns a conditional safety risk into an apparent general or actual event and should be qualified.
- **11. U05-s4** [D] fix=No HR=Low — The surrounding lines present a stylized scene of brake lights sending a confusing signal. Saying the driver does not know why is a reasonable narrative inference about that mismatch, not a consequential claim about a documented driver.
- **12. U05-s6** [C] fix=Yes HR=Low — The total of 183,211 is correct, but it combines two Chinese recall notices rather than appearing in a single notice. The singular phrasing is a small scope imprecision and does not change the total or the affected lines.
- **13. U06-s8** [C] fix=Yes HR=Low — The listed prices and increase are accurate for the U.S. standalone plan, and the surrounding article discusses when the change applies. The sentence omits the U.S. scope and the possible third-party billing exception, so a brief qualifier would improve precision.
- **14. U06-s9** [C] fix=Yes HR=Low — The listed prices and increase are accurate for the U.S. standalone Premium monthly plan, and the surrounding article distinguishes timing by subscriber and billing cycle. The sentence omits the U.S. scope and possible third-party billing differences, a minor but correctable limitation.
- **15. U06-s16** [D] fix=No HR=Low — In context, “preview” refers to the public headline about the increase, not a literal notice sent to every subscriber. The following lines explicitly clarify that the date the change appears on bills varies.
- **16. U06-s17** [D] fix=No HR=Low — The sentence naturally summarizes that the effective date for existing subscribers depends on their billing cycle. It need not mean that every subscriber has a unique date, especially given the surrounding explanation of differing billing cycles.
- **17. U06-s21** [C] fix=Yes HR=Low — For subscribers covered by the U.S. pricing information, signup date and billing cycle are relevant to determining when the change applies. The claim is a little too categorical because third-party billing can have different prices or conditions.
- **18. U07-s1** [C] fix=Yes HR=Low — The headline’s plural “AI Lawsuits” generalizes beyond the specific complaint described in the article. The article context makes the intended case clear, so this is a limited framing issue rather than a major factual distortion.
- **19. U07-s5** [A] fix=Yes HR=High — The complaint seeks destruction of models incorporating the plaintiffs’ content, not GPT or similar models without qualification. Omitting that limitation can make readers believe the plaintiffs seek destruction of those models generally, substantially expanding the requested relief.
- **20. U07-s21** [D] fix=No HR=Low — “Had not yet responded” is a reasonable paraphrase of Reuters reporting that the spokesperson did not respond immediately, particularly with the sentence anchored to the time of the report. It does not imply that OpenAI never responded or had filed no legal answer beyond that reported status.
- **21. U07-s22** [D] fix=No HR=Low — This is broad editorial framing about common AI-news coverage, not a specific factual claim about the lawsuit. It works as a natural transition and does not materially alter any ledger fact.
- **22. U08-s25** [C] fix=Yes HR=Medium — The caution against inferring that AI demand caused the revenue forecast is reasonable, but the ledger does not establish that the announcement itself offered no explanation of the connection. The unsupported point is limited and does not materially misstate either figure.
- **23. X09-s8** [B] fix=Yes HR=Medium — The ledger says the proposed payment was reimbursement for U.S. costs of securing the Strait, while “ensuring U.S. security” can suggest the broader purpose of protecting the United States. The nearby reference to cargo passing through Hormuz narrows the interpretation, but the stated purpose could still mislead and should be clarified.
- **24. X09-s10** [D] fix=No HR=Low — The sentence is a reasonable narrative observation about why a proposed 20% charge applying to all cargo attracted attention. It does not claim that the plan was implemented or that the proposal caused a specific market movement.
- **25. X10-s5** [D] fix=No HR=Low — The sentence is a rhetorical contrast that redirects attention from a fanciful, planet-destroying weapon to the meaning of “space weapon.” It does not make a concrete claim about the deployed system’s capabilities.
- **26. X11-s4** [C] fix=Yes HR=Medium — The ledger specifies that the destruction request concerns models and training sets incorporating the plaintiffs’ content. “Problematic content” is vaguer and could imply a wider category, although the sentence remains attributed to the plaintiffs and the surrounding context concerns their claims.
- **27. X11-s7** [A] fix=Yes HR=High — The sentence makes the models’ output the grammatical subject of both copying content and removing copyright management information. The ledger instead attributes the removal claim to OpenAI, changing the alleged actor in a significant way.
- **28. X11-s17** [C] fix=Yes HR=Medium — The ledger limits the requested destruction to models and training sets incorporating the plaintiffs’ content, whereas “what we claim you made using those articles” could sound broader. The surrounding sentences identify the models and training sets as the focus, so the scope drift is limited.
- **29. X11-s25** [D] fix=No HR=Low — “OpenAI had not commented right away” is a natural shorthand for Reuters reporting that its spokesperson did not immediately respond to a comment request. In context, it does not suggest that OpenAI never responded or offered a substantive legal position.

### Sol

- **1. U01-s18** [D] fix=No HR=Low — In context, “any information” refers back to the sensitive information whose accidental sharing employees feared. The sentence cautions against treating a reported concern as proof of an incident; it does not assert that no information of any kind was shared.
- **2. U02-s18** [D] fix=No HR=Low — The reported temporary narrowing of gains followed by recovery reasonably supports the ordinary-language summary that Brent did not plunge. “So” functions here as a narrative transition, not a clear claim that replacing the proposal prevented a crash, and the following sentence acknowledges the temporary retreat.
- **3. U03-s1** [C] fix=No HR=Low — “Special attack” is playful headline language, and the following context explicitly redirects readers away from imagined cinematic weapons. However, calling it “secret” slightly overstates the ledger, which establishes deployment without establishing that a particular attack capability exists and is classified.
- **4. U03-s5** [C] fix=No HR=Low — The main contrast between acknowledged orbital deployment and unspecified technical details is faithful to the ledger. “Remain secret” adds a modest unsupported implication of deliberate secrecy, rather than simply saying the announcement does not provide performance details.
- **5. U03-s13** [D] fix=No HR=Low — The surrounding passage makes this a statement about the deployment announcement being discussed, not an exhaustive claim about every previous public disclosure. Distinguishing acknowledgment of deployment from knowledge of specific systems or attack capabilities is a reasonable explanation of the ledger's limits.
- **6. U03-s17** [A] fix=Yes HR=High — The ledger documents the destruction of one satellite, COSMOS 1408, in one specified Russian test. “Has destroyed satellites,” reinforced by “these were tests” in the next sentence, turns that single event into an apparent record of multiple satellite destructions and should be corrected.
- **7. U03-s33** [D] fix=No HR=Low — In this concluding summary, “capabilities” naturally refers to the specific technical and attack capabilities discussed earlier. The stated defensive purpose does not itself disclose those details, so this is a reasonable summary rather than a substantive denial of information the ledger supplies.
- **8. U04-s7** [D] fix=No HR=Low — The preceding sentence explicitly anchors the discussion in small decorative runway clutches and rejects treating all small bags as practical comeback items. The “little star” description is a natural metaphor for their artistic, outfit-accent role, not a consequential claim about every mini bag.
- **9. U04-s15** [D] fix=No HR=Low — This is a rhetorical summary of the coexistence of decorative small styles and roomy large styles in the cited collections. It offers contrasting styling choices without saying that small bags can never carry belongings or that large bags cannot be decorative.
- **10. U05-s1** [B] fix=Yes HR=Medium — The headline accurately describes the possible brake-light malfunction and does not confuse it with brake failure. However, its categorical wording, reinforced by the opening dialogue, omits that this is a possibility limited to extreme cases involving a detached component; a brief qualifier would avoid making the malfunction sound like an established routine occurrence.
- **11. U05-s4** [D] fix=No HR=Low — The surrounding dialogue and personification make this an imagined scene illustrating mismatched brake signals, not a verified claim about a particular driver's knowledge. It does not materially change the recall facts.
- **12. U05-s6** [C] fix=No HR=Low — The total actually comes from two recall notices, rather than one notice naming all 183,211 vehicles. However, the sentence preserves the correct total, vehicle lines, and Chinese scope, so the administrative simplification has little effect on readers' understanding.
- **13. U06-s8** [C] fix=No HR=Low — The prices, increase, and standalone-plan scope are correct. The future tense and omitted US and third-party-billing qualifications make the summary slightly broad, but it does not explicitly claim worldwide pricing or a single implementation date, and the surrounding narrative introduces timing distinctions.
- **14. U06-s9** [C] fix=No HR=Low — The Premium monthly prices and $2.50 increase accurately match the ledger. The sentence omits regional and third-party-billing qualifications and summarizes the change prospectively, but the context signals that implementation timing will be explained separately rather than asserting simultaneous application to everyone.
- **15. U06-s16** [D] fix=No HR=Low — The preview, release-date, and main-story language forms an extended entertainment metaphor about announcement versus billing dates. In this context, 'sent to everyone' is not reasonably read as a factual assertion that Disney delivered an individual notification to every subscriber.
- **16. U06-s17** [D] fix=No HR=Low — 'Different for each person' naturally means that the applicable date depends on the person's circumstances, not that every subscriber has a unique date. The surrounding references to billing cycles and subscriber status reinforce the ledger's intended distinction.
- **17. U06-s21** [C] fix=No HR=Low — This is a reasonable practical summary of how the standard pricing schedule applies according to signup date and billing cycle. It omits the possibility of different third-party-billing conditions, so the advice is somewhat overgeneralized, but the central explanation remains accurate.
- **18. U07-s1** [D] fix=No HR=Low — The headline uses this lawsuit to make a thematic point that AI litigation can concern remedies beyond money. The immediately following sentences identify the particular case, and 'a demand' correctly presents model destruction as requested relief rather than a court order.
- **19. U07-s5** [B] fix=Yes HR=Medium — The sentence correctly attributes destruction to the plaintiffs' demands, but omits the limitation to models incorporating their content. Because the scope of the requested destruction is a central issue, this could suggest a broader demand against GPT models generally, although the nearby discussion of allegedly copied training content partly supplies the missing connection.
- **20. U07-s21** [D] fix=No HR=Low — This is a normal paraphrase of Reuters reporting that a spokesperson did not immediately respond to its comment request. It explicitly limits the statement to the reporting time and does not imply a failure to answer the lawsuit in court or continued silence afterward.
- **21. U07-s22** [D] fix=No HR=Low — This is a general narrative contrast introducing the article’s focus on training material and model destruction demands. It does not alter any lawsuit fact or turn an allegation into an established finding.
- **22. U08-s25** [B] fix=Yes HR=Medium — The warning against treating the demand assessment as a complete explanation of consolidated revenue guidance is reasonable. However, saying the announcement does not explain the connection makes a source-wide claim that the supplied facts do not establish; the announcement could contain additional explanation.
- **23. X09-s8** [A] fix=Yes HR=High — Reading the adjoining fragment produces “the cost of ensuring U.S. security,” so this is not merely a sentence-segmentation issue. The ledger describes reimbursement for the United States providing security in the Strait of Hormuz, not for ensuring the security of the United States itself, materially changing the stated purpose.
- **24. X09-s10** [D] fix=No HR=Low — Describing a 20% proposal covering all cargo as headline-grabbing is ordinary editorial narration. It does not introduce a consequential explanation of market movements or the proposal’s subsequent withdrawal.
- **25. X10-s5** [D] fix=No HR=Low — In context, the Earth-destroying weapon and laser cannon are clearly science-fiction imagery used to reset readers’ expectations. The sentence identifies the article’s subject rather than purporting to establish the deployed weapons’ technical capabilities.
- **26. X11-s4** [B] fix=Yes HR=Medium — “Problematic content” replaces the specific condition that the models incorporate the plaintiffs’ content with a vague, potentially broader category. The surrounding copyright allegations limit the likely misunderstanding, but the destruction demand would be more accurately described using the plaintiffs’ content as its defining condition.
- **27. X11-s7** [A] fix=Yes HR=High — The grammar attributes removal of copyright management information to the models’ output, whereas the ledger attributes the alleged removal to OpenAI. This changes the alleged conduct and suggests an output-stage mechanism that the supplied fact does not establish; retaining attribution to the plaintiffs does not resolve that change.
- **28. X11-s17** [D] fix=No HR=Low — The preceding sentences explicitly identify models and training sets, so “what we claim you made using those articles” naturally refers back to those objects. This is an illustrative paraphrase distinguishing monetary relief from destruction, and the following sentences preserve the distinction between a request and a court order.
- **29. X11-s25** [D] fix=No HR=Low — In this reporting context, saying OpenAI had not commented right away is normal shorthand for its spokesperson not immediately responding to a comment request. The explicit reference to the time of Reuters’ report preserves the temporal limitation and does not imply a missing court response or continuing silence.

### Astra

- **1. U01-s18** [D] fix=No HR=Low — In context, “any information” refers back to the sensitive information whose accidental sharing concerned employees. The sentence appropriately distinguishes a reported concern from evidence of an actual incident; it does not assert that no information was shared.
- **2. U02-s18** [D] fix=No HR=Low — The reported brief narrowing of gains followed by recovery reasonably supports the narrative contrast with a sudden plunge. The following sentence explicitly acknowledges the temporary decline, and “So” does not clearly assert that the replacement deal prevented a crash.
- **3. U03-s1** [C] fix=No HR=Low — “Special attack” and “address” are plainly playful framing, not claims about a particular weapon or precise orbital location. Calling the attack “secret” nevertheless goes slightly beyond the ledger by implying an established but concealed attack capability.
- **4. U03-s5** [C] fix=No HR=Low — The ledger does not establish that performance details are formally secret, so the wording is stronger than saying they are not specified in this account. However, the sentence supplies no invented performance characteristics and preserves the central distinction between acknowledged deployment and unspecified capabilities.
- **5. U03-s13** [D] fix=No HR=Low — In this passage, “have been given” naturally refers to the announcement being discussed, rather than every public disclosure anywhere. The sentence reasonably explains the limits of the supplied information and reinforces the ledger’s instruction not to invent specific systems or attack capabilities.
- **6. U03-s17** [A] fix=Yes HR=High — The ledger documents the destruction of one named satellite in one Russian test, whereas “has destroyed satellites” presents a record of multiple satellite destructions. The following reference to “these … tests” reinforces that unsupported expansion rather than resolving it as a generic description.
- **7. U03-s33** [C] fix=No HR=Low — The deployment acknowledgment is accurately summarized, and readers will likely understand “capabilities” as the weapons’ detailed technical capabilities. Still, the blanket nondisclosure wording is broader than the ledger, which includes a general protective function and does not independently establish the full extent of public disclosure.
- **8. U04-s7** [D] fix=No HR=Low — The preceding sentence explicitly anchors this discussion to decorative runway clutches, making the “little star” description a natural continuation of that example. The passage offers a styling perspective rather than a factual claim that all mini bags lack practical functions.
- **9. U04-s15** [D] fix=No HR=Low — This is a conversational summary of the coexistence of decorative small bags and roomier designs, which both ledger entries support. It does not impose an exclusive rule about what every small or large bag can do, particularly given the next sentence’s recognition of bags’ dual roles.
- **10. U05-s1** [B] fix=Yes HR=Medium — The headline accurately depicts the potential brake-light symptom and does not suggest that braking itself fails. However, its categorical wording and the immediate dramatization omit both the exceptional component-failure condition and the uncertainty, potentially making a conditional recall risk sound like an observed occurrence.
- **11. U05-s4** [D] fix=No HR=Low — The surrounding dialogue and personification clearly frame this as an imagined scene illustrating misleading brake lights. It is not presented as a verified account of an actual driver's knowledge.
- **12. U05-s6** [C] fix=No HR=Low — The total actually comes from two notices, so attributing it to a single notice is technically inaccurate. However, the sentence preserves the correct combined vehicle count, both vehicle lines, and the China scope, leaving the main recall facts intact.
- **13. U06-s8** [C] fix=No HR=Low — The plan, prices, and increase are correct. The future tense and omitted US and third-party-billing qualifications make this somewhat less precise, but a price-summary sentence need not repeat every applicability condition or establish the full implementation schedule.
- **14. U06-s9** [C] fix=No HR=Low — The Premium monthly prices and calculated increase match the ledger. The sentence compresses the timing and billing qualifications, but the surrounding transition to separate subscriber paths makes it reasonable to read this as a price summary rather than a claim of identical treatment for everyone.
- **15. U06-s16** [D] fix=No HR=Low — The references to a preview, release date, and main story form an obvious entertainment metaphor for the announcement and subsequent billing changes. In context, 'sent to everyone' is not a factual assertion that Disney delivered an individual notification to every subscriber.
- **16. U06-s17** [D] fix=No HR=Low — 'Different for each person' naturally means that timing depends on individual circumstances, not that every subscriber has a unique date. The surrounding explanation about billing cycles and subscriber status supports precisely that reading.
- **17. U06-s21** [C] fix=No HR=Low — This accurately summarizes how signup timing and billing cycles determine applicability under the published schedule. It does not acknowledge that third-party billing may introduce exceptions, but that omission is a limited qualification gap rather than a substantial distortion of the general guidance.
- **18. U07-s1** [D] fix=No HR=Low — The headline draws a reasonable thematic lesson from a lawsuit seeking both monetary and nonmonetary relief. The following reference to 'this AI lawsuit' anchors the discussion to the specific case, and 'demand' correctly distinguishes the requested remedy from a court order.
- **19. U07-s5** [B] fix=Yes HR=Medium — The sentence correctly identifies destruction as a plaintiffs' demand, but omits the meaningful restriction to models incorporating their content. The nearby training allegations help establish the connection, yet the wording can still suggest a broader demand against GPT models generally; adding the restriction would remove that ambiguity.
- **20. U07-s21** [D] fix=No HR=Low — This is a reasonable paraphrase of Reuters' report that OpenAI did not immediately respond to its comment request. The explicit reporting-time limit and reference to a request for comment avoid implying either permanent silence or a failure to answer the lawsuit in court.
- **21. U07-s22** [D] fix=No HR=Low — This is ordinary introductory framing about AI coverage, not a substantive claim about the lawsuit. It provides a natural contrast with the discussion of training material and model destruction without changing any ledger fact.
- **22. U08-s25** [B] fix=Yes HR=Medium — The warning against treating strong AI demand as a complete explanation of consolidated revenue guidance is reasonable. However, saying the announcement itself does not explain the connection goes beyond what these ledger entries establish about the announcement's contents.
- **23. X09-s8** [A] fix=Yes HR=High — Read together with the following fragment, the sentence says the payment reimburses the cost of ensuring U.S. security. The ledger instead describes reimbursement for security provided by the United States in the Strait of Hormuz, so the wording changes the stated object of protection and rationale for the proposal.
- **24. X09-s10** [D] fix=No HR=Low — The reference to grabbing headlines is ordinary narrative emphasis on the proposal's striking rate and broad coverage. It does not introduce a consequential causal claim about oil prices or the subsequent withdrawal.
- **25. X10-s5** [D] fix=No HR=Low — In context, the Earth-destroying weapon is an explicitly fanciful image used to redirect readers away from science-fiction expectations. The sentence does not purport to establish the deployed systems' specific capabilities and is acceptable rhetorical framing.
- **26. X11-s4** [C] fix=No HR=Low — “Problematic content” is less precise than the plaintiffs' own content and could suggest a broader category in isolation. However, the surrounding discussion identifies the plaintiffs' allegations about unauthorized use of news content, while the sentence correctly presents destruction as requested relief rather than an order.
- **27. X11-s7** [A] fix=Yes HR=High — The sentence grammatically attributes removal of copyright management information to the models' output, whereas the ledger attributes that alleged conduct to OpenAI. This changes the actor and suggests an output-stage mechanism that the ledger does not establish; retaining allegation language does not resolve that distortion.
- **28. X11-s17** [D] fix=No HR=Low — The surrounding sentences explicitly identify models and training sets as the objects of the destruction demand. Within that context, “what we claim you made using those articles” is an accessible summary, not a meaningful expansion to all article-derived products, and the passage preserves the distinction between a request and an order.
- **29. X11-s25** [D] fix=No HR=Low — The references to Reuters' reporting time and the lack of an immediate comment preserve the essential limits of the ledger entry. Omitting the spokesperson and explicit mention of the comment request is normal journalistic compression here, not a claim of permanent silence or a missing court response.

## 6. 未決事項・STOP
- Fable/Opus/Sonnetの実行にはANTHROPIC_API_KEY(とSDK)の用意が必要(ユーザー判断)。用意されれば同じpacket/prompt/バッチで追実行可能(事前登録のsha固定済み)。ただし今回はSTOP。
- User/ChatGPTのA/B/C/D照合はChatGPT側。Production wiringへは進まない。Closeout分類(Sonnet提案): USER_DECISION_REQUIRED(Anthropic 3モデル未実施・User照合未了のためVALIDATED/REJECTEDにしない)。Fable確定。
