# DESIGN: ASTRA-REVISE-MATRIX-01 (FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_15, 2026-10-08)

性質: Trial/DEV。到達上限Status = `MEASURED`(人間確認待ち)。Production変更なし。ユーザーGo取得済み(2026-10-08「はい、Goしてください。」)。

## 設計(ユーザー確定)
- 起点 R0 = Fact Lock v1 の meta b2、Writer直後本文(R1/R2未通過)、inline タグ除去済み。
- 2系列 x 3段(R1 -> R2 -> R3)。モデルは全て `gpt-6-astra`、reasoning は Step 1 と同一(`{"effort": "high"}`、`step1_chat_repro_01/conditions.json` と `run_step1.py`)。
  - 系列A「ユーザーPromptのみ」: developer/system メッセージなし。user メッセージのみ。
  - 系列B「熟練編集者」: developer = Step 1 F2 developer 文(`conditions.json` から取得、逐語):
    「あなたは熟練の編集者です。元記事の事実はそのままに、読者が思わず続きを聞きたくなる記事に書き直してください。構成の組み替え、段落の分け方、語りかけ、問いかけ、余韻のある結びなど、必要だと思う手段は自由に使ってください。」
  - 各段の user メッセージ(両系列共通): `以下の記事:\n\n{前段本文}\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。`
  - 逐次: R1入力 = R0、R2入力 = R1出力(Markdown除去前の生出力)、R3入力 = R2出力。`previous_response_id` は不使用(本文テキスト渡し)。記号禁止リストは付けない。
  - 系列A/Bは2プロセス並列、段内は逐次。生成はretryなし(エラー時はERROR記録のみ)。

## R0 の同一性確認(Fact Lock v1 meta b2)
- R0 = `er052_output/factlock_writer_trial_01/step2_astra_r3_01/inputs/FL_R0/meta/b2/source.md`(委任_14 準備)。
- 元ファイル = `er052_output/factlock_writer_trial_01/runs/meta/control/b2__factlock__r1/ja_writer/original.md`(採用 rep = r1。MANIFEST.json で r1/r2 とも completed、選択規則「r1が completed なら r1」)。
- 突合: `strip_tags(original.md).strip() + "\n"` は `source.md` とバイト一致、`source_prestrip.md` は `original.md` とバイト一致(スクリプト検証済み)。`source.md` と `original.md` の差は末尾改行1つのみ(2178 vs 2177 byte)。生成入力は `.strip()` 後なので同一本文。`original.md` は 【事実N】タグ除去済み(タグ付き版は `original_with_tags.md`)。
- 台帳(verified_fact_ledger) = `er052_output/factlock_writer_trial_01/runs/meta/control/b2__factlock__r1/research_ledger/verified_fact_ledger.txt`。
- B3 brief = `er052_output/factlock_writer_trial_01/runs/meta/control/b2__factlock__r1/storyline_b3/selected_brief.md`(= `er052_output/factlock_writer_trial_01/briefs/meta/b2/selected_brief_factlock.md` とSHA一致)。

