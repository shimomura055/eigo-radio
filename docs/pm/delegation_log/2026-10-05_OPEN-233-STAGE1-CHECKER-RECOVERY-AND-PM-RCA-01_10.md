# 委任_10(ループ2/3「RCA・設計」段、¥0)

## 管理ID
OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01。並行タスクなし。

## 性質/禁止事項
- 性質: ¥0分析+設計文書作成+Opus#17レビューpacket作成。有料API禁止。Checker・runnerコードの変更禁止(実装はOpus#17→Fable評価の後)。試算用スクリプトは`er052_output/open233_kpi_recovery_02_offline_01/`配下の新規オフラインスクリプトのみ可(既存モジュールのimportは可、書き換え不可)。gold・fixture・Safety-critical定義の変更禁止。SSOT編集は`OPEN_ITEMS.md`該当行進捗欄・`REPORT_LEDGER.md`1行のみ。`git add -A`/`stash`/`amend`禁止。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。1回の書き込み2,500文字以下。
- T-0: 本ファイルに全文保存(分割)、check実行・結果記録。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## Fable判断(ループ1の結果)
委任_09(commit 675b4cb4)の見込み【No】を受け、段階B(E2E 40〜50円)は見送り、ループ2へ入る。ループ1の記録: 「Safety採用基準は合格、Cost KPI見込みNo(Stage 1のみで+1.5円/run、Stage 2外挿込み+3.0、NORMAL +4.4、基準+2)」。ユーザー指示: 「重大に対して甘くするのは禁止。重大でないものへの過剰検出削減は可。Safety-criticalの定義・gold・母数を都合よく変更禁止」「『LLMは揺れるから仕方ない』で終わらせない」。ループ2も「RCA/設計→Opus独立レビュー→Fable評価→実装→限定Trial→KPI評価」の順。

