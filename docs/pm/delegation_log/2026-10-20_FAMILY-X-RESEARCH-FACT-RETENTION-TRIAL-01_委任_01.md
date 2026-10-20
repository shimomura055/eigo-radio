# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_01(ユーザー2026-10-20指示原文保存[T-0]+既存Research実装の工程分解[検索/抽出・構造化/検証の分離可否]+事前登録Trial設計書[複数方式の比較・コスト比較・一般化・下流接続]+Trial専用harness+①現行再現[既存出典のみ、追加Web検索0]+費用見積と承認区分の判定)。2026-10-20。
並行タスク衝突確認: 並行でFAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 委任_01(Family Z、er006/er026、`docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/`、SSOT: CURRENT_SPEC PL行・新規OPEN-426・REGISTER #126・DECISION_LOG末尾・REPORT_LEDGER)が走る。本委任はそれらを編集しない。本委任のSSOT編集権: `DECISION_LOG.md`末尾追記と`docs/pm/REPORT_LEDGER.md`行追加のみ(共有プロトコル: 編集直前に`git status --porcelain`→再Grep→自分の行のみ→即add→即commit、`.git/index.lock`は待つ)。OPEN_ITEMS新規行・REGISTER新規番号は委任_02で採番(番号衝突回避)。書込先=`docs/research/FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01/`、`er085_research_fact_retention_trial_01_*.py`(新規)、`er085_output/research_fact_retention_trial_01/`、`docs/pm/RESULT_PACKET_XRFR1.md`、delegation_log。`er019_output/`・`er083_output/`は読取のみ。

## 性質/到達上限Status/禁止事項
- 性質: Trial設計+harness+現行再現(Trial専用経路)。Production Prompt/schema/Researcher/Verifier/B3/Writerは変更しない(Trialは別Prompt・別経路でProduction関数を**呼ぶ/複製する**のみ)。
- 到達上限Status(本委任): `XRFR_DESIGN_HARNESS_READY_BASELINE_REPRODUCED_PENDING_FABLE`。Trial全体の到達上限=VALIDATED(Production採用はユーザーのみ)。
- 禁止: (1)追加Web検索(API)。出典は`run_mey_01`の記録URL(委任_01 XRG1で原文取得済み: scratchpad `xrg1/`、HTTP 200のもの)と、一般化用テーマの記録URLの**無料HTTP再取得**のみ。(2)比較方式B〜Eの有料実走(委任_02、Fable照合後)。本委任の有料実走は**①現行再現**のみ(≤JPY30)。(3)架空Fact・出典にない主体/動機/因果の創作(評価の正解集合[gold]は出典原文の逐語引用で定義)。(4)`git add -A/-u/-f`・amend・rebase・force push・stash。(5)結果を見てから指標・閾値を変える(設計書を実走前にcommit)。
- 修正範囲の線引き(11-8): 本委任に不具合修正は含まない。
- Opus独立技術レビューGate(11-3): 本委任=非該当。設計書完成後、Fableが任意レビュー要否を判断(設計書に「Opusレビュー観点案5件以内」を含める)。
- 費用/日次: 当日既使用=集計ツール値JPY390.26(RESULT_PACKET_XRG3.md、案件別積上げ約283との差約107は未確認→**本委任で`daily_dev_cost_01.py`の内訳を出力し差分の出所[theme tag/run dir/二重計上]を特定して報告**)。並行PLWP1が最大+80。本委任見積JPY≤30(①現行再現: 既存出典テキストを入力にしたResearcher相当呼出2 sample、研究記録の実測research≈JPY27/回は検索込みのため、検索なし呼出は下回る想定。超えそうなら1 sampleで止める)。承認区分C。**Trial全体(委任_02)の見積が案件合算300円を超える設計になる場合は、その旨と削減案(sample数・方式数・題材数の削減)を設計書に併記し、Fableがユーザー費用承認(7-7)の要否を判断する。**
- T-3: 上限¥30(Guardrail、本委任分)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 時間見込み: 全体3.5〜5h(T-0 10分/工程分解60分/gold定義+一般化題材選定45分/設計書60分/harness+test 60分/①実走30分/費用差分突合20分/報告20分)。並列化: 工程分解とgold定義は独立。①実走はharness後。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**保存は打ち直さずsession JSONLから抽出**(`extract_delegation_from_jsonl_01.py --role assistant --tool-use-name Agent --tool-input-field prompt --index <N>`、管理ID行に`FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_01`を含む最初のもの。index走査で特定できなければJSONL行を直接抽出)→`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_01.md`。ユーザー原文は同抽出結果の`---(原文ここから)---`〜`---(原文ここまで)---`を切り出し`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_USER.md`へ(先頭メタ1行`<!-- 受領日: 2026-10-20 / 受領者: Fable(sandwich-pm) / 保存: 委任_01 -->`のみ付加)。文字数・sha256を記録。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): 本委任はTTSを伴わない。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 定型文は上記に記載済み。

