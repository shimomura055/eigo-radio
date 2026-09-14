# RESULT_PACKET: EDITORIAL-4TYPE-FOLLOWUP-01-NEWS-B1-ADDITION

## 1) status・使用path
status=OK(STOP無し、予算¥50以内)。Production正式path
`er003_v1_n3_01_articles_generate.run_one_pattern(client, theme_id,
"B1B", prompt, verified_ledger_text, topic, out_dir)`をmonkeypatchなしで
そのまま呼び出し(新規driver`er014_output/four_type_observation_01/news/
run_news_b1b.py`、既存`run_news_a2.py`からResearch/Verification部分のみ
除去した派生)。Research/Verificationは再実行せず既存
`news/research/verified_fact_ledger.txt`(VERIFIED 13件)を再利用。
A2既存成果物(`news/a2/`, `news/reader_facing_article.txt`等)は無変更。

## 2) B1記事
`er014_output/four_type_observation_01/news/reader_facing_article_b1b.txt`
(369 words、`news/b1b/`配下にaudit一式)。

## 3) B1主要QA結果
fact_verdict=REVIEW_REQUIRED(EU 10^23閾値の単位表現/AISI 50%数値の集計
表現/UN 40人任命時期の3点。Ledgerとの矛盾ではなく表現精度の指摘、
Ledger本文F004自体は"floating-point operations"と正しい)。
ledger_status=LEDGER_COMPLIANT(deviation 2件、いずれもMINOR)。
Point Overlap/Value QA: 1回目NGでDiagnostic Full Retry発火
(`point_overlap_article_retry_attempts=1`)、2回目でOK。
Local Rewrite/diff QA: 発火なし(`local_rewrite_results`/`cycles`とも空)。
Directional Fact Precheck: `DIRECTION_REVIEW_REQUIRED`(A2と同様、
advisory・non-blockingな既存挙動)。

## 4) Cross-Level Consistency判定
既存の自動Cross-Level比較機構は無し(`CURRENT_SPEC.md`該当節は仕様変更
時の運用ルールでランタイムQAではない)。手動突合(15項目、
`news/cross_level_consistency.md`)の結果、**A2/B1間の日付・数値・因果・
方向性の直接的矛盾は無し**。差分はB1B側のlevel相応の省略(企業名の一般化、
米国大統領令の省略、経過措置日の省略)のみ。

## 5) actual model_id
`gpt-5.6-luna`(provider=openai、A2/B1B双方とも全call共通)。

## 6) 費用
**News Production 1生成セット総原価(共通Research/Ledger+A2+B1)=¥98.32**
(`news/production_set_cost.json`)。内訳(機械分離できる直接費のみ、
50:50配賦なし): Research/Ledger ¥42.52(既存・再計上なし)、A2 Writer
¥2.84、A2 QA ¥24.80、B1 Writer ¥2.34、B1 QA ¥22.83、rewrite ¥0、
retry=分離不可(B1Bでretry 1回発生も、aggregate_usage.py仕様上
`retry_extra_cost_jpy=None`のためWriter/QA内に混在のまま)、
other(uncategorized)¥3.00(B1B破棄済みattempt1のEvidence Compression
呼び出しがaudit1スロット上書きで対応不能。除外・隠蔽なし)。
B1追加分の実費=¥28.16(予算¥50以内)。

## 7) API token(B1分)
input 126,173 / output 42,880 / cached 3,665 / total 169,053、10 calls
(`news/observation_b1b.json`)。

## 8) Open Item候補
- aggregate_usage.pyの`CATEGORY_FILE_PATTERNS`は、Point Overlap article
  retry発生時に「破棄されたattempt」のEvidence Compression呼び出しを
  uncategorizedにする既知の限界(audit jsonが1スロットのみで上書きされる
  設計に起因、本タスクのB1Bで¥3.00分観測)。集計精度向上が必要か
  どうかはUSER_DECISION_REQUIRED(低優先、実害は僅少)。
- B1B fact_verdict=REVIEW_REQUIREDの人間レビューへの正式な回付先
  (キュー等)の有無は本タスクでは未調査。

## 9) commit対象候補一覧
`er014_output/four_type_observation_01/news/run_news_b1b.py`,
`.../news/b1b/`(生成物一式), `.../news/cost_summary_b1b.json`,
`.../news/observation_b1b.json`, `.../news/production_set_cost.json`,
`.../news/cross_level_consistency.md`, `.../news/raw_usage_log_b1b.jsonl`,
`.../news/reader_facing_article_b1b.txt`, `.../news/run_result_b1b.json`,
`er014_output/four_type_observation_01/progress_log.md`(追記のみ),
`docs/pm/delegation_log/EDITORIAL-4TYPE-FOLLOWUP-01-NEWS-B1-ADDITION.md`,
`docs/pm/delegation_log/EDITORIAL-4TYPE-FOLLOWUP-01-NEWS-B1-ADDITION_check.json`,
`docs/pm/RESULT_PACKET_4T_NEWS_B1.md`。本タスクではGit操作自体は未実施
(委任文どおりSSOT/Git対象外)。

## 10) T-0・事前指定外Read・STOP
T-0: PASS(reasons無し、
`docs/pm/delegation_log/EDITORIAL-4TYPE-FOLLOWUP-01-NEWS-B1-ADDITION_check.json`)。
事前指定外Read: aggregate_usage.pyの集計結果検証のため
`build_response_id_category_map`/`load_records`の挙動を
`--run-dir`実引数付きの小さな診断スクリプトで確認(理由:
`aggregate_usage.py`はrun_dir直下`raw_usage_log.jsonl`固定名+
`*/audit/...`1階層下glob前提で、B1B出力(`news/b1b/`)とログ分離
[`raw_usage_log_b1b.jsonl`]の構成が委任文どおり噛み合わなかったため、
scratchpad配下に集計専用の一時ディレクトリ[コピーのみ、実artifact無改変]
を作り`--run-dir`をそこに向けて実行。実行コマンドは
`.venv/Scripts/python.exe er014_output/four_type_observation_01/
aggregate_usage.py --run-dir <scratchpad>/b1b_agg --out
er014_output/four_type_observation_01/news/observation_b1b.json`)。
STOP: 無し。
