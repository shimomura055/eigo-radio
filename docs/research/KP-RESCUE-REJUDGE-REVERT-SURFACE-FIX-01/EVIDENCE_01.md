# KP-RESCUE-REJUDGE-REVERT-SURFACE-FIX-01 委任_01 EVIDENCE_01(OPEN-633)

Status: 修正完了・検証済み、Fable受入待ち。種別=不具合修正(承認済み救済仕様との矛盾の是正、PM_GOVERNANCE 11-8)。新Gate/QA基準緩和/Rule7・canonicalization変更/N5 Prompt変更なし。

## 1. 原因(OPEN-631 AUDIT_01 §4-1で特定、本委任で再確認)
canonicalizationが見出し形`get heated`を返す -> Rule7不合格 -> 救済`REVERT_SURFACE`(`er125_kp_rescue_production_01.py:42`)で表層形`gets heated`へ戻す
-> 救済済み項目のQA再判定でLLMが再び見出し形を返す -> 旧`_norm_lc(r.key_phrase) != _norm_lc(key)` -> `NOT_REJUDGED`(`error=key_mismatch_or_invalid_fields`)
-> `er119_kp_human_review_01.py:540`(rescue_unverified)のfail-closedで提示されない。承認済み『活用形は表層形へ戻して候補を残す』が一致条件で常に無効化されていた。
再現(修正前コードに同一生応答を与えるAPI 0 replay): 5/5(下表)でNOT_REJUDGED。永続化run記録(`work/keywords_canonicalized.json`の`rescue.qa`)も同じ5件がNOT_REJUDGED。

## 2. 変更(`er125_kp_rescue_production_01.py`)
- `_headword_of_same_item`(:506)新設: 救済前の見出し形が表層形と同語数で、各語が同一/語幹共有(共通接頭辞3以上)/既存不規則形表(`ft._PAST_ONLY_IRREGULAR`等)の対応のときだけ『同じ項目の活用差』とする。辞書追加なし・決定論。無関係語句を同一項目として受けないための保守的確認。
- `_revert_origin_key`(:522)新設: REVERT_SURFACE項目の救済record値(`kp_rescue.llm_key_phrase`、または`alt_keys_by_rank`)を返す(REVERT以外・表層形と無関係はNone)。
- `qa_rejudge`(:535)に任意引数`alt_keys_by_rank`、一致条件(:558-565)を『表層形key または 上記の見出し形』へ(rank一致=pseudo rank位置は従来どおり必須)。verdict計算(`_qa_field_effective_verdict`)・NOT_REJUDGED返却・fail-closedは不変。
- `finalize_rescued_items`(:599)がREVERT項目の`llm_key_phrase`を渡す。
- test: `er125_kp_rescue_production_test_01.py` `TestQaRejudgeRevertSurfaceKey`(:753、10件)。

## 3. 検証
### 3-1 単体(API 0)
- 新10件: 見出し形=同一項目 / 表層形 / 無関係語4種(`get hot`等)=NOT_REJUDGED / rank不一致=NOT_REJUDGED / 一致してもQA FAIL=FAILのまま(REVIEW_REQUIRED) / QA欄不正=NOT_REJUDGED / 非REVERT・record無し=従来どおり / 項目別(別項目の見出し形を受けない) / 救済前keyが表層形と無関係(`totally different`等)=受けない / 活用差判定の可否表。
- 新10件のうち修正前コードで落ちる5件(見出し形・非REVERT対比・QA FAIL保持・項目別・活用差判定)を、修正前コードで実行して確認(残りは従来挙動を固定する回帰)。
- 既存`er125_kp_rescue_production_test_01` 58件 + 新10件 = 68件 OK。
- 関連既存test(er119 hr_selection_flow/rescue_wiring/human_review/backfill/x_wiring/z_wiring/human_review_outputs/human_review_cli/p7w5/isolation/grammar_review, er138 n5_generalization/wiring, er105 fulltext_selector/rule_compliance, er108 cmu_gate, er124 phrase_word5): 修正前(origin/main版er125)と修正後で失敗名・件数が**完全一致**(新規失敗0)。両者に残る失敗(`er119_z_wiring`の15 error、isolation系の`test_no_production_file_references_er105`等5件)はsparse checkout環境の資材不足/全repo走査由来で、修正前コードでも同一。
  途中、ガード追加前の初版では`er119_kp_human_review_01_test_01.test_outer_retry_replaces_list_when_auto_lt3`・`er119_kp_backfill_test_01` TBF20 s04が新規失敗(testのmockがQA再判定でも救済前の無関係key`totally different`を返し、それが『同一項目』として受理されたため)。これは『救済前keyが表層形と無関係なら受けない』確認(`_headword_of_same_item`)の必要性を示す実例で、ガード追加後は既存testを変更せずPASS(testの期待値は変更していない)。
