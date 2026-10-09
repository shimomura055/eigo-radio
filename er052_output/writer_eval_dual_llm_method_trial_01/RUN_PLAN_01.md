# RUN_PLAN_01: 実行手順(実行は別委任。本委任ではAPIを呼ばない)

凡例: 【確認】【見積】【推測】。

## 1. 前提(実行前にFable/ユーザーが決めること)
1. モデル構成(P1/P2/P3、MODEL_OPTIONS_COST_01.md §3)とrep数(1または2)。
2. DeepSeek等の単価登録(pricing_snapshot.jsonへの追加はユーザー/Fable承認)。
3. 予算上限(推奨: P1は上限¥30、P2は上限¥800、P3は¥0のAPI。いずれも見積の高値側を上回る設定)。
4. 事前登録(PREREGISTRATION_01.md)の承認。承認後は変更しない。

## 2. 成果物と物理的分離
| ファイル | 評価LLMへ | runnerが読む | 集計時に読む |
|---|---|---|---|
| `eval_items_01.json`(case_id, fact, target_sentence, context_before/after) | 渡す(1要素ずつ) | 読む | 読む |
| `eval_prompt_01.txt` | 渡す | 読む | - |
| `cases_01.json`、`CASES_01.md`(人間既知・Checker参考・出典・K番号) | **渡さない** | **読まない** | 集計scriptのみ |
| `results_{model}.jsonl`、`logs/` | - | 書く | 読む |
- runner(`run_eval_01.py`、実行委任で作成)は `cases_01.json` を `open` しないことをコードで保証し、単体テストで確認する(import/pathの静的検査を含む)。
- 集計(`aggregate_01.py`、同じく実行委任で作成)は評価完了後にだけ実行し、ここで初めて人間既知・Checker参考を結合する。

## 3. runner設計(`run_eval_01.py`)
- 引数: `--model-key`(例 openai_gpt6_luna / deepseek_v4_flash)、`--items eval_items_01.json`、`--prompt eval_prompt_01.txt`、`--rep N`、`--out results_{model}.jsonl`、`--budget-cap-jpy`、`--dry-run`。
- 処理: items順に(固定順)、1ケースにつき1回API呼び出し。各試行の「リクエスト全文、応答全文、usage(input/output/reasoning token)、model_id、パラメータ、タイムスタンプ、試行番号、HTTP/例外」を `logs/{model}_rep{N}_raw.jsonl` に追記(上書き禁止)。
- `results_{model}.jsonl` は1行=1(case_id, rep): `{case_id, rep, label, reason, misread_type, valid_json, attempts, cost_jpy_est}`。人間・Checker・K番号は含めない。
- 再試行: JSON/列挙値の違反は1回だけ再呼び出し(元の応答も保存)。API一時失敗(timeout,5xx,429)は最大2回再試行。いずれも上限回数を守り、独自に増やさない。最終的に不正なら `valid_json=false` として判定不能扱い(PREREGISTRATION_01 §4)。
- 費用ガード: 呼び出しごとに登録単価×実usageで累計を計算し、`--budget-cap-jpy` 超過見込みなら次の呼び出し前に停止。cost記録は既存の `raw_usage_log` 形式に合わせる【推測: 既存形式に合わせる方針。実装時に既存ログ形式を再確認】。
- 再利用候補: OpenAI呼び出しは `er006_model_routing_contract_01.py` の経路、DeepSeekは `er005_research_model_ab_01.py` の `_deepseek_call`(Chat Completions、json_object mode、推論トークンが出力予算を消費する点に注意)【確認: 該当ファイルの存在。実装可否は未検証】。
- Claude subagent(P3): runnerでは呼べない。Fable側が1ケースごとに、ツール無効の指示付きで `eval_prompt_01.txt` + 1要素を渡して起動し、返ったJSONを同形式の `results_claude_subagent.jsonl` に保存する(原応答も保存)。

## 4. 実行手順
| 手順 | 内容 | 依存 | 並列/直列 |
|---|---|---|---|
| 0 | ¥0確認: runnerの単体テスト、`--dry-run`(API非呼び出しでリクエスト組み立てとcases_01.json非参照を検査)、各モデルのtemperature/seed/reasoning指定可否をAPI仕様書で確認 | 実行承認 | 直列(以降の前提) |
| 1 | 小規模試し: 各モデルで1ケース(例 K08)のみ呼び、JSON形式・usage・推論トークン量を確認(¥0.1未満の見込み)。この結果は本番rep1に含めない | 手順0 | モデル間は並列可 |
| 2 | 本番rep1: モデルA、モデルBを別プロセスで同時実行(別vendor、状態共有なし、順序依存なし) | 手順1で形式OK | **並列**(理由: 独立、条件同一) |
| 3 | 本番rep2(実施する場合): 同様に並列。rep1完了後に開始(rep1の結果を見て条件を変えない) | 手順2 | モデル間は並列 |
| 4 | 集計: `aggregate_01.py` でRESULT_TABLE_TEMPLATE_01.mdを生成し、PREREGISTRATION_01.md §3に機械適用 | 手順2〜3 | 直列(全結果が前提) |
| 5 | 最終報告(Status, 1表, 結論1行)。Productionには触れない | 手順4 | - |
- 所要時間見込み【推測】: 手順1〜3はAPI応答待ちが主で、10ケース×1rep×1モデルで数分〜十数分。並列化で全体は手順の最長モデルに律速される。実測は実行委任で記録する。

## 5. 実行委任に含めない/禁止
- 新規Writer生成、Checker変更、Production変更、プロンプトの結果後変更、ケースの追加・差し替え(事前登録の変更になる)。
- 結果を見たうえでの再実行・差し替え、APIキー値のログ出力(キーは読まず環境変数のみ参照)。
- VALIDATEDでも、そのまま大規模Writer比較Trialへ進めない。次はユーザー判断。

- 委任_01b追記: `eval_items_01.json` の `context_source` は監査用の運用情報であり、評価LLMへは渡さない(runnerは上記5項目のみ渡す)。設計(プロンプト・事前登録・閾値)は変更していない。

- 委任_01c追記: `run_eval_01.py`(runner)と `run_eval_01_test.py`(単体テスト、API不要)を作成済み(未実行)。引数は本書3節の案から `--model`(gpt-6-luna / deepseek-v4-flash)、`--max-yen`、`--allow-unpriced` に簡素化。DeepSeekは単価未登録のため `--allow-unpriced` なしでは起動拒否。ケースは差替え済み(CASES_01.md冒頭)。M2対象は K08,K09,K12。任意ブロックは OPTIONAL_BLOCK_01.md(設計のみ)。