## ユーザー指示(原文)
---(原文ここから)---
# Family X Researcher Fact欠落・根本改善比較Trial

**管理ID：FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01**

## 1. 目的

Researcherが取得済みの出典に含まれる重要情報を、Fact抽出・構造化の際に脱落させる問題を根本改善する。

中東記事では、国連の出典に明示された「攻撃主体＝フーシ派」や「紅海・イエメン情勢の背景」がFact Ledgerへ十分に反映されなかった。

**品質を改善しながら、検索・処理時間・量産単価の無駄な増加を防ぐこと。**

優先順位：品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費用。

## 2. Trialの実施方針【ユーザー承認済み】

以下①〜⑤を一括実施する。

| 項目 | 内容 |
|---|---|
| ① 現行再現 | 既存の出典・Researcherで欠落を再現し、原因と発生条件を確認 |
| ② 複数仕様の比較 | Promptの指示方法、Fact粒度、情報保持方式、検証方式などを複数比較 |
| ③ 正確性検証 | 出典にない主体・動機・因果関係の創作がないことを確認 |
| ④ 一般化検証 | 中東以外の記事でも重要情報を保持できるか検証 |
| ⑤ 下流接続 | 抽出FactがLedgerに登録され、B3から利用可能であることを確認 |

単一Promptへの決め打ちは禁止。

異なる改善アプローチを比較し、**1回のTrialで採否判断に足る結果を取得できるよう設計すること。**

比較候補数・組合せ・実行方法はFable／Claudeが最適化する。既存仕様や過去Trialを確認し、重複検証を避ける。

## 3. 改善の基本要件

出典に明示された、記事理解に必要な情報をFact化の段階で不当に省略しない。

特に以下を検証する。

- 主体：誰が行ったか
- 行為・対象：何を、誰に対して行ったか
- 理由：出典に明示されている場合のみ保持
- 背景・文脈：出来事の理解に必要な関連情報を保持
- 情報の出典・根拠：既存のFact Ledger仕様を維持

全Factに一律の項目を強制したり、不要なFactを大量生成したりしない。

また、Researcherの段階でストーリーに使うFactを過度に絞り込まない。最終的なストーリー設計とFact選定はB3の役割である。

## 4. コスト比較【必須・重要】

**改善によって無駄なWeb検索やLLM呼出が増える方式は、原則として採用候補にしない。**

各方式について、現行Production方式を基準に次の項目を比較する。

| 比較指標 | 確認内容 |
|---|---|
| Web検索 | 検索回数、追加検索回数、重複検索、検索費用 |
| LLM | 使用モデル、呼出回数、入力・出力token、費用 |
| 検証処理 | Validator／再評価／retryの回数と費用 |
| 全体原価 | Research〜Ledger登録までの1記事当たり推定費用 |
| 処理時間 | 現行比での所要時間増減 |
| 品質 | 重要Fact保持率、欠落率、創作・誤帰属、不要Fact増加 |

