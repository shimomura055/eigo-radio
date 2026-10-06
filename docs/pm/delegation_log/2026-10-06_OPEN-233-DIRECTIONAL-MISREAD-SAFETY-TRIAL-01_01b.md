## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01(委任_01b: Trial対象セット構築+Ledger側正解の事前登録)。並列委任_01a(母集団集計)、_01c(script骨格)、_01d(ACTIVE_TASK/OPEN_ITEMS)が同時進行。**書込先は`er052_output/open233_directional_misread_trial_01/testset_01.{json,md}`、同`synthetic_reversal_01.py`、`docs/pm/RESULT_PACKET_TRIAL_01B.md`、`docs/pm/delegation_log/`のみ。他ファイル・SSOT・gold定義・git操作なし。LLM呼出なし。**
作業方式: Write/Editは1回40行以内、Bash heredoc不使用、説明最小。T-0は委任文をWrite+Edit追記で逐語保存。時間目安35分。

## 性質/到達上限Status/禁止事項
性質: ¥0データ準備。到達上限: 対象セット完成(事前登録)。禁止: 有料API/残11 run/Production変更/gold定義(`SAFETY_CRITICAL_CLAIM_DEFS`)の変更/KPI変更/人工文のLLM生成(決定論で作る)。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う(一覧外は理由記録)。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_01b.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: ¥0のため対象外。

## ユーザー指示(原文、要点)
> Trial対象: 最低限、HC-012今回実例/A5-0等の既知方向反転gold/過去の方向・比較系Safety例/正常な忠実文/人工的に作った方向反転文10〜20件程度を含める。必要なら同一重要例を複数回反復し、AI揺れも見る。
> 評価項目: 真の方向反転を検出できた件数/見逃し件数/正常文を誤って方向反転とした件数/判断不能件数/Ledger側方向性判定の精度/記事側方向抽出の精度/最終機械比較の結果。

## 固定分類(enum、Opus推奨。script側(委任_01c)と同一にする)
`result_state` ∈ {AVAILABLE(利用可能・稼働・復元済み), STOPPED(停止・撤回・中止), PAUSED(一時停止・当面停止), INCREASED, DECREASED, UNCHANGED, STARTED, ENDED, EXPANDED, NARROWED, NOT_MENTIONED, UNCLEAR}。方向対: AVAILABLE↔STOPPED/PAUSED、INCREASED↔DECREASED、STARTED↔ENDED、EXPANDED↔NARROWED。PAUSED vs STOPPEDは「一時性の差」で逆転扱いしない。

## 作業内容
A. **実例の収集**(各項目: id, source, fixture, fact_id, Ledger fact本文(逐語), article_sentence(逐語), expected_ledger_state(enum), expected_article_state(enum), expected_compare ∈ {SAME, REVERSED, NOT_MENTIONED, UNCLEAR}, label(真の反転/忠実/曖昧), origin):
 1. HC-012: `er052_output/open233_prod_e2e_02/runs/meta_run03_advanced.json` Grep `HC-012` →紐づく全claim(Opus指摘では32文、同fixtureの他runも`runs/meta_run03_*.json` Grep `HC-012`で収集)。反転文「restored the human concierge feature…」=REVERSED、忠実文(rolled back系)=SAME。Ledger本文は`er019_output/meta/run_03/ledger/verified_fact_ledger.txt` Grep `HC-012`。
 2. A5-0: runner `er052_open233_self_recovery_flow_runner_01.py` Grep `SAFETY_CRITICAL_CLAIM_DEFS` →範囲ReadでA5-0のfixture/fact_id/記事文(「temporarily put back」等)を特定→Ledger本文を取得。
 3. 比較・方向系過去例: HF-009(K16/K19)、委任_61の比較方向反転ケース: `docs/pm/delegation_log/` Grep `委任_61|K16|K19|HF-009|方向反転` →特定できた範囲で記事文・Ledger行。`er052_output/open233_directional_misread_offline_01/sensor_quality_01.md`の手順C表も参照(そこにK16/K19/D61合成の文があれば流用)。
 4. 忠実文(正常): 新9 run jsonの重大4件以外から、状態変化語を含むfactに紐づくclaim(ラベル「問題なし」、`er052_output/open233_prod_e2e_02/labels/labels_merged.json`参照)を**20件以上**。
 5. 非該当fact(状態変化なし)に紐づく忠実文を5件(NOT_MENTIONED/SAME側の挙動確認用)。
B. **人工反転文(決定論、10〜20件)**: `synthetic_reversal_01.py`で、忠実文(A-4)に対し方向語の対訳置換テーブル(restored↔rolled back, resumed↔suspended, increased↔decreased, expanded↔narrowed, started↔stopped, reinstated↔withdrew, raised↔lowered, extended↔shortened, added↔removed 等)を適用して生成。置換が成立した文のみ採用、元文と対で記録(expected=REVERSED)。LLM不使用。gold非変更、Trial専用。
C. **Ledger側正解の事前登録**: 対象fact(A-1〜5で登場する全fact)について、Fableの代理として`expected_ledger_state`と`has_direction`(true/false)を、Ledger本文の逐語根拠を付けて登録。曖昧なものは`UNCLEAR`+理由。委任_01aの語彙近似とは独立に判断(あとで突合する)。
D. **反復指定**: HC-012反転文・A5-0・HF-009は`repeat: 3`、その他は`repeat: 1`。
E. 出力: `testset_01.json`(項目配列+enum定義+集計: 件数内訳)、`testset_01.md`(内訳表: 真の反転/忠実/人工反転/非該当/曖昧、各件数と合計call見込み=項目数×repeat)、`docs/pm/RESULT_PACKET_TRIAL_01B.md`(要約10行+T-0+一覧外Read理由+未特定の過去例があればその旨)。

## 事前指定Read/Grep一覧
上記A〜Cに記載。run json・labels jsonは全文Readせずscript/Grepで抽出。gold定義は範囲Readのみ(変更禁止)。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_01b.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_01b.md_check.json`
2. `.venv\Scripts\python.exe er052_output\open233_directional_misread_trial_01\synthetic_reversal_01.py`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_TRIAL_01B.md`。最終報告8行以内(内訳件数、合計call見込み、未特定例)。
