## 管理ID

EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06
並行タスク衝突確認: 並行してFAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01(er003_*/er011_output/SSOT/docs/pm/ACTIVE_TASK.md/Git)が走る。本タスクは**er013_*とer013_output/のみ**を扱い、SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`・Git操作(add/commit/push)を**一切行わない**。RESULT_PACKETは`docs/pm/RESULT_PACKET_FC6.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 再設計Trial。**最大Status: VALIDATED**(Production採用禁止)。終了時はREJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれか。
- 出発点(ユーザー人間評価): 現行v5(Trial-05)はQA全PASSだが、ユーザーが読んだ結果「NG。論外」。理由: 「未来」と言いつつ冒頭場面が現在すでに一部地域で起きている(Future Leapが弱い)/わくわく・ドキドキがない/人間が読んで面白くない。一方、制約を外した自由生成記事(中心発想: Home Robot「ロボットが怖いのは暴走ではなく、便利すぎて人間が人生の選択を少しずつ渡してしまうこと」/BMI「脳と機械がつながる未来では思考のプライバシーが新しい問題になる」)をユーザーは「めちゃくちゃ面白い」と高評価。この差が再設計の出発点。
- 最重要原則: QAが全部PASSでも、読んで面白くなければFAIL。「Interesting first, safe by design」(面白さを最初に作り、最後まで保護する)。
- 新原則の生成フロー: Provocative Future Premise → Core Provocation → Story → Evidence / Safety Boundary Check。Research/Evidenceは未来像を作る主役ではなく「想像の境界を確認するガードレール」。Fact Safetyは維持。
- テーマ: The future of home robots(まずこれのみ)。現行Trial-05のScene/Scaffold(er013_output/family_c_future_trial_02〜05/research/world_scaffold*・Layer2/3出力)はそのまま再利用しない。上記自由生成の「思想」は参考にしてよいが文章コピー禁止。狙い: 現在にはないFuture Leap/便利さ/少し怖い転換/価値観を揺らす問い。
- レベル: まずA2相当、約350語目標。評価優先順位: 1面白い 2未来を感じる 3わくわく・ドキドキ 4読後に問いが残る 5Fact Safety。語数・構造はその下。
- BMI一般化Trial(The future of brain-computer interfaces)はロボット記事で新設計が成立した(Story Spark Gate PASS+Fact Safety PASS)場合のみ簡易実施可。ロボットで弱い場合はBMIへ進まず、先に原因分析→最小改善Trial。
- 費用: Family C Trial残額¥182.13内(ハード上限)。配分目安: ロボット(候補生成+本生成+Spark Gate+Safety+最小改善Trial1回まで)≤¥90、BMI簡易Trial≤¥60(新規CURRENT FACT収集を含む)、予備。費用は開発・Trial費と量産時1記事あたり単価(未確定なら「量産単価: 未確定」)に分離して報告。
- 禁止: 既存er013_family_c_future_*_01〜05.pyの編集(新規_06系ファイル。既存モジュールのimport再利用可)/er013_output/family_c_future_trial_01〜05/の改変/Fact Checker A'の判定緩和(先に緩めない、位置づけ再設計案を出すのみ)/SSOT・Git/er003_*・er011_*・er010_*・er012_*の編集/Production採用宣言/run_project_regression.py --patternに_testを含まないglob。
- 失敗時(1回弱い記事が出ても「失敗」で終了しない): 原因を「Core Provocation弱い/Future Leap不足/Evidenceに引っ張られた/Writerで弱まった/QAで削られた/3 Voicesで希釈/Prompt制約過多」に分解し、予算内で有望な最小改善Trial(1回)まで実施。それでも弱ければUSER_DECISION_REQUIRED。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は--porcelain/--stat/--short等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01/PM-CLOSEOUT-CONSOLIDATION-117、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文をdocs/pm/delegation_log/<管理ID>.mdへ保存し、python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.jsonを実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> 新原則: Provocative Future Premise → Core Provocation → Story → Evidence / Safety Boundary Check。Research / Evidenceは、未来像を作る主役ではなく、想像の境界を確認するガードレールとして使う。Fact Safetyは維持する。
> Core Provocation定義: 読者が「え、それが本当に起きたらどうなる?」と思う、記事全体を貫く最も強い中心問い。Main Story / Scene / Voice / Conclusionは、全部このCore Provocationを強くするために存在する。
> Story Spark Gateを最上位に置く(Fact / Ledger / Framing / Word Countより上位)。最低評価軸: Future Leap(現在でも普通に起きる話ではないか)/Curiosity(続きを読みたいか)/Emotional Pull(わくわく・ドキドキ・不安・驚きがあるか)/Thought-provokingness(読後に考えたくなる問いが残るか)/Core Provocation clarity(「この記事の何が面白いか」を1文で説明できるか)。このGateに落ちる記事は、Fact Safety PASSでも記事としてFAILとする。
> 3 Voicesは即廃止しない。ただし「3つの違う話に分散」ではなく、同じCore Provocationを3方向から強める構造にする。Voice diversificationより、Core Provocation preservationを優先。3 Voicesによって面白さが薄まるなら、その設計は失敗と判断する。
> Prompt制約方針: 現行v5のような見出し3固定/感情変化1/選択1/出来事数/場面順固定/hedging細則などを積み上げることを中心解法にしない。最初は制約を減らす。最低限: Future / Current Factの区別、Fact Safety、語数、英語レベル、Research解説記事に戻さない、程度。Writerの第一目的を、Core Provocationを最も面白く読者に体験させること、とする。
> Core Provocation候補生成: 記事生成前に、5〜10程度のCore Provocation候補を作る。評価: Future Leap/excitement/tension/thought-provokingness/現在実現済みとの距離/Evidenceとの接続可能性。最も面白く、かつSafety boundary内に置けるものを選ぶ。一番安全な案を選ぶのではない。
> Fact Safetyレイヤー: CURRENT FACT(厳密にFact Check)/PLAUSIBILITY BRIDGE(現在技術から未来像への接続が完全飛躍していないか確認)/IMAGINED FUTURE(予測精度をFact Checkしない。確認するのは、現在事実のように誤記していないか、架空未来と明確に分かるか、のみ)。
> Fact Checker A': 前回のFuture A' REVIEW_REQUIRED問題は、今回の再設計後に位置づけ直す。先にA'を緩めない。新3レイヤーに対し、A'をどこへ使うか/Ledgerをどこへ使うか/Framing QAをどこへ使うか、を再設計案として出す。
> 最終報告必須(Future): 1現行Family Cで面白さが落ちた根本原因 2新生成フロー 3Core Provocation候補 4選定理由 5新記事全文 6現行Trial-05との比較 7Story Spark Gate 8Fact Safety 9Evidenceの使い方 10 3 Voicesの扱い 11制約数増減 12開発・Trial費 13量産時1記事単価 14残る問題 15Gate 1判定 16ユーザー判断事項。記事は必ずユーザーが直接読めるリンクを付けること。

