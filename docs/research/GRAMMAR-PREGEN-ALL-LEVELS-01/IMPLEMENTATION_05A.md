# IMPLEMENTATION_05A 文法選定仕様変更(Top1/Top2提示・1件選択・0件可・2件禁止)の実装(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05A)

Status: **IMPLEMENTED**(核・確定内容保護・CLI・exporter)。到達上限=IMPLEMENTED。X/Y/Zのrunner・ページ・Validator(委任_03)とフォームUI(AI-ISLAND委任_02)は未着手/別Agent。PRODUCTION_WIREDではない。API 0・JPY0。
契約差分: `SCHEMA_CONTRACT_02.md`、設計差分: `DESIGN_03.md`。承認根拠: ユーザー正式決定2026-10-27(APPROVED_FOR_PRODUCTION)。新flagなし・Prompt/正規表現/閾値/辞書の編集なし。

## 1. 変更(ファイル:行)
| ファイル | 変更 |
|---|---|
| `er120_part2_grammar_production_01.py` | `PREGEN_MAX` 8→2(:48)、`GRAMMAR_MAX` 2→1(:49)、`TOP_N`=2は「提示上限」と注記(:57)。`_pick_ids`(:1621)のメッセージ=2件同時選択禁止。`_require_fresh_part2_v2`(:1928)に結果≤`GRAMMAR_MAX`検査(旧2件結果=Stale)。コメント更新 |
| `er119_grammar_review_01.py` | `render_request_md`(v2): Top1/Top2を「AI推奨(Top1)/Top2」と評価順位付きで順位順に提示、3位以降は「他N件は非表示」の件数のみ、操作案内を1件選択に。`apply_form_selection`/`op_decide`のメッセージ。`require_explanations`の案内から`all_candidates`を撤去 |
| `er128_kp_confirmed_content_01.py` | `GRAMMAR_MAX`=1(:59)・`GRAMMAR_PENDING`(:60)。`_validate_form_grammar`(:1424): 件数≤1、`presented_ids`(Top1/Top2)外=ISSUE、`presented_ids`を戻す。`_write_grammar_sidecar`: `status`/`presented_ids`/`max_select`/`confirmed_after_pending`、pending sidecarは退避せず上書き(`_archive_prior_grammar_files`:1522)。`cmd_from_form(grammar_pending=)`(:1317)・`_pending_grammar_mark`(:1555)・`cmd_grammar_from_form`(:1566)・CLI `--grammar-pending`/`--grammar-from-form`(:1810〜)。`grammar_state`はpending=None(:870/:874)。`_grammar_problems`/`_grammar_sentences`はpath_rel無しのpendingに対応 |
| `er119_kp_human_review_cli_01.py` | `grammar-pregen --all-candidates`**撤去**(:141付近)。help/使い方をTop1/Top2・1件選択に更新 |
| `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py` | `grammar_from_bundle`: items≤2・rank順を検査(:196)。出力に`grammar_max_select=1`/`grammar_present_max=2`/`grammar_presented_ids`/`grammar_candidates_sha256`/`grammar_text_sha256`(:257、`grammar_meta_from_study_dir`:213) |

## 2. test(全てmock・API 0)
- 更新: `er120_part2_pregen_test_01.py`(件数3→2・Top2のみ・3位非表示・reselect後は新Top1の1件だけ生成・2件pick拒否・1件/0件候補の数合わせ無し)、`er119_grammar_review_test_01.py`(依頼書のTop1/Top2表示・CLIで2件pick/3位pick/`--all-candidates`拒否)、`er128_kp_confirmed_content_grammar_v2_test_01.py`(2件系を1件系へ・2件ISSUE・3位ISSUE・presented_ids/exporter新キー)。
- 新規: `er128_kp_confirmed_content_grammar_pending_test_01.py`(pending: KP保護有効/文法保護なし/review PENDING/sidecar pending、pendingのままfinalize=待機、後から1件、後から0件(omit)、冪等、別内容拒否、2件/3位/解説改変のISSUEで何も書かない、KP区分不一致拒否、study dir無し、CLI)。
- 結果: `RESULT_PACKET_GPG5A.md`(3)参照。

## 3. 残置・引継ぎ
- `er120_part2_wiring_01.py`(委任_03所有、本委任では未編集): `pregen_stage(all_candidates=)`引数が残る(`PREGEN_MAX`参照のためTop1/Top2までしか生成しない)。引数撤去・docstringの「PREGEN_MAX=8」・`_pick`系の「複数」記述は委任_03で。wiringの`explain_signature`検査でPart2Stale(GPG4既知不具合)は本委任では触らない。
- `er120_part2_wiring_integration_test_01.py`(委任_03所有): 2件採用を検証する2 test(`XPart2Integration/ZPart2Integration.test_two_items_adopted_*`)は新仕様(2件禁止)と矛盾するため、委任_03で1件採用へ更新が必要(本委任では未編集)。
- レンダラ(`render_markdown`/`render_html_block`/`count_grammar_blocks`)はN件対応のまま(旧2件結果の読取互換)。新規生成は1件以下。
- フォームUI(`user_test/selection_form_v3/**`)・`build_data_01.py`(AI-ISLAND委任_02所有)は`grammar_max_select`/`grammar_presented_ids`を読むだけでよい。
