# NG_hormuz 工程別NG台帳(OPEN-233-E2E-STAGEWISE-NG-AUDIT-01 / 委任_A1 / 2026-10-07)

基準(全工程同一): 重大=事実の意味が変わり読者に誤解を与える(主体・対象の入れ替わり/方向・状態の逆転/台帳にない事実の断定で理解が変わる/否定の反転)。軽微=意味は逆転しないが不正確・過剰断定・対象範囲の曖昧さ・台帳未提示事項の軽い具体化。同一誤りは同一工程1件(JA/ENで同一IDを共有)。
工程: 1 JA最終稿(ja_writer/revision2.md) 2 EN Rewrite前(b1b/article.md) 3 EN Rewrite後(checker jsonの最終 en_text_after_rewrite。Rewriteなしは2と同一) 4 Checker最終cycle判定 5 独立評価(3+JAをE_*.mdで再ラベル)。
状態凡例: 発生/残存/修正済/該当なし(その工程に対応文が存在しない)。5はE_*.mdの既存評価を出発点に、本基準で再ラベルした結果。

## P2版 hormuz rep1  (er052_output/open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep1)

Checker: checker/runs/meta_run03_advanced.json (final_state=RESOLVED_REWRITE_THEN_DOWNGRADE, 3cycle)

### NG台帳

| NG ID | 重大度 | fact_id | 1 JA | 2 EN前 | 3 EN後 | 5 独立評価 | Checker(4) | Rewrite修正 | 内容(該当文) | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| hor-p2r1-01 | 軽微 | HF-003 | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE | なし | JA「言い換えると、海峡を通る荷物に、広く同じ割合で費用を負担してもらう案です。」/EN「In other words, the plan was to have all cargo passing through the strait share the cost at the same rate.」(費用負担者=貨物と特定) | HF-002は「すべての貨物への20%償還料」と述べるため貨物への賦課自体は台帳内。支払義務者の細部はHF-003で未提示=軽い具体化 |
| hor-p2r1-02 | 軽微 | HF-003 | 発生 | 発生 | 修正済 | 修正済 | BLOCKING(cycle1) | あり | JA「貨物に直接料金をかける方法と、…」/EN b1b「One is to charge cargo directly.」(徴収方法の特定) | 徴収方法はHF-003で未提示。ENは「propose a charge」に修正、JA R2には残存。Checkerは重大扱い |
| hor-p2r1-03 | 軽微 | HF-007 | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE(3サイクル。cycle3「A planned cargo fee…talks」もACCEPTABLE) | なし | JA題名「海峡の請求書が、翌日には商談になった」/「相手国との協議を通じて貿易や投資につなげる方法」/EN「become trade and investment talks the next day」「use talks with the other country to lead to trade and investment」(置換先を「協議」とし、協議→貿易投資の因果を示唆) | 台帳: 置換先は貿易・投資案件、協議は決定の理由。本文の明示文(HF-007)は正確なため軽微。E_hormuzの「対象」「因果」(talks)を統合 |
| hor-p2r1-04 | 軽微 | HF-007/HF-008 | 発生 | 発生 | 残存 | 残存 | QUALITY | なし | JA「料金を集めるという発想そのものが、別の舞台へ移ったことです。」/EN「It is that the very idea of collecting a fee moved to a different setting.」(料金案が形を変えて継続した、との示唆) | 直前に「撤回」と明示されており比喩的。HF-008(誰にも課すべきでない)と緊張するが、意味の逆転には至らず軽微 |
| hor-p2r1-05 | 軽微 | HF-007 | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE(03と同一文で指摘) | なし | JA「相手国との協議」/EN「talks with the other country」(台帳は湾岸諸国=複数。単数化) | JAは「相手国」、ENで単数が強化 |
| hor-p2r1-06 | 軽微 | HF-007 | 発生 | 発生 | 残存 | 残存 | 未検出 | なし | JA「今回の投稿は、その切り替えが一日で起きたことを示しました。」/EN「This post showed that the switch happened in one day.」(実際は約24時間48分後) |  |
| hor-p2r1-07 | 軽微 | HF-003 | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE | なし | JA「もし実施されれば、通る貨物すべてが対象になる大きな仕組みでした。」/EN「it would have been a large system covering every piece of cargo that passed through.」(制度規模) | 「すべての貨物」はHF-002内、「大きな仕組み」の評価は台帳外 |
| hor-p2r1-08 | 軽微 | HF-002/HF-007 | 発生 | 発生 | 残存 | 残存 | QUALITY(cycle1,3)/ACCEPTABLE(cycle2) | なし | JA「同じ安全確保をめぐる話でも、入り口は二つあります。」/EN「Even when the issue is about providing security, there are two ways in.」(貿易・投資案件を安全確保の別方式と位置付け) |  |

Rewrite履歴:
- cycle1 narrow_scope(e1_minimal_word_edit): 「One is to charge cargo directly.」→「One is to propose a charge on cargo.」

### 工程別集計

