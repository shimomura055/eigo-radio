## 管理ID

EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07
並行タスク衝突確認: 並行してPM-CLOSEOUT-CONSOLIDATION-126(SSOT/docs/pm/ACTIVE_TASK.md/Git)が走る。本タスクは**er013_*とer013_output/のみ**を扱い、SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`・Git操作(add/commit/push)を**一切行わない**。RESULT_PACKETは`docs/pm/RESULT_PACKET_FC7.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(発想スケール比較)。**最大Status: VALIDATED**(Production採用禁止)。終了時はREJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれか。
- 目的: 「ルールを足して面白くする」のではなく、**Core Provocationを考える時点で同じテーマを異なるスケール・視点から探索すると、記事の面白さ・派手さ・没入感がどう変わるか**を比較する。「どのスケールが正しいか」を決めるTrialではない。
- ユーザー人間評価(v6): BCI=良い(1側面に絞ったStoryとして成立)、ただしFuture記事としてはもっと派手・大きな未来も期待/Robot=改善したがまだ「惜しい」/Core Provocationは面白いがStory具体化で現実性・魅力が弱くなることがある/**Reader-facing本文に現在統計を入れるのは明確にNG**。
- **CURRENT FACT契約の変更(必須)**: Reader-facing本文へCURRENT FACT文を最低1件入れる契約は**撤廃**、デフォルト**0件**。Research/Ledgerは裏側のSafety boundaryとしてのみ使用。現在事実を本文へ入れるのは「その事実自体が記事を明確に面白くする場合のみ」。Fact Safety証明目的の統計・研究説明(「In 2023, more than…」等)の本文挿入は**禁止**。Fact SafetyはQA側で守る。
- **Writer**: v6の低制約方針を維持(Future/Current区別・Fact Safety・約350語・A2英語レベル・研究解説に戻さない、の5項目程度)。新たな構造ルール・感情ルール・見出し固定・出来事数制約を**追加しない**。3本を同じ型に揃えず、各Provocationに合ったStoryを書かせる。
- **Plausibility Pass等の新後処理Gateは実装しない**(Human/AI behavior plausibility、不自然箇所の局所rewrite等)。不自然なStoryが出てもそのまま結果として記録し、勝手に修正工程を追加しない。
- Story Spark Gate(`er013_family_c_future_spark_gate_06.py`)は**補助評価**として実行・記録するのみ。Gate PASS/FAILで採用・破棄を決めない(FAILでも記事は残し比較ページに載せる)。
- Framing QA v2は、後段の決定的スキャンとして利用可能かを**設計上確認してよい**(REPORTに1節)が、今回の結果を左右する新Gateにしない(実行するなら参考記録のみ)。
- テーマ: 第一に **The future of home robots**。BCIは「home robotsのスケール比較完了後、予算に余裕があり比較上有益なら2〜3スケールの簡易比較」まで可、home robotsで十分な知見が得られたら無理に実施しない。
- 費用: Family C残額**¥160.97**(ハード上限)。大量生成禁止・最小比較。配分目安: home robots(候補生成+記事3本[+追加レンズ最大1本]+補助QA)≤¥60、BCI簡易比較≤¥40、予備。**開発・Trial費**と**量産時1記事単価**(未確定なら「未確定」)を分けて報告。
- 禁止: 既存`er013_family_c_future_*_01〜06.py`の編集(新規`_07`系。既存モジュールのimport再利用可)/`er013_output/family_c_future_trial_01〜06*/`の改変/Fact Checker A'の緩和/SSOT・Git/er003_*・er011_*・er010_*・er012_*の編集/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: 費用上限到達/routing契約(Approved Model)違反が避けられない場合。

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

> Core Provocationの探索: 同じテーマを使い、異なるスケール・視点でCore Provocation候補を作る。最低限、以下3種類は必ず比較する。A. Intimate Future: 一人・一家族の日常、感情、選択、関係性が変わる未来(例「ロボットが自分以上に自分の生活を理解するようになったら?」)。B. Societal Future: 仕事、教育、法律、住宅、家族制度、経済など、社会全体のルールが変わる未来(例「家庭用ロボットが当たり前になったとき、"家事をする能力"は生活能力として評価されなくなるのか?」)。C. Radical Future: 現在の生活概念や常識そのものが崩れる未来(例「人間が家を管理するのではなく、家そのものが自律的に人生を運営するようになったら?」)。
> 追加で並立評価する発想レンズ(Writerへの制約ではない): D. Second-order Future: その技術が完全に普通になった後に起きる、二次的・三次的変化(例「誰も家事を覚えなくなった20年後に何が起きるか」)。E. Inversion Future: 便利さ・メリットが十分に成功した結果、その成功そのものが新しい問題を生む未来(例: ロボットが人間を理解しすぎる結果、「本人の希望」より「本人に最適な選択」を優先し始める)。この2つは有望ならIntimate/Societal/Radicalと組み合わせてもよい(Intimate×Inversion、Societal×Second-order、Radical×Inversion等)。ただし組合せを網羅的に生成しない。
> Trial方法: まずhome robotsについて、各スケール/レンズからCore Provocation候補を複数生成する。従来のような絶対点の6軸採点は、今回は主手段にしない。前回、候補が16〜18点に集中して判別力がなかったため、相対比較・強制ランキングを主にする。最低限、候補ごとに短く: 何が未来なのか/何が面白いのか/何が読者を驚かせるのか/Storyにしたとき何が起きるか、を説明。その後、代表的な異なるスケールから記事を生成する。理想は同じhome robotテーマで、Intimate/Societal/Radicalの少なくとも3本。追加レンズに明らかに強い案があれば、最大1本追加可。大量生成は禁止。
> 評価: 今回はStory Spark Gateの機械精度を作り込むことを主目的にしない。ユーザー人間評価を最上位に置く。比較軸: Future Leap/面白さ/わくわく・ドキドキ/想像したことのない未来感/Storyとしての自然さ/読後に問いが残るか/現在の延長説明に落ちていないか。LLM評価は補助。Gate PASSだから採用、Gate FAILだから破棄、とはしない。
> Plausibility Pass: 今回は実装しない。
> Fact Safety: CURRENT FACT/PLAUSIBILITY BRIDGE/IMAGINED FUTUREの3層は維持。ただしReader-facing本文へのCURRENT FACT挿入は不要。Fact Safetyは裏側の検証。Reader-facing StoryをResearch説明に戻さない。
> 最重要: 「最初に考える未来の幅を広げることで、Writerに強い材料を渡す」。Writerは低制約のまま。まず、Core Provocationの質×Futureのスケールだけで、記事の面白さがどこまで変わるかを見る。

## 事前指定Read一覧

1. `er013_family_c_future_provocation_06.py` 全文(候補生成の派生元。構造変更のため全文可)。
2. `er013_family_c_future_writer_06.py` 全文(低制約Writer契約の派生元。CURRENT FACT必須要件の箇所を特定し、v7で撤廃する)。
3. `er013_family_c_future_safety_06.py`: Grep `^def ` → 関数一覧と、CURRENT FACT文0件時の挙動(skip/形式PASS)の該当範囲のみRead。
4. `er013_family_c_future_trial_06_run.py` 全文(run骨格・費用集計・CLIフラグ・比較HTML生成の再利用元)。
5. `er013_output/family_c_future_trial_06b/a2/reader_facing_article.txt`、`er013_output/family_c_future_trial_06/a2/reader_facing_article.txt`、`er013_output/family_c_future_trial_06_bmi/a2/reader_facing_article.txt`(各全文、比較ページのv6基準として並記するため)。
6. `EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06_REPORT.md` L127-142(v6選定理由の書式)とL421-443(残る問題、v7で再発したかを確認する対象)。
7. `docs/pm/PM_GOVERNANCE.md`: Grep `15-5|5区分` → 費用報告5区分の定義範囲のみRead。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 新規ファイル(既存編集なし): `er013_family_c_future_provocation_07.py`(スケール/レンズ別候補生成: A/B/C各3〜4件+D/E各1〜2件、各候補に「何が未来か/何が面白いか/何が読者を驚かせるか/Storyにしたとき何が起きるか」の4項目短文を必須。評価は**相対比較・強制ランキング**を主手段: LLMに全候補を一括で順位付けさせ(同順位禁止)、順位理由を短文で。v6の6軸絶対点は参考として残してもよいが選定根拠にしない。代表案選定: A/B/Cから各1件[各スケール内の最上位]+D/Eに明らかに強い案があれば最大1件)、`er013_family_c_future_writer_07.py`(v6契約からCURRENT FACT必須要件を撤廃。FACT文は「記事を明確に面白くする場合のみ任意」、統計・研究説明の挿入禁止を明記。それ以外の制約は増やさない。制約項目数を数えて記録)、`er013_family_c_future_trial_07_run.py`(フロー: 候補生成+ランキング→代表案ごとに記事生成→補助評価[Spark Gate 06をそのまま実行・記録のみ]→Fact Safety 3層[safety_06再利用、FACT文0件時はCURRENT FACT層skipを明示記録]→Framing QA v2決定的スキャン[参考記録のみ、任意]→比較ページ)。テストは`er013_family_c_future_qa_test_07.py`(決定的部分のみ、API不要)。
- 出力: `er013_output/family_c_future_trial_07/`(`provocation/candidates.json`+`ranking.md`、`home_robots/{intimate,societal,radical[,lens_extra]}/reader_facing_article.txt`+各`spark_gate_result.json`+`safety_result.json`、`bci/...`[実施時]、`cost_summary.json`、`raw_usage_log.jsonl`、`comparison.md`、`index.html`)。
- **比較ページ(`index.html`)必須構成**: (1)候補一覧表(スケール/レンズ・4項目短文・相対順位・順位理由)、(2)採用代表案とその理由、(3)記事全文を横並び/縦並びで(Intimate/Societal/Radical[+追加レンズ]、参考としてv6 06b/06/BCI本文もリンクまたは折りたたみで併記)、(4)各記事の語数・FACT文件数・Spark Gate補助スコア・Fact Safety結果、(5)ユーザー人間評価用の比較ポイント(7軸: Future Leap/面白さ/わくわく・ドキドキ/想像したことのない未来感/Storyとしての自然さ/読後に問いが残るか/現在の延長説明に落ちていないか)を各記事に対する空欄チェック表として提示(Sonnetの自己採点は別欄で「補助」と明記)。
- BCI簡易比較(条件成立時のみ): 同様にA/B/Cで候補→各1本、`er013_output/family_c_future_trial_07/bci/`。
- `docs/pm/RESULT_PACKET_FC7.md`は新規作成。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07.md --json-out docs\pm\delegation_log\EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07_check.json`
2. offline検証(生成前): `.venv\Scripts\python.exe run_project_regression.py --pattern "er013*_test_*.py"`(期待: 既存88+新規全PASS)
3. home robots本Trial: `.venv\Scripts\python.exe er013_family_c_future_trial_07_run.py --theme home_robots --level a2 --budget-jpy 60`
4. BCI簡易比較(条件成立時のみ): `.venv\Scripts\python.exe er013_family_c_future_trial_07_run.py --theme bci --level a2 --budget-jpy 40`
5. 費用集計: `cost_summary.json`の合計がハード上限¥160.97以内であることを確認。
(3〜4のCLIフラグと総額ガードは本タスクで実装。)

