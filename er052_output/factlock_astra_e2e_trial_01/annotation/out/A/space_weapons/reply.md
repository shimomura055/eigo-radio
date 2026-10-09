=== ANNOTATED_BRIEF_BEGIN ===
# Selected Fact Brief

## Storyline
米国が軌道上の「space control weapons」配備を初めて公に認めた発言を起点に、従来の地上発射ASATや通常の衛星任務、広義のcounterspaceと区別し、既存条約が禁じる範囲を誇張せず整理する。

## Selected Facts
- 【事実1】F-001：2026年9月14日【中核数値】、米空軍長官Troy Meinkは、敵対的な相手の行動から統合軍を防護できる軌道上のspace control weaponsを米国が配備していると述べた。米政府機関の公式記事は、これをSpace Forceが宇宙に兵器を配備したことを初めて認めた発言として記録している。具体的なシステム名や攻撃能力は補わない。
- 【事実2】F-003：地上発射型ASATミサイルによる衛星破壊は過去にも行われており、ロシアは2021年【周辺数値】にCOSMOS 1408【周辺数値】を破壊した。これは地上から発射した試験であり、兵器の軌道上配備とは区別する。
- 【事実3】F-011：米宇宙軍の用語では、counterspace operationsは軌道、通信リンク、地上の各セグメントでの行動を指す。したがってcounterspaceは、宇宙空間に置かれた兵器だけを意味しない。
- 【事実4】F-015：GPS、ミサイル追跡、宇宙領域認識、衛星アーキテクチャのレジリエンスは、米宇宙軍が継続的な任務・優先事項として説明している。こうした衛星運用・保護の任務は、攻撃兵器の軌道上配備とは分けて扱う。
- 【事実5】F-016：Outer Space Treaty第4条【周辺数値】は、核兵器その他の大量破壊兵器の軌道上配備などを禁じる一方、宇宙兵器全般を包括的に禁止するとは記していない。この条文だけから個別の配備の適法性を断定しない。
=== ANNOTATED_BRIEF_END ===
=== SIDECAR_JSON_BEGIN ===
{
  "slug": "space_weapons", "annotator": "A",
  "spec_sha256": "8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57",
  "brief_sha256": "84c69f1329262f9868be25af77baa47b6afc2f7184ec8999affc232e19b421f9",
  "facts": [
    {"n": 1, "ledger_ids": ["F-001"]},
    {"n": 2, "ledger_ids": ["F-003"]},
    {"n": 3, "ledger_ids": ["F-011"]},
    {"n": 4, "ledger_ids": ["F-015"]},
    {"n": 5, "ledger_ids": ["F-016"]}
  ],
  "numbers": [
    {"surface": "2026年9月14日", "kind": "date_time", "concept": "C_meinke_date", "ledger_ids": ["F-001"], "class": "core", "role": "米空軍長官の発言日"},
    {"surface": "2021年", "kind": "year", "concept": "C_year_2021", "ledger_ids": ["F-003"], "class": "peripheral", "role": "COSMOS 1408破壊の年(年だけ)"},
    {"surface": "COSMOS 1408", "kind": "name_embedded", "concept": "C_cosmos", "ledger_ids": ["F-003"], "class": "peripheral", "role": "衛星名の一部の番号"},
    {"surface": "第4条", "kind": "ordinal", "concept": "C_ost_art4", "ledger_ids": ["F-016"], "class": "peripheral", "role": "Outer Space Treaty条文番号"}
  ],
  "unmapped_claims": [],
  "annotation_notes": [
    {"where": "事実2「過去にも行われており」", "question": "一般化の文だが台帳F-003(2021年)のほかF-004/F-005にも根拠がある。ledger_idsに加えるか", "options": ["F-003のみ", "F-003,F-004,F-005"], "chosen": "F-003のみ(項目見出しの台帳IDに合わせ、主な根拠は2021年の事例)", "rule": "§5-1"},
    {"where": "概念 n=1(2026年9月14日のみ)", "question": "上限は3、適格(date_or_period先頭の日付2026年9月14日と一致)", "options": ["中核", "周辺"], "chosen": "中核", "rule": "§3-5"},
    {"where": "COSMOS 1408", "question": "数量か名称内番号か", "options": ["magnitude", "name_embedded"], "chosen": "name_embedded", "rule": "§5-3"}
  ]
}
=== SIDECAR_JSON_END ===
