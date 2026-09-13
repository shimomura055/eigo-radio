## 管理ID
EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04

## 範囲
性質: ¥0構造診断→仕様再設計→(必要なら)同一テーマ・同一Ledgerの最小再Trial。到達上限`VALIDATED`(REJECTED/VALIDATED/USER_DECISION_REQUIRED、判定語はFableが確定)。**別テーマTrial禁止。Production配線・CURRENT_SPEC正式化・APPROVED変更禁止。** 既存Production経路・Discovery成果物(`FAMILY-A-DISCOVERY-*`、`er011_*`)・SSOT本文・既存`er013_*_01/_02/_03`は無編集(新規`_04`のみ)。**Git操作は行わない**(別途Fableが統合)。費用: Family C残額¥125.54内(実行前見積、超過見込みは生成せず報告)。Sonnet往復1回で完結。

## 固定ブロック
---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0: 本委任文を`docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04.md`へ保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04.md" --json-out "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04_check.json"`を実行し結果をRESULT_PACKETへ1行記録(FAILでも継続)。
---

## ユーザー指示(原文、REPORT冒頭に転記)
> 前回のFable推奨「別テーマでもう1本Trial」は採用しません。次の記事・次テーマには進まないでください。理由は、今回の550語/744語という長さが、単なる軽微な超過ではなく、Family C仕様そのものが文章を膨らませている可能性を疑うべき水準だからです。したがって、まず同一テーマ・同一記事で長文化原因を是正してください。重要なのは、単にWriter Promptへ「もっと短く」と追記することではありません。まず費用ゼロで、なぜFamily Cが長くなるのかを構造的に診断してください。最低限、以下を確認してください。時点数が多すぎないか/各時点ごとに場面描写を要求しすぎていないか/各場面で「出来事+感情+選択+希望+不安」をすべて要求する構造になっていないか/World Scaffoldから受け取る情報量が多すぎないか/3層構造・framing要求が本文へ説明負荷を持ち込んでいないか/想像と事実を区別するための指示が、冗長な文章を誘発していないか/締めやtransitionの要求が重複していないか/A2・B1それぞれの標準分量と、現在のFamily C Writer contractが構造的に矛盾していないか/「感情強度2」「研究解説感0」を達成するために不要な描写まで増えていないか。そのうえで、必要なら以下まで含めて仕様を再設計してください。時点数の削減/各時点の役割の整理/場面数上限/paragraph・scene budget/1場面あたりの情報量上限/A2・B1別の明確なlength budget/必須要素と任意要素の切り分け/同じ意味の感情・希望・不安表現の重複禁止/Writerへの入力情報量の削減。目標は、研究・データ解説感0+Fact Safety維持+感情強度維持+Futureらしい没入感維持+A2/B1の標準分量内です。「少し長いが許容」とする前提では進めません。特に今回のような大幅超過を次テーマへ持ち越すのは禁止です。まず診断を行い、仕様原因を特定してください。その後、同一Ledger・同一テーマで最小再Trialが必要なら、Family C残額内で実施して構いません。ただし、別テーマTrialには進まないでください。Trial終了時はREJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれかに分類してください。Family CもまだProduction採用承認ではありません。

## 事前指定Read一覧
- `er013_family_c_future_writer_03.py`(全文、1回。Prompt contract全体の構造診断用)
- `er013_output/family_c_future_trial_03/a2/reader_facing_article.txt`と`b1/`相当の読者向け本文(各1回)、同ディレクトリの内部版(マーカー付き、各1回)
- `er013_output/family_c_future_trial_02/research/world_scaffold_result.json`(Writer入力量の実測用、1回)

## 事前指定Grep一覧+更新位置の手順
1. `er013_family_c_future_writer_02.py`: Grep `-n` `時点|scene|場面|emotion|感情|hope|fear|transition|締め|word|語|IMAGINED|META|FACT` で要求項目の行を列挙(全文Readは不要、`_03`との差分把握のみ)。
2. `er013_family_c_future_scaffold_02.py`: Grep `-n` `def |max|limit|件|items`(Scaffold件数・上限の有無)。
3. `er013_family_c_future_qa_03.py`: Grep `-n` `def |target_range|threshold|hedge|word_count`(現在の閾値)。
4. `CURRENT_SPEC.md`: Grep `-n` `A2.*(語|words)|B1.*(語|words)|word_count|標準分量`(A-FamilyのA2/B1標準分量の正式値と根拠行)。
SSOT全文読込禁止。

