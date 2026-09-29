## 管理ID

LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01(Part B=過去 STOP 事例の抽出・厳しさの分類・QCD 影響の実測調査、委任 _02)。**read-only 調査**。一時ファイル `docs/pm/ACTIVE_TASK_LDB.md` / `docs/pm/RESULT_PACKET_LDB.md`(commitしない)。並行: 別 Sonnet 1 件(Part A=現行仕様整理・hard/soft・Hormuz trace、出力先 `docs/pm/investigation_ledger_deviation_check_01_part_a.md`)→ 同ファイルに触れない。本タスクの出力先: `docs/pm/investigation_ledger_deviation_check_01_part_b.md`(新規)+delegation_log のみ。**Production code・Prompt・Checker threshold・SSOT 4 点・REPORT_LEDGER の変更禁止、Trial 開始禁止、E2E 再開禁止、API 呼び出し禁止(費用 ¥0)、Opus 起動禁止**。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 背景(ユーザー問題意識、要旨)

Hormuz 記事(`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01` run_02)で JA「料金案が消えたからといって、価格がそのまま大きく下がる展開にはなりませんでした。」が EN 側 Deviation Check で `changed_causality` MAJOR(origin=ja_source)となり STOP。JA 側 Fact Check は COMPLIANT。ユーザーは EN 側が英語学習サービスとして厳しすぎる可能性を見ている。eigo-radio は英語学習サービス(嘘・低信ぴょう性・根拠なしを許容しない)であり、Production 量産には Quality / Cost / Delivery のバランスが必要。目的は「信頼性の最低ラインを守りながら過剰品質の Check を見直せるかの調査」。**本委任は調査のみ。新仕様・閾値・判定ロジックを提案採用・実装しない**。

## 調査項目(出力ファイルの章立てをこの順にする。章番号はユーザー指定に合わせ 3・4・5)

### 3. 過去の STOP 事例
過去の Production / Trial / REPORT / audit ログから、Ledger Check(JA Fact Check)・Deviation Check(EN)の事例を抽出。探索起点: `Glob **/deviation_checks/*.json`、`Glob **/fact_check*.json`、`Glob **/must_fix*.json`、`Grep -l "LEDGER_DEVIATION" er0*_output/**/*.json`(数が多ければ `--count` で規模を先に把握し、代表・全 MAJOR を対象)、REPORT の Grep `LEDGER_DEVIATION|MAJOR|JA_RECHECK_REQUIRED|must-fix|Deviation Check|Fact Check`、OPEN_ITEMS/HISTORY・DECISION_LOG/HISTORY の同 Grep、`git log --oneline -i --grep="deviation" | head -40`。
- **A. 明らかに止めるべきだった事例**(数字違い/人物・企業・国の取り違え/原文と逆の意味/根拠のない Fact 追加/時系列誤り/重大な因果捏造)
- **B. 過剰品質の可能性がある事例**(一般利用者の理解をほぼ変えない因果ニュアンス/要約に伴う自然な圧縮/断定強度の軽微な変化/英語学習教材として実質問題になりにくい表現/STOP による QCD 損失が大きかった事例)
各事例の最低項目: 管理ID/対象記事/該当文(JA・EN 逐語)/判定(category・severity・origin)/STOP したか/retry 回数/最終的な解決(must-fix・再生成・人手・放置)/追加コスト・手間(`raw_usage_log.jsonl`・REPORT の費用記載から取れる範囲)。**表**にまとめ、evidence パス(ファイル)を各行に付ける。A/B の振り分けは「現行事例の可視化」であり、あなたの分類理由を 1 行で付す(断定せず「候補」と表記)。auto_downgraded(MAJOR→MINOR 自動降格)された事例があれば別表で列挙。

### 4. 現在の判定がどこまで厳しいかの分類
章 3 の事例を、実装変更せず分析だけで 4 区分へマッピング: (i) 絶対に STOP すべき/(ii) 高リスクなので STOP 妥当/(iii) 品質改善として意味はあるが STOP 必須か疑問/(iv) 英語学習サービスとしては過剰品質の可能性が高い。区分ごとに件数・代表例・共通する category(changed_causality/certainty/scope 等)・origin(ja_source/translation)を集計。**新しい正式仕様を決めない**(可視化のみ)。10 category × severity × origin のクロス集計表(実データ)を付ける。

### 5. QCD 影響
過去 log から取れる範囲で実測: 1 記事あたりの Checker call 数(JA Fact Check 回数+EN Deviation Check 回数、Standard/Advanced 別)/retry 発生率/MAJOR STOP 率/JA 再生成・EN 再生成の追加 call/Human Review へ上がる頻度(`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`・`er011_output/attempt_history.jsonl` に Checker 起因の項目があるか)/追加 API コスト(`raw_usage_log.jsonl` の usage・model・cost を集計、Checker call の model=`gpt-5.6-luna` 等とトークン量)/throughput 影響(所要時間の記録があれば)/STOP による未完成記事率(Trial・Production run のうち Checker STOP で完成しなかった run 数)/Checker 自体のモデルコスト(1 call あたり平均 ¥)。**実測値がなければ推測せず「未計測」と明記**。集計スクリプトは scratchpad(`C:\Users\tensh\AppData\Local\Temp\claude\...\scratchpad`)に置き、repo に追加しない。母集団(対象 run 数・期間・Family)を明記。

## 出力ファイル `docs/pm/investigation_ledger_deviation_check_01_part_b.md`

- 章 3・4・5(上記)。各主張に evidence(ファイルパス/管理ID/commit)。推測は「推測」、未計測は「未計測」。**採用提案・仕様決定・Production 変更提案を書かない**。ユーザー向け表記は Standard/Advanced。
- 末尾に「Part A(現行仕様・hard/soft・Hormuz trace)との統合は別委任」と明記。

## 固定ブロック

T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_02.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_02.md --json-out docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_02.md_check.json` を実行し結果1行記録。T-2: TTS なし。T-3: API 支出なし(¥0)。E-1/D-1/G-1/F-1 標準。

## 事前指定Read一覧 / 事前指定Grep一覧

- 上記探索起点。REPORT: `Glob *_REPORT.md` のうち Grep `LEDGER_DEVIATION|JA_RECHECK|Deviation Check` に該当するもの(該当箇所のみ)。`CURRENT_SPEC.md`/`DECISION_LOG*.md`/`OPEN_ITEMS*.md` は Grep 該当箇所のみ(全文読込禁止)。
- 更新位置: 出力ファイル(新規)、delegation_log のみ。

## 実行コマンド全文

- `git log --oneline -i --grep="deviation" | head -40`、`git log --oneline -i --grep="ledger" | head -40`
- 集計: `.venv\Scripts\python.exe <scratchpad>\aggregate_checker_logs.py`(自作、repo 外)

## Git

- add 対象(path 指定のみ): `docs/pm/investigation_ledger_deviation_check_01_part_b.md`、delegation_log+`_check.json`。メッセージ `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01: Part B(過去STOP事例の抽出・厳しさの分類・QCD影響の実測、read-only調査)`、trailer `Management-ID: LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01`。push。

## 報告(RESULT_PACKET_LDB + handback、目安35行)

事例件数(A/B、区分 i〜iv)と代表例/クロス集計の要点/QCD 実測値(母集団明記)と未計測項目/新たに見つかった重大問題(修正せず報告)/費用 ¥0/commit hash・raw URL。
