# AUW 委任_02b: 統一ASR判定の配線 静的監査(import graph方式)。DESIGN_02_ADDENDUM_01 §3-2 / OF-AUW-04。
#
# 方式: Production entrypointからASTでimportを辿り(関数内の遅延importも含む)、到達したmodule内の
#       `transcribe | classify_asr_match | classify_ja_asr_match | evaluate_attempt*` の**呼出**を全数列挙し、
#       allowlist(er078_asr_unified_wiring_allowlist_01.json、理由付き)と突合する。手書きの呼出点一覧(DESIGN_01 §3.1)の網羅漏れを機械検出する。
#
# 段階(allowlistの "phase"):
#   pre_wiring  (本委任_02b時点): 現状の呼出一覧をsnapshot化したもの。testは「snapshotとの完全一致」(=未登録の新規ASR呼出が増えていない/
#                                 意図せず消えていない)を検査する。統一judgeはまだentrypointから到達しない。
#   post_wiring (委任_03/04で配線後に切替え): 「統一judge/adapter(allowlist内の internal_modules)経由以外のASR呼出0」をassertする。
#                                 切替え手順: `python er078_asr_unified_wiring_static_audit_01.py --regenerate --phase post_wiring` ではなく、
#                                 allowlist JSONの phase を post_wiring に変え、adapter側の呼出のみを internal として残すこと(理由必須)。
#
# 使い方:
#   python er078_asr_unified_wiring_static_audit_01.py --regenerate   # allowlist(snapshot)を生成/更新
#   pytest er078_asr_unified_wiring_static_audit_01.py -q            # 検査
from __future__ import annotations

import ast
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWLIST_PATH = os.path.join(ROOT, "er078_asr_unified_wiring_allowlist_01.json")

# Production entrypoint(DESIGN_01 §3.1 / 委任文)。globパターンはROOT直下の存在するfileに展開。
ENTRYPOINTS = [
    "er019_family_x_audio_production_runner_01.py",
    "er063_family_z_audio_01.py",
    "er026_family_z_fiction_production_runner_01.py",
    "er012_b_family_voices_a2_production_01.py",
    "er012_b_family_voices_production_01.py",
    "er013_family_c_production_runner_01.py",
    "er012_e_family_entertainment_two_level_runner_01.py",
    "er003_v1_n3_01_tts_generate.py",
]
CALLEE_RE = re.compile(r"^(transcribe|classify_asr_match|classify_ja_asr_match|evaluate_attempt\w*)$")
UNIFIED_MODULES = {"er078_asr_unified_judge_01", "er078_asr_value_guard_01", "er078_pass_with_warning_registry_01"}

# 判定点(DESIGN_01 §3.1 J1〜J11)とmoduleの対応。J11は引継ぎ・再利用経路(追補§3-1)。
JUDGEMENT_POINTS = {
    "J1": ("er003_v1_sing01_voice01_generate", "generate_charon_english"),
    "J2": ("er003_v1_sing01_news_tail_fix", "generate_news_narration_wide_margin"),
    "J3": ("er003_v1_crosslevel_audio_02_common", "_run_a2_minimal_fallback_attempt"),
    "J4": ("er012_b_family_voices_production_01", "generate_voice_body_wide_margin"),
    "J5": ("er003_v1_repro01_main_generate", "generate_narration_snippet_verified_strict"),
    "J6": ("er003_v1_sing01_point_headings_aoede", None),
    "J7": ("er003_v1_n3_01_tts_generate", ("apply_a2_slowdown_postprocess", "_post_slowdown_cascade_rescue")),
    "J8": ("er003_v1_n3_01_tts_generate", "generate_a2_japanese_with_fallback"),
    "J9": ("er003_v1_sing01_voice01_generate", "generate_charon_japanese"),
    "J10": ("er003_v1_sing01_voice01_generate", "generate_charon_japanese"),
    "J11": ("er019_family_x_validation_inheritance_01", "rejudge_with_current_judge"),
}


def _local_module(name: str, root: str = ROOT):
    if not name:
        return None
    top = name.split(".")[0]
    return top if os.path.exists(os.path.join(root, top + ".py")) else None


def _parse(path: str):
    with open(path, encoding="utf-8") as f:
        return ast.parse(f.read(), filename=path)


