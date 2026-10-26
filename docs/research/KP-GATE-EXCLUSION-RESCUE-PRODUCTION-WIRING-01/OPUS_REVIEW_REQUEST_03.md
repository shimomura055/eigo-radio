# OPUS_REVIEW_REQUEST_03: 変更部のみの独立技術レビュー依頼(Opus条件A・Fableが委任_02前に依頼)

管理ID: KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 / 2026-10-26。既レビュー済み: `KP-GATE-EXCLUSION-RESCUE-DESIGN-01/OPUS_REVIEW_01.md`(M1〜M6/R1〜R4)、`…DESIGN-02/OPUS_REVIEW_02.md`(M1〜M4/R1〜R6)。
本依頼は**前回レビューから変わった部分だけ**。見る資料: `DESIGN_03.md`(§2〜§6)、`er125_kp_rescue_production_01.py`、`er125_kp_rescue_production_test_01.py`(53件)、`idiom_exception_listing_01.json`、`rescue_eval_prod_01.json`。Production未配線・API 0。

## 変更点と、レビューしてほしい論点

### ① 慣用句の一般機構(27件閉表 -> 辞書見出し+構造条件)  [最重要]
- 変更: Opus-02 M3が承認した『人手レビュー済み27件の閉表』を廃止し、Wiktionary English idioms(10,661見出し)の見出し一致+構造条件(助動詞始まり・be系除外・倒置/疑問文除外・中身語1以上・先頭itのみ除去)+除外表10件に置換(ユーザー要件『個別5表現でなく一般的な仕組み』)。
- 論点: (a)構造条件で名詞主語のことわざ/完全文/疑問文/断片を漏らさないか(敵対的15件+追加18件で固定、辞書全体で116件が構造条件を満たし25件が判断を変える。25件の目視確認を依頼)。(b)辞書に残るスラング/侮蔑語の取りこぼしリスク(除外表10件は旧レビュー由来で閉表)。許容できるか、より機械的な防止(例: 辞書メタの語義ラベル取得)が必要か。(c)`come what may`型の内部助動詞を『先頭come限定』にした判断。(d)`it`のみを主語として除去する判断(that/there/名詞主語は除去しない)。(e)辞書sha二重ピン+fail-closedで十分か。

### ② HRなし(自動採用)経路での救済候補の扱い
- 変更: Fable設計§4βを既定化。canonicalization段の救済(revert/M1)は、gloss強制再整合=REALIGNED かつ QA 12項目再判定=PASS のときだけ`auto_eligible`維持。選定段の救済(D1/慣用句の核)は救済後の通常canonicalization(gloss・QA込み)を通るので追加条件なし。DESIGN-01 M4(『QA欄を上書きしない・未再判定と表示』)を拡張し、再判定できたときだけQA欄を置換。
- QA再判定の方式: 新Promptを作らず、承認済みfulltext canonicalization prompt/schemaに、救済後keyを`display_phrase`として渡して12項目を判定(返却keyが一致しなければNOT_REJUDGED)。論点: (a)『display_phrase=救済後key』で得たQAは、元の本文表層->救済後keyの関係(意味保持・過剰短縮)を判定したことにならないが、救済後keyを学習単位として評価する意味では妥当か。(b)`qa_traceable_contiguous_span`を実際の(key, display)組の承認済み有効判定へ再計算する扱い。(c)再判定できない/失敗時にHRでのみ採用可とする安全側設計で足りるか。

### ③ 既定ON化と対象経路
- 変更: DESIGN-01 M2の『既定OFF・明示引数』から、ユーザー採用に伴う『`generate_candidates`経由で既定ON(kill switch `EIGO_KP_RESCUE=0`)』へ。hookは4箇所(H1 `contains_finite_aux_role_based`、H2 `validate_and_resolve`、H3 `run_key_phrase_canonicalization(rescue=)`、H4 `annotate_candidate`)。論点: (a)H1が選定段とvalidatorの両方に効く(1関数共有)ことの副作用。(b)H2を`validate_and_resolve`の中に置く(call1/call2の共通choke point)ことで、`apply_exclusions`/`build_exclusion_note`(F1累積・LLMへの除外通知)との整合。(c)`rescue=True`が旧候補なし経路(`run_key_phrases`・Z `run_kp_with_outer_retry_fulltext`)へ漏れない構造か。(d)旧規則の撤去: `test_rescue_flow_not_wired_in_er105`の禁止トークン検査の改訂方針。

### ④ retry/resume一貫性(M5の変更を含む)
- 変更: DESIGN-01 M5は『救済句を`gate_dropped`相当として数えretry発動を維持』としたが、ユーザー指示(委任文§5)で『救済成功で候補が足りればretryしない』に変更(救済成功itemはdropped[]に入らない)。救済失敗のみF1累積。救済メタは候補ファイルに永続化し、resumeは再計算せず読み戻す(`candidates_sha256`は救済メタ込み)。論点: (a)retry抑制が品質に与える影響(救済候補はauto_eligibleでなければ`n_auto`に数えないため、n_autoが不足する場合は従来どおりretryする=品質を守る設計になっているか)。(b)canonicalization gate内retryを消費しない設計(parse直後・validate前の救済)の妥当性。(c)`verify_persisted_rescue`の自己整合のみで、読み戻した候補の信頼性として足りるか。

## 変更していない部分(再レビュー不要)
M1再導出の{display語,LLM語}限定、最終Gate同一引数(M6)、gloss強制再整合(M3)、区分1の是正3件(845cfcb0a)、Human NG不迂回、短縮(A1)・スロット(A2)・CMU分解の不採用。量化詞限定詞guard(区分1)の差分はer105の1関数+1分岐(parity true・実データ新規受理0・A/B/C golden 1002件バイト一致)。

## 期待する出力
各論点の採否(Must/Should/Optional)、Mustがあれば修正案。Opusレビュー後、Fableが11-3に従い照合のうえ委任_02(配線+runtime evidence)へ進む。
