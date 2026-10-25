# BUDGET_PLAN_02 (委任_32: Round 2の費用計画。API 0・本委任は有料生成なし)

## 1. 残枠
- ユーザー承認の個別上限200円(USER_12)− Round 1までの実費67.04円(`BUDGET_LOG_01.md`)= **132.96円**。
- 日次(JST)は2026-10-25の終了時点で961.08円(残約39円)。Round 2は**JST日付変更後**(2026-10-26 00:00以降)に起動する。起動前に `docs/pm/tools/daily_dev_cost_01.py` で当日の累計を確認する。

## 2. 見積(Round 1実測: 1生成+判定 平均16.8円、生成 high ≒ 13.7〜19.7円)
| 区分 | 内容 | 見積(再生成なし) | 最悪(全生成で再生成1回) |
|---|---|---|---|
| (a) high | Prompt 02 × 2テーマ × 2生成 | 約55〜80円 | 約125円 |
| (b) medium | Prompt 02 × 2テーマ × 1生成 | 約17〜24円(medium実測なし。推定) | 約45円 |
| 合計 | 6本 | **約72〜104円** | 約170円(guardが先に停止) |
- 実際の再生成は決定論検査NG時のみ(Round 1は0/4)。guardは予約方式で、各callの前に『テーマ別の実費累計+そのcallの見積(high 20円/medium 14円/判定0.8円)>テーマCap』なら停止する。最悪値はCap超過前に止まる。
- 残枠132.96円に対し期待値の72〜104円は収まる。最悪ケースは**Cap(下記)が先に止める**ため132.96円を超えない。

## 3. Cap設定(Fableが起動時に作成)
`er110_output/family_y_closing_general_02/BUDGET_APPROVED.json`(無い限り `--paid` でも起動しない)。例:
```
{"cap_jpy": 130, "management_id": "FAMILY-Y-VOICES-DESIGN-01", "delegation": "委任_33(Round 2起動)", "approved_by": "ユーザー(Closing一般化Trial個別承認上限200円、USER_12)", "basis": "残132.96円(200-67.04)", "note": "Round 2: Prompt 02 high 2テーマx2生成 + medium 2テーマx1生成"}
```
- テーマ別Cap=cap/2=65円。1テーマの期待消費は36〜52円(high 2生成+medium 1生成)で収まり、最悪は予約guardが停止する。
- 日次1,000円を超えそうな場合(他agentの消費で残が足りない場合)は、起動前に計測して判断する(超過見込みの事前承認は7-9)。案件見積300円未満・承認済みScope内のため都度ユーザー承認は不要(7-7)。

## 4. 起動コマンド(Fableが翌日、日次を確認してから。別process4本を並列。出力先とログは分離されるため競合しない)
起動前に毎回: `py tools/stop_scope_check_01.py --managed-id FAMILY-Y-VOICES-DESIGN-01 --run-dir er110_output/family_y_closing_general_02 --out er110_output/family_y_closing_general_02/stop_check_<委任名>.json`(rc=3なら起動しない)。
```
py er110_family_y_closing_general_trial_01.py dryrun --prompt-version 02 --effort high      # API 0。sha=4713ceff…を確認
py er110_family_y_closing_general_trial_01.py gen --theme redelivery_fee --prompt-version 02 --effort high   --gens 2 --paid
py er110_family_y_closing_general_trial_01.py gen --theme sns_age_limit  --prompt-version 02 --effort high   --gens 2 --paid
py er110_family_y_closing_general_trial_01.py gen --theme redelivery_fee --prompt-version 02 --effort medium --gens 1 --paid
py er110_family_y_closing_general_trial_01.py gen --theme sns_age_limit  --prompt-version 02 --effort medium --gens 1 --paid
```
- 出力: `er110_output/family_y_closing_general_02/<theme>/gen_{high_1,high_2,medium_1}/`(`closing_final.txt`・`analysis_final.json`・`gate_leak_check.json`・`grounding_report.json`・`gen_meta.json`[effort・prompt_version・prompt_sha256・style])、`raw_usage_log_{high,medium}.jsonl`。
- 再起動: 外部停止・原因不明のrc≠0が2回続いたら再起動せずSTOP。完了済みgenは `gen_meta.json` が `DONE` なら skip(done) される(同一コマンドでの再実行は、委任文が許す回数のみ)。
- 実費確認: `py -c "import er110_family_y_closing_general_trial_01 as g; print(g.spent_jpy('er110_output/family_y_closing_general_02/redelivery_fee'))"`(テーマ別。effort別のlogも合算される)。

## 5. 起動後の更新
- medium実測の1生成+判定の実費を `BUDGET_LOG_02.md` に記録し、`GEN_EST_BY_EFFORT["medium"]` を実測へ更新する(以後の見積用。更新時はtestの期待値も更新)。
