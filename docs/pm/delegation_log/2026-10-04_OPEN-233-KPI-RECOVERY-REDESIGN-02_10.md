## 管理ID

`OPEN-233-KPI-RECOVERY-REDESIGN-02`(委任_10)。親: `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: Step 7(再ループ)の前半=**¥0のみ**。rep29(委任_09、`er052_output/open233_self_recovery_flow_runner_01_rep29/`)で残ったHuman Review 3件(s1/s2 `meta_run03_advanced`、s1 `safety_A4`)の構造的RCA、worst費用超過(safety_A4 s1 +¥3.34)のRCA、後段設計の改善案比較、Opus#14向けcontext packet作成。**実装・有料API実行は本委任では行わない**(設計変更はOpus批判レビュー→Fable評価の後に委任_11で実装する)。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。QCD優先: 1重大見逃し0 2Human Review 0 3不要Rewriteを増やさない 4+¥2 5非決定性・追加call最小 6Production複雑化回避。「Safetyを理由にHuman Reviewへ逃がさないこと。Human Reviewゼロ自体がKPI」。
- 到達上限Status: `IN_PROGRESS`のまま。`VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない。既存の個別APPROVED項目のStatusも変更しない。
- Fableの前提(変更しない): (ア)Human Review件数はrep27→28→29で3→3→3のまま、原因は毎回別の実装不整合(span不完全→L6順序→Recheck自己矛盾→actor_guard/title delete→related_fact_id空→今回はladder成功判定・span未特定・複数fact収束)。**個別の穴埋めの繰り返しになっていないか**を本RCAで正面から問う。「同じclaimが未解消で再BLOCKINGされたらHuman Review(`same_claim_fact_id_reblocked`)」「違反範囲が特定できなければHuman Review(`violation_span_unverified`)」「cycle上限でHuman Review(`cycle_limit_exhausted_after_recheck`)」は、いずれも「Human Reviewへ倒す経路」であり、KPI上は後段で決定論的に解消する設計が求められる。(イ)Opus批判レビューは必須(ユーザー指示: 後段Safety設計変更は実装前にOpus。かつ条件B: 同じKPI未達へ2回以上修正して再発)。(ウ)費用はPhase累計¥695.39/¥900、残¥204.61。再Trial(rep30、≈¥26)は1回分を見込む。設計は「限定確認(数instance、≈¥5)→rep30 1回」で済む形にする。
- 禁止事項: Production正式path変更禁止(読むのは可、編集不可)。Checker本体Prompt・Schema・判定規則・V7b・同義語表(`ACTOR_SYNONYM_CLASSES`)不変。本委任ではrunner・テストも編集しない(設計書・packet・RCA文書・¥0集計スクリプト/出力のみ)。KPI緩和案・Human Review温存案・「LLMなので保証困難」を結論にしない。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。`PM_GOVERNANCE.md`・`CURRENT_SPEC.md`・`DECISION_LOG.md`は編集しない。
- 費用上限: ¥0(有料API実行なし。既存出力のオフライン再集計・replayのみ)。T-3: Capは暴走防止Guardrail。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_10.md`。**委任文は全文そのまま保存(要旨化不可)。** 一時ファイルはリポジトリ外。スクリプトはWrite/Editで作る。

## ユーザー指示(原文、該当部分。全文は`DECISION_LOG.md`末尾の`OPEN-233-KPI-RECOVERY-REDESIGN-02`)

````
必須作業2 後段設計見直し
「AI1回で重大→問題なし」が可能な構造は禁止候補…
必須作業3 Opusを改善ループの一部に
原因分析→設計→Opus批判レビュー→Fable評価→自律改善→限定Trial→KPI確認→未達なら再設計→必要なら再Opus→本当に判断が必要な場合だけユーザーへ。
Opusから問題を指摘されたら、そのままユーザーへ投げず、採用/不採用/修正して採用をFable/Claudeで判断
Step 7
まだ未達なら、自律的に原因分析→改善ループをもう一度回す。
合理的な改善余地が残っている限り、ユーザーへKPI緩和を提案しない。
「設計した→レビューした→報告した」で終わらない。KPIを満たすまで、Guardrail内で自分たちで改善ループを回すこと。
````

## 作業1: 構造的RCA(¥0、`docs/pm/rca_open233_rep29_stage4_01.md`新規)

rep29の各STAGE4 instance JSON・Recheck出力・Ledgerを直接確認し、cycleごとの時系列(Stage 1 claim→Stage 2判定→ladder level→Rewrite前後文→Recheck結果→prior解消by_index→次cycleの判断)を逐語で書く。各件で「どの判定が、どの入力で、なぜHuman Reviewへ倒れたか」と「後段だけで決定論的に解けたか(解けたなら何を見れば解けたか)」を分ける。

1. **(1)(2) `meta_run03_advanced` MUSE-HC-006**(「users had no way to know whether they were talking to AI or a person」、通話するのは企業側=`changed_actor`)。確認事項: (a)1_word_connectiveが「成功」とされた判定基準(runner内の成功条件の行番号・引用)。成功判定が「Rewrite文が生成されguardを通った」だけで「issueの主体語がRewrite後も残っていないか」を見ていないか。(b)次cycleで同claimが再BLOCKINGされたとき、ladderは前cycleのlevelを引き継いで昇段しているか、またはlevel 1から再開しているか(行番号)。(c)`same_claim_fact_id_reblocked`がSTAGE4理由になっている条件(行番号・引用)と、その代わりに「前cycle levelの上位へ昇段」とした場合の振る舞いをオフラインで追う(Rewrite案は既存ログの3_sentence/4_paragraph案があれば流用、無ければ「必要なLLM call数」を見積る)。(d)s2の`violation_span_unverified`: cycle 3でspanが英語本文で特定できなかった直接原因(Checkerの`claim_in_article`が前cycleの文を指していたのか、Rewrite後文と乖離したのか、L6/carry-forwardがなぜ効かなかったか)。`related_fact_id`からfactの文を特定する決定論的fallbackで解けたか。
2. **(3) `safety_A4` s1**(7 BLOCKING、HC-006/010/012に跨り、3 cycleで収束せず、費用¥4.34)。確認事項: (a)cycleごとの新規MAJORは「Rewriteが新たに生んだ」のか「同一本文に対するCheckerの判定ゆれ」か「前cycleで未検出だったもの」かを、claim文と本文の差分で分類する。(b)同一cycleに複数factのBLOCKINGがあるとき、Rewriteは全claimを1回でまとめて行っているか、claimごとか(行番号)。(c)`HARD_MAX_CYCLES=3`到達後にHuman Reviewへ倒す条件(行番号)と、到達時点で残っていた未解消claimの内容・materiality(S1判定含む)。(d)費用内訳(cycle別、Stage 1/2/3/Recheck/S1別)。

## 作業2: 改善案比較(¥0、設計書`docs/pm/design_open233_kpi_recovery_02.md` §17新設)

候補を少なくとも次の観点で比較(各案: 閉じる穴/閉じない穴/不要Rewrite・非決定性・追加call・Production複雑度への影響/既存Evidenceで裏取り可能か/rep29の3件が解けるか[オフライン追跡の結果]):

- **A: ladder成功判定の厳格化**: level 1(語句)の「成功」に「issue中の主体語(`changed_actor`)・数値・否定・時期などの焦点要素がRewrite後spanから消えているか/入れ替わっているか」の決定論チェックを加え、残っていれば成功扱いにせず同cycle内で上位levelへ昇段(新retry loopではなく既存ladder内の判定)。
- **B: ladder levelのcycle間引継ぎ(昇段)**: 同claim(同fact_id・同焦点)が次cycleで再BLOCKINGされたら、前cycleのlevelの上位から開始。`same_claim_fact_id_reblocked`はSTAGE4ではなく昇段のtriggerにする。ladder枯渇(4_paragraphでも未解消)時の決定論的最終手段(例: 該当文を関連factの日本語本文に基づく定型英訳へ置換、または該当文のdelete[構造要素以外]は既存ルール上許されるか)を比較。
- **C: `changed_actor`flag時の最小level**: 主体入れ替えは語句置換で直せないことが多いなら最初から3_sentenceで開始(不要Rewrite・費用への影響を既存ログで集計)。
- **D: span未特定時の決定論fallback**: `violation_span_unverified`をSTAGE4にせず、`related_fact_id`→Ledger fact→本文中の該当文(前cycleのRewrite位置・carry-forward・L6・factキーワード)で特定する順序を定義。特定不能の場合の扱い(前cycleのspanの位置を保持する等)。
- **E: 複数fact同時BLOCKINGの収束**: cycle内で全BLOCKING claimを1回のRewriteにまとめる/段落単位へ早期昇段/Recheckで新規に出たMAJORをStage 2(S1含む)へ通す現行フローの確認。cycle上限到達時に残るのが「新規に出たQUALITY級」なら、Recheck判定の扱いで解けるか(KPI緩和にならない範囲で、正式materiality基準に沿うか)。
- **F: cycle上限・費用**: `MAX_CYCLES`/`HARD_MAX_CYCLES`を変えずにworst費用を+¥3以内に収める案(S1のbatch化・Recheck対象の限定等)と、変える案の費用影響。

各案の組合せ推奨(Fable評価用)を1つ出し、「Human Reviewへ倒す経路(`same_claim_fact_id_reblocked`/`violation_span_unverified`/`cycle_limit_exhausted_after_recheck`/`ladder_exhausted`系)のうち、設計後も残る経路」と「それが残る理由(本当に後段で解けないのか)」を明記する。

## 作業3: Opus#14向けcontext packet(`docs/pm/opus_packet_open233_kpi_recovery_02_04.md`新規)

雛形(a)〜(g): (a)管理ID・性質・到達上限・禁止事項、(b)ユーザー指示原文(上記)、(c)現行フロー要約(Stage 1→handoff→Stage 2→ladder→Recheck→STAGE4条件)と該当コードの行番号・引用(ladder成功判定・level引継ぎ・STAGE4条件・HARD_MAX_CYCLES・複数claim Rewrite)、(d)rep29の3件のRCA(作業1の要約+逐語Evidenceへのパス)、rep27/28/29のHuman Review推移と原因一覧、(e)改善案A〜F比較と推奨組合せ(作業2)、(f)Opusへの観点: ①なぜ「Rewrite成功」と「issue解消」が乖離できたか、新設計で閉じるか ②Human Reviewへ倒す経路を決定論的解消に置き換える案が「重大見逃し」を生まないか(Safety hole) ③不要Rewrite・非決定性・追加call・worst費用への影響 ④より単純・決定論的な代替 ⑤個別穴埋めの繰り返しになっていないか(構造的な見直しが必要か) ⑥限定確認→rep30 1回で判定できる設計か、(g)`docs/pm/OPUS_INDEPENDENT_REVIEW_BLOCK.md`逐語貼付(条件B・ユーザー指示による必須レビュー)。packetは読み取り専用のOpusが追加探索できるようパス・行番号を具体的に書く。

## 作業4: SSOT

`OPEN_ITEMS.md` KPI-RECOVERY-02行Statusに「委任_10: rep29 STAGE4 3件の構造的RCA・改善案A〜F比較・Opus#14 packet作成(¥0)。次: Opus#14→Fable評価→委任_11実装」を追記。`docs/pm/REPORT_LEDGER.md`1行、REPORT §60。`docs/pm/ACTIVE_TASK.md`更新(addしない)。

## 事前指定Read/Grep

- rep29: `er052_output/open233_self_recovery_flow_runner_01_rep29/` の`summary_kpi_01.json`、STAGE4 3件のinstance JSON(他instanceは読まない)。
- runner: Grep `same_claim_fact_id_reblocked|violation_span_unverified|cycle_limit_exhausted|ladder_exhausted|HARD_MAX_CYCLES|MAX_CYCLES|1_word_connective|3_sentence|4_paragraph|ladder_level|rewrite_success|stage4_reason|normalize_recheck_outcome|aggregate_prior_issues_resolved|carry_forward_resolution|vs_sentence_restore_resolve` → 該当範囲(全文Read禁止)。
- 設計書§12〜§16、`docs/pm/rca_open233_b3_stage2_misdowngrade_01.md`(欠陥一覧の書式を踏襲)、`docs/pm/opus_l2_review_open233_kpi_recovery_02_13.md`(Opus#13の結論部のみ)、`docs/pm/opus_packet_open233_kpi_recovery_02_03.md`(雛形)、`docs/pm/OPUS_INDEPENDENT_REVIEW_BLOCK.md`。
- SSOT: Grep `KPI-RECOVERY-REDESIGN-02`。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。
T-0: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_10.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_10.md_check.json
¥0集計スクリプト(必要なら): `er052_output/open233_kpi_recovery_02_offline_01/agg_rep29_stage4_rca_01.py`(Write)→実行、出力は同ディレクトリ。
順序: T-0 → 作業1 → 2 → 3 → 4 → commit/push → 報告。

## Git

明示add: RCA文書、設計書§17、packet、¥0集計スクリプト・出力、`OPEN_ITEMS.md`、`REPORT_LEDGER.md`、REPORT、委任ログ+check.json。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: rep29 Human Review 3件(ladder成功判定と解消の乖離・span未特定・複数fact収束)の構造的RCA、改善案A〜F比較、Opus#14向けpacket(委任_10、¥0)`

## 報告(RESULT_PACKET項目)

(1)結論10行以内(3件の根本原因を1行ずつ、推奨組合せ、「個別穴埋めか構造問題か」の判断)、(2)RCA要点(各件: 倒れた判定・行番号・後段で解けたか)、(3)改善案比較表と推奨、残るHuman Review経路と理由、(4)safety_A4費用内訳とworst対策、(5)packetパス(Fableが追加編集なしでOpusへ渡せる状態か)、(6)SSOT・T-0・commit・push・raw URL、一覧外Read、確認/推測の区別、(7)Fableへの論点。