## 事前指定Read一覧

1. er013_output/family_c_future_trial_05/a2/reader_facing_article.txt 全文(「論外」評価の対象。比較基準・反面教師)。
2. EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05_REPORT.md L112-135(制約密度表、v6で制約数増減を比較するため)。
3. er013_output/family_c_future_trial_01/research/layer1_only_ledger.txt 全文(CURRENT FACTの既存検証済み材料。ガードレールとして再利用可。Scaffold/Sceneは再利用禁止)。
4. er013_family_c_future_trial_05_run.py L40-65(費用集計・pricing・logging_contextの流儀)、L91-160(コスト計算関数群、v6 runで再利用)、L290-320(Fact Checker A'呼び出し方、r3.build_fact_check_prompt/run_fact_checker_with_gatesのシグネチャ確認用)。
5. er013_family_c_future_writer_02.py: Grep IMAGINED_OPEN_TEMPLATE|IMAGINED_CLOSE|META_OPEN|FACT_OPEN_TEMPLATE → マーカー定義範囲のみRead(v6でもFuture/Current Factの区別マーカーは最低限維持)。
6. er013_family_c_future_qa_03.py: Grep ^def → 関数一覧のみ(既存Framing QA v2・編集Gateの再利用可否判断用。必要な関数のみ定義範囲Read)。
7. docs/pm/PM_GOVERNANCE.md: Grep 15-5|5区分 → 費用報告5区分の定義範囲のみRead。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 新規ファイル(既存編集なし): er013_family_c_future_provocation_06.py(Core Provocation候補生成+評価+選定。LLM 1〜2呼び出し、候補5〜10、6軸スコア表、選定理由)、er013_family_c_future_writer_06.py(制約最小のWriter契約: Core Provocation/Future-Current区別マーカー/Fact Safety/約350語/A2英語レベル/研究解説に戻さない、の5点のみ。制約項目数を数えて記録)、er013_family_c_future_spark_gate_06.py(Story Spark Gate: LLM判定で5軸各0〜3+総合PASS/FAIL+「この記事の何が面白いか」1文+根拠引用。PASS基準: 5軸すべて2以上かつFuture Leap≥2。Fact/Ledger/Framing/語数より先に実行し、FAILなら他QAを実行する前に原因分類→再生成)、er013_family_c_future_safety_06.py(3レイヤー分離: CURRENT FACT文をFact Checker A'へ[既存関数をそのまま使用、緩和なし]+Layer1 Ledger Deviation、PLAUSIBILITY BRIDGE文はLLM判定「完全飛躍でないか」のみ、IMAGINED FUTURE文は「現在事実のように誤記していないか/架空未来と明確に分かるか」の2点のみ決定的+LLM軽判定)、er013_family_c_future_trial_06_run.py(フロー: provocation→writer→spark gate→safety→(必要なら3 Voices構造化)→比較HTML)。テストはer013_family_c_future_qa_test_06.py(決定的部分のみ、API不要)。
- 出力: er013_output/family_c_future_trial_06/(provocation/candidates.json+selected.md、a2/reader_facing_article.txt、a2/spark_gate_result.json、a2/safety_result.json、cost_summary.json、raw_usage_log.jsonl、comparison.md[Trial-05 A2との並記比較]、index.html)。最小改善Trialはer013_output/family_c_future_trial_06b/、BMIはer013_output/family_c_future_trial_06_bmi/。
- 3 Voicesの扱い: 記事はナレーター1人のまま、Core Provocationを「3方向(例: 便利さの魅力/静かな転換/価値観を揺らす問い)」から強める構造をWriterへ目標として示す(固定構造の強制はしない)。生成後、3方向が同じCore Provocationを強めているか/薄めていないかをSpark Gateの補助項目として判定し、薄めていれば「3 Voices希釈」と分類して報告。
- Fact Checker A'再設計案: 実装はA'そのまま。REPORTに「新3レイヤーに対するA'/Ledger/Framing QAの配置案」(表)を出す。Trial-06ではCURRENT FACT文のみA'へ渡し、verdictをそのまま記録(REVIEW_REQUIREDでも緩和せず、指摘内容がCURRENT FACTに対するものか、IMAGINED側の誤混入かを分類)。
- BMI簡易Trial(条件成立時のみ): CURRENT FACT材料は既存Ledgerが無いため、Fact Checker A'のweb検索付き検証を「CURRENT FACT文の事後検証」として使い、事前Researchは最小(LLM 1呼び出しでCURRENT FACT候補5件程度→A'で検証)に留める。費用≤¥60。
- docs/pm/RESULT_PACKET_FC6.mdは新規作成。

## 実行コマンド全文

(すべて C:\Users\tensh\eigo-radio で実行)
1. T-0: .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06.md --json-out docs\pm\delegation_log\EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06_check.json
2. offline検証(生成前): .venv\Scripts\python.exe run_project_regression.py --pattern "er013*_test_*.py"(期待: 既存74+新規全PASS)
3. ロボット本Trial: .venv\Scripts\python.exe er013_family_c_future_trial_06_run.py --theme home_robots --level a2 --budget-jpy 90
4. 最小改善Trial(Spark Gate FAIL時のみ): .venv\Scripts\python.exe er013_family_c_future_trial_06_run.py --theme home_robots --level a2 --budget-jpy 40 --variant 06b --improvement "<原因分類に対応する1変更を明記>"
5. BMI簡易Trial(ロボット成立時のみ): .venv\Scripts\python.exe er013_family_c_future_trial_06_run.py --theme bci --level a2 --budget-jpy 60 --variant 06_bmi
6. 費用集計: 各出力dirのcost_summary.json合計がハード上限¥182.13以内であることを確認。
(3〜5のCLIフラグは本タスクで実装すること。総額ガードを実装し超過前に停止。)

## SSOT追記文

本タスクではSSOTを編集しない。root REPORT EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06_REPORT.md末尾に「SSOT追記文案(編集は行っていない)」節として、OPEN-147末尾追記案(ユーザー人間評価「v5 NG」の記録、v6結果、分類、開発・Trial費、量産単価[未確定なら明記]、残額)とDECISION_LOG新エントリ案を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない(並行タスクとのindex衝突回避。Fableが後続CONSOLIDATIONで明示addする)。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

docs/pm/RESULT_PACKET_FC6.mdに、ユーザー必須16項目を同じ番号で: 1現行Family Cで面白さが落ちた根本原因(Trial-05本文の具体引用で示す)/2新生成フロー/3Core Provocation候補(全候補+6軸スコア表)/4選定理由/5新記事全文の相対パス(本文はREPORTに全文転記)/6Trial-05との比較(Future Leap・面白さ・語数・QA)/7Story Spark Gate結果(5軸スコア+根拠引用+「何が面白いか」1文)/8Fact Safety(3レイヤー別結果、A' verdictと指摘の分類)/9Evidenceの使い方/10 3 Voicesの扱いと希釈判定/11制約数増減(v5=16→v6=実数)/12開発・Trial費(API別+5区分、Trial-06/06b/06_bmi別)/13量産時1記事単価(未確定なら「量産単価: 未確定」+理由)/14残る問題/15Gate 1判定材料/16ユーザー判断事項。加えて: 分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)、失敗時の原因分類と最小改善Trialの結果、BMI実施有無と結果、Family C残額、Artifact相対パス(index.html)、commit対象候補一覧、T-0結果、事前指定外Read(理由付き)、STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり(新規ファイル・出力dir命名)
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥182.13ハード上限、配分目安)
- [x] 並行タスク衝突回避あり(er013限定・SSOT/Git/ACTIVE_TASK不可)
