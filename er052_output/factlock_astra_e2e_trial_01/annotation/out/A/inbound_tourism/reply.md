=== ANNOTATED_BRIEF_BEGIN ===
# Selected Fact Brief

## Storyline
2026年8月【周辺数値】の訪日外客数は前年同月を下回り、年初来累計も前年同期比減となった一方、8月単月は2019年【周辺数値】水準を上回っており、コロナ禍前を超える年間水準と直近の減速が併存している。

## Selected Facts
・【事実1】2026年8月【周辺数値】の訪日外客数は3,098,900人【中核数値】で、前年同月比9.6％【中核数値】減。2025年8月【周辺数値】の3,428,406人【中核数値】を下回った（F01）。
・【事実2】2026年1～8月【周辺数値】は27,626,300人【中核数値】で、2025年【周辺数値】同期比2.7％【中核数値】減（F02）。
・【事実3】一方、2026年8月【周辺数値】の数は2019年8月【周辺数値】の2,520,134人【中核数値】を578,766人【周辺数値】（約23％【周辺数値】）上回った（F03）。
・【事実4】2025年【周辺数値】の年間訪日外客数は2019年【周辺数値】の31,882,049人【周辺数値】を上回った。2025年【周辺数値】の最新確定値は42,683,301人【周辺数値】（F06）。
・Ledgerには、2026年【周辺数値】の減少が起きた原因を確定するFactはない。原因を推測せず、上記の比較と推移を中心に扱うこと。
=== ANNOTATED_BRIEF_END ===
=== SIDECAR_JSON_BEGIN ===
{
  "slug": "inbound_tourism", "annotator": "A",
  "spec_sha256": "8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57",
  "brief_sha256": "0bdfa5688ce2f50b0b5f56a6c044dfa72ebeef691d09e39c3cbfb2d2989844a3",
  "facts": [
    {"n": 1, "ledger_ids": ["F01"]},
    {"n": 2, "ledger_ids": ["F02"]},
    {"n": 3, "ledger_ids": ["F03"]},
    {"n": 4, "ledger_ids": ["F06"]}
  ],
  "numbers": [
    {"surface": "2026年8月", "kind": "date_time", "concept": "C_aug2026", "ledger_ids": ["F01", "F03"], "class": "peripheral", "role": "2026年8月(最新月)"},
    {"surface": "2019年", "kind": "year", "concept": "C_year2019", "ledger_ids": ["F06"], "class": "peripheral", "role": "2019年(年のみ)"},
    {"surface": "3,098,900人", "kind": "magnitude", "concept": "C_aug2026_count", "ledger_ids": ["F01", "F03"], "class": "core", "role": "2026年8月の訪日外客数"},
    {"surface": "9.6％", "kind": "magnitude", "concept": "C_aug_yoy", "ledger_ids": ["F01"], "class": "core", "role": "8月の前年同月比減少率"},
    {"surface": "2025年8月", "kind": "date_time", "concept": "C_aug2025", "ledger_ids": ["F01"], "class": "peripheral", "role": "前年同月(日付がF01の先頭日付と不一致で不適格)"},
    {"surface": "3,428,406人", "kind": "magnitude", "concept": "C_aug2025_count", "ledger_ids": ["F01"], "class": "core", "role": "2025年8月の訪日外客数"},
    {"surface": "2026年1～8月", "kind": "date_time", "concept": "C_ytd2026", "ledger_ids": ["F02"], "class": "peripheral", "role": "年初来期間"},
    {"surface": "27,626,300人", "kind": "magnitude", "concept": "C_ytd2026_count", "ledger_ids": ["F02"], "class": "core", "role": "2026年1～8月累計"},
    {"surface": "2025年", "kind": "year", "concept": "C_year2025", "ledger_ids": ["F02", "F06"], "class": "peripheral", "role": "2025年(年のみ)"},
    {"surface": "2.7％", "kind": "magnitude", "concept": "C_ytd_yoy", "ledger_ids": ["F02"], "class": "core", "role": "累計の前年同期比減少率"},
    {"surface": "2019年8月", "kind": "date_time", "concept": "C_aug2019", "ledger_ids": ["F03"], "class": "peripheral", "role": "2019年8月(適格だがcap超過)"},
    {"surface": "2,520,134人", "kind": "magnitude", "concept": "C_aug2019_count", "ledger_ids": ["F03"], "class": "core", "role": "2019年8月の訪日外客数"},
    {"surface": "578,766人", "kind": "magnitude", "concept": "C_diff_aug", "ledger_ids": ["F03"], "class": "peripheral", "role": "2019年8月との差(cap超過)"},
    {"surface": "約23％", "kind": "magnitude", "concept": "C_diff_aug_pct", "ledger_ids": ["F03"], "class": "peripheral", "role": "2019年8月との差の比率(cap超過)"},
    {"surface": "31,882,049人", "kind": "magnitude", "concept": "C_year2019_count", "ledger_ids": ["F06"], "class": "peripheral", "role": "2019年の年間訪日外客数(cap超過)"},
    {"surface": "42,683,301人", "kind": "magnitude", "concept": "C_year2025_count_final", "ledger_ids": ["F06"], "class": "peripheral", "role": "2025年の最新確定値(numeric_valueに無く不適格)"},
    {"surface": "2026年", "kind": "year", "concept": "C_year2026", "ledger_ids": [], "class": "peripheral", "role": "運用指示文中の年"}
  ],
  "unmapped_claims": [
    {"text": "Ledgerには、2026年の減少が起きた原因を確定するFactはない。原因を推測せず、上記の比較と推移を中心に扱うこと。", "type": "qualifier"},
    {"text": "2026年(第5項目の運用指示文中の年)", "type": "new_number"}
  ],
  "annotation_notes": [
    {"where": "Selected Facts 第5項目(Ledgerには…)", "question": "台帳の事実に基づかない運用指示文に【事実N】を付けるか", "options": ["事実5として付ける", "付けない"], "chosen": "付けない", "rule": "§5-6"},
    {"where": "Selected Facts 各項目の行頭", "question": "行頭が「・」の箇条書きで、定義済みの「- 」を挿入するか", "options": ["「- 」を追加", "「・」の直後に【事実N】のみ付ける"], "chosen": "「・」の直後に【事実N】のみ付ける(元の文字を変えない)", "rule": "§5-6"},
    {"where": "（F01）（F02）（F03）（F06）", "question": "括弧内のID形を数字として扱うか", "options": ["数字として印を付ける", "台帳ID形として印を付けない"], "chosen": "印を付けない", "rule": "§3 冒頭"},
    {"where": "事実1・事実4", "question": "同一項目内の2文を分けるか", "options": ["分ける", "分けない"], "chosen": "分けない(各項目とも根拠は単一の台帳ID)", "rule": "§5-1"},
    {"where": "Storyline 全体", "question": "Storylineに出る量(magnitude/range)があるか", "options": ["あり", "なし"], "chosen": "なし(Storylineの数字は2026年8月と2019年のみ)。全ての量は優先順位(2)", "rule": "§3-5-4"},
    {"where": "概念数 n", "question": "上限の計算", "options": ["n=14(量10+日付4)→上限max(3,min(6,7))=6"], "chosen": "上限6。中核は出現順の先頭6量", "rule": "§3-5-3"},
    {"where": "概念 C_diff_aug / C_diff_aug_pct / C_year2019_count", "question": "適格だが上限6の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_aug2026 / C_aug2019 / C_ytd2026", "question": "日付は適格だが量が優先されるため上限の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "2025年8月", "question": "F01のdate_or_period先頭日付は2026年8月で、2025年8月は一致しない", "options": ["適格", "不適格"], "chosen": "不適格のため周辺", "rule": "§3-5-2"},
    {"where": "42,683,301人", "question": "F06のnumeric_valueは42,683,600で、42,683,301はambiguity_noteにのみ記載", "options": ["適格", "不適格"], "chosen": "numeric_valueに無いため不適格・周辺。ledger_idsにはF06を記載", "rule": "§3-5-2 / §5-2"},
    {"where": "Storyline の 2019年", "question": "2019年(年のみ)の台帳ID。F03(2019年8月)と併記すると概念統合で年と日付のkindが衝突する", "options": ["F03,F06", "F06のみ"], "chosen": "F06のみ(年は常に周辺・別概念)", "rule": "§5-4 / §3-3"},
    {"where": "2026年1～8月", "question": "月の範囲を含む期間を range とするか date_time とするか", "options": ["range", "date_time"], "chosen": "date_time(期間・月を含む)。F02のdate_or_period先頭日付と一致するため適格だがcap超過で周辺", "rule": "§3-2 / §5-6"},
    {"where": "「2025年同期」「前年同期比」", "question": "「2025年」のみを表記とするか", "options": ["2025年", "2025年同期"], "chosen": "2025年(数字に直接つく語のみ含める)", "rule": "§3-1 / §5-5"}
  ]
}
=== SIDECAR_JSON_END ===
