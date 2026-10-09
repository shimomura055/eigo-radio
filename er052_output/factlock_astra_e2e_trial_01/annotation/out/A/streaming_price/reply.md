=== ANNOTATED_BRIEF_BEGIN ===
# Selected Fact Brief

## Storyline
調査で確認できた主要な米国向け発表の範囲で最も新しいDisney+の2026年9月23日【周辺数値】の値上げでは、米国の広告付き単体月額とPremiumの月額・年額が改定され、新規契約者と既存契約者で適用時期が分かれる一方、確認資料からはDisneyが示した理由を特定できない。

## Selected Facts
- 【事実1】対象は、2026年10月8日【周辺数値】までの調査で確認できた主要な米国向け発表の範囲。Disney+の広告付き単体月額は11.99ドル【中核数値】から12.49ドル【中核数値】へ、Premium単体月額は18.99ドル【中核数値】から21.49ドル【中核数値】へ、Premium単体年額は189.99ドル【周辺数値】から214.99ドル【周辺数値】へ改定。新規契約者向けの新価格は2026年9月23日【周辺数値】からで、それ以前に契約した利用者には2026年10月21日【周辺数値】以降の請求サイクルから適用される。既存契約者への適用日は個々の請求サイクルによる。確認したDisney+米国価格ページとReuters報道では、Disneyが今回の改定理由を明示した記述は確認できず、Reutersは同社がコメント要請に直ちには回答しなかったと報じている。第三者請求パートナー経由では価格や適用条件が異なる場合がある。
=== ANNOTATED_BRIEF_END ===
=== SIDECAR_JSON_BEGIN ===
{
  "slug": "streaming_price", "annotator": "A",
  "spec_sha256": "8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57",
  "brief_sha256": "776ac8d80c32dbeda5c60ae37dd86a24e13e0df40a4f1368bdfeba1b9cc7625d",
  "facts": [ {"n": 1, "ledger_ids": ["F01", "F02", "F03", "F04", "F05", "F06", "F07"]} ],
  "numbers": [
    {"surface": "2026年9月23日", "kind": "date_time", "concept": "C_new_start", "ledger_ids": ["F01", "F02", "F03", "F04", "F06"], "class": "peripheral", "role": "新規契約者向け新価格の開始日・発表日(Storylineにも出現)"},
    {"surface": "2026年10月8日", "kind": "date_time", "concept": "C_survey_base", "ledger_ids": ["F01"], "class": "peripheral", "role": "調査基準日"},
    {"surface": "11.99ドル", "kind": "magnitude", "concept": "C_ads_old", "ledger_ids": ["F02"], "class": "core", "role": "広告付き単体月額の旧価格"},
    {"surface": "12.49ドル", "kind": "magnitude", "concept": "C_ads_new", "ledger_ids": ["F02"], "class": "core", "role": "広告付き単体月額の新価格"},
    {"surface": "18.99ドル", "kind": "magnitude", "concept": "C_prem_m_old", "ledger_ids": ["F03"], "class": "core", "role": "Premium単体月額の旧価格"},
    {"surface": "21.49ドル", "kind": "magnitude", "concept": "C_prem_m_new", "ledger_ids": ["F03"], "class": "core", "role": "Premium単体月額の新価格"},
    {"surface": "189.99ドル", "kind": "magnitude", "concept": "C_prem_y_old", "ledger_ids": ["F04"], "class": "peripheral", "role": "Premium単体年額の旧価格"},
    {"surface": "214.99ドル", "kind": "magnitude", "concept": "C_prem_y_new", "ledger_ids": ["F04"], "class": "peripheral", "role": "Premium単体年額の新価格"},
    {"surface": "2026年10月21日", "kind": "date_time", "concept": "C_existing_start", "ledger_ids": ["F02", "F03", "F04", "F06"], "class": "peripheral", "role": "既存契約者の価格変更が始まる請求サイクルの基準日"}
  ],
  "unmapped_claims": [],
  "annotation_notes": [
    {"where": "Selected Facts 1項目の文", "question": "S1(F01)・S2(F02-04)・S3/S4(F06)・S5(F07)・S6(F05由来の限定文)と、台帳IDの異なる文が4つ以上に分かれうる", "options": ["3つ以下に分ける", "分けない(1事実)"], "chosen": "分けない(1事実、ledger_idsにF01-F07を併記)", "rule": "§2 4つ以上に分けたくなったら分けない / §5-1"},
    {"where": "第三者請求パートナー経由の文(F05由来)", "question": "限定する文が別の台帳IDに由来する", "options": ["別事実にする", "直前の事実に含めF05をledger_idsに追加"], "chosen": "直前の事実に含めF05を追加", "rule": "§2 限定文は別事実にしない"},
    {"where": "項目の形", "question": "元のニュース欄のSelected Factsは箇条書きでなく段落だが、先頭に定義済みの `- ` を入れた", "options": ["`- `を入れる", "入れない"], "chosen": "入れる(【事実1】を付けるため)", "rule": "§1 定義済みの改行/行頭の挿入"},
    {"where": "概念 C_survey_base (2026年10月8日)", "question": "F01のdate_or_period先頭の日付表現は発表日2026-09-23であり、2026-10-08は先頭ではない", "options": ["適格(中核候補)", "不適格(周辺)"], "chosen": "不適格のため周辺", "rule": "§3-5-2 / §5-2"},
    {"where": "概念 C_existing_start (2026年10月21日)", "question": "台帳のdate_or_period先頭の日付表現は2026-09-23で、2026-10-21は先頭ではない(F06のnumeric_valueの日付は日付判定の対象外)", "options": ["適格(中核候補)", "不適格(周辺)"], "chosen": "不適格のため周辺", "rule": "§3-5-2 / §5-2"},
    {"where": "概念 C_new_start (2026年9月23日)", "question": "date_or_period先頭の日付表現と一致し適格だが、日付の優先順は量の後で上限4の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_prem_y_old / C_prem_y_new (189.99ドル/214.99ドル)", "question": "numeric_valueに含まれ適格だが、n=9(上限4)で量の上位4つ(11.99/12.49/18.99/21.49)の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "全体の概念数", "question": "magnitude/date_time/rangeの概念はn=9(価格6+日付3)で上限は4。Storylineに量はなくStorylineの数字は日付のみ", "options": ["上限4", "別の上限"], "chosen": "上限4", "rule": "§3-5-3"},
    {"where": "台帳F01・F07 (AMBIGUOUS)", "question": "AMBIGUOUS記録のため断定禁止・曖昧さ保持が必要。注記では本文を変更せず、ledger_idsにのみ反映", "options": ["本文に変更を加える", "本文は不変更"], "chosen": "本文は不変更(注記のみ)", "rule": "§1 付け足すだけ"}
  ]
}
=== SIDECAR_JSON_END ===
