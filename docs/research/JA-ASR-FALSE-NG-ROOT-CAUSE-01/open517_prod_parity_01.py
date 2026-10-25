# OPEN-517 Production(HEAD) 再現一致確認 (JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_09)。API 0(socket guard)。保存済み転写のみ。
# 目的: 委任_08が『pin 89b630bd1 の Production + proto v4 apply_in_process』で作った base+F1F2(F12)列と、07A commit後のHEAD Production関数(既定値=523/524 ON、および523/524 OFF)が
#       同じ入力集合で完全一致するかを確認する。入力=月題12・N-3 30 clip・実履歴P-S対・Melos・合成負例(M3/FB/V1)・attempt_pool 562・unknown_pool 493 の Primary 転写。
# 実行: リポジトリrootで PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_prod_parity_01.py
#   -> 3モード(pin+proto v4 / HEAD既定 / HEAD 523・524 OFF)を子processで実行し比較。出力 open517_prod_parity_01.out.json。決定的。
import hashlib, io, json, os, subprocess, sys, tarfile, tempfile

PIN = "89b630bd1086a638b2fec1f00d69bfae8722b665"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MODE = os.environ.get("PARITY_MODE")


def snapshot():
    d = os.path.join(tempfile.gettempdir(), "blight_snap_" + PIN[:10])
    if not os.path.exists(os.path.join(d, "er007_ja_secondary_asr_01.py")):
        os.makedirs(d, exist_ok=True)
        data = subprocess.run(["git", "archive", PIN, ":(glob)*.py", ":(glob)*.json", ":(glob)*.txt"], cwd=REPO, capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(data)) as t:
            t.extractall(d)
    return d


def inputs():
    o = json.load(open(os.path.join(HERE, "eval_b_light_api0_02.out.json"), encoding="utf8"))
    items = []
    for g in ("moon", "n3", "hist"):
        for i, r in enumerate(o[g]):
            items.append((f"{g}:{i}", r["canon"], r["primary"], r["F12"]))
    m = o["melos"]
    items.append(("melos:0", m["canon"], m["primary"], m["F12"]))
    for i, r in enumerate(o["synthetic_negative"]):
        items.append((f"syn:{i}", r["canon"], r["primary"], {"pass": r["F12_pass"], "secondary": r["secondary"]}))
    att = json.load(open(os.path.join(HERE, "attempt_pool_01.json"), encoding="utf8"))
    for i, x in enumerate(att):
        items.append((f"att:{i}", x["canon"], x["primary"], None))
    unk = json.load(open(os.path.join(HERE, "unknown_pool_02.json"), encoding="utf8"))
    for i, x in enumerate(unk):
        if x.get("canon") and x.get("asr"):
            items.append((f"unk:{i}", x["canon"], x["asr"], None))
    return items


