# E_meta 評価シート(OPEN-233-META-ALLFACT-NOTE-E2E-TRIAL-02 / 委任_C1 / 2026-10-07 / 評価者: Sonnet)
方針: Fact整合は台帳(P2版=Control版とfact本文同一)を直接照合し、Checker結果は後から参照。AI面白さ採点なし。件数=判定した問題の件数(軽微含む)。
EN本文は b1b/article.md(Checker前)と Checker rewrite後(checker jsonのen_text_after_rewrite)の差を明記。評価の主対象は「最終EN(rewrite後)+JA R2」。
Meta ★fact: MUSE-HC-012(ロールバック=人間コンシェルジュ機能のみ)、MUSE-HC-014(公開展開条件)。今回のbriefでHC-012は全3記事に含まれ、HC-014はP2 rep2のみ。
台帳の重要限定: HC-006「一部の電話」「テスト」、HC-010「懸念の存在・漏えいと断定しない」、HC-012「適切な開示なしに契約スタッフが電話をかけるテストを開始→ミス→当面ロールバック。サービス全体停止ではない」。**台帳は「誰に対して開示しなかったか」を明記していない。**

---
## A. P2 rep1 (meta/nb/p2/rep1)  brief: HC-006, HC-010, HC-012
### (1) Fact整合
| 区分 | 件数 | 該当文 | 根拠 |
|---|---|---|---|
| 主体 | 0 | - | - |
| 対象 | 0 | - | - |
| 範囲 | 0 | - | 一部の電話/テスト/機能のみ、を明記しており台帳に整合 |
| 時系列 | 0 | - | - |
| 否定 | 0 | - | 「ミューズ全体が止まったわけではない」「すべての電話を人間が担当したわけでもありません」は台帳notesに整合 |
| 因果 | 1(軽微) | EN one-liner「Meta’s AI calling test sometimes relied on undisclosed human contractors, raising privacy concerns for users.」 | HC-010は従業員の懸念(情報共有の可能性)で、開示不足が懸念を生んだとは台帳にない。"raising"で結んでいる |
| 台帳にない具体的事実の追加 | 4 | (a) JA R2「AIが仕事を受け取り、困ったところは人間のプロがさっと解決する。そんな華やかな舞台裏にも見えます。」/EN(Checker前)「AI takes the request, and a human professional quickly solves anything difficult.」(ENはCheckerがrewrite済み。JA R2には残存) (b) JA R2「つまり、AIにお願いしたはずの電話に、人間の助っ人が登場していたわけです。」/EN「In other words, a human helper had appeared in a call that users thought they had asked AI to make.」(利用者の認識) (c) JA R2「AIの画面を見ているつもりが、その先で人間が仕事をしている。」/EN「You may think you are looking at an AI screen, while a human is doing the work on the other side.」(画面・ユーザー体験) (d) JA R2「問題は、そうした可能性があるのに、利用者へ十分な説明がないままテストが始まったことでした。」/EN「The problem was that, even though this possibility existed, the test began without enough explanation for users.」(開示対象を「利用者」と特定) | (a)役割分担・難案件のみ引継ぎ・迅速性は台帳なし。(b)(c)ユーザー認識/UIは台帳なし。(d)開示対象は台帳に記載なし(rep2では対象が「電話の相手」とされており、両版で食い違う=どちらも台帳外) |
### (2) ★fact
| fact_id | 該当段落(全文) | 判定 | 理由 |
|---|---|---|---|
| MUSE-HC-012 | JA R2「メタの担当副社長は、契約スタッフが電話をかけるテストを適切な開示なしに始めたことを「ミス」だったと、社内への投稿で認めました。そして、人間コンシェルジュ機能は当面、元の状態に戻されました。 … ここで大切なのは、ミューズ全体が止まったわけではないという点です。元に戻されたのは、あくまで人間コンシェルジュの機能です。また、すべての電話を人間が担当したわけでもありません。対象はテスト中の一部の電話でした。」/EN「In an internal post, Meta’s vice president in charge admitted that starting a test in which contract workers made calls, without proper disclosure, was a “mistake.” The Human Concierge feature was then returned to its original state for the time being. The important point here is that Muse as a whole was not stopped. Only the Human Concierge feature was returned to its original state. Also, humans did not handle every call. It was only some of the calls in the test.」 | 正しい | 認めた主体・「ミス」・当面・対象=人間コンシェルジュ機能のみ・サービス全体停止でない、すべて台帳と一致。「元の状態に戻す」は文脈上ロールバックと読め、ここでは重大にしない |
### (3) JA→EN意味変化
| 区分 | 件数 | 該当文(R0 / R2 / EN) | 備考 |
|---|---|---|---|
| R0→R2 | 3 | ①R0「困ったときに人が助けてくれる、親切なサービスに見えます」→R2「AIが仕事を受け取り、困ったところは人間のプロがさっと解決する」→EN同旨(Checker後は削除) ②R0に無し→R2「AIの画面を見ているつもりが、その先で人間が仕事をしている」→EN「You may think you are looking at an AI screen…」 ③R0「メタの人工知能研究部門の副社長」→R2「メタの担当副社長」→EN「Meta’s vice president in charge」 | ③は部門名を落としただけ(台帳はSuperintelligence Labs部門。R0の「人工知能研究部門」より中立) |
| R2→EN | 1 | R2「AIにお願いしたはずの電話」→EN「a call that users thought they had asked AI to make」 | 「はず」(推定)が「users thought」(利用者の認識の断定)へ強化 |
| 退行 | 3 | (a)印象表現→具体的役割分担(R2「人間のプロがさっと解決する」) (b)R2新規「AIの画面を見ているつもり」 (c)R2→EN「users thought」 | R0で正しかった表現そのものの誤変換ではなく、R0に無かった/弱かった台帳外要素がR2/ENで増えた。R0の「一部の電話」「大規模漏えい確認なし」はR2/ENで保持 |
### (4) Checker・後段
- final_state: RESOLVED_REWRITE_THEN_DOWNGRADE / cycle数: 2 / blocking最終0
- Rewrite: 1件(cycle1, narrow_scope, e2_generic_rewrite)。before「The name alone makes it sound very dependable. AI takes the request, and a human professional quickly solves anything difficult. That is what this polished system seemed to be like behind the scenes.」→after「The name alone makes it sound very dependable. Some calls were handled by trained human contractors. That is what this polished system seemed to be like behind the scenes.」(JA R2側は未修正で食い違いが残る。書き換え後の「That is what…」は指示対象が曖昧)
- 誤許容(ACCEPTABLE扱いだが自分が誤りとした文): 「In other words, a human helper had appeared in a call that users thought they had asked AI to make.」((1)(b))、「You may think you are looking at an AI screen, while a human is doing the work on the other side.」((1)(c)) → 2件。他のACCEPTABLEは決定論検査(negation_polarity_mismatch)の差戻しで、内容は台帳と一致し妥当。
- must_fix・retry: BLOCKING 1件(上記rewrite)、retryなし。
- 最終記事に残った問題(Checker未指摘含む): (b)(c)(d)とone-linerの因果(軽微)=4。(a)はENでは解消、JA R2には残存。

