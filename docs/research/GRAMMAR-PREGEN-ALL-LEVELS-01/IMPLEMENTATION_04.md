# IMPLEMENTATION_04 文法解説の事前生成: 確定内容保護(er128)・CLI・フォームexporterへの接続(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_04)

Status: **IMPLEMENTED(接続)**。到達上限=IMPLEMENTED。X/Y/Zのrunner配線・ページ・Validatorは委任_03、実run evidenceは委任_05。PRODUCTION_WIREDではない。API 0・JPY0。
根拠: 承認済み新仕様(ユーザー正式決定 `docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_USER.md`)の接続実装。承認済みPrompt/閾値/辞書/正規表現・保護のAND(G0〜G4)は無変更。新flagなし。
契約: `SCHEMA_CONTRACT_01.md` §2(review v2)・§4(凍結v2 + KCPの4関数)・§5(form_grammar_bundle / cmd_from_formの照合)・§6(ISSUE解消)。設計: `DESIGN_02.md` O-4(呼出順)。

## 1. er128(確定内容保護)の変更 — `er128_kp_confirmed_content_01.py`
| 項目 | 内容(関数:行) |
|---|---|
| 契約§4の4関数 | `load_frozen_grammar_items`(:903) / `freeze_from_sidecar_items`(:990) / `freeze_part2_result_items`(:967) / `verify_part2_items`(:1046)。wiring(`er120_part2_wiring_01`)が`getattr`で個別に検出して自動的にこちらを使う |
| 凍結 v2 | `_write_frozen_items`(:941): `confirmed_grammar_frozen.json`は`eigo_radio_confirmed_grammar_frozen_v2`(`items[]`≤2、各item`frozen_sha256`=従来式、`file_sha256`)。**全件まとめて1ファイル(all-or-nothing)**。v1(トップレベル単一item)は`_fz_items_of`が長さ1として読取互換(書き換えない) |
| 読込の検査 | 自己sha・`confirmation_id`・各item sha・**確定した文法集合との一致(過不足なし)**が崩れればINTEGRITY(G4) |
| G4(verify) | 結果(v2 `items[]`/v1単一)の文法id集合==確定集合、各itemの英文・解説全文・訳==凍結値。確定1件以上なのにZERO/別集合=INTEGRITY。**確定0件(フォームで文法なし)なのに結果に文法=INTEGRITY**。`decision.explanation_sha_by_id`とsidecarの`explanation_sha256`の照合(`_review_shown_sha_diffs`) |
| v1互換API | `load_frozen_grammar`/`freeze_part2_result`/`freeze_from_sidecar`/`verify_part2`は2件以上で黙って先頭を返さず(`_single`→`KpReviewError`)、`*_items`へ委譲。証跡tool(`kcp2b_ev_*`/`kcp3_ev_*`)の呼出は無変更で動く |
| level | `_rec_level`(:275): レコードの`article.level`(a2/b1b)必須。**`or "b1b"`(旧:853/:1097)撤去**。sidecar v2は`level`を持ち、`grammar_state`が確定レコードのlevelと照合(別levelのsidecar混入=INTEGRITY) |
| `guard_grammar` | `candidate_ids`(確定集合と完全一致のときだけ許可)対応。`candidate_id`単独は確定が1件のときのみ。確定0件は同じ0件のみ許可 |
| sidecar | `_write_grammar_sidecar`(:1483): `<study_dir>/confirmed_grammar.json`を**level指定のstudy dir**へ(`discover_dirs(run)[0]`撤去)。schema v2(`level`/`explanation_sha_by_id`/各item`explanation_sha256`)。**0件も記録**(items空=『文法なしの確定』)。再確認(revoke後)では前の凍結値・sidecarを`RECONFIRM_SUPERSEDED`へ退避(confirmation_id違いの凍結でINTEGRITY化しない) |

