# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_02(ユーザー2026-10-20決定の記録: C1「VALIDATED(範囲限定)」評価の撤回とSSOT是正[OPEN-423/REGISTER #123/TRIAL_CLOSEOUT_01追記]+C1陽性対照Trialの設計・陽性対照Ledger候補の探索/構成[実在の検証済みFactのみ]+harness準備[er083再利用]+Fable照合後に実走する前提のdry-run。**有料実走は本委任ではしない**)。2026-10-20。
並行タスク衝突確認: 並行で(a)FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_02b(er084*、docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/、SSOTはOPEN-424/REGISTER #124行)、(b)本管理IDの委任_01(Research根本原因、`docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/RESEARCH_GAP_ROOT_CAUSE_01.md`、delegation_logのUSER原文保存を担当)が走る。本委任はそれらのファイルを編集しない。本委任の書込先=`docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/C1_POSITIVE_CONTROL_DESIGN_01.md`・`C1_*`、`er083_output/c1_positive_control_01/`、`er083_b3_background_fact_trial_01_*`の**新規ファイルのみ**(既存er083ファイルは変更しない。拡張は`er083_c1_positive_control_01_*.py`新規)、SSOT該当行、`docs/pm/RESULT_PACKET_XRG2.md`、delegation_log(自委任文)。SSOT編集権: あり(`OPEN_ITEMS.md` OPEN-423行+新規OPEN-425、`DECISION_LOG.md`末尾、`docs/pm/USER_DECISION_REGISTER_01.md` #123行+新規#125、`docs/pm/REPORT_LEDGER.md`、`docs/research/FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01/TRIAL_CLOSEOUT_01.md`への是正追記節)。**SSOT共有プロトコル**: 編集直前に`git status --porcelain`で他agentのstaged/unstaged変更を確認→対象ファイルを再Grep→自分の行だけ編集→即`git add <file>`→即commit(`.git/index.lock`があれば待つ)。他agentの行は触らない。`docs/pm/ACTIVE_TASK.md`は先頭へ自委任ヘッダ4行を追記のみ。

## 性質/到達上限Status/禁止事項
- 性質: SSOT是正+Trial設計・準備(DEV/Trial専用)。Production Prompt/schema/producer/Writer/B3は変更しない。
- 到達上限Status(本委任): `C1_EVAL_RETRACTED_POSITIVE_CONTROL_DESIGN_READY_PENDING_FABLE`。Trial全体の到達上限=VALIDATED(Production採用はユーザーのみ)。
- 禁止: (1)有料API実走(B3呼出・Writer呼出・Research)。dry-runのみ。(2)架空Factの作成(テスト用Ledgerは**実在の検証済みFact**[出典URL・媒体・確認日時付き]のみ)。(3)Production module変更・flag新設・Production配線。(4)過去テーマへの大規模展開。(5)`git add -A/-u/-f`・amend・rebase・force push・stash。(6)`er019_output/middle_east_yemen_saudi/run_mey_01/`は読取のみ。
- 修正範囲の線引き(11-8): 本委任に不具合修正は含まない(評価記録の是正はユーザー決定の反映)。
- Opus独立技術レビューGate(11-3): 本委任=非該当。陽性対照Trial設計はOpus_I(前Trial設計レビュー)の延長であり、新構造でなければ再レビュー不要(設計書に「Opus_Iとの差分」節を置き、Fableが要否判断)。
- 費用/日次: 当日既使用JPY49.70(出典RESULT_PACKET_PLW2a.md、並行PLW 委任_02bが最大+200)/本委任見積JPY0(dry-run・HTTP取得のみ)/Trial実走(委任_03)の見積は設計書で算出(目安: B3 call ≈JPY2〜4/回[前Trial R1実績 7 call≈JPY15.5]、Writer W-1≈JPY10〜15/本。陽性対照2 Ledger×{baseline, C1}×2 sample+陰性対照1×2 + Writer 2〜4本 ≈ JPY60〜90、案件合算300円以下)/承認区分C。
- T-3: 本委任はCapを伴わない(JPY0)。委任_03のCapは設計書の見積に基づきFableが設定。
- 時間見込み: 全体2.5〜3.5h(T-0 10分/SSOT是正30分/既存Ledger探索45分/陽性対照Ledger構成[必要時]45分/設計書40分/harness拡張+test 40分/dry-run・報告20分)。並列化: Ledger探索とharness拡張は独立。委任_01と並列。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**保存は打ち直さず`extract_delegation_from_jsonl_01.py`で抽出**(`--role assistant --tool-use-name Agent --tool-input-field prompt --index <N>`、管理ID行に`FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_02`を含む最初のもの)→`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_委任_02.md`。ユーザー原文の全文保存は委任_01が担当(`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_USER.md`。SSOT記録で参照する際、未作成なら「委任_01で保存中」と記し、sha256は委任_01のRESULT_PACKET_XRG1.mdから後で転記)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): 本委任はTTSを伴わない。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 本委任はCapを伴わない。

