## 管理ID

GRAMMAR-PREGEN-ALL-LEVELS-01 委任_04(F-5/F-6: 確定内容保護(er128)への文法v2接続=`SCHEMA_CONTRACT_01.md` §4の4関数・`cmd_from_form`の文法照合(id/title/body一致/件数≤2、不一致ISSUE)・呼出順(検証→KPロック→`gr.apply_form_selection`→sidecar→KPレコード)・`:850 or "b1b"`と`:1258 discover_dirs(run)[0]`の撤去・level別sidecar・凍結v2 items[]、CLI(`--level/--ids`、`grammar-accept-translation`、`grammar-pregen --all-candidates`)、フォームexporterの`form_grammar_items`接続(fail-closed: 事前生成不完全/`part2_failed.json`/sha不整合はデータを出さない)。er128のTypeError 12件の解消。API 0・JPY0)。設計=`DESIGN_02.md`/`SCHEMA_CONTRACT_01.md`/`IMPLEMENTATION_02.md` §4/KCP `DESIGN_02.md`。並行Agent: (a)GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03(runner/ページ/Validator/`er120_part2_wiring_01.py`薄い追加)、(b)AI-ISLAND-FORM-PRODUCTION-01 委任_01(**`export_form_data_01.py`に文法items取込の最小拡張とフォームデータを編集中**=exporterは本委任の最後に着手し、着手前に`git log origin/main -1 -- docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`で(b)のcommitを確認してHEAD blobへ自hunkを重ねる。(b)未完了ならexporter部分は「委任_04b引継ぎ」として報告し待たない)。あなたの所有=`er128_kp_confirmed_content_01.py`+test(`er128_*_test_*.py`)、`er119_kp_human_review_cli_01.py`(あれば)/`er119_kp_human_review_01.py`(CLI部分のみ)、`er119_grammar_review_01.py`(CLI引数のみ。核ロジックは変えない)、`export_form_data_01.py`(上記条件付き)、`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/IMPLEMENTATION_04.md`、`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/DESIGN_02.md`(付録: 文法v2追補)、`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_04.md`(+check.json)、`docs/pm/RESULT_PACKET_GPG4.md`(gitignore、`-f`禁止)。runner/ページ/er120核は編集しない。SSOT編集権なし。pathspec付きcommit(他Agentのstage分を巻き込まない)。

## 性質/禁止

- 性質: 承認済み新仕様の接続実装(KCP/CLI/exporter)。到達上限=IMPLEMENTED(接続)。
- 禁止: 保護の緩和(既存G0〜G4のAND維持)、`pinned_items`復活、`b1b`既定値の残置、Step B呼出の追加、所有外編集、禁止Git操作(`add -f`/`pull --rebase`/pathspecなしcommit)。
- 時間見込み: 約3h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_04.md` をN=721から順に試し、先頭「## 管理ID」+「GRAMMAR-PREGEN-ALL-LEVELS-01 委任_04」のものを採用(同時刻に委任_03あり)。

## 実施事項

1. **er128**: 契約§4の4関数(凍結v2 items[]の読み書き・照合、`explanation_sha_by_id`照合、level別sidecar `<study_dir>/confirmed_grammar.json`、v1読取互換)、`cmd_from_form`の文法照合(payload v2 `grammar[]`の`candidate_id`/`name`/`explanation_full`を`grammar_explanations.json`と逐語照合、件数≤2、不一致→ISSUE(修正案提示)、0件→`gr.apply_form_selection(ids=[])`でomit)、呼出順の固定(全検証→KPロック→文法ロック→`gr.apply_form_selection`→文法review→sidecar→KPレコード保存=確定点、冪等)、`:850 or "b1b"`/`:1258 discover_dirs(run)[0]`撤去(level必須、`grammar_candidates.json.level`一致確認)、G4のv2対応(2件・本文出現順・節単位)。TypeError 12件解消。test(er128 86件+新規: 文法照合ISSUE、0件omit、2件凍結、level不一致fail-closed、冪等、v1互換)。
2. **CLI**: `grammar-pregen --level <lv> [--ids ...] [--all-candidates]`、`grammar-accept-translation --level <lv> --candidate-id <id> --user-ref <path>`(`op_accept_translation_diff`)、`confirm --from-form`の文法引数、`grammar-show --level`。ヘルプ・エラー文は「次の一手」を明示。
3. **exporter(条件付き)**: `form_grammar_bundle(level)`(核)を使い`grammar[]`(id/name/explanation_full/level/sha)をフォームデータへ。fail-closed(不完全/failed/sha不整合はデータを出さず`data_warnings`+エラー、`candidates_available`にしない)。AI島委任_01の暫定拡張と重複しないよう統合(同じ契約名に揃える)。
4. `IMPLEMENTATION_04.md`、KCP `DESIGN_02.md`付録(文法v2)。

## 事前指定Read一覧

- `docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{SCHEMA_CONTRACT_01,DESIGN_02,IMPLEMENTATION_02}.md`、`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/{DESIGN_02,IMPLEMENTATION_02B,EVIDENCE_02}.md`、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/DATA_MODEL_02.md`
- `er128_kp_confirmed_content_01.py`(全体。特に :74,:835-1000,:1168-1268)、`er119_grammar_review_01.py`(新API: Grep `def apply_form_selection|def op_accept_translation_diff|def form_grammar_bundle|def pregen_stage|argparse|add_argument` ±5)、`er120_part2_wiring_01.py`(Grep `frozen|load_frozen|getattr` ±5)、`er119_kp_human_review_01.py`(Grep `argparse|subparsers|confirm` ±5)、`export_form_data_01.py`(HEAD版+origin/main最新)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_04.md --json-out ...\_check.json`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er128_*_test_*.py"`、`--pattern "er120_*_test_*.py"`、`--pattern "er119_grammar_review_test_01.py"`、`--pattern "er119_*_test_*.py"`、`--pattern "form1_selection_form_v3_test_01.py"`(exporter変更時)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_GPG4.md`にOPEN-556/559更新文案。

## Git

- commit message: `GRAMMAR-PREGEN-ALL-LEVELS-01 委任_04: 確定内容保護へ文法v2接続(from-form文法照合・0件omit・level別sidecar・凍結items[]・b1b既定値撤去)+CLI(pregen/accept-translation)+exporter form_grammar_items(fail-closed)+test(API 0)`。trailer: `Delegation: GRAMMAR-PREGEN-ALL-LEVELS-01/04`。push。

## 報告

`docs/pm/RESULT_PACKET_GPG4.md`: (0)T-0、(1)er128差分(ファイル:行)、(2)CLI、(3)exporter(実施/引継ぎ)、(4)test結果、(5)委任_05 evidenceへの引継ぎ(from-form手順・CLI列)、(6)判断候補、(7)必須4行+「判定整合: 重大NG=<なし|あり>」、(8)SSOT文案、commit hash・raw URL。末尾10行要約。