## SSOT追記文

本タスクではSSOTを編集しない。root REPORT `EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07_REPORT.md`末尾に「SSOT追記文案(編集は行っていない)」節として、OPEN-147末尾追記案(v6人間評価の記録、CURRENT FACT契約撤廃、Trial-07結果・分類・開発・Trial費・量産単価[未確定なら明記]・残額)とDECISION_LOG新エントリ案を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない(Fableが後続CONSOLIDATIONで明示addする)。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FC7.md`に、ユーザー必須14項目を同じ番号で: 1) Core Provocation候補一覧/2) 各候補のスケール・レンズ/3) 相対ランキング(順位理由付き)/4) 採用した代表案/5) 記事全文の相対パス(本文はREPORTに全文転記)/6) Intimate・Societal・Radicalの違い(記事に現れた差を引用で)/7) Second-order・Inversionが有効だったか/8) CURRENT FACT 0件化の影響(本文の読みやすさ・Fact Safety層の挙動)/9) Writer制約数(v6=5との比較)/10) 人間評価に向けた比較ポイント(7軸、Sonnet補助採点は「補助」と明記)/11) 開発・Trial費(API別+5区分、テーマ別)/12) 量産時1記事単価(未確定なら「未確定」+理由)/13) 残る問題(不自然なStoryが出た場合はその事実を修正せず記録)/14) Gate 1判定材料。加えて: 分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)、BCI実施有無、Framing QA v2の決定的スキャン利用可否の設計確認結果、Family C残額、Artifact相対パス(index.html)、commit対象候補一覧、T-0結果、事前指定外Read(理由付き)、STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり(新規ファイル・出力dir・比較ページ構成)
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥160.97ハード上限、配分目安)
- [x] 並行タスク衝突回避あり(er013限定・SSOT/Git/ACTIVE_TASK不可)
