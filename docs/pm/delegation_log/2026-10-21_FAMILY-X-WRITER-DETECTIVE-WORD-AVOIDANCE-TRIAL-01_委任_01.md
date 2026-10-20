# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01 委任_01(Writer追加指示A/B/Cの比較Trial: 中東記事E2E-02の既存Ledger/B3入力を再利用し、Writer以降のtext工程のみTrial専用経路で再生成、Baselineと4観点比較、比較ページ作成、Closeout案)。並行agent: (1)`FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 委任_01`(er026/er062/er063・OPEN_ITEMS末尾新規行・REPORT_LEDGER・ACTIVE_TASK)/(2)`FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_05`(OPEN-416行・REGISTER #112/#128・DECISION_LOG・REPORT_LEDGER・E2E_PLAN_02.md)。本委任はこれらのファイル・行を編集しない(SSOTは最後にOPEN_ITEMS新規行1件+REPORT_LEDGER 1行のみ、共有プロトコル適用)。`run_mey_02`配下は**読取のみ**。

## 性質/到達上限Status/禁止事項
- 性質: Trial(新Prompt候補=`TRIAL`)。到達上限=`VALIDATED`(Fableが最終ラベル。Sonnetは機械判定・判断候補まで)。Production採用はユーザーの別途明示承認。**正式Production Writer(`er003_v1_en_direct_vfl_01_generate.py`/`er019_family_x_entertainment_production_runner_01.py`等)のPrompt・コード・実行経路は一切変更しない**(Trial専用script内でのruntime monkeypatch/ラッパのみ。Production fileへのdiff=0をgit statusで証明)。
- 費用/日次: 本日2026-10-21(JST)既使用JPY0(出典: RESULT_PACKET_MEY5。S0で`daily_dev_cost_01.py --date 2026-10-21`再確認。並行の開いた窓Phase1はJPY0)。本委任見積: Writer R0→R1→R2(Sol)約JPY12.7+Advanced英語化/IOL/RF b1b約1.1+Standard調整/RF a2約1.6=約JPY15.5/Pattern(出典: run_mey_02実測、E2E_PLAN_02.md §5)×3=約JPY47+LLM判定(gpt-6-luna等、約JPY3)=**約JPY50**。承認区分C(ユーザー指示で承認済みScope、案件見積300円以下、日次内)。T-3: 上限¥100(Guardrail=見積の約2倍、暴走防止)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。ユーザー§7「個別承認予算の超過見込み」=¥100超過見込み時はSTOP。
- 禁止: Research/Fact抽出/B3/TTS/scaffold/Assemblyの再実行・web_search呼出・Pattern D/E等の追加・Pattern別に異なるモデル/工程を使うこと・禁止語リストの新設(「investigator」等の類似語を機械的に禁止しない。出現は観測として記録のみ)・Baseline成果物の変更・`git add -A`/`-u`/stash/amend/rebase/force push/branch操作。
- Opus独立技術レビューGate(11-3): 非該当(Production構造変更なし、Trial専用。Production採用提案時に条件C該当の可能性=Fable判断)。
- 時間見込み: 全体90〜120分。並列化: 3 Patternの生成は入力・出力dirが独立なので**並列実行可**(同一Production moduleをimportするがmonkeypatchはprocess内のみ=process分離で実行)。評価・比較ページは生成後に直列。設計書+harness+Baseline計測は生成前に並行。
- 開発・評価用途の最新モデル原則(PM_GOVERNANCE 25節): 生成はProductionと同一条件(Sol R0→R2等、変更不可)。評価用LLM判定は最新上位系(gpt-6-luna等、Productionと同じ世代)を使い、報告に使用モデル/最新か/理由を明記。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01_委任_01.md`へ逐語保存(打ち直し禁止。`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <上記path>`、N=本委任文[「DETECTIVE-WORD-AVOIDANCE」を含む最新。同時刻にE2E-02 委任_05、直前192は開いた窓 委任_01])し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <上記path> --json-out <上記path>_check.json`を実行、結果をRESULT_PACKETへ1行。
T-2: TTSなし(TTS/Assembly再実行禁止)。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01_USER.md` へ逐語保存(先頭に `# ユーザー指示原文(2026-10-21)` と `管理ID: FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01(§2〜§9) / FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_05(§1)` の2行、以降一字一句変えない。文字数・sha256を報告)。
--- 原文ここから ---
# 中東記事 最終Closeout ＋ Writer「Detective」表現改善Trial

