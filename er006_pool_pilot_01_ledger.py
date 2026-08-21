# ============================================================
# er006_pool_pilot_01_ledger.py
# ER-006-POOL-PILOT-01: VFL(JSON) -> production Writer向けplain-text Ledger変換
# ============================================================
# ER-005-WRITER-COST-QUALITY-01のbuild_ledger_text_from_vfl()を土台に、
# 各Factへsource側の引用メタデータ(著者/組織・発表年・掲載誌)を直接
# 埋め込むよう拡張した。
#
# 背景(ER-006-POOL-PILOT-01 Topic 3で発見、Pipeline/Systemic issue):
# 旧版はFactへ"source: SRC-003/E-001"という内部IDだけを埋め込んでいた。
# Writerは記事内で出典に自然に触れようとした結果、著者名・発表年・
# 掲載誌名をLedgerからではなく自身の一般知識から補って書き、Ledger
# Deviation Check(記事の記述はLedgerに書かれた範囲を超えてはならない)
# がこれを「Ledgerにない新規Fact」として毎回検知していた
# (Business Horizons誌のKuratko et al. 2020、NFXのPete Flint 2020等、
# 5件の同種MINOR deviationがTopic 3のB1/A2両方で再現)。
# 検知された引用自体はいずれも事実として正しかった(捏造ではない)が、
# Ledgerに書いていない情報を記事が「知っている」形になるのは望ましくない。
# 個別記事のprompt調整ではなく、Ledger変換そのものに引用メタデータを
# 含めることで、今後のPool記事全件に対する恒久対策とする。
from __future__ import annotations


def build_ledger_text_from_vfl(vfl_parsed: dict, evidence_parsed: dict, title: str) -> str:
    evidence_by_id = {e["evidence_id"]: e for e in evidence_parsed["evidence_items"]}
    source_by_id = {s["source_id"]: s for s in evidence_parsed["sources"]}
    lines = [
        f"ER-006-POOL-PILOT-01 Verified Fact Ledger: {title}",
        "(Evidence Pack型Research Layerで生成。新しいFactの追加・削除は行っていない)",
        "",
        "注記1: 本Ledgerは、number_classification(ANCHOR/SUPPORTING/DISPENSABLE)および",
        "exactness_requirement(EXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLY)の個別タグを",
        "含まない。Spoken-first原則(数字の扱い、A〜E)は編集判断として適用すること。",
        "",
        "注記2: 各Factの[source: ...]行には、著者/組織・発表年・掲載誌を明記している。",
        "記事内で出典に触れる場合は、この行に書かれた情報の範囲内で正確に引用すること",
        "(書かれていない詳細を一般知識から補わない)。",
        "",
        "=== Source一覧 ===",
        "",
    ]
    for sid, s in source_by_id.items():
        cite = f"[{sid}] {s.get('title')} — {s.get('authors_or_organization') or '著者不明'}"
        if s.get("publication_date"):
            cite += f" ({s['publication_date']})"
        if s.get("doi"):
            cite += f" DOI:{s['doi']}"
        if s.get("access_status"):
            cite += f" [access_status: {s['access_status']}]"
        lines.append(cite)
    lines += ["", "=== Fact一覧 ===", ""]

    for f in vfl_parsed["facts"]:
        ev = evidence_by_id.get(f["evidence_id"], {})
        src = source_by_id.get(f["source_id"], {})
        lines.append(f"[{f['fact_id']}] {f['claim']}")
        if f.get("numeric_value"):
            lines.append(f"  numeric_value: {f['numeric_value']}")
        if f.get("numeric_scope"):
            lines.append(f"  numeric_scope: {f['numeric_scope']}")
        lines.append(f"  causal_strength: {f.get('causal_strength')}")
        if f.get("ambiguity"):
            lines.append(f"  ambiguity: {f['ambiguity']}")
        if f.get("scope"):
            lines.append(f"  scope: {f['scope']}")
        source_loc = ev.get("source_location")
        cite_bits = []
        if src.get("authors_or_organization"):
            cite_bits.append(src["authors_or_organization"])
        if src.get("publication_date"):
            cite_bits.append(f"({src['publication_date']})")
        if src.get("journal_or_venue"):
            cite_bits.append(f"in {src['journal_or_venue']}")
        cite_str = " ".join(cite_bits)
        lines.append(f"  source: {f['source_id']}/{f['evidence_id']}"
                      + (f" — {cite_str}" if cite_str else "")
                      + (f" ({source_loc})" if source_loc else ""))
        lines.append("")
    return "\n".join(lines)
