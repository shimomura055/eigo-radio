# ============================================================
# er093_pnmh_trial_01_core.py (PNMH Trial 委任_04: Trial専用・Production無変更)
# 計画v3の判定層L1(`multiword_span_equivalent_v3`: ストレス無視/V8/G5/全語+entity_like代表発音限定)を、
# val.protected_check のソースをメモリ上でpatchして差し込む(ファイル無編集、Production経路にimportされない)。
# `judge(c, a, mode)`: mode="current"=現行Validator判定(層B) / "v3"=entity_like引数ありの提案判定(層C)
#                      / "v3flat"=entity_like無し(TRIAL_CASES_01.json/unit testと同じ配線)
# ============================================================
from __future__ import annotations
import inspect, os, sys, json
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT); sys.path.insert(0, ROOT)
PLAN = os.path.join(ROOT, "docs", "research", "PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01")
sys.path.insert(0, PLAN)
import proto_multiword_span_01 as P          # multiword_span_equivalent_v3 を使う(import時にv1 patchが入るので下で上書き)
val = P.val
import er006_secondary_asr_01 as sec
import er021_en_asr_semantic_equivalence_production_01 as se
se.append_telemetry_log = lambda *a, **k: None   # telemetry副作用を抑止

MODE = {"m": "current"}
_src = inspect.getsource(val.protected_check.__wrapped__) if hasattr(val.protected_check, "__wrapped__") else None
# P.install_proto() が既に val.protected_check を差替え済み(v1 patch、PROTO_MULTIWORD(canon_span, asr_span))。
# ここでは元ソースから再構築し、entity_likeを渡す版へ上書きする。
import importlib
importlib.reload(val)                              # patch前の元関数へ戻す
_orig = inspect.getsource(val.protected_check)
_OLD = "                    homophone_candidate = bool(result_h)\n"
assert _OLD in _orig
_NEW = _OLD + ("                if not homophone_candidate and PROTO_MULTIWORD(canon_span, asr_span, entity_like):\n"
               "                    homophone_candidate = True\n")
def _mw(c, a, entity_like=False):
    m = MODE["m"]
    if m == "current": return False
    if m == "v3flat": return P.multiword_span_equivalent_v3(c, a)
    return P.multiword_span_equivalent_v3(c, a, entity_like)
val.__dict__["PROTO_MULTIWORD"] = _mw
exec(compile(_orig.replace(_OLD, _NEW), "<pnmh_trial_protected_check>", "exec"), val.__dict__)
# 注: 以後 val.classify_asr_match は patch版protected_checkを呼ぶ。MODE=currentでは_mwが常にFalse=現行と同一挙動(O1 (2)でバイト一致を検証)。

def judge(c, a, mode="current"):
    """戻り値: (classification, final: 'PASS'|'PASS:<label>'|'NOT_PASS', result)。final は should_pass or sec._step_alternate_pass。"""
    MODE["m"] = mode
    try:
        r = val.classify_asr_match(c, a)
        final = "PASS" if r.should_pass else None
        if final is None and (sec.is_entity_like_mismatch(r) or sec.is_homophone_candidate_mismatch(r)):
            lab = sec._step_alternate_pass(r)
            if lab: final = "PASS:" + lab
        return r.classification, (final or "NOT_PASS"), r
    finally:
        MODE["m"] = "current"

def is_pass(fin): return fin.startswith("PASS")