## 作業(出力: docs/pm/design_open233_stage1_loop2_01.md、docs/pm/opus_packet_open233_stage1_loop2_01.md、試算er052_output/open233_kpi_recovery_02_offline_01/loop2_cost_structure_01.{py,json,md})
1. 費用構造RCA(¥0、実測): 段階A 42 run・84 callのraw usage(input/output/reasoning tokens、model)をcall種別(r3初回/r3欠落再実行/r5)別に集計し、0.763円/callの内訳を出す。出力tokenのうちSUPPORTED単位の逐語引用(support_fact_ids+quote)が占める割合を推定(出力jsonの文字数から)。「Stage 1だけで+1.5円」の主因を特定(出力長か、reasoningか、入力のLedger長か)。
2. SC 6件の候補の具体性(委任_09の未集計分): SC 18 run・hold-out 9 runで、gold対応候補のflags・issue・related_fact_id・claim_in_articleを列挙し、「fact Xの要素Yと食い違う」と具体化できているか(汎用フラグのみか)を判定。(A)2層化でSC候補が全て「具体側」に残るかの根拠。neg5(R:関係単位)・HF-011も含む。
3. (B)否定極性検査の是正案の¥0検証: 是正案(日本語Ledger全行照合/「なし」「ではなく」対比構文・「ほどなく」「せず」の除外/英語Ledger対応、または決定論検査から否定を外しLLM changed_negationへ寄せる)をオフラインスクリプト内で再実装し(モジュール書き換え禁止)、旧149件のうち残る件数、「真の可能性あり2件」の扱い、SC/hold-outの検出に影響しないこと(否定系SCがLLM経路で検出済み)を確認。
4. 設計案の比較(各案: 構造・Safety影響(SC 6件+hold-out 9種+neg5ごとに「検出維持の根拠」)・費用見込み・実装規模・Opus論点): (A)2層化(CANDIDATE=具体的discrepancy必須、不能はUNSURE→安価triage。triage方式候補: 決定論/小batch gpt-6-luna/「迷って候補」のみbatch)、(B)決定論是正、(C)Stage 2 batch化(同一fact束ね、上限なし)、(D)経路整理(r3がほぼ上位集合、r5のみ0.7/記事、SC r3単独18/18・r5単独17/18。r5廃止は0.76円/run削減だが冗長性を失う→Safety根拠を正直に。r5を「r3の欠落ID補完専用」に縮小する案も)、(E)Stage 1出力の軽量化(SUPPORTEDはsupport_fact_idsのみで逐語引用を省く/CANDIDATEのみ引用必須。quote_not_in_ledger検査への影響と、引用省略で3'-Rの「網羅強制」が弱まらないかの根拠)、(F)組合せ案(推奨構成)。各案の費用見込みは1.の実測構造から積み上げ、rep30同基準で「+x円/run(Stage 1+Stage 2+Rewrite)」とProduction基準2.77円併記。
5. 推奨構成とKPI見込み: 組合せでHuman Review 0/見逃し0/+2円を満たす見込み(Yes/No/不明、根拠)。限定Trial計画(¥0 offline→小規模fresh(何run・円)→E2E(何run・円))と予算(残約174円: 枠238円−使用64.20円)。STOP条件(Safety-Cost構造的両立不能の判定基準を明記)。
6. Opus#17 packet: 論点を絞る(①(A)2層化でSafetyを緩めていないか/UNSURE triageの妥当性、②(D)/(E)の費用削減がSafety冗長性を損なうか、③(B)是正の妥当性、④費用見込みの前提の穴、⑤「追認させない」ため、Fable/Workerの推奨とは別案も出すよう依頼)。委任_09の30件ラベル(推測)の抜き取り妥当性確認も依頼項目に。読み先ファイル・Grep語を列挙(全文読み禁止注記)。
7. SSOT: OPEN_ITEMS.md本管理ID行進捗「ループ1: Safety合格・Cost見込みNo→段階B見送り。ループ2/3開始: 委任_10 RCA・設計(費用主因【…】、推奨【…】、見込み【…】)、次Opus#17」。REPORT_LEDGER.md 1行。ACTIVE_TASK.md(addしない)にループ2開始・Fable判断を記録。
8. commit/push(明示add: 設計文書・packet・試算スクリプト/出力、OPEN_ITEMS、REPORT_LEDGER、委任ログ+check.json)。メッセージ: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01: ループ2 RCA・設計(Stage 1費用主因【…】、SC候補具体性、否定検査是正¥0検証、案A〜F比較・推奨構成・KPI見込み【…】)、Opus#17 packet(委任_10、¥0)

## 事前指定Read一覧
docs/pm/design_open233_stage1_loop2_prep_01.md(全文)、er052_output/open233_kpi_recovery_02_offline_01/stageA_candidate_composition_01.md(全文)、docs/pm/design_open233_stage1_coverage_impl_01.md(全文)、docs/pm/opus_packet_open233_stage1_redesign_01.md(形式参照)、docs/pm/opus_l2_review_open233_stage1_redesign_16.md(Opus#16の条件・懸念、再発防止)。段階A run json(Pythonで一括、usage欄)。

## 事前指定Grep一覧+追記位置・更新位置の手順
er052_open233_stage1_coverage_checker_01.py: negation|polarity|NEGATION_WORDS|quote_not_in_ledger|support_fact_ids|SUPPORTED|usage→該当範囲のみRead。er052_open233_stage1_stageA_01.py: usage|cost|tokens。DECISION_LOG.md: STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01(ユーザー原文、該当節のみ)。docs/pm/PM_GOVERNANCE.md: 11-3|11-4|11-5。OPEN_ITEMS本管理ID行。REPORT_LEDGER末尾。

## 実行コマンド全文
T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_10.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_10.md_check.json
試算: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\loop2_cost_structure_01.py
Git: git status --porcelain→明示add→commit→git push origin main→git log --oneline -1。

## 報告
RESULT_PACKET.mdには短い要約(20行程度)。詳細は上記出力ファイルへ。報告(短く): (1)結論8行以内(費用主因、SC候補の具体性、(B)是正後の残件、推奨構成と見込みYes/No/不明、Trial計画と費用)、(2)表(案A〜F比較: Safety根拠/費用/規模)、(3)Opus#17 packetの論点一覧、(4)SSOT・T-0・commit・push・raw URL、一覧外Read、確認/推測、(5)Fableへの論点。