## ユーザー指示(原文、該当部抜粋。全文は委任_01保存ファイル)
> **ユーザー決定：** 1. **C1の有効性が確認されたという評価を撤回する。** 2. C1は背景Factの追加実績が0件であり、核心機能は未検証。従来の `VALIDATED（範囲限定）` はC1全体の有効性を意味しない。記録上も、確認済みの限定的成果と未検証機能を明確に区別する。 3. Researchの根本原因調査を進める。既存仕様の不具合なら、承認範囲内で修正・検証まで自律的に完了する。 4. B3の正式Production仕様は変更しない。C1のProduction採用は未承認。 5. 中東記事の音声化は引き続き保留。
> ## 3. C1 Trialの評価是正と追加検証
> 前回はC1・C2・C3を比較したものの、7回すべてで背景Fact追加が0件だった。C1の選定理由は、不必要な追加をしないこと、背景不足を正しく記録すること、ストーリー性を損なわないことに限定される。**必要な背景Factを見つけ、追加するという核心機能は一度も実証されていない。** したがって、C1の有効性を実証済みと扱わない。過去のTrial結果やFable分類は履歴として残し、現時点の評価を正しく修正する。
> ### 検証内容
> Research根本原因調査とは独立して実施可能な準備は並列化する。まず、既存のFact Ledgerから、以下の条件を満たす記事を探す。- 主要ストーリーに対して理解上必要な背景Factが実在する。- その背景FactがLedger内に記録されている。- 通常のB3では、そのFactが選ばれない可能性がある。- 追加すべきFactを、事後評価で明確に判定できる。
> 適切な既存Ledgerがない場合は、**実在する検証済みFactを用いたテスト用Ledger**で陽性対照を構成する。単なる架空の主張を事実として扱わない。
> C1について、以下を検証する。1. 必要な背景Factを正しく追加するか。2. 不必要なFactを追加しないか。3. 中心Storyline・エンターテインメント性を維持するか。4. 選定した背景Factが既存のWriter入力経路に正しく反映されるか。5. 記事として実際に理解しやすくなるか。6. 誤帰属・根拠のない因果関係・過剰な網羅化が生じないか。
> 既存のB3下限2 Factと、今回の補完候補を混同しない。検証はDEV／Trial環境に限定し、既存ProductionのPrompt・schema・producer・Writer経路を無断で変更しない。なお、**陽性対照を用いた限定的な追加Trialは今回の指示範囲内**とする。ただし、過去テーマへの大規模展開・Production採用・新規仕様の正式実装は別途ユーザー承認が必要。
> ### Trial Closeout
> - 核心機能の成功と記事品質維持を確認できた場合：`VALIDATED`。Production採用は未承認。- 失敗した場合：原因を分析し、承認範囲・予算内で合理的な修正と再検証を実施する。- 改善見込みがない場合：`REJECTED` を提案。- 新仕様や品質基準の変更が必要な場合：`USER_DECISION_REQUIRED`。単に「追加しなかった」という結果を、背景補完能力の成功として扱わない。
> ## 4. Writerへの伝達について
> 今回の本質的な問題は、B3の背景不足メモがWriterに届かなかったことではない。**Writerに不足を知らせても、裏付けとなるFactが存在しなければ記事は改善しない。** したがって、不足メモの伝達機構を新設することを優先しない。ただし、C1によって実際に背景Factを追加できた場合は、そのFactが後続の決定論的producerを通じてWriterに正しく渡り、本文で使われることまで検証する。必要なschema・producer変更が判明した場合は、実装を独断で進めず、変更範囲・QCD・正式採用の必要性を報告すること。
> ## 5. (抜粋) Trialは核心機能の検証に必要な最小構成とし、陽性・陰性条件から有効な結論を得る。

