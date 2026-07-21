# ER-003-P2K プロジェクト全体回帰テスト入口の一本化

## 1. 決定

**プロジェクト全体回帰テストの正式入口を [run_project_regression.py](../../run_project_regression.py) の1つに固定する。**

- canonical command: `python run_project_regression.py`
- discovery pattern: `er0*_test_*.py`(自動探索、手動module列挙は廃止)
- scope: `er002_test_*.py`(ER-002)+ `er003_test_*.py`(ER-003)
- 文書: [TESTING.md](../../TESTING.md)

## 2. ER-001の調査結果

`er001*.py`ファイル群(`er001b*_common_spec.py`, `*_compare.py`, `*_narration.py`等)を調査したが、**unittest形式の回帰テストは1件も存在しない**。これらは全て、実TTS生成・比較のための一回限りの実験スクリプトであり、`unittest`をimportしていない。したがって、現時点でcanonical patternへ含めるべきER-001回帰テストは存在しない。将来`er001_test_*.py`が追加された場合の扱いは、その時点で別途判断する。

## 3. 現在HEADでの実行証拠

```text
python run_project_regression.py --json-summary er003_output/p2k/ER-003-P2K_canonical_run_summary.json
```

| 区分 | 件数 |
|---|---:|
| 対象ファイル数 | 24(er002: 10 / er003: 14) |
| collected | 1135 |
| passed | 1135 |
| failed | 0 |
| errors | 0 |
| skipped | 0 |

内訳: er002_test_*.py = 438件、er003_test_*.py = 697件(438+697=1135)。

詳細: [ER-003-P2K_canonical_run_summary.json](ER-003-P2K_canonical_run_summary.json)

## 4. 手動列挙方式との決別

ER-003-P2Hが使っていた「test module名を手動で21個列挙するcommand」は、正式手順から外す。ER-003-P2Jで、この方式がER-003-P2I完了報告の対象範囲食い違い(1032件 vs 660件、DIFFERENT_TEST_SCOPE)の一因(P2I側が自動探索へ切り替えた際にer002側を丸ごと対象外にした)であったことを確認済み。今後の完了報告では、[TESTING.md](../../TESTING.md)の「Reporting rules」に従い、targeted testsとproject-wide regressionを明確に区別して記載する。

## 5. preflightへの反映状況

本ステージでは、既存の8つのpreflightスクリプトへの一括書き換えは行っていない(大規模変更を避け、最小範囲に留める方針のため)。

**未移行のpreflightスクリプト(現状のまま、canonical entryを呼んでいない):**

- `er003_v1_p1_preflight.py`
- `er003_v1_p1b_preflight.py`
- `er003_v1_p2_preflight.py`
- `er003_v1_p2b_preflight.py`
- `er003_v1_p2d_preflight.py`
- `er003_v1_p2e_preflight.py`
- `er003_v1_p2f_preflight.py`
- `er003_v1_p2g_preflight.py`

これらはいずれも過去ステージ(P1〜P2G)のpreflightであり、そのステージ自体は完了済みで再実行を前提としていない。今後新たに追加するステージのpreflightでは、可能な範囲で`run_project_regression.py`をproject-wide regressionの最終確認として呼ぶ(targeted testはそのステージ固有のものを別途残してよい)。

## 6. 副次的に発見・修正したテスト不具合

本ステージのcanonical実行で、`er003_test_p2j_investigate.py`の`SavedArtifactConsistencyTests`が2件失敗した(`AssertionError: 1135 != 1117`)。原因は、ER-003-P2Jが保存したJSONスナップショットの`current_head.collected`値(P2J完了時点の1117)を、本ステージが新たなテストファイル(`er003_test_p2k_regression_entry.py`)を追加した後の「今この瞬間」の値と厳密一致で比較していたことによる。

`current_head`はglob探索による時々刻々変化する値であり、将来ステージがテストを追加するたびに同じ理由で失敗し続ける設計上の欠陥だったため、該当2箇所を「保存値を下回っていないこと(`assertGreaterEqual`)」の検証へ修正した。P2Hの1032件・P2Iの660件など、固定モジュールリストに基づく過去時点のスナップショット比較(時間が経っても変化しない値)は、厳密一致のまま変更していない。テストの削除・無効化は行っていない(アサーションを、本来あるべき「増加のみを許容する」検証へ訂正しただけ)。
