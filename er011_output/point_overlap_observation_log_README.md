# point_overlap_observation_log.jsonl README

管理ID: OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01
(Part 2、ユーザー正式決定A-UDR-22、2026-09-09)。

## 目的

`OPEN_ITEMS.md` OPEN-134行(A-UDR-7観測へ統合)が定める観測Exit条件の
実施記録先。G1修正(前回Point本文を診断promptへ渡す回帰修正)後も
「Point Overlap問題が解決した」とは扱わず、Production正式pathでの
記事生成runにおける残存NG要因を継続観測するための記録ファイル。

**本タスク(OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01)では、
このファイルとREADMEの雛形のみを作成する。実際の観測record追記は、
今後のProduction記事生成run(A-Family通常News・Trend Synthesis、
A2/B1B)実施時に別タスクで行う。**

## 観測対象・Exit条件(OPEN_ITEMS.md OPEN-134行より転記)

- **対象**: Production正式pathでの記事生成run(A-Family通常News・
  Trend Synthesis、A2/B1B)。
- **観測量**: 次の20 run(10記事×A2/B1B)または30日のいずれか早い方。
- **主要因判定**: 単一failure modeがNG runの50%以上かつ4件以上→
  「主要因」と判定し改善Trial起票を`USER_DECISION_REQUIRED`で提示。
- **全体NG率の再対策閾値**: 20 run中NG率40%以上(8件以上)→再対策検討を
  `USER_DECISION_REQUIRED`で提示。20%以下→観測終了(closeout報告)。
  中間(20〜40%)→追加10 runの観測延長を1回だけ可、その後は判断提示。
- **報告**: 10 run到達で中間報告、20 run到達または30日で最終報告。
- **比較基準(baseline)**: G1修正前の`FAMILY-A-POINT-OVERLAP-GAP-FIX-
  TRIAL-05_REPORT.md`実測(Hanshin baseline/gapfix NG率67〜100%、
  Theme 2 baseline/gapfix NG率50%)。

## record schema(1 run = 1 JSON line)

各記事生成run完了時、run単位で以下のfieldを持つ1行のJSONを追記する
(既存run summary[`articles_run_summary.json`/`point_overlap_article_
retry_log.json`/`fact_qa.json`/`ledger_deviation.json`等]から集計)。

```json
{
  "observed_at": "2026-09-09T00:00:00+09:00",
  "management_id": "記事生成runの管理ID(例: OPEN-112-...-01)",
  "theme": "テーマ名(例: hanshin/health/household/theme2等)",
  "editorial_mode": "null(通常News)またはtrend_synthesis",
  "level": "A2またはB1B",
  "final_status": "OKまたはNG_REVIEW_REQUIRED",
  "ng_cause": "Point Overlap(初回)|Point Overlap(retry後もNG)|Value QA|Fact Checker FAIL|Ledger Deviation|その他|null(final_status=OKの場合)",
  "point_overlap_article_retry_attempts": 0,
  "lexical_flagged_final": false,
  "value_qa_flagged_final": false,
  "fact_verdict": "PASS/REVIEW_REQUIRED/FAIL/null",
  "ledger_status": "LEDGER_COMPLIANT等/null",
  "source_report": "根拠となったReportファイル名またはrun_summary.jsonのパス"
}
```

`ng_cause`は必ず単一値(複数原因が絡む場合は最初にblockした工程を優先:
Point Overlap→Value QA→Fact Checker→Ledger Deviation→その他の順)。

## 集計方法

20 run到達時、`ng_cause`ごとの件数を集計し、Exit条件の判定基準(上記)へ
機械的に照合する。主要因判定・再対策閾値のいずれかに該当した場合は
`USER_DECISION_REQUIRED`として提示し、該当しない場合(NG率20%以下)は
観測終了・closeout報告とする。
