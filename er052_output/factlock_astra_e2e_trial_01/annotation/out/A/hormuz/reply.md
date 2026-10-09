=== ANNOTATED_BRIEF_BEGIN ===
# Selected Fact Brief

## Storyline
トランプ氏のホルムズ海峡通航貨物への20％【中核数値】償還料案は翌日に湾岸諸国の対米貿易・投資案件へ置き換えられたが、Brentは撤回後に一時上げ幅を縮めただけで高水準へ戻った。7月13日【周辺数値】の急騰も海上封鎖や供給懸念と結び付けられており、相場では案の撤回後も地政学的リスクが意識されていた。

## Selected Facts
- 【事実1】7月13日【周辺数値】午前、トランプ氏はホルムズ海峡を通るすべての貨物について、米国の安全確保費用として20％【中核数値】の償還を求めると投稿した。
- 【事実2】同日のBrent先物は7.29ドル【中核数値】（9.59％【中核数値】）上昇し、83.30ドル【中核数値】で清算された。Reutersはこの上昇を、翌日に始まる予定とされた米国の対イラン海上封鎖と、海峡を通るエネルギー輸送への懸念に関連付けた。20％【中核数値】案だけが上昇の原因だったとは断定しない。
- 【事実3】7月14日【周辺数値】午前、トランプ氏は20％【中核数値】償還料案を湾岸諸国による対米貿易・投資案件に置き換えると投稿した。
- 【事実4】置換発表後、Brentは一時上げ幅を縮小したが、ほどなく発表前に近い高い水準へ戻った。記事掲載時点では約2.6％【周辺数値】高、1バレル85ドル超【周辺数値】と報じられ、海上封鎖や攻撃、タンカー安全上の懸念も続いていた。撤回後に原油価格が全面的に下落したとは書かない。
=== ANNOTATED_BRIEF_END ===
=== SIDECAR_JSON_BEGIN ===
{
  "slug": "hormuz", "annotator": "A",
  "spec_sha256": "8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57",
  "brief_sha256": "73afafe8c17aac57da2f2f7034f4200c32c1a4dfdf62a2e421d265fb33a708cf",
  "facts": [
    {"n": 1, "ledger_ids": ["HF-002"]},
    {"n": 2, "ledger_ids": ["HF-006"]},
    {"n": 3, "ledger_ids": ["HF-007"]},
    {"n": 4, "ledger_ids": ["HF-009"]}
  ],
  "numbers": [
    {"surface": "20％", "kind": "magnitude", "concept": "C_rate20", "ledger_ids": ["HF-002", "HF-003", "HF-007"], "class": "core", "role": "償還料の率(Storylineに出る量)"},
    {"surface": "7月13日", "kind": "date_time", "concept": "C_0713", "ledger_ids": ["HF-002", "HF-003", "HF-005", "HF-006"], "class": "peripheral", "role": "提案日・Brent急騰日"},
    {"surface": "7.29ドル", "kind": "magnitude", "concept": "C_up729", "ledger_ids": ["HF-006"], "class": "core", "role": "Brent前日比上昇額"},
    {"surface": "9.59％", "kind": "magnitude", "concept": "C_up959", "ledger_ids": ["HF-006"], "class": "core", "role": "Brent前日比上昇率"},
    {"surface": "83.30ドル", "kind": "magnitude", "concept": "C_settle8330", "ledger_ids": ["HF-005", "HF-006"], "class": "core", "role": "7月13日のBrent清算値"},
    {"surface": "7月14日", "kind": "date_time", "concept": "C_0714", "ledger_ids": ["HF-007", "HF-008"], "class": "peripheral", "role": "置換発表日"},
    {"surface": "約2.6％", "kind": "magnitude", "concept": "C_up26", "ledger_ids": ["HF-009"], "class": "peripheral", "role": "記事掲載時点のBrent上昇率"},
    {"surface": "1バレル85ドル超", "kind": "magnitude", "concept": "C_over85", "ledger_ids": ["HF-009"], "class": "peripheral", "role": "記事掲載時点のBrent価格"}
  ],
  "unmapped_claims": [
    {"text": "相場では案の撤回後も地政学的リスクが意識されていた", "type": "generalization"}
  ],
  "annotation_notes": [
    {"where": "概念数 n", "question": "n=8(20％・7月13日・7月14日・7.29ドル・9.59％・83.30ドル・約2.6％・1バレル85ドル超)で上限は4", "options": ["上限3", "上限4"], "chosen": "上限4", "rule": "§3-5-3"},
    {"where": "概念 C_up26", "question": "適格だが上限4の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_over85", "question": "適格だが上限4の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_0713 / C_0714", "question": "日付は適格だが上限4の外(優先順は量の後)", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "【事実2】", "question": "3文を分けるか(2文目は同じHF-006、3文目は限定文)", "options": ["分ける", "分けない"], "chosen": "分けない", "rule": "§5-1"},
    {"where": "【事実4】", "question": "3文を分けるか(2文目HF-009、3文目は限定文)", "options": ["分ける", "分けない"], "chosen": "分けない", "rule": "§5-1"},
    {"where": "1バレル85ドル超", "question": "「1バレル」を表記に含めるか(数字に直接つく単位表現)", "options": ["含める", "85ドル超のみ"], "chosen": "含める(主数字は85)", "rule": "§5-5"},
    {"where": "約2.6％高", "question": "「高」をヘッジ語として含めるか", "options": ["含める", "含めない"], "chosen": "含めない(約2.6％)", "rule": "§3-1"}
  ]
}
=== SIDECAR_JSON_END ===
