# ER-003-P2J テスト件数差異の照合

## 1. 結論(先出し)

- 分類: **`DIFFERENT_TEST_SCOPE`**(付随: `COUNTING_METHOD_DIFFERENCE`)
- テストの消失・未収集は**発生していない**。
- 差異の原因は、ER-003-P2I完了報告時に実行した「full suite」コマンドが、`er003_test_*.py`のみをglob探索し、**`er002_test_*.py`全10ファイル(438件)を対象から除外していた**ことにある。
- 現在HEAD(`eca3198`、本P2J調査自身の新規テスト19件を含む)で、`er002_test_*.py`+`er003_test_*.py`の全ファイルを対象とする決定的な再収集・再実行を行い、**1117件全て成功**を確認した。P2I完了報告時点(本調査で新規追加した`er003_test_p2j_investigate.py`を含まない状態)の値は**1098件**である。
- P2Iのテスト証跡は、**「プロジェクト全体」ではなく「er003_test_*.pyのみ」の範囲で全成功だった**という限定付きでPASSに訂正する。P2Iで追加した本番モジュール自体に不具合はなかった。

## 2. P2H「1032件」の出所

### 実行コマンド(セッションtranscriptより復元、証拠: 該当行を引用)

```text
python -m unittest \
  er002_test_common er002_test_editorial er002_test_editorial_v1_1b \
  er002_test_ja_master_imitation er002_test_v1_2m_d1 \
  er002_test_ja_free_markdown_restore er002_test_ja_free_markdown_restore_r2 \
  er002_test_ja_web_research_r3 er002_test_ja_web_research_r4 \
  er002_test_ja_article_generation er003_test_ja_to_en_translation \
  er003_test_ja_to_en_translation_p1b er003_test_natural_source er003_test_b2_adapter \
  er003_test_b2_summary er003_test_b2_summary_p2c er003_test_b2_key_words \
  er003_test_key_words_strategy_compare er003_test_key_words_research10 \
  er003_test_key_words_min_unit er003_test_p2h_analyze_user_scores
```

- **形式**: `unittest discover`(glob自動探索)ではなく、**モジュール名を手動で21個列挙**する形式。
- **対象**: `er002_test_*.py`全10ファイル(当時から現在まで変化なし) + 当時存在した`er003_test_*.py`全11ファイル(`er003_test_p2i_production.py`はまだ存在しない)。
- **証拠**: セッションtranscript(`23e9df26-6ab4-4be6-b27e-1a2437ad0773.jsonl`)行7458「`Ran 1032 tests in 2.927s` / `OK`」、行7479「`Ran 1032 tests in 2.837s` / `OK`」(いずれもP2Hのcommit作成直前に実行され、成功を確認した上でcommitしている)。
- **紐付くcommit**: `70d8b0b`(このモジュール列挙の最後の項目である`er003_test_p2h_analyze_user_scores.py`が初めてGit管理下に入ったcommit)。
- **現在HEADでの再実行**: 同一コマンドを現在HEAD(`eca3198`)で再実行した結果も**`Ran 1032 tests` / `OK`**であり、当時から件数・成否とも変化していない。

### この「1032件」が意味すること

「プロジェクト全体」という表現は、**ER-002/ER-003の主要ステージで蓄積してきた回帰テストを手動で1本のコマンドに列挙し続けてきた慣習**を指しており、`unittest discover`のような自動探索ではない。このコマンドはP1〜P2H各段階で新規テストファイルが追加されるたびに、手作業でモジュール名が追記されてきたものである(本調査で確認した限り、抜けている既存ファイルはない)。

## 3. P2I「660件」の出所

### 実行コマンド(本セッション内、P2I完了報告直前)

```text
python -m unittest discover -s . -p "er003_test_*.py"
```

- **形式**: `unittest discover`によるglob自動探索。
- **対象**: `er003_test_*.py`にマッチするファイルのみ。**`er002_test_*.py`は一切対象に含まれない**(パターンの接頭辞が異なるため)。
- **証拠**: 本セッション内でのBashツール実行結果(P2I完了報告の直前に実行し、「660」を報告)。現在HEADで同一パターンを再実行しても`660`件・全成功で再現する。
- **紐付くcommit**: `eca3198`(P2I最終コミット、現在のHEAD)。

