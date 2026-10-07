# E_hormuz 評価シート(OPEN-233-META-ALLFACT-NOTE-E2E-TRIAL-02 / 委任_C1 / 2026-10-07 / 評価者: Sonnet)
方針: 台帳(P2版=Control版とfact本文同一)を直接照合→Checker結果は後から参照。AI面白さ採点なし。件数=判定した問題の件数(軽微含む)。「比喩・一般論」は事実誤りに数えず、末尾の備考に回す。
EN本文は b1b/article.md(Checker前)とChecker rewrite後の差を明記。評価の主対象は「最終EN+JA R2」。
Hormuz ★fact: HF-007(置換・協議理由)、HF-008(誰にも課すべきでない)、HF-009(撤回後Brent一時縮小→回復)、HF-011、HF-012。今回のbriefで含まれるのは、P2 rep1=HF-002/007、P2 rep2=HF-002/007/009、Control=HF-002/007/009相当+HF-008(JA R2に含む)。
台帳の重要限定: HF-003(7/13時点で徴収主体・支払義務者・通貨・免除等は未提示→「導入した」と書かない)、HF-007(24時間48分後、理由=協議)、HF-009(一時縮小→回復、約+2.6%・85ドル超、全面下落と書かない)。

---
## A. P2 rep1 (hormuz/nb/p2/rep1)
### (1) Fact整合
| 区分 | 件数 | 該当文 | 根拠 |
|---|---|---|---|
| 主体(支払義務者等) | 2 | ①JA R2「言い換えると、海峡を通る荷物に、広く同じ割合で費用を負担してもらう案です。」/EN「In other words, the plan was to have all cargo passing through the strait share the cost at the same rate.」(貨物が支払う=支払義務者の特定。Checker=ACCEPTABLE) ②JA R2「貨物に直接料金をかける方法と、相手国との協議を通じて貿易や投資につなげる方法です。」/EN b1b「One is to charge cargo directly.」(徴収方法の特定。ENはCheckerがBLOCKINGでrewrite→「One is to propose a charge on cargo.」、JA R2には残存) | HF-003: 支払義務者・徴収方法は未提示 |
| 対象 | 1 | JA R2題名「海峡の請求書が、翌日には商談になった」/本文「湾岸諸国との貿易や投資を進める案になりました」/EN「it became a plan to promote trade and investment with the Gulf states」「…turn into business talks between countries」、one-liner「A planned cargo fee in the Strait of Hormuz became trade and investment talks the next day.」、「It is that the very idea of collecting a fee moved to a different setting.」 | 台帳: 置換先は「貿易・投資案件(deals)」、「協議(talks)」は決定の理由。置換先を「talks」とし、さらに「料金徴収の考え方が別の場所へ移った」と継続性を示唆(CheckerもQUALITY/ACCEPTABLE) |
| 範囲 | 1 | JA R2「相手国との協議を通じて貿易や投資につなげる方法」/EN「The other is to use talks with the other country to lead to trade and investment.」 | 台帳は「湾岸諸国(複数)」。ENは単数"the other country"、JAも「湾岸諸国」を「相手国」に置換 |
| 時系列 | 1(軽微) | JA R2「今回の投稿は、その切り替えが一日で起きたことを示しました。」/EN「This post showed that the switch happened in one day.」 | 台帳は約24時間48分後(「翌日」は正しいが「一日で」は厳密には不正確。Control版は「just over a day」で正確) |
| 否定 | 0 | - | - |
| 因果 | 1 | EN「The other is to use talks with the other country to lead to trade and investment.」(協議が貿易・投資をもたらすという因果。Checker=ACCEPTABLEを3サイクル維持) | 台帳は「協議に基づく決定」と説明したのみ |
| 台帳にない具体的事実の追加 | 2 | ①JA R2「もし実施されれば、通る貨物すべてが対象になる大きな仕組みでした。」/EN「…it would have been a large system covering every piece of cargo that passed through.」(制度規模。Checker=ACCEPTABLE) ②JA R2「同じ安全確保をめぐる話でも、入り口は二つあります。」/EN「Even when the issue is about providing security, there are two ways in.」(貿易・投資案件を安全確保の別方式と位置付け。Checker=QUALITY/ACCEPTABLE) | 台帳なし |
### (2) ★fact
| fact_id | 該当段落(全文) | 判定 | 理由 |
|---|---|---|---|
| HF-007 | JA R2「翌日の七月十四日、トランプ氏は、その二十パーセントの米国償還料案を撤回しました。そして代わりに、湾岸諸国による対米貿易と投資の案件へ置き換えると投稿しました。中東の指導者たちとの「非常に生産的な協議」に基づく決定だと説明しています。」/EN「On the next day, July 14, Trump withdrew the U.S. plan for a 20 percent reimbursement fee. Instead, he posted that it would be replaced with trade and investment deals between the Gulf states and the United States. He explained that the decision was based on “very productive talks” with Middle Eastern leaders.」 | 曖昧 | 上記の明示文自体は正確。ただし記事全体の筋(題名・one-liner・「料金徴収の考え方が移った」「協議を通じて貿易・投資につなげる」)が「置換先=talks」「料金案の継続」として語り直しており、理由(協議)と置換物(案件)の混同を誘う。誤読と断定はできないため重大にしない |
### (3) JA→EN意味変化
| 区分 | 件数 | 該当文(R0 / R2 / EN) | 備考 |
|---|---|---|---|
| R0→R2 | 3 | ①R0「湾岸諸国との貿易や投資を通じて、米国との関係を深めるやり方へ移りました」→R2「相手国との協議を通じて貿易や投資につなげる方法」→EN「use talks with the other country to lead to trade and investment」 ②R0「米国は…直接お金を集める案を引っ込め、湾岸諸国との取引を増やす方向を選んだ」→R2「料金を集めるという発想そのものが、別の舞台へ移ったことです」→EN「the very idea of collecting a fee moved to a different setting」 ③R0に無し→R2「通る貨物すべてが対象になる大きな仕組み」→EN「a large system」 | |
| R2→EN | 1 | R2「相手国との協議」→EN「talks with the other country」(単数化、範囲の縮小) | |
| 退行 | 4 | ①R0「湾岸諸国との貿易や投資」→R2「相手国との協議」(置換先の明確さが低下) ②R0「案を引っ込め…取引を増やす方向を選んだ」(置換として明快)→R2「発想そのものが移った」 ③R0に無い「大きな仕組み」 ④R2→EN「the other country」(単数) | R0の「たった一日で」「米国との関係を深める」はR0時点で既に台帳外/軽微 |
### (4) Checker・後段
- final_state: RESOLVED_REWRITE_THEN_DOWNGRADE / cycle数: 3 / blocking最終0
- Rewrite: 1件(cycle1, narrow_scope, e1_minimal_word_edit)。before「One is to charge cargo directly.」→after「One is to propose a charge on cargo.」
- 誤許容(自分が誤りとした文がACCEPTABLE/QUALITY扱い): ①「In other words, the plan was to have all cargo passing through the strait share the cost at the same rate.」②「…it would have been a large system covering every piece of cargo that passed through.」③「It is that the very idea of collecting a fee moved to a different setting.」(QUALITY) ④「Even when the issue is about providing security, there are two ways in.」(QUALITY) ⑤「The other is to use talks with the other country to lead to trade and investment.」(3サイクルACCEPTABLE) ⑥「A planned cargo fee in the Strait of Hormuz became trade and investment talks the next day.」(cycle3で「talksの混同の可能性」と自ら指摘しつつACCEPTABLE) → 6件。
- must_fix・retry: BLOCKING 1件(rewrite済み)、retryなし。
- 最終記事に残った問題: 上記①〜⑥と時系列「one day」。(1)の件数で言えば残存7(主体1/対象1/範囲1/時系列1/因果1/追加2)。同じ主体問題(支払義務者)でもrep2ではBLOCKINGになっておりChecker判定が不安定。