## 作業
W1. **評価の撤回・SSOT是正**(ユーザー決定1・2・4・5を忠実に): (a)`OPEN_ITEMS.md` OPEN-423行末に「2026-10-20 ユーザー決定: C1『VALIDATED(範囲限定)』評価を**撤回**。確認済み=不必要な追加をしない/背景不足を正しく記録する/ストーリー性を損なわない(7 call・追加0件)。**未検証=必要な背景Factを見つけて追加する核心機能(追加実績0件)**。Status=C1_CORE_UNVERIFIED(陽性対照Trialで再評価、FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01)。C1のProduction採用は未承認・B3正式仕様不変・中東記事音声化は保留継続」。(b)`docs/pm/USER_DECISION_REGISTER_01.md` #123行末に同趣旨+新規#125「判断済み(2026-10-20): C1評価撤回/Research根本原因調査/陽性対照を用いた限定的追加Trial承認(大規模展開・Production採用・新仕様実装は別途承認)/B3仕様不変/中東音声化保留」。(c)`docs/research/FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01/TRIAL_CLOSEOUT_01.md`末尾に「§X 2026-10-20 評価是正(ユーザー決定)」節を追記(本文は改変せず履歴として残す。確認済み/未検証の対比表)。(d)`DECISION_LOG.md`末尾にユーザー決定5項目(原文パス・sha[委任_01から転記、未取得なら「保存中」]・文字数)+Fable決定(委任_01/_02並列、C1 Status撤回)。(e)`OPEN_ITEMS.md`新規OPEN-425「FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01(Research欠落原因[委任_01]+C1陽性対照Trial[委任_02/_03])。Status=IN_PROGRESS」。(f)`docs/pm/REPORT_LEDGER.md`行追加。
W2. **既存Ledgerからの陽性対照候補探索**(API 0): `er019_output/*/run_*/`のFact Ledger(Glob `**/fact_ledger*.json`・`**/ledger*.json`、Family Xテーマ: coffee_prices等)を全走査し、各テーマについて(i)Ledger Fact一覧(ID・短文・種別・検証状態)、(ii)実際のB3採用ID(`b3*`/`storyline*`成果物)、(iii)**不採用Factの中に「主要ストーリーの理解に必要な背景(主体・動機・経緯・前提条件)を与えるFact」があるか**を、事前に固定した判定基準(背景Fact定義: 中心事象の「誰が/なぜ/何の前提で」を与え、無いと読者が中心事象の意味を誤解または理解不能になるFact。対義: 周辺数値・補足統計)で列挙。候補ごとにユーザー4条件(背景Fact実在/Ledger内に記録/通常B3で選ばれない可能性/事後判定が明確)の充足を○×で表にする。既存の前Trial(er083)の7 callのLedger=中東11件は「背景Fact自体がLedgerに無い」ため陽性対照にならないことを明記。
W3. **陽性対照Ledgerの構成**(W2で適格な既存Ledgerが無い場合、または1件しか無い場合に追加): 中東テーマ(run_mey_01の11件)を基礎に、**実在の検証済みFact**(例: 攻撃主体の声明・当局発表・通信社報道[Reuters/AP/公的発表]に基づく「誰が・なぜ・イエメン情勢との接続」)を2〜3件、出典URL・媒体・該当箇所引用・確認日時(無料HTTP取得で原文確認、取得不可なら候補から除外)付きで追加した`test_ledger_mey_positive_01.json`を作る(Production schemaに準拠、`verification=VERIFIED`の付与根拠を各Factに明記、`is_test_ledger=true`・`test_origin`を付けてProduction経路に混入しない名前・場所に置く)。**委任_01の原因調査で同じ出典を使う可能性があるため、追加Factの出典は委任_01の成果物と後で突き合わせられるよう記録**。陰性対照=背景Factが不要または既にB3で選ばれるLedger(W2で特定、例: 既存テーマのうち採用IDが背景を含むもの)1件。
W4. **Trial設計書**`C1_POSITIVE_CONTROL_DESIGN_01.md`: 条件{baseline(現行B3), C1}×Ledger{陽性対照1〜2, 陰性対照1}×sample 2(B3の非決定性)=8〜12 B3 call、Writer W-1は「C1で背景Factが追加された場合のみ」baseline記事と比較用に生成(最大4本)。評価6項目(ユーザー§3)の判定方法(1・2は機械判定: 追加ID∈期待背景Fact集合か/期待外追加0か、3・5・6は盲検rubric[前Trial R1_BLIND流用、採点者=別process・記事ラベル隠蔽]、4は`producer`出力→Writer入力の決定論的追跡[既存契約V5 `rules_sha256`不変を確認])。判定基準の事前固定(VALIDATED=陽性対照で期待背景Factを2/2 sample以上で追加かつ陰性対照で追加0かつWriter到達・本文使用かつrubricでストーリー性非劣化/REJECTED=追加0または陰性で追加/判断候補=トレードオフ)。費用見積・Cap案。Opus_Iとの差分節。E-1(B3仕様文・契約V5・OPEN-420下限2件との混同防止)。
W5. **harness拡張**(新規`er083_c1_positive_control_01_run.py`/`_eval.py`/`_test_01.py`、既存er083 libを**import再利用**): test Ledger読込・Production B3 module呼出(proxy方式は前Trialと同一、Production Prompt不変)・追加ID判定・Writer probe呼出(既存`er083_b3_background_fact_trial_01_writer_probe.py`を再利用)・費用集計(THEME_TAG `C1_POSCTRL_01`)・`--dry-run`。test 8件程度(API 0)。
W6. dry-run(呼出数・見積JPY)→RESULT_PACKET。

