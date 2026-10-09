# WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01 委任_01d (2026-10-09, ¥0, 評価LLM未実行)

ユーザー判断(逐語): 「1. K01 → C 2. K03 → C 3. K11 → C寄り。ただしBの余地あり」(A=問題なし/B=境界・曖昧/C=重大NG)

## 変更
- CASES_01.md / cases_01.json(生成元 build_cases_01.py を修正し再生成): K01=C(ユーザー確認済み)、K03=C(ユーザー確認済み)、K11=C寄り・B余地あり(ユーザー判断)。旧「Fable確定」「Sonnet判定」は履歴として残す。
- eval_items_01.json: 変更なし(再生成後も差分なし。人間判定を含まない)。
- PREREGISTRATION_01.md: K03をM1必須へ昇格(Fable判断)。M1=K01,K02,K03 x 2モデル=6判定(Aあり→REJECTED/Aなし・B混在→USER_DECISION_REQUIRED/全C→PASS)。K11は参考、期待=CまたはB(Aなら見逃し報告)。限界欄にHC-012同一Fact2件(K01,K03)がM1に入る旨を追記。§6-7を追加。
- RESULT_TABLE_TEMPLATE_01.md: 人間既知列表記・M1(6判定)・M6を更新。

## 範囲外
評価LLM実行、API支出、Production変更なし。
