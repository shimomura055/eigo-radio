# OPUS_REVIEW_REQUEST_01 (Fable用下書き。条件A: 新しい処理フロー) ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 Phase 1

## レビュー対象
候補E2「Ledgerの出典付き読みへの直接音素一致」(`DESIGN_01.md` §2、`trial_direct_ledger_phoneme_01.py`)。M1(承認2026-10-13)のOF-184「直接音素置換は範囲外・需要はtelemetryで測定」を、gacha実例(`ROOT_CAUSE_01.md` §4)を根拠に実装する提案。Production無変更・Trial専用。

## 事実の要約(レビュアーが読む順)
1. `ROOT_CAUSE_01.md` §0・§4(M1が不発の2段: 入口=UNCERTAIN限定、`_enumerate_subs`=期待綴りCMU要件)
2. `DESIGN_01.md` §1表、§2
3. `TRIAL_01_RESULT_01.md` 表E2・E1・A・B・C・F
4. 主要コード: `er006_m1_multi_candidate_01.py`(`_entry_gate`、`_c2_candidates`、`_enumerate_subs`)、`er006_preprod_hardening_01_validation.py`(`loanword_flags`583、`LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION`)、`er006_secondary_asr_01.py`(M1呼出点・凍結)

## 論点(5〜6件)
1. **UDR #52「綴りだけを根拠に任意の発音を許容しない」との整合**: E2は根拠が「出典付きLedger読み+音素完全一致+置換後の既存classify PASS」で綴りでない、と整理した。この解釈は妥当か。P2(G-1/G-2: ASR側OOVの自動許容、Fable非推奨)との境界(E2は正準語側OOV+ASR語がCMU収録、1:1置換のみ)は十分に明確か。
2. **Ledger読みの信頼**: gacha entryは confidence=medium・evidence_tier=NAME_IN_CITED_PAGE(読みは二次情報)。reactive lookup由来のentryを受理根拠にしてよいか。confidence下限(medium)・evidence_tier要件・ledger_key別の事後集計(OF-187)で足りるか。meink(confidence=low)は除外される。
3. **処理順序**: 「Primary NG→M1→E2→Secondary」の位置(Secondaryを呼ばずに受理)は、統一judge(L2814「Secondary 1回+cache」「Primary NGは原則Secondary」)と矛盾しないか。PASS_WITH_WARNING+事後試聴リストで独立証拠の欠如を補う設計でよいか(M1・Tier3の既存性質と同じ)。
4. **2つの読み(US/UK)を持つ語**: Ledgerが複数候補を持つ場合、どれか1つとの一致で受理=既存M1と同じ。学習者向けに読みを一意に保証しない点をどう扱うか。
5. **Phase 2の検証設計の十分性**: 保存データの正例が3件のみ(gacha×2・meink)。追加正例の収集(借用語5〜8語、約15〜30円)とRegression(保存5,604行、PASS→NG=0、NG→PASS全件目視)で採用判断に足りるか。
6. **供給側(G)**: プラン段階でCMU未登録の小文字語をLedgerへ先行登録する案は、E2と同時に検討すべきか、E2の結果後でよいか(初回出現segmentの救済、費用は未測定)。

## 非論点(確認済みでOpus不要)
- 候補A(prompt)・B(G2P)・F(クロス確認)は実測で不採用/除外。
- F1 `tokenize` の ’ 未対応は11-8の既存不具合(別途Fable判断)。
