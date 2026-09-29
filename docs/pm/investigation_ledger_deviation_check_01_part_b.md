# LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01 Part B

過去STOP事例の抽出・厳しさの分類・QCD影響の実測調査(read-only、委任_02)。
**本ファイルは調査結果の記録のみであり、新仕様・閾値・判定ロジックの採用提案は行わない。**
費用: ¥0(API呼び出しなし。全て既存ログ・REPORTのGrep/Read/集計のみ)。

## 0. 母集団・スコープ

- 全文検索対象: リポジトリ内で「deviation」を含むディレクトリ名/ファイル名を持つ`*.json`。
  724件をスキャンし、うち481件が10-category Ledger Deviation Checker schema
  (`parsed.overall_status`＝`LEDGER_COMPLIANT`/`LEDGER_DEVIATION`、`parsed.deviations[]`)を持つ。
  431件`LEDGER_COMPLIANT`・50件`LEDGER_DEVIATION`、deviation個票は224件(MAJOR 87・MINOR 137)。
  対象期間はコミット履歴でER-009(2026年6月頃)〜FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01
  (2026-09-29)まで、er003_output〜er045_output、約40プロジェクトディレクトリ。
- このうち**origin(ja_source/translation)フィールドを持つのは9ファイル・15件のみ**、全て
  Family X Entertainment(JA原文→EN Advanced/Standard翻訳)パイプライン
  (er019/er037/er039/er045)。これがユーザーの問題意識(Hormuz記事のEN側origin=ja_source
  MAJOR STOP)に直接該当する母集団であり、本章のA/B分類・4区分・cross-tabは主にこの15件を
  対象とする。それ以外の209件(pool_pilot/cefr_direct/Editorial B-Family等)は英語原文記事
  (JA→EN翻訳を経ない)や旧世代Checkerで、originの概念自体が存在しないため参考扱いとする。
- 集計スクリプト: scratchpad
  `C:\Users\tensh\AppData\Local\Temp\claude\...\scratchpad\aggregate_checker_logs.py`
  (repo外、再現用にコマンドのみ記録: `.venv\Scripts\python.exe <scratchpad>\aggregate_checker_logs.py`)。

## 3. 過去のSTOP事例(Family X, origin付き15件)

### A候補: 明らかに止めるべきだったと思われる事例

| # | 管理ID/対象 | 該当文(JA→EN逐語) | 判定 | STOP/retry | 解決 | コスト | Evidence |
|---|---|---|---|---|---|---|---|
| A-1 | FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01系列前身、`family_x_b3_production_wiring_01`run_01 Meta記事 | JA Original「ロールバックされます」(未来形、上流ドリフト)→Advanced/Standard英訳もこの未来形を継承 | MAJOR、origin混在(claim単位でja_source/translation) | 2回ともCheckerがCOMPLIANT誤判定(RuntimeErrorのSTOPは発生せず)。後に**別タスクの手動テキスト直接修正**(`fact_fidelity_fix_01`)で是正・recheck | 人手修正+recheck ¥1.567(b1b¥0.323+a2¥1.244) | `NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01_REPORT.md`§3/§9-B、`er019_output/family_x_b3_production_wiring_01/run_01/audit/fact_fidelity_fix_01_recheck_summary.json` |
| A-2 | `family_xy_concreteness_control_trial_01`hormuz task_a_advanced(A3) | JA「上げ幅が一時的に縮小した」(HF-009)→EN「prices began to fall」 | MAJOR/ja_source | Trial測定(retry無し)。USER_DECISION_REQUIRED、Production不採用のまま終了 | Trial実測費用のみ(個別call、REPORT参照) | `er037_output/.../task_a_advanced/A3_deviation.json`、`FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_REPORT.md`L165 |
| A-3 | `family_xy_concreteness_control_trial_01`hormuz task_a_advanced(A3、別項目) | JA「支払義務者は未提示」(HF-003)→EN「those carrying the cargo would repay」(支払義務者を具体化) | MAJOR/ja_source | 同上Trial測定 | 同上 | `er037_output/.../task_a_advanced/A3_deviation.json` |
| A-4 | `family_xy_concreteness_control_trial_02`meta cells/AN2-T1 | JA「相手」(企業・店舗)→EN「users」(Museのユーザー) | MAJOR/translation | Trial cell測定(retry無し) | 同上 | `er039_output/.../meta/cells/AN2-T1_deviation.json` |
| A-5 | `family_x_no_heading_segmentation_trial_01`meta | JA「元に戻しました」(ロールバック)→EN「put back the feature」(再有効化と読める、意味反転) | MAJOR/translation | v1でMAJOR検出→v2でmust-fix retry 1回実施→LEDGER_COMPLIANT | ¥0.8142(retry generate+recheck) | `er045_output/.../meta/v2/must_fix_retry_result.json` |

