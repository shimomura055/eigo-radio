# JA-ASR-FALSE-NG-ROOT-FIX-02 委任_02B 統合評価ハーネス(API 0・socket guard・決定的)。事前登録=PREREGISTERED_02.md。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/eval_unified_02.py [out_json_path]
# 層: L0 / L1 / L1+L2 / L1+L3 / L1+L2+L3 を各行で判定し、L4(best-of-N)は保存drawのシミュレーション。
import collections, hashlib, json, os, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02")
import eval_unified_01 as U1
import proto_unified_02 as U
import eval_common_02 as E
import er007_ja_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj

OUT = "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/"
J = U1.J
MOON = U1.MOON
TAIL = "！その奥に潜む「岩の上着」の秘密"
NEG_SHA_PREREG = "d55f24e239d3eb024951c01e57a8d186d9cd6a8ebf979c6470399b5cea2405dd"
FL = {"L0": U.Flags(), "L1": U.Flags(True), "L1+L2": U.Flags(True, True), "L1+L3": U.Flags(True, False, True), "L1+L2+L3": U.Flags(True, True, True)}
FINAL = "L1+L2+L3"


def l3_cases():
    """L3専用の合成コーパス。POS=辞書で救済されるべき正例、NEG=救済してはならない負例。月題固有でない汎用題を含む。"""
    C = []

    def add(group, tag, canon, asr, truth, scen=("PS_same", "S_canon", "P_only")):
        sc = {}
        for s in scen:
            sc[s] = {"PS_same": asr, "S_canon": canon, "P_only": None}[s]
        C.append({"group": group, "truth": truth, "tag": tag, "canon": canon, "primary": asr, "scen": sc})
    # POS
    for k in ("超え", "越え", "こえ"):
        add("L3_POS", f"月題:{k}", MOON, f"月のしわ、8,900本{k}" + TAIL, "POS")
        add("L3_POS", f"汎用人:{k}", "参加者は100人超でした", f"参加者は100人{k}でした", "POS")
        add("L3_POS", f"汎用円:{k}", "売上は1,200円超です", f"売上は1,200円{k}です", "POS")
    add("L3_POS", "月題:詩は+超え(L1+L3併用)", MOON, "月の詩は、8,900本超え" + TAIL, "POS")
    add("L3_POS", "月題:市は+越え(L1+L3併用)", MOON, "月野市は、8,900本越え" + TAIL, "POS")
    # NEG: 値違い・助数詞違い
    for v in ("8,800", "890", "89,000", "9,900", "8,090"):
        add("L3_NEG", f"値違い:{v}本超え", MOON, f"月のしわ、{v}本超え" + TAIL, "NEG")
    for u in ("個", "枚", "人", "円", "冊"):
        add("L3_NEG", f"助数詞違い:{u}", MOON, f"月のしわ、8,900{u}超え" + TAIL, "NEG")
    add("L3_NEG", "汎用値違い", "参加者は100人超でした", "参加者は1,000人超えでした", "NEG")
    add("L3_NEG", "汎用助数詞違い", "参加者は100人超でした", "参加者は100匹超えでした", "NEG")
    add("L3_NEG", "汎用値違い2", "売上は1,200円超です", "売上は1,300円超えです", "NEG")
    # NEG: E4/C2同形異音(本長/本帳/本蝶…は不受理)
    for k in ("長", "帳", "蝶", "調", "町", "鳥"):
        add("L3_NEG", f"E4/C2同形異音:本{k}", MOON, f"月のしわ、8,900本{k}" + TAIL, "NEG")
        add("L3_NEG", f"E4/C2同形異音(汎用):人{k}", "参加者は100人超でした", f"参加者は100人{k}でした", "NEG")
    # NEG: 語句挿入・脱落・意味変化
    for t, a in (("挿入:を", f"月のしわ、8,900本を超え" + TAIL), ("挿入:は", f"月のしわ、8,900本は超え" + TAIL), ("脱落:助数詞", f"月のしわ、8,900超え" + TAIL),
                 ("脱落:数値", f"月のしわ、本超え" + TAIL), ("脱落:末尾", "月のしわ、8,900本超え"), ("脱落:中間", "月のしわ、8,900本超え！その奥に潜む秘密"),
                 ("意味:未満", f"月のしわ、8,900本未満" + TAIL), ("意味:以上", f"月のしわ、8,900本以上" + TAIL), ("意味:超えない", f"月のしわ、8,900本超えない" + TAIL),
                 ("意味:超えず", f"月のしわ、8,900本超えず" + TAIL), ("意味:超える(活用形は辞書対象外)", f"月のしわ、8,900本超える" + TAIL),
                 ("同音異表記便乗:しわ→すわ+超え", f"月のすわ、8,900本超え" + TAIL), ("同音異表記便乗:岩→石+超え", f"月のしわ、8,900本超え！その奥に潜む「石の上着」の秘密")):
        add("L3_NEG", t, MOON, a, "NEG")
    # NEG: 数量に付かない超
    add("L3_NEG", "数量に付かない超(超高速)", "超高速で3回走る", "こえ高速で3回走る", "NEG")
    add("L3_NEG", "数量に付かない超(超高速2)", "超高速で3回走る", "超え高速で3回走る", "NEG")
    # NEG: 片方のengineだけ値が違う(explicit)
    for t, p, s in (("P値違い+S正", "月のしわ、8,800本超え" + TAIL, "月のしわ、8,900本越え" + TAIL), ("P正+S値違い", "月のしわ、8,900本超え" + TAIL, "月のしわ、8,800本越え" + TAIL),
                    ("P値garble+S正", "月のしわ、8000900本超え" + TAIL, "月のしわ、8,900本越え" + TAIL), ("P正+S助数詞違い", "月のしわ、8,900本超え" + TAIL, "月のしわ、8,900個越え" + TAIL)):
        C.append({"group": "L3_NEG", "truth": "NEG", "tag": "片engine:" + t, "canon": MOON, "primary": p, "scen": {"explicit": s}})
    return C


