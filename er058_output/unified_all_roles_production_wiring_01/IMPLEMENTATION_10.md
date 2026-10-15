# IMPLEMENTATION_10 (AUW `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_10)

作成: 2026-10-16(JST)。到達上限Status: `U1_FIXED_EVIDENCE_PENDING_FABLE`(`PRODUCTION_WIRED`は宣言しない)。
**重要: 既定値は条件付きSTOP s1により `U1_KEEP_C1_SIMILARITY_EXCLUSIONS = True`(旧挙動)のまま。** 解放実装・Regressionは完了しており、Fableの採否判断後に定数を1行`False`にする(下記§5)。

## 1. 差分(ファイル:行)

| ファイル | 変更 |
|---|---|
| `er078_asr_unified_judge_01.py:64-73` | U1コメント更新、`U1_KEEP_C1_SIMILARITY_EXCLUSIONS`(**Trueのまま**=s1)、死定数`U2_FORCE_SECONDARY_SCOPE`撤去 |
| `er078_asr_unified_judge_01.py:125,148` | `A7_READING_DICT_MISMATCH`新設(langs=("ja",)、u1_gated=False、signal=`reading_dictionary_mismatch`)。表の順序はA6の後(U1=True時は従来どおりA6が先に命中=ロールバックで旧rule_idを維持) |
| `er007_ja_secondary_asr_01.py:473-481` | `NO_SPEECH_SENTINEL`、`_scg_reading_dict_reason`(A7用signal) |
| `er007_ja_secondary_asr_01.py:581-583` | `signals["reading_dictionary_mismatch"]`を追加(`c1_proper_noun_diff`はU1=True時のA6用に維持) |
| `er007_ja_secondary_asr_01.py:631-636` | Azure正常完了の空転写→`SecondaryOutcome(NO_SPEECH_SENTINEL, accepted=False, label="NO_SPEECH")`→`NG_BOTH` |
| `er007_ja_secondary_asr_01.py:188-215,663` | 診断`_scg_exclusion_reason(..., u1_released=)`: 解放時は登録読み(A7)→C2(A4)→否定マーカー順、類似度/C1を除外理由にしない。既定(False)は旧SCG経路・既存testの旧挙動。cascade側は`not U1_KEEP...`を渡す |
| `er078_asr_unified_wiring_10_test_01.py`(新規) | unit負例・空転写・EN不変・ロールバック・U2静的・解放後frozen 25行 |
| `er078_auw_runtime_evidence_10.py`(新規) | 保存wav x live Azure / live負例対照 harness |

## 2. R1〜R7 対応表

| 要件 | 対応 |
|---|---|
| R1 (U1R-01 BLOCKER) | A7新設。unit負例: Latin登録語(`Meta`→`エムイーティーエー`/`メタン`)・漢字登録語(`昨日`→`アクジツ`)でAzureが原稿表記を返してもSecondary不呼出で`NG_EXCLUDED(A7)`。`entity_like`(ガス→カス)と辞書未登録Latinは解放(正答は`PASS_WITH_WARNING`、Secondaryも誤りなら`NG_BOTH`)。**範囲限定はユーザー報告で明示** |
| R2 (U1R-02) | JA adapterのみ。空/空白転写→`NG_BOTH`(`unavailable=False`・technical_stop無し・circuit breaker非カウント)。真のSecondary障害(error付き)は従来どおり`NG_SECONDARY_UNAVAILABLE`。EN不変 |
| R3 (U1R-04) | A3挙動不変。SSOT記述を訂正しOPEN-388起票 |
| R4 (U1R-05) | (a)unit負例 (b)live負例対照8 clip (c)保存wav x live Azure 8本+遷移件数0+Melos切り分け (d)ロールバックtest(`test_u1_true_rolls_back_to_previous_exclusions`)。fresh正例JA 1〜3 clipは任意のため未実施 |
| R5 (U1R-06) | 死定数撤去、静的test(`force_secondary=True`呼出点=`er003_v1_crosslevel_audio_02_common.py`のみ・`_run_a2_minimal_fallback_attempt`内)、`CURRENT_SPEC`1935行目付近/LR行を追記訂正、OPEN-389起票。`er003_v1_sing01_audio_generate.py:118/158`はsing01 AUDIO-01方式でlegacy扱い(`crosslevel_audio_02_common.py:341`コメント)、現行Production経路かは未確認 |
| R6 (U1R-09) | 診断順とコメント(judge:64-73、er007:394付近)更新 |
| R7 (U1R-10) | 一時worktree `cf4aca321`でkoro系2件が同一assertion(`PHONETIC_MATCH != ORTHOGRAPHIC_VARIANT_CONFIRMED`)で失敗 = **AUW起因ではない既存失敗**。OPEN-391。β期待値変更なし |

## 3. α testの更新一覧(β期待値は不変)