---
## B. P2 rep2 (meta/nb/p2/rep2)  brief: HC-006, HC-012, HC-014
### (1) Fact整合
| 区分 | 件数 | 該当文 | 根拠 |
|---|---|---|---|
| 主体 | 1 | JA R2「電話の相手はAIか、それとも人間か。今回の答えは、少なくとも一部では人間でした。」/EN「Was the person on the other end of the call an AI or a human? This time, at least in some cases, it was a human.」 | 人間だったのは「電話をかける側(契約スタッフ)」。ENの"the other end"は通常「電話を受けた側(事業者)」と読め、立場が逆に読める(Checkerもcycle3でQUALITY指摘したがblockingにせず) |
| 対象 | 1 | JA R2「ただし、主役になった人間が知らされていなかった。」/EN b1b「But the humans who ended up in the main role had not been told.」→Checker rewrite後「But the humans who ended up on the other end had not been properly told.」 | 台帳は「適切な開示なしにテストを開始」とだけ。契約スタッフ本人が知らされていなかったとは言っていない(元文は対象の取り違え)。rewrite後は「電話の相手側の人間」へ変わったが、これも台帳に根拠なし |
| 範囲 | 0 | - | 「一部の電話」「テスト」「電話機能全体を止めたわけではない」は台帳notes整合 |
| 時系列 | 0 | - | - |
| 否定 | 0 | - | - |
| 因果 | 2 | ①JA R2「Metaはその説明を忘れて、いったん舞台の幕を下ろしたわけです。」/EN「Meta forgot to give that explanation and, for now, brought the curtain down on the stage.」(「忘れた」=原因・意図の断定) ②EN one-liner「Meta’s AI phone test used undisclosed human callers, so the company temporarily rolled back the feature.」(「so」=開示不足→ロールバックの因果。軽微) | 台帳は「ミスだったと認め、ロールバック」まで |
| 追加 | 3 | (a)JA R2「AIが電話をかけてくれると思ったら、舞台裏では人間のスタッフが登場する。」/EN「You think AI is making the call, but behind the scenes, a human staff member appears.」(利用者の認識) (b)JA R2「ややこしい話なら、人間が対応したほうが自然に進むこともあります。」/EN「If the matter is complicated, things may go more smoothly if a human handles it.」(性能・比較) (c)JA R2「問題は、その事実を相手に十分知らせないまま、テストを始めたことでした。」/EN「The problem was that the test began without properly telling the person on the other end about this fact.」(開示対象=電話の相手。rep1は「利用者」) | 台帳なし |
### (2) ★fact
| fact_id | 該当段落(全文) | 判定 | 理由 |
|---|---|---|---|
| MUSE-HC-012 | JA R2「Metaの部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを始めたことを「ミス」だったと認めました。そして、人間コンシェルジュ機能をいったん元に戻しました。 … ここで間違えてはいけないのは、電話機能のサービス全体を止めたわけではないという点です。ロールバックされたのは、人間が電話をかけるこの機能です。」/EN「The vice president of a Meta division admitted that starting a test in which contract workers made calls without proper disclosure was a “mistake.” Meta then temporarily rolled back the human concierge feature. What we must not get wrong here is that Meta did not stop the phone service as a whole. What was rolled back was this feature in which humans made the calls.」 | 正しい | 主体・ミス・当面のロールバック・対象限定を保持。ENは"rolled back"と明示しrep1より明確 |
| MUSE-HC-014 | JA R2「Metaは、電話の相手となる事業者との改善を続け、準備が整い、適切な説明ができる場合にだけ、広く公開するとしています。」/EN「Meta says it will continue working to improve the service with the businesses it calls, and will make it widely available only when it is ready and can explain it properly.」 | 曖昧 | 条件(準備完了・適切な開示)は保持。ただし「公開」の対象が電話機能全体か人間コンシェルジュ機能かが文中で不明(ロールバック対象を述べた直後の文で"it"と書く)。台帳notesの「公開済みの一般機能とロールバック対象を区別する」を満たしていない。誤読を断定できる水準ではないため重大にしない |
### (3) JA→EN意味変化
| 区分 | 件数 | 該当文(R0 / R2 / EN) | 備考 |
|---|---|---|---|
| R0→R2 | 3 | ①R0「AIの電話だと思ったら、話していたのは人間だった」→R2「電話の相手はAIか、それとも人間か。今回の答えは、少なくとも一部では人間でした。」→EN同旨(立場の曖昧さはJAにもあるが、ENで"other end"としより明確に) ②R0に無し→R2「ただし、主役になった人間が知らされていなかった。」→EN同旨 ③R0「ひとことの説明でした。Metaは今回、人間を使ったことではなく、人間が対応していると適切に開示しなかったことを問題にしたわけです」→R2「Metaはその説明を忘れて、いったん舞台の幕を下ろしたわけです」 | |
| R2→EN | 2 | R2「電話の相手はAIか、それとも人間か」→EN「the person on the other end of the call」(callee読みが強まる) / R2に無し→EN one-liner「so the company temporarily rolled back the feature」 | |
| 退行 | 3 | R0で正しかった「(Metaは)適切に開示しなかったことを問題にした」→R2「主役になった人間が知らされていなかった」(対象取り違え) / R0「ひとことの説明でした」→R2「説明を忘れて」(原因断定) / R0「Metaの社内向け説明によると」(出典帰属)がR2/ENで脱落 | 3点目は軽微 |
### (4) Checker・後段
- final_state: RESOLVED_REWRITE_THEN_DOWNGRADE / cycle数: 3 / blocking最終0
- Rewrite: 1件(cycle1, narrow_scope, e1_minimal_word_edit)。before「But the humans who ended up in the main role had not been told. That was the problem.」→after「But the humans who ended up on the other end had not been properly told. That was the problem.」(対象を電話の相手側へ置換しただけで、台帳根拠のない開示対象の特定は残存)
- 誤許容(ACCEPTABLE/QUALITY扱いだが自分が誤りとした文): 「You think AI is making the call, but behind the scenes, a human staff member appears.」(追加a)、「If the matter is complicated, things may go more smoothly if a human handles it.」(追加b)、「Meta forgot to give that explanation and, for now, brought the curtain down on the stage.」(因果①)、「Meta’s AI phone test used undisclosed human callers, so the company temporarily rolled back the feature.」(因果②)、「But the humans who ended up on the other end had not been properly told.」(対象。cycle3でACCEPTABLE)、「This time, at least in some cases, it was a human.」(主体。QUALITY) → 6件。
- must_fix・retry: BLOCKING 1件(rewrite済み)、retryなし。
- 最終記事に残った問題(Checker未指摘含む): 上記6件に加え、追加(c)「the person on the other end」(開示対象)、HC-014「公開」対象の曖昧。残存合計8(主体1/対象1/因果2/追加3/★曖昧1)。

