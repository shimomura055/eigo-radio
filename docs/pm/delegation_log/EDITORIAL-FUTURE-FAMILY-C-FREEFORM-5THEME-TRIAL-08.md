## 管理ID

EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08
並行タスク衝突確認: 並行タスクなし。本タスクは**er013_*とer013_output/のみ**を扱い、SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`・Git操作(add/commit/push)を**一切行わない**。RESULT_PACKETは`docs/pm/RESULT_PACKET_FC8.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(自由生成・5テーマ)。**最大Status: VALIDATED**(Production採用禁止)。終了時はREJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれか。
- 仮説(ユーザー): 「Future記事は、スケールや型を事前指定せず、Core Provocation/Storyを自由に作らせた方が面白い可能性が高い」。Trial-07のユーザー人間評価: 「どれも悪くないが、指定すると少し凝った形になり、面白みや分かりやすさが薄れる」。
- **今回のHard方針は2つだけ**: (1)Reader-facing本文にCurrent fact/現在統計/研究結果/販売台数等を**入れない**(CURRENT FACT 0件が正常状態。"In 2023, more than 2.1 million…"はNG。Research/Ledger/Evidenceは裏側のSafety boundaryのみ)。(2)登場人物は基本1〜2人、最大3人。主人公に名前は可、それ以外は固有名を増やさず関係性(her mother/his father/her friend/their daughter等)で表す。全員に名前を付けない。
- **Writerへ与えない指定**(禁止): Intimate/Societal/Radicalの指定、見出し数固定、感情変化数、選択数、場面数、出来事数、ストーリー型、結論型、感情順序(期待→不安等)。Writerの目的は「このテーマで、読者が未来を感じ、続きを読みたくなり、わくわく・ドキドキするストーリーを書く」。
- リスニング適性は**編集目標**(Hard Gateにしない): 登場人物過多/人名過多/時系列ジャンプ過多/制度説明の連続/抽象概念の連打/一文が長すぎる/「今誰の話か」を見失う構造、を避ける。
- **新Gate・Validator禁止**: Plausibility Pass、構造Gate、人物関係Validator、感情アークValidator等を追加しない(必要性を感じてもOpen Item候補として報告のみ)。制約数はv6/v7(5項目)より増やさない(Hard方針2つは既存項目の文言更新+人物数1項目の追加まで許容し、合計制約項目数を数えて記録。目安: 6項目以下)。
- Core Provocation: 各テーマで**1〜3個の中心アイデアを短く考え、最も面白いものを選ぶ**程度(LLM 1呼び出し)。Trial-07のようなスケール別大量候補+強制ランキングは行わない。
- 対象テーマ(各1本、A2相当、約350語、300〜420語許容): 1. Home robots / 2. BCI (Brain-computer interfaces) / 3. The future of memory / 4. Digital twins of ourselves / 5. The future of language。Home robots/BCIは再生成(前回良かった面白さを維持しつつCurrent factだけ消す。前回記事の文章コピー禁止、新たに自由生成。Home robotsで「AIが現在より不自然に知能低下する展開」は望ましくないがルール追加はしない。不自然さが出ればそのまま記録)。
- Fact Safety 3層(CURRENT FACT/PLAUSIBILITY BRIDGE/IMAGINED FUTURE)は裏側で従来どおり実施。**CURRENT FACT 0件のときFact Checker A'の形式実行をTrial限定でskip**してよい(`er013_family_c_future_safety_06.py`の`run_current_fact_layer`を無編集のまま、Trial-08 run側でfact_blocksが空なら呼び出しをskipし`{"skipped": true, "reason": "CURRENT FACT 0件(Trial-08限定skip)"}`を記録。Production仕様変更なし)。Layer1 Ledger Deviationは既存どおり0件skip。新テーマ3本(memory/digital twins/language)にはLedgerが無いが、CURRENT FACT 0件方針のためLedger作成は不要(PLAUSIBILITY BRIDGE/IMAGINED FUTUREの軽判定のみ実施)。
- Story Spark評価(補助のみ、PASS/FAILで破棄しない): 各記事にFuture Leap/面白さ/わくわく・ドキドキ/分かりやすさ/リスニング適性/読後の問い の6軸を短く(0〜3+一言)。`spark_gate_06`をそのまま流用してもよいが、分かりやすさ・リスニング適性の2軸を追加した軽いLLM評価1回で足りるなら新規`_08`評価関数として実装(既存ファイル無編集)。
- 費用: Family C残額**¥137.71**(ハード上限)。想定: 5記事×(中心アイデア1回+Writer1回+補助評価1回+Safety軽判定)≈¥3〜6/記事、合計¥20〜35。**大量再生成禁止**(各テーマWriter呼び出しは原則1回。マーカー崩れ等の技術的retryのみ最大1回)。
- 禁止: 既存`er013_family_c_future_*_01〜07.py`の編集(新規`_08`系のみ。import再利用可)/`er013_output/family_c_future_trial_01〜07*/`の改変/SSOT・Git/er003_*・er011_*・er012_*・er014_*編集/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: 費用上限/routing契約違反が避けられない場合。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> 今回の仮説は: Future記事は、スケールや型を事前指定せず、Core Provocation / Storyを自由に作らせた方が面白い可能性が高い。したがって今回は、Intimate / Societal / Radical等の分類をWriterへ与えない。それらは必要なら事後分析用のラベルとしてのみ使う。
> 対象テーマ: 1. Home robots 2. BCI / Brain-computer interfaces 3. The future of memory 4. Digital twins of ourselves 5. The future of language
> 最重要方針: 今回のWriterは、低制約・自由生成を維持する。以下のような指定はしない: Intimate / Societal / Radicalの指定/見出し数固定/感情変化数/選択数/場面数/出来事数/ストーリー型/結論型/期待→不安などの感情順序。目的は: 「このテーマで、読者が未来を感じ、続きを読みたくなり、わくわく・ドキドキするストーリーを書く」こと。
> Reader-facing CURRENT FACTは禁止。CURRENT FACT 0件を正常状態とする。
> 登場人物数の制限: 登場人物は基本1〜2人、多くても3人まで。主人公に名前を付けるのは可。それ以外の人物は、可能な限り固有名を増やさず、主人公との関係性で表現する。不要な人名追加は禁止。
> Home robots / BCIについて: この2テーマは再生成。基本的には前回良かったOutputの面白さを維持しつつ、Current factだけ消えること。ただし前回記事の文章をコピーしない。Plausibility Pass等の追加Gateは今回は実装しない。
> Core Provocation: 各テーマについて、記事を書く前に1〜3個程度の有望な中心アイデアを短く考え、その中から最も面白いものを選ぶ程度にとどめる。
> 目標記事: A2相当。約350語。目安として300〜420語程度は許容。語数より、面白い/分かりやすい/リスニングで追える/未来を感じる/読後に何か残る、を優先。
> リスニング適性: 読むと面白いだけでなく、耳で聞いて追えること。ただし新たなHard Gateにはしない。Writerの編集目標として扱う。
> Fact Safety: 裏側では従来どおり確認。CURRENT FACT 0件なら、不要なFact Checker A'形式実行でコストを浪費しない設計が可能か確認。もし既存Trialコード上、skipが安全に可能なら、Trial限定でskip可。Production仕様変更はしない。
> Story Spark評価: LLM評価は補助のみ。最終判断はユーザー人間評価。Gate PASS/FAILで記事を破棄しない。
> 比較ページ: 5記事を1ページで読み比べられるArtifact。各テーマについて: Title/Article全文/word count/登場人物数/Core Provocation 1行 だけ簡潔に掲載。
> 費用: 開発・Trial費/量産時1記事単価(未確定なら明記)。Family C残予算: ¥137.71。大量再生成は禁止。
> 今回の最重要原則: 型で面白くしようとしない。面白い未来を自由に書かせ、読みやすさを壊す明確な要因だけ最小限に抑える。

