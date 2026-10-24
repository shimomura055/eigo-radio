# IMPL_F1_APOSTROPHE_01 (ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_02 §1) F1 `tokenize` の ’(U+2019) 修正

**分類=修正へ進む(11-8、既存承認仕様の整合是正)→ FIXED。OPEN-500。** 単独commit(E2 Trial成果物とは別commit)。ユーザー判断不要(新仕様でなく、他層 er006:497,1022 / er006_m1:60,331 が既に行う正規化への整合)。

## 1. 問題と変更
- 問題: `er011_b1_connected_speech_validator_01.py` の `tokenize()` が `[A-Za-z']+` で、ASRが出す ’(U+2019) を語構成文字にしない。`you’ve` が `you`,`ve` に割れ、F1(Connected Speech)の residual が偽残差になり、M1/Eq層の入口(F1残差 kind=content)で却下され得る。
- 変更(1関数): `tokenize()` が入力を `’→'`、`‘→'` に正規化してから分割(他層と同じ正規化)。`None`/空文字も安全に空リスト。
- 変更ファイル: `er011_b1_connected_speech_validator_01.py`(+3/-1行)、新規test `er011_b1_tokenize_curly_apostrophe_open500_test_01.py`(4 test)。

## 2. 影響分析gate(API 0)
| gate | 結果 | 証跡 |
|---|---|---|
| 保存全行(5,604行/ユニーク(canonical,asr)2,698)をProduction関数で修正前後比較(`f1_replay_02.py`、修正前=tokenizeを旧実装に差替えて再現) | **PASS→NG 0件・NG→PASS 0件**(`should_pass` 変化0)。F1診断(`new_judgment`)変化224、残差件数変化407、Eq層`layer_judgment`変化257(いずれも診断ラベル。偽残差の解消[UNCLASSIFIED→NO_DIFF 217]が大半)。最終`classification`ラベル変化2件(いずれもPASS系同士: TRANSCRIPT_STYLE_NORMALIZED_MATCH→CONNECTED_SPEECH_PASS_WITH_WARNING/CONNECTED_SPEECH_ACCEPT。canonicalの`let’s`が偽残差で連結音層を止めていたものが、正規に連結音層で説明されるようになった) | `work/f1_replay_before_venv.json` `work/f1_replay_after_venv.json` `work/f1_replay_compare.txt` |
| 逆方向の変化 | NO_DIFF→UNCLASSIFIED の4ペア(canonical側に`parents’ own`のような所有格’が有り、ASR側が`parents own`)。最終`classification`は4件とも NORMALIZED_MATCH/PASS のまま不変(F1診断のみ) | 同上 |
| M1/Eq/F1 test | PASS: `er011_b1_connected_speech_validator_01_f1_test_01.py` 39、`er006_m1_multi_candidate_01_test_01.py` 68、`er006_secondary_asr_01_m1_wiring_test_01.py` 22、`er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py` 16、`er077_m1_oov_multi_pronunciation_01_test_01.py` 14、`er026_cs_audit_regression_01_test_01.py` 16、新test 4 | pytest実行ログ(本ファイル作成時に取得) |
| 全回帰(`run_project_regression.py`、`REGRESSION_BASELINE_2026-10-24.md`比) | 既定: collected 7109 / passed 7098 / failed 1(`er064_kp_int_01_test_01...test_no_tracked_py_or_template_modified`=baseline記載の恒常失敗[未commitのtracked .py変更があると必ず失敗]。clean tree=commit後は0) / skipped 10。`er1*`: collected 491 / passed 487 / failed 4。内訳は下記 | `work/regression_f1_summary.txt`(全文はローカル保存・未追跡) |
| X/Z golden | `er109_wiring_golden_test_01.py` 3 test失敗(X/Z/unset各1)。**F1修正の有無で結果が同一**(旧tokenizeを注入して実行しても同じ3 test・同じ要素が失敗)=自分起因でない。HEAD清浄worktreeでの再現は下記(HEAD baseline欄) | 本ファイル §3 |

## 3. 全回帰の失敗帰属(自分起因の新規失敗0の確認)
- `er064...test_no_tracked_py_or_template_modified`: 未commit tracked .py変更の検査。本件のF1ファイル変更を含む(commit後に解消する性質。baseline記載どおり)。
- `er112_kp_gm_trial_06_test_01.T06.test_default_off_isolation_no_api_no_files`、`er1*`の他3件・`er109_wiring_golden_test_01` 3件: 本修正(tokenizeのみ)と無関係。golden 3件は旧tokenize注入でも同一失敗(再現済み)。他agentの並行作業(Family Y・UKUS配線等)の可能性が高い。帰属の最終確認はHEAD清浄worktreeでの再現(§4)で行う。

## 4. HEAD baseline(清浄worktree)
HEAD(8b9164c52)の清浄worktree(git worktree、作業後に撤去)で `er109_wiring_golden_test_01.py` を実行: **同じ3 test失敗(X/Z/unset)・4 passed**=F1修正前のHEADでも既存の失敗。自分起因でない。ただしworktreeは未追跡データファイルを持たないため、失敗の根因が『HEAD自体のgolden陳腐化(UKUS v2_ukus01配線 commit 719de3adc の golden 未更新の疑い)』か『未追跡fixture欠落』かは未特定 → 本委任外の既存失敗としてFableへ報告(新規OPEN候補、分類=修正へ進む[要帰属調査])。

## 5. 残存Grep
- `tokenize(` の他の呼出し側(`er011_b1_connected_speech_validator_01.py:108,109,256`)は同一関数の利用のみ。旧実装(’を割る)を前提にしたassert: `er011_b1_connected_speech_validator_01_f1_test_01.py` 39件PASSで残存なし。
