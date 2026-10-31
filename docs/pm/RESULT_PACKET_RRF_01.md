# RESULT_PACKET KP-RESCUE-REJUDGE-REVERT-SURFACE-FIX-01 委任_01 (OPEN-633)
Status案: 修正完了・検証済み、Fable受入待ち。コード=er125_kp_rescue_production_01.py(qa_rejudge一致条件、:506-531/:535/:558-565/:599)、test=TestQaRejudgeRevertSurfaceKey 10件(er125計68 OK)。
(1)既存仕様整合: CURRENT_SPEC KP救済節(旧line2028「revertは再判定keyがほぼ不一致=HR限定」を仕様①以降の実害として解消、追記line2033)、er119_kp_human_review_01.py:540 rescue_unverified fail-closed不変、AUDIT_01 §4-1。
(2)未承認機能の既定値: 新flag・新Gateなし。既定ON既存経路の不具合修正のみ。Grep: 新規env/flag 0、QA_VERDICTS/QA_FIELDS/retry/HR経路は無変更(diff確認)。
(3)失敗終了時の成果物/目的適合: 不一致・別語・rank不一致・QA欄不正は従来どおりNOT_REJUDGED(提示されない=fail-closed)でtest固定。成果物=docs/research/KP-RESCUE-REJUDGE-REVERT-SURFACE-FIX-01/EVIDENCE_01.md+ev01/。目的(承認済み『表層形へ戻して候補を残す』が実際に機能する)に適合: 実データ5/5がNOT_REJUDGED->QA再判定PASS。
(4)撤去・残置: 旧一致式 `_norm_lc(r.get("key_phrase", "")) != _norm_lc(key)` は新式に置換(Grep 0件残存)。撤去したtest・規則なし。既存test期待値の変更0。
判定整合: 重大NG=なし
検証: 単体68(er125)OK、関連既存testは修正前後で失敗集合同一(新規失敗0)、実データreplay 5/5 NOT_REJUDGED->PASS(対照rate at whichはQA FAILのまま)、API約¥1.99(Cap ¥10)。
原因仮説/観測: REVERT後の表層形keyとQA再判定LLMの見出し形key不一致(旧er125:526)。初版は無関係な救済前keyも受理し既存2testが新規失敗->同一項目確認(_headword_of_same_item)追加で解消。次の一手: なし(受入待ち)。
判断候補: 本件はなし(A既判断=承認済み救済仕様+11-8範囲内の是正)。参考=EVIDENCE_01 §5(表層形そのものでQAさせる場合はPrompt変更を伴うため別判断)。
