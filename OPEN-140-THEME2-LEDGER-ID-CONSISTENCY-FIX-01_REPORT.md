# OPEN-140-THEME2-LEDGER-ID-CONSISTENCY-FIX-01

管理ID: OPEN-140-THEME2-LEDGER-ID-CONSISTENCY-FIX-01
費用: ¥0(ファイル編集のみ、API呼び出しなし)
Git操作: なし(本レポート作成のみ、commit/pushは実施していない)

## 1. 不整合の実体

Theme2(若者のスロー旅行)Verified Fact Ledgerのうち、現在Production Writer
配線(`er011_open112_trend_synthesis_production_wiring_01_run.py`が直接読む
`THEME2_LEDGER_PATH`)が参照している本番相当ファイル
`er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/research/
theme2_verified_fact_ledger_CORRECTED_trial12.txt`の「注記3(central tension
パラグラフ)」内で、地の文の引用括弧`(F-2xx)`とFact一覧`[F-201]`〜`[F-209]`
の実際の対応関係が4箇所でずれていた(単純な参照ずれ、Fact一覧本体の内容は
無傷)。

| 箇所(注記3内の文) | 旧引用ID | 正しいID | 判定根拠 |
|---|---|---|---|
| 観光白書「滞在長期化を図る必要がある」 | F-211 | F-206 | F-211はFact一覧に存在しない欠番。文言が[F-206]本文と完全一致 |
| じゃらん秋調査、平均1.8泊・中央値2.0泊 | F-206 | F-205 | 数値が[F-205]本文と完全一致(F-206は別内容) |
| 「1カ月休暇なら1週間程度」24.1% | F-205 | F-204 | 数値が[F-204]本文と完全一致(F-205は別内容) |
| Z世代女性「有名な観光地を巡る」44.7% | F-208 | F-202 | 数値が[F-202]本文と完全一致(F-208は別内容) |

なお`F-209`・`F-210`(旧版で「海外旅行Z世代9割が自由時間を希望」に誤って
使われていた番号)は既にTrial-12で`F-203`へ修正済みであり、本タスクの対象外
(参考情報としてのみ`id_mapping.json`に記載)。

## 2. 判定根拠

各誤引用箇所は、引用元の数値・文言がFact一覧の特定の1件とのみ完全一致し、
他のFactとは一致しない(一意に決定できる)。Fact一覧`[F-201]`〜`[F-209]`
自体の記述内容・出典・evidence_strength等は今回一切変更していない
(意味・Fact対応関係の変更なし)。

## 3. 修正内容

対象ファイル: `er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/
research/theme2_verified_fact_ledger_CORRECTED_trial12.txt`(注記3のみ、
4箇所の引用ID修正+Trial-12の既存修正メモと同形式の訂正注記を追加)。

対応表: `er011_output/open140_theme2_ledger_id_fix_01/id_mapping.json`

以下は**変更していない**(記録物として保持):
- `er011_output/open112_engagement_reference_cross_topic_ab_trial_11/
  research/theme2_verified_fact_ledger.txt`(Trial-11時点の過去成果物)
- `er011_output/open112_trend_synthesis_production_wiring_01/a2/audit/
  prompt.txt`等の既存audit記録(実際にWriterへ送信されたLedgerスナップ
  ショット)
- `er011_open112_trend_synthesis_production_wiring_01_run.py`内の
  `THEME2_TREND_GATE_CHECKLIST`コメント中のF-211言及(2026-09-08時点の
  人手判定記録)

## 4. 影響範囲

- 既にAPPROVED_FOR_PRODUCTIONとなっているTheme2 A2/B1完成音声(rerun_04)
  の生成には、既存の`prompt.txt`(不変)が使われており、今回の修正は
  さかのぼって影響しない。
- 影響があるのは、今後このLedgerファイルを読んで新たに記事・音声を
  再生成する場合のみ(引用IDが正しくFact一覧を指すようになる、prospective
  な修正)。
- Production・Prompt・QA・retryコードの変更なし。ACTIVE_TASK/OPEN_ITEMS/
  DECISION_LOG/CURRENT_SPECは本タスクでは編集していない(Fableの後続統合
  待ち)。

## 5. STOPの有無

STOPなし。4箇所全て「どのIDが正か」が引用文言とFact一覧本文の完全一致で
一意に決まり、Fact自体の意味・対応関係は変わらないため、ユーザー決定
(2026-09-10)に基づき自律修正した。
