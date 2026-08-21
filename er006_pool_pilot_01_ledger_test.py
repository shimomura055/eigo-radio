# ============================================================
# er006_pool_pilot_01_ledger_test.py
# ER-006-POOL-PILOT-01: build_ledger_text_from_vfl()のregression test
# ============================================================
# Topic 3(pool_startups)で発見したPipeline/Systemic issueの再発防止テスト。
# 旧版は各Factの[source: ...]行に内部ID(SRC-003/E-001)しか含んでおらず、
# Writerが著者名・発表年・掲載誌をLedgerからではなく自身の一般知識から補って
# 記事に書き、それをDeviation Checkが「Ledgerにない新規Fact」として誤検知して
# いた(5件、Topic 3のB1/A2両方で再現)。
# 恒久対策としてer006_pool_pilot_01_ledger.pyのLedger変換に引用メタデータを
# 埋め込むよう修正した。このテストは、その埋め込みが将来のリファクタで
# 再度失われないことを保証する。
from __future__ import annotations

from er006_pool_pilot_01_ledger import build_ledger_text_from_vfl

evidence_parsed = {
    "sources": [
        {
            "source_id": "SRC-001",
            "title": "Example Paper on Network Effects",
            "authors_or_organization": "Katz, M. and Shapiro, C.",
            "publication_date": "1985",
            "doi": None,
            "access_status": "OPEN_ACCESS",
        },
    ],
    "evidence_items": [
        {"evidence_id": "E-001", "source_id": "SRC-001", "source_location": "p.3"},
    ],
}
vfl_parsed = {
    "facts": [
        {
            "fact_id": "F-001",
            "claim": "Network effects were formally analyzed in 1985.",
            "evidence_id": "E-001",
            "source_id": "SRC-001",
            "causal_strength": "DIRECT",
        },
    ],
}

ledger_text = build_ledger_text_from_vfl(vfl_parsed, evidence_parsed, "Test Title")

assert "=== Source一覧 ===" in ledger_text, "Source一覧セクションが失われている"
assert "Katz, M. and Shapiro, C." in ledger_text, "Source一覧に著者名が含まれていない"

fact_block_start = ledger_text.index("[F-001]")
fact_block = ledger_text[fact_block_start:fact_block_start + 400]
assert "Katz, M. and Shapiro, C." in fact_block, (
    "FactのsourceにCatalog行の著者名が埋め込まれていない"
    "(Topic 3で発見したPipeline/Systemic issueが再発している可能性)"
)
assert "(1985)" in fact_block, "Factのsourceに発表年が埋め込まれていない"

# journal_or_venueがある場合も反映されることを確認(Topic 3後にスキーマへ追加したフィールド)
evidence_parsed2 = json_copy = {
    "sources": [dict(evidence_parsed["sources"][0], journal_or_venue="Journal of Economics")],
    "evidence_items": evidence_parsed["evidence_items"],
}
ledger_text2 = build_ledger_text_from_vfl(vfl_parsed, evidence_parsed2, "Test Title")
fact_block2 = ledger_text2[ledger_text2.index("[F-001]"):ledger_text2.index("[F-001]") + 400]
assert "Journal of Economics" in fact_block2, "journal_or_venueがFactのsource行に反映されていない"

print("OK: er006_pool_pilot_01_ledger_test.py all assertions passed")