---
## B. P2 rep2 (hormuz/nb/p2/rep2)
### (1) Fact整合
| 区分 | 件数 | 該当文 | 根拠 |
|---|---|---|---|
| 主体(支払義務者等) | 3 | ①JA R2「船が通るたびに、アメリカの安全対策費を払う。」/EN b1b「Every time a ship passed, it would pay for U.S. security measures.」(船が通過ごとに支払う。Checker BLOCKING→rewrite済み。JA R2に残存) ②JA R2「アメリカが海峡の安全を確保するために使う費用を、通過する貨物に負担してもらう考えです。」/EN b1b「The idea was to have passing cargo pay for the costs…」(貨物が支払う。BLOCKING→rewrite済み。JA R2に残存) ③JA R2「通行する貨物に直接料金をかける話が、湾岸諸国との商談に変わったわけです。」/EN「A plan to charge passing cargo directly had turned into business talks with the Gulf states.」(最終ENに残存。Checker=ACCEPTABLE) | HF-003: 支払義務者・徴収方法は未提示 |
| 対象 | 1 | JA R2題名「料金所を開くはずが、翌日には商談会になった」/EN「…the Next Day It Became a Business Meeting」、「business talks with the Gulf states」 | 置換先は「貿易・投資案件」、「商談/talks」は理由側の語。rep1と同型の言い換え(本文の明示文は「replaced by trade and investment deals」で正確) |
| 範囲 | 1 | EN one-liner「…but oil prices stayed high because the strait remained dangerous.」/EN「Why did oil prices not fall much…」 | 台帳はBrent先物(約+2.6%)。ENは「oil prices」一般へ拡張(CheckerもQUALITY指摘) |
| 時系列 | 1(軽微) | JA R2「その料金表は一日で姿を消し」/EN「that fee schedule disappeared in one day」「vanished within a day」 | 台帳は約24時間48分後(題名の「翌日」は正しい。「within a day」は不正確。CheckerはQUALITY扱いで残存) |
| 否定 | 0 | - | - |
| 因果 | 2 | ①JA R2「海峡の危険そのものが、消えたわけではないからです。」/EN「Because the danger itself in the strait had not disappeared.」+one-liner「…oil prices stayed high because the strait remained dangerous.」(価格高止まりの原因を断定) ②JA R2「だから市場も、…海峡の現実を思い出したように、高い水準へ戻ったのです。」/EN「So after reacting a little to the withdrawal of the fee plan, the market seemed to remember the reality of the strait and returned to a high level.」 | HF-009: 台帳は一時縮小→回復と、撤回以外に攻撃・封鎖・タンカー懸念が継続していた、という並置まで(causal_strengthはソース記述として許容されるが「市場が思い出した」は台帳外) |
| 追加 | 2 | ①JA R2「かなり大きな料金所です。」/EN「It would be quite a large toll booth.」(制度規模) ②JA R2「第三幕で原油市場が見せた反応は、もっと冷静でした。」/EN「…the reaction from the oil market was much calmer.」(比較評価) | 台帳なし |
### (2) ★fact
| fact_id | 該当段落(全文) | 判定 | 理由 |
|---|---|---|---|
| HF-007 | JA R2「トランプ氏は、20パーセントの償還料案を、湾岸諸国によるアメリカ向けの貿易と投資の案件に置き換えると発表しました。中東の指導者との「非常に生産的な協議」を踏まえた決定だと説明しています。」/EN「Trump announced that the 20 percent fee plan would be replaced by trade and investment deals between the Gulf states and the United States. He explained that the decision was based on “very productive talks” with Middle Eastern leaders.」 | 正しい | 置換先(案件)と理由(協議)を区別して正確。後段で「商談/business talks」へ言い換えるが、上記の明示文が優先 |
| HF-009 | JA R2「発表の後、ブレント先物は一時的に上げ幅を縮めました。ところが、ほどなくして発表前に近い高い水準へ戻りました。記事が出た時点では、およそ2.6パーセント高く、1バレル85ドルを上回っていました。」/EN「After the announcement, Brent futures temporarily gave back some of their gains. But soon they returned to a high level close to where they had been before the announcement. When the article was published, they were up about 2.6 percent and above 85 dollars a barrel.」 | 正しい | 数値・時点・方向が台帳と一致し、「全面下落」とも書いていない。直後の因果(上記因果①②)は別途誤許容としてカウント |
### (3) JA→EN意味変化
| 区分 | 件数 | 該当文(R0 / R2 / EN) | 備考 |
|---|---|---|---|
| R0→R2 | 3 | ①R0「貨物にその場で料金をかける方法」→R2「船が通るたびに…払う」→EN b1b「Every time a ship passed, it would pay…」 ②R0に無し→R2「かなり大きな料金所です」→EN「quite a large toll booth」 ③R0に無し→R2「第三幕で…もっと冷静でした」→EN「much calmer」 | |
| R2→EN | 1 | R2に無し→EN one-liner「Trump’s proposed Hormuz toll vanished within a day, but oil prices stayed high because the strait remained dangerous.」(「toll」「oil prices」「within a day」「because」の追加) | |
| 退行 | 4 | ①R0「貨物にその場で料金」→R2「船が通るたびに…払う」(支払主体・徴収方式の具体化) ②R0に無い「かなり大きな料金所」 ③R0に無い「もっと冷静」 ④EN one-liner(oil prices全般化・断定的因果・within a day) | R0の市場段落(一時縮小→回復、2.6%、85ドル超)はR2/ENで保持 |
### (4) Checker・後段
- final_state: RESOLVED_REWRITE_THEN_DOWNGRADE / cycle数: 2 / blocking最終0
- Rewrite: 2件+1件は同サイクル内で他のrewriteに吸収。①before「Imagine a toll booth suddenly appearing in the strait. Every time a ship passed, it would pay for U.S. security measures. It would be quite a large toll booth.」→after「…The proposal would seek reimbursement for U.S. security costs on all cargo passing through the strait. It would be quite a large toll booth.」②before「The idea was to have passing cargo pay for the costs the United States would use to keep the strait safe.」→after「The idea was to have a 20 percent fee on all passing cargo cover the costs the United States would use to keep the strait safe.」
- 誤許容: 「A plan to charge passing cargo directly had turned into business talks with the Gulf states.」(主体③)、「Because the danger itself in the strait had not disappeared.」(因果①)、「So after reacting a little to the withdrawal of the fee plan, the market seemed to remember the reality of the strait…」(因果②)、「But in the third act, the reaction from the oil market was much calmer.」(QUALITY、追加②)、one-liner「Trump’s proposed Hormuz toll vanished within a day, but oil prices stayed high because the strait remained dangerous.」(QUALITY→cycle2はACCEPTABLE、範囲・時系列・因果) → 5件(「Diplomatic announcements can change completely in one day」「tankers … do not become safe just because of an announcement」の一般論はCheckerもACCEPTABLEとしたが私は事実誤りには数えず備考扱い)。
- must_fix・retry: BLOCKING 3件(cycle1、ship/cargo payer、すべてrewrite済み)、retryなし。
- 最終記事に残った問題: 主体③・対象・範囲・時系列・因果2・追加2=8(Checker解消済みのship/cargo payerは含まない)。
- 備考: 台帳外の一般論(外交発表は一日で完全に変わり得る/危険海域のタンカーは発表だけでは安全にならない)が複数残る(評価・解釈として扱う)。

