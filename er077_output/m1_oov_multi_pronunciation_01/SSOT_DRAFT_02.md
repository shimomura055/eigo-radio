# SSOT_DRAFT_02(委任_03で正式SSOTへ反映する文案。本委任ではSSOT未編集。OPUS_FINDINGS_LEDGERのみ追記済み)

## CURRENT_SPEC 文案
- M1(複数発音候補)= `MODULE_IMPLEMENTED_PENDING_WIRING`。`er006_m1_multi_candidate_01.py`(新規Production module、未import)。ユーザー承認(2026-10-13、複数の合理的発音候補のいずれか1つで音韻整合すればPASS可)に基づく。
- 候補: C1=CMU全異読(固有名詞らしき差分は代表発音のみ)、C2=Pronunciation Ledger IPA(CMU未収録語のみ。canonical_spelling≠surface除外・sources空除外・segment開始以降の更新除外・ja_reading_katakana除外・非英語ラベル断片除外)。C3(綴り規則推定)・ASR転写からの後付け候補は存在しない。語あたり上限6。
- 受理: 置換後文のF1残差0、かつexact以外の置換位置が全て`f1_explained`(Pattern A/B/C)に含まれること(benign吸収は不受理、OF-178)。受理理由`M1_MULTI_CANDIDATE_ACCEPT`(PASS_WITH_WARNING)。audit: ledger_key/updated_at/ipa_raw/candidate_set_hash/一致候補[出典クラス・confidence]/secondary_agree/no_match_reason。
- 凍結: 候補集合はsegment最初の試行前に1回凍結し判定へ注入(再計算・monkeypatch禁止)。Secondary同意は必須化せず、両転写が手元にある場合のみ矛盾(protected fail/内容誤り)で非PASS。

## DECISION_LOG 文案(D-2'限定置換を明記)
- 2026-10-13: **D-2'(`er006_secondary_asr_01.py` L221-225「Tier3情報はHR用のみ、自動PASS根拠に使わない」)の限定的置換**。ユーザー承認「辞書未収録語は既存Pronunciation Ledgerや利用可能な発音情報から合理的な候補を取得する」に包含されるとFableが照合。置換範囲はM1かつCMU未収録語に限る。Tier3調査結果の即時利用(同一segment内)・ASR後付け候補・綴り推定は引き続き禁止。docstring更新は配線(委任_03)時。
- OF-178〜187(Opus条件A)の反映状況はOPUS_FINDINGS_LEDGER参照。

## OPEN-339 更新文案
- M1: 設計+offline評価(委任_01)→Production module+unit test 68件PASS(委任_02、Melos 12件 12/12、F1反例19/19、674ペアで新規PASS18件[全てMelos↔Mello/Mellow型、回帰0]。`eval_02/EVAL_02.md`)。配線・実機evidenceは委任_03。Status=`MODULE_IMPLEMENTED_PENDING_WIRING`。

## 新規OPEN 起票案
1. **直接音素置換の要否**(OF-184): 現行はASR語とPattern期待綴りがともにCMU収録語である場合のみ置換可能。ASR語がCMU未収録・期待綴りがCMU未収録の場合は`no_candidates`/`asr_word_not_in_cmu`/`no_phoneme_match`のtelemetry(理由別)で需要を測り、必要なら別委任で検討(新規処理のためOpus条件A)。
2. **Ledger由来フィールド新設の要否**: 自動生成/人手確定の区別は現状`entity_type`/`resolution_method`/`updated_at`で代替。運用で`aggregate_by_ledger_key`により低信頼自動エントリ起因の受理を事後監視。専用フィールドは要判断。
3. **KP効果測定**(OF-185): 案K-A(C1+C2適用)の効果をread-onlyで先行測定、新規PASSがあれば全件人手確認(測定段階のみ、runtime Gateにしない)。
4. **Tier3書込のupdated_at欠落確認**: `pronun_ledger.upsert`は`updated_at`を書くが、seed等で欠落するエントリは「時刻不明」として候補に含める(module仕様)。欠落エントリが増える運用がないか監視。
5. **所有格正規化・stem+s救済の移植要否**(委任_01 offlineには有り、本moduleは未移植)。

## UDR #52 → 判断済み
- UDR #52(OOV複数発音候補方式の採否): 2026-10-13ユーザー承認+Fable照合(D-2'限定置換)により判断済み。残る判断=Production採用(`APPROVED_FOR_PRODUCTION`は人間ユーザーのみ)・配線後の実機evidence結果の評価。
