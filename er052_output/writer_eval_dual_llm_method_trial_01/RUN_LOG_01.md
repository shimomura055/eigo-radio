# RUN_LOG_01: 実行記録(委任_02、2026-10-09)

python: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe (openai・dotenv導入済みを確認)。単体テスト: 25件OK(run_eval_01_test.py)。

## 1. dry-run(全経路、API非呼び出し)
```
[DRY-RUN] model=gpt-6-luna provider=openai rep=1 (API非呼び出し)
  items=10 呼び出し数(最小)=10 / 最大(形式再呼び出しを全件で使った場合)=20
  見積入力token(全件)=14558  見積出力token/件=600-4000  上限 max_output_tokens=6000
  渡す項目=['case_id', 'fact', 'target_sentence', 'context_before', 'context_after'] (context_source・人間判定・Checker情報は渡さない)
  出力先 results=results\gpt-6-luna_rep1.jsonl logs=logs\gpt-6-luna_rep1_raw.jsonl
  見積費用(登録単価 gpt-6-luna)= JPY 0.71 - 3.43 (形式再呼び出しなしの1rep) / --max-yen=6.0
  再試行上限: 形式違反=1回 / 一時障害=2回。結果を見た再実行・差し替えは禁止。
[DRY-RUN] model=gpt-6-luna provider=openai rep=2 (API非呼び出し)
  items=10 呼び出し数(最小)=10 / 最大(形式再呼び出しを全件で使った場合)=20
  見積入力token(全件)=14558  見積出力token/件=600-4000  上限 max_output_tokens=6000
  渡す項目=['case_id', 'fact', 'target_sentence', 'context_before', 'context_after'] (context_source・人間判定・Checker情報は渡さない)
  出力先 results=results\gpt-6-luna_rep2.jsonl logs=logs\gpt-6-luna_rep2_raw.jsonl
  見積費用(登録単価 gpt-6-luna)= JPY 0.71 - 3.43 (形式再呼び出しなしの1rep) / --max-yen=6.0
  再試行上限: 形式違反=1回 / 一時障害=2回。結果を見た再実行・差し替えは禁止。
[DRY-RUN] model=gpt-5.6-luna provider=openai rep=1 (API非呼び出し)
  items=10 呼び出し数(最小)=10 / 最大(形式再呼び出しを全件で使った場合)=20
  見積入力token(全件)=14558  見積出力token/件=600-4000  上限 max_output_tokens=6000
  渡す項目=['case_id', 'fact', 'target_sentence', 'context_before', 'context_after'] (context_source・人間判定・Checker情報は渡さない)
  出力先 results=results\gpt-5.6-luna_rep1.jsonl logs=logs\gpt-5.6-luna_rep1_raw.jsonl
  見積費用(登録単価 gpt-5.6-luna)= JPY 1.62 - 8.15 (形式再呼び出しなしの1rep) / --max-yen=9.0
  再試行上限: 形式違反=1回 / 一時障害=2回。結果を見た再実行・差し替えは禁止。
[DRY-RUN] model=gpt-5.6-luna provider=openai rep=2 (API非呼び出し)
  items=10 呼び出し数(最小)=10 / 最大(形式再呼び出しを全件で使った場合)=20
  見積入力token(全件)=14558  見積出力token/件=600-4000  上限 max_output_tokens=6000
  渡す項目=['case_id', 'fact', 'target_sentence', 'context_before', 'context_after'] (context_source・人間判定・Checker情報は渡さない)
  出力先 results=results\gpt-5.6-luna_rep2.jsonl logs=logs\gpt-5.6-luna_rep2_raw.jsonl
  見積費用(登録単価 gpt-5.6-luna)= JPY 1.62 - 8.15 (形式再呼び出しなしの1rep) / --max-yen=9.0
  再試行上限: 形式違反=1回 / 一時障害=2回。結果を見た再実行・差し替えは禁止。
[DRY-RUN] model=gpt-6-luna provider=openai rep=1 (API非呼び出し)
  items=22 呼び出し数(最小)=22 / 最大(形式再呼び出しを全件で使った場合)=44
  見積入力token(全件)=31937  見積出力token/件=600-4000  上限 max_output_tokens=6000
  渡す項目=['case_id', 'fact', 'target_sentence', 'context_before', 'context_after'] (context_source・人間判定・Checker情報は渡さない)
  出力先 results=results\optional_block_gpt-6-luna_rep1.jsonl logs=logs\optional_block_gpt-6-luna_rep1_raw.jsonl
  見積費用(登録単価 gpt-6-luna)= JPY 1.57 - 7.55 (形式再呼び出しなしの1rep) / --max-yen=15.0
  再試行上限: 形式違反=1回 / 一時障害=2回。結果を見た再実行・差し替えは禁止。
```

見積合計(形式再呼び出しなし): 本体 JPY 4.7-23.2(6-luna 2rep=1.4-6.9、5.6-luna 2rep=3.2-16.3)、任意ブロック JPY 1.57-7.55。上限は本体6-luna各6円・5.6-luna各9円(合計最大30円)、任意15円。

## 2. 実行(2026-10-09 21:5x、3プロセス並列: 6-luna鎖 / 5.6-luna鎖 / 任意ブロック。rep2はrep1完了後に開始)
- 起動: `chain_6luna.sh` / `chain_56luna.sh` / `chain_opt.sh`(同梱)。結果は `results/`、全試行の生ログは `logs/*_raw.jsonl`、標準出力は `logs/stdout_*.txt`。
- 全5ラン完了。費用上限到達なし、API認証失敗なし、形式違反0件(全62試行が初回で有効JSON)、API例外試行0件、形式再呼び出し0件。
- temperature=0指定は全モデルで拒否(推論モデル)され、実効は「未指定」。拒否応答は課金対象外・各プロセスの先頭1回のみ(raw logには記録されない)。したがってrep間一致(M4)は決定論ではなく実測のばらつき。
- 実費(usage実測x登録単価): 本体 JPY 1.763(6-luna rep1 0.397 / rep2 0.250、5.6-luna rep1 0.637 / rep2 0.478)、任意ブロック JPY 0.695、合計 JPY 2.458。見積(本体4.7-23.2円、任意1.57-7.55円)を下回った(推論トークンが見積上限4,000/件より小さかったため)。
- 結果表: `RESULT_TABLE_01.md`(自動生成 `aggregate_01.py`、数値は `aggregate_01.json`)。
- 実行直前の補足: 実行前にcases_01.jsonのK08/K09/K12をユーザー確認済みAへ更新(evalへ渡す項目は不変、eval_items_01.jsonの差分なし)。
