# OPUS_REVIEW_REQUEST_02(条件C: 重要変更のProduction採用前レビュー。①固有名詞 RET Production Wiring 設計)

管理ID: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN 委任_03 / 2026-10-23。対象=`WIRING_DESIGN_01.md`(同ディレクトリ)。
前提: ユーザーは①(OPEN-472)をX/Z共通でProduction採用承認済み(`APPROVED_FOR_PRODUCTION`、UDR #168、原文`docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER_02.md`)。本レビューは採用可否ではなく「配線設計が承認仕様(Trial VALIDATED範囲=DESIGN_02/TRIAL_RESULT_01)を変えず、安全条件を保ち、抜けが無いか」の独立確認。条件Aレビュー(OPUS_REVIEW_01.md, OF-PN2-01〜13)は反映済みで重複させない。

## 見てほしい論点(5つ)
1. **配線点の抜け**: resume/regen(`covered_text_sha256`+`builder_version`による未カバーtextのみNER→和集合、A-5)、Store再利用(A-11 `entity_contributed`新guard。scope外は既存PNAPブロックが先に止めるので追加で効くのはrollback時のみ、という整理の妥当性)、Local Rewrite(A-12=LR時にNERせず次の構築点で和集合。OF-PN2-06(ii)からの設計変更が許容か)、継承再判定(A-10 保存entryから復元、`builder_version`不一致で再判定NG)、retry/fallback(A-13)、kp_vote_check(A-14)、HR Lock(A-15)に見落としは無いか。Zが`run_tts_stage`のlevel単位で表を作る点(最大2 call)と、X b1b/a2別プロセスの並行書込(atomic+再読込和集合)の妥当性。
2. **RET-3(G3)の`er103`本体変更の安全性**: Trialは判定関数の複製(drift guard付き)で検証したが、Productionは`er103.evaluate_alarm_eligibility`本体に`entity_table=None`引数と2か所の分岐(G5の`ledger_surfaces | grant`、G3の不受理分岐限定`ret3_check`)を入れる。(a)`entity_table`がNone/空のとき現行とバイト一致、(b)RET-3は従来不受理になる場合のみ作用、(c)合成spanにも`_noun_checks`+P-03、の3点を、drift guardの代わりに「実装前凍結のbaseline署名(D1 88件+D2+fixture)との一致test」(D-5)で担保する案で十分か。11-7限定例外が使えない経路(既存関数本体の直接編集)を「承認済み正式採用に基づくProduction実装」として扱う整理に問題は無いか。
3. **既定ONの妥当性と隔離**: 有効条件=`RUN_ENTITY_TABLE_ENABLED ∧ pnap.is_active_for_run()`(PNAP scope依存、`er109_xz_scope_01`不使用)。委任文の「er109 scope再利用」と異なる選択(§B-2: PNAP消費者に一致、PNAP OFFでのRET単独ON不整合の回避、finally構造)の妥当性。A/B/C・dry_run・scope外・単体呼出の不活性、rollback=定数1行の挙動(A-10/A-11)。構築失敗=現行同一(SC-6)で、設定不備(cost logger/単価)のみ伝播する扱い。
4. **構築入力の設計変更**: Trial/OF-PN2-05は「実際にTTSへ渡る供給後canonical text」を入力にしたが、Productionは構築点がTTS前(hook)のため**供給前script text**(runnerの`results[..]["canonical_text"]`と同じ)をNERに渡し、判定時のみ供給後textで`occurrences()`を取る(D-4)。この二段で(i)供給で綴りが変わった語の取りこぼし、(ii)供給前後で文字列が変わる誤付与、が生じないか。providerでKP/JA/HEADING_READOUT/`APPLICABLE_ROLES`外を除外する選別(A-4、`resolve_narrative_role`)の漏れ。
5. **X側evidence設計と②との干渉**: X evidenceをX-1(保存済み実誤読wav[`Kristie Tse`等]を`run_scope("X")`内の正式adapter+実ASRで判定、表は正式hook構築)+X-2(正式入口`--only-segments`の入口path証拠、自然発火は必須にしない)+X/Z-3,4(API 0)に分けたことが、受入条件4・9(X/Z双方の正式runtime証拠と承認仕様の一致)を満たすか。Z-1=B工程(Bertie 4clip再生成)と兼ねる点。②UKUSとの近接hunk(`er078_reuse_value_guard_01.py`・`er019…inheritance`・allowlist)と処理順(②が同値判定を先に行いPNAPに到達しない)に干渉・安全条件の相互緩和が無いか。

## 追加の確認点(軽)
- `builder_version`をhashにする対象(prompt A/B・`_token_class`・カテゴリ規則・`MAX_ENTITY_WORDS`)は過不足ないか。
- NER費用上限を独自usage logではなく定数(`MAX_NER_CALLS_PER_BUILD=2`+入力文字数上限)にする設計と、cost logger未initを伝播させる方針。
- 実装委任でTrialの`er111_pn_*`複製依存testを撤去/skipする扱い(C表)。

## 回答フォーマット(Fable記録用)
総合判定(配線設計可/必須修正後可/再設計)、必須修正(OF-PN3-xx)、推奨、情報。論点ごとに根拠のfile:lineを添える。
