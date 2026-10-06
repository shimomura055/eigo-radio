## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03(委任_01b: HC-012/A5-0比較資料+前回誤爆3件の再発リスク整理。Opus投入用Evidence packet②)。並列委任_01a/01c/01dが同時進行。**書込先: `docs/pm/evidence_opus_review_03/02_hc012_a5_fp3.md`(新規)、`docs/pm/RESULT_PACKET_OR03_01B.md`、`docs/pm/delegation_log/`。他ファイル・コード・SSOT・git操作なし。LLM呼出なし。**
作業方式: Write/Editは1回40行以内、Bash heredoc不使用、説明最小。packetは120行以内。T-0はWrite+Edit追記で逐語保存。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: ¥0 read-only整理。禁止: 有料API/Prompt修正の本実装/Production変更/gold・KPI変更/結論の断定(事実と【推測】を分ける)。Opus Gate: 本管理IDでOpusレビューを別途実施。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_01b.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
> 修正案: 「上げ幅」ではなく「Brent先物の上げ幅」のように、Ledger側事象へ対象の実体名を含める。記事側の事象選択では必要に応じて意味上の部分一致を許容する。Opusに、D61を拾える可能性/HC-012・A5-0を壊さないか/前回解消した正常文誤爆3件を再発させないか/事象名を具体化しすぎて別表現を拾えなくならないか、を評価させる。

## 作業内容(逐語引用+出典)
A. HC-012(G-01)・A5-0(G-02): `er052_output/open233_directional_misread_trial_02/run/results_merged.jsonl`からG-01/G-02 recordの3反復(ledger_events_subjects/selected_subject/ledger_state/article_state/compare/quotes)を表に。Ledger側HC-012のevents(`run/ledger_cache.json` rep1〜3)。記事文(testset_02.json)。TRIAL-01(同`../trial_01/run_same_blind/results_same_blind.jsonl`)の同recordとの差分。
B. 前回誤爆3件(F-09/F-10/F-19): TRIAL-01でREVERSEDになった経路(どのeventと比較してREVERSEDか)と、TRIAL-02でSAMEになった経路(選択subject)を並べる。記事文逐語。
C. 修正案の影響の事前整理(事実ベース、判断はOpus): (i)現在のLedger側subject_xラベルの一覧(10 fact×3反復、重複除去)と、「実体名を含めた場合」のラベル案(例: 機能→「ヒューマンコンシェルジュ機能」、上げ幅→「Brent先物の上げ幅」)を対応表に。(ii)各ラベル案に対し、HC-012/A5-0/F-09/F-10/F-19/G-03の記事文に実体名(または同義表現)が含まれるかを機械的にチェック(文字列一致/部分一致の有無を表に、意味上の一致は【推測】欄)。(iii)記事側が複数ラベル間で迷う可能性がある組(例: 「電話テスト」と「機能」)を列挙。
D. 記事側選択promptの現行文(`er052_open233_directional_trial_02.py` Grep `def build_article_prompt`→逐語)と「意味上の部分一致を許容」を加えた場合に変わる箇所の候補(文案は書かない、変更点の列挙のみ)。
E. packet末尾に「Opusが確認すべきファイル一覧」。

## 事前指定Read/Grep一覧
上記のjsonl/jsonはPython/Grepで該当recordのみ抽出(全文Read禁止)。scriptはGrep→範囲Read。testset_02.jsonは該当id行のみ。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_01b.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_01b.md_check.json`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_OR03_01B.md`: packetパス、C(ii)の要点(実体名が記事文に含まれる/含まれない件数)、T-0、一覧外Read理由。最終報告5行以内。
