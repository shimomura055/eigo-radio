## 管理ID

GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05B

(抽出不可・要約再構成: jsonl抽出が index 729-736 でNOT_FOUNDまたは別委任のため、受領した委任文の要点を再構成)

## 性質/禁止

- 性質: 承認済み仕様変更の残配線+既知不具合是正。到達上限=IMPLEMENTED。API 0・JPY0。
- 禁止: 保護緩和、Prompt/品質変更、所有外編集、`add -f`/`pull --rebase`/pathspecなしcommit/force push。SSOT編集権なし。

## 範囲

(1) a1bb5fa71のorigin/main反映確認(未反映ならfast-forward push) (2) er120_part2_wiring_01.py: pregen_stage(all_candidates=)撤去・docstring「PREGEN_MAX=8」修正・form_grammar_bundle<=2確認 (3) er120_part2_wiring_integration_test_01.py の2件採用test2件を1件採用+2件拒否へ (4) GPG4是正: 凍結済み候補でもexplain_signature検査でPart2Staleになる不具合をM6に従い是正、expectedFailure解除 (5) ページbuilder/Validatorの文法ブロック<=1前提確認 (6) Std/Adv mock E2E再確認。
所有: er120_part2_wiring_01.py / er120_part2_wiring_integration_test_01.py / er120_part2_pregen_test_01.py / er128_..._grammar_v2_test_01.py(expectedFailure解除分) / er119_z,x_wiring_test_01.py / docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{IMPLEMENTATION_05B,REMOVAL_RESULT_02}.md / 本ファイル / docs/pm/RESULT_PACKET_GPG5B.md(gitignore)。

## Git

commit message: `GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05B: wiringの新仕様追従(all_candidates撤去・1件採用test)+凍結済み文法のmodel変更耐性(M6)是正+mock E2E再確認(API 0)` / trailer `Delegation: GRAMMAR-PREGEN-ALL-LEVELS-01/05B` / `git push origin HEAD:main`。

## 固定ブロック

従来どおり E-1 / D-1 / G-1 / F-1。T-0: 委任文保存+check(抽出不可のため要約再構成)。T-2/T-3: なし。

## 事前指定Read一覧 / 事前指定Grep一覧(追記位置・更新位置の手順)

IMPLEMENTATION_05A/04/03、SCHEMA_CONTRACT_02、DESIGN_03(引継ぎ節)。Grep: er120_part2_wiring_01.py `all_candidates|PREGEN_MAX|require_final|finalize_stage|explain_signature|frozen|ref_ja`、er120_part2_grammar_production_01.py `PREGEN_MAX|GRAMMAR_MAX|require_fresh_part2|frozen:`、test側 `two_items|expectedFailure|KNOWN_DEFECT`。更新位置=上記の実体箇所のみ。

## 実行コマンド全文

- `.venv\Scripts\python.exe run_project_regression.py --pattern "er120_*_test_*.py"` (同 er128_/er119_z_wiring_test_01.py/er119_x_wiring_test_01.py/er119_kp_p7w5_e2e_test_01.py/er026_*/er019_*)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` -> 0件

## SSOT追記文

編集権なし。RESULT_PACKET_GPG5Bに文案。

## 報告

docs/pm/RESULT_PACKET_GPG5B.md: (0)T-0 (1)差分 (2)不具合根拠 (3)test (4)委任_05 evidence引継ぎ (5)判断候補 (6)必須4行+判定整合 (7)SSOT文案。末尾5行要約。
