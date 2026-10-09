=== ANNOTATED_BRIEF_BEGIN ===
# Selected Fact Brief

## Storyline
2026年10月8日【周辺数値】時点で直近の完了済みFOMCは、インフレ高止まりへの対応として9月16日【周辺数値】に25ベーシスポイント【中核数値】利上げした一方、住宅ローン金利は政策金利に自動連動せず、複数の市場要因で上昇しており、固定ローンの借り手には月額負担増が示されている。

## Selected Facts
- 【事実1】米国について、2026年10月8日【周辺数値】時点で直近の完了済みFOMC決定は9月16日【周辺数値】。
- 【事実2】FOMCはフェデラルファンド金利の目標レンジを0.25ポイント【中核数値】引き上げ、3.75～4.00％【中核数値】とした。
- 【事実3】FOMCは、経済活動や国内支出が堅調である一方、インフレが高止まりしていると説明した。利上げはインフレを2％【中核数値】目標へより早く戻す助けになるとの考えを示した。これは政策の目的・見込みであり、効果が既に実現したという確認ではない。
- 【事実4】APによると、30年固定【周辺数値】住宅ローンの全米平均金利は2026年2月下旬【周辺数値】の5.98％【中核数値】から10月8日【周辺数値】の7.40％【中核数値】へ上昇。APは、この金利差を40万ドル【周辺数値】の借入例に当てはめ、月額費用が概算376ドル【周辺数値】増えると試算した。個別の借り手全員に当てはまる支払額ではない。
- 【事実5】Fedの政策金利は住宅ローン金利を直接決めない。固定型は契約期間中に金利が固定され、変動・調整金利型は契約条件に応じて金利が変わり得る。
- 【事実6】APは住宅ローン金利上昇の要因として、インフレ、Fed政策、債券市場投資家の経済見通しを挙げ、直近の上昇には債券市場の変動や原油高によるインフレ懸念も関わったと報じた。したがって、2月【周辺数値】から10月【周辺数値】までの固定住宅ローン金利上昇や試算された負担増を、9月【周辺数値】のFed利上げだけに帰属させない。
=== ANNOTATED_BRIEF_END ===
=== SIDECAR_JSON_BEGIN ===
{
  "slug": "central_bank_mortgage",
  "annotator": "A",
  "spec_sha256": "8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57",
  "brief_sha256": "cddeced887f1a38c32eabad27631915507ee4ab5341d15deace76f6c84479349",
  "facts": [
    {"n": 1, "ledger_ids": ["F001"]},
    {"n": 2, "ledger_ids": ["F002"]},
    {"n": 3, "ledger_ids": ["F003"]},
    {"n": 4, "ledger_ids": ["F007"]},
    {"n": 5, "ledger_ids": ["F008"]},
    {"n": 6, "ledger_ids": ["F010", "F007"]}
  ],
  "numbers": [
    {"surface": "2026年10月8日", "kind": "date_time", "concept": "C_date_1008", "ledger_ids": ["F001", "F006", "F007", "F010"], "class": "peripheral", "role": "直近決定の確認時点", "note": "適格だがcap超過で周辺化"},
    {"surface": "9月16日", "kind": "date_time", "concept": "C_date_0916", "ledger_ids": ["F001", "F002"], "class": "peripheral", "role": "直近FOMC決定日"},
    {"surface": "25ベーシスポイント", "kind": "magnitude", "concept": "C_hike", "ledger_ids": ["F002"], "class": "core", "role": "利上げ幅(Storyline)"},
    {"surface": "0.25ポイント", "kind": "magnitude", "concept": "C_hike", "ledger_ids": ["F002"], "class": "core", "role": "利上げ幅(別表記)"},
    {"surface": "3.75～4.00％", "kind": "range", "concept": "C_range", "ledger_ids": ["F002"], "class": "core", "role": "新しい目標レンジ"},
    {"surface": "2％", "kind": "magnitude", "concept": "C_target2", "ledger_ids": ["F003"], "class": "core", "role": "インフレ目標"},
    {"surface": "30年固定", "kind": "name_embedded", "concept": "C_30y", "ledger_ids": ["F006", "F007"], "class": "peripheral", "role": "住宅ローンの種類名"},
    {"surface": "2026年2月下旬", "kind": "date_time", "concept": "C_date_feb", "ledger_ids": ["F007", "F010"], "class": "peripheral", "role": "金利比較の起点"},
    {"surface": "5.98％", "kind": "magnitude", "concept": "C_rate_old", "ledger_ids": ["F007"], "class": "core", "role": "2月下旬の30年固定平均金利"},
    {"surface": "10月8日", "kind": "date_time", "concept": "C_date_1008", "ledger_ids": ["F001", "F006", "F007", "F010"], "class": "peripheral", "role": "金利比較の終点"},
    {"surface": "7.40％", "kind": "magnitude", "concept": "C_rate_new", "ledger_ids": ["F006", "F007"], "class": "core", "role": "10月8日の30年固定平均金利"},
    {"surface": "40万ドル", "kind": "magnitude", "concept": "C_loan", "ledger_ids": ["F007"], "class": "peripheral", "role": "試算の借入例(numeric_scope内のみで不適格)"},
    {"surface": "376ドル", "kind": "magnitude", "concept": "C_cost", "ledger_ids": ["F007"], "class": "peripheral", "role": "月額費用の概算増", "note": "適格だがcap超過で周辺化"},
    {"surface": "2月", "kind": "date_time", "concept": "C_date_feb", "ledger_ids": ["F007", "F010"], "class": "peripheral", "role": "金利上昇の起点月"},
    {"surface": "10月", "kind": "date_time", "concept": "C_date_1008", "ledger_ids": ["F001", "F006", "F007", "F010"], "class": "peripheral", "role": "金利上昇の終点月"},
    {"surface": "9月", "kind": "date_time", "concept": "C_date_0916", "ledger_ids": ["F001", "F002"], "class": "peripheral", "role": "Fed利上げの月"}
  ],
  "unmapped_claims": [],
  "annotation_notes": [
    {"where": "Selected Facts 1項目目", "question": "2文が別の台帳ID(F001とF002)を主な根拠にしており分けるか", "options": ["分ける", "分けない"], "chosen": "S1・S2を満たすため2つに分け、事実1=F001、事実2=F002", "rule": "§2"},
    {"where": "Selected Facts 2・3・4・5項目目", "question": "複数文あるが同一台帳ID(限定文を含む)か", "options": ["分ける", "分けない"], "chosen": "分けない(S2を満たさない)", "rule": "§2, §5-1"},
    {"where": "事実6(5項目目)", "question": "限定文「したがって〜帰属させない」が別台帳ID(F007)に由来", "options": ["別事実にする", "同一事実にしてledger_idsに追加"], "chosen": "同一事実にしF007をledger_idsに追加", "rule": "§2"},
    {"where": "概念 C_date_1008", "question": "適格(F006のdate_or_period先頭が2026-10-08)だが上限5の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_date_0916", "question": "適格(F001/F002先頭日付が2026-09-16)だが上限5の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_date_feb", "question": "適格(F007先頭日付が2026年2月下旬)だが上限5の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_cost(376ドル)", "question": "適格(F007のnumeric_valueに376)だが優先順で6番目、上限5の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念数 n", "question": "n=10(C_date_1008, C_date_0916, C_hike, C_range, C_target2, C_rate_old, C_rate_new, C_loan, C_cost, C_date_feb)、上限=max(3,min(6,5))=5。優先順は C_hike(Storyline量)→C_range→C_target2→C_rate_old→C_rate_new→C_cost→日付", "options": ["上限5"], "chosen": "中核は C_hike, C_range, C_target2, C_rate_old, C_rate_new の5概念", "rule": "§3-5"},
    {"where": "25ベーシスポイント / 0.25ポイント", "question": "主数字(25と0.25)が異なるが同じ台帳データ(F002の利上げ幅)を指す", "options": ["別概念", "同一概念"], "chosen": "同一概念C_hike。25がnumeric_valueに含まれ適格のため両表記とも中核", "rule": "§3-3, §3-5"},
    {"where": "40万ドル", "question": "40はF007のnumeric_scope内の数字で、numeric_value欄には無い", "options": ["適格", "不適格"], "chosen": "不適格(周辺)", "rule": "§3-5-2"},
    {"where": "30年固定", "question": "量か名称内番号か(F006のnumeric_valueに30がある)", "options": ["magnitude", "name_embedded"], "chosen": "name_embedded(商品名の一部、番号を変えると別商品)で常に周辺", "rule": "§5-3"},
    {"where": "2026年2月下旬", "question": "「下旬」を表記に含めるか", "options": ["含める", "含めない"], "chosen": "数字(月)に直接つくので含める", "rule": "§5-5"},
    {"where": "概算376ドル", "question": "「概算」はヘッジ語の列挙に無い", "options": ["含める", "含めない"], "chosen": "列挙に無いので含めず376ドルを表記とする", "rule": "§5-6"},
    {"where": "2月 / 10月 / 9月(事実6)", "question": "月だけの表記を日付として扱うか、同概念にまとめるか", "options": ["不適格", "適格で同概念"], "chosen": "表記に月があり台帳先頭日付と一致(F007の2月、F006/F001/F002の10月・9月)。長い表記と台帳ID共通のため同概念、全て周辺", "rule": "§3-3, §3-5-2"},
    {"where": "全体", "question": "漢数字だけの数量、丸め表現(運用明確化b)の有無", "options": ["あり", "なし"], "chosen": "該当なし。Storylineの主張・数字は全て台帳にあるためSTOPなし", "rule": "§3, §4"}
  ]
}
=== SIDECAR_JSON_END ===