**コスト測定は、共通条件・同一出典で比較すること。**

特に以下を徹底する。

1. 既に取得した出典を再利用できる場合、追加Web検索を行わない。
2. Promptや構造化方法の改善だけで解決できるなら、検索工程を増やさない。
3. 検証用LLM呼出を増やす場合も、品質改善に必要か、より安価な代替がないか比較する。
4. 単に検索や検証回数を増やして品質を上げる方式は、費用対効果を明示する。
5. Trial費用と量産時の恒常費用を区別する。
6. Research単体だけでなく、既存の**70円／記事セット**という全体原価目標への影響も示す。

**品質が同等なら、追加検索・追加LLM呼出が少なく、安価で速い方式を優先する。**

品質が改善しても量産単価が増える場合は、その増加が不可避か、既存出典の再利用等で回避可能かを検証する。

重要なコスト増加を伴う方式は、自動的にProduction採用候補としない。

## 5. Trial設計・実行

- まずCURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、今回の根本原因調査を確認する。
- 現行実装と承認済み仕様の整合を確認し、原因に応じた改善方式を設計する。
- Promptの表現変更だけでなく、情報抽出と検証工程の役割分担も比較対象とする。
- 中東記事の既存出典を主たる比較条件とし、別題材で一般化を確認する。
- 各条件で同一出典を使用し、方式の差を比較できるようにする。
- 取得済みデータ・出典・中間成果物を最大限再利用する。
- 独立した比較・評価は並列実行する。
- 成果が見込めない反復を避け、必要なら異なるアプローチへ切り替える。

既存の承認済み品質基準を変更しない。

Trial設計に必要な技術的判断・比較条件の選択はFable／Claudeへ委任する。

費用は承認済み開発予算・日次上限1,000円（JST）および個別承認枠内で管理する。新たな予算上限の承認が必要なら、超過前にSTOPして報告する。

## 6. 受入条件

- 中東記事の主体・背景に関する欠落が改善される。
- 出典にない事実・動機・因果関係を作らない。
- 別題材でも情報保持の改善が確認できる。
- Ledgerへの登録とB3からの利用可能性が確認できる。
- 現行比の品質・検索回数・LLM費用・処理時間が比較できる。
- 無駄な検索・再検証の増加がない、または必要性と削減不能な理由が説明されている。
- Productionの正式経路には未承認変更を加えない。

## 7. 最終報告

結果は以下の順序で報告する。

1. **最も推奨する改善方式と、その理由**
2. 現行方式と改善候補の品質比較
3. **Web検索回数・LLM呼出・量産単価・処理時間の比較**
4. 中東記事での欠落改善結果（Before／Afterの具体的Fact）
5. 別記事での一般化結果
6. Ledger→B3接続確認
7. 未解決問題・リスク
8. Production採用に必要なユーザー判断

改善候補はTrial終了時に `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED` へ分類する。

`VALIDATED` であっても正式Productionへ自動配線しない。Production採用にはユーザーの明示的承認を必要とする。

Git・Trial成果物・SSOT・Open Itemの整合を確認し、Fableが独立評価する。

## 8. その他の進行中タスク

C1陽性対照Trialは予定どおり継続する。

**結果が出たら報告すること。現時点で追加の議論やユーザー判断を求める必要はない。**

Researcher改善Trialと独立して進め、不要な待機・依存関係を設けない。

---

**最終目的は、Researcherが重要Factを落とさずLedgerに供給できる仕組みを、品質・速度・量産単価の観点から最適化すること。**

単にFact保持率を上げるのではなく、追加検索・追加LLM呼出を極力発生させず、継続的な量産に適した改善方式を見極めること。
---(原文ここまで)---