## 作業A(¥0): 構造診断
1. **要求要素の棚卸し**: `_03` Writer promptが要求している要素を「時点数」「場面ごとの必須要素(出来事/感情/選択/希望/不安/台詞)」「枠外の一般示唆」「transition」「締め」「FACT例外」「META」ごとに列挙し、それぞれが最小で何文・何語を誘発するかを実記事(Trial-03 A2/B1)の段落と対応づけて実測(段落別語数表: 場面段落/反応段落/枠外示唆/締め)。
2. **原因の特定**: (a)時点数×場面必須要素の積(例: 3時点×[出来事+感情+選択+希望+不安]=15要素)が標準分量と構造的に矛盾するか、(b)World Scaffold 25件が「全部使う」圧力になっていないか(記事内で参照されたScaffold件数を実測)、(c)3層・framing指示(枠の入口宣言・枠外示唆・境界文)が各時点に定型文を生んでいないか、(d)「希望」「不安」の対比を各時点+締めで重複要求していないか、(e)A2/B1標準分量(CURRENT_SPEC値)とcontractの矛盾、を根拠(段落引用+語数)付きで判定。
3. **仕様再設計案(Family C v4 Writer contract)**: 時点数の削減(既定2、テーマ依存で1〜3)/各時点の役割整理(例: 時点1=変化の始まりと期待、時点2=定着後の葛藤)/場面数上限と1場面あたりの語数budget/paragraph budget(A2: 場面2×最大N語+示唆1段落+締め1文=標準分量内、B1同様)/必須要素(場面・出来事・1つの感情・1つの選択)と任意要素(台詞・第2の感情・別の未来)の切り分け/同義の感情・希望・不安表現の重複禁止(希望・不安の対比は記事全体で1回)/Writer入力のScaffoldを「本テーマで使う上位N件」に絞る(Scaffold選択はLLM 1回または規則)/A2・B1別のlength budgetを契約として明示し、編集Gateの語数閾値と一致させる。代替案(例: 時点1のみ+別未来の分岐で対比)も併記しQCD比較。
4. offline検証(¥0): 新契約でのprompt構築snapshot、編集Gate閾値の整合テスト、既存テスト(`_02` 24件/`_03` 21件)無変更PASS、A/B-Family回帰(`--pattern "er013*"`→default全件1回、`.venv\Scripts\python.exe`使用)。

## 作業B: 最小再Trial(同一テーマ・同一Ledger・World Scaffold再利用、必要な場合のみ)
- 新規`er013_family_c_future_writer_04.py`/`qa_04`(必要分のみ)/`trial_04_run.py`。A2/B1各1本(+再生成余裕1回)。見積(前回¥13.55)を記録、残額¥125.54内。
- 評価(Trial-03との前後比較、引用必須): 語数(A2/B1、標準分量内か)、時点数・場面数・段落数、研究解説スキャン(0維持)、Framing QA v2(PASS)、枠外未来断定/枠内現在事実捏造(0)、Fact Checker A'(Layer 1)/Ledger Deviation、感情強度(0〜2主観、台詞/行動引用)、没入感(0〜2主観、引用)、枠内hedge密度。比較artifact `er013_output/family_c_future_trial_04/comparison.md`+`index.html`(Trial-03と並置)。
- 分量内に収まらない場合は「まだ残る構造問題」として原因を特定し、追加の仕様変更案を提示してSTOP(別テーマへは進まない)。

## 実行コマンド全文
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er013*"`
- `.venv\Scripts\python.exe run_project_regression.py`
- `git status --porcelain`(参照のみ、Git操作なし)

## SSOT追記文
- 編集しない(REPORT末尾に追記文案のみ)。

## Git
- 本タスクではGit操作を行わない。

## 報告
- `EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04_REPORT.md`(root): 何が長文化を生んでいたか(根拠・語数表)/どの仕様を変えたか(前後の契約差分)/変更前後の語数/研究解説感0の維持/感情強度の維持/Fact Safetyの維持/まだ残る構造問題/実費(API別+5区分)/Gate 1判定材料/ユーザー判断事項/SSOT追記文案。
- `docs/pm/RESULT_PACKET_FC4.md`(30行以内)+T-0検証結果1行。最終メッセージ10行以内。
