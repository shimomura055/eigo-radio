# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_01(ユーザー2026-10-20指示原文保存[T-0]+中東記事`run_mey_01`で背景情報3点[攻撃主体/動機/イエメン情勢との接続]がResearch/Fact Ledgerから欠落した根本原因の工程別切り分け+原因別の対応案[範囲内不具合なら修正設計まで])。2026-10-20。
並行タスク衝突確認: 並行で(a)FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_02b(er084*、docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/、user_test/plw_trial_01/)、(b)本管理IDの委任_02(C1陽性対照Trial準備: er083*・`docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/C1_*`・OPEN-423/REGISTER #123の是正)が走る。本委任は上記ファイルを編集しない。本委任の書込先=`docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/RESEARCH_GAP_ROOT_CAUSE_01.md`(+補助json/py)、`docs/pm/RESULT_PACKET_XRG1.md`、delegation_log。**`er019_output/middle_east_yemen_saudi/run_mey_01/`は読取のみ**。SSOT編集権: 無し(文案はRESULT_PACKETへ。SSOT初回記録は委任_02が担当)。`docs/pm/ACTIVE_TASK.md`は先頭へ自委任ヘッダ4行を追記のみ。commit前に`git status --porcelain`で`.git/index.lock`不在と他agentのstaged変更が無いことを確認し、自ファイルのみ明示add→即commit。

## 性質/到達上限Status/禁止事項
- 性質: 調査(原因究明)+原因別対応案。コード変更は本委任では行わない(範囲内不具合が特定された場合は修正設計[変更箇所:行・Regression案・正式経路検証案・費用]を文書化し、Fable照合後の委任_03で実装)。
- 到達上限Status: `RESEARCH_GAP_ROOT_CAUSE_IDENTIFIED_PENDING_FABLE`。
- 禁止: (1)Researchの有料再実行(LLM/Web Search API)。原因究明は既存記録の追跡で行う。(2)Production Prompt/schema/producer/Writer/B3の変更。(3)架空の背景Factの作成・推測による補完(裏付けのない主体・動機を書かない)。(4)`git add -A/-u/-f`・amend・rebase・force push・stash。(5)全記事一律バックテスト。
- 許可: 既存Research記録に残る出典URLの**原文確認**(無料のHTTP取得、`curl.exe`等。取得できない場合は「未確認」)。取得本文はscratchpad(`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\xrg1\`)へ置き、repoへcommitしない(抜粋引用のみ文書へ)。
- 修正範囲の線引き(11-8): 範囲外=Research仕様・Fact Ledger schema・B3受理面の新設/拡大(新仕様→判断候補)。範囲内=承認済みResearch仕様文・Prompt・QA・Ledger生成仕様と実装の乖離(例: 仕様上取得すべき情報が抽出/構造化段階で落ちる、Fact採否記録と仕様の不整合)の是正。
- Opus独立技術レビューGate(11-3): 本委任=非該当(調査)。修正が新構造を伴えば委任_03前に条件A。
- 費用/日次: 当日既使用JPY49.70(出典RESULT_PACKET_PLW2a.md、並行PLW 委任_02bが最大+200)/本委任見積JPY0(API 0。HTTP取得は無料)/承認区分C。
- T-3: 本委任は費用上限を伴わない(JPY0)。
- 時間見込み: 全体2.5〜4h(T-0 10分/run_mey_01の工程構造把握30分/検索記録・出典・抽出・Fact採否の追跡90分/出典原文確認30分/仕様・過去対策照合30分/文書・報告30分)。並列化: 出典原文確認(HTTP)は追跡と並列可。委任_02と並列。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**保存は打ち直さず`extract_delegation_from_jsonl_01.py`でsession JSONLから抽出**(`--role assistant --tool-use-name Agent --tool-input-field prompt --index <N>`、管理ID行に`FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_01`を含む最初のもの)→`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_委任_01.md`。ユーザー原文(下記)は同じ抽出結果から`---(原文ここから)---`〜`---(原文ここまで)---`の間を切り出して`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_USER.md`へ保存(先頭メタ1行`<!-- 受領日: 2026-10-20 / 受領者: Fable(sandwich-pm) / 保存: 委任_01 -->`のみ付加、本文改変なし)。文字数・sha256を記録。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): 本委任はTTSを伴わない。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 本委任はCapを伴わない。

## ユーザー指示(原文)
---(原文ここから)---
# Claude Codeへの指示｜Family X Research根本原因調査・B3 C1検証是正

## 1. 目的とユーザー決定

今回の目的は、Family Xの中東記事で、読者の理解に必要な背景情報がResearch／Fact Ledgerから欠落した原因を解明し、今後の量産でも同様の問題が起きないようにすること。

併せて、B3背景Fact補完TrialのC1について、評価上の不備を是正する。

**ユーザー決定：**

1. **C1の有効性が確認されたという評価を撤回する。**
2. C1は背景Factの追加実績が0件であり、核心機能は未検証。従来の `VALIDATED（範囲限定）` はC1全体の有効性を意味しない。記録上も、確認済みの限定的成果と未検証機能を明確に区別する。
3. Researchの根本原因調査を進める。既存仕様の不具合なら、承認範囲内で修正・検証まで自律的に完了する。
4. B3の正式Production仕様は変更しない。C1のProduction採用は未承認。
5. 中東記事の音声化は引き続き保留。

品質（Q）＞納期・速度（D）＞量産単価（C）≫開発費用、ならびにプロジェクトの8原則・PM Gateを遵守すること。

## 2. 最優先：Researchで背景情報が欠落した根本原因

今回の中東記事で不足した情報は、次の3点。

1. 誰がサウジ側施設を攻撃したのか。
2. なぜ攻撃したのか。
3. イエメン情勢と今回の攻撃がどうつながっているのか。

**「Ledgerに存在しなかった」は原因分析として不十分。**

既存Researchの検索記録、参照元、抽出・構造化結果、Fact採否記録、Ledger生成経路、CURRENT_SPEC、過去の同種対策まで遡り、次を切り分けること。

- 信頼できる情報源に、そもそも情報が存在したのか。
- Researchで調査していなかったのか、調査したが見落としたのか。
- 調査で取得したが、構造化・Fact化の途中で脱落したのか。
- 現行Research仕様・Prompt・QAに不足があったのか。
- 当該事案で主体や動機が確認できないこと自体が、正しい調査結果だったのか。

特に、**事件の攻撃主体・その主体の一般的な動機・地域紛争の背景を混同しない**こと。裏付けがない情報を推測で補わない。

不足が事実として解消可能だった場合は、なぜ既存工程で取り逃したかを特定する。

### 原因別の対応

- **既存仕様の不具合・適用漏れ：** 承認済み範囲で原因究明→修正→Regression→正式経路の検証まで自律的に完了。
- **信頼できる情報が存在しない：** 未確認事項として正しく記録し、架空の背景Factを作らない。
- **新仕様が必要：** 具体的な欠落原因、改善案、品質・Delivery・量産単価への影響を示し、USER_DECISION_REQUIREDとして報告。正式採用・Production配線は行わない。

全記事で機械的に「誰が・なぜ」を必須にするなど、ストーリー性を損なう過剰な仕様変更は提案しない。

## 3. C1 Trialの評価是正と追加検証

前回はC1・C2・C3を比較したものの、7回すべてで背景Fact追加が0件だった。

C1の選定理由は、不必要な追加をしないこと、背景不足を正しく記録すること、ストーリー性を損なわないことに限定される。

**必要な背景Factを見つけ、追加するという核心機能は一度も実証されていない。**

したがって、C1の有効性を実証済みと扱わない。過去のTrial結果やFable分類は履歴として残し、現時点の評価を正しく修正する。

### 検証内容

Research根本原因調査とは独立して実施可能な準備は並列化する。

まず、既存のFact Ledgerから、以下の条件を満たす記事を探す。

- 主要ストーリーに対して理解上必要な背景Factが実在する。
- その背景FactがLedger内に記録されている。
- 通常のB3では、そのFactが選ばれない可能性がある。
- 追加すべきFactを、事後評価で明確に判定できる。

適切な既存Ledgerがない場合は、**実在する検証済みFactを用いたテスト用Ledger**で陽性対照を構成する。単なる架空の主張を事実として扱わない。

C1について、以下を検証する。

1. 必要な背景Factを正しく追加するか。
2. 不必要なFactを追加しないか。
3. 中心Storyline・エンターテインメント性を維持するか。
4. 選定した背景Factが既存のWriter入力経路に正しく反映されるか。
5. 記事として実際に理解しやすくなるか。
6. 誤帰属・根拠のない因果関係・過剰な網羅化が生じないか。

既存のB3下限2 Factと、今回の補完候補を混同しない。

検証はDEV／Trial環境に限定し、既存ProductionのPrompt・schema・producer・Writer経路を無断で変更しない。

なお、**陽性対照を用いた限定的な追加Trialは今回の指示範囲内**とする。ただし、過去テーマへの大規模展開・Production採用・新規仕様の正式実装は別途ユーザー承認が必要。

### Trial Closeout

- 核心機能の成功と記事品質維持を確認できた場合：`VALIDATED`。Production採用は未承認。
- 失敗した場合：原因を分析し、承認範囲・予算内で合理的な修正と再検証を実施する。
- 改善見込みがない場合：`REJECTED` を提案。
- 新仕様や品質基準の変更が必要な場合：`USER_DECISION_REQUIRED`。

単に「追加しなかった」という結果を、背景補完能力の成功として扱わない。

## 4. Writerへの伝達について

今回の本質的な問題は、B3の背景不足メモがWriterに届かなかったことではない。

**Writerに不足を知らせても、裏付けとなるFactが存在しなければ記事は改善しない。**

したがって、不足メモの伝達機構を新設することを優先しない。

ただし、C1によって実際に背景Factを追加できた場合は、そのFactが後続の決定論的producerを通じてWriterに正しく渡り、本文で使われることまで検証する。

必要なschema・producer変更が判明した場合は、実装を独断で進めず、変更範囲・QCD・正式採用の必要性を報告すること。

## 5. QCD・実行管理

- 既存Research、Fact Ledger、Trial成果物を最大限再利用する。
- 不必要なResearch再実行や、全記事への一律バックテストを行わない。
- 調査とC1の検証準備は、依存関係のない範囲で並列化する。
- Trialは核心機能の検証に必要な最小構成とし、陽性・陰性条件から有効な結論を得る。
- 原因が分かった時点で、同じ方向の無益な試行を繰り返さない。
- 当日開発予算1,000円、個別承認枠、既存のSTOP条件を遵守する。
- 新たな仕様採用・Production変更を日次予算内であることだけを理由に無断承認しない。

## 6. Fable独立評価・最終報告

Fableは、特に以下を独立照合すること。

- Research欠落の原因が、検索・情報源・構造化・Ledger作成・仕様のどこにあったか。
- 既存仕様の不具合であれば、修正から正式経路の検証まで完了しているか。
- C1について、陽性対照が実際に存在し、必要な背景Factを正しく追加できたか。
- WriterにFactが渡り、記事品質にどう影響したか。
- Production仕様が未承認のまま変更されていないか。
- SSOT／Git／OPEN_ITEMS／判断Statusに矛盾がないか。

**最終報告は次の順序とする。**

1. Researchで3点の背景情報が欠落した根本原因（証拠付き）。
2. 原因別の是正内容と再発防止の効果。
3. C1の陽性対照Trial結果（採用FactのBefore／After）。
4. 記事品質・ストーリー性の比較。
5. QCD（実費、追加工程の時間、量産単価への影響）。
6. Production配線・SSOT・Gitの状態。
7. 残るユーザー判断事項と推奨案。

**今回の完了条件は、「Researchに原因があった」「C1は有望だった」という報告ではない。**

Researchの欠落原因を具体的に解明し、承認済み仕様内の問題は自律解決すること。そしてC1の背景補完能力について、実際に追加が必要な条件で検証し、根拠のあるStatus判定を行うことである。
---(原文ここまで)---

## 本委任の作業(§2のみ。§3/§4は委任_02)
成果物: `docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/RESEARCH_GAP_ROOT_CAUSE_01.md`。構成:
- §1 **工程マップ**: run_mey_01のResearch→抽出・構造化→Fact検証→Ledger生成→Fact Lock→B3→producer→Writerの各工程について、実行script(関数:行)・入力/出力ファイル(run_mey_01内の実パス)・使用モデル・Prompt(ファイル:行)を表にする。特に「検索クエリ」「取得した出典一覧(URL・媒体・取得日時)」「抽出候補Fact(採用/不採用とその理由コード)」「検証(verify)結果」「Ledger 11件の確定」の記録がどこにあるかを特定する(`entry_point.json`、`research/`、`fact_ledger*.json`、`audit/`配下をGrep `query|source|url|reject|verify|ledger`)。
- §2 **3点の欠落の追跡**(各点ごとに1表): (a)検索クエリに主体・動機・背景を問う語(例: who/claimed responsibility/Houthi/Ansar Allah/why/Yemen conflict/coalition)が含まれていたか(クエリ原文を引用)。(b)取得出典の本文に該当情報があったか=**出典URLの原文を無料HTTP取得して確認**(取得日時・該当箇所の短い引用。取得不可なら「未確認」。推測で補わない)。(c)抽出・構造化段階の候補Factに該当情報が現れたか(候補一覧を全数走査し、主体・動機・背景に関する候補の有無と採否理由コード)。(d)Fact検証段階で落ちたか(verify結果・閾値・理由)。(e)Ledger生成・Fact Lockで落ちたか。(f)B3/producer/Writerで落ちたか(Ledgerに無ければ「到達前に欠落」と明記)。→各点の**欠落工程**を1つに確定し、「情報源に存在せず(正しい結果)/未調査/調査したが見落とし/構造化で脱落/検証で棄却/仕様不足」の6区分で判定。
- §3 **承認済みResearch仕様との照合(E-1)**: CURRENT_SPEC/DECISION_LOGのResearch・Fact Ledger・Fact検証・B3に関する仕様文(Grep `Research|Fact Ledger|Fact検証|verify|B3|出典|信頼できる|Reuters|AP`、行番号付き逐語)と、§2の各工程の実挙動を突き合わせ、11-8不具合判定(仕様文と実装の乖離=範囲内不具合/仕様どおり/仕様の空白)を各工程に付ける。過去の同種対策(OPEN_ITEMS/DECISION_LOGをGrep `背景|主体|動機|context|background|欠落`)を列挙し、再発か新規かを判定。
- §4 **「主体・動機の混同」チェック**: 出典が示すのが(i)事件の攻撃主体(声明・当局発表)なのか、(ii)その主体の一般的動機なのか、(iii)地域紛争の一般的背景なのかを区別して整理。裏付けの質(一次発表/通信社報道/分析記事)を付す。
- §5 **原因別の対応案**: 範囲内不具合→修正設計(変更箇所:行・最小変更・Regression案・正式経路検証案[中東テーマで1回のResearch再実行が必要か、費用見積]・影響Family)。情報源に存在しない→「未確認事項」としての記録案。新仕様→判断候補(欠落原因・改善案・Q/D/C影響・過剰仕様の回避[全記事一律必須化はしない])。
- §6 **結論(ユーザー向け、3〜6文)**: 3点それぞれの欠落工程と原因を証拠付きで。
- §7 Opusレビュー観点案(修正が新構造を伴う場合のみ、5件以内)。

## 事前指定Read一覧
- `er019_output/middle_east_yemen_saudi/run_mey_01/entry_point.json`(全体)
- `er019_output/middle_east_yemen_saudi/run_mey_01/`直下と`research/`・`audit/`・`b3*/`のディレクトリ一覧(`Get-ChildItem -Recurse -Depth 2 | Select FullName,Length`)→主要json先頭200行ずつ
- `er019_family_x_entertainment_production_runner_01.py`: Grep `research|ledger|verify|fact_lock|stage`→stage順序と関数名の範囲
- Family X Research実装: Glob `er019_family_x_*research*.py`・`er019_*fact*ledger*.py`・`er019_*fact*verif*.py`→各ファイルのGrep `def |PROMPT|query|source|reject|REASON`→主要関数とPrompt本文の範囲
- `docs/research/FAMILY-X-B3-FACT-MIN2-PRODUCTION-01/MEY_REGEN_02_REPORT_01.md`: Grep `Ledger|F0[0-9]|F1[0-1]|不採用`→Ledger 11件の内容と採否
- `docs/research/FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01/TRIAL_CLOSEOUT_01.md`: Grep `Ledger|不足|欠落|主体|動機`
- `docs/pm/delegation_log/2026-10-19_FAMILY-X-B3-FACT-MIN2-PRODUCTION-01_USER.md`(ユーザーが求めた記事水準の把握、全体2,418字)
- `CURRENT_SPEC.md`: Grep結果の該当行のみ(全文Read禁止)

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep `"query"|"queries"|search_query|"url"|"source"|rejected|reject_reason|verify|verification|confidence` in `er019_output/middle_east_yemen_saudi/run_mey_01/**/*.json`(`-l`で所在→該当ファイルを範囲Read)。
- Grep `Houthi|Ansar|claimed|responsib|Yemen|coalition|drone|missile` in 同run dir全json/md(`-n`、ヒットの所在=どの工程の成果物に主体情報が存在したか)。
- Grep `Research|Fact Ledger|Fact検証|B3` in `CURRENT_SPEC.md`(`-n`、見出し行と仕様文)。
- Grep `背景|主体|動機|background|context不足` in `OPEN_ITEMS.md`・`DECISION_LOG.md`(`-n`、過去対策)。
- `docs/pm/ACTIVE_TASK.md`先頭ヘッダ4行。

## 実行コマンド全文
- 抽出/T-0: `.venv\Scripts\python.exe docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 0 --out docs\pm\delegation_log\_extract_try_0.md`(indexを増やして照合) → `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_委任_01.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_委任_01.md_check.json`
- 原文sha: `powershell -Command "Get-FileHash -Algorithm SHA256 docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_USER.md | Select-Object -ExpandProperty Hash; (Get-Content -Raw docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_USER.md).Length"`
- 出典取得(例): `curl.exe -L -s -A "Mozilla/5.0" -o C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\xrg1\src_01.html "<出典URL>"`(URLごとに連番、取得時刻とHTTP statusを記録)
- run dir構造: `powershell -Command "Get-ChildItem -Recurse -Depth 2 er019_output\middle_east_yemen_saudi\run_mey_01 | Select-Object FullName,Length | Format-Table -AutoSize"`
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain`→明示add→commit→push(直近のorigin/main HEADに対しff-only、`git log --oneline -3 origin/main`で到達確認)

## SSOT追記文
編集権無し。RESULT_PACKETへ文案: OPEN_ITEMS新規(番号は委任_02が採番するOPEN-425と重複しないよう「XRG Research原因」1行案のみ)、DECISION_LOG(ユーザー決定5項目の記録は委任_02が行うため、本委任は「Research原因結論」1行案)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: delegation_log 2件(+check)。msg: `FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_01: ユーザー2026-10-20指示原文保存(C1評価撤回・Research根本原因調査・陽性対照Trial承認)`
- commit 2: `RESEARCH_GAP_ROOT_CAUSE_01.md`+補助script/json(出典原文は含めない)。msg: `FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_01: 中東記事 背景3点の欠落工程の追跡(検索/出典/抽出/検証/Ledger)+仕様照合+原因別対応案(API 0)`
- trailer: `Delegation: FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/委任_01`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_XRG1.md`: (1)T-0(原文・委任文の文字数・sha・check) (2)§6結論(逐語) (3)3点×6区分の判定表と欠落工程 (4)出典原文確認の結果(URL・媒体・取得可否・該当箇所の短い引用) (5)11-8判定(範囲内不具合の有無、あれば修正設計の要点と正式経路検証の費用見積) (6)過去対策との関係(再発/新規) (7)判断候補(新仕様が必要な場合のみ、ラベル無し) (8)費用JPY0 (9)Git (10)一覧外Read理由。判定整合行1行。