## 1. ユーザー正式判断：中東記事を受入

中東記事 E2E-02について、**Standard／Advanced両方のユーザー試聴PASSを正式確定する。**

対象：
https://shimomura055.github.io/eigo-radio/user_test/middle_east_yemen_saudi_e2e_02/index.html

- 音声・記事品質ともに今回の完成版を承認。
- `USER_LISTENING_PENDING` を解消する。
- 既存成果物の再生成・再組立は不要。
- OPEN-416、DECISION_LOG、REGISTER、REPORT_LEDGER等を必要十分に更新し、正式Closeoutする。
- FableがCloseoutを独立確認する。

**今回のDetective表現は中東記事の受入を妨げない。** 新たな改善Trialとして切り分ける。

## 2. 新Trialの目的

**目的：ニュース記事のエンターテインメント性を損なわず、Writerが「Detective」という単語を使用しないようにする。**

現状の課題：

Writerにエンターテインメント性を高めるよう指示すると、ニュースを探偵・捜査になぞらえる表現が出現しやすい。

ただし、ユーザーは謎解き的な展開や構成自体を否定していない。

今回、禁止したい対象は**Detectiveという単語**であり、ニュースの構成上の自由度を不必要に狭めないことが重要。

### TrialのStatus

- 新Prompt候補：`TRIAL`
- Trial成功時の到達上限：`VALIDATED`
- Production採用：ユーザーの別途明示承認が必要
- 正式Production Writerへの配線：今回の対象外

## 3. 比較条件

中東記事E2E-02を題材とする。

既存の承認済みResearch／Fact Ledger／B3入力とWriterの現行Prompt・モデル・生成条件を再利用し、**追加指示だけを変える**。

Research、Fact抽出、B3選定、TTS、Assemblyは再実行しない。

既存完成原稿はBaselineとして保存し、変更しない。

### Pattern A：単語のみ禁止

Writerへの追加指示：

> Do not use the word "detective" anywhere in the article.

検証目的：
単純な禁止だけで指定単語を排除できるか。

### Pattern B：単語禁止＋構成の自由を明示

Writerへの追加指示：

> Do not use the word "detective" anywhere in the article. However, this restriction does not prohibit a mystery-like narrative structure or a detective-like progression of the news story, as long as it remains faithful to the verified facts.

検証目的：
Detectiveという単語だけを禁止し、ニュース展開・構成の自由度と面白さを維持できるか。

### Pattern C：単語禁止＋面白さの作り方を誘導

Writerへの追加指示：

> Do not use the word "detective" anywhere in the article. Create an engaging news story through the actual events, surprising developments, decisions, consequences, and connections between verified facts. Avoid relying on a detective metaphor to make the story entertaining. A mystery-like narrative structure is acceptable when it naturally follows the facts.

検証目的：
Detectiveという比喩に頼らず、事実そのものから面白さを引き出せるか。

**注意：Pattern Cでも、探偵的な構成そのものは禁止しない。**

## 4. Trial設計

### 基本方針

1. BaselineとA／B／Cを同一条件で比較する。
2. 各Patternは原則として独立した生成とする。
3. 現行WriterのEntertainment Revisionなど、既存の生成・改稿工程を維持する。
4. 各工程で追加指示が有効に作用しているか確認する。
5. 特定Patternだけ別のモデルや改稿工程を使わない。
6. Trial専用の成果物として保存し、Productionへ影響させない。