if MODE is None:
    snap = snapshot()
    outs = {}
    for name, cwd, mode, extra in (("pin_v4", snap, "pin", {}), ("head_default", REPO, "head", {}), ("head_off", REPO, "head", {"PARITY_OFF": "1"})):
        tmp = os.path.join(tempfile.gettempdir(), f"parity_{name}.json")
        env = dict(os.environ, PARITY_MODE=mode, PARITY_OUT=tmp, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", **extra)
        r = subprocess.run([sys.executable, os.path.abspath(__file__)], cwd=cwd, env=env)
        if r.returncode:
            sys.exit(r.returncode)
        outs[name] = json.load(open(tmp, encoding="utf8"))
    items = inputs()
    res = {"pin": PIN, "n_items": len(items)}
    ref = outs["pin_v4"]["sig"]
    for name in ("head_default", "head_off"):
        sig = outs[name]["sig"]
        diffs = [k for k in ref if ref[k] != sig[k]]
        res[name] = {"diff_count": len(diffs), "diffs": [{"key": k, "canon": next(c for kk, c, _, _ in items if kk == k)[:40], "primary": next(p for kk, _, p, _ in items if kk == k)[:40],
                                                         "pin_v4": ref[k], name: sig[k]} for k in diffs]}
        res[name]["diff_all_pass_to_ng_only"] = all(ref[k][0] in outs["pin_v4"]["passing"] and sig[k][0] not in outs["pin_v4"]["passing"] for k in diffs)
    saved = {}
    for k, c, p, f12 in items:
        if f12 and "pass" in f12 and not k.startswith("syn:"):
            st = outs["pin_v4"]["sig"][k][0] in outs["pin_v4"]["passing"]
            if f12.get("kind") == "primary" or f12.get("pass") and f12.get("kind") == "primary":
                saved[k] = (f12["pass"], st)
    res["saved_08_F12_primary_pass_vs_pin_v4_stage"] = {"n": len(saved), "mismatch": [k for k, (a, b) in saved.items() if a != b]}
    syn_mis = []
    for k, c, p, f12 in items:
        if k.startswith("syn:"):
            st = outs["head_off"]["sig"][k][0] in outs["pin_v4"]["passing"] or (outs["head_off"]["sig"][k][0] == "NG_SECONDARY_UNAVAILABLE" and outs["head_off"]["sec_accept"][k])   # 08のfinal(): NG_SECONDARY_UNAVAILABLEのときだけSecondary EXACT/NORMALIZED受理でPASS
            if st != f12["pass"]:
                syn_mis.append(k)
    res["syn_saved_F12_pass_vs_head_off"] = {"mismatch": syn_mis}
    by = {}
    for k in ref:
        by.setdefault(k.split(":")[0], [0, 0, 0])
        by[k.split(":")[0]][0] += 1
        by[k.split(":")[0]][1] += int(ref[k] != outs["head_default"]["sig"][k])
        by[k.split(":")[0]][2] += int(ref[k] != outs["head_off"]["sig"][k])
    res["by_group[n, diff_default, diff_off]"] = by
    res["head_default_flags"] = outs["head_default"]["flags"]
    res["head_off_flags"] = outs["head_off"]["flags"]
    js = json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True)
    open(os.path.join(HERE, "open517_prod_parity_01.out.json"), "w", encoding="utf8", newline="\n").write(js + "\n")
    print(js)
    print("sha256", hashlib.sha256(js.encode("utf8")).hexdigest())
    sys.exit(0)

# ---------------- inner ----------------
sys.path.insert(0, HERE)
sys.path.insert(0, ".")
import eval_common_02 as E
import er078_asr_value_guard_01 as vg
import er078_asr_unified_judge_01 as uj

if MODE == "pin":
    import proto_value_gate_fix_04 as F4
    assert not hasattr(vg, "value_guard_kana_unified")
else:
    assert hasattr(vg, "value_guard_kana_unified")
    if os.environ.get("PARITY_OFF") == "1":
        vg.KANA_WORD_BOUNDARY_CHECK, vg.WEAK_KANA_REGION_COMPAT = False, False
E.api0_guard_on()
sig, sec_accept = {}, {}
for k, c, p, f in inputs():
    if k.startswith("syn:"):
        sec_accept[k] = bool(E.secondary_accept_kind(c, f["secondary"])[0])
    if MODE == "pin":
        with F4.apply_in_process():
            s = E.primary_stage(c, p, False)
    else:
        s = E.primary_stage(c, p, False)
    rs = s["reason"]
    rs = "primary_pass" if str(rs).startswith("primary_pass") else rs
    sig[k] = [s["state"], rs, s["label"], sorted(s["warnings"])]
flags = {"READING_MATCH_FINAL_GATE": getattr(uj, "READING_MATCH_FINAL_GATE", None), "KANA_WORD_BOUNDARY_CHECK": getattr(vg, "KANA_WORD_BOUNDARY_CHECK", None),
         "WEAK_KANA_REGION_COMPAT": getattr(vg, "WEAK_KANA_REGION_COMPAT", None)}
json.dump({"sig": sig, "sec_accept": sec_accept, "passing": sorted(uj.PASSING_STATES), "flags": flags}, open(os.environ["PARITY_OUT"], "w", encoding="utf8"), ensure_ascii=False)
