# 委任_06c: AUW — Opus条件Cレビュー所見(OF-AUW-C-01〜C-14)のFable採用分の実装(API 0)
(原文は呼出元Fableの委任文。要旨保存) branch feat/auw-unified-asr-01 (HEAD 5bacf9b47)。main禁止。有料API 0。
項目: (a)非ラテン救済の最終ANDゲートを採用転写(Azure)対象に (b)Secondary障害網羅(_AzureShared._call try/except、EN canceled部分転写をエラー扱い、cost設定不備RuntimeError再送出) (c)再利用経路の値ガード通過+bulk rejudge (d)Secondary障害は技術STOP、HR Lockにしない (e)試聴リスト導出失敗表示 (f)test決定化 (g)死コード撤去+flag OFF test (h)Dialogue(Std)/A2通算3回外側ループ (i)費用試算補完(RUNTIME_EVIDENCE_06 §12-9) (j)evidence_06b由来のHR queue行除去 (k)IMPLEMENTATION_06c.md+commit/push。
git message: ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_06c: Opus条件C所見の是正(...)。main無変更、JPY0
