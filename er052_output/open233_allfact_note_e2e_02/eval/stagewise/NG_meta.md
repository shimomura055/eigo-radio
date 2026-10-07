# NG_meta 工程別NG台帳(OPEN-233-E2E-STAGEWISE-NG-AUDIT-01 / 委任_A1 / 2026-10-07)

基準(全工程同一): 重大=事実の意味が変わり読者に誤解を与える(主体・対象の入れ替わり/方向・状態の逆転/台帳にない事実の断定で理解が変わる/否定の反転)。軽微=意味は逆転しないが不正確・過剰断定・対象範囲の曖昧さ・台帳未提示事項の軽い具体化。同一誤りは同一工程1件(JA/ENで同一IDを共有)。
工程: 1 JA最終稿(ja_writer/revision2.md) 2 EN Rewrite前(b1b/article.md) 3 EN Rewrite後(checker jsonの最終 en_text_after_rewrite。Rewriteなしは2と同一) 4 Checker最終cycle判定 5 独立評価(3+JAをE_*.mdで再ラベル)。
状態凡例: 発生/残存/修正済/該当なし(その工程に対応文が存在しない)。5はE_*.mdの既存評価を出発点に、本基準で再ラベルした結果。

## P2版 meta rep1  (er052_output/open233_allfact_note_e2e_02/runs/meta/nb/p2/rep1)

Checker: checker/runs/meta_run03_advanced.json (final_state=RESOLVED_REWRITE_THEN_DOWNGRADE, 2cycle)

### NG台帳

| NG ID | 重大度 | fact_id | 1 JA | 2 EN前 | 3 EN後 | 5 独立評価 | Checker(4) | Rewrite修正 | 内容(該当文) | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| meta-p2r1-01 | 軽微 | MUSE-HC-010 | 該当なし | 発生 | 残存 | 残存 | 未検出(one-liner非指摘) | なし | EN one-liner「Meta’s AI calling test sometimes relied on undisclosed human contractors, raising privacy concerns for users.」(開示不足がプライバシー懸念を生んだ、という因果の結び) | JAに該当文なし(EN工程で新規発生)。HC-010の懸念は情報共有の可能性であり開示不足が原因とは台帳にない |
| meta-p2r1-02 | 軽微 | MUSE-HC-006 | 発生 | 発生 | 修正済 | 修正済 | BLOCKING(cycle1) | あり | JA「AIが仕事を受け取り、困ったところは人間のプロがさっと解決する。そんな華やかな舞台裏にも見えます。」/EN「AI takes the request, and a human professional quickly solves anything difficult.」 | 役割分担・迅速性は台帳なし。ただし「見えます/seemed」の印象表現で後続文が人間の担当を明示するため軽微と判定(Checkerは重大扱い)。ENは修正、JA R2には残存 |
| meta-p2r1-03 | 軽微 | MUSE-HC-006 | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE | なし | JA「AIにお願いしたはずの電話に、人間の助っ人が登場していたわけです。」/EN「a human helper had appeared in a call that users thought they had asked AI to make.」(利用者の認識の言及。JAは「はず」、ENは「users thought」で断定が強化) | 台帳に利用者認識の記述なし |
| meta-p2r1-04 | 軽微 | MUSE-HC-006 | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE | なし | JA「AIの画面を見ているつもりが、その先で人間が仕事をしている。」/EN「You may think you are looking at an AI screen, while a human is doing the work on the other side.」 | 画面・UI体験は台帳なし |
| meta-p2r1-05 | 軽微 | MUSE-HC-012 | 発生 | 発生 | 残存 | 残存 | 未検出 | なし | JA「問題は、そうした可能性があるのに、利用者へ十分な説明がないままテストが始まったことでした。」/EN「The problem was that, even though this possibility existed, the test began without enough explanation for users.」(開示対象を「利用者」と特定) | 台帳は「適切な開示なし」のみで開示対象を明記しない。軽い具体化(rep2とは対象が食い違う) |

