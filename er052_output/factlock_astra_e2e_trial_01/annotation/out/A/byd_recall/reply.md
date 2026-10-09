=== ANNOTATED_BRIEF_BEGIN ===
# Selected Fact Brief

## Storyline
中国国内の召回公告でBYDは唐系・秦系の計183,211台【中核数値】を対象とし、製造上の材料異常で制動ペダルのストッパーパッドが長期使用後に割れ、極端な場合には脱落して制動灯が点き続け、後続車に誤信号を送る安全上の懸念があるとして、改善部品への無料交換を行う。

## Selected Facts
- 【事実1】対象台数は唐系142,895台【中核数値】、秦系40,316台【中核数値】。規制当局公告によると、制動ペダルの限位垫（ストッパーパッド）に材料異常があり、長期間の使用でひび割れ・破損する可能性がある。極端な場合に脱落すると、ペダルを踏んでいないときにも制動灯が点灯し続け、後方車両に誤った信号を伝える懸念がある。BYDは認定販売店を通じ、改善後の部品へ無料交換する。
=== ANNOTATED_BRIEF_END ===
=== SIDECAR_JSON_BEGIN ===
{
  "slug": "byd_recall", "annotator": "A",
  "spec_sha256": "8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57",
  "brief_sha256": "f374a470436438e3cbf01b3dc0b98bfc1dedab7bc78c99c926f3a97dc07181b0",
  "facts": [ {"n": 1, "ledger_ids": ["BYD-RECALL-01", "BYD-RECALL-06", "BYD-RECALL-07", "BYD-RECALL-08", "BYD-RECALL-11"]} ],
  "numbers": [
    {"surface": "183,211台", "kind": "magnitude", "concept": "C_total", "ledger_ids": ["BYD-RECALL-01"], "class": "core", "role": "召回対象の合算台数(Storyline)"},
    {"surface": "142,895台", "kind": "magnitude", "concept": "C_tang", "ledger_ids": ["BYD-RECALL-01"], "class": "core", "role": "唐系の対象台数"},
    {"surface": "40,316台", "kind": "magnitude", "concept": "C_qin", "ledger_ids": ["BYD-RECALL-01", "BYD-RECALL-02", "BYD-RECALL-04"], "class": "core", "role": "秦系の対象台数"}
  ],
  "unmapped_claims": [],
  "annotation_notes": [
    {"where": "Selected Facts の1項目(4文)", "question": "文の境目で分けるか(S1,S2を満たすと4つ以上の事実に分かれる)", "options": ["4事実に分ける", "分けない(1事実)"], "chosen": "分けない(1事実、ledger_idsに関連IDを併記)", "rule": "§2 / §5-1"},
    {"where": "概念 C_total / C_tang / C_qin", "question": "n=3で上限3のため、適格な3概念が全て中核になる", "options": ["中核", "周辺"], "chosen": "中核(3つとも numeric_value に含まれ適格)", "rule": "§3-5"}
  ]
}
=== SIDECAR_JSON_END ===