## Fableからの前提共有(鵜呑みにせず照合)
- 根本原因(XRG 委任_01、`docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/RESEARCH_GAP_ROOT_CAUSE_01.md`): 出典(国連特使声明10/11・国連発表10/9)に主体`Ansar Allah`・紅海/Bab al-Mandab文脈が明記→Researcherのclaim化で受動形になり主体・文脈が脱落(F01/F11)→検証は正しさのみで省略を検知せず。Researcher Promptの構造化4観点(`er003_v1_en_direct_vfl_01_generate.py:156-162`)、検証観点(同:237-246)、`FACT_LEDGER_JSON_SCHEMA`に帰属欄なし。共用`build_researcher_prompt`は15本超がimport。XRG 委任_01 §5-3に新観点案(条件付き第5/6観点+検証1行)。
- C1陽性対照Trial(XRG 委任_03): LedgerにF12(主体)があれば現行B3が選びWriter本文で使われる(PC2 baseline 2/2)=下流は機能。是正の本線は上流Research。
- 実測費用: research≈JPY26.995/回+ledger≈9.110/回(run_mey_01、`MEY_REGEN`/XRG1記録。researchは検索込み)。

## 本委任の作業
W1. **工程分解**(JPY0): Family X Research経路を関数:行で分解する。(a)検索(どのAPI/モデルで何回、`run_researcher_for_topic`内で検索とFact抽出が1 LLM呼出に統合されているか分離されているか)、(b)抽出・構造化(claim化のPromptと出力schema)、(c)検証(`run_verification_for_topic`の入力=出典本文を再取得するのか、Researcherの引用のみか)、(d)Ledger生成(`fact_ledger_draft.json`→`VERIFIED`確定→`fact_ledger.json`)、(e)B3への受け渡し。各工程の使用モデル・token・費用の記録箇所(cost log行)を特定。**重要**: 「同一出典・検索なし」で方式比較するための注入点(出典本文を与えてclaim化だけを走らせる関数/Prompt分割が存在するか。無ければTrial harnessでProductionのPrompt本文を**複製**し、検索ツールなしのモデル呼出に出典本文を同梱する方式=Production同等性の限界を設計書に明記)。
W2. **gold(正解集合)の定義**(JPY0): 中東=XRG1で取得済み出典(scratchpad `xrg1/`のHTML、HTTP 200のもの。無ければ同URLを無料再取得)から、「記事理解に必要な重要情報」をユーザー§3の5区分(主体/行為・対象/理由[明示時のみ]/背景・文脈/出典)で**出典原文の逐語引用付き**に列挙(例: 主体=Ansar Allah[特使声明10/11]、背景=9月のフーシ派攻勢・紅海商船への脅威[国連発表10/9]、理由=出典に明示なし→gold対象外)。不要Factの定義(周辺数値の重複等)も事前固定。一般化題材: `er019_output/`の既存テーマ(hormuz/coffee/semiconductor等)から、出典URLが記録され無料再取得できテーマ理解に主体・背景が必要なものを**1〜2件**選び、同様にgoldを定義(選定規則を事前記録)。
W3. **比較方式の設計**(設計書`TRIAL_DESIGN_01.md`、実走前commit): 現行(E0)+候補4〜5: A=Prompt指示追加(XRG1 §5-3の条件付き観点、他は不変)/B=Fact粒度・構造(claimに任意の`actor`/`context`付記を許す出力schema拡張[Trial専用schema、Ledger本体schemaは不変で`notes`等既存欄へ格納できるかも比較])/C=検証側(verifierに「出典が明示した主体・文脈の省略検知」を追加、Researcher不変)/D=A+C/E=二段(抽出後に「保持監査」LLM呼出を1回追加=コスト増方式、費用対効果の対照として含める)。各方式について追加Web検索=0・追加LLM呼出数・使用モデル(最新上位系を原則、現行と同一モデルで比較、25節)・token見積・1記事当たり恒常費用・処理時間・70円/記事セットへの影響を事前見積。指標: 重要Fact保持率(gold一致、採点規則固定)/欠落率/創作・誤帰属(gold外で出典に裏付けのない主体・動機・因果=0が必須、採点は出典逐語照合)/不要Fact増加数/Ledger登録可否(Trial用Ledger生成→schema検証)/B3利用可能性(er083系harnessでB3 1 callしF12相当が選ばれるか、方式ごとに最良1条件のみ)。sample数(非決定性、各2)。判定基準(VALIDATED候補=保持率が現行比で明確改善かつ創作0かつ不要Fact増≤Xかつ追加LLM呼出0[Eは例外明示]かつ一般化題材でも改善/REJECTED/判断候補)。費用見積表(Trial費用と量産恒常費用を分離)。**案件合算300円以下に収まる構成を主案**とし、超える場合は削減案を併記。並列化計画。§Opusレビュー観点案5件以内。§E-1(CURRENT_SPECのResearch/Fact Ledger仕様行の逐語、OPEN-416/425、DECISION_LOG 20154)。
W4. **harness**(`er085_research_fact_retention_trial_01_{lib,run,eval,test_01}.py`): 出典本文(テキスト化、URL・取得時刻・sha)をmanifestで固定→方式別Prompt(E0はProduction Prompt本文の複製、差分は設計書に逐語で)→LLM呼出(費用は`er005_cost_logger` THEME_TAG `XRFR_TRIAL_01`、token・model・時間を記録)→claim JSON→Trial用Ledger生成(Production schema検証関数を呼ぶ)→eval(gold一致・創作検出・不要Fact・費用)。test 8件程度(API 0: Prompt差分の固定、採点規則、創作検出の正負例、集計)。
W5. **①現行再現**(有料≤JPY30): 中東出典でE0を2 sample実行し、主体・文脈の脱落が再現するか(gold保持率・どのFactで落ちるか)を記録。再現しない場合はその事実と条件差(入力形式・モデル・検索有無)を分析して報告(都合の良い解釈をしない)。
W6. **費用差分突合**: `daily_dev_cost_01.py --date 2026-10-20`の内訳(theme tag/run dir別)を出し、案件別積上げ(メロス再生成28.79/PLW Trial 114.9/XRG 139.18/他)との差約107円の出所を特定。
W7. 報告`docs/pm/RESULT_PACKET_XRFR1.md`+DECISION_LOG末尾1行(ユーザー承認の記録: 原文パス・sha・文字数、Fable決定=設計先行・①のみ実走)+REPORT_LEDGER行。ACTIVE_TASK先頭ヘッダ。

