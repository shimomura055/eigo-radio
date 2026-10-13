# SSOT_DRAFT_01(本委任では未適用。委任_02/Fableが照合のうえ適用)

## CURRENT_SPEC(M1 OOV複数発音候補仕様。Opus条件Aレビュー後にProduction仕様として記載する案)
M1(連結発音の音素同等性)の発音候補は、canonical語のみから事前固定する(ASR非依存)。C1=CMU全異読(固有名詞らしき語は代表発音のみ)、C2=Pronunciation Ledgerの全発音(confidence不問、CMU未収録語のみ、英語IPAのみ、決定論IPA→ARPAbet変換、変換不能は候補不成立)。語あたり上限6。1候補でも既存M1(音素正規化→Pattern A/B/C→F1全差分点検)が成立すれば`M1_MULTI_CANDIDATE_ACCEPT`(PASS_WITH_WARNING+audit)。C3(規則G2P)とASR側綴りの近似は不採用。Ledgerは読取のみ(confidenceの書換なし)。Secondary同意は共通候補音素列で両エンジン成立。ユーザー正式承認=2026-10-13(複数の合理的候補のいずれか1つで可)。Status: WIRING_DESIGN_DRAFT(未配線)。

## DECISION_LOG(ユーザー正式決定の記録)
2026-10-13 ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01: ユーザーがM1のOOV扱いについて「複数の合理的な発音候補のうち1つでも連結発音・ASR転写・文章全体と音韻整合すればPASS可。後付け候補は禁止。M1が成立しても他の内容差分があれば無条件PASSにしない」を`APPROVED_FOR_PRODUCTION`として正式承認(到達目標PRODUCTION_WIRED)。委任_01=設計+offline評価(JPY0): Melos 12件 4/12→12/12(全件C2_ledger_alt・low)、674ペア新規PASS13件(全てMelos)、F1反例19/19維持、合成24/24。Opus条件A待ち。

## OPEN_ITEMS
- OPEN-339(M1/F1配線)更新: UDR-1(OOV)は判断済み(複数候補承認)。M1は設計済み・Opus条件A待ち・未配線。
- 新規OPEN候補: (1)C3(規則G2P)採否=不採用で確定するか (2)KP適用(案K-A既定、実データ効果測定を先行) (3)Ledger運用上限・自動生成/人手確定の区別フィールド(新規フィールド追加の要否) (4)直接音素置換(語幹がCMU未収録の語への拡張)の要否(新規処理) (5)Ledger由来受理の事後集計。

## USER_DECISION_REGISTER
UDR-1(OOV)→「判断済み(2026-10-13: 複数発音候補方式を承認)」(委任_02で更新)。
