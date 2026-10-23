# WIRING_DESIGN_02 -- ②英米綴り(UKUS) Production配線設計 改訂版(OF-UKUS-W-01〜10反映差分表)
(UKUS 委任_04 / 2026-10-23 / WIRING_DESIGN_01.md に OPUS_REVIEW_02_COND_C.md[Fable転記]を反映。判定ロジック・対表・安全条件は不変)

| OF | 区分 | WIRING_DESIGN_01 -> 02 の変更 | 実装箇所(file:line、commit 719de3adc) | 検証 |
|---|---|---|---|---|
| W-01 | 必須 | 同等性差分testを網羅sweepへ強化。(1) active 6,361対を両方向×13文型(文頭/文中/文頭+次大文字/所有格/ハイフン複合/v1救済span隣接/数・否定・contraction隣接/n:n複数位置/長さ不一致flag/entity)で埋め込み Trial⇔Production 比較(165,386件)+保存rows(6,158件)(2)比較項目 equivalent/reason/warnings集合/ukus_pairs完全一致/rules集合、spansは比較対象外(3)`reason`=`all_diff_spans_phoneme_equal_or_ukus_variant`移植(4)W1文言を『同数・全unitがword』に修正。**Productionはwhole-span既存判定が先、不合格spanのみ位置別救済**(Trialは再整列後に全span位置別)、救済は1位置以上が対表で同値化された場合のみ成立 | `er109_asr_orthographic_equivalence_01.py` opcodeループ(`ukus and (bad or not rec.equivalent)`分岐)、`er109_ukus_spelling_01.py:rescue_span` | `WIRING/DIFF_TEST_RESULT_pairs_01.json`/`_stored_01.json`(diff 0)、`er109_ukus_spelling_01_test_01.py::StoredRegression`(固定expected 6,924件) |
| W-02 | 必須 | c12解除手順を `reuse_blocked` 印方式へ(segmentsキー削除をやめる)、checkpoint確認・provenance superseded注記・累積カウンタ確認を手順化 | `UKUS/RUNTIME_EVIDENCE_01.md` §Z手順(B工程で実施。本委任ではZ実行しない) | B工程時 |
| W-03 | 必須 | `ukus_contributed`: `asr_judgement`+`asr_judgement_inherited`両方、sites全件の`er109.rules`/`ukus_pairs`、fail-closed(ortho適用・version `*_ukus*`・site audit欠落=寄与あり)、`kp_vote_gate_follows`早期returnより前・既存ortho判定直後 | `er109_xz_scope_01.py:ukus_contributed`、`er078_reuse_value_guard_01.py`(ortho判定直後) | `Hooks::test_e5_*` 4件(inheritedのみ/KP票site/audit欠落/旧v1不変) |
| W-04 | 必須 | T-K(①RET⇔②UKUS両方ON相互作用)の割当 | ①RET(er103系)は本委任時点で未commit(`git status` er103系変更なし) -> **T-Kは①側(後からcommitする側)で実施**。RESULT_PACKET(6)に明記、Fableが①委任へ回す。②側不変性(②OFF/ONで①署名不変の②側半分)は`DefaultOnScope::test_ukus_flag_off_equals_pre_ukus_v1_signature`で実施 | - |
| W-05 | 推奨 | golden: 既存行不変、合成UKUS行(g0298〜14件)追加、新行pre署名のみ配線前commit overlay(b7b6d07d8)で採取、既存行再計算==fixtureバイト同一確認、v1->v2差分3分類 | `er109_wiring_golden_build_01.py:SYNTHETIC_UKUS`/`--append-ukus`、`WIRING/golden_rebuild_01.py`、`WIRING/GOLDEN_CHANGE_01.json/.md` | overlay再計算 mismatch 0(none/X/Z)、version文字列のみ598行/新規UKUS PASS(既存行)0/PASS->NG 0/想定外0、`er109_wiring_golden_test_01.py` 7 PASS |
| W-06 | 推奨 | HR rejudge dirty検査対象に新module+対表json | `er109_hr_lock_rejudge_01.py:_code_commit` | `er109_hr_lock_rejudge_01_test_01` 8 PASS |
| W-07 | 推奨 | run単位evidenceに`ukus_active`・表sha・LAYER_VERSION。表sha不一致は**失敗状態をcache** | `er109_xz_scope_01.py:ukus_run_evidence()`、`er109_ukus_spelling_01.py:table()`(自前cache)。per-entry: UKUS適用時のみauditへ`ukus_active`/`ukus_table_sha256`。runner summaryへの組込は共有runner(①編集中のer019 :347-390近傍)を避け未配線=関数提供のみ(RESULT_PACKET残存リスク) | `Table::test_sha_*`、`Structure::test_run_evidence_summary` |
| W-08 | 推奨 | X陽性証拠: 正式TTS段のdecorator付き入口で実run(UK専用語2〜3文、最初の発火で停止、上限3clip・約3円)+V6行列をhook差し替えなしで再実行 | `er109_ukus_runtime_evidence_01.py`(隔離run_dir)、`Hooks`(T-E1〜E5)、golden UKUS行(X/Z 5経路) | `UKUS/RUNTIME_EVIDENCE_01.md` |
| W-09 | 推奨 | c12は`pron_differs=true`である旨をB報告の最終試聴確認点に明記 | `RUNTIME_EVIDENCE_01.md` §Z手順、`ukus_pairs[].pron_differs`(audit) | `Behavior::test_c12_both_directions` |
| W-10 | 推奨 | test更新: `evaluate(ukus=)`を渡してよいのは`_evaluate_cached`のみのAST test新設。既存spy(`xz_isolation:248`)・`xz_scope_test`の`_evaluate_cached`参照は*a/**kのため無改修で通る(確認済み) | `er109_ukus_spelling_01_test_01.py::Structure::test_evaluate_ukus_kwarg_only_passed_by_evaluate_cached`、`er109_xz_isolation_01_test_01.py`(Trial許可リスト撤去) | 14 + 56 PASS |
| W-11〜15 | 情報 | LAYER_VERSION副作用は監査のみ(機能比較は`xz:131,214`のみ)=確認済み/P-06安全性は`Structure::test_p06_*`(表12,627語の数字・否定・値atom 0、`nought/naught`含む)/flag構成は`ORTHOGRAPHIC_EQUIVALENCE_ENABLED`と同型/近接hunkは本委任がer109・xz_scope・reuse guardのみ・①のer103系は未触/offline tool(`er109_stored_*`)は`evaluate`既定False(v1)で不変 | - | - |

## 実装中の設計判断(WIRING_DESIGN_01からの差分)
1. **救済の起点をwhole-span判定の後ろに置いた**: Trialは『既存evaluateがNGなら全spanを位置別に再整列』だったが、Productionは『spanごとに既存whole-span判定→不合格spanだけ位置別救済』。既存合格spanに触れない=PASS->NG 0が構造保証(ukus=Falseと出力同一)。sweep 171,544件でTrialと全項目一致(差分0)を実測。
2. 救済成立条件に『1位置以上が対表で同値化』を追加(UKUS無関係のNG->PASSを作らない)。sweepで影響0。
3. 救済失敗時は`ukus=False`と同一のNG記録を使う(NGのみ、先に救済済みの他位置span記録がNG記録に残る場合あり=監査のみ、decision()はNG->None)。
4. 対表のsha照合は『pairsの正規化JSONのsha256』(`PAIRS_CANONICAL_SHA256`定数)。ファイルバイトshaは改行変換(autocrlf)で揺れるため。対表ファイルは内容不変で`git mv`のみ(R100)。
5. UKUS層の例外(sha不一致等)はevaluate内でcatchして**v1判定へfail-closed**(`EquivalenceResult.ukus_error`)し、decision()がsinkへ記録。(v1全体を落とさない)