比較可能性を確保しながら、必要な生成回数・費用を最小化する。

### 比較対象

- Baseline：既存完成記事
- Pattern A
- Pattern B
- Pattern C

各Patternについて、まず1セットの原稿を生成する。

結果が明確であれば追加生成せず終了する。効果が不明瞭で、承認済みTrial予算内で追加比較する価値が高い場合に限り、必要最小限の再現確認を行う。

追加のPrompt候補D／E等を独断で増やさない。

## 5. 品質評価

以下の4項目を比較する。

### ① Detectiveの排除

- `detective` の大文字・小文字違いを含め、本文中の出現が0件であること。
- 完成記事全体を確認する。
- Preview／Comment等が今回のWriter評価範囲に含まれる場合は、本文と区別して結果を報告する。
- 単純な表記置換で済ませず、Writerが自然な文章を生成できるかを見る。

### ② エンターテインメント性

- 冒頭の引き
- 展開の自然さ
- 意外性・興味を引く構成
- 読み進めたくなる面白さ
- 不自然な比喩や演出の有無

**単語を消せたことだけでTrial成功としない。**

### ③ 事実・ニュース品質

- Ledger外の事実追加がない。
- 攻撃主体（フーシ派）の記述が維持されている。
- 「誰の発表・主張か」という帰属が正確である。
- 原因・動機を根拠なしに創作しない。
- 時系列・因果関係・人物関係に新たな誤りがない。

### ④ QCD

- Pattern別のLLM呼出回数
- 使用モデル
- 実費
- 所要時間
- retry／再生成の有無
- Production適用時の量産単価への影響

既存工程に追加API呼出を必要としないPrompt変更であれば、その点を明確にする。

## 6. Fable独立評価

Fableは単にDetective出現件数を見るのではなく、次の観点で評価する。

- A／B／Cのどれが今回のユーザー目的に最も忠実か。
- Detective禁止によって、面白さ・自然さが低下していないか。
- `investigator` など類似表現への不自然な言い換えが起きていないか。
- 類似表現の使用を理由に、今回の未承認の禁止語リストを新設していないか。
- 中東記事固有の効果なのか、他のニュースにも適用できそうか。
- 追加Promptの長さ・複雑さに見合う効果があるか。

必要十分な品質に達した時点で比較を終了する。無益な反復をしない。

## 7. 予算・STOP条件

- 日次開発予算1,000円（JST）を遵守する。
- Trialの個別費用枠は既存承認を確認し、その範囲内で実行する。未承認の費用枠を新設しない。
- 既存入力・出力を再利用し、Researchや音声生成に費用をかけない。
- 品質・費用・技術上の理由がなければ独立作業を並列化する。
- 既存Production経路は変更しない。

以下の場合はSTOPする。

- ユーザー承認のない仕様変更が必要
- 個別承認予算の超過見込み
- 重大な事実改変・品質問題を承認範囲内で解決できない
- 明示的なSTOP条件に抵触

既存仕様・予算内の技術的不具合は自律的に解決する。

## 8. 最終報告・Trial Closeout

以下を報告する。

1. **A／B／Cの比較結果とFable推奨Pattern**
2. 各Patternの原稿を確認できる比較ページまたはリンク
3. Detective出現件数
4. エンターテインメント性・自然さの比較
5. 事実整合性・攻撃主体・帰属の検査結果
6. 使用モデル・実費・所要時間・量産原価影響
7. Trial Status（REJECTED／VALIDATED／USER_DECISION_REQUIRED）
8. Production採用に必要なユーザー判断

A／B／Cの原稿は、ユーザーが内容を比較して評価できる形で提示する。

**Fableの推奨があっても、Production採用は自動決定しない。**

Trial完了後、ユーザーが正式採用を判断するまでProduction WriterのPrompt・コード・実行経路を変更しない。

---

## 9. PM上の最重要事項

今回の問題は「探偵的な構成をなくしたい」ではない。

**「Detectiveという単語を使わずに、これまでのニュース記事の面白さを維持したい」ことが目的である。**