## 事前指定Read一覧

1. `er013_family_c_future_writer_07.py` 全文(v7低制約契約の派生元。CURRENT FACT任意→禁止、人物数方針の追加、スケール関連の記述があれば削除)。
2. `er013_family_c_future_provocation_07.py`: Grep `^def |def _call|client|model` → LLM呼び出しの流儀(routing・logging_context)の該当範囲のみRead(1〜3案の軽い中心アイデア生成に縮約した`_08`版を作る)。
3. `er013_family_c_future_trial_07_run.py` 全文(run骨格・費用集計・比較HTML生成の再利用元)。
4. `er013_family_c_future_safety_06.py`: Grep `^def |fact_blocks|skipped` → 3層の関数一覧とCURRENT FACT 0件時の挙動のみRead(Trial-08 run側でのskip実装のため)。
5. `er013_family_c_future_spark_gate_06.py`: Grep `^def |AXES|axes` → 関数・軸定義のみRead(補助評価の流用可否判断)。
6. `er013_output/family_c_future_trial_07/index.html`: Grep `<table|<h2|<h3` → 構造のみ(比較ページの簡素化版を作るため。技術QAは載せない)。
7. `docs/pm/PM_GOVERNANCE.md`: Grep `15-5|5区分` → 費用報告5区分の定義範囲のみRead。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 新規ファイル: `er013_family_c_future_writer_08.py`(契約: Future/Current区別マーカーは維持しつつCURRENT FACT本文禁止、A2・約350語、研究解説に戻さない、人物1〜2人最大3人・関係性表現、リスニング適性は編集目標として1段落、面白さ最優先。制約項目数を数えて記録)、`er013_family_c_future_provocation_08.py`(テーマごとに中心アイデア1〜3案+選定理由、1呼び出し)、`er013_family_c_future_eval_08.py`(補助評価6軸、1呼び出し。人物数・固有名数は決定的に数える: 大文字始まりの人名候補を抽出し人物数を推定、手動確認値も併記)、`er013_family_c_future_trial_08_run.py`(フロー: 中心アイデア→Writer(技術retry最大1)→Safety 3層[CURRENT FACT 0件ならA' skip]→補助評価→比較ページ。テーマ5件を順に。総額ガード¥137.71、目安¥35で警告)。テスト`er013_family_c_future_qa_test_08.py`(決定的部分: 人物数カウント・CURRENT FACTマーカー0件判定・制約項目数、API不要)。
- 出力: `er013_output/family_c_future_trial_08/{home_robots,bci,memory,digital_twins,language}/`(`core_idea.json`、`reader_facing_article.txt`、`safety_result.json`、`eval_result.json`、`word_count.json`)、`cost_summary.json`、`raw_usage_log.jsonl`、`comparison.md`、`index.html`(各テーマ: Title/本文全文/word count/登場人物数/Core Provocation 1行のみ。技術QAは載せない。末尾にTrial-07 home robots・BCI記事へのリンクのみ)。
- `docs/pm/RESULT_PACKET_FC8.md`は新規作成。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08.md --json-out docs\pm\delegation_log\EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08_check.json`
2. offline検証(生成前): `.venv\Scripts\python.exe run_project_regression.py --pattern "er013*_test_*.py"`(期待: 既存102+新規全PASS)
3. 生成: `.venv\Scripts\python.exe er013_family_c_future_trial_08_run.py --themes home_robots,bci,memory,digital_twins,language --level a2 --budget-jpy 137.71`
4. 費用確認: `cost_summary.json`合計がハード上限内であること。
(3のCLIフラグと総額ガードは本タスクで実装。)

## SSOT追記文

本タスクではSSOTを編集しない。root REPORT `EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08_REPORT.md`末尾に「SSOT追記文案(編集は行っていない)」節として、OPEN-147末尾追記案(Trial-07人間評価の記録、Trial-08結果・分類・開発・Trial費・量産単価[未確定なら明記]・残額)とDECISION_LOG新エントリ案を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない(Fableが後続CONSOLIDATIONで明示addする)。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FC8.md`に、ユーザー必須15項目を同じ番号で: 1) 5テーマのCore Provocation(各1行+候補1〜3案)/2) 5記事全文の相対パス(本文はREPORTに全文転記)/3) word count/4) 登場人物数(名前付き人数・関係性表現の人数、決定的カウント+手動確認)/5) Current fact混入0件確認(マーカー0件+数値・研究語・製品名の決定的grep結果)/6) リスニング適性所見(一文平均語数・人物切替回数・抽象語密度など簡易指標+一言)/7) Future Leap(補助評価)/8) 面白さ(補助評価)/9) Home robots・BCIの前回(Trial-07)比較(面白さ維持・Current fact消失・人物数・不自然さの有無)/10) 新テーマ3本(memory/digital twins/language)への一般化結果/11) 開発・Trial費(API別+5区分、テーマ別)/12) 量産時1記事単価(未確定なら「未確定」+参考値)/13) 残る問題(不自然さ・Home robotsのAI知能低下展開の有無等はそのまま記録)/14) Gate 1判定材料/15) ユーザー判断事項。加えて: 分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)、制約項目数(v7=5との比較)、A' skipの実施有無と節約額、Family C残額、Artifact相対パス(index.html)、commit対象候補一覧、T-0結果、事前指定外Read(理由付き)、STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり(新規ファイル・出力dir・比較ページ構成)
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥137.71ハード上限、目安¥35)
- [x] 並行タスク衝突回避あり(並行なし・Git操作なし)
