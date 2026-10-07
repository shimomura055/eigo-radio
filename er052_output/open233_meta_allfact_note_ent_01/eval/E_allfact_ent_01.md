# E_allfact_ent_01 全fact一律の多義語注意 2パターン×N=1 評価(OPEN-233-META-ALLFACT-NOTE-ENT-TRIAL-01、2026-10-07)
条件: P1=全15factのnotes末尾に「 / 注意(多義): <文言>」追記(OPEN233_NOTE_PREFIX=「注意(多義):」)、P2=「注意: <既存notes> / 注意(多義): <文言>」に整形(OPEN233_NOTE_PREFIX=「注意:」)。ベース台帳=control(sha ea0ce587…)、全15factのnotesは空でなく(空notes0件)全件へ付与。台帳sha: P1 b41276bb…/P2 d2db1058…(ledger/FREEZE.json)。nb variant、B3→JA R0/R1/R2→EN→自動Checker。N=1のため数値で結論を出さない。runnerの制約でout-dirは runs/meta/nb/<p1|p2>/rep1(指示のruns/meta/<p>/rep1から変更)。

## (e) brief転記状況
| run | brief行数 | 選択fact数 | 多義注意の転記 | 備考 |
|---|---|---|---|---|
| P1 | 14 | 3(HC-006/010/012) | 3/3件(文言逐語、切れなし) | 全factにNoteがあるため選択3件全てに付与 |
| P2 | 14 | 3(HC-006/010/012) | 多義注意 0/3件 | 「注意:」で始まる既存notesのみ転記(「注意: 全ての電話を人間が…限定する」等3行、URL省略)、末尾「/ 注意(多義): …」は3件とも転記されず |
| Control rep1 | 7 | - | なし | |
| rep13(HC-012のみ) | 11 | - | 1件 | |
P2の転記は規則(『注意:』始まりの注意文を意味を変えずそのまま)に沿って既存notesを転記したが、多義部分は落ちた(1行目接頭辞が『注意:』で、末尾の「注意(多義):」は同一行内の後半のため)。P2は実質「従来notesをbriefへ転記する条件」であり、多義語注意はWriterに届いていない。

## (a) rollback(HC-012)3分類(正しい/曖昧/重大誤読)
基準は既存(trial02評価と同一): 正しい=取り下げ・止めた等、機能が提供されない側が明確/曖昧=元に戻した・ロールバックのみ/重大誤読=復活・再提供等。
- P1 JA R2: 「そして二〇二六年九月二十二日までに、人間コンシェルジュ機能を当面ロールバックしました。Muse全体を止めたわけではありません。」(段落全文: 「Metaのスーパーインテリジェンス研究部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを始めたのは「ミス」だったと認めました。そして二〇二六年九月二十二日までに、人間コンシェルジュ機能を当面ロールバックしました。Muse全体を止めたわけではありません。」) 判定=曖昧。理由: 「ロールバック」のまま方向が未確定。ただし直後の「Muse全体を止めたわけではありません」が、対象機能は止まった側という読みを支える。復活側の表現なし。
- P1 EN: 「The vice president of Meta’s Superintelligence research division admitted that starting tests in which contract staff made calls without proper disclosure was a “mistake.” By September 22, 2026, Meta had temporarily rolled back the human concierge feature. It did not stop Muse as a whole.」 判定=曖昧。理由: rolled backのまま。「did not stop Muse as a whole」が対比として機能。
- P2 JA R2: 「Metaの担当副社長は、適切な開示なしに契約スタッフが電話をするテストを始めたのは「ミス」だったと認めました。そして、人間コンシェルジュ機能を当面ロールバックしました。Muse全体を止めたのではなく、人間が電話を担当する機能をいったん戻したのです。」 判定=曖昧(復元型候補)。理由: 「いったん戻した」は『機能を元の状態に戻した』とも『引っ込めた』とも読め、方向未確定。ただし「当面」「止めたのではなく…機能」で重大誤読(復活・再提供)とまでは言えない。
- P2 EN: 「A Meta vice president in charge acknowledged that starting tests in which contract workers made calls without proper disclosure was a “mistake.” Meta then temporarily pulled back the human concierge feature. It did not stop Muse as a whole; it temporarily pulled back the feature in which humans handled the calls.」 判定=正しい寄り(境界)。理由: pulled backは「引っ込める・撤回する」の意で、機能が提供されない側に読める。JA(戻した)より方向が明確。
- 参考 Control rep1 JA R2: 「Metaの幹部は、この始め方を「ミス」だったと認めました。そして9月22日までに、人間コンシェルジュ機能をロールバックしました。Museという作品そのものを上映中止にしたわけではありません。元に戻されたのは、人間スタッフが電話を担当する機能です。」 判定=曖昧(復元型候補、「元に戻された」)。(Control rep1 EN: 「Meta executives admitted … By September 22, they had rolled back the human concierge feature. They did not stop Muse itself. What was rolled back was the feature in which human staff handled the phone calls.」 判定=曖昧)
- 参考 rep13 JA R2(HC-012のみ付与): 「Metaの幹部は、…ミスだったと認めました。そのため、人間コンシェルジュ機能はいったん取りやめにしました。今後は、準備が整い、…公開するとしています。」 判定=正しい(「取りやめ」)。
- 要約: P1=曖昧(JA/EN)、P2=曖昧(JA)/正しい寄り(EN)、重大誤読は全run0件。N=1で効果は断定しない。

