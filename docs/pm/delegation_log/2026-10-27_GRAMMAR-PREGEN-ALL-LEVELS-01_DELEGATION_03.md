## 管理ID

GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03(**最優先・緊急**: 委任_02の共通核(commit 26383d6c7/b27d88309)で`level`必須化・finalize LLM引数撤去により、X/Y/Z runner経由のPart 2が`TypeError`(API前fail-closed)になっている=origin/mainのProduction runnerがPart 2 stageで動かない状態。F-4 adapter配線(X/Y/Z runner: `candidate_and_pregen_stage`・`level`渡し・`cand_marker(level=)`・`finalize_stage`のLLM引数撤去)、ページ側(Std節の文法ブロック、`public_study_html(level=)`、節単位4者一致検査の配線)、Validator/test更新(`*_ON_STANDARD_PAGE`置換、X `--stage study_text`のAdv限定parser.error撤去、旧integration test更新)、KCP3所見D1(自動採用runへ後から確定を入れると来歴親sha不一致でSTOP→API 0再バインド)・D4(拒否されたregenerateが`part2_failed.json`を残しループ)の是正。API 0・JPY0)。設計=`DESIGN_02.md`/`SCHEMA_CONTRACT_01.md`/`IMPLEMENTATION_02.md` §4。並行Agent: (a)GRAMMAR-PREGEN-ALL-LEVELS-01 委任_04(`er128_kp_confirmed_content_01.py`・`er119_kp_human_review_cli`・フォームexporter)、(b)AI-ISLAND-FORM-PRODUCTION-01 委任_01(フォームデータ・exporter最小拡張・DEV文法生成。runnerは使わない見込み)。**あなたの所有**=`er019_family_x_audio_production_runner_01.py`、`er121_family_y_runner_01.py`、`er026_family_z_fiction_production_runner_01.py`、`er062_family_z_writer_01.py`(stage台帳)、`er063_family_z_audio_01.py`、`er121_family_y_audio_01.py`(ページ差込)、`er_user_listening_page_common_01.py`、`er019_nws2_final_page_01.py`(共通関数呼出のみ)、`er120_part2_wiring_01.py`(adapter向け薄い追加のみ。核のAPIは変えない)、integration test(`er120_part2_wiring_integration_test_01`/`er119_z_wiring_test_01`/`er119_kp_p7w5_e2e_test_01`/X runner wiring test)、`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{IMPLEMENTATION_03,REMOVAL_RESULT_01}.md`、`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_03.md`(+check.json)、`docs/pm/RESULT_PACKET_GPG3.md`(gitignore、`-f`禁止)。er128/er119_kp_human_review/exporter/フォームは編集しない。SSOT編集権なし。pathspec付きcommit(`git commit <pathspec>`、他Agentのstage分を巻き込まない)。

## 性質/禁止

