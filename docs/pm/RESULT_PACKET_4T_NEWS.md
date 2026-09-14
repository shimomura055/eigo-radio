# RESULT PACKET — EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01(記事1/4: News、修正指示1回目R1)

## 1. Status / 使用path

**status=OK(生成成功)。**
使用path: Fableが先例(DECISION_LOG L941、Trial-09/12)を根拠に指示した
「Research経路→Ledger作成→`er003_v1_n3_01_articles_generate.run_one_pattern()`」。
Researcher/Verificationは`er003_v1_en_direct_vfl_01_generate.py`の
`build_researcher_prompt`/`build_verification_prompt`+`client.responses.create`
(web_search tool)をTrial-09/12と同一構造でtopicだけ差し替えて再現
(新規driver: `er014_output/four_type_observation_01/news/run_news_a2.py`)。
記事生成は`run_one_pattern()`をそのまま呼び出し(monkeypatch・再実装なし、
Focus Module/Point Role hintなしのNews既定)。

## 2. 記事

level=A2、word_count=406語(`length_report.json`のtotal、soft range内)。
`er014_output/four_type_observation_01/news/reader_facing_article.txt`

## 3. Ledger / Verification

Researcher: 15件下書き(web_search 9 calls)。Verification: VERIFIED
(CONFIRMED)=13件、AMBIGUOUS=1件、REJECTED=1件(web_search 12 calls)。
Ledgerへ採用したのはVERIFIED 13件のみ(先例と同一方針、未検証は含めない)。

## 4. 主要QA結果・retry・fallback

- Point Overlap/Value QA: retry 0/2、lexical_flagged=false、value_qa
  status=PASS。
- Fact Checker: status=FACT_CHECK_COMPLETED、verdict=**PASS**(1 attempt)。
- Ledger Deviation Check: overall_status=**LEDGER_COMPLIANT**(deviations=0)。
  Local Rewrite: 0 cycle(MAJOR無し)。
- Directional Fact Precheck(暫定・non-blocking advisory):
  overall_status=DIRECTION_REVIEW_REQUIRED(31件中29件が「片側のみ方向
  表現があり機械判定不能」、実際にconflictsが検出されたのはF004[EU AI Act
  GPAI FLOP閾値]1件のみ、confidence=low)。ブロッキングではなく参考指摘
  (Production設計どおり、記事は既にstatus=OKで確定済み)。
- retry回数: 記事全体retry=0、Local Rewrite cycle=0。fallback発生なし。

## 5. actual model_id

provider=openai、model_id=**gpt-5.6-luna**(全8 call共通、Researcher/
Verification/Point Role Planning/Writer/Evidence Compression/Point Value
QA/Fact Checker/Ledger Deviation Checkすべて同一)。

## 6. 費用: 量産時1記事単価(Standard同期・今回実測)

**合計 ¥70.16**(budget¥130以内)。内訳(response_idを各audit JSONの
response_idと完全一致で突き合わせて機械的に分類、推測ではない):
- Research/Ledger生成: ¥42.52(Researcher+Verification、2 call)
- Writer(Point Role Planning+Writer本体+Evidence Compression): ¥2.84(3 call)
- QA(Point Value QA+Fact Checker+Ledger Deviation Check): ¥24.80(3 call)
- rewrite/regeneration: ¥0(Local Rewrite 0 cycle)
- retry追加分: ¥0(記事全体retry=0)
- **retryなし部分=¥70.16(全額)**
開発・検証費=¥0(上記が本番相当の1本のみの実測)。

## 7. API token使用量(記事単位、全てretryなし分/通常生成分)

| provider | model_id | calls | input | output | cached_input | total |
|---|---|---|---|---|---|---|
| openai | gpt-5.6-luna | 8 | 307,109 | 39,908 | 4,471 | 347,017 |

retry追加分: 0 call/0 token(retry未発生のため該当なし)。
詳細: `er014_output/four_type_observation_01/news/observation.json`

## 8. Open Item候補

1. **CURRENT_SPEC L760「手動供給のみ」表記と先例の不一致**: DECISION_LOG
   L941系(Trial-09/12)は既存Research正式経路で新規Ledgerを作成済みだが、
   CURRENT_SPEC本文は「自動Research供給経路は未配線」との表記のまま
   (今回はFableの先例判断で進めたが、SSOT表記自体は未更新)。
2. Cost Loggerの`stage`タグが粗い(`writer_a2`1本にWriter/QA複数種別の
   呼び出しが混在)。本タスクでは`response_id`をaudit JSON側と突合せて
   事後的にWriter/QA/rewriteへ分類したが、Production自体には工程別の
   コストタグ付け機構が無い(将来の計測改善候補、今回は実装していない)。
3. Directional Fact Precheck F004(EU AI Act GPAI FLOP閾値10^23/10^25の
   数値表現)がlow-confidenceで方向不一致の可能性を示唆。記事本文は該当
   数値を明示引用していないため実害は低いと見えるが、人間レビュー推奨
   (non-blocking advisory、QAは緩めていない)。

## 9. commit対象候補一覧

新規: `er014_output/four_type_observation_01/news/run_news_a2.py`、
`er014_output/four_type_observation_01/aggregate_usage.py`、
`er014_output/four_type_observation_01/news/`配下の全成果物
(research/、a2/、reader_facing_article.txt、run_result.json、
cost_summary.json、raw_usage_log.jsonl、observation.json)、
`docs/pm/delegation_log/EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_NEWS_R1.md`
(+`_R1_check.json`)、`docs/pm/RESULT_PACKET_4T_NEWS.md`(本ファイル)。
更新: `er014_output/four_type_observation_01/progress_log.md`。
Git操作は本タスクでは実施していない(委任文の指示どおり)。

## 10. T-0結果・事前指定外Read・STOP有無

- T-0: **PASS**(reasons無し、`..._NEWS_R1_check.json`)。
- 事前指定外Read(理由付き):
  - `er003_v1_en_direct_vfl_01_generate.py`の関数定義本体(MODEL/
    REASONING_EFFORT/JSON Schema/prompt template/get_client等)
    (理由: driverがvfl01の関数を直接呼ぶため、シグネチャだけでなく
    実装詳細の確認が必要だった)。
  - `er003_v1_n3_01_articles_generate.py::run_one_pattern`本体全文
    (シグネチャ+docstring超過分、理由: out_dir配置[dirname(out_dir)/
    research/stage_b3_vfl.json]・戻り値キー・QA工程順序を正確に把握し、
    driverの出力ディレクトリ構造を誤らないようにするため)。
  - `er005_cost_logger.py`のinstall/_patch_openai本体(理由: フィールド名
    範囲指定Readだけでは`stage`/`response_id`/`web_search_call_count`
    等の集計に必要な全体構造が不明だったため)。
  - `er011_news_stage3_new_theme_ledger_trial_09.py`の`stage_build_ledger`
    /`_call_cost_usd`/`compute_cost_so_far_jpy`全文(理由: 事前指定は
    Grep範囲のみだったが、Ledger保存形式とコスト計算式を正確に踏襲する
    必要があった)。
- STOP: なし(budget超過なし、CONFIRMED facts 0件にもならず正常完了)。
