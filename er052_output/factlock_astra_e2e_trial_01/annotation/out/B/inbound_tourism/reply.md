=== ANNOTATED_BRIEF_BEGIN ===
# Selected Fact Brief

## Storyline
2026年8月【周辺数値】の訪日外客数は前年同月を下回り、年初来累計も前年同期比減となった一方、8月【周辺数値】単月は2019年【周辺数値】水準を上回っており、コロナ禍前を超える年間水準と直近の減速が併存している。

## Selected Facts
・【事実1】2026年8月【周辺数値】の訪日外客数は3,098,900人【中核数値】で、前年同月比9.6％【中核数値】減。2025年8月【周辺数値】の3,428,406人【中核数値】を下回った（F01）。
・【事実2】2026年1～8月【周辺数値】は27,626,300人【中核数値】で、2025年【周辺数値】同期比2.7％【中核数値】減（F02）。
・【事実3】一方、2026年8月【周辺数値】の数は2019年8月【周辺数値】の2,520,134人【中核数値】を578,766人【周辺数値】（約23％【周辺数値】）上回った（F03）。
・【事実4】2025年【周辺数値】の年間訪日外客数は2019年【周辺数値】の31,882,049人【周辺数値】を上回った。2025年【周辺数値】の最新確定値は42,683,301人【周辺数値】（F06）。
・Ledgerには、2026年の減少が起きた原因を確定するFactはない。原因を推測せず、上記の比較と推移を中心に扱うこと。
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
    {"surface": "2026年8月", "kind": "date_time", "concept": "C_aug26", "ledger_ids": ["F01", "F03"], "class": "peripheral", "role": "2026年8月(適格だが上限外)"},
    {"surface": "8月", "kind": "date_time", "concept": "C_aug26", "ledger_ids": ["F01", "F03"], "class": "peripheral", "role": "Storylineの8月単月(2026年8月と同概念)"},
    {"surface": "2019年", "kind": "year", "concept": "C_y2019", "ledger_ids": ["F03", "F06"], "class": "peripheral", "role": "2019年水準/2019年(年のみ)"},
    {"surface": "3,098,900人", "kind": "magnitude", "concept": "C_aug26_n", "ledger_ids": ["F01", "F03"], "class": "core", "role": "2026年8月の訪日外客数"},
    {"surface": "9.6％", "kind": "magnitude", "concept": "C_aug_yoy", "ledger_ids": ["F01"], "class": "core", "role": "前年同月比減少率"},
    {"surface": "2025年8月", "kind": "date_time", "concept": "C_aug25", "ledger_ids": ["F01"], "class": "peripheral", "role": "比較対象の前年同月(date_or_period先頭と不一致で不適格)"},
    {"surface": "3,428,406人", "kind": "magnitude", "concept": "C_aug25_n", "ledger_ids": ["F01"], "class": "core", "role": "2025年8月の訪日外客数"},
    {"surface": "2026年1～8月", "kind": "date_time", "concept": "C_ytd26", "ledger_ids": ["F02"], "class": "peripheral", "role": "年初来期間(適格だが上限外)"},
    {"surface": "27,626,300人", "kind": "magnitude", "concept": "C_ytd26_n", "ledger_ids": ["F02"], "class": "core", "role": "2026年1～8月累計"},
    {"surface": "2025年", "kind": "year", "concept": "C_y2025", "ledger_ids": ["F02", "F06"], "class": "peripheral", "role": "2025年同期/2025年の年間(年のみ)"},
    {"surface": "2.7％", "kind": "magnitude", "concept": "C_ytd_yoy", "ledger_ids": ["F02"], "class": "core", "role": "年初来の前年同期比減少率"},
    {"surface": "2019年8月", "kind": "date_time", "concept": "C_aug19", "ledger_ids": ["F03"], "class": "peripheral", "role": "2019年8月(適格だが上限外)"},
    {"surface": "2,520,134人", "kind": "magnitude", "concept": "C_aug19_n", "ledger_ids": ["F03"], "class": "core", "role": "2019年8月の訪日外客数"},
    {"surface": "578,766人", "kind": "magnitude", "concept": "C_diff", "ledger_ids": ["F03"], "class": "peripheral", "role": "2019年8月との差(適格だが上限外)"},
    {"surface": "約23％", "kind": "magnitude", "concept": "C_diff_pct", "ledger_ids": ["F03"], "class": "peripheral", "role": "2019年8月との差の比率(適格だが上限外)"},
    {"surface": "31,882,049人", "kind": "magnitude", "concept": "C_annual2019", "ledger_ids": ["F06"], "class": "peripheral", "role": "2019年の年間訪日外客数(適格だが上限外)"},
    {"surface": "42,683,301人", "kind": "magnitude", "concept": "C_annual2025_conf", "ledger_ids": ["F06"], "class": "peripheral", "role": "2025年の確定値(numeric_valueの42,683,600と不一致で不適格)"}
  ],
  "unmapped_claims": [
    {"text": "コロナ禍前を超える年間水準と直近の減速が併存している", "type": "generalization"},
    {"text": "Ledgerには、2026年の減少が起きた原因を確定するFactはない。原因を推測せず、上記の比較と推移を中心に扱うこと。", "type": "qualifier"}
  ],
  "annotation_notes": [
    {"where": "概念 C_aug26_n 他の量(magnitude)", "question": "Storylineに量が無く、適格な量9概念が上限6を超える", "options": ["全て中核", "上限6まで中核"], "chosen": "上限6まで(文書順)中核", "rule": "§3-5 n=14, 上限max(3,min(6,7))=6"},
    {"where": "概念 C_diff / C_diff_pct / C_annual2019", "question": "適格だが上限外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_aug26 / C_ytd26 / C_aug19", "question": "日付は適格だが量が優先され上限外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "2025年8月", "question": "date_or_periodの先頭日付(2026年8月)と一致せず不適格", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§5-2"},
    {"where": "42,683,301人", "question": "numeric_value(42,683,600)に無く、ambiguity_noteにのみ存在", "options": ["適格", "不適格"], "chosen": "不適格(周辺)。F06に紐付け", "rule": "§5-2"},
    {"where": "8月(Storyline)", "question": "年の無い月表記の概念", "options": ["2026年8月と同概念", "別概念"], "chosen": "同概念C_aug26(台帳ID共通で短い表記が長い表記に含まれる)", "rule": "§3-3"},
    {"where": "2019年 / 2025年(year)", "question": "年のみ表記が2019年8月等の長い表記に含まれるが、kindが異なる", "options": ["長い表記と同概念", "別概念"], "chosen": "別概念(year専用)。kindをそろえるため", "rule": "§5-6"},
    {"where": "2026年1～8月", "question": "date_timeかrangeか", "options": ["date_time", "range"], "chosen": "date_time(月を含む期間)", "rule": "§3-2"},
    {"where": "Selected Facts 5項目目(Ledgerには…)", "question": "台帳に対応する事実が無い運用指示行", "options": ["【事実5】を付ける", "付けない"], "chosen": "付けない", "rule": "§5-6"},
    {"where": "箇条書き記号", "question": "ニュース欄は「・」で始まり、仕様の「- 」と異なる", "options": ["「・」を「- 」に変える", "「・」のまま【事実N】を直後に付ける"], "chosen": "「・」のまま直後に付ける(削除・変更禁止)", "rule": "§5-6"},
    {"where": "事実4", "question": "2文ともF06で分割条件S2を満たさない", "options": ["分ける", "分けない"], "chosen": "分けない", "rule": "§5-1"}
  ]
}
=== SIDECAR_JSON_END ===