判定保留(集計に含めない):
- meta-p2r1-H1: Rewrite後の挿入文「Some calls were handled by trained human contractors. That is what this polished system seemed to be like behind the scenes.」の「That」の指示対象が曖昧 / 理由: 事実の意味変化ではなく文章品質(指示語)の問題で、本基準(重大/軽微の事実判定)に当てはまらない。判定保留とし集計には含めない

Rewrite履歴:
- cycle1 narrow_scope(e2_generic_rewrite): 「AI takes the request, and a human professional quickly solves anything difficult.」→「Some calls were handled by trained human contractors.」

### 工程別集計

| 工程 | 重大 | 軽微 |
|---|---|---|
| 1 JA最終稿 | 0 | 4 |
| 2 EN Rewrite前 | 0 | 5 |
| 3 EN Rewrite後 | 0 | 4 |
| 4 Checker最終(blocking/non_blocking) | 0 | 8 |
| 5 独立評価(3対象) | 0 | 4 |

4詳細: cycle2 blocking=0 / non_blocking=8 (ACCEPTABLE7+QUALITY1)。non_blockingは正しい文へのACCEPTABLE指摘を多く含み、軽微NG件数とは同質でない。

### 遷移

| 遷移 | 重大 | 軽微 |
|---|---|---|
| 1->2 英語化で新規発生(JAに対応文なし) | 0 | 1 |
| 2->3 Rewriteで修正 | 0 | 1 |
| 2->3 Rewriteで新規発生 | 0 | 0 |
| 4->5 Checker見逃し(5で残存・4で非BLOCKINGまたは未検出) | 0 | 4 |

注: 1->2は「JA側に対応文が存在しない」ものだけを新規発生とした(JAに弱い形で既に存在しENで断定が強まったものは同一IDの強化として備考に記載)。Rewriteの新規発生はb1bと最終ENの差分再読で0件。

総括: 既存評価E_meta A節(Fact整合5件、最終EN残存4件)と同数。本委任で追加したNGなし。

## P2版 meta rep2  (er052_output/open233_allfact_note_e2e_02/runs/meta/nb/p2/rep2)

Checker: checker/runs/meta_run03_advanced.json (final_state=RESOLVED_REWRITE_THEN_DOWNGRADE, 3cycle)

### NG台帳