## (b) 決定論指標
JA R2(ja_copy_rate、台帳はベースcontrol台帳で統一。ent_metricsの語単位指標は日本語に不適のため、文字数と「。」数で代替):
| run | 文字数(空白除去) | 文数(「。」) | 台帳12字連続一致率 |
|---|---|---|---|
| P1 | 989 | 28 | 0.1234 |
| P2 | 853 | 23 | 0.1395 |
| Control rep1 | 900 | 28 | 0.1256 |
| TRIAL-02 rep13(HC-012のみ) | 877 | 25 | 0.0912 |

EN(ent_metrics_p01、見出し除外、台帳が日本語のため8語一致は0になりやすい):
| run | 文数 | 語数 | 平均文長(語) | type-token比 | 8語一致率 |
|---|---|---|---|---|---|
| P1 | 28 | 431 | 15.393 | 0.4803 | 0.0 |
| P2 | 23 | 388 | 16.87 | 0.4923 | 0.0 |
| Control rep1 | 25 | 384 | 15.36 | 0.5 | 0.0 |
(rep13はJAのみでENなし)

## (c) LLMペア比較(gpt-5.6-sol、順序入替2回、各軸を2回一致=その側が「優る」、割れ=「同等」扱い。断定しない)
| 比較 | story | tempo | natural | soft | overall |
|---|---|---|---|---|---|
| JA P1_vs_C | P1 | P1 | P1 | P1 | P1 |
| JA P2_vs_C | 割れ(P2/C) | 割れ(P2/C) | 割れ(P2/C) | 割れ(P2/C) | 割れ(P2/C) |
| JA P1_vs_P2 | P1 | P2 | 割れ(P2/P1) | P2 | 割れ(P2/P1) |
| EN P1_vs_C | P1 | P1 | P1 | P1 | P1 |
| EN P2_vs_C | 割れ(P2/C) | P2 | P2 | P2 | P2 |
| EN P1_vs_P2 | P1 | P1 | P1 | P1 | P1 |
読み方: 「P1」等は2回とも当該側が選ばれた軸、「割れ(A/B)」は順序入替で結果が割れた(位置バイアス含む=同等)。N=1・単一評価者(LLM)のため参考。生データ=eval/pairwise_allfact.json、費用¥29.03。
要約: JA P1 vs Control=P1が全軸優る / JA P2 vs Control=全軸同等 / JA P1 vs P2=storyのみP1・tempo/softはP2・naturalとoverallは同等 / EN P1 vs Control=P1が全軸優る / EN P2 vs Control=overallほかP2優る(storyは同等) / EN P1 vs P2=P1が全軸優る。

## (d) Checker結果(自動Checker、DEV)
| run | final_state | cycle数 | Rewrite発火 | 最終cycleの重大(BLOCKING最終)件数 | calls | 費用¥ |
|---|---|---|---|---|---|---|
| P1 | RESOLVED_REWRITE_THEN_DOWNGRADE | 3 | あり(cycle1でHC-012のusers…文をnarrow_scope) | 0 | 16 | 5.31 |
| P2 | RESOLVED_STAGE2_DOWNGRADE | 1 | なし | 0 | 5 | 2.61 |
| Control rep1 | RESOLVED_REWRITE_THEN_DOWNGRADE | 2 | あり(cycle1でHC-010) | 0 | 14 | 4.68 |
全run pass系(重大NG最終0)。P1 Rewrite内容: 「Still, users were not given enough information about the possibility that contract staff might handle their calls.」→「The test proceeded without proper disclosure that contract staff would handle some calls.」(Checker出力のen_text_after_rewrite。記事ファイルは未変更)。P1で残った指摘(ACCEPTABLE): 「Superintelligence research division」(台帳はSuperintelligence Labs部門)・比喩「途中から代役」。P2の指摘(ACCEPTABLE): 「The person on the other end had not been told clearly enough…」(説明を受けなかった対象が台帳に特定されない)ほか。Checker結果は承認根拠にしない。

