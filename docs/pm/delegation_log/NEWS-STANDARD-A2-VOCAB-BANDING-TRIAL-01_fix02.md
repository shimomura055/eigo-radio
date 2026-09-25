## 管理ID
`NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01`(修正2回目=ユーザー承認による
Sewer v4生成)。**並行タスクあり**: 別sonnet-workerが
`TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01`(er016_*、`_TD`一時
ファイル)を実行中。本タスクは標準`docs/pm/ACTIVE_TASK.md`/
`RESULT_PACKET.md`、er015_*のみ。SSOT不変。commit時`index.lock`は10秒
待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクの
パスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/
`RESULT_PACKET*`/`.env`はaddしない。**履歴操作(reset/amend/rebase)禁止**。

## 性質/到達上限/禁止
- Trial継続。到達上限`VALIDATED`。Production変更・SSOT変更禁止。**追加
  LLM callは1回のみ**(Sewer Advanced→Standard v4)。現行v4 Promptを
  **そのまま**使用(一字も変えない、sha256でMeta実行時の
  prompt_standard_v4.txtと一致確認)。追加Variation・retry/fallback・
  新Validator・新品質チェック工程禁止。Web Search禁止。費用上限
  ¥100(暴走防止)。`git add -A`/`stash`禁止。
- STOP条件: 追加callが必要/Story・意味が崩れる/Production変更が必要/
  ¥100超過見込み。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を
`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix02.md`
へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行
(FAILでも継続)。

## 事前指定Read一覧
- `er015_output/news_standard_a2_vocab_banding_trial_01/prompt_standard_v4.txt`
  (逐語、sha256記録)、`vocab_bands_all.json`・`frequency_rank_top20000.json`
  (既存帯ルックアップ再利用)、`b1v4_standard_meta.md`(参照のみ)。
- `er015_output/news_natural_advanced_standard_a2_trial_01/comparison_sewer.md`
  (Sewer Advanced Baseline逐語、sha256`a7fa…`系は`sources.json`のAdvanced
  出力hashではなく日本語R2のhashなので混同しない。Advanced本文は
  `a1_advanced_sewer.md`があればそれを逐語入力にし、sha256を記録)。
- `er015_output/news_standard_a2_vocab_effectiveness_trial_01/a2v3_standard_sewer.md`
  (Sewer v3、比較用)、`vocab_analysis_v3.md`。
- `er015_news_standard_a2_vocab_banding_trial_01.py`: Grep
  `def |argparse|--step|article`→Sewer入力用の引数追加(既存のMeta処理は
  変更しない。`--article sewer`等の追加のみ)。

## 事前指定Grep
- 対象: `er015_news_standard_a2_vocab_banding_trial_01.py`
- パターン: `def |argparse|--step|--article|add_argument`
- 目的: 既存のMeta用関数(`cmd_generate_v4`/`cmd_evaluate*`/
  `cmd_assemble`)の位置を確認した上で、それらを一切変更せず、Sewer用の
  新規関数(`cmd_generate_v4_sewer`/`cmd_evaluate_sewer*`/
  `cmd_assemble_sewer`)と`--article`引数のみを追加する。

## 実行手順
1. `--step generate-v4 --article sewer --budget-jpy 100`: Sewer Advanced→
   v4→`a2v4_standard_sewer.md`(+`.meta.json`: `response.model`実値/
   tokens/latency/JPY/retry=0)。
2. `--step evaluate --article sewer`: 帯別残存語(Sewer Advanced / v3 /
   v4)、Advanced→v4の消えた/残った/新出語(帯付き)、Level指標、
   Fact diff(Advanced→v4)、structure_map(段落対応、Reveal/比喩
   [main artery・washing machine]/Ending位置、比喩が比喩のままか)。
