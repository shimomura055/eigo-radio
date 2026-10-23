# ============================================================
# golden_rebuild_01.py -- ASR-QUALITY-2ITEMS ②UKUS 委任_04 W-05: X/Z golden fixture再作成(一回限りの手順script・API 0)。
#  1. 既存golden rows(g0000-g0297)はbyte不変のまま、UKUS合成行(g0298〜)を末尾へ追記(er109_wiring_golden_build_01.py --append-ukus)。
#  2. 配線前commit overlay(ER109_OVERLAY)で signature tool を走らせ、(a) 既存行の再計算が既存fixtureとバイト同一であること(手順の妥当性)を確認し、
#     (b) 新行のpre署名だけを pre_wiring_signatures_{none,X,Z}_01 の末尾へ追記(既存行・manifest.pre_wiring_commit は触らない)。
#  3. 現行コード(v2)でX/Z署名を採り、post_wiring_changed_{X,Z}_01 を再作成(pre署名と異なる行=v2署名)。
#  4. 変化行を3分類で全件確認: (i) version文字列のみ (ii) 新規UKUS PASS (iii) PASS->NG=0 / その他=想定外(あれば失敗)。結果をGOLDEN_CHANGE_01.mdへ。
# 使い方(cwd=repo root): python docs/research/.../WIRING/golden_rebuild_01.py --overlay <dir of b7b6d07d8 root .py/.json> [--write]
# ============================================================
import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.getcwd()
FIX = os.path.join(ROOT, "er109_output", "aho4_golden_01")
TOOL = os.path.join(ROOT, "er109_wiring_signature_01.py")
OUTMD = os.path.join(ROOT, "docs", "research", "ASR-QUALITY-2ITEMS-COMPREHENSIVE-01", "UKUS", "WIRING", "GOLDEN_CHANGE_01.md")
V1 = "er109_orthographic_equivalence_v1_proto_aho02"
V2 = "er109_orthographic_equivalence_v2_ukus01"
VOL = ("created_at", "rejudged_at", "timing", "ms", "checked_at", "total_ms", "secondary_ms")


def sv(o):
    if isinstance(o, dict):
        return {k: sv(v) for k, v in o.items() if k not in VOL}
    if isinstance(o, list):
        return [sv(v) for v in o]
    return o


def read_raw_lines(path):
    return [l for l in gzip.open(path, "rt", encoding="utf-8").read().split("\n") if l.strip()]


def key_of(line):
    return json.loads(line)["k"].rsplit("|scope=", 1)[0]


def run_tool(rows, scope, out, overlay=None, require_xz=False):
    env = dict(os.environ)
    for k in ("OPENAI_API_KEY", "GEMINI_API_KEY", "SPEECH_KEY", "AZURE_SPEECH_KEY"):
        env.setdefault(k, "dummy")
    env["PYTHONIOENCODING"] = "utf-8"
    if overlay:
        env["ER109_OVERLAY"] = overlay
    cmd = [sys.executable, TOOL, "--rows", rows, "--scope", scope, "--out", out]
    if require_xz:
        cmd.append("--require-xz")
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"tool failed scope={scope} overlay={bool(overlay)}: {r.stderr[-600:]}")
    d = {}
    for l in open(out, encoding="utf-8"):
        if l.strip():
            o = json.loads(l)
            d[o["k"].rsplit("|scope=", 1)[0]] = o["sig"]
    return d


def passof(sig):
    for k in ("verified", "ok"):
        if k in sig:
            return sig[k]
    if "blocked" in sig:
        return not sig["blocked"]
    return None


