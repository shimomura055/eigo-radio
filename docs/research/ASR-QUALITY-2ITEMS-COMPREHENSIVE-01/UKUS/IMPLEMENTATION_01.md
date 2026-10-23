# IMPLEMENTATION_01 -- ②英米綴り(UKUS) Production実装(委任_04 / 2026-10-23 / commit 719de3adc、origin/main push済み)
承認: APPROVED_FOR_PRODUCTION(UDR #168)。対象=Family X/Z。A/B/C凍結。**PRODUCTION_WIRED表記はFable受入後**(X/Z双方のevidence必須。Z evidenceは後続B工程)。

## 変更ファイル(file:line、commit時点)
| ファイル | 内容 |
|---|---|
| `er109_asr_orthographic_equivalence_01.py:35-36,45,544-545,553-575,733-,774` | `UKUS_SPELLING_EQUIVALENCE_ENABLED=True`(rollback switch)、`LAYER_VERSION="er109_orthographic_equivalence_v2_ukus01"`、`ukus_is_enabled()`(親flag従属)、`EquivalenceResult.ukus_pairs/ukus_error`、`audit()`はUKUS適用時のみ`ukus_pairs/ukus_pairs_n/pron_differs_n/ukus_active/ukus_table_sha256`を追加、`evaluate(..., ukus=False)`: opcodeループで既存判定(bad/`_judge_span`)が不合格のspanだけ`rescue_span`を呼ぶ(遅延import、例外はv1へfail-closed)、`reason`=`all_diff_spans_phoneme_equal_or_ukus_variant` |
| `er109_ukus_spelling_01.py`(新規) | `PairTable`(sha照合)、`table()`(失敗状態cache)、`canon_entity_flags`(固有名詞らしさ、canonical側)、`rescue_span`(同数・全unitがword、位置別: 既存位置別判定→不合格位置のみ対表、CMU未登録位置はbad除外・音素注入なし、1位置以上が対表で同値化された場合のみ成立) |
| `er109_ukus_pairs_v1.json`(`git mv` R100)・`er109_ukus_pairs_build_01.py`(`git mv`) | 固定対表(6,361対active、内容不変)・開発ツール |
| `er109_xz_scope_01.py:36,97,105,122,155,186` | `UKUS_OUT_OF_SCOPE_BLOCK_REASON`、`is_ukus_active_for_run()`、`ukus_run_evidence()`、`_evaluate_cached(canonical,text,ukus)`(cache keyにflag)、`decision()`が`is_ukus_active_for_run()`を渡す(UKUS層errorはsinkへ記録)、`ukus_contributed(aj)`(W-03) |
| `er078_reuse_value_guard_01.py:78` | `ukus_contributed ∧ not is_ukus_active_for_run()`ならblock(既存ortho判定直後・`kp_vote_gate_follows`早期returnより前) |
| `er109_hr_lock_rejudge_01.py:72-73` | dirty検査対象に新module+対表json(W-06) |
| `er109_wiring_golden_build_01.py` / `er109_wiring_golden_test_01.py` / `er109_output/aho4_golden_01/*` | UKUS合成行14件追記・fixture再作成・UKUS行の期待値test |
| `er109_ukus_spelling_01_test_01.py`(新規 53件)/ `er109_ukus_spelling_01_test_cases_01.py` | 移植test(Trial 27件相当+W-01/03/12/10)、hook別(T-E1〜E5)、DefaultOnScope、固定expected(6,924件)、AST |
| `er109_xz_isolation_01_test_01.py`・`er109_asr_orthographic_equivalence_01_test.py` | Trial(`er111_ukus_*`)許可リスト撤去 |
| 撤去: `er111_ukus_spelling_trial_01.py`・`_test_01.py`・`er111_ukus_trial_eval_01.py`・`er111_ukus_trial_cases_01.py`(->`er109_ukus_spelling_01_test_cases_01.py`へ改名) | Trial撤去(sweep結果保存後) |
| 証跡: `UKUS/WIRING/`(sweep script/結果、golden再作成script/結果)、`er109_output/ukus_wiring_01/stored_regression_expected_01.jsonl.gz` | |
| `er109_ukus_runtime_evidence_01.py` | X実run evidence script(隔離run_dir) |

## 構造保証
- PASS->NG 0: 既存whole-span判定が合格したspanは救済関数に入らない。`ukus=False`出力はHEAD(v1)と同一(sweep: 171,544件で`off_vs_head_DIFF` 0・`off_pass_output_changed` 0)。
- 既定値: scope無し/`evaluate`既定 -> `ukus=False`。X/Z scope内のみ `UKUS_SPELLING_EQUIVALENCE_ENABLED=True`(親`ORTHOGRAPHIC_EQUIVALENCE_ENABLED`従属)。env/引数/設定dict/起動scriptから変更不可(AST test)。`evaluate(ukus=...)`は`_evaluate_cached`のみが渡す(AST test)。
- rollback: UKUS flagのみFalse -> X/Zでも従来(v1)判定、UKUS受理済みStore entryは再利用ブロック(W-03)で再生成(費用が出る旨コメント済み)。

## 撤去・残置
- 撤去: Trial module群(`er111_ukus_spelling_trial_01`、同test、`er111_ukus_trial_eval_01`、`er111_ukus_trial_cases_01`)、`er109_xz_isolation_01_test_01.py`/`er109_asr_orthographic_equivalence_01_test.py`のTrial許可。
- 残置(凍結): `val.BR_AM_SPELLING_PAIRS`(13ペア、A/B/C共有Validator。X/Zでは新層が上位互換)。DESIGN_01旧方式(key正規化/breame/Tier-2 PASS_WITH_WARNING/wordfreq)はProductionに無い(test `no_dev_or_old_design`)。
- 残存参照(意図的): `er111_pn_entity_table_trial_01_test_01.py:415`の `startswith("er111_ukus_")` はファイル名skip条件(①PNの隔離test。該当ファイル無しで無害・①担当ファイルのため未編集)。