U1の既定を変えない(True)ため、旧挙動を固定する既存testは原則そのまま。更新したのは次のみ:
1. `er078_asr_unified_ja_wiring_test_01.py::test_secondary_unavailable_is_never_pass` — 空転写(`("", None)`)のparamを削除(R2により`NG_BOTH`。専用testは新規ファイル)。
2. 同 `::test_u1_constants_unchanged` — `U2_FORCE_SECONDARY_SCOPE`のassertを「属性が存在しない」へ(R5)。
3. 同 `::test_c1_proper_noun_and_low_similarity_excluded_u1_current` — 既定値に依存しないよう`U1=True`をmonkeypatch。
4. 同 `::test_u1_release_flag_changes_behavior_only_via_constant` — `U1=False`のmonkeypatchを明示(元から同等)。
5. `er078_asr_unified_judge_01_test_01.py::test_p2_exclusions_table` — monkeypatch引数追加+A7のassert追加。
6. 同 `::test_exclusion_table_is_data_with_expected_ids` — id列に`A7_READING_DICT_MISMATCH`追加。
7. 同 `::test_u1_flag_releases_a5_a6_in_one_line` — 元のassertを維持(`is True`→`False`へpatch)。
8. `er007_ja_scg_test_01.py::test_e_similarity_below_0_4_not_executed` — `U1=True`を明示patch(既定値非依存)。
9. 同 `::test_f_azure_none_and_empty_fall_back_to_legacy` — 空転写を`NG_BOTH`の期待へ分離(R2)。
10. 同 `::test_c1_entity_like_diff_in_mixed_diffs_not_executed` — `U1=True`を明示patch。
`er007_ja_scg_phase0_regression_test_01.py`は**変更なし**(旧挙動をそのまま固定。解放後の25行は新規testで固定)。
β(最終判定の安全性: 数値・否定・C群誤PASS等)の期待値は一切変更していない。

## 4. test結果

- 中核(委任_08相当のAUW中核12 file相当+新規+backcompat+er007系: `er078_asr_unified_{backcompat_07,en_wiring,ja_wiring,judge_01,wiring_05,wiring_06c,wiring_06d,wiring_06e}_test_01.py`・`er078_asr_value_guard_01_test_01.py`・`er078_pass_with_warning_registry_01_test_01.py`・`er007_ja_secondary_asr_01_test.py`・`er007_ja_asr_validator_01_test.py`・`er007_ja_scg_test_01.py`・`er007_ja_scg_c2_neg_test_01.py`・`er007_ja_scg_phase0_regression_test_01.py`・新規`er078_asr_unified_wiring_10_test_01.py`): **478 passed / 2 failed**(失敗2件=R7の既存失敗。新規失敗0)。
- 静的監査 `er078_asr_unified_wiring_static_audit_01.py`: pytest 15 passed、script差分空(`unlisted_new_calls`/`vanished`/`count_changed`すべて空)。
- flag OFF経路 `-k test_g`: 中核リスト全体で5 passed(委任文の期待は3 passed。件数差の理由は未確認[対象file集合の違いの可能性]。失敗0)。
- 広域(`evidence_10/wide_test_run.txt`、`er007_ja_secondary_asr_01`/`er078_asr_unified_judge_01`/`evaluate_attempt_ja`を参照する21 file): 5 failed = (1)(2)koro系2件(R7、AUW前から失敗)、(3)`er025_..._phase3_b1b_en_wiring_01_test_01::test_b1_segments_pass_enable_pronunciation_resolver_true`(KeyError 'part2'。**クリーンなHEAD(fa4d7df4f)の一時worktreeでも同一失敗**=既存、本委任の差分と無関係)、(4)(5)`er020_*ProductionModuleUnchangedTest`2件(commit前の未コミット差分を検出するtest。クリーンHEADでは2件ともPASS=本委任のcommit後に解消する性質)。

## 5. 解放手順(Fable採否判断後の1行変更)

1. `er078_asr_unified_judge_01.py:73` の `U1_KEEP_C1_SIMILARITY_EXCLUSIONS = True` を `False` にする。
2. `er078_asr_unified_ja_wiring_test_01.py::test_u1_constants_unchanged` と `er078_asr_unified_wiring_10_test_01.py::test_u1_default_state_documented` のassertを `False` に更新。
3. Phase0 regression 25行は旧挙動固定のまま、解放後の期待は新規`test_released_frozen_25_rows_only_g7_g8_change_and_c_group_stays_ng`が固定済み。ただし`er007_ja_scg_phase0_regression_test_01.py`の旧挙動固定testは既定を`False`にすると失敗するため、その時は同ファイルの該当5testを解放後の期待(g7/g8が救済・verified 15)へ更新する(私の試行で更新案は確認済み: g7/g8を`mock.patch`でTrue固定する旧挙動版+既定の解放版の併記)。