| NG ID | 重大度 | fact_id | 1 JA | 2 EN前 | 3 EN後 | 5 独立評価 | Checker(4) | Rewrite修正 | 内容(該当文) | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| meta-p2r2-01 | 軽微 | MUSE-HC-006 | 発生 | 発生 | 残存 | 残存 | QUALITY(cycle3) | なし | JA「電話の相手はAIか、それとも人間か。今回の答えは、少なくとも一部では人間でした。」/EN「Was the person on the other end of the call an AI or a human? This time, at least in some cases, it was a human.」(終盤「Whether the one on the other end of the phone is an AI or a human」も同型) | 「other end」が電話の受け手(事業者)に読める曖昧さ。本文中で「契約スタッフが電話をかけた」と明示されるため前後文脈上は軽微と判定。ENでcallee読みが強まる |
| meta-p2r2-02 | 重大 | MUSE-HC-012 | 発生 | 発生 | 残存 | 残存 | BLOCKING(cycle1)→rewrite後cycle3でACCEPTABLE。「telling the person on the other end」文は未検出 | あり | JA「ただし、主役になった人間が知らされていなかった。」「問題は、その事実を相手に十分知らせないまま、テストを始めたことでした。」/EN b1b「But the humans who ended up in the main role had not been told.」→Rewrite後「But the humans who ended up on the other end had not been properly told.」+「…without properly telling the person on the other end about this fact.」(開示されなかった対象の特定) | 台帳は「適切な開示なし」とだけ述べ対象を特定しない。JA/b1bは契約スタッフ本人が知らされていなかったと読め、開示不足の対象の取り違え。Rewriteは対象を「電話の相手側の人間」に置換しただけで、台帳外の対象断定は残存(同一誤りの形を変えた残存。新規発生としては数えない)。E_meta「対象1」と「追加(c)」を同一誤りとして統合 |
| meta-p2r2-03 | 軽微 | MUSE-HC-012 | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE(cycle1のみ。最終cycle3では非掲出=未検出) | なし | JA「Metaはその説明を忘れて、いったん舞台の幕を下ろしたわけです。」/EN「Meta forgot to give that explanation and, for now, brought the curtain down on the stage.」 | 「忘れた」は原因・意図の断定。台帳は「ミスと認めた」まで |
| meta-p2r2-04 | 軽微 | MUSE-HC-012 | 該当なし | 発生 | 残存 | 残存 | ACCEPTABLE(cycle1,3) | なし | EN one-liner「Meta’s AI phone test used undisclosed human callers, so the company temporarily rolled back the feature.」(開示不足→ロールバックの因果) | JAに該当文なし(EN工程で新規発生) |
| meta-p2r2-05 | 軽微 | MUSE-HC-006 | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE(cycle1,3) | なし | JA「AIが電話をかけてくれると思ったら、舞台裏では人間のスタッフが登場する。」/EN「You think AI is making the call, but behind the scenes, a human staff member appears.」 | 利用者の認識は台帳なし |
| meta-p2r2-06 | 軽微 | MUSE-HC-008(根拠不足) | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE(cycle1,3) | なし | JA「ややこしい話なら、人間が対応したほうが自然に進むこともあります。」/EN「If the matter is complicated, things may go more smoothly if a human handles it.」 | HC-008は一部テストの成功率レンジのみ。難案件で人間が優る旨は台帳外 |
| meta-p2r2-07 | 軽微 | MUSE-HC-014 | 発生 | 発生 | 残存 | 残存 | 未検出 | なし | JA「Metaは、電話の相手となる事業者との改善を続け、準備が整い、適切な説明ができる場合にだけ、広く公開するとしています。」/EN「Meta says it will continue working to improve the service with the businesses it calls, and will make it widely available only when it is ready and can explain it properly.」(「公開」対象が電話機能全体か人間コンシェルジュ機能かが不明) | E_metaでは「曖昧」判定。対象や範囲の曖昧さ=軽微として再ラベル(台帳notesの区別要求を満たさない) |

Rewrite履歴:
- cycle1 narrow_scope(e1_minimal_word_edit): 「But the humans who ended up in the main role had not been told.」→「But the humans who ended up on the other end had not been properly told.」(対象を置換したのみ)

### 工程別集計

| 工程 | 重大 | 軽微 |
|---|---|---|
| 1 JA最終稿 | 1 | 5 |
| 2 EN Rewrite前 | 1 | 6 |
| 3 EN Rewrite後 | 1 | 6 |
| 4 Checker最終(blocking/non_blocking) | 0 | 11 |
| 5 独立評価(3対象) | 1 | 6 |

4詳細: cycle3 blocking=0 / non_blocking=11 (ACCEPTABLE10+QUALITY1)。non_blockingは正しい文へのACCEPTABLE指摘を多く含み、軽微NG件数とは同質でない。

### 遷移

| 遷移 | 重大 | 軽微 |
|---|---|---|
| 1->2 英語化で新規発生(JAに対応文なし) | 0 | 1 |
| 2->3 Rewriteで修正 | 0 | 0 |
| 2->3 Rewriteで新規発生 | 0 | 0 |
| 4->5 Checker見逃し(5で残存・4で非BLOCKINGまたは未検出) | 1 | 6 |

注: 1->2は「JA側に対応文が存在しない」ものだけを新規発生とした(JAに弱い形で既に存在しENで断定が強まったものは同一IDの強化として備考に記載)。Rewriteの新規発生はb1bと最終ENの差分再読で0件。