3. **語彙遷移表** `vocab_transition_sewer_v4.md`: ユーザー指定9語
   (municipalities/installation/inspections/artery/wastewater/septic/
   collects/distant/および v3で出た gathers/faraway/putting in の元語)
   について、Advanced→v3→v4の表現と帯、判定(そのまま残った/自然に
   置換/不自然に置換/難語→別の難語)。加えて帯B/C/Dの全content wordを
   同じ4分類で整理(Sonnet目視、根拠1行ずつ、最終判定はFable/ユーザー)。
4. `comparison_sewer_v3_v4.md`(Advanced→v3→v4全文)。
5. REPORT追記: 既存§1–§13は変更せず、末尾に「§14 Sewer v4(ユーザー
   承認後の追加検証)」として 14.1 生成条件・cost/14.2 Sewer v4全文/
   14.3 帯別残存語(Advanced/v3/v4)/14.4 語彙遷移表(9語+帯B/C/D全件)/
   14.5 Level指標/14.6 Story・比喩・Ending/14.7 Fact drift/
   14.8 Fable最終評価`[Fable記入]`/14.9 最終分類`[Fable記入]`/
   14.10 USER_DECISION_REQUIRED`[Fable記入]` を追加。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er015_news_standard_a2_vocab_banding_trial_01.py --out-dir er015_output\news_standard_a2_vocab_banding_trial_01 --step generate-v4 --article sewer --budget-jpy 100
.venv\Scripts\python.exe er015_news_standard_a2_vocab_banding_trial_01.py --out-dir er015_output\news_standard_a2_vocab_banding_trial_01 --step evaluate --article sewer
.venv\Scripts\python.exe er015_news_standard_a2_vocab_banding_trial_01.py --out-dir er015_output\news_standard_a2_vocab_banding_trial_01 --step assemble --article sewer
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix02.md --json-out docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix02.md_check.json
git status --short
```

## SSOT追記文
なし。

## Git
明示add: `er015_news_standard_a2_vocab_banding_trial_01.py`、
`er015_output/news_standard_a2_vocab_banding_trial_01/` 配下の新規・
更新ファイル、`NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_REPORT.md`、
`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_fix02.md`、
同`_check.json`。
メッセージ: `NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01: ユーザー承認により
Sewer AdvancedからStandard v4を1本生成し、頻度帯別の語彙遷移(残存/自然
置換/不自然置換/難語→難語)をv3と比較(Luna 1 call、Production変更なし)`
trailer: `Management-ID: NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01`

## 報告(RESULT_PACKET)
0. T-0 1. Prompt sha256一致、Advanced入力sha256 2. `response.model`実値/
tokens/latency/JPY、追加call=1 3. 語彙遷移表(9語)の転記 4. 帯B/C/D全件
の4分類集計(件数) 5. Level指標(Advanced/v3/v4) 6. structure_map要約
7. Fact drift 8. STOP該当有無 9. `git status --short`・commit SHA・push
10. 一覧外Read理由、Open Item候補。

---
## 【ユーザー指示全文】

① NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01 継続。ユーザー判断: Sewer
記事でv4を1回生成してよい。目的は、Metaでは検証しきれなかった、難語の
頻度帯ごとの扱い分け/不自然な言い換え抑止/難語→別の難語への単なる
置換抑止 が、Sewerのように難語が多い記事でも機能するか確認すること。
条件: Advanced Sewer→Standard v4/現行v4 Promptをそのまま使用/追加
Variation禁止/retry・fallback不要/新Validator追加禁止/新しい品質
チェック工程追加禁止/追加LLM callは1回のみ。確認したい点: 特に前回
問題だった municipalities/installation/inspections/artery/wastewater/
septic/collects→gathers/distant→faraway/installation→putting in を
見る。頻度帯ごとに、そのまま残った/自然に置換された/不自然に置換された/
難語→別の難語になった を整理すること。固有名詞は当然別扱い。Closeout:
今回のSewer結果まで見て、v4の語彙設計をREJECTED/VALIDATED/
USER_DECISION_REQUIREDのいずれかに分類。良好でもProduction採用しない。
PM上の扱い: A2 vocab: Sewer v4結果待ち。両タスク終了後、ユーザー判断
事項を明示してSTOP。
