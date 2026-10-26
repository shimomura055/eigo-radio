# SPEC_LEDGER_01: ユーザー採用表 -> 実装項目の対応(KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01)

管理ID: KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01 / 2026-10-26 / 性質: 設計確定+DEV実装+test(API 0)。到達Status=DESIGN_FINAL+DEV_IMPLEMENTED(PRODUCTION_WIREDではない。配線は委任_02、判定はFable)。
ユーザー原文(逐語)=`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_USER.md` §2。

## 1. 採用表(APPROVED_FOR_PRODUCTION 2026-10-26)と実装

| ユーザー決定(原文§2表) | 実装項目 | 実体(file:関数) | test |
|---|---|---|---|
| 時制・活用形: 本文との対応を確認でき、正しく原形化できる場合は救済 | (a) revert(表層形維持) / (b) M1限定再導出(display窓内で{display語,LLM提案語}) / (c) D1再アンカー(本文表層へ戻して正規canonicalization) | `er125_kp_rescue_production_01.py`: `rescue_canonicalization_item`/`rederive_m1`(a,b)、`rescue_selection_item`/`reanchor`(c) | TestEleven #4 #5 #11、TestAdversarialNoFalseAccept |
| 時制・活用形(通常フローで落ちていた分): `studied separately`/`had our eye on`/`rang through`/`have a say` | 区分1の是正(副詞後続guard・have役割判定・過去形表補完) | **適用済み**=845cfcb0a(`er105`:689-697,885-1029)。回帰=`er105_kp_rule_compliance_test_01.py` | TestEleven #2 #3 #6 #10 |
| 慣用句: 助動詞等の機械的判定で不当に除外される自然な慣用表現を救済 | 一般機構=辞書見出し(Wiktionary English idioms 10,661見出し)+構造条件(助動詞始まり・倒置/疑問文/断片/名詞主語を除外)+除外表(スラング/侮蔑10件)。主語`it`だけを除去して核を選定(`it can't be helped`->`can't be helped`) | `er125`: `idiom_exception`/`idiom_aux_exception_applies`(H1)/`rescue_selection_item`(H2) | TestEleven #7 #9、TestIdiomMechanism、TestLexiconFailClosed |
| 5語以下: 制限維持。6語以上を意味のない短縮で救済しない | 短縮救済(A1)を実装しない。選定段で語数理由を含む除外は救済対象外 | `rescue_selection_item`(語数理由を見つけた時点でNone) | TestEleven #1 |
| 本文にない語の追加: 不採用 | スロット一般化(A2 `too soon to do`)を実装しない。M1再導出はLLM提案語/display語のみ=新語形を作らない | `rederive_m1` | #1、TestAdversarial |
| 発音辞書未登録語の分解救済: 不採用 | CMU未登録(`redelivery fee`)は救済しない。救済後keyもCMU検査(`_gate`) | `_gate` | #8 |
| 既存仕様に反する実装条件4件: 承認済み仕様に合わせて是正 | 3件=適用済み(845cfcb0a)。残り1件=**量化詞限定詞guard**(`accepts no responsibility`)を本委任で是正 | `er105_kp_fulltext_selector_01.py`:`_QUANT_DET`/`_quant_follow_ok`、`_token_pair_ok`の1分岐 | `er105_kp_rule_compliance_test_01.py::test_quant_determiner_guard_applied_positive_and_negative`、`quant_parity_01.json`(parity true)、`quant_newly_accepted_01.json`(実データ新規受理0) |
| Human NGは救済で復活させない | `ng_blocked`(原句・救済形の両方を`match_ng`で照合)。救済候補も既存`auto_eligible_now`のNG判定を通る | `er125.ng_blocked` | TestHumanNgNotBypassed |
| 個別5表現の例外登録ではなく一般的な仕組み | 27件閉表を廃止し辞書+構造条件の汎用判定へ | `idiom_exception` | IDIOM_LEXICON_01.md |

## 2. Fable解釈(委任文)の確認と影響

