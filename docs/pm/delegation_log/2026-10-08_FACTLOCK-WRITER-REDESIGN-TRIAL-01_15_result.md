# FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_15 結果(ASTRA-REVISE-MATRIX-01、2026-10-08)

Status: **MEASURED(人間確認待ち)**。Production コード・CURRENT_SPEC は未変更。ユーザー Go 取得済み。

## 1. 実費・所要・トークン
- 総額 約¥48.48(推定): 生成6本 ¥45.77(**astra 単価は routing contract 未登録のため gpt-6-sol 2.00/0.20/10.00 USD per 1M x2.5 の推定**、USD/JPY=160)+ JA FC 7本 ¥1.31(luna、実測トークン x 登録単価)+ (ii) 7本 ¥1.40(usage 非取得のため 1本 0.2 円の概算計上)。予算上限 ¥60 内、停止なし。
- 生成6本のトークン合計: input 4402 / cached 0 / output 10563(うち reasoning 6303)。
- 所要: 生成は A/B 2プロセス並列で約2分(A 合計124秒、B 合計119秒の逐次)、評価(ii 7本+FC 7本、4スレッド)98秒。

## 2. R0 突合
R0 = `er052_output/factlock_writer_trial_01/step2_astra_r3_01/inputs/FL_R0/meta/b2/source.md`(SHA 4dd147ff...)。元 = `.../runs/meta/control/b2__factlock__r1/ja_writer/original.md`(SHA 0b672113...、採用 rep = r1、r1/r2 とも completed)。`strip_tags(original.md).strip()+"\n"` が source.md とバイト一致、source_prestrip.md が original.md とバイト一致を確認(差は末尾改行1つのみ)。台帳 = 同 run の `research_ledger/verified_fact_ledger.txt`(SHA ea0ce587...)、B3 brief = 同 run の `storyline_b3/selected_brief.md`(= `briefs/meta/b2/selected_brief_factlock.md`、SHA d5a6a14c...)。

## 3. 7本の指標表
系列A = ユーザーPromptのみ、系列B = 熟練編集者。字数等はタイトル行除く。FC・決定論指標は Markdown 除去後(P1)本文。

