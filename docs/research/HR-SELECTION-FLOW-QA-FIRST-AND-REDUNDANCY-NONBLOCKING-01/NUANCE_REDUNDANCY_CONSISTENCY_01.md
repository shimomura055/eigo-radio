# NUANCE_REDUNDANCY_CONSISTENCY_01(委任_03A 1節。ユーザー原文USER_02 §2)

判定基準(固定): 提示前(候補生成段階)の重複除外=承認済み仕様に適合 / 人間が選定した後に重複を理由に確定・TTS・assemble・Productionを停止する経路=承認済み共通仕様との矛盾(11-8、修正対象)。修正はer134/er128/exporter(form_logic.js・index.html)側のみ(runner本体は無変更)。重複以外のGateは維持。
結論: **不整合3件(選定後の重複停止3経路)を発見し全て修正**。ほか7項目は適合(修正なし)。

| # | 項目 | file:line(修正後) | 判定 | 修正 |
|---|---|---|---|---|
| 1 | 候補生成時: KP/Word重複(暫定選定①②との same_focus)=NG→候補0件(NO_CANDIDATE: overlap_ng)、judge不能=FAILED_TECHNICAL | er134_nuance_explanation_01.py:731(judge_overlap)・:758(decide)・:877(NO_CANDIDATE) | 適合(提示前の除外) | なし |
| 2 | 候補生成時: 文法Top1/Top2との重複=警告のみ(verdictに影響しない) | er134:758-(grammar_conflicts) | 適合 | なし |
| 3 | 提示poolの他候補との焦点重複(pool_conflicts)=旧「HRでそれらを選ぶと採用不可」 | er128_kp_confirmed_content_01.py:1785(旧: 交差があればraise_issue→確定拒否) | **不整合(選定後の重複停止#1)** | 修正: 交差はアラームとして記録のみ。`nuance_redundancy_alarms`(:1694、決定論・API 0)→`confirmed_nuance.json.redundancy_alarms`(:1809)+`nuance_redundancy_alarm.json`(:1816、0件でも書く)+cmd_from_form/`nuance-select`の戻り値(:1524,:2027) |
| 4 | V3フォーム: 採用+該当項目を①②で選ぶと送信/コピーを止める(`nuanceConflicts`→`nuanceBlocked`、`guard()`で拒否) | user_test/selection_form_v3/form_logic.js:67,73、index.html:96,135(旧guardのnc拒否) | **不整合(#2)** | 修正: `nuanceBlocked`は未決定のみ。重複は橙の「重複アラーム(確認用・送信は止まりません)」表示。guardから重複拒否を撤去 |
| 5 | ページ生成入口 finalize_stage: 確定後にKP/Word確定集合が変わると `NuanceStale`(『重複の最終確認が成立しません』)でSTOP | er134:1149-1154(旧: confirmed_against≠live_idsでraise NuanceStale) | **不整合(#3。X/Y/Z全runnerのページ入口=er019:4122/er121/er026経由で停止)** | 修正: 現在のlive集合に対し保存済みの候補判定(pool_conflicts/against[])から決定論でアラームを再計算し、`nuance_result.json`に`redundancy_alarms`+`final_overlap_check{verdict:alarm|pass, nonblocking:true, kp_word_set_changed_after_confirm}`を記録して続行(LLM 0)。引用改ざん/本文変化のNuanceStaleは維持(重複ではない) |
| 6 | HR依頼書(render_request_md)の文言「選ぶと採用できません」 | er134:1025 | 不整合(文言。#1の説明) | 修正: 「重複アラーム(確認用・非停止)」へ |
| 7 | 採用時の `overlap_check.verdict != pass` 拒否 | er128:1777 | 適合(候補段階の判定結果の整合検査。CANDIDATE docは構造上passのみ=:877) | なし |
| 8 | M-4 被覆検査: 確定①②のidが比較済み集合(against[])に無ければISSUE | er128:1781 | 適合(重複の判定結果ではなく『判定の対象外=ニュアンス候補と照合されていない』構造的欠落。フォームは提示poolから作るため通常は発生しない)。finalize側で同じ状況はアラーム(unjudged)として非停止 | なし |
| 9 | KP/Word提示pool同一性(pool_identity_sha)・候補shaの鮮度検査 | er128:1721-1732 | 適合(候補doc鮮度。提示した候補と別物を確定しないための検査で、重複判定ではない) | なし |
| 10 | 追加解説(②)・本文意味(③)・KP/Word相互の重複(ニュアンス以外) | er119_kp_human_review_01.py:572(redundancy_alarms)・:607(final_qa_to_alarm)・:848(op_select) | 適合(委任_02rで仕様②に対応済み) | なし |
| 11 | 文法解説とKP/Word/ニュアンス | grammar側に重複検査なし(er120_part2_grammar_production_01.py/er120_part2_wiring_01.pyをGrep: 重複停止0)。ニュアンス×文法=警告のみ(#2) | 適合 | なし |
| 12 | retry/regeneration/resume: `nuance-retry`は技術失敗(FAILED_TECHNICAL)の候補docだけ退避(er134:1088)、確定後の候補再生成は`guard_nuance`で拒否(er128:1868)、確定済みはn1_stageが生成0(er134:1052-)、finalizeは決定論(LLM 0・冪等) | 上記 | 適合(重複停止なし。resumeは全てアラーム形を再利用)。KP側resume(ALARMキャッシュ)も実LLM証跡あり=EVIDENCE_01 | なし |

X/Y/Z・Std/Adv: ニュアンスの経路は共通関数(`er134.n1_stage`/`er120_part2_wiring.finalize_nuance`/`er128._validate_form_nuance`)を3 runnerが呼ぶ(er019:4122、er121:598-604、er026経由)。runner側に重複停止のhook(例外catch・STOP文言)は無い(`NuanceStale`/`NuanceNotConfirmed`のcatchはer120_part2_wiring.py:469-471=引用改ざん/未確定のみ)。

## test
- 反転: `er128_nuance_hr_test_01.T2_CoverageAndConflicts.test_pool_conflict_blocks_adopt_when_that_item_is_chosen_but_not_otherwise` → `..._is_alarm_only_when_that_item_is_chosen_spec2`、`T7.test_pool_conflict_blocks_adopt_in_form_logic` → `..._never_blocks_in_form_logic_spec2`、`er134_nuance_runner_wiring_test_01.T3_Overlap.test_pool_conflict_chosen_at_hr_blocks_adoption_but_reject_is_accepted` → `..._is_alarm_only_adoption_proceeds_spec2`(旧期待値=採用拒否/ConfirmedContentIssue。仕様②が置換)。
- 新規: `test_redundancy_alarm_helper_is_deterministic_and_nonblocking_spec2`、`test_no_pool_conflict_records_empty_alarm_file_and_pass_spec2`、`test_kp_set_changed_after_nuance_confirm_is_alarm_not_stale_stop_spec2`。
- 候補段階の除外が不変であることは既存 `test_kp_word_overlap_is_discarded_before_hr_and_not_replaced`(T3_Overlap)・`er134_nuance_explanation_01_test_01`(45 OK)で固定。
- 撤去した旧規則: 確定時の `pool_conflicts` 交差ISSUE(`d("pool_conflicts", ...)`)、JS `guard()` の `nuanceConflicts` 拒否、finalize の `confirmed_against` 不一致 `NuanceStale`。残置: 候補段階NG(R_OVERLAP_NG)、文法警告、M-4被覆ISSUE、pool鮮度ISSUE、引用改ざん/本文変化NuanceStale。