## 所見(断定しない)
- P1はNoteがbriefに3/3逐語転記され、EN・JAともControlよりpairwiseで優る側が多いが、Checkerで1回Rewrite発火(Control同様)、rollback表現は曖昧のまま(Controlと同水準)。
- P2は多義注意がbriefに届いていない(従来notesのみ転記)ため、多義Noteの効果ではなく従来notes転記の効果を見ている。ENでは「pulled back」でrollback表現が相対的に明確、Checkerはクリーンに近い(Rewriteなし、1cycle)。
- P2のJA/EN本文に「(説明を)相手に十分知らせていなかった」という対象のずれ(台帳は利用者への開示)が出ており、Checkerに指摘された。P1 JAは「利用者」としており正確。
- 副次発見(実装せず報告): 転記規則は『注意:』始まりの1行を「そのまま」転記するため、P2形式(1行に既存notes+多義)では後半が脱落しうる。

## 実費
cost.json参照(run別・phase別、合計≈¥50.2)。

## (f) 記事全文
### P1 JA R2(ja_writer/revision2.md)
その電話、AIですか、人間ですか。Museに現れた意外な代役

電話を一本、AIに任せる。そんな便利な未来の舞台裏で、思わぬ配役変更が起きていました。主役として登場するはずのAIの代わりに、人間のスタッフが電話をしていたのです。

Metaが個人向けAIエージェント「Muse」で試した電話機能は、利用者に代わってAIが電話をかけ、相手との用件を進めるものです。ところが、その一部の電話では、AIではなく、訓練を受けた契約スタッフが登場しました。スタッフは電話をかけ、相手とのやり取りを完了させていました。

ここで大事なのは、すべての電話が人間だったわけではないことです。あくまで一部です。けれど、契約スタッフが電話を担当する可能性は、利用者に十分説明されていませんでした。

これは舞台でいえば、観客が主役をAIだと思って見ていたら、途中から代役が出てきたようなものです。しかも、その代役は声だけでなく、電話の内容も聞いています。笑える仕掛けならよかったのですが、電話には、つい個人的な話が混ざります。AIが処理していると思っていた情報を、人間の契約スタッフが知る可能性がある。ここで、便利な未来の話が、急にプライバシーの話へ変わります。

Metaの社内では、電話中の機微な情報が、コールセンターの契約スタッフに意図せず共有される可能性をめぐり、懸念が出ました。念のため言うと、大規模な情報漏えいが起きたという話ではありません。問題は、誰が電話をしているのかを、利用者が十分に知らないまま試験が進められたことです。

AIのサービスでは、賢く答えることばかりが注目されます。でも、電話の向こうに誰がいるのかを名乗ることも、同じくらい重要です。正体を隠したまま進む電話は、便利でも、安心とは少し違います。

Metaのスーパーインテリジェンス研究部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを始めたのは「ミス」だったと認めました。そして二〇二六年九月二十二日までに、人間コンシェルジュ機能を当面ロールバックしました。Muse全体を止めたわけではありません。

AIに電話を頼む時代の、まさかのどんでん返し。最後に確認したいのは、用件が終わったかだけではありません。受話器の向こうにいるのは、AIなのか、人間なのか。その答えを先に知らせることが、このサービスの本当の第一声になりそうです。

### P1 EN(b1b/article.md、Checker前)
# That Call—AI or Human? An Unexpected Stand-In Appears in Muse

Leave one phone call to AI. Behind that convenient future, an unexpected change in casting was taking place. Human staff were making the calls instead of the AI that was supposed to be the star.

Meta tested a phone feature in its AI agent for individuals, “Muse.” The feature lets AI make calls for users and handle matters with the other person. But on some of those calls, trained contract staff appeared instead of AI. The staff made the calls and completed the conversations.

The important point is that not all the calls were handled by humans. It was only some of them. Still, users were not given enough information about the possibility that contract staff might handle their calls.

In theater terms, it was like the audience watching a show thinking that AI was the star, only to see a stand-in come on halfway through. And the stand-in did not just hear the voice; they also heard what was said on the call. It would have been fine if this were just a funny trick. But personal matters can easily get mixed into a phone call. Human contract staff might learn information that users thought AI was handling. At that point, the story of a convenient future suddenly becomes a story about privacy.

Inside Meta, concerns arose that sensitive information from calls might be shared unintentionally with contract staff at call centers. To be clear, this does not mean that a large information leak occurred. The problem was that the test went forward without users knowing enough about who was making the calls.

