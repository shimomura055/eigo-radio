# 委任_06 受領全文(FACTLOCK-WRITER-REDESIGN-TRIAL-01、2026-10-08)

## 管理ID

FACTLOCK-WRITER-REDESIGN-TRIAL-01(委任_06: R3最小指示Trial「R3-MINIMAL-01」。既存「6×現行」記事12本へ、ユーザー提示の1文指示でRevise 3回目を追加し、面白さ・事実逸脱を測る)。並行タスクあり: 同管理ID委任_04b(sweep生成、4並列、`sweep_01/`)、委任_04c(sweep評価準備、`sweep_01/eval/`)、`PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01`委任_03(配線・git)。本委任はそれらのファイルに書き込まない。git操作禁止・SSOT編集禁止。

## 性質/到達上限Status/禁止事項

- 性質: Trial(小規模比較)。到達上限Status: `MEASURED`。しきい値・推奨なし。
- 隔離規則: 書込は `er052_output/factlock_writer_trial_01/r3_minimal_01/` 配下、`docs/pm/RESULT_PACKET_FACTLOCK_R3.md`(新規)、`docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_06.md`(+`_check.json`)のみ。既存harness・Production code編集禁止。API並列は**2まで**(sweepが4並列で稼働中、メモリ配慮)。
- 費用: 上限¥60(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。見込み≈¥45(R3 24 call≈¥20、JA FC 24 call≈¥12、pairwise 48 call≈¥10、記号Gate確認¥0)。
- Opus独立技術レビューGate: 非該当(既存Revision段の指示文を1パス追加する探索。構造変更なし)。
- 時間見込み: ≈60分(harness 20分/実行20分/評価・集計20分)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Readを基本。G-1: git出力は使わない。F-1: transcript退避不要。T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ全文保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2: TTSなし。T-3: 費用上限はGuardrail(上記定型文)。

## ユーザー指示(原文)

「Chatgptに『事実は変えずにエンターテイメント性をもっと上げた記事にReviseください』といったら、良くなりました。元の設計(Writerに自由に書かせる)よりもまだ一歩というところですが、だいぶましです。参考にしてみて下さい。(R3を設ける? R1,R2のPromptを振ってみるetc)」(2026-10-08)。ユーザーはmeta b2の6×現行記事(「AI電話の舞台裏に、人間の助演がいた」)を元に、ChatGPTで1パスRevise版を得た。特徴: 冒頭にセリフ+転換のフック、短段落、問いかけ、比喩は「舞台」1系統のまま新しい像で展開、事実の歯止めは1箇所、末尾に一言のオチ。

## KPI provenance欄

pairwiseスコア・JA FC逸脱・文体指標: **fresh**。元記事(6×現行 R2)12本: **reuse**。E2E自己確認: No。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- 元記事12本: `er052_output/all6_writer_redesign_necessity_01/runs/{meta,hormuz,space_weapons}/control/b{1,2,3,4}__all6__r1/ja_writer/revision2.md`(r1がSTOPで無いbriefはr2を使う。存在確認してから)
- 台帳: `er052_output/open233_b3_trial_01/runs/<slug>/nb/V0/b<i>/research_ledger/verified_fact_ledger.txt`
- `er019_family_x_ja_writer_o_r1_r2_01.py`: Grep `REVISION_INSTRUCTIONS|previous_response_id|call_fresh|def _call` →該当範囲Read(R1/R2の呼び出し方・連鎖・fallback書式・記号禁止ブロックの取得方法。R3-chainはR2の`response_id`が必要だが既存runには保存されていない可能性→その場合はR3-chainを「R2本文を渡したうえで現行R1/R2と同じ指示ブロック構成(記号禁止ブロック込み)で呼ぶ」近似とし、差をRESULT_PACKETに明記)
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `def run_deviation_check` →該当範囲Read(JA FCの呼び方。model=gpt-6-luna明示)
- `er052_factlock_sweep_01_run.py`: Grep `call_fresh|strip|retag` →連鎖切り呼び出しの実装(流用)
- `er052_output/factlock_writer_trial_01/v2_design/DIAGNOSIS_01.md` 文体指標定義・比喩語彙表
- `er052_output/factlock_writer_trial_01/tools/eval_fl.py` L130-200(pairwise流用元。**判定文は下記中立版に差し替え**)

## 事前指定Grep一覧+追記位置・更新位置の手順

- 2アーム: **R3-fresh**=新規context、入力=「以下の記事:\n\n{R2本文}\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。」(ユーザー文を逐語。記号禁止ブロックは現行R1/R2と同じものを付与し、台帳・briefは渡さない)。**R3-chain**=上記のとおりR2 response_idが無い場合は近似実装(現行Revision指示ブロック構成でR2本文を渡す)。model=gpt-6-luna、reasoning high(現行と同じ)。
- 事実逸脱: 各R3出力をJA FC(`run_deviation_check`、全台帳、gpt-6-luna)で判定→MAJOR/MINOR/COMPLIANT・10種flag。比較として元R2のJA FC結果(既存run `ja_writer/audit/deviation_checks`から読む。無ければ元R2も再判定、+¥6)。
- 面白さ: 各R3出力 対 元R2 をpairwise、判定文(中立版、逐語): 「以下は同じニュースをもとにした、日本語ラジオで読み上げる記事AとBです。あなたが聞き手だとして、続きを聞きたい、誰かに話したくなるのはどちらですか。事実の正確さは別に評価するので考えなくてかまいません。winnerはA/B/tie。reasonは、そう感じた箇所を具体的に挙げて日本語2文以内で。」developer=「あなたはラジオ番組の聞き手です。」順序入替2回、judge=gpt-6-luna。スコア: 2順序とも勝ち=1、割れ=0.5、2順序とも負け=0。brief別・テーマ別・合計、割れ率。
- 文体指標(決定論): です・ます率、アラビア数字/1000字、仮定語、問い、比喩種数(語彙表)、字数、「ではありません」型、台帳との逐語n-gram率(6-gram一致率)。元R2との差。
- 記号Gate: 既存の禁止記号チェック関数を適用し発火件数を記録(STOPはしない)。
- 追記位置: `r3_minimal_01/runs/<slug>/b<i>/{r3_fresh.md,r3_chain.md,fc_fresh.json,fc_chain.json,pairwise_*.json}`、`r3_minimal_01/SUMMARY_R3.md`、`r3_minimal_01/MANIFEST.json`。

## 実行コマンド全文

cwd=`C:\Users\tensh\eigo-radio`、python=`.venv\Scripts\python.exe -X utf8`。
0. 委任文全文保存+検証: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_06.md --json-out docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_06.md_check.json`
1. harness `er052_output/factlock_writer_trial_01/r3_minimal_01/run_r3_minimal.py`(新規。`require_model_or_override("B1_WRITER","gpt-6-luna",override_reason="FACTLOCK R3-MINIMAL-01")`経由、cost記録はraw usageから6-luna単価で計算)。mockテスト1本(dry-runでAPIなし・入力構成)。
2. 実行: `.venv\Scripts\python.exe -X utf8 er052_output\factlock_writer_trial_01\r3_minimal_01\run_r3_minimal.py --arms fresh,chain --budget-jpy 60 --parallel 2 --yes-run-paid`
3. 評価・集計→`SUMMARY_R3.md`: アーム別(fresh/chain) pairwiseスコア合計(/12)・brief別・割れ率、JA FC MAJOR/MINOR件数(元R2との比較、10種flagの内訳)、文体指標の差、n-gram率、記号Gate発火、費用/本、所要秒。ユーザー提示のmeta b2については、R3-fresh出力の全文を`SUMMARY_R3.md`に掲載(ユーザーのChatGPT版と読み比べ用)。

## SSOT追記文

なし。RESULT_PACKETにDECISION_LOG追記文案(ユーザー提示のR3最小指示を試行)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

git操作禁止。commit候補: `r3_minimal_01/**`、`docs/pm/RESULT_PACKET_FACTLOCK_R3.md`、委任文(+check.json)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FACTLOCK_R3.md`(ヘッダ: 管理ID・Status=MEASURED・実費/¥60・git未操作)。本文: 1. 結果表(fresh/chain × 面白さスコア・割れ率・JA FC MAJOR/MINOR・文体差・n-gram率・記号Gate・費用)。2. テーマ別・brief別の符号。3. meta b2のR3-fresh全文。4. 事実逸脱の中身(MAJOR/MINORの引用、3件まで)。5. 悪化項目。6. 限界(N=12、LLM判定、chain近似の有無)。7. 問題・残作業、check_delegation_prompt結果、一覧外Read。推奨は書かない。
