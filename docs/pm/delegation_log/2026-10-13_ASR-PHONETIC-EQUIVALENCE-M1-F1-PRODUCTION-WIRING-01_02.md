# ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_02 (要点保存)

注: 委任_01が逐語保存中に停止したため、Fable指示により「ユーザー指示(原文)」以外は見出しを保ち要点のみ保存。ユーザー指示は要点(逐語ではない)。

## 管理ID
ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_02。並行: FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_03。SSOT編集権なし。出力: er075_output/m1_f1_production_wiring_01/。Managed-ID trailer必須。

## 性質/到達上限Status/禁止事項
性質: M1/F1(APPROVED_FOR_PRODUCTION)のProduction配線設計+OOV安全性整合+F1影響事前集計。Production code無変更。到達上限=WIRING_DESIGN_DRAFT(Opus条件A/C待ち)。PRODUCTION_WIRED宣言禁止。費用JPY0。禁止: Production code/Validator/Gate/Prompt編集、新許容ルール、OOV任意綴り近似の許容、R1/V2/allow-list混入、既存Gate緩和、共有telemetry書込、git add -A等。STOP条件: 新許容ルール必要/OOV未確定/誤PASS増加/既存品質大幅悪化/配線不能/新仕様判断→USER_DECISION_REQUIRED候補。

## ユーザー指示(要点)
M1=連結発音のASR表記揺れ(Mello/Mellow→Melo)の発音同等性判定、F1=最初の食い違いだけ見て全文PASSする既存Validator不備の是正。必須条件: Melos専用hardcode不可/固有名詞・一般語共通/綴り類似だけでPASS不可/Pattern A/B/C許容範囲を未承認拡張しない/OOVはLedger等の信頼発音を確認/発音不確証語は無制限な綴り近似で救済しない/判定理由・元ASR・正規化内容の追跡可能性。OOV fallbackがそのまま移せなければ未承認の代替を実装せずSTOP報告。F1: 全差分確認、連結発音で説明できる差分のみ許容、他は通常Validator、内容語・否定・数値・時制・欠落・別固有名詞を見逃さない。Production適用範囲: Family X/Z、Std通常/6%減速後/Adv/初回/retry/fallback/regen/dialogue。非対象: R1/V2/個別allow-list/Gate緩和/無関係Prompt変更/Family Z再生成。最終報告10項目。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3 適用(T-2 TTSなし、T-3 JPY0)。

## KPI provenance / Opus台帳 / SSOT追記文 / Git / 報告
設計のみ(reuse、fresh E2E=No)。OF-153〜158参照。SSOT編集せずRESULT_PACKETに委任_03用文案。明示add対象のみcommit/push。RESULT_PACKET_M1F1.mdに(0)〜(8)。