def n3_redraw_cases():
    d = json.load(open(OUT + "n3_redraw_02.json", encoding="utf8"))
    clips = {c["id"]: c for c in json.load(open(J + "n3_clips_01.json", encoding="utf8"))}
    az = {}
    stored = {}
    for l in open(J + "phase3_run/usage_log.jsonl", encoding="utf8"):
        r = json.loads(l)
        if r["stage"] == "N3_asr":
            az[r["item"]] = r["azure_text"]
            stored[r["item"]] = r["openai_text"]
    C = []
    for x in d["draws"]:
        c = clips[x["id"]]
        C.append({"group": "N3_redraw", "truth": "NEG", "tag": f"{x['id']}#d{x['draw']}|{c['type']}", "canon": c["canonical"], "primary": x["text"],
                  "scen": {"real": az[x["id"]], "S_canon": c["canonical"]}, "n3": {"id": x["id"], "draw": x["draw"]}})
    return C, az, stored, clips


def summarize_flags_row(res):
    return {k: {"cat": v["cat"], "reason": v["reason"], "route": v["route"], "needs_azure": v.get("needs_new_azure_call", False),
                "layers": [a.get("layer") for a in v.get("layers", [])]} for k, v in res.items()}


def judge_all(canon, prim, sec_text, wav):
    return {name: U.judge(canon, prim, sec_text, wav, fl) for name, fl in FL.items()}