- 過剰に禁止範囲を広げない。
- 元のニュースの事実・品質を守る。
- 中東記事の完成承認は維持する。
- 今回のTrial成功を正式採用と混同しない。

既存仕様とQCDを守り、最小限の比較で結論を得ること。
--- 原文ここまで ---

## KPI provenance欄
Baseline=reuse(run_mey_02完成原稿、production_formal_path)。A/B/C=fresh(Trial専用経路、Productionと同一モデル・工程+追加指示)。Detective件数=決定論Grep(fresh)。Entertainment/事実判定=LLM判定(fresh)+Sonnet所見、最終評価はFable。E2E自己確認: No(text工程のみ、TTS/Assemblyなし=ユーザー指示どおり)。

## 設計(事前登録。生成前に`docs/research/FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01/TRIAL_DESIGN_01.md`へ確定・commitしてから有料生成)
1. **Baseline計測(JPY0)**: run_mey_02の`b1b/article.md`・`a2/article.md`・`writer_run_summary.json`(R0/R1/R2各稿)・audio側`a2_support_texts.json`/b1b support/KPに対し、`detective`(大小文字不問、`detectives`等の派生も別集計)の出現件数を本文/Preview・Comment/KPで区別して表にする。出現文を引用。Baselineの「探偵比喩」がどの工程(R0/R1 Entertainment Revision/R2/Std調整)で入ったかをR0〜R2稿のGrepで特定(ユーザー§4-4「各工程で追加指示が有効に作用しているか」の対照に使う)。
2. **注入点の確定**: `er019_family_x_entertainment_production_runner_01.py --stage writer/advanced/standard`が呼ぶProduction関数とPrompt組立箇所(Grep `factlock_r0__r1_r2_independent_sol61|def run_writer|build_.*prompt|ENTERTAINMENT|R1|R2|std_adjust|advanced` 等で特定。前回XRFRで把握した`er003_v1_en_direct_vfl_01_generate.py`も確認)。追加指示は**本文prose を生成/改稿する全LLM工程(R0・R1[Entertainment Revision]・R2・Advanced英語化・Standard調整)のuser/system指示末尾に同一文を追記**する(A/B/Cで同じ注入点・同じ位置。Risk Flagger・IOL・記号Validator等の検査系には注入しない)。注入はTrial script `er086_writer_detective_avoidance_trial_01_lib.py`内のmonkeypatch/ラッパで行い、Production fileは不変。注入後の実Prompt全文(各工程)を`prompt_dump/<pattern>_<stage>.txt`に保存(有効化の証拠)。
3. **入力の再利用**: 新しいTrial out-dir `er086_output/writer_detective_avoidance_trial_01/<pattern>/`へ、run_mey_02の`research_ledger/`と`storyline_b3/`をコピー(sha一致を記録)。runnerのwriter/advanced/standard stageをこのout-dirで実行(`--budget-jpy 40`、`--run-label DWA-T1-<pattern>`、`--theme`は同一文字列)。runnerがprovenance(U-1 PROVENANCE_MISMATCH等)でコピー入力を拒否する場合は、Trial libからProduction関数を直接呼ぶ形に切替え(同一モデル・同一Prompt+追加指示、同一retry設定)、その旨を設計書に記す。**Production runnerのcode変更禁止**。
4. **Pattern文**: ユーザー原文§3のA/B/C英文をbyte単位でそのまま使用(改変禁止。`design_matrix_01.json`に格納しsha記録)。
5. **評価**: ①決定論Grep(本文/Preview・Comment/KPは今回Writer範囲外=本文[R2最終・Advanced・Standard]のみ対象と明記。support/KPは再生成しないため「対象外」と報告)。②Entertainment: LLM判定(gpt-6-luna、temperature固定、Baseline/A/B/Cを**ラベルを伏せて**ランダム順で提示、5観点[冒頭の引き/展開の自然さ/意外性・構成/読み進めたくなるか/不自然な比喩・演出]を1〜5点+根拠引用、2回実行して安定性を見る。判定Promptは設計書に全文)。③事実: Ledger外事実追加(固有名詞・数字・場面をLedgerと突合、XRG/E2E-02 §14同手順)、攻撃主体(Houthi/Ansar Allah)記述の維持と帰属(連合軍報道官の発表)の正確さ、原因・動機の創作、時系列/因果/人物関係の新誤り、をPatternごとに表。類似語(`investigator|investigation|clue|mystery|case file|sleuth`等)の出現は**観測として件数と文脈を記録するのみ**(禁止リスト化しない)。④QCD: Pattern別LLM呼出回数・モデル・実費(raw_usage_log×pricing_snapshot)・所要時間・retry有無・Production適用時の量産単価影響(追加API呼出0=Prompt追記のみならその旨)。
6. **機械判定規則(事前固定)**: 候補=本文detective 0件 かつ ③で新たな事実誤り0 かつ ②平均がBaseline−0.5点以内。複数候補があれば、追加指示が短いものを「同等なら優先」。いずれも満たさなければ`REJECTED_CANDIDATE_MACHINE`。最終ラベル(VALIDATED/REJECTED/USER_DECISION_REQUIRED)はFable。
7. **再現確認**: 1セット生成で結果が明確(候補が1つに定まる/全滅)なら追加生成しない。不明瞭(候補が複数で②差が0.3点未満等)の場合のみ、候補Patternに限り1回ずつ再生成(Guardrail内、Fable事前承認不要だが理由を記録)。

