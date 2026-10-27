# TEST_08 コメント既定語の空扱い統一 + 文法解説末尾=====の除去(委任_08、2026-10-27、API 0・JPY0)

契約: `COPY_FORMAT_01.md` §6。JS(`form_logic.js` `normalizeComment`/`bodyView`)とPython(`er128_form_readable_restore_01.py` `normalize_comment`/`body_view`/`norm_body`)に同時適用。照合コード構造・UI上限・fail-closedは不変。

| # | 検証 | 結果 |
|---|---|---|
| 1 | node `selection_form_logic_test_01.js`(既存56 + 新規2: 既定語12種=コメントなし/m8=0/buildStructured.comment=''、実コメント4種保持、AI島b1b Top1で`=====`消失、bodyView境界) | ALL PASS 58 |
| 2 | `run_project_regression.py --pattern er128_form_readable_restore_test_01.py`(66件往復・改変17種・fixture JS/Pythonバイト一致を含む) | collected=55 passed=55 |
| 3 | `--pattern "er128_*_test_*.py"` | collected=201 passed=201 |
| 4 | `--pattern form1_selection_form_v3_test_01.py`(node出力==正式参照実装`er128_form_readable_restore_01.build_readable`のバイト一致に変更) | collected=22 passed=22 |
| 5 | headless(ローカルhttp.server) `browser_check_08.mjs` | pass=32 fail=0、Console error 0 |

- 追加fixture(追加のみ): `comment08_{nashi,tokuninashi,empty_ws,real}`、`b1b_top1_trailing_term08`。「なし」「特になし」「空白のみ」の3表記は同一バイト(m8=0)。
- 既存fixtureの更新1件(契約変更の必然): `ai_island_temple__b1b__prod__r1.readable.txt`は旧規則の期待コピーに`=====`が残っていたため新規則へ更新(manifestのsha/codeも更新)。他は不変。
- 変更したtest: 旧`test_comment_literal_nashi_is_refused`(「なし」を拒否)は新仕様と矛盾するため撤去し、`test_comment_default_words_are_no_comment_08`/`test_comment_tamper_with_default_word_still_refused_08`(実コメントのコードに対する「なし」への書換えは従来どおり拒否)に置換。
- `form1_selection_form_v3_test_01.py`: 旧試作proto06との比較を正式参照実装へ変更(旧試作は`=====`を残す旧規則のため)。
