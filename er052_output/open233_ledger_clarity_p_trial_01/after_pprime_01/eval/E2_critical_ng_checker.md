# E2 真の重大NG+Checker副作用 評価(OPEN-233-LEDGER-CLARITY-P-TRIAL-01、¥0、read-only)
ラベルは labeling_guide_01.md 基準の単独Sonnet推測(label_source=sonnet_guess、confirmed_by空)。最終判定はFable。比較は meta 1テーマ・After 1 run(n=1)で統計的結論ではない。AfterとBeforeはResearcher台帳から再生成のため別素材(台帳ID MMHC- vs MUSE-HC-)。

## 1 HC-012 Rollback型 3値ラベル(After)
After台帳 MMHC-007 は「ロールバックした」(notes: 原語=rolled back this feature、当面/for now)。方向の解消ではなく原語維持。
| 段 | 該当文(逐語) | ラベル |
|---|---|---|
| 台帳 MMHC-007 | human concierge機能を当面ロールバックしたと社内投稿で述べた | 曖昧(片仮名) |
| B3 brief | 適切な開示なしに始めたとして機能を当面ロールバックした | 曖昧(片仮名) |
| JA R0 | Metaの副社長は、その点を問題として認め、機能を当面ロールバックした。 | 曖昧(片仮名) |
| JA R2 | Metaの副社長は、human concierge機能を当面ロールバックしたと説明した。 | 曖昧(片仮名) |
| EN b1b | Meta's vice president explained that the company had temporarily rolled back the human concierge feature. | 曖昧(原語維持) |
- 復元型(重大)=0段。Before(00c): R0で「以前の状態に戻しました」、EN b1b "restored ... to the way it had been before"(誤)。5 run中復元型3/5、重大(Y)1/5。
- EN判定: guide 1-1「Ledgerと整合」=問題なし(Y/N: N)。"rolled back a feature"は英語で通常「撤回/元に戻す」の意で読まれ、台帳原語そのもの。Before neg2(changed back to how it was before)をG-06曖昧型=Nとした扱いとも整合。ただし方向は台帳側でも未解消のため「予防成功」ではなく「誤訳を誘発しなかった」。次回別runで再び復元型に訳される可能性はn=1では否定できない。
- Checker: 同文は決定論(negation_polarity_mismatch)で候補化→LLM/S1二次とも ACCEPTABLE。Beforeと同経路で、今回は正しい判定。

## 2 After EN記事 全文走査(重大Y=0、軽微N=5、問題なし=他)
重大(Y)=0件。軽微5件(いずれも true_critical=N):
1. S3.3 "It handed requests received by Muse to human contractors." MMHC-001/004: 「一部の電話」が依頼全般に読める範囲拡張(a-c: c範囲)。
2. S4.1 "when you ask AI to make a call, the baton is passed to a human partway through." MMHC-001/004: 一部→一般化+「partway through(途中)」は台帳(Museが引渡し→人間が発信)に無い機構的含み。境界(後述gold B4-a近縁、ただし「AI単独で困った時」の発動条件なし→gold非該当)。Fable確認推奨。
3. S6.1 "what was meant to add a fast runner also meant carrying some unexpected baggage." 比喩だが「速い走者を加える意図」は台帳(MMHC-009: 目的=フィードバック収集)に無い動機の暗示。(b)軽微。
4. S8.1 "What Meta admitted was a problem..." MMHC-007: 主体 VP→Meta社(c)。直後S8.2で副社長を明記し緩和。
5. In one line "...handed some calls to human contractors, raising privacy concerns despite their higher success rates." MMHC-008: 「some tests」限定が落ち、社内テスト限定も欠落(c範囲)。
問題なし(主要): S1.3(internal tests, some calls)、S2.2/2.3(米国事業者・予約/在庫/見積もり)、S2.4 "takes care of bothersome calls for you."(一般的修辞、具体Factなし)、S3.2/3.4、S5.2 95%〜98%(some tests/人間発信限定を保持)、S5.3、S6.2(従業員の懸念、確定事実でない旨を保持)、S7.2 "no confirmation ... wide scale"、S7.3(one employee reported、台帳notesと整合)、S8.2(rolled back)、結語・タイトル(修辞)。数値・日付・固有名の新規追加なし(b該当0)。
gold相当誤り(全て不出現): A4-0 "completed the exchanges with users"=無/B4-a "take over when AI alone has trouble"=無(S4.1が近縁・非該当)/Meta-1・2 "needed user information to continue"=無(S6.2は「通話中の機微情報」でMMHC-005に忠実)/A5-0 "temporarily put back the feature"=無/A4-1 "actually speaking with human staff"=無。
Before比: Before記事の新規事実追加(HC-006/HC-012周辺「ユーザーが気づかず人間が応対」「知る手段がなかった」等)がAfter記事では出ていない=改善寄り。ただしn=1。