def imports_of(path: str, root: str = ROOT) -> set:
    """moduleのimport先(repo直下の*.pyのみ)。関数内遅延import・importlib.import_module("literal")も拾う。"""
    out = set()
    for n in ast.walk(_parse(path)):
        if isinstance(n, ast.Import):
            for a in n.names:
                m = _local_module(a.name, root)
                if m:
                    out.add(m)
        elif isinstance(n, ast.ImportFrom):
            if n.module:
                m = _local_module(n.module, root)
                if m:
                    out.add(m)
                for a in n.names:  # from pkg import submodule
                    m2 = _local_module(a.name, root)
                    if m2:
                        out.add(m2)
        elif isinstance(n, ast.Call):
            f = n.func
            nm = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if nm in ("import_module", "__import__") and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                m = _local_module(n.args[0].value, root)
                if m:
                    out.add(m)
    return out


def reachable_modules(entrypoints=None, root: str = ROOT) -> dict:
    """entrypoint module -> 到達module集合 ではなく、{到達module: 最初に到達したentrypoint} を返す。"""
    eps = [e[:-3] for e in (entrypoints or ENTRYPOINTS) if os.path.exists(os.path.join(root, e))]
    seen, stack = {}, [(e, e) for e in eps]
    while stack:
        mod, via = stack.pop()
        if mod in seen:
            continue
        seen[mod] = via
        path = os.path.join(root, mod + ".py")
        if not os.path.exists(path):
            continue
        for dep in imports_of(path, root):
            if dep not in seen:
                stack.append((dep, via))
    return seen


def _callee_name(func) -> str:
    if isinstance(func, ast.Attribute):
        base = []
        cur = func
        while isinstance(cur, ast.Attribute):
            base.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            base.append(cur.id)
        return ".".join(reversed(base))
    return getattr(func, "id", "")


def asr_calls_in(path: str) -> list:
    """[(enclosing_function, callee_dotted_name, lineno)]。"""
    tree = _parse(path)
    out = []

    def visit(node, fn):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                visit(child, child.name if fn == "<module>" else f"{fn}.{child.name}")
                continue
            if isinstance(child, ast.Call):
                nm = _callee_name(child.func)
                if nm and CALLEE_RE.match(nm.split(".")[-1]):
                    out.append((fn, nm, child.lineno))
            visit(child, fn)

    visit(tree, "<module>")
    return out


def inventory(entrypoints=None, root: str = ROOT) -> dict:
    """{(module, function, callee): {"count": n, "lines": [...], "via": entrypoint}}"""
    inv = {}
    reach = reachable_modules(entrypoints, root)
    for mod in sorted(reach):
        path = os.path.join(root, mod + ".py")
        if not os.path.exists(path):
            continue
        for fn, nm, ln in asr_calls_in(path):
            e = inv.setdefault((mod, fn, nm), {"count": 0, "lines": [], "via": reach[mod]})
            e["count"] += 1
            e["lines"].append(ln)
    return inv


def _judgement_label(mod: str, fn: str) -> str:
    labels = []
    for j, (m, f) in JUDGEMENT_POINTS.items():
        fs = (f,) if isinstance(f, str) else f
        if m == mod and (f is None or fn.split(".")[0] in fs or fn in fs):
            labels.append(j)
    return ",".join(labels)


def _reason_for(mod: str, fn: str, nm: str) -> str:
    j = _judgement_label(mod, fn)
    if mod in ("er006_secondary_asr_01", "er007_ja_secondary_asr_01"):
        return "既存Cascade/SCG実装本体(委任_03/04でadapter化し内部をunified_judge委譲へ)。configは現状Production経路"
    if mod in ("er008_disfluency_qa_18", "er011_open121_repetition_qa_production_01"):
        return "Safety QA用の転写(disfluency/repetition)。内容一致の判定点ではない=統一judge対象外(最後にANDされる既存構造は不変)"
    if mod == "er013_family_c_production_runner_01":
        return "Family C(legacy)の診断用ASR(get_or_run_asr)。DESIGN J1-J11に未列挙。委任_04で採用判定に使われていないことを確認すること(未確認)"
    if mod == "er006_preprod_hardening_01_validation":
        return "EN検証ライブラリ内部の呼出(classify_asr_match/evaluate_attempt。既存Primary側P-chain)。adapter化の対象外・値ガード接続点"
    if mod in ("er006_asr_provider_routing_01",):
        return "ASR provider routing(Primary転写の取得実装。統一judgeはこの出力を受ける側)"
    if j:
        return f"判定点{j}: leaf内のPrimary転写+判定呼出(委任_03/04でunified_judge経由へ)"
    return "SNAPSHOT: 現行呼出(配線前)。委任_03/04で統一judge経由かadapter内部かを個別に確定する"