| 工程 | 重大 | 軽微 |
|---|---|---|
| 1 JA最終稿 | 0 | 8 |
| 2 EN Rewrite前 | 0 | 8 |
| 3 EN Rewrite後 | 0 | 7 |
| 4 Checker最終(blocking/non_blocking) | 0 | 7 |
| 5 独立評価(3対象) | 0 | 7 |

4詳細: cycle3 blocking=0 / non_blocking=7 (ACCEPTABLE5+QUALITY2)。non_blockingは正しい文へのACCEPTABLE指摘を多く含み、軽微NG件数とは同質でない。

### 遷移

| 遷移 | 重大 | 軽微 |
|---|---|---|
| 1->2 英語化で新規発生(JAに対応文なし) | 0 | 0 |
| 2->3 Rewriteで修正 | 0 | 1 |
| 2->3 Rewriteで新規発生 | 0 | 0 |
| 4->5 Checker見逃し(5で残存・4で非BLOCKINGまたは未検出) | 0 | 7 |

注: 1->2は「JA側に対応文が存在しない」ものだけを新規発生とした(JAに弱い形で既に存在しENで断定が強まったものは同一IDの強化として備考に記載)。Rewriteの新規発生はb1bと最終ENの差分再読で0件。

総括: E_hormuz A節 8件(b1b)/残存7件と同数。内訳の差: E「対象」と「因果」(talks)を統合(hor-p2r1-03)し、E「対象」内の継続性示唆を分離(hor-p2r1-04)。重大なし。

## P2版 hormuz rep2  (er052_output/open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep2)

Checker: checker/runs/meta_run03_advanced.json (final_state=RESOLVED_REWRITE_THEN_DOWNGRADE, 2cycle)

### NG台帳

| NG ID | 重大度 | fact_id | 1 JA | 2 EN前 | 3 EN後 | 5 独立評価 | Checker(4) | Rewrite修正 | 内容(該当文) | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| hor-p2r2-01 | 軽微 | HF-003 | 発生 | 発生 | 修正済 | 修正済 | BLOCKING(cycle1) | あり | JA「船が通るたびに、アメリカの安全対策費を払う。」/EN b1b「Every time a ship passed, it would pay for U.S. security measures.」(支払者=船、通過ごとの徴収) | 台帳は貨物への20%賦課(HF-002)で、支払義務者・徴収方式は未提示(HF-003)。船か貨物かの差は意味逆転ではなく軽い具体化と判定(Checkerは重大扱い)。ENは修正、JAには残存 |
| hor-p2r2-02 | 軽微 | HF-002/HF-003 | 発生 | 発生 | 修正済 | 修正済 | BLOCKING(cycle1) | あり | JA「…費用を、通過する貨物に負担してもらう考えです。」/EN b1b「The idea was to have passing cargo pay for the costs…」 | 貨物への賦課はHF-002内。「pay」は軽い具体化。ENは「a 20 percent fee on all passing cargo cover」に修正、JAには残存 |
| hor-p2r2-03 | 軽微 | HF-003 | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE(cycle1のみ。最終cycle2は非掲出) | なし | JA「通行する貨物に直接料金をかける話が、湾岸諸国との商談に変わったわけです。」/EN「A plan to charge passing cargo directly had turned into business talks with the Gulf states.」(徴収方法「直接」の特定) |  |
| hor-p2r2-04 | 軽微 | HF-007 | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE(03と同一文のみ) | なし | JA題名「…翌日には商談会になった」/EN「…the Next Day It Became a Business Meeting」「business talks with the Gulf states」(置換先を商談/talksと言い換え) | 本文の明示文(replaced by trade and investment deals / 協議は理由)は正確なため軽微。E「対象」に相当 |
| hor-p2r2-05 | 軽微 | HF-009 | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE/QUALITY(one-liner, cycle1-2) | なし | JA「なぜ原油価格は大きく下がらなかったのでしょうか」/EN one-liner「…oil prices stayed high because the strait remained dangerous.」(台帳はBrent先物。oil prices一般へ拡張) | 因果部分は台帳HF-009がcausal_strength=CAUSAL_STATED_BY_SOURCE・conditionsに危険継続を含むためNG扱いしない。範囲拡張(Brent→oil prices)のみ軽微 |
| hor-p2r2-06 | 軽微 | HF-007 | 発生 | 発生 | 残存 | 残存 | QUALITY/ACCEPTABLE(one-liner) | なし | JA「その料金表は一日で姿を消し」/EN「that fee schedule disappeared in one day」「vanished within a day」(実際は約24時間48分後) |  |
| hor-p2r2-07 | 軽微 | HF-002 | 発生 | 発生 | 残存 | 残存 | 未検出 | なし | JA「かなり大きな料金所です。」/EN「It would be quite a large toll booth.」(制度規模) |  |
| hor-p2r2-08 | 軽微 | HF-009 | 発生 | 発生 | 残存 | 残存 | QUALITY(cycle1,2) | なし | JA「第三幕で原油市場が見せた反応は、もっと冷静でした。」/EN「…the reaction from the oil market was much calmer.」(比較評価) | 台帳外の評価語。軽微 |

