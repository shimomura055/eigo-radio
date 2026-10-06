## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02(委任_01: Trial script修正版の作成。記事側AIに「Ledger側のどの事象について述べているか」を選ばせ、選択事象のみ比較。総当たり比較禁止。API呼出は本委任では行わない)。並列委任_02(testset_02/正解データ)、_03(集計script)、_04(SSOT)が同時進行。**書込先: `er052_open233_directional_trial_02.py`(新規、TRIAL-01の`er052_open233_directional_trial_01.py`はコピー元として残し変更しない)、`er052_open233_directional_trial_02_test.py`(新規)、`er052_output/open233_directional_misread_trial_02/dryrun/`、`docs/pm/RESULT_PACKET_TRIAL02_01.md`、`docs/pm/delegation_log/`。Production code・SSOT・git操作なし。**
作業方式: Edit/Writeは1回40行以内(関数単位)、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存。時間目安30分。

## 性質/到達上限Status/禁止事項
性質: Trial専用script修正(¥0、dry-run)。到達上限: unit test PASS+dry-run完走。禁止: 有料API/残11 run/Production変更/floor復活/gold・KPI変更/新Safety原則の追加。Opus Gate: 非該当(Opus Part 2 U3推奨の実装、設計は条件Aレビュー済み)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う(一覧外は理由記録)。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_01.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 本委任¥0(実行は別委任、上限¥10は`--budget-yen`で強制)。

## ユーザー指示(原文、要点)
> 今回の修正: 前回のsame_blind構成を維持する。ただし、記事側AIに「この文がLedger側のどの事象について述べているか」をまず選ばせる。その後、選択された事象だけについてLedger側の状態と記事側の状態を比較する。複数事象すべてとの総当たり比較は禁止。
> Trial本実行も、順序依存がなく条件同一性を保てるなら複数processで並列化する。

## 設計(固定)
1. Ledger側抽出: TRIAL-01と同じ(factごと、記事を見せない、events=[{subject_x, result_state, quote}]、enum同一)。`--ledger-only --ledger-repeat 3 --out-dir`で実行し`ledger_cache.json`({fact_id: {rep1: events, rep2:..., rep3:...}})を出力。
2. 記事側(blind、1 callで選択+抽出): 入力=**Ledger側eventsの`subject_x`ラベル一覧のみ**(result_state・quote・Ledger本文は渡さない。ラベルは重複除去し順序固定)+記事文+前後文。prompt=「この文は、次の対象のうちどれについて『事象後の結果状態』を述べているか。1つ選ぶ(どれも述べていなければNONE)。選んだ対象の結果状態をenumから1つ、逐語引用付きで答えよ」。schema `{selected_subject: str|"NONE", result_state: enum, quote: str}`。`selected_subject`がラベル一覧に無ければUNCLEAR扱い。記事側はLedger側の**同じrepeat番号**のeventsを使う(rep i の記事側はrep i のLedger events。再現性のため)。
3. 比較(Python): 選択eventのみ`compare()`(TRIAL-01と同じ規則: REVERSEDは方向対該当かつ両側quote非空のみ、PAUSED vs STOPPED=SAME_FAMILY、quote欠落・enum外=UNCLEAR)。NONE→NOT_MENTIONED。**他eventとの比較は行わない**(unit testで、Ledgerに逆方向の別eventがあっても選択eventがSAMEならSAMEになることをassert)。最終compare=repeat別compareの配列と、「rep0(最初の反復)」の値を両方記録(集計はrep0基準+全repeat率)。
4. shard並列: `--article-shard i/n`(testset項目をid順にn分割、i番目)+`--ledger-cache <path>`(Ledger側は再実行せずキャッシュ読込)+`--merge <dir>`(shard出力の`results_shard_*.jsonl`を結合しsummaryを再計算)。shard間で入力条件が同一であること(同じcache・同じprompt・同じmodel/effort)をmergeで検証(各shardの`run_meta.json`のhash一致)。
5. 費用: TRIAL-01と同じPRICE_TABLE・為替、`--budget-yen`は各process独立のため、Fableが各shardに「残額/n」を渡す。call_log必須。
6. 出力record keys(委任_03の集計scriptと契約): `id, fact_id, label, origin, expected_compare, acceptable_compare, expected_event_subject(あれば), repeats: [{rep, ledger_events_subjects: [...], selected_subject, ledger_state, article_state, compare, ledger_quote, article_quote}], final_compare_rep0, final_compares, cost_jpy`。summary keys: `n_items, n_calls, cost_jpy, by_label: {label: {n, reversed_rep0, reversed_any, unclear, not_mentioned}}, gold_detail: {id: {hits: k, reps: 3}}`。
7. testset入力: `--testset <testset_02.json>`(委任_02が作成中、keysはTRIAL-01と同じ+`expected_event_subject`任意。未完成の場合はTRIAL-01の`er052_output/open233_directional_misread_trial_01/testset_01.json`でdry-run)。
8. unit test(unittest): 事象選択のみ比較(総当たり禁止のassert)、blind保証(記事側promptにLedger state・quote・本文が含まれない)、NONE→NOT_MENTIONED、ラベル外→UNCLEAR、shard分割の網羅性(n shardの和=全項目、重複なし)、merge時のmeta hash不一致で停止、budget停止。TRIAL-01のtest 8件の該当分も移植。
9. dry-run: `--dry-run`で固定ダミー応答、3項目のミニセット+testset全件で`--ledger-only`→shard 3→mergeの一連を通す。

## 事前指定Read/Grep一覧
1. `er052_open233_directional_trial_01.py`: 全文(コピー元、約400行想定。Grep `def |argparse` で構成把握後、必要関数を範囲Read)。
2. `er052_open233_directional_trial_01_test.py`: 全文(移植元)。
3. `docs/pm/RESULT_PACKET_TRIAL_02.md`: 全文(短い、TRIAL-01実行時の引数・model・effort確認)。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_01.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_01.md_check.json`
2. `.venv\Scripts\python.exe -m unittest er052_open233_directional_trial_02_test`
3. dry-run一連: `--dry-run --ledger-only ...` → `--dry-run --article-shard 1/3 --ledger-cache ...`(2/3, 3/3) → `--merge ...`(出力先`er052_output\open233_directional_misread_trial_02\dryrun`)

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_TRIAL02_01.md`: test件数、dry-run出力パス、本実行コマンド例(ledger-only→shard×3→merge、引数込み)、record/summary keys、T-0結果、一覧外Read理由。最終報告8行以内。

## 注記(Sonnet追記、本文は逐語)
事前指定Grep一覧+追記位置・更新位置の手順: 追記/更新位置は新規ファイルのため該当なし。