分類理由(候補・断定せず): A-1/A-5は「起きた/まだ起きていない」「ロールバック/再有効化」という
事実の方向そのものが反転しており、英語学習記事としても事実誤認を生む可能性が高い。A-2は
数値の言い換え(上げ幅縮小→価格下落)で実際の値動きの向きが変わっている。A-3/A-4は
支払主体・対象範囲(誰が対象か)という具体的な取り違えで、プライバシー文脈(A-4)では
特に重要となりうる。

### B候補: 過剰品質の可能性がある事例

| # | 管理ID/対象 | 該当文(JA→EN逐語) | 判定 | STOP/retry | 解決 | コスト | Evidence |
|---|---|---|---|---|---|---|---|
| B-1 | `family_x_b3_production_wiring_01`run_01(diversity_trial ja_writer)/`family_x_refresh_e2e_01`run_01/b1b/`family_xy_concreteness_control_trial_01`A3/`family_xy_concreteness_control_trial_02`AN3-T1(**4回独立発生**) | JA「原油価格が高い状態が続けば、ガソリンや輸送費など身近な価格にも影響する」→EN「oil prices...linked to gasoline prices and transportation costs」 | MAJOR/ja_source(unsupported_new_claim・changed_scope) | 各回で個別にSTOP/Trial終了、retryなし(ja_source起因のためfail-closedでretry対象外) | 各回のCheckerコール実費(¥0.5〜1.6程度/回) | `er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/ja_writer/audit/deviation_checks/ja_original_attempt1.json`、`er019_output/family_x_refresh_e2e_01/hormuz/run_01/b1b/audit/deviation_checks/advanced_attempt1.json`、`er037_output/.../task_a_advanced/A3_deviation.json`、`er039_output/.../hormuz/cells/AN3-T1_deviation.json` |
| B-2 | **`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`run_02(委任背景に記載の本件)**、`family_x_refresh_e2e_01`hormuz run_02/b1b | JA「料金案が消えたからといって、価格がそのまま大きく下がる展開にはなりませんでした」→EN「The disappearance of the fee plan did not lead to a large, lasting fall in prices.」 | MAJOR/ja_source(changed_causality、related_fact_id=HF-011) | **STOP**(origin=ja_source検知でfail-closed、retry未実施の設計) | **未解決**(2026-09-29時点でUSER_DECISION_REQUIRED、次工程未着手) | run_02累計¥5.07(前run_01¥0.99232と合算で管理ID全体約¥6.05)+複数回委任(_08〜_10)の調査工数(未計測) | `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`L923-960、`er019_output/family_x_refresh_e2e_01/hormuz/run_02/b1b/audit/deviation_checks/advanced_attempt1.json` |
| B-3 | `family_xy_concreteness_control_trial_01`hormuz task_b_cleanup(B1) | JA全体の文脈→EN「...continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering.」(接続詞"so"で因果連結) | MAJOR/ja_source(changed_causality、HF-007) | Trial測定、retryなし | 未評価(Trial終了) | 同上 | `er037_output/.../task_b_cleanup/B1_deviation.json` |
| B-4 | `family_x_b3_production_wiring_01`run_01/b1b(Meta記事、他3項目) | JA「Meta従業員のプライバシー懸念」→EN「People feel differently when they think they are speaking to a machine and when they know a person is listening.」等、一般読者心理への一般化3件 | MAJOR/ja_source×2、translation×1(MUSE-HC-004/006/010) | 初回MAJOR→retry 1回(feedback未伝達の全文再生成)→最終的にCOMPLIANT | retry generate+check込み(§5参照、run全体¥4.9853) | `er019_output/family_x_b3_production_wiring_01/run_01/b1b/audit/deviation_checks/advanced_attempt1.json` |

分類理由(候補・断定せず): B-1は原油価格とガソリン価格の連動という一般常識レベルの経済知識で
あり、Checker自身のプロンプトが許容範囲と明記する「新規Factを伴わない一般的な情景描写」に
近い可能性がある(4回独立して同種claimが指摘されており、偶発ではなく構造的パターン)。
B-2(本件)は「一時的な上げ幅縮小+回復」という観測を「大幅な持続的下落は起きなかった」と
要約しており、意味の実質を大きく変えていない自然な要約表現である可能性がある。B-3は
複数の事実を並べる際の自然な接続表現(「so」)であり、断定的な単一原因の主張とまでは
言い切れない可能性がある。B-4は解説記事によくある一般化的言い回し。

### auto_downgraded(MAJOR→MINOR自動降格)事例