Rewrite履歴:
- cycle1 narrow_scope(e2_generic_rewrite): 「Every time a ship passed, it would pay for U.S. security measures.」→「The proposal would seek reimbursement for U.S. security costs on all cargo passing through the strait.」
- cycle1 narrow_scope(e1_minimal_word_edit): 「The idea was to have passing cargo pay for the costs…」→「The idea was to have a 20 percent fee on all passing cargo cover the costs…」
- (3件目BLOCKINGは上記に吸収: covered_by_earlier_rewrite_in_cycle)

### 工程別集計

| 工程 | 重大 | 軽微 |
|---|---|---|
| 1 JA最終稿 | 0 | 8 |
| 2 EN Rewrite前 | 0 | 8 |
| 3 EN Rewrite後 | 0 | 6 |
| 4 Checker最終(blocking/non_blocking) | 0 | 7 |
| 5 独立評価(3対象) | 0 | 6 |

4詳細: cycle2 blocking=0 / non_blocking=7 (ACCEPTABLE6+QUALITY1)。non_blockingは正しい文へのACCEPTABLE指摘を多く含み、軽微NG件数とは同質でない。

### 遷移

| 遷移 | 重大 | 軽微 |
|---|---|---|
| 1->2 英語化で新規発生(JAに対応文なし) | 0 | 0 |
| 2->3 Rewriteで修正 | 0 | 2 |
| 2->3 Rewriteで新規発生 | 0 | 0 |
| 4->5 Checker見逃し(5で残存・4で非BLOCKINGまたは未検出) | 0 | 6 |

注: 1->2は「JA側に対応文が存在しない」ものだけを新規発生とした(JAに弱い形で既に存在しENで断定が強まったものは同一IDの強化として備考に記載)。Rewriteの新規発生はb1bと最終ENの差分再読で0件。

総括: E_hormuz B節 最終残存8件に対し本台帳s3は6件(s2は8件)。差分理由: E「因果①(危険が消えなかったから高止まり)」はHF-009がCAUSAL_STATED_BY_SOURCEで危険継続を条件に記載するためNG非該当、E「因果②(市場が思い出した)」は「seemed」付き比喩のためNG非該当(E_hormuz冒頭方針「比喩は事実誤りに数えない」に準拠)。E「主体」3件(船/貨物/直接)は本台帳01-03に対応(01-02はEN修正済)。

## 従来版(Control) hormuz rep1  (er052_output/open233_polysemy_trial_04/runs/hormuz/control/rep1)

Checker: checker/runs/meta_run03_advanced.json (final_state=RESOLVED_STAGE2_DOWNGRADE, 1cycle, Rewriteなし)

### NG台帳

| NG ID | 重大度 | fact_id | 1 JA | 2 EN前 | 3 EN後 | 5 独立評価 | Checker(4) | Rewrite修正 | 内容(該当文) | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| hor-c-01 | 軽微 | HF-009 | 発生 | 発生 | 残存 | 残存 | 未検出 | なし | JA「記事の時点では二点六パーセント高の一バレル八十五ドル超」/EN「they were up 2.6 percent, at more than 85 dollars a barrel」(台帳は「約+2.6%」。「約」の脱落) |  |

Rewrite履歴:
- なし(en_text_after_rewrite無し。③=②と同一)

### 工程別集計

| 工程 | 重大 | 軽微 |
|---|---|---|
| 1 JA最終稿 | 0 | 1 |
| 2 EN Rewrite前 | 0 | 1 |
| 3 EN Rewrite後 | 0 | 1 |
| 4 Checker最終(blocking/non_blocking) | 0 | 1 |
| 5 独立評価(3対象) | 0 | 1 |

4詳細: cycle1 blocking=0 / non_blocking=1 (ACCEPTABLE: 一般論1文のみ。事実誤りではない)。non_blockingは正しい文へのACCEPTABLE指摘を多く含み、軽微NG件数とは同質でない。

### 遷移

| 遷移 | 重大 | 軽微 |
|---|---|---|
| 1->2 英語化で新規発生(JAに対応文なし) | 0 | 0 |
| 2->3 Rewriteで修正 | 0 | 0 |
| 2->3 Rewriteで新規発生 | 0 | 0 |
| 4->5 Checker見逃し(5で残存・4で非BLOCKINGまたは未検出) | 0 | 1 |

注: 1->2は「JA側に対応文が存在しない」ものだけを新規発生とした(JAに弱い形で既に存在しENで断定が強まったものは同一IDの強化として備考に記載)。Rewriteの新規発生はb1bと最終ENの差分再読で0件。

総括: E_hormuz C節は残存2件(範囲=「約」脱落/因果=「供給への心配が消えたわけではない」)。因果は台帳HF-009(CAUSAL_STATED_BY_SOURCE・危険継続)で許容されるためNG非該当とし1件。