| 本 | FC MAJOR | FC MINOR | 新規具体主張(ii) | 字数 | 段落 | 1文段落 | 問い | ダッシュ | 台帳外数値 | Markdown残存(raw #行/**) | 記号Gate(raw/P1) | 費用(推定円) | 秒 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R0 | 0 | 0 | 0 | 727 | 6 | 0 | 0 | 0 | 0 | 0/0 | 0/0 | - | - |
| A_r1 | 0 | 0 | 2 | 990 | 8 | 0 | 2 | 0 | 0 | 1/0 | 0/0 | 5.14 | 31.9 |
| A_r2 | 0 | 0 | 0 | 961 | 9 | 0 | 3 | 0 | 0 | 1/0 | 2/2 | 8.43 | 51.5 |
| A_r3 | 0 | 1 | 2 | 989 | 9 | 0 | 3 | 0 | 0 | 1/0 | 4/4 | 7.50 | 40.2 |
| B_r1 | 0 | 0 | 0 | 894 | 8 | 0 | 3 | 1 | 0 | 1/0 | 0/0 | 8.83 | 41.6 |
| B_r2 | 0 | 0 | 0 | 969 | 11 | 1 | 1 | 1 | 0 | 1/0 | 0/0 | 6.43 | 30.9 |
| B_r3 | 0 | 0 | 3 | 928 | 12 | 1 | 2 | 0 | 0 | 1/0 | 0/0 | 9.45 | 46.5 |

## 4. FC 指摘全文
MAJOR は全7本で 0件。overall_status は全7本 LEDGER_COMPLIANT。MINOR は A_r3 に1件のみ:
- NG文: 「利用者が知らされていない」「AIに頼んだはずが、説明なしで人間にバトンタッチ」
- 型: changed_scope, unsupported_new_claim(related_fact_id MUSE-HC-012)
- 台帳: MUSE-HC-012「MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。」
- 理由: Ledgerは契約スタッフが電話を担当するテストに適切な開示がなかったとするが、誰に開示されていなかったかまでは特定していない。記事はMuseを依頼した利用者が知らされていなかったと対象を絞っている。

## 5. 重大候補(HUMAN_CHECK_MATRIX.md)
MAJOR 0件、主体・因果・否定型の MINOR 0件。参考として上記 A_r3 の MINOR(範囲限定型)と、(ii) new_specific_claim 該当文(A_r1 2、A_r3 2、B_r3 3)を同ファイルに列挙済み(いずれも断定・一般化の型で新規固有事実ではない)。

## 6. (ii) 新規具体主張(R0 = 0件比)
A: r1=2 → r2=0 → r3=2、B: r1=0 → r2=0 → r3=3。段が進むと単調に増えるわけではない。該当文全文は `eval/SUMMARY_MATRIX.md` と `HUMAN_CHECK_MATRIX.md`。

## 7. USER_PACK.md
`er052_output/factlock_writer_trial_01/astra_revise_matrix_01/USER_PACK.md`。7本の本文全文(Markdown 見出し・太字除去後、各本文の冒頭に字数のみ)。段は R0/R1/R2/R3 を明示、系列は X/Y で伏せる(FC 結果は不掲載)。X/Y と系列の対応は `_private/MAP.json`(git add 対象外。ローカルのみ): X = 系列A(ユーザーPromptのみ)、Y = 系列B(熟練編集者)。

## 8. COST_MATRIX の要点(astra 単価は推定)
- 累積(推定円): A は R1のみ 5.14 / R1+R2 13.57 / R1+R2+R3 21.06。B は 8.83 / 15.26 / 24.71。
- 同 run の Luna R1+R2 実費 ¥0.383(`cost.json` は全項目 0 円で課金未記録のため、`raw_usage_log.jsonl` の実測トークン x luna 登録単価で算出)。置換時の純増は Astra 累積から ¥0.383 を引いた値。
- 1記事セット換算: 現行約¥52(Standard 同期)/約¥43(Batch)に Astra 3段で +約¥21〜¥25(合計 Standard 約¥73〜¥77、Batch 約¥64〜¥68)、1段のみなら +約¥5〜¥9。Astra に batch 割引は仮定しない。

## 9. SSOT・Git
- REPORT §107、DECISION_LOG 本日分エントリ、REPORT_LEDGER 1行、PM_BRIEF 末尾「PM運用メモ」節に1行(ユーザー指示)を追記。
- commit hash: (commit後に追記)
- raw URL:
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_writer_trial_01/astra_revise_matrix_01/USER_PACK.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_writer_trial_01/astra_revise_matrix_01/DESIGN.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_writer_trial_01/astra_revise_matrix_01/eval/SUMMARY_MATRIX.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_writer_trial_01/astra_revise_matrix_01/eval/HUMAN_CHECK_MATRIX.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_writer_trial_01/astra_revise_matrix_01/eval/COST_MATRIX.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_writer_trial_01/astra_revise_matrix_01/tools/run_matrix.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_writer_trial_01/astra_revise_matrix_01/tools/make_report.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/REPORT_LEDGER.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/PM_BRIEF.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_15.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_15_result.md

## 10. check_delegation_prompt 結果
FAIL(想定どおり。委任文が標準テンプレート形式でないため: 必須セクション欠落[性質/事前指定Read一覧/事前指定Grep一覧/実行コマンド全文]、固定ブロックラベル E-1/D-1/G-1/F-1 欠落、「実行コマンド全文」セクションなし)。委任指示どおり続行。記録 `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_15.md_check.json`。

## 11. 未解決点・逸脱
- 逸脱: 委任文は「`python` で実行」前提だが、システム python には dotenv が無く、リポジトリの `.venv\Scripts\python.exe` を使用(最初の起動は import エラーで終了、API 支出なし、再起動)。
- 逸脱(軽微): (ii) の費用は usage 非取得のため 1本 0.2 円の概算計上(Step 2 harness と同じ扱い)。
- `docs/pm/ACTIVE_TASK.md` は未追跡の一時ファイルで、固定ヘッダはFable管理のため更新していない。
- 人間確認待ち: USER_PACK の盲検読み。FC は gpt-6-luna 自己判定、N=1 記事 x 系列あたり1本のため差が1件以内は誤差内。astra 単価は推定。
- git status に本タスクと無関係の既存差分・未追跡ファイルが多数あり、個別 add で混入させていない。