## 2. `cmd_from_form` の文法照合と呼出順 — `_validate_form_grammar`(:1390)・`_apply_form_grammar_review`(:1469)
順序(DESIGN_02 O-4): **(1)文法照合(何も書かない)→(2)既存の`rv.op_select`(KP検証)→(3)KPロック→(4)`gr.apply_form_selection`(文法ロック。0件=同ロック内でomit・冪等)→(5)sidecar→(6)KPレコード保存=確定点**。
- 照合: payload `selection.grammar[]`(フォームの実キー`id`/`title`/`explanation_full`/`explanation_status`/`example`。`candidate_id`/`name`の別名も受理し、矛盾はISSUE)を、**そのlevelの**事前生成物と逐語照合: idが現候補docにある / `title==construct_ja` / `explanation_status=="provided"` / **`explanation_full==explanations[id].explanation_md`(バイト一致)** / (あれば)`explanation_sha256`・`example`一致 / 件数≤2 / 重複なし。
- 不一致=`ConfirmedContentIssue`(rc=4)。`confirmed_content_issue.json`に差分と**修正案(正しい文法名・解説sha)**を記録し、KP review・文法review・sidecar・レコードのどれも書かない。titleでの対応付け・解説の書換え採用はしない。
- fail-closed(CliError rc=2、次の一手つき): 文法study dirなしで文法あり / levelの候補doc不一致 / 複数dir / **事前生成が不完全・`part2_failed.json`・sha不整合は文法0件の送信でも拒否**(`grammar-pregen`を案内)。
- 文法を見せていないフォーム(study dir自体がない)の0件は従来どおり(文法の記録を作らない)。
- 冪等/crash: 文法review適用後・レコード保存前に落ちても、同じ入力の再送で文法reviewは変更されず(revision不変)、レコードが作られる。レコード確定後の同一再送は従来どおり`CONFIRMED_CONTENT_LOCKED`。
- `frozen_sha`は`er120.frozen_sha_of`と同一式(突合test)。`GRAMMAR_MAX`は`er120.GRAMMAR_MAX`と同値(突合test)。

## 3. CLI — `er119_kp_human_review_cli_01.py`(`--level`必須。先頭dir・path推定なし)
- `grammar-show/select/ng/unng --run --level`: `gr.discover_dirs(run, level)`(候補doc levelと一致確認・曖昧はエラー)。
- `grammar-select --choice pick --ids <id>[,<id>]`(最大2件・本文出現順へ正規化)。`--choice top1/top2/omit/reselect/reextract`は従来どおり。`pick`に`--ids`無し・`pick`以外に`--ids`はエラー。
- `grammar-accept-translation --level --candidate-id <id>[,..] --user-ref <path> --by [--reason]`: `gr.op_accept_translation_diff`。`--user-ref`のファイルが存在しなければ拒否。再送は冪等(`already_recorded`)。
- `grammar-pregen --level [--ids] [--all-candidates] [--managed-id]`: `p2w.pregen_stage`(Step B唯一の呼出点)を呼ぶだけ(**Step B呼出は追加していない**)。有料(約0.3円/件・先頭8件)。実行前に`tools/stop_scope_check_01.py`の`check`でSTOP適用を確認し、適用ありなら有料呼出なしで拒否。再実行は未生成分のみ(signature一致は再利用=API 0)。`--all-candidates`は明示opt-in(auto採用/確定済みrunの事後Review用)。**`--ids`は核の`pregen_stage`が未対応のため、この版では指定すると拒否(黙って全件生成しない)**。核に`ids`引数が追加されれば自動的に渡す(`inspect.signature`検出)。
- 依頼書(`render_request_md`)のコマンド案内に`--level`を追加(`er119_grammar_review_01.py`の文字列のみ。核ロジック無変更)。