---
## C. 従来版 Control rep1 (polysemy_trial_04 / meta/control/rep1)  brief: 個別fact ID無しの統合1段落(HC-004/006/010/012相当)
### (1) Fact整合
| 区分 | 件数 | 該当文 | 根拠 |
|---|---|---|---|
| 主体 | 1(軽微) | JA R2「Metaの幹部は、この始め方を「ミス」だったと認めました。そして9月22日までに、人間コンシェルジュ機能をロールバックしました。」/EN「Meta executives admitted that this way of starting the test was a “mistake.” By September 22, they had rolled back the human concierge feature.」 | 台帳は副社長1名。複数形のexecutives/theyへ拡張(CheckerもQUALITY指摘、最終まで残存) |
| 対象/範囲/時系列/否定 | 0 | - | 9月22日までに、一部の電話、Muse全体は止めていない、すべて台帳整合 |
| 因果 | 2 | ①JA R2「Metaの従業員が心配したのは、まさにそこでした。」(直前の「利用者に十分伝わっていなければ観客は台本を見失う」へ従業員の懸念を結びつけ。ENはCheckerがBLOCKINGで削除済み) ②EN one-liner「…without clearly telling users, raising privacy concerns.」(軽微) | HC-010の懸念は情報共有の可能性。開示不足への懸念ではない |
| 追加 | 1 | JA R2「その出演者が誰なのか、利用者に十分伝わっていなければ、観客は途中で台本を見失います。」/EN「if users are not told clearly enough who the performer is…」「the test … began without properly telling users about it.」(開示対象=利用者) | 台帳なし |
### (2) ★fact
| fact_id | 該当段落(全文) | 判定 | 理由 |
|---|---|---|---|
| MUSE-HC-012 | JA R2「Metaの幹部は、この始め方を「ミス」だったと認めました。そして9月22日までに、人間コンシェルジュ機能をロールバックしました。Museという作品そのものを上映中止にしたわけではありません。元に戻されたのは、人間スタッフが電話を担当する機能です。」/EN「Meta executives admitted that this way of starting the test was a “mistake.” By September 22, they had rolled back the human concierge feature. They did not stop Muse itself. What was rolled back was the feature in which human staff handled the phone calls.」 | 正しい | 日付・対象・全体停止でない点が正確。「幹部」複数形のみ軽微逸脱 |
### (3) JA→EN意味変化
| 区分 | 件数 | 該当文 | 備考 |
|---|---|---|---|
| R0→R2 | 1 | R0に無し→R2「Metaの従業員が心配したのは、まさにそこでした。」→ENはCheckerが削除 | R0は懸念(情報共有)と開示不足を分けて書いていた |
| R2→EN | 0 | (翻訳による変化なし。Checkerによる削除のみ) | |
| 退行 | 1 | R2「従業員が心配したのは、まさにそこ」(R0では正しく分離) | ENでは解消 |
### (4) Checker・後段
- final_state: RESOLVED_REWRITE_THEN_DOWNGRADE / cycle数: 2
- Rewrite: 1件(narrow_scope)。before「That was exactly what worried Meta employees. Sensitive information from users…」→after「(文頭の1文を削除)Sensitive information from users …」
- 誤許容: 「Meta executives admitted that this way of starting the test was a “mistake.”」(QUALITY、主体)、「Meta tested having human workers handle some AI phone calls without clearly telling users, raising privacy concerns.」(ACCEPTABLE、因果軽微) → 2件。
- 残存: 主体1/因果1/追加1=3(Checker未指摘は追加=開示対象「users」)。

---
## テーマ差(P2版 vs 従来版 / 断定しない)
- Fact整合合計: P2 rep1=5、P2 rep2=7、Control=4。P2版では台帳に無い「利用者/電話の相手の認識・開示対象」が両repで出ており(rep1は利用者、rep2は電話の相手と食い違う)、Controlでも開示対象「利用者」は出ている。rep2は主体(電話の相手)・対象(知らされていなかった人間)の取り違えが1件ずつありControlより多いが、n=2でありrun揺れとNote由来の切り分けはできない。
- ★fact: HC-012は3記事とも正しい。HC-014はrep2のみ曖昧(Controlのbriefには含まれず比較不能)。Checker誤許容はP2 rep1=2、rep2=6、Control=2。Noteの効果(多義語の解釈改善)がこの題材では確認できる差として現れていない。
