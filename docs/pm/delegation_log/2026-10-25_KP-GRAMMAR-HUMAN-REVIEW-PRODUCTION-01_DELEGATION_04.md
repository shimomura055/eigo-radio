管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_04 兼 PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_04(正式runtime evidence R1〜R4の有料実走+evidence文書。本日JST 10/25中。Cap 150円[委任_02のmock漏れ推定≤25円を含む]、日次1,500円)。

## 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(両案件節のみ)、`docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/{EVIDENCE_PLAN_01,OPERATIONS_01,DESIGN_02,TEST_PLAN_02,BUDGET_PLAN_02}.md`、`docs/research/PART2-GRAMMAR-PRODUCTION-WIRING-01/{DESIGN_02,TEST_PLAN_02}.md`、ユーザー原文 `docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_USER.md`(検証7点・PRODUCTION_WIRED条件・「Humanなし」経路)と `..._PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md`(受入条件10項目)、`er119_kp_human_review_cli_01.py`(status/show/select/reselect/ng/declare-absent/grammar-*)、runner `er019`/`er026`の`--kp-review`・rc=4・`[KP_REVIEW_PENDING]`。

## 事前確認(各起動前)
- `git log origin/main --oneline -5`にcommit `daf0fdb8a`(統合)が含まれ、作業ツリーがそれ以降であること。
- `py docs/pm/tools/daily_dev_cost_01.py`の当日累計+94.28円(ツール未捕捉)+本委任見積(≤70円)が1,500円以内(並行でFamily Y E-1/E-3 ≤146円が走る可能性あり。各起動前に再確認)。
- `py tools/stop_scope_check_01.py --managed-id KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 --run-dir <run_dir> --out <run_dir>/stop_check_<name>.json`(rc=3なら起動しない)。
- 共有store(`er119_output/kp_human_review_store_01/`)にtest由来の宣言・NGがないことを再確認(list)。
- 有料は`.venv\Scripts\python.exe`。同一run dirへの起動間隔150秒以上・5分3回禁止(Z RESTART_STORM、Xは手動遵守)。外部停止/原因不明rc≠0が2回続いたら再起動せずSTOP。

## 実走(EVIDENCE_PLAN_01の順序。対象記事は計画どおり=本文確定済みの既存run dirをcopy-run/新run dirで。X/Z各HRあり・なし)
- **R1(X・HRあり)+R3(Z・HRあり)を並列起動** → 候補生成後rc=4(`[KP_REVIEW_PENDING]`1回、`review_request.md`にKP TOP 8と文法TOP 2が統合表示)→ CLIで**HRあり操作**: KP=AI順位と異なる3件を`select`(理由)+1件を`ng`(理由必須)+必要なら`reselect`1回、文法=R1は`grammar-select top2`(理由)、R3は`grammar-reselect`(理由)→候補が尽きる場合は`omit`(理由)→同じコマンドで再開→完走(Part 1[5件]・Part 2解説・TTS・ASR・gate・assemble・pages・page_verify)。
- **R2(X・HRなし)+R4(Z・HRなし)**: `declare-absent`(`declared_by`=Fable代行、`user_ref`=ユーザー原文「Humanなし」経路の検証指示、候補sha/round紐づけ)→自動確定(KP TOP1〜3・解説TOP1〜5・文法TOP1)→完走。R2では**R1で登録したNGが同一記事の候補からskipされる**ことを確認(同一記事・別run dirで実施)。
- 各runで収集(evidence 7点/10項目): stage順序log(候補抽出がKP候補生成と同一待機点の前、Step Bは確定後)、rc=4が1回、再開時の有料API 0(support/KP選定/Step A''の再実行0をcost logで)、確定JSON↔Part 1/Part 2↔study_text↔TTS結果↔公開ページの一致(`verify_selection_matches_outputs` KP/grammar)、NGと未レビュー(NOT_SELECTED/null)の区別、`UNREVIEWED_AUTO_ADOPTED`がREVIEWEDと数えられない、Advancedのみ表示・Standard非表示、0件固定文面(該当時)、actual model_id/routing key/Prompt sha(Prompt 2無変更sha・Prompt 2-V sha・Step A''/Step B sha)、Redundancy QA確定集合再適用、実費(stage別)、所要、retry/HR Lock。
- 公開: 既存の`user_test/`運用に従い**evidence用dirのみ**(既公開記事の差替えはしない)。page_verify PASS後にPages反映確認。
- `EVIDENCE_01.md`(R1〜R4結果、検証7点×証跡、受入条件10項目×証跡、機能×Family[X/Y/Z]のStatus表案[Y=未配線・OPEN-484/520]、実費・量産単価実測[KP HR+Part 2の増分]、HR負担の実測時間、残課題)。`BUDGET_LOG_01.md`。

## SSOT・Git・逐語保存
OPEN-518/519更新(evidence結果。PRODUCTION_WIRED判定はFable=本委任では書かない)。直前再Read・最小Edit・バックアップ(他agent並行編集中)。CURRENT_SPEC変更なし。Git: 対象pathのみ(wav/raw_usage_log/STOP/lock不追跡、公開mp3は`user_test/`配下のみ)→`git commit --only`または一時index方式→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_DELEGATION_04.md`(Nは597前後、先頭「管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_04 兼」を590〜635で走査)+PART2側へコピー。

## 禁止
Prompt 2/2-V/Step A''/Step B/Gate基準の変更。コード変更は実走で見つかった明確な不具合の最小修正のみ(変更内容・理由を記録し、修正後の再実走は起動間隔を守る)。既公開ページの差替え。Family Y runnerの起動(別案件)。Cap/日次超過。

## 報告(RESULT_PACKET_KPHR4.md+口頭要約)
R1〜R4の結果(表)、検証7点・受入10項目の充足/未充足、HRあり/なしの証跡、NG skip証跡、実費・単価増分実測・HR所要、不具合と最小修正、公開URL(evidence用)、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。