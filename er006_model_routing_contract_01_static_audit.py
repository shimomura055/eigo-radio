# ============================================================
# er006_model_routing_contract_01_static_audit.py
# ER-006-MODEL-ROUTING-CONTRACT-01 / 追補: Static Audit Test(SSOT迂回防止)
# ============================================================
# 目的: production-reachableなファイル内で、Approved Model判定を要する
# leaf関数(run_writer_with_technical_retry/run_deviation_check/
# make_fact_checker_fn/run_support_text/make_selector_fn/
# make_canonicalization_fn)への**全ての**呼び出し箇所を機械的に検出し、
# その呼び出しがSSOT(er006_model_routing_contract_01.require_model)を
# 経由するmodel指定を伴っているかを検証する。
#
# 「既知の正しい行がまだそこにあるか」を確認するだけの前回版とは異なり、
# 今回は関数呼び出しパターンそのものを正規表現でスキャンするため、
# 新しいcall siteが追加されてSSOTを経由しなかった場合、その新しい行も
# 含めて検出できる(=新規callerがSSOTを迂回するとこのtestがFAILする)。
from __future__ import annotations

import re

# (production-reachableと定義したファイル, そのファイル内で許可される
#  「SSOT経由の目印」トークンの正規表現)
PRODUCTION_FILES = {
    "er003_v1_n3_01_articles_generate.py": r"routing\.require_model\(",
    "er003_v1_n3_01_scaffold_generate.py": r"routing\.require_model\(|_b1_support_model\(\)|_a2_support_model\(\)",
    "er006_pool_pilot_01_support.py": r"routing\.require_model\(",
    "er006_pool_pilot_01_research.py": r"routing\.require_model\(",
}

# 検査対象のleaf関数呼び出し(この関数名の直後に"("が来るものを検出する)
GATED_FUNCTIONS = [
    "run_writer_with_technical_retry",
    "run_deviation_check",
    "make_fact_checker_fn",
    "run_support_text",
    "make_selector_fn",
    "make_canonicalization_fn",
]

# 呼び出し箇所から、閉じ括弧までの実引数リストを取り出す(単純な括弧対応
# カウント。文字列リテラル内の括弧は今回のcodebaseでは対象呼び出しの
# 引数に現れないため考慮しない)。
def extract_call_args(text: str, call_start: int) -> str:
    depth = 0
    i = text.index("(", call_start)
    start = i
    for j in range(i, len(text)):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                return text[start:j + 1]
    return text[start:]


CONTEXT_WINDOW_CHARS = 400  # 呼び出し直前の局所変数計算(例: model = routing.require_model(...))
                            # まで見えるようにする、呼び出し引数だけでは足りないため


def find_call_sites(text: str, fn_name: str) -> list[tuple[int, str, str]]:
    """text中の`fn_name(...)`呼び出し(directとmodule.fn_name(...)の両方)を
    列挙し、(行番号, 引数文字列, 直前の局所コンテキスト込みの文字列)を返す。
    定義(`def fn_name`)は除外する。"""
    sites = []
    for m in re.finditer(rf"(?<!def )(?:\w+\.)?{re.escape(fn_name)}\s*\(", text):
        args = extract_call_args(text, m.start())
        line_no = text.count("\n", 0, m.start()) + 1
        window_start = max(0, m.start() - CONTEXT_WINDOW_CHARS)
        context = text[window_start:m.start()] + args
        sites.append((line_no, args, context))
    return sites


def run():
    failures = []
    total_checked = 0

    print("=== SSOT迂回防止: leaf関数への全call siteがSSOTを経由しているか ===")
    for filename, ssot_marker_pattern in PRODUCTION_FILES.items():
        text = open(filename, encoding="utf-8").read()
        for fn_name in GATED_FUNCTIONS:
            sites = find_call_sites(text, fn_name)
            for line_no, args, context in sites:
                total_checked += 1
                # "model=..."を直接渡す形と、"**kwargs"展開でmodelを条件付きで
                # 渡す形(kwargs["model"]=...を直前で組み立てるパターン)の両方を許容する。
                has_model_kw = ("model=" in args) or ("**kwargs" in args)
                has_ssot_marker = re.search(ssot_marker_pattern, context) is not None
                ok = has_model_kw and has_ssot_marker
                status = "OK" if ok else "FAIL"
                print(f"[{status}] {filename}:{line_no} {fn_name}(...) "
                      f"model={'あり' if has_model_kw else 'なし'} SSOT経由={'あり' if has_ssot_marker else 'なし'}")
                if not ok:
                    failures.append(f"{filename}:{line_no} {fn_name}() がSSOT経由のmodel指定を伴っていない"
                                     f"(新しいcaller追加時にSSOTを迂回した可能性)")

    print(f"\n({total_checked}件のcall siteを検査)")

    print("\n=== Negative: 素のgpt-5.6-solが production files に復活していないこと ===")
    for filename in PRODUCTION_FILES:
        text = open(filename, encoding="utf-8").read()
        ok = re.search(r'model="gpt-5\.6-sol"', text) is None
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {filename}: 'gpt-5.6-sol' literal not present")
        if not ok:
            failures.append(f"{filename}: gpt-5.6-sol literal found")

    print("\n=== 回帰確認: 意図的にSSOT経由を外した偽陽性コードで検出できるか(self-test) ===")
    fake_text_bad = 'result = run_support_text(client, role, context, max_attempts=2)\n'  # model=なし
    fake_text_bad2 = 'result = run_support_text(client, role, context, model="gpt-5.6-sol")\n'  # SSOT経由でない
    fake_text_good = 'result = run_support_text(client, role, context, model=_b1_support_model())\n'
    for name, fake_text, should_detect_violation in [
        ("modelなし", fake_text_bad, True),
        ("SSOT経由でないmodel", fake_text_bad2, True),
        ("正しいSSOT経由", fake_text_good, False),
    ]:
        sites = find_call_sites(fake_text, "run_support_text")
        assert len(sites) == 1, f"self-test fixture自体が想定通り検出できなかった: {name}"
        _, args, context = sites[0]
        has_model_kw = "model=" in args
        has_ssot_marker = re.search(PRODUCTION_FILES["er003_v1_n3_01_scaffold_generate.py"], context) is not None
        violation_detected = not (has_model_kw and has_ssot_marker)
        ok = violation_detected == should_detect_violation
        status = "OK" if ok else "FAIL"
        print(f"[{status}] self-test({name}): violation_detected={violation_detected} (expected {should_detect_violation})")
        if not ok:
            failures.append(f"self-test({name}) failed — audit機構自体が偽陽性/偽陰性を検出できていない")

    if failures:
        raise AssertionError(f"{len(failures)}件のstatic audit checkが失敗した:\n" + "\n".join(f"  - {f}" for f in failures))
    print(f"\nOK: 全チェックPASS(production call site {total_checked}件 + negative + self-test)")


if __name__ == "__main__":
    run()
