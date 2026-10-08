# S0_USER_CHECK: 要約 MAJOR の判定にユーザー確認が要る3件(境界例・過剰判定の疑い)

作成日 2026-10-08(OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_02 S0)。出典・分類根拠は `S0_AUDIT_01.md` §3。各件の質問は「この要約文は、台帳の範囲で書いたものとして許容してよいか(許容/不許容)」。同型の世代数も併記する。

## 確認1: 「users」(開示を受ける相手)を書いたことは MAJOR か(世代 G02 最終。同型 G07・G09・G12 も)

- 要約文: "Meta paused its human-concierge feature after contract workers made calls without properly informing users."
- 台帳(MUSE-HC-012): 「…適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックした」(conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト。開示の相手の記載なし)
- 指摘理由(Checkerではなく EN deviation check、changed_scope、MAJOR): 「Ledgerは適切な開示がなかったことを記録していますが、誰に開示されなかったかは特定していません。記事は…対象を限定しています」(この指摘が解消せず STOP)

## 確認2: 「so」で因果をつなぐことは MAJOR か(世代 G09 最終)

- 要約文: "Meta’s AI calling test used human contractors without proper disclosure, so the company rolled back that feature."
- 台帳(MUSE-HC-012): 「…適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した」(ミスの認定とロールバックを並記。因果は明示なし)
- 指摘理由(changed_causality、MAJOR): "The word “so” presents the lack of disclosure as the cause of the rollback, while the Ledger reports the admission and rollback without explicitly establishing that causal link."(この指摘が解消せず STOP)

## 確認3: Brent先物の動きを「oil prices」と一般化することは MAJOR か(世代 G06 最終)

- 要約文: "In one line: “Oil prices stayed high despite the shift from a proposed Hormuz fee to investment deals, as shipping-safety fears persisted.”"
- 台帳(HF-009): 「Yahoo Financeは…Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた」(scope: 国際指標Brent原油先物の短時間の値動き。notes: 撤回後に原油価格が全面的に下落したとは書かない)
- 指摘理由(changed_scope、MAJOR): 「Brent先物の値動きを、原油価格全般の動きとして表現しています」(この指摘が解消せず STOP)

補足(事実のみ): 上記3件は STOP した8世代のうちの3件(他に G02 の「users」同型が G07・G12 にあり、G08・G14 は境界例)。確認結果は「許容/不許容」の別だけで分類を更新できる。
