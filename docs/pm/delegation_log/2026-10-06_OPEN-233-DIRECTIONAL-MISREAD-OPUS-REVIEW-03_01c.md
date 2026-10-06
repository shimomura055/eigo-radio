## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03(委任_01c: TRIAL-01/02の差分整理(prompt逐語・規則・結果)+全体構造の整理。Opus投入用Evidence packet③)。並列委任_01a/01b/01dが同時進行。**書込先: `docs/pm/evidence_opus_review_03/03_trial01_02_diff.md`(新規)、`docs/pm/RESULT_PACKET_OR03_01C.md`、`docs/pm/delegation_log/`。他ファイル・コード・SSOT・git操作なし。LLM呼出なし。**
作業方式: Write/Editは1回40行以内、Bash heredoc不使用、説明最小。packetは150行以内。T-0はWrite+Edit追記で逐語保存。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: ¥0 read-only整理。禁止: 有料API/Prompt修正の本実装/Production変更/gold・KPI変更/評価の断定(事実と【推測】を分ける)。Opus Gate: 本管理IDでOpusレビューを別途実施。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_01c.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
> 別の見逃し・誤爆を増やさないか: 同義表現/主語省略/比較表現/increase・decrease等の方向表現/一つのFactに複数事象/記事側の言い換え、について新修正が新しい盲点を作らないか。
> 今回の修正は根本原因に対する修正なのか、D61だけを通すための過学習的patchなのか。「Ledger側の事象抽出→記事側blind事象選択→機械比較」という全体構造自体に、これ以上Trialを繰り返す前に直すべき問題がないか。

## 作業内容
A. Prompt逐語: TRIAL-01 `er052_open233_directional_trial_01.py`とTRIAL-02 `er052_open233_directional_trial_02.py`のLedger側prompt・記事側prompt・schema(Grep `prompt|schema|PROMPT|SCHEMA|def build_` →範囲Read)を逐語で並記し、差分を箇条書き。
B. 規則の差分: 記事側の対象指定(01=Ledger側の各subject_xを1つずつ渡して全event比較/02=ラベル一覧から1つ選択→選択eventのみ比較)、同一subject内複数eventのtie-break(02: SAME/SAME_FAMILY優先、なければworst)、NONE/ラベル外/quote欠落の扱い、compare規則(方向対・SAME_FAMILY・UNCLEAR条件)を表に。
C. 結果差分(`trial_summary_02.md`の前回比表と`regression_vs_trial01.md`から転記): gold別、誤爆、UNCLEAR/NOT_MENTIONED、人工反転(リスト内/外)、曖昧、費用/run。項目単位で「01検出→02見逃し」「01見逃し→02検出」「01誤爆→02解消」のid一覧(results jsonlをPythonで突合)。
D. ユーザー指定6観点(同義表現/主語省略/比較表現/方向表現/複数事象/言い換え)ごとに、今回のtestsetで該当する項目idと01/02の結果を表にし、「修正案(実体名付与+意味上の部分一致)で変わりうる箇所」を事実ベースで記載(評価はOpus)。
E. 全体構造の整理: Ledger側抽出→記事側blind選択→機械比較、の各段で「情報が失われる/判断が偏る」可能性のある箇所を列挙(事実: 何を渡し何を渡さないか。例: 記事側はラベルのみでLedger本文・stateを見ない=blindの代償として対応付けの手掛かりが少ない)。設計doc `docs/pm/design_open233_directional_misread_safety_01.md` §8/§14のOpus推奨(事象リストから記事側に選ばせる/enum固定値/未言及=通過)との整合・不整合。
F. packet末尾に「Opusが確認すべきファイル一覧」。

## 事前指定Read/Grep一覧
scriptはGrep→範囲Read。`trial_summary_02.md`は前回比表のGrep `前回|TRIAL-01` →範囲。results jsonlはPythonで突合のみ。設計docはGrep `§8|§14|事象リスト|enum` →範囲Read(40行以内)。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_01c.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_01c.md_check.json`

## SSOT追記文
なし。
## Git
なし。
## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_OR03_01C.md`: packetパス、C要点(01→02で変わったid数)、T-0、一覧外Read理由。最終報告5行以内。