**0件**。スキャンした481ファイル・224件の個票のいずれにも`auto_downgraded: true`は存在しなかった
(該当キー自体は`family_x_refresh_e2e_01`のスキーマに存在するが、実際に発火した記録は見つからず)。

## 4. 現在の判定がどこまで厳しいかの分類(15件、可視化のみ・新仕様は決めない)

| 区分 | 件数 | 代表例 | 共通category | 共通origin |
|---|---|---|---|---|
| (i) 絶対にSTOPすべき | 2件 | A-2(価格方向反転)、A-5(ロールバック↔再有効化) | changed_causality/changed_number相当、changed_scope | ja_source1・translation1 |
| (ii) 高リスクなのでSTOP妥当 | 3件 | A-3(支払義務者具体化)、A-4(ユーザー範囲取り違え)、B-3系(具体的因果は要注意) | unsupported_new_claim、changed_scope | ja_source2・translation1 |
| (iii) 品質改善の意味はあるがSTOP必須か疑問 | 7件 | B-3(接続詞"so")、B-2(本件)、B-4の3項目、A-1のうち生成解釈寄りの一部 | changed_certainty、changed_causality | ja_source中心 |
| (iv) 過剰品質の可能性が高い | 3件 | B-1(原油→ガソリン価格、4回独立発生) | unsupported_new_claim、changed_scope | ja_source |

(この4区分は本調査担当者による1回限りの目視分類であり、断定ではなく「候補」。合議・再現性検証は
未実施。件数はMAJOR/MINOR15件全件を重複なく1区分ずつに割り当てた結果。)

### category × severity × origin クロス集計(実データ)

**全母集団(224件、origin無しの旧世代含む)**:

| category | MAJOR | MINOR |
|---|---|---|
| changed_fact | 31 | 14 |
| changed_scope | 16 | 24 |
| changed_causality | 14 | 9 |
| changed_certainty | 9 | 49 |
| changed_number | 1 | 0 |
| changed_actor | 0 | 7 |
| changed_negation | 0 | 0 |
| changed_comparison | 3 | 1 |
| changed_time | 1 | 7 |
| unsupported_new_claim | 36 | 28 |

**origin付き15件のみ(MAJORのみ、origin別)**:

| category | ja_source | translation |
|---|---|---|
| changed_fact | 0 | 0 |
| changed_scope | 3 | 1 |
| changed_causality | 5 | 0 |
| changed_certainty | 0 | 1 |
| changed_number | 0 | 0 |
| changed_comparison | 1 | 0 |
| changed_time | 0 | 0 |
| unsupported_new_claim | 7 | 2 |

(全母集団ではchanged_fact/changed_certaintyが最多カテゴリだが、origin付きFamily X 15件では
changed_causality・unsupported_new_claimに偏っている。これはFamily Xが「JA原文への忠実な
翻訳+Ledgerとの整合」という二重制約下にあり、数値そのものの誤りより「原文の含意をどこまで
因果・新規主張として引き継ぐか」が主な論点になっているためと推測される。断定はしない。)

## 5. QCD影響

**母集団**: 主にFamily X entertainment(Hormuz/Meta Muse記事、er019/037/039/045、
2026年9月)。一部、Editorial B-Family(4V/2V Trial、er012)のFact Checker A'(Web検索付き、
Ledger Deviation Checkerとは別のCheckerだが同じ3段構成の一部)のコストも参考値として含む。

### Checker単発コール(実測、n=12、model=gpt-5.6-luna、reasoning=high)

| 指標 | コスト(JPY) | latency(秒) |
|---|---|---|
| 最小 | ¥0.323 | 9.55 |
| 中央値 | ¥0.9024 | 33.16 |
| 平均 | ¥0.954 | 38.07 |
| 最大 | ¥1.6505 | 84.89 |

出典: `NEWS-FAMILY-X-JA-FACT-DOUBLE-CHECK-COST-01_REPORT.md`§0/§1。

### retry(MAJOR時の生成+再Check、翻訳origin相当のみ実施される経路)

| 事例 | GENコスト | CHECKコスト | 結果 |
|---|---|---|---|
| meta final advanced 1回目→retry | ¥1.8575→¥0.6569 | ¥0.5939(MAJOR)→¥0.6477(compliant) | 解消 |
| hormuz(diversity trial) advanced 1回目→retry | ¥0.6656→¥0.8296 | ¥1.0079(MAJOR)→¥1.5466(なおMAJOR) | **retry後もSTOP** |
| meta first-pass standard 1回目→retry | ¥1.1477→¥0.3119 | ¥1.2140(MAJOR)→¥1.1136(compliant) | 解消 |
| no_heading_segmentation meta v1→v2 must-fix retry | ¥0.3333(gen)+¥0.4809(check) | 合計¥0.8142 | 解消 |

