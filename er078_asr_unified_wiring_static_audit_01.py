# AUW 委任_02b: 統一ASR判定の配線 静的監査(import graph方式)。DESIGN_02_ADDENDUM_01 §3-2 / OF-AUW-04。
#
# 方式: Production entrypointからASTでimportを辿り(関数内の遅延importも含む)、到達したmodule内の
#       `transcribe | classify_asr_match | classify_ja_asr_match | evaluate_attempt*` の**呼出**を全数列挙し、
#       allowlist(er078_asr_unified_wiring_allowlist_01.json、理由付き)と突合する。手書きの呼出点一覧(DESIGN_01 §3.1)の網羅漏れを機械検出する。
#
# 段階(allowlistの "phase"):
#   pre_wiring  (本委任_02b時点): 現状の呼出一覧をsnapshot化したもの。testは「snapshotとの完全一致」(=未登録の新規ASR呼出が増えていない/
#                                 意図せず消えていない)を検査する。統一judgeはまだentrypointから到達しない。
#   post_wiring_en (委任_03: EN配線済み・JA未配線): ENのentrypoint(leaf)が統一judge(adapter=er006_secondary_asr_01経由)へ到達すること、
#                                 EN判定点でadapterを経由しない直接のclassify_asr_match/evaluate_attempt呼出が「明示の繰延リスト(A2減速=委任_05、J11=委任_04)」
#                                 以外に無いこと、JA経路(er007_ja_secondary_asr_01)が統一judgeへ未到達であることをassertする。allowlistの各entryは
#                                 `category`を持ち、未知categoryはFAIL。再生成: `--regenerate --phase post_wiring_en`。
#   post_wiring (委任_04: EN+JA+J11配線済み): 「統一judge/adapter経由以外のASR呼出0」をassertする。EN/JA両entrypointから統一judgeへ到達すること、
#                                 繰延カテゴリ(ja_unwired/j11_deferred/diagnostic_unconfirmed)のentryが0件であることをassertする。
#                                 [委任_05で締め] A2 6%減速後の再検証(apply_a2_slowdown_postprocess)は統一judge(EN adapter)経由へ置換済み。
#                                 category `a2_slowdown_pending_delegation_05` は **0件**(deferred 0・pending 0)。A2_PENDING_ENTRIES=[]。
#                                 apply_a2_slowdown_postprocess内の routing.transcribe は Primary転写の取得(primary_acquisition)、判定は
#                                 _post_slowdown_unified_judge -> evaluate_attempt_with_cascade_detail(en_adapter_entry)。
#                                 再生成: `--regenerate --phase post_wiring`。
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
PHASES = ("pre_wiring", "post_wiring_en", "post_wiring")

# post_wiring_en のentry category(委任_03)。繰延(deferred)カテゴリはpost_wiringでは0件でなければならない。
CAT_ADAPTER_INTERNAL = "adapter_internal"                  # EN adapter本体(er006_secondary_asr_01): Primary P-chainの呼出+統一judge呼出
CAT_LIBRARY_INTERNAL = "library_internal"                  # EN検証library(er006_preprod_hardening_01_validation)内部。adapter経由でのみ判定に使われる
CAT_EN_ADAPTER_ENTRY = "en_adapter_entry"                  # EN判定点(leaf)からadapterへの入口呼出(evaluate_attempt_with_cascade[_detail])
CAT_PRIMARY_ACQUISITION = "primary_acquisition"            # Primary ASR転写の取得(judgeの入力側。判定ではない)
CAT_SAFETY_QA = "safety_qa"                                # disfluency/repetition用の転写(内容判定ではない)
CAT_JA_UNWIRED = "ja_unwired_delegation_04"                # (post_wiring_enのみ)JA(委任_04で配線)
CAT_J11_DEFERRED = "j11_deferred_delegation_04"            # (post_wiring_enのみ)引継ぎ・再利用経路の再判定(委任_04)
CAT_A2_DEFERRED = "a2_slowdown_pending_delegation_05"      # (廃止: 委任_05でA2減速後を統一judge化し0件。ALLOWED_CATEGORIESに含めない=残存すればFAIL)
CAT_DIAGNOSTIC_UNCONFIRMED = "diagnostic_unconfirmed"      # (post_wiring_enのみ)Family C診断ASR(判定に使われているか未確認)
# 委任_04で追加(post_wiringの正規category)
CAT_JA_ADAPTER_ENTRY = "ja_adapter_entry"                  # JA判定点(leaf)からJA adapter(er007_ja_secondary_asr_01)への入口呼出=統一judge経由
CAT_J11_UNIFIED_ENTRY = "j11_unified_judge_entry"          # J11: 引継ぎ再判定。内部でunified_judgeを呼ぶ(保存転写のPrimary再導出+最終ANDゲート、API 0)
CAT_DIAGNOSTIC_CONFIRMED = "diagnostic_not_judgement"      # Family C診断ASR: 結果はaudit/consistency行に記録されるだけで採用判定(verified/Gate)に使われない(確認済み)
# 委任_04で未配線のため繰延のまま許容するのはA2のみ(post_wiring)。それ以外の繰延は0でなければならない。
DEFERRED_CATEGORIES = (CAT_JA_UNWIRED, CAT_J11_DEFERRED, CAT_DIAGNOSTIC_UNCONFIRMED)
PENDING_DELEGATION_05_CATEGORIES = ()   # 委任_05で空(A2減速後を統一judge化)。
ALLOWED_CATEGORIES = (CAT_ADAPTER_INTERNAL, CAT_LIBRARY_INTERNAL, CAT_EN_ADAPTER_ENTRY, CAT_PRIMARY_ACQUISITION, CAT_SAFETY_QA,
                      CAT_JA_ADAPTER_ENTRY, CAT_J11_UNIFIED_ENTRY, CAT_DIAGNOSTIC_CONFIRMED) + DEFERRED_CATEGORIES + PENDING_DELEGATION_05_CATEGORIES