def main():
    outp = sys.argv[1] if len(sys.argv) > 1 else OUT + "eval_unified_02.out.json"
    E.api0_guard_on()
    dwav = E.dummy_wav()
    res = {"production_sha256": {f: hashlib.sha256(open(f, "rb").read()).hexdigest()[:16] for f in ("er007_ja_secondary_asr_01.py", "er078_asr_unified_judge_01.py", "er078_asr_value_guard_01.py", "er007_ja_asr_validator_01.py")},
           "head_consts": {"READING_MATCH_FINAL_GATE": uj.READING_MATCH_FINAL_GATE, "JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED": sec.JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED}}
    # ---- コーパス(Phase 1と同一 + L3 + N3_redraw) ----
    base = U1.corpus()
    neg_rows = []
    for c in base:
        for sn, st in c["scen"].items():
            if c["truth"] == "NEG":
                neg_rows.append([c["group"], c["tag"], c["canon"], c["primary"], sn, st])
    neg_sha = hashlib.sha256(json.dumps(sorted(neg_rows), ensure_ascii=False).encode()).hexdigest()
    assert neg_sha == NEG_SHA_PREREG, neg_sha
    res["neg_set"] = {"n": len(neg_rows), "sha256": neg_sha}
    n3c, n3_az, n3_stored, n3_clips = n3_redraw_cases()
    corpus = base + l3_cases() + n3c
    rows = []
    for c in corpus:
        for sn, st in c["scen"].items():
            r = judge_all(c["canon"], c["primary"], st, dwav)
            rows.append({"group": c["group"], "truth": c["truth"], "tag": c["tag"], "canon": c["canon"], "primary": c["primary"], "scenario": sn, "secondary": st,
                         "n3": c.get("n3"), "res": summarize_flags_row(r)})
    res["rows"] = rows
    # ---- Phase 1 M0/M1 との行ごと一致 ----
    p1 = json.load(open(OUT + "eval_unified_01.out.json", encoding="utf8"))["rows"]
    key = lambda r: (r["group"], r["tag"], r["canon"], r["primary"], r["scenario"], r["secondary"])
    cur = {key(r): r for r in rows}
    m0_mis, m1_diff, n_cmp = [], [], 0
    for r in p1:
        k = key(r)
        n_cmp += 1
        c = cur[k]["res"]
        if (c["L0"]["cat"], c["L0"]["reason"]) != (r["res"]["M0"]["cat"], r["res"]["M0"]["reason"]):
            m0_mis.append(list(k[:3]))
        if c["L1"]["cat"] != r["res"]["M1"]["cat"]:
            m1_diff.append({"k": list(k[:5]), "M1": r["res"]["M1"]["cat"], "L1": c["L1"]["cat"], "L0": c["L0"]["cat"], "irregular": bool(U.irregular_atoms(r["canon"]))})
    res["parity"] = {"n_compared": n_cmp, "L0_vs_M0_mismatch": len(m0_mis), "L0_vs_M0_mismatch_examples": m0_mis[:10], "L1_vs_M1_diff": m1_diff}
    # ---- 正例6音声 ----
    pos = []
    for p in U1.load_positives():
        wav = p["wav"]
        a0 = p["azure"][0][1] if p["azure"] else None
        draws = []
        for otag, ot in p["openai"]:
            draws.append({"openai_tag": otag, "openai": ot, "azure": a0, "res": summarize_flags_row(judge_all(MOON, ot, a0, wav))})
        extra_az = []
        for atag, at in p["azure"][1:]:
            for otag, ot in p["openai"]:
                extra_az.append({"openai_tag": otag, "azure_tag": atag, "res": summarize_flags_row(judge_all(MOON, ot, at, wav))})
        pos.append({"run": p["run"], "attempt": p["attempt"], "sha16": p["sha16"], "openai": p["openai"], "azure": p["azure"], "whisper_local": p["whisper_local"],
                    "draws": draws, "extra_azure_pairs": extra_az})
    res["positives"] = pos
    # ---- L4 best-of-N(正例): 保存順 + 超幾何 ----
    # 実際のjudge結果(dict)が必要なため、ここで再判定して best_of_n を計算する(決定的)
    l4 = []
    for p, pr in zip(U1.load_positives(), pos):
        a0 = p["azure"][0][1] if p["azure"] else None
        per_flag = {}
        for name in ("L1+L2", FINAL):
            seq = [U.judge(MOON, ot, a0, p["wav"], FL[name]) for _, ot in p["openai"]]
            m = sum(1 for r in seq if r["cat"] != "NG")
            per_flag[name] = {"k": len(seq), "m_nonNG": m,
                              "N": {str(n): {"stored_order": U.best_of_n(seq, n), "hyper_reach": round(U.hyper_reach(len(seq), m, n), 4)} for n in (1, 2, 3, 4)}}
        l4.append({"run": p["run"], "attempt": p["attempt"], "per_flag": per_flag})
    res["l4_positive"] = l4
    # ---- L4 best-of-N(N3負例): 新4 draw、stored(第0draw)併記 ----
    l4n = {"clips": {}}
    by_id = collections.defaultdict(list)
    for c in n3c:
        by_id[c["n3"]["id"]].append(c)
    for cid, cs in sorted(by_id.items()):
        cs.sort(key=lambda c: c["n3"]["draw"])
        entry = {"type": n3_clips[cid]["type"], "tts_input": n3_clips[cid]["tts_input"], "canon": n3_clips[cid]["canonical"], "azure": n3_az[cid], "stored_openai": n3_stored[cid], "new_draws": [c["primary"] for c in cs], "scn": {}}
        for scn, sectxt in (("real", n3_az[cid]), ("S_canon", n3_clips[cid]["canonical"])):
            for fname in ("L0", FINAL):
                new = [U.judge(n3_clips[cid]["canonical"], c["primary"], sectxt, dwav, FL[fname]) for c in cs]
                withstored = [U.judge(n3_clips[cid]["canonical"], n3_stored[cid], sectxt, dwav, FL[fname])] + new
                ent = {"new_cats": [r["cat"] for r in new], "stored_cat": withstored[0]["cat"],
                       "N_new": {str(n): U.best_of_n(new, n)["cat"] for n in (1, 2, 3, 4)},
                       "N_with_stored": {str(n): U.best_of_n(withstored, n)["cat"] for n in (1, 2, 3, 4, 5)},
                       "hyper_new": {str(n): round(U.hyper_reach(4, sum(1 for r in new if r["cat"] != "NG"), n), 4) for n in (1, 2, 3, 4)},
                       "hyper_with_stored": {str(n): round(U.hyper_reach(5, sum(1 for r in withstored if r["cat"] != "NG"), n), 4) for n in (1, 2, 3, 4, 5)},
                       "routes": [r["route"] for r in withstored if r["cat"] != "NG"]}
                entry["scn"][f"{scn}|{fname}"] = ent
        # Human Review 候補(全層NG後、全draw+stored対)
        pairs = [(n3_stored[cid], n3_az[cid])] + [(c["primary"], n3_az[cid]) for c in cs]
        entry["hr"] = U.hr_candidate(n3_clips[cid]["canonical"], pairs)
        l4n["clips"][cid] = entry
    res["l4_n3"] = l4n
    # ---- Human Review 候補: 正例(全層+L4[N=3]でも残るもの) と 負例text行 ----
    hr_pos = []
    for p, pr in zip(U1.load_positives(), pos):
        a0 = p["azure"][0][1] if p["azure"] else None
        pairs = [(ot, a0) for _, ot in p["openai"]]
        hr_pos.append({"run": p["run"], "attempt": p["attempt"], "hr": U.hr_candidate(MOON, pairs)})
    res["hr_positive"] = hr_pos
    hr_rows = collections.Counter()
    for r in rows:
        if r["truth"] != "NEG" or r["group"] == "N3_redraw":
            continue
        fin = r["res"][FINAL]
        if fin["cat"] != "NG":
            continue
        h = U.hr_candidate(r["canon"], [(r["primary"], r["secondary"])])
        hr_rows[(r["group"], h["candidate"])] += 1
    res["hr_neg_text"] = {f"{g}|{'cand' if c else 'not'}": n for (g, c), n in sorted(hr_rows.items())}
    E.api0_guard_off()
    s = json.dumps(res, ensure_ascii=False, sort_keys=True, indent=1)
    open(outp, "w", encoding="utf-8", newline="\n").write(s)
    print("sha256", hashlib.sha256(s.encode("utf-8")).hexdigest(), "rows", len(rows), "L0_vs_M0_mismatch", res["parity"]["L0_vs_M0_mismatch"], "L1_vs_M1_diff", len(m1_diff))


if __name__ == "__main__":
    main()