## 比較ページ
`user_test/writer_detective_trial_01/index.html`(GitHub Pages): Baseline/A/B/Cの**Advanced本文・Standard本文**を並べて表示(Pattern文・detective件数・類似語件数・LLM判定点・事実検査要約・費用を各列に)。ラベルは表示してよい(ユーザー比較用)。commit/push後HTTP200確認。

## 事前指定Read/Grep一覧
- `docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02/E2E_PLAN_02.md` §3・§5(Writer記録・費用)。
- `er019_output/middle_east_yemen_saudi/run_mey_02/`: `writer_run_summary.json`、`b1b/article.md`、`a2/article.md`、`storyline_b3/fact_selection_evidence.json`、`research_ledger/verified_fact_ledger.*`、`cost.json`(読取のみ)。
- `er019_family_x_entertainment_production_runner_01.py`: L240-260(provenance)、L400-470(stage dispatch)、Grep `def run_writer|def _stage_writer|import er0` → 該当。
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `def build_.*prompt|ENTERTAIN|def run_writer|R1|R2` → 該当±20。Writerが別moduleならそちら(runnerのimportから辿る)。
- `er085_research_fact_retention_trial_01_lib.py`: L1-80(前回Trialのmonkeypatch/注入の書式を流用)。
- `docs/research/FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01/TRIAL_DESIGN_01.md`: §1〜§3(設計書書式)。
- `docs/pm/PM_GOVERNANCE.md`: Grep `^## 25|^### 25` → 25節(最新モデル原則)のみ。
- `OPEN_ITEMS.md`: 末尾5行(採番確認。並行agentがOPEN-428を使う可能性→編集直前に再Grepし次番号)。`docs/pm/REPORT_LEDGER.md`: 末尾5行。

