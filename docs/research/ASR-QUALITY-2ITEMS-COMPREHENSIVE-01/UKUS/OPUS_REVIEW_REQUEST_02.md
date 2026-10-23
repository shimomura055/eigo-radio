# OPUS_REVIEW_REQUEST_02 -- ②英米綴り(UKUS) Production配線設計 Opus条件C独立レビュー依頼
(2026-10-23 / UKUS 委任_03 / 条件C=重要変更のProduction採用提案前[PM_GOVERNANCE 11-3]。Fableが依頼を中継する。レビューは設計に対して行い、実装は次委任)

## 依頼対象
`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/WIRING_DESIGN_01.md`(配線点表W1〜W15、flag/隔離、対表同梱、test/evidence計画、①RETとの整理、c12 LR解除手順)。
背景: ユーザーが①RET・②UKUSのX/Z共通Production採用を承認済み(2026-10-23、UDR #168)。**判定ロジック・固定対表・安全条件はTrial(OPUS_REVIEW_01 OF-UKUS-01〜14反映済み、VALIDATED[Fable])のままで、本レビューはそれをProductionへ移す「配線」の妥当性**が対象。仕様の是非ではない。

## 参照
`TRIAL_RESULT_01.md`、`DESIGN_02.md`、`OPUS_REVIEW_01.md`、`er111_ukus_spelling_trial_01.py`、`er109_asr_orthographic_equivalence_01.py:709-764`、`er109_xz_scope_01.py:97-139,195-283`、`er078_reuse_value_guard_01.py:58-66`、`er063_family_z_audio_01.py:748-796`、`er109_wiring_golden_test_01.py`。

## 論点(条件C。優先順)
1. **hook自動伝播の確認漏れ**: 「Production内で`e109.evaluate`を直接呼ぶのは`_evaluate_cached`のみ、他hookは全て`decision()`経由」(付録A)という前提に漏れがないか。`decision()`を経由せず`explain_protected`や`record_site`等で`eq`を再評価・再利用する箇所、`SpanRecord.rule`をrule名で分岐する箇所(Grep上は`multiword_homophone_er094`/`compound_spacing`がoffline toolにのみ)、`eq.warnings`と`PASS_WITH_WARNING`/`ORTHO_*`写像の副作用の見落とし。
2. **LAYER_VERSION/golden更新の副作用**: version bumpで(a)保存済みentryの再利用可否が変わらないこと(§4-3の根拠は妥当か)、(b)golden fixture再作成で「scope無し完全一致」「X/Z変化行の全件分類」が保てるか、(c)versionをcache keyや比較に使う見落とし、(d)auditキー追加を「UKUS適用時のみ」にした設計の妥当性。
3. **構造変更の同等性**: Trialは「`evaluate`後に別関数で再整列」、Productionは「`evaluate`のopcodeループ内で不合格spanだけ局所救済」へ形を変える。既存PASSのバイト同一(単調性)と、Trial⇔Production差分test(保存6,137行+合成)で十分に同等性が担保されるか。ループ内救済でspan単位の`SpanRecord`の粒度(位置ごと)が既存のspan集計(`explain_protected`のspans走査)を壊さないか。
4. **entity除外の実装位置**: canonical側の固有名詞らしさ判定を`rescue_span`内に置き、①RETの表を参照しない設計(`evaluate`の純関数性とLRU cacheを守る)で、①②両方ON時に固有名詞を取りこぼし/誤同値しないか。将来RET共有する場合のcache key設計の注意。
5. **c12 LR上書き解除手順の安全性(§9)**: 当該1clipの結果entry無効化のみで足りるか(Master Audio Store・`review_lock_state`累積カウンタ・budget_guard・`attempt_history`・Z結果再利用の他経路が`forte`音声を再利用する可能性)。誤って他clip/HR Lock/他levelのentryを巻き込まない担保。失敗時の復元手順。
6. **①RETとの干渉**: 共有ファイル(`er109_xz_scope_01.py`/`er078_reuse_value_guard_01.py`/test許可リスト/SSOT)のcommit順、両方ON時の相互作用(T-K)、PASS種別の衝突(`PASS`[②] vs `PASS_WITH_PRONUNCIATION_ALARM`[①])。
7. **flag設計**: 既定ONの単一定数、親flag従属、`evaluate(ukus=)`引数をxz以外が渡さないAST固定、UKUS flagのみOFF時のStore再利用ブロック(W11)の妥当性と過不足。
8. **回帰・受入**: 受入条件9項目(原文`USER_02.md`)に対するtest/evidence計画(§6/§8)の不足。特にX側に保存NG事例が無い状況でのXの発火証拠(合成+実TTS 1clip+「発火しない事実の記録」)が「正式runtimeでの発火証拠」として十分か。

## 期待する出力
OF-UKUS-W-xx形式で、必須(実装前に設計修正)/推奨/情報に分類。GO/条件付きGO/NO-GOの総合判定。Fableが照合のうえ、11-3のSTOP条件に該当しなければFable判断で次工程(実装委任)へ進む(Opusレビュー自体はユーザー承認Gateではない。Production採用の承認は既にユーザー済み。PRODUCTION_WIRED判定はFable受入後)。

## 前提として明示する制約
コード変更0・API 0円(本依頼まで)。A/B/C凍結。`er111_*`は実装時にコピー元として読むだけで、Productionから参照しない。①RET側ファイルは編集しない。
