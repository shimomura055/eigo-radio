管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_03 兼 PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_03(統合: Part 2 runner接続+文法HR接続+R-7撤去+事故確認。**有料API 0・Production run 0**。evidence R1〜R4は次委任で**本日JST 10/25中**に実施=「翌日」計画は撤回済み)。

## 0. 先に行う確認(事故のFable確認事項)
1. 委任_02で既存testが実リポジトリの共有store `er119_output/kp_human_review_store_01/` に範囲宣言6件を書き込み、削除済みと報告されている。**現在のstore内容を全件列挙**し、宣言(declaration)・NG registryに本日作成のtest由来レコードが残っていないことを確認・報告(残っていれば退避のうえ削除し、何を消したか記録)。test隔離(`KpTestCase.setUp`でSTORE_ROOTをtmpへ)が全test classに効いていることをgrepで確認。
2. 委任_02の有料API到達(推定6〜15円、X既存testのmock漏れ)について、`er119_output/`・`er0XX_output/`に残った実LLM出力(選定結果に`bog`/`speciality`等)の所在を特定し、Production runの成果物dirを汚染していないことを確認(汚染していれば退避)。費用は後でOpenAI usage照合するためtimestamp範囲を記録。
3. 遮断下で見つかった`er103_run_entity_table_01.ensure_table`経由の既存`api.openai.com`接続試行18件(X runner `main(--stage all)`を通る既存test)は、本件とは別の既存問題として**新規OPEN登録**(11-8分類)し、本委任では修正しない(ただし今後の回帰実行はネットワーク遮断harnessで行う)。

## 1. R-7(期限・範囲付き不在宣言)の撤去【ユーザー決定: 不採用】
`er119_kp_human_review_cli_01.py`の`--scope-family/--scope-date/--until`と、核側の範囲宣言ロジック・test・OPERATIONS_01の記述を撤去。残すのは「宣言なし=待機/明示宣言(`--kp-review auto`または`declare-absent`、候補sha・roundに紐づく)のみ自動確定/Human操作で以後のroundは失効/`declared_by`・出所必須・AI宣言は`user_ref`必須」。撤去後の残存Grep 0を報告。

## 2. 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(両案件節を更新、他節を消さない)、KP HR `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/{DESIGN_02,TEST_PLAN_02,BUDGET_PLAN_02,OPERATIONS_01,OPUS_REVIEW_01}.md`、Part 2 `docs/research/PART2-GRAMMAR-PRODUCTION-WIRING-01/{DESIGN_02,TEST_PLAN_02,BUDGET_PLAN_02,OPUS_REVIEW_01}.md`(DESIGN_02 §3=er119へのI/F要求6件、§6未確認事項)、`er119_*`、`er120_part2_grammar_production_01.py`(+test 99)、`er019`/`er026`/`er062`/`er006`(routing契約)。

