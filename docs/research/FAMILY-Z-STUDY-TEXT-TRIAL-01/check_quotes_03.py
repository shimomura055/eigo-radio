# 決定論的な引用逐語一致照合(DEV)。出力中の英語スパン(5語以上)が本文に逐語で存在するかを確認。Part 4と「比較用」行は対象外(別枠で列挙)。
import re, sys, os, json
BASE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
sys.path.insert(0, BASE)
import run_trial_03 as r3, run_trial_01 as t1
def norm(s): return re.sub(r"\s+", " ", s.replace("’","'").replace("‘","'").replace("“",'"').replace("”",'"').replace("*","")).strip().lower()
TEXT = {"gift": t1.TEXT, "open_window": r3.read(r3.OW), "ig_nobel": r3.read(r3.IG)}
res = {}
files = sorted(f for f in os.listdir(BASE) if f.startswith("OUTPUT_") and f.endswith("_RAW.md"))
for f in files:
    m = re.match(r"OUTPUT_(02B|02|03dR2|03d|03cR2|03c|03bR2|03b|03|01)(?:_(gift|ig_nobel|open_window))?_RAW\.md", f)
    if not m: continue
    work = m.group(2) or "gift"
    src = norm(TEXT[work])
    out = open(os.path.join(BASE, f), encoding="utf-8").read()
    out = out.split("## Part 4")[0]
    ok = 0; bad = []; comp = []
    for line in out.splitlines():
        for sp in re.findall(r"[A-Za-z0-9’‘“”\"'\-—,.;:!?() ]{20,}", line):
            sp = sp.strip(" ,;:()*")
            if len(re.findall(r"[A-Za-z]+", sp)) < 5: continue
            is_comp = "比較用" in line or "比較" in line and "：" in line
            n = norm(sp)
            n2 = n.strip('" ,.;:!?')
            if n2 in src or any(n2.strip('" ') == x for x in []): ok += 1
            elif is_comp: comp.append(sp)
            else: bad.append(sp)
    res[f] = {"verbatim_ok": ok, "not_found_non_comparison": bad, "comparison_or_other": comp}
open(os.path.join(BASE, "quote_check_03.json"), "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
for f, v in res.items():
    print(f, "ok", v["verbatim_ok"], "NOTFOUND", len(v["not_found_non_comparison"]), "comp", len(v["comparison_or_other"]))
    for b in v["not_found_non_comparison"]: print("   NF:", b[:150])
