=== ANNOTATED_BRIEF_BEGIN ===
# Selected Fact Brief

## Storyline
2026年8月【周辺数値】の訪日外客数は前年同月を下回り、年初来累計も前年同期比減となった一方、8月【周辺数値】単月は2019年【周辺数値】水準を上回っており、コロナ禍前を超える年間水準と直近の減速が併存している。

## Selected Facts
・【事実1】2026年8月【周辺数値】の訪日外客数は3,098,900人【中核数値】で、前年同月比9.6％【中核数値】減。2025年8月【周辺数値】の3,428,406人【中核数値】を下回った（F01）。
・【事実2】2026年1～8月【周辺数値】は27,626,300人【中核数値】で、2025年【周辺数値】同期比2.7％【中核数値】減（F02）。
・【事実3】一方、2026年8月【周辺数値】の数は2019年8月【周辺数値】の2,520,134人【中核数値】を578,766人【周辺数値】（約23％【周辺数値】）上回った（F03）。
・【事実4】2025年【周辺数値】の年間訪日外客数は2019年【周辺数値】の31,882,049人【周辺数値】を上回った。2025年【周辺数値】の最新確定値は42,683,301人【周辺数値】（F06）。
・Ledgerには、2026年【周辺数値】の減少が起きた原因を確定するFactはない。原因を推測せず、上記の比較と推移を中心に扱うこと。
=== ANNOTATED_BRIEF_END ===
=== SIDECAR_JSON_BEGIN ===
{
  "slug": "inbound_tourism", "annotator": "B",
  "spec_sha256": "8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57",
  "brief_sha256": "0bdfa5688ce2f50b0b5f56a6c044dfa72ebeef691d09e39c3cbfb2d2989844a3",
  "facts": [
    {"n": 1, "ledger_ids": ["F01"]},
    {"n": 2, "ledger_ids": ["F02"]},
    {"n": 3, "ledger_ids": ["F03"]},
    {"n": 4, "ledger_ids": ["F06"]}
  ],
  "numbers": [
    {"surface": "2026年8月", "kind": "date_time", "concept": "C_aug2026", "ledger_ids": ["F01", "F03"], "class": "peripheral", "role": "2026年8月(対象月)。適格だが日付は優先順が最後でcap外"},
    {"surface": "8月", "kind": "date_time", "concept": "C_aug2026", "ledger_ids": ["F01", "F03"], "class": "peripheral", "role": "Storylineの「8月単月」(2026年8月の短い表記)"},
    {"surface": "2019年", "kind": "year", "concept": "C_y2019", "ledger_ids": ["F03", "F06"], "class": "peripheral", "role": "比較基準年(年のみ)"},
    {"surface": "3,098,900人", "kind": "magnitude", "concept": "C_aug26_total", "ledger_ids": ["F01", "F03"], "class": "core", "role": "2026年8月の訪日外客数"},
    {"surface": "9.6％", "kind": "magnitude", "concept": "C_aug_yoy", "ledger_ids": ["F01"], "class": "core", "role": "8月の前年同月比減少率"},
    {"surface": "2025年8月", "kind": "date_time", "concept": "C_aug2025", "ledger_ids": ["F01"], "class": "peripheral", "role": "前年同月(台帳date_or_periodの先頭は2026年8月のため不適格)"},
    {"surface": "3,428,406人", "kind": "magnitude", "concept": "C_aug25_total", "ledger_ids": ["F01"], "class": "core", "role": "2025年8月の訪日外客数"},
    {"surface": "2026年1～8月", "kind": "date_time", "concept": "C_jan_aug2026", "ledger_ids": ["F02"], "class": "peripheral", "role": "年初来累計の期間。適格だがcap外"},
    {"surface": "27,626,300人", "kind": "magnitude", "concept": "C_ytd26_total", "ledger_ids": ["F02"], "class": "core", "role": "2026年1～8月累計"},
    {"surface": "2025年", "kind": "year", "concept": "C_y2025", "ledger_ids": ["F02", "F06"], "class": "peripheral", "role": "前年同期・年間比較の年(年のみ)"},
    {"surface": "2.7％", "kind": "magnitude", "concept": "C_ytd_yoy", "ledger_ids": ["F02"], "class": "core", "role": "累計の前年同期比減少率"},
    {"surface": "2019年8月", "kind": "date_time", "concept": "C_aug2019", "ledger_ids": ["F03"], "class": "peripheral", "role": "2019年8月(適格だがcap外)"},
    {"surface": "2,520,134人", "kind": "magnitude", "concept": "C_aug19_total", "ledger_ids": ["F03"], "class": "core", "role": "2019年8月の訪日外客数"},
    {"surface": "578,766人", "kind": "magnitude", "concept": "C_aug_diff19", "ledger_ids": ["F03"], "class": "peripheral", "role": "2019年8月との差(適格だがcap外)"},
    {"surface": "約23％", "kind": "magnitude", "concept": "C_aug_diff19_pct", "ledger_ids": ["F03"], "class": "peripheral", "role": "2019年8月との差の比率(適格だがcap外)"},
    {"surface": "31,882,049人", "kind": "magnitude", "concept": "C_y2019_total", "ledger_ids": ["F06"], "class": "peripheral", "role": "2019年の年間訪日外客数(適格だがcap外)"},
    {"surface": "42,683,301人", "kind": "magnitude", "concept": "C_y2025_final", "ledger_ids": ["F06"], "class": "peripheral", "role": "2025年の確定値。F06のnumeric_valueは42,683,600人で不一致のため不適格"},
    {"surface": "2026年", "kind": "year", "concept": "C_y2026", "ledger_ids": [], "class": "peripheral", "role": "台帳外メタ指示文中の年(年のみ)"}
  ],
  "unmapped_claims": [
    {"text": "Ledgerには、2026年の減少が起きた原因を確定するFactはない。原因を推測せず、上記の比較と推移を中心に扱うこと。", "type": "qualifier"}
  ],
  "annotation_notes": [
    {"where": "Selected Facts 全行頭", "question": "ニュース欄の行頭は「・」で「- 」ではない。【事実N】をどこに置くか", "options": ["「・」を残して直後に置く", "「・」を「- 」に置換する"], "chosen": "「・」を残して直後に【事実N】を置く(置換は禁止のため)", "rule": "§1, §5-6"},
    {"where": "Selected Facts 第5項目(Ledgerには…Fact…)", "question": "台帳の事実に対応しない運用指示文に【事実N】を付けるか", "options": ["事実5として付ける(ledger_ids空)", "付けない"], "chosen": "付けない(unmapped_claimsにqualifierで記録)。含まれる2026年は周辺の年として印を付けた", "rule": "§4, §5-6"},
    {"where": "Selected Facts 第4項目", "question": "2文を分けるか", "options": ["F06の2文を分ける", "分けない"], "chosen": "分けない(2文とも台帳F06が根拠)", "rule": "§2, §5-1"},
    {"where": "Selected Facts 第1項目", "question": "2文を分けるか", "options": ["分ける", "分けない"], "chosen": "分けない(2文とも台帳F01が根拠)", "rule": "§2, §5-1"},
    {"where": "概念数 n", "question": "n=14(量10: 3,098,900/9.6/3,428,406/27,626,300/2.7/2,520,134/578,766/約23/31,882,049/42,683,301、日付4: 2026年8月/2025年8月/2026年1～8月/2019年8月)。上限=max(3,min(6,floor(14/2)=7))=6", "options": ["上限6"], "chosen": "上限6。Storylineに量なし。他の量のうち出現順で適格な先頭6つ(3,098,900/9.6/3,428,406/27,626,300/2.7/2,520,134)を中核", "rule": "§3-5"},
    {"where": "概念 C_aug_diff19 / C_aug_diff19_pct / C_y2019_total", "question": "適格だが上限6の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_aug2026 / C_aug2019 / C_jan_aug2026", "question": "日付は適格(台帳date_or_period先頭と年月一致)だが上限の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "2025年8月", "question": "F01のdate_or_period先頭は2026年8月で一致しない", "options": ["適格", "不適格"], "chosen": "不適格のため周辺", "rule": "§3-5-2"},
    {"where": "42,683,301人", "question": "F06のnumeric_valueは42,683,600人で、42,683,301人はambiguity_noteにのみ記載。numeric_valueに含まれない", "options": ["中核候補にする", "不適格で周辺"], "chosen": "不適格で周辺(台帳IDはF06)", "rule": "§3-5-2, §5-2"},
    {"where": "Storylineの「8月単月」の「8月」", "question": "月のみの表記を日付(2026年8月と同概念)として扱うか。台帳IDはF01/F03", "options": ["2026年8月と同概念", "別概念", "印なし"], "chosen": "2026年8月と同概念・同じ周辺印", "rule": "§3-3, §5-2"},
    {"where": "2026年1～8月", "question": "期間をrangeかdate_timeか", "options": ["range", "date_time"], "chosen": "date_time(期間・月を含む)", "rule": "§3-2"},
    {"where": "年のみの表記(2019年/2025年/2026年)", "question": "年の表記は常に周辺", "options": ["周辺"], "chosen": "周辺", "rule": "§3-2"}
  ]
}
=== SIDECAR_JSON_END ===
