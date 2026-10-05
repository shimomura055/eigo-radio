# 委任_11(ループ2/3「Fable評価→実装」段、¥0)

## 管理ID
OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01(委任_11)。並行タスクなし。

## 性質/禁止事項
- 性質: Opus#17結果の保存・台帳・Fable評価の記録、¥0集計、Trial専用コードの実装+単体テスト+費用見積。**有料API禁止**(有料Trialは次の委任_12)。
- 禁止: Production正式path(er003*/er009*/er010*/er012*/er019*)変更禁止。編集可はer052_open233_*と文書のみ。既存prompt定数(V0/V4A/3'-R/5-lite)は不変(新定数を追加、sha記録)。Stage 2(er052_open233_self_recovery_stage2_production_01.py)はユーザー承認済み構成(APPROVED_FOR_PRODUCTION)のため変更禁止。gold・fixture・Safety-critical定義変更禁止。git add -A/stash/amend禁止。ACTIVE_TASK.md/RESULT_PACKET.mdはaddしない。1回の書き込み2,500文字以下。長文はファイル間転写スクリプトで。
- T-0: 本ファイルに全文保存(分割)、check実行・結果記録。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## Fable評価(Opus#17後。記録・反映する)
Opus#17(必須レビュー条件A、回数上限外)の結論「条件付き(推奨Fは順序と主軸を組み替え)」を採用。
1. ループ2主構成=Opus別案1: r3(網羅)+r5-V(r3がSUPPORTEDにした単位+関係単位のみをfact→記事方向で検証、記事全文は文脈、r3の引用・判定は見せない)+(B)否定是正案a。∪はnorm_sentence(claim_text)キー統合のためr5がr3-CANDIDATE単位に重なっても検出は増えず、検出集合は構造上維持される。
2. (A)2層化はループ2では不採用(費用削減NORMAL¥0.47のみ、UNSURE triageが第2のStage 1化、goldがUNSURE落ちするリスク)。採用するならOpus#17 §1の3条件(absence型の具体側定義)+保存候補の分類proxy(約¥5〜8)を先に。見出し・hookはUNSURE対象外。OPEN_ITEMS進捗欄に「条件付き保留(採用条件明記)」として残す。
3. (G)reasoning effort引下げ=先行実験(経路別: r3 medium/r5-V medium・low)。採否基準=各経路のモデル判定(M)検出がhigh時より減らない(∪・決定論(D)検出だけで判定しない)。n=18は「不合格を示す用途」に限る。
4. KPI基準点=(iii)で書面固定(Trial前): 追加費用=「新フロー配線後Production」−「現行Production」の同記事種別差。差し引けるのは配線計画上実際に取り除かれる部品=現行英語Stage 1(V4A Ledger逸脱check)の実費のみ。(ii)¥2.77はJA検査・gpt-5.6-luna・重複行(meta run_03、実質n=7)が混在するため使わない。基準点は実質KPI定義のためユーザー確認事項として最終報告に載せる(Fableは保守側(iii)で進める)。
5. Safety合格数にD検出を入れない(経路別M/D区分を採用基準・STOP条件に明記)。
6. 構造的両立不能の判定=「(iii)基準で+¥2超、かつG・r5-Vを試し切った後」。worst run ¥3超は全件記録(§7の¥6は撤回)。
7. 否定是正案aの条件: 合成陽性例を複数(否定付加/除去/二重否定)単体テスト化、「only」を広く除外語に入れない、真の可能性あり2件は残す。
8. Opus別案2(Stage 2出力短縮)は本管理ID対象外(Stage 2はユーザー承認済み構成)。ユーザー向け選択肢として記録のみ。
9. 委任_09の30件ラベルは「Stage 2負荷推定用」に限定(neg4 S2.1/S2.2のR判定の循環は注記)。
10. 費用順序: ¥0(基準点・V4A実費)→ r5-V(保存r3出力再利用、約¥15)+G arm(約¥20)→ 合格組合せのみ小規模fresh(約¥30)→ E2E。

## 作業
A. Opus#17保存: docs/pm/tools/extract_agent_text_from_transcript_01.pyでtranscript(f9ae115b-...jsonl)からマーカー<<<OPUS17_BEGIN>>>〜<<<OPUS17_END>>>を抽出し docs/pm/opus_l2_review_open233_stage1_loop2_17.md へ保存(文字数報告)。失敗時は要点保存とせず原因報告。
B. Opus台帳: docs/pm/OPUS_FINDINGS_LEDGER.md にOF-026〜(#17の指摘: 2層化主軸不適/absence3条件/r5-V/否定案a条件/G先行/2.77不適・(iii)/BLOCKING率過小/fit外挿/ラベル循環/別案2/worst¥3)を1行ずつ、採否=上記Fable評価の番号で。
C. Fable評価の記録: docs/pm/design_open233_stage1_loop2_01.md末尾に§「Opus#17後Fable評価」(1〜10)を追記。DECISION_LOG.mdへはappend_decision_log_from_sources_01.pyで転写(見出し: ## OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01: ループ2 Opus#17後Fable評価(2026-10-05、委任_11))。
D. ¥0集計: (1)KPI基準点(iii)定義文書 docs/pm/kpi_cost_baseline_open233_stage1_01.md(定義・差し引き可否の根拠・Trial前固定宣言・(i)(ii)(iii)対応表)。(2)現行Production英語Stage 1(V4A Ledger逸脱check)の1記事実費を既存usageから集計(er052_output/open233_kpi_recovery_02_offline_01/agg_v4a_stage1_actual_cost_01.{py,json,md}。特定不能なら「特定不能」と報告し推定で埋めない)。(3)(iii)でS0/別案1(+G)の見込みを再計算(委任_10の数値を流用、推測と明記)。
E. 実装(Trial専用、既定挙動不変): er052_open233_stage1_coverage_checker_01.py+runner(er052_open233_self_recovery_flow_runner_01.py)・段階Aスクリプト: (1)STAGE1_R5_MODE∈{full,verify_supported}(r5-V: 入力=r3のSUPPORTED単位+関係単位のID・本文、記事全文、Ledger全文。r3の引用・判定は渡さない。新prompt定数R5V_...+sha、schemaは5-liteと同形)。(2)STAGE1_R3_REASONING/STAGE1_R5_REASONING(既定high、medium/low可)、usage・effortをrun jsonに記録。(3)否定是正案a(日本語Ledger全行照合は不採用、「ほどなく/ではなく/せず」等の除外、「なし」追加、英語Ledger対応、「only」は限定的)+単体テスト(旧149件の再分類が9件になることのregression、合成陽性例>=3種)。(4)集計にM/D区分(候補のsourceにmodel_r3/model_r5/deterministic/coverage_gapを保持し、Safety判定はM限定を別欄で)。(5)worst ¥3超の全件記録欄。既存テスト42件+新規がPASS。
F. 費用見積(¥0): r5-V on 保存r3出力(42 run)・G arm(SC 6x3+hold-out 9+NORMAL 6、経路別effort)の--stage estimateで見積(実行は委任_12)。
G. SSOT: OPEN_ITEMS.md本管理ID行進捗、REPORT_LEDGER.md 1行、ACTIVE_TASK.md(addしない)。
H. commit/push(明示add)。メッセージ: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01: Opus#17保存・台帳OF-026〜、Fable評価(別案1 r3+r5-V+否定案a・G先行実験・(A)条件付き保留・KPI基準点(iii)固定)、V4A実費集計、r5-V/effort/否定是正を実装+単体テスト(委任_11、¥0)

## 事前指定Read一覧
Read: design_open233_stage1_loop2_01.md(全文)、opus_l2_review_open233_stage1_redesign_16.md(§条件のみ)、OPUS_FINDINGS_LEDGER.md(末尾20行)、extract/append_decision_logの使用法ヘッダ、agg_production_baseline_cost_01.py(L1-40)、coverage_checkerはGrepで範囲限定。

## 事前指定Grep一覧+追記位置・更新位置の手順
Grep: checker: NEGATION|polarity|R5_|r5|reasoning|union_candidates|SUPPORTED|def run_。runner: STAGE1_MODE|STAGE1_ROUTES|stage1_coverage_fresh|stage1_fresh_dispatch。stageA: estimate|reasoning|effort。現行Production出力: er0{03,19}*_output/**/raw_usage_log.jsonlでdeviation|vfl|ledgerのstage名。OPEN_ITEMS本管理ID行、REPORT_LEDGER末尾、DECISION_LOG末尾。

## 実行コマンド全文
T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_11.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_11.md_check.json
抽出: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\extract_agent_text_from_transcript_01.py --transcript C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\f9ae115b-0305-437d-ac2d-b452b22a5e2a.jsonl --start-marker <<<OPUS17_BEGIN>>> --end-marker <<<OPUS17_END>>> --out C:\Users\tensh\eigo-radio\docs\pm\opus_l2_review_open233_stage1_loop2_17.md
テスト(指示のpathは存在せず実ファイル名、pytest未導入のためunittest): C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest C:\Users\tensh\eigo-radio\er052_open233_stage1_coverage_checker_01_test_01.py
集計: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\agg_v4a_stage1_actual_cost_01.py
見積: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage1_stageA_01.py --stage estimate --plan g_arm --r5-mode verify_supported --r3-reasoning medium --r5-reasoning medium --estimate-out C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\estimate_loop2_garm33_verify_supported_r3medium_r5medium_01.json
Git: git status --porcelain→明示add→commit→git push origin main→git log --oneline -1。

KPI provenance: 本委任の数値は既存fresh出力(段階A 42 run)の再集計・単体テスト・費用見積(¥0)であり、E2Eではない。到達上限VALIDATED、APPROVED_FOR_PRODUCTIONではない。

## 報告
(1)結論8行以内、(2)表(実装スイッチ一覧、否定是正の旧149件再分類結果)、(3)SSOT・T-0・commit・push・raw URL、一覧外Read、確認/推測、(4)Fableへの論点(委任_12の有料Trial設計上の注意)。