## 3. 実装Scope(API 0)
W1. `er006`へ`STUDY_TEXT_GRAMMAR_EXTRACT`/`STUDY_TEXT_GRAMMAR_EXPLAIN`を登録(SUPPORT_MODEL契約、列挙test更新)。
W4. 文法HRをer119共通核に`kind="grammar"`で接続: er120 DESIGN_02 §3のI/F要求6件(①`read_mode_declaration()`唯一読取点・dict形 ②共有NG registry `family+slug+level`・`ng=`引数・排他lock・copy-run引継ぎ ③status enumに`NO_CANDIDATE_UNREVIEWED`追加、PENDING/RESELECTION_REQUESTED/STALEは下流fail-closed ④`grammar_selection_signature`共用または突合test ⑤KPと文法のpendingを**1つの`review_request.md`・rc=4 1回**に統合 ⑥決定入力dict `{choice,candidates_sha256,reason,by,accept_ai}`・CLIでreason必須)をer119側で満たす。CLIに文法用操作(status/show/select top1|top2/reselect/omit/reextract/ng/unng/--accept-ai)を追加。KP HR DESIGN_01 §kの「コーナーなし」記述をer120の0件固定文面(`ZERO_P2`)に整合。
W2. Z hook(`er026`/`er062`): `part2_cand_b1b`(input=本文sha+label、候補抽出=Step A''、KP候補生成と同じ待機点の前に実行)と`part2_b1b`(input=`sha(text_sha|label|grammar selection_signature)`、確定後の解説生成)。`DEPENDENTS["r2"]`→`part2_cand_b1b`→`part2_b1b`、`ALL_STAGE_NAMES`/`--regenerate-stage`choices(再finalize=再抽出なし+子孫stale化)、PENDINGは専用例外で出力を書かずに抜ける(rc=4、`[GRAMMAR_REVIEW_PENDING]`または統合マーカー)、`load_level_inputs`(b1bのみ)/`stage_pages`/`stage_page_verify`で`require_fresh_part2(candidates_doc, grammar_review)`、`ctx.stage_context("part2_*")`費用タグ、pagesはPart 1ブロック直後に`compose_study_html`(R-1 CSS)、Standardページに出さない、`verify_selection_matches_outputs(kind="grammar")`をpage_verifyで実行。
W3. X hook(`er019`): 候補抽出をscaffold b1bの本文確定直後(KP候補生成と同一待機点の前)、確定後のStep Bは再開後、`--stage study_text`をPart 2込みに拡張(KP成功前提と分離)、`part2_failed.json`+rc=3、M-7(再開時にsupport/KP/Step A''を再生成しない)、`tts`/`assemble`/`player`入口でM-2検査、公開builderは共通関数1つから(R-2、Standardから呼ばない静的test)、player末尾で一致検証(R-3)。
W5準備. evidence runner計画を`EVIDENCE_PLAN_01.md`に具体化: R1(X・HRあり: KP reselect+NG登録、文法top2)、R3(Z・HRあり: KP select、文法reselect→候補枯渇→omit等)を並列起動→候補確認→CLI操作→再開完走、次にR2(X・auto: R1のNGがskipされること)とR4(Z・auto)。対象記事(既存run dirの再利用可否・本文確定済みのもの)、コマンド列、起動間隔(RESTART_STORM)、期待成果物、stage順序logの取り方、費用見積(KP HR 30〜60円+Part 2約5円、Cap 150円)、`stop_scope_check`。HRの操作はFable/委任agentが行う(ユーザー不要)が、**宣言はAI宣言=`user_ref`にユーザー原文(2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_USER.md「Humanなし」経路の検証指示)を参照**する形にする。
test. 新規統合test(mock・ネットワーク遮断harnessで実行): Opus追加分(Part 2 M-2/M-3/M-4/M-5/M-6/M-7、R-1、Standard非表示、KP+文法の待機1回、再開API 0)。回帰: er003/er019/er026/er062/er063/er105/er106/er108/er117/er119/er120全PASS(既存失敗5件=er109 golden 3・xz_isolation 2は別原因として記録)。**全test実行はネットワーク遮断harness下で行い、`api.openai.com`等への接続試行0を証明**(`.venv`のPythonで実行可=回帰にwordfreq必要のため。ただし有料到達0を遮断で保証)。

## 4. SSOT・Git
OPEN-518(KP HR)・OPEN-519(Part 2)をStatus=INTEGRATED_PENDING_EVIDENCE(本日evidence予定)へ更新、R-7撤去・事故(有料到達推定6〜15円・store書込み事故)を事実として記録。新規OPEN(er103接続試行)。OPEN_ITEMS/DECISION_LOGは直前再Read・最小Edit・バックアップ(Family Y Phase 0 agent・JA ASR agentが並行編集中)。CURRENT_SPEC変更なし(PRODUCTION_WIRED時)。Git: 対象pathのみadd→`git commit --only`→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。`git status --porcelain`で意図外混入なし確認(`er119_output/`はtest隔離後に不追跡であること)。
委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_DELEGATION_03.md`(Nは581前後、先頭「管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_03 兼」を575〜600で走査)。PART2側にも同内容を`..._PART2-GRAMMAR-PRODUCTION-WIRING-01_DELEGATION_03.md`としてコピー保存。

## 5. 禁止
有料API 0(test中の実client生成block+遮断harness必須。mock漏れを再発させない=新入口を呼ぶ既存test一覧をgrepで先に洗い出す)。Production run起動0。Prompt 2/Step A''/Step B/Gate基準の変更禁止。Tier内順位改善・HIGH判定変更・OTHER拡張禁止。期限付き不在宣言の復活禁止。公開ページ・`er0XX_output/`既存成果物の変更禁止(事故退避を除く)。Family Yの正式入口新設禁止(別案件FAMILY-Y-PRODUCTION-LAUNCH-01で設計中。共通核はYから呼べる形を保つ)。

## 6. 報告(RESULT_PACKET_KPHR3.md+口頭要約)
§0の確認結果(store・汚染・timestamp)、R-7撤去の残存0、W1〜W4の変更点、test件数(新規/回帰、PASS、遮断下の接続試行0)、Production runner既定動作(宣言なし→rc=4 1回、KP+文法統合マーカー)、EVIDENCE_PLAN_01の要点(コマンド・費用・所要)、費用0円、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3仕分け)。