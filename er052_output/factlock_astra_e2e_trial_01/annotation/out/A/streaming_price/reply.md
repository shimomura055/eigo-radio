=== ANNOTATED_BRIEF_BEGIN ===
# Selected Fact Brief

## Storyline
2026年10月8日【周辺数値】までに確認できた主要な米国向け改定のうち最新として選定されたDisney+の発表では、単体プラン3種【周辺数値】の価格と適用時期が変更されたが、今回確認した資料ではDisneyが値上げ理由を明示したとは確認できない。

## Selected Facts
- 【事実1】対象は米国の単体プラン。広告付き月額プランは11.99ドル【中核数値】から12.49ドル【中核数値】、Premium月額プランは18.99ドル【中核数値】から21.49ドル【中核数値】、Premium年額プランは189.99ドル【中核数値】から214.99ドル【周辺数値】に改定された。
- 【事実2】新規契約者向け新価格は2026年9月23日【周辺数値】から適用され、同日より前に契約した利用者は2026年10月21日【周辺数値】以降の請求サイクルから変更される（全員が同日に請求されるという意味ではない）。
- 【事実3】今回確認したDisney+米国価格ページとReuters報道では理由を確認できず、ReutersによればDisneyはコメント要請に直ちには回答しなかった。確認対象外の顧客通知等で追加説明があった可能性までは否定しない。
=== ANNOTATED_BRIEF_END ===
=== SIDECAR_JSON_BEGIN ===
{
  "slug": "streaming_price", "annotator": "A",
  "spec_sha256": "8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57",
  "brief_sha256": "39312c9e54c6ef146ef1e559dbaee90df60647e6323cb0f74999a2d1a17ac1ff",
  "facts": [
    {"n": 1, "ledger_ids": ["F02", "F03", "F04", "F05"]},
    {"n": 2, "ledger_ids": ["F06"]},
    {"n": 3, "ledger_ids": ["F07"]}
  ],
  "numbers": [
    {"surface": "2026年10月8日", "kind": "date_time", "concept": "C_survey_date", "ledger_ids": ["F01"], "class": "peripheral", "role": "調査基準日(台帳F01のdate_or_period先頭は2026-09-23のため不適格)"},
    {"surface": "3種", "kind": "magnitude", "concept": "C_plan_count", "ledger_ids": ["F02", "F03", "F04"], "class": "peripheral", "role": "単体プラン数(台帳numeric_valueに無く不適格)"},
    {"surface": "11.99ドル", "kind": "magnitude", "concept": "C_ads_old", "ledger_ids": ["F02"], "class": "core", "role": "広告付き月額の旧価格"},
    {"surface": "12.49ドル", "kind": "magnitude", "concept": "C_ads_new", "ledger_ids": ["F02"], "class": "core", "role": "広告付き月額の新価格"},
    {"surface": "18.99ドル", "kind": "magnitude", "concept": "C_prem_old", "ledger_ids": ["F03"], "class": "core", "role": "Premium月額の旧価格"},
    {"surface": "21.49ドル", "kind": "magnitude", "concept": "C_prem_new", "ledger_ids": ["F03"], "class": "core", "role": "Premium月額の新価格"},
    {"surface": "189.99ドル", "kind": "magnitude", "concept": "C_year_old", "ledger_ids": ["F04"], "class": "core", "role": "Premium年額の旧価格"},
    {"surface": "214.99ドル", "kind": "magnitude", "concept": "C_year_new", "ledger_ids": ["F04"], "class": "peripheral", "role": "Premium年額の新価格(cap超過)"},
    {"surface": "2026年9月23日", "kind": "date_time", "concept": "C_new_start", "ledger_ids": ["F06"], "class": "peripheral", "role": "新規契約者向け新価格の適用開始日(cap超過)"},
    {"surface": "2026年10月21日", "kind": "date_time", "concept": "C_existing_start", "ledger_ids": ["F06"], "class": "peripheral", "role": "既存契約者の請求サイクル基準日(date_or_period先頭でなく不適格)"}
  ],
  "unmapped_claims": [],
  "annotation_notes": [
    {"where": "概念 C_year_new", "question": "適格だが上限5の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_new_start", "question": "日付は適格だが上限5の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念数 n", "question": "n=10(量7: 3種と価格6のうち3種を含み7、日付3)で上限max(3,min(6,5))=5", "options": ["上限4", "上限5"], "chosen": "上限5", "rule": "§3-5-3"},
    {"where": "概念 C_existing_start 2026年10月21日", "question": "F06のdate_or_period先頭は2026-09-23で、10-21は先頭でない", "options": ["適格", "不適格"], "chosen": "不適格(周辺)", "rule": "§3-5-2"},
    {"where": "概念 C_survey_date 2026年10月8日", "question": "F01のdate_or_period先頭は発表日2026-09-23で、2026-10-08は先頭でない", "options": ["適格", "不適格"], "chosen": "不適格(周辺)", "rule": "§3-5-2"},
    {"where": "Storyline 3種", "question": "台帳numeric_valueに3が無い。F02-F04の3プランの個数にあたるが、中核になりうる台帳外数値としてSTOPか", "options": ["STOP", "周辺で続行"], "chosen": "周辺で続行(ledger_idsは該当3件を併記、中核にしない)", "rule": "§5-2, §5-4"},
    {"where": "Selected Facts 全体", "question": "S1・S2を満たす文が4グループ(対象文+価格文 / 適用日文 / 理由文+限定文)に見え、対象文と価格文を分けると4つ以上になりかねない", "options": ["4分割", "対象文と価格文を1事実に統合して3事実"], "chosen": "3事実(最大3の上限内、分けない側)", "rule": "§5-1"},
    {"where": "事実1 ledger_ids", "question": "対象文(F05の米国向け限定)と価格文(F02-F04)の台帳が複数", "options": ["F02-F04のみ", "F02-F05"], "chosen": "F02,F03,F04,F05", "rule": "§5-4"},
    {"where": "Selected Facts 先頭", "question": "節が箇条書きでなく段落", "options": ["行頭に- を挿入", "挿入しない"], "chosen": "節の先頭と各。の直後に- を挿入", "rule": "§1"}
  ]
}
=== SIDECAR_JSON_END ===
