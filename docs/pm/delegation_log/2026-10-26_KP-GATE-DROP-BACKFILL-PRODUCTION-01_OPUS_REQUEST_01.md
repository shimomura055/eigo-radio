## 依頼種別

Opus独立技術レビュー(PM_GOVERNANCE 11-3 条件A: 新処理フローの実装前レビュー)。対象=KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_01の設計(commit f5d466617)。read-only。結論は返信本文で(Fableが転記)。

## 背景(ユーザー承認済み、APPROVED_FOR_PRODUCTION、2026-10-26)

「GateでNG除外されたフレーズ・単語候補の不足分補完」: 補完はAIが一度選定した候補が後続GateでNG除外された場合に限る(初回選定件数が上限未満という理由では発動しない)。補完件数=実際にGateで除外された件数。対象はフレーズ・単語。初回に合格した候補は保持し、再生成・入れ替えをしない。除外件数だけ追加探索、重複・同じNGの反復防止、補完候補にも承認済みGate適用、品質基準緩和禁止、反復回避、補完後の上限未達は許容。KP救済方式との処理順序を確認し、救済で残った候補を除外と数えない。HR限定候補・Human NG・retry・fallback・resume・再生成と整合。単語優先順位①本文一致②1語③上級者向け④易語除外⑤単語単体価値(必須でない)を厳守。含有語の重複扱いは既存Gateと整合(未承認のGate緩和なし)。新Prompt・採用枠・Gate変更が必要なら既存承認と区別して報告。7+5候補生成PromptのProduction採用は自動確定しない。原文全文=`docs/pm/delegation_log/2026-10-26_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER.md` §3〜§6。

## 読む物

1. `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/OPUS_REVIEW_REQUEST_01.md`(P1〜P10)
2. 同dir `DESIGN_01.md`、`CURRENT_FLOW_01.md`、`TEST_PLAN_01.md`、`EVIDENCE_PLAN_01.md`(必要箇所)
3. 現行コード(Grep→該当範囲): `er119_kp_candidates_01.py:157-375`(`_generate_candidates_impl`、外側retry `n_auto<3 and (gate_dropped or rescued_not_auto)` :347-371)、`er105_kp_fulltext_selector_01.py:456-531`(call1のattempt内全件再選定 MAX_ATTEMPTS=2)、`er119_kp_prompt_2v_01.py:19-98`、`er119_kp_human_review_01.py:49,536-554,1272-1345`(auto_select先頭3/5、resume読み戻し)、`er125_kp_rescue_production_01.py`(救済の順序、`rescued_not_auto`)、`docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/DESIGN_03.md` §1・§5

## 論点

- P1〜P10(依頼文のとおり)。特に:
  - **P4 外側retry R1**: 現行の外側retry(`n_auto<3 and gate_dropped`で候補全件を再生成・置換、Fable/Opus設計M-7c、CURRENT_SPEC記載なし)は、承認原文「初回合格候補を保持し再生成・入れ替えをしない」と矛盾する。設計案=`gate_dropped`脚を撤去して補完へ置換、`rescued_not_auto`脚は残す。この是正を「承認済み仕様との矛盾是正(11-8範囲内)」と扱ってよいか、それとも承認済み挙動の変更としてユーザー報告が必要か。`rescued_not_auto`脚を残す場合、救済済みHR限定候補だけが多い(auto<3)ケースで全件再生成が走り「初回合格保持」に反しないか。
  - **P5 call1 K0/K1**: `er105`のattempt内全件再選定(1件不合格で3件再選定)も入れ替え機構。是正案K1(後方互換keyword-only引数)の影響範囲とリスク、K0(据置)で原文との矛盾が残るか。
  - **P1/P2 除外の定義**: 許可リスト(validate/duplicate_of_top3/cmu/canonicalization/cmu_post_canon/symbol/src_d1/human_ng/excluded)の妥当性。`human_ng`(ユーザーがHRでNGにした句)を「Gate除外」に数えて補完するのは原文の意図(Gate NG除外)に合うか。`duplicate_of_top3`(含有語)を数えることの妥当性(Gate維持の前提)。
  - **P3 Prompt再利用**: Prompt 2-V再利用(`already`に現存+救済前元句、除外句は`build_exclusion_note`、件数文言なしでGate通過後先頭N件)で、2-Vが最大5件返す→N件だけ採る設計の無駄(余剰候補の扱い=捨てる? HR限定候補として残す?)と、「同じNGの繰り返し防止」の実効性(除外理由を渡しても同型のNGを返す可能性)。
  - **P6/P7**: 重複判定の正規化(表層/原形/大小文字)、resume(補完結果の読み戻し)・`--regenerate-stage`・HR Lock・補完call失敗時の継続(新STOPを作らない)の妥当性。
  - **P8**: 単一読取関数`backfill_enabled()`既定ON(承認済み仕様)、`"0"`で外側retry条件も含めて現行へ完全復帰する設計の安全性。A/B/C不変の確認方法。
  - **Fable追加F-1(単語枠)**: 現行Productionには単語専用選定がなく(Adv単語解説は同一プール先頭5)、「単語」の補完は将来7+5採用時のslot抽象で対応する設計。承認原文「対象はフレーズ・単語の両方」に対し、現行経路でのこの扱いが妥当か(ユーザーへ区別報告すべき事項か)。
  - **Fable追加F-2(選定フォームとの関係)**: 並行で選定フォームv3(フレーズ最大7・単語最大5表示、①②③累積上限)を実装中。補完後の候補数・HR限定旗・救済旗をフォームが受け取るデータ契約として、設計に不足がないか。

## 出力形式

1. 結論(GO / GO with changes / NO-GO)+理由3行
2. 論点別判定表(P1〜P10、F-1〜F-2): 判定、根拠(ファイル:行)、必須修正M-番号/推奨R-番号
3. ユーザーへ区別報告すべき事項(承認範囲外・挙動変更に当たるもの)の列挙
4. 見落としリスク
5. 5行要約

推測で断定しない。未確認は未確認と書く。