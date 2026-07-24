# ER-003-P2L P2J履歴監査テストと現行回帰テストの責務分離

## 1. 事実確認: ER-003-P2Kで変更した2テスト

対象ファイル: [er003_test_p2j_investigate.py](../../er003_test_p2j_investigate.py)(P2K当時のクラス名`SavedArtifactConsistencyTests`)

### テスト1: `test_inventory_json_matches_freshly_built_inventory`

- **対象P2J成果物**: `er003_output/p2j/ER-003-P2J_test_inventory.json`
- **P2K以前(P2J作成時)のassertion**: `self.assertEqual(fresh["current_head"]["collected"], saved["current_head"]["collected"])`(厳密一致)
- **P2Kでの変更後assertion**: `self.assertGreaterEqual(fresh["current_head"]["collected"], saved["current_head"]["collected"])`
- **何を保証しようとしていたか**: 保存済みinventoryの`current_head.collected`が、テストを実行するたびに`build_inventory()`で再計算した「今この瞬間」の値と乖離していないか(ドリフト検出)。

### テスト2: `test_current_run_json_matches_fresh_build`

- **対象P2J成果物**: `er003_output/p2j/ER-003-P2J_current_test_run.json`
- **P2K以前(P2J作成時)のassertion**: `self.assertEqual(fresh_run["collected"], saved["collected"])` / `self.assertEqual(fresh_run["passed"], saved["passed"])`(厳密一致)
- **P2Kでの変更後assertion**: `self.assertGreaterEqual(fresh_run["collected"], saved["collected"])` / `self.assertGreaterEqual(fresh_run["passed"], saved["passed"])`
- **何を保証しようとしていたか**: テスト1と同じ(current_test_run.json版)。

**判定**: いずれもP2Kでの変更後assertionは`current_count >= historical_count`と同等であり、本指示(ER-003-P2L)で指摘された通り、テスト消失検出として不十分だった(重要なテストを削除し無関係なテストを追加して総数だけ維持しても合格してしまう)。責務分離へ修正した。

## 2. 副次的に発見した同型の不備(2テストの範囲外だが、同一原則で修正)

`CollectionCountTests.test_er003_only_pattern_at_least_p2i_era_count`も、`self.assertGreaterEqual(inv_mod.collect_count("er003_test_*.py"), inv_mod.P2I_REPORTED_COUNT)`という同型の閾値比較だった(このテストはP2Kではなく、それ以前のER-003-P2H起因ドリフト対応の際に導入したもの)。同じ理由で、件数のしきい値比較ではなく、P2I時点に存在した各ファイルが今も個別に存在するかを直接確認する形へ書き換えた(`test_er003_only_pattern_still_includes_all_p2i_era_files`)。

## 3. P2J履歴監査テストが保証すること(新設計)

新クラス`HistoricalRecordIntegrityTests`が、保存済みP2J成果物について次を検証する(いずれも保存済みJSONを`load_saved_inventory()`/`load_saved_current_run()`でそのまま読み込み、`build_inventory()`等による再計算は一切行わない)。

- 必須セクション(`p2h`/`p2i`/`current_head`/`classification`/`p2i_final_test_verdict`/`detail`)の存在
- `current_test_run.json`の必須フィールドの存在
- `p2h`/`p2i`セクションが混同されていない(commit文字列・scope文字列の内容確認)
- `validate_saved_inventory_schema()`による構造・型・enum検証(必須フィールド、非負整数、commit hash形式、command/scope非空、classification/verdict enum適合)。この検証関数自体のreject挙動(欠落field・負数・型不一致・不正commit・空command/scope・不正enum・不正JSON)を個別にテスト
- `classification`が許容enum内、かつ`DIFFERENT_TEST_SCOPE`を含む
- `p2i_final_test_verdict`が許容enum内、かつ`PASS`
- **immutability**: `p2h.collected == 1032`、`p2i.collected == 660`、`current_head.collected == 1117`、`current_test_run.collected == 1117`、`p2i_targeted_collected == 66`(いずれも凍結定数`P2H_REPORTED_COUNT`/`P2I_REPORTED_COUNT`/`P2J_CURRENT_HEAD_REPORTED_COUNT`との厳密一致であり、現在のlive集計値とは無関係)
- 構造的な保証: `HistoricalRecordIntegrityTests`クラス自身のソースコードに`build_inventory(`/`collect_count(`/`build_current_run_record(`という呼び出しが一切存在しないことを検証する(責務分離そのものをテストで固定する)

## 4. P2J履歴監査テストが保証しないこと

- 現在のtest countが過去以上/以下/一致であること
- 現在のtest file数が過去以上/以下/一致であること
- 現在のpassed数が過去以上/以下/一致であること
- 件数増加を品質向上とみなすこと
- 件数減少だけでtest消失を判定すること

過去件数と現在件数の`==`・`>=`・`<=`比較は、`HistoricalRecordIntegrityTests`および`CollectionCountTests`から完全に削除した。

## 5. 現在の回帰品質の検証方法

現在HEADの回帰品質は、[run_project_regression.py](../../run_project_regression.py)(canonical entry point)の実行結果だけで判断する。過去の記録との突き合わせは行わない。

```text
python run_project_regression.py
```

| 区分 | 件数 |
|---|---:|
| 対象ファイル数 | 24(er002: 10 / er003: 14) |
| collected | 1157 |
| passed | 1157 |
| failed | 0 |
| skipped | 0 |

詳細: [ER-003-P2L_canonical_run_summary.json](ER-003-P2L_canonical_run_summary.json)

(ER-003-P2K完了時点の1135件から22件増加。内訳は本ステージで`HistoricalRecordIntegrityTests`関連のテストを新設・拡充したことによる。er002_test_*.py側に変更はない。)

## 6. P2J成果物本体の変更

`er003_output/p2j/ER-003-P2J_test_inventory.json`・`ER-003-P2J_current_test_run.json`ともに**変更していない**(内部矛盾も発見しなかった)。今回変更したのは、これらを検証するテストコード(`er003_test_p2j_investigate.py`)と、検証ロジックを支えるhelper(`er003_v1_p2j_investigate.py`への`CLASSIFICATION_ENUM`/`VERDICT_ENUM`/`P2J_CURRENT_HEAD_REPORTED_COUNT`/`load_saved_inventory`/`load_saved_current_run`/`validate_saved_inventory_schema`の追加)のみ。

なお、本ステージの作業中に`er003_output/p2k/ER-003-P2K_canonical_run_summary.json`を誤って上書きしかけたが、コミット前に検出し`git checkout`で復元した。P2K自身の凍結記録も、P2J同様「過去のある時点のスナップショット」であり、以後のステージの実行のたびに上書きしてよいものではないと判断したため。本ステージの実行結果は新設の`er003_output/p2l/ER-003-P2L_canonical_run_summary.json`へ保存する。

## 7. 文書化

[TESTING.md](../../TESTING.md)へ「Historical test evidence vs. current project-wide regression」の節を追記した。