## 固定SHA256
| ファイル | SHA256 |
|---|---|
| R0 `step2_astra_r3_01/inputs/FL_R0/meta/b2/source.md` | 4dd147ff853f0cedad01a8d8216f4b4ccd7aaba8710e6bc5d12e5c4b327ad40f |
| 元 `runs/meta/control/b2__factlock__r1/ja_writer/original.md` | 0b672113b7a9eae22fa5d1f9858a1c75cbb5229af59323b4fb45e06098a916fc |
| 台帳 `verified_fact_ledger.txt` | ea0ce587e605beeac8f02315ae4520899156393bbba2e059d99f45988b7c5f56 |
| B3 brief `storyline_b3/selected_brief.md` / `briefs/meta/b2/selected_brief_factlock.md` | d5a6a14c095b5f16fe09fac76df1b939ef0482d48bd8ca3f531062d96eefb9f0 |
| `step1_chat_repro_01/conditions.json` | 2f2e894e6c26e7713e6222664750678ed987df72821e56874e2474047afe4c8d |
| `step1_chat_repro_01/run_step1.py` | 6b45af7739f290cc16c4eb16578b45e3bf34904fb4d4edf0b2c8d23bf3f79ac1 |
| 本試験 `tools/run_matrix.py`(生成・評価実行時点) | 4ba6c7c7fdd9aeb6fbf9ead7878bb49e6c618f13cf30c51b4358bab2df390d0c |
| 本試験 `tools/make_report.py`(初回実行時点。最終版は後記のとおり変更し得る) | e84bb4c6334e630a1f3ba362cd70f3ea71af18a2d41560ab7e3429df3e21458f |
| 再利用(read-only import) `er052_step2_astra_r3_01_run.py` | ca781663828d29c4bfcdaff065115d78b0a920e0c1dbb1dc80e4dee5ab2d5342 |
| 再利用 `r3_minimal_01/run_r3_minimal.py` | 2454beb91ef46cee67530391daf801c60394e8942d66ab53d4a47324f4dbaeaf |
| 再利用 `er003_v1_en_direct_vfl_01_generate.py`(JA FC `run_deviation_check`) | 63286c2b558cdcc3cd2def090bae6975ca48385e962dd53c9c70f7e116afde80 |

## 評価
- JA Fact Check: gpt-6-luna、全台帳、`run_deviation_check(hook_aware=False, include_related_fact_id=True)`(sweep `EVAL_RULES_V2.md` / R3-MINIMAL / Step2 harness と同一呼び出し・同一プロンプト)。FC・決定論指標の対象はMarkdown除去後(P1、`strip_markdown`)の本文。
- 決定論指標: `det_metrics`(字数・段落・1文段落・問い・ダッシュ・Markdown残存・記号Gate `detect_prohibited_symbols`(計測のみ)・台帳外数値)。
- 新規具体主張: Step2/sweep の (ii) `untagged_check`(5分類のうち `new_specific_claim`)。R0 を基準に増減を見る。
- 重大候補: `eval/HUMAN_CHECK_MATRIX.md`。集計: `eval/SUMMARY_MATRIX.md`。費用: `eval/COST_MATRIX.md`。ユーザー提示: `USER_PACK.md`(系列は X/Y で伏せ、対応は `_private/MAP.json`、git add 対象外)。

## 予算・単価
上限 ¥60。astra 単価は routing contract 未登録 -> 推定(gpt-6-sol 2.00/0.20/10.00 USD per 1M x2.5 = 5.00/0.50/25.00、USD/JPY=160)。トークン数は全て実測を記録。

## 実行コマンド(リポジトリの `.venv` の python を使用)
```
.venv\Scripts\python.exe er052_output\factlock_writer_trial_01\astra_revise_matrix_01\tools\run_matrix.py --phase gen --series A --yes-run-paid   # 並列プロセス1
.venv\Scripts\python.exe er052_output\factlock_writer_trial_01\astra_revise_matrix_01\tools\run_matrix.py --phase gen --series B --yes-run-paid   # 並列プロセス2
.venv\Scripts\python.exe er052_output\factlock_writer_trial_01\astra_revise_matrix_01\tools\run_matrix.py --phase eval --yes-run-paid
.venv\Scripts\python.exe er052_output\factlock_writer_trial_01\astra_revise_matrix_01\tools\make_report.py
```
(ドライラン: `--yes-run-paid` を付けない。システムの `python` には dotenv が無く、リポジトリの `.venv` が必要。)

## 出力
`runs/{A,B}/r{1,2,3}.md`(生出力)・`.p1.md`(Markdown除去後)・`.response.json`、`usage_log.jsonl`、`eval/{fc,ii}/*.json`、`eval/METRICS_MATRIX.json`、`gen_A.log` `gen_B.log` `eval.log`。
