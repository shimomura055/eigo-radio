=== ANNOTATED_BRIEF_BEGIN ===
# Selected Fact Brief

## Storyline
2026年10月8日【周辺数値】時点で直近の完了済みFOMCは、インフレ高止まりへの対応として9月16日【周辺数値】に25ベーシスポイント【中核数値】利上げした一方、住宅ローン金利は政策金利に自動連動せず、複数の市場要因で上昇しており、固定ローンの借り手には月額負担増が示されている。

## Selected Facts
- 【事実1】米国について、2026年10月8日【周辺数値】時点で直近の完了済みFOMC決定は9月16日【周辺数値】。
- 【事実2】FOMCはフェデラルファンド金利の目標レンジを0.25ポイント【中核数値】引き上げ、3.75～4.00％【中核数値】とした。
- 【事実3】FOMCは、経済活動や国内支出が堅調である一方、インフレが高止まりしていると説明した。利上げはインフレを2％【中核数値】目標へより早く戻す助けになるとの考えを示した。これは政策の目的・見込みであり、効果が既に実現したという確認ではない。
- 【事実4】APによると、30年【周辺数値】固定住宅ローンの全米平均金利は2026年2月下旬【周辺数値】の5.98％【中核数値】から10月8日【周辺数値】の7.40％【中核数値】へ上昇。APは、この金利差を40万ドル【周辺数値】の借入例に当てはめ、月額費用が概算376ドル【周辺数値】増えると試算した。個別の借り手全員に当てはまる支払額ではない。
- 【事実5】Fedの政策金利は住宅ローン金利を直接決めない。固定型は契約期間中に金利が固定され、変動・調整金利型は契約条件に応じて金利が変わり得る。
- 【事実6】APは住宅ローン金利上昇の要因として、インフレ、Fed政策、債券市場投資家の経済見通しを挙げ、直近の上昇には債券市場の変動や原油高によるインフレ懸念も関わったと報じた。したがって、2月【周辺数値】から10月【周辺数値】までの固定住宅ローン金利上昇や試算された負担増を、9月【周辺数値】のFed利上げだけに帰属させない。
=== ANNOTATED_BRIEF_END ===
=== SIDECAR_JSON_BEGIN ===
{
  "slug": "central_bank_mortgage", "annotator": "B",
  "spec_sha256": "8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57",
  "brief_sha256": "cddeced887f1a38c32eabad27631915507ee4ab5341d15deace76f6c84479349",
  "facts": [
    {"n": 1, "ledger_ids": ["F001"]},
    {"n": 2, "ledger_ids": ["F002"]},
    {"n": 3, "ledger_ids": ["F003"]},
    {"n": 4, "ledger_ids": ["F007", "F006"]},
    {"n": 5, "ledger_ids": ["F008"]},
    {"n": 6, "ledger_ids": ["F010", "F007"]}
  ],
  "numbers": [
    {"surface": "2026年10月8日", "kind": "date_time", "concept": "C_asof", "ledger_ids": ["F001", "F006", "F007", "F010"], "class": "peripheral", "role": "確認・報道時点"},
    {"surface": "9月16日", "kind": "date_time", "concept": "C_decision", "ledger_ids": ["F001", "F002", "F003"], "class": "peripheral", "role": "直近FOMC決定日"},
    {"surface": "25ベーシスポイント", "kind": "magnitude", "concept": "C_hike", "ledger_ids": ["F002"], "class": "core", "role": "利上げ幅"},
    {"surface": "0.25ポイント", "kind": "magnitude", "concept": "C_hike", "ledger_ids": ["F002"], "class": "core", "role": "利上げ幅(別表記)"},
    {"surface": "3.75～4.00％", "kind": "range", "concept": "C_range", "ledger_ids": ["F002"], "class": "core", "role": "新しい目標レンジ"},
    {"surface": "2％", "kind": "magnitude", "concept": "C_target", "ledger_ids": ["F003"], "class": "core", "role": "インフレ目標"},
    {"surface": "30年", "kind": "name_embedded", "concept": "C_term30", "ledger_ids": ["F006", "F007"], "class": "peripheral", "role": "30年固定ローンの商品名内の年数"},
    {"surface": "2026年2月下旬", "kind": "date_time", "concept": "C_feb", "ledger_ids": ["F007", "F010"], "class": "peripheral", "role": "金利比較の起点"},
    {"surface": "5.98％", "kind": "magnitude", "concept": "C_rate598", "ledger_ids": ["F007"], "class": "core", "role": "2月下旬の30年固定平均金利"},
    {"surface": "10月8日", "kind": "date_time", "concept": "C_asof", "ledger_ids": ["F001", "F006", "F007", "F010"], "class": "peripheral", "role": "金利比較の終点"},
    {"surface": "7.40％", "kind": "magnitude", "concept": "C_rate740", "ledger_ids": ["F006", "F007"], "class": "core", "role": "10月8日の30年固定平均金利"},
    {"surface": "40万ドル", "kind": "magnitude", "concept": "C_loan", "ledger_ids": ["F007"], "class": "peripheral", "role": "AP試算の借入額例"},
    {"surface": "376ドル", "kind": "magnitude", "concept": "C_pay376", "ledger_ids": ["F007"], "class": "peripheral", "role": "月額費用の概算増"},
    {"surface": "2月", "kind": "date_time", "concept": "C_feb", "ledger_ids": ["F007", "F010"], "class": "peripheral", "role": "上昇期間の起点"},
    {"surface": "10月", "kind": "date_time", "concept": "C_asof", "ledger_ids": ["F001", "F006", "F007", "F010"], "class": "peripheral", "role": "上昇期間の終点"},
    {"surface": "9月", "kind": "date_time", "concept": "C_decision", "ledger_ids": ["F001", "F002", "F003"], "class": "peripheral", "role": "Fed利上げ月"}
  ],
  "unmapped_claims": [],
  "annotation_notes": [
    {"where": "概念数 n", "question": "上限の計算", "options": ["n=10, 上限5"], "chosen": "n=10(C_hike, C_range, C_target, C_rate598, C_rate740, C_loan, C_pay376, C_asof, C_decision, C_feb)、上限max(3,min(6,5))=5", "rule": "§3-5-3"},
    {"where": "概念 C_pay376", "question": "適格(F007 numeric_value)だが上限5の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_asof / C_decision / C_feb", "question": "日付は適格だが上限の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_loan(40万ドル)", "question": "40万はF007のnumeric_scope内のみで、scope外のnumeric_valueに無い", "options": ["適格", "不適格"], "chosen": "不適格のため周辺", "rule": "§3-5-2"},
    {"where": "概念 C_hike(25ベーシスポイント/0.25ポイント)", "question": "主数字が異なるが同じ台帳データ。0.25はnumeric_valueに無い", "options": ["同一概念", "別概念"], "chosen": "同一概念(25がnumeric_valueにあり適格、Storylineに出る量として中核)", "rule": "§3-3 / §5-4"},
    {"where": "表記 30年", "question": "量か名称内番号か(15年固定と区別される商品名内の年数)", "options": ["magnitude", "name_embedded"], "chosen": "name_embedded(周辺、nの数に入れない)", "rule": "§5-3"},
    {"where": "表記 2026年2月下旬", "question": "下旬を表記に含めるか", "options": ["含める", "含めない"], "chosen": "含める(月に直接つく)", "rule": "§5-5"},
    {"where": "事実1/2", "question": "項目1(F001とF002の2文)を分けるか", "options": ["分ける", "分けない"], "chosen": "分ける(S1,S2成立、別ID)", "rule": "§2"},
    {"where": "事実4/6の限定文", "question": "限定文(個別の借り手全員…/したがって…帰属させない)は別事実か", "options": ["別事実", "直前と同一"], "chosen": "同一事実に含め、事実6にはF007を追加", "rule": "§2"},
    {"where": "Storylineの重複行", "question": "Storyline文には【事実N】を付けない", "options": ["付ける", "付けない"], "chosen": "付けない", "rule": "§2"}
  ]
}
=== SIDECAR_JSON_END ===