## 実行コマンド全文
- T-0/原文保存: 上記。S0: `.venv\Scripts\python.exe docs\pm\tools\daily_dev_cost_01.py --date 2026-10-21`。
- 生成(例、Pattern A。B/Cは`<pattern>`置換、3 processを並列起動可): `$env:TTS_EXECUTION_MODE="STANDARD"; $env:PYTHONIOENCODING="utf-8"; .venv\Scripts\python.exe er086_writer_detective_avoidance_trial_01_run.py --pattern A --source-run er019_output/middle_east_yemen_saudi/run_mey_02 --out-dir er086_output/writer_detective_avoidance_trial_01/A --budget-jpy 40`(run scriptはProduction runner/関数をimportして注入後に呼ぶ。実在引数は実装に合わせ、設計書に全文を記す)。
- 評価: `.venv\Scripts\python.exe er086_writer_detective_avoidance_trial_01_eval.py --root er086_output/writer_detective_avoidance_trial_01 --baseline er019_output/middle_east_yemen_saudi/run_mey_02 --out docs/research/FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01/COMPARISON_RESULT_01.md`。
- test: `er086_writer_detective_avoidance_trial_01_test_01.py`(注入が全対象工程のPromptに含まれる/Production module定数が実行後も不変/Pattern文byte一致/Grep集計)、`.venv\Scripts\python.exe -m unittest er086_writer_detective_avoidance_trial_01_test_01 -v`。Production不変証明: `git status --porcelain er003_v1_en_direct_vfl_01_generate.py er019_family_x_entertainment_production_runner_01.py`(空であること)+関連Production fileのsha256を実行前後で比較し記録。
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`(hits=0必須)。

## SSOT(編集権: OPEN_ITEMS.md新規行1件・REPORT_LEDGER.md 1行のみ。共有プロトコル: 編集直前に`git status --porcelain`と末尾再Grep→自分の行だけ追記→即add/commit。`index.lock`は30秒待ち再試行。`git diff --cached --stat`で自分のファイルのみ確認、他agent分は`git restore --staged`)
- 新規行文案: `OPEN-4NN | **FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01 [DWA_TRIAL_CLOSEOUT_PENDING_FABLE(機械判定=...)・Trial承認(到達上限VALIDATED)・Production採用未承認・Production変更0]**(2026-10-21、委任_01、実費JPY..): ユーザー2026-10-21指示(原文=...USER.md、sha)。目的=Writerが「detective」を使わずニュースの面白さを維持(探偵的構成は禁止しない、禁止語リスト新設なし)。Baseline=run_mey_02、A/B/C=追加指示のみ差替え(注入点=...)。結果=...。比較ページ=https://shimomura055.github.io/eigo-radio/user_test/writer_detective_trial_01/index.html。設計=TRIAL_DESIGN_01.md、結果=COMPARISON_RESULT_01.md、Closeout=TRIAL_CLOSEOUT_01.md。 |`(POST_USER_VALIDATION)。DECISION_LOG/CURRENT_SPECは編集しない(Fable照合後の委任_02)。

## Git
commit最低3回: (1)T-0+原文+設計書+harness+test(生成前)、(2)生成結果(er086_output配下のmd/json/txt、prompt_dump含む。大容量なし)+COMPARISON_RESULT+比較ページ、(3)Closeout+OPEN_ITEMS/REPORT_LEDGER。明示add。secret scan hits=0。`git push origin HEAD:main`(force禁止。並行agentでorigin/mainが進んでいてもfast-forwardできればOK。rejectedなら`git pull --ff-only origin main`は行わず報告)。raw URL列挙。

## 報告(docs/pm/RESULT_PACKET_DWA1.md 上書き。ユーザー§8の1〜8の順。Sonnetは「判断候補」表記、USER_DECISION_REQUIREDラベルは付けない)
1. A/B/C比較表と機械判定・Sonnet所見(推奨はFableが決める。所見として順位と理由)。2. 比較ページURL(HTTP200)。3. detective件数(本文/工程別R0・R1・R2・Adv・Std、Baseline含む)+類似語観測。4. Entertainment LLM判定(2回、ラベル伏せ、点数+根拠引用)。5. 事実整合・攻撃主体・帰属の検査表。6. モデル・実費(Pattern別、出典)・所要時間・retry・量産単価影響(追加API呼出の有無)。7. 機械判定Status。8. Production採用時に必要な事項(注入点がProduction Promptのどこに相当するか、変更規模、Opus条件C該当可能性)。加えてT-0結果・Production不変証明(git status/sha)・並行競合の有無・当日累計。