総括: E_meta B節の最終残存8件(主体1/対象1/因果2/追加3/★曖昧1)に対し本台帳s3は7件。差分理由=E「対象」と「追加(c)」(いずれも開示対象の特定)を同一誤りとして1件に統合(meta-p2r2-02)。重大はこの1件のみ。

## 従来版(Control) meta rep1  (er052_output/open233_polysemy_trial_04/runs/meta/control/rep1)

Checker: checker/runs/meta_run03_advanced.json (final_state=RESOLVED_REWRITE_THEN_DOWNGRADE, 2cycle)

### NG台帳

| NG ID | 重大度 | fact_id | 1 JA | 2 EN前 | 3 EN後 | 5 独立評価 | Checker(4) | Rewrite修正 | 内容(該当文) | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| meta-c-01 | 軽微 | MUSE-HC-012 | 発生 | 発生 | 残存 | 残存 | QUALITY | なし | JA「Metaの幹部は、この始め方を「ミス」だったと認めました。そして9月22日までに…ロールバックしました。」/EN「Meta executives admitted … By September 22, they had rolled back…」(台帳は副社長1名。複数形へ拡張) |  |
| meta-c-02 | 軽微 | MUSE-HC-010 | 発生 | 発生 | 修正済 | 修正済 | BLOCKING(cycle1) | あり | JA「Metaの従業員が心配したのは、まさにそこでした。」/EN「That was exactly what worried Meta employees.」(直前の「利用者に十分伝わっていなければ…」へ従業員の懸念を結びつけ) | 直後の文でHC-010の懸念(情報共有の可能性)が正しく説明されるため前後文脈上は軽微と判定(Checkerは重大扱い)。ENは文削除で解消、JA R2には残存 |
| meta-c-03 | 軽微 | MUSE-HC-010 | 該当なし | 発生 | 残存 | 残存 | ACCEPTABLE(cycle1,2) | なし | EN one-liner「Meta tested having human workers handle some AI phone calls without clearly telling users, raising privacy concerns.」(開示不足→懸念の因果) | JAに該当文なし(EN工程で新規発生) |
| meta-c-04 | 軽微 | MUSE-HC-012 | 発生 | 発生 | 残存 | 残存 | ACCEPTABLE(cycle1。最終cycle2では非掲出) | なし | JA「その出演者が誰なのか、利用者に十分伝わっていなければ…」「適切な開示がないまま始まっていました」/EN「if users are not told clearly enough who the performer is」「without properly telling users about it」(開示対象を利用者と特定) | 台帳に開示対象の記述なし |

Rewrite履歴:
- cycle1 narrow_scope(e2_generic_rewrite): 「That was exactly what worried Meta employees.」を削除(以降の情報共有懸念の文は維持)

### 工程別集計

| 工程 | 重大 | 軽微 |
|---|---|---|
| 1 JA最終稿 | 0 | 3 |
| 2 EN Rewrite前 | 0 | 4 |
| 3 EN Rewrite後 | 0 | 3 |
| 4 Checker最終(blocking/non_blocking) | 0 | 7 |
| 5 独立評価(3対象) | 0 | 3 |

4詳細: cycle2 blocking=0 / non_blocking=7 (ACCEPTABLE6+QUALITY1)。non_blockingは正しい文へのACCEPTABLE指摘を多く含み、軽微NG件数とは同質でない。

### 遷移

| 遷移 | 重大 | 軽微 |
|---|---|---|
| 1->2 英語化で新規発生(JAに対応文なし) | 0 | 1 |
| 2->3 Rewriteで修正 | 0 | 1 |
| 2->3 Rewriteで新規発生 | 0 | 0 |
| 4->5 Checker見逃し(5で残存・4で非BLOCKINGまたは未検出) | 0 | 3 |

注: 1->2は「JA側に対応文が存在しない」ものだけを新規発生とした(JAに弱い形で既に存在しENで断定が強まったものは同一IDの強化として備考に記載)。Rewriteの新規発生はb1bと最終ENの差分再読で0件。

総括: E_meta C節(残存3件=主体1/因果1/追加1)と同数。
