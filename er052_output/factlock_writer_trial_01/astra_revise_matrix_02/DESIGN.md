# DESIGN: ASTRA-REVISE-MATRIX-02 (FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_16, 2026-10-08)

性質: Trial/DEV。到達上限Status = `MEASURED`(人間確認待ち)。Production変更なし。ユーザーGo取得済み(2026-10-08「OKです。提示は元記事＋XYのR2のみでよいです(R1は不要)。Goお願いします。」)。委任文は `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_16.md`。

## 設計(委任_15 ASTRA-REVISE-MATRIX-01 と同一条件、記事を2本、段はR1・R2のみ)
- モデルは全て `gpt-6-astra`、reasoning `{"effort": "high"}`(委任_15・Step 1 と同一)。routing contract は override 記録(`require_model_or_override`、astra 単価未登録)。
- 系列A(=X、ユーザーPromptのみ): developer/system メッセージなし。系列B(=Y、熟練編集者): developer = Step 1 F2 文(`step1_chat_repro_01/conditions.json` から逐語)。
- user メッセージ(共通): `以下の記事:\n\n{前段本文}\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。`
- R1 入力 = R0(タグ除去済み)、R2 入力 = R1 の生出力。`previous_response_id` 不使用。記号禁止リストなし。R3 なし。生成は retry なし。
- 4系列(記事x系列)を同一 process 内 ThreadPool(max 4)で並列、段内は逐次。ホルムズとミニバッグは別 process で時間をずらして実行(ミニバッグは R0 生成待ち)。

## R0
### 記事1 ホルムズ(Fact Lock v1 既存)
- 選択規則: `runs/hormuz/control/b2__factlock__r1/ja_writer/original.md`、manifest `exit_reason=completed` -> 採用(prep_inputs.py で規則を実行して確認)。
- `strip_tags(original_with_tags.md)` が `original.md` と一致することを確認。R0 = `strip_tags(original.md).strip()+"\n"`(`inputs/hormuz/R0.md`)。
- SHA256: original.md 169f06a48f4357e18e5b657d3c432f765af92ec58a6b710b76f8cc8429fada54 / R0.md c9ee84e0b965d79719cb50d238f7ccddc75412d1ec4b2580726a4a618ac18fd7 / 台帳 9bd6834e68e7e4378ba0ebccdd84c0128df2a5cd0aca7c1e84df612ae77ae1a6 / B3 brief(storyline_b3/selected_brief.md、注記版 briefs/hormuz/b2/selected_brief_factlock.md と同SHA) 4ed19d3787d2850cc1d1c8038af2efecb8a038f27b9beb470ab2df8cf56c330e。
- 台帳: `runs/hormuz/control/b2__factlock__r1/research_ledger/verified_fact_ledger.txt`。

### 記事2 ミニバッグ(新規生成、Fact Lock v1 R0 手順)
- 入力: `er052_output/gpt6_wiring_e2e_01/run_02/` の台帳(SHA 0cc8ca3f...8f6f0f)・B3 brief(`storyline_b3/selected_brief.md`、SHA 55bb9ba3...cea)。
- 注記版 brief 作成(`tools/prep_inputs.py`): 元 brief の `## Selected Facts` は箇条書きでなく1段落だったため、文境界で3事実(ELLE紹介 / 秋ランウェイまとめ / Who What Wear 10月)に分け、本文は逐語のまま `- 【事実N】` を付与(分割位置のみが加工、本文改変なし)。数値注記: 中核 = 2026年9月(ELLE紹介時期)・2026年10月(micro見解の時期)の2件、周辺 = Fall 2026・2026年。台帳IDは brief 内に無し。`inputs/small_bag/selected_brief_factlock.md`(SHA 0e4fe52e...9abd)、`core_numbers.json`。
- R0 生成(`tools/gen_r0_small_bag.py`): Production 関数 `jaw.run_ja_writer_o_r1_r2` の Original 段(R0_PROMPT + Fact Lock R0 ブロック[`apply_factlock_patches`]、gpt-6-luna[`apply_all6_patches`]、JA Fact Check Full Ledger、MAJOR->must-fix 1回->STOP、記号Gate)をそのまま通し、R1 呼び出し直前で `BaseException` により打ち切る(R1/R2 の API 呼び出しなし。ファイル編集なし、実行時 patch のみ)。続けて Fact Lock v1 と同じタグ照合(`check_stage`、測定のみ)と `strip_tags`。
- 結果: `r0_small_bag/R0_RUN.json`(Writer 1 call、JA FC `LEDGER_COMPLIANT` MAJOR 0/MINOR 0、must-fix 不要、記号 must-fix 不要)。R0 = `inputs/small_bag/R0.md`(SHA 88ba339d...e1b0)。

## 評価
- JA Fact Check: gpt-6-luna、全台帳、`run_deviation_check(hook_aware=False, include_related_fact_id=True)`(委任_15 と同一呼び出し)。FC・決定論指標はMarkdown除去後(P1)の本文。台帳は記事ごとの全台帳。
- 決定論指標: `det_metrics`(字数・段落・1文段落・問い・ダッシュ・Markdown残存・記号Gate[計測のみ]・台帳外数値[記事ごとの brief+台帳の数値集合])。(ii)新規具体主張: `untagged_check`(R0 比)。
- 集計: `tools/make_report2.py` -> `eval/{SUMMARY_MATRIX_02.md, HUMAN_CHECK_MATRIX_02.md, COST_MATRIX_02.md, METRICS_MATRIX_02.json, COST_SUMMARY_02.json}`、ユーザー提示 `USER_PACK_02.md`(系列は X/Y を開示、R1・FC は載せない)。

## 予算・単価
上限 ¥80。astra 単価は routing contract 未登録 -> 推定(gpt-6-sol 2.00/0.20/10.00 USD per 1M x2.5、USD/JPY=160)。トークンは全て実測を記録。luna は登録単価(0.10/0.01/0.50)。(ii) は usage 非取得のため1本0.2円の概算。

## 実行コマンド(`.venv\Scripts\python.exe -X utf8`)
```
tools\prep_inputs.py                                   # API なし
tools\gen_r0_small_bag.py --yes-run-paid               # ミニバッグ R0 生成
tools\run_matrix2.py --phase gen --articles hormuz --yes-run-paid
tools\run_matrix2.py --phase gen --articles small_bag --yes-run-paid
tools\run_matrix2.py --phase eval --articles hormuz --yes-run-paid
tools\run_matrix2.py --phase eval --articles small_bag --yes-run-paid
tools\make_report2.py                                  # API なし
```

## 出力
`inputs/`、`r0_small_bag/`、`runs/<article>/{A,B}/r{1,2}.md`(生出力)・`.p1.md`(Markdown除去後)・`.response.json`、`usage_log.jsonl`、`eval/{fc,ii}/*.json`、`gen_*.log` `eval_*.log` `gen_r0_small_bag.log`。