With AI services, people tend to focus only on whether AI gives smart answers. But saying who is on the other end of the phone is just as important. A call that continues while the caller’s identity is hidden may be convenient, but it is not quite the same as feeling safe.

The vice president of Meta’s Superintelligence research division admitted that starting tests in which contract staff made calls without proper disclosure was a “mistake.” By September 22, 2026, Meta had temporarily rolled back the human concierge feature. It did not stop Muse as a whole.

This is an unexpected twist in the age of asking AI to make phone calls. The final thing we need to check is not only whether the matter was completed. Is the one on the other end of the phone AI or a human? Telling users that answer first may become the service’s true first greeting.

## In one line
Meta’s AI phone service sometimes used undisclosed human contractors, raising privacy concerns.

### P2 JA R2(ja_writer/revision2.md)
AIに電話を頼んだら、一部では人間が電話していた

電話の依頼をする。AIが店にかけて、予約や確認を済ませる。ここまでは、未来の便利機能です。

ところが、MetaのAIエージェント、Museのテストで起きたのは、まさかの主役交代でした。電話をかけていたのは、AIではなく、人間の契約スタッフだったのです。

Museは、米国内の企業や店に電話をかけ、散髪の予約を取ったり、在庫を確認したり、業者から見積もりを取ったりできます。ところが、その電話の一部では、AIが相手とのやり取りを最後まで担当していませんでした。訓練を受けた人間の契約スタッフが電話をかけ、話を完了させていたのです。

AIが仕事を進めるはずの場面で、AIは人間にマイクを渡していた。そんな、少し不思議な仕組みです。AIが電話をするサービスというより、AIが電話の仕事を人間へ引き継ぐサービス。そのテストだった、と考えると、急に舞台裏が見えてきます。

しかし、そこで新しい問題が登場しました。舞台裏の出演者が誰なのかを、相手に十分知らせていなかったのです。

Metaの社内では、人間の契約スタッフが電話を担当すると、電話中に利用者の機微な情報がコールセンターの契約スタッフへ意図せず共有される可能性があるとして、プライバシー上の懸念が出ました。

ここは慎重に見たいところです。大規模な情報漏えいが実際に起きた、という話ではありません。問題になったのは、AIに任せたつもりの電話に人間が入り、その人に利用者の情報が伝わる可能性を、十分に見せていなかったことです。

Metaの担当副社長は、適切な開示なしに契約スタッフが電話をするテストを始めたのは「ミス」だったと認めました。そして、人間コンシェルジュ機能を当面ロールバックしました。Muse全体を止めたのではなく、人間が電話を担当する機能をいったん戻したのです。

AIの話なのに、最後にスポットライトを浴びたのは人間でした。だからこそ、誰が話しているのかを最初に名乗ることが、便利な電話の大事な一機能になりそうです。

### P2 EN(b1b/article.md、Checker前)
# I Asked AI to Make a Call, but Humans Were Making Some of the Calls

You ask AI to make a phone call. AI calls the store and makes a reservation or checks something for you. Up to this point, it sounds like a useful feature from the future.

But in a test of Meta’s AI agent, Muse, the main role unexpectedly changed. The ones making the calls were not AI, but human contract workers.

Muse can call companies and stores in the United States, book haircuts, check whether items are in stock, and get price estimates from businesses. However, on some of those calls, the AI did not handle the conversation all the way to the end. Trained human contract workers made the calls and finished the conversations.

In situations where AI was supposed to handle the work, it handed the microphone to humans. It was a slightly strange system. Rather than a service where AI makes phone calls, it was a service where AI hands phone work over to humans. If we think of it as that kind of test, the backstage suddenly comes into view.

But then a new problem appeared. The person on the other end had not been told clearly enough who was working behind the scenes.

Within Meta, privacy concerns arose over the possibility that, when human contract workers handled calls, sensitive information about users could be unintentionally shared with contract workers at a call center during the call.

We should look at this point carefully. This does not mean that a large information leak actually happened. The problem was that, in a call people thought they had left to AI, a human could join the call, and people had not been clearly shown enough that the user’s information might reach that person.

A Meta vice president in charge acknowledged that starting tests in which contract workers made calls without proper disclosure was a “mistake.” Meta then temporarily pulled back the human concierge feature. It did not stop Muse as a whole; it temporarily pulled back the feature in which humans handled the calls.

Although this was a story about AI, humans were the ones who ended up in the spotlight. That is why saying who is speaking at the start may become an important feature of convenient phone calls.

## In one line
Meta’s AI phone-call test revealed that human contractors, not AI, sometimes handled calls without clear disclosure.
