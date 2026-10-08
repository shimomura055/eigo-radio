# FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_04c(委任文の保存。Opusレビュー全文は docs/pm/opus_l2_review_factlock_sweep_eval_01.md に逐語保存)

## 管理ID

FACTLOCK-WRITER-REDESIGN-TRIAL-01(委任_04c: sweep評価。Opus任意レビュー反映→判定ノイズ基準の先行測定→生成完了後に本評価・集計)。並行タスクあり: 同管理ID委任_04b(生成33本・照合・文体指標。書込先sweep_01/runs/・sweep_01/MANIFEST.json・sweep_01/eval/CHECK_SUMMARY_SWEEP.md・sweep_01/eval/STYLE_METRICS.md・sweep_01/PREREGISTRATION_SWEEP.md[改訂履歴]・docs/pm/RESULT_PACKET_FACTLOCK_SWEEP.md・harness)、PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01委任_03(配線・git)。本委任は04bの完了まで それらのファイルに書き込まない。git操作禁止・SSOT編集禁止。

## 性質/到達上限Status/禁止事項

- 性質: Trial評価。到達上限Status: EVALUATED。しきい値は「読み規則」として事前固定するが、推奨は書かない。
- 隔離規則: 書込は er052_output/factlock_writer_trial_01/sweep_01/eval/ 配下(04bが書くCHECK_SUMMARY_SWEEP.md・STYLE_METRICS.mdは読み取りのみ)、sweep_01/tools/eval_sweep.py等の新規tool、docs/pm/RESULT_PACKET_FACTLOCK_SWEEP_EVAL.md(新規)、docs/pm/opus_l2_review_factlock_sweep_eval_01.md(新規)、本ファイル(+_check.json)。PREREGISTRATION_SWEEP.mdへの「評価規則v2」節の追記は04b完了後。既存tools/eval_fl.pyは編集せず、新規eval_sweep.pyに中立化した判定文を実装。
- 費用: 上限¥120(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。見込み: ノイズ基準≈¥3、pairwise 33対x2順序≈¥10、5.6併用(O1)≈¥30、多様性LLM所見≈¥5、重大候補抽出用の軽量rubric≈¥40。
- 開始条件(本評価): docs/pm/RESULT_PACKET_FACTLOCK_SWEEP.md のStatusがGENERATED(04b完了)。満たすまで5分間隔polling、最大150分。待機中は先行作業を行う。
- Opus独立技術レビューGate: 任意レビュー実施済み。Fable判断: M1〜M7採用、O1・O2・O4採用、O3は次段へ。
- 時間見込み: 先行作業40分+本評価40分+集計20分。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(委任文のとおり: 再読しない、Grep→範囲Read、git出力不使用、T-0=本ファイル保存+check_delegation_prompt実行をRESULT_PACKETへ1行、TTSなし、費用上限Guardrail)。

## ユーザー指示(原文)
「…5でも10でもパターンを振って方向性を決めるのが良い…時間重視で一回の評価で広く知見がえられる、方向性が決めれる、そのような評価を考えてください。」(2026-10-08)

## KPI provenance
pairwiseスコア・ノイズ基準・決定論数値チェック・増幅(ii)・多様性: fresh。S0/S5参照記事: reuse。重大候補: LLM抽出→人間確認待ち。E2E自己確認: No。

## Opus台帳更新
SSOT編集禁止のため、RESULT_PACKET_FACTLOCK_SWEEP_EVALにM1〜M7/O1〜O4の採否・状態表と台帳追記文案を記載。

## 実行手順の要約(委任文の「実行コマンド全文」)
0. 委任文保存+check。
1. 先行: Opusレビュー保存。EVAL_RULES_V2.md作成(M1面白さ判定文逐語[「以下は同じニュースをもとにした、日本語ラジオで読み上げる記事AとBです。あなたが聞き手だとして、続きを聞きたい、誰かに話したくなるのはどちらですか。事実の正確さは別に評価するので考えなくてかまいません。winnerはA/B/tie。reasonは、そう感じた箇所を具体的に挙げて日本語2文以内で。」developer=「あなたはラジオ番組の聞き手です。」主judge=gpt-6-luna、併用=gpt-5.6-luna]、M3スコア化[勝ち1/割れ0.5/負け0、brief別3つ、合計0-3、割れ率]、M2不戦勝assert、M4ノイズ基準[S0 r1対r2]、M5読み規則[3brief全勝かつ合計>=2.5=明確に上/逆=明確に下/他=同等、metaは数値規則軸では読まない、S9でR3不採用はS4同等と別記、S11はS3/S4・S12はS5と比較]、M6事実主指標[重大全件HUMAN_CHECK/決定論数値チェック/増幅(ii)/JA FC MAJOR・STOP率、軽微は参考列でEN由来分離、(i)は付録、「事実は変わらない=検出できる差がない」注記]、M7多様性[比喩領域重複数/決まり文句共通数、bigram Jaccardは付録、LLM所見は変種名を伏せ11組シャッフル1 call]、論点4文体指標[DIAGNOSISの6指標を1000字正規化、O2勝者-敗者の符号集計、O4台帳逐語n-gram率]、出力表の列)。
2. tools/eval_sweep.py実装(mockテスト最小限)。ノイズ基準を先に実行(≈¥3)しeval/NOISE_BASELINE.mdへ。
3. 重大候補抽出用の軽量rubric call設計。
4-8(開始条件後): PREREGISTRATION_SWEEP.mdへ評価規則v2追記→盲検コピー(eval/blind_sweep/、MAP非公開)・pairwise(各変種x3 brief対S0、2順序、6-luna主+5.6併用)・S5対S0アンカー6判定→事実側(決定論数値、(ii)増幅、JA FC/STOP、重大候補→HUMAN_CHECK_SWEEP.md)→多様性・文体・O2・O4→SUMMARY_SWEEP.md(表+10軸要約+「面白さ同等以上かつ決定論指標非悪化」変種一覧+言えること/言えないこと)。

## Git
git操作禁止。commit候補: sweep_01/eval/**(_private/除外)、sweep_01/tools/eval_sweep.py、docs/pm/opus_l2_review_factlock_sweep_eval_01.md、docs/pm/RESULT_PACKET_FACTLOCK_SWEEP_EVAL.md、委任文(+check.json)。

## 報告
docs/pm/RESULT_PACKET_FACTLOCK_SWEEP_EVAL.md(ヘッダ: 管理ID・Status=EVALUATED[または待機タイムアウト]・実費/¥120・git未操作)。本文: 1.一覧表(11変種+S5アンカー) 2.ノイズ基準の幅 3.10軸の要約(事実のみ) 4.重大候補件数とHUMAN_CHECKパス 5.多様性・文体・O2符号集計・O4転記度 6.悪化項目 7.限界 8.M/O採否表と台帳文案 9.問題・残作業、check結果、一覧外Read。推奨は書かない。

## 事前指定Read一覧
Opusレビュー全文(本ファイル元の委任文末尾)→docs/pm/opus_l2_review_factlock_sweep_eval_01.md へ逐語保存 / tools/eval_fl.py L130-200 / PREREGISTRATION_SWEEP.md 全文、DESIGN_SWEEP_01.md §2〜§3 / DIAGNOSIS_01.md 文体指標定義節・比喩語彙表 / S0参照r1/r2本文(all6_writer_redesign_necessity_01) / (開始条件後)MANIFEST.json、runs/**/revision2.md、CHECK_SUMMARY_SWEEP.md、STYLE_METRICS.md、factlock_check_r0/r2.json

## 事前指定Grep一覧+追記位置・更新位置の手順
Grep PW_INSTR|winner|reason in eval_fl.py→eval_sweep.pyに中立化判定文を実装 / Grep "status"|GENERATED in RESULT_PACKET_FACTLOCK_SWEEP.md→開始条件判定 / 追記位置: sweep_01/eval/EVAL_RULES_V2.md(先行)、04b完了後にPREREGISTRATION_SWEEP.md末尾へ「評価規則v2」節。結果は eval/SUMMARY_SWEEP.md、HUMAN_CHECK_SWEEP.md、eval/_private/MAP_SWEEP.json。

## 実行コマンド全文
cwd=C:\Users\tensh\eigo-radio、python=.venv\Scripts\python.exe -X utf8。0. .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_04c.md --json-out docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_04c.md_check.json
