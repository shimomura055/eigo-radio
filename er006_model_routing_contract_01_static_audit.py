# ============================================================
# er006_model_routing_contract_01_static_audit.py
# ER-006-MODEL-ROUTING-CONTRACT-01: Static Audit Test
# ============================================================
# Production到達可能な、B1/A2 Writer・Writer Fact Check・B1/A2 Support・
# Support Fact Checkの実際のAPI呼び出し箇所に、routing.require_model()を
# 経由した明示的なmodel指定が残っていることを確認する(=退行検知)。
# 「gpt-5.6-sol」という文字列自体は、Translation pipeline・preflight script・
# 過去の実験タスク(ER-005等)など、このタスクのスコープ外の場所に多数残って
# いる。それらは意図的にPool/N3 Production経路の対象外としており削除しない。
# ここでは「対象と定義した production-reachable な呼び出し箇所」だけを
# 個別に検査する(全ファイルへの一般的なgrep検査は行わない、過剰検知のため)。
from __future__ import annotations

import re

# (file, 期待する内容の正規表現, 説明)
PRODUCTION_REACHABLE_CHECKS = [
    ("er003_v1_n3_01_articles_generate.py",
     r'vfl01\.run_writer_with_technical_retry\(client, prompt, model=_WRITER_MODEL\)',
     "B1/A2 Writer呼び出しがrouting経由のmodelを明示指定している"),
    ("er003_v1_n3_01_articles_generate.py",
     r'r3\.make_fact_checker_fn\(fc_prompt, model=_WRITER_FACT_CHECK_MODEL\)',
     "Writer Fact Check呼び出しがrouting経由のmodelを明示指定している"),
    ("er003_v1_n3_01_articles_generate.py",
     r'vfl01\.run_deviation_check\(client, verified_ledger_text, article_text, model=_WRITER_MODEL\)',
     "Deviation Check呼び出しがrouting経由のmodelを明示指定している"),
    ("er003_v1_n3_01_articles_generate.py",
     r'_WRITER_MODEL = routing\.require_model\("B1_WRITER", routing\.WRITER_MODEL\)',
     "_WRITER_MODELがModel Contract経由で確定している"),
    ("er003_v1_n3_01_scaffold_generate.py",
     r'b1s\.run_support_text\(client, b1s\.COMMENT_1_ROLE, c1_context, model=_B1_SUPPORT_MODEL\)',
     "B1 Support(Comment1)呼び出しがrouting経由のmodelを明示指定している"),
    ("er003_v1_n3_01_scaffold_generate.py",
     r'a2gen\.run_support_text\(client, a2gen\.COMMENT_1_ROLE, c1_context, model=_A2_SUPPORT_MODEL\)',
     "A2 Support(Comment1)呼び出しがrouting経由のmodelを明示指定している"),
    ("er003_v1_n3_01_scaffold_generate.py",
     r'_B1_SUPPORT_MODEL = routing\.require_model\("B1_SUPPORT", routing\.SUPPORT_MODEL\)',
     "_B1_SUPPORT_MODELがModel Contract経由で確定している"),
    ("er006_pool_pilot_01_support.py",
     r'routing\.require_model\("SUPPORT_FACT_CHECK", routing\.SUPPORT_FACT_CHECK_MODEL\)',
     "Support Fact Check呼び出しがrouting経由のmodelを明示指定している"),
    ("er006_pool_pilot_01_research.py",
     r'routing\.require_model\("EVIDENCE_PACK", routing\.RESEARCH_MODEL\)',
     "Evidence Pack呼び出しがrouting経由のmodelを明示指定している"),
    ("er006_pool_pilot_01_research.py",
     r'routing\.require_model\("VFL", routing\.RESEARCH_MODEL\)',
     "VFL呼び出しがrouting経由のmodelを明示指定している"),
    ("er006_pool_pilot_01_research.py",
     r'routing\.require_model\("VERIFICATION", routing\.RESEARCH_MODEL\)',
     "Verification呼び出しがrouting経由のmodelを明示指定している"),
    ("er006_pool_pilot_01_research.py",
     r'routing\.require_provider\("EXCEPTION_SEARCH", "perplexity"\)',
     "Exception SearchがPerplexity providerを明示検証している"),
]

# 上記のexplicit override呼び出し箇所自体に、素のSol指定が復活していないかの
# 否定チェック(model="gpt-5.6-sol" が直接埋め込まれていないこと)。
NEGATIVE_CHECKS = [
    ("er003_v1_n3_01_articles_generate.py", r'model="gpt-5\.6-sol"'),
    ("er003_v1_n3_01_scaffold_generate.py", r'model="gpt-5\.6-sol"'),
    ("er006_pool_pilot_01_support.py", r'model="gpt-5\.6-sol"'),
    ("er006_pool_pilot_01_research.py", r'model="gpt-5\.6-sol"'),
]


def run():
    failures = []
    print("=== Positive: production-reachable呼び出し箇所がroutingを経由している ===")
    for filename, pattern, desc in PRODUCTION_REACHABLE_CHECKS:
        text = open(filename, encoding="utf-8").read()
        ok = re.search(pattern, text) is not None
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {filename}: {desc}")
        if not ok:
            failures.append(f"{filename}: {desc}")

    print("\n=== Negative: 素のgpt-5.6-solが復活していないこと ===")
    for filename, pattern in NEGATIVE_CHECKS:
        text = open(filename, encoding="utf-8").read()
        ok = re.search(pattern, text) is None
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {filename}: 'gpt-5.6-sol' literal not present")
        if not ok:
            failures.append(f"{filename}: gpt-5.6-sol literal found")

    if failures:
        raise AssertionError(f"{len(failures)}件のstatic audit checkが失敗した: {failures}")
    print(f"\nOK: 全{len(PRODUCTION_REACHABLE_CHECKS) + len(NEGATIVE_CHECKS)}件のstatic audit check PASS")


if __name__ == "__main__":
    run()