## 4. フォームexporter — `export_form_data_01.py --grammar-study-dir <study_dir>`(AI島委任_01の`--grammar-bundle`とは排他・同じ契約名)
- `grammar_bundle_from_study_dir(study_dir, level)`が`form_grammar_bundle(study_dir, level=)`を直接読み、既存の`grammar_from_bundle`(AI島委任_01)でフォームentryへ(id/candidate_id/title/body=explanation_full/explanation_sha256/level/rank/ai_recommended…)。
- fail-closed: 事前生成不完全・`part2_failed.json`・explanations/sha不整合・level不一致は**出力ファイルを作らず**stderrへ`GRAMMAR_NOT_READY`+`data_warnings`+次の一手を出してrc=4。`candidates_available`にしない(`no_candidates_found`=0件と区別)。
- AI島委任_01の`--grammar-bundle`(保存済みbundle json)経路は無変更で残置(暫定・今回記事限り用)。正式経路は`--grammar-study-dir`。

## 5. 既存testの更新(理由付き)
| test | 変更 | 理由 |
|---|---|---|
| `er128_..._02b_test_01.py` `TestM6Part2Frozen` | helperをv2へ(フォームは事前生成物と逐語一致、両levelをフォーム確定、`level="b1b"`、凍結=`items[]`/`form_displayed`、LLM呼出は`base_calls`基準) | v2仕様(解説は確定前に事前生成。確定後にStep Bなし)。旧『解説なしで確定→確定後にStep B』は廃止(ISSUEで拒否する新testに置換) |
| 同 `test_KNOWN_DEFECT_...` | `@expectedFailure`で明示 | **不具合(wiring側)**: `require_final`/`finalize_stage`が凍結済み候補でも事前生成物のexplain_signature(model依存)を検査し、model変更でPart2Stale。M6要件(model変更で失効しない)に反する。wiring(委任_03/核の所有)の修正待ち。修正されたら`unexpected success`になるので通常testへ |
| `TestYStageKpG1Runtime`/`TestZPersonGate`/`TestZStageKpG1`(2ファイル) | 文法のHuman確定を両level(b1b/a2)へ | Stdにも事前生成+確認が入ったため |
| `er128_..._test_01.py` `test_grammar_sidecar_written_and_tamper_detected` | `{}`の偽候補docを実際の事前生成済みfixtureへ | levelの候補doc不一致はfail-closedになったため |
| `er119_grammar_review_test_01.py` TestCli | `--level b1b`を付与 | grammar-*の`--level`必須化 |

## 6. 旧ルール撤去・残置のGrep(Charter 8)
| 識別子 | 状態 | 確認 |
|---|---|---|
| `or "b1b"`(er128:853,1097) | 撤去(`_rec_level`) | `grep -n 'or "b1b"' er128_kp_confirmed_content_01.py` = 0件(test T10が恒久検査) |
| `gr.discover_dirs(run)`の先頭選択(er128:1258・CLI:`gdirs[0]`) | 撤去 | `grep -n "discover_dirs(run)" er128_kp_confirmed_content_01.py`=0件。CLIの`discover_dirs(a.run)`はstatus一覧(level未指定=列挙のみ)の1か所 |
| `explanation_status=="missing"`での確定(確定後にStep B) | 撤去(ISSUE) | test `test_form_with_unpregenerated_explanation_is_issue_and_confirms_nothing` |
| v1凍結/sidecar読取・v1名API | 残置(読取互換。書込みはv2) | test `T7_V1Compat` |

## 7. 次委任への引継ぎ
- **不具合(修正へ進む。wiring側=委任_03または別委任)**: `require_final`/`finalize_stage`の`validate_explanations`が凍結済み候補のsignature失効まで検査する(上表)。修正案: 凍結値でカバーされる候補のitemは署名検査から除く(`ids`から凍結済みを除外し、itemループも対象を絞る)。KCP側の関数は凍結済みなら`frozen_sha`で検証するので、wiring側のみの修正で足りる見込み(未検証)。
- `grammar-pregen --ids`: `pregen_stage`に`ids`引数を追加(任意最適化・費用削減)。
- 委任_05 evidence手順: `RESULT_PACKET_GPG4.md` (5)参照。
