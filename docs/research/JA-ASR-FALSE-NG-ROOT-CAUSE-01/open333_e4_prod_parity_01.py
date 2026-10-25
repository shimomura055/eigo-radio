# OPEN-333 E4 Production適用の proto↔Production 一致検証(委任_14。E3版 eval_open333_prod_parity_01.py のコピーを凍結流用せず新規化)。API 0・費用0円(socket guard)。
# 4通りを同一入力で計算し、判定(classify結果+正式adapterのPrimary段state/reason/label+Secondary受理sim)を全件比較する:
#   head  = git HEAD のtop-level *.py スナップショット(適用前Production。E3は適用済み、er011にE4 flag CANDIDATE_E_CASCADE_DIFF_RETURNが無い)
#   off   = 作業ツリーのProduction + E4 rollback定数をFalse(E3は両方ON)        -> headと完全一致であるべき(OFF=HEAD)
#   on    = 作業ツリーのProduction(既定ON)                        -> protoと完全一致であるべき(M-4)
#   proto = head スナップショット + proto_open333_fix_06 の E4       -> 基準
# 入力 = eval_open333_api0_04.py が保存した全行(既存771+未知493+合成負例91)+M-3 sweep+旧sweep+E4行+Secondary対(保存+全Primary転写)。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open333_e4_prod_parity_01.py
import hashlib, io, json, os, subprocess, sys, tarfile, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "open333_e4_prod_parity_01.out.json")


def snapshot_head() -> str:
    rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, check=True, text=True).stdout.strip()
    d = os.path.join(tempfile.gettempdir(), "open333_e4_head_snap_" + rev[:10])
    if not os.path.exists(os.path.join(d, "er011_ja_asr_variant_layer_01.py")):
        os.makedirs(d, exist_ok=True)
        data = subprocess.run(["git", "archive", rev, ":(glob)*.py", ":(glob)*.json", ":(glob)*.txt"], cwd=REPO, capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(data)) as t:
            t.extractall(d)
    return d


if len(sys.argv) < 3 or sys.argv[1] != "--emit":
    # ---------------- driver ----------------
    snap = snapshot_head()
    results = {}
    for name, cwd in (("head", snap), ("proto", snap), ("off", REPO), ("on", REPO)):
        outp = os.path.join(tempfile.gettempdir(), f"open333_e4_parity_{name}.json")
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PARITY_REPO=REPO)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--emit", name, outp], cwd=cwd, env=env)
        if r.returncode != 0:
            sys.exit(f"emit {name} failed rc={r.returncode}")
        results[name] = json.load(open(outp, encoding="utf8"))
    items = sorted(results["head"].keys())
    assert all(sorted(v.keys()) == items for v in results.values())
    cmp = {}
    E4_REASON = "<E4 cascade reason>"

    def norm(v, strip_new):
        # on vs proto: protoは説明文(reason)に『(proto E4)』を付ける自由文のみが異なる。判定キーは全て比較する。新field名はprotoに無いので除外。
        if strip_new and isinstance(v, dict):
            v = dict(v)
            if "jkeys" in v:
                v["jkeys"] = [x for x in v["jkeys"] if x != "candidate_e_cascade_return"]
            if isinstance(v.get("reason"), str) and ("(proto E4)Candidate E" in v["reason"] or "(JA ASR Variant Layer/Candidate E)残差分は読みで説明できたが" in v["reason"]):
                v["reason"] = E4_REASON
        return v

    def brief(a, b):
        return {k: [a.get(k), b.get(k)] for k in set(a) | set(b) if a.get(k) != b.get(k) and k != "jkeys"}
    for a, b in (("off", "head"), ("on", "proto")):
        diffs = [k for k in items if norm(results[a][k], a == "on") != norm(results[b][k], a == "on")]
        cmp[f"{a}_vs_{b}"] = {"n": len(items), "diff": len(diffs), "examples": [(k, brief(norm(results[a][k], a == "on"), norm(results[b][k], a == "on"))) for k in diffs[:5]]}
    on_vs_head = [k for k in items if results["on"][k] != results["head"][k]]
    cmp["on_vs_head_changed"] = len(on_vs_head)
    cmp["on_vs_head_direction"] = {"PASS->nonPASS": len([k for k in on_vs_head if results["head"][k].get("pass") and not results["on"][k].get("pass")]),
                                   "other": len([k for k in on_vs_head if not (results["head"][k].get("pass") and not results["on"][k].get("pass"))])}
    cmp["on_vs_head_other_examples"] = [(k, brief(results["head"][k], results["on"][k])) for k in on_vs_head
                                        if not (results["head"][k].get("pass") and not results["on"][k].get("pass"))][:6]
    cmp["secondary_acceptance_changed(acc/orth, on vs head)"] = len([k for k in on_vs_head if k.startswith("S|") and (results["head"][k]["acc"] != results["on"][k]["acc"] or results["head"][k]["orth"] != results["on"][k]["orth"])])
    cmp["on_vs_head_new_field_rows"] = len([k for k in items if "candidate_e_cascade_return" in results["on"][k].get("jkeys", [])])
    cmp["head_or_off_new_field_rows"] = len([k for k in items if "candidate_e_cascade_return" in results["head"][k].get("jkeys", []) or "candidate_e_cascade_return" in results["off"][k].get("jkeys", [])])
    cmp["key_set_compared_rows(off==head)"] = len([k for k in items if "jkeys" in results["head"][k]])
    # 変化の方向: on がheadより広がっていないこと(headで不合格→onで合格 = 0)
    widen = [k for k in on_vs_head if (not results["head"][k].get("pass", True)) and results["on"][k].get("pass", False)]
    cmp["on_vs_head_widened(NG->PASS)"] = len(widen)
    print(json.dumps(cmp, ensure_ascii=False, indent=1))
    json.dump({"cmp": cmp, "keys": len(items)}, open(OUT, "w", encoding="utf8"), ensure_ascii=False, indent=1, sort_keys=True)
    print("out sha256:", hashlib.sha256(open(OUT, "rb").read()).hexdigest())
    sys.exit(0 if cmp["off_vs_head"]["diff"] == 0 and cmp["on_vs_proto"]["diff"] == 0 and not widen and cmp["secondary_acceptance_changed(acc/orth, on vs head)"] == 0 and cmp["head_or_off_new_field_rows"] == 0 else 1)