出典: 同REPORT§1-2/§2、`er045_output/.../must_fix_retry_result.json`。

### NG(MAJOR)発生率(参考値、母数小さい)

- n=7(Family X production/diversity trial、Advanced/Standard 1回目コールのみ): MAJOR 3/7≈43%。
  うち2/3は1回retryでLEDGER_COMPLIANTに解消、1/3(hormuz diversity trial)はretry後もMAJORが
  残りSTOP。出典: 同REPORT§2。
- Family X E2E本番(`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`、Hormuz記事1本×run_01/run_02の
  2回試行): **2/2がAdvanced段でorigin=ja_source MAJORによりSTOP、Standard・Audio未着手**
  (完成0/2)。母数が記事1本・2 runのみのため一般化不可。出典:
  `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`L964-968。

### Human Review・attempt_historyへのCheckerの寄与

**未計測**(該当ログに含まれず)。`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`
(63行)・`er011_output/attempt_history.jsonl`(9,643行)を"deviation"/"ledger"でGrepしたが、
ヒットは全てTTS/ASR音声QA文脈(記事本文中の統計値"standard deviations"、themeディレクトリ名に
"ledger_trial"を含むだけ)であり、Ledger Deviation Checker/JA Fact Check起因のHuman Review
エスカレーションは1件も確認できなかった。

### Checker自体のモデルコスト・比較値

- Ledger Deviation Checker(Family X、web検索なし): 1回あたり中央値¥0.90(¥0.32〜¥1.65)。
- 参考: 別Checker「Fact Checker A'」(Editorial B-Family、web検索付き、Ledger Deviation Checker
  とは別コンポーネント)は1回¥20〜25、MAX_WRITER_ATTEMPTS=3ループで1記事Writer段合計¥74.49
  に達した実例あり(`LEDGER-DEVIATION-CHECKER-SEARCH-COST-RECONCILIATION-01_REPORT.md`§10)。
  Family XのLedger Deviation Checker自体はこれよりコスト的に軽い(web検索0回)。

### throughput・未完成記事率

- 1呼び出しあたりのlatencyは実測済み(上記中央値33秒)。「STOPまでの所要時間」の記事単位集計は
  ログに存在せず**未計測**。
- 未完成記事率: Family X E2E(Hormuz、上記)は2/2試行が未完成。他Family(diversity trial、
  concreteness trial等)はTrial扱いのため「未完成」の定義に当てはまらない(Trialは意図的に
  1回で測定終了するため)。

### アーキテクチャ上の重要な観測(修正提案ではなく事実の記録)

`NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01_REPORT.md`(既存REPORT、read-only調査)によれば、
現行retry機構は(a)1回目Checkerの指摘内容(`deviations`のclaim/issue/explanation)を2回目の
生成呼び出しへ一切渡さない「ゼロベース全文再生成」であり、(b) `origin="ja_source"`のMAJORは
そもそもretryの対象外でfail-closedに即STOPする設計。したがって、ja_source起因のMAJORは
(i)〜(iv)のどの区分であっても常に同じ扱い(即STOP・retry無し)を受けており、**問題の深刻度
(区分)とSTOP時の挙動が現状では連動していない**。これは既存仕様どおりの動作であり、本調査は
この設計自体の変更を提案しない(採用判断はユーザー)。

## 新たに見つかった重大問題(修正せず報告)

1. A-1(Metaのロールバック時制ドリフト)は、2回のCheckerコールいずれも見逃し、最終的に
   人手の直接テキスト修正でしか是正できなかった。Checkerの`changed_time`/`changed_certainty`
   フラグの定義文が「動詞の時制(完了/未来)」を明示的にカバーしておらず、判定者(LLM)ごとに
   解釈が割れる余地があるという既存REPORTの指摘(§9-B)を本調査でも確認した。
2. B-1(原油価格→ガソリン価格)のclaimは、独立した4つのrun/trialで繰り返し同様の判定を受けて
   おり、偶発的なブレではなく構造的パターンである可能性が高い。
3. origin=ja_source MAJORはretry機構の対象外という設計により、A/B分類上「過剰品質の可能性が
   高い」候補(B-1、B-2本件)も「絶対にSTOPすべき」候補(A-2〜A-5相当)も、現状は全く同じ
   fail-closed即STOPという扱いを受けている。

## Part Aとの関係

本ファイルはPart B(過去STOP事例・厳しさの分類・QCD影響の実測)のみを扱う。現行仕様の
hard/soft基準整理およびHormuz trace(現行仕様がどのコードパスをどう通ったかの逐語追跡)は
**Part A(別委任、出力先`docs/pm/investigation_ledger_deviation_check_01_part_a.md`)** の
範囲であり、両者の統合は別委任で行う。
