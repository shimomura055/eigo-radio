# FABLE_ACCEPT_01 (KP-CANON-REVIEW-REQUIRED-FIX-01 委任_02, 2026-10-25)

判定: OPEN-504 = FIXED (Fable受入2026-10-25)。

- 照合対象: docs/pm/RESULT_PACKET_KCRR1.md, IMPACT_01.md, RUNTIME_EVIDENCE_01.md, commit 746934961 / 68ab115e8。
- X/Z正式経路でCANONICALIZATION_REVIEW_REQUIREDは採用されない(PASSのみ採用、上限到達で既存の人間確認停止)。test 8件・runtime evidence(mode A/B/C)で確認。A/B/C無影響。
- 留意(非blocking、UDR #190): CURRENT_SPEC:1966の2026-08-08決定文「REVIEW_REQUIRED→自動retryなし→人間承認で採用可」に対し、人間確認前に除外語付き再選定(外側retry、通算3回内)を挟む。既存Z外側retry(INVALID対象、委任_10「Z限定・暫定」)の適用拡大。不良KPを採用しない点は仕様整合。Fable推奨=承認(HR停止を記事あたり0.1%未満)。代替=即HR停止(HR約1%/KP段)。代替選択時は run_kp_with_outer_retry のREVIEW_REQUIRED分岐を即停止へ変更(小変更)。
- 事故記録: 委任_01でSSOT編集scriptがCURRENT_SPEC.md作業コピーを一時的に空にし、HEAD+変換で復元。再発防止=SSOT編集前にバックアップ、編集後にgit diff --statと内容差分を確認。
- 残差分処置: CURRENT_SPEC.md=孤立CR改行化のみ(改行除去後の内容が完全一致)でHEADへ戻した。DECISION_LOG.md=委任_36節4行の削除(HEADに存在)を誤差分としてHEADへ戻した(HEADには同節が2箇所重複して存在、別途整理候補)。USER_DECISION_REGISTER_01.md=全行CRLF化のみの差分をHEADへ戻してUDR #190を追記。