# ---------------- emitter (cwd = スナップショットまたは作業ツリー) ----------------
mode, outp = sys.argv[2], sys.argv[3]
repo = os.environ["PARITY_REPO"]
D = os.path.join(repo, "docs", "research", "JA-ASR-FALSE-NG-ROOT-CAUSE-01")
sys.path.insert(0, ".")
sys.path.insert(1, D)
import eval_common_02 as E
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL
import er007_ja_secondary_asr_01 as sec

javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False
cwd_abs = os.path.abspath(".").lower()
if mode in ("head", "proto"):
    assert os.path.abspath(".").lower() != os.path.abspath(repo).lower(), "head/proto must run on the HEAD snapshot"
    assert hasattr(VL, "CANDIDATE_E_FULL_DIFF_CHECK") and not hasattr(VL, "CANDIDATE_E_CASCADE_DIFF_RETURN"), "HEAD snapshot must contain E3 and predate E4"
else:
    assert os.path.abspath(".").lower() == os.path.abspath(repo).lower()
    assert hasattr(VL, "CANDIDATE_E_CASCADE_DIFF_RETURN")
    assert VL.CANDIDATE_E_FULL_DIFF_CHECK is True and VL.CANDIDATE_E_VALUE_GUARD_CHECK is True
    if mode == "off":
        VL.CANDIDATE_E_CASCADE_DIFF_RETURN = False
    else:
        assert VL.CANDIDATE_E_CASCADE_DIFF_RETURN is True
if mode == "proto":
    import proto_open333_fix_06 as P6
    ctx = P6.apply_in_process("E4")
else:
    import contextlib
    ctx = contextlib.nullcontext()

ev = json.load(open(os.path.join(D, "open333_api0_eval_04.out.json"), encoding="utf8"))
bl = json.load(open(os.path.join(D, "eval_b_light_api0_02.out.json"), encoding="utf8"))
pairs = {}
for r in ev["rows"]:
    pairs[("row", r["canon"], r["asr"])] = 1
for x in ev["sweep"]:
    pairs[("sweep", x["canon"], x["asr"])] = 1
for x in ev["old_sweep"]:
    pairs[("old", x["canon"], x["asr"])] = 1
for x in ev["e4"]:
    pairs[("e4", x["canon"], x["asr"])] = 1
e4ev = json.load(open(os.path.join(D, "open333_e4_eval_01.out.json"), encoding="utf8"))
for k in ("real", "sweep", "old_sweep", "e4"):
    for x in e4ev[k]:
        pairs[("e4ev_" + k, x["canon"], x["asr"])] = 1
sec_pairs = []
for k in ("moon", "n3", "hist"):
    for x in bl[k]:
        if x.get("secondary") and x.get("canon"):
            sec_pairs.append((x["canon"], x["secondary"]))
for s in bl["synthetic_negative"]:
    if s.get("secondary"):
        sec_pairs.append((s["canon"], s["secondary"]))
sec_pairs += [(r["canon"], r["asr"]) for r in ev["rows"] if r["asr"]]
sec_pairs = sorted(set(sec_pairs))

E.api0_guard_on()
out = {}
PASSING = E.uj.PASSING_STATES
with ctx:
    for (kind, c, a) in sorted(pairs):
        cl = javal.classify_ja_asr_match(c, a, allow_reading_resolver=False)
        st = E.primary_stage(c, a, False)
        _o = sec._azure_stt_strict
        sec._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (None, "api0_stub_no_call")
        try:
            _r = sec.evaluate_attempt_ja_with_cascade_detail(c, a, E.dummy_wav(), cascade_enabled=True, attempt_ctx={"max_len": 400})
        finally:
            sec._azure_stt_strict = _o
        _j = _r["asr_judgement"]
        out[f"P|{kind}|{c}|{a}"] = {"jkeys": sorted(_j.keys()), "jstate": _j.get("state"), "jreason": str(_j.get("reason_code")), "jlabel": (_j.get("primary") or {}).get("label"), "cls": cl.classification, "should_pass": cl.should_pass, "reason": cl.reason, "state": st["state"], "sreason": str(st["reason"]), "label": st["label"],
                                    "pass": st["state"] in PASSING}
    for (c, s) in sec_pairs:
        c1 = javal.classify_ja_asr_match(c, s, allow_reading_resolver=False)
        c2 = sec._apply_variant_layer_voicing_upgrade(c, s, c1)
        out[f"S|{c}|{s}"] = {"c1": c1.classification, "c2": c2.classification, "acc": c1.classification in sec.SCG_PASS_CLASSIFICATIONS,
                             "orth": bool(sec._orthographic_reading_confirmed(c2)), "reason": c1.reason, "pass": c1.classification in sec.SCG_PASS_CLASSIFICATIONS}
E.api0_guard_off()
json.dump(out, open(outp, "w", encoding="utf8"), ensure_ascii=False, sort_keys=True)
print(f"emit {mode}: {len(out)} keys")
