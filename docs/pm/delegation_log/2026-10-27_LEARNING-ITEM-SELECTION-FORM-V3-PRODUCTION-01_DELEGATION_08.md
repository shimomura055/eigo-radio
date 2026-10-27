## 管理ID

LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_08(委任_07(b62a070cf/a87da3ab6)・07R(9fd1b65b2)の残課題2件の小修正。API 0・JPY0)。並行Agent: GPG委任_05(evidence run)、AI-ISLAND委任_03(X runner、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`と`user_test/selection_form_v3/data/*.json`を触る可能性あり=**編集禁止**)、PM-SSOT-SYNC-22(SSOT権)。あなたの所有=`user_test/selection_form_v3/form_logic.js`(+必要なら`index.html`)、`er128_form_readable_restore_01.py`、`er128_form_readable_restore_test_01.py`、`form1_selection_form_v3_test_01.py`、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{selection_form_logic_test_01.js,COPY_FORMAT_01.md(§改訂追記),fixtures/readable_cases_01/(追加のみ),TEST_08.md}`、`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_08.md`(+check.json)、`docs/pm/RESULT_PACKET_FORM8.md`(gitignore、`-f`禁止)。pathspec付きcommit。

## 性質/禁止

- 性質: 承認済み機能(USER_03 §B)の表示・堅牢性の小修正。契約(`COPY_FORMAT_01.md`)の変更はJS/Python両方で同時・バイト一致を維持。
- 禁止: UI上限・照合コード構造(`AIF1-…-k4`)の変更、fail-closed原則の緩和(曖昧な入力を推測で通さない)、データJSONの編集、禁止Git操作。
- 時間見込み: 約40分。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check(jsonl index=738付近から順に、先頭「## 管理ID」+「委任_08(」一致)。T-2/T-3: なし。

## 実施事項

1. **コメント「なし」問題**: 自由コメントが「なし」「特になし」「-」等のときに復元側が拒否(コメントなしと区別不能)する件。方針=フォーム側で正規化(trim後にこれら既定語のみ、または空白のみなら**コメントなし**として扱い、コピー本文では「コメント：なし」等の固定表記、`m8`は空コメント基準で算出)、復元側も同じ正規化関数で一致させる。既定語の一覧は`COPY_FORMAT_01.md`に追記し、JS/Pythonで同一定数。fixtureに「なし」「特になし」「(空)」「本当のコメント」の4ケース追加しバイト一致test。
2. **文法解説の終端`=====`**: データ側で解説末尾が`。=====`(直前に改行なし)の1件(AI島b1b Top1)がコピーに`=====`を残す件。方針=フォーム`buildReadable`とPython参照実装`build_readable`・`norm_body`の双方で、末尾の`\s*=+\s*$`を除去する規則に統一(本文中の`=====`は触らない)。既存fixture/往復test(66件・改変17種)が引き続きPASSすることを確認し、AI島b1b Top1で`=====`が消えることをtest化。
3. 公開(`user_test/selection_form_v3/`)+headless(公開URL、Console error 0、AI島b1bでTop1選択時のコピー文末尾確認)。
4. commit: `LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_08: コメント既定語の空扱い統一+文法解説末尾=====の除去規則をJS/Python同時適用(照合コード契約不変、API 0)`、trailer `Delegation: LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/08`、`git push origin HEAD:main`。Secret grep 0件。

## 事前指定Read一覧

`COPY_FORMAT_01.md`、`RESTORE_TOOL_IMPL_01.md`、`docs/pm/RESULT_PACKET_FORM7.md`(【Fableへ】3・4項)、`docs/pm/RESULT_PACKET_FORM7R.md`(注意点4)、`form_logic.js`(Grep `buildReadable|comment|m8|=====` ±10)、`er128_form_readable_restore_01.py`(Grep `norm_body|comment|m8|def build_readable` ±10)。

## 報告

`RESULT_PACKET_FORM8.md`: (0)T-0、(1)差分、(2)test(node/py/headless)、(3)判断候補、(4)必須4行+「判定整合」、(5)SSOT文案(OPEN-545残課題解消)、commit hash・raw URL。末尾5行要約。
