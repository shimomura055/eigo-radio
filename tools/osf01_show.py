# OSF01 表示+機械チェック(DEV/Trial専用)。使い方: py osf01_show.py <ver> <tag> [<tag>...]
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osf01_gen as g
BANNED = ["backfire", "sold on", "live up to the hype", "torn between", "tide is turning", "room for improvement"]
def norm(s): return re.sub(r"[^a-z ]", "", s.lower().replace("-", " ")).strip()
def checks(cell, doc):
    inp = g.inputs_for(cell); body = norm(inp["body"]); kps = [norm(k[0]) for k in inp["kp"]]; iss = []
    for it in doc["result"]["items"]:
        core = norm(re.sub(r"\b(A|B|something|someone|somebody|one's|your|my)\b", "", it["core_expression"]))
        core = re.sub(r"\s+", " ", core).strip()
        for k in kps:
            if k and (k in core or core in k): iss.append(f"KP_overlap:{core}~{k}")
        if core and core in body: iss.append(f"core_in_body:{core}")
        fl = norm(it["further_en"])
        for k in kps:
            if k and k in fl: iss.append(f"KP_in_further_sentence:{k}")
        if any(b in fl for b in BANNED): iss.append("banned_example_expr")
        if len(it["point_ja"]) > 130: iss.append(f"point_len={len(it['point_ja'])}")
        for f in ("topic_hook_ja", "basic_en", "basic_ja", "further_en", "further_ja", "core_expression", "point_ja", "why_ja"):
            if not str(it.get(f, "")).strip(): iss.append("empty:" + f)
    if not (1 <= len(doc["result"]["items"]) <= 2): iss.append("n_items")
    return iss
if __name__ == "__main__":
    ver = sys.argv[1]
    for tag in sys.argv[2:]:
        print("=" * 20, tag)
        for c in g.CELLS:
            p = os.path.join(g.OUT, f"{c}__{ver}__{tag}.json")
            if not os.path.exists(p): continue
            d = json.load(open(p, encoding="utf-8"))
            if not d["result"]: print(c, "PARSE_ERR", d["parse_error"]); continue
            print(f"--- {c} [{d['model']}] ¥{d['cost_jpy']} {d['elapsed_sec']}s out_tok={d['usage']['output_tokens']}  checks={checks(c, d)}")
            for it in d["result"]["items"]:
                print(f"  CORE: {it['core_expression']}\n  hook: {it['topic_hook_ja']}\n  basic: {it['basic_en']} / {it['basic_ja']}\n  further: {it['further_en']} / {it['further_ja']}\n  point: {it['point_ja']}\n  why: {it['why_ja']}\n  shift: {it['meaning_shift_note']}")
