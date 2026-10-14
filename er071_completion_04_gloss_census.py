# 委任_04 gloss整合census (API 0円、read-only)。keywords_canonicalized.json群で key_phrase が display_phrase と異なるitemを抽出。
import glob, json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
W = re.compile(r"[a-z']+")
def toks(s): return W.findall((s or "").lower().replace("’", "'"))
def stem(t): return re.sub(r"(ing|ed|es|s|d)$", "", t)
seen = {}
for p in glob.glob("er*_output/**/keywords_canonicalized.json", recursive=True):
    try: d = json.load(open(p, encoding="utf-8"))
    except Exception: continue
    for it in d.get("items", []) if isinstance(d, dict) else []:
        kp = it.get("key_phrase"); dp = it.get("display_phrase"); g = it.get("japanese_gloss")
        if not kp or not dp: continue
        a = {stem(t) for t in toks(dp)}; b = [stem(t) for t in toks(kp)]
        extra = [t for t in b if t not in a]
        key = (dp, kp, g)
        e = seen.setdefault(key, {"n": 0, "extra": extra, "flag": it.get("kp_extends_beyond_candidate"), "ex": p})
        e["n"] += 1
rows = sorted(seen.items(), key=lambda kv: tuple(str(x) for x in kv[0]))
total = len(rows)
diff = [(k, v) for k, v in rows if k[0].lower() != k[1].lower()]
ext = [(k, v) for k, v in diff if v["extra"]]
print("unique triples", total, "kp!=display", len(diff), "kp has extra token", len(ext))
json.dump([{"display_phrase": k[0], "key_phrase": k[1], "gloss": k[2], "extra_tokens": v["extra"], "files": v["n"], "example": v["ex"]} for k, v in ext],
          open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in ext: print(f"{k[0]!r} -> {k[1]!r} | {k[2]} | extra={v['extra']} n={v['n']}")