---
## C. 従来版 Control rep1 (polysemy_trial_04 / hormuz/control/rep1)  brief: HF-002/007/009相当の統合(個別fact ID無し)
### (1) Fact整合
| 区分 | 件数 | 該当文 | 根拠 |
|---|---|---|---|
| 主体/対象/否定/時系列 | 0 | - | 「誰が誰に支払うのか…示されませんでした」と明示してHF-003を保持。「約24時間48分後」「just over a day」で時系列も正確。置換先は"trade and investment deals involving the Gulf countries and the United States"で正確 |
| 範囲 | 1(軽微) | JA R2「記事の時点では二点六パーセント高の一バレル八十五ドル超」/EN「When this article was written, they were up 2.6 percent, at more than 85 dollars a barrel.」 | 台帳「約2.6%」の「約」が脱落(R0時点から) |
| 因果 | 1(軽微) | JA R2「この動きから分かるのは、料金案の置き換えだけで、供給への心配が消えたわけではないということです。」/EN「This movement shows that replacing the fee plan alone did not remove worries about supplies.」 | 台帳は撤回以外の懸念が継続していたという並置。価格から「懸念が消えなかった」と読み取る推論(rep2の因果①②より弱い) |
| 追加 | 0 | - | 一般論「Political words may change direction suddenly, but tension at sea does not always change at the same speed.」(Checker=ACCEPTABLE)は備考扱い |
### (2) ★fact
| fact_id | 該当段落(全文) | 判定 | 理由 |
|---|---|---|---|
| HF-007 | JA R2「そして、およそ二十四時間四十八分後の七月十四日午前十一時四分。トランプ氏は、その二割の償還料を、湾岸諸国による対米貿易や投資の案件に置き換えると投稿しました。理由として挙げたのは、中東の指導者たちとの「非常に生産的な協議」です。」/EN「Then, about 24 hours and 48 minutes later, at 11:04 a.m. on July 14, Mr. Trump posted that the 20 percent reimbursement fee would be replaced with trade and investment deals involving the Gulf countries and the United States. The reason he gave was “very productive talks” with leaders in the Middle East.」 | 正しい | 時刻・間隔・置換先・理由を分離して正確 |
| HF-008 | JA R2「さらに記者団には、ホルムズ海峡を通る船に誰も料金を課すべきではなく、料金という考え方自体を好まないとも述べました。」/EN「He also told reporters that no one should charge ships passing through the Strait of Hormuz, and that he did not like the idea of charging a fee at all.」 | 正しい | 台帳どおり(負担の不公平主張の併記は無いが誤りではない) |
| HF-009 | JA R2「ブレント原油先物は上げ幅をいったん縮めました。しかし、ほどなく発表前に近い高い水準へ戻り、記事の時点では二点六パーセント高の一バレル八十五ドル超でした。」/EN「Brent crude oil futures temporarily gave up some of their gains. But soon they returned to a high level close to where they had been before the announcement. When this article was written, they were up 2.6 percent, at more than 85 dollars a barrel.」 | 正しい | 方向・水準・時点を台帳どおり保持 |
### (3) JA→EN意味変化
| 区分 | 件数 | 該当文 | 備考 |
|---|---|---|---|
| R0→R2 | 1 | R0「料金案が消えても、原油価格は大きく下がりませんでした。理由は、値段を押し上げていた心配が、料金案だけではなかったからです」→R2「料金案の置き換えだけで、供給への心配が消えたわけではない」 | R2の方が断定が弱く改善 |
| R2→EN | 0 | - | 置換先は"involving"と穏当に訳出 |
| 退行 | 0 | - | R0・R2・ENとも台帳整合を維持 |
### (4) Checker・後段
- final_state: RESOLVED_STAGE2_DOWNGRADE / cycle数: 1 / blocking 0 / Rewriteなし
- ACCEPTABLE指摘は1件(一般論「Political words may change…」)のみ。自分が誤りとしたもの(「約」脱落・「This movement shows…」)はCheckerが拾っていない(誤許容=0、未指摘2)。
- 残存: 範囲1+因果1=2(いずれも軽微)。

---
## テーマ差(P2版 vs 従来版 / 断定しない)
- Fact整合合計: P2 rep1=8、P2 rep2=10、Control=2。P2両repで「支払義務者・徴収方式の具体化(HF-003違反)」と「置換先=協議(talks/商談)への言い換え」が出ており、Controlは「誰が誰に支払うのか示されなかった」と明示してこれを回避している。時系列も、P2は「一日で/within a day」、Controlは「約24時間48分/just over a day」。ただしこの差はNote(多義語)由来かrun揺れ(P2版はいずれも比喩的な構成で、Control版は事実列挙型)かは、n=2/1では切り分けられない。
- ★fact: HF-007はrep1=曖昧、rep2/Control=正しい。HF-009はrep2/Controlとも正しい(因果の後段付けはrep2のみ)。退行件数はP2 rep1=4、rep2=4、Control=0。Checker挙動: 同種の支払義務者問題をrep1はACCEPTABLEで通し、rep2はBLOCKING→rewriteと判定が割れた。誤許容はrep1=6、rep2=5、Control=0。