## 事前指定Read一覧
- `docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/RESEARCH_GAP_ROOT_CAUSE_01.md`(全体)、`xrg1_trace_01_result.json`: 先頭150行
- `docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/C1_POSITIVE_CONTROL_CLOSEOUT_01.md`: Grep `F12|Writer|所見`
- `er003_v1_en_direct_vfl_01_generate.py`:130-300(Researcher/検証Prompt、schema)、Grep `def build_researcher_prompt|def run_researcher_for_topic|def run_verification_for_topic|search|perplexity|tool`
- `er012_e_family_entertainment_two_level_runner_01.py`:170-230
- `er019_family_x_entertainment_production_runner_01.py`:90-150
- `er019_output/middle_east_yemen_saudi/run_mey_01/`: Grep `-l "source_url"`→draft/ledger json全体、cost log(Grep `research|ledger`)
- `er083_c1_positive_control_01_run.py`: Grep `def |b3|ledger`(B3呼出の再利用点)
- `er005_cost_logger.py`:30-70、`docs/pm/tools/daily_dev_cost_01.py`:1-80(内訳出力の引数)
- `er005_output/cost_baseline_01/pricing_snapshot.json`: Grep `gpt|gemini|perplexity|sonar|search`
- `docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/TRIAL_DESIGN_01.md`:52-64(事前登録基準の書式前例)
- `CURRENT_SPEC.md`: Grep `Research|Fact Ledger|Researcher|検証者|verify`→該当行のみ(全文Read禁止)

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep `source_url|"url"` in `er019_output/*/run_*/**/fact_ledger*.json`(`-l`)→一般化題材の出典URL有無。
- Grep `THEME_TAG|theme_tag` in `er005_cost_logger.py`・`er083_*lib.py`→費用記録の踏襲。
- `DECISION_LOG.md`: 末尾追記。`docs/pm/REPORT_LEDGER.md`: Grep `FAMILY-X-RESEARCH-BACKGROUND`→直後に新行。
- `docs/pm/ACTIVE_TASK.md`先頭ヘッダ5行以内。

