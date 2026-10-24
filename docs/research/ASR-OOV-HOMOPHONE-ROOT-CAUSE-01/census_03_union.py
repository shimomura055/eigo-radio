# census_03_union.py -- ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_01 §1(c)/§3-C。API 0・読取専用。
# 保存済みの(Primary転写, Secondary=Azure転写)の両方がある attempt で、
#  (1) 現行の判定結果(NG_BOTH/救済/...)と、 (2) 『語単位クロスエンジン確認(候補E)』= 原稿の全token位置が少なくとも一方のエンジンで
#  逐語一致(equal block)していて、挿入/脱落が相手エンジンで否定されている、が成り立つ行の数を機械抽出する。
import collections, difflib, glob, json, os, re, sys
sys.path.insert(0, ".")
import er109_stored_census_01 as C
TOK = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")
def norm(t): return TOK.findall((t or "").lower().replace("’", "'"))
NEG = {"not", "no", "never", "nothing", "none", "cannot", "can't", "don't", "doesn't", "didn't", "won't", "isn't", "aren't", "wasn't", "weren't", "n't"}

def align(c, h):
    """returns confirmed: set(idx of c) matched equal; hyp_pos: dict c idx -> h idx; ins_gaps: list of gap idx where h has insertion"""
    sm = difflib.SequenceMatcher(None, c, h, autojunk=False)
    conf, pos, ins = set(), {}, []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1): conf.add(i1 + k); pos[i1 + k] = j1 + k
        elif op == "insert": ins.append(i1)
    return conf, pos, ins

def union_rule(c, p, s):
    if not c: return False, "empty"
    cp, pp, ip = align(c, p); cs, ps, is_ = align(c, s)
    unconfirmed = [i for i in range(len(c)) if i not in cp and i not in cs]
    if unconfirmed: return False, "unconfirmed:" + " ".join(c[i] for i in unconfirmed)
    # 数字/否定が絡む位置は対象外(保護差は既存Gateに委ねる=本集計では保守的に非救済)
    dif = [i for i in range(len(c)) if i not in cp or i not in cs]
    for i in dif:
        if any(ch.isdigit() for ch in c[i]) or c[i] in NEG: return False, "protected_token:" + c[i]
    # 挿入の否定: 一方の挿入gapは、他方で隣接equalでなければ非救済
    for ins, other_pos in ((ip, ps), (is_, pp)):
        for g in ins:
            a, b = g - 1, g
            if a >= 0 and b < len(c):
                if not (a in other_pos and b in other_pos and other_pos[b] == other_pos[a] + 1): return False, "insertion_unrefuted"
            else:
                return False, "edge_insertion"
    return True, "ok"

def rows():
    out = []
    for f in sorted(glob.glob("**/*tts_generation_results*.json", recursive=True)):
        if ".venv" in f: continue
        try: d = json.load(open(f, encoding="utf-8"))
        except Exception: continue
        azm = C.azure_texts_by_attempt(os.path.dirname(os.path.dirname(f)))
        def add(seg_id, v, kp):
            canon = v.get("canonical_text") or v.get("text")
            before = v.get("canonical_text_before_local_rewrite")
            if not C.is_english(canon): return
            for idx, a in enumerate(v.get("attempts_log") or []):
                j = a.get("asr_judgement") or {}
                pr = j.get("primary") or {}; sec = j.get("secondary") or {}
                ptxt = a.get("asr_text") or pr.get("text")
                stxt = sec.get("text") if sec.get("called") else azm.get((seg_id, str(a.get("attempt"))))
                if not ptxt or not stxt: continue
                out.append({"src": f.replace("\\", "/"), "seg": seg_id, "kp": kp, "attempt": a.get("attempt"), "idx": idx, "n_attempts": len(v.get("attempts_log") or []),
                            "canonical": canon, "canonical_before_lr": before, "p": ptxt, "s": stxt, "state": j.get("state"), "primary_label": pr.get("label") or a.get("audio_classification"),
                            "sec_label": sec.get("label"), "verified": a.get("verified"), "final_status": v.get("status")})
        for sid, v in (d.get("segments") or {}).items():
            if isinstance(v, dict): add(sid, v, False)
        for rk, v in (d.get("key_phrases") or {}).items():
            e = (v or {}).get("english") or {}
            if isinstance(e, dict): add(f"kp{rk}_en", e, True)
    return out

def main():
    R = rows(); print("rows with both P and S text:", len(R))
    res = []
    for r in R:
        c1 = norm(r["canonical"]); c0 = norm(r["canonical_before_lr"]) if r["canonical_before_lr"] else None
        best = None
        for c in ([c0] if c0 else []) + [c1]:
            ok, why = union_rule(c, norm(r["p"]), norm(r["s"]))
            if best is None or ok: best = (ok, why)
            if ok: break
        r["union_ok"], r["union_why"] = best
        res.append(r)
    pn = [r for r in res if r["primary_label"] not in C.PASS_LABELS]
    print("Primary非PASS行:", len(pn))
    cnt = collections.Counter((r["state"], r["union_ok"]) for r in pn)
    print(cnt)
    fix = [r for r in pn if r["union_ok"] and r["state"] in ("NG_BOTH", None) and not r["verified"]]
    print("union_ok かつ 現行未検証(NG):", len(fix))
    for r in fix: print(" ", r["src"].split("/")[1] if "/" in r["src"] else r["src"], r["seg"], r["attempt"], r["state"], r["primary_label"], r["sec_label"], r["final_status"])
    json.dump({"rows": len(R), "primary_non_pass": len(pn), "union_ok_not_verified": fix, "state_by_union": {f"{k[0]}|{k[1]}": v for k, v in cnt.items()}}, open("docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/census_03_union_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
main()