## 事前指定Read一覧
- `docs/research/FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01/TRIAL_DESIGN_01.md`(全体)、`TRIAL_CLOSEOUT_01.md`(全体)、`R1_BLIND_PACK_01.md`:1-40(rubric書式)
- `er083_b3_background_fact_trial_01_lib.py`・`_run.py`・`_eval.py`・`_writer_probe.py`(全体、Trialファイル)
- `er019_family_x_storyline_b3_fact_selection_01.py`: Grep `def |PROMPT|min_verified_selected|VERIFIED|AMBIGUOUS`→関数シグネチャとPrompt範囲(読取のみ)
- `er019_output/middle_east_yemen_saudi/run_mey_01/`: Fact Ledgerファイル(Grep `-l "F01"`で所在)全体、`entry_point.json`
- `er019_output/`配下の他テーマ: Glob `er019_output/*/run_*/**/fact_ledger*.json`→各先頭150行、対応するB3成果物(Glob `**/b3*/*.json`・`**/storyline*.json`)の採用ID部分
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `^- #12[3-9]`→末尾番号・#123行
- `OPEN_ITEMS.md`: Grep `^- OPEN-42[3-9]`→OPEN-423行・末尾番号(全文Read禁止)
- `CURRENT_SPEC.md`: Grep `B3|Fact Ledger|契約V5|rules_sha256`→該当行のみ

## 事前指定Grep一覧+追記位置・更新位置の手順
- `OPEN_ITEMS.md`: Grep `^- OPEN-423`→行末追記。Grep `^- OPEN-424`→その直後にOPEN-425を追加(無ければ末尾)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `^- #123\(`→行末追記。Grep `^- #124`→直後に#125。
- `DECISION_LOG.md`: 末尾(直近の`## 2026-10-20`エントリの後)。
- `docs/pm/REPORT_LEDGER.md`: Grep `FAMILY-X-B3-BACKGROUND`→同書式で新行。
- `docs/pm/ACTIVE_TASK.md`先頭ヘッダ4行。

## 実行コマンド全文
- 抽出/T-0: `.venv\Scripts\python.exe docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 0 --out docs\pm\delegation_log\_extract_try_0.md`(indexを増やして照合) → `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_委任_02.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_委任_02.md_check.json`
- Ledger走査: `powershell -Command "Get-ChildItem -Recurse er019_output -Filter *ledger*.json | Select-Object FullName,Length,LastWriteTime | Format-Table -AutoSize"`
- 出典取得(W3): `curl.exe -L -s -A "Mozilla/5.0" -o C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\xrg2\src_01.html "<出典URL>"`(連番、取得時刻・HTTP status記録。本文はcommitしない)
- test: `.venv\Scripts\python.exe -m pytest er083_c1_positive_control_01_test_01.py -q`
- dry-run: `.venv\Scripts\python.exe er083_c1_positive_control_01_run.py --design docs\research\FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01\c1_posctrl_matrix_01.json --out er083_output\c1_positive_control_01 --dry-run`
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain`→明示add→commit→push(origin/main HEADへff-only、`git log --oneline -3 origin/main`で到達確認)

## SSOT追記文
W1(a)〜(f)のとおり(実値で埋める)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1(SSOT是正、先行): OPEN_ITEMS/REGISTER/DECISION_LOG/REPORT_LEDGER/TRIAL_CLOSEOUT_01追記/delegation_log。msg: `FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_02: C1評価撤回のSSOT是正(OPEN-423 C1_CORE_UNVERIFIED/REGISTER #123・#125/DECISION_LOG/TRIAL_CLOSEOUT是正節)+OPEN-425起票`
- commit 2: 設計書・候補探索結果・test Ledger(実在Fact、出典付き)・harness・test。msg: `FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_02: C1陽性対照Trial設計+既存Ledger候補探索(<n>テーマ)+陽性対照Ledger<n>件/陰性対照<n>件+harness・test(API 0、dry-run見積JPY<v>)`
- trailer: `Delegation: FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/委任_02`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_XRG2.md`: (1)T-0 (2)SSOT是正の差分(ファイル:行) (3)既存Ledger候補表(テーマ×4条件○×、背景Fact候補の内容と不採用理由) (4)陽性対照Ledgerの構成(追加Factの原文・出典URL・媒体・引用・確認日時・VERIFIED根拠)/陰性対照 (5)設計書要点(条件・call数・判定基準・費用見積・Cap案・Opus_Iとの差分) (6)harness・test結果・dry-run見積 (7)委任_01との依存(同一出典の突合せ点) (8)費用JPY0 (9)Git (10)判断候補(あれば、ラベル無し) (11)一覧外Read理由。判定整合行1行。