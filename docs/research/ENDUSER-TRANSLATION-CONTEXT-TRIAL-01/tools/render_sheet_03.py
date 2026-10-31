import json, sys
sheet = json.load(open(sys.argv[1], encoding="utf-8")); a, b = int(sys.argv[2]), int(sys.argv[3])
for r in sheet:
    if not (a <= r["row"] <= b):
        continue
    pv = (r["prev"][-1][:90] + "｜") if r["prev"] else ""; nx = ("｜" + r["next"][0][:90]) if r["next"] else ""
    print(f"#{r['row']} EN: {r['en']}\n   (ctx: {pv}…{nx})")
    for L, t in r["variants"].items():
        print(f"  {L}: {t}")