### 3-2 実データreplay(公式経路 `finalize_rescued_items`->`qa_rejudge`、実API 1 call/ケース、記事・音声・canonicalization・gloss・選定の再生成なし)
入力=永続化済みrun記録(`er019_output/.../kp_candidates/round_1/work/keywords_canonicalized.json`+同dirの`canonicalization_prompt.txt`の本文)。モデル=gpt-6-luna(run記録のQA再判定と同じ`B1_SUPPORT`既定。最新世代の既定ルーティング)。
修正前=origin/mainのer125に**同じ生応答**を与えた判定(API 0)、修正後=本修正版(実API)。スクリプト=`ev01/run_replay_rejudge.py`、結果=`ev01/replay_result.json`。

| 事例(run) | 表層形key | 救済前の見出し形 | QA再判定でLLMが返したkey | run記録 | 修正前replay | 修正後 |
|---|---|---|---|---|---|---|
| ai_chat b1b | counted as having failed | count as having failed | count as having failed | NOT_REJUDGED | NOT_REJUDGED(rescue_unverified) | **PASS**(12欄PASS、提示可) |
| jwst a2 | limited the search to | limit the search to | limit the search to | NOT_REJUDGED | NOT_REJUDGED | **PASS** |
| untidiness a2 | gets heated | get heated | get heated | NOT_REJUDGED | NOT_REJUDGED | **PASS** |
| untidiness a2 | relied | rely | rely | NOT_REJUDGED | NOT_REJUDGED | **PASS** |
| untidiness b1b backfill | gets heated | get heated | get heated | NOT_REJUDGED | NOT_REJUDGED | **PASS** |
| (対照)ai_chat b1b | rate at which | rate at which participants choose | rate at which(表層形) | PASS | FAIL | **FAIL**(qa_standalone_natural_unit/comprehensibility/context_sufficiency=REVIEW_REQUIRED、提示されない) |

- 5件は修正前NOT_REJUDGED->修正後にQA再判定が出てPASS。判定は無条件通過ではなくLLMのQA 12欄に従う。対照`rate at which`(従来から表層形で一致する項目)は修正前後で同一判定、今回の応答ではQA FAILで正当に落ちる(同じ項目の以前のrun記録はPASSだった=LLM判定の揺れ。本修正の対象外)。
- 初版(ガード追加前)のreplay(`ev01/replay_result_v1_before_headword_guard.json`)も同じ5件がPASS(対照のみLLM揺れでPASS)。ガード追加後に再実行し、5件が同じ結果であることを確認(最終版の証跡は無印)。
### 3-3 失敗経路(test固定)
LLMが別語を返す(`get hot`/`get angry`/`heated`/空)・rank不一致・QA欄不正・見出し形が表層形と無関係・REVERT以外の救済・救済record無しの素のitem: すべて従来どおり`NOT_REJUDGED`(error=key_mismatch_or_invalid_fields)->`rescue_unverified`で提示されない(fail-closed)。QA FAILは`REJUDGED_FAIL`のまま。

## 4. 費用・安全
- 実データreplay: 初版¥0.896 + 最終版¥1.092 = **約¥1.99**(個別Cap ¥10内、`ev01/cost_summary.json`、4 call×2)。記事・音声再生成0。日次1,000円内。
- STOP確認: `ev01/stop_check_*.json`(開始時・各有料run前にrc 0)。
- Production到達: 既定ON経路(Family X/Z KP救済)の不具合修正。新flag・新Gate・Prompt/正規表現/閾値/辞書の編集なし(`_HEADWORD_MIN_COMMON_PREFIX=3`は新設の局所定数で、既存規則の閾値ではない)。
- 影響範囲: 既存の保存済みrun記録は不変(次回生成から有効)。他callerの`qa_rejudge`(surname choice/gloss requalify系tool)は`alt_keys_by_rank`未指定かつ`kp_rescue`無しのitemでは挙動不変。

## 5. 残る限界・判断候補
1. 再判定はLLMが見た見出し形(例`rely`)のQA判定を表層形(`relied`)の判定として採用する(承認済み救済仕様の枠内。QA 12欄は表層形そのものを見た判定ではない)。厳密に表層形でQAさせたい場合は、QA再判定メッセージでkey_phraseを逐語で返すよう指示する案(承認済みPrompt変更を伴うため本委任では実施せず)。
2. 活用差の同一項目確認は保守的(語幹共有3文字/既存不規則形表)。表に無い不規則形(例`go`/`went`は表に有り、`be`系も有り。未登録の稀な不規則動詞)は従来どおりNOT_REJUDGED=提示されない(悪化なし)。
3. 既存run(untidiness a2/b1b等)の記録は再生成していない。`gets heated`等を選定UIに載せるには該当runの再生成(別委任・Fable判断)が必要。
