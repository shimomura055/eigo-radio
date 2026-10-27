## 管理ID

LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_07R(ユーザー正式決定USER_03 §B(APPROVED_FOR_PRODUCTION)のClaude側実装: ユーザーがChatGPT経由で貼り付けた人間可読の選定結果(+照合コード1行)から、公開データJSONを参照してcandidate_id・候補集合sha・本文shaを復元し、payload v2を生成して確定内容保護`confirm --from-form`へ渡す復元・照合tool。設計=委任_06(commit b8917f366): `RESTORE_TOOL_SPEC_01.md`/`COPY_FORMAT_01.md`/`TEST_PLAN_06.md`、試作=`proto06_copy_restore_01.py`(66/66一致・改変9種検出)。API 0・JPY0)。並行Agent: (a)LEARNING-ITEM 委任_07(フォームJS側=`COPY_FORMAT_01.md`契約で並列。照合コードはnode/Pythonでバイト一致が条件)、(b)GPG 05B(`er120_part2_wiring_01.py`等=編集しない)、(c)AI-ISLAND 委任_03(runner実行のみ)。あなたの所有=新module `er128_form_readable_restore_01.py`+test `er128_form_readable_restore_test_01.py`、`er119_kp_human_review_cli_01.py`(`confirm --from-readable`サブコマンド追加のみ)、`er128_kp_confirmed_content_01.py`(**無変更が原則**。必要な場合は`cmd_from_form`へ委譲する薄いentryのみ)、`er119_isolation_test_01.py`(ALLOWED登録)、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{RESTORE_TOOL_IMPL_01,TEST_07R}.md`、`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_07R.md`(+check.json)、`docs/pm/RESULT_PACKET_FORM7R.md`(gitignore、`-f`禁止)。SSOT編集権なし。pathspec付きcommit(他Agentのstage分を巻き込まない)。

## 性質/禁止

- 性質: 承認済み改善のClaude側実装(明示実行時のみ動作、Production既定動作不変)。到達上限=IMPLEMENTED+test。
- 禁止: 不一致時の自動補正(訳・解説・区分の黙った置換=fail-closed)、照合コードなし/破損時の推測復元、`cmd_from_form`の検証緩和、禁止Git操作(`add -f`/`pull --rebase`/pathspecなしcommit)。
- 時間見込み: 約2h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_07R.md` をN=732から順に試し、先頭「## 管理ID」+「LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_07R」のものを採用(同時刻に委任_07あり)。

## 実施事項

1. `er128_form_readable_restore_01.py`: 入力=貼付テキスト(コードブロック囲み・半角/全角コロン・箇条書き記号・CRLF・先頭大文字化の揺れを吸収)、照合コード`AIF1-<stem>-<d6>-<c8>-<t8>-<s10>-<g10>-<m8>-<k4>`の解析・検証、公開データJSON(ローカルrepo `user_test/selection_form_v3/data/<stem>.json`、`d6`でデータ版を特定。不一致ならgit履歴から該当版を取得、取れなければ拒否)、term+訳(+区分)→candidate_id解決(同一termの複数候補は照合コードの選択集合hashで解消)、文法=文法名+解説全文の逐語照合(同名候補あり=解説全文で一意化、省略/改変/末尾切れは拒否)、コメント照合(`m8`)、payload v2(`schema_version:2`,`schema_minor:1`、`selection.{key_phrase,extra_explanation,meaning_display}`、`selection.grammar`≤1、`article.{candidates_sha256,text_sha256}`)生成、`cmd_from_form`へ委譲(`--run/--level/--by/--user-ref`透過、`--grammar-pending`も透過)。`--dry-run`で復元payloadと照合結果のみ出力。
2. CLI: `er119_kp_human_review_cli_01.py`に`confirm --from-readable <text.txt> [--dry-run] ...`。
3. test: 試作の66ケース相当(全11データ×乱択)で`buildStructured`相当と一致、改変9種検出、揺れ5種吸収、data更新(履歴あり/なし)、照合コードのPython実装が`COPY_FORMAT_01.md`の定義とバイト一致(固定fixture=委任_07と共有する`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/fixtures/readable_cases_01/`を**本委任が先に作成**しcommit)、AI島Std/Advのユーザー確定(`docs/research/AI-ISLAND-FORM-PRODUCTION-01/payloads/*.json`)を人間可読化→復元で逆変換一致、`er128`全test回帰、isolation。
4. `RESTORE_TOOL_IMPL_01.md`(使い方=Fable/Agentが貼付テキストを受け取ってから確定までのコマンド列)。

## 事前指定Read一覧

- `docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{RESTORE_TOOL_SPEC_01,COPY_FORMAT_01,HANDOFF_DESIGN_01,TEST_PLAN_06,DATA_MODEL_02}.md`、`proto06_copy_restore_01.py`、`proto06_node_structured.js`、`proto06_output_01.txt`
- `er128_kp_confirmed_content_01.py`(origin/main: Grep `def cmd_from_form|grammar_pending|payload\[|selection\[` ±10)、`er119_kp_human_review_cli_01.py`(Grep `confirm|add_argument|from-form` ±5)、`er119_isolation_test_01.py`(ALLOWED)
- `user_test/selection_form_v3/data/*.json`(schema)、`docs/research/AI-ISLAND-FORM-PRODUCTION-01/payloads/`

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_07R.md --json-out ...\_check.json`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er128_form_readable_restore_test_01.py"`、`--pattern "er128_*_test_*.py"`、`--pattern "er119_isolation_test_01.py"`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_FORM7R.md`にOPEN-545/556更新文案(復元tool IMPLEMENTED、運用手順)。

## Git

- fixtures先行commit+本体commit: `LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_07R: 人間可読選定結果+照合コードからの復元・照合tool(er128_form_readable_restore_01、confirm --from-readable、fail-closed)+test(API 0)`。trailer: `Delegation: LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/07R`。push(`git push origin HEAD:main`)。

## 報告

`docs/pm/RESULT_PACKET_FORM7R.md`: (0)T-0、(1)差分、(2)test結果(一致/検出/吸収/逆変換)、(3)運用手順、(4)判断候補、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)SSOT文案、commit hash・raw URL。末尾5行要約。