# post_wiringの委任_05繰延(明示の既知集合)。委任_05でA2を統一judge化したため空。増えたらFAIL。
A2_PENDING_ENTRIES: list = []
JA_FUNCTIONS = {("er003_v1_sing01_voice01_generate", "generate_charon_japanese"),
                ("er003_v1_n3_01_tts_generate", "generate_a2_japanese_with_fallback")}
EN_LEAF_MODULES = ("er003_v1_sing01_voice01_generate", "er003_v1_sing01_news_tail_fix", "er003_v1_crosslevel_audio_02_common",
                   "er012_b_family_voices_production_01", "er003_v1_repro01_main_generate", "er003_v1_sing01_point_headings_aoede")

# 判定点(DESIGN_01 §3.1 J1〜J11)とmoduleの対応。J11は引継ぎ・再利用経路(追補§3-1)。
JUDGEMENT_POINTS = {
    "J1": ("er003_v1_sing01_voice01_generate", "generate_charon_english"),
    "J2": ("er003_v1_sing01_news_tail_fix", "generate_news_narration_wide_margin"),
    "J3": ("er003_v1_crosslevel_audio_02_common", "_run_a2_minimal_fallback_attempt"),
    "J4": ("er012_b_family_voices_production_01", "generate_voice_body_wide_margin"),
    "J5": ("er003_v1_repro01_main_generate", "generate_narration_snippet_verified_strict"),
    "J6": ("er003_v1_sing01_point_headings_aoede", None),
    "J7": ("er003_v1_n3_01_tts_generate", ("apply_a2_slowdown_postprocess", "_post_slowdown_unified_judge")),
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


def category_for(mod: str, fn: str, nm: str, phase: str = "post_wiring") -> tuple:
    """(category, reason)。phase=post_wiring_en(委任_03時点: JA/J11/Family Cは繰延)かpost_wiring(委任_04: JA/J11配線済み)。"""
    last = nm.split(".")[-1]
    top = fn.split(".")[0]
    en_only = (phase == "post_wiring_en")
    if phase == "post_wiring":
        if mod == "er007_ja_secondary_asr_01":
            return CAT_ADAPTER_INTERNAL, "JA統一judge adapter本体(AUW 委任_04): Primary(classify_ja_asr_match)とSecondary許容集合判定。判定は全てunified_judge経由"
        if mod == "er019_family_x_validation_inheritance_01":
            return CAT_J11_UNIFIED_ENTRY, "J11 引継ぎ・再利用の再判定(AUW 委任_04): 保存転写のPrimary再導出後にunified_judge(最終ANDゲート)を通す。API 0・Secondary新規呼出なし"
        if mod == "er013_family_c_production_runner_01":
            return CAT_DIAGNOSTIC_CONFIRMED, "Family C(legacy)の診断用ASR(get_or_run_asr)。確認済み(委任_04): 結果はaudit asr_text/comment_consistency.jsonの記録のみで採用判定に使われない"
        if last == "evaluate_attempt_ja_with_cascade":
            return CAT_JA_ADAPTER_ENTRY, "JA判定点(leaf)からJA adapter(er007_ja_secondary_asr_01)への入口呼出=統一judge経由"
    if mod == "er006_secondary_asr_01":
        return CAT_ADAPTER_INTERNAL, "EN統一judge adapter本体(AUW 委任_03): Primary P-chain([val.evaluate_attempt/classify_asr_match])とjudge呼出。判定は全てunified_judge経由"
    if mod == "er006_preprod_hardening_01_validation":
        return CAT_LIBRARY_INTERNAL, "EN検証library内部の呼出(Primary P-chain本体)。adapter(evaluate_attempt_with_cascade_detail)経由でのみ判定に使われる"
    if mod in ("er008_disfluency_qa_18", "er011_open121_repetition_qa_production_01"):
        return CAT_SAFETY_QA, "Safety QA用の転写(disfluency/repetition)。内容一致の判定点ではない(最後にANDされる既存構造は不変)"
    if en_only and mod == "er013_family_c_production_runner_01":
        return CAT_DIAGNOSTIC_UNCONFIRMED, "Family C(legacy)の診断用ASR(get_or_run_asr)。判定に使われているか未確認(委任_04で確認)"
    if en_only and mod == "er019_family_x_validation_inheritance_01":
        return CAT_J11_DEFERRED, "J11 引継ぎ・再利用の再判定(保存転写に対するAPI 0再判定)。統一判定の入口への置換は委任_04"
    if en_only and (mod == "er007_ja_secondary_asr_01" or nm.startswith(("ja_secondary.", "javal."))):
        return CAT_JA_UNWIRED, "JA判定(SCG/JA cascade)。統一judgeへの配線は委任_04(本委任では未配線)"
    if en_only and (mod, top) in JA_FUNCTIONS and last != "transcribe":
        return CAT_JA_UNWIRED, "JA leafの判定呼出。委任_04"
    if en_only and (mod, top) in JA_FUNCTIONS:
        return CAT_JA_UNWIRED, "JA leafのPrimary転写取得(JA判定とセット)。委任_04"
    if mod == "er003_v1_n3_01_tts_generate" and top == "apply_a2_slowdown_postprocess" and last == "transcribe":
        return CAT_PRIMARY_ACQUISITION, "A2 6%減速後wavのPrimary ASR転写の取得(AUW 委任_05)。判定は_post_slowdown_unified_judge経由(統一judge)"
    if last in ("evaluate_attempt_with_cascade", "evaluate_attempt_with_cascade_detail"):
        return CAT_EN_ADAPTER_ENTRY, "EN判定点(leaf)からadapter(er006_secondary_asr_01)への入口呼出=統一judge経由"
    if last == "transcribe":
        return CAT_PRIMARY_ACQUISITION, "Primary ASR転写の取得(統一judgeの入力側。EN leaf/EN+JA共用関数)"
    return "UNCATEGORIZED", "未分類(post_wiring_en/post_wiringはFAIL)"


def build_allowlist(inv=None, phase: str = "pre_wiring") -> dict:
    assert phase in PHASES, phase
    inv = inv if inv is not None else inventory()
    entries = []
    for (mod, fn, nm), v in sorted(inv.items()):
        e = {"module": mod, "function": fn, "callee": nm, "count": v["count"], "judgement_point": _judgement_label(mod, fn),
             "reason": _reason_for(mod, fn, nm)}
        if phase != "pre_wiring":
            e["category"], e["reason"] = category_for(mod, fn, nm, phase)
        entries.append(e)
    return {"phase": phase, "managed_id": "ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01",
            "generated_by": {"pre_wiring": "delegation_02b", "post_wiring_en": "delegation_03", "post_wiring": "delegation_05"}[phase],
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
        phase = argv[argv.index("--phase") + 1] if "--phase" in argv else "pre_wiring"
        al = build_allowlist(phase=phase)
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
    assert al["phase"] in PHASES, al["phase"]
    # 全phase共通: snapshotとの完全一致。未登録の新規ASR呼出(統一judgeを経由しない呼出点の増殖)も、意図しない消失もFAIL。
    assert d == {"unlisted_new_calls": [], "vanished": [], "count_changed": []}, d
    if al["phase"] == "post_wiring":
        # 繰延カテゴリ(JA未配線/J11/診断未確認)は0件でなければならない。
        left = [e for e in al["entries"] if e.get("category") in DEFERRED_CATEGORIES]
        assert left == [], f"post_wiringに繰延カテゴリが残っている: {left}"
        # 委任_05: A2減速後の再検証も統一judge化済み=pending(委任_05繰延)も0件。
        pend = [e for e in al["entries"] if e.get("category") in PENDING_DELEGATION_05_CATEGORIES + (CAT_A2_DEFERRED,)]
        assert pend == [] and A2_PENDING_ENTRIES == [], f"post_wiringに委任_05 pendingが残っている: {pend}"


def test_unified_judge_reachability_matches_phase():
    al = load_allowlist()
    reach = reachable_modules()
    if al["phase"] == "pre_wiring":
        assert "er078_asr_unified_judge_01" not in reach, "配線前のはずが統一judgeがProduction entrypointから到達している(未承認配線の疑い)"
    else:
        assert "er078_asr_unified_judge_01" in reach


def _closure(start: str) -> set:
    seen, st = set(), [start]
    while st:
        m = st.pop()
        if m in seen:
            continue
        seen.add(m)
        path = os.path.join(ROOT, m + ".py")
        if os.path.exists(path):
            st.extend(d for d in imports_of(path) if d not in seen)
    return seen


def _en_phase_only(fn):
    """pre_wiringではskip(何もしない)。post_wiring_en以降のみ検査する。"""
    def wrapper(*a, **k):
        if load_allowlist()["phase"] == "pre_wiring":
            return None
        return fn(*a, **k)
    wrapper.__name__ = fn.__name__
    return wrapper


@_en_phase_only
def test_post_wiring_every_entry_has_known_category():
    al = load_allowlist()
    bad = [e for e in al["entries"] if e.get("category") not in ALLOWED_CATEGORIES]
    assert bad == [], f"未知/未分類category(新しいASR呼出点が増えた/分類漏れ): {bad}"
    # 再導出したcategoryとallowlistが一致(allowlistの手編集で分類を偽らない)
    for e in al["entries"]:
        assert e["category"] == category_for(e["module"], e["function"], e["callee"], al["phase"])[0], e


@_en_phase_only
def test_post_wiring_every_en_leaf_reaches_unified_judge_through_adapter():
    for m in EN_LEAF_MODULES:
        assert "er078_asr_unified_judge_01" in _closure(m), f"EN leaf {m} が統一judgeへ到達しない"
        assert "er006_secondary_asr_01" in imports_of(os.path.join(ROOT, m + ".py")), f"{m} がadapter(er006_secondary_asr_01)をimportしない"
    assert "er078_asr_unified_judge_01" in imports_of(os.path.join(ROOT, "er006_secondary_asr_01.py"))


@_en_phase_only
def test_post_wiring_no_judgement_bypasses_adapter_except_explicit_pending():
    """EN leaf(J1-J6)の内容判定はadapter(evaluate_attempt_with_cascade[_detail])経由のみ。judge/adapter以外の直接
    classify_asr_match/evaluate_attempt/classify_ja_asr_match呼出は、adapter/library内部・J11(unified経由)・[post_wiring_enのみ]繰延だけ。"""
    al = load_allowlist()
    direct = [e for e in al["entries"]
              if e["callee"].split(".")[-1] in ("classify_asr_match", "evaluate_attempt", "classify_ja_asr_match")]
    ok_cats = {CAT_ADAPTER_INTERNAL, CAT_LIBRARY_INTERNAL, CAT_J11_UNIFIED_ENTRY}   # 委任_05: A2繰延は無し
    if al["phase"] == "post_wiring_en":
        ok_cats |= {CAT_JA_UNWIRED, CAT_J11_DEFERRED}
    for e in direct:
        assert e["category"] in ok_cats, f"判定点がadapterを経由せず直接判定している: {e}"
    pending = sorted((e["module"], e["function"]) for e in al["entries"] if e["category"] in PENDING_DELEGATION_05_CATEGORIES + (CAT_J11_DEFERRED,))
    expect = sorted(A2_PENDING_ENTRIES + ([("er019_family_x_validation_inheritance_01", "rejudge_with_current_judge")]
                                           if al["phase"] == "post_wiring_en" else []))
    assert pending == expect, pending
    # EN leaf J1-J6は全てadapter入口を持つ
    have = {(e["module"], e["callee"].split(".")[-1]) for e in al["entries"]}
    for j in ("J1", "J2", "J3", "J4", "J5", "J6"):
        m, _f = JUDGEMENT_POINTS[j]
        assert any(mm == m and cal.startswith("evaluate_attempt_with_cascade") for (mm, cal) in have), f"{j} {m} にadapter入口が無い"


@_en_phase_only
def test_post_wiring_ja_phase_dependent_wiring():
    al = load_allowlist()
    if al["phase"] == "post_wiring_en":
        for m in ("er007_ja_secondary_asr_01", "er007_ja_asr_validator_01"):
            c = _closure(m)
            assert not (c & UNIFIED_MODULES), f"JA経路 {m} が統一judge系へ到達している(委任_04前の未承認配線): {c & UNIFIED_MODULES}"
            assert "er006_secondary_asr_01" not in c
        assert [e for e in al["entries"] if e["category"] == CAT_JA_UNWIRED], "JA未配線entryが無い(分類漏れ)"
        return
    # post_wiring: JA adapterが統一judgeをimportし、JA leaf全てがJA adapter入口を持つ
    assert "er078_asr_unified_judge_01" in imports_of(os.path.join(ROOT, "er007_ja_secondary_asr_01.py"))
    assert "er078_asr_value_guard_01" in imports_of(os.path.join(ROOT, "er007_ja_secondary_asr_01.py"))
    for m in ("er003_v1_sing01_voice01_generate", "er003_v1_n3_01_tts_generate", "er003_v1_repro01_main_generate"):
        assert "er007_ja_secondary_asr_01" in imports_of(os.path.join(ROOT, m + ".py")), m
        assert "er078_asr_unified_judge_01" in _closure(m), m
    have = {(e["module"], e["function"].split(".")[0], e["callee"].split(".")[-1]) for e in al["entries"]}
    for j in ("J5", "J8", "J9", "J10"):
        m, f = JUDGEMENT_POINTS[j]
        assert any(mm == m and cal == "evaluate_attempt_ja_with_cascade" for (mm, _ff, cal) in have), f"{j} {m} にJA adapter入口が無い"
    # JA判定の直接呼出(classify_ja_asr_matchなど)はJA adapter内部(er007_ja_secondary_asr_01)のみ
    for e in al["entries"]:
        if e["callee"].split(".")[-1] in ("classify_ja_asr_match", "evaluate_attempt_ja_with_cascade_detail"):
            assert e["module"] == "er007_ja_secondary_asr_01" and e["category"] == CAT_ADAPTER_INTERNAL, e
    assert [e for e in al["entries"] if e["category"] in DEFERRED_CATEGORIES] == []


@_en_phase_only
def test_post_wiring_both_entrypoint_families_reach_unified_judge():
    """EN/JA両方のProduction entrypointから、統一judge(adapter経由)へ到達できる。"""
    reach = reachable_modules()
    for need in ("er078_asr_unified_judge_01", "er078_asr_value_guard_01", "er078_pass_with_warning_registry_01",
                 "er006_secondary_asr_01", "er007_ja_secondary_asr_01", "er019_family_x_validation_inheritance_01"):
        assert need in reach, f"Production entrypointから到達しない: {need}"
    for adapter in ("er006_secondary_asr_01", "er007_ja_secondary_asr_01"):
        assert "er078_asr_unified_judge_01" in imports_of(os.path.join(ROOT, adapter + ".py")), adapter


@_en_phase_only
def test_post_wiring_j11_calls_unified_judge_and_never_calls_asr_api():
    """J11(rejudge_with_current_judge)は統一judge(unified_judge)を呼ぶ。Primary再導出はclassify_asr_match(保存転写・API 0)のみで、
    transcribe/Azure(Secondary)関数は呼ばない。"""
    tree = _parse(os.path.join(ROOT, "er019_family_x_validation_inheritance_01.py"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "rejudge_with_current_judge")
    names = [_callee_name(c.func) for c in ast.walk(fn) if isinstance(c, ast.Call)]
    assert any(n.endswith("unified_judge") for n in names), names
    for forbidden in ("transcribe", "get_full_text_via_azure_stt_with_phrase_list", "_azure_stt_strict",
                      "get_full_text_via_azure_stt_continuous"):
        assert not any(n.endswith(forbidden) for n in names), (forbidden, names)


@_en_phase_only
def test_post_wiring_family_c_asr_is_diagnostic_only():
    """Family C(legacy)のget_or_run_asrは採用判定に使われない: 判定系関数(evaluate_attempt*/classify*)を一切呼ばず、
    戻り値はaudit asr_textと診断consistency行(match)にのみ入る。"""
    path = os.path.join(ROOT, "er013_family_c_production_runner_01.py")
    src = open(path, encoding="utf-8").read()
    assert not re.search(r"\b(evaluate_attempt\w*|classify_asr_match|classify_ja_asr_match|unified_judge)\b", src)
    tree = _parse(path)
    # asr_verified / status(OK/STOPPED)をASR転写で決める代入が無い(asr_textはaudit_segments[...]["asr_text"]とconsistency行にのみ入る)
    assert "asr_verified" not in src


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