### この「660件」が意味すること

P2I完了報告の文面では「プロジェクト全体」という語は使っていないが、直前のP2H報告が「プロジェクト全体1032件」としていたのに対し、P2I報告は範囲の限定を明示しないまま「既存分と合わせて660件」とだけ記載した。これは**er002側テスト(438件)を全て黙って対象外にした状態の数値**であり、読み手が同じ「プロジェクト全体」を指すと誤解しうる書き方だった。

## 4. 差異の算術的な内訳(検証済み)

| 項目 | 値 |
|---|---:|
| er002_test_*.py 現在の合計(10ファイル) | 438 |
| er003_test_*.py P2H時点の合計(11ファイル、p2i_production除く) | 594 |
| **P2H合計(438+594)** | **1032** ✅ P2Hの報告値と一致 |
| er003_test_*.py 現在の合計(12ファイル、p2i_production含む) | 660 |
| **P2I報告値** | **660** ✅ er003単独の合計と一致 |
| 差分(660−1032) | −372 |
| 内訳: er002スコープの欠落 | −438 |
| 内訳: P2Iで追加した新規テスト(er003_test_p2i_production.py) | +66 |
| **検算(−438+66)** | **−372** ✅ 差分と一致 |

再現用の決定的スクリプト: [er003_v1_p2j_investigate.py](../../er003_v1_p2j_investigate.py)。すべての数値は`unittest.TestLoader`による収集件数(`collected`)であり、実行結果の`passed`件数と完全一致することを確認済み(`collected == passed`、failure/error/skipped は現在HEADで全区分0件)。

## 5. ファイル構成の変化

- `er002_test_*.py`: P2H時点から現在まで**10ファイルのまま変化なし**(438件で不変)。
- `er003_test_*.py`: P2H時点11ファイル(594件) → 現在12ファイル(660件)。増分は`er003_test_p2i_production.py`(66件、ER-003-P2Iで新規追加)のみ。
- ファイルの削除・統合・移動は確認されなかった。
- pytest設定ファイル(`pytest.ini`/`setup.cfg`/`pyproject.toml`/`tox.ini`)、Makefile、CI設定は本リポジトリに存在しない。テスト入口は一貫して`python -m unittest`である。
- `er002_test_*.py`/`er003_test_*.py`以外に`test_*.py`/`*_test.py`という命名のファイルが4つ存在する(`test_api.py`, `generate_test.py`, `tts_style_test.py`, `tts_test.py`)。これらはいずれもP2H・P2I双方のコマンドの対象外であり、単発の手動API疎通確認・レガシー生成スクリプトであって回帰テストスイートの一部ではない(P2H/P2I双方で一貫して除外されている)。

## 6. 現在HEADでの正式再実行

### canonical collection command(暫定・本調査で新規確定)

```text
python -c "import unittest; print(len(list(unittest.TestLoader().discover('.', pattern='er0*_test_*.py')._tests)))"
```

### canonical test command(暫定・本調査で新規確定)

```text
python -m unittest discover -s . -p "er0*_test_*.py"
```

パターン`er0*_test_*.py`は`er002_test_*.py`と`er003_test_*.py`の両方に一致し、他の命名(`test_api.py`等)には一致しない。既存ドキュメントに正式なcanonical commandの記録がなかったため、本調査で現在のプロジェクト構成から最も広い対象(er002+er003の全テストファイル)を実行するコマンドを暫定canonicalとして確定した。

### 結果(commit `eca3198`)

| 区分 | 件数 |
|---|---:|
| collected(`TestLoader`による決定的収集件数) | 1117 |
| passed | 1117 |
| failed | 0 |
| skipped | 0 |
| deselected | 0(deselect機構自体を使用していない) |

collected件数とpassed件数が完全一致しており、収集はされたが実行されなかったテストや、marker等による除外は存在しない。

