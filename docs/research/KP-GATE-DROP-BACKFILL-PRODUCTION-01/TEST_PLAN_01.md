# TEST_PLAN_01: 補完機構のtest計画(委任_02で実装・実行。本委任は計画のみ)

方針: 全てLLM mock(`vocab_call_fn`/`select_fn`/`canon_fn`/`redundancy_fn`注入、既存`er119_test_support_01.py`のfake流儀)。API 0。不整合出力をassertしない。test名はTBFxx。受入条件(委任文§6の番号)対応を併記。

| ID | 目的 | 期待 | 受入 |
|---|---|---|---|
| TBF01 | 除外0 -> 補完不発動 | 初回8件(or任意)全通過、E=0。補完call回数0、`backfill.triggered=false`、候補sha・出力が補完機構OFF時と同一 | 3 |
| TBF02 | 初回が上限未満(call2が4件返答、除外0)-> 不発動 | E=0。補完call0、候補7件のまま(AI島Adv型) | 4 |
| TBF03 | 初回が上限未満+除外あり -> 除外分のみ | call2が4件+validate除外1: E=1、補完call1回、追加最大1件。「5-4=1」の不足分は補完対象外であること(E=2なら最大2) | 4 |
| TBF04 | 除外2 -> 補完最大2 | E=2。LLMが5件返しても先頭2件のみ採用、余りは`backfill_surplus`にlog | 5 |
| TBF05 | 補完件数=実除外件数・上限超過なし | N=min(E, cap-現存)。候補総数<=`KP_CANDIDATE_MAX` | 5 |
| TBF06 | 救済成立は除外に数えない | 選定段救済(D1/慣用句の核)・canon段救済(M1/revert)が成立した句はdroppedに無く、E算定に含まれない。救済済み+auto不可(`rescued_not_auto`)も数えない。救済不成立のみ数える | 6 |
| TBF07 | HR限定候補(qa_fail/gloss_hr_pending/similar_to_ng)は数えない | 候補に残り、E=0なら補完なし | 6 |
| TBF08 | `duplicate_of_top3`は数える(Gate維持) | 除外に数え補完対象。補完候補が再びcall1と包含ならまた除外(Gate不変)。`_containment`の挙動が既存と同一(既存testの流用) | 5,6 |
| TBF09 | overflowは数えない | call2が6件返答(最大5件超)-> overflow分はE外 | 5 |
| TBF10 | 補完は1回だけ | 補完候補が全て不合格でもcall数は補完1回(+技術再試行のみ)。再補完・累積除外更新による再callなし。上限未達を許容 | 5 |
| TBF11 | 補完候補への同一Gate再適用 | 補完候補が語数6/CMU未登録/本文不一致/finite aux -> 除外(基準不変、緩和なし)。救済機構は初回と同じ条件で成立 | 5 |
| TBF12 | 重複は捨てて補完しない | 返答が現存候補・救済前元句・除外句・Human NGと完全一致 -> 捨てる。Nに数えず、再callなし | 5 |
| TBF13 | 補完Promptの構成 | message=2-V本文(sha固定一致)+`already`(現存候補+救済前元句)+既存exclusion note。本文に件数文言なし。`prompt_prefix_intact`True | 8 |
| TBF14 | 初回合格候補の保持 | 補完前後で初回候補の`candidate_id`・`used_form`・gloss・`ai_rank`・`item`が不変(deep equal)。補完は末尾追加のみ。初回のcanonicalization出力ファイル不変 | 5 |
| TBF15 | Human NG | NG句を補完が返したら除外(選定段+canon後used_form+救済前元句)。similarは旗 | 6 |
| TBF16 | resume再課金0 | 補完込み`kp_candidates.json`を`ensure_kp_review`が読み戻し。generate_fn呼出0、LLM mock呼出0、`candidates_sha256`不変 | 6 |
| TBF17 | RESELECTION/STALE/regenerate | 新roundは初回選定から(補完もround内で新規1回)。旧round候補はSUPERSEDED。確定済みHRは再抽選しない | 6 |
| TBF18 | 外側retry条件(R1) | (a)Gate除外のみ+n_auto<3 -> 外側retryは起動せず補完。(b)call1/call2技術失敗・live0・canon全体失敗 -> 従来どおり外側retry。(c)`rescued_not_auto`+n_auto<3の脚は存続(現行どおり、補完分は破棄されうることをlog) | 6 |
| TBF19 | 補完call失敗は初回候補で続行 | 技術失敗2回 -> `backfill.status=FAILED`、初回候補採用、外側retry起動なし、新STOP無し | 6 |
| TBF20 | kill switch | `EIGO_KP_BACKFILL=0`で補完0かつ外側retry条件が現行と完全同一(既存testの期待値と一致)。未設定=ON。flag読取は`backfill_enabled()`の1箇所のみ(Grep test) | 7,8 |
| TBF21 | X/Y/Z配線(静的) | `_generate_candidates_impl`が唯一の配線点。X/Y/Zの呼出点がこの関数を経由すること、Family別の補完分岐が無いことをAST/Grep test(`er119_x_wiring_test_01.py`/`er119_z_wiring_test_01.py`流儀)。Zでは補完候補にもsrc_d1/人称整合 | 6 |
| TBF22 | A/B/C不変 | 補完moduleを`er119_isolation_test_01.py`のimport制限に追加。A/B/C golden(1002件)バイト一致。`er105`/`er003`/Prompt/辞書/閾値のsha不変(K1のkeyword-only既定False引数追加時は既定経路のgolden一致) | 7 |
| TBF23 | 単語優先順位の不侵害(7+5経路を将来採用時用) | slot抽象のword slotで補完`prompt_fn`が初回Prompt本体と同一shaを返す。補完tailにpriority文言を足さない(Grep test) | 3-3 |
| TBF24 | 純リファクタ回帰(`_gate_chain`抽出) | 抽出前後で既存`er119_*test*`全件PASS・同一入力で候補doc deep-equal(E=0経路) | 7 |
| TBF25 | 計数の決定論 | 同一入力3回でE・N・補完結果が同一(set順非依存) | 7 |
| TBF26 | 費用/ログ | `backfill`ブロックにtriggered/E/N/stage内訳/prompt sha/model_id/dropped。cost loggerに補完callが別行で記録 | 8 |

必須Regression(委任_02で実行): `er119_kp_human_review_01_test_01.py`・`er119_kp_rescue_wiring_test_01.py`・`er119_x_wiring_test_01.py`・`er119_z_wiring_test_01.py`・`er119_isolation_test_01.py`・`er125_kp_rescue_production_test_01.py`・`er105_kp_fulltext_selector_01_test_01.py`・`er105_kp_rule_compliance_test_01.py`・golden 1002件。K1採用時は`er105`のA/B/C既定経路のgolden。

撤去/更新が要るtest(委任_02で確認): 外側retryの`gate_dropped`脚を前提とするtest(`test_outer_retry_only_when_auto_lt3_and_gate_drop_M7c`、`test_shortfall_without_gate_drop_does_not_retry`の前者)は期待値を「補完へ置換」へ更新(不整合な旧期待値をassertし続けない)。残存Grep結果は委任_02のRESULT_PACKETで報告。