## 3 JA段の走査(台帳基準、重大=0)
- R0: 重大0。軽微3: (i)「Museへの依頼を人間の請負業者へ引き渡す」(一部→全般)、(ii)「誰が電話しているのかをきちんと伝えないままテストが始まった」(台帳は「適切な開示なし」のみ、開示内容を「誰が電話か」に特定する新事実)、(iii)見出し「人間が出てきた」・「Museに電話を任せる利用者」(社内従業員テスト→利用者一般への含み)。
- R2: 重大0。R0の(ii)は本文から消え「適切な開示なしに始めた」と台帳に忠実化(改善)。一方「AIに電話を頼んだら、途中で人間にバトンが渡る」(S4.1の由来、R2で新規導入)と「速い走者を加えたつもりが」(S6.1の由来)はR2で新規に入った軽微。(i)は継続。
- 追跡: ロールバック方向の誤読はJA段で発生せず(Beforeは発生)、EN段へ原語のまま伝播。ENで消えた軽微=R0(ii)・(iii)(R2→b1b)。ENに残った軽微=R2由来の4件(S3.3/S4.1/S6.1/S8.1相当)。EN段で新規発生した軽微=In one lineの限定落ち。

## 4 Checker副作用(meta_run03_advanced、After vs Before、同一構成)
| 項目 | After | Before(e2e_02) |
|---|---|---|
| final_state / cycles / Rewrite / human_review | RESOLVED_STAGE2_DOWNGRADE / 1 / 0 / 0 | 同左 |
| Stage1候補(union) | 8(model6+決定論のみ2) | 5(model4+決定論のみ1) |
| Stage2対象 | 12 | 8 |
| blocking / non-blocking | 0 / 12 | 0 / 8 |
| floor_reason | 全件null | 全件null |
| S1 second: confirmed_downgrade | 12/12(ACC→ACC 10, QUALITY→QUALITY 1, ACC→QUALITY 1) | 8/8(ACC→ACC 6, ACC→Q 1, Q→ACC 1) |
| 最終 QUALITY | 2(S4.1、S1.3) | 2 |
| 費用(円) / 呼出 | 2.54 / 7 | 2.41 / 7 |
Afterのnon-blocking 12件(文→理由→結末。全て S1二次で降格確認):
1 S2.4 takes care of bothersome calls: 一般化(scope/unsupported)で候補→ACC(修辞、不要)
2 S3.1 Muse not the only one: 決定論negation_polarity_mismatch→ACC(不要・誤爆)
3 S3.3 handed requests...: scope拡張→ACC(軽微相当、妥当)
4 S4.1 baton passed partway: scope/因果→QUALITY(妥当、軽微と一致)
5 S6.1 fast runner baggage: 因果比喩→ACC(軽微、降格は許容範囲)
6 S8.2 rolled back: 決定論negation_polarity_mismatch→ACC(忠実、不要だがBeforeと同経路)
7 S8.1 What Meta admitted: actor→ACC(軽微、降格)
8 In one line: scope→ACC(軽微、降格)
9 S3.2 testing human concierge: 決定論系の関連付けでMMHC-007に誤紐付け→ACC(不要)
10 S5.2 95%to98%: 同上MMHC-007誤紐付け→ACC(不要)
11 S1.3 internal tests: MMHC-007へ誤紐付け(changed_actor誤指摘)→最終QUALITY(不要NGが非ACCEPTABLEで残存、副作用1件)
12 S6.2 concerns shared: changed_actor誤指摘(MMHC-007誤紐付け)→ACC(不要)
不要NG(私のラベルで「問題なし」なのに候補化): After 7/12(S2.4, S3.1, S8.2, S3.2, S5.2, S1.3, S6.2、うち最終非ACCEPTABLE=1)、Before 4/8(Beforeラベルも私の推測、真重大Yの復元文は候補化済で見逃し)。絶対数は+3だが総候補が12 vs 8で比率は58% vs 50%。いずれもS1二次でACCEPTABLEへ降格済で、Rewrite・human_reviewへの波及0。
所見の観点: 新台帳でMMHC-007が長文化(「ミス」「適切な開示なし」「ロールバック」を1 claimに集約)し、MMHC-007にS3.2/S5.2/S1.3/S6.2など無関係文が紐付いた(changed_actor誤指摘は「副社長」と「Meta」の混同由来、4文)=claim長文化がfact紐付け側に出た副作用の可能性(因果は未検証、再現はn=1)。notes短縮による「台帳一致」判定の悪化は確認されず(基準:全て降格または妥当QUALITY)。

## 5 総合所見(最終判定はFable)
- ③真の重大NG: HC-012復元型は新台帳・After記事で非発生(Beforeは3/5 run発生、重大1/5)。Rollback以外のgold相当・新規重大も出ていない。悪化なし(改善寄り、n=1)。
- ①Checker副作用: 最終状態・Rewrite・human_review・floor・費用は変化なし。候補/不要候補が増加(8 vs 5、不要7 vs 4)。MMHC-007への誤紐付け型の不要候補が4件新規。害は軽い(全件降格)が「不要NG増加」の兆候として要注視。
- 注意: 本評価はCheckerの出力を承認根拠として使っていない。ラベルは推測・未確認。ロールバックの方向自体は台帳側で未解消(片仮名のまま)。