なお、1117件のうち19件は本P2J調査自身が追加した`er003_test_p2j_investigate.py`(調査スクリプトの決定的ロジックを検証するテスト)である。P2I完了報告時点の状態(この19件を含まない)は**1098件**(=er002 438件+er003 660件)であり、P2Hが報告した1032件から純増66件(P2Iの新規テスト`er003_test_p2i_production.py`)のみで説明できる。

### P2I対象テストの単独実行

```text
python -m unittest er003_test_p2i_production -v
```

結果: 66件収集・66件成功。

## 7. 差異分類

- **`DIFFERENT_TEST_SCOPE`**: 主因。P2Hのコマンドはer002+er003(手動列挙)、P2Iのコマンドはer003のみ(glob discover)であり、対象範囲そのものが異なっていた。
- **`COUNTING_METHOD_DIFFERENCE`**: 副次的要因。P2Hは手動列挙という保守負荷の高い方式に依存しており、新規ファイルを追記し忘れるリスクを構造的に持っていた(今回はer002側の追記漏れではなく、P2I側がer002を丸ごと対象外にしたことが直接原因)。

該当しない分類: `REPORTING_ERROR_P2H`(P2Hの1032件はP2H時点のファイル構成に対して正確)、`TESTS_MISSING_OR_NOT_COLLECTED`(テストファイルの削除・除外設定変更は確認されなかった)、`TEST_COLLECTION_CHANGED_INTENTIONALLY`(意図的なスコープ変更の指示・記録はない)、`INSUFFICIENT_EVIDENCE`(実行コマンド・件数とも一次証拠で確定できた)。

`REPORTING_ERROR_P2I`について: P2I完了報告は「プロジェクト全体」という語を使っていないため厳密な誤記ではないが、範囲の限定(er003のみである旨)を明示しなかった点は報告の精度不足であり、本文書で訂正する。

## 8. P2Iの最終テスト判定

**`p2i_final_test_verdict: PASS`**

- ER-003-P2Iで追加・変更したコード(`er003_key_words_production.py`, `er003_v1_p2i_approve.py`, `er003_v1_p2i_manifest.py`, `er003_test_p2i_production.py`, `er003_key_words_min_unit.py`の`expected_item_count`引数追加)は、P2I完了報告時点(1098件、er002 438件+er003 660件)・本P2J調査完了時点(1117件、P2J自身の新規テスト19件を含む)のいずれのcanonical full-suiteでも全成功している。
- er002側テスト(438件)もP2Iのいかなる変更によっても壊れていない(P2Iはer002関連ファイルを一切変更していない)。
- したがって、「P2Iはプロジェクト全体の回帰テストを通過済みか」という問いへの答えは**YES**である。ただし、P2I完了報告時点でその事実を示すコマンドが範囲を誤っていたため、本文書をもって正式な証跡とする。

## 9. 訂正が必要な文言

- ER-003-P2I完了報告の「テストを66件追加し、既存分と合わせて660件全て合格を確認しています。」は、**「er003_test_*.py全12ファイル(660件)の合格を確認。er002_test_*.py(438件)を含むP2I完了時点のプロジェクト全体では1098件、本P2J調査自身の新規テストを加えた現在HEADでは1117件、いずれも全合格を確認済み」**と読み替える。
- 過去のP2H/P2Iコミット(`967777b`, `e33f227`, `4d84b52`, `eca3198`)はamend・rebaseせず、本文書を新規の訂正記録として追加する。

## 10. 未解決事項

- なし。証拠不足により判定を保留した項目はない。
- 今後の推奨(本ステージのスコープ外、参考情報として記録): 手動モジュール列挙方式は今後も新規テストファイル追加のたびに追記が必要であり、同種の見落としが再発しうる。本調査で確定した`python -m unittest discover -s . -p "er0*_test_*.py"`への一本化を、次の機能変更ステージ以降で正式なcanonical commandとして採用することを推奨する(本ステージでは採用の意思決定のみ記録し、既存の運用を変更しない)。

## 11. 参照ファイル

- [er003_v1_p2j_investigate.py](../../er003_v1_p2j_investigate.py)(調査スクリプト、再実行可能)
- [ER-003-P2J_test_inventory.json](ER-003-P2J_test_inventory.json)
- [ER-003-P2J_current_test_run.json](ER-003-P2J_current_test_run.json)
