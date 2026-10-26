# OPUS_REVIEW_REQUEST_01: Gate除外補完機構(Production)設計の独立技術レビュー依頼(11-3 条件A)

対象: `DESIGN_01.md`(+`CURRENT_FLOW_01.md`/`TEST_PLAN_01.md`/`EVIDENCE_PLAN_01.md`/`BUDGET_PLAN_01.md`)。実装前レビュー。コード未変更。
前提: ユーザー原文§3-1〜3-3・§4(委任文に逐語)。7+5候補生成Promptのproduction採用は前提にしない(現行 call1 Prompt 2 + call2 Prompt 2-V と将来7+5の両対応の抽象)。
レビュー観点は各論点に「結論/根拠(file:line)/修正案」で回答を求める。

## 論点
- **P1 発動条件の判定点(救済との順序・除外の定義)**: DESIGN §2。除外=「AI選定itemのうち候補組立後`dropped`に残りstageが許可リストに入るもの」。救済(H2/H3)がdropped前に成立するため構造的に救済済みを数えないが、(i)選定段救済で原句が除外指定と一致した場合のR6処理、(ii)canonicalization INVALID->item除外->再実行の途中で救済が絡む順序、(iii)`rescued_not_auto`が候補に残る扱い、に取りこぼし/二重計上がないか。
- **P2 human_ng/excludedを除外に数える是非**: AIが再び選んだHuman NG/累積除外句を「Gate除外」として補完の対象に含める(DESIGN §2)。Human NG運用(reselect上限2、NG復活防止の多層)と矛盾しないか。数えない案との比較。
- **P3 Prompt 2-V再利用 vs 新Prompt**: 件数文言を足さず(1)`already`=現存候補+救済前元句、(2)既存`ft.build_exclusion_note`、(3)先頭N件をローカル採用、で足りるか。既存noteの「無理に3件に揃えず」の括弧書きが2-Vに添えて問題ないか。足りない場合の最小差分(件数1行note)は「新Prompt」と区別報告する扱いで妥当か。7+5のslotで「初回Prompt本体再利用」により単語優先順位①〜⑤・⑤非必須が構造的に保たれる主張は妥当か。
- **P4 外側retryとの関係(R1)**: `gate_dropped`脚の撤去(補完へ置換)・技術失敗retry存続・`rescued_not_auto`脚存続(DESIGN §9)。(i)これを「承認済み仕様(原文§3-1)との矛盾の是正=11-8の不具合(分類B)」とする判断は妥当か、それとも承認済み仕様の変更として扱うべきか。(ii)n_auto<3のまま確定する挙動(AUTOで`auto_select`「不足は不足のまま」)は品質上許容か。(iii)`rescued_not_auto`脚が残ると補完分を破棄しうるが許容か。
- **P5 call1のattempt内全件再選定(K0/K1)**: `er105_kp_fulltext_selector_01.py:530`。K1(後方互換keyword-only引数でitem除外->補完へ)の影響範囲(A/B/Cとの共有、`sc.run_key_phrase_selection`経由)、K0で十分か。K1を採る場合の安全な差分。
- **P6 重複・同NG防止の十分性**: 完全一致の機械破棄+Gate(`duplicate_of_top3`は現行のまま、現存候補全体への包含判定は新設しない)+RQA旗。補完候補が現存候補と包含/意味重複になる穴(Gateを緩めない前提での許容範囲)。補完1回のみで「同じNGの繰り返し」を抑えられるか。
- **P7 resume・regenerate整合**: 補完結果は`kp_candidates.json`に含み`ensure_kp_review`が読み戻す(再課金0)。STALE/RESELECTION/`--regenerate-stage`で初回からやり直し。`candidates_sha256`・HR確定済み候補の不変性・`rescue_provenance`との整合に漏れはないか。補完call失敗時に初回候補で続行(新STOPなし)は妥当か。
- **P8 A/B/C不変・kill switch・配線**: 単一配線点(`_generate_candidates_impl`)、`_gate_chain`抽出の純リファクタ安全性、`EIGO_KP_BACKFILL`既定ON(承認済み仕様のため11-7限定例外不要とする判断)。`er119`非import(A/B/C)と`er105`無変更(K0時)。
- **P9 evidence十分性**: EVIDENCE_PLAN(fresh 6 level-run+replay 6件、合計約¥21.5/上限¥30)で受入2〜8を立証できるか。replay(凍結初回+実補完)を「正式経路の動作証拠」とみなす区分は妥当か。足りない観測(例: 補完発動後のHR依頼書表示、Z SRC D1の補完候補適用)。
- **P10 コスト**: 補完1発動+約¥0.7〜1.0、`gate_dropped`脚撤去による外側retry減との差引。

## 参照
`CURRENT_FLOW_01.md`(現行事実)、`DESIGN_01.md §2,§4,§6,§9`、`er119_kp_candidates_01.py:157-375`、`er105_kp_fulltext_selector_01.py:456-531`、`er119_kp_prompt_2v_01.py`、`KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/DESIGN_03.md`、`KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/PROMPT_DIFF_01.md`、`KP_CANDIDATE_COUNT_CHECK_01.md`。
Opus台帳(`OPUS_FINDINGS_LEDGER.md`)への反映はFableがレビュー後に実施(本委任はSSOT編集権なし)。