def build_allowlist(inv=None) -> dict:
    inv = inv if inv is not None else inventory()
    entries = []
    for (mod, fn, nm), v in sorted(inv.items()):
        entries.append({"module": mod, "function": fn, "callee": nm, "count": v["count"], "judgement_point": _judgement_label(mod, fn),
                        "reason": _reason_for(mod, fn, nm)})
    return {"phase": "pre_wiring", "managed_id": "ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01", "generated_by": "delegation_02b",
            "entrypoints": ENTRYPOINTS, "callee_pattern": CALLEE_RE.pattern, "entry_count": len(entries), "entries": entries}


def load_allowlist(path: str = ALLOWLIST_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def diff_against_allowlist(inv: dict, allow: dict) -> dict:
    want = {(e["module"], e["function"], e["callee"]): e["count"] for e in allow["entries"]}
    have = {k: v["count"] for k, v in inv.items()}
    return {
        "unlisted_new_calls": sorted(k for k in have if k not in want),
        "vanished": sorted(k for k in want if k not in have),
        "count_changed": sorted(k for k in have if k in want and have[k] != want[k]),
    }


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if "--regenerate" in argv:
        al = build_allowlist()
        with open(ALLOWLIST_PATH, "w", encoding="utf-8") as f:
            json.dump(al, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"allowlist written: {ALLOWLIST_PATH} ({al['entry_count']} entries)")
        return 0
    d = diff_against_allowlist(inventory(), load_allowlist())
    print(json.dumps(d, ensure_ascii=False, indent=2))
    return 0 if not any(d.values()) else 1


# ============================================================
# pytest
# ============================================================
def test_entrypoints_exist():
    missing = [e for e in ENTRYPOINTS if not os.path.exists(os.path.join(ROOT, e))]
    assert missing == [], f"entrypointが存在しない(監査対象の取りこぼし/改名): {missing}"


def test_reachable_set_contains_known_leaf_modules():
    reach = reachable_modules()
    for need in ("er003_v1_sing01_voice01_generate", "er003_v1_sing01_news_tail_fix", "er003_v1_repro01_main_generate",
                 "er006_secondary_asr_01", "er007_ja_secondary_asr_01"):
        assert need in reach, f"import graphで到達できない: {need}"


def test_allowlist_exists_and_every_entry_has_reason():
    al = load_allowlist()
    assert al["entries"], "allowlistが空"
    for e in al["entries"]:
        assert e["reason"].strip(), f"理由なしallowlist entry: {e}"
        assert e["count"] >= 1


def test_asr_call_inventory_matches_allowlist():
    al = load_allowlist()
    inv = inventory()
    d = diff_against_allowlist(inv, al)
    if al["phase"] == "pre_wiring":
        # 配線前: snapshotとの完全一致。未登録の新規ASR呼出(統一judgeを経由しない呼出点の増殖)も、意図しない消失もFAIL。
        assert d == {"unlisted_new_calls": [], "vanished": [], "count_changed": []}, d
    else:
        # post_wiring(委任_03/04で切替え): allowlistは「統一judge/adapter内部の呼出」のみ。それ以外のASR呼出が1件でもあればFAIL。
        assert d["unlisted_new_calls"] == [], d
        assert all(e["module"] in UNIFIED_MODULES or e.get("internal") for e in al["entries"]), "post_wiringではinternal理由のentryのみ許可"


def test_unified_judge_reachability_matches_phase():
    al = load_allowlist()
    reach = reachable_modules()
    if al["phase"] == "pre_wiring":
        assert "er078_asr_unified_judge_01" not in reach, "配線前のはずが統一judgeがProduction entrypointから到達している(未承認配線の疑い)"
    else:
        assert "er078_asr_unified_judge_01" in reach


def test_judgement_points_j1_to_j10_present_in_inventory():
    inv = inventory()
    mods = {m for (m, _f, _n) in inv}
    for j, (m, _fn) in JUDGEMENT_POINTS.items():
        assert m in mods, f"{j}: {m} にASR呼出が見つからない(DESIGN J1-J10の前提が崩れた/改名)"


def test_j11_inheritance_rejudge_path_is_in_inventory():
    # J11(追補§3-1): 引継ぎ・再利用経路 er019_family_x_validation_inheritance_01.rejudge_with_current_judge は保存転写に対し
    # classify_asr_matchを直接呼ぶ(API 0)。配線後はこの呼出も統一判定の入口(最終ANDゲート再適用)経由へ置換する(委任_04)。
    inv = inventory()
    assert ("er019_family_x_validation_inheritance_01", "rejudge_with_current_judge", "en_validator.classify_asr_match") in inv


def test_no_asr_call_in_new_er078_modules():
    for m in UNIFIED_MODULES:
        assert asr_calls_in(os.path.join(ROOT, m + ".py")) == [], m


if __name__ == "__main__":
    sys.exit(main())