def norm_v(o):
    return json.loads(json.dumps(o, ensure_ascii=False).replace(V2, V1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--overlay", required=True)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp()
    rows_new = os.path.join(tmp, "golden_rows_new.jsonl")
    subprocess.check_call([sys.executable, "er109_wiring_golden_build_01.py", "--append-ukus", os.path.join(FIX, "golden_rows_01.jsonl"), rows_new], cwd=ROOT)
    n_old = sum(1 for l in open(os.path.join(FIX, "golden_rows_01.jsonl"), encoding="utf-8") if l.strip())
    ids_old = {json.loads(l)["id"] for l in open(os.path.join(FIX, "golden_rows_01.jsonl"), encoding="utf-8") if l.strip()}
    pre_lines, pre = {}, {}
    for sc in ("none", "X", "Z"):
        pre_lines[sc] = read_raw_lines(os.path.join(FIX, f"pre_wiring_signatures_{sc}_01.jsonl.gz"))
        pre[sc] = {key_of(l): sv(json.loads(l)["sig"]) for l in pre_lines[sc]}
    chg_old = {sc: {key_of(l): sv(json.loads(l)["sig"]) for l in read_raw_lines(os.path.join(FIX, f"post_wiring_changed_{sc}_01.jsonl.gz"))} for sc in ("X", "Z")}
    # ---- 2. overlay: 既存行の再計算 == 既存fixture(手順の妥当性) / 新行のpre署名
    ov = {sc: run_tool(rows_new, sc, os.path.join(tmp, f"ov_{sc}.jsonl"), overlay=a.overlay) for sc in ("none", "X", "Z")}
    report = {"overlay_method_check": {}}
    new_pre_lines = {}
    for sc in ("none", "X", "Z"):
        mism = [k for k in pre[sc] if sv(ov[sc].get(k)) != pre[sc][k]]
        report["overlay_method_check"][sc] = {"existing_keys": len(pre[sc]), "mismatch": len(mism), "mismatch_sample": mism[:5]}
        new_keys = [k for k in ov[sc] if k.split("|")[0] not in ids_old]
        new_pre_lines[sc] = [json.dumps({"k": k, "sig": json.loads(json.dumps(ov[sc][k], ensure_ascii=False, sort_keys=True))}, ensure_ascii=False, sort_keys=True) for k in new_keys]
        report["overlay_method_check"][sc]["new_keys"] = len(new_keys)
    # ---- 3. 現行コード(v2)
    now = {sc: run_tool(rows_new, sc, os.path.join(tmp, f"now_{sc}.jsonl"), require_xz=(sc != "none")) for sc in ("none", "X", "Z")}
    full_pre = {sc: {**pre[sc], **{k: sv(ov[sc][k]) for k in ov[sc] if k.split("|")[0] not in ids_old}} for sc in ("none", "X", "Z")}
    out_chg = {}
    cls = {}
    for sc in ("X", "Z"):
        base_v1 = {**pre[sc], **chg_old[sc]}                   # 中間baseline: 現HEAD(v1)のX/Z署名(既存行のみ)
        chg_lines, c = [], {"version_only": [], "new_ukus_pass": [], "other_changed": [], "PASS_to_NG": [], "unchanged_vs_pre": 0, "new_rows_ukus_or_same": []}
        for k, s in now[sc].items():
            s = sv(s)
            p = full_pre[sc].get(k)
            if p is None:
                raise RuntimeError("missing pre for " + k)
            if s == p:
                c["unchanged_vs_pre"] += 1
                continue
            chg_lines.append(json.dumps({"k": k, "sig": json.loads(json.dumps(s, ensure_ascii=False, sort_keys=True))}, ensure_ascii=False, sort_keys=True))
            if passof(p) is True and passof(s) is False:
                c["PASS_to_NG"].append(k)
            rid = k.split("|")[0]
            if rid not in ids_old:
                c["new_rows_ukus_or_same"].append(k)
                continue
            b = base_v1.get(k)
            if b is not None and norm_v(s) == norm_v(b):
                c["version_only"].append(k)
            elif "ukus_spelling_variant" in json.dumps(s) and passof(b) is False and passof(s) is True:
                c["new_ukus_pass"].append(k)
            else:
                c["other_changed"].append(k)
        out_chg[sc] = chg_lines
        cls[sc] = c
    report["classification"] = {sc: {k: (len(v) if isinstance(v, list) else v) for k, v in cls[sc].items()} for sc in cls}
    report["other_changed_keys"] = {sc: cls[sc]["other_changed"][:20] for sc in cls}
    report["PASS_to_NG_keys"] = {sc: cls[sc]["PASS_to_NG"] for sc in cls}
    report["new_ukus_pass_keys"] = {sc: cls[sc]["new_ukus_pass"] for sc in cls}
    print(json.dumps(report, ensure_ascii=False, indent=1))
    bad = (any(v["mismatch"] for v in report["overlay_method_check"].values()) or any(cls[sc]["PASS_to_NG"] for sc in cls) or any(cls[sc]["other_changed"] for sc in cls))
    # scope none: 配線前と完全一致(新行含む)
    diff_none = [k for k, s in now["none"].items() if sv(s) != full_pre["none"][k]]
    report["scope_none_diff_vs_pre"] = diff_none
    print("scope none diff vs pre:", len(diff_none))
    if bad or diff_none:
        print("UNEXPECTED -> not writing")
        sys.exit(2)
    if a.write:
        def wgz(path, lines):
            with gzip.open(path, "wt", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(lines) + "\n")
        for sc in ("none", "X", "Z"):
            wgz(os.path.join(FIX, f"pre_wiring_signatures_{sc}_01.jsonl.gz"), pre_lines[sc] + new_pre_lines[sc])
        for sc in ("X", "Z"):
            wgz(os.path.join(FIX, f"post_wiring_changed_{sc}_01.jsonl.gz"), out_chg[sc])
        with open(os.path.join(FIX, "golden_rows_01.jsonl"), "wb") as f:
            f.write(open(rows_new, "rb").read())
        man = json.load(open(os.path.join(FIX, "manifest.json"), encoding="utf-8"))
        man["sha256"] = {f: hashlib.sha256(open(os.path.join(FIX, f), "rb").read()).hexdigest() for f in man["sha256"]}
        man["note_UKUS_委任_04"] = ("ASR-QUALITY-2ITEMS UKUS: golden_rows 末尾へUKUS合成行g0298〜を追記、pre_wiring_signatures_*は新行の行だけを配線前commit(pre_wiring_commit)overlayで追記(既存行は不変・再計算がfixtureとバイト同一を確認)、"
                                    "post_wiring_changed_{X,Z}はv2(LAYER_VERSION=" + V2 + ")署名で再作成。変化行の3分類=WIRING/GOLDEN_CHANGE_01.md")
        json.dump(man, open(os.path.join(FIX, "manifest.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
        json.dump(report, open(OUTMD.replace(".md", ".json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
        print("written")


if __name__ == "__main__":
    main()