- 性質: 承認済み新仕様のProduction配線第2段(runner/ページ/Validator)+runner不動作の緊急解消。到達上限=IMPLEMENTED(配線)。
- 禁止: Prompt/品質変更、Advanced限定条件の残置、Step B呼出点の追加、Part 1のStdへの拡張(対象外)、`_assert_study_ready`をtts_a2に付けること、公開済みX記事scriptの書換え(履歴)、新flag、所有外編集、禁止Git操作(`add -f`/`pull --rebase`/pathspecなしcommit)。
- 時間見込み: 約4h。**最初の1時間でrunnerの`TypeError`解消(最小adapter)を先行commit・pushし、その後ページ/Validator/D1/D4**。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし(mock E2Eのみ)。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_03.md` をN=721から順に試し、先頭「## 管理ID」+「GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03」のものを採用(同時刻に委任_04あり)。

## 実施事項

1. **緊急(先行commit)**: X/Y/Z runnerのPart 2呼出を核の新API(`candidate_and_pregen_stage(level=...)`、`finalize_stage(level=...)`LLM引数なし、`cand_marker(level=)`)へ適合。Std(a2)/Adv(b1b)の両levelでstage定義(Y `DEPENDENTS`/Z stage台帳`er062:64-72`は葉のまま、TTS依存辺を張らない)。Std study dir=`<out>/a2/study_text`。`_assert_study_ready`はpages/page_verifyのみ。integration test(14+13+1件)を新APIに更新しPASS。先行commit message: `GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03a: X/Y/Z runnerを文法事前生成核の新API(level必須)へ適合(runner TypeError解消、API 0)`。push。
2. **ページ**: 共通builder(`er_user_listening_page_common_01.py:51-70`)経由でStd節にも文法ブロック(Advと同一テンプレート、Part 1なし)。Y `if lvd["id"]=="advanced"`(er121 runner:1113付近)/Z `label=="Advanced"`(er063:2588付近)/X `build_player_html`(er019:3022付近)の限定解除、`public_study_html(level=)`必須。2件採用時は本文出現順。節単位4者一致検査`verify_outputs(level, html_text=節)`をpages/page_verifyに配線(fail-closed)。
3. **Validator/test**: `FAMILY_Y_PART2_ON_STANDARD_PAGE`(er121:945付近)/`FAMILY_Z_PART2_ON_STANDARD_PAGE`(er026:1708付近)を「自levelの節に文法ブロックがちょうど1個(0件確定時は固定文面)」+節単位検査へ置換。X `--stage study_text`のAdv限定`parser.error`(er019:3548付近)撤去。`m.LEVEL=="Advanced"` assert撤去。mock E2E(X/Y/Z)で両levelのPart 2(候補≥1→事前生成→HR待ちrc=4→mock確定→finalize→pages)と0件経路、2件採用経路を通す。
4. **D1**: Y/Z runnerで、確定(フォーム/HR)によりreview署名が変わった場合の`kp_<lv>`来歴input_sha不一致を、API 0で再バインド(確定由来の署名変化のみ。本文変化は従来どおりSTOP)。test。
5. **D4**: 拒否された`--regenerate-stage part2_cand_<lv>`が`part2_failed.json`を書かない/書いた場合に「次の一手」が同一コマンドのループにならない(revoke案内)。test。
6. `REMOVAL_RESULT_01.md`(撤去: `*_ON_STANDARD_PAGE`、Adv限定parser.error、`m.LEVEL`assert、Adv限定分岐。残存Grep 0件の証跡)、`IMPLEMENTATION_03.md`。

## 事前指定Read一覧

- `docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{DESIGN_02,SCHEMA_CONTRACT_01,IMPLEMENTATION_02,ADV_ONLY_INVENTORY_01,CURRENT_FLOW_01}.md`(§4引継ぎ・C1-C8条件・撤去一覧)
- `er120_part2_wiring_01.py`(全体、新API)、`er120_part2_grammar_production_01.py`(Grep `def pregen|def finalize|def candidate|level` ±5)
- runner: `er019_family_x_audio_production_runner_01.py`(Grep `part2|study_text|build_player_html|public_study_html|parser.error` ±10)、`er121_family_y_runner_01.py`(Grep `part2|DEPENDENTS|advanced|ON_STANDARD_PAGE|input_sha|provenance` ±10)、`er026_family_z_fiction_production_runner_01.py`(Grep `part2|ON_STANDARD_PAGE|Advanced|input_sha|cand_input_sha` ±10)、`er062_family_z_writer_01.py:60-80`、`er063_family_z_audio_01.py:2570-2600`、`er121_family_y_audio_01.py`(Grep `study_html|part2` ±8)、`er_user_listening_page_common_01.py:40-80`
- `docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/EVIDENCE_02.md`(D1/D3/D4の事実)、`tools/kcp3_ev_y_rebind_01.py`(D1の暫定手当て)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_03.md --json-out ...\_check.json`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er120_*_test_*.py"`、`--pattern "er119_z_wiring_test_01.py"`、`--pattern "er119_kp_p7w5_e2e_test_01.py"`、`--pattern "er030_*_test*.py"`、`--pattern "er121_*_test_*.py"`、`--pattern "er026_*_test_*.py"`、`--pattern "er019_*_test_*.py"`、`--pattern "er063_*_test_*.py"`(既存失敗=OPEN-543は切り分け。er128側のTypeError 12件は委任_04が解消)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_GPG3.md`にOPEN-559更新文案(配線完了、撤去一覧)、OPEN-543関連。

## Git

- 先行commit(上記1)+本体commit: `GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03: Std/Adv両levelの文法ブロック(X/Y/Zページ)・節単位4者一致検査・Adv限定Validator撤去・来歴再バインド(D1)・regenerate拒否時の後始末(D4)+mock E2E(API 0)`。trailer: `Delegation: GRAMMAR-PREGEN-ALL-LEVELS-01/03`。push。

## 報告

`docs/pm/RESULT_PACKET_GPG3.md`: (0)T-0、(1)緊急解消の差分とtest、(2)ページ/Validator差分(ファイル:行)、(3)D1/D4、(4)mock E2E結果(両level・0件・2件)、(5)委任_05 evidenceへの引継ぎ(stage列・go/no-go手順)、(6)判断候補、(7)必須4行+「判定整合: 重大NG=<なし|あり>」、(8)SSOT文案、commit hash・raw URL。末尾10行要約。