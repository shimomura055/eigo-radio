管理ID: PART2-GRAMMAR-PRODUCTION-WIRING-01。Opus必須レビュー(PM_GOVERNANCE 11-3 条件A: 新しい処理フローのProduction導入、実装=runner接続の前)。読み取り専用。日本語で報告。

## 背景
ユーザーが2026-10-25に正式採用(APPROVED_FOR_PRODUCTION、Family X/Y/Z共通): ①Part 2「Grammar & Sentence Structure」(Trial-07で検証: 本文から学習価値のある構文を最大1件選定・逐語引用・仕組み/通常語順との比較/意味・ニュアンス解説・適格0件は0件許容)、②Trial-08選定方式(Tier1=倒置以外の適格、Tier2=倒置、Tier3=なし。Tier内順位改善・HIGH判定安定化・OTHER拡張は承認対象外)、④文法Human Review(AIがTOP1/TOP2提示、HumanはTOP1/TOP2/再選定/省略、Human不介入時はTOP1自動採用、未レビューを最終承認扱いしない)。方針: 既知の品質課題を理由に延期しない/追加Trial・基準変更を前提にしない/明確な不具合のみ修正。
ユーザー原文: C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-25_PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md(文字化けあり、要旨は上記)

Sonnet成果物(C:\Users\tensh\eigo-radio\docs\research\PART2-GRAMMAR-PRODUCTION-WIRING-01\): EXISTING_SPEC_CHECK_01.md / DESIGN_01.md / OPUS_REVIEW_REQUEST_01.md(O-1〜O-6) / TEST_PLAN_01.md / BUDGET_PLAN_01.md。
実装: C:\Users\tensh\eigo-radio\er120_part2_grammar_production_01.py(+ _test_01.py、77 PASS、API 0。runner未接続、routing未登録でfail-closed)。
Trial正本: docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/{run_trial_07.py,run_trial_08.py,DESIGN_08,PREREGISTERED_CRITERIA_08,EVAL_08,PART2_TRIAL08_RESULTS_01}.md
接続先: er026_family_z_fiction_production_runner_01.py(stage_kp, kp_part1_ja_b1b, ensure_stage)、er062_family_z_writer_01.py(DEPENDENTS, ensure_stage)、er019_family_x_audio_production_runner_01.py(run_theme_scaffold, --stage study_text)、Part 1参照パターン er003_kp_general_explanation_01.py、KP HR設計 docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/{DESIGN_01,OPUS_REVIEW_01}.md(§k 文法層、kind非依存共通核 er119 は別agentが実装中)。

Sonnet報告の要点: 対象レベルはAdvanced(b1b)のみ(Prompt明記・Trial実績がAdvのみ)。Z=新stage `part2_b1b`(ensure_stage、TTS前、KP非依存、er062 DEPENDENTSのr2従属へ追加要)、X=scaffold b1b内(KP PASS後)+再実行stage+marker、Y=正式入口なし=未配線。Prompt byte一致(Step A'' sha 51912fe1…/Step B 59588b59…)、29標本の再parseでselect_tiered一致。Trialからの差分6点: D-1 parse不能はTrialでは0件扱い→Productionは技術retry1回→STOP(0件にしない)、D-2 全適格候補を順位付きlistで保持(採用1件)、D-3 Step B構造検査追加、D-4 T1訳をStep Bの参考訳として渡す(Prompt本文不変)、D-5 節見出しにPart番号を出さない、D-6 0件時はTrialと同じ固定文面。HR接続: `review_request()`がkind="grammar"でTOP1/TOP2、choice top1|top2|reselect|omit、mode既定wait(PENDING_REVIEW、有料工程へ進まない)、auto明示時のみTOP1自動採用、候補0件は待機せずZERO。routing新process 2件(STUDY_TEXT_GRAMMAR_EXTRACT/EXPLAIN)は次委任でer006登録。原価0.43〜0.48円/セット。

## レビューしてほしい論点(絞る。追加探索可)
1. 移植忠実性: D-1〜D-6が承認済みTrial規則の「意味的変更」に当たらないか(特にD-1: Trialの0件扱いをSTOPへ変える点、D-4: 参考訳の追加がStep B出力を変えうる点=Prompt本文不変でも入力が変わる)。承認範囲内の安全側修正と言えるか、それともユーザー確認事項か。
2. Z配線: `part2_b1b` stageの位置(TTS前・KP非依存)、ensure_stageのinput_sha(本文+HR確定署名を含むべきか)、DEPENDENTS r2従属、`--regenerate-stage`/resume/copy-runでの再利用と再選定の区別、fail-closed(解説欠落のまま公開しない)がpages/assemble/page_verifyまで一貫するか。
3. X配線: scaffold b1b内(KP PASS後)の位置、`--stage study_text`再実行・markerとの整合、rc=4待機(文法HR)からの再開時にsupport等の有料工程を再生成しないか(KP HRのM-4と同じ問題)。
4. 文法HR接続: TOP2定義(同一文を除く次の適格)、reselect時の再抽出(候補が尽きた場合のみ再抽出=有料)の上限と再利用、omit時の表示、NG候補の復活防止がKP HR共通核(NG registry記事単位・宣言のround紐づけ)と同じ強度で効くか、0件ZERO(待機なし)の妥当性、「未レビューをREVIEWED扱いしない」の担保。
5. 描画・組立: Part 1ブロック直後への配置、0件時の固定文面、公開ページ・study_text・確定JSONの一致検証、Standardページに出さないこと。
6. Y: 正式入口なし=未配線の扱いと、OPEN-484要件の妥当性。
7. TEST_PLAN/BUDGET/evidence計画(X/Z各1 run以上、HRあり/なし、KP HR evidenceと同一run)の過不足。

## 出力形式
必須修正(M-n: 理由・具体案・該当箇所)/推奨(R-n)/問題なし確認(C-n)/ユーザー確認が必要と考える点(あれば明示、理由付き)/runner接続着手可否の総合所見。断定できない点は「未確認」。