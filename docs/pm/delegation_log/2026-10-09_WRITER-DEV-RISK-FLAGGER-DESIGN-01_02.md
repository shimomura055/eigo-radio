# 委任ログ: WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_02(Opus条件Aレビュー反映 = 改善ループ1)

- 日付: 2026-10-09 / 実行層: Sonnet / 範囲: P0修正(¥0) -> P0' D0記事スイープ(¥0) -> P1パイロット(<=¥30) -> P2要素Trial(<=¥250)、P2完了でSTOP
- 対象: `er052_output/writer_dev_risk_flagger_01/`。別workerの `casebank/checker_reference_01.json` / `CHECKER_REFERENCE_01.md` には触れていない。
- Opus所見要約: `docs/pm/opus_a_review_risk_flagger_01.md`(14所見全件採用)
- 使用モデル: gpt-6.1-sol のみ(旧モデル不使用、Astra不使用)。保留セット(holdout)は一切流していない。

## P0 修正一覧(¥0、テスト54件PASS)
1. `case_to_unit` を実スキーマ(fact{id,text,src}、context{before,after,source})へ。LLMへは全台帳(fact_id,text)と対象文(+before/after)のみ。
2. `make_blind_01`: LABEL_KEYSを`flagger_lib.LABEL_KEYS`へ集約(label_basis*/label_src/accident_type/notes/near_dup_group/legacy_ids/synthetic/split等を追加)、runnerと共有。split別盲検ファイル出力、`ledger`(全台帳)を付与、fact.src/context.sourceは除去。
3. aggregator全面改修(split絞り込み、accident_type別、known_incident、Recall_human主/Recall_all副、FPR_clear/boundary/hard-negative、Wilson、Flag数2種、記事モード±2文窓とRecall@top3、confidence曲線、S0反転再計算)。
4. D0: 'the way it had been'削除、K01=回帰テスト(汚染済み)を明記、英語語の語境界化(block/blockade)、一般否定cue除外、総当たり(言語をまたぐ)、和集合投入はrollbackのみ(gate_only)。合成方向反転系の事故タイプ訂正。
5. D1map廃止、D1full一本化(casebankにも全台帳)。D1にFlag上限3。タイプ別適用先はラベルで選ばない(全件 or `--gate d0`)。
6. D2rank追加、D2の確信度正直化+閾値曲線。
7. 見出しを文として残す。8. 費用台帳の限界を注記。9. 設計書v2(§4/§6/§13)、KPI5裁定用紙(所要分数欄)。

## 事前登録(P2実行前に記録)
- D1ゲート規則(`--gate d0`): 主体対象入替・否定反転=常に呼ぶ / rollback反転=いずれかの文に方向語 / 不在断定=不在cue / 数量時系列=数値。ゲートを使うかはP1実測後の見積で判断し、使う場合はゲート有無を結果ファイル名に残す。
- confidence閾値曲線の運用閾値は、P2の開発セット結果から保留評価の前にFableが固定する(本委任では固定しない)。
