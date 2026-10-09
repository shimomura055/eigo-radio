# RUN_LOG_02: 追加Trial 実行記録(委任_04、2026-10-09)

## 1. 事前整備
- DeepSeek公式単価を `er005_output/cost_baseline_01/pricing_snapshot.json` に登録(出典 https://api-docs.deepseek.com/quick_start/pricing、HTTP 200、2026-10-09)。Standard=Peak(input $0.30 / cache hit $0.006 / output $1.20)、Off-peakは別tierで記録のみ。モデル名脚注: `deepseek-v4-flash` は引退済みで DeepSeek-V4.1-Flash が応答(Flash価格で課金)。
- `run_eval_01.py`: gpt-5.6-sol追加、DeepSeekを費用ガード対象へ、割引tierを費用算出から除外、DeepSeek max_tokens=32000。単体テスト `run_eval_01_test.py` 25件OK、`er006_model_routing_pricing_coverage_test_01.py` 10件OK(DeepSeek単価テスト追加)。

## 2. dry-run(API非呼び出し)
```
[DRY-RUN] model=gpt-5.6-sol rep=1: 見積入力token(全件)=14558 見積出力token/件=600-4000
  見積費用(登録単価 gpt-5.6-sol)= JPY 40.45 - 203.65 (1rep、形式再呼び出しなし) / --max-yen=40.0
[DRY-RUN] model=deepseek-v4-flash rep=1: 同入力
  見積費用(登録単価 deepseek-v4-flash)= JPY 1.85 - 8.38 (1rep) / --max-yen=20.0
```
- 参考(実測ベース): 前Trialの実使用は input 10,537 tok/rep、output(推論込み)は gpt-5.6-luna 1,559〜1,853、gpt-6-luna 2,365〜2,859 tok/rep。これをsol単価に当てると 1rep 約 JPY 16〜22、2rep 約 JPY 32〜44(Solの推論量次第)。**sol 2rep上限 JPY 40 は、機械的見積(下限だけで1rep超過)では超過、実測ベース見積でも上限をまたぐ。**
- 判定: **sol は上限超過見込みのため、指示に従い実行せずSTOPして報告**(上限引上げ/rep数の判断はFable/ユーザー)。DeepSeek は見積(2rep最大 約JPY 17)が上限JPY 20以内のため実行する。

## 3. DeepSeek実行(2026-10-09)
- 実行: `.venv\Scripts\python.exe run_eval_01.py --model deepseek-v4-flash --rep {1,2} --max-yen 10`(rep別上限JPY 10、合計上限JPY 20)。結果 `results/deepseek-v4-flash_rep{1,2}.jsonl`、生ログ `logs/deepseek-v4-flash_rep{1,2}_raw.jsonl`。
- 形式違反0、再呼び出し0、例外0。実費 JPY 3.90(rep1)+2.16(rep2)=6.06(登録単価、Peak標準)。応答model=`deepseek-flash`。
- 集計: `aggregate_02.py` → `RESULT_TABLE_02.md`(部分: sol未実行)。
## 4. gpt-5.6-sol: 未実行(STOP)
理由は2節。Fable/ユーザーが(a)上限JPY 40の引上げ(実測ベース2rep約JPY 32〜44、機械的見積上限は1repで約JPY 204)、(b)上限据置で1rep実行などを決めた後、`run_eval_01.py --model gpt-5.6-sol --rep {1,2} --max-yen <上限/2>` で実行可能(経路・テスト整備済み)。

## 5. 委任_04b: gpt-5.6-sol 実行(2026-10-09)
- 上限引上げ JPY50/rep を PREREGISTRATION_02 s8 に実行前固定(08491e12)。`run_eval_01.py --model gpt-5.6-sol --rep {1,2} --max-yen 50`。rep1 JPY 15.006、rep2 JPY 10.970(合計25.975)。形式違反0、再呼び出し0、例外0。実効: reasoning=medium、temperature=指定なし(拒否)、seed未対応。
