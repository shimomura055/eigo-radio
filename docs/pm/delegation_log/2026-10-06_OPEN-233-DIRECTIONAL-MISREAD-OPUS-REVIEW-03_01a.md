## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03(委任_01a: D61見逃しのtrace整理。Opus投入用Evidence packet①)。並列委任_01b/01c/01dが同時進行。**書込先: `docs/pm/evidence_opus_review_03/01_d61_trace.md`(新規)、`docs/pm/RESULT_PACKET_OR03_01A.md`、`docs/pm/delegation_log/`。他ファイル・コード・SSOT・git操作なし。LLM呼出なし。**
作業方式: Write/Editは1回40行以内、Bash heredoc不使用、説明最小。packetは120行以内。T-0はWrite+Edit追記で逐語保存。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: ¥0 read-only整理。禁止: 有料API/Prompt修正の本実装/Production変更/gold・KPI変更/原因の断定(事実と仮説を分け、仮説は【推測】)。Opus Gate: 本管理IDでOpusレビューを別途実施(本委任はその入力)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う(一覧外は理由記録)。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_01a.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
> D61見逃しの原因分析は正しいか。現在の仮説: Ledger側の事象名が「上げ幅」「水準」のように抽象的すぎたため、記事側AIが対象文と対応付けられずNONE/NOT_MENTIONEDと判断した。これが本当に主因か、artifact・Trial結果を根拠に確認する。他に原因がある場合は明示すること。

## 作業内容(すべて逐語引用+出典パス・行/record id付き)
A. D61(G-03)の定義: `er052_output/open233_directional_misread_trial_02/testset_02.json`からG-03のrecord全体(article_sentence、article_context、fact_id、expected_*、origin)。TRIAL-01の`testset_01.json`のG-03と差分があれば併記。
B. Ledger HF-009原文: `er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt` Grep `HF-009` →block逐語。`ledger_truth_02.json`のHF-009登録(events/aliases/quote)。
C. Ledger側抽出(TRIAL-02): `run/ledger_cache.json`のHF-009 rep1〜3のevents逐語(subject_x/result_state/quote)。TRIAL-01のLedger側抽出(`../open233_directional_misread_trial_01/run_same_blind/results_same_blind.jsonl` G-03 recordの`ledger`/`repeat_events`)との差分。
D. 記事側に実際に渡した入力: `er052_open233_directional_trial_02.py` Grep `def build_article_prompt|selected_subject|NONE|subject` →記事側prompt本文(逐語)と、G-03で渡されたラベル一覧(`run/results_merged.jsonl` G-03 recordの`repeats[*].ledger_events_subjects`)。応答(`selected_subject`/`article_state`/`article_quote`)3反復。call_log(`run/shard_*/call_log*`)にraw応答があれば該当3件の逐語。
E. 対比: 同じHF-009に紐づく他項目(G-04/G-05曖昧、F-09/F-10、S-06等HF-009由来の人工反転)で記事側が選択に成功した例(selected_subject≠NONE)と失敗した例を表にし、記事文の表現(「Brent crude oil prices fell」「pared gains」等)と選択結果の関係を整理。TRIAL-01でG-03がrep2/3で検出できたときのarticle側応答(subject_x指定方式)も併記。
F. 事実から言えること/言えないこと: (i)仮説「ラベルの抽象性」を支持する事実、(ii)反する事実(例: 同じラベルで他の文は選択できた、など)、(iii)代替仮説候補(例: G-03の記事文が「上げ幅」「水準」のどちらにも直接対応しない比較表現である/選択promptの「NONE」への誘導/前後文の有無/testsetのexpected_event_subject設定)を列挙(【推測】)。断定しない。
G. packet末尾に「Opusが確認すべきファイル一覧(パス・行)」。

## 事前指定Read/Grep一覧
上記A〜Eのファイルを、Grep/Pythonで該当recordのみ抽出(jsonl全文Read禁止)。scriptはGrep→範囲Read。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_01a.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_01a.md_check.json`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_OR03_01A.md`: packetパス、F(i)(ii)(iii)の要点各1行、T-0、一覧外Read理由。最終報告5行以内。