1. **A1短縮救済は不採用**: `too soon to wave a flag`(#1)は除外のまま(外側retryで別候補)。影響=11件中1件が救えない。ユーザー表の「6語以上を意味のない短縮で救済しない」と「5語以下 制限維持」を狭義(意味が狭まる短縮も含む)に解釈した。広義(意味を保つ短縮は可)を採るなら新Prompt/新仕様=ユーザー判断が必要(本委任では判断候補にしない=Fable解釈どおり)。
2. **A2スロット一般化・CMU分解は不採用**(ユーザー表どおり)。
3. **慣用句の一般機構**: 委任文の候補(i)辞書見出し照合を採用。(ii)規則のみ=誤受理リスク高で不採用、(iii)LLM判定=非決定論・費用で不採用。理由とQCD比較=DESIGN_03 §2。
4. **HRなし経路**: 推奨β(QA再判定あり=品質優先)を既定にした。理由=DESIGN_03 §4。

## 3. Opus台帳の本設計での反映状況(台帳自体は編集しない。Fable sync用)

| ID | 指摘 | 本設計での反映 |
|---|---|---|
| OF-KPRS-M1 | 再導出は{display語,LLM語}の選択のみ(誤った基本形を採らない) | **採用・実装**: `rederive_m1`(新語形を生成しない)。test: 敵対的reject全件がrevertのみ(`increase supply`等を決して採らない) |
| OF-KPRS-M2 | HRを経ない経路への意図しない有効化 | **変更して採用**: 有効化は`generate_candidates`がcanon_fnへ渡す明示引数(`rescue=True`)のみ。`run_key_phrases`系・A/B/C・旧候補なし経路にはhookを渡さない(バイト同一)。ユーザー採用により『既定OFF』ではなく『generate_candidatesで既定ON+kill switch』(DESIGN_03 §6) |
| OF-KPRS-M3 | gloss再整合は表示候補に無い語がある場合しか動かない | **採用・実装**: `force_gloss_realign`(救済rankを強制対象にする。承認済みgloss規則・Gateはそのまま) |
| OF-KPRS-M4 | LLMのqa_*欄は救済前keyへの判定。PASSと見せない | **採用・実装(拡張)**: 救済後に承認済みfulltext canonicalization promptを無変更で使ってQA 12項目を再判定(`qa_rejudge`)。再判定できなければ`RESCUED_QA_NOT_REJUDGED`でauto不可。成功時のみqa欄を置換 |
| OF-KPRS-M5 | 外側retry判定で救済句を数える/累積除外しない | **Fable判断で変更**: 救済に成功した句はdropped[]に入らない=`gate_dropped`に数えない(委任文§5)。救済失敗のみ従来どおりdropped+F1累積。Opus再確認依頼=OPUS_REVIEW_REQUEST_03 ④ |
| OF-KPRS-M6 | 救済内のvalidator引数は最終Gateと同一 | **採用・実装**: `_gate`(allow_inflection_normalization=True・original_span・role_ok_poss)。引数shaを`validator_args_sha256`で永続化 |
| OF-KPRS-R1 | トリガーをRule7以外のkey起因違反+CMU post-canonへ拡張 | **採用・実装**: 最終Gate不合格またはCMU未登録なら発動 |
| OF-KPRS-R2 | 2c(短縮)採用時の歯止め | **N/A**(短縮不採用) |
| OF-KPRS-R3 | 外側retry・call1 retryで消えた句をdropped/inventoryに記録 | **未実装(観測のみ・範囲外)**。OPEN候補(実害なし) |
| OF-KPRS-R4 | 必須test3件 | (1)誤った基本形を採らない=TestAdversarialNoFalseAccept (2)HRなし/旧経路の分離=`test_non_fulltext_items_untouched`+TestUnwiredInProduction+DESIGN_03 §6 (3)救済あり/なしでgate再試行数が増えない=`test_gate_passes_after_rescue_without_retry`(ただし外側retry判定はM5変更に従う) |
| OF-KPRS2-M1 | -ly名詞の誤受理 | 適用済み(845cfcb0a)。本委任で再確認(敵対的22 conversions) |
| OF-KPRS2-M2 | 不変化分詞・量化詞介在のhave誤判定 | 適用済み(845cfcb0a)。量化詞限定詞guardは本委任(区分1) |
| OF-KPRS2-M3 | 慣用句例外が名詞主語のことわざ・完全文を通す | **採用・実装(方式変更)**: 27件閉表->辞書+構造条件。名詞主語/疑問文/完全文/断片を構造条件で除外(敵対的15件+追加18件で固定) |
| OF-KPRS2-M4 | A2を区分3で閉じない | 不採用(ユーザー表: 本文にない語の追加) |
| OF-KPRS2-R1 | OPEN-152は部分解消 | 維持(A/B/C不変) |
| OF-KPRS2-R2 | Productionは決定論のみ | 維持(新LLM評価者は作らない。QA再判定は承認済みprompt・schemaの再利用) |
| OF-KPRS2-R3 | 過去形補完から同形異義語除外 | 適用済み(845cfcb0a) |
| OF-KPRS2-R4 | SCOPE_WORDS拡張 | N/A(短縮不採用) |
| OF-KPRS2-R5 | 縮約形全般の測定 | **未是正**(ASCII `can't`すり抜け・curly拒否の既存挙動は不変。慣用句例外はcurly/ASCII両対応で救う)。OPEN-529追記候補(修正へ進む・範囲外) |
| OF-KPRS2-R6 | LLM評価の限界/モデル記載 | N/A(LLM評価者なし) |