## 実行コマンド全文
- 抽出/T-0: `.venv\Scripts\python.exe docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 0 --out docs\pm\delegation_log\_extract_try_0.md`(index走査) → `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_01.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_01.md_check.json`
- 原文sha: `powershell -Command "Get-FileHash -Algorithm SHA256 docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_USER.md | Select-Object -ExpandProperty Hash; (Get-Content -Raw docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_USER.md).Length"`
- 出典再取得(必要時): `curl.exe -L -s -A "Mozilla/5.0" -o C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\xrfr1\src_01.html "<URL>"`(テキスト化した本文はTrial manifest配下`er085_output/research_fact_retention_trial_01/sources/`へ保存可[引用目的・repo commit可否は著作権配慮で抜粋のみcommit、全文はcommitしない])
- test: `.venv\Scripts\python.exe -m pytest er085_research_fact_retention_trial_01_test_01.py -q`
- ①現行再現: `.venv\Scripts\python.exe er085_research_fact_retention_trial_01_run.py --design docs\research\FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01\design_matrix_01.json --variant E0 --topic mey --samples 2 --out er085_output\research_fact_retention_trial_01 --budget-jpy 30`(先に`--dry-run`)
- eval: `.venv\Scripts\python.exe er085_research_fact_retention_trial_01_eval.py --out er085_output\research_fact_retention_trial_01 --report docs\research\FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01\BASELINE_REPRO_01.md`
- 費用内訳: `.venv\Scripts\python.exe docs\pm\tools\daily_dev_cost_01.py --date 2026-10-20`(内訳出力の引数はhelpで確認、無ければscript内の集計元jsonlを直接集計して表にする)
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain`→明示add→commit→push(origin/main HEADへff-only、`git log --oneline -3 origin/main`で到達確認)

## SSOT追記文
DECISION_LOG末尾1行(W7)とREPORT_LEDGER行のみ。OPEN/REGISTERの文案はRESULT_PACKETへ(委任_02で採番)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: delegation_log 2件+check。msg: `FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_01: ユーザー2026-10-20指示原文保存(Researcher Fact保持 複数方式比較Trial承認)`
- commit 2(実走前): 設計書・design_matrix・gold定義・harness・test。msg: `FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_01: 工程分解+gold定義(出典逐語)+事前登録Trial設計(E0+A〜E、コスト比較)+harness・test(API 0)`
- commit 3: ①現行再現結果+費用差分突合+DECISION_LOG/REPORT_LEDGER。msg: `FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_01: ①現行再現(E0×2、実費JPY<v>)+当日費用差分突合+SSOT初回記録`
- trailer: `Delegation: FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01/委任_01`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_XRFR1.md`: (1)T-0 (2)工程分解の要点(検索と抽出の分離可否、注入点、Production同等性の限界) (3)gold一覧(中東+一般化題材、逐語引用付き)と題材選定規則 (4)設計書要点(方式E0/A〜E、指標、判定基準、sample数、費用見積[Trial/恒常]、案件合算と300円判定、削減案) (5)harness・test結果 (6)①現行再現の結果(脱落の再現有無、保持率、落ちたFact) (7)当日費用差分の突合結果 (8)費用(本委任実費・当日累計) (9)Git (10)判断候補(あれば、ラベル無し。特にTrial費用が300円超の場合の費用承認要否) (11)一覧外Read理由。判定整合